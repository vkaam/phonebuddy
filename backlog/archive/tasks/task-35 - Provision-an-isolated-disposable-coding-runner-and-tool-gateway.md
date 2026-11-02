---
id: TASK-35
title: Provision an isolated disposable coding runner and tool gateway
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
references:
  - https://github.com/vkaam/phonebuddy/issues/40
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: task
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The planned Azure sandbox and coding model are not implemented in this repository. Repository code must be executable without inheriting the interactive developer session, production credentials, or unrestricted repository authority.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A versioned provisioning path creates a disposable runner from a pinned source commit and toolchain, proves the selected model can edit and test a bounded change through allowed tools, and destroys the runner after retaining evidence.
- [ ] #2 Enforced network, filesystem and identity boundaries deny production data, deployment permissions, repository policy changes and credential access; narrowly scoped repository and model actions use revocable short-lived authorization outside the checkout.
- [ ] #3 Process-tree deadlines, resource quotas and cancellation terminate child processes; crash and cancellation tests demonstrate cleanup of runners, credentials and temporary data with auditable outcomes.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/40 (observed 2026-11-01T09:26:03Z; UTF-8 body SHA-256 a7b3ff64dae5fa64a6ac434eb09fb88a586143117e9c3d922083634c08ecabae). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
