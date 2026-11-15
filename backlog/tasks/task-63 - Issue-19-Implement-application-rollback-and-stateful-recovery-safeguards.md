---
id: TASK-63
title: Issue 19 - Implement application rollback and stateful recovery safeguards
status: Done
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-15T19:04:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-61
  - TASK-62
references:
  - https://github.com/vkaam/phonebuddy/issues/19
modified_files:
  - >-
    backlog/tasks/task-63 -
    Issue-19-Implement-application-rollback-and-stateful-recovery-safeguards.md
  - scripts/release_recovery.py
  - tests/test_release_recovery.py
  - infra/hosting.bicep
  - .github/workflows/ci.yml
  - infra/release-schema.json
  - .github/workflows/azure-deploy.yml
  - scripts/deployment_policy.py
  - tests/test_deployment_policy.py
  - .github/workflows/azure-recover.yml
  - docs/quality-and-delivery.md
  - tests/test_bicep_ci_boundary.py
  - tests/test_release_test.py
priority: high
type: task
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/19
Approved revision: 2026-11-01T09:24:59Z; body SHA-256 816b8bcb2f162508a7fcc9d14a3bfbcb71cfd174cbab82a86415f58f69519029.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-19-1-release-recovery
Scope: .github/workflows/**; apps/web/**; infra/**; scripts/**; tests/**; docs/quality-and-delivery.md; backlog/tasks/task-63 - Issue-19-Implement-application-rollback-and-stateful-recovery-safeguards.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. The owner waived hosted automatic rollback failure injection on 2026-11-15 (issue 19 comment 6899527814); it remains unverified. Manual recovery evidence is run 43589085675.
Spec amendment: The owner directed the reproduced storage/SQL What-If property-deletion gap be independent later work and not a precondition (issue 19 comment 6899591603; issue 132). This does not assert that the gap is fixed or that live failure cases were demonstrated.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Automatic recovery workflow is implemented; its decision safeguards and workflow wiring have deterministic coverage. Hosted automatic rollback is unverified under the owner waiver.
- [x] #2 Last-known-good state advances only after successful observation and is protected from concurrent runs and retries.
- [x] #3 First-release, incompatible-schema and retry-limit decisions have deterministic coverage; stop and alert paths are implemented, with hosted failure cases not exercised.
- [x] #4 Recovery checks declared schema compatibility and blocks resource deletion or replacement; the known SQL/Storage property-deletion detection gap is deferred independently as issue 132 and is not claimed fixed.
- [x] #5 An authorized manual recovery selects immutable releases, records operator evidence, and verifies backend and frontend recovery; hosted automatic failure injection is waived.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Approved design:
1. Define an immutable release manifest for the exact backend image, frontend asset artifact, effective release configuration, and declared schema compatibility.
2. Store the per-environment last-known-good manifest in private, versioned Azure Blob Storage. Serialize release runs and use conditional state updates so retries or overlapping runs cannot advance the pointer early; advance it only after successful health observation. Reuse the existing per-environment storage account if its scope and access model fit, with narrowly scoped Blob data access.
3. On a failed candidate, attempt recovery once only when the saved manifest is present and schema/infrastructure compatibility permits it. Redeploy the exact artifacts/configuration and verify health. First release, incompatible schema, destructive change, missing state, or failed recovery stops promotion, alerts, and retains evidence; never automate database restore or destructive infrastructure rollback.
4. Add a protected manual recovery workflow that selects an immutable manifest and records the actor, source run, release identity, and outcome.
5. Add deterministic coverage for state transitions, stale retries, first release, incompatibility, bounded recovery, and recovery failure; update delivery policy, then run the task local checks. Hosted failure injection and operator recovery remain external acceptance evidence.

Owner amendment, 15 November 2026: hosted automatic failure injection is waived; the verified manual recovery run is retained. The reproduced What-If property-deletion gap is deferred to independent issue 132 / TASK-104 without blocking this task or other work.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented immutable SHA/run-scoped release manifests and frontend archives; added versioned private Blob state with ETag compare-and-swap, first-release/incompatibility/retry/destructive fail-closed decisions, protected main-only manual recovery with operator evidence, and delivery documentation. Updated the deployment workflow to persist artifacts before promotion, verify backend health before switching the frontend, advance last-known-good only after both surfaces pass, and attempt one compatible recovery with evidence/alerting.

Local validation: scripts/quality.py passed; scripts/run_required_unittests.py passed (164 tests); scripts/check_bicep.py passed with pinned Bicep 0.34.44; actionlint passed for ci.yml, pr-safety.yml, azure-deploy.yml and azure-recover.yml. scripts/check.py passed all steps except web-browser: Playwright could not find Chromium headless shell. Installing it failed with ENOSPC on the 9.8 GB workspace volume; incomplete files were removed.

Draft PR: https://github.com/vkaam/phonebuddy/pull/118. Hosted checks passed on the final PR head: Quality (including workflow ShellCheck, Bicep, Gitleaks), Repository-wide task and issue drift, Risk report (advisory), and Build immutable release image (not applicable for this PR). An earlier Quality run found ShellCheck findings; these were fixed and the rerun passed.

Outstanding acceptance: hosted Azure failure-injection cases and an authorized manual recovery exercise are not run. No Azure deployment or Blob RBAC assignment was performed; the documented Storage Blob Data Contributor assignment must be applied by the Azure owner before hosted workflows can access release state. Keep TASK-63 In Progress until these gates have evidence.

Addressed both unresolved P1 review findings on PR #118 in .github/workflows/azure-deploy.yml: manifest creation now prefixes the immutable image digest while deployment/configuration keep the unprefixed value; the recovery token and frontend restore conditions now include always() with their prerequisite outcomes. Retaining the task's existing hosted Azure recovery and operator exercise acceptance gates.

Current review follow-up verification passed: actionlint .github/workflows/azure-deploy.yml; python3 -B scripts/run_required_unittests.py (164 tests), using the installed Bash 5 and an isolated Git init.defaultBranch override for the macOS test environment. The first local attempt exposed host Bash 3.2, default-branch and sandbox socket constraints; the adjusted rerun passed.

Owner waived hosted automatic failure-injection testing and accepted the known What-If property-deletion gap as independent non-blocking later work (issue 19 comments 6899527814 and 6899591603; issue 132 / TASK-104). Manual recovery run 43589085675 selected immutable release 907f397/43400758871-1; operator vkaam and verified result are recorded in artifact 14112330179. Backend health passed 100 requests over 600 seconds and frontend release identity matched. Automatic rollback, live incompatible-schema and failed-recovery paths remain unverified; declared schema compatibility is not proof of actual database migration state. Independent audit and 36 deterministic recovery/policy/boundary tests passed.

Independent agent task63_evidence validated the amended criteria against 36 passing deterministic tests, merged workflow inspection and the retained manual recovery artifact. Full local baseline passed; Bicep baseline passed with installed 0.48.1 and actionlint passed. Hosted automatic failure injection was explicitly waived; the independent issue 132 defect remains open and is not a dependency.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented guarded immutable release recovery in merged PR 118. An authorized manual recovery was verified in run 43589085675 with retained operator, backend and frontend evidence. Decision and workflow-wiring safeguards passed deterministic tests. The owner waived hosted automatic rollback failure injection; automatic rollback remains unverified in a hosted failure. The owner deferred the reproduced What-If property-deletion gap to independent issue 132 / TASK-104, which is not a precondition. Declared schema checks do not establish live database migration compatibility.
<!-- SECTION:FINAL_SUMMARY:END -->
