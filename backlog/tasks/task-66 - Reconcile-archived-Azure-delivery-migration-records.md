---
id: TASK-66
title: Reconcile archived Azure delivery migration records
status: Done
assignee:
  - '@codex'
created_date: '2026-11-02T16:38:00Z'
updated_date: '2026-11-02T17:01:00Z'
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
    backlog/tasks/task-16 -
    Add-Entra-sign-in-and-organization-scoped-authorization.md
  - >-
    backlog/tasks/task-18 -
    Prove-browser-SIP-calling-and-per-leg-audio-capture.md
  - >-
    backlog/tasks/task-23 -
    Stream-and-persist-Dutch-and-English-call-transcription.md
  - >-
    backlog/tasks/task-25 -
    Generate-evidence-linked-call-summaries-and-action-items.md
  - backlog/tasks/task-30 - Validate-the-complete-web-softphone-pilot.md
  - >-
    backlog/tasks/task-42 -
    Qualify-a-narrowly-approved-development-lane-without-per-PR-human-approval.md
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
Need: GitHub now owns the intent for Azure delivery. The legacy Backlog tasks #5–#14 were replaced with issue-linked execution records, but PR review found active downstream tasks still referencing archived task IDs. This left parts of the product and pilot dependency graph blocked even after replacement work completed.

Primary issue: https://github.com/vkaam/phonebuddy/issues/37
Approved issue revision: 2026-11-01T09:52:42Z; body SHA-256 e89fb516577a1895faad3736db993a071936a91605451ac43357ba337c217deb.
Approval evidence: The human user authorized the initial migration repair with “fix this” and approved this follow-up scope by instructing “fix the pr comment” in Codex on 2026-11-02. This authorizes remapping only the identified native dependencies; it does not authorize Azure deployment, merging, or closing issues.
Branch: agent/gh-37-2-azure-task-reconciliation
Scope: backlog/archive/tasks/task-5 - Create-modular-Bicep-baseline-and-environment-parameters.md; backlog/archive/tasks/task-6 - Bootstrap-federated-GitHub-deployment-identities.md; backlog/archive/tasks/task-7 - Validate-Bicep-changes-in-pull-request-CI.md; backlog/archive/tasks/task-8 - Provision-Azure-pilot-application-hosting.md; backlog/archive/tasks/task-9 - Provision-data-messaging-Speech-and-Foundry-foundations.md; backlog/archive/tasks/task-10 - Add-deployment-health-gates-and-observability.md; backlog/archive/tasks/task-11 - Deploy-default-branch-changes-automatically-through-CI-CD.md; backlog/archive/tasks/task-12 - Implement-application-rollback-and-stateful-recovery-safeguards.md; backlog/archive/tasks/task-13 - Verify-automatic-deployment-and-rollback-end-to-end.md; backlog/archive/tasks/task-14 - Provision-SIP-gateway-and-TURN-infrastructure-with-Bicep.md; backlog/tasks/task-16 - Add-Entra-sign-in-and-organization-scoped-authorization.md; backlog/tasks/task-18 - Prove-browser-SIP-calling-and-per-leg-audio-capture.md; backlog/tasks/task-23 - Stream-and-persist-Dutch-and-English-call-transcription.md; backlog/tasks/task-25 - Generate-evidence-linked-call-summaries-and-action-items.md; backlog/tasks/task-30 - Validate-the-complete-web-softphone-pilot.md; backlog/tasks/task-42 - Qualify-a-narrowly-approved-development-lane-without-per-PR-human-approval.md; backlog/tasks/task-57 - Issue-13-Bootstrap-federated-GitHub-deployment-identities.md; backlog/tasks/task-58 - Issue-14-Validate-Bicep-changes-in-pull-request-CI.md; backlog/tasks/task-59 - Issue-15-Provision-Azure-pilot-application-hosting.md; backlog/tasks/task-60 - Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md; backlog/tasks/task-61 - Issue-17-Add-deployment-health-gates-and-observability.md; backlog/tasks/task-62 - Issue-18-Deploy-default-branch-changes-automatically-through-CI-CD.md; backlog/tasks/task-63 - Issue-19-Implement-application-rollback-and-stateful-recovery-safeguards.md; backlog/tasks/task-64 - Issue-20-Verify-automatic-deployment-and-rollback-end-to-end.md; backlog/tasks/task-65 - Issue-21-Provision-SIP-gateway-and-TURN-infrastructure-with-Bicep.md; backlog/tasks/task-66 - Reconcile-archived-Azure-delivery-migration-records.md
Verify: From repository root run git diff --check; backlog task view TASK-16 TASK-18 TASK-23 TASK-25 TASK-30 TASK-42 --plain; backlog task list --ready --status "To Do" --search "Issue" --plain. Verify direct dependencies now point TASK-9→TASK-60, TASK-14→TASK-65 and TASK-13→TASK-64 for the identified dependents, all unrelated direct dependencies remain, only TASK-57 and TASK-58 are ready within the Azure issue-task filter (other unrelated tasks may be ready), legacy TASK-5–TASK-14 remain archived, TASK-5 remains Done, and GitHub issues are unchanged.
Spec: Preserve each active task's acceptance and all unrelated dependencies. Replace only direct dependencies on the archived Azure tasks with their current native replacements.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Backlog task creation and archival CLI operations succeed.
- [x] #2 The first-app Azure deployment path is represented by TASK-57 → TASK-59 → TASK-61 → TASK-62, with TASK-58 also required by TASK-62.
- [x] #3 Legacy imported tasks TASK-5–TASK-14 are archived with status/history preserved; TASK-5 remains Done and other unfinished records do not satisfy dependencies merely by archival.
- [x] #4 Verification confirms only TASK-57 and TASK-58 are ready within the Azure issue-task filter; unrelated ready tasks may exist, and no GitHub issue or Azure resource was changed.
- [x] #5 Active TASK-16, TASK-18, TASK-23, TASK-25, TASK-30 and TASK-42 no longer depend on archived Azure tasks TASK-9, TASK-13 or TASK-14; their replacement dependencies and all unrelated direct dependencies are preserved.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Pin current approved issue snapshots and the existing Azure task graph.
2. Create and archive the issue-linked Azure execution task mapping while preserving completed TASK-5 evidence.
3. Remap the identified active dependents from archived TASK-9, TASK-13 and TASK-14 to replacements TASK-60, TASK-64 and TASK-65, preserving every other dependency.
4. Verify exact direct dependencies, ready-task frontier, archived records and issue immutability.
5. Publish one reviewable PR, monitor final-head checks, and resolve the addressed review thread.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created TASK-57 through TASK-65 from open issues #13–#21, each with its approved body timestamp and SHA-256, direct authorization evidence, unique future branch, explicit path scope, verification gates, acceptance criteria and dependencies. Corrected TASK-64's issue #20 body digest against the live issue. Archived imported TASK-5 through TASK-14 after creating their replacement tasks; TASK-5's completed status remains satisfied. No GitHub issue, Azure resource, application source, or deployment setting was changed.

Published draft PR https://github.com/vkaam/phonebuddy/pull/70 at head 3f7342dc663f8c15fa1ad91baca8e0bd2311476f; hosted checks are pending. PR keeps all issue links neutral and does not close any parent issue.

Final-head verification: PR #70 head 918d34544b37f05420d4b5f6374f5ce4f2044e60 passed Quality (run 41483638965) and Risk report (advisory; run 41483634849). Local git diff --check passed. TASK-57 and TASK-58 are the only ready tasks; TASK-62 depends on TASK-57, TASK-58, TASK-59 and TASK-61. No GitHub issue or Azure resource was changed. Maintainer review and merge remain outstanding; no Azure deployment was performed.

PR review finding on 2026-11-02 identified stale active dependencies: TASK-16, TASK-18, TASK-23 and TASK-25 referenced archived TASK-9; TASK-18 also referenced archived TASK-14; TASK-30 and TASK-42 referenced archived TASK-13. The user directly authorized this bounded scope amendment with “fix the pr comment”. Remap these direct edges to TASK-60, TASK-65 and TASK-64 respectively; retain all unrelated direct dependencies.

Applied the approved PR review fix through the Backlog CLI: TASK-16 TASK-9→TASK-60; TASK-18 TASK-9→TASK-60 and TASK-14→TASK-65; TASK-23 and TASK-25 TASK-9→TASK-60; TASK-30 and TASK-42 TASK-13→TASK-64. Preserved every other direct dependency. JSON task views verify each replacement edge; the Azure issue-task ready filter remains TASK-57 and TASK-58 only. The review thread remains unresolved pending final-head checks.

Final PR-head verification: commit 423a63f65bc3f8bb9f4c5cb73158066591423981 passed Quality (run 41486886178) and Risk report (advisory; runs 41486915829 and 41486877851). The review finding is fully addressed by the six dependency remaps recorded above. GitHub PR #70 remains open for maintainer review and merge; no Azure deployment was performed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Reconciled the Azure migration dependency graph through CLI-managed task updates and archived superseded legacy tasks with history preserved. Fixed review feedback by remapping active TASK-16/18/23/25/30/42 dependencies to TASK-60/64/65 while preserving unrelated dependency edges. Verified the Azure issue-task ready frontier is TASK-57 and TASK-58, TASK-5 remains Done and archived, and git diff --check passed. PR #70 head 423a63f passed Quality and both advisory risk checks. No GitHub issue or Azure resource was changed and no deployment was performed; maintainer review and merge remain outstanding.
<!-- SECTION:FINAL_SUMMARY:END -->
