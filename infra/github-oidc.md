# GitHub Actions OIDC bootstrap

The owner approved one shared Entra application and service principal for `dev`
and `test`. Its GitHub Actions federation is limited to the two environments of
`vkaam/phonebuddy`. It receives Contributor separately on the dev and test West
Europe foundation resource groups. **Either environment can access both resource
groups:** the federation credentials authenticate the same Azure identity and do
not isolate its Azure permissions. Production is excluded.

The existing application is shared with other uses; review its complete trust,
credentials, ownership, and all current Azure role assignments before granting it
additional access. The script requires an explicit application ID and rejects any
federated trust beyond the two approved repository-ID-qualified subjects. It does
not create or remove app registrations, service principals, or federation trusts.
Avoid storing identifiers in repository files or logs.

## Bootstrap

Identity and role assignment changes require Azure tenant and RBAC bootstrap
review. Authenticate with Azure CLI and select the approved nonproduction
subscription. The operator needs role-assignment permissions on both groups.
The script defaults to a no-change dry run:

```sh
python3 scripts/bootstrap_github_oidc.py --environment dev --subscription-id <approved-subscription-id> --app-id <reviewed-application-client-id>
python3 scripts/bootstrap_github_oidc.py --environment test --subscription-id <approved-subscription-id> --app-id <reviewed-application-client-id>
```

After review, run each command with `--apply`. The script checks both federation
trusts before assigning Contributor on the selected foundation resource group.
It does not prove that other assignments do not exist; inspect all direct and
inherited role assignments before and after use. It creates no client secret.

## GitHub repository owner setup

In **Settings → Environments**, restrict both `dev` and `test` to deployment
branch `main`. Each environment must have `AZURE_CLIENT_ID` (the same shared
application client ID), `AZURE_TENANT_ID` and `AZURE_SUBSCRIPTION_ID` secrets.
Never add a client secret or certificate. Verify the two existing federated
credentials use the GitHub Actions issuer, Azure token exchange audience and
repository-ID-qualified dev/test environment subjects.

## Verify

Inspect Azure federation and role assignments, including inherited permissions.
After the workflow is available on `main`, run **Azure OIDC authorization smoke**
for both `dev` and `test`. Each run authenticates and reads both foundation
resource groups, confirming the deliberately shared access. The workflow runs
only on `main` and is not triggered by PRs; GitHub branch restrictions and Entra
federation provide additional boundaries. Passing the smoke check does not prove
write scope or enable application deployment. Record the two run URLs and Azure
readback evidence before marking acceptance complete.
