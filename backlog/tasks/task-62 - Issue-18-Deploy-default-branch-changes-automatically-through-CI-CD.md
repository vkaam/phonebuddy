---
id: TASK-62
title: Issue 18 - Deploy default-branch changes automatically through CI/CD
status: Done
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-12T07:28:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-57
  - TASK-58
  - TASK-59
  - TASK-61
references:
  - https://github.com/vkaam/phonebuddy/issues/18
  - .github/workflows/ci.yml
  - infra/hosting.bicep
  - scripts/check_bicep.py
  - scripts/health_gate.py
  - infra/release-test/Dockerfile
  - infra/github-oidc.md
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
modified_files:
  - >-
    backlog/tasks/task-62 -
    Issue-18-Deploy-default-branch-changes-automatically-through-CI-CD.md
  - .github/workflows/ci.yml
  - .github/workflows/azure-deploy.yml
  - infra/hosting.bicep
  - scripts/check_bicep.py
  - scripts/health_gate.py
  - scripts/deployment_policy.py
  - tests/test_bicep_ci_boundary.py
  - tests/test_health_gate.py
  - tests/test_deployment_policy.py
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
  - infra/github-oidc.md
priority: high
type: task
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/18
Approved revision: 2026-11-01T09:24:57Z; body SHA-256 eb438edc998e814bc7b7a9f879559a475e10b6ec63532edd171590ed8826e449.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-18-1-automatic-app-deployment
Scope: .github/workflows/**; apps/web/**; infra/**; scripts/**; tests/**; docs/quality-and-delivery.md; docs/azure-delivery-policy.md; backlog/tasks/task-62 - Issue-18-Deploy-default-branch-changes-automatically-through-CI-CD.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted default-branch runs must prove exact-SHA authorization, immutable artifact promotion, serialized environment deployments, health-gated release, failure stop/recovery and safe duplicate/concurrent trigger behavior.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Default-branch updates trigger exact-SHA validation, immutable build artifacts, applicable Bicep deployment, application release and health-gated promotion.
- [x] #2 Artifacts and configuration are versioned and promoted without rebuilding; failed or stale CI cannot authorize deployment.
- [x] #3 Deployments serialize per environment, prevent older releases overwriting newer ones and avoid unsafe in-flight cancellation.
- [x] #4 Failure halts promotion and invokes recovery; duplicate triggers, concurrent pushes and partial deployment are tested.
- [x] #5 Document repository and environment settings enabling deployment without an extra routine manual release approval.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current CI, Bicep hosting template, application build, OIDC workflow, health gate, and delivery policy to find the smallest complete main-to-release path consistent with the approved issue. 2. Add a main-only exact-SHA deployment workflow that waits for successful required Quality evidence, builds and identifies immutable application artifacts once, serializes environment releases, deploys applicable Bicep and the same artifact through OIDC, and gates promotion on readiness and telemetry. 3. Add deterministic coverage for stale or failed CI, duplicate and concurrent triggers, immutable artifact promotion, deployment failure, health failure, and recovery behavior within the approved paths. 4. Document required GitHub environment, identity, and repository settings and run the task's local verification commands. 5. Publish a draft PR and verify all hosted checks on its current head; leave live Azure deployment evidence and any unavailable environment prerequisites explicit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Draft PR #97: https://github.com/vkaam/phonebuddy/pull/97. Current source head b0def7c5fb9b819579a0aa7e316e69d3347f4ef7 passed hosted Quality, the non-main release-image no-op, and advisory Risk report. The required 128-test suite, Bicep baseline, actionlint, and diff checks pass locally. Executable policy tests cover current-main freshness, exact run/attempt artifact provenance, locked-image reuse for duplicate triggers, and recovery decisions; recovery selects only the active revision for the failed source version. The health query filters health_request events before parsing. Latest live health run 42984895566 predates the query change and failed closed with Log Analytics cli_error after request probes passed. Current Azure telemetry behavior and CI-driven Bicep deployment remain unverified. Remaining gates: human review/merge, dev OIDC settings, registry-scoped AcrPush, and a successful main CI deploy and health gate.

Post-merge verification against source 4d4003a87944a47da9240b0e479c043a7f6cef25 confirmed main CI and the first trusted Azure release succeeded. Same-source duplicate attempts 2 and 3 reused locked image sha256:01fc61298e6f9c4893618e2a89c51bc37bfdc2d2dad7491028dac21c1d7b94c3 without rebuilding, but both failed the live HTTP gate (attempt 2: 3 dependency outages / 3% errors; attempt 3: 100 unhealthy responses). Attempt 2 isolated its candidate; attempt 3 found no active candidate, and subsequent read-only probes returned Azure Container App unavailable/404 for /ready and /. The live duplicate-success gate remains unproven; keep TASK-62 open pending remediation and a passing same-source duplicate verification tracked by https://github.com/vkaam/phonebuddy/issues/110.

Post-merge operational evidence on dd5a0cfe420db5897506a48b0c191fc925918c79: main CI run 43170455805 passed; trusted Azure release run 43170616234 attempts 1 and 2 passed the 100-request, 10-window, 600-second gate with 0% errors, no version mismatch or dependency failures, and source-bound retained artifacts. The same locked image digest sha256:fb8824a63cf872a5c2ce546942ea05aa08328ba71cd5d0ae7f94c7323443ef99 was reused by attempt 2 without rebuilding/pushing; workflow output confirms it matched the immutable CI artifact. Failure recovery regression coverage and the Single-mode revision fix merged in PR #112. Issue #18 was updated; finalization is pending independent review and PR #111 merge.

Independent review confirmed all five original criteria are supported. Issue #18 requirements were left unchanged; progress comments record main CI run 43170455805 and Azure release run 43170616234 attempts 1/2. Task-92 PR #111 contains the acceptance and evidence reconciliation; its hosted checks passed before finalization.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed the approved default-branch CI/CD release path and reconciled its post-merge evidence. Exact-source CI and the trusted dev deployment passed; the same-source duplicate reused the locked image digest and passed the full health gate. Serialization, stale-source, failure/recovery regression tests, documentation, independent acceptance review, and linked issue progress are recorded.
<!-- SECTION:FINAL_SUMMARY:END -->
