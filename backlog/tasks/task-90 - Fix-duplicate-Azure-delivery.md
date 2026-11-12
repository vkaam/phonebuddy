---
id: TASK-90
title: Fix duplicate Azure delivery
status: Done
assignee:
  - '@codex'
created_date: '2026-11-11T18:05:00Z'
updated_date: '2026-11-12T05:10:00Z'
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
- [x] #1 Duplicate delivery detects and reuses a matching immutable image after verification; writable or mismatched images fail closed.
- [x] #2 An absent tag follows the normal publication path, with automated tests covering both lookup paths.
- [x] #3 Relevant local and hosted checks pass; the live duplicate-delivery verification is tracked separately in TASK-92.
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

The first hosted run using Bicep 0.34.44 showed that its full-path scope representation differs from Bicep 0.49.2 resourceId() output. Scope validation now recognizes both expression shapes, requires exact Microsoft.App resource type boundaries and environment-derived resource names, and rejects wrong types/targets. Local 0.49.2 Bicep validation, 43 relevant tests, and repository checks pass; hosted 0.34.44 must be rerun on the latest head.

Hosted CI run 43158391782 passed on head e48e6b365bafecc6b583704eb10b6694b0246fa3. Its Bicep validation step used the CI-pinned Bicep CLI 0.34.44 and passed with the legacy full-path diagnostic scope form. Local Bicep CLI 0.49.2 validation, all 43 scoped tests, and repository checks also pass. The branch includes fetched origin/main 3124b948272a3a8f3dd5a1b6cc8f19e5c4937765.

Follow-up independent review identified that substring matching could accept an unused expected-name argument while the actual format placeholder targeted another name. Scope validation now parses the outer ARM function arguments and verifies the exact target placeholder argument for full-path expressions; regression tests reject this extra-argument case as well as wrong resource types and names. Bicep 0.49.2 validation, all 43 scoped tests, and repository checks pass locally.

Hosted run 43158899927 still failed Bicep 0.34.44 scope validation, despite the local 0.49.2 check and 43 tests passing. Added the compiler-emitted scope expressions to the sanitized validation error to identify the exact legacy shape and complete the compatibility fix.

Hosted Bicep 0.34.44 diagnostics show the legacy scope shape is format("Microsoft.App/<resourceType>/{0}", <expected environment name>), with no providers prefix. The parser and regression tests now support that exact type/name placeholder form alongside 0.34 full-path and 0.49.2 resourceId forms. Wrong placeholder arguments remain rejected. Local Bicep 0.49.2 validation and 43 scoped tests pass; latest 0.34.44 hosted rerun is pending.

Final verification: hosted Quality run 43159359422 passed on the current PR head 46994cc, including Bicep 0.34.44, all required repository and workflow checks, and PR task-claim validation. Independent review of 46994cc found no remaining issues. The fetched latest main is 3124b948272a3a8f3dd5a1b6cc8f19e5c4937765 and is an ancestor of the PR branch. Local Bicep 0.49.2, the 43 focused tests, and scripts/quality.py pass. Live duplicate-delivery deployment verification remains in approved follow-up TASK-92.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Fixed duplicate Azure delivery tag detection and verification, removed the exact Bicep CLI version gate, and made compiled Bicep checks accept both CLI 0.34.44 and 0.49.2 output forms. Validation passed locally on 0.49.2 with 43 scoped tests and scripts/quality.py; hosted Quality run 43159359422 passed on PR head 46994cc using 0.34.44. Independent review found no remaining issues. PR #106 is ready to merge. Live duplicate-delivery deployment verification remains tracked in TASK-92 after merge.
<!-- SECTION:FINAL_SUMMARY:END -->
