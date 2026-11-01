# GitHub Actions OIDC bootstrap

This setup creates a separate Entra application and service principal for `dev`
and `test`. Each principal trusts only the `vkaam/phonebuddy` GitHub environment
subject and receives `Contributor` at its matching West Europe foundation
resource group. It creates no client secret. The identity cannot manage the
other environment or resources outside its resource group. Production is
intentionally excluded until its subscription and write scope are approved.

Identity creation is an Azure tenant and RBAC bootstrap exception. Review this
runbook and the change before applying it. The operator needs permission to
register applications in Entra and assign `Contributor` on the two resource
groups. Use the approved nonproduction subscription and a trusted workstation.
Do not run the applying command in CI or paste identifiers into repository
files, issues, or logs.

## Bootstrap

Install and authenticate Azure CLI, then check the selected account and
subscription before proceeding. The script defaults to a no-change dry run:

```sh
az login
az account show --query '{tenant:tenantId,subscription:id,state:state}' --output table
python3 scripts/bootstrap_github_oidc.py --environment dev --subscription-id <approved-subscription-id>
python3 scripts/bootstrap_github_oidc.py --environment test --subscription-id <approved-subscription-id>
```

After review, pass `--apply` once for each environment. The operation is
idempotent for the expected app, service principal, GitHub federation trust and
resource-group role assignment. It fails if duplicate app names or a different
existing federation trust are found. It never prints tenant, subscription,
application or principal IDs and does not create client credentials.

```sh
python3 scripts/bootstrap_github_oidc.py --environment dev --subscription-id <approved-subscription-id> --apply
python3 scripts/bootstrap_github_oidc.py --environment test --subscription-id <approved-subscription-id> --apply
```

The expected role scopes are exactly `rg-pb-dev-westeurope-foundation` and
`rg-pb-test-westeurope-foundation`. The federation subjects are
`repo:vkaam/phonebuddy:environment:dev` and
`repo:vkaam/phonebuddy:environment:test`; both use issuer
`https://token.actions.githubusercontent.com` and audience
`api://AzureADTokenExchange`.

## GitHub repository owner setup

In **Settings → Environments**, create environments named `dev` and `test`.
For each environment, restrict deployment branches to `main` and add these
environment secrets:

| Secret | Value |
| --- | --- |
| `AZURE_CLIENT_ID` | The matching app registration's application (client) ID |
| `AZURE_TENANT_ID` | The tenant ID from the selected Azure account |
| `AZURE_SUBSCRIPTION_ID` | The approved nonproduction subscription ID |

Find the client IDs by exact app name after bootstrap, and get the tenant ID
from the selected Azure account. Store each environment's own client ID in its
environment; the tenant and subscription values can be the same for both if
that matches the approved account. These IDs are identifiers rather than
passwords, but keeping them environment-scoped makes configuration explicit.
Never add a client secret or certificate.

## Verify

After the workflow and environment configuration are available on `main`, run
**Actions → Azure OIDC authorization smoke → Run workflow** once for `dev` and
once for `test`. Each run authenticates with its selected environment identity,
reads its own foundation resource group, and attempts a harmless empty ARM
deployment to the other environment. The workflow passes that probe only when
Azure returns `AuthorizationFailed`. The probe creates no Azure resources; if
an unexpectedly broad grant allows it, the workflow deletes its deployment
record and fails.

Also inspect role assignments and federated credentials in Azure before calling
the bootstrap complete. A PR or fork cannot invoke this workflow and the job
requires the protected `main` ref. GitHub environment branch restrictions and
the Entra environment subject provide independent checks. A successful smoke
run verifies identity and resource-group authorization only; it does not enable
automatic application deployment.
