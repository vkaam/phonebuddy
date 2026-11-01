---
id: TASK-50
title: Require lint for web verification
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T15:05:00Z'
updated_date: '2026-11-01T15:19:00Z'
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
  - apps/web/biome.json
  - apps/web/src/main.tsx
priority: high
type: chore
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user approved issue #39 and instructed continuation in this Codex chat on 2026-11-01.
Triage amendment v2, 2026-11-01: user explicitly approved switching from ESLint to Biome in this chat after the vulnerable minimatch dependency blocked the audit. Add apps/web/biome.json to scope and remove the previously added ESLint configuration; retain the same acceptance criteria and verification. Earlier ESLint audit and check evidence is invalidated.
Branch: agent/gh-39-3-web-lint
Scope: apps/web/package.json, apps/web/package-lock.json, apps/web/eslint.config.js (removal), apps/web/biome.json, apps/web/src/main.tsx, apps/web/src/config.js, apps/web/tests/config.test.mjs, .github/workflows/ci.yml, scripts/check.py, tests/test_check.py, docs/quality-and-delivery.md, docs/agentic-development-contract.md and this task record only.
Dependency: TASK-49 completed on main in PR #57. Archived TASK-34 remains historical and is not restored or treated as complete.
Verify from repository root: python3 -B -m unittest discover -s tests -v; python3 -B scripts/check.py; npm --prefix apps/web run lint; npm --prefix apps/web audit; git diff --check. Demonstrate lint fails on a temporary deliberately invalid source sample; hosted Quality and PR safety must succeed on the final head. Node, npm and registry access required.
Spec: Add a pinned, meaningful Biome lint setup covering web JavaScript and TypeScript source, without altering app behavior. Run lint in local evidence and hosted Quality with retained output; report browser smoke as still outstanding. Dependency changes must pass npm audit.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A pinned lint command checks the web JavaScript and TypeScript source and rejects a demonstrated invalid sample.
- [x] #2 Local evidence and hosted Quality require lint, retain its output and fail when it fails.
- [x] #3 The locked install, lint, tests, build, npm audit and declared Python checks pass; documentation retains the outstanding browser and hosted-only gates.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Replace ESLint with pinned Biome and configure meaningful checks for web JavaScript and TypeScript without changing app behavior. 2. Retain local and hosted lint evidence and update the runbooks. 3. Verify lint rejects a deliberate defect, rerun every declared check and monitor the updated PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Blocked: npm audit reports a moderate minimatch vulnerability affecting all releases below 11.0.1; ESLint 10.14.0 and TypeScript ESLint 8.72.1 currently require minimatch 10.x, and npm reports no compatible automatic fix. Do not override the supported range or suppress audit. The user has been asked to approve a triage amendment to replace ESLint with Biome and change the config file scope. Lint passes current source and rejects a deliberately unused variable; 34 Python tests and git diff --check passed, but the required npm audit fails and task remains In Progress.

User decision 2026-11-01: keep ESLint and wait for a compatible fix; do not replace it with Biome or override unsupported minimatch ranges. Required npm audit remains failing, so acceptance is incomplete.

Draft PR https://github.com/vkaam/phonebuddy/pull/63 records the audit blocker and remains in progress until an upstream compatible minimatch fix exists and checks can be rerun.

Triage amendment v2: user approved replacing ESLint with Biome on 2026-11-01; added apps/web/biome.json and ESLint config removal to the scoped paths. Re-run all checks for the revised dependency and source identity.

Amendment v2 validation: Biome 2.6.4 checks both web source files and exits nonzero for a temporary TypeScript sample containing an unused variable. npm audit reports zero vulnerabilities; 34 Python tests passed and python3 -B scripts/check.py passed all ten checks with unchanged source (evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-768p3t6d/report.json); git diff --check passed. Awaiting hosted validation on the revised PR head and independent review.

Quality https://github.com/vkaam/phonebuddy/actions/runs/41320601378 and PR safety advisory https://github.com/vkaam/phonebuddy/actions/runs/41320612013 passed on revised head 5071b64f2bf64d86143a6a34c70d535ab75b1560. Final task metadata commit requires fresh hosted checks. Human review and merge remain outstanding; branch-local Done is provisional.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added pinned Biome linting for web JavaScript and TypeScript to local and hosted evidence. The ten-check local bundle, 34 Python tests, clean npm audit, negative lint fixture and pre-finalization hosted checks passed. Independent review and merge remain outstanding; browser smoke and broader issue #39 evidence remain incomplete.
<!-- SECTION:FINAL_SUMMARY:END -->
