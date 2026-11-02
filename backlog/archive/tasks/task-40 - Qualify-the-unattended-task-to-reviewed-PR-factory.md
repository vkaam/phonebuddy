---
id: TASK-40
title: Qualify the unattended task-to-reviewed-PR factory
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
  - TASK-37
  - TASK-38
  - TASK-39
references:
  - https://github.com/vkaam/phonebuddy/issues/45
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: task
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Individual components do not establish that the factory works unattended. A reproducible campaign must prove useful delivery, resumability and resistance to hostile task or repository content before enabling more authority.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A versioned campaign contains at least ten distinct eligible tasks across documentation, behavior fixes and small code features; at least eight reach a reviewable PR without an operator prompt or code edit, with cost, duration and all interventions reported.
- [ ] #2 All seeded must-detect defects and denied-authority attempts stop or fail correctly, including task, repository and log prompt injection, evidence forgery, stale CI, policy edits, duplicate events, reviewer outage, exhausted budgets and restart during PR publication.
- [ ] #3 A controller interruption and sandbox loss recover without duplicate claims or PRs; each terminal run retains useful evidence and no resources or credentials survive cleanup.
- [ ] #4 At least one real eligible PhoneBuddy task completes the same path; the report distinguishes autonomous PR readiness from still-required human merge approval and deployment prerequisites.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/45 (observed 2026-11-01T09:52:59Z; UTF-8 body SHA-256 7e959be6cb40d1608faaebac8c444b49cb2866a0c4f38d532c848d15b7204786). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
