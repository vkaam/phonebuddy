---
id: TASK-38
title: Add independent final-diff review with separately executed verification
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
labels:
  - factory
  - autonomy
dependencies:
  - TASK-34
  - TASK-35
  - TASK-37
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
