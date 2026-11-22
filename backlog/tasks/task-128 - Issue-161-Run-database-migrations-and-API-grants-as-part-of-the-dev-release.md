---
id: TASK-128
title: Issue 161 - Run database migrations and API grants as part of the dev release
status: To Do
assignee: []
created_date: '2026-11-22T14:09:00Z'
updated_date: '2026-11-22T14:10:00Z'
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
- [ ] #1 The dev release applies the versioned SQL in services/api/migrations before the new revision receives traffic, idempotently, and a failed migration stops the release before any traffic change
- [ ] #2 The release manifest records the migration mode, and rollback or recovery never reverses a migration or restores a database over newer data
- [ ] #3 A versioned idempotent SQL step grants the API managed identity SELECT on OrganizationMembership and SELECT, INSERT, UPDATE, DELETE on WebSocketTicket, and no write access to OrganizationMembership
- [ ] #4 The step authenticates with Entra only; no SQL password, secret or token is committed or logged, and tests show the workflow and scripts never print connection secrets
- [ ] #5 No human runs SQL: the Bicep deployment makes the deployment identity the SQL server Entra administrator (or equivalent), the release connects with an Entra token, opens a temporary firewall rule for the runner and removes it afterwards, and creates the API identity user by SID so no directory lookup is needed
- [ ] #6 The owner's initial dev membership is seeded by the same release step from a public Actions Variable listing object IDs, idempotently, so a first sign-in works without manual SQL; the owner keeps database access through a user the step creates
- [ ] #7 Tests cover the migration runner, its failure handling and the firewall cleanup, and the runbook describes the automated flow instead of manual SQL
<!-- AC:END -->
