---
id: TASK-94
title: Restore live dev health after repeated Azure release runs
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-12T06:13:00Z'
updated_date: '2026-11-12T06:42:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/110
  - https://github.com/vkaam/phonebuddy/issues/18
  - https://github.com/vkaam/phonebuddy/issues/105
  - https://github.com/vkaam/phonebuddy/actions/runs/43160100893
  - >-
    https://github.com/vkaam/phonebuddy/actions/runs/43160100893/artifacts/13919473233
  - scripts/deployment_policy.py
  - .github/workflows/azure-deploy.yml
  - tests/test_deployment_policy.py
  - tests/test_bicep_ci_boundary.py
  - https://github.com/vkaam/phonebuddy/pull/112
modified_files:
  - >-
    backlog/tasks/task-94 -
    Restore-live-dev-health-after-repeated-Azure-release-runs.md
  - scripts/deployment_policy.py
  - tests/test_deployment_policy.py
  - .github/workflows/azure-deploy.yml
  - tests/test_bicep_ci_boundary.py
  - docs/azure-delivery-policy.md
  - infra/hosting.bicep
priority: low
type: bug
ordinal: 83000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: A repeated same-source Azure release left the dev Container App unavailable after the health gate failed, blocking the required live duplicate verification for TASK-62.

Issue: https://github.com/vkaam/phonebuddy/issues/110
Approved revision: 2026-11-12T06:08:22Z; body SHA-256 850c8ce825bcbad1d8d4451a589ae6eaa04a580f4579f44727e1424e1a6d2ecb.
Approval evidence: The user requested completion of TASK-62 and had already authorized post-merge duplicate verification; repository governance requires a linked issue and native task for post-merge failures. Incident evidence is in Azure release run 43160100893 attempts 2 and 3 and retained artifacts 13919595198 and 13919473233.
Branch: agent/gh-110-1-restore-live-dev-health
Scope: .github/workflows/azure-deploy.yml; infra/hosting.bicep; scripts/deployment_policy.py; scripts/health_gate.py; tests/test_bicep_ci_boundary.py; tests/test_deployment_policy.py; tests/test_health_gate.py; docs/azure-delivery-policy.md; backlog/tasks/task-94 - Restore-live-dev-health-after-repeated-Azure-release-runs.md.
Verify: python3 -B scripts/check.py; python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml .github/workflows/azure-deploy.yml; hosted PR Quality; trusted main CI and Azure deployment including the same-source duplicate release and retained health evidence.
Spec: Preserve the approved issue #18 acceptance criteria. Keep deployment fail-closed and preserve immutable image reuse. Do not claim the app is restored until the current dev endpoint and trusted health gate pass.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The dev app serves version-matched readiness and root responses after a release.
- [ ] #2 A trusted same-source duplicate Azure release reuses the existing locked image digest without rebuilding or pushing and passes the 100-request, 10-minute health gate.
- [ ] #3 A failed or partial release follows a tested recovery path that does not leave the dev app unavailable.
- [ ] #4 Relevant local and hosted checks pass, and deployment and health evidence is retained and source-bound.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect app routing, Bicep revision settings, deployment/recovery code, and run 43160100893 attempts 1-3 to identify why recovery left the dev app unavailable. 2. Use Azure Container Apps Single-mode behavior to deploy a unique revision per trusted workflow attempt, verify the exact source/image revision becomes active, and keep recovery from deactivating the active revision; add deterministic regression coverage. 3. Run local tests, Bicep validation and workflow lint, then verify hosted PR checks. 4. Merge only after independent review and required checks pass; observe main CI and the trusted Azure release, then record a passing same-source duplicate health gate before resuming TASK-92/TASK-62.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementation now gives every trusted Azure workflow attempt a unique Bicep Container Apps revision suffix. The workflow validates an active revision bound to the exact source SHA and locked image digest, and recovery records state without manual revision activation/deactivation. Bicep validation passed with 0.34.44 and 0.49.2. Required unittest suite passed: 147 tests, 0 skipped when Git Bash and a temporary python3 shim were available. Full check.py remains platform-inconclusive on Windows because npm command resolution fails in its subprocess runner; hosted PR checks remain required.

Published draft PR #112 at https://github.com/vkaam/phonebuddy/pull/112 from head de74371e9188ed0d29d7d2858c36f8964c6ea668; origin/main remains an ancestor. Independent review and hosted checks are pending; the PR intentionally remains draft until those gates complete.

Independent review found that exact-revision verification failures skipped recovery evidence. Fixed by passing the verification step outcome into recovery-required; verification failure now triggers recovery even when health observation is skipped. Added a regression test; focused suites pass and the full required unittest suite passes (147, 0 skipped). Independent re-review and updated hosted checks are pending.
<!-- SECTION:NOTES:END -->
