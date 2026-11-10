---
id: TASK-81
title: Trusted dev health gate cannot query Log Analytics
status: Done
assignee:
  - '@codex'
created_date: '2026-11-10T20:46:00Z'
updated_date: '2026-11-10T21:21:00Z'
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
Approval evidence: Direct human instruction on 2026-11-10 to fix issue #92. Execution-scope amendment: the requester clarified that the trusted gate result can only be checked after merge. This task covers the bounded diagnostic code change in one PR; the post-merge gate result remains issue-level evidence, and any failure is handled as linked follow-up work. This does not weaken or rewrite issue-level acceptance.

Branch: agent/gh-92-1-trusted-dev-health-gate
Scope: .github/workflows/azure-health-gate.yml; scripts/health_gate.py; tests/test_health_gate.py; tests/test_bicep_ci_boundary.py; this task's own CLI-managed record
Verify: From repository root run python3 -B -m unittest discover -s tests -p 'test_health_gate.py'; python3 -B scripts/quality.py; verify the required hosted Quality check passes on the final PR head. After merge, observe the trusted main-only dev workflow and retain its run evidence for 100 successful requests, at least 100 version-matched workspace events under the dev GitHub app identity, and a verified source-bound Application Insights annotation. If that post-merge run fails, record it as new linked follow-up work. No Azure permission change is included; any grant requires explicit owner approval at the dev workspace.
Spec: Add a bounded redacted diagnostic for hosted Log Analytics query failures while preserving fail-closed behavior. Reports may include only fixed categories and a bounded exit code, never raw stderr, query content, resource IDs, call data, tokens, or secrets. The successful trusted gate and annotation remain post-merge observations, not pre-merge task criteria.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Hosted query failures produce bounded redacted diagnostics containing only a fixed category and bounded exit code; raw CLI output, query contents, resource IDs, call data, and secrets are never emitted.
- [x] #2 Query failures remain fail-closed as dependency_outage, and missing telemetry and unhealthy events continue to fail closed.
- [x] #3 Focused health-gate tests, repository Quality, and the required hosted Quality check on the final PR head pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add fixed-category, bounded exit-code diagnostics for Log Analytics CLI failures without echoing command output. 2. Preserve dependency_outage and existing missing-telemetry and unhealthy-event fail-closed behavior. 3. Validate redaction and timeout handling in focused tests, run repository Quality, then verify required hosted PR checks. 4. After merge, observe the trusted main-only gate at issue level and open linked follow-up work if it fails.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Focused verification passed: python3 -B -m unittest discover -s tests -p test_health_gate.py (12 tests) and python3 -B scripts/quality.py. The diagnostic includes only a fixed category and bounded exit code; failed reports preserve dependency_outage. No Azure permission was changed. The trusted post-merge main-only dev run remains pending because it can only run on main after merge and must confirm the app identity can query the dev workspace and write the source-bound annotation.

Published draft PR #93: https://github.com/vkaam/phonebuddy/pull/93 at head 326827133ddb88ab670e5078ce39fec626689147. Hosted Quality and advisory Risk checks completed successfully on that exact head. The PR remains draft and TASK-81 remains In Progress pending the trusted post-merge main-only dev gate; no Azure permission change or release annotation was performed.

Independent read-only review on 2026-11-10 found no code-level defect in the diagnostic patch: the report emits only fixed labels and an exit code, and query failures remain fail-closed. Reviewer confirmed acceptance remains incomplete because no trusted hosted diagnostic or successful post-merge gate is evidenced and the query command is unchanged. Current PR head a56534c8ed749988052ff79beda239f1f532f868 has passing hosted Quality and advisory Risk checks. Keep PR #93 draft and TASK-81 In Progress pending hosted evidence and any required owner-approved workspace permission.

Triage amendment on 2026-11-10: requester clarified the trusted result is only observable after merge. Reframed TASK-81 as the single-PR diagnostic implementation. Post-merge gate success remains issue-level evidence; a failure becomes linked follow-up work under current repository instructions. Independent review found no pre-merge code defect.

Pre-merge gates now complete on final PR head 9751336c359b2a3d84d774a24da6c7f1a289dfb0: focused tests and Quality passed after latest-main integration; hosted Quality and advisory Risk checks passed. Earlier notes proposing to keep the PR draft pending the gate result are superseded by the requester's clarification that the trusted gate is a post-merge observation. No Azure role change or annotation has been made.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added bounded, redacted Log Analytics CLI failure diagnostics with fixed categories and exit codes, preserving fail-closed gate behavior. Focused tests, repository Quality, hosted Quality, and independent read-only review passed on the current PR head. The trusted main-only dev gate remains a post-merge issue-level observation; Azure permissions were not changed.
<!-- SECTION:FINAL_SUMMARY:END -->
