---
id: TASK-60
title: Issue 16 - Provision data messaging Speech and Foundry foundations
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
  - https://github.com/vkaam/phonebuddy/issues/16
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
