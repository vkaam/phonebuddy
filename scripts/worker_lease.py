"""Run a cooperative worker under a renewable task lease."""
import argparse
import json
import os
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

    def _terminate_group(self, child):
        try:
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                child.wait()
                return
            try:
                child.wait(timeout=self.grace)
            except subprocess.TimeoutExpired as error:
                self.lost.set()
                raise WorkerError('worker termination could not be confirmed') from error
            deadline = time.monotonic() + self.grace
            while True:
                try:
                    os.killpg(child.pid, 0)
                except ProcessLookupError:
                    break
                if time.monotonic() >= deadline:
                    self.lost.set()
                    raise WorkerError('process group cleanup could not be confirmed')
                time.sleep(min(self.poll_interval, max(0, deadline - time.monotonic())))
        except OSError as error:
            self.lost.set()
            raise WorkerError('process group cleanup could not be confirmed') from error

    def run(self, command, *, stdout=None, stderr=None, timeout=None, env=None):
        if not self.healthy() or self.stop.is_set():
            raise WorkerError('lease unavailable or shutdown requested')
        child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr,
                                 start_new_session=True, env=env)
        deadline = None if timeout is None else time.monotonic() + timeout
        try:
            while child.poll() is None:
                if deadline is not None and time.monotonic() >= deadline:
                    raise WorkerError('preflight timed out')
                healthy = self.healthy()
                if self.stop.is_set() or not healthy:
                    raise WorkerError('lease lost or shutdown requested')
                time.sleep(self.poll_interval)
            healthy = self.healthy()
            if self.stop.is_set() or not healthy:
                raise WorkerError('lease lost or shutdown requested')
            result = child.returncode
            self._terminate_group(child)
            healthy = self.healthy()
            if self.stop.is_set() or not healthy:
                raise WorkerError('lease lost or shutdown requested')
            return result
        except BaseException:
            self._terminate_group(child)
            raise

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
