---
id: TASK-121
title: Issue 152 - Create the dev Entra app registrations from the deployment
status: To Do
assignee: []
created_date: '2026-11-22T09:31:00Z'
updated_date: '2026-11-22T11:08:00Z'
labels: []
dependencies: []
priority: high
ordinal: 104000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-3-entra-registrations
Scope: infra/**; .github/workflows/**; scripts/**; tests/**; docs/azure-delivery-policy.md; docs/infra-entra-dev.md; apps/web/README.md
Verify: python3 -B scripts/check.py; python3 -B scripts/run_required_unittests.py

The owner decided on 2026-11-22 that the deployment, not the owner by hand, creates the dev API and SPA app registrations in the nonproduction tenant. No registrations exist for dev, and the deployment identity may lack directory permissions. This task must state the minimum Microsoft Graph permission the owner has to grant once, as a documented manual step, and keep the identity from touching test, prod or any corporate tenant. If that permission cannot be scoped safely, stop and ask the owner to reconsider hand creation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A repeatable deployment step creates or reuses the dev API registration (exposed scope) and the dev SPA registration (redirect URIs for the dev web origin and local development only) idempotently
- [ ] #2 The step runs only against the dev nonproduction tenant and fails closed if run for test, prod or another tenant
- [ ] #3 The tenant ID, SPA client ID, API client ID and API scope are published as non-secret outputs for the four web Actions Variables and the API settings; no client secret is created, stored or logged
- [ ] #4 The one-time owner permission grant is documented with the least privilege required and how to revoke it
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Context 2026-11-22: the API settings preflight (scripts/api_settings.py) and the web config generator expect the registration outputs as public Actions Variables: PHONEBUDDY_DEV_ENTRA_TENANT_ID, PHONEBUDDY_DEV_ENTRA_API_CLIENT_ID (new, API app), PHONEBUDDY_DEV_ENTRA_CLIENT_ID (SPA), PHONEBUDDY_DEV_API_SCOPE, plus SQL ones. Until they exist, the main dev release stops at the settings preflight.
<!-- SECTION:NOTES:END -->
