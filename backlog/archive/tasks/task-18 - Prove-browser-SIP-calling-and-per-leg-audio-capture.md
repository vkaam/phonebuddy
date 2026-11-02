---
id: TASK-18
title: Prove browser SIP calling and per-leg audio capture
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - telephony
  - spike
  - historical-import
  - needs-triage
dependencies:
  - TASK-60
  - TASK-65
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/25
priority: high
type: spike
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Resolve browser/WebRTC-to-SIP and both-speaker capture risks against a controlled peer before committing the production adapter. This extends the infrastructure connectivity test with application/media evidence.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Demonstrate inbound/outbound two-way calls, forced TURN, codec negotiation and DTMF on a documented pilot browser matrix.
- [ ] #2 Prove independently attributable local/remote audio without duplication or echo and a 60-minute call with reconnect and credential refresh observations.
- [ ] #3 Demonstrate Speech-compatible audio conversion and both-speaker transcription; document unsupported cases and the selected adapter contract.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/25 (observed 2026-11-01T09:25:18Z; UTF-8 body SHA-256 bed76e701f3be3d81076903c7c3b322c4e6ad3150ef5d1b41f4d93d61b45204f). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
