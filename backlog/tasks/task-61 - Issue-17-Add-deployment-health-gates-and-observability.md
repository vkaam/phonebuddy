---
id: TASK-61
title: Issue 17 - Add deployment health gates and observability
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-03T20:34:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/17
  - infra/hosting.bicep
  - infra/release-test/server.py
  - scripts/check_bicep.py
  - .github/workflows/azure-hosting-what-if.yml
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
  - tests/test_bicep_ci_boundary.py
  - tests/test_release_test.py
  - scripts/release_annotation.py
  - .github/workflows/azure-health-gate.yml
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - tests/test_release_annotation.py
modified_files:
  - >-
    backlog/tasks/task-61 -
    Issue-17-Add-deployment-health-gates-and-observability.md
  - infra/release-test/server.py
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - tests/test_release_test.py
  - infra/hosting.bicep
  - scripts/check_bicep.py
  - scripts/release_annotation.py
  - .github/workflows/azure-health-gate.yml
  - tests/test_bicep_ci_boundary.py
  - tests/test_release_annotation.py
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/17
Approved revision: 2026-11-01T09:24:54Z; body SHA-256 8d4a38d23215c8706bc19f086c585b9ebcafe76dfe747de51edbbbd35951d749.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-17-1-deployment-health-gates
Scope: infra/**; .github/workflows/**; scripts/**; tests/**; docs/quality-and-delivery.md; docs/azure-delivery-policy.md; backlog/tasks/task-61 - Issue-17-Add-deployment-health-gates-and-observability.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted pilot runs inject unhealthy responses and missing telemetry, confirm alerts/failure evidence, and confirm healthy version/readiness passes after warm-up.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Telemetry, release annotations and alerts are provisioned in Bicep without logging secrets or call content.
- [ ] #2 Bounded readiness and smoke checks verify the deployed version and essential paths after warm-up.
- [ ] #3 Document error and latency thresholds and observation windows; missing telemetry blocks promotion and dependency outages are distinguishable.
- [ ] #4 Injected unhealthy responses and missing telemetry trigger failure evidence and alerts; healthy workloads pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend the release-test workload with structured, bounded health telemetry that records only synthetic health events, response status, duration, and configured release version; never log request bodies, query strings, secrets, or call content.
2. Extend the hosting Bicep template with workspace-backed diagnostics, release metadata, and Azure Monitor alerts for missing telemetry, unhealthy responses, and latency, preserving opt-in workload creation and requiring no notification recipient until an owner configures one.
3. Add a bounded smoke/observation runner that waits for warm-up, verifies the expected version and required routes, checks sample count, 5-minute error rate and p95 latency over the documented 10-minute window, and fails closed on missing data or dependency outages.
4. Add a manually dispatched, read-only hosted workflow and deterministic tests for healthy, unhealthy, missing-telemetry, and dependency-outage cases.
5. Update delivery docs with thresholds, observation windows, alert semantics, and prerequisites; run the task verification commands and record which hosted Azure gates remain outstanding.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented structured health telemetry that excludes request lines, client addresses, query strings and bodies; added 30-day Log Analytics, Application Insights, Container Apps diagnostics, and Azure Monitor rules for missing telemetry, non-200 health responses, and p95 latency. Added the 60-second warm-up/10-minute dev-test gate, source-bound deployment annotations, and a manual main-only workflow that observes an existing deployment without deploying it. Live Backlog claim validation passed with claim_verified=true against origin/main; TASK-59 is completed. Verification on the implementation source: full local baseline passed (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-rwk2dj6b/report.json); pinned Bicep 0.34.44 validation passed; actionlint passed on all five workflows. The required hosted Azure checks have not run: the task's recorded approval explicitly excludes deployment, and no release-test workload has been deployed. No Azure resource was changed.
<!-- SECTION:NOTES:END -->
