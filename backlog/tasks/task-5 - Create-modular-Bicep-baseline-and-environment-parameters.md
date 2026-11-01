---
id: TASK-5
title: Create modular Bicep baseline and environment parameters
status: Done
assignee:
  - '@codex'
created_date: '2026-10-29T20:04:00Z'
updated_date: '2026-11-01T13:39:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-4
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - docs/azure-delivery-policy.md
  - infra/main.bicep
  - https://github.com/vkaam/phonebuddy/pull/8
  - https://github.com/vkaam/phonebuddy/issues/12
  - https://github.com/vkaam/phonebuddy/pull/50
  - https://github.com/vkaam/phonebuddy/pull/52
  - https://github.com/vkaam/phonebuddy/pull/53
modified_files:
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - infra/environments/prod.bicepparam
  - scripts/check_bicep.py
  - infra/README.md
  - tests/test_bicep_preflight.py
  - >-
    backlog/tasks/task-5 -
    Create-modular-Bicep-baseline-and-environment-parameters.md
priority: high
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Complete the approved foundation-only Azure baseline for issue #12.

Approved issue revision: https://github.com/vkaam/phonebuddy/issues/12 updated 2026-11-01T13:37:06Z; body SHA-256 c16d37b5fb3aa9da273743c6ec8e8f968e6c655f2953e19f412fd15af20b05f2. Approval evidence: direct user reply on 2026-11-01 approving the narrow foundation-only scope and assigning application capacity to TASK-8.

Branch: agent/gh-12-5-finalize-foundation-task.
Scope: the existing foundation Bicep entry point/module, environment parameter files, preflight validator/tests, foundation runbook, and this task record through the Backlog CLI. Application hosting, application capacity, workload authorization, network/data isolation and production provisioning remain out of scope and belong to TASK-8 and downstream tasks.

Evidence: merged foundation work in PRs #50, #52 and #53; verify with pinned Bicep 0.34.44, dev/test deployment-readiness checks, focused unittest suite, git diff --check and recorded Azure deployment/what-if/budget readback. No credentials or private identifiers may be committed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Pinned Bicep tooling builds and lints the entry point and all environment parameter files; invalid inputs fail.
- [x] #2 The foundation uses deterministic environment-specific resource-group names and deployment scopes, with secret-free outputs. Application hosting and capacity isolation are out of scope for TASK-5 and remain assigned to TASK-8 and downstream application tasks.
- [x] #3 Dev/test foundation-only deployments and repeat deployments demonstrate reproducibility; bootstrap exceptions and protected-resource cleanup are documented. No workload capacity is provisioned in TASK-5.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Record the user's approved foundation-only amendment in issue #12 and pin the updated revision and approval evidence in TASK-5. 2. Map the revised acceptance criteria to merged foundation work in TASK-45, TASK-46 and TASK-47, leaving workload capacity to TASK-8. 3. Run current pinned Bicep and focused regression checks; confirm cleanup/bootstrap guidance. 4. Record evidence and finalize TASK-5 through the CLI on this branch. 5. Publish one PR, monitor final-head checks, and mark Done only after they pass.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added subscription-scoped foundation module and per-environment parameters, pinned Bicep 0.34.44 local compiler checks, and documented deployment and cleanup prerequisites.

Draft PR #8 depended on PR #7. The Bicep readiness preflight rejects unresolved owner and cost-center values and verifies the selected environment. Region parameters remained unresolved until explicit approval.

Earlier verification passed pinned Bicep compilation, lint, environment selection and invalid-environment checks. Deployment-readiness correctly failed closed while location and owner inputs were unresolved.

Dev deployment evidence (2026-11-01): deployed rg-pb-dev-foundation in Sweden Central with dev/service/cost-center tags; the owner contact is intentionally not retained in this public task record. The initial what-if showed resource-group creation, a later what-if showed no changes, and the repeated deployment succeeded. A $20/month USD MCA budget filtered to PHONEBUDDY-DEV was created with 50/80/100 actual and 100 forecast alerts; it was later superseded and removed as part of the approved West Europe dev/test scope. Budgets alert but do not cap spend. No application capacity was provisioned.

Approved scope amendment (2026-11-01): the user narrowed TASK-5 to the Bicep foundation only and left application capacity in TASK-8. Issue #12 was updated at 2026-11-01T13:37:06Z (body SHA-256 c16d37b5fb3aa9da273743c6ec8e8f968e6c655f2953e19f412fd15af20b05f2). Acceptance #2 covers deterministic foundation scope and secret-free outputs; it makes no claim about workload authorization, network/data isolation or capacity isolation. #3 covers dev/test resource-group-only deployment/repeatability and documented cleanup boundaries.

Completion evidence (2026-11-01): pinned Bicep 0.34.44 baseline passed; dev and test deployment-readiness passed; prod readiness failed closed on unresolved location. All 11 focused preflight unittests and git diff --check passed. PR #50 verified the initial dev foundation deployment/repeat; PR #52 verified deterministic environment-specific foundation boundaries; PR #53 verified West Europe dev/test deployments and no-change repeated what-ifs. PRs #50, #52 and #53 are merged. Bootstrap exceptions, protected cleanup limits and the absence of application capacity are documented. No credentials or personal identifiers are retained here.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Completed TASK-5 as an Azure foundation-only task under the user-approved amendment to issue #12. The Bicep baseline, deterministic environment-specific resource-group/deployment scopes, and secret-free output boundary are verified; application hosting and workload capacity isolation remain in TASK-8. Dev/test foundation deployments and repeat runs are documented, along with bootstrap and protected-resource cleanup limits. Pinned Bicep baseline and dev/test readiness checks passed, production failed closed on unresolved location as expected, all 11 focused unit tests passed, and git diff --check passed. Supporting deployment and isolation PRs #50, #52, and #53 are merged. No application capacity or production resources were deployed.
<!-- SECTION:FINAL_SUMMARY:END -->
