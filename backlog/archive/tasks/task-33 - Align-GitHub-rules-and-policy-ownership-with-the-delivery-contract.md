---
id: TASK-33
title: Align GitHub rules and policy ownership with the delivery contract
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
  - https://github.com/vkaam/phonebuddy/issues/38
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: chore
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The active Standard main ruleset requires Quality and resolved threads but zero approvals, despite documentation requiring independent human and Code Owner review. A classic branch-protection 404 does not describe the effective ruleset.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Effective default-branch rules require current independent approval and Code Owner review, dismiss stale approvals, require the latest push to be independently approved, and retain strict Quality, resolved conversations, deletion and force-push protection without bypass actors.
- [ ] #2 Sensitive delivery and factory paths have valid owners with write access, including an independent reviewer for owner-authored PRs; an unavailable second maintainer is reported as a blocker.
- [ ] #3 A passing PR, failing Quality check, stale approval and policy-change PR demonstrate the expected enforcement, and documentation records dated effective settings rather than inferring protection from a single API.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/38 (observed 2026-11-01T09:25:56Z; UTF-8 body SHA-256 9c1086fc518cee9b2302d9da74e12422f6541fc899196ec44653695902d50bd0). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
