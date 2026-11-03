---
id: TASK-74
title: Verify trusted Bicep what-if and fork boundaries
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-03T18:50:00Z'
updated_date: '2026-11-03T19:25:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-58
references:
  - https://github.com/vkaam/phonebuddy/issues/14
  - https://github.com/vkaam/phonebuddy/actions/runs/41699912355
  - https://github.com/vkaam/phonebuddy/pull/80
priority: high
type: task
ordinal: 68000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Verify issue 14 trusted what-if and untrusted PR boundaries after the workflow is merged to main.

Issue: https://github.com/vkaam/phonebuddy/issues/14
Approved revision: 2026-11-01T09:24:44Z; body SHA-256 17ae7da5cbf33307a4ab96b173258c85762f3764cdf30382143091346eb1ef09.
Approval evidence: Owner requested the trusted job and corrected project management in this Codex chat on 2026-11-03, including a post-merge verification split. This does not authorize Azure role changes, deployment, merge or issue closure.
Branch: agent/gh-14-2-what-if-verification
Scope: backlog/tasks/task-74 - Verify-trusted-Bicep-what-if-and-fork-boundaries.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml .github/workflows/azure-hosting-what-if.yml. After explicit approval for any required Azure permissions or live invocation, run the trusted dev what-if on merged main and retain source, permission and result evidence. Exercise invalid-template failure paths and the PR credential-boundary regression through hosted CI and retain evidence; the owner directed skipping the live fork PR on 2026-11-03; required hosted checks and independent review apply.
Spec: TASK-58 must be complete on default branch. Any workflow or permission changes require separately approved triage; preserve issue 14 aggregate acceptance.

Triage amendment 2026-11-03: The owner directed skipping the real fork PR test. Record the hosted static workflow-boundary regression honestly; do not describe it as an observed fork run or rewrite issue #14 acceptance.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A trusted main-only run produces complete scoped dev what-if evidence tied to the merged source, and documents identity permissions and any limitations.
- [ ] #2 Hosted tests demonstrate invalid templates and policy violations fail, and missing or incomplete evidence does not pass.
- [x] #3 Hosted regression checks verify the credentialed workflow is manual-only and excludes PR events; the owner waived the separate live fork PR test.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Record the successful trusted main what-if run and verify its source and identity permission evidence. 2. Inspect existing hosted PR, fork and failure-path runs for objective evidence; perform only authorized tests within the task scope. 3. Run the declared local and hosted checks, record any missing evidence or blockers, and publish the task record for independent review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Run 41699912355 attempt 3 succeeded on merged main 8eed705c322f06d0690e860ec56fe555c7d4faba. It verified exact-commit Quality, authenticated via dev OIDC, and reported six Create changes for the dev hosting preview with deployWorkload=false; the workflow records counts only, not detailed resource changes. Read-only Azure RBAC readback found Contributor and Role Based Access Control Administrator on the dev foundation group with no condition; this is a shared dev/test identity and is not evidence of least privilege or lack of other permissions. No resources were deployed. Hosted Quality 41699306514 exercised invalid-environment and failure-path regression tests on the implementation PR, but no actual cross-repository fork PR was found and the full hosted evidence is incomplete.

Local checks passed on the current verification branch: full baseline phonebuddy-quality-ir3rjeme, pinned Bicep 0.34.44, actionlint 1.7.12 and git diff --check. Hosted implementation PR tests cover several invalid inputs and policy/failure cases, but no hosted malformed-template PR or actual fork PR has been evidenced. The successful live run reports only change counts and no retained per-resource preview; a complete auditable preview remains unverified. All acceptance criteria remain open.

Draft PR #80 records current verification evidence. Hosted fork PR, hosted malformed-template failure and detailed retained preview evidence remain open; the unconditioned dev RBAC Administrator grant also requires owner review. Do not mark complete on the successful preview alone.

Owner direction 2026-11-03: skip the real fork PR test. Hosted Quality run 41699306514 passed test_azure_identity_is_confined_to_manual_main_workflow, which statically checks that PR events cannot trigger the credentialed workflow and the ordinary CI workflow does not request an OIDC token. This is static workflow evidence, not an observed fork execution; issue-level acceptance and its owner decision remain visible. The malformed-template and detailed what-if evidence gaps remain open.

Acceptance #3 is checked only for the owner-approved static boundary regression and fork-test waiver, backed by hosted Quality run 41699306514. No actual fork execution is claimed.
<!-- SECTION:NOTES:END -->
