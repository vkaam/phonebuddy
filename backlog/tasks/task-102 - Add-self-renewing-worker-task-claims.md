---
id: TASK-102
title: Add self-renewing worker task claims
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-14T11:49:00Z'
updated_date: '2026-11-14T14:03:00Z'
labels: []
dependencies:
  - TASK-101
references:
  - https://github.com/vkaam/phonebuddy/issues/129
  - scripts/task_lease.py
  - docs/factory-leases.md
  - scripts/worker_lease.py
modified_files:
  - scripts/worker_lease.py
  - tests/test_worker_lease.py
  - docs/factory-leases.md
priority: high
type: feature
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/129
Approved requirements revision: 2026-11-14T11:48:03Z; SHA-256 b5efcdcec78ebcb5d9e173d9642832b467e11ccd3a6d8f873118e3c58b7e475e
Approval evidence: owner approved worker-held self-renewing leases and cooperative fail-closed behavior in Codex on 2026-11-14.
Branch: agent/gh-129-1-worker-leases
Scope: scripts/task_lease.py; scripts/worker_lease.py; tests/test_task_lease.py; tests/test_worker_lease.py; docs/factory-leases.md; this task record only
Verify: python3 -B -m unittest tests.test_task_lease tests.test_worker_lease; python3 -B scripts/check.py; git diff --check
Depends on merged and completed TASK-101. Worker-held claims are cooperative and do not fence a stale worker with independent GitHub credentials. Trusted publication remains separate work under issue 127.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A worker acquires a task-specific Blob lease before task work; a competing claimant is rejected while it remains active.
- [ ] #2 The worker renews throughout execution, releases on clean completion or shutdown, and stops task work and publishing when ownership is lost or uncertain.
- [ ] #3 After expiry, a replacement can acquire the task and must reconcile existing task, branch and PR state before resuming; retry and interruption fail closed.
- [ ] #4 Automated tests cover contention, renewal failure, release, expiry and recovery, and operating documentation explains credentials, renewal, takeover and the cooperative enforcement limitation.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Build a worker command wrapper that acquires the task lease and performs live task, branch and PR reconciliation before starting work.
2. Renew in the background and stop the child process group on lease loss, uncertainty or shutdown; release on clean exit.
3. Add failure, contention, takeover and process lifecycle tests and document authentication and cooperative limits.
4. Run required checks, publish and obtain independent review.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Draft task-record PR: https://github.com/vkaam/phonebuddy/pull/130. TASK-101 is In Progress in PR 128 and is not yet on main; do not claim TASK-102 until its dependency is merged and finalized.

PR 130 was closed temporarily because the repository-wide audit rejects an open implementation PR with an unclaimed To Do task and TASK-101 is absent from main. Reopen after TASK-101 is merged and finalized, when this task can be claimed. The task record is preserved on its feature branch.

TASK-101 merged and reached Done on main in PR 128. Task intake is being published on separate triage branch triage/gh-129-task-102; the reserved implementation branch remains agent/gh-129-1-worker-leases. The old task-record PR 130 remains closed. Before implementation, fetch main and rerun the live claim verification and applicable lease requirements.

TASK-102 acquired an exclusive Blob lease; live claim guard passed with claim_verified true on the synchronized branch.

Independent review of the initial wrapper identified cleanup, bounded-preflight, split-namespace, branch recheck and loss/shutdown edge cases. The implementation was revised to fail closed, terminate and verify the process group, bind to the approved storage namespace, bound preflight and recheck the branch. Final committed-head review remains required.

Live Azure verification on the reserved synthetic task confirmed that an unknown task is rejected before the worker runs, and that the supervisor renews and releases a real Blob lease around a harmless command. Independent review findings have been addressed in scope; final-head independent review remains pending.
<!-- SECTION:NOTES:END -->
