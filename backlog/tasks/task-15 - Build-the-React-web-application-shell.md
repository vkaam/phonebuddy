---
id: TASK-15
title: Build the React web application shell
status: Done
assignee:
  - '@codex'
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-10-31T14:54:00Z'
labels:
  - frontend
dependencies: []
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - .github/workflows/ci.yml
  - apps/web/package.json
  - https://github.com/vkaam/phonebuddy/pull/9
  - apps/web/src/main.tsx
  - apps/web/src/style.css
modified_files:
  - apps/web/package.json
  - apps/web/package-lock.json
  - apps/web/tsconfig.json
  - apps/web/index.html
  - apps/web/src/config.js
  - apps/web/src/main.tsx
  - apps/web/src/style.css
  - apps/web/tests/config.test.mjs
  - apps/web/config.example.json
  - apps/web/README.md
  - .gitignore
  - .github/workflows/ci.yml
priority: high
type: feature
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create the browser product foundation for the internal pilot, with room for organization-scoped calling, history and settings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Vite/React/TypeScript builds reproducibly with locked dependencies and integrates with existing CI and static deployment artifacts.
- [x] #2 Responsive navigation, loading/error/empty states and accessible keyboard focus work for dialer, history and settings routes.
- [x] #3 Public runtime configuration contains no secrets; missing required configuration gives an actionable startup error.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create a locked Vite/React/TypeScript application with validated public runtime configuration and a deployable static build.
2. Implement responsive, keyboard-accessible navigation and clear loading, empty and error states for dialer, history and settings without implying calling is available.
3. Integrate repeatable build and tests into the existing unprivileged CI quality job; verify behavior and record evidence.

4. Address PR review: restore the default route on Back and prevent tablet grid overflow; verify navigation, skip link, and responsive layout.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Locked install, unit tests and production build passed. Chromium exercised dialer, history and settings navigation, keyboard focus, 375px layout and missing-configuration error. Local quality and actionlint passed; production dependency audit reported zero vulnerabilities. The shell intentionally has no authentication, API integration or calling yet. Hosted PR CI and review remain pending.

PR #9 tracks hosted CI and review.

Hosted CI run 41063037362 passed; final task update requires a new run.

PR review fixes: browser Back from history to an empty hash restores Dialer; skip to content retains Settings and focuses main. At 800px the grid is one column and document scroll width equals viewport width. npm ci, tests, build and repository checks passed. npm reports one high severity development dependency advisory.

PR review fixes passed hosted Quality and Risk report checks on commit 138adaf; final task update requires fresh checks.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Built the React shell with responsive navigation, public configuration validation and static CI artifacts. Local tests, browser interaction checks, production build, actionlint and hosted CI passed. Authentication and calling remain future work.

PR review fixes restore Back navigation and prevent tablet overflow; browser checks, local tests and hosted checks passed. The existing Vite development dependency has high-severity advisories; review and merge remain pending.
<!-- SECTION:FINAL_SUMMARY:END -->
