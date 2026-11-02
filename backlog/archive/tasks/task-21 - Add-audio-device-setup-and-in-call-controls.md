---
id: TASK-21
title: Add audio-device setup and in-call controls
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
  - TASK-20
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/27
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/27 (observed 2026-11-01T09:25:25Z; UTF-8 body SHA-256 e8987f80f094c72e63fc4dff6cb71c86006716a6d408438384c257dee98e0f78). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
