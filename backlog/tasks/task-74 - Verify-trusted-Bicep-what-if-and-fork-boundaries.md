---
id: TASK-74
title: Verify trusted Bicep what-if and fork boundaries
status: To Do
assignee: []
created_date: '2026-11-03T18:50:00Z'
updated_date: '2026-11-03T18:58:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-58
references:
  - https://github.com/vkaam/phonebuddy/issues/14
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
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml .github/workflows/azure-hosting-what-if.yml. After explicit approval for any required Azure permissions or live invocation, run the trusted dev what-if on merged main and retain source, permission and result evidence. Exercise fork and invalid-template failure paths through hosted CI and retain evidence; required hosted checks and independent review apply.
Spec: TASK-58 must be complete on default branch. Any workflow or permission changes require separately approved triage; preserve issue 14 aggregate acceptance.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A trusted main-only run produces complete scoped dev what-if evidence tied to the merged source, and documents identity permissions and any limitations.
- [ ] #2 Hosted tests demonstrate invalid templates and policy violations fail, and missing or incomplete evidence does not pass.
- [ ] #3 Hosted fork and PR tests demonstrate that untrusted code cannot obtain Azure deployment credentials.
<!-- AC:END -->
