---
id: TASK-60
title: Issue 16 - Provision data messaging Speech and Foundry foundations
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-05T19:03:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-57
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/16
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - infra/environments/prod.bicepparam
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
  - infra/modules/data-platform.bicep
  - scripts/azure_foundations_smoke.py
  - infra/README.md
  - https://github.com/vkaam/phonebuddy/pull/84
modified_files:
  - >-
    backlog/tasks/task-60 -
    Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md
  - infra/modules/data-platform.bicep
  - infra/main.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - infra/environments/prod.bicepparam
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - scripts/azure_foundations_smoke.py
  - infra/README.md
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/16
Approved revision: 2026-11-01T09:24:52Z; body SHA-256 3e38abfd66622238c1dbb33b2da50562ba17ec079d6c80dc047082bf79ef565d.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-16-1-product-service-foundations
Scope: infra/**; scripts/**; tests/**; docs/azure-delivery-policy.md; docs/quality-and-delivery.md; backlog/tasks/task-60 - Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py. In authorized test environments, run synthetic authorized/denied data-plane, queue dead-letter, Speech auth and Foundry inference checks; record quota, model, geography, retention and backup evidence. No production data is used.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bicep provisions SQL, blob storage, Service Bus, Speech and Foundry project/model resources with environment-specific retention and capacity.
- [ ] #2 Quota, model lifecycle and processing geography are validated; unavailable configurations fail without cross-geography fallback.
- [ ] #3 Synthetic checks prove authorized data-plane access and denial of unauthorized access, queue dead-letter behavior, Speech authentication and Foundry inference.
- [ ] #4 Backup, deletion and secret-handling requirements are documented and validated where applicable.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing Bicep foundation, environment parameters, validation scripts, tests and delivery guidance; confirm exact Azure resource and API contracts from primary documentation.
2. Add environment-scoped SQL, blob storage, Service Bus, Speech and Foundry project/model resources with explicit capacity, retention, identity and geography settings; reject unavailable or unresolved configurations without cross-geography fallback.
3. Extend deterministic preflight checks and focused tests for resource contracts, quota/model/geography failures, secret-safe outputs and environment isolation.
4. Add synthetic nonproduction probes for authorized and denied data access, queue dead-lettering, Speech authentication and Foundry inference; document backup, deletion and secret-handling evidence.
5. Run the required repository and Bicep checks, then gather authorized current-source Azure evidence where available; keep acceptance unchecked while any required external gate is unverified.

6. Use the owner-authorized alternate EU location for dev/test; verify subscription SQL capabilities, provider location support, and exact Foundry GlobalStandard catalog/quota before changing parameters or deploying; keep production unresolved.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Owner direction 2026-11-04: pin gpt-5-mini to GlobalStandard. This SKU can process prompts and responses in any Azure region; account/model catalog and quota checks remain tied to the configured resource region, with no automatic SKU, model, or resource-region fallback. Production setup is deferred by the owner.

Read-only Azure preflight on 2026-11-04 passed in West Europe: dev requested 10 GlobalStandard units and test requested 20; both returned 500 available units. Production remains unresolved and unpreflighted by design.

The owner designated their Entra account as dev/test SQL administrator. Its identifiers are intentionally supplied at runtime and omitted from repository task notes and tracked parameter files. Production SQL administrator inputs remain unresolved. No Azure resources were deployed.

Local validation before the runtime-override change: full `python3 -B scripts/check.py` passed with report `/private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-kefhuqkv/report.json`; 25 focused tests passed; pinned Bicep baseline and dev/test deployment readiness passed; `git diff --check` passed. Latest hosted Quality pass remains run 41779641622 on head 198ac649b861456b9bc3caa8a65752c93edbf838. Acceptance remains unchecked pending authorized nonproduction deployment, live data-plane smoke, and backup/restore/deletion evidence.

Modified files: backlog/tasks/task-60 - Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md, infra/modules/data-platform.bicep, infra/main.bicep, infra/environments/dev.bicepparam, infra/environments/test.bicepparam, infra/environments/prod.bicepparam, scripts/check_bicep.py, tests/test_bicep_preflight.py, scripts/azure_foundations_smoke.py, infra/README.md, docs/azure-delivery-policy.md, docs/quality-and-delivery.md

Runtime SQL administrator handling: dev/test parameter files remain `UNRESOLVED` in source control. `scripts/check_bicep.py --deployment-ready` now accepts `PHONEBUDDY_SQL_ADMIN_OBJECT_ID` and `PHONEBUDDY_SQL_ADMIN_LOGIN` from the process environment, and fails closed if either is absent. The README shows how the signed-in Entra user can provide these values for a local readiness check and deployment override. Exact identifiers are omitted from task notes and tracked parameter files.

Validation after this change: 27 focused Foundry/data-platform tests passed; pinned Bicep baseline passed; dev/test readiness passed using the current signed-in identity via temporary process environment variables; `git diff --check` passed. No Azure deployment was run.

Post-merge validation: `python3 -B scripts/check.py` passed with report `/private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-xxyc03pe/report.json`. Live TASK-60 claim validation passed against updated `origin/main` (`6ce96012526ec1790d631361b86688cd64d25903`) with `claim_verified: true`. Bicep deployment readiness passed for dev and test using runtime-only values from the current signed-in Entra identity. The repository is now up to date with TASK-61 on main.

Authorized nonproduction deployment attempt 2026-11-04: the initial dev subscription deployment name collided with the foundation module deployment name and failed before child resources were applied. Retrying with a distinct root name partially provisioned dev. Service Bus, blob storage, workload identity, Speech/Foundry accounts, the GlobalStandard model deployment, and role assignments succeeded; SQL server creation failed with Azure `RegionDoesNotAllowProvisioning` because West Europe is not accepting new SQL Database servers. Foundry project creation also failed with `RequestConflict` while project and model child writes ran concurrently. Existing hosting resources were unchanged. No deletes were attempted.

Test deployment was not attempted after the same West Europe SQL creation failure made it predictably partial. Production remains deferred. Added an explicit project-before-model dependency to serialize Foundry child writes for the next deployment attempt. No acceptance criteria are checked until all required nonproduction resources and smoke/recovery evidence pass.

Independent read-only review of the Foundry sequencing fix found no actionable issues; reviewer confirmed the compiled model dependency targets `Microsoft.CognitiveServices/accounts/projects`. Its effect still needs verification in Azure because the dev deployment was blocked by West Europe SQL server creation.

Post-merge validation after the sequencing fix: Bicep baseline passed; 30 focused tests passed; full `python3 -B scripts/check.py` passed with report `/private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-0c8tpoiw/report.json`; `git diff --check` passed. These checks were run after merging main commit `ec7368c`.

Post-fix Azure deployment retries 2026-11-04: the user explicitly authorized dev and test. Retried dev with the Foundry project-before-model dependency, then attempted test; both deployments partially provisioned the non-SQL foundations and both failed SQL server creation with Azure RegionDoesNotAllowProvisioning because West Europe is not accepting new SQL Database servers. Dev Foundry project/model provisioning completed without the earlier write conflict. No resources were deleted. Hosted PR Quality workflow 41797061702 passed for head 7e5dd6bdf03dd0312cb4411883ea9a031fdd4536. Acceptance remains unchecked pending full environment provisioning, synthetic data-plane evidence, and backup/restore/deletion validation.

Owner direction 2026-11-05: move dev and test from West Europe to an EU region available for this subscription, while keeping production deferred. Microsoft.Sql provider is already Registered. SQL subscription capabilities report France Central, Sweden Central, and Germany West Central as Available; West and North Europe are only Visible. Storage, Service Bus, and Cognitive Services provider metadata list France Central. Direct Foundry preflight in France Central passed dev=10 and test=20 GlobalStandard units for gpt-5-mini 2025-08-07, GenerallyAvailable, with 470 units reported available. France Central is selected for the approved dev/test retry.

France Central validation 2026-11-05: Microsoft.Sql subscription capabilities report Available; SQL provider is Registered; Storage, Service Bus and Cognitive Services metadata list the region. Repository Foundry preflight reads each environment parameter file and passed dev=10/test=20 GlobalStandard units for gpt-5-mini 2025-08-07, GenerallyAvailable, with 470 available units. Read-only ARM What-If passed for both new France Central foundation groups: 22 Creates each, 0 Modify, 0 Delete, 0 NoChange, 0 Ignore. Both deployment-readiness checks passed with runtime-only SQL admin overrides. 34 focused tests, pinned Bicep baseline and full scripts/check.py passed; local report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-dd7l4c7q/report.json.

Independent read-only review of the France Central region change, parameter-driven preflight and smoke harness found no actionable issues. Reviewer confirmed the smoke harness follows the configured region and no longer uses SQL as the resource-group locator for Speech/Foundry. Live deployment, data-plane probes, and backup/restore/deletion remain external acceptance gates.
<!-- SECTION:NOTES:END -->
