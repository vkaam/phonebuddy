---
id: TASK-16
title: Add Entra sign-in and organization-scoped authorization
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - identity
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-60
  - TASK-15
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/22
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/22 (observed 2026-11-01T09:25:07Z; UTF-8 body SHA-256 00bf2af01986581544cb703b4f5dadb2f8e77e8db5e73a9ce3c7b8362a001e74). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
