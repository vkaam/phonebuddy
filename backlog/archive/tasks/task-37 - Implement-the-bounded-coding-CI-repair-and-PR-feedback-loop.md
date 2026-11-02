---
id: TASK-37
title: Implement the bounded coding, CI repair and PR feedback loop
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
  - TASK-34
  - TASK-35
  - TASK-36
references:
  - https://github.com/vkaam/phonebuddy/issues/42
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: feature
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A persistent scheduler alone cannot deliver work. Each approved task needs a bounded implementation run that produces a reusable PR and responds to actual CI and review findings without repeatedly requiring an operator to prompt it.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 An opted-in task progresses from frozen acceptance criteria through isolated implementation, meaningful checks, commit and push to one reviewable PR containing scope, source-bound evidence, limitations and Backlog references.
- [ ] #2 The controller waits for all applicable checks on the current head, repairs in-scope failures and merge conflicts within configured attempts, refreshes evidence after base or head changes, and never treats pending, missing, cancelled or skipped checks as successful.
- [ ] #3 Review feedback is revalidated against the final diff; fully fixed comments receive the required reaction and resolution, unresolved feedback remains visible, and ambiguous requirements or exceeded scope stop for owner input.
- [ ] #4 The run updates Backlog and Groma references through their CLIs, preserves unrelated work, and cannot approve, merge, deploy or broaden its permissions.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/42 (observed 2026-11-01T09:52:53Z; UTF-8 body SHA-256 9210524660e4d6657da26abcbe7ae7cdea5eb3dd50d07756525248088d14db8e). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
