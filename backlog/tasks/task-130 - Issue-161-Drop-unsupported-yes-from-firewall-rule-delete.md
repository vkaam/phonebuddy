---
id: TASK-130
title: Issue 161 - Drop unsupported --yes from firewall-rule delete
status: Done
assignee:
  - '@claude'
created_date: '2026-11-22T21:04:00Z'
updated_date: '2026-11-22T21:05:00Z'
labels:
  - task
dependencies: []
ordinal: 110000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/161
Branch: agent/gh-161-firewall-delete
Scope: scripts/database_release.py; tests/test_database_release.py
Verify: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py

Live dev release run 45069554117 failed because az sql server firewall-rule delete does not accept --yes (unrecognized arguments). The administrator sign-in and migrations 001/002 already worked live. A leftover rule pb-release-45068400522-1 remains on the dev SQL server and is removed by the fixed stale-rule sweep on the next release.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both firewall-rule delete calls (temporary rule removal and stale-rule sweep) no longer pass --yes
- [x] #2 Unit tests assert the delete argument lists contain no --yes
- [x] #3 No other az command in workflows, scripts or docs passes an unsupported --yes
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove --yes from both firewall-rule delete calls. 2. Assert in tests. 3. grep for other unsupported --yes (none found).
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed --yes from both az sql server firewall-rule delete calls in scripts/database_release.py (TemporaryFirewallRule.remove and remove_stale_rules). Tests assert the delete argument lists carry no --yes. Searched .github, scripts, docs, tests and infra: no other --yes use. quality.py passed and run_required_unittests.py ran 264 tests OK. Leftover rule pb-release-45068400522-1 is left for the next release's stale sweep.
<!-- SECTION:FINAL_SUMMARY:END -->
