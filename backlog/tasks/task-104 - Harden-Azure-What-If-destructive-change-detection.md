---
id: TASK-104
title: Harden Azure What-If destructive change detection
status: To Do
assignee: []
created_date: '2026-11-15T18:58:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/132
  - scripts/release_recovery.py
  - scripts/check_bicep.py
priority: high
type: bug
ordinal: 92000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/132
Approved requirements revision: 2026-11-15T18:57:12Z; SHA-256 7efbd63e69e92da20b91a59ea6f5f1fb5dbd101923e73b8772cc6424055ce9e6
Approval evidence: owner explicitly approved independent later follow-up in Codex on 2026-11-15 and directed that it not block other tasks.
Branch: agent/gh-132-1-what-if-guard
Scope: scripts/release_recovery.py; scripts/check_bicep.py; tests/test_release_recovery.py; tests/test_bicep_preflight.py; docs/quality-and-delivery.md; this task record only
Verify: python3 -B -m unittest tests.test_release_recovery tests.test_bicep_preflight; python3 -B scripts/check.py; git diff --check
Independent later work; no dependency on TASK-63 and no task depends on this item.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Actual Azure What-If resource IDs identify SQL and Storage resources, including nested types and case variations; destructive property deletions are rejected.
- [ ] #2 Missing or malformed resource identity and ambiguous change details fail closed while reviewed non-destructive changes remain allowed.
- [ ] #3 Regression tests cover the retained Azure What-If shape and the combined validation path; required checks pass without a live destructive deployment.
<!-- AC:END -->
