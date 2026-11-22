---
id: TASK-125
title: Issue 152 - Run the API in the dev Container App through the release pipeline
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-22T09:34:00Z'
updated_date: '2026-11-22T09:54:00Z'
labels:
  - task
dependencies: []
priority: high
ordinal: 103000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-hosting
Scope: infra/hosting.bicep; infra/main.bicep; infra/release-schema.json; infra/environments/dev.bicepparam; .github/workflows/ci.yml; .github/workflows/azure-deploy.yml; scripts/**; tests/**
Verify: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py; BICEP=bicep python3 -B scripts/check_bicep.py

Merged API changes must reach dev through the normal release, as the web app does. Today CI builds only infra/release-test and the Container App passes only RELEASE_VERSION. Follows the contract in the sibling task Issue 152 - Package the PhoneBuddy API as a releasable container image (image from services/api/Dockerfile, port 8080, /ready, env var names). Entra IDs and the web origin are public values supplied as Actions Variables or Bicep parameters, never secrets. Live proof is a separate follow-up task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 CI builds the API image from services/api and the release workflow promotes it by digest the way it promotes the stand-in today
- [ ] #2 hosting.bicep runs the API image on target port 8080 over HTTPS-only ingress with the contract environment variables, WEB_ORIGIN set to the dev Static Web App origin, and no secret values
- [ ] #3 Existing health-gate, rollback and what-if tests still pass and new tests cover the added settings
- [ ] #4 Placeholder or missing Entra and SQL settings fail the release preflight with a clear message instead of deploying a broken API
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Merge origin/main; reconcile Backlog records.
2. Make api_settings preflight require the full <name>.database.windows.net host to match the API config.
3. Confirm Bicep /ready probe and health gate agree with the API contract (GET / and /ready, health_request logs).
4. Run quality, required unittests and check_bicep; open draft PR.
<!-- SECTION:PLAN:END -->
