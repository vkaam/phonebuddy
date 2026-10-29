---
id: TASK-21
title: Add audio-device setup and in-call controls
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - frontend
  - telephony
dependencies:
  - TASK-20
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 21000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users must choose working audio devices and operate the call reliably, including when permissions or hardware change.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Microphone permission and device selection have usable denial, missing-device and unplug/reconnect behavior; audio checks prevent accidental feedback.
- [ ] #2 Mute, hold/resume and negotiated DTMF work against the controlled SIP peer and show the actual call state.
- [ ] #3 Tests cover network loss, unsupported output selection and browser session closure; the UI clearly states background-ringing limitations.
<!-- AC:END -->
