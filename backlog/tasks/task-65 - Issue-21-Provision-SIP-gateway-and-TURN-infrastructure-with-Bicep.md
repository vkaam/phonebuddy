---
id: TASK-65
title: Issue 21 - Provision SIP gateway and TURN infrastructure with Bicep
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-12T20:38:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-57
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/21
  - infra/hosting.bicep
  - infra/README.md
  - docs/software-plan.md
  - docs/azure-delivery-policy.md
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - infra/gateway/render_config.py
  - tests/test_gateway_config.py
  - infra/gateway/README.md
  - infra/media.bicep
  - infra/gateway/coturn/turnserver.conf.template
  - infra/gateway/asterisk/pjsip.conf.template
modified_files:
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
priority: high
type: task
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/21
Approved revision: 2026-11-01T09:25:03Z; body SHA-256 ce52d049e93c960089fa57f47be9240faeeca3b8bf63a7aa3aac26be1107c638.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-21-1-sip-turn-infrastructure
Scope: infra/**; apps/**; scripts/**; tests/**; docs/quality-and-delivery.md; docs/azure-delivery-policy.md; backlog/tasks/task-65 - Issue-21-Provision-SIP-gateway-and-TURN-infrastructure-with-Bicep.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py. In the authorized pilot environment, synthetic browser-to-SIP tests verify both media directions, forced TURN, TLS, restricted management and graceful update behavior; no provider secrets are committed.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Bicep provisions gateway/relay compute, fixed addressing, bounded media ports, DNS/certificate prerequisites and private administration paths.
- [ ] #2 Gateway software/configuration are reproducible and versioned; provider secrets stay server-side and controlled tests do not require Fonzer.
- [ ] #3 A synthetic browser-to-SIP call verifies both media directions, forced TURN, TLS and restricted management access.
- [ ] #4 Updates drain new calls; active-call limitations and compatible image/configuration rollback are documented and tested.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend the resource-group Bicep with opt-in media capacity: a fixed public gateway IP, bounded SIP/WebRTC/TURN media ports, private-only control/management, and reproducible versioned VM image inputs consistent with docs/software-plan.md. 2. Add versioned Asterisk and coturn configuration with safe server-side secret injection, TLS/DNS inputs, and documented drain/update/rollback behavior. 3. Extend deterministic Bicep validation and security-focused tests for ports, private access, image pinning, secret handling, and deployment opt-in. 4. Document prerequisites and exact local/hosted/controlled-call verification without claiming unperformed Azure evidence. 5. Run task verification commands, record evidence and remaining external gates, then publish one PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented opt-in media networking and VM resources, static IPs, a narrow inbound port set, egress allowlist, Bastion-only SSH, exact Compute Gallery version selection, versioned Asterisk/coturn configuration templates, and owner-only runtime secret rendering. Added Bicep contract checks and renderer/security tests. Verification passed: python3 -B scripts/check.py; python3 -B scripts/run_required_unittests.py (89 tests); BICEP=/private/tmp/phonebuddy-task65-azure/bin/bicep with DOTNET_BUNDLE_EXTRACT_BASE_DIR=/private/tmp/phonebuddy-task65-bicep-extract python3 -B scripts/check_bicep.py. The full local quality bundle passed after network and loopback access were enabled. No image build pipeline or Azure deployment was performed; live forced-TURN browser call, image provenance, and update/drain/rollback exercise remain unverified acceptance gates.

Final-source verification rerun passed: python3 -B scripts/check.py (Local baseline: pass) and BICEP=/private/tmp/phonebuddy-task65-azure/bin/bicep DOTNET_BUNDLE_EXTRACT_BASE_DIR=/private/tmp/phonebuddy-task65-bicep-extract python3 -B scripts/check_bicep.py (Bicep baseline checks passed). git diff --check passed. origin/main was fetched and is an ancestor of this branch. Acceptance criteria 2-4 remain open pending reproducible image build provenance and authorized Azure deployment, forced-TURN synthetic call, and update/drain/rollback exercise.

Published draft PR: https://github.com/vkaam/phonebuddy/pull/83 (Refs #21). GitHub CI Quality job passed on head f46cc520142e73c31fe3c27cc75171776e466323, including repository/policy checks, web build/tests, Bicep validation and history secret scan. PR remains draft and TASK-65 remains In Progress because live acceptance gates are outstanding.

Final PR-head verification passed on fb5ac173c9733a0cb53212bf0bc5c2d75c49a276: GitHub Quality and advisory Risk report checks both completed successfully. Criterion 1 is evidenced by successful Bicep build plus automated contract checks for opt-in deployment, fixed IPs, bounded inbound/outbound media ports, Bastion-only SSH, pinned Gallery image version and secret-free outputs. Criteria 2-4 remain unchecked because there is no image build/provenance pipeline or authorized live Azure environment evidence for call, drain, update and rollback behavior.
<!-- SECTION:NOTES:END -->
