# Azure environments and automatic delivery policy

This is the implementation contract for TASK-4, not evidence that Azure resources,
GitHub protections, deployment jobs, or alerts exist. No environment is enabled
for deployment until its owner supplies the inputs below and the gates are built
and exercised. The values and thresholds here are initial pilot defaults to be
validated against real traffic and revised through a reviewed PR.

## Environment register

`dev` is the pilot development environment; `test` validates promotion separately;
`prod` is the production environment. No environment is currently provisioned.

| Environment | Subscription and geography | Naming and ownership | Budget and outstanding inputs |
| --- | --- | --- | --- |
| dev (pilot development) | Subscription ID and tenant unresolved; choose approved EU geography after service availability and quota checks. | Proposed prefix `pb-dev`, resource groups `rg-pb-dev-<region>-<purpose>`; pilot and technical owners not assigned. | Amount, currency, alert recipients and forecast threshold unresolved. |
| test | Subscription ID and tenant unresolved; same approved processing boundary as production, with service availability and quotas verified. | Proposed prefix `pb-test`, resource groups `rg-pb-test-<region>-<purpose>`; test and technical owners not assigned. | Amount, currency, alert recipients and forecast threshold unresolved. |
| prod | Dedicated subscription preferred; subscription ID and tenant unresolved. Approved EU geography and actual Speech/Foundry processing boundary require confirmation. | Proposed prefix `pb-prod`, resource groups `rg-pb-prod-<region>-<purpose>`; service, incident and budget owners not assigned. | Amount, currency, alert recipients and forecast threshold unresolved. |

Use distinct resource groups, data, secrets, workload identities, deployment
identities and access assignments for each environment, even if subscriptions
are shared. No production data or credentials in dev or test. Keep factory
resources separately scoped. Names are conventions, subject to each Azure
resource's length, character and global uniqueness rules; add a stable suffix
where needed. Tag resources with environment, service, owner and cost center
once those values are known. Before enabling each environment, record actual
subscription, region, owners, cost center, monthly budget and alert destinations;
configure Azure budget alerts at 50%, 80% and 100% of actual spend and a forecast
alert at 100%. Budgets alert; they do not guarantee a spending cap.

Other prerequisites include the tenant and RBAC model, supported browsers,
usage and concurrency, retention and recording policy, data residency, service
SKUs/quotas, DNS, and a responsible on-call contact. Validate service and model
availability and processing location rather than assuming an EU resource ensures
EU inference. An unresolved required input blocks enabling its environment.

## Delivery order

1. Require a PR to protected `main`, independent human review, required CI and
   resolved conversations before merge. Review material infrastructure and
   migration effects in the PR. PR jobs have no Azure deployment identity.
2. After a successful protected-main build, build once and bind immutable
   artifacts, configuration, migration version, provenance and scan results to
   that commit. Serialize releases so a later commit cannot overtake an earlier
   promotion; an incident stop prevents queued releases from proceeding.
3. In a trusted job, validate Bicep and parameters and run authenticated what-if
   for each target with its own least-privilege federated identity. Missing,
   failed, or unexpected material changes stop the release for investigation and
   a reviewed correction. What-if is not proof of a successful deployment.
4. Deploy dev, then test, then prod using the same artifact digests and each
   environment's approved configuration. Each stage must pass its deployment,
   migration, smoke and observation gates before the next begins. Promotion is
   automatic after merge; there is no routine manual production approval. An
   operator may stop the pipeline for an incident; resumption requires resolving
   the cause and a fresh successful gate, not bypassing it.
5. Record commit, artifacts, parameters, what-if, migration, gate results, times,
   deployment identity, and rollback outcome. No Azure deployment occurs from a
   PR or advisory workflow. Environment protections must enforce branch and
   identity restrictions without adding routine approval gates.

## Gates and recovery

These are minimum initial release gates, to be implemented for each applicable
component. A missing metric, insufficient samples, timeout or unavailable test is
unknown and fails closed. Do not substitute a green deployment command for health.
For components not deployed in a release, record why their gate is not applicable.

| Gate | Initial pass condition and window | Failure action |
| --- | --- | --- |
| Deployment and migrations | Deployment completes within its configured timeout; every migration succeeds and compatibility with the previous release is verified before traffic moves. | Stop promotion; keep or restore the last healthy application version only if schema compatibility is established. |
| Readiness and smoke | All required instances ready and all versioned smoke, authentication and organization-isolation checks pass. Run smoke checks once after deployment and again at the end of observation. | Stop promotion; withdraw the new version from traffic where supported. |
| Observation | Observe at least 10 consecutive minutes after readiness in each environment; all one-minute readiness samples must pass, with no critical alert or restart loop. | Stop promotion on any breach or missing sample. |
| Request health | During observation, at least 100 representative requests, including synthetic requests when traffic is low; server-error rate below 1% and p95 latency below 2 seconds per rolling five-minute window. | Stop promotion if either threshold is exceeded or sample count is insufficient. Synthetic traffic must exercise the deployed service, not just a static health endpoint. |
| Stateful and telephony components | Required queue, database and controlled call checks pass; no failed or stuck migration, dead-letter growth attributable to the release, or failed controlled call. Drain active calls and streaming sessions before replacing a gateway. | Stop promotion and preserve diagnostic evidence; do not force termination merely to meet the window. |

These thresholds are provisional release controls, not established service-level
objectives. Component owners must define representative checks and alert queries
before enabling the component; tests and metrics must identify the candidate
version. Evaluate production before completing its rollout as well as earlier
stages. Changes to thresholds require reviewed evidence.

On a failed first release there is no previous healthy artifact: stop, keep the
service unavailable or isolated, alert the incident owner, and investigate; do
not claim rollback succeeded. On later releases, the deployment automation stops
promotion and attempts to return traffic to the last known healthy artifact only
when the migration and state are compatible and the rollback path has been
validated. Otherwise isolate the affected service and escalate. Never automatically
reverse destructive migrations or restore a database over newer data. Preserve
queues, backups and evidence; a data owner decides recovery using the applicable
restore and replay runbook. Re-run health gates after any recovery before resuming.

The deployment operator owns stopping and investigating a failed release; the
service incident owner coordinates response and communications; the data owner
authorizes stateful recovery; and the budget owner responds to cost alerts. Named
people or on-call rotations and escalation contacts are prerequisites for enabling
each environment. TASK-10 through TASK-13 implement and exercise these controls;
until then automatic delivery is not enabled.
