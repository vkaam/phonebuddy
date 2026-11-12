---
id: TASK-95
title: Provision missing pilot Static Web App
status: To Do
assignee: []
created_date: '2026-11-12T12:20:00Z'
updated_date: '2026-11-12T12:23:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/15
  - https://github.com/vkaam/phonebuddy/pull/114
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
