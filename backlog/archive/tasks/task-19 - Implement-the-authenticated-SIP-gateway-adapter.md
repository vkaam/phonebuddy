---
id: TASK-19
title: Implement the authenticated SIP gateway adapter
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - telephony
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-17
  - TASK-18
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/24
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/24 (observed 2026-11-01T09:25:14Z; UTF-8 body SHA-256 cd68599aa4fda7b3f5c898d4be8b35e2a0206db839cfdfd2eb07c675b56c4bbb). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
