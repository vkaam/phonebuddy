---
id: TASK-109
title: Publish public runtime auth config with dev web releases
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-16T21:06:00Z'
updated_date: '2026-11-16T21:30:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/137
  - apps/web/src/config.js
  - .github/workflows/azure-deploy.yml
  - .github/workflows/ci.yml
  - apps/web/scripts/generate-public-config.mjs
  - apps/web/tests/config-generation.test.mjs
  - apps/web/README.md
  - docs/azure-delivery-policy.md
modified_files:
  - >-
    backlog/tasks/task-109 -
    Publish-public-runtime-auth-config-with-dev-web-releases.md
  - apps/web/scripts/generate-public-config.mjs
  - apps/web/tests/config-generation.test.mjs
  - .github/workflows/ci.yml
  - apps/web/README.md
  - docs/azure-delivery-policy.md
priority: high
type: feature
ordinal: 95000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Problem: The web app reads /config.json, but the trusted release artifact does not generate or include it. The local config is ignored and cannot configure hosted instances.

Issue: https://github.com/vkaam/phonebuddy/issues/137
Approved requirements revision: updated 2026-11-16T20:56:49Z; SHA-256 6dd2cb6c26ccdb6ee18639eaf1c09f32cc0a145e1c73ee388040b9d849c62e3d.
Approval: Owner @vkaam approved the intent in issue #137 and directly instructed implementation in this Codex conversation, supplying the local public config values and dev Static Web App URL.

Branch: agent/gh-137-1-publish-public-runtime-auth-config
Scope: .github/workflows/azure-deploy.yml; .github/workflows/ci.yml; apps/web/**; scripts/**; docs/azure-delivery-policy.md; backlog/tasks/task-109 - Publish-public-runtime-auth-config-with-dev-web-releases.md
Scope amendment rule: Paths outside this list require a triage amendment before changes.

Verify: npm ci --prefix apps/web; npm test --prefix apps/web; npm run lint --prefix apps/web; python3 -B scripts/check.py; after an authorized main-branch release, validate the published dev /config.json over HTTPS or record why the endpoint is unavailable.

Spec: Generate and publish only validated public runtime settings for the dev Static Web App. Do not hardcode or invent an API endpoint. When required settings are missing or invalid, publish no config and preserve the web app's unconfigured behavior. Keep environment values separate and never expose credentials, tokens, client secrets, or API keys. The supplied localhost API URL is for local development; hosted config requires a real dev API HTTPS URL.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A configured dev release serves a valid /config.json at the site root with the dev API HTTPS URL, tenant ID, SPA client ID, and API scope.
- [ ] #2 If required API URL or identity settings are absent or invalid, the release does not publish a fabricated or malformed config and the shell keeps its clear unconfigured behavior.
- [ ] #3 The generated runtime configuration contains only public settings and no credentials, client secrets, tokens, or API keys.
- [ ] #4 Automated checks cover config generation and validation, and deployment documentation explains how dev values are supplied and how other environments stay separate.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Trace how CI builds and packages the immutable frontend artifact and how the dev Static Web App deploy consumes it.
2. Add a fail-closed runtime-config generation/validation step using public environment-specific values; omit /config.json when required values are absent or invalid, and never synthesize an API URL.
3. Wire the dev release and automated tests so valid configured values produce the root config, while missing, malformed, localhost-hosted, or secret-bearing values do not publish one.
4. Document dev value provisioning and environment separation, run the recorded checks, and verify the hosted dev config only if a real HTTPS API endpoint and authorized release are available.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented fail-closed generation from public dev Actions Variables and included root config.json in the immutable CI web artifact when all values validate. Added coverage for valid, missing, malformed URL, invalid Entra/scope, stale file removal, and public-field allow-list behavior; documented local versus dev values and environment separation.

Verification: focused generator tests passed (5/5); full web Node tests passed (16/16) after production-only dependency install; web lint passed using the already-installed pinned Biome binary; actionlint passed for ci.yml; node --check passed for both new JS files; scripts/quality.py passed; required Python unit tests passed (215/215) on retry. Full npm ci failed with ENOSPC; python scripts/check.py also failed while writing its report after ENOSPC. The partial install and task-generated temp bundle were removed.

Hosted /config.json remains unverified: the supplied localhost API URL is invalid for hosting, and no separate dev API HTTPS origin has been supplied. The workflow therefore omits config until all four public Actions Variables are configured with valid dev values; no endpoint was invented.,

Final web suite rerun after the last test expansion passed 17/17. The current dev host GET https://thankful-wave-01ad93d0f.3.azurestaticapps.net/config.json returned Azure Static Web Apps 404. Groma reports no architecture owner for the changed CI, generator, and test files; no architecture map edits were needed.

Draft PR: https://github.com/vkaam/phonebuddy/pull/139 (Refs #137). PR head 0c226fd52b9105c031ad746ca4b2cdce34514487. Repository-wide Backlog audit passed; Quality and Build immutable release image jobs passed. The PR event intentionally skipped main-push-only web build/test steps, so the final web suite was verified locally at 17/17. Hosted config remains blocked by the current /config.json 404 and the missing real dev API HTTPS origin.
<!-- SECTION:NOTES:END -->
