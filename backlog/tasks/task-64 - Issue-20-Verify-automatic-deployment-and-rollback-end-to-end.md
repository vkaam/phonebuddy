---
id: TASK-64
title: Issue 20 - Verify automatic deployment and rollback end to end
status: To Do
assignee: []
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-02T16:36:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-60
  - TASK-62
  - TASK-63
references:
  - https://github.com/vkaam/phonebuddy/issues/20
priority: high
type: task
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The Azure delivery path needs live evidence that deployment and recovery work together.

Issue: https://github.com/vkaam/phonebuddy/issues/20
Approved revision: 2026-11-01T09:25:01Z; body SHA-256 88a3c7b29836e655a4c6ea7dfefa9b3f72fe56d90d240783a5d9a3a2d2f3c09f.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-20-1-deployment-recovery-verification
Scope: .github/workflows/**; infra/**; scripts/**; tests/**; docs/quality-and-delivery.md; docs/azure-delivery-policy.md; backlog/tasks/task-64 - Issue-20-Verify-automatic-deployment-and-rollback-end-to-end.md
Verify: From repository root run python3 -B scripts/check.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Run the controlled Azure end-to-end deployment/recovery drills, retain source/artifact/run links and measured recovery evidence, and document any environment prerequisite that prevents a drill.
Spec: Preserve issue #20's approved acceptance. External Azure and hosted checks are explicit gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A controlled default-branch change deploys automatically and exposes the expected version with retained source/artifact/run evidence.
- [ ] #2 An unhealthy candidate rolls back to the prior healthy release within a documented measured recovery target.
- [ ] #3 Concurrent releases, first-release failure, denied credentials, partial infrastructure failure and missing telemetry have demonstrated safe outcomes with stateful data preserved.
- [ ] #4 Runbooks cover bootstrap, recovery, backup restore drills, escalation, evidence retention and cost; remaining blocked checks are explicit.
<!-- AC:END -->
