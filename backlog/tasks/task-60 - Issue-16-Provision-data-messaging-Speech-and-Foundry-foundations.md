---
id: TASK-60
title: Issue 16 - Provision data messaging Speech and Foundry foundations
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-03T20:54:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-57
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/16
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - infra/environments/prod.bicepparam
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
  - infra/modules/data-platform.bicep
  - scripts/azure_foundations_smoke.py
  - infra/README.md
modified_files:
  - >-
    backlog/tasks/task-60 -
    Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md
  - infra/modules/data-platform.bicep
  - infra/main.bicep
  - infra/environments/dev.bicepparam
  - infra/environments/test.bicepparam
  - infra/environments/prod.bicepparam
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - scripts/azure_foundations_smoke.py
  - infra/README.md
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/16
Approved revision: 2026-11-01T09:24:52Z; body SHA-256 3e38abfd66622238c1dbb33b2da50562ba17ec079d6c80dc047082bf79ef565d.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-16-1-product-service-foundations
Scope: infra/**; scripts/**; tests/**; docs/azure-delivery-policy.md; docs/quality-and-delivery.md; backlog/tasks/task-60 - Issue-16-Provision-data-messaging-Speech-and-Foundry-foundations.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py. In authorized test environments, run synthetic authorized/denied data-plane, queue dead-letter, Speech auth and Foundry inference checks; record quota, model, geography, retention and backup evidence. No production data is used.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bicep provisions SQL, blob storage, Service Bus, Speech and Foundry project/model resources with environment-specific retention and capacity.
- [ ] #2 Quota, model lifecycle and processing geography are validated; unavailable configurations fail without cross-geography fallback.
- [ ] #3 Synthetic checks prove authorized data-plane access and denial of unauthorized access, queue dead-letter behavior, Speech authentication and Foundry inference.
- [ ] #4 Backup, deletion and secret-handling requirements are documented and validated where applicable.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the existing Bicep foundation, environment parameters, validation scripts, tests and delivery guidance; confirm exact Azure resource and API contracts from primary documentation.
2. Add environment-scoped SQL, blob storage, Service Bus, Speech and Foundry project/model resources with explicit capacity, retention, identity and geography settings; reject unavailable or unresolved configurations without cross-geography fallback.
3. Extend deterministic preflight checks and focused tests for resource contracts, quota/model/geography failures, secret-safe outputs and environment isolation.
4. Add synthetic nonproduction probes for authorized and denied data access, queue dead-lettering, Speech authentication and Foundry inference; document backup, deletion and secret-handling evidence.
5. Run the required repository and Bicep checks, then gather authorized current-source Azure evidence where available; keep acceptance unchecked while any required external gate is unverified.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Local verification on current source:
- `python3 -B scripts/check.py` passed; report: `/private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-k74s3q7c/report.json`. This includes the complete required Python suite, web audit, lint, tests, browser smoke and build.
- `DOTNET_BUNDLE_EXTRACT_BASE_DIR=/private/tmp/bicep-extract BICEP=/private/tmp/phonebuddy-azure-cli/bin/bicep python3 -B scripts/check_bicep.py` passed with Bicep CLI 0.34.44.
- `git diff --check` passed.
- Focused `python3 -B -m unittest tests.test_bicep_preflight -v` passed (22 tests).

External acceptance remains open: no authorized Azure deployment, live model quota preflight, data-plane smoke, or backup/restore/deletion exercise was run. The SQL Entra admin parameters and prod environment inputs remain UNRESOLVED. No acceptance criterion is checked until these current-source gates have evidence. Do not deploy or delete resources without separate authorization.
<!-- SECTION:NOTES:END -->
