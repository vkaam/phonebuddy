---
id: TASK-29
title: Integrate and validate a Fonzer account
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - telephony
  - integration
  - historical-import
  - needs-triage
dependencies:
  - TASK-21
  - TASK-28
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/35
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/35 (observed 2026-11-01T09:25:47Z; UTF-8 body SHA-256 44a1eacad84cc2cd12ca0d378234e12fd76379505617dd62b367bd4d6fe81f2f). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
