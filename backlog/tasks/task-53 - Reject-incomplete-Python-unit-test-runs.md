---
id: TASK-53
title: Reject incomplete Python unit test runs
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-01T20:15:00Z'
updated_date: '2026-11-01T20:17:00Z'
labels:
  - factory
dependencies:
  - TASK-52
references:
  - https://github.com/vkaam/phonebuddy/issues/39
  - scripts/check.py
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
modified_files:
  - scripts/run_required_unittests.py
  - tests/test_required_unittests.py
  - scripts/check.py
  - tests/test_check.py
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
priority: high
type: chore
ordinal: 52000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user approved issue #39 and instructed continued work in this Codex chat on 2026-11-01.
Branch: agent/gh-39-6-required-python
Scope: scripts/run_required_unittests.py, scripts/check.py, tests/test_required_unittests.py, tests/test_check.py, .github/workflows/ci.yml, docs/quality-and-delivery.md, docs/agentic-development-contract.md and this task record only.
Dependency: TASK-52 completed on main in PR #66. Archived TASK-34 remains historical and is not restored or treated as complete.
Verify from repository root: python3 -B scripts/run_required_unittests.py; PLAYWRIGHT_BROWSERS_PATH=/private/tmp/phonebuddy-playwright-browsers python3 -B scripts/check.py; npm --prefix apps/web audit; git diff --check. Chromium, Node, npm and registry access required. Hosted Quality and PR safety checks must succeed on final PR head.
Spec: Introduce a fail-closed Python unittest runner used by the local bundle and hosted Quality. Empty discovery, skips, expected failures, failures and errors must not pass; preserve verbose test logs and Python 3.9 compatibility. Do not change application behavior. Node unit-test skip detection and full issue #39 acceptance remain outstanding.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The required Python unit-test runner fails on empty discovery, skips, expected failures, failures and errors, and passes a complete successful suite.
- [ ] #2 Regression tests exercise real unittest discovery and outcomes; local and hosted verification invoke the fail-closed runner with verbose logs.
- [ ] #3 Declared local verification and final hosted checks pass; documentation states the Python runner behavior and remaining Node test gap.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a fail-closed unittest discovery runner with explicit skip and expected-failure handling. 2. Add subprocess fixtures for passing, empty, skipped, expected-failure, failing and error outcomes. 3. Use the runner in local evidence and hosted CI, document remaining Node coverage gap, and run declared checks before publishing and monitoring the PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verification: fail-closed Python runner passed 35 tests; regression fixtures exercised passing, empty, skipped, expected-failure, failing and error outcomes. Initial run exposed repository-root imports missing from sys.path; fixed and reran successfully. Full 11-check local bundle passed with unchanged source, including Chromium; evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-3sbbf8ki/report.json. npm audit reports zero vulnerabilities and git diff --check passed. Hosted checks and independent review pending.
<!-- SECTION:NOTES:END -->
