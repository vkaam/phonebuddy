---
id: TASK-51
title: Verify web shell behavior in a real browser
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-01T15:25:00Z'
updated_date: '2026-11-01T15:28:00Z'
labels:
  - factory
dependencies:
  - TASK-50
references:
  - https://github.com/vkaam/phonebuddy/issues/39
  - apps/web/src/main.tsx
  - apps/web/src/style.css
  - .github/workflows/ci.yml
  - scripts/check.py
  - docs/quality-and-delivery.md
modified_files:
  - apps/web/package.json
  - apps/web/package-lock.json
  - apps/web/playwright.config.js
  - apps/web/e2e/smoke.spec.js
  - scripts/check.py
  - tests/test_check.py
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
priority: high
type: chore
ordinal: 50000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user approved issue #39 and instructed continuation in this Codex chat on 2026-11-01.
Branch: agent/gh-39-4-browser-smoke
Scope: apps/web/package.json, apps/web/package-lock.json, apps/web/playwright.config.js, apps/web/e2e/smoke.spec.js, apps/web/src/main.tsx, apps/web/src/style.css, .github/workflows/ci.yml, scripts/check.py, tests/test_check.py, docs/quality-and-delivery.md, docs/agentic-development-contract.md and this task record only.
Dependency: TASK-50 completed on main in PR #63. Archived TASK-34 remains historical and is not restored or treated as complete.
Verify from repository root: python3 -B -m unittest discover -s tests -v; python3 -B scripts/check.py; npm --prefix apps/web run test:browser; npm --prefix apps/web audit; git diff --check. Install the pinned Playwright Chromium browser before testing; CI must install browser dependencies. Hosted Quality and PR safety must pass on final PR head.
Spec: Add deterministic real Chromium smoke tests for application routes, missing public config and keyboard navigation, using controlled config responses and no real backend. Register the browser suite in local evidence and hosted CI with logs; report hosted-only gates accurately. Dependency additions must pass npm audit. Preserve application behavior unless required to make keyboard interaction work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pinned real-browser smoke tests verify the dialer, history and settings routes with controlled valid configuration; missing configuration produces the user-facing setup error.
- [ ] #2 Keyboard-only navigation and the skip link are exercised, with observable focus and route assertions.
- [ ] #3 Local evidence and hosted Quality execute the browser suite, retain logs and fail for missing browsers or failing tests; setup prerequisites are documented.
- [ ] #4 The locked install, browser and existing checks, npm audit and declared Python tests pass; remaining hosted-only and issue-wide evidence gaps are explicit.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Install pinned Playwright and configure an isolated Chromium test server and output outside the checkout. 2. Add real-browser smoke cases for routes, config failure and keyboard focus/navigation. 3. Register tests in local evidence and CI, document browser prerequisites, and fix only observed keyboard defects in scope. 4. Run the declared checks, publish and monitor the PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Local verification: three Chromium tests passed for routes, missing configuration and keyboard skip/navigation; an intentionally empty browser path caused the suite to fail with a missing executable error. npm audit reported zero vulnerabilities; 34 Python tests and git diff --check passed. Full 11-check local bundle passed with unchanged source; evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-ikm2egf3/report.json. Chromium was installed under /private/tmp/phonebuddy-playwright-browsers for this run. Hosted checks and independent review remain pending.
<!-- SECTION:NOTES:END -->
