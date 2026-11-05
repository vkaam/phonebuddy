# Bicep foundation

This subscription-scoped foundation gives each selected environment and region a
distinct deployment name and resource group
(`phonebuddy-<environment>-<region>-foundation` and
`rg-pb-<environment>-<region>-foundation`) with environment, owner, service and
cost-center tags. The pinned local check
enforces those names and the single `resourceGroupName` output. This is a
foundation naming boundary, not proof of workload authorization, data, network,
or capacity isolation. The template creates no application capacity, budgets,
identities, network, data, or secrets. Follow the
[environment policy](../docs/azure-delivery-policy.md) for prerequisites and
later deployment gates.

The original dev foundation group, `rg-pb-dev-foundation`, is in Sweden Central
and was deployed twice on 2026-11-01; its repeat what-if reported no changes.
Azure does not allow changing a resource group's location after creation, so this
group is retained. Earlier dev/test data foundation attempts in West Europe
partially provisioned resources, but Azure rejected SQL server creation for
this subscription. Those resources remain in
`rg-pb-dev-westeurope-foundation` and `rg-pb-test-westeurope-foundation`; no
cleanup was performed. The owner then selected France Central for the current
dev/test foundation parameters after subscription SQL capability, resource
provider, and model capacity checks passed. Those parameters use owner
`PHONEBUDDY-PLATFORM` and cost center `PHONEBUDDY-NONPROD`. Existing dev hosting
remains in its West Europe group. Production remains unresolved.

Separate $10 USD monthly budgets `phonebuddy-dev-monthly-10usd` and
`phonebuddy-test-monthly-10usd` are configured at the MCA billing-account scope.
Each filters on its environment tag and `costCenter=PHONEBUDDY-NONPROD`, with
actual-spend alerts at 50%, 80% and 100%, plus a 100% forecast alert to the
environment owner. These are alerts, not spending caps. Cost Management does
not automatically inherit resource-group tags into usage records; future
billable resources must carry the environment and cost-center tags directly or
the billing profile must enable tag inheritance.

## Local verification

Use Bicep CLI **0.34.44**. For Linux x64 the official release binary is
`https://github.com/Azure/bicep/releases/download/v0.34.44/bicep-linux-x64`
with SHA-256 `dcc869edf53652303d4822b650d727419eeac33bce80cfb61f8ccc5cd2ccee47`.
Verify the digest before execution. Other platforms must install the same version
from the official release and verify their own published provenance. Run:

```sh
BICEP=/path/to/bicep python3 -B scripts/check_bicep.py
```

The check pins the reported version, lints and compiles the entry point and
foundation module, compiles all three parameter files, and verifies their
environment values. It confirms that deployment and resource-group names are
environment-specific, that the environment tag follows the selected parameter,
and that only the resource-group name is output. It also confirms an invalid
environment fails compilation. It needs no Azure credentials and does not prove
workload authorization, data, network or capacity isolation. PR CI integration
is tracked separately in TASK-7.

## Deployment and recovery prerequisites

The dev and test parameter files are configured for France Central, the approved subscription,
owner and nonproduction cost center. Production still contains unresolved inputs
and is not deployment-ready. Never put secrets in parameter files or outputs.
The foundation output exposes only its region-qualified resource-group name.
The intended target is a subscription deployment using a separately scoped
federated identity; confirm the selected subscription explicitly, then run the
preflight for the target:

```sh
BICEP=/path/to/bicep python3 -B scripts/check_bicep.py --deployment-ready dev
```

Substitute `test` or `prod` as appropriate. Dev and test must pass; prod fails
closed while its inputs remain unresolved. This rejects placeholders and a
mismatched environment, but it cannot verify Azure approvals, permissions, quota,
budget or geography. It is not automatically enforced by Azure or CI: the future
trusted deployment pipeline must invoke it and fail closed. For each approved
environment, validate and review what-if, deploy and repeat the exact deployment
to demonstrate convergence, then record both runs and resource state. The
original Sweden Central dev group has a successful repeated deployment and
no-change what-if. West Europe data deployments were partial; the current France
Central parameter values still need their own what-if and deployment evidence.
Production has not been deployed.

Resource groups use fixed names per environment and region. Distinct subscriptions or
resource groups alone are not authorization, data, network or capacity isolation;
future modules and RBAC must enforce and verify those boundaries. Keep capacity
and state independently scoped per environment. Azure subscription permissions,
federated identity bootstrap, budget setup, external DNS and Entra consent are
bootstrap exceptions and require documented, reviewed setup; no credentials are
created here.

For the reviewed dev/test GitHub Actions identity bootstrap and manual GitHub
environment setup, see [GitHub OIDC bootstrap](github-oidc.md).

For disposable testing use an explicitly designated nonproduction subscription
and unique test scope, with a named owner, budget and expiry. The fixed
environment-and-region resource group name makes parallel disposable deployments
unsafe in the same subscription; choose an isolated subscription before testing.
The existing Sweden Central dev group is not moved or deleted by this foundation.
Inspect locks, resource contents, retention, backup and ownership before cleanup.
Never delete production or shared
resources as part of a test. A deployment rollback does not delete resources
removed from a template; resource group deletion is destructive and must follow
the owner's approved cleanup procedure. Record what remains and any protected
resources instead of bypassing locks.

## Trusted dev hosting what-if

After the workflow is reviewed and merged, open **Actions → Dev hosting what-if → Run workflow** and select `main`. The
credentialed job runs only for that manual request on this repository's `main`,
after the latest Quality check for the exact commit passes; pull requests cannot
enter it. It uses the `dev`
environment and previews `infra/hosting.bicep` against
`rg-pb-dev-westeurope-foundation` with the release workload disabled. It does not
deploy resources or preview the subscription-scoped foundation template. The
job prints change counts without resource identifiers or property values; it does
not provide sufficient detail to approve deployment. Review a detailed preview
through an appropriately protected channel before deployment. A preview does not
authorize deployment. Incomplete, ignored or unsupported results fail.

Azure what-if can require the same permissions as deployment, including role
assignment permissions for the hosting template. The shared identity currently
has Contributor on dev and test foundation groups; that does not grant role
assignment permissions, and the job may fail until the owner reviews an
appropriate permission design. Do not grant privileges merely to make the job
green. TASK-58's post-merge follow-up must record the run, permission scope and
hosted PR/fork failure-boundary evidence; no live result is claimed here.

## Data, messaging and AI foundation

`infra/main.bicep` also deploys `modules/data-platform.bicep` into that
environment's foundation group. It provisions an Entra-only SQL serverless
database, private blob container with versioning and soft-delete, keyless
Service Bus queues, Speech, an Azure AI Foundry project and a pinned
`GlobalStandard` model deployment. A user-assigned workload identity receives
only the Blob Data Contributor, Service Bus sender/receiver, Speech User and
Cognitive Services OpenAI User roles required by the application. Resource
names and outputs contain identifiers and endpoints only; no credentials are
emitted.

Retention is environment-specific: SQL point-in-time recovery and blob/container
soft-delete use 7 days for dev, 14 for test and 35 for prod. Blob versions are
enabled. SQL backup redundancy is locally redundant in dev/test and zone
redundant in prod. Service Bus message TTL is 1, 7 and 30 days respectively;
the separate `foundation-smoke` queue has a one-day TTL and a delivery limit of
three for nonproduction probes. Production uses zone-redundant storage and
Premium Service Bus; dev/test use LRS storage and Standard Service Bus.

The checked-in parameter files leave the SQL administrator unresolved. Supply
the deploying Entra user's identifiers in process environment variables so
they do not enter source control or shell history, then run the readiness check:

```sh
export PHONEBUDDY_SQL_ADMIN_OBJECT_ID="$(az ad signed-in-user show --query id -o tsv)"
export PHONEBUDDY_SQL_ADMIN_LOGIN="$(az ad signed-in-user show --query displayName -o tsv)"
python3 -B scripts/check_bicep.py --deployment-ready dev
```

Use the signed-in Entra user's display name and object ID as the SQL
administrator; Azure accepts the display name or UPN for this administrator.
Pass these variables as `sqlAdminObjectId` and `sqlAdminLogin` parameter
overrides when creating the deployment. Production inputs remain unresolved for
later setup. Check the
exact model/version, Generally Available inference lifecycle, `GlobalStandard`
SKU, selected resource-region model catalog, available quota and requested deployment units
against Azure before preview/deploy:

```sh
python3 -B scripts/check_bicep.py --foundry-preflight dev --subscription-id <subscription-id>
```

The account and quota check use the selected resource geography. The approved
`GlobalStandard` SKU can process prompts and responses in any Azure region.
There is no automatic alternate-SKU or alternate-resource-region fallback.
Prod remains blocked until its geography, owner, cost center and SQL
administrator are approved and supplied. The model capacity API check is
evidence at preflight time, not a reservation; deployment can still fail if
capacity changes.

After an authorized dev/test deployment and RBAC propagation, run the synthetic
data-plane probes with the intended Entra identity:

```sh
python3 -B scripts/azure_foundations_smoke.py --environment dev --subscription-id <subscription-id>
```

The script writes and deletes one synthetic blob, verifies anonymous denial,
sends a synthetic Service Bus message and abandons it until the broker moves it
to the DLQ, then checks Speech synthesis and Foundry inference with both Entra
and unauthenticated requests. It only targets dev/test and prints statuses, not
tokens, response bodies or synthetic content. It requires the active identity
to have the data roles and outbound access to the resource endpoints. Record
successful output against the exact deployed source revision. The script was
not run as part of local source validation; no Azure deployment or live data
plane result is claimed.

Deletion must follow the approved environment owner procedure after checking
resource locks, SQL PITR window, blob versions/soft-delete, Service Bus DLQ and
retention, and any legal hold. Soft-delete and SQL backups provide recovery
windows, not an independent long-term archive or a substitute for a tested
restore. Keep all access keyless through Entra; do not create keys, SAS URLs,
secrets in parameter files, or credentials in deployment outputs. No backup
restore or deletion exercise is claimed until recorded from the authorized
environment.
