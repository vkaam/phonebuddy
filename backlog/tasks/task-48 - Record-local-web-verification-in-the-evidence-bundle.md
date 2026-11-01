---
id: TASK-48
title: Record local web verification in the evidence bundle
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T14:49:00Z'
updated_date: '2026-11-01T14:52:00Z'
labels:
  - factory
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/39
  - scripts/check.py
  - tests/test_check.py
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
modified_files:
  - scripts/check.py
  - tests/test_check.py
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
priority: high
type: chore
ordinal: 47000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user explicitly approved starting a bounded issue #39 slice in this Codex chat on 2026-11-01.
Branch: agent/gh-39-1-local-web-evidence
Scope: scripts/check.py, tests/test_check.py, docs/quality-and-delivery.md, docs/agentic-development-contract.md, and this task record only.
Dependencies: none; issue #39 declares none. Archived TASK-34 is historical and is not restored or treated as complete.
Verify from repository root: python3 -B -m unittest discover -s tests -v; python3 -B scripts/check.py; git diff --check. Hosted Quality and PR safety checks must succeed on the final PR head. Requires Node.js, npm and access to dependencies for npm ci; missing prerequisites must fail explicitly.
Spec: Extend local evidence to include the existing locked web install, web tests and strict typecheck/build, source-bound results and tool versions. Clearly distinguish this partial local baseline from issue-wide complete evidence: lint, browser smoke, dependency scanning and hosted-only gates remain outstanding. Do not alter CI policy, dependencies or application behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The local command runs locked web installation, existing web tests and the typecheck/build alongside the existing baseline and records each command, outcome and log.
- [x] #2 A missing, failed or timed-out required local step causes the bundle to fail; tests cover failures and source identity behavior.
- [x] #3 Evidence records Node and npm versions and clearly identifies outstanding lint, browser, dependency and hosted-only checks without claiming issue-wide completeness.
- [x] #4 Declared local checks pass and documentation accurately describes the command and remaining limitations.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend the local evidence runner with explicit Node/npm version, locked install, test and build checks, preserving per-command logs and source snapshots. 2. Add focused regression coverage for required web checks and failure handling. 3. Update both runbooks to describe the expanded but still incomplete evidence boundary. 4. Run declared checks and publish the scoped PR with outstanding issue-level gaps.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Local verification: python3 -B -m unittest discover -s tests -v passed 34 tests; python3 -B scripts/check.py passed all eight checks with unchanged source and evidence at /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-016s0gqp/report.json; git diff --check passed. Local Node was v26.10.0; hosted CI uses its pinned version. Issue-wide lint, browser smoke, vulnerability scanning, complete hosted evidence and review remain outstanding. This slice does not complete issue #39.

Draft PR: https://github.com/vkaam/phonebuddy/pull/56. Committed source 1aa2abd passed the full local evidence command with a clean checkout; bundle /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-pkhmeihe/report.json. Hosted checks and independent review are pending; issue #39 remains open for remaining checks and coverage.

Hosted checks on cfbf00d392c5da1a7e0581c465da592532456cba passed: Quality https://github.com/vkaam/phonebuddy/actions/runs/41318281449 and advisory PR safety https://github.com/vkaam/phonebuddy/actions/runs/41318279513. Final task-metadata commit requires fresh hosted checks. Independent human review and merge remain outstanding; this branch-local Done is provisional.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Expanded source-bound local evidence to run the existing locked web install, tests and typecheck/build, record tool and dependency versions, and expose outstanding checks. The 34-test Python suite and local bundle passed; hosted Quality and advisory checks passed on the pre-finalization head. Human review and merge remain outstanding, and broader issue #39 is incomplete.
<!-- SECTION:FINAL_SUMMARY:END -->
