---
id: TASK-28
title: Add organization and telephony administration
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - frontend
  - backend
dependencies:
  - TASK-16
  - TASK-19
  - TASK-22
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: medium
type: feature
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Pilot operators need scoped user, provider and policy configuration with a path toward multiple organizations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Authorized admins manage membership/roles, provider profiles, dial restrictions and concurrency limits with server-side validation.
- [ ] #2 Provider secrets are entered through protected server handling, are never returned to the browser, and support rotation with audited changes.
- [ ] #3 Registration/connection diagnostics are actionable and redacted; non-admin and cross-organization attempts fail in API and UI tests.
<!-- AC:END -->
