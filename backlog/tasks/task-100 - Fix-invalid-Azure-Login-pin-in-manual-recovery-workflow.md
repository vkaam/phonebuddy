---
id: TASK-100
title: Fix invalid Azure Login pin in manual recovery workflow
status: Done
assignee:
  - '@codex'
created_date: '2026-11-13T11:52:00Z'
updated_date: '2026-11-19T04:16:00Z'
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
- [x] #1 The manual recovery workflow pins a resolvable immutable Azure Login commit consistent with the trusted deployment workflow.
- [x] #2 A regression test fails if the manual recovery workflow's Azure Login pin drifts from the trusted deployment workflow.
- [x] #3 A protected-main manual recovery dispatch gets past runner setup and Azure login, completes recovery verification, and retains operator evidence.
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

Draft PR: https://github.com/vkaam/phonebuddy/pull/126. The hosted-main manual recovery acceptance criterion remains pending because this protected workflow only runs on main. Keep TASK-100 In Progress until a post-merge manual recovery completes and its evidence artifact is retained.

Reconciled 2026-11-19. AC1: on main, azure-recover.yml pins azure/login@a641126d1b8aa4d1fa005f4f92df94a3a4c4c906, the same commit as azure-deploy.yml. AC2: tests/test_bicep_ci_boundary.py test_manual_recovery_uses_the_trusted_azure_login_commit asserts both workflows use one identical 40-character pin. AC3: protected-main manual dispatch run 43589085675 (2026-11-14, source 6d3553b) passed Azure login, deployed the selected immutable release, verified backend and frontend recovery and retained artifact manual-recovery-43589085675-1.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed the manual recovery workflow pin (issue #125): azure-recover.yml now uses the same resolvable Azure Login commit as the trusted deployment workflow, and a regression test fails on drift. Merged in PR #126 on 2026-11-13. The post-merge manual recovery dispatch (run 43589085675) passed login, recovered the selected release, verified backend and frontend, and retained its evidence.
<!-- SECTION:FINAL_SUMMARY:END -->
