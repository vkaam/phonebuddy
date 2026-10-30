---
id: TASK-5
title: Create modular Bicep baseline and environment parameters
status: In Progress
assignee:
  - '@codex'
created_date: '2026-10-29T20:04:00Z'
updated_date: '2026-10-30T13:35:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-4
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - docs/azure-delivery-policy.md
  - infra/main.bicep
  - https://github.com/vkaam/phonebuddy/pull/8
modified_files:
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - infra/environments/prod.bicepparam
  - scripts/check_bicep.py
  - infra/README.md
  - tests/test_bicep_preflight.py
priority: high
type: task
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Azure infrastructure needs reproducible environment-specific definitions before provisioning.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Pinned Bicep tooling builds and lints entry points and environment parameter files; invalid inputs fail.
- [ ] #2 Environment names, scopes and capacity are isolated with no secrets in source or outputs.
- [ ] #3 Disposable deployment and repeat deployment demonstrate reproducibility; bootstrap exceptions and protected-resource cleanup are documented.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Establish a minimal modular subscription-scoped Bicep baseline and isolated environment parameter files using the existing environment policy.
2. Pin tooling and provide repeatable local build, lint and invalid-input checks without credentials or secrets.
3. Document bootstrap, deployment, repeatability and protected-resource cleanup; run local verification and record any Azure deployment evidence blockers.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added subscription-scoped foundation module and per-environment parameters, pinned Bicep 0.34.44 local compiler checks, and documented deployment and cleanup prerequisites. Local compiler, lint, environment selection, and invalid-environment checks passed. Disposable and repeat deployment remain blocked: no designated subscription, Azure identity, approved region, owners or budgets are configured. No application capacity or isolation has yet been provisioned or validated.

Draft PR #8 depends on unmerged PR #7; Azure deployment evidence and environment isolation remain outstanding.

Added an opt-in deployment-readiness preflight that rejects unresolved owner and cost center values and verifies the selected environment; it must be wired into a trusted deployment pipeline before any deployment.

Region parameters now remain explicitly unresolved rather than suggesting an unapproved geography.

Verified pinned Bicep compilation and invalid environment handling; deployment-ready dev fails on unresolved location as intended. Preflight unit tests, local baseline and diff checks passed. Azure deployment and repeatability remain unverified.
<!-- SECTION:NOTES:END -->
