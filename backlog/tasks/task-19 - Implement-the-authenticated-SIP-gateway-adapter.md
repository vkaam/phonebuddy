---
id: TASK-19
title: Implement the authenticated SIP gateway adapter
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - telephony
  - backend
dependencies:
  - TASK-17
  - TASK-18
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Application call control must safely map authenticated users and organization sessions onto the SIP gateway without exposing provider credentials.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Server-authorized endpoint credentials and routes are scoped to organization/user, expire or revoke correctly, and never expose provider-wide secrets.
- [ ] #2 Gateway events map to durable call/leg IDs; call authorization enforces allowed destinations and concurrency with idempotent cleanup.
- [ ] #3 Registration failures, gateway restart, stale events and unauthorized control requests have tested outcomes; management APIs remain private.
<!-- AC:END -->
