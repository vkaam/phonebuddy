---
id: TASK-41
title: Add a trusted merge controller for independently approved PRs
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
labels:
  - factory
  - autonomy
dependencies:
  - TASK-33
  - TASK-40
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: feature
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The advisory classifier always reports merge_authorized false and repository auto-merge is disabled. After unattended PR production is qualified, an independently scoped controller can remove manual merge handling while preserving the existing human approval contract.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A trusted controller re-reads live policy, current head and base, independent approvals, veto labels, resolved threads and all successful applicable required checks immediately before requesting a native merge path; saved advisory JSON alone cannot authorize it.
- [ ] #2 The coding runner has no merge rights; the controller cannot alter policy, bypass repository rules or merge sensitive or unknown classes, and changed source, revoked approval, stale evidence and unavailable APIs invalidate the request.
- [ ] #3 A reviewed activation procedure verifies repository support and settings, demonstrates allowed merges and denied stale or vetoed cases, and supports immediate disablement; no auto-merge setting is enabled until the complete contract is approved.
<!-- AC:END -->
