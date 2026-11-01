---
id: TASK-32
title: Approve the factory autonomy contract and control plane
status: To Do
assignee: []
created_date: '2026-10-31T18:39:00Z'
updated_date: '2026-10-31T18:44:00Z'
labels:
  - factory
  - autonomy
dependencies: []
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: docs
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The software plan proposes Azure DevOps while the implemented delivery baseline uses GitHub. Unattended work needs one authoritative queue, explicit eligible change classes, and an agreed boundary between delegated work and decisions requiring an owner.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A reviewed decision identifies the source of truth, factory runtime, initial coding and review model access, responsible owner, and unresolved tenant, region, quota, and budget inputs.
- [ ] #2 The contract defines eligible tasks, trusted instructions, allowed tools and paths, approval boundaries, stop and resume rules, and escalation ownership; unknown scope is ineligible.
- [ ] #3 The contract separates unattended PR creation, merging after human approval, and any future merging without per-PR human approval; existing restrictions remain in force until separately revised.
- [ ] #4 The bootstrap runbook records build and test commands, trusted project instructions, architecture-context sources and Groma scanner coverage; any first-scan curation follows the required user decision and uses the Groma CLI.
<!-- AC:END -->
