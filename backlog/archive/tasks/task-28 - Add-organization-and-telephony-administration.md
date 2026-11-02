---
id: TASK-28
title: Add organization and telephony administration
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - frontend
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-16
  - TASK-19
  - TASK-22
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/34
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/34 (observed 2026-11-01T09:25:45Z; UTF-8 body SHA-256 b27d514a184e60f71eb6f6f0749962d5f590b4861fdedfad5caca2bccf793b9d). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
