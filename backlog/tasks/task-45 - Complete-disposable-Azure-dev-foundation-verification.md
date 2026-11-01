---
id: TASK-45
title: Complete disposable Azure dev foundation verification
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-01T10:30:00Z'
updated_date: '2026-11-01T10:37:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/12
  - docs/azure-delivery-policy.md
  - infra/README.md
  - infra/environments/dev.bicepparam
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - scripts/check_bicep.py
modified_files:
  - infra/environments/dev.bicepparam
  - >-
    backlog/tasks/task-5 -
    Create-modular-Bicep-baseline-and-environment-parameters.md
priority: high
type: task
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Completes the remaining dev foundation deployment evidence from migrated issue #12. The template creates only a tagged resource group; no application capacity is in scope.

Approved issue revision: https://github.com/vkaam/phonebuddy/issues/12 updated 2026-11-01T09:24:47Z; body SHA-256 294ffca40d3b855da99756164687afc214bf018536d424f3fd98f1647ddc2c7c.
Approval evidence: direct user instruction in this Codex conversation on 2026-11-01 to continue the infra setup ticket, then user-provided Azure subscription and explicit budget, owner, cost-center, and region preferences.
Branch: agent/gh-12-1-configure-dev-azure.
Scope: infra/environments/dev.bicepparam; Azure subscription 3787e2b4-802f-4b28-8793-1a32cc410b45, its dev foundation resource group, and an MCA billing-account budget filtered to the PHONEBUDDY-DEV cost-center tag; this task record and the legacy TASK-5 record through Backlog CLI only.
Verify: BICEP=<pinned 0.34.44 executable> python3 -B scripts/check_bicep.py --deployment-ready dev; az deployment sub what-if followed by az deployment sub create twice using infra/main.bicep and infra/environments/dev.bicepparam; inspect resource-group tags and retrieve the budget to confirm USD amount, monthly period, filter, expiry, and alerts.
No credentials or secrets may be committed. Budget alerts are not a spending cap; tagged resources in this cost center must carry costCenter=PHONEBUDDY-DEV.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dev foundation parameters use Sweden Central, the signed-in Azure principal as owner, and the new PHONEBUDDY-DEV cost-center tag without storing secrets.
- [x] #2 A $20 monthly USD budget at the MCA billing-account scope is filtered to the PHONEBUDDY-DEV cost-center tag, with 50%, 80%, and 100% actual and 100% forecast alerts sent to the Azure owner.
- [x] #3 The dev foundation deploys successfully twice to the user-designated subscription; the second deployment converges without unexpected changes and the resource group has the expected tags.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Confirm issue snapshot, Azure principal, billing-account USD scope, allowed regions, and existing resources/budgets.
2. Set dev Bicep parameters to Sweden Central, the signed-in Azure UPN, and the PHONEBUDDY-DEV cost-center tag.
3. Run the pinned local Bicep checks and deployment-readiness preflight; review subscription what-if.
4. Deploy the dev foundation twice and verify resource-group tags and idempotent result.
5. Create and verify a 20 USD monthly MCA billing-account budget filtered by the PHONEBUDDY-DEV tag, with policy thresholds emailed to the Azure owner.
6. Record deployment and budget evidence on this task and append evidence to the legacy TASK-5 record through the CLI.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Bicep 0.34.44 baseline and deployment-readiness dev checks passed. The first subscription what-if showed exactly one change: create rg-pb-dev-foundation in Sweden Central with the expected dev/service/owner/costCenter tags. Deployment phonebuddy-dev-foundation-20261101 succeeded. The next what-if reported one no-change result; repeat deployment phonebuddy-dev-foundation-repeat-20261101 also succeeded. Resource-group tags verified. Created and read back phonebuddy-dev-monthly-20usd at MCA billing-account scope: amount 20.0 USD, Monthly, 2026-11-01 through 2027-11-01; filter costCenter=PHONEBUDDY-DEV; actual alerts at 50/80/100 and forecast at 100 to the signed-in Azure owner. Budget is alert-only. The dev baseline creates no billable application capacity; Sweden Central has no cost advantage over West Europe for this resource-group-only deployment.
<!-- SECTION:NOTES:END -->
