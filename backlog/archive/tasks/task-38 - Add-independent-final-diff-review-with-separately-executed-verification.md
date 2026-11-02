---
id: TASK-38
title: Add independent final-diff review with separately executed verification
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
  - TASK-37
references:
  - https://github.com/vkaam/phonebuddy/issues/43
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: feature
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PR safety classifies bounded documentation risk and does not review implementation correctness. An unattended coding loop needs a separate reviewer to challenge behavior and acceptance evidence without inheriting the implementer context.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A separate reviewer identity and fresh context consume the frozen specification, complete final diff and independently executed checks tied to the current head and base; implementer reasoning and self-reported success cannot satisfy review.
- [ ] #2 Findings identify affected files, severity and acceptance criteria; a material finding, incomplete evidence or changed source blocks readiness until a new review verifies the fix.
- [ ] #3 Seeded defects in behavior, organization isolation and misleading test evidence are detected, reviewer or model outages fail closed, and agent review cannot substitute for required human approval or authorize policy changes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/43 (observed 2026-11-01T09:26:12Z; UTF-8 body SHA-256 eead5c408d7d67935d4e82320a2e367ecda302a9a35361c1bdaed7e29ceb41ab). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
