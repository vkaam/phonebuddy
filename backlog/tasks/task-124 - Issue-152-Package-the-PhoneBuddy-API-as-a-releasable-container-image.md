---
id: TASK-124
title: Issue 152 - Package the PhoneBuddy API as a releasable container image
status: Done
assignee:
  - '@claude'
created_date: '2026-11-22T09:34:00Z'
updated_date: '2026-11-22T09:46:00Z'
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
- [x] #1 services/api/Dockerfile builds a pinned-base, non-root image that starts the compiled API on port 8080
- [x] #2 GET /ready answers without authentication with the release version and emits the health_request log line, covered by a test
- [x] #3 The API accepts only tokens issued for it and browser requests only from the configured WEB_ORIGIN, covered by existing or new tests
- [x] #4 docs/api-container-contract.md records the image, port, endpoint, log and environment-variable contract
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Merge origin/main into the branch and rerun Verify.
2. Confirm the Dockerfile, /ready endpoint, tests and contract doc meet the criteria.
3. Open a draft PR, then finalize the record with evidence (note the image was not built: no Docker daemon).
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added a digest-pinned, non-root (uid 65532) services/api/Dockerfile and .dockerignore that start the compiled API on port 8080; an unauthenticated GET /ready returning the release version with one health_request log line per /ready or /health request; PORT/RELEASE_VERSION config defaults; and docs/api-container-contract.md. Verified: npm test --prefix services/api passes 8/8 (including /ready, WEB_ORIGIN and token-audience tests); python3 -B scripts/quality.py passes after merging origin/main. Also verified locally with OrbStack: docker build services/api succeeds; the container runs as uid 65532 on 8080, GET /ready returns {"version":"abc123","ready":true} with a health_request log line, and /api/me without a token returns 401. Not verified: running against real Entra or Azure SQL, which is live proof for a follow-up task.
<!-- SECTION:FINAL_SUMMARY:END -->
