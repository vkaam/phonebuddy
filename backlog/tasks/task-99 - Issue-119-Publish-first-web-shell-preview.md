---
id: TASK-99
title: Issue 119 - Publish first web shell preview
status: Done
assignee:
  - '@codex'
created_date: '2026-11-13T09:09:00Z'
updated_date: '2026-11-13T09:20:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/119
  - apps/web/src/main.tsx
  - apps/web/src/config.js
  - apps/web/e2e/smoke.spec.js
  - apps/web/tests/config.test.mjs
  - apps/web/README.md
  - docs/azure-delivery-policy.md
  - https://github.com/vkaam/phonebuddy/pull/124
modified_files:
  - apps/web/src/main.tsx
  - apps/web/e2e/smoke.spec.js
  - apps/web/README.md
  - docs/azure-delivery-policy.md
priority: high
type: task
ordinal: 87000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Publish the existing shell as a dev-only preview without a fabricated API endpoint.

Issue: https://github.com/vkaam/phonebuddy/issues/119
Approved revision: 2026-11-12T20:47:51Z; body SHA-256 4d45fb1ac088a34f40568eb6bce74d83d83947df2bb264c41c8315cc52e5ce99.
Approval evidence: Issue records the owner’s 2026-11-12 direction to publish the first version; the user requested implementation on 2026-11-13 and waived the lease requirement.
Branch: agent/issue-119-first-web-release
Scope: apps/web/src/main.tsx; apps/web/src/config.js; apps/web/tests/config.test.mjs; apps/web/e2e/smoke.spec.js; apps/web/README.md; docs/azure-delivery-policy.md; backlog/tasks/task-99 - Issue-119-Publish-first-web-shell-preview.md
Verify: From apps/web run npm ci, npm test, npm run lint, npm run build, npm run test:browser; from repository root run python3 -B scripts/check.py. Verify hosted Quality and observe trusted dev release after merge.
Spec: Use the existing protected-main dev release path; no test or production deployment, secrets, or fake API endpoint.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The shell starts without an API endpoint, navigation works, and calling and backend integration are clearly unavailable with call controls disabled.
- [x] #2 Configuration remains public and secret-free, and the preview limitations and trusted dev release behavior are documented.
- [x] #3 Unit, browser, build, lint and repository checks pass, and the existing trusted main release workflow is configured to publish the built shell to dev.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Remove the startup dependency on API configuration and clearly label the disconnected preview. 2. Verify navigation, disabled controls and configuration-free startup in browser tests. 3. Document the existing trusted dev release path and preview limitations. 4. Run scoped checks, publish the PR and observe the protected-main release after merge.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Live claim check passed against origin/main 9c033af1ab3f9bf1928a1d67ffad00dcdfdc18ab on 2026-11-13; owner waived the durable lease for this request.

Implementation complete: no configuration fetch at startup; the shell labels calling and backend integration unavailable. Independent preliminary review found no code blockers and the reported documentation typo was corrected. Web unit, lint, build and browser tests pass; repository baseline passes with Homebrew Bash and init.defaultBranch=master (evidence phonebuddy-quality-p19ps_5f). Hosted checks, final-head review and live dev release remain pending.

Draft PR: https://github.com/vkaam/phonebuddy/pull/124. Hosted checks and final-head independent review are pending; live publication remains post-merge.

Triage clarification 2026-11-13: AC 3 evaluates the existing release workflow configuration before merge; issue 119 still requires actual HTTPS publication, which can only be observed after the protected-main merge. No issue requirement or file scope changed.

Independent agent review of 7577bc25 found no blocking findings; browser, unit, lint, build and full baseline passed independently (phonebuddy-quality-kzppmw8e). Hosted Quality and advisory checks passed at 7577bc25. Live HTTPS publication remains to be observed after merge.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Prepared the dev web preview to load without an API endpoint, identify unavailable calling and backend integration, and keep call controls disabled. Browser and local baseline checks passed; the existing source-bound dev release workflow was reviewed. Live deployment remains post-merge verification.
<!-- SECTION:FINAL_SUMMARY:END -->
