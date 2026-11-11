---
id: TASK-80
title: Issue 91 - Fix Contributor-only dev hosting preview
status: Done
assignee:
  - '@codex'
created_date: '2026-11-10T20:42:00Z'
updated_date: '2026-11-11T07:20:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/91
  - .github/workflows/azure-hosting-what-if.yml
modified_files:
  - .github/workflows/azure-hosting-what-if.yml
  - tests/test_bicep_ci_boundary.py
  - backlog/tasks/task-80 - Issue-91-Fix-Contributor-only-dev-hosting-preview.md
priority: high
type: bug
ordinal: 70000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The trusted main-only dev hosting What-If failed because ARM prechecks required roleAssignments/write for the ACR pull role assignment even though the workflow is read-only and the GitHub dev identity has Contributor. Issue #91 proposes provider-level validation while preserving exact France Central dev scope and safety checks.

Issue: https://github.com/vkaam/phonebuddy/issues/91
Approved requirements revision: 2026-11-10T17:14:42Z; SHA-256 of UTF-8 issue body c666d098a222fc816c6ae70eaa283df54506869a011ea2672520e0ce39c9c82f.
Approval evidence: User explicitly requested “please fix issue #91” in this Codex conversation on 2026-11-10, approving the issue body’s proposed acceptance criteria.
Branch: fix/issue-91-contributor-hosting-preview
Scope: .github/workflows/azure-hosting-what-if.yml; tests/test_bicep_ci_boundary.py; this task's own CLI-managed record
Verify: python3 -B -m unittest tests.test_bicep_ci_boundary; python3 -B scripts/check_bicep.py; python3 -B scripts/check.py; actionlint .github/workflows/azure-hosting-what-if.yml. A trusted post-merge main-only What-If run is required as hosted evidence; no resource deployment or role grant is authorized.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The main-only dev hosting preview succeeds with the existing Contributor-only dev identity, without role-assignment write permission or resource deployment.
- [x] #2 Provider-level validation and the exact France Central dev scope check remain enforced; unexpected deletes or ignored resources fail the preview gate.
- [x] #3 Boundary tests, pinned Bicep validation, local Quality, and a trusted post-merge What-If run pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the hosting What-If workflow and its CI boundary tests; identify the current ARM validation invocation and preserved scope/evidence checks. 2. Change only the workflow and boundary test so provider validation skips the Contributor-incompatible RBAC precheck while retaining the France Central dev scope and failure gates. 3. Run the focused boundary test, pinned Bicep validation, local Quality and actionlint. 4. Commit and push this branch, open or reuse its PR, and report hosted checks; after merge, confirm the trusted main-only What-If run without deploying resources.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Focused boundary unittest passed (4 tests). Pinned Bicep 0.34.44 baseline passed with BICEP=/tmp/bicep. Pinned actionlint 1.7.12 passed on the changed workflow. Local scripts/check.py ran all checks; only web-browser failed because Chromium could not load the missing system library libnspr4.so (and related Chromium dependencies). Installing system packages was unavailable because sudo requires a password. Hosted PR checks and a trusted post-merge What-If remain outstanding; no deployment or role grant was performed.

Draft PR: https://github.com/vkaam/phonebuddy/pull/94. Hosted pull-request run 42900765001 completed successfully on head d2ddb11be7b7f7a1af6141c25c774cd679ead2ea; Quality job completed successfully, including repository checks, issue/Backlog consistency, web tests, workflow validation, pinned Bicep validation, and Gitleaks. Risk report 42900765025 also passed. Acceptance remains incomplete until the trusted main-only What-If runs on the merged fix; PR remains draft pending review/merge controls and that hosted evidence.

Independent read-only review completed on PR #94 head 1f256dfcbd1197c8316a99b9735163fc2b875547; reviewer found no blocking code findings and recommends merge. Reviewer verified ProviderNoRbac semantics, manual main-only gate, exact France Central scope check, fail-closed delete/unexpected-ignore validation, and current-head hosted checks. Review evidence is the independent Codex agent review in this task conversation; no GitHub approval review was submitted. Current-head Quality run 42901437593 and Risk report 42901432379 passed. Remaining required evidence is the manual trusted main-only What-If after merge.

Reconciled on 2026-11-11 from the merged TASK-80 feature branch and current hosted evidence. PR #94 merged at 6c716b92f097d93fc42f275fbdcce8388baa93cb. Default-branch Quality run 42903321260 passed; trusted main-only Dev hosting What-If run 42903622293 passed on the merge commit using the existing Contributor-only dev identity, validating ProviderNoRbac and exact France Central scope without deployment. The feature branch records focused boundary tests (4 passed), pinned Bicep 0.34.44, actionlint 1.7.12, and local Quality passed after extracting Chromium dependencies. No role grant or resource deployment occurred.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
PR #94 merged the Contributor-compatible ProviderNoRbac dev hosting preview while preserving the manual main-only gate, exact France Central scope, and fail-closed delete/ignored-resource checks. Boundary tests, pinned Bicep, actionlint, local and hosted Quality, and the trusted post-merge What-If passed. The preview used the existing Contributor identity and did not deploy resources or grant roles.
<!-- SECTION:FINAL_SUMMARY:END -->
