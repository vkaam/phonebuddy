---
id: TASK-77
title: Allow intentional workload ignores in the trusted Bicep what-if
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-04T06:02:00Z'
updated_date: '2026-11-04T06:13:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/17
modified_files:
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - tests/test_bicep_ci_boundary.py
  - >-
    backlog/tasks/task-77 -
    Allow-intentional-workload-ignores-in-the-trusted-Bicep-what-if.md
priority: high
type: bug
ordinal: 70000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The trusted main-only dev hosting What-if on merged main 6ce96012526ec1790d631361b86688cd64d25903 failed because the checker rejects the release-test App and its three health alert rules returned as Ignore when deployWorkload=false. Preserve fail-closed protection while accepting only resources intentionally omitted by this preview mode.

Issue: https://github.com/vkaam/phonebuddy/issues/17
Approved revision: 2026-11-01T09:24:54Z; body SHA-256 8d4a38d23215c8706bc19f086c585b9ebcafe76dfe747de51edbbbd35951d749.
Approval evidence: The approved Issue #17 scope explicitly includes scripts/** and tests/**, including this checker and its validation tests. On 2026-11-04 the user reported the merged-main What-if failure and instructed us to fix it without reopening Issue #14. Reproduction against the same merged template/parameters showed Ignore entries for the conditional dev release-test Container App and its three scheduled query rules, plus the already-approved Azure-managed Smart Detection action group. This task corrects only the checker and tests for those exact conditional resources; it does not change the Issue #17 acceptance criteria or perform Azure deployment/alert validation.
Branch: agent/gh-17-2-what-if-workload-ignore
Scope: scripts/check_bicep.py; tests/test_bicep_preflight.py; tests/test_bicep_ci_boundary.py; backlog/tasks/task-77 - Allow-intentional-workload-ignores-in-the-trusted-Bicep-what-if.md.
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py, and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml .github/workflows/azure-hosting-what-if.yml. Run the trusted read-only dev what-if with deployWorkload=false and validate its JSON using python3 -B scripts/check_bicep.py --what-if-result PATH; no deployment is part of this task.
Spec: Accept only the exact dev/test release-test App and the three named health alert rules when they are returned as Ignore, plus the Azure-managed Smart Detection action group. Unknown or unexpected Ignore entries must continue to fail. Preserve the Issue 17 acceptance criteria.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The checker accepts only the known conditional dev/test release-test App and three scheduled health alert rules as Ignore entries, as well as the Azure-managed Smart Detection action group.
- [ ] #2 Tests prove that unknown or unexpected ignored resource IDs still fail closed and that the known conditional resources pass.
- [ ] #3 The trusted dev what-if from merged main passes validation with the expected Ignore entries and no deployment is performed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm the trusted dev What-if Ignore resource IDs and the Bicep-generated dev/test resource names.
2. Update the validator to allow only Smart Detection plus the exact conditional release-test app and three health alert rules in the expected dev/test foundation resource groups.
3. Add tests covering all intentional IDs and fail-closed unknown IDs, then run local Bicep, Python, workflow, and read-only What-if validation.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reproduced merged-main run 41781619804 locally with deployWorkload=false. Azure returned five Ignore entries: Smart Detection, the conditional dev release-test app, and its three scheduled query rules. No deployment was performed.

Implementation: validate_what_if now accepts only the prior Smart Detection suffix plus exact release-test Container App and the three named health scheduled query rules for dev/test foundation resource groups. IDs must include a canonical subscription GUID; prod, wrong resource group, wrong type/name, and malformed IDs continue to fail closed.
Local validation: 20 focused Bicep tests passed; python3 -B scripts/check.py passed (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-61b4ud7c/report.json); pinned Bicep 0.34.44 check passed; actionlint on ci.yml, pr-safety.yml, and azure-hosting-what-if.yml passed. Saved read-only dev What-if passed with 0 Create, 6 Modify, 3 NoChange, and 5 Ignore entries, including the four conditional workload resources. No deployment or telemetry drill occurred.
<!-- SECTION:NOTES:END -->
