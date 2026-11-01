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
group is retained. The approved West Europe dev and test foundations use
`rg-pb-dev-westeurope-foundation` and `rg-pb-test-westeurope-foundation` in
the user-designated subscription; their parameter files use owner
`PHONEBUDDY-PLATFORM` and cost center `PHONEBUDDY-NONPROD`. These resource groups
deployed successfully twice on 2026-11-01; the second what-if for each reported
no changes. They contain no application capacity. Production remains unresolved.

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

The test parameter file is configured for West Europe, the approved subscription,
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
original Sweden Central dev group and the new West Europe dev/test groups have
all been deployed and verified with repeat what-if checks; production has not.

Resource groups use fixed names per environment and region. Distinct subscriptions or
resource groups alone are not authorization, data, network or capacity isolation;
future modules and RBAC must enforce and verify those boundaries. Keep capacity
and state independently scoped per environment. Azure subscription permissions,
federated identity bootstrap, budget setup, external DNS and Entra consent are
bootstrap exceptions and require documented, reviewed setup; no credentials are
created here.

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
