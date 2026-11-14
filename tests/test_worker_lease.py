import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from scripts.task_lease import LeaseError
from scripts.worker_lease import Supervisor, WorkerError, main, reconcile


class FakeLease:
    duration = 60

    def __init__(self):
        self.valid = True
        self.renewals = 0
        self.releases = 0
        self.fail = False

    def _check(self):
        if not self.valid:
            raise LeaseError('lost')

    def renew(self):
        self.renewals += 1
        if self.fail:
            self.valid = False
            raise LeaseError('lost')

    def release(self):
        self.releases += 1
        self.valid = False


class SupervisorTests(unittest.TestCase):
    def test_renews_and_releases_on_clean_exit(self):
        lease = FakeLease()
        supervisor = Supervisor(lease, interval=0.02, poll_interval=0.01)
        supervisor.start()
        try:
            self.assertEqual(supervisor.run([sys.executable, '-c', 'import time; time.sleep(0.12)']), 0)
        finally:
            supervisor.close()
        self.assertGreater(lease.renewals, 0)
        self.assertEqual(lease.releases, 1)

    def test_renewal_failure_stops_child_before_it_can_publish(self):
        lease = FakeLease()
        lease.fail = True
        supervisor = Supervisor(lease, interval=0.05, poll_interval=0.01, grace=0.1)
        with tempfile.TemporaryDirectory() as directory:
            marker = str(Path(directory) / 'published')
            code = 'import pathlib,sys,time; time.sleep(0.5); pathlib.Path(sys.argv[1]).write_text("published")'
            supervisor.start()
            try:
                with self.assertRaises(WorkerError):
                    supervisor.run([sys.executable, '-c', code, marker])
                time.sleep(0.6)
                self.assertFalse(os.path.exists(marker))
            finally:
                supervisor.close()
        self.assertEqual(lease.releases, 0)

    def test_normal_exit_stops_background_descendants_before_release(self):
        lease = FakeLease()
        supervisor = Supervisor(lease, interval=1, poll_interval=0.01, grace=0.1)
        with tempfile.TemporaryDirectory() as directory:
            marker = str(Path(directory) / 'late')
            background = 'import pathlib,sys,time; time.sleep(0.5); pathlib.Path(sys.argv[1]).write_text("late")'
            parent = 'import subprocess,sys; subprocess.Popen([sys.executable,"-c",sys.argv[1],sys.argv[2]])'
            supervisor.start()
            try:
                try:
                    self.assertEqual(supervisor.run([sys.executable, '-c', parent, background, marker]), 0)
                except WorkerError:
                    # Some hosts cannot confirm orphan-group disappearance; fail closed.
                    self.assertTrue(supervisor.lost.is_set())
            finally:
                supervisor.close()
            time.sleep(0.6)
            self.assertFalse(os.path.exists(marker))
        self.assertEqual(lease.releases, 0 if supervisor.lost.is_set() else 1)

    def test_hung_preflight_is_stopped_and_lease_released(self):
        lease = FakeLease()
        supervisor = Supervisor(lease, interval=1, poll_interval=0.01, grace=0.1)
        supervisor.start()
        try:
            with self.assertRaisesRegex(WorkerError, 'timed out'):
                supervisor.run([sys.executable, '-c', 'import time; time.sleep(5)'], timeout=0.1)
        finally:
            supervisor.close()
        self.assertEqual(lease.releases, 1)

    def test_shutdown_stops_running_worker_and_releases_lease(self):
        lease = FakeLease()
        supervisor = Supervisor(lease, interval=1, poll_interval=0.01, grace=0.1)
        supervisor.start()
        timer = threading.Timer(0.1, supervisor.stop.set)
        timer.start()
        try:
            with self.assertRaises(WorkerError):
                supervisor.run([sys.executable, '-c', 'import time; time.sleep(5)'])
        finally:
            timer.cancel()
            supervisor.close()
        self.assertEqual(lease.releases, 1)

    def test_expired_handle_cannot_start_worker(self):
        lease = FakeLease()
        lease.valid = False
        supervisor = Supervisor(lease, interval=1)
        supervisor.start()
        try:
            with patch('scripts.worker_lease.subprocess.Popen') as popen:
                with self.assertRaises(WorkerError):
                    supervisor.run(['should-not-run'])
                popen.assert_not_called()
        finally:
            supervisor.close()
        self.assertEqual(lease.releases, 0)

    def test_cleanup_error_does_not_release_lease(self):
        lease = FakeLease()
        supervisor = Supervisor(lease, interval=1)
        supervisor.start()
        child = Mock(pid=12345)
        try:
            with patch('scripts.worker_lease.os.killpg', side_effect=PermissionError()):
                with self.assertRaises(WorkerError):
                    supervisor._terminate_group(child)
        finally:
            supervisor.close()
        self.assertEqual(lease.releases, 0)

    def test_namespace_override_is_rejected(self):
        with self.assertRaises(SystemExit):
            main(['--account', 'alternate', '--task', 'TASK-102',
                  '--branch', 'agent/example', '--', 'worker'])

    def test_lost_lease_kills_without_graceful_signal(self):
        lease = FakeLease()
        supervisor = Supervisor(lease, interval=1, grace=0.1)
        child = Mock(pid=12345)
        with patch('scripts.worker_lease.os.killpg', side_effect=[None, ProcessLookupError()]) as kill:
            supervisor._terminate_group(child)
        self.assertEqual(kill.call_args_list[0].args[1], __import__('signal').SIGKILL)

    def test_invalid_renewal_interval_is_rejected(self):
        with self.assertRaises(ValueError):
            Supervisor(FakeLease(), interval=60)


class ReconciliationTests(unittest.TestCase):
    def test_fetch_and_verified_guard_are_required(self):
        class Stub:
            def __init__(self, evidence, branch='agent/task'):
                self.evidence = evidence
                self.branch = branch
                self.commands = []
            def run(self, command, stdout=None, **kwargs):
                self.commands.append(command)
                if stdout is not None:
                    if command[:2] == ['git', 'branch']:
                        stdout.write(self.branch)
                    else:
                        json.dump(self.evidence, stdout)
                    stdout.flush()
                return 0
        good = Stub({'status': 'pass', 'claim_verified': True})
        reconcile(good, 'TASK-102', 'agent/task')
        self.assertEqual(good.commands[0], ['git', 'fetch', 'origin'])
        self.assertIn('TASK-102', good.commands[1])
        bad = Stub({'status': 'pass', 'claim_verified': False})
        with self.assertRaises(WorkerError):
            reconcile(bad, 'TASK-102', 'agent/task')
        changed = Stub({'status': 'pass', 'claim_verified': True}, branch='other')
        with self.assertRaises(WorkerError):
            reconcile(changed, 'TASK-102', 'agent/task')

    def test_fetch_failure_prevents_guard_and_worker(self):
        class Stub:
            def run(self, command, stdout=None, **kwargs):
                return 1
        with self.assertRaises(WorkerError):
            reconcile(Stub(), 'TASK-102', 'agent/task')


if __name__ == '__main__':
    unittest.main()
