---
id: TASK-127
title: Issue 152 - Prove sign-in and the API on the hosted dev app
status: To Do
assignee: []
created_date: '2026-11-22T10:22:00Z'
labels:
  - task
dependencies:
  - TASK-125
  - TASK-126
priority: high
ordinal: 107000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-live-proof
Scope: docs/dev-sign-in-runbook.md; docs/azure-delivery-policy.md; docs/api-container-contract.md; scripts/**; tests/**
Verify: python3 -B scripts/quality.py

Issue 152 is complete only when a pilot user can sign in to the hosted dev app and reach the dev API. TASK-124, TASK-125 and TASK-126 delivered and locally verified the image, pipeline and runbook, but nothing was proven live: the dev deploy is blocked until the owner sets the five PHONEBUDDY_DEV_* Actions Variables, creates the Entra registrations and decides who may sign in (open decisions in docs/dev-sign-in-runbook.md). Unblocks #137 / TASK-114, which needs the dev API address and sign-in values. This is the post-merge live proof the factory workflow keeps separate from the delivery tasks. Doc or script fixes found while proving are in Scope; larger gaps become their own tasks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A release from main reaches dev with the API image active: the release gate and health check pass and the run is recorded
- [ ] #2 The dev API answers over HTTPS on /ready, rejects a token with the wrong audience, and rejects a browser Origin other than the dev web app
- [ ] #3 A pilot user with an organization membership signs in on the hosted dev app, reaches the workspace, and signing out and session expiry behave as they do locally
- [ ] #4 A signed-in user without a membership is shown the no-access message
- [ ] #5 The recorded steps match the runbook, with any correction made in the runbook, and no secret appears in the run logs or repository
<!-- AC:END -->
