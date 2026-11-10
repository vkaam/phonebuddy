---
id: TASK-79
title: Issue 17 - Verify France Central health gate and alerts
status: Done
assignee:
  - '@codex'
created_date: '2026-11-09T19:19:00Z'
updated_date: '2026-11-10T16:19:00Z'
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
  - scripts/bootstrap_github_oidc.py
  - .github/workflows/azure-oidc-smoke.yml
  - tests/test_azure_oidc_bootstrap.py
  - tests/test_oidc_smoke_workflow.py
  - infra/github-oidc.md
  - >-
    backlog/tasks/task-61 -
    Issue-17-Add-deployment-health-gates-and-observability.md
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
Scope: infra/hosting.bicep; infra/README.md; infra/release-test/server.py; .github/workflows/azure-health-gate.yml; .github/workflows/azure-hosting-what-if.yml; .github/workflows/azure-oidc-smoke.yml; scripts/bootstrap_github_oidc.py; tests/test_azure_oidc_bootstrap.py; infra/github-oidc.md; scripts/health_gate.py; scripts/check_bicep.py; tests/test_health_gate.py; tests/test_bicep_ci_boundary.py; tests/test_oidc_smoke_workflow.py; tests/test_release_test.py; docs/azure-delivery-policy.md; docs/quality-and-delivery.md; backlog/tasks/task-61 - Issue-17-Add-deployment-health-gates-and-observability.md; backlog/tasks/task-79 - Issue-17-Verify-France-Central-health-gate-and-alerts.md.
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint on changed workflows. In authorized France Central dev, run bounded healthy observation, injected unhealthy and missing-telemetry cases, and Azure Monitor alert checks. Record Azure deployment, telemetry, alert, and cleanup evidence on the current source.
Spec: Preserve issue #17 approved acceptance and TASK-61 code scope. This is the second, verification-focused PR required by the one-task-one-PR rule because PR #82 was merged while live evidence remained deferred. Reconcile TASK-61 through the Backlog CLI after all original criteria are proven.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 France Central dev hosting, telemetry and alert resources deploy from reviewed Bicep with no secret or call-content logging.
- [x] #2 Healthy versioned readiness and 10-minute observation pass after warm-up with sufficient workspace telemetry.
- [x] #3 Injected unhealthy responses and missing telemetry fail closed and produce alert/failure evidence; dependency outages are distinguishable.
- [x] #4 TASK-61 and issue #17 are reconciled to the merged code and live verification evidence without weakening the original issue acceptance.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the merged TASK-61 health gate, hosting Bicep, current France Central dev resources and identity scopes; determine the smallest approved live target. 2. Align the pilot hosting and read-only health workflow with the France Central dev group while retaining explicit region and source gates. 3. Run pinned Bicep, workflow and repository tests; preview exact Azure changes before deploying the synthetic release-test app and telemetry. 4. Verify healthy observation, injected unhealthy and missing-telemetry failures, and Azure Monitor alert evidence; clean synthetic changes and record remaining limits. 5. Obtain independent review, update PR #90 and TASK-61/79 evidence, rerun final-head checks, merge when gates pass, and inspect main CI.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Triage amendment 2026-11-09: France Central provider metadata omits Microsoft.Web/staticSites while it supports the Container Apps, ACR, Key Vault, workspace and Insights services needed for this health pilot. Add infra/README.md and the existing manual OIDC/what-if workflows plus their boundary tests to the explicit file scope so the target can be aligned without a cross-region fallback; issue #17 acceptance and required checks remain unchanged. The owner was asked separately for action-time authorization before moving the dev deployment identity role.

2026-11-09 France Central preflight: the new subscription dev foundation group contains TASK-60 data resources but no pilot hosting app; its Belgium dev group is empty. Azure provider metadata lists France Central for Container Apps managed environments, ACR, Key Vault, Log Analytics and Application Insights, but not Static Web Apps. The hosting template now keeps Static Web Apps default-on for supported regions and requires an explicit false opt-out for this France health pilot. Read-only ARM What-If for dev bootstrap with deployWorkload=false and deployStaticSite=false succeeded: 8 Create, 9 Ignore for exact existing TASK-60 data resources, zero Modify/Delete. The checker now admits only narrowly named France data-foundation ignores and rejects unexpected ignores; the live What-If JSON passed it. Pinned Bicep baseline, actionlint on affected workflows and 17 focused tests passed (the HTTP tests needed loopback socket permission). No hosting resource has been deployed yet. The dev OIDC app currently has Contributor only on the Belgium dev group; owner decision on moving that scope is pending.

Live France Central dev bootstrap deployment phonebuddy-task79-health-bootstrap-20261109 Succeeded from the reviewed template with deployWorkload=false and deployStaticSite=false. Readback confirms the Container Apps environment, 30-day Log Analytics workspace, Application Insights, Basic ACR and RBAC Key Vault all have location francecentral; the registry pull identity has AcrPull on that registry. Existing TASK-60 data resources were not modified or deleted. PR #90 head 3b0cea9 passed hosted Quality run 42687365738 and advisory Risk run 42687405995. The full local scripts/check.py gate passed (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-u08mg3ij/report.json). The image build is blocked because the local OrbStack Docker API stopped responding; owner was asked before a restart that could affect other local containers. No app or alert drill has run yet.

Image build fallback check: Azure ACR Tasks in the new subscription returned TasksOperationsNotAllowed for pbdev3dg66adbcqbhw, matching the older subscription policy. This did not create an image. OrbStack Docker _ping remained unresponsive for more than four minutes; the stalled build was stopped without creating or pushing an image. Owner approval for an OrbStack restart remains pending.

Owner approval 2026-11-09: move the dev GitHub OIDC app Contributor role from Belgium Central to only its matching France Central dev group; the app federation remained the single repository-ID-qualified dev environment trust. Live Azure readback after the move showed exactly one Contributor assignment, on rg-pb-dev-francecentral-foundation, and none on Belgium. Triage scope amendment adds the bootstrap script, its boundary test and OIDC runbook so future use matches this approved role move. The owner also authorized restarting OrbStack; graceful stop/start restored Docker, enabling an amd64 release-test image build and push to the new France Central ACR. Digest b4dcf33532ed92671592272e39bfc1647553d702d8f7fffcfaf59f9f3c8f39c5 includes a linux/amd64 manifest.

2026-11-10 France Central dev workload deployment phonebuddy-task79-health-app-20261110 Succeeded from reviewed Bicep with deployWorkload=true and deployStaticSite=false. Preview showed five Creates (Container App, app diagnostics, three scheduled-query alerts), no Delete, with ARM representation noise on existing hosting resources and exact TASK-60 data-resource ignores. The app is ready in France Central at version 3b0cea9 from ACR digest b4dcf33532ed92671592272e39bfc1647553d702d8f7fffcfaf59f9f3c8f39c5. /ready and / returned HTTP 200 with ready=true and matching version. Alert config readback shows enabled five-minute missing-telemetry rule scoped to the dev Log Analytics workspace. Full local scripts/check.py passed on the current tree; healthy 10-minute observation is running.

First live 10-minute observation (2026-11-10 05:37 UTC) failed closed: 100 HTTP samples, three dependency_outage timeouts, 3% error rate, one latency window breach, and zero matching workspace events in the final 15-minute query. Azure system logs show the minReplicas=0 Container App scaled to zero at 05:24 UTC during a host pause, and Azure Monitor raised a missing-telemetry alert at 05:37 UTC. The app restarted and workspace console ingestion later resumed through 05:39 UTC (ingested 05:44 UTC). A second 10-minute observation is running with host idle sleep inhibited; the failed first run is retained as negative evidence, not counted as healthy acceptance.

Second 10-minute observation ended 2026-11-10 06:44 UTC and also failed closed: 100 samples, ten dependency-outage timeouts, 10% error rate and zero recent workspace events. The host remained interrupted for hours; console event readback later showed last event at 05:59 UTC, ingested at 06:04 UTC, before the gate ended. Current macOS system resolver times out for Azure/GitHub despite direct DNS queries succeeding; a process-local, untracked DNS fallback in /private/tmp is being used for read-only Azure inspection. Azure alert history shows missing-telemetry alert instances Fired at 05:07, 05:37 and 06:07 UTC (first two Resolved), and an unhealthy-response alert Fired at 05:45 and Resolved at 06:01 UTC after an observed 404. A deliberate unknown-route request returned 404 at 14:21 UTC; workspace and alert confirmation are pending.

Controlled unhealthy drill 2026-11-10: one unknown-route request at 14:21 UTC returned 404. Log Analytics ingested 27 recent synthetic health events including one non-200 by 14:29 UTC. Azure AlertsManagement reported a new Phonebuddy dev unhealthy health response instance Fired at 14:30:12 UTC. Recovery traffic then returned 36/36 HTTP 200. Synthetic requests were stopped after 14:30 UTC to exercise the existing minReplicas=0 and missing-telemetry rule; the earlier missing-telemetry instance remains Fired while traffic is withheld.

Final healthy France Central dev evidence: hosted app release 3b0cea9 at the reviewed ACR digest returned 100/100 successful /ready and / responses after a 60-second prewarm across ten one-minute samples and 600 seconds of observation. The saved 2026-11-10 14:48:38 UTC gate report passed with error_rate=0, p95_latency_ms=232.339, no failure reasons, and Log Analytics telemetry_event_count=117 with unhealthy_event_count=0. The earlier failed 100-sample gate reported dependency_outage separately from unhealthy_response, and the bounded missing-version workspace probe returned missing_telemetry. The deliberate 14:21 UTC 404 was ingested and a new unhealthy-response alert Fired at 14:30:12, Resolved at 14:46:10 UTC. The existing missing-telemetry alert Resolved at 14:43:23 during resumed health traffic; after synthetic traffic stopped and the app scaled to zero, a new missing-telemetry instance Fired at 15:07:23 UTC. Thus both alert conditions fired in the live workspace without logging request data. Independent final acceptance review requested; final-head checks and PR merge remain.

Finalization 2026-11-10: Independent agent validated TASK-79 AC1-3 and TASK-61 AC1-4 against deployment, gate and alert artifacts and found no blocking finding. TASK-61 proposed Done record and issue #17 progress comments now reconcile merged code PR #82 with the France Central live evidence; issue stays open until PR #90 merges. Full final local scripts/check.py passed (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-zjf4wxd7/report.json), pinned Bicep baseline passed, changed-workflow actionlint passed, and git diff --check passed. The trusted main-only health workflow release annotation is a post-merge operational verification, not a pre-merge code grant.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Provisioned France Central dev hosting and health alerts, aligned the dev OIDC role and workflows, and verified a clean 10-minute versioned gate with 117 workspace events. Deliberate unhealthy and missing-telemetry conditions fired Azure Monitor alerts. Independent review and local checks passed; PR #90 awaits final-head hosted checks and merge, followed by the trusted workflow and main CI observation.
<!-- SECTION:FINAL_SUMMARY:END -->
