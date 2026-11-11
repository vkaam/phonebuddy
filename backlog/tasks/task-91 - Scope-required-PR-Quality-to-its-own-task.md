---
id: TASK-91
title: Scope required PR Quality to its own task
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T18:21:00Z'
updated_date: '2026-11-11T18:45:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/107
  - .github/workflows/ci.yml
  - scripts/backlog_consistency.py
  - https://github.com/vkaam/phonebuddy/pull/108
modified_files:
  - backlog/tasks/task-91 - Scope-required-PR-Quality-to-its-own-task.md
  - scripts/backlog_consistency.py
  - tests/test_backlog_consistency.py
  - .github/workflows/ci.yml
  - docs/quality-and-delivery.md
  - docs/issue-backlog-governance.md
  - .github/workflows/backlog-audit.yml
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Required PR Quality currently fails for unrelated repository bookkeeping and an event-time main SHA, delaying otherwise ready PRs.
Issue: https://github.com/vkaam/phonebuddy/issues/107
Approved revision: 2026-11-11T18:26:37Z; body SHA-256 5b94aecf30406e1b9c8427df479a88d807ec7d397c67b9522edd53bb9c6eb37e.
Approval evidence: On 2026-11-11 the owner explicitly selected a PR-scoped blocking guard with unrelated mismatches reported separately, merge-based task completion, and early merge followed by full verification on main before promotion.
Branch: agent/gh-107-1-pr-quality-scope
Scope: .github/workflows/ci.yml; .github/workflows/backlog-audit.yml; scripts/backlog_consistency.py; tests/test_backlog_consistency.py; docs/quality-and-delivery.md; docs/issue-backlog-governance.md; backlog/tasks/task-91 - Scope-required-PR-Quality-to-its-own-task.md
Verify: From repository root run python3 -B -m unittest discover -s tests -p test_backlog_consistency.py, python3 -B scripts/run_required_unittests.py, python3 -B scripts/quality.py, actionlint .github/workflows/ci.yml .github/workflows/backlog-audit.yml, and the live Backlog consistency guard against fresh origin/main. Verify hosted PR Quality and the separate advisory audit on the final PR head. The actual main Quality and promotion result is post-merge evidence for a separate issue 107 task.
Spec: Keep the PR's own approval, claim, scope and dependency violations blocking. Retain full repository audit evidence in a separate workflow so its failure or delay cannot stop the CI workflow or downstream promotion. On PRs keep fast deterministic safety checks and source-scope security checks; wire full web, dependency and browser verification to merged main before release promotion. Existing Bicep PR validation remains required by issue 14. The trusted release consumes only the exact verified main artifact.
Triage amendment 2026-11-11: The owner added early merge, full main verification and promote-after-verification. This changes the PR/main check boundary within issue 107; no Azure release workflow change is needed because it already waits for successful exact-SHA main CI.
Triage amendment 2026-11-11 after independent review: TASK-91 pre-merge acceptance covers verified workflow wiring and PR checks. Actual merged-main verification and promotion evidence cannot precede this PR's merge and is assigned to a separate issue 107 slice.
Triage scope amendment 2026-11-11 after independent review: Add .github/workflows/backlog-audit.yml for the separate advisory audit. Keeping it inside CI could delay the trusted release even when advisory failures do not change CI's conclusion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A PR with an invalid or missing claim, approval revision, changed-file scope, or dependency fails required Quality.
- [ ] #2 Unrelated task and issue inconsistencies are retained in an advisory audit report without failing another PR or the CI workflow; missing audit evidence is visibly inconclusive.
- [ ] #3 Moving main does not fail a PR solely for an event-time base SHA; the guard uses current evidence or reports an actionable rerun condition.
- [ ] #4 The reviewed CI wiring keeps fast repository, policy, workflow, infrastructure and introduced-secret checks on PRs and requires full web, dependency and browser checks on the exact merged main SHA before the immutable release image can be built or promoted.
- [ ] #5 Regression tests, hosted PR checks and policy documentation prove the blocking boundary, unrelated stale records, moving main, and pre-promotion main verification wiring.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Separate focused PR consistency failures from complete repository audit findings. 2. Keep fast PR checks and move web/dependency/browser verification to exact-SHA main CI; move the repository-wide audit into its own workflow so it cannot delay release. 3. Make stale-main failures actionable, add regression coverage and update policy documentation. 4. Run declared checks, publish the PR, obtain independent review and final-head checks, then merge and inspect main verification.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented PR-focused live consistency validation, an advisory repository-wide audit job, and main-only locked web install/audit/lint/unit/build/browser checks. PRs retain repository/Python policy tests, actionlint, Bicep and Gitleaks; the existing main release image still depends on Quality and the trusted Azure workflow verifies the exact source artifact before promotion. Focused guard tests passed (30); required Python suite passed (137) with local loopback allowed; repository checks, actionlint 1.7.12 checksum-verified, live PR-scoped guard and git diff --check passed. Hosted PR and main results remain pending.

Draft PR #108 opened at head f071d283e612c96a0d2d65323bdea54e4abe2ec7. Hosted current-head checks and independent review are pending; keep this task active.

Independent review identified two closure/safety issues: post-merge main evidence cannot be a pre-merge TASK-91 criterion, and an advisory artifact upload failure could fail the overall CI workflow. The owner-approved triage amendment assigns actual main evidence to a separate issue 107 task; CI now marks the entire audit job advisory and warns on missing artifacts.

Addressed both independent review findings before finalization. TASK-91 acceptance now checks pre-merge wiring, with actual main results assigned to later issue 107 work. The entire advisory audit job is continue-on-error, including artifact upload, and missing evidence emits a warning. Added fail-closed rejection of --ci-pr with --offline. Focused tests passed (30), required Python suite passed (137 with local loopback), repository checks passed, and checksum-verified actionlint 1.7.12 passed after the fixes. Re-review and final-head hosted checks are pending.

Independent review found that an advisory job inside CI still delays the workflow_run promotion trigger. Approved triage scope now includes a separate backlog-audit workflow; this supersedes the in-CI audit job design.

Moved the repository-wide Backlog audit to its own workflow after the independent timing review. The advisory workflow has read-only permissions, publishes JSON with if-no-files-found: error, and is not a CI job or release prerequisite. Pinned actionlint 1.7.12 passed on both workflows; repository checks and diff checks passed. Final-head hosted checks and independent re-review are pending.
<!-- SECTION:NOTES:END -->
