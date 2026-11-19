---
id: TASK-117
title: Pin release-state Storage defaults so What-If stops reporting deletions
status: Done
assignee:
  - '@claude'
created_date: '2026-11-19T04:28:00Z'
updated_date: '2026-11-19T04:31:00Z'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 100000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/136
Branch: agent/gh-136-2-pin-storage-defaults
Scope: infra/hosting.bicep; tests/test_bicep_ci_boundary.py; docs/azure-delivery-policy.md
Verify: python3 -B scripts/check_bicep.py; python3 -B scripts/run_required_unittests.py; a read-only az deployment group what-if of infra/hosting.bicep against the dev foundation resource group with the release workflow parameters, checked with scripts/check_bicep.py --what-if-result.

Since PR #135 hardened the What-If guard (TASK-104), every dev release stops at the Bicep preview: runs 43814988299 (16 Nov) and 44456932634 (19 Nov). The guard treats any Storage property Delete as destructive. The only Storage deletions in the retained what-if.json are Azure defaults the template never sets: blobServices/default deleteRetentionPolicy.allowPermanentDelete (false), and the release-state container defaultEncryptionScope ($account-encryption-key) and denyEncryptionScopeOverride (false). Other property deletions are on non-Storage resources, which the guard does not inspect. An earlier triage record (TASK-107) was announced on the issue but never committed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 infra/hosting.bicep sets allowPermanentDelete false on the release-state blob service, and defaultEncryptionScope $account-encryption-key and denyEncryptionScopeOverride false on the release-state container, matching current dev values so no Azure setting changes
- [x] #2 A regression test fails if any of the three explicit values is removed from the template
- [x] #3 The destructive-change guard is unchanged and still rejects Storage property deletions
- [x] #4 A read-only What-If of the dev hosting deployment with the changed template contains no Storage property deletions and passes scripts/check_bicep.py --what-if-result
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Set allowPermanentDelete false on releaseStateBlobService.deleteRetentionPolicy, and defaultEncryptionScope $account-encryption-key plus denyEncryptionScopeOverride false on releaseStateContainer, in infra/hosting.bicep (values equal current dev state).
2. Add a regression test in tests/test_bicep_ci_boundary.py that fails if any of the three is removed; leave scripts/release_recovery.py unchanged.
3. Note the explicit defaults in docs/azure-delivery-policy.md.
4. Run check_bicep.py and the unit suite; run a read-only what-if with the release workflow parameters and validate it with check_bicep.py --what-if-result.
5. Finish the task record, independent review, merge, then watch the next main release.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Claim check 2026-11-19: status pass, claim_verified true (base e80a5ff). Owner instructed this work and the approved label on issue 136 in a Claude Code session.

Verification 2026-11-19. Compiled template: blobServices deleteRetentionPolicy {enabled, days 30, allowPermanentDelete false}; release-state container {publicAccess None, defaultEncryptionScope $account-encryption-key, denyEncryptionScopeOverride false}, equal to the before-values in the retained what-if.json, so no Azure setting changes. BICEP=~/.azure/bin/bicep python3 -B scripts/check_bicep.py passed; required unit suite OK; scripts/quality.py passed. New tests: test_release_state_storage_pins_azure_defaults_that_what_if_would_delete and test_storage_property_deletion_still_blocks_the_release; scripts/release_recovery.py unchanged.
Read-only what-if against rg-pb-dev-francecentral-foundation with the release workflow parameters (image digest and release version of blocked run 44456932634): status Succeeded, counts Create 0 / Modify 7 / NoChange 9 / Ignore 10; all release-state Storage resources NoChange with no deletions; check_bicep.py --what-if-result with the expected scope exit 0; release_recovery.py check-what-if destructive=false. Control: the same what-if with the origin/main template gives destructive=true. Remaining Modify entries are on Container Apps, diagnostic settings, the registry, App Insights and the Static Web App, which the guard does not treat as destructive (unchanged behavior).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Unblocked dev releases (issue #136). Since the What-If guard was hardened in PR #135, every release stopped at the Bicep preview because Azure reported three omitted Storage defaults as deletions. infra/hosting.bicep now sets them explicitly to their current values: allowPermanentDelete false on the release-state blob service, and defaultEncryptionScope $account-encryption-key plus denyEncryptionScopeOverride false on the release-state container. The guard is unchanged and still rejects Storage deletions. A read-only what-if with the blocked release parameters now passes both release checks (destructive=false); with main template it still fails. Regression tests cover the pinned values and the guard. The delivery policy notes the rule. The live release after merge is the final confirmation.
<!-- SECTION:FINAL_SUMMARY:END -->
