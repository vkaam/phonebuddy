---
id: TASK-123
title: Issue 152 - Prove dev sign-in and API through the hosted release
status: To Do
assignee: []
created_date: '2026-11-22T09:31:00Z'
labels: []
dependencies:
  - TASK-120
  - TASK-121
  - TASK-122
priority: high
ordinal: 106000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-5-dev-live-proof
Scope: docs/azure-delivery-policy.md; apps/web/README.md
Verify: after an authorized main release, sign in at the dev Static Web App as a member and as a non-member, sign out, and call the API over HTTPS with a valid token, a wrong-audience token and a disallowed Origin; record the results.

Split from the pre-merge tasks on 2026-11-22: these criteria need the live dev environment, which cannot be checked before merge. It also supplies the dev API address and sign-in values TASK-114 needs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A member signs in at the hosted dev app, reaches the workspace, signs out, and an expired session returns to the signed-out state
- [ ] #2 A signed-in user without membership sees the no-access message
- [ ] #3 The dev API answers over HTTPS, rejects a token issued for another audience, and rejects a browser request from another origin
- [ ] #4 A merged API change reaches dev through the normal release with the new revision active
- [ ] #5 Evidence names the release run and records no secret
<!-- AC:END -->
