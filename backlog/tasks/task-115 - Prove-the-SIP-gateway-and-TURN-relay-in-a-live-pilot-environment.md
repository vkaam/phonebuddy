---
id: TASK-115
title: Complete and prove the SIP gateway and TURN relay in a live pilot environment
status: To Do
assignee: []
created_date: '2026-11-19T04:16:00Z'
updated_date: '2026-11-19T04:21:00Z'
labels: []
dependencies:
  - TASK-65
priority: high
type: task
ordinal: 98000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/21
Branch: agent/gh-21-2-live-gateway-verification
Scope: infra/**; scripts/**; tests/**; .github/workflows/**; docs/quality-and-delivery.md; docs/azure-delivery-policy.md
Verify: python3 -B scripts/check.py; python3 -B scripts/check_bicep.py; in the authorized pilot environment, synthetic browser-to-SIP tests for both media directions, forced TURN, TLS, restricted management, drain and rollback, with retained evidence.

Split from TASK-65 on 2026-11-19 after its PR (#83) merged with only the Bicep provisioning criterion proven. The remaining criteria include build work (a reproducible, versioned gateway image with provenance, likely needing a workflow) as well as live proof in an authorized Azure environment, neither of which existed when TASK-65 merged. Split further at triage if it does not fit one reviewable PR.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Gateway software/configuration are reproducible and versioned; provider secrets stay server-side and controlled tests do not require Fonzer.
- [ ] #2 A synthetic browser-to-SIP call verifies both media directions, forced TURN, TLS and restricted management access.
- [ ] #3 Updates drain new calls; active-call limitations and compatible image/configuration rollback are documented and tested.
<!-- AC:END -->
