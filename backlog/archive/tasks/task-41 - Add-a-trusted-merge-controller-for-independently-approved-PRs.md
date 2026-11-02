---
id: TASK-41
title: Add a trusted merge controller for independently approved PRs
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
  - TASK-33
  - TASK-40
references:
  - https://github.com/vkaam/phonebuddy/issues/46
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/46 (observed 2026-11-01T09:53:03Z; UTF-8 body SHA-256 20d2aeae955d41556348cd9a9f67feea8593c0b306ddca0140e812978b70040c). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
