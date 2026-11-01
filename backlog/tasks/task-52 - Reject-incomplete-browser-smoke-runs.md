---
id: TASK-52
title: Reject incomplete browser smoke runs
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-01T19:57:00Z'
updated_date: '2026-11-01T20:01:00Z'
labels:
  - factory
dependencies:
  - TASK-51
references:
  - https://github.com/vkaam/phonebuddy/issues/39
  - apps/web/playwright.config.js
  - docs/quality-and-delivery.md
modified_files:
  - apps/web/e2e/required-reporter.js
  - apps/web/playwright.config.js
  - apps/web/tests/required-reporter.test.mjs
  - docs/quality-and-delivery.md
priority: high
type: chore
ordinal: 51000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user approved issue #39 and instructed continued issue work in this Codex chat on 2026-11-01.
Branch: agent/gh-39-5-browser-no-skips
Scope: apps/web/playwright.config.js, apps/web/e2e/required-reporter.js, apps/web/tests/required-reporter.test.mjs, docs/quality-and-delivery.md and this task record only.
Dependency: TASK-51 completed on main in PR #64. Archived TASK-34 is historical and is not restored or treated as complete.
Verify from repository root: python3 -B -m unittest discover -s tests -v; PLAYWRIGHT_BROWSERS_PATH=/private/tmp/phonebuddy-playwright-browsers python3 -B scripts/check.py; npm --prefix apps/web run test:browser; npm --prefix apps/web audit; git diff --check. Chromium and registry access required. Verify intentionally skipped and empty test selections fail. Hosted Quality and PR safety checks must pass on the final head.
Spec: Make the required Playwright suite fail for skipped or empty runs and focused tests, without weakening failures or modifying application behavior. Preserve ordinary Playwright output and local/CI evidence. Other test runners and full issue acceptance remain outside this slice.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The required browser suite fails on skipped tests, empty selections or focused tests and retains normal test output.
- [ ] #2 Regression tests demonstrate successful and unsuccessful reporter outcomes, including skipped and empty test suites; actual browser smoke still passes.
- [ ] #3 The declared local checks and final-head hosted Quality and advisory checks pass, and documentation states the behavior and limits.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add a Playwright reporter that fails required browser runs for skipped or empty suites and retain the standard list reporter; forbid focused tests. 2. Test reporter outcomes and exercise real skip and empty scenarios without modifying repository fixtures. 3. Document browser-only scope, run declared checks, publish the PR and monitor final-head hosted checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Verification: npm test passed four tests, including reporter outcomes; real Playwright runs with skipped, focused and empty selections all returned nonzero, with the reporter detecting skipped and empty cases. The full local evidence bundle passed all 11 checks including three real Chromium smoke tests, with unchanged source: /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-hyhx1zbv/report.json. 34 Python tests, npm audit (zero vulnerabilities) and git diff --check passed. Hosted checks and independent review pending.

Draft PR https://github.com/vkaam/phonebuddy/pull/66; implementation head a04a5c6. Hosted checks and independent review remain pending; other test runners and aggregate issue #39 acceptance remain outstanding.

Strengthened the guard to reject any non-passing result, including an expected failure, and added a regression case. npm test and git diff --check passed; the full 11-check bundle passed after the change (evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-vd4cuwhr/report.json). Rechecking hosted CI on the revised head.
<!-- SECTION:NOTES:END -->
