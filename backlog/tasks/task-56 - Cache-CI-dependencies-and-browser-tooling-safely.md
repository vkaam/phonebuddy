---
id: TASK-56
title: Cache CI dependencies and browser tooling safely
status: In Progress
assignee:
  - '@vkaam'
created_date: '2026-11-02T16:21:00Z'
updated_date: '2026-11-02T16:25:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/65
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
modified_files:
  - backlog/tasks/task-56 - Cache-CI-dependencies-and-browser-tooling-safely.md
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
priority: high
type: enhancement
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
## Problem and intended outcome
The Quality workflow repeatedly installs the locked web dependency graph and Playwright Chromium. Add scoped, versioned GitHub Actions caches that shorten dependency and browser downloads while every CI run still performs the locked install, audit, lint, unit and browser tests, build, workflow validation, secret scan, and artifact evidence steps. Document what is cached, how keys invalidate, trust boundaries, measurements, and limitations.

## Approved issue revision
- Issue: https://github.com/vkaam/phonebuddy/issues/65
- Approved requirements snapshot: updated 2026-11-01T15:29:46Z; SHA-256 bd0bdcb7269d5e1af66e6404a4d43d671089fabdb7814074c162e399a1bdbe76
- Approver and evidence: vkaam; direct user instruction in the Codex conversation on 2026-11-02: “Issue #65, please complete this issue.”

## Branch
agent/gh-65-1-safe-ci-caching

## Scope
- .github/workflows/ci.yml
- docs/quality-and-delivery.md
- backlog/tasks/task-56 - Cache-CI-dependencies-and-browser-tooling-safely.md (this task record only)

## Specification and constraints
Use runner- and lockfile/toolchain-scoped cache keys with explicit invalidation. Keep npm ci and npm audit, all browser smoke and other required checks, source-bound report/artifact generation, and read-only workflow permissions. Cache data must not flow from untrusted pull requests into privileged workflows; do not add cache use to pull_request_target or consume caches as verification evidence. Record cold and warm hosted CI durations and identify the steps improved. Baseline evidence must be bound to the approved main SHA; improved evidence must identify the PR head and Actions run IDs.

## Verification
- From repository root: python3 -B scripts/quality.py
- From repository root: python3 -B scripts/run_required_unittests.py
- From apps/web: npm ci --no-audit --no-fund; npm audit; npm run lint; npm test; npm run build; npx playwright install --with-deps chromium; npm run test:browser
- Hosted gate: CI / Quality succeeds on the PR head, including actionlint and Gitleaks; record its source SHA and run URL.
- Performance evidence: record representative baseline and improved cold and warm Quality run durations and relevant step durations from GitHub Actions, with run URLs and source SHAs. A cache hit alone is not a passing result.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Representative baseline and improved cold and warm CI durations are reported with run links, source revisions, and the affected steps.
- [ ] #2 Dependency and browser caches use scoped, versioned keys that invalidate on relevant lockfile or toolchain changes, and cache misses still pass all checks.
- [ ] #3 Locked installs, vulnerability scanning, browser smoke tests, required checks, and source-bound evidence remain active on every CI run; cache hits are not treated as verification.
- [ ] #4 Cache trust boundaries prevent untrusted pull request data from influencing privileged workflows, and documentation records cache contents, invalidation, measurements, and remaining limitations.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Capture baseline Quality run durations and source-bound workflow evidence from main. 2. Add dependency and browser caches in the CI workflow with branch-safe scope and lockfile/toolchain invalidation. 3. Document contents, keys, trust boundaries, and limitations. 4. Run local checks and verify hosted cold and warm CI runs. 5. Record run evidence, finalize the task, and publish one PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Baseline evidence from uncached main runs: latest Quality run 41403043185 on bd99978362536dbf6d026ed47a7262b3ded57cd3 took 52 seconds (https://github.com/vkaam/phonebuddy/actions/runs/41403043185); Build and test web shell took 31.1 seconds and installed Chromium 156 / Playwright v1248 browser binaries (~8.3 seconds of downloads) plus Linux dependencies. Recent comparison runs 41347032710 on 4ae593d03c0be3e1a41a8e34f7eb8ddc25e767a2 took 42 seconds (https://github.com/vkaam/phonebuddy/actions/runs/41347032710), and 41345888941 on 19001039764ff8ccf0c061216ebbff583d15f4cd took 41 seconds (https://github.com/vkaam/phonebuddy/actions/runs/41345888941). The three-run uncached median is 42 seconds; the combined build/test step spans 24.6–31.1 seconds. This is observational baseline only; hosted cold and warm cache runs remain required.

Implemented caches in CI: setup-node caches the lockfile-keyed npm download store, and actions/cache v4.2.4 caches the Playwright browser directory with a versioned OS/architecture/Node/lockfile key and no restore-key fallback. npm ci, npm audit, playwright install --with-deps, browser tests, and the existing verification/evidence steps remain unconditional. Documentation records baseline runs and states the privileged PR safety workflow does not consume CI caches.

Local verification passed on 2026-11-02: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py (35 tests); from apps/web, npm ci --no-audit --no-fund, npm audit (0 vulnerabilities), npm run lint, npm test (5 tests), npm run build, npx playwright install chromium (macOS-supported; downloaded Chromium 156 / Playwright v1248), and npm run test:browser (3 passed). Hosted Ubuntu CI remains necessary to validate the workflow with --with-deps, actionlint, Gitleaks, and cache timings.
<!-- SECTION:NOTES:END -->
