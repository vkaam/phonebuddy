---
id: TASK-119
title: Issue 152 - Package the PhoneBuddy API as a release image
status: To Do
assignee: []
created_date: '2026-11-22T09:30:00Z'
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
- [ ] #1 The API has a container image definition that listens on the ingress port, runs as non-root and holds no secret
- [ ] #2 CI builds the API image on main and the release workflow promotes it by digest to the dev registry like the release-test image
- [ ] #3 The release-test readiness and health-gate checks still pass or are replaced by API readiness checks of equal strictness
- [ ] #4 Unit tests or policy tests cover the new image build and promotion rules
<!-- AC:END -->
