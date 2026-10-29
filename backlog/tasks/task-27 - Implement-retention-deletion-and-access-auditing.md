---
id: TASK-27
title: Implement retention, deletion and access auditing
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
labels:
  - privacy
  - backend
dependencies:
  - TASK-23
  - TASK-25
  - TASK-26
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
priority: high
type: feature
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Call data and derived artifacts must follow organization policy, including asynchronous jobs and backups, before real pilot use.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Retention and authorized deletion cover transcripts, summaries, optional recordings and exports; tombstones prevent queued retries from recreating deleted content.
- [ ] #2 Access and policy-change audit events omit sensitive call content and credentials; protected artifacts cannot be accessed by another organization.
- [ ] #3 Tests cover deletion during processing and replay after restore; backup expiry, deletion reapplication and artifact retention are documented.
<!-- AC:END -->
