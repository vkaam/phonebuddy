import threading
from unittest.mock import Mock, patch
from urllib.error import HTTPError
import unittest

from scripts.task_lease import BlobStore, LeaseError, acquire, suspend_aware_time


class Clock:
    now = 0

    def __call__(self):
        return self.now


class Store:
    def __init__(self, clock):
        self.clock = clock
        self.lock = threading.Lock()
        self.records = {}
        self.leases = {}
        self.fail_renew = False

    def initialize(self, task):
        with self.lock:
            self.records.setdefault(task, {'generation': 0})

    def acquire(self, task, lease_id, duration):
        with self.lock:
            current = self.leases.get(task)
            if current and self.clock() < current[1]:
                raise LeaseError('contended')
            self.leases[task] = (lease_id, self.clock() + duration, duration)

    def read(self, task):
        with self.lock:
            return self.records[task].copy()

    def write(self, task, lease_id, value):
        with self.lock:
            if self.leases[task][0] != lease_id or self.clock() >= self.leases[task][1]:
                raise LeaseError('lost')
            self.records[task] = value.copy()

    def lease_action(self, task, lease_id, action):
        with self.lock:
            current = self.leases.get(task)
            if self.fail_renew or not current or current[0] != lease_id or self.clock() >= current[1]:
                raise LeaseError('lost')
            if action == 'renew':
                self.leases[task] = (lease_id, self.clock() + current[2], current[2])
            else:
                del self.leases[task]


class LeaseTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.store = Store(self.clock)

    def acquire(self):
        return acquire(self.store, 'TASK-101', duration=15, clock=self.clock)

    def test_contended_claim_and_generation_after_release(self):
        first = self.acquire()
        with self.assertRaises(LeaseError):
            self.acquire()
        first.release()
        second = self.acquire()
        self.assertEqual((first.generation, second.generation), (1, 2))

    def test_expiry_blocks_old_holder_and_recovers(self):
        first = self.acquire()
        self.clock.now = 15
        second = self.acquire()
        self.assertEqual(second.generation, 2)
        with self.assertRaises(LeaseError):
            first.renew()
        with self.assertRaises(LeaseError):
            first.release()

    def test_sleep_elapsed_invalidates_old_holder(self):
        lease = self.acquire()
        # The lease clock advances during suspend even if monotonic is frozen.
        with patch('scripts.task_lease.time.monotonic', return_value=0):
            self.clock.now = 16
            with self.assertRaises(LeaseError):
                lease.renew()
        self.assertFalse(lease.valid)

    def test_darwin_clock_uses_continuous_time(self):
        library = Mock()
        library.mach_continuous_time.return_value = 8_000_000_000
        def set_timebase(info):
            info._obj.numer = 1
            info._obj.denom = 1
            return 0
        library.mach_timebase_info.side_effect = set_timebase
        with patch('scripts.task_lease.sys.platform', 'darwin'), \
             patch('scripts.task_lease.ctypes.CDLL', return_value=library), \
             patch('scripts.task_lease.time.monotonic', return_value=0):
            self.assertEqual(suspend_aware_time(), 8)
            library.mach_continuous_time.assert_called_once()

    def test_platform_clock_is_available(self):
        self.assertGreaterEqual(suspend_aware_time(), 0)

    def test_renewal_failure_invalidates_holder(self):
        lease = self.acquire()
        self.store.fail_renew = True
        with self.assertRaises(LeaseError):
            lease.renew()
        self.store.fail_renew = False
        with self.assertRaises(LeaseError):
            lease.renew()

    def test_renewal_clock_failure_invalidates_handle(self):
        lease = self.acquire()
        lease.clock = Mock(side_effect=[0, LeaseError('clock unavailable')])
        with self.assertRaises(LeaseError):
            lease.renew()
        self.assertFalse(lease.valid)
        lease.clock = self.clock
        with self.assertRaises(LeaseError):
            lease.renew()

    def test_renewal_extends_deadline(self):
        lease = self.acquire()
        self.clock.now = 10
        lease.renew()
        self.clock.now = 16
        lease.release()

    def test_simultaneous_acquire_has_one_winner(self):
        barrier = threading.Barrier(2)
        results = []
        def contender():
            barrier.wait()
            try:
                results.append(self.acquire())
            except LeaseError:
                results.append(None)
        threads = [threading.Thread(target=contender) for _ in range(2)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(sum(value is not None for value in results), 1)

    def test_invalid_state_and_inputs_fail(self):
        self.store.records['TASK-101'] = {'generation': True}
        with self.assertRaises(LeaseError):
            self.acquire()
        with self.assertRaises(ValueError):
            acquire(self.store, '../other', clock=self.clock)
        with self.assertRaises(ValueError):
            acquire(self.store, 'TASK-101', duration=0, clock=self.clock)


class BlobStoreTests(unittest.TestCase):
    def test_existing_blob_is_not_overwritten(self):
        store = BlobStore('account123', 'task-leases', lambda: 'token')
        error = HTTPError('https://example.invalid', 409, 'exists', {'x-ms-error-code': 'BlobAlreadyExists'}, None)
        with patch('scripts.task_lease.urlopen', side_effect=error) as call:
            store.initialize('TASK-101')
        request = call.call_args.args[0]
        self.assertEqual(request.get_header('If-none-match'), '*')
        self.assertEqual(request.get_header('X-ms-blob-type'), 'BlockBlob')

    def test_unrelated_conflict_is_not_treated_as_existing_blob(self):
        store = BlobStore('account123', 'task-leases', lambda: 'token')
        error = HTTPError('https://example.invalid', 409, 'conflict', {'x-ms-error-code': 'LeaseAlreadyPresent'}, None)
        with patch('scripts.task_lease.urlopen', side_effect=error):
            with self.assertRaises(LeaseError):
                store.initialize('TASK-101')

    def test_storage_failure_is_not_treated_as_existing_blob(self):
        store = BlobStore('account123', 'task-leases', lambda: 'token')
        error = HTTPError('https://example.invalid', 403, 'forbidden', {}, None)
        with patch('scripts.task_lease.urlopen', side_effect=error):
            with self.assertRaises(LeaseError):
                store.initialize('TASK-101')

    def test_lease_id_not_printed(self):
        clock = Clock()
        lease = acquire(Store(clock), 'TASK-101', duration=15, clock=clock)
        self.assertNotIn(lease.lease_id, repr(lease))


if __name__ == '__main__':
    unittest.main()
