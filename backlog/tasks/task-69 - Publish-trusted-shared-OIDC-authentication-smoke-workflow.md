---
id: TASK-69
title: Publish trusted shared OIDC authentication smoke workflow
status: Done
assignee:
  - '@codex'
created_date: '2026-11-02T21:15:00Z'
updated_date: '2026-11-02T21:57:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/13
  - .github/workflows/azure-oidc-smoke.yml
  - https://github.com/vkaam/phonebuddy/pull/75
modified_files:
  - >-
    backlog/tasks/task-57 -
    Issue-13-Bootstrap-federated-GitHub-deployment-identities.md
  - .github/workflows/azure-oidc-smoke.yml
  - tests/test_oidc_smoke_workflow.py
priority: high
type: task
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Publish a minimal trusted authentication smoke workflow independently so TASK-57 can collect the two required live runs before its own completion.
Issue: https://github.com/vkaam/phonebuddy/issues/13
Approved revision: 2026-11-02T20:47:52Z; body SHA-256 31d3571e5b62e2fc8a4efa86f325d5f757bccc09f4516fc7f7cabf17d417305b.
Approval evidence: Repository owner explicitly requested a narrow split PR in this conversation on 2026-11-02 after approving a shared dev/test principal.
Branch: agent/gh-13-2-oidc-smoke
Scope: .github/workflows/azure-oidc-smoke.yml; tests/test_oidc_smoke_workflow.py; backlog/tasks/task-57 - Issue-13-Bootstrap-federated-GitHub-deployment-identities.md; this task's own CLI-managed record.
Verify: From repository root run python3 -B scripts/run_required_unittests.py; python3 -B scripts/quality.py; /private/tmp/phonebuddy-qa-tools/actionlint .github/workflows/azure-oidc-smoke.yml .github/workflows/ci.yml .github/workflows/pr-safety.yml; git diff --check; hosted Quality and advisory checks. Live authentication runs after merge are evidence for TASK-57, not a condition for this enabling slice.
Spec: Workflow is manual and main-only, uses GitHub environments and least-privilege token permissions, reads the two approved resource groups without deployments, does not disclose credentials or identifiers, and documents shared access. Never authorize merge or deploy. Update TASK-57 triage and issue revision only to record the split and dependency.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Manual workflow is configured for main-only dispatch via dev or test GitHub environments, authenticates with OIDC, and reads both foundation resource groups without deployment writes.
- [x] #2 Regression checks and workflow lint verify the trusted trigger and permissions; TASK-57 records the split and waits for this PR to merge.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Split the reviewed workflow from TASK-57 and record the dependency. 2. Verify trust boundaries and local checks. 3. Publish one PR and verify current-head CI.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Workflow and boundary regression prepared from existing draft PR #55. Local 63 Python tests, repository checks, actionlint, offline guard and git diff --check passed. TASK-57 is paused on this prerequisite and its existing PR claim is retained. Live authentication is explicitly deferred until after this enabling PR is reviewed and merged.

Draft PR #75 opened; awaiting hosted Quality and advisory checks on the current head. The workflow must reach main through review before either live smoke run can be collected.

Acceptance evidence: boundary regression and actionlint verify configured manual main-only environment job, OIDC permission, group-read-only commands and no PR trigger or deployment command; 63 Python tests and repository checks passed. TASK-57 is paused with TASK-69 dependency. PR #75 head 2e62275 passed hosted Quality run 41526941786 and advisory run 41526939615. Live authentication runs are explicitly TASK-57 evidence after review and merge, not claimed here. Final metadata requires revalidation.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Prepared the reviewed main-only shared OIDC smoke workflow and TASK-57 prerequisite split. Local tests, actionlint, offline guard and hosted checks passed on implementation head; final metadata head requires revalidation. Live authentication runs and TASK-57 acceptance remain outstanding until this PR is reviewed and merged.
<!-- SECTION:FINAL_SUMMARY:END -->
