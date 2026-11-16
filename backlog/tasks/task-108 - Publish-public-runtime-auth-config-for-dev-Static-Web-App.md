---
id: TASK-108
title: Publish public runtime auth config for dev Static Web App
status: To Do
assignee: []
created_date: '2026-11-16T20:56:00Z'
updated_date: '2026-11-16T21:24:00Z'
labels:
  - web
  - cicd
  - auth
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/137
type: enhancement
ordinal: 95000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/137
Approved revision: 2026-11-16T20:53:48Z; SHA-256 6dd2cb6c26ccdb6ee18639eaf1c09f32cc0a145e1c73ee388040b9d849c62e3d.
Approval evidence: owner request in this conversation on 2026-11-16: “create a task for that gap,” referring to the missing deployed /config.json generation described immediately before the request. Issue #137 records that intent and its acceptance criteria.
Branch: agent/gh-137-1-public-runtime-config
Scope: .github/workflows/azure-deploy.yml; scripts/deployment_config.py; tests/test_deployment_config.py; apps/web/config.example.json; apps/web/README.md; this task's own CLI-managed record
Verify: python3 -B scripts/check.py; python3 -B scripts/run_required_unittests.py; (cd apps/web && npm ci --no-audit --no-fund && npm run lint && npm test && npm run build)

Keep this task limited to the dev Static Web App release. The product API URL may not yet be available; do not invent one. Preserve the existing safe, unconfigured shell behavior until valid dev API and identity settings are supplied.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Configured dev releases serve a valid root /config.json with the dev API HTTPS URL, tenant ID, SPA client ID, and API scope.
- [ ] #2 Missing or invalid settings never produce a fabricated or malformed config; the shell retains its clear unconfigured behavior.
- [ ] #3 Runtime config contains only public settings and no credentials, client secrets, tokens, or API keys.
- [ ] #4 Automated checks cover config generation and validation, and docs explain dev settings and environment separation.
<!-- AC:END -->
