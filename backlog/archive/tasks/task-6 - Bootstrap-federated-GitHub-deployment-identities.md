---
id: TASK-6
title: Bootstrap federated GitHub deployment identities
status: To Do
assignee: []
created_date: '2026-10-29T20:04:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-4
  - TASK-5
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Trusted workflows need environment-scoped Azure access without long-lived credentials.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Distinct environment identities use restricted repository and environment federation with least-privilege Azure roles.
- [ ] #2 Trusted workflow authentication succeeds while fork PR access and cross-environment writes are rejected.
- [ ] #3 Bootstrap and GitHub environment configuration are reproducible or explicitly documented; credentials never enter logs.
<!-- AC:END -->
