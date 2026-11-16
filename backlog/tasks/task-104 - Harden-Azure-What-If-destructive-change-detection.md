---
id: TASK-104
title: Harden Azure What-If destructive change detection
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-15T18:58:00Z'
updated_date: '2026-11-16T05:51:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/132
  - scripts/release_recovery.py
  - scripts/check_bicep.py
modified_files:
  - scripts/release_recovery.py
  - scripts/check_bicep.py
  - tests/test_release_recovery.py
  - tests/test_bicep_preflight.py
  - docs/quality-and-delivery.md
priority: high
type: bug
ordinal: 92000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/132
Approved requirements revision: 2026-11-15T18:57:12Z; SHA-256 7efbd63e69e92da20b91a59ea6f5f1fb5dbd101923e73b8772cc6424055ce9e6
Approval evidence: owner explicitly approved independent later follow-up in Codex on 2026-11-15 and directed that it not block other tasks.
Branch: agent/gh-132-1-what-if-guard
Scope: scripts/release_recovery.py; scripts/check_bicep.py; tests/test_release_recovery.py; tests/test_bicep_preflight.py; docs/quality-and-delivery.md; this task record only
Verify: python3 -B -m unittest tests.test_release_recovery tests.test_bicep_preflight; python3 -B scripts/check.py; git diff --check
Independent later work; no dependency on TASK-63 and no task depends on this item.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Actual Azure What-If resource IDs identify SQL and Storage resources, including nested types and case variations; destructive property deletions are rejected.
- [x] #2 Missing or malformed resource identity and ambiguous change details fail closed while reviewed non-destructive changes remain allowed.
- [ ] #3 Regression tests cover the retained Azure What-If shape and the combined validation path; required checks pass without a live destructive deployment.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Parse and validate Azure What-If resource IDs in the recovery destructive-change guard, derive nested resource types from provider paths, and fail closed on missing, malformed, or conflicting identity details.
2. Detect SQL and Storage property deletions from either resourceId-derived or consistent resourceType identity while allowing reviewed non-destructive changes.
3. Apply the same guard in the general What-If validator so the combined validation path rejects the retained Azure shape before deployment.
4. Add regressions for nested/case-varied resource IDs, malformed and ambiguous changes, non-destructive changes, and combined validation; update the safety documentation.
5. Run the task-listed unit tests, repository check, and whitespace check; do not perform a live deployment.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Independent review found no blocking defects and validated acceptance coverage. Validation: 74 tests passed across test_release_recovery, test_bicep_preflight, and test_bicep_ci_boundary; full scripts/check.py passed with process-local Bash 5 and Git init default overrides; git diff --check passed. No live destructive deployment was performed.
<!-- SECTION:NOTES:END -->
