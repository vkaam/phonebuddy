---
id: TASK-84
title: 'Issue 18 follow-up: Fix live Azure telemetry gate and verify release'
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T10:33:00Z'
updated_date: '2026-11-11T13:39:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/18
  - https://github.com/vkaam/phonebuddy/pull/97
  - >-
    backlog/tasks/task-62 -
    Issue-18-Deploy-default-branch-changes-automatically-through-CI-CD.md
modified_files:
  - >-
    backlog/tasks/task-84 -
    Issue-18-follow-up-Fix-live-Azure-telemetry-gate-and-verify-release.md
  - scripts/health_gate.py
  - tests/test_health_gate.py
priority: high
type: bug
ordinal: 75000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The first CI-driven release from merged PR #97 completed CI, exact-image promotion, Bicep what-if and apply, but the release health gate failed during telemetry observation. Retained evidence for run 43001834438 records 100 successful health requests, 0.0% errors and p95 latency 276.474 ms; the Log Analytics query returned cli_error with exit code 1 and zero events. The workflow safely deactivated only the candidate revision. Identify and fix the live query failure, then prove the corrected release gate on main. This follow-up is split from TASK-62 because that task already maps to the merged PR #97.

Issue: https://github.com/vkaam/phonebuddy/issues/18
Approved revision: 2026-11-01T09:24:57Z; body SHA-256 eb438edc998e814bc7b7a9f879559a475e10b6ec63532edd171590ed8826e449.
Approval evidence: The user explicitly authorized fixing failures from the merged deployment in this Codex conversation on 2026-11-11: “We can merge it and fix it if it fails there.”
Branch: agent/gh-18-2-telemetry-gate-fix
Scope: scripts/health_gate.py; tests/test_health_gate.py; .github/workflows/azure-deploy.yml; docs/azure-delivery-policy.md; backlog/tasks/task-84 - Issue-18-follow-up-Fix-live-Azure-telemetry-gate-and-verify-release.md
Verify: python3 -B scripts/run_required_unittests.py; BICEP=/tmp/bicep python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/azure-deploy.yml .github/workflows/pr-safety.yml; hosted main CI and Azure release deployment must prove the exact source-bound artifact deploys and the telemetry gate passes.

Replaced by: TASK-87
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The root cause of the Azure Log Analytics telemetry query failure is identified and corrected; the release health gate observes at least 100 version-matched health events with zero unhealthy events after the full observation window.
- [ ] #2 Query failure diagnostics remain bounded and secret-free, and any failed observation triggers recovery of only the candidate revision with retained evidence.
- [ ] #3 Required local checks and hosted checks pass on the final task branch, and a main-triggered CI deployment records source, artifact, Bicep, readiness and telemetry evidence.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the failed run’s retained evidence and the live health-query implementation; determine the exact Azure CLI failure cause without exposing raw credentials or caller data.
2. Correct the KQL/CLI integration and improve bounded, secret-free failure classification, with regression tests.
3. Run the required unit, Bicep and actionlint checks, plus relevant workflow/policy checks.
4. Commit and push the task branch, open a PR against main, and monitor all checks on the current head.
5. After merge, verify the source-bound CI deployment and successful full-window readiness and telemetry gate; retain the evidence and keep this task active until verified.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Live deployment attempt 43001834438 (main merge commit e0a6f7148ca3d7913052d1798bce3ccc4e63d778) passed exact-source validation, artifact download/integrity, Bicep compile, OIDC login, ACR digest promotion, what-if and apply. The 600-second health window had 100 successful version checks, 0.0% errors and p95 276.474 ms; telemetry query failed with generic cli_error/exit 1 and zero events. Recovery safely deactivated candidate revision ca-pb-dev-release-test--0000001; retained artifact 13847172636. Existing report intentionally discarded raw stderr, so the underlying query failure is not yet identified. Added bounded provider error-code extraction (no raw stderr, query, IDs or token values) and regression coverage; 129 required unit tests pass, Bicep baseline passes, actionlint and diff checks pass. Next: publish this diagnostic change and use the retained report from the next authorized main deployment to identify the exact provider error before changing query behavior.

Replaced by: TASK-87. The owner redirected the release-gate requirement to HTTP readiness/health only; the merged diagnostic PR remains historical evidence, but the analytics-query acceptance is no longer the selected outcome.
<!-- SECTION:NOTES:END -->
