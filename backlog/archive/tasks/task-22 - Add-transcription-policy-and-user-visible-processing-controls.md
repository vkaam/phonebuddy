---
id: TASK-22
title: Add transcription policy and user-visible processing controls
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - privacy
  - frontend
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-16
  - TASK-17
  - TASK-20
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/28
priority: high
type: feature
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Automatic transcription needs organization policy and clear participant/user notice before audio is captured; recording is a separate option.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Authorized administrators configure transcription policy, notice behavior and retention; persistent recording is off by default and independently controlled.
- [ ] #2 Call UI shows enabled, paused, unavailable and stopped processing accurately; policy decisions and changes are audited without sensitive content.
- [ ] #3 Denied or disabled processing prevents media capture and inference, including mid-call changes, with clear partial-transcript boundaries.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/28 (observed 2026-11-01T09:25:28Z; UTF-8 body SHA-256 29f1da0530f221533136787bfacf1e8e4db947eaa303e4c13322e26e2beaf89a). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
