---
id: TASK-93
title: Allow completed issue closure after merged task PRs
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T18:54:00Z'
updated_date: '2026-11-11T19:00:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/107
  - scripts/backlog_consistency.py
modified_files:
  - >-
    backlog/tasks/task-93 -
    Allow-completed-issue-closure-after-merged-task-PRs.md
  - scripts/backlog_consistency.py
  - tests/test_backlog_consistency.py
  - docs/issue-backlog-governance.md
  - docs/quality-and-delivery.md
ordinal: 82000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Legacy reconciliation tasks can remain In Progress on main even after their only PR merged with all native acceptance checked; TASK-75 after PR #81 is an example. A second PR solely to flip status repeats the same loop.
Issue: https://github.com/vkaam/phonebuddy/issues/107
Approved revision: 2026-11-11T18:51:59Z; body SHA-256 5b94aecf30406e1b9c8427df479a88d807ec7d397c67b9522edd53bb9c6eb37e.
Approval evidence: owner explicitly selected merge-based task completion, closure after all required PRs merge, and post-merge live proof as separate work when needed.
Branch: agent/gh-107-2-merge-based-completion
Scope: scripts/backlog_consistency.py; tests/test_backlog_consistency.py; docs/issue-backlog-governance.md; docs/quality-and-delivery.md; backlog/tasks/task-93 - Allow-completed-issue-closure-after-merged-task-PRs.md
Verify: python3 -B -m unittest discover -s tests -p test_backlog_consistency.py; python3 -B scripts/run_required_unittests.py; python3 -B scripts/quality.py; live consistency against fresh origin/main; hosted PR Quality.
Spec: Effective task completion follows a checked acceptance record and its single merged implementation PR on current main. A legacy In Progress status after that merge is reported for cleanup but cannot require another PR just to complete the task. Unmerged, unchecked, or genuinely incomplete tasks stay blocking. Closed issues are valid only when all linked required tasks have effective completion.
Triage amendment 2026-11-11: Investigation showed unchanged Done tasks are already skipped by the audit. The actual legacy loop is a checked In Progress task stranded after its PR merge. Adjust this slice to effective merge-based completion without silently accepting unmerged or unchecked work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A task with checked native acceptance and its single merged PR on main has effective completion even when a legacy record still says In Progress; this is reported for cleanup without requiring a second PR.
- [ ] #2 Unmerged, unchecked or branch-local proposed completion does not satisfy dependencies or permit issue closure.
- [ ] #3 A multi-task issue remains open while any required task PR is unmerged and can close after every task has effective completion on main.
- [ ] #4 Regression tests and policy documentation explain the merge-based path, the legacy status warning and separate post-merge live work.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend effective completion evidence to checked legacy In Progress records on main with a merged PR, retaining visible stale-status warnings. 2. Use effective completion for issue-state and dependency validation without weakening checks for unmerged work. 3. Add regression tests and update policy guidance, then publish and verify the PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented effective completion for checked legacy In Progress records on main with a merged PR; audit emits a stale-status warning. Closed issue state requires effective completion for linked tasks. Added multi-task, unmerged and unchecked regression cases. Focused guard tests passed (32); required Python suite passed (139); repository checks and live claim guard passed with one expected stale-status warning.

Preserved archived unfinished dependencies as unsatisfied; a checked but archived In Progress task does not gain effective completion. Focused tests pass (32) and required suite passes (139) after this edge-case fix.
<!-- SECTION:NOTES:END -->
