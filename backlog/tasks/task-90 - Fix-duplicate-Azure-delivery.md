---
id: TASK-90
title: Fix duplicate Azure delivery
status: To Do
assignee: []
created_date: '2026-11-11T18:05:00Z'
updated_date: '2026-11-11T18:06:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/105
priority: low
type: bug
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: A repeated delivery can fail when an immutable image tag already exists because the ACR tag query expects objects but receives strings.

Issue: https://github.com/vkaam/phonebuddy/issues/105
Approved revision: 2026-11-11T18:04:24Z; body SHA-256 a8f1aa6aca896b074222f04e010eea6eb2c296d0d6825ceae38933a2abeceecb.
Approval evidence: The owner requested a low-priority follow-up in Codex on 2026-11-11.
Branch: agent/gh-105-duplicate-delivery
Scope: .github/workflows/azure-deploy.yml; tests/test_deployment_policy.py; tests/test_bicep_ci_boundary.py; backlog/tasks/task-90 - Fix-duplicate-Azure-delivery.md
Verify: python3 -B scripts/check.py; python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/azure-deploy.yml .github/workflows/pr-safety.yml. Record hosted duplicate-delivery evidence when Azure is available.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Duplicate delivery detects and reuses a matching immutable image after verification; writable or mismatched images fail closed.
- [ ] #2 An absent tag follows the normal publication path, with automated tests covering both lookup paths.
- [ ] #3 Relevant local and hosted checks pass and safe duplicate delivery evidence is recorded when Azure is available.
<!-- AC:END -->
