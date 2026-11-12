---
id: TASK-92
title: Verify live duplicate Azure delivery
status: To Do
assignee: []
created_date: '2026-11-11T18:34:00Z'
updated_date: '2026-11-11T18:34:00Z'
labels: []
dependencies:
  - TASK-90
references:
  - https://github.com/vkaam/phonebuddy/issues/105
priority: low
type: task
ordinal: 82000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The main-only release workflow cannot exercise the proposed duplicate-image fix against Azure before it merges. Verify safe duplicate delivery of the merged source and reconcile TASK-62 only after its original criteria are proven.

Issue: https://github.com/vkaam/phonebuddy/issues/105
Approved revision: 2026-11-11T18:04:24Z; body SHA-256 a8f1aa6aca896b074222f04e010eea6eb2c296d0d6825ceae38933a2abeceecb.
Approval evidence: The owner approved splitting the fix from post-merge live verification on 2026-11-11; see https://github.com/vkaam/phonebuddy/issues/105#issuecomment-6804113134.
Branch: agent/gh-105-duplicate-delivery-verification
Scope: backlog/tasks/task-92 - Verify-live-duplicate-Azure-delivery.md; backlog/tasks/task-62 - Issue-18-Deploy-default-branch-changes-automatically-through-CI-CD.md
Verify: python3 -B scripts/check.py; python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml; inspect main-triggered CI and Azure release runs including a safe duplicate delivery and retained evidence. Preserve TASK-62 acceptance and do not claim unverified concurrent or failure behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A main-triggered duplicate delivery safely reuses the matching locked image without rebuilding and retains source-bound deployment and health evidence.
- [ ] #2 TASK-62 acceptance is independently validated against the original requirements and evidence, with any missing criteria left open.
- [ ] #3 Required checks, review and issue/task reconciliation are recorded; TASK-62 is finalized only when every original gate is proven.
<!-- AC:END -->
