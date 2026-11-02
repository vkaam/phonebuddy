---
id: TASK-39
title: Enforce factory budgets, durable audit evidence and operator controls
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - factory
  - autonomy
  - historical-import
  - needs-triage
dependencies:
  - TASK-32
  - TASK-35
  - TASK-36
references:
  - https://github.com/vkaam/phonebuddy/issues/44
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: feature
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Current evidence is temporary locally and retained for 14 days in CI. Unattended operation needs accountable ownership, recoverable records and enforced spend limits across model calls, compute and retries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Each run has durable access-controlled records linking task, specification, policy, model and prompt versions, source and artifact digests, tool decisions, checks, reviewer findings, PR and outcome, with tested redaction and approved retention and deletion.
- [ ] #2 Externally enforced per-run and aggregate token, cost, compute, wall-time and retry limits reject work before overspend; cancellation and a global stop revoke tools, terminate active work and prevent queued starts.
- [ ] #3 Metrics expose useful PR completion rate, interventions, repair attempts, queue age, cost and escaped defects; stuck runs, unavailable dependencies and evidence loss create deduplicated actionable alerts, while unchanged healthy state stays quiet.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/44 (observed 2026-11-01T09:26:17Z; UTF-8 body SHA-256 0f3d5a122e42a9f73addd56ef90a811a4f2991cdbc1c0ae87ee9af4f90e84080). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
