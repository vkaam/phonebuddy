---
id: TASK-112
title: Allow task-intake-only pull requests
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-18T08:55:00Z'
updated_date: '2026-11-18T09:03:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/141
  - scripts/backlog_consistency.py
  - tests/test_backlog_consistency.py
  - docs/issue-backlog-governance.md
modified_files:
  - scripts/backlog_consistency.py
  - tests/test_backlog_consistency.py
  - docs/issue-backlog-governance.md
type: bug
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The required PR gate blocks branches that only add future tasks.

Issue: https://github.com/vkaam/phonebuddy/issues/141
Approved revision: 2026-11-18T05:52:23Z SHA-256 063a1ff389021b4ba24d1b4388b495a86be9bd15498113663255c7dc5453026c
Approval evidence: Owner directed implementation in Codex on 2026-11-18 after review of issue 141 proposed acceptance.
Branch: agent/issue-141-task-intake
Scope: scripts/backlog_consistency.py; tests/test_backlog_consistency.py; docs/issue-backlog-governance.md; this task record only
Verify: python3 -B -m unittest tests.test_backlog_consistency; python3 scripts/quality.py; python3 -B scripts/run_required_unittests.py
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 New task-only intake PRs can pass the PR gate while new records are appropriately validated.
- [ ] #2 Existing task edits, deletions, renames, non-task files and mixed implementation changes retain existing checks.
- [ ] #3 Regression tests cover the exception and bypass attempts and documentation explains the boundary.
- [ ] #4 Applicable local and hosted checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Identify task-only additions from the base tree and validate their native records and issue evidence. 2. Keep all other PRs on the existing execution-task scope path. 3. Add regression coverage and document the boundary; run declared checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented intake-only classification and live validation; 36 focused tests, repository quality and 218 required unit tests passed locally using Homebrew Bash and a master initial branch for Git fixtures. Independent review requested; hosted checks pending.

Draft PR: https://github.com/vkaam/phonebuddy/pull/143. Hosted Quality and independent final-head review pending.

Independent review of 0f6ba4d found no blocking defects; 36 focused tests and hosted Quality run 44272005343 passed. Automatic approval review rejected proposed task finalization because a resulting task-record commit would require final-head revalidation. Task remains active and PR draft pending resolution.
<!-- SECTION:NOTES:END -->
