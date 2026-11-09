---
id: TASK-78
title: Issue 88 - Move dev and test foundations to Belgium Central
status: Done
assignee:
  - '@codex'
created_date: '2026-11-08T21:15:00Z'
updated_date: '2026-11-09T07:08:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-47
  - TASK-57
references:
  - https://github.com/vkaam/phonebuddy/issues/88
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - scripts/bootstrap_github_oidc.py
  - .github/workflows/azure-oidc-smoke.yml
  - infra/github-oidc.md
  - https://github.com/vkaam/phonebuddy/pull/89
modified_files:
  - >-
    backlog/tasks/task-78 -
    Issue-88-Move-dev-and-test-foundations-to-Belgium-Central.md
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - scripts/bootstrap_github_oidc.py
  - tests/test_azure_oidc_bootstrap.py
  - .github/workflows/azure-oidc-smoke.yml
  - .github/workflows/azure-hosting-what-if.yml
  - .github/workflows/azure-health-gate.yml
  - infra/github-oidc.md
  - infra/README.md
  - docs/azure-delivery-policy.md
priority: high
type: task
ordinal: 71000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Phonebuddy dev and test have moved to a new Azure subscription and tenant and now use separate Entra applications, but the repository and Azure foundation still target the former West Europe/shared-identity setup. The owner requested the missing setup on 2026-11-08.

Issue: https://github.com/vkaam/phonebuddy/issues/88
Approved revision: 2026-11-09T07:08:20Z; body SHA-256 09782a9c3d8895bafefa9eec451c93671ea477b60473a40264380716a7680834.
Approval evidence: Direct owner request in this Codex conversation on 2026-11-08 to provide the missing setup after the live audit.
Branch: agent/gh-88-1-belgium-foundations
Scope: infra/environments/dev.bicepparam; infra/environments/test.bicepparam; scripts/bootstrap_github_oidc.py; tests/test_azure_oidc_bootstrap.py; .github/workflows/azure-oidc-smoke.yml; .github/workflows/azure-hosting-what-if.yml; .github/workflows/azure-health-gate.yml; infra/github-oidc.md; infra/README.md; docs/azure-delivery-policy.md; backlog/tasks/task-78 - Issue-88-Move-dev-and-test-foundations-to-Belgium-Central.md.
Azure scope: register required providers in the newly designated nonproduction subscription; deploy only two Belgium Central foundation groups with existing nonproduction tags; assign each existing dev/test app Contributor only on its own foundation group; inspect SQL edition availability and budgets without creating SQL or application capacity. GitHub scope: align dev/test environment secret values with their respective existing app and new tenant/subscription while retaining main-only branch restrictions. Preserve all old resources.
Verify: python3 -B -m unittest discover -s tests -p test_azure_oidc_bootstrap.py -v; BICEP=/path/to/pinned/bicep python3 -B scripts/check_bicep.py --deployment-ready dev; repeat for test; actionlint .github/workflows/azure-oidc-smoke.yml .github/workflows/azure-hosting-what-if.yml .github/workflows/azure-health-gate.yml; git diff --check; Azure provider/group/federation/role/budget readback and non-mutating SQL edition query; hosted Quality and applicable PR checks. No credentials or private account identifiers may be committed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Dev and test Belgium Central foundation groups exist in the new subscription with expected tags, and prior groups/resources remain intact.
- [x] #2 Each existing app has only its matching GitHub federation and Contributor at its own new foundation group, with no cross-environment role assignment in the new subscription.
- [x] #3 Repository parameters, workflows, bootstrap, tests, and runbooks target Belgium Central and distinct identities; local and required PR checks pass.
- [x] #4 Provider and SQL edition checks, budget coverage or explicit billing-scope blocker, and GitHub environment/OIDC verification or explicit access blocker are recorded with evidence.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Change dev/test Bicep parameters and all trusted Azure workflow group references to Belgium Central, and replace shared-identity bootstrap assumptions with one app per environment. 2. Update focused tests and runbooks, keeping old resources out of cleanup scope. 3. Run local Bicep, unit, workflow and diff checks. 4. Register required providers, deploy only new Belgium Central foundation groups, assign each existing app Contributor at only its matching group, and verify provider/SQL/budget state. 5. Configure GitHub environment credentials if an authorized interface is available, publish the PR, obtain independent review, and monitor required checks; record any remaining live smoke or billing blocker.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-08/09 foundation setup: Pinned Bicep 0.34.44 dev and test readiness checks passed. Initial subscription what-if showed exactly one Create per environment. The first create attempt used the same top-level deployment name as the nested module and failed with DeploymentActive before any group was created; retried with distinct rollout names and both deployments succeeded. Readback verified both Belgium Central groups with environment, service, owner and costCenter tags. Repeat what-if returned Deploy for the nested deployment metadata, with no group Modify/Delete. Required providers App, CognitiveServices, ContainerRegistry, KeyVault, ManagedIdentity, OperationalInsights, ServiceBus, Sql and Web now report Registered; Storage was already Registered. SQL edition listing now succeeds in Belgium Central, with Free Trial restrictions on some higher tiers. The existing dev and test app registrations each retain exactly one matching repository-ID-qualified federation and no password/certificate returned by credential list. Contributor was assigned only to each matching new group; direct/inherited readback found exactly one role assignment per app at its own group. No existing groups or workloads were changed. GitHub environment secret values and smoke runs remain unverified; GitHub asks for owner passkey confirmation. Separate budget alert recipient and billing scope are pending review.

2026-11-09 follow-up: GitHub Safari passkey confirmation completed. Both dev and test environments retain main-only deployment rules and three Azure secrets each, last updated by the owner approximately 12 hours before readback; their encrypted values cannot be inspected, and the owner states they set them yesterday. Both AZURE_LOCATION variables were changed from westeurope to belgiumcentral and read back after save. Separate resource-group-scoped phonebuddy-dev-monthly-10 and phonebuddy-test-monthly-10 budgets were created in the new subscription and read back with $10 Monthly amount, 50/80/100% Actual and 100% Forecasted alerts to the owner-approved current GitHub/Azure email. The signed-in user ID in the new tenant differs from both environments’ PHONEBUDDY_SQL_ADMIN_OBJECT_ID variable; owner confirmation to correct this future access setting is pending. Local 97 required Python tests, pinned Bicep 0.34.44 dev/test readiness, actionlint on changed workflows and git diff --check pass. GitHub Azure secret contents and post-merge OIDC smoke remain unverified.

2026-11-09 independent review: a separate agent reviewed the scoped diff and independently read back both Azure groups, matching tags, one matching federation per app, and one own-group Contributor assignment per app. It found no blocking code defect. Its two documentation findings were corrected in docs/azure-delivery-policy.md and infra/README.md. GitHub dev PHONEBUDDY_COST_CENTER was corrected from PHONEBUDDY-TEST to PHONEBUDDY-NONPROD and read back. Issue #88 received a progress/evidence comment; the approved issue revision is pinned to its resulting 2026-11-09T06:51:31Z update. Required PR checks and post-merge dev/test OIDC smoke are still pending.

2026-11-09 GitHub variable follow-up: With owner action-time confirmation, both dev and test PHONEBUDDY_SQL_ADMIN_OBJECT_ID values were updated from the prior-tenant object ID to the signed-in user object ID in the new tenant. Each saved value was read back in GitHub; the identifier itself is intentionally omitted from repository records. This is configuration only: no SQL server or database exists in these new groups.

2026-11-09 publication: Draft PR https://github.com/vkaam/phonebuddy/pull/89 opened from the approved branch against current main. Local git push failed 403 because the configured CLI credential is for a different account; the connected GitHub app published the identical local tree and remote readback verified matching tree and main ancestry. Issue #88 was updated with PR and access evidence and is still open. Required PR checks, final task acceptance, merge, and trusted post-merge dev/test OIDC smoke remain pending.

2026-11-09 finalization evidence: Old subscription readback still lists Sweden Central dev, West Europe dev/test, and France Central dev/test foundation groups. PR #89 current head 359d6c0 has required Quality=success and advisory Risk report=success; repository ruleset Standard main requires strict Quality from GitHub Actions, zero approving reviews, and resolved review threads; PR discussion has no comments or threads and is now ready for review. Local required checks passed as previously recorded. Pre-merge GitHub/OIDC access blocker: environment deployment rules permit only main, so the updated workflow cannot obtain a trusted dev/test environment OIDC token from its feature branch. GitHub encrypts the existing secret values, preventing direct readback. The owner reports the new values were set; each must be exercised by the updated main-only smoke workflow immediately after merge. This explicit access boundary is the TASK-78 AC4 pre-merge alternative, not a claim that OIDC has passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Configured and verified separate Belgium Central dev/test foundation groups, provider registration, one matching GitHub federation and own-group Contributor assignment per existing app, and separate $10 monthly resource-group budget alerts. Updated repository parameters, bootstrap guard, trusted workflows, tests, and runbooks; aligned GitHub location and approved SQL admin variables. Old subscription groups remain. Local 97-test suite, pinned Bicep dev/test checks, workflow lint, diff check, independent review, and PR #89 Quality/risk checks passed at head 359d6c0. GitHub encrypted secret values cannot be read and main-only environment restrictions prevent pre-merge OIDC smoke; run the updated dev/test smoke workflows after merge to prove authentication and isolation. No SQL or billable application workload was provisioned.
<!-- SECTION:FINAL_SUMMARY:END -->
