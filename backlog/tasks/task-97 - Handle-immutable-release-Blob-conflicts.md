---
id: TASK-97
title: Handle immutable release Blob conflicts
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-13T06:11:00Z'
updated_date: '2026-11-13T06:15:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/120
  - https://github.com/vkaam/phonebuddy/actions/runs/43305635770
  - scripts/release_recovery.py
  - tests/test_release_recovery.py
  - https://github.com/vkaam/phonebuddy/pull/121
modified_files:
  - scripts/release_recovery.py
  - .github/workflows/azure-deploy.yml
  - tests/test_release_recovery.py
  - tests/test_bicep_ci_boundary.py
priority: high
type: bug
ordinal: 85000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Main release attempt 3 failed at candidate persistence with HTTP 409 after the same immutable bundle was written before deployment. Preserve fail-closed immutability and first-release bootstrap.

Issue: https://github.com/vkaam/phonebuddy/issues/120
Approved revision: 2026-11-12T21:28:53Z; body SHA-256 ee276ba33da818a162271aa53ed685ec972c05ef292836e838612c188090f1be.
Approval evidence: The owner requested working automatic main-to-dev deployment and on 2026-11-13 approved a one-task lease exception and independent review for issue 120.
Branch: agent/gh-120-1-blob-conflict
Scope: scripts/release_recovery.py; tests/test_release_recovery.py; .github/workflows/azure-deploy.yml; tests/test_bicep_ci_boundary.py; backlog/tasks/task-97 - Handle-immutable-release-Blob-conflicts.md.
Verify: python3 -B -m unittest tests.test_release_recovery tests.test_bicep_ci_boundary; python3 -B scripts/check.py; hosted PR Quality; observe trusted main CI and dev release after merge.
Spec: Preserve conditional writes, reject differing content and unrelated conflicts, and do not bypass recovery safeguards.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Repeated immutable Blob writes accept existing identical content for the observed Azure conflict without overwriting it, including first-release bootstrap.
- [ ] #2 Differing content and unrelated Blob conflicts remain failures, with meaningful regression tests.
- [ ] #3 Required local checks and hosted PR checks pass; independent review covers the final change.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Identify the exact Azure conflict and distinguish existing blobs from other errors. 2. Make idempotent writes compare existing bytes without weakening conditional updates; avoid publishing an incomplete first-release manifest. 3. Add focused regression coverage, run required checks, obtain independent review and publish a PR. 4. After merge, observe the automatic main release and record its outcome.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Live claim check passed against main 7d46f867; the owner approved a one-task lease exception and independent review. Scoped tests passed (24); actionlint passed. Full local baseline passed at /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-wx04ql3d/report.json with modern Bash and temporary init.defaultBranch=master. Preliminary independent review found no code-level blockers; Azure 409 provider code remains unobserved and post-merge deployment must verify the fix.

Draft PR #121 published from db4c06f; hosted checks and final-head independent review pending.
<!-- SECTION:NOTES:END -->
