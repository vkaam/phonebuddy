---
id: TASK-22
title: Add transcription policy and user-visible processing controls
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - privacy
  - frontend
  - backend
dependencies:
  - TASK-16
  - TASK-17
  - TASK-20
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
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
