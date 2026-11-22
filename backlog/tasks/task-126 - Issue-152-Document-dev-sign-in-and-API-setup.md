---
id: TASK-126
title: Issue 152 - Document dev sign-in and API setup
status: Done
assignee:
  - '@claude'
created_date: '2026-11-22T09:34:00Z'
updated_date: '2026-11-22T09:44:00Z'
labels:
  - docs
dependencies: []
priority: high
ordinal: 104000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-runbook
Scope: docs/dev-sign-in-runbook.md; docs/azure-delivery-policy.md; services/api/README.md; apps/web/README.md
Verify: python3 -B scripts/quality.py

Issue 152 requires the dev sign-in and API setup to be recreatable from documented steps, separate from test and production, with no secret published or committed. Owner decisions are still open: which accounts may sign in to dev, and whether Entra app registrations are made by the deployment or by hand by the owner. The runbook assumes by hand by the owner and says so, because the deployment identity may lack directory permissions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Runbook lists the API and SPA Entra app registrations to create in the nonproduction tenant: exposed scope, redirect URI for the dev Static Web App origin, and the values that become public Actions Variables
- [x] #2 Runbook explains how to grant a pilot user an organization membership row and what a user without one sees
- [x] #3 Runbook states the dev, test and production separation and that no secret or token is committed or published
- [x] #4 Open owner decisions are listed explicitly in the runbook
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Merge origin/main into the runbook branch and rerun python3 -B scripts/quality.py. 2. Open draft PR. 3. Check each acceptance criterion against docs/dev-sign-in-runbook.md sections, write final summary, set Done. 4. Independent review follows.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added docs/dev-sign-in-runbook.md covering the API and SPA Entra app registrations (scope, redirect URI, public Actions Variables), granting a pilot user a membership row, what a user without one sees, dev/test/production separation with no secrets committed, and the open owner decisions; linked it from the azure delivery policy and the API and web READMEs. Verified: python3 -B scripts/quality.py passes after merging origin/main; each criterion read against the runbook sections. Limitations: docs only, nothing proven live; owner decisions on dev accounts, app-registration ownership, membership SQL identity and API origin remain open.
<!-- SECTION:FINAL_SUMMARY:END -->
