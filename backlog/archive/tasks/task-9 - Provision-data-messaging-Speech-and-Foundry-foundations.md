---
id: TASK-9
title: Provision data, messaging, Speech and Foundry foundations
status: To Do
assignee: []
created_date: '2026-10-29T20:04:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-6
  - TASK-8
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Durable call processing and Azure-hosted inference need separately verifiable infrastructure and identity access.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bicep provisions SQL, blob storage, Service Bus, Speech and Foundry project/model resources with environment-specific retention and capacity.
- [ ] #2 Quota, model lifecycle and processing geography are validated; unavailable configurations fail without cross-geography fallback.
- [ ] #3 Synthetic checks prove authorized data-plane access and denial of unauthorized access, queue dead-letter behavior, Speech authentication and Foundry inference.
- [ ] #4 Backup, deletion and secret-handling requirements are documented and validated where applicable.
<!-- AC:END -->
