---
id: TASK-128
title: Issue 161 - Run database migrations and API grants as part of the dev release
status: Done
assignee:
  - '@claude'
created_date: '2026-11-22T14:09:00Z'
updated_date: '2026-11-22T20:40:00Z'
labels:
  - task
dependencies: []
priority: high
ordinal: 108000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/161
Branch: agent/gh-161-ci-migrations
Scope: .github/workflows/azure-deploy.yml; .github/workflows/azure-recover.yml; infra/hosting.bicep; infra/modules/data-platform.bicep; infra/main.bicep; infra/release-schema.json; scripts/**; tests/**; services/api/migrations/**; docs/azure-delivery-policy.md; docs/dev-sign-in-runbook.md
Verify: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py; npm test --prefix services/api; BICEP=bicep python3 -B scripts/check_bicep.py

The dev SQL server accepts Entra logins only and the release workflow never touches the database; migration_mode in infra/release-schema.json is none. The migration and the API identity grants for #152 therefore had to be run by hand, which contradicts the policy that every migration succeeds before traffic moves. The owner will not run SQL by hand, so the release itself must be able to reach the database: the deployment identity has to become a database administrator through infrastructure code, not through a manual step. Changing the server administrator is an owner decision recorded in the issue; the owner must still have a way in. The live run is a separate follow-up task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The dev release applies the versioned SQL in services/api/migrations before the new revision receives traffic, idempotently, and a failed migration stops the release before any traffic change
- [x] #2 The release manifest records the migration mode, and rollback or recovery never reverses a migration or restores a database over newer data
- [x] #3 A versioned idempotent SQL step grants the API managed identity SELECT on OrganizationMembership and SELECT, INSERT, UPDATE, DELETE on WebSocketTicket, and no write access to OrganizationMembership
- [x] #4 The step authenticates with Entra only; no SQL password, secret or token is committed or logged, and tests show the workflow and scripts never print connection secrets
- [x] #5 No human runs SQL: the Bicep deployment makes the deployment identity the SQL server Entra administrator (or equivalent), the release connects with an Entra token, opens a temporary firewall rule for the runner and removes it afterwards, and creates the API identity user by SID so no directory lookup is needed
- [x] #6 The owner's initial dev membership is seeded by the same release step from a public Actions Variable listing object IDs, idempotently, so a first sign-in works without manual SQL; the owner keeps database access through a user the step creates
- [x] #7 Tests cover the migration runner, its failure handling and the firewall cleanup, and the runbook describes the automated flow instead of manual SQL
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Feasibility (done): data-platform.bicep is not deployed by any workflow (owner runs subscription-scope main.bicep). The release identity has Contributor on the dev foundation group only, which allows Microsoft.Sql administrators and firewallRules writes but not role assignments. So the SQL Entra administrator is set from infra/hosting.bicep (existing server, opt-in manageSqlAdministrator) by the release itself; data-platform/main.bicep gain a sqlAdminPrincipalType parameter so a manual re-run cannot revert to a user.
2. scripts/database_release.py: validated inputs (GUID rule from api_settings), destructive-SQL lint, migration ledger runner over a connection abstraction (go-sqlcmd with ActiveDirectoryAzCli, pinned binary), SID-based CREATE USER for the API identity and owner, role membership, idempotent membership seeding, firewall rule context manager that always removes the rule, token masking, secret-free output.
3. Migration 002 creates role pb_api with the minimal grants; release step adds the API identity to it.
4. azure-deploy.yml: validate inputs early, grant admin via Bicep (workload off), install pinned sqlcmd, migrate before the traffic-changing deploy, always remove firewall rule; recovery workflow never migrates.
5. release-schema.json: version 2, migration_mode expand.
6. Tests under tests/, runbook and delivery policy updates, run Verify, finalize record.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Owner decision (conversation, 2026-11-22): the deployment identity becomes the SQL server Entra administrator via infrastructure code; the release step creates a database user for the owner so they keep access, and seeds the owner membership. Nobody runs SQL by hand.

Validation: quality.py passed; run_required_unittests 260 OK (38 new in tests/test_database_release.py); services/api npm test 8 pass; check_bicep passed (BICEP on PATH). Unproven until the live follow-up: go-sqlcmd ActiveDirectoryAzCli against the real server, that Azure accepts the Application administrator login string, runner IP detection via api.ipify.org, and the CREATE USER by SID on the real database. data-platform.bicep itself is still not deployed by any workflow; the release manages only the administrator through hosting.bicep. The first migrated release is not auto-rolled back to the schema-0 release (recovery refuses by design).

Review follow-up: the owner database user is now created right after connecting and before any migration; seeding makes only the owner admin (others user); API privilege check uses EXECUTE AS USER with HAS_PERMS_BY_NAME; destructive lint covers DELETE without FROM and MERGE ... THEN DELETE; firewall cleanup failure no longer hides the original error. Unproven live: the SQL administrator SID is the deployment identity's object ID, as Microsoft's Bicep docs state for administrators sid; whether Azure accepts it for this service principal is untested until the live follow-up. Portal recovery for an owner lock-out is in docs/dev-sign-in-runbook.md.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The dev release now migrates the database before traffic moves. scripts/database_release.py discovers services/api/migrations (ordered, ledgered in dbo.SchemaMigration with checksums, destructive SQL refused unless a contract release), opens a temporary firewall rule for the runner and always removes it (plus a stale-rule sweep and an always-run workflow step), connects with go-sqlcmd ActiveDirectoryAzCli (Entra token, no password), creates the API identity user by SID and adds it to role pb_api (migration 002: SELECT on OrganizationMembership, SELECT/INSERT/UPDATE/DELETE on WebSocketTicket, writes to memberships revoked and verified absent), creates the owner db_owner user, and seeds missing memberships from PHONEBUDDY_DEV_MEMBER_OBJECT_IDS / PHONEBUDDY_DEV_ORGANIZATION_ID without touching existing rows. hosting.bicep gained an opt-in manageSqlAdministrator that makes the deployment identity the Entra administrator (Contributor suffices); data-platform and main gained sqlAdminPrincipalType. azure-deploy.yml runs check, the administrator deployment (workload off), migrate, then the traffic-changing deployment; recovery workflows never migrate. release-schema.json is version 2, expand. Verified by unit tests and the four Verify commands. Not proven: any live run (separate follow-up), including the points listed in the notes.
<!-- SECTION:FINAL_SUMMARY:END -->
