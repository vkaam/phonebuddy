---
id: TASK-124
title: Issue 152 - Package the PhoneBuddy API as a releasable container image
status: To Do
assignee: []
created_date: '2026-11-22T09:34:00Z'
labels:
  - task
dependencies: []
priority: high
ordinal: 102000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-api-image
Scope: services/api/**; docs/api-container-contract.md
Verify: npm test --prefix services/api; python3 -B scripts/quality.py

The dev Container App only runs the release-test stand-in, so signed-in features cannot be tried in hosted dev. The API must be packaged as a non-root container that the existing release gate can treat like the stand-in. Shared contract for sibling tasks: image listens on PORT 8080; GET /ready returns {"version": RELEASE_VERSION, "ready": true}; each /ready or /health request logs one JSON line {"event":"health_request","version","status","duration_ms"} with no request data; settings come only from env vars (ENTRA_TENANT_ID, ENTRA_API_CLIENT_ID, WEB_ORIGIN, SQL_SERVER, SQL_DATABASE, SQL_MANAGED_IDENTITY_CLIENT_ID, RELEASE_VERSION); no secrets.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 services/api/Dockerfile builds a pinned-base, non-root image that starts the compiled API on port 8080
- [ ] #2 GET /ready answers without authentication with the release version and emits the health_request log line, covered by a test
- [ ] #3 The API accepts only tokens issued for it and browser requests only from the configured WEB_ORIGIN, covered by existing or new tests
- [ ] #4 docs/api-container-contract.md records the image, port, endpoint, log and environment-variable contract
<!-- AC:END -->
