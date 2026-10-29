---
id: TASK-26
title: Build call history and transcript-summary detail views
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - frontend
  - backend
dependencies:
  - TASK-17
  - TASK-24
  - TASK-25
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users need to retrieve completed and missed calls and inspect the evidence behind generated summaries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Organization-authorized paginated history supports useful date, direction and status filters with loading, empty and failure states.
- [ ] #2 Call detail displays transcript, summary status and action items; selecting a cited claim navigates to its supporting segments and identifies partial or superseded results.
- [ ] #3 Tests cover access denial, long transcripts, deleted calls, pending/failed summaries and retry controls limited to authorized users.
<!-- AC:END -->
