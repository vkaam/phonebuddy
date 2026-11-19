---
id: TASK-109
title: Publish public runtime auth config with dev web releases
status: Done
assignee:
  - '@codex'
created_date: '2026-11-16T21:06:00Z'
updated_date: '2026-11-19T04:16:00Z'
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
- [x] #1 The generated runtime configuration contains only public settings and no credentials, client secrets, tokens, or API keys.
- [x] #2 Automated checks cover config generation and validation, and deployment documentation explains how dev values are supplied and how other environments stay separate.
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
Implemented fail-closed generation of a root config.json from the four public dev Actions Variables and wired it into the exact-source CI frontend build before archive checksumming. Missing or invalid values remove any stale output. Added automated coverage for valid values, absent/invalid settings, HTTPS-only hosted URLs, identity and scope validation, stale-file removal, and the allow-listed public fields. Updated web and Azure delivery documentation for local config, dev variable names, and environment separation.

Verification: final web suite 17/17 passed using a temporary production-only install; lint passed using the existing pinned Biome binary; node --check and real CLI configured/unconfigured cases passed; actionlint and scripts/quality.py passed; Python unit tests 215/215 passed on retry. Full npm ci and scripts/check.py could not complete because the host ran out of disk space (ENOSPC); task-generated partial installs and temp output were removed. PR CI Quality and repository-wide audit passed; PR-only CI intentionally skipped main-push web build/test steps.

Acceptance evidence: AC #3 and #4 are verified. AC #1 remains unverified and AC #2 is not fully checked because the hosted application has not been rebuilt. A read-only request to the supplied dev host returned 404 for /config.json. The supplied API URL is localhost-only, and no separate dev API HTTPS origin exists in the supplied configuration; the workflow safely leaves the site unconfigured until valid public variables are supplied.

Draft PR: https://github.com/vkaam/phonebuddy/pull/139 (Refs #137). Keep TASK-109 active until a real dev API HTTPS origin is available and the authorized main release serves the validated config.,

Reconciled 2026-11-19: criteria 1 (configured release serves /config.json) and 2 (absent or invalid settings publish no config) need a real dev API HTTPS origin and a configured release, so they moved to follow-up TASK-114 under issue #137. The remaining criteria were verified before PR #139 merged on 2026-11-17.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added fail-closed generation of a root config.json from the four public dev Actions Variables in the exact-source CI frontend build, with tests for valid, absent and invalid values and documentation of how dev values are supplied and environments stay separate. Merged in PR #139 on 2026-11-17. Live proof that a configured release serves the config, and that an unconfigured release publishes none, is tracked in TASK-114.
<!-- SECTION:FINAL_SUMMARY:END -->
