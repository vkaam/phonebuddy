---
id: TASK-122
title: Issue 152 - Document dev sign-in recreation and seed invited dev memberships
status: To Do
assignee: []
created_date: '2026-11-22T09:31:00Z'
labels: []
dependencies:
  - TASK-121
priority: medium
ordinal: 105000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-4-dev-runbook-memberships
Scope: docs/**; apps/web/README.md; services/api/README.md; services/api/migrations/**; scripts/**; tests/**
Verify: python3 -B scripts/check.py; python3 -B scripts/run_required_unittests.py; npm --prefix services/api test

The owner decided on 2026-11-22 that only the owner and invited guests may sign in to dev. A signed-in user without an active membership must be told they have no access, and memberships may only be created by an authorized provisioning process. Someone else must be able to rebuild the dev sign-in and API setup from written steps.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A runbook covers inviting a guest to the nonproduction tenant, adding or deactivating their dev membership row through the provisioning path, and recreating dev sign-in and the API from scratch
- [ ] #2 The runbook and examples contain no secret, token or real credential and keep dev separate from test and prod
- [ ] #3 A test shows a signed-in user without an active membership is denied by the API and the web app shows a no-access message
<!-- AC:END -->
