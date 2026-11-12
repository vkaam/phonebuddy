---
id: TASK-63
title: Issue 19 - Implement application rollback and stateful recovery safeguards
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-12T18:21:00Z'
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
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted controlled failure injection verifies release recovery and alerts; first release and incompatible schema cases stop safely. An authorized operator exercises the immutable-release manual recovery path.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Failed candidate health restores eligible last-known-good application, frontend assets and configuration and verifies recovery.
- [ ] #2 Last-known-good state advances only after successful observation and is protected from concurrent runs and retries.
- [ ] #3 First deployment without a prior release, incompatible schemas and failed recovery stop promotion and alert; bounded retries prevent rollback loops.
- [ ] #4 Expand/contract database compatibility is enforced; destructive infrastructure or database rollback and backup restore are never blindly automated.
- [ ] #5 An authorized manual recovery workflow selects immutable releases and records operator and evidence; failure injection demonstrates automatic rollback.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Approved design:
1. Define an immutable release manifest for the exact backend image, frontend asset artifact, effective release configuration, and declared schema compatibility.
2. Store the per-environment last-known-good manifest in private, versioned Azure Blob Storage. Serialize release runs and use conditional state updates so retries or overlapping runs cannot advance the pointer early; advance it only after successful health observation. Reuse the existing per-environment storage account if its scope and access model fit, with narrowly scoped Blob data access.
3. On a failed candidate, attempt recovery once only when the saved manifest is present and schema/infrastructure compatibility permits it. Redeploy the exact artifacts/configuration and verify health. First release, incompatible schema, destructive change, missing state, or failed recovery stops promotion, alerts, and retains evidence; never automate database restore or destructive infrastructure rollback.
4. Add a protected manual recovery workflow that selects an immutable manifest and records the actor, source run, release identity, and outcome.
5. Add deterministic coverage for state transitions, stale retries, first release, incompatibility, bounded recovery, and recovery failure; update delivery policy, then run the task local checks. Hosted failure injection and operator recovery remain external acceptance evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented immutable SHA/run-scoped release manifests and frontend archives; added versioned private Blob state with ETag compare-and-swap, first-release/incompatibility/retry/destructive fail-closed decisions, protected main-only manual recovery with operator evidence, and delivery documentation. Updated the deployment workflow to persist artifacts before promotion, verify backend health before switching the frontend, advance last-known-good only after both surfaces pass, and attempt one compatible recovery with evidence/alerting.

Local validation: scripts/quality.py passed; scripts/run_required_unittests.py passed (164 tests); scripts/check_bicep.py passed with pinned Bicep 0.34.44; actionlint passed for ci.yml, pr-safety.yml, azure-deploy.yml and azure-recover.yml. scripts/check.py passed all steps except web-browser: Playwright could not find Chromium headless shell. Installing it failed with ENOSPC on the 9.8 GB workspace volume; incomplete files were removed.

Outstanding acceptance: hosted Azure failure-injection cases and an authorized manual recovery exercise are not run. No Azure deployment or Blob RBAC assignment was performed; the documented Storage Blob Data Contributor assignment must be applied by the Azure owner before hosted workflows can access release state. Keep TASK-63 In Progress until these gates have evidence.
<!-- SECTION:NOTES:END -->
