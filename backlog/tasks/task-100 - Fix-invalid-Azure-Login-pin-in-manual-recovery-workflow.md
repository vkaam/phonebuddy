---
id: TASK-100
title: Fix invalid Azure Login pin in manual recovery workflow
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-13T11:52:00Z'
updated_date: '2026-11-13T11:57:00Z'
labels:
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/125
modified_files:
  - >-
    backlog/tasks/task-100 -
    Fix-invalid-Azure-Login-pin-in-manual-recovery-workflow.md
  - .github/workflows/azure-recover.yml
  - tests/test_bicep_ci_boundary.py
priority: high
type: bug
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The first authorized dispatch of the manual recovery workflow failed during runner setup before checkout or Azure login because its pinned Azure Login commit cannot be resolved. The run made no Azure changes. This is a post-merge defect found while exercising TASK-63.

Primary issue: https://github.com/vkaam/phonebuddy/issues/125
Approved revision: 2026-11-13T11:51:30Z; body SHA-256 bd47fcba5a7393f3f9683a6582b00ef294ed7c7d0f10624e0c2ae9e5764c81ee.
Approval evidence: The user explicitly approved this follow-up on 2026-11-13 with “yes fix it” after the need for a new issue, task and PR was explained.
Related: issue #19, merged PR #118, failed dispatch run #43416629403.
Branch: agent/gh-125-1-manual-recovery-pin
Scope: .github/workflows/azure-recover.yml; tests/test_bicep_ci_boundary.py; this task's own CLI-managed record
Verify: python3 -B scripts/run_required_unittests.py; actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml .github/workflows/azure-recover.yml; hosted main-branch manual recovery dispatch with retained operator evidence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The manual recovery workflow pins a resolvable immutable Azure Login commit consistent with the trusted deployment workflow.
- [ ] #2 A regression test fails if the manual recovery workflow's Azure Login pin drifts from the trusted deployment workflow.
- [ ] #3 A protected-main manual recovery dispatch gets past runner setup and Azure login, completes recovery verification, and retains operator evidence.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Align the manual recovery workflow’s Azure Login pin with the already-validated immutable pin in the trusted deployment workflow.
2. Add a regression assertion that both trusted workflows use the same full 40-character action ref, so future drift is caught by required Python tests.
3. Run the required unit suite and actionlint; push the task branch, open a draft PR, and monitor hosted checks.
4. Once merged, dispatch manual recovery for an immutable schema-compatible release, verify backend/frontend and operator evidence, and record the workflow run/artifact.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Corrected the manual workflow pin to the resolvable Azure Login commit used by azure-deploy.yml and added a regression test requiring a single full 40-character pin in both workflows and exact equality. The failed run was confirmed to stop at runner setup before checkout or Azure login.

Local verification passed: python3 -B scripts/run_required_unittests.py (178 tests); python3 -B scripts/quality.py; actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml .github/workflows/azure-recover.yml; GitHub API lookup confirmed the pinned commit exists. The hosted manual recovery dispatch remains pending merge.
<!-- SECTION:NOTES:END -->
