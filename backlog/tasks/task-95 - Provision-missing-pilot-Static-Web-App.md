---
id: TASK-95
title: Provision missing pilot Static Web App
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-12T12:20:00Z'
updated_date: '2026-11-12T14:16:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/15
  - https://github.com/vkaam/phonebuddy/pull/114
  - infra/hosting.bicep
  - .github/workflows/azure-deploy.yml
  - TASK-71
modified_files:
  - backlog/tasks/task-95 - Provision-missing-pilot-Static-Web-App.md
  - infra/hosting.bicep
  - .github/workflows/azure-deploy.yml
  - scripts/check_bicep.py
  - tests/test_bicep_ci_boundary.py
  - docs/azure-delivery-policy.md
priority: high
type: task
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Issue 15 requires a Static Web App, but the trusted dev release workflow omits it and no Static Web App exists in the designated subscription. Provision the missing pilot resource through reviewed source and trusted CI/CD; TASK-71 retains independent live hosting verification.

Issue: https://github.com/vkaam/phonebuddy/issues/15
Approved revision: 2026-11-01T09:24:49Z; body SHA-256 3990d679f2058124599c9c0e4d518017736c3f9c5e1b3e238c381d3c7ee7c60d.
Approval evidence: The owner instructed “Fix the web app in the subscription” in this Codex conversation on 2026-11-12 after the missing Static Web App was disclosed. On 2026-11-12 the owner selected West Europe, authorized deployment and requested PR merge, acknowledging globally distributed assets.
Branch: agent/gh-15-4-static-web-app
Scope: .github/workflows/azure-deploy.yml; infra/hosting.bicep; scripts/check_bicep.py; tests/test_bicep_ci_boundary.py; tests/test_bicep_preflight.py; docs/azure-delivery-policy.md; backlog/tasks/task-95 - Provision-missing-pilot-Static-Web-App.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py; validate reviewed Bicep and workflow changes, required hosted checks and independent review, and require a successful safe Azure what-if for the selected location. After merge, TASK-71 retains trusted CI/CD deployment and live resource, location and source evidence.
Spec: Preserve issue-level acceptance. Do not publish application content or alter other environments. The owner extended the lease exception to this task on 2026-11-12. On 2026-11-12 the owner approved the split: TASK-95 verifies deployment configuration before merge, while TASK-71 retains merged-source live deployment proof. Issue-level requirements remain unchanged. After West Europe was rejected, the owner directed the agent to find an available region, deploy there and record it on 2026-11-12. East US 2 passed the subscription what-if preview; the selected Static Web App resource location is East US 2.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Reviewed Bicep and trusted dev CI/CD configure the Static Web App in East US 2 without changing test or production.
- [ ] #2 Tests and documentation cover the resource location, deployment behavior and pilot access boundaries; required local and hosted checks pass.
- [ ] #3 Azure what-if for the approved pilot configuration succeeds within the expected resource group without unexpected or destructive changes.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Configure the Static Web App in East US 2 while leaving the existing workload in France Central. 2. Review the complete Azure what-if and verify template, tests, and documentation. 3. Run required checks and obtain independent review; merge through the permitted path and verify the resulting deployment under TASK-71.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-12: Owner approved extending the one-task lease exception to TASK-95, selected West Europe for the Static Web App, and requested deployment and PR merge. Live claim check passed against origin/main 6e58aa0bc47c8ff56a96834efef882e36e418c8f. PR #114 was temporarily closed to resolve the guard rejection of an open PR with To Do status and will be reopened after this claim is pushed.

2026-11-12: Read-only Azure what-if of the compiled working-tree template with deployStaticSite=true and staticSiteLocation=westeurope failed InvalidTemplateDeployment / RequestDisallowedByAzure: the selected region is currently not accepting new customers. No deployment occurred. Provider metadata lists West Europe as the only European Static Web Apps location in this subscription; no region fallback is authorized. The implementation must remain unmerged until availability is resolved. The requested pre-merge/live-proof split remains pending owner approval.

Implementation in progress: the template accepts a separate Static Web App location while defaulting to the original resource-group location; trusted dev preview and apply explicitly select West Europe. Bicep baseline and 44 focused CI-boundary/preflight tests pass. The required scripts/check.py baseline failed in this Windows environment; hosted checks and independent review remain pending.

Independent preliminary review of the uncommitted implementation found a blocking Azure availability failure: enabling the site now would fail the automatic dev release preview. Review also identified the pre-merge/live-proof circular gate and requested negative location coverage; negative location-binding tests were added and 45 focused tests plus Bicep baseline pass. This preliminary review is not final-head approval.

Triage amendment 2026-11-12: owner explicitly approved moving merged-source live deployment proof to existing TASK-71 after merge; TASK-95 verifies the configuration and safe preview before merge. Issue 15 acceptance is unchanged. Azure West Europe rejection remains a merge blocker.

Triage amendment 2026-11-12: after the West Europe rejection, the owner directed use of an available region and requested recording the selection. East US 2 what-if succeeded with one Static Web App create and six modifications to existing resources; detailed review of those changes remains required. Region is outside Europe and Static Web Apps assets are globally distributed. The actual deployment remains to be verified under TASK-71.

East US 2 source validation: Bicep baseline and 45 focused CI-boundary/preflight tests passed. scripts/check.py failed on Windows in bundle phonebuddy-quality-v44o_spo (required test suite incomplete and npm commands could not be launched). Azure preview proposed the site in eastus2, six existing-resource modifications, six no-change and ten ignored resources. Independent review of those modifications and final hosted checks are pending.

Independent preliminary comparison: all six existing-resource Modify delta objects match retained successful TASK-71 release attempt 3, except the expected revision suffix. This is historical evidence, not proof of future deployment safety; ProviderNoRbac does not verify the deployment identity can create the site. Exact-source deployment, resource readback and health remain required under TASK-71. An attempt to report the selected region and preview details on issue 15 was rejected by automatic approval review; task/issue reconciliation remains incomplete.

Owner explicitly approved GitHub disclosure; issue #15 was updated at https://github.com/vkaam/phonebuddy/issues/15#issuecomment-6826043733. East US 2 selection and preview evidence are now published on the task branch; final-head checks and independent review remain required.
<!-- SECTION:NOTES:END -->
