---
id: TASK-114
title: Verify hosted dev runtime config after a configured release
status: To Do
assignee: []
created_date: '2026-11-19T04:16:00Z'
updated_date: '2026-11-19T04:21:00Z'
labels: []
dependencies:
  - TASK-109
priority: high
type: task
ordinal: 97000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/137
Branch: agent/gh-137-2-verify-hosted-runtime-config
Scope: docs/azure-delivery-policy.md; apps/web/README.md
Verify: after an authorized main-branch release with the four public dev Actions Variables set, request https://<dev Static Web App host>/config.json and record the response; for the unconfigured case, record release evidence that no config.json was published and that the hosted shell shows its unconfigured state.

Split from TASK-109 on 2026-11-19 when its PR (#139) merged: these two criteria need live proof that was not available. TASK-109 built the fail-closed generator; on 2026-11-16 the supplied API URL was localhost-only, no dev API HTTPS origin existed, and /config.json returned 404 on the dev host. The generator has not shipped yet: the release for 7aff57a (run 44150139399) was skipped. This task needs a release, and a real dev API HTTPS origin for the configured case.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A configured dev release serves a valid /config.json at the site root with the dev API HTTPS URL, tenant ID, SPA client ID, and API scope.
- [ ] #2 If required API URL or identity settings are absent or invalid, the release does not publish a fabricated or malformed config and the shell keeps its clear unconfigured behavior.
<!-- AC:END -->
