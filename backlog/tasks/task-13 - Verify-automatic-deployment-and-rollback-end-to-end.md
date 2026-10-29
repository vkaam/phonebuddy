---
id: TASK-13
title: Verify automatic deployment and rollback end to end
status: To Do
assignee: []
created_date: '2026-10-29T20:04:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-9
  - TASK-11
  - TASK-12
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The infrastructure milestone needs live Azure evidence that deployment and recovery work together.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A controlled default-branch change deploys automatically and exposes the expected version with retained source/artifact/run evidence.
- [ ] #2 An unhealthy candidate rolls back to the prior healthy release within a documented measured recovery target.
- [ ] #3 Concurrent releases, first-release failure, denied credentials, partial infrastructure failure and missing telemetry have demonstrated safe outcomes with stateful data preserved.
- [ ] #4 Runbooks cover bootstrap, recovery, backup restore drills, escalation, evidence retention and cost; remaining blocked checks are explicit.
<!-- AC:END -->
