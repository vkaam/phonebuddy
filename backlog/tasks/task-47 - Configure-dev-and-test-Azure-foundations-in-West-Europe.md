---
id: TASK-47
title: Configure dev and test Azure foundations in West Europe
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T12:49:00Z'
updated_date: '2026-11-01T13:13:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-46
references:
  - https://github.com/vkaam/phonebuddy/issues/12
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - infra/README.md
modified_files:
  - >-
    backlog/tasks/task-47 -
    Configure-dev-and-test-Azure-foundations-in-West-Europe.md
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - infra/README.md
priority: high
type: task
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Complete the approved dev and test foundation configuration for issue #12. The existing dev foundation resource group rg-pb-dev-foundation is in Sweden Central and Azure does not permit changing its location; create a new West Europe region-qualified dev group and leave the original group untouched. Approved issue revision: https://github.com/vkaam/phonebuddy/issues/12 updated 2026-11-01T09:24:47Z; body SHA-256 294ffca40d3b855da99756164687afc214bf018536d424f3fd98f1647ddc2c7c. Approval evidence: direct user instructions in this conversation to continue TASK-5 and configure dev/test in West Europe in the user-designated subscription, using owner tag PHONEBUDDY-PLATFORM, costCenter PHONEBUDDY-NONPROD, and a separate 10 USD monthly budget for each. Branch: agent/gh-12-3-configure-test-azure. Repository scope: infra/main.bicep; infra/modules/foundation.bicep; infra/environments/dev.bicepparam; infra/environments/test.bicepparam; scripts/check_bicep.py; tests/test_bicep_preflight.py; infra/README.md; this task record through Backlog CLI. Azure scope: create rg-pb-dev-westeurope-foundation and rg-pb-test-westeurope-foundation in the user-designated subscription; preserve rg-pb-dev-foundation in Sweden Central; replace the old dev budget with phonebuddy-dev-monthly-10usd and create phonebuddy-test-monthly-10usd at the user-designated MCA billing-account scope, each filtered by its environment tag and costCenter PHONEBUDDY-NONPROD. Production and cleanup of the old Sweden Central dev group are out of scope. Verify with pinned Bicep 0.34.44 dev/test readiness checks, the focused unittest suite, git diff --check, subscription what-if and repeated deployments using the matching parameter files, resource-group location/tag inspection, and budget readback for amount, monthly period, environment/costCenter filter, expiry and alert thresholds/owner routing. No credentials or private account identifiers may be committed. Budget alerts do not stop spend.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dev and test parameter files use westeurope, owner PHONEBUDDY-PLATFORM and costCenter PHONEBUDDY-NONPROD; the preflight validates region-specific distinct resource-group names and passes for both environments.
- [x] #2 West Europe dev and test foundation resource groups deploy successfully twice in the user-designated subscription; the second what-if for each reports no changes, expected environment and cost-center tags are present, and the existing Sweden Central dev group is preserved.
- [x] #3 Separate 10 USD monthly budgets exist for dev and test, each filtered to its environment and costCenter PHONEBUDDY-NONPROD, with the approved alert thresholds and budget owner routing verified.
- [x] #4 The runbook documents the region-scoped names, both deployments and budget evidence, and the retained legacy dev group and cleanup limitation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reconfirm the existing dev resource group is in Sweden Central and never attempt to change its immutable location; use region-qualified names for the new West Europe dev and test groups, preserving the old group. 2. Update Bicep naming, dev/test parameter values, preflight contracts and regression tests so resource-group names encode the environment and region. 3. Update the runbook with the approved subscription, West Europe region, cost center,  per-environment budgets and retained legacy dev group. 4. Run pinned Bicep validation, focused tests and diff checks. 5. Authenticate with the user-designated subscription, review what-if for both groups, deploy each twice, verify tags and converge/no-change results, and update the separate budgets filtered by environment plus cost center. 6. Record evidence in TASK-47 and publish one PR; note any remaining identity, budget-scope or cleanup gate.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Existing rg-pb-dev-foundation is in Sweden Central and remains unchanged. The initial what-if for the two West Europe groups showed one expected create action each; both deployments succeeded and repeated what-if checks reported no changes. Resource-group readback verified locations and tags. Separate MCA budgets phonebuddy-dev-monthly-10usd and phonebuddy-test-monthly-10usd are configured at 10 USD/month from 2026-11-01 to 2027-11-01, filtered by matching environment and PHONEBUDDY-NONPROD, with actual 50/80/100 and forecast 100 alerts routed to the approved budget owner. The superseded 20 USD dev budget was removed. Budget alerts are informational, and future billable resources need direct tags or billing-profile tag inheritance. No production configuration or old resource-group cleanup was performed.

For public-repository safety, repository content now uses owner tag PHONEBUDDY-PLATFORM and omits subscription, tenant, billing-account and personal-email identifiers; budget owner routing remains configured in Azure. The dev/test owner-tag-only deployments both succeeded, and final what-if for each returned no changes. Final local verification after the sanitized parameter update passed for dev readiness, test readiness, all 11 focused tests and diff checks.

Publication blocker (2026-11-01): sanitized commit db197b7 is local on agent/gh-12-3-configure-test-azure and based on current origin/main. git push -u origin agent/gh-12-3-configure-test-azure returned HTTP 403: GitHub denied write access to vkaam/phonebuddy for the checkout credential mees-vankaam_ravago. No PR exists yet. Keep TASK-47 In Progress. Next action: repository owner must grant this GitHub identity write access or configure an authorized credential; then push this branch and open a PR.

Publication update (2026-11-01): Git push was denied for the checkout credential, so the sanitized branch was published using the connected GitHub tools. Draft PR #53: https://github.com/vkaam/phonebuddy/pull/53 (head f378b5583453e890d252621d2f8d52697a24b25a). The previous publication blocker is resolved; required PR checks and review remain outstanding. Keep TASK-47 In Progress until required checks pass.

Final PR verification (2026-11-01): on PR #53 head 8c5cc5446fcf614436fbcc73dcf53b5b65835092, Quality and Risk report (advisory) both completed successfully. PR review and merge remain repository gates.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Configured and deployed region-qualified West Europe Azure foundations for dev and test, with PHONEBUDDY-NONPROD tags and separate 10 USD monthly budgets. Preserved the legacy Sweden Central dev resource group. Updated Bicep naming, preflight checks, regression tests and the runbook. Verified pinned Bicep 0.34.44 readiness for both environments, 11 focused unit tests, diff checks, repeated deployments, resource tags and budget settings; final what-if for each environment reported no changes. Published sanitized changes in PR #53 using the connected GitHub tools. The latest PR head passed Quality and Risk report (advisory). Budget alerts do not stop spend; production and legacy-group cleanup remain out of scope. PR review and merge are still pending.
<!-- SECTION:FINAL_SUMMARY:END -->
