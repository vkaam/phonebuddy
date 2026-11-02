---
id: TASK-24
title: Display live transcripts and processing status
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - frontend
  - speech
  - historical-import
  - needs-triage
dependencies:
  - TASK-20
  - TASK-23
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/30
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/30 (observed 2026-11-01T09:25:33Z; UTF-8 body SHA-256 3c3e6e87ad7477b9c8fac9952ff3419686a3ae42b5d42b5fb7fb272ae7cea367). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
