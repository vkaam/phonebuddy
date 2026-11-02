---
id: TASK-56
title: Cache CI dependencies and browser tooling safely
status: In Progress
assignee:
  - '@vkaam'
created_date: '2026-11-02T16:21:00Z'
updated_date: '2026-11-02T16:36:00Z'
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
- Approver and evidence: vkaam; direct user instruction in the Codex conversation on 2026-11-02: “Issue #65, please complete this issue.”

## Branch
agent/gh-65-1-safe-ci-caching

## Scope
- .github/workflows/ci.yml
- docs/quality-and-delivery.md
- backlog/tasks/task-56 - Cache-CI-dependencies-and-browser-tooling-safely.md (this task record only)

## Specification and constraints
Use a browser-cache key scoped to runner OS, architecture, Node version, and the package-lock hash, with an explicit cache-format version and no restore-key fallback. Measurements showed the current small npm graph downloads quickly and its 59 MB package-manager cache did not shorten `npm ci`, so do not cache npm. Keep `npm ci` and `npm audit` active on every run. Install only Chromium's headless shell because the configured smoke tests use Playwright's default headless Chromium mode; retain the full browser smoke tests and all source-bound evidence. Cache data must not flow into privileged workflows; do not add cache use to `pull_request_target` or consume caches as verification evidence. Record cold and warm hosted run durations and affected-step timings.

## Verification
- From repository root: python3 -B scripts/quality.py
- From repository root: python3 -B scripts/run_required_unittests.py
- From apps/web: npm ci --no-audit --no-fund; npm audit; npm run lint; npm test; npm run build; npx playwright install --with-deps --only-shell chromium; npm run test:browser
- Hosted gate: CI / Quality succeeds on the PR head, including actionlint and Gitleaks; record its source SHA and run URL.
- Performance evidence: report baseline, cold-cache, and warm-cache Quality job durations and relevant step durations from GitHub Actions, with run URLs and source SHAs. A cache hit alone is not a passing result.
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
1. Preserve source-bound uncached baseline and compare the first cache-enabled runs. 2. Remove the unhelpful npm cache and narrow Playwright installation/cache to the configured headless-shell smoke-test browser. 3. Use a new versioned key and current immutable cache action pin; document exact contents and trust boundaries. 4. Run local checks and hosted cold/warm CI; record job and step timings. 5. Finalize the task and publish one PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Baseline evidence from uncached main runs: latest Quality run 41403043185 on bd99978362536dbf6d026ed47a7262b3ded57cd3 took 52 seconds (https://github.com/vkaam/phonebuddy/actions/runs/41403043185); Build and test web shell took 31.1 seconds and installed Chromium 156 / Playwright v1248 browser binaries (~8.3 seconds of downloads) plus Linux dependencies. Recent comparison runs 41347032710 on 4ae593d03c0be3e1a41a8e34f7eb8ddc25e767a2 took 42 seconds (https://github.com/vkaam/phonebuddy/actions/runs/41347032710), and 41345888941 on 19001039764ff8ccf0c061216ebbff583d15f4cd took 41 seconds (https://github.com/vkaam/phonebuddy/actions/runs/41345888941). The three-run uncached median is 42 seconds; the combined build/test step spans 24.6–31.1 seconds. This is observational baseline only; hosted cold and warm cache runs remain required.

Implemented caches in CI: setup-node caches the lockfile-keyed npm download store, and actions/cache v4.2.4 caches the Playwright browser directory with a versioned OS/architecture/Node/lockfile key and no restore-key fallback. npm ci, npm audit, playwright install --with-deps, browser tests, and the existing verification/evidence steps remain unconditional. Documentation records baseline runs and states the privileged PR safety workflow does not consume CI caches.

Local verification passed on 2026-11-02: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py (35 tests); from apps/web, npm ci --no-audit --no-fund, npm audit (0 vulnerabilities), npm run lint, npm test (5 tests), npm run build, npx playwright install chromium (macOS-supported; downloaded Chromium 156 / Playwright v1248), and npm run test:browser (3 passed). Hosted Ubuntu CI remains necessary to validate the workflow with --with-deps, actionlint, Gitleaks, and cache timings.

Cold hosted cache run on PR #69: run 41481776795 succeeded on source efd31c6182add1ae36b4679696f8cf906be47a7b in 50 seconds (https://github.com/vkaam/phonebuddy/actions/runs/41481776795). Both npm and Playwright caches missed and were saved. Build and test web shell took 19.2 seconds; browser binary downloads took 5.2 seconds. This is within the uncached 41–52 second range but above its 42-second median; no cold-run improvement is claimed. Warm cache measurement remains outstanding.

First v1 warm-cache experiment on PR #69 succeeded: run 41482167446 restored a 59 MB npm cache and 279 MB Playwright cache; browser binaries were restored and not downloaded, but npm ci still took about 2 seconds. The Quality log span was about 35.8 seconds versus 35.4 seconds for the cold experiment, with variability in uncached Linux dependency installation. The npm cache provided no measured improvement, and the combined browser cache was larger than needed. Narrowing the browser install to the configured headless shell and dropping the npm cache before final performance measurement.

Adjusted the workflow after the v1 warm-cache experiment: removed setup-node npm caching because a cache hit did not reduce the 2-second locked install; changed Playwright to --with-deps --only-shell for the configured default-headless Chromium tests; changed the cache format key to v2 to avoid restoring the old 279 MB full-browser cache; pinned actions/cache v6.1.0 at immutable commit 55cc8345863c7cc4c66a329aec7e433d2d1c52a9.

Updated the documentation for the final design: v2 caches only Chromium headless-shell files, npm caching was dropped based on the measured no-benefit experiment, and baseline job durations now use first-to-last timestamps from runner logs (excluding queue/control-plane delays).

Final design local verification on 2026-11-02: repository quality check passed; 35 Python tests passed; npm audit reported 0 vulnerabilities; web lint passed; all 5 required Node tests passed; TypeScript/Vite build passed; Playwright 1.64.1 installed only Chromium headless shell in an isolated /private/tmp browser directory and all 3 browser smoke tests passed. Hosted Ubuntu v2 cold/warm runs and final PR-head CI are still required.
<!-- SECTION:NOTES:END -->
