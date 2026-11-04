---
id: TASK-61
title: Issue 17 - Add deployment health gates and observability
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-04T05:36:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/17
  - infra/hosting.bicep
  - infra/release-test/server.py
  - scripts/check_bicep.py
  - .github/workflows/azure-hosting-what-if.yml
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
  - tests/test_bicep_ci_boundary.py
  - tests/test_release_test.py
  - scripts/release_annotation.py
  - .github/workflows/azure-health-gate.yml
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - tests/test_release_annotation.py
modified_files:
  - >-
    backlog/tasks/task-61 -
    Issue-17-Add-deployment-health-gates-and-observability.md
  - infra/release-test/server.py
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - tests/test_release_test.py
  - infra/hosting.bicep
  - scripts/check_bicep.py
  - scripts/release_annotation.py
  - .github/workflows/azure-health-gate.yml
  - tests/test_bicep_ci_boundary.py
  - tests/test_release_annotation.py
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/17
Approved revision: 2026-11-01T09:24:54Z; body SHA-256 8d4a38d23215c8706bc19f086c585b9ebcafe76dfe747de51edbbbd35951d749.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-17-1-deployment-health-gates
Scope: infra/**; .github/workflows/**; scripts/**; tests/**; docs/quality-and-delivery.md; docs/azure-delivery-policy.md; backlog/tasks/task-61 - Issue-17-Add-deployment-health-gates-and-observability.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted pilot runs inject unhealthy responses and missing telemetry, confirm alerts/failure evidence, and confirm healthy version/readiness passes after warm-up.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Telemetry, release annotations and alerts are provisioned in Bicep without logging secrets or call content.
- [ ] #2 Bounded readiness and smoke checks verify the deployed version and essential paths after warm-up.
- [ ] #3 Document error and latency thresholds and observation windows; missing telemetry blocks promotion and dependency outages are distinguishable.
- [ ] #4 Injected unhealthy responses and missing telemetry trigger failure evidence and alerts; healthy workloads pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend the release-test workload with structured, bounded health telemetry that records only synthetic health events, response status, duration, and configured release version; never log request bodies, query strings, secrets, or call content.
2. Extend the hosting Bicep template with workspace-backed diagnostics, release metadata, and Azure Monitor alerts for missing telemetry, unhealthy responses, and latency, preserving opt-in workload creation and requiring no notification recipient until an owner configures one.
3. Add a bounded smoke/observation runner that waits for warm-up, verifies the expected version and required routes, checks sample count, 5-minute error rate and p95 latency over the documented 10-minute window, and fails closed on missing data or dependency outages.
4. Add a manually dispatched, read-only hosted workflow and deterministic tests for healthy, unhealthy, missing-telemetry, and dependency-outage cases.
5. Update delivery docs with thresholds, observation windows, alert semantics, and prerequisites; run the task verification commands and record which hosted Azure gates remain outstanding.

6. After HTTP observation, require at least 100 version-matched health events in the dev/test Log Analytics workspace and no unhealthy events; fail closed on empty telemetry or query/dependency failure before writing the release annotation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented structured health telemetry that excludes request lines, client addresses, query strings and bodies; added 30-day Log Analytics, Application Insights, Container Apps diagnostics, and Azure Monitor rules for missing telemetry, non-200 health responses, and p95 latency. Added the 60-second warm-up/10-minute dev-test gate, source-bound deployment annotations, and a manual main-only workflow that observes an existing deployment without deploying it. Live Backlog claim validation passed with claim_verified=true against origin/main; TASK-59 is completed. Verification on the implementation source: full local baseline passed (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-rwk2dj6b/report.json); pinned Bicep 0.34.44 validation passed; actionlint passed on all five workflows. The required hosted Azure checks have not run: the task's recorded approval explicitly excludes deployment, and no release-test workload has been deployed. No Azure resource was changed.

Draft PR #82: https://github.com/vkaam/phonebuddy/pull/82 at head 37656a7d19db0f1b9fb71645e8bb60cd50154eac. PR is draft while hosted Azure alert-injection and healthy-release evidence remain outstanding; no task acceptance criteria are checked and no Azure resources were changed.

User explicitly authorized dev/test deployment and alert drill in Codex on 2026-11-03. Selected existing dev target rg-pb-dev-westeurope-foundation in West Europe after account and tag verification; the group was empty. Local deployment-ready preflight passed and the read-only hosting what-if succeeded with 9 Create, 0 Modify, 0 NoChange, no diagnostics, using deployWorkload=false. Preflight reviewed current Microsoft pricing: Basic Container Registry is /bin/zsh.1666/day (~.07 per 30.4 days); the registry, monitoring ingestion/alerts, and active workload add metered charges. The documented dev monthly budget is  and is an alert, not a spending cap. No resources deployed yet.

Correction and status update for the preceding note: zsh expanded dollar signs in the recorded text. The accurate Basic Container Registry retail price is 0.1666 USD/day, about 5.07 USD per 30.4 days. The dev monthly budget is 10 USD and is an alert, not a spending cap. The bootstrap deployment succeeded and created nine resources. ACR Tasks are blocked by subscription policy, so the image was built locally and pushed. The first workload deployment failed because the image was ARM64. The corrected amd64 deployment then failed because Azure rejected ContainerAppConsoleLogs on the Container App-level diagnostic setting; Microsoft documents this category at the managed environment level. The app and alerts are not yet successfully provisioned; no alert drill has run.

Azure deployment diagnostics: the first workload attempt failed because the pushed image index had no linux/amd64 child. The corrected amd64 image deployed to ACR; the next attempt reported ContainerAppConsoleLogs unsupported at the Container App diagnostic-settings scope. Updated infra/hosting.bicep to route console and system logs through the Container Apps managed-environment diagnostic setting and keep only AllMetrics at app scope; scripts/check_bicep.py now enforces this documented Azure scope. Local validation and a new deployment preview are pending.

Validation after the managed-environment diagnostics fix: pinned Bicep 0.34.44 check passed; full scripts/check.py baseline passed (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-di10vjh0/report.json); actionlint passed on all five workflows. The Bicep scope change is not deployed yet; hosted alerts and healthy gate remain outstanding pending commit, PR checks, and retry.

Live dev state update: after the failed ARM deployment response, ARM operations show the Container App revision succeeded and all three scheduled query alerts exist. GET /ready and GET / both returned ready=true, version 8c420b3e2f6dc8fa925db5361ecda10d0c70ef9d. The rejected app-level diagnostic setting still needs replacement by the corrected managed-environment log setting; telemetry and alert drills have not run. Application Insights Smart Detection action group exists with zero email and zero role receivers. The corrected Bicep/checker/test changes are locally validated and pushed CI is still pending.

Evidence correction: GitHub Quality and Risk report passed on commit 9adc3c9 before the narrow Ignore-validator change; that validator/test change is not yet pushed. The actual ARM what-if validator accepted the corrected preview with 1 Create, 7 Modify, 6 NoChange, and one Ignore for only the Azure-managed Smart Detection action group. The action group has zero receivers. The required Python suite now passes all 88 tests with loopback access, and pinned Bicep validation passes. Live /ready and / returned version 8c420b3e2f6dc8fa925db5361ecda10d0c70ef9d. Current full quality baseline is rerunning after the final task-note correction.

Final candidate validation: python3 -B scripts/check.py passed with report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-ogz2jhx2/report.json. The candidate includes the narrow Smart Detection Ignore handling and test; current PR checks on 9adc3c9 predate that last change and must be rerun after push.

Implementation update (2026-11-04): the Azure health workflow now queries the selected dev/test Log Analytics workspace after HTTP observation, requires at least 100 health_request events matching the candidate release version and zero non-200 events, polls for up to five minutes for ingestion, and blocks annotations on missing records or query/dependency failures. Alert and gate KQL now parse the JSON payload after Azure’s timestamp prefix. Added tests for the CLI result shape, query failures, unhealthy events, value escaping, and bounded ingestion polling.

Validation: python3 -B scripts/check.py passed (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-hy_t0prt/report.json); pinned Bicep 0.34.44 baseline passed; actionlint passed on all five workflows; 13 focused health-gate/Bicep-boundary tests passed.

The user asked to skip further live Azure telemetry validation and keep the deployed state as-is. No additional Azure deployment or alert verification was performed after that direction. The dev app remains deployed and previously returned ready=true at version 8c420b3e2f6dc8fa925db5361ecda10d0c70ef9d. Workspace ingestion and unhealthy-alert firing remain unverified; no acceptance criteria are checked and TASK-61 remains In Progress.

Hosted CI on 4843ba5 caught actionlint ShellCheck SC2129 in the new workflow output writes. Grouped the three GITHUB_OUTPUT writes, then reran the full baseline successfully (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-22cpt7bc/report.json), pinned Bicep 0.34.44 validation, actionlint on all five workflows, and 13 focused tests. The source fix is ready for a new commit; CI on the next head remains outstanding.
<!-- SECTION:NOTES:END -->
