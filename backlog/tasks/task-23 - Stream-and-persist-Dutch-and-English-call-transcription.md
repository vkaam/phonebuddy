---
id: TASK-23
title: Stream and persist Dutch and English call transcription
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - speech
  - backend
dependencies:
  - TASK-19
  - TASK-22
  - TASK-9
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
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
