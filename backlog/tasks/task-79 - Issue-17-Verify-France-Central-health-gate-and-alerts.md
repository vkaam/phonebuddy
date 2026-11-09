---
id: TASK-79
title: Issue 17 - Verify France Central health gate and alerts
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-09T19:19:00Z'
updated_date: '2026-11-09T19:50:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/17
  - https://github.com/vkaam/phonebuddy/pull/82
  - https://github.com/vkaam/phonebuddy/pull/90
modified_files:
  - >-
    backlog/tasks/task-79 -
    Issue-17-Verify-France-Central-health-gate-and-alerts.md
  - infra/hosting.bicep
  - scripts/check_bicep.py
  - tests/test_bicep_ci_boundary.py
  - .github/workflows/azure-hosting-what-if.yml
  - .github/workflows/azure-health-gate.yml
  - infra/README.md
  - docs/azure-delivery-policy.md
priority: high
type: task
ordinal: 72000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the live dev health-gate and alert evidence left open after TASK-61 code PR #82 merged. The owner had paused further Azure validation on 2026-11-04 and explicitly requested finishing TASK-61 on 2026-11-09. The current nonproduction workload target is France Central in the new subscription; no pilot hosting app exists in that resource group yet.
Primary issue: https://github.com/vkaam/phonebuddy/issues/17
Approved revision: 2026-11-01T09:24:54Z; body SHA-256 8d4a38d23215c8706bc19f086c585b9ebcafe76dfe747de51edbbbd35951d749.
Approval evidence: The owner directly asked in Codex on 2026-11-09, "can we finish task-61 then?" This authorizes the remaining scoped dev verification and supersedes the earlier pause. Issue acceptance remains unchanged.
Branch: agent/gh-17-3-live-health-verification
Scope: infra/hosting.bicep; infra/README.md; infra/release-test/server.py; .github/workflows/azure-health-gate.yml; .github/workflows/azure-hosting-what-if.yml; .github/workflows/azure-oidc-smoke.yml; scripts/health_gate.py; scripts/check_bicep.py; tests/test_health_gate.py; tests/test_bicep_ci_boundary.py; tests/test_oidc_smoke_workflow.py; tests/test_release_test.py; docs/azure-delivery-policy.md; docs/quality-and-delivery.md; backlog/tasks/task-61 - Issue-17-Add-deployment-health-gates-and-observability.md; backlog/tasks/task-79 - Issue-17-Verify-France-Central-health-gate-and-alerts.md.
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint on changed workflows. In authorized France Central dev, run bounded healthy observation, injected unhealthy and missing-telemetry cases, and Azure Monitor alert checks. Record Azure deployment, telemetry, alert, and cleanup evidence on the current source.
Spec: Preserve issue #17 approved acceptance and TASK-61 code scope. This is the second, verification-focused PR required by the one-task-one-PR rule because PR #82 was merged while live evidence remained deferred. Reconcile TASK-61 through the Backlog CLI after all original criteria are proven.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 France Central dev hosting, telemetry and alert resources deploy from reviewed Bicep with no secret or call-content logging.
- [ ] #2 Healthy versioned readiness and 10-minute observation pass after warm-up with sufficient workspace telemetry.
- [ ] #3 Injected unhealthy responses and missing telemetry fail closed and produce alert/failure evidence; dependency outages are distinguishable.
- [ ] #4 TASK-61 and issue #17 are reconciled to the merged code and live verification evidence without weakening the original issue acceptance.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the merged TASK-61 health gate, hosting Bicep, current France Central dev resources and identity scopes; determine the smallest approved live target. 2. Align the pilot hosting and read-only health workflow with the France Central dev group while retaining explicit region and source gates. 3. Run pinned Bicep, workflow and repository tests; preview exact Azure changes before deploying the synthetic release-test app and telemetry. 4. Verify healthy observation, injected unhealthy and missing-telemetry failures, and Azure Monitor alert evidence; clean synthetic changes and record remaining limits. 5. Obtain independent review, update PR #90 and TASK-61/79 evidence, rerun final-head checks, merge when gates pass, and inspect main CI.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Triage amendment 2026-11-09: France Central provider metadata omits Microsoft.Web/staticSites while it supports the Container Apps, ACR, Key Vault, workspace and Insights services needed for this health pilot. Add infra/README.md and the existing manual OIDC/what-if workflows plus their boundary tests to the explicit file scope so the target can be aligned without a cross-region fallback; issue #17 acceptance and required checks remain unchanged. The owner was asked separately for action-time authorization before moving the dev deployment identity role.

2026-11-09 France Central preflight: the new subscription dev foundation group contains TASK-60 data resources but no pilot hosting app; its Belgium dev group is empty. Azure provider metadata lists France Central for Container Apps managed environments, ACR, Key Vault, Log Analytics and Application Insights, but not Static Web Apps. The hosting template now keeps Static Web Apps default-on for supported regions and requires an explicit false opt-out for this France health pilot. Read-only ARM What-If for dev bootstrap with deployWorkload=false and deployStaticSite=false succeeded: 8 Create, 9 Ignore for exact existing TASK-60 data resources, zero Modify/Delete. The checker now admits only narrowly named France data-foundation ignores and rejects unexpected ignores; the live What-If JSON passed it. Pinned Bicep baseline, actionlint on affected workflows and 17 focused tests passed (the HTTP tests needed loopback socket permission). No hosting resource has been deployed yet. The dev OIDC app currently has Contributor only on the Belgium dev group; owner decision on moving that scope is pending.
<!-- SECTION:NOTES:END -->
