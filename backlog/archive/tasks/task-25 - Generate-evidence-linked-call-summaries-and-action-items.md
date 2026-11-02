---
id: TASK-25
title: Generate evidence-linked call summaries and action items
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - ai
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-60
  - TASK-23
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/31
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/31 (observed 2026-11-01T09:25:36Z; UTF-8 body SHA-256 e9db93baea58bf6fb8c6a97b8673b116c583fd2da7e12113be4203045d2efd3c). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
