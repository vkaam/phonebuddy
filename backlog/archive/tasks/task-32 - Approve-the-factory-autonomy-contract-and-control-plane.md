---
id: TASK-32
title: Approve the factory autonomy contract and control plane
status: To Do
assignee: []
created_date: '2026-10-31T18:39:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - factory
  - autonomy
  - historical-import
  - needs-triage
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/37
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/37 (observed 2026-11-01T09:52:42Z; UTF-8 body SHA-256 e89fb516577a1895faad3736db993a071936a91605451ac43357ba337c217deb). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates. Governance/runbook slices TASK-43 and TASK-44 are merged; owner/runtime/model/tenant/quota/budget decisions remain open in issue #37. Do not treat their completion as completion of this broad gate.
<!-- SECTION:NOTES:END -->
