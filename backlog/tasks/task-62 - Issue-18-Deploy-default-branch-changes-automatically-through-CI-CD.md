---
id: TASK-62
title: Issue 18 - Deploy default-branch changes automatically through CI/CD
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-11T09:15:00Z'
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
  - tests/test_bicep_ci_boundary.py
  - tests/test_health_gate.py
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
- [ ] #1 Default-branch updates trigger exact-SHA validation, immutable build artifacts, applicable Bicep deployment, application release and health-gated promotion.
- [ ] #2 Artifacts and configuration are versioned and promoted without rebuilding; failed or stale CI cannot authorize deployment.
- [ ] #3 Deployments serialize per environment, prevent older releases overwriting newer ones and avoid unsafe in-flight cancellation.
- [ ] #4 Failure halts promotion and invokes recovery; duplicate triggers, concurrent pushes and partial deployment are tested.
- [ ] #5 Document repository and environment settings enabling deployment without an extra routine manual release approval.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current CI, Bicep hosting template, application build, OIDC workflow, health gate, and delivery policy to find the smallest complete main-to-release path consistent with the approved issue. 2. Add a main-only exact-SHA deployment workflow that waits for successful required Quality evidence, builds and identifies immutable application artifacts once, serializes environment releases, deploys applicable Bicep and the same artifact through OIDC, and gates promotion on readiness and telemetry. 3. Add deterministic coverage for stale or failed CI, duplicate and concurrent triggers, immutable artifact promotion, deployment failure, health failure, and recovery behavior within the approved paths. 4. Document required GitHub environment, identity, and repository settings and run the task's local verification commands. 5. Publish a draft PR and verify all hosted checks on its current head; leave live Azure deployment evidence and any unavailable environment prerequisites explicit.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Draft PR #97: https://github.com/vkaam/phonebuddy/pull/97. The source implementation at ad17d462897dedb0b24979edd9bab3dc47f2edca has hosted Quality, the explicit non-main release-image no-op, and advisory Risk report all passing. Local Bicep baseline, actionlint, focused boundary tests, and diff checks pass; the local browser suite could not launch because libnspr4.so is missing, but the hosted Quality browser suite passed. Remaining delivery gates: review/merge, a configured dev environment and registry-scoped AcrPush role, and a successful health/telemetry gate. Health run 42984895566 passed 100 request probes (0% errors, p95 325ms) but failed closed when the Log Analytics CLI query returned cli_error with zero telemetry rows. No CI Azure deployment has occurred yet.
<!-- SECTION:NOTES:END -->
