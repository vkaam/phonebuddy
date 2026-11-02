---
id: TASK-66
title: Reconcile archived Azure delivery migration records
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:38:00Z'
updated_date: '2026-11-02T16:39:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/37
  - https://github.com/vkaam/phonebuddy/issues/13
  - https://github.com/vkaam/phonebuddy/issues/14
  - https://github.com/vkaam/phonebuddy/issues/15
  - https://github.com/vkaam/phonebuddy/issues/16
  - https://github.com/vkaam/phonebuddy/issues/17
  - https://github.com/vkaam/phonebuddy/issues/18
  - https://github.com/vkaam/phonebuddy/issues/19
  - https://github.com/vkaam/phonebuddy/issues/20
  - https://github.com/vkaam/phonebuddy/issues/21
modified_files:
  - >-
    backlog/archive/tasks/task-5 -
    Create-modular-Bicep-baseline-and-environment-parameters.md
  - >-
    backlog/archive/tasks/task-6 -
    Bootstrap-federated-GitHub-deployment-identities.md
  - backlog/archive/tasks/task-7 - Validate-Bicep-changes-in-pull-request-CI.md
  - backlog/archive/tasks/task-8 - Provision-Azure-pilot-application-hosting.md
  - >-
    backlog/archive/tasks/task-9 -
    Provision-data-messaging-Speech-and-Foundry-foundations.md
  - >-
    backlog/archive/tasks/task-10 -
    Add-deployment-health-gates-and-observability.md
  - >-
    backlog/archive/tasks/task-11 -
    Deploy-default-branch-changes-automatically-through-CI-CD.md
  - >-
    backlog/archive/tasks/task-12 -
    Implement-application-rollback-and-stateful-recovery-safeguards.md
  - >-
    backlog/archive/tasks/task-13 -
    Verify-automatic-deployment-and-rollback-end-to-end.md
  - >-
    backlog/archive/tasks/task-14 -
    Provision-SIP-gateway-and-TURN-infrastructure-with-Bicep.md
  - >-
    backlog/tasks/task-57 -
    Issue-13-Bootstrap-federated-GitHub-deployment-identities.md
  - >-
    backlog/tasks/task-58 -
    Issue-14-Validate-Bicep-changes-in-pull-request-CI.md
  - >-
    backlog/tasks/task-59 -
    Issue-15-Provision-Azure-pilot-application-hosting.md
  - >-
    backlog/tasks/task-60 -
    Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md
  - >-
    backlog/tasks/task-61 -
    Issue-17-Add-deployment-health-gates-and-observability.md
  - >-
    backlog/tasks/task-62 -
    Issue-18-Deploy-default-branch-changes-automatically-through-CI-CD.md
  - >-
    backlog/tasks/task-63 -
    Issue-19-Implement-application-rollback-and-stateful-recovery-safeguards.md
  - >-
    backlog/tasks/task-64 -
    Issue-20-Verify-automatic-deployment-and-rollback-end-to-end.md
  - >-
    backlog/tasks/task-65 -
    Issue-21-Provision-SIP-gateway-and-TURN-infrastructure-with-Bicep.md
  - >-
    backlog/tasks/task-66 -
    Reconcile-archived-Azure-delivery-migration-records.md
priority: high
type: task
ordinal: 63000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: GitHub now owns the intent for Azure delivery, but legacy Backlog tasks #5–#14 were still active on the default branch while a local migration archived them without creating current execution records. That made the first-app release path ambiguous and left no native task graph for the open issues.

Primary issue: https://github.com/vkaam/phonebuddy/issues/37
Approved issue revision: 2026-11-01T09:52:42Z; body SHA-256 e89fb516577a1895faad3736db993a071936a91605451ac43357ba337c217deb.
Approval evidence: The human user directly instructed “fix this” in Codex on 2026-11-02 after identifying the archived unfinished Azure delivery tasks. This authorizes migration reconciliation and task creation for the already-open Azure issues; it does not authorize Azure deployment, merging, or closing any issue.
Branch: agent/gh-37-2-azure-task-reconciliation
Scope: backlog/archive/tasks/task-5 - Create-modular-Bicep-baseline-and-environment-parameters.md; backlog/archive/tasks/task-6 - Bootstrap-federated-GitHub-deployment-identities.md; backlog/archive/tasks/task-7 - Validate-Bicep-changes-in-pull-request-CI.md; backlog/archive/tasks/task-8 - Provision-Azure-pilot-application-hosting.md; backlog/archive/tasks/task-9 - Provision-data-messaging-Speech-and-Foundry-foundations.md; backlog/archive/tasks/task-10 - Add-deployment-health-gates-and-observability.md; backlog/archive/tasks/task-11 - Deploy-default-branch-changes-automatically-through-CI-CD.md; backlog/archive/tasks/task-12 - Implement-application-rollback-and-stateful-recovery-safeguards.md; backlog/archive/tasks/task-13 - Verify-automatic-deployment-and-rollback-end-to-end.md; backlog/archive/tasks/task-14 - Provision-SIP-gateway-and-TURN-infrastructure-with-Bicep.md; backlog/tasks/task-57 - Issue-13-Bootstrap-federated-GitHub-deployment-identities.md; backlog/tasks/task-58 - Issue-14-Validate-Bicep-changes-in-pull-request-CI.md; backlog/tasks/task-59 - Issue-15-Provision-Azure-pilot-application-hosting.md; backlog/tasks/task-60 - Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md; backlog/tasks/task-61 - Issue-17-Add-deployment-health-gates-and-observability.md; backlog/tasks/task-62 - Issue-18-Deploy-default-branch-changes-automatically-through-CI-CD.md; backlog/tasks/task-63 - Issue-19-Implement-application-rollback-and-stateful-recovery-safeguards.md; backlog/tasks/task-64 - Issue-20-Verify-automatic-deployment-and-rollback-end-to-end.md; backlog/tasks/task-65 - Issue-21-Provision-SIP-gateway-and-TURN-infrastructure-with-Bicep.md; backlog/tasks/task-66 - Reconcile-archived-Azure-delivery-migration-records.md.
Verify: From repository root run git diff --check; backlog task view TASK-57 through TASK-65 --plain; backlog task list --ready --status "To Do" --search "Issue" --plain. Confirm only TASK-57/#13 and TASK-58/#14 are ready, later tasks carry the expected native dependency chain, legacy TASK-5–TASK-14 are archived, TASK-5 remains Done, and GitHub issues are unchanged.
Spec: Reconcile only the Azure delivery migration. Keep the completed foundation evidence, create one scoped native task for each approved open issue #13–#21 with revision, approval, branch, scope, verification and acceptance, then archive superseded legacy tasks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backlog task creation and archival CLI operations succeed.
- [ ] #2 The first-app Azure deployment path is represented by TASK-57 → TASK-59 → TASK-61 → TASK-62, with TASK-58 also required by TASK-62.
- [ ] #3 Legacy imported tasks TASK-5–TASK-14 are archived with status/history preserved; TASK-5 remains Done and other unfinished records do not satisfy dependencies merely by archival.
- [ ] #4 Verification confirms only TASK-57 and TASK-58 are ready and no GitHub issue or Azure resource was changed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Pin current approved revisions and dependencies for open Azure issues #13–#21, preserving completed TASK-5 evidence.
2. Create fresh CLI-managed execution tasks with issue, approval snapshot, branch, explicit scope, verification and native acceptance.
3. Archive the superseded imported Azure tasks #5–#14 without changing issue bodies or statuses.
4. Validate the ready-task frontier and dependency graph; publish one reviewable PR and monitor its final-head checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created TASK-57 through TASK-65 from open issues #13–#21, each with its approved body timestamp and SHA-256, direct authorization evidence, unique future branch, explicit path scope, verification gates, acceptance criteria and dependencies. Corrected TASK-64's issue #20 body digest against the live issue. Archived imported TASK-5 through TASK-14 after creating their replacement tasks; TASK-5's completed status remains satisfied. No GitHub issue, Azure resource, application source, or deployment setting was changed.

Published draft PR https://github.com/vkaam/phonebuddy/pull/70 at head 3f7342dc663f8c15fa1ad91baca8e0bd2311476f; hosted checks are pending. PR keeps all issue links neutral and does not close any parent issue.
<!-- SECTION:NOTES:END -->
