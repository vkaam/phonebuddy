---
id: TASK-83
title: Retry throttled health-gate telemetry queries safely
status: Done
assignee:
  - '@codex'
created_date: '2026-11-11T07:35:00Z'
updated_date: '2026-11-11T07:42:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-81
references:
  - https://github.com/vkaam/phonebuddy/issues/92
  - scripts/health_gate.py
  - tests/test_health_gate.py
modified_files:
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - >-
    backlog/tasks/task-83 -
    Retry-throttled-health-gate-telemetry-queries-safely.md
priority: high
type: bug
ordinal: 74000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Trusted main-only release health gate run 42904952753 failed after 100 requests and 600 seconds with four dependency outages. Its Log Analytics query was throttled (exit code 1), returned no workspace events, and the source-bound release annotation was skipped. TASK-81 added redacted diagnostics but intentionally did not retry query errors; retrying a transient throttle may allow the same gate to collect its required telemetry without changing permissions or weakening health thresholds.

Issue: https://github.com/vkaam/phonebuddy/issues/92
Approved requirements revision: 2026-11-10T21:39:02Z; SHA-256 of UTF-8 issue body d50d4126742aaba1b05f78c0973f9a3a3eddc2aa55851b8a69ff709e6fc31c5c.
Approver: Human requester in this conversation.
Approval evidence: Direct instruction on 2026-11-11 to check and fix main CI issues. The bounded follow-up is limited to retrying transient throttling; no Azure permission change or threshold relaxation is authorized.

Branch: agent/gh-92-2-retry-throttled-health-query
Scope: scripts/health_gate.py; tests/test_health_gate.py; this task's own CLI-managed record.
Verify: From repository root run python3 -B -m unittest discover -s tests -p test_health_gate.py; python3 -B scripts/quality.py; python3 -B scripts/backlog_consistency.py --base origin/main. Confirm hosted Quality passes on the final PR head. A trusted post-merge gate is issue-level evidence and must still fail closed if throttling persists, events are missing, or unhealthy events occur.
Spec: Add finite, bounded-backoff retries only for classified Log Analytics throttling. Preserve redacted diagnostics, the 100-event requirement, HTTP error thresholds, fail-closed behavior after exhausted retries, and existing permissions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Classified Log Analytics throttling is retried a finite number of times with bounded backoff, without exposing raw CLI output or query details.
- [x] #2 Exhausted retries remain dependency_outage, and missing telemetry, unhealthy events, and HTTP health thresholds continue to fail closed.
- [x] #3 Focused health-gate tests, local Quality, live consistency validation, and hosted Quality pass on the final PR head.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current query helper and tests to preserve redaction and fail-closed behavior. 2. Retry only diagnostics classified as throttled, with a finite retry count and capped exponential backoff; preserve the final diagnostic after exhaustion. 3. Add tests for recovery after a transient throttle, exhausted retries, and no retries for authorization or query errors. 4. Run focused health-gate tests, local Quality, and live consistency. 5. Commit and push this branch, open one PR against main, and monitor required checks; keep successful post-merge gate evidence at issue level.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented three finite retries for throttled Log Analytics queries with 10/20/30-second capped exponential backoff. Only the fixed throttled diagnostic category retries; authorization, query, timeout, and other errors fail immediately. Persistent throttling returns the existing redacted dependency_outage diagnostic. Focused health-gate suite passed (15 tests), repository Quality passed, and live consistency/claim validation passed against current origin. No permission or health threshold changes were made.

PR #96 opened at commit 03b069f. Hosted Quality run 42981250248 passed and advisory Risk report 42981250259 passed on that head. TASK-83 is marked Done on the feature branch; finalization will be committed to the same PR and checks will be rerun on the resulting final head. The trusted post-merge Azure gate remains issue-level verification under #92.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added up to three retries for Log Analytics throttling with 10, 20, and 30 second capped backoff. Persistent throttling remains a redacted dependency_outage; other query failures do not retry. Focused tests, local Quality, live consistency, and hosted Quality passed. No Azure permissions or health thresholds changed. Successful trusted post-merge gate evidence remains outstanding under issue #92.
<!-- SECTION:FINAL_SUMMARY:END -->
