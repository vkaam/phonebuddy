---
id: TASK-42
title: Qualify a narrowly approved development lane without per-PR human approval
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
  - TASK-64
  - TASK-40
  - TASK-41
references:
  - https://github.com/vkaam/phonebuddy/issues/47
documentation:
  - docs/autonomous-development-plan.md
priority: medium
type: task
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fully unattended development conflicts with the current mandatory human-review contract. Expanding authority requires a separate reviewed policy change and measured evidence; simply enabling native auto-merge cannot remove required approvals or supply domain correctness.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Maintainers explicitly approve eligible code classes, risk and cost limits, rollback expectations and the enforcement design before any no-human-approval lane is enabled; sensitive policy, identity, tenancy, telephony, retention, migrations, infrastructure and evaluation-threshold changes retain human review.
- [ ] #2 The policy design is compatible with branch-wide GitHub rules and cannot be simulated by blanket bypass or bot self-approval; ineligible changes and unavailable reviewers or evidence stop rather than silently widening scope.
- [ ] #3 After shadow evaluation and at least ten supervised eligible PRs, at least 90 percent require no manual code or prompt repair, all seeded critical defects and policy violations are blocked, and a seven-day bounded pilot records interventions, escaped defects, lead time and spend; owners review results before expansion.
- [ ] #4 A qualified allowed change completes Backlog to code, independent verification, PR, permitted merge, immutable deployment, health observation and completion without an operator prompt; an injected regression stops promotion or restores service through TASK-13 recovery, with release evidence reconciled to Backlog and no premature Done state.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/47 (observed 2026-11-01T09:53:10Z; UTF-8 body SHA-256 b5683e7002ce1180033fef0a4b5f8d5ec45e886142017d2f1cb7aa3d3abc45bb). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
