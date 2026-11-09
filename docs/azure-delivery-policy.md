# Azure environments and automatic delivery policy

This policy began as the implementation contract for TASK-4. The dev and test
foundation groups, scoped identities, and budget alerts below were read back in
the new subscription on 2026-11-09. Trusted dev/test OIDC runs passed on 2026-11-09; encrypted GitHub secret
values cannot be read back directly. Application deployment remains gated by the
separate delivery checks. Values and thresholds should be reviewed against real
traffic through a PR.

## Environment register

`dev` is the pilot development environment; `test` validates promotion separately;
`prod` is the production environment. Earlier nonproduction resources exist in
Sweden Central, West Europe and France Central; the new dev/test target is the
separate nonproduction subscription and tenant in Belgium Central. Existing
resources remain until separately reviewed for migration or cleanup.

| Environment | Subscription and geography | Naming and ownership | Budget and outstanding inputs |
| --- | --- | --- | --- |
| dev (pilot development) | Owner-designated new nonproduction subscription and tenant; Belgium Central (`belgiumcentral`). | `rg-pb-dev-belgiumcentral-foundation`; distinct dev deployment identity; owner tag `PHONEBUDDY-PLATFORM`, cost center `PHONEBUDDY-NONPROD`. | $10 monthly resource-group budget with 50/80/100% actual and 100% forecast alerts to the owner. |
| test | Same new nonproduction subscription and tenant; Belgium Central (`belgiumcentral`). | `rg-pb-test-belgiumcentral-foundation`; distinct test deployment identity; owner tag `PHONEBUDDY-PLATFORM`, cost center `PHONEBUDDY-NONPROD`. | Separate $10 monthly resource-group budget with the same alert routing. |
| prod | Dedicated subscription preferred; subscription ID and tenant unresolved. Approved EU geography and actual Speech/Foundry processing boundary require confirmation. | Proposed prefix `pb-prod`, resource groups `rg-pb-prod-<region>-<purpose>`; service, incident and budget owners not assigned. | Amount, currency, alert recipients and forecast threshold unresolved. |

The owner selected France Central on 2026-11-09 for the entire TASK-60 dev/test
workload in this new subscription: SQL, Blob Storage, Service Bus, Speech and
Foundry. Its parameter files create separate
`rg-pb-dev-francecentral-foundation` and
`rg-pb-test-francecentral-foundation` groups. Belgium Central foundation groups
remain unchanged. The Belgium group budgets do not cover France group spending. Separate
France-group monthly €10 budgets now send 50/80/100% actual and 100% forecast
alerts to the owner; they are alerts, not spending caps.
This explicit location decision follows the Cognitive Services and Foundry
preflight rejection of Belgium Central and does not permit automatic fallback.
The TASK-79 health pilot also targets the France Central dev group. Static Web
Apps is unavailable there for this subscription, so its hosting deployment
explicitly omits that unused resource; the synthetic Container App and its
monitoring resources stay in France Central. [Static Web Apps assets are globally
distributed](https://learn.microsoft.com/en-us/azure/static-web-apps/faq), so any later web-front-end residency decision
requires separate review.

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
EU inference. The owner selected Foundry `GlobalStandard`, which may process
prompts and responses in any Azure region; resource geography remains separately
configured and preflighted. An unresolved required input blocks enabling its
environment.

## Delivery order

1. Require a PR to protected `main`, independent agent review, applicable
   required CI and resolved blocking conversations before merge. Validate the
   task's scoped acceptance and review material infrastructure and migration
   effects in the PR. Merge early when these gates pass so default-branch
   CI/CD can run. PR jobs have no Azure deployment identity.
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

Merge completes the scoped Backlog task and its issue when all required task
PRs are merged. Release and health results remain separate operational facts.
If a post-merge gate fails, open a linked issue and native task for correction
and keep the failed release stopped or recovered under this policy.

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

### Health telemetry and pilot observation

The Azure release-test workload emits one structured event for each `/ready`, `/`
or unknown-route request. Events contain only the configured release version,
HTTP status and response duration. Request lines, client addresses, query strings,
request bodies, secrets and call content are excluded. Azure Monitor sends
container console and system logs to the environment's 30-day Log Analytics
workspace; queries are restricted to this synthetic health event.

After a 60-second warm-up, the manual dev/test health workflow probes `/ready`
and `/` for 10 consecutive minutes, with 10 requests in each one-minute sample.
It requires at least 100 responses, the expected version and readiness value on
every response, a server-error rate below 1% and p95 latency below 2 seconds in
each rolling five-minute window. Before recording the release annotation, the
workflow also queries the environment's Log Analytics workspace and requires at
least 100 health events matching the candidate version, with no unhealthy
responses. It polls for up to five minutes for Azure Monitor ingestion. Empty or
insufficient telemetry after that wait, unhealthy events, a failed query,
missing response, version mismatch, timeout or dependency outage fails closed.
The report distinguishes an unavailable dependency from an unhealthy service
response and records counts and timings without storing response bodies or target
URLs.

Azure Monitor evaluates missing health telemetry, server errors and p95 latency
every five minutes over a five-minute window. Log ingestion can take several
minutes, so an alert is an operational signal and the health workflow remains
the promotion gate. Alert rules create Azure Monitor alert state; notification
recipients and on-call routing are not configured until the environment owner
assigns approved contacts. Successful gates add a source-bound Application
Insights deployment annotation with environment, release version, commit and
workflow reference. The workflow only observes and annotates an existing dev or
test deployment; it does not deploy or promote resources.

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

## Data and AI resource controls

TASK-60's Bicep module provisions SQL Database, private Blob Storage, Service
Bus, Speech, and an Azure AI Foundry project and model deployment inside each
environment's region-specific foundation group. The environment settings use
7/14/35-day SQL point-in-time restore and blob/container soft-delete windows,
1/7/30-day Service Bus message TTLs, LRS/ZRS storage, Standard/Premium Service
Bus, and Foundry `GlobalStandard` model capacity of 10/20/50 units for
dev/test/prod. Production inputs remain unresolved and block deployment.

The owner explicitly selected `GlobalStandard` for `gpt-5-mini` on 2026-11-04.
This SKU may process prompts and responses in any Azure region. The account is
created in the configured resource region, and preflight checks that region's
model catalog and subscription capacity for the exact `GlobalStandard` SKU,
Generally Available lifecycle, unexpired inference and SKU lifecycle, and
valid capacity default/range. Missing or insufficient evidence fails closed;
the deployment does not automatically substitute another SKU, model, or
resource region. Capacity evidence is time-sensitive and does not reserve
quota. Repeat it immediately before a deployment preview, and treat an Azure
capacity rejection as a failed gate.

SQL and all cognitive and messaging data-plane access use Entra authentication;
SQL administrator object ID/login must be explicitly supplied. Blob public
access and Shared Key are disabled, Service Bus SAS/local auth and cognitive
account key auth are disabled, and workload access is granted through
environment-scoped managed identity roles. Never put credentials in Bicep
parameters, resource tags, logs, task evidence or outputs. Endpoint and resource
names may be recorded; tokens and payloads may not.

Before the environment is enabled, the data owner must approve retention,
restore and deletion procedures. SQL short-term backup and blob versioning and
soft-delete provide bounded recovery windows; they are not an independent
archive. Confirm any legal hold, SQL restore point, blob versions, Service Bus
DLQ, resource locks and owner before deletion. Validate a restore in an authorized
nonproduction scope and record its source revision, timestamp, result and data
owner. Never automatically reverse destructive migrations or delete a production
resource group.

The dev/test-only `scripts/azure_foundations_smoke.py` checks synthetic authorized
and unauthenticated access to Blob Storage, Service Bus, Speech and Foundry, and
exercises Service Bus DLQ delivery. Run it only after an authorized deployment
and RBAC propagation with the intended identity. It does not deploy resources,
use production data or grant permission to do either. The source implementation
does not count as live evidence: the exact deployed commit and probe result must
be recorded before the corresponding external gate passes.
