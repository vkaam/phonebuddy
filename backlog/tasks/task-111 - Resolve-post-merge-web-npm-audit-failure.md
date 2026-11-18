---
id: TASK-111
title: Resolve post-merge web npm audit failure
status: To Do
assignee: []
created_date: '2026-11-18T05:54:00Z'
updated_date: '2026-11-18T05:56:00Z'
labels:
  - web
  - cicd
  - security
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/140
modified_files:
  - backlog/tasks/task-111 - Resolve-post-merge-web-npm-audit-failure.md
priority: high
type: bug
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/140
Approved revision: 2026-11-18T05:19:30Z; SHA-256 2e6898d3978586f79b25d0d01edaf5f439f79f61607011ae01ed01b38051481d.
Approval evidence: owner reported the post-merge Quality failure and supplied the Actions job URL in this Codex conversation on 2026-11-18.
Branch: agent/gh-140-1-resolve-web-npm-audit
Scope: apps/web/package.json; apps/web/package-lock.json; this task's own CLI-managed record
Verify: (cd apps/web && npm ci --no-audit --no-fund && npm audit && npm run lint && npm test && npm run build && npx playwright install --only-shell chromium && npm run test:browser); hosted Quality on the final PR head

Keep the dependency audit enabled and preserve web app behavior. Do not apply an unreviewed breaking dependency downgrade.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The committed web lockfile installs cleanly and npm audit reports no vulnerabilities.
- [ ] #2 Web lint, unit tests, build, and browser smoke run and pass in hosted Quality on the final PR head.
- [ ] #3 The remediation preserves app behavior and does not weaken or skip dependency auditing.
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @codex
created: 2026-11-18T05:56:00Z

---

2026-11-18 implementation preflight is blocked before claim: the required live guard exited 1 with claim_verified=false and "A read-only GitHub connection is required." Project docs also state no trusted lease/publishing controller is configured. This task remains To Do; no application files were changed.

---
<!-- COMMENTS:END -->
