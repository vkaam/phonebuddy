"""Azure Blob-backed task leases. Publishing must be fenced separately."""
import ctypes
import json
import sys
from email.utils import formatdate
import re
import time
import uuid
from dataclasses import dataclass, field
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


class LeaseError(RuntimeError):
    """Lease ownership cannot be established with certainty."""


def suspend_aware_time():
    """Elapsed seconds including system suspend; fail closed on unsupported hosts."""
    if sys.platform == 'darwin':
        class Timebase(ctypes.Structure):
            _fields_ = [('numer', ctypes.c_uint32), ('denom', ctypes.c_uint32)]
        try:
            lib = ctypes.CDLL('/usr/lib/libSystem.B.dylib')
            lib.mach_continuous_time.restype = ctypes.c_uint64
            info = Timebase()
            if lib.mach_timebase_info(ctypes.byref(info)) != 0 or not info.denom:
                raise LeaseError('suspend-aware clock unavailable')
            return lib.mach_continuous_time() * info.numer / info.denom / 1_000_000_000
        except (OSError, AttributeError) as error:
            raise LeaseError('suspend-aware clock unavailable') from error
    if hasattr(time, 'CLOCK_BOOTTIME'):
        return time.clock_gettime(time.CLOCK_BOOTTIME)
    raise LeaseError('suspend-aware clock unavailable')


class BlobError(LeaseError):
    def __init__(self, status, code):
        self.status = status
        self.code = code
        super().__init__(f"storage rejected operation ({status}, {code})")


class BlobStore:
    """Minimal Azure Blob REST adapter. Token provider must return an Entra token."""

    def __init__(self, account, container, token_provider, timeout=10):
        if not re.fullmatch(r"[a-z0-9]{3,24}", account):
            raise ValueError("invalid storage account")
        if not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{1,61}[a-z0-9])", container) or '--' in container:
            raise ValueError("invalid container")
        self.base = f"https://{account}.blob.core.windows.net/{container}/"
        self.token_provider = token_provider
        self.timeout = timeout

    def request(self, task, method, *, query='', headers=None, body=None):
        url = self.base + quote(task, safe='') + query
        request_headers = {'Authorization': 'Bearer ' + self.token_provider(),
                           'x-ms-version': '2023-11-03', 'x-ms-date': formatdate(usegmt=True)}
        request_headers.update(headers or {})
        try:
            with urlopen(Request(url, data=body, headers=request_headers, method=method), timeout=self.timeout) as response:
                return response.read(), response.headers
        except HTTPError as error:
            code = error.headers.get('x-ms-error-code', 'Unknown')
            raise BlobError(error.code, code) from None
        except (URLError, OSError, TimeoutError) as error:
            raise LeaseError("storage operation uncertain") from error

    def initialize(self, task):
        try:
            self.request(task, 'PUT', headers={'x-ms-blob-type': 'BlockBlob', 'If-None-Match': '*'}, body=b'{"generation":0}')
        except BlobError as error:
            if (error.status, error.code) not in {(409, 'BlobAlreadyExists'), (412, 'ConditionNotMet')}:
                raise

    def acquire(self, task, lease_id, duration):
        self.request(task, 'PUT', query='?comp=lease', headers={'x-ms-lease-action': 'acquire', 'x-ms-proposed-lease-id': lease_id, 'x-ms-lease-duration': str(duration)}, body=b'')

    def read(self, task):
        data, _ = self.request(task, 'GET')
        return json.loads(data)

    def write(self, task, lease_id, value):
        self.request(task, 'PUT', headers={'x-ms-blob-type': 'BlockBlob', 'x-ms-lease-id': lease_id}, body=json.dumps(value).encode())

    def lease_action(self, task, lease_id, action):
        self.request(task, 'PUT', query='?comp=lease', headers={'x-ms-lease-action': action, 'x-ms-lease-id': lease_id}, body=b'')


@dataclass
class Lease:
    store: BlobStore
    task: str
    lease_id: str = field(repr=False)
    generation: int
    duration: int
    deadline: float
    clock: object = suspend_aware_time
    valid: bool = True

    def _check(self):
        try:
            if not self.valid or self.clock() >= self.deadline:
                raise LeaseError('lease expired or ownership uncertain')
        except Exception:
            self.valid = False
            raise

    def renew(self):
        self._check()
        try:
            started = self.clock()
            self.store.lease_action(self.task, self.lease_id, 'renew')
            if self.clock() >= self.deadline:
                raise LeaseError('renewal completed after local deadline')
            self.deadline = started + self.duration
        except Exception:
            self.valid = False
            raise

    def release(self):
        self._check()
        self.valid = False
        self.store.lease_action(self.task, self.lease_id, 'release')


def acquire(store, task, duration=60, clock=suspend_aware_time):
    if not re.fullmatch(r'TASK-[1-9][0-9]*', task):
        raise ValueError('invalid task ID')
    if not isinstance(duration, int) or isinstance(duration, bool) or not 15 <= duration <= 60:
        raise ValueError('duration must be 15 to 60 seconds')
    store.initialize(task)
    lease_id = str(uuid.uuid4())
    started = clock()
    store.acquire(task, lease_id, duration)
    try:
        state = store.read(task)
        generation = state['generation']
        if type(generation) is not int or generation < 0:
            raise LeaseError('invalid generation record')
        generation += 1
        store.write(task, lease_id, {'generation': generation})
        if clock() >= started + duration:
            raise LeaseError('acquisition completed after local deadline')
        return Lease(store, task, lease_id, generation, duration, started + duration, clock)
    except Exception:
        # An uncertain acquisition is never handed to a caller; expiry recovers it.
        raise
