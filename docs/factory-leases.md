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
scope. Cooperative workers need separately authorized container access; unlike a
trusted controller, they can break leases and alter records. Do not grant them
GitHub publishing credentials for an enforced boundary. Provisioning the role requires suitable role-assignment permissions. Use Entra
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
The returned in-memory lease has a unique lease ID, a generation and a suspend-aware
local deadline (macOS continuous time or Linux boot time); unsupported hosts fail closed. Renew well before the 15–60 second duration expires. Failed or
late renewal invalidates the handle; stop work that depends on ownership and
reconcile task, branch and PR state before reacquiring. Release when finished.
Lease IDs are credentials: do not expose them to workers or logs. A failed or
ambiguous acquisition is not granted to the caller; wait for expiry before retry.
Azure can delay a new acquisition after expiry; retry with bounded backoff.

Storage loss, token failure or ambiguous responses fail closed. Blob leases can
be broken by authorized principals and do not protect unrelated resources.
The implementation uses one primary account; disaster recovery and cross-region
failover need a separate epoch and controller protocol before activation.

## Cooperative worker wrapper

A worker with explicitly authorized Blob Data Contributor access to the private
container and a current Azure CLI login can run a command under a task lease:

```sh
python3 -B scripts/worker_lease.py --task TASK-123 \
  --branch agent/example -- worker-command arg
```

The wrapper uses the single approved `pbphonebuddyleases` / `task-leases`
namespace; it does not accept an alternate account or container. Run from the
task's checkout on its approved branch. The wrapper acquires a
60-second lease, renews it every 20 seconds, fetches `origin`, and requires the
live Backlog guard to reconcile the task, branch, issue and PR before starting
the command. It needs the GitHub CLI's read access for that guard. A takeover
uses the same command after the prior lease expires; do not bypass reconciliation.
The fetch and guard have bounded timeouts; a hung preflight stops without
starting work. The wrapper terminates remaining members of the child process
group before releasing a confirmed lease after normal exit or handled shutdown.
If the host cannot confirm the group is gone (including permission errors), the
wrapper exits with an error and leaves the lease to expire, even if the direct
command completed. Group termination is abrupt to avoid work after lease loss.
On renewal failure, expiry, uncertain ownership or shutdown it stops the child
process group and exits nonzero. It does not release a lease it cannot confirm.
The lease expires if the wrapper or host crashes. An uncatchable wrapper crash
may leave a child running; process-group cleanup cannot run in that case.

This mechanism is cooperative. It cannot stop work outside its child process
group, a process that escapes that group, or a worker that ignores the wrapper;
it does not revoke GitHub credentials or fence in-flight GitHub operations. A
worker must not publish outside this supervised command and must stop if it
cannot confirm the lease. Do not interpret this as the trusted publishing
controller or authorization for unattended publishing. Restrict and audit
storage access: a Blob Data Contributor can break leases or alter generations.
