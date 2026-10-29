---
id: TASK-24
title: Display live transcripts and processing status
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - frontend
  - speech
dependencies:
  - TASK-20
  - TASK-23
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 24000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users need to follow both sides of the conversation and understand whether transcription is current, incomplete or unavailable.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The live transcript distinguishes speakers, interim/final text, timestamps, gaps and processing failures without treating remote roles as verified identities.
- [ ] #2 Authorized subscriptions reconnect and resume from persisted state without duplicate segments or cross-organization leakage.
- [ ] #3 Keyboard and screen-reader behavior, auto-scroll control and long-call performance are exercised; transcript lag is measured against the pilot target.
<!-- AC:END -->
