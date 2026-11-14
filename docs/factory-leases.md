# Factory task lease foundation

This is a storage foundation, not an authorization system for autonomous work.
A Blob lease protects the task's record; it cannot fence GitHub writes. Do not
use this component to authorize autonomous claims or publishing until a trusted
controller owns the GitHub credentials, validates each current lease generation
at the publishing boundary, and the effective GitHub permissions prevent workers
from bypassing that controller. Issue #127 tracks that remaining work.

## Infrastructure

Deploy `infra/factory-leases.bicep` separately into an approved factory resource
group with a globally unique account name and the object ID of the trusted
coordinator's service principal. The account disables shared keys and public
blob access. The coordinator receives Blob Data Contributor at the container
scope; workers must not receive this role or GitHub publishing credentials.
Provisioning the role requires suitable role-assignment permissions. Use Entra
access tokens for `https://storage.azure.com/`; do not place tokens in blobs,
logs, source control or command-line arguments.

The coordinator identity can delete blobs, break leases and rewrite generations.
It is therefore trusted: limit its access, protect its credentials, and audit
administrative actions. Never delete or restore a task blob to an older version:
that can repeat a generation. A recovery after deletion or account restoration
requires stopping all publishers and establishing a new, externally recorded
coordination epoch before resuming. Versioning and soft delete aid investigation;
they do not preserve monotonicity automatically. Protect the account from deletion.

## Lifecycle

Supply `BlobStore` a token provider callable and call `acquire(store, 'TASK-123')`.
The returned in-memory lease has a unique lease ID, a generation and a monotonic
local deadline. Renew well before the 15–60 second duration expires. Failed or
late renewal invalidates the handle; stop work that depends on ownership and
reconcile task, branch and PR state before reacquiring. Release when finished.
Lease IDs are credentials: do not expose them to workers or logs. A failed or
ambiguous acquisition is not granted to the caller; wait for expiry before retry.
Azure can delay a new acquisition after expiry; retry with bounded backoff.

Storage loss, token failure or ambiguous responses fail closed. Blob leases can
be broken by authorized principals and do not protect unrelated resources.
The implementation uses one primary account; disaster recovery and cross-region
failover need a separate epoch and controller protocol before activation.
