---
id: TASK-20
title: Build inbound and outbound browser calling
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - frontend
  - telephony
  - historical-import
  - needs-triage
dependencies:
  - TASK-15
  - TASK-17
  - TASK-19
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/26
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/26 (observed 2026-11-01T09:25:23Z; UTF-8 body SHA-256 193d3739d8f0b04a29d5aac1846696aedf5ac4c3c5c2e88bb2b0cdebd1f9336d). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
