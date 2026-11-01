---
id: TASK-50
title: Require lint for web verification
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-01T15:05:00Z'
updated_date: '2026-11-01T15:08:00Z'
labels:
  - factory
dependencies:
  - TASK-49
references:
  - https://github.com/vkaam/phonebuddy/issues/39
  - apps/web/src/main.tsx
  - apps/web/src/config.js
  - .github/workflows/ci.yml
  - scripts/check.py
  - docs/quality-and-delivery.md
modified_files:
  - apps/web/package.json
  - apps/web/package-lock.json
  - apps/web/eslint.config.js
  - scripts/check.py
  - tests/test_check.py
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
priority: high
type: chore
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user approved issue #39 and instructed continuation in this Codex chat on 2026-11-01.
Branch: agent/gh-39-3-web-lint
Scope: apps/web/package.json, apps/web/package-lock.json, apps/web/eslint.config.js, apps/web/src/main.tsx, apps/web/src/config.js, apps/web/tests/config.test.mjs, .github/workflows/ci.yml, scripts/check.py, tests/test_check.py, docs/quality-and-delivery.md, docs/agentic-development-contract.md and this task record only.
Dependency: TASK-49 completed on main in PR #57. Archived TASK-34 remains historical and is not restored or treated as complete.
Verify from repository root: python3 -B -m unittest discover -s tests -v; python3 -B scripts/check.py; npm --prefix apps/web run lint; npm --prefix apps/web audit; git diff --check. Demonstrate lint fails on a temporary deliberately invalid source sample; hosted Quality and PR safety must succeed on the final head. Node, npm and registry access required.
Spec: Add a pinned, meaningful ESLint setup covering web JavaScript and TypeScript source, without altering app behavior. Run lint in local evidence and hosted Quality with retained output; report browser smoke as still outstanding. Dependency changes must pass npm audit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A pinned lint command checks the web JavaScript and TypeScript source and rejects a demonstrated invalid sample.
- [ ] #2 Local evidence and hosted Quality require lint, retain its output and fail when it fails.
- [ ] #3 The locked install, lint, tests, build, npm audit and declared Python checks pass; documentation retains the outstanding browser and hosted-only gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add pinned ESLint and TypeScript support with rules for both web source languages, fixing any existing lint violations without changing behavior. 2. Register lint in the local evidence bundle and hosted Quality with logs. 3. Update the runbooks and verify lint rejects a deliberate defect, then run all declared checks and publish the PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Blocked: npm audit reports a moderate minimatch vulnerability affecting all releases below 11.0.1; ESLint 10.14.0 and TypeScript ESLint 8.72.1 currently require minimatch 10.x, and npm reports no compatible automatic fix. Do not override the supported range or suppress audit. The user has been asked to approve a triage amendment to replace ESLint with Biome and change the config file scope. Lint passes current source and rejects a deliberately unused variable; 34 Python tests and git diff --check passed, but the required npm audit fails and task remains In Progress.

User decision 2026-11-01: keep ESLint and wait for a compatible fix; do not replace it with Biome or override unsupported minimatch ranges. Required npm audit remains failing, so acceptance is incomplete.

Draft PR https://github.com/vkaam/phonebuddy/pull/63 records the audit blocker and remains in progress until an upstream compatible minimatch fix exists and checks can be rerun.
<!-- SECTION:NOTES:END -->
