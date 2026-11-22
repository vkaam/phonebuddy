---
id: TASK-120
title: >-
  Issue 152 - Host the API in the dev Container App with sign-in and CORS
  settings
status: To Do
assignee: []
created_date: '2026-11-22T09:31:00Z'
labels: []
dependencies:
  - TASK-119
priority: high
ordinal: 103000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-2-dev-api-hosting
Scope: infra/**; services/api/src/**; services/api/test/**; docs/azure-delivery-policy.md; apps/web/README.md; tests/**
Verify: python3 -B scripts/check.py; python3 -B scripts/run_required_unittests.py; npm --prefix services/api test

The hosted dev API needs its public sign-in settings, database address and managed identity wiring, HTTPS-only ingress and a CORS origin restricted to the dev web app. These must come from deployment parameters, never from committed secrets, and stay separate from test and prod.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The dev Container App receives ENTRA_TENANT_ID, ENTRA_API_CLIENT_ID, WEB_ORIGIN, SQL_SERVER, SQL_DATABASE and SQL_MANAGED_IDENTITY_CLIENT_ID from parameters or variables, with no secret in the template or repository
- [ ] #2 Ingress is HTTPS only and the API allows browser requests only from the exact dev Static Web App origin
- [ ] #3 The app managed identity gets only the Azure SQL access the API needs, and test and prod parameters are unchanged
- [ ] #4 What-If and Bicep validation pass without destructive changes
<!-- AC:END -->
