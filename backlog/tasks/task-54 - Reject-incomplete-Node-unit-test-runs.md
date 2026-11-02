---
id: TASK-54
title: Reject incomplete Node unit test runs
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T20:29:00Z'
updated_date: '2026-11-02T06:49:00Z'
labels:
  - factory
dependencies:
  - TASK-53
references:
  - https://github.com/vkaam/phonebuddy/issues/39
  - apps/web/package.json
  - docs/quality-and-delivery.md
modified_files:
  - apps/web/scripts/run-required-tests.mjs
  - apps/web/tests/required-node-tests.test.mjs
  - apps/web/package.json
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
  - backlog/tasks/task-54 - Reject-incomplete-Node-unit-test-runs.md
priority: high
type: chore
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user approved issue #39 and instructed continued work in this Codex chat on 2026-11-01.
Branch: agent/gh-39-7-required-node
Scope: apps/web/package.json, apps/web/scripts/run-required-tests.mjs, apps/web/tests/required-node-tests.test.mjs, docs/quality-and-delivery.md, docs/agentic-development-contract.md and this task record only.
Dependency: TASK-53 completed on main in PR #67. Archived TASK-34 remains historical and is not restored or treated as complete.
Verify from repository root: npm --prefix apps/web test; python3 -B scripts/run_required_unittests.py; PLAYWRIGHT_BROWSERS_PATH=/private/tmp/phonebuddy-playwright-browsers python3 -B scripts/check.py; npm --prefix apps/web audit; git diff --check. Node, npm, Chromium and registry access required; hosted Quality and PR safety must succeed on the final PR head.
Spec: Make the existing required Node unit test command fail on skipped, todo, cancelled, failed or missing tests and unavailable or inconclusive test results, preserving useful logs. Exercise real Node test-runner fixtures for each applicable outcome. The existing local and hosted paths already call npm test. Do not modify application behavior or claim aggregate issue #39 acceptance.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Required Node unit tests pass only when at least one test ran and every test passed without skipped, todo or cancelled tests; errors and inconclusive output fail.
- [x] #2 Regression fixtures exercise real Node test-runner success, skip, todo, failure, and empty-discovery outcomes, with useful output retained.
- [x] #3 Local and hosted verification use the required Node test command; declared checks and final-hosted checks pass, and documentation describes the completeness rule.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Wrap the native Node test runner with fail-closed validation of test counts and non-passing outcomes while preserving TAP output. 2. Add real subprocess fixtures for success, skip, todo, failure, cancellation and empty discovery. 3. Update documentation, run required local and hosted checks, and publish the task PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verification: required Node runner passed five tests under local Node 26.10.0 and CI Node 22.15.1; subprocess fixtures confirmed success and rejection of skip, todo, failure, cancelled, duplicate/inconclusive summary and empty discovery. Python runner passed 35 tests; full 11-check evidence bundle passed with unchanged source at /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-l415anl7/report.json; npm audit reported zero vulnerabilities; git diff --check passed. Initial fixture issues involving inherited NODE_TEST_CONTEXT and an unresolved cancellation were corrected before final verification. Hosted CI and independent review pending.

Draft PR https://github.com/vkaam/phonebuddy/pull/68; implementation head 7514994. Hosted checks and independent review remain pending; aggregate issue #39 acceptance is outstanding.

Hosted Quality https://github.com/vkaam/phonebuddy/actions/runs/41347399670 and PR safety advisory https://github.com/vkaam/phonebuddy/actions/runs/41347398206 passed on head 9dcf5363de439647d18dfe39d286999d548b0da1. Final task metadata commit requires fresh checks. Independent review and merge remain outstanding; branch-local Done is provisional.

PR #68 review follow-up: the required Node runner now counts TAP events for actual test cases separately from its discovered-file wrapper, and real subprocess fixtures cover an empty discovered test file and a successful early process exit before registered tests execute. npm --prefix apps/web test passed (5 tests); python3 -B scripts/run_required_unittests.py passed (35 tests); elevated PLAYWRIGHT_BROWSERS_PATH=/private/tmp/phonebuddy-playwright-browsers python3 -B scripts/check.py passed all local checks; git diff --check passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Hardened required Node unit-test validation to require at least one executed test case, separately from file-level TAP success. Added real subprocess regression fixtures for empty discovered files and successful early process exits, retaining existing outcome coverage. Web tests (5), Python tests (35), and the full local quality bundle passed; broader issue #39 acceptance and PR review/merge remain outstanding.
<!-- SECTION:FINAL_SUMMARY:END -->
