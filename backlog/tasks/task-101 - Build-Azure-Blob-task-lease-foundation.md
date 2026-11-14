---
id: TASK-101
title: Build Azure Blob task lease foundation
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-14T07:21:00Z'
updated_date: '2026-11-14T07:28:00Z'
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
- [ ] #1 A dedicated private storage account and container support identity-scoped task lease coordination without embedded credentials.
- [ ] #2 Atomic task leases support contention, renewal, release, recovery after expiry, and durable increasing generations while failing closed on uncertain ownership.
- [ ] #3 Tests cover contention, lease loss, expiry, generation persistence, and backend errors; operational documentation states setup and the limitations pending publishing enforcement.
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
<!-- SECTION:NOTES:END -->
