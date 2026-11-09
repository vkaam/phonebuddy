---
id: TASK-60
title: Issue 16 - Provision data messaging Speech and Foundry foundations
status: Done
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-09T19:06:00Z'
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
Approved revision: 2026-11-09T17:25:18Z; body SHA-256 3e38abfd66622238c1dbb33b2da50562ba17ec079d6c80dc047082bf79ef565d.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-16-1-product-service-foundations
Scope: infra/**; scripts/**; tests/**; docs/azure-delivery-policy.md; docs/quality-and-delivery.md; backlog/tasks/task-60 - Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py. In authorized test environments, run synthetic authorized/denied data-plane, queue dead-letter, Speech auth and Foundry inference checks; record quota, model, geography, retention and backup evidence. No production data is used.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
Owner authorization: On 2026-11-09 the owner selected whole dev/test France Central workload deployment, authorized scoped temporary data-plane roles for synthetic probes with removal afterward, and asked to make PR #84 mergeable. The approved issue body digest is unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Bicep provisions SQL, blob storage, Service Bus, Speech and Foundry project/model resources with environment-specific retention and capacity.
- [x] #2 Quota, model lifecycle and processing geography are validated; unavailable configurations fail without cross-geography fallback.
- [x] #3 Synthetic checks prove authorized data-plane access and denial of unauthorized access, queue dead-letter behavior, Speech authentication and Foundry inference.
- [x] #4 Backup, deletion and secret-handling requirements are documented and validated where applicable.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing Bicep foundation, environment parameters, validation scripts, tests and delivery guidance; confirm exact Azure resource and API contracts from primary documentation.
2. Add environment-scoped SQL, blob storage, Service Bus, Speech and Foundry project/model resources with explicit capacity, retention, identity and geography settings; reject unavailable or unresolved configurations without cross-geography fallback.
3. Extend deterministic preflight checks and focused tests for resource contracts, quota/model/geography failures, secret-safe outputs and environment isolation.
4. Add synthetic nonproduction probes for authorized and denied data access, queue dead-lettering, Speech authentication and Foundry inference; document backup, deletion and secret-handling evidence.
5. Run the required repository and Bicep checks, then gather authorized current-source Azure evidence where available; keep acceptance unchecked while any required external gate is unverified.

6. Use the owner-authorized alternate EU location for dev/test; verify subscription SQL capabilities, provider location support, and exact Foundry GlobalStandard catalog/quota before changing parameters or deploying; keep production unresolved.

7. Integrate the latest Belgium Central foundation branch into PR #84, preserve its workload definitions, validate the merged tree, and keep the PR draft while live data-plane and recovery gates remain outstanding.

8. Apply the owner-approved 2026-11-09 France Central location amendment for the entire dev/test workload in the new subscription; retain Belgium foundation resources, verify France SQL/provider/model capacity, perform exact-target what-if and live probes before proposing completion.
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

France Central dev deployment 2026-11-05: Azure accepted the region and provisioned non-SQL resources, then SQL administrator provisioning failed with InvalidParameterValue for the Login property. The runtime UPN is rejected by this subscription API call. Microsoft guidance permits either the Entra display name or UPN for a SQL Entra administrator; update the local procedure to supply the signed-in displayName and retry. No deletions were performed.

2026-11-09 mergeability update: integrated main after TASK-78 moved dev/test to Belgium Central in the new subscription. Resolved region and runbook conflicts in favor of the current target. Focused Bicep preflight tests (34) and pinned Bicep 0.34.44 baseline pass. Live workload deployment, data-plane probes, and recovery evidence remain pending; no Azure deployment was attempted in this mergeability update.

2026-11-09 new-subscription preflight: the signed-in account is in the approved new subscription/tenant and the dev/test Belgium Central groups contain no workload resources. The required Foundry preflight for both environments fails closed: Microsoft.CognitiveServices locations/models rejects belgiumcentral with NoRegisteredProviderFound; provider account locations also omit Belgium Central. No deployment was attempted. Read-only France Central preflight in the new subscription confirms gpt-5-mini 2025-08-07 GlobalStandard is GenerallyAvailable with 500 units available for a 20-unit request. Owner decision on an explicit Speech/Foundry location amendment is pending; TASK-60 acceptance remains unchecked.

Scope amendment approval: owner explicitly selected Move the whole dev/test workload to France Central in Codex on 2026-11-09; reported on https://github.com/vkaam/phonebuddy/issues/16#issuecomment-6746714927. This supersedes Belgium Central for TASK-60 workload deployments only; the approved acceptance and checks remain unchanged.

2026-11-09 new-subscription France Central execution: dev deployment phonebuddy-task60-dev-sqlfix-20261109 and test deployment phonebuddy-task60-test-france-20261109 both Succeeded. SQL server creation required inline Entra-only administrator properties; the child-admin sequence failed with InvalidParameterValue Login. The successful deployment readback showed each SQL database online or auto-paused on GP_S_Gen5 1 vCore, Local backup redundancy, Entra-only admin in the new tenant, dev/test PITR 7/14 days; Blob versioning and blob/container soft delete 7/14 days; Service Bus smoke queue TTL P1D, maxDeliveryCount 3, dead-lettering true; and gpt-5-mini 2025-08-07 GlobalStandard chat deployment Succeeded at 10/20 units. France-group €10 monthly budgets with owner email and actual 50/80/100% plus forecast 100% alerts were read back. Repeat what-if after deployment: 20 Deploy and one Azure-managed master DB Ignore per environment, zero Modify/Delete. Synthetic authorized/denied Blob, Service Bus dead-letter MaxDeliveryCountExceeded, Speech synthesis and Foundry inference checks all passed for dev and test using the PR proposed source. The signed-in tester received five temporary resource-scoped data roles per environment; all ten were deleted and a fresh assignment list confirmed zero remaining. Synthetic blobs and queue messages were deleted/consumed. Production was not touched. Bicep baseline and 35 focused tests passed; full hosted Quality is pending on the pushed PR head.

Recovery evidence 2026-11-09: dev SQL phonebuddy database exposed earliestRestoreDate 2026-11-09T18:00:02Z and Local backup redundancy. A controlled restore to temporary phonebuddy-restore-smoke at 18:30Z reached Online on GP_S_Gen5. The temporary database was deleted; post-delete list showed only original phonebuddy (Online) and master. Test 14-day PITR and both environments Blob versioning/7-14 day soft delete were read back. The restore proves dev SQL PITR service operation for an empty foundation database, not application row recovery. Backup, deletion and secret-handling limits are documented in infra/README.md. Independent agent read-only review found no code defect; requested durable live evidence and this recovery result before finalization.

PR #84 head 25b8b8440dce6282949afc8236788c13395a3f37: hosted Quality run 42679823223 and advisory Risk run 42679922389 both passed. Independent agent reviewed the final scope after the France Central and smoke changes, ran 35 focused tests plus diff check, and found no blocking code defect. Live TASK-60 consistency returned status pass and claim_verified true. All four task acceptance criteria now have source and Azure evidence; the remaining PR transition is finalization commit, refreshed head checks, and merge.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Provisioned the owner-approved dev/test Phonebuddy workload in France Central in the new subscription. Corrected Azure SQL server creation to set its Entra-only administrator inline. Both deployments succeeded; live readback confirmed SQL, Blob, Service Bus, Speech and pinned Foundry model settings. Four synthetic authorized/denied data-plane checks passed in each environment; all temporary tester roles were removed. A dev SQL point-in-time restore reached Online and the temporary database was deleted. Pinned Bicep baseline, 115 required Python tests, independent review, live consistency validation and hosted PR Quality passed. Production remains deferred; GlobalStandard inference can process outside France Central, and the restore did not test application rows.
<!-- SECTION:FINAL_SUMMARY:END -->
