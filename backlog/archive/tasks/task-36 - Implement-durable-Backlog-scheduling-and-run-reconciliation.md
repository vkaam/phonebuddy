---
id: TASK-36
title: Implement durable Backlog scheduling and run reconciliation
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - factory
  - autonomy
  - historical-import
  - needs-triage
dependencies:
  - TASK-32
references:
  - https://github.com/vkaam/phonebuddy/issues/41
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/41 (observed 2026-11-01T09:52:48Z; UTF-8 body SHA-256 1b8080f03f0fbe297ddc41eb2c1a1c6d7771b5c4deda9cbb54f9bb63664aec4b). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
