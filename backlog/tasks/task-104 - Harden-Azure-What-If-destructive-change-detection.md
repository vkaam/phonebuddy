---
id: TASK-104
title: Harden Azure What-If destructive change detection
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-15T18:58:00Z'
updated_date: '2026-11-16T06:03:00Z'
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
- [ ] #1 Actual Azure What-If resource IDs identify SQL and Storage resources, including nested types and case variations; destructive property deletions are rejected.
- [ ] #2 Missing or malformed resource identity and ambiguous change details fail closed while reviewed non-destructive changes remain allowed.
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

Draft PR: https://github.com/vkaam/phonebuddy/pull/135. Independent review passed with no blocking findings; hosted checks are pending. Task remains In Progress pending hosted verification and merge.

Final PR head bcd55bde4b823d3fe0a94bbf93c128b8c3f9497b passed hosted CI (run 43813256771) and the advisory Backlog audit (run 43813256694). Independent review of this head found no blocking findings. PR #135 is ready for review; all acceptance criteria are verified.

Supersedes the earlier pending/draft note: PR #135 is ready for review and all current hosted checks pass. All acceptance criteria are checked and task status is Done in this feature-branch record; merging this PR makes that status final on main.

Reopened after P1 review thread on PR #135 identified valid ARM extension-resource IDs with multiple /providers/ segments. Current parser blocks these ordinary deployment What-If entries. Fix and revalidation are in progress; prior acceptance and review evidence is stale for the new head.

P1 fix applied locally: parser now validates each provider segment and derives identity from the terminal provider, allowing valid extension-resource paths. Added regression for Microsoft.Insights diagnosticSettings nested under Microsoft.App. Independent re-review found no blockers. 75 targeted tests, full scripts/check.py, and git diff --check pass. Prior Done/acceptance evidence is superseded; PR hosted checks must rerun on the new head.
<!-- SECTION:NOTES:END -->
