---
id: TASK-98
title: Reconcile merged hosting task statuses
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-13T06:53:00Z'
updated_date: '2026-11-13T07:00:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/122
  - https://github.com/vkaam/phonebuddy/pull/81
  - https://github.com/vkaam/phonebuddy/pull/114
  - https://github.com/vkaam/phonebuddy/pull/123
modified_files:
  - backlog/tasks/task-75 - Reconcile-TASK-59-completion-after-merge.md
  - backlog/tasks/task-95 - Provision-missing-pilot-Static-Web-App.md
priority: high
type: chore
ordinal: 86000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: TASK-75 and TASK-95 remain In Progress on main despite checked acceptance and merged PRs; preserve unfinished live verification.

Issue: https://github.com/vkaam/phonebuddy/issues/122
Approved revision: 2026-11-13T06:53:21Z; body SHA-256 5044ea7ad4011a79abe1b358bd6081f5b5d771697d2dd6f240023440b5a80e4d.
Approval evidence: The owner requested accurate ticket statuses on main on 2026-11-13.
Branch: agent/reconcile-main-ticket-status
Scope: backlog/tasks/task-75 - Reconcile-TASK-59-completion-after-merge.md; backlog/tasks/task-95 - Provision-missing-pilot-Static-Web-App.md; backlog/tasks/task-98 - Reconcile-merged-hosting-task-statuses.md.
Verify: python3 -B scripts/backlog_consistency.py --base origin/main; python3 -B scripts/check.py; git diff --check; hosted PR Quality.
Spec: Preserve existing acceptance and evidence. Keep issue 15 and TASK-71 open for live hosting verification.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 TASK-75 and TASK-95 reflect their verified merged completion while preserving evidence and checked acceptance.
- [ ] #2 Incomplete hosting verification remains open; live consistency audit and required checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verify merged PRs and checked acceptance for TASK-75 and TASK-95. 2. Set only those records to Done and preserve their evidence; keep TASK-71 and issue 15 open. 3. Run live consistency and local checks, obtain independent review, and merge the reconciliation PR after required checks pass.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-13: Owner approved a one-task exception to the unavailable durable lease service. Live claim check passed with claim_verified true against main 46c0ee881a5294424a5474d08b633d38eaa464d0; PR 123 was temporarily closed to satisfy the unclaimed PR guard and will be reopened after the claim is pushed.
<!-- SECTION:NOTES:END -->
