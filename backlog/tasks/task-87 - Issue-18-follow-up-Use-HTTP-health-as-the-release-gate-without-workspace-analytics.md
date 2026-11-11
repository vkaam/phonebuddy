---
id: TASK-87
title: Keep workspace analytics out of the pilot release gate
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T13:31:00Z'
updated_date: '2026-11-11T14:16:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/101
  - https://github.com/vkaam/phonebuddy/issues/18
  - https://github.com/vkaam/phonebuddy/pull/100
  - https://github.com/vkaam/phonebuddy/actions/runs/43027064165
  - docs/azure-delivery-policy.md
  - docs/issue-backlog-governance.md
  - >-
    backlog/archive/tasks/task-84 -
    Issue-18-follow-up-Fix-live-Azure-telemetry-gate-and-verify-release.md
  - >-
    backlog/archive/tasks/task-85 -
    Issue-18-follow-up-Fix-live-Azure-telemetry-query.md
  - >-
    backlog/archive/tasks/task-86 -
    Issue-18-follow-up-Identify-and-fix-Azure-telemetry-query-failure.md
modified_files:
  - >-
    backlog/tasks/task-87 -
    Issue-18-follow-up-Use-HTTP-health-as-the-release-gate-without-workspace-analytics.md
  - >-
    backlog/tasks/task-84 -
    Issue-18-follow-up-Fix-live-Azure-telemetry-gate-and-verify-release.md
  - >-
    backlog/archive/tasks/task-84 -
    Issue-18-follow-up-Fix-live-Azure-telemetry-gate-and-verify-release.md
  - backlog/tasks/task-85 - Issue-18-follow-up-Fix-live-Azure-telemetry-query.md
  - >-
    backlog/archive/tasks/task-85 -
    Issue-18-follow-up-Fix-live-Azure-telemetry-query.md
  - >-
    backlog/tasks/task-86 -
    Issue-18-follow-up-Identify-and-fix-Azure-telemetry-query-failure.md
  - >-
    backlog/archive/tasks/task-86 -
    Issue-18-follow-up-Identify-and-fix-Azure-telemetry-query-failure.md
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - .github/workflows/azure-deploy.yml
  - .github/workflows/ci.yml
  - docs/azure-delivery-policy.md
priority: high
type: bug
ordinal: 78000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Four source-bound Azure release attempts applied Bicep and passed 100 version-matched HTTP health requests, but the Log Analytics CLI query failed and prevented release promotion. The owner has directed that workspace analytics not block this product-focused pilot for now. Preserve readiness and HTTP health gating while removing the required Log Analytics query from release acceptance, and reconcile the superseded diagnostic task records.

Issue: https://github.com/vkaam/phonebuddy/issues/101
Approved requirements revision: 2026-11-11T13:34:38Z; body SHA-256 7d9c56e9a2a30974e203e405f91b28e7bd8db43537213161e1d779db0e0bcabf.
Approval evidence: The owner directed: “I think we can just skip the log analytics cli check. We are not really interested in analytics for now anyways. We want to focus on product.” New Issue #101 records this direction. Original Issue #18 remains unchanged. This changes the release gate only; exact-source authorization, Bicep and HTTP readiness/health checks remain required.
Scope amendment (2026-11-11): The owner approved adding .github/workflows/ci.yml to address long waits caused by network-dependent browser dependency setup. See Issue #101 comments 6798126113 and 6798131856.
Branch: agent/gh-18-5-http-only-release-health-gate
Scope: scripts/health_gate.py; tests/test_health_gate.py; .github/workflows/azure-deploy.yml; .github/workflows/ci.yml; docs/azure-delivery-policy.md; backlog/tasks/task-84 - Issue-18-follow-up-Fix-live-Azure-telemetry-gate-and-verify-release.md; backlog/archive/tasks/task-84 - Issue-18-follow-up-Fix-live-Azure-telemetry-gate-and-verify-release.md; backlog/tasks/task-85 - Issue-18-follow-up-Fix-live-Azure-telemetry-query.md; backlog/archive/tasks/task-85 - Issue-18-follow-up-Fix-live-Azure-telemetry-query.md; backlog/tasks/task-86 - Issue-18-follow-up-Identify-and-fix-Azure-telemetry-query-failure.md; backlog/archive/tasks/task-86 - Issue-18-follow-up-Identify-and-fix-Azure-telemetry-query-failure.md; backlog/tasks/task-87 - Issue-18-follow-up-Use-HTTP-health-as-the-release-gate-without-workspace-analytics.md.
Verify: python3 -B scripts/run_required_unittests.py; BICEP=/tmp/bicep python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/azure-deploy.yml .github/workflows/pr-safety.yml; git diff --check; hosted main CI and Azure deployment must prove exact-source artifact identity, Bicep apply, 100 version-matched healthy HTTP requests, and release annotation without requiring Log Analytics query success. CI browser validation remains required and must not wait on long package-manager retries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A main release is gated by exact-source CI, Bicep apply, readiness, and at least 100 version-matched HTTP health requests with zero unhealthy responses and within the documented latency/error limits; Log Analytics CLI failure or missing analytics events do not block promotion.
- [ ] #2 Regression tests prove HTTP health failures still block promotion and trigger candidate-only recovery, while analytics query availability is not a release prerequisite.
- [ ] #3 Required local and hosted checks pass, and a main-triggered exact-source deployment records Bicep and HTTP health evidence plus a successful release annotation without a required Log Analytics query.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the deployment workflow, health-gate interface, tests and docs to map where Log Analytics is a release prerequisite.
2. Remove the workspace query from the main deployment decision path while preserving source verification, Bicep apply, readiness, HTTP sample thresholds, error-rate and latency gates, and candidate-only recovery.
3. Update regression coverage and delivery docs to state exactly which HTTP checks still gate promotion and that workspace analytics is deferred.
4. Run required unit, Bicep, actionlint, diff and live consistency checks; commit the scoped task branch and open one PR.
5. After merge, verify a main-triggered source-bound deployment completes Bicep apply, passes the full HTTP observation window, writes its release annotation, and retains evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Correction: tests/test_bicep_ci_boundary.py protects the standalone azure-health-gate.yml workflow, which remains outside the main CI release gate and is unchanged. No scope addition or edit to that file is needed.

Implemented the HTTP-only main release profile: health_gate.py accepts --skip-workspace-telemetry; azure-deploy.yml no longer lists the workspace or stores its ID artifact and passes that fixed flag; the manual azure-health-gate.yml workflow still retains its independent analytics query. Documentation distinguishes the main release gate from the manual analytics observation. Focused health-gate suite passes 20 tests; full unit, Bicep, actionlint, diff and hosted verification remain pending.

Required local verification after the HTTP-only changes: repository Python suite passed 134 tests; Bicep baseline checks passed; actionlint 1.7.12 passed using the CI-pinned binary verified against its SHA-256; git diff --check passed; live TASK-87 consistency guard passed with claim_verified=true on origin/main 8c23918. Hosted PR and post-merge release evidence remain pending.

PR #102: https://github.com/vkaam/phonebuddy/pull/102. Branch agent/gh-18-5-http-only-release-health-gate is published with commit 52466ad. PR is ready for review/checks; TASK-87 remains active until hosted main release evidence records passing HTTP health and annotation.

Owner-approved scope amendment added .github/workflows/ci.yml. CI run 43034054328 completed the web install, lint, unit tests and build, then stalled in Playwright --with-deps while apt could not resolve azure.archive.ubuntu.com; the job's 10-minute cap cancelled the step. Updated CI to install only the Chromium headless shell, avoiding network-dependent apt package retries while retaining the required browser test. Hosted validation pending.
<!-- SECTION:NOTES:END -->
