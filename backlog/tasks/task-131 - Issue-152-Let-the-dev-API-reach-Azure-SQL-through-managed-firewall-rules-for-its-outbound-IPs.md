---
id: TASK-131
title: >-
  Issue 152 - Let the dev API reach Azure SQL through managed firewall rules for
  its outbound IPs
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-23T07:56:00Z'
updated_date: '2026-11-23T07:56:00Z'
labels: []
dependencies: []
ordinal: 111000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-sql-firewall-api
Scope: infra/**; scripts/check_bicep.py; scripts/database_release.py only if needed; tests/** for those; docs/azure-delivery-policy.md; docs/dev-sign-in-runbook.md
Verify: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py; BICEP=$HOME/.azure/bin/bicep python3 -B scripts/check_bicep.py

Live dev: every /api/me returns 503 because Azure SQL (public access on, Entra-only auth) has no firewall rule for the Container App's outbound IP (98.66.189.7): 'Client with IP address is not allowed to access the server'. The owner decided the fix is infrastructure code, not a portal step: the release manages SQL server firewall rules for the Container App's outbound IPs (read from the app's outboundIpAddresses so the rules follow IP changes on each release). Not the allow-all-Azure-services 0.0.0.0 rule and no private networking in dev; production should adopt private networking later. The release's temporary runner rules use the pb-release- prefix and a stale sweep deletes by it, so the new rules must use a different prefix. Post-merge live proof is a separate follow-up task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 hosting.bicep declares one SQL server firewall rule per outbound IP address of the Container App (read from the app), named with a prefix that does not start with pb-release-, only when the workload is deployed
- [ ] #2 No rule uses the 0.0.0.0 allow-Azure-services range and no SQL credential or private networking is introduced
- [ ] #3 scripts/database_release.py's stale-rule sweep provably cannot delete the managed API rules, covered by a test
- [ ] #4 check_bicep.py validates the rule shape and tests cover it; the what-if guard still accepts the release preview
- [ ] #5 docs/azure-delivery-policy.md and docs/dev-sign-in-runbook.md document the rule, why it exists, the stale-rule limitation and that production should use private networking
- [ ] #6 python3 -B scripts/quality.py, scripts/run_required_unittests.py and check_bicep.py pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add infra/modules/sql-firewall-rules.bicep (one rule per outbound IP, name pb-api-egress-N) and call it from hosting.bicep when deployWorkload, passing app.properties.outboundIpAddresses (module param keeps the loop valid at deploy time).
2. Extend check_bicep.py (shape, prefix, no 0.0.0.0) and tests; add database_release sweep test.
3. Document in azure-delivery-policy and dev-sign-in-runbook.
4. Verify, read-only what-if against dev, finalize record.
<!-- SECTION:PLAN:END -->
