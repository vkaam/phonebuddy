---
id: TASK-3
title: Add reproducible local quality evidence command
status: Done
assignee:
  - '@codex'
created_date: '2026-10-29T19:42:00Z'
updated_date: '2026-10-29T19:43:00Z'
labels: []
dependencies: []
references:
  - scripts/quality.py
  - docs/quality-and-delivery.md
  - scripts/check.py
  - tests/test_check.py
modified_files:
  - scripts/check.py
  - tests/test_check.py
  - docs/quality-and-delivery.md
priority: high
type: chore
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Existing validation commands must be run separately and do not produce a local evidence bundle tied to source identity. Add a single dependency-free command for the current repository checks to support the Phase 0 delivery loop.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 One command runs repository validation and unittest discovery with bounded execution and returns failure for failed or timed-out checks.
- [x] #2 A JSON report records head and working-tree identity, exact commands, timings, exit results, and log digests without claiming hosted CI or independent review.
- [x] #3 Meaningful runner failure and success tests pass, and usage explains evidence limitations and artifact handling.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a dependency-free runner for the two existing Python checks, unique evidence directories outside the repository, source manifests, timeouts, and failure reporting. 2. Test success, failure, timeout, and source-change handling. 3. Document invocation and evidence limits, run the full command, and verify its report.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verified the new command end to end: repository check and all 21 tests pass, source snapshots agree, and saved log SHA-256 digests match. Runner tests exercise nonzero exits, timeout, missing executable, snapshot failure, changed source, dirty/untracked/deleted/ignored files, and invalid CLI options. git diff --check passes. Initial bundle: /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-gluduh44/report.json. Bundle predates this final task metadata update; executable source is unchanged. Hosted checks and independent review remain pending.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added scripts/check.py to run both existing local checks with per-check timeouts and unique JSON/log evidence bundles outside the checkout. Source manifests and log digests identify tested content; failures and source changes fail the command. Added six meaningful runner tests and documented invocation, raw-log handling, retention, source limitations, and distinction from hosted CI and isolation. All 21 tests, repository checks, and whitespace checks pass. Changes remain local and uncommitted.
<!-- SECTION:FINAL_SUMMARY:END -->
