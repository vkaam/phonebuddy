---
id: TASK-25
title: Generate evidence-linked call summaries and action items
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - ai
  - backend
dependencies:
  - TASK-23
  - TASK-9
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After a call ends, a bounded Foundry workflow should turn its sealed transcript into reliable summaries without inventing decisions or assignments.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Durable summary requests and idempotent retries bind outputs to organization, call, transcript revision, prompt/schema and model versions; failures reach a visible retry/dead-letter state.
- [ ] #2 Validated structured output includes summary, decisions, open questions and suggested action items with supporting segments; unsupported owners/deadlines remain unset.
- [ ] #3 Incomplete and long transcripts, malicious spoken instructions, model outages and late transcript revisions have tested behavior; inference cannot execute call content as tool instructions.
- [ ] #4 A versioned Dutch/English evaluation set measures unsupported claims, action-item quality, latency and cost with human-scored examples.
<!-- AC:END -->
