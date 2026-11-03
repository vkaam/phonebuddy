# Pilot hosting and release-test workload

`infra/hosting.bicep` is a resource-group-scoped deployment, separate from the
subscription-scoped foundation. It creates billable resources. It does not run
automatically and must be reviewed before any live deployment. Select the approved
environment's foundation group and subscription explicitly. Do not use production
until its inputs and deployment are approved.

The first deployment uses `deployWorkload=false`. Build `infra/release-test`, tag
and push the image to the new registry using a separately authorized publishing
identity; registry admin credentials are disabled. Resolve the pushed digest,
then deploy the same template with `deployWorkload=true`, `image` set to the
registry's digest-qualified image and `releaseVersion` set to the expected build
identity. The pull identity has AcrPull on that registry only; allow for RBAC
propagation before deploying the app. Deployment role-assignment permissions and
registry-push permissions are separate prerequisites. Do not pass secrets as
parameters or environment variables. The template does not enforce that an image
parameter points to the intended registry or that its version matches the image:
the operator must verify both before deployment.

The public HTTPS endpoint exposes `/ready` and `/`, returning only readiness and
the configured version. The Static Web App has no application content until a
separate deployment publishes it. The vault uses Azure RBAC, soft delete and purge
protection, and disables public network access; no vault private endpoint or secret
access is configured here. The Container Apps environment uses Azure-managed
networking and public ingress; it does not establish private network isolation.
No runtime identity has secret access. Registry public networking remains enabled;
registry access requires authorization. Review inherited permissions and deployed
configuration rather than inferring the complete access boundary from the template.

Before an authorized deployment, validate location/SKU availability, quotas,
pricing, budget and role-assignment permissions; inspect what-if and record approval.
Deploy twice, verify the returned version and readiness over HTTPS, read back RBAC
and administrative settings, and record the resources, cost estimate and cleanup
boundary. Managed services and retained vaults may continue to incur costs. Purge
protection prevents immediate vault deletion. Never delete a shared resource group
or bypass locks; obtain explicit cleanup authorization and inspect dependencies,
retention and ownership first. Azure budget alerts do not cap spending.
