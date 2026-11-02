---
id: TASK-56
title: Cache CI dependencies and browser tooling safely
status: Done
assignee:
  - '@vkaam'
created_date: '2026-11-02T16:21:00Z'
updated_date: '2026-11-02T16:43:00Z'
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
The Quality workflow downloads Playwright browser tooling on every run, increasing feedback time. Cache the Chromium headless-shell binaries used by the existing headless browser smoke tests with a scoped, versioned GitHub Actions cache. Keep the locked web dependency install and every vulnerability scan, lint, unit and browser test, build, workflow validation, secret scan, and evidence step running. Document cache contents, invalidation, trust boundaries, measurements, and limitations.

## Approved issue revision
- Issue: https://github.com/vkaam/phonebuddy/issues/65
- Approved requirements snapshot: updated 2026-11-01T15:29:46Z; SHA-256 bd0bdcb7269d5e1af66e6404a4d43d671089fabdb7814074c162e399a1bdbe76
- Approver and evidence: vkaam; the direct user instruction in the Codex conversation on 2026-11-02 explicitly authorized completing linked issue #65.

## Branch
agent/gh-65-1-safe-ci-caching

## Scope
- .github/workflows/ci.yml
- docs/quality-and-delivery.md
- backlog/tasks/task-56 - Cache-CI-dependencies-and-browser-tooling-safely.md (this task record only)

## Specification and constraints
Use a browser-cache key scoped to runner OS, architecture, Node version, and the package-lock hash, with an explicit cache-format version and no restore-key fallback. Measurements showed the current small npm graph downloads quickly and its 59 MB package-manager cache did not shorten npm ci, so do not cache npm. Keep npm ci and npm audit active on every run. Install only Chromium's headless shell because the configured smoke tests use Playwright's default headless Chromium mode; retain the full browser smoke tests and all source-bound evidence. Cache data must not flow into privileged workflows; do not add cache use to pull_request_target or consume caches as verification evidence. Record cold and warm hosted run durations and affected-step timings.

## Verification
- From repository root: python3 -B scripts/quality.py
- From repository root: python3 -B scripts/run_required_unittests.py
- From apps/web: npm ci --no-audit --no-fund; npm audit; npm run lint; npm test; npm run build; npx playwright install --with-deps --only-shell chromium; npm run test:browser
- Hosted gate: CI / Quality succeeds on the PR head, including actionlint and Gitleaks; record its source SHA and run URL.
- Performance evidence: report baseline, cold-cache, and warm-cache Quality job durations and relevant step durations from GitHub Actions, with run URLs and source SHAs. A cache hit alone is not a passing result.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Representative baseline and improved cold and warm CI durations are reported with run links, source revisions, and the affected steps.
- [x] #2 Dependency and browser caches use scoped, versioned keys that invalidate on relevant lockfile or toolchain changes, and cache misses still pass all checks.
- [x] #3 Locked installs, vulnerability scanning, browser smoke tests, required checks, and source-bound evidence remain active on every CI run; cache hits are not treated as verification.
- [x] #4 Cache trust boundaries prevent untrusted pull request data from influencing privileged workflows, and documentation records cache contents, invalidation, measurements, and remaining limitations.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Preserve source-bound uncached baseline and compare the first cache-enabled runs. 2. Remove the unhelpful npm cache and narrow Playwright installation/cache to the configured headless-shell smoke-test browser. 3. Use a new versioned key and current immutable cache action pin; document exact contents and trust boundaries. 4. Run local checks and hosted cold/warm CI; record job and step timings. 5. Finalize the task and publish one PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Uncached baseline from successful main runs (runner-log duration; web step): 45.4/31.1 s on bd99978362536dbf6d026ed47a7262b3ded57cd3 (run 41403043185), 35.8/24.6 s on 4ae593d03c0be3e1a41a8e34f7eb8ddc25e767a2 (run 41347032710), and 36.8/26.2 s on 19001039764ff8ccf0c061216ebbff583d15f4cd (run 41345888941). Medians: 36.8 s Quality job and 26.2 s web step. Sources and URLs are documented.

Final v2 cold run 41483343913 passed on 32b0aba2b1c00efc13194acb552dd6de7248b5c6 (38.0 s job log, 23.4 s web step; exact cache miss saved only headless shell/FFmpeg). Warm run 41483702707 passed on 365acdd69073b86091556f16837c9aa719a6bd4d (28.9 s job log, 16.1 s web step; 108 MiB exact-key hit, 3 browser tests passed). Final current-head run 41484042748 passed on 20dfba9fc03a1e627dcddae51657ca1d3fd7751a (32.8 s job log, 20.5 s web step; 108 MiB hit, 3 browser tests, actionlint, and Gitleaks passed). See https://github.com/vkaam/phonebuddy/actions/runs/41483343913, https://github.com/vkaam/phonebuddy/actions/runs/41483702707, and https://github.com/vkaam/phonebuddy/actions/runs/41484042748.

Local checks passed: repository quality, 35 Python tests, npm audit (0 vulnerabilities), lint, 5 required Node tests, build, and 3 browser smoke tests using only the Chromium headless shell. The first v1 experiment showed the npm cache did not help, so it was removed. PR #69 is awaiting independent review and merge; issue #65 remains open until the merge and aggregate gates.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added an immutable, v2-keyed Playwright headless-shell cache to CI, scoped by OS, architecture, Node 22.15.1, and package-lock hash. Removed npm caching after measurements showed no benefit for the 28-package graph. All locked installs, audit, tests, browser smoke tests, build, actionlint, Gitleaks, and source-bound artifacts continue to run on cache hits and misses. Documented trust boundaries, invalidation, limitations, and source-bound baseline/cold/warm timings. Local checks passed; hosted cold, warm, and current-head checks passed. Warm Quality job logs improved from a 36.8 s uncached median to 28.9 s, and the web step from 26.2 s to 16.1 s; results are observational, not controlled. PR #69 awaits independent review and merge. This branch-local Done state is provisional; issue #65 must remain open until merge and aggregate acceptance gates pass.
<!-- SECTION:FINAL_SUMMARY:END -->
