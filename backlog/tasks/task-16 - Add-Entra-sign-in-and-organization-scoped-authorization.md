---
id: TASK-16
title: Add Entra sign-in and organization-scoped authorization
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - identity
  - backend
dependencies:
  - TASK-15
  - TASK-9
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The internal pilot must enforce organization boundaries from the first authenticated feature while preparing for multiple customer organizations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Browser sign-in, sign-out and session expiry work; the API validates token issuer, audience and lifetime.
- [ ] #2 Organization membership is resolved server-side independently of Entra directory ID; unauthorized organization and object access is denied.
- [ ] #3 Tests cover user/admin roles, revoked membership, expired tokens and cross-organization HTTP and WebSocket access.
<!-- AC:END -->
