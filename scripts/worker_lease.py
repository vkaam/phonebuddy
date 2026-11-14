"""Run a cooperative worker under a renewable task lease."""
import argparse
import json
import os
import select
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.task_lease import BlobStore, LeaseError, acquire

ROOT = Path(__file__).resolve().parent.parent
LEASE_ACCOUNT = 'pbphonebuddyleases'
LEASE_CONTAINER = 'task-leases'

# The watchdog owns the process group and stays alive until the supervisor
# terminates it. The worker is stopped before exec until the supervisor arms it.
CHILD_BOOTSTRAP = (
    'import os,signal,sys; os.kill(os.getpid(),signal.SIGSTOP); '
    'os.execvp(sys.argv[1],sys.argv[1:])'
)
WATCHDOG = """import os, select, signal, subprocess, sys, time
control, status = map(int, sys.argv[1:3])
try:
    child = subprocess.Popen([sys.executable, '-I', '-S', '-c', sys.argv[3], *sys.argv[4:]])
    while True:
        ready, _, _ = select.select([control], [], [], .05)
        if ready and not os.read(control, 1):
            raise RuntimeError('supervisor stopped')
        pid, state = os.waitpid(child.pid, os.WUNTRACED | os.WNOHANG)
        if pid and os.WIFSTOPPED(state):
            break
        if pid:
            raise RuntimeError('bootstrap exited before stopping')
        time.sleep(.01)
    os.write(status, b'R')
    if os.read(control, 1) != b'G':
        raise RuntimeError('supervisor stopped')
    os.kill(child.pid, signal.SIGCONT)
    while True:
        ready, _, _ = select.select([control], [], [], .05)
        if ready and not os.read(control, 1):
            raise RuntimeError('supervisor stopped')
        result = child.poll()
        if result is not None:
            os.write(status, ('X%d\\n' % result).encode())
            # Keep the group leader alive until the supervisor kills the group.
            while os.read(control, 1):
                pass
            break
finally:
    os.killpg(os.getpgrp(), signal.SIGKILL)
"""


class WorkerError(RuntimeError):
    """The worker could not safely begin or continue."""


class Supervisor:
    def __init__(self, lease, interval=20, poll_interval=0.2, grace=5):
        if interval <= 0 or interval >= lease.duration:
            raise ValueError('renewal interval must be positive and less than lease duration')
        self.lease = lease
        self.interval = interval
        self.poll_interval = poll_interval
        self.grace = grace
        self.stop = threading.Event()
        self.lost = threading.Event()
        self.thread = threading.Thread(target=self._renew, daemon=True)

    def _renew(self):
        while not self.stop.wait(self.interval):
            try:
                self.lease.renew()
            except Exception:
                self.lost.set()
                return

    def start(self):
        self.thread.start()

    def healthy(self):
        if self.lost.is_set():
            return False
        try:
            self.lease._check()
        except Exception:
            self.lost.set()
            return False
        return True

    def _terminate_group(self, watchdog):
        try:
            try:
                os.killpg(watchdog.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            watchdog.wait(timeout=self.grace)
            deadline = time.monotonic() + self.grace
            while True:
                try:
                    os.killpg(watchdog.pid, 0)
                except ProcessLookupError:
                    break
                if time.monotonic() >= deadline:
                    self.lost.set()
                    raise WorkerError('process group cleanup could not be confirmed')
                time.sleep(min(self.poll_interval, max(0, deadline - time.monotonic())))
        except (OSError, subprocess.TimeoutExpired) as error:
            self.lost.set()
            raise WorkerError('process group cleanup could not be confirmed') from error

    def run(self, command, *, stdout=None, stderr=None, timeout=None, env=None):
        if not self.healthy() or self.stop.is_set():
            raise WorkerError('lease unavailable or shutdown requested')
        control_read, control_write = os.pipe()
        try:
            status_read, status_write = os.pipe()
        except OSError:
            os.close(control_read)
            os.close(control_write)
            raise
        try:
            watchdog = subprocess.Popen(
                [sys.executable, '-I', '-S', '-c', WATCHDOG, str(control_read),
                 str(status_write), CHILD_BOOTSTRAP, *command], cwd=ROOT,
                pass_fds=(control_read, status_write), stdin=subprocess.DEVNULL,
                stdout=stdout, stderr=stderr, start_new_session=True, env=env)
        except BaseException:
            for fd in (control_read, control_write, status_read, status_write):
                os.close(fd)
            raise
        os.close(control_read)
        os.close(status_write)
        deadline = None if timeout is None else time.monotonic() + timeout
        termination_started = False
        try:
            ready, _, _ = select.select([status_read], [], [], 5)
            if not ready or os.read(status_read, 1) != b'R':
                self.lost.set()
                raise WorkerError('worker watchdog unavailable')
            if not self.healthy() or self.stop.is_set():
                raise WorkerError('lease lost or shutdown requested')
            os.write(control_write, b'G')
            data = b''
            while True:
                healthy = self.healthy()
                if self.stop.is_set() or not healthy:
                    raise WorkerError('lease lost or shutdown requested')
                if deadline is not None and time.monotonic() >= deadline:
                    raise WorkerError('preflight timed out')
                ready, _, _ = select.select([status_read], [], [], self.poll_interval)
                if ready:
                    chunk = os.read(status_read, 64)
                    if not chunk:
                        self.lost.set()
                        raise WorkerError('worker watchdog stopped')
                    data += chunk
                    if b'\n' in data:
                        if not data.startswith(b'X'):
                            self.lost.set()
                            raise WorkerError('invalid watchdog status')
                        result = int(data[1:].strip())
                        break
            termination_started = True
            self._terminate_group(watchdog)
            if self.stop.is_set() or not self.healthy():
                raise WorkerError('lease lost or shutdown requested')
            return result
        except BaseException:
            if not termination_started:
                self._terminate_group(watchdog)
            raise
        finally:
            os.close(control_write)
            os.close(status_read)

    def close(self):
        self.stop.set()
        self.thread.join(timeout=self.lease.duration)
        if self.thread.is_alive():
            self.lost.set()
            raise WorkerError('renewal did not stop; lease ownership is uncertain')
        if not self.lost.is_set() and self.healthy():
            self.lease.release()


def azure_token():
    try:
        result = subprocess.run(['az', 'account', 'get-access-token', '--resource',
                                 'https://storage.azure.com/', '--query', 'accessToken', '-o', 'tsv'],
                                capture_output=True, text=True, timeout=15, check=True)
    except (OSError, subprocess.SubprocessError) as error:
        raise WorkerError('Azure token unavailable') from error
    token = result.stdout.strip()
    if not token:
        raise WorkerError('Azure token unavailable')
    return token


def reconcile(supervisor, task, branch):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0')
    if supervisor.run(['git', 'fetch', 'origin'], timeout=120, env=env) != 0:
        raise WorkerError('could not refresh origin')
    with tempfile.TemporaryFile(mode='w+t') as output:
        command = [sys.executable, '-B', str(ROOT / 'scripts/backlog_consistency.py'),
                   '--base', 'origin/main', '--task', task, '--branch', branch]
        if supervisor.run(command, stdout=output, timeout=180, env=env) != 0:
            raise WorkerError('task reconciliation failed')
        output.seek(0)
        try:
            evidence = json.load(output)
        except (ValueError, OSError) as error:
            raise WorkerError('task reconciliation evidence unavailable') from error
        if evidence.get('status') != 'pass' or evidence.get('claim_verified') is not True:
            raise WorkerError('task reconciliation did not verify the claim')
    with tempfile.TemporaryFile(mode='w+t') as output:
        if supervisor.run(['git', 'branch', '--show-current'], stdout=output, timeout=15, env=env) != 0:
            raise WorkerError('cannot confirm current branch')
        output.seek(0)
        if output.read().strip() != branch:
            raise WorkerError('current branch changed during reconciliation')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', required=True)
    parser.add_argument('--branch', required=True)
    parser.add_argument('--duration', type=int, default=60)
    parser.add_argument('--renew-interval', type=float, default=20)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a worker command is required after --')
    current = subprocess.run(['git', 'branch', '--show-current'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    if current != args.branch:
        raise WorkerError('current branch does not match the approved task branch')
    if not 15 <= args.duration <= 60 or not 0 < args.renew_interval < args.duration:
        parser.error('duration must be 15-60 seconds and renewal interval must be shorter')
    store = BlobStore(LEASE_ACCOUNT, LEASE_CONTAINER, azure_token)
    lease = acquire(store, args.task, args.duration)
    supervisor = Supervisor(lease, args.renew_interval)
    previous = {}
    try:
        for sig in (signal.SIGINT, signal.SIGTERM):
            previous[sig] = signal.signal(sig, lambda *_: supervisor.stop.set())
        supervisor.start()
        reconcile(supervisor, args.task, args.branch)
        return supervisor.run(command)
    finally:
        try:
            supervisor.close()
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (LeaseError, WorkerError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f'worker lease: {error}', file=sys.stderr)
        sys.exit(1)
