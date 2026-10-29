---
id: TASK-17
title: Define and persist call sessions and event contracts
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - backend
  - telephony
dependencies:
  - TASK-16
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
UI, SIP events and asynchronous processing need one durable call identity despite duplicates, disconnects and out-of-order events.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Versioned API/event contracts cover call and leg IDs, organization, direction, participants, timestamps and lifecycle transitions.
- [ ] #2 Persisted sessions reconcile duplicate and out-of-order events idempotently, including incoming calls, unanswered calls and missed hangups.
- [ ] #3 Contract and database tests prove valid transitions, organization isolation and recovery after service restart.
<!-- AC:END -->
