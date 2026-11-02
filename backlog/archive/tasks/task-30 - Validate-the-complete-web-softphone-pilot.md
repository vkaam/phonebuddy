---
id: TASK-30
title: Validate the complete web softphone pilot
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - qa
  - pilot
  - historical-import
  - needs-triage
dependencies:
  - TASK-64
  - TASK-21
  - TASK-24
  - TASK-26
  - TASK-27
  - TASK-28
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/36
priority: high
type: feature
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The internal pilot needs evidence of the full calling-to-summary experience beyond passing repository CI. Fonzer acceptance is additionally required if the pilot launches on Fonzer.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Document and exercise the supported browser/headset/network matrix and keyboard accessibility for sign-in, calls, live transcripts, history and summaries.
- [ ] #2 Run 10 concurrent calls and 60-minute sessions with synthetic or approved data; measure call reliability, transcript lag, summary latency and resource cost.
- [ ] #3 Fault injection proves AI outages preserve voice, cross-organization access is denied, reconnects expose gaps, and release rollback behavior during active calls is documented.
- [ ] #4 Pilot onboarding and troubleshooting guidance records notice/retention settings, known limits, operational owners and remaining blockers; real Fonzer launch requires its separate acceptance task.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/36 (observed 2026-11-01T09:25:50Z; UTF-8 body SHA-256 53e76a198af7d2358e021ae5d2b398a376b83177a50e604c6945eab9b401e2ea). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
