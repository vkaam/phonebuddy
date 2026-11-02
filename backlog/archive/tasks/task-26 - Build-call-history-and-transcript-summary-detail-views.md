---
id: TASK-26
title: Build call history and transcript-summary detail views
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - frontend
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-17
  - TASK-24
  - TASK-25
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/33
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/33 (observed 2026-11-01T09:25:39Z; UTF-8 body SHA-256 638f2e06e1ebf4639371e66f21ffee9108c99099b0a666aa58fb82ae48c45ee7). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
