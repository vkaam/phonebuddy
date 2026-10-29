---
id: TASK-7
title: Validate Bicep changes in pull-request CI
status: To Do
assignee: []
created_date: '2026-10-29T20:04:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Infrastructure defects must be caught before merge without granting untrusted PR code Azure privileges.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Required CI checks lint/build Bicep, validate parameters and workflows with pinned tooling.
- [ ] #2 Authenticated what-if uses a trusted scoped path; arbitrary PR code never runs with deployment credentials.
- [ ] #3 Invalid templates, policy violations and missing evidence produce explicit failures; fork handling is tested.
<!-- AC:END -->
