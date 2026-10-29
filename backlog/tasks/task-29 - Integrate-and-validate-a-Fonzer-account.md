---
id: TASK-29
title: Integrate and validate a Fonzer account
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - telephony
  - integration
dependencies:
  - TASK-21
  - TASK-28
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: medium
type: feature
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add Fonzer after generic SIP behavior is proven; account-specific extension versus trunk capabilities must be established rather than assumed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Record the actual account type, supported authentication/transport/codecs, routing, caller ID, DTMF, registration limits and provider permission for media capture.
- [ ] #2 Provider-specific configuration lives behind the generic adapter/profile boundary; credentials remain server-side and failure messages are actionable.
- [ ] #3 Authorized inbound/outbound acceptance calls demonstrate both-way audio, hold/resume, DTMF and transcription; unresolved provider limitations and emergency-call policy are documented before rollout.
<!-- AC:END -->
