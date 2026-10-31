---
id: TASK-36
title: Implement durable Backlog scheduling and run reconciliation
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
updated_date: '2026-10-31T18:48:00Z'
labels:
  - factory
  - autonomy
dependencies:
  - TASK-32
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: feature
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
AGENTS.md tells an interactive agent how to choose work, but there is no persistent controller to wake, claim tasks, or recover after process loss. Cross-branch Backlog state can differ from main, and a merged PR can leave its task incomplete when live acceptance evidence is blocked, as illustrated by TASK-5.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A durable controller selects only opted-in unassigned eligible tasks with satisfied dependencies, reconciles branch and open-PR state, and treats unknown, archived-unfinished or ambiguous dependencies as blocked.
- [ ] #2 Atomic leases, heartbeat expiry and idempotent event handling prevent duplicate ownership and duplicate PRs under two controllers, repeated events, and a restart during every external action.
- [ ] #3 Run state records the pinned specification, base commit, branch, task identity and lifecycle; restart, stale lease, branch deletion, no-eligible-work, and exhausted-budget paths resume safely or stop with actionable evidence.
<!-- AC:END -->
