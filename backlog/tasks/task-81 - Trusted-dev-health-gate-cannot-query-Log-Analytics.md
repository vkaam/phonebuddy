---
id: TASK-81
title: Trusted dev health gate cannot query Log Analytics
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-10T20:46:00Z'
updated_date: '2026-11-10T20:51:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/92
  - scripts/health_gate.py
  - tests/test_health_gate.py
modified_files:
  - >-
    backlog/tasks/task-81 -
    Trusted-dev-health-gate-cannot-query-Log-Analytics.md
  - scripts/health_gate.py
  - tests/test_health_gate.py
priority: high
type: bug
ordinal: 73000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/92

Approved requirements revision: 2026-11-10T17:28:23Z; SHA-256 of UTF-8 issue body d50d4126742aaba1b05f78c0973f9a3a3eddc2aa55851b8a69ff709e6fc31c5c
Approver: Human requester in the current conversation, treated as the authorized issue owner for this interactive triage.
Approval evidence: Direct human instruction in this conversation on 2026-11-10 to fix issue #92; this approves the issue's proposed acceptance criteria as the scope for this execution slice.

Branch: agent/gh-92-1-trusted-dev-health-gate
Scope: .github/workflows/azure-health-gate.yml; scripts/health_gate.py; tests/test_health_gate.py; tests/test_bicep_ci_boundary.py; this task's own CLI-managed record
Verify: From repository root run python3 -B -m unittest discover -s tests -p 'test_health_gate.py'; python3 -B scripts/quality.py; then run the trusted post-merge dev workflow on main and retain evidence of 100 successful requests, at least 100 version-matched workspace events under the dev GitHub app identity, and a verified source-bound Application Insights annotation. The PR Quality check must also pass.
Spec: Diagnose the hosted Log Analytics query failure with a bounded redacted diagnostic, fix the query path so the trusted dev gate succeeds, and preserve fail-closed handling for missing telemetry, unhealthy events, and dependency errors. Do not expose tokens, query contents, call data, or secrets. Any Azure permission change remains narrowly scoped to the dev workspace and requires explicit owner approval before granting it. Azure RBAC changes are external to this repository task and require a separately approved owner operation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Hosted query failures produce bounded redacted diagnostics without exposing tokens, query contents, call data, or secrets.
- [ ] #2 The trusted main-only dev gate records 100 successful readiness requests and at least 100 version-matched workspace events under the dev GitHub app identity.
- [ ] #3 Missing telemetry, unhealthy events, and dependency errors continue to fail closed; successful runs create and verify a source-bound Application Insights release annotation.
- [ ] #4 Focused local tests and Quality pass, and a trusted post-merge dev run passes with its evidence recorded.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reproduce and isolate the Log Analytics CLI failure while inspecting only bounded diagnostic metadata. 2. Adjust the query execution path and emit a safe redacted diagnostic without changing fail-closed decisions. 3. Add focused tests for success, query failure, redaction, missing telemetry, unhealthy events, and workflow annotation gating. 4. Run focused tests and Quality, then publish a PR and record the trusted post-merge dev run as an external acceptance gate.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Focused verification passed: python3 -B -m unittest discover -s tests -p test_health_gate.py (12 tests) and python3 -B scripts/quality.py. The diagnostic includes only a fixed category and bounded exit code; failed reports preserve dependency_outage. No Azure permission was changed. The trusted post-merge main-only dev run remains pending because it can only run on main after merge and must confirm the app identity can query the dev workspace and write the source-bound annotation.
<!-- SECTION:NOTES:END -->
