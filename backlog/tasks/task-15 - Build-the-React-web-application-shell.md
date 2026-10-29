---
id: TASK-15
title: Build the React web application shell
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - frontend
dependencies: []
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the browser product foundation for the internal pilot, with room for organization-scoped calling, history and settings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Vite/React/TypeScript builds reproducibly with locked dependencies and integrates with existing CI and static deployment artifacts.
- [ ] #2 Responsive navigation, loading/error/empty states and accessible keyboard focus work for dialer, history and settings routes.
- [ ] #3 Public runtime configuration contains no secrets; missing required configuration gives an actionable startup error.
<!-- AC:END -->
