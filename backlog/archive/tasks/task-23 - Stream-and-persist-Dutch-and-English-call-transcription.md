---
id: TASK-23
title: Stream and persist Dutch and English call transcription
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - speech
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-60
  - TASK-19
  - TASK-22
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/29
priority: high
type: feature
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Both sides of an authorized call must become a durable, attributable transcript without allowing AI failures to interrupt voice.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Per-leg audio produces timestamped final segments and interim updates in Dutch and English using Azure Speech with tested identity/token refresh.
- [ ] #2 Sequence numbers, gaps, bounded buffers and reconnect behavior preserve provenance; Speech failure or overload leaves the voice call running.
- [ ] #3 Hangup finalizes or marks incomplete streams and seals a transcript revision; duplicates and late corrections are handled without silently losing or duplicating text.
- [ ] #4 Representative Flemish/Dutch and English fixtures measure accuracy, language switching, overlap and narrowband audio; results and limitations are recorded.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/29 (observed 2026-11-01T09:25:31Z; UTF-8 body SHA-256 e8b59f2bb6895ef5c608f670dacd27cced804ddf3a6887d79ff085facae375e3). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
