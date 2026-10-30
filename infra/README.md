# Bicep foundation

This is a subscription-scoped starting point: each environment gets a distinct
foundation resource group and tags. It creates no application capacity, budgets,
identities, network, data, or secrets. It is not an enabled environment or a
proof of isolation. Follow the [environment policy](../docs/azure-delivery-policy.md)
for prerequisites and later deployment gates.

## Local verification

Use Bicep CLI **0.34.44**. For Linux x64 the official release binary is
`https://github.com/Azure/bicep/releases/download/v0.34.44/bicep-linux-x64`
with SHA-256 `dcc869edf53652303d4822b650d727419eeac33bce80cfb61f8ccc5cd2ccee47`.
Verify the digest before execution. Other platforms must install the same version
from the official release and verify their own published provenance. Run:

```sh
BICEP=/path/to/bicep python3 -B scripts/check_bicep.py
```

The check pins the reported version, lints and compiles the entry point, compiles
all three parameter files, verifies their environment values and confirms an
invalid environment fails compilation. It needs no Azure credentials. It does
not establish Azure deployment validity or resource isolation. PR CI integration
is tracked separately in TASK-7.

## Deployment and recovery prerequisites

The parameter files contain example geography and `UNRESOLVED` owner and cost
center values. They are not deployment-ready and do not automatically prevent a
deployment: replace them through reviewed configuration after confirming the
subscription, tenant, region, quota, budget, owners and access controls in the
policy. Never put secrets in parameter files or outputs. The intended target is
a subscription deployment using a separately scoped federated identity; confirm
the selected subscription explicitly, validate and review what-if first, then
deploy and repeat the exact deployment to demonstrate convergence. Record both
runs and resource state; this has not yet been tested.

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
