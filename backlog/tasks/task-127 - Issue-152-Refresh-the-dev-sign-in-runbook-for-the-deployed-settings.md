---
id: TASK-127
title: Issue 152 - Refresh the dev sign-in runbook for the deployed settings
status: Done
assignee:
  - '@claude'
created_date: '2026-11-22T13:14:00Z'
updated_date: '2026-11-22T13:14:00Z'
labels:
  - docs
dependencies: []
priority: medium
ordinal: 107000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-runbook-refresh
Scope: docs/dev-sign-in-runbook.md
Verify: python3 -B scripts/quality.py

The runbook merged in TASK-126 predates the owner decisions of 2026-11-22 and the merged API pipeline: it lists settled decisions as open, says only four variables exist, and tells the reader to set API settings on the dev API by hand. The release now deploys them from Actions Variables and the web values must be repository-level. Without this, setting up dev from the runbook fails at the settings preflight or leaves the site unconfigured. It also ships a new main commit so the web config built from the now-set API address reaches dev. Remaining guest-invitation and SQL-grant steps stay with TASK-122 and TASK-120.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The runbook records the decided owner decisions and keeps the SQL-identity and guest-provisioning questions open
- [x] #2 The runbook lists every Actions Variable the web build and the release need, where each must be set, and that WEB_ORIGIN comes from the template
- [x] #3 The runbook states that the web config needs a new main commit and that rerunning CI for the same commit is refused
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Rewrote the owner-decisions section of docs/dev-sign-in-runbook.md (decided 2026-11-22: owner and invited guests only; the deployment will create the registrations, hand creation until TASK-121 lands; SQL identity and guest provisioning still open), replaced section 4 with the variable-to-setting table the release deploys from (five variables, repository or dev environment, WEB_ORIGIN from the template, preflight and GUID rules), required the four web variables at repository level, and documented that the web config needs a new main commit because a CI rerun for the same commit is refused. Verified: python3 -B scripts/quality.py passes; statements checked against the workflows (ci.yml has no environment, azure-deploy.yml runs in dev), scripts/api_settings.py, and the live dev release run. Not covered: guest invitation steps and the SQL grant (TASK-122, TASK-120); no live sign-in proof (TASK-123).
<!-- SECTION:FINAL_SUMMARY:END -->
