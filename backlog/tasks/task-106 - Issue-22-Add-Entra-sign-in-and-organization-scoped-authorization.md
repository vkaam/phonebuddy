---
id: TASK-106
title: Issue 22 - Add Entra sign-in and organization-scoped authorization
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-15T20:39:00Z'
updated_date: '2026-11-15T21:27:00Z'
labels:
  - identity
  - backend
  - frontend
dependencies:
  - TASK-60
references:
  - https://github.com/vkaam/phonebuddy/issues/22
  - docs/software-plan.md
  - apps/web/src/main.tsx
  - apps/web/README.md
  - >-
    https://learn.microsoft.com/en-us/entra/identity-platform/reference-third-party-cookies-spas
  - https://learn.microsoft.com/en-us/entra/identity-platform/access-tokens
  - >-
    https://learn.microsoft.com/en-us/azure/azure-sql/database/azure-sql-javascript-mssql-quickstart
modified_files:
  - >-
    backlog/tasks/task-106 -
    Issue-22-Add-Entra-sign-in-and-organization-scoped-authorization.md
  - services/api/package.json
  - services/api/package-lock.json
  - services/api/tsconfig.json
  - services/api/src/repository.ts
  - services/api/src/config.ts
  - services/api/src/token.ts
  - services/api/src/app.ts
  - services/api/src/server.ts
  - services/api/migrations/001_identity.sql
  - services/api/README.md
  - services/api/test/app.test.ts
  - apps/web/package.json
  - apps/web/package-lock.json
  - apps/web/README.md
  - apps/web/src/config.js
  - apps/web/src/auth.js
  - apps/web/src/main.tsx
  - apps/web/src/style.css
  - apps/web/e2e/smoke.spec.js
  - apps/web/tests/config.test.mjs
  - apps/web/tests/auth.test.mjs
  - apps/web/config.example.json
priority: high
type: feature
ordinal: 94000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The existing web preview has no authentication or backend, while every pilot feature must enforce organization boundaries from the first authenticated request.

Issue: https://github.com/vkaam/phonebuddy/issues/22
Approved revision: 2026-11-01T09:25:07Z; body SHA-256 00bf2af01986581544cb703b4f5dadb2f8e77e8db5e73a9ce3c7b8362a001e74.
Approval evidence: Canonical issue authored by the repository owner; the owner authorized prerequisite work in Codex on 2026-11-15 with “Work prerequisites first” after selecting issue #26.
Branch: agent/gh-22-identity-org-auth
Scope: apps/web/**; services/api/**; tests/**; backlog/tasks/task-106 - Issue-22-Add-Entra-sign-in-and-organization-scoped-authorization.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/run_required_unittests.py, and npm --prefix services/api test. CI Quality must pass on the final PR head. Exercise the identity and organization-isolation cases in the acceptance criteria with synthetic identities only.
Spec: Preserve issue #22 acceptance. Use the already planned React web and Fastify API boundaries. Do not deploy Azure resources, create/consent Entra applications, add real users, or use production data as part of this task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The browser can sign in, sign out, and clear the application session on expiry using the configured Entra identity flow.
- [x] #2 The API accepts only tokens with a valid signature and the configured issuer, audience, and lifetime; invalid or expired tokens are denied.
- [x] #3 The server resolves organization membership and user/admin roles independently of the Entra directory ID and enforces them on protected HTTP and WebSocket access.
- [x] #4 Tests cover user/admin roles, revoked membership, expired tokens, and cross-organization HTTP and WebSocket denial.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Research the React shell, planned Fastify API and Azure SQL boundaries, Entra OIDC requirements, and test conventions. The current issue prerequisites are satisfied; no Entra app registration or Azure deployment is included.
2. Implement browser sign-in with MSAL Browser authorization code plus PKCE. Keep client ID/authority/scope as public configuration and send access tokens only to the HTTPS API; never put a client secret or access token in browser configuration or a WebSocket URL.
3. Implement Fastify API access-token validation with JOSE and Entra discovery/JWKS, enforcing signature, configured issuer, API audience, and token time claims. Resolve tenant/object identity to server-side organization membership and roles from Azure SQL with managed identity, keeping organizationId separate from Entra tenant ID.
4. Add an authenticated WebSocket-ticket endpoint that returns a short-lived, one-use opaque ticket bound to the principal and organization. Store only its hash and consume it exactly once during WebSocket upgrade; reject expired, replayed, and cross-organization tickets.
5. Add synthetic tests for sign-in/session expiry, token signature/issuer/audience/time failures, membership and roles, revocation, and HTTP/WebSocket isolation. Run local tests/checks, final Quality, and the live Backlog claim check.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented SPA auth code + PKCE with MSAL session storage, sign-in/out and reauthentication handling; protected workspace rendering waits for API membership confirmation. API validates Entra RS256 tokens against tenant issuer, audience, required claims and token lifetime; membership and roles come from Azure SQL, and one-use hashed WebSocket tickets are organization-bound and recheck active membership. Synthetic API tests cover user/admin memberships, no-membership/cross-organization HTTP denial, revoked membership, invalid signature/issuer/audience/expired tokens, WebSocket organization binding and replay. Web unit tests, web build, Playwright smoke tests, API integration tests, and full scripts/check.py passed. scripts/check.py needed a per-process init.defaultBranch=master override for one pre-existing fixture that assumes that default; repository settings were not changed. Real Entra app registration, SQL deployment and live identity are intentionally not configured in this task.

Independent read-only review found and drove two fixes: SQL ticket creation now checks the INSERT OUTPUT recordset after cleanup instead of the cleanup-sensitive rowsAffected[0], and MSAL token expiry now triggers silent renewal; failed renewal clears the confirmed workspace session and requires sign-in. Added a synthetic timed expiry test. Reviewer rechecked both fixes and reported no remaining blocker; SQL behavior has no live database integration test because this task intentionally uses synthetic identities and no deployed database.
<!-- SECTION:NOTES:END -->
