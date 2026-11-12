---
id: TASK-95
title: Provision missing pilot Static Web App
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-12T12:20:00Z'
updated_date: '2026-11-12T12:33:00Z'
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
modified_files:
  - backlog/tasks/task-95 - Provision-missing-pilot-Static-Web-App.md
priority: high
type: task
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Issue 15 requires a Static Web App, but the trusted dev release workflow omits it and no Static Web App exists in the designated subscription. Provision the missing pilot resource through reviewed source and trusted CI/CD; TASK-71 retains independent live hosting verification.

Issue: https://github.com/vkaam/phonebuddy/issues/15
Approved revision: 2026-11-01T09:24:49Z; body SHA-256 3990d679f2058124599c9c0e4d518017736c3f9c5e1b3e238c381d3c7ee7c60d.
Approval evidence: The owner instructed “Fix the web app in the subscription” in this Codex conversation on 2026-11-12 after the missing Static Web App was disclosed. Location and web-front-end residency approval remain outstanding; do not deploy until resolved.
Branch: agent/gh-15-4-static-web-app
Scope: .github/workflows/azure-deploy.yml; infra/hosting.bicep; scripts/check_bicep.py; tests/test_bicep_ci_boundary.py; tests/test_bicep_preflight.py; docs/azure-delivery-policy.md; backlog/tasks/task-95 - Provision-missing-pilot-Static-Web-App.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py; validate reviewed Bicep and workflow changes, required hosted checks and independent review, then use trusted default-branch CI/CD for authorized pilot deployment and retain resource, location and deployment evidence.
Spec: Preserve issue-level acceptance. Do not publish application content or alter other environments. The pilot region and residency decision must be approved before deployment; the owner’s TASK-71-only lease exception does not automatically apply to this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Reviewed Bicep and trusted dev CI/CD provision the Static Web App in the owner-approved pilot location without changing test or production.
- [ ] #2 Tests and documentation cover the resource location, deployment behavior and pilot access boundaries; required local and hosted checks pass.
- [ ] #3 Trusted deployment evidence identifies the merged source and confirms the provisioned Static Web App in the designated subscription.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Separate the Static Web App location from the France Central workload location and constrain the trusted dev release to the approved West Europe resource. 2. Extend template and workflow verification for the selected location and safe what-if behavior; document the residency and access boundary. 3. Run required checks and obtain independent review, then merge through the permitted path and observe the trusted deployment and resource readback.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-12: Owner approved extending the one-task lease exception to TASK-95, selected West Europe for the Static Web App, and requested deployment and PR merge. Live claim check passed against origin/main 6e58aa0bc47c8ff56a96834efef882e36e418c8f. PR #114 was temporarily closed to resolve the guard rejection of an open PR with To Do status and will be reopened after this claim is pushed.
<!-- SECTION:NOTES:END -->
