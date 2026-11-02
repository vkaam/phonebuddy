---
id: TASK-14
title: Provision SIP gateway and TURN infrastructure with Bicep
status: To Do
assignee: []
created_date: '2026-10-29T20:04:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-6
  - TASK-8
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The browser-to-SIP spike needs an always-on Azure media environment; this work can follow hosting without blocking initial delivery automation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bicep provisions gateway/relay compute, fixed addressing, bounded media ports, DNS/certificate prerequisites and private administration paths.
- [ ] #2 Gateway software/configuration are reproducible and versioned; provider secrets stay server-side and controlled tests do not require Fonzer.
- [ ] #3 A synthetic browser-to-SIP call verifies both media directions, forced TURN, TLS and restricted management access.
- [ ] #4 Updates drain new calls; active-call limitations and compatible image/configuration rollback are documented and tested.
<!-- AC:END -->
