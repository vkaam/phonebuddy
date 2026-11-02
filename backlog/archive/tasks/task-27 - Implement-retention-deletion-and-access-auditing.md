---
id: TASK-27
title: Implement retention, deletion and access auditing
status: To Do
assignee: []
created_date: '2026-10-29T20:07:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - privacy
  - backend
  - historical-import
  - needs-triage
dependencies:
  - TASK-23
  - TASK-25
  - TASK-26
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/32
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

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/32 (observed 2026-11-01T09:25:42Z; UTF-8 body SHA-256 8deb99a62bf0dd7a57446efd0cf5dc072b5c937d9766cd182bf5190f2ce6db56). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates.
<!-- SECTION:NOTES:END -->
