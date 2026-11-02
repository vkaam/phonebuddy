---
id: TASK-65
title: Issue 21 - Provision SIP gateway and TURN infrastructure with Bicep
status: To Do
assignee: []
created_date: '2026-11-02T16:36:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-57
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/21
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
- [ ] #1 Bicep provisions gateway/relay compute, fixed addressing, bounded media ports, DNS/certificate prerequisites and private administration paths.
- [ ] #2 Gateway software/configuration are reproducible and versioned; provider secrets stay server-side and controlled tests do not require Fonzer.
- [ ] #3 A synthetic browser-to-SIP call verifies both media directions, forced TURN, TLS and restricted management access.
- [ ] #4 Updates drain new calls; active-call limitations and compatible image/configuration rollback are documented and tested.
<!-- AC:END -->
