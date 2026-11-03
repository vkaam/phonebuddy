---
id: TASK-58
title: Issue 14 - Validate Bicep changes in pull-request CI
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:35:00Z'
updated_date: '2026-11-03T18:58:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
references:
  - https://github.com/vkaam/phonebuddy/issues/14
  - .github/workflows/ci.yml
  - scripts/check_bicep.py
  - infra/main.bicep
  - https://github.com/vkaam/phonebuddy/pull/74
  - TASK-74
modified_files:
  - .github/workflows/ci.yml
  - infra/README.md
  - backlog/tasks/task-74 - Verify-trusted-Bicep-what-if-and-fork-boundaries.md
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - tests/test_bicep_ci_boundary.py
  - .github/workflows/azure-hosting-what-if.yml
priority: high
type: task
ordinal: 55000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/14
Approved revision: 2026-11-01T09:24:44Z; body SHA-256 17ae7da5cbf33307a4ab96b173258c85762f3764cdf30382143091346eb1ef09.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-14-1-bicep-pr-validation
Scope: .github/workflows/ci.yml; .github/workflows/azure-hosting-what-if.yml; scripts/check_bicep.py; infra/**; tests/**; backlog/tasks/task-58 - Issue-14-Validate-Bicep-changes-in-pull-request-CI.md; backlog/tasks/task-74 - Verify-trusted-Bicep-what-if-and-fork-boundaries.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted checks validate the implementation PR. Post-merge trusted what-if and hosted fork and failure-path evidence are retained in TASK-74.
Spec: Owner-approved split on 2026-11-03: TASK-58 implements the trusted what-if job and credential-free PR validation; TASK-74 retains post-merge what-if and hosted fork and failure-path evidence. Issue #14 aggregate acceptance remains unchanged. No Azure role changes, live run, merge or issue closure are authorized by this split.

Triage amendment 2026-11-03: The owner requested creation of the trusted job and correct project management. A separate manual-only workflow is included in scope so PRs do not create an intentionally skipped credentialed check. The job remains main-only and uses the dev environment; live verification stays in TASK-74.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Required Quality CI lints and builds Bicep, validates parameters and workflows with pinned tooling, without Azure credentials in PR jobs.
- [ ] #2 A manually requested main-only dev job is configured for environment-scoped authentication and hosting what-if, and is excluded from PRs.
- [ ] #3 Missing, incomplete or uncertain what-if evidence fails; usage, permissions and retained live verification are documented and required checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add digest-verified Bicep validation to credential-free Quality checks. 2. Implement the owner-approved manual main-only dev hosting what-if job with environment-scoped OIDC and fail-closed evidence validation. 3. Test the workflow boundary and invalid or incomplete evidence, run required checks and document operation and permissions. 4. Publish for independent review; TASK-74 retains the post-merge live what-if and hosted fork/failure evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added the existing pinned Bicep preflight to the required Quality job without Azure credentials. Local Bicep 0.34.44 preflight and actionlint 1.7.12 passed. Authenticated what-if, hosted invalid-template and fork credential evidence remain outstanding; TASK-57 identity bootstrap remains in open PR #55. The first local baseline was blocked by sandbox DNS and loopback restrictions; retrying with access.

Blocked after integrating latest main: mandatory live claim check reports TASK-57 issue body changed and requires authorized triage reassessment. Hook-generated .github-scripts_WARNINGS.txt was removed. Authenticated what-if and hosted fork/invalid-template evidence remain incomplete; do not resume until the live claim check succeeds.

Draft PR: https://github.com/vkaam/phonebuddy/pull/74. Work remains blocked pending the mandatory live claim check and the outstanding acceptance evidence.

2026-11-03: Integrated origin/main 31eed2478721ad27cefb380cb1ba60ffff7f2c49; mandatory live claim verification passed. Full local baseline passed (phonebuddy-quality-s9kjnhvw), Bicep 0.34.44 preflight and actionlint 1.7.12 passed. The trusted what-if workflow design, permitted Azure deployment scope and required hosted fork/invalid-template evidence remain unresolved; no Azure credentials were used.

Triage amendment 2026-11-03: The owner requested the trusted main-only what-if job and a project-management split so its live execution can be verified after merge. TASK-58 implements the workflow and validates its credential boundary and local checks. A follow-up task retains post-merge hosted what-if, fork, invalid-template and policy-failure evidence. Issue #14 acceptance remains unchanged. The user authorized the necessary follow-up task record and its inclusion in PR #74; no Azure role changes or live execution are authorized by this amendment.

Implemented the owner-requested manual main-only dev hosting what-if job in the existing CI workflow. It runs after Quality, uses the existing dev environment and fixed resource group, compiles the main-branch template with pinned Bicep, invokes what-if only, and rejects missing or uncertain output. TASK-74 retains live Azure, fork and hosted failure evidence; no role changes or live invocation performed. The current Contributor identity may lack role-assignment permissions needed for what-if.

Implementation verification: full local baseline passed (phonebuddy-quality-cgw3n2iv); Bicep 0.34.44, actionlint 1.7.12, 15 focused tests, live claim check and diff check passed. PR/fork execution boundaries and unsuccessful what-if inputs have local regression coverage; hosted fork behavior and live Azure results remain TASK-74. No live preview has been run and identity permissions remain unverified.

After correcting Azure CLI flattened what-if result handling, full local baseline passed (phonebuddy-quality-3xghbou5), pinned Bicep and actionlint passed, and focused tests cover missing, failed, uncertain and incomplete results plus the PR credential boundary. The job has not been run against Azure; TASK-74 retains that evidence and hosted fork/failure verification.

The manual what-if is now a separate workflow so normal PRs do not receive a skipped credentialed-job check. Before Azure login it requires the latest GitHub Actions Quality check for the exact source commit to have completed successfully. The workflow itself remains manual, main-only and scoped to the dev environment; live proof remains TASK-74.

Integrated main db48351 and validated the separate manual-only workflow: full local baseline phonebuddy-quality-xt43ehxy passed; pinned Bicep, actionlint for all three workflows, focused Quality-evidence and what-if tests, and diff checks passed. TASK-74 remains responsible for actual Azure what-if and hosted fork/failure evidence.
<!-- SECTION:NOTES:END -->
