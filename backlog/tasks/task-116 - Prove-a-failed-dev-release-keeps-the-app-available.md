---
id: TASK-116
title: Prove a failed dev release keeps the app available
status: To Do
assignee: []
created_date: '2026-11-19T04:16:00Z'
labels: []
dependencies:
  - TASK-94
priority: medium
type: bug
ordinal: 99000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/110
Branch: agent/gh-110-2-failed-release-availability
Scope: .github/workflows/azure-deploy.yml; scripts/deployment_policy.py; scripts/release_recovery.py; tests/test_deployment_policy.py; tests/test_bicep_ci_boundary.py; docs/azure-delivery-policy.md
Verify: python3 -B scripts/run_required_unittests.py; a controlled failed or partial trusted dev release (or retained evidence of one) showing the recovery path ran and the dev app kept serving a healthy version-matched release.

Split from TASK-94 on 2026-11-19 after its PR (#112) merged. The other criteria are evidenced by later releases. The only failed release since then (run 43305635770, 12 Nov, attempt 3) failed while persisting the candidate to Blob Storage, then alerted and isolated the candidate because no safe fallback existed. The run evidence does not show whether the dev app stayed available, so this criterion is unproven.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A failed or partial release follows a tested recovery path that does not leave the dev app unavailable.
<!-- AC:END -->
