---
id: TASK-101
title: Build Azure Blob task lease foundation
status: Done
assignee:
  - '@codex'
created_date: '2026-11-14T07:21:00Z'
updated_date: '2026-11-14T12:12:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/127
  - scripts/task_lease.py
  - infra/factory-leases.bicep
modified_files:
  - scripts/task_lease.py
  - infra/factory-leases.bicep
  - tests/test_task_lease.py
  - docs/factory-leases.md
priority: high
type: feature
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/127
Approved requirements revision: 2026-11-14T07:21:00Z; SHA-256 55fbd22115c1711e26e6bb9b49f094d20435aa1792cdd04e4034389b195b134e
Approval evidence: owner request in Codex on 2026-11-14 to build the system in a new Azure account and bootstrap without a lease.
Branch: agent/gh-127-1-blob-leases
Scope: scripts/task_lease.py; tests/test_task_lease.py; infra/factory-leases.bicep; docs/factory-leases.md; this task record only
Verify: python3 -B -m unittest tests.test_task_lease; python3 -B scripts/check.py; git diff --check
This task implements the storage and lease foundation; trusted publishing enforcement remains a separate required task before this may authorize autonomous execution.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A dedicated private storage account and container support identity-scoped task lease coordination without embedded credentials.
- [x] #2 Atomic task leases support contention, renewal, release, recovery after expiry, and durable increasing generations while failing closed on uncertain ownership.
- [x] #3 Tests cover contention, lease loss, expiry, generation persistence, and backend errors; operational documentation states setup and the limitations pending publishing enforcement.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Provision isolated coordination storage and scope data-plane access to a designated identity.
2. Implement atomic per-task lease lifecycle and persistent generations with fail-closed handling.
3. Test concurrency and failure cases and document operation and publishing limitations.
4. Run scoped verification and publish for independent review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Owner approved bootstrap without a lease. Live pre-claim audit passed. Nine focused tests pass and Bicep 0.48.1 compiles. No live Azure provisioning or integration test has run; subscription, resource group and coordinator identity remain to be selected. GitHub publishing fencing is a separate required slice.

Draft PR: https://github.com/vkaam/phonebuddy/pull/128. Full local baseline passed with modern Bash and init.defaultBranch override; Bicep 0.48.1 compiled. Hosted checks, independent review and live Azure validation remain pending.

Owner authorization 2026-11-14: use the Azure CLI selected subscription for the new dedicated storage account; choose an appropriate name. Planned external deployment: subscription 43c19721-4a1d-49ed-954b-5e8a29b346b1, resource group phonebuddy in Belgium Central, account pbphonebuddyleases, and a new dedicated managed coordinator identity. Live claim revalidated with claim_verified true. The coordinator identity does not by itself implement trusted publishing.

Azure deployment factory-lease-foundation succeeded in subscription 43c19721-4a1d-49ed-954b-5e8a29b346b1, phonebuddy, Belgium Central: account pbphonebuddyleases, private task-leases container, managed identity id-pb-factory-coordinator. Shared key and public blob access are disabled, HTTPS and TLS 1.2 required. A temporary container-scoped user role was removed and the remaining direct role assignment is the coordinator. Live tests using reserved TASK-999999999999999999 passed contention, renew, release, increasing generation, expiry and reacquisition. This revealed Azure BlobAlreadyExists HTTP 409, now handled and covered by regression tests. The reserved test blob must not be deleted or reused. Trusted publishing remains unimplemented; do not use as autonomous claim authorization.

Independent review at b5eafb8144e043329646da03ad566f22336569f6 identified a blocking deadline flaw: macOS monotonic time can stop during sleep. Updated deadlines to use macOS continuous time or Linux CLOCK_BOOTTIME, failing closed when unavailable; added sleep and clock regressions. Review and acceptance must be refreshed on the updated head.

Independent review at cfb220c5d769cf5efa604f7ae252365510f68d37 confirmed suspend handling but identified a second-clock-read failure path that left the handle valid. Fix moves the read into the invalidating guard and adds a regression; final-head review remains pending.

Independent agent review and scoped acceptance at 5cf0ea70b74586e8fc183fef75947d9f8a8c9a06: no blocking findings; 14 focused tests and diff check pass from an isolated archive. Reviewer independently confirmed live account settings and coordinator role; live lease operations were verified earlier and are recorded above. Review must be revalidated on the final task-record head.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added and deployed dedicated private Azure Blob lease storage and implemented fail-closed task lease acquisition, renewal, expiry handling and durable generations. Live contention and recovery tests, 14 focused tests, the full local baseline and hosted checks passed. A separate trusted publishing controller remains required for enforced GitHub fencing.
<!-- SECTION:FINAL_SUMMARY:END -->
