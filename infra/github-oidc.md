# GitHub Actions OIDC bootstrap

`dev` and `test` use distinct Entra applications and service principals in the
approved nonproduction tenant. Each application has exactly one GitHub Actions
federation for its matching environment in `vkaam/phonebuddy`, and receives
Contributor only on its own foundation resource group: France Central for dev,
Belgium Central for test until its workload migration is separately reviewed. Production
is excluded. The previous shared identity and West Europe groups are historical;
do not remove them as part of this bootstrap.

Review each application's complete trust, credentials, ownership, and Azure role
assignments before granting access. The script requires the application ID for
the selected environment, rejects any additional federation, and rejects roles
outside that environment's foundation group in the selected subscription. It
does not create or remove app registrations, service principals, or federation
trusts. Avoid storing account identifiers in repository files or logs.

## Bootstrap

Identity and role assignment changes require Azure tenant and RBAC bootstrap
review. Authenticate with Azure CLI and select the approved nonproduction
subscription. The operator needs role-assignment permissions on both groups.
The script defaults to a no-change dry run:

```sh
python3 scripts/bootstrap_github_oidc.py --environment dev --subscription-id <approved-subscription-id> --app-id <reviewed-dev-application-client-id>
python3 scripts/bootstrap_github_oidc.py --environment test --subscription-id <approved-subscription-id> --app-id <reviewed-test-application-client-id>
```

After review, run each command with `--apply`. The script checks the selected
application's single federation and direct/inherited assignments before creating
Contributor on the matching group. Verify both assignments again after use. It
creates no client secret.

The automatic dev image-delivery workflow also needs the dev application to
push images to the dev Azure Container Registry. `Contributor` on the resource
group does not grant ACR data-plane push access. After reviewing the exact dev
registry, grant the dev service principal the `AcrPush` role scoped to that
registry only. This is a one-time Azure RBAC bootstrap by an authorized owner;
the deployment workflow does not grant roles. The hosting Bicep template can
create the Container App pull role assignment during bootstrap, but routine CI
deployments set `managePullRoleAssignment=false` and therefore require no role
assignment write permission. Verify the registry scope and assignments after
bootstrap. Do not grant `Owner` or subscription-wide permissions for this path.

## GitHub repository owner setup

In **Settings → Environments**, restrict both `dev` and `test` to deployment
branch `main`. Each environment must have `AZURE_CLIENT_ID` (its own application
client ID), `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID` secrets. The tenant and
subscription are shared by these two nonproduction environments; the client IDs
must differ.
Never add a client secret or certificate. Verify the two existing federated
credentials use the GitHub Actions issuer, Azure token exchange audience and
repository-ID-qualified subjects, one per application.

For automatic deployment, the `dev` environment must be restricted to branch
`main` and have the dev application's three secrets configured. The identity
needs Contributor on `rg-pb-dev-francecentral-foundation` for the Bicep resource
deployment, plus the registry-scoped `AcrPush` role described above. The
workflow uses an immutable image artifact from the successful CI run and does
not rebuild in the Azure job. `test` remains an OIDC smoke-only environment;
this pilot does not deploy test resources.

## Verify

Inspect Azure federation and role assignments, including inherited permissions.
After the updated workflow is available on `main`, run **Azure OIDC authorization
smoke** for both `dev` and `test`. Each run must authenticate, read its own
foundation group in its configured region, and receive an authorization denial for the
other group. The workflow runs only on `main` and is not triggered by PRs;
GitHub branch restrictions and Entra federation provide additional boundaries.
Passing the smoke check does not prove write scope or enable application
deployment. Record both run URLs and Azure readback evidence.
