---
id: TASK-90
title: Fix duplicate Azure delivery
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T18:05:00Z'
updated_date: '2026-11-11T19:36:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/105
modified_files:
  - backlog/tasks/task-90 - Fix-duplicate-Azure-delivery.md
  - .github/workflows/azure-deploy.yml
  - tests/test_deployment_policy.py
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - tests/test_bicep_ci_boundary.py
  - docs/quality-and-delivery.md
  - backlog/tasks/task-92 - Verify-live-duplicate-Azure-delivery.md
priority: low
type: bug
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: A repeated delivery can fail when an immutable image tag already exists because the ACR tag query expects objects but receives strings.

Issue: https://github.com/vkaam/phonebuddy/issues/105
Approved revision: 2026-11-11T18:04:24Z; body SHA-256 a8f1aa6aca896b074222f04e010eea6eb2c296d0d6825ceae38933a2abeceecb.
Approval evidence: The owner requested a low-priority follow-up in Codex on 2026-11-11. The owner approved the split and post-merge verification on 2026-11-11; see https://github.com/vkaam/phonebuddy/issues/105#issuecomment-6804113134. The owner later directed that the Bicep validation work support both the repository's CI version and the newer installed version.
Branch: agent/gh-105-duplicate-delivery
Scope: .github/workflows/azure-deploy.yml; tests/test_deployment_policy.py; scripts/check_bicep.py; tests/test_bicep_preflight.py; tests/test_bicep_ci_boundary.py; docs/quality-and-delivery.md; backlog/tasks/task-90 - Fix-duplicate-Azure-delivery.md; backlog/tasks/task-92 - Verify-live-duplicate-Azure-delivery.md
Verify: python3 -B scripts/check.py; python3 -B scripts/check_bicep.py; tests/test_bicep_preflight.py; actionlint .github/workflows/ci.yml .github/workflows/azure-deploy.yml .github/workflows/pr-safety.yml. Live duplicate-delivery verification is assigned to TASK-92 after this fix merges.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Duplicate delivery detects and reuses a matching immutable image after verification; writable or mismatched images fail closed.
- [ ] #2 An absent tag follows the normal publication path, with automated tests covering both lookup paths.
- [ ] #3 Relevant local and hosted checks pass; the live duplicate-delivery verification is tracked separately in TASK-92.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the release workflow and existing tests for tag detection and immutable image verification. 2. Correct tag detection and add meaningful coverage for existing and absent tags and fail-closed verification. 3. Run the declared local checks and publish the existing draft PR. 4. Obtain independent review, required hosted checks and available duplicate-delivery evidence before finalizing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The ACR lookup now requests detailed tag objects before filtering by name. Focused policy and workflow tests pass locally; the behavioral promotion-step test requires Bash and is skipped on this Windows host. Full scripts/check.py failed locally and check_bicep.py could not find Bicep; hosted checks and duplicate-delivery Azure evidence remain required. Independent review identified the missing workflow-level coverage, which is now added but awaits execution in hosted CI.

PR #106 head 5097d99e4edd7608c8f62df07fa1c29ca6232923 passed hosted Quality run 43076192295 attempt 2, including the Linux behavioral tests, actionlint and Bicep validation. An independent agent reviewed that exact tree and found no additional scoped defects; live Azure duplicate-delivery evidence remains outstanding. The current host has no Azure CLI or Docker.

Read-only Azure evidence (2026-11-11): the installed Azure CLI and dev account are available. Against the existing main-source tag 63e88d30f87c392814fb7c859b96724f868285d1, the detailed ACR lookup returned the tag with writeEnabled false; the earlier query without --detail returned no match. A detailed lookup for an absent all-zero tag returned no match. This verifies live query behavior only, not full image reuse or duplicate deployment. Docker remains unavailable on this host.

Owner directed removing the strict Bicep CLI version gate because the installed newer version should be accepted; this adds scripts/check_bicep.py to the task scope.

Owner requested removing the exact Bicep version check. scripts/check_bicep.py no longer requires 0.34.44 and accepts the installed 0.49.2, but the full Bicep check then failed its existing compiled logging contract: Console and system logs must route from the Container Apps environment. scripts/check.py also remains failing locally; see local report from the latest run.

Bicep 0.49.2 validation now passes locally with python3.15.exe -B scripts/check_bicep.py. All 36 tests in tests.test_bicep_preflight pass, including checks for both the 2022-09-01 and 2025-04-01 compiler-emitted output API versions and rejection of unrelated references; all 6 tests in tests.test_bicep_ci_boundary pass. Updated docs/quality-and-delivery.md to state CI uses 0.34.44 and 0.49.2 passed locally. The full scripts/check.py baseline still reports failure on this Windows host; python3.15.exe -B scripts/quality.py passes. The live backlog claim guard could not read the GitHub CLI token on this host and did not verify the claim. Hosted CI with Bicep 0.34.44 remains required on the updated PR head.

Independent review found the compiler-compatibility substring check for diagnostic scopes could accept similarly named incorrect resource types. The validator now requires the exact compiler-generated environment and app resource ID expressions, including expected resource names. Added negative tests for wrong types and targets. Re-ran Bicep 0.49.2 baseline validation, all 43 relevant preflight and CI-boundary tests, and repository checks successfully.
<!-- SECTION:NOTES:END -->
