---
id: TASK-58
title: Issue 14 - Validate Bicep changes in pull-request CI
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:35:00Z'
updated_date: '2026-11-03T18:44:00Z'
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
modified_files:
  - .github/workflows/ci.yml
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
Scope: .github/workflows/ci.yml; scripts/check_bicep.py; infra/**; tests/**; backlog/tasks/task-58 - Issue-14-Validate-Bicep-changes-in-pull-request-CI.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted checks must prove invalid templates fail and fork PRs never receive Azure credentials; authenticated what-if is restricted to the trusted scoped path.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Required CI checks lint/build Bicep, validate parameters and workflows with pinned tooling.
- [ ] #2 Authenticated what-if uses a trusted scoped path; arbitrary PR code never runs with deployment credentials.
- [ ] #3 Invalid templates, policy violations and missing evidence produce explicit failures; fork handling is tested.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Retain credential-free pinned Bicep validation in the required Quality job and integrate current main. 2. Add a separately gated manual, main-only trusted what-if path in the approved CI workflow, with environment-scoped OIDC and no credentialed PR execution, after review of its precise scope and permissions. 3. Exercise invalid-template and fork credential boundaries and capture hosted evidence. 4. Verify the trusted what-if in an explicitly approved nonproduction scope, then record evidence and complete review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added the existing pinned Bicep preflight to the required Quality job without Azure credentials. Local Bicep 0.34.44 preflight and actionlint 1.7.12 passed. Authenticated what-if, hosted invalid-template and fork credential evidence remain outstanding; TASK-57 identity bootstrap remains in open PR #55. The first local baseline was blocked by sandbox DNS and loopback restrictions; retrying with access.

Blocked after integrating latest main: mandatory live claim check reports TASK-57 issue body changed and requires authorized triage reassessment. Hook-generated .github-scripts_WARNINGS.txt was removed. Authenticated what-if and hosted fork/invalid-template evidence remain incomplete; do not resume until the live claim check succeeds.

Draft PR: https://github.com/vkaam/phonebuddy/pull/74. Work remains blocked pending the mandatory live claim check and the outstanding acceptance evidence.

2026-11-03: Integrated origin/main 31eed2478721ad27cefb380cb1ba60ffff7f2c49; mandatory live claim verification passed. Full local baseline passed (phonebuddy-quality-s9kjnhvw), Bicep 0.34.44 preflight and actionlint 1.7.12 passed. The trusted what-if workflow design, permitted Azure deployment scope and required hosted fork/invalid-template evidence remain unresolved; no Azure credentials were used.
<!-- SECTION:NOTES:END -->
