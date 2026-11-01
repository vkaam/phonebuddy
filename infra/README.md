# Bicep foundation

This subscription-scoped foundation gives each selected environment a distinct
deployment name and resource group (`phonebuddy-<environment>-foundation` and
`rg-pb-<environment>-foundation`) with an environment tag. The pinned local check
enforces those names and the single `resourceGroupName` output. This is a
foundation naming boundary, not proof of workload authorization, data, network,
or capacity isolation. The template creates no application capacity, budgets,
identities, network, data, or secrets. Follow the
[environment policy](../docs/azure-delivery-policy.md) for prerequisites and
later deployment gates.

The dev foundation is configured for the user-designated subscription in Sweden
Central and was deployed twice on 2026-11-01; the repeat what-if reported no
changes. It creates only `rg-pb-dev-foundation`. Test and production parameter
files remain unresolved and their deployment-readiness preflights fail until
their own subscription, region, owner, and cost center are approved.

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

The test and production parameter files contain `UNRESOLVED` geography, owner
and cost center values. They are not deployment-ready: replace them through
reviewed configuration after confirming the subscription, tenant, region, quota,
budget, owners and access controls in the policy. Never put secrets in parameter
files or outputs. The foundation output exposes only its resource-group name.
The intended target is a subscription deployment using a separately scoped
federated identity; confirm the selected subscription explicitly, then run the
preflight for the target:

```sh
BICEP=/path/to/bicep python3 -B scripts/check_bicep.py --deployment-ready dev
```

Substitute `test` or `prod` as appropriate. This rejects placeholders and a
mismatched environment, but it cannot verify Azure approvals, permissions, quota,
budget or geography. It is not automatically enforced by Azure or CI: the future
trusted deployment pipeline must invoke it and fail closed. For each approved
environment, validate and review what-if, deploy and repeat the exact deployment
to demonstrate convergence, then record both runs and resource state. The dev
foundation deployment and repeat have been verified; test and production have
not.

Resource groups use fixed names per environment. Distinct subscriptions or
resource groups alone are not authorization, data, network or capacity isolation;
future modules and RBAC must enforce and verify those boundaries. Keep capacity
and state independently scoped per environment. Azure subscription permissions,
federated identity bootstrap, budget setup, external DNS and Entra consent are
bootstrap exceptions and require documented, reviewed setup; no credentials are
created here.

For disposable testing use an explicitly designated nonproduction subscription
and unique test scope, with a named owner, budget and expiry. The fixed resource
group name makes parallel disposable deployments unsafe in the same subscription;
choose an isolated subscription before testing. Inspect locks, resource contents,
retention, backup and ownership before cleanup. Never delete production or shared
resources as part of a test. A deployment rollback does not delete resources
removed from a template; resource group deletion is destructive and must follow
the owner's approved cleanup procedure. Record what remains and any protected
resources instead of bypassing locks.
