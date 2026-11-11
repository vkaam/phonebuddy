---
id: TASK-91
title: Scope required PR Quality to its own task
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T18:21:00Z'
updated_date: '2026-11-11T18:35:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/107
  - .github/workflows/ci.yml
  - scripts/backlog_consistency.py
modified_files:
  - backlog/tasks/task-91 - Scope-required-PR-Quality-to-its-own-task.md
  - scripts/backlog_consistency.py
  - tests/test_backlog_consistency.py
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
  - docs/issue-backlog-governance.md
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Required PR Quality currently fails for unrelated repository bookkeeping and an event-time main SHA, delaying otherwise ready PRs.
Issue: https://github.com/vkaam/phonebuddy/issues/107
Approved revision: 2026-11-11T18:26:37Z; body SHA-256 5b94aecf30406e1b9c8427df479a88d807ec7d397c67b9522edd53bb9c6eb37e.
Approval evidence: On 2026-11-11 the owner explicitly selected a PR-scoped blocking guard with unrelated mismatches reported separately, merge-based task completion, and early merge followed by full verification on main before promotion.
Branch: agent/gh-107-1-pr-quality-scope
Scope: .github/workflows/ci.yml; scripts/backlog_consistency.py; tests/test_backlog_consistency.py; docs/quality-and-delivery.md; docs/issue-backlog-governance.md; backlog/tasks/task-91 - Scope-required-PR-Quality-to-its-own-task.md
Verify: From repository root run python3 -B -m unittest discover -s tests -p test_backlog_consistency.py, python3 -B scripts/run_required_unittests.py, python3 -B scripts/quality.py, actionlint .github/workflows/ci.yml, and the live Backlog consistency guard against fresh origin/main. Verify hosted Quality on the final PR head and main Quality after merge.
Spec: Keep the PR's own approval, claim, scope and dependency violations blocking. Retain full repository audit evidence. On PRs keep fast deterministic safety checks and source-scope security checks; run full web, dependency and browser verification on the merged main SHA before release promotion. Existing Bicep PR validation remains required by issue 14. The trusted release consumes only the exact verified main artifact.
Triage amendment 2026-11-11: The owner added early merge, full main verification and promote-after-verification. This changes the PR/main check boundary within issue 107; no Azure release workflow change is needed because it already waits for successful exact-SHA main CI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A PR with an invalid or missing claim, approval revision, changed-file scope, or dependency fails required Quality.
- [ ] #2 Unrelated task and issue inconsistencies are retained in an audit report without failing another PR; main audits still surface them.
- [ ] #3 Moving main does not fail a PR solely for an event-time base SHA; the guard uses current evidence or reports an actionable rerun condition.
- [ ] #4 PR Quality keeps fast repository, policy, workflow, infrastructure and introduced-secret checks; full web, dependency and browser checks run on the merged main SHA and gate immutable artifact promotion.
- [ ] #5 Regression tests and policy documentation cover the blocking boundary, unrelated stale records, moving main, and main verification before promotion.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Separate focused PR consistency failures from complete repository audit findings. 2. Keep fast PR checks and move web/dependency/browser verification to exact-SHA main CI; leave existing Bicep PR safety and trusted main release gating intact. 3. Make stale-main failures actionable, add regression coverage and update policy documentation. 4. Run declared checks, publish the PR, obtain independent review and final-head checks, then merge and inspect main verification.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented PR-focused live consistency validation, an advisory repository-wide audit job, and main-only locked web install/audit/lint/unit/build/browser checks. PRs retain repository/Python policy tests, actionlint, Bicep and Gitleaks; the existing main release image still depends on Quality and the trusted Azure workflow verifies the exact source artifact before promotion. Focused guard tests passed (30); required Python suite passed (137) with local loopback allowed; repository checks, actionlint 1.7.12 checksum-verified, live PR-scoped guard and git diff --check passed. Hosted PR and main results remain pending.
<!-- SECTION:NOTES:END -->
