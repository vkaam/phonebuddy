---
id: TASK-30
title: Validate the complete web softphone pilot
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - qa
  - pilot
dependencies:
  - TASK-21
  - TASK-24
  - TASK-26
  - TASK-27
  - TASK-28
  - TASK-13
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
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
