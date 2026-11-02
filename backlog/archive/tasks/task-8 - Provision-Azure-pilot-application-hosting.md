---
id: TASK-8
title: Provision Azure pilot application hosting
status: To Do
assignee: []
created_date: '2026-10-29T20:04:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-6
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: task
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The first deployable environment needs hosting, networking and artifact storage before VoIP implementation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bicep provisions Container Apps environment, registry, Static Web App, Key Vault, identities and required networking.
- [ ] #2 A minimal version-identifying release-test workload is reachable and exposes readiness without secrets.
- [ ] #3 Runtime access is scoped, administration is restricted, and repeat deployment, cleanup boundaries and baseline cost are demonstrated.
<!-- AC:END -->
