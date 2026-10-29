---
id: TASK-20
title: Build inbound and outbound browser calling
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - frontend
  - telephony
dependencies:
  - TASK-15
  - TASK-17
  - TASK-19
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Pilot users need a usable dialer and incoming-call experience around the actual SIP adapter.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Users can place, accept, reject, cancel and end one active call; ringing, busy, unavailable, failed and ended states reflect server/gateway state.
- [ ] #2 Number input handles supported formats and validation; incoming identity display distinguishes unverified caller information.
- [ ] #3 Keyboard-accessible controls and browser tests cover race conditions such as remote hangup while accepting, duplicate incoming events and another browser tab owning the active session.
<!-- AC:END -->
