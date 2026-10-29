---
id: TASK-18
title: Prove browser SIP calling and per-leg audio capture
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - telephony
  - spike
dependencies:
  - TASK-14
  - TASK-9
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
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
