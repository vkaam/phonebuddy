---
id: TASK-119
title: Issue 152 - Package the PhoneBuddy API as a release image
status: To Do
assignee: []
created_date: '2026-11-22T09:30:00Z'
updated_date: '2026-11-22T11:08:00Z'
labels: []
dependencies: []
priority: high
ordinal: 102000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-1-api-image
Scope: services/api/**; .github/workflows/ci.yml; .github/workflows/azure-deploy.yml; scripts/**; tests/**; docs/quality-and-delivery.md
Verify: npm --prefix services/api test; python3 -B scripts/check.py; python3 -B scripts/run_required_unittests.py

The dev Container App runs only the release-test image, so merged API changes cannot reach dev. CI already builds and the release workflow already promotes one image by digest; that path must carry the real API instead, so API changes ship the same way the web app does.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The API has a container image definition that listens on the ingress port, runs as non-root and holds no secret
- [ ] #2 CI builds the API image on main and the release workflow promotes it by digest to the dev registry like the release-test image
- [x] #3 The release-test readiness and health-gate checks still pass or are replaced by API readiness checks of equal strictness
- [ ] #4 Unit tests or policy tests cover the new image build and promotion rules
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reconciled 2026-11-22: TASK-124 (PRs #156, #157 for #152) delivered services/api/Dockerfile (digest-pinned, non-root, port 8080, no secret), GET / and GET /ready plus health_request logs, and CI now builds the API image under the retained release-test names. AC 1 and 3 have evidence: image built and run locally, scripts/health_gate.py check_response accepted both probes from the container, independent reviews recorded on #156. Still open: AC 2 (promotion by digest of the API image is unchanged code but never ran, because the main deploy stops at the API settings preflight until the PHONEBUDDY_DEV_* variables are set) and AC 4 (no test covers the image build step itself). Live proof belongs to TASK-123.
<!-- SECTION:NOTES:END -->
