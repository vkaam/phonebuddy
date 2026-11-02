---
id: TASK-17
title: Define and persist call sessions and event contracts
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - backend
  - telephony
  - historical-import
  - needs-triage
dependencies:
  - TASK-16
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/23
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/23 (observed 2026-11-01T09:25:11Z; UTF-8 body SHA-256 8dcbe9ce4ab8c9571c316a8f8d1dec8496cc42a22cecada76e3eb153a9c8e404). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
