---
id: TASK-86
title: 'Issue 18 follow-up: Identify and fix Azure telemetry query failure'
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T12:57:00Z'
updated_date: '2026-11-11T13:06:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/18
  - https://github.com/vkaam/phonebuddy/pull/97
  - https://github.com/vkaam/phonebuddy/pull/98
  - https://github.com/vkaam/phonebuddy/pull/99
  - backlog/tasks/task-85
modified_files:
  - >-
    backlog/tasks/task-86 -
    Issue-18-follow-up-Identify-and-fix-Azure-telemetry-query-failure.md
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - docs/azure-delivery-policy.md
priority: high
type: bug
ordinal: 77000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Main deployment run 43022610694 applied Bicep and passed 100 version checks with 0.0% health errors and p95 266.375 ms, but workspace telemetry still failed. Retained evidence shows the Log Analytics CLI returned exit code 1 with category cli_error, no provider error code, and error_source stderr; recovery deactivated candidate revision ca-pb-dev-release-test--0000003. PR #99 expanded safe parsing to both output streams but did not identify or correct the underlying failure. Determine the response class/status from safe metadata, correct the live query or required in-scope integration, and prove telemetry passes on a source-bound main release.

Issue: https://github.com/vkaam/phonebuddy/issues/18
Approved revision: 2026-11-01T09:24:57Z; body SHA-256 eb438edc998e814bc7b7a9f879559a475e10b6ec63532edd171590ed8826e449.
Approval evidence: User explicitly authorized merging and fixing the deployed failure: “We can merge it and fix it if it fails there.”
Branch: agent/gh-18-4-live-telemetry-query-root-cause
Scope: scripts/health_gate.py; tests/test_health_gate.py; docs/azure-delivery-policy.md; this task's own CLI-managed record
Verify: python3 -B scripts/run_required_unittests.py; BICEP=/tmp/bicep python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/azure-deploy.yml .github/workflows/pr-safety.yml; hosted main CI and Azure release must prove exact-source Bicep deployment and a passing telemetry gate with at least 100 version-matched events and zero unhealthy events.
Change control: Further files or Azure RBAC changes require recorded triage and any required owner approval.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The real Azure CLI/query failure is identified and corrected based on observed provider response and the deployed workspace configuration.
- [ ] #2 Diagnostics expose safe, bounded response status/classification and never raw stderr/stdout, query text, workspace identifiers, or tokens.
- [ ] #3 Required local and PR checks pass, and a main-triggered exact-source release records at least 100 version-matched telemetry events with zero unhealthy events.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm the latest retained run shows a real stderr response and compare the current query, Bicep resource-specific log schema, and identity setup. 2. Add a bounded parser for safe HTTP status/response classes and documented Azure CLI error shapes, with tests that prove no raw output leaks. 3. Use the next source-bound deployment evidence to identify the exact provider failure; make the in-scope query/integration correction and regression tests, or record a separate triage task if evidence requires an out-of-scope Azure RBAC change. 4. Run required unit, Bicep, actionlint and live consistency checks; publish one PR and monitor checks. 5. After merge, verify the full main CI Bicep release gate passes with at least 100 version-matched events and zero unhealthy events.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Latest live evidence: run 43022610694 on main merge 12563888 passed source verification, artifact verification, Bicep compile/apply and 100 health requests (0.0% errors, p95 266.375 ms), then failed Log Analytics with exit code 1, category cli_error, error_code null, error_source stderr; candidate revision ca-pb-dev-release-test--0000003 was deactivated. The Bicep source configures azure-monitor with Dedicated routing; official schema docs identify ContainerAppConsoleLogs fields ContainerAppName and Log, matching the current query. The local environment has no Azure login, so root-cause proof must come from safe hosted diagnostics.

Added allowlisted numeric HTTP status extraction from both bounded CLI streams and fixed status-to-category mapping (authentication, authorization, missing resource, query rejection, throttling, timeout and provider error). No raw CLI output is retained. Focused suite passes (18 tests); repository suite passes (131 tests); Bicep checks, actionlint and diff check pass. The exact HTTP status from the live stderr is still unknown and the task remains active pending a main deployment.

Draft PR #100: https://github.com/vkaam/phonebuddy/pull/100, head 6823f95e70d078d31913535412eb461ca9a05f22. Hosted checks and the next main-triggered deployment are pending; this PR adds safe status evidence and does not claim the live query is fixed.
<!-- SECTION:NOTES:END -->
