---
id: TASK-58
title: Issue 14 - Validate Bicep changes in pull-request CI
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:35:00Z'
updated_date: '2026-11-02T20:26:00Z'
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
1. Add pinned, digest-verified Bicep validation to the existing required Quality job, with no Azure credentials on PR runs. 2. Run the prescribed local checks and verify the workflow configuration. 3. Publish a draft PR and record any remaining trusted what-if and hosted fork-evidence gates; keep the task active until they are satisfied.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added the existing pinned Bicep preflight to the required Quality job without Azure credentials. Local Bicep 0.34.44 preflight and actionlint 1.7.12 passed. Authenticated what-if, hosted invalid-template and fork credential evidence remain outstanding; TASK-57 identity bootstrap remains in open PR #55. The first local baseline was blocked by sandbox DNS and loopback restrictions; retrying with access.
<!-- SECTION:NOTES:END -->
