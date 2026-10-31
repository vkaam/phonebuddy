---
id: TASK-42
title: Qualify a narrowly approved development lane without per-PR human approval
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
labels:
  - factory
  - autonomy
dependencies:
  - TASK-13
  - TASK-40
  - TASK-41
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
