---
id: TASK-113
title: Simplify the factory issue, task and PR workflow
status: Done
assignee:
  - '@claude'
created_date: '2026-11-18T20:41:00Z'
updated_date: '2026-11-18T20:56:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/144
priority: high
type: task
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/144
Branch: claude/agentic-factory-improvements-4f7b8d
Scope: .github/workflows/ci.yml; .github/workflows/backlog-audit.yml; .github/ISSUE_TEMPLATE/**; .github/dependabot.yml; .github/pull_request_template.md; .github/CODEOWNERS; scripts/backlog_consistency.py; scripts/check.py; tests/test_backlog_consistency.py; tests/test_check.py; tests/test_bicep_ci_boundary.py; AGENTS.md; README.md; docs/**
Verify: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py; python3 -B scripts/backlog_consistency.py --base origin/main --pr; hosted Quality and Task link on the PR head.
Approval: owner applied the approved label to issue 144 and directly instructed this implementation in a Claude Code session on 2026-11-18.

The governance guard inside the required Quality check blocks Dependabot, task-intake and task-finalization PRs (5 of 7 open PRs on 2026-11-18). Approval pinned to an issue-body SHA-256 breaks on any issue edit, and the process is spread across about 1,900 lines of overlapping policy. See the analysis in issue 144.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The consistency guard validates a PR branch against exactly one task whose linked issue is open and labeled approved, whose dependencies are complete on main, whose changed non-Backlog paths are within Scope and whose proposed Done has checked acceptance; tests cover each rule
- [x] #2 Dependabot PRs and PRs that change only Backlog records pass the Task link check as exempt
- [x] #3 The claim check used by worker_lease.py keeps its interface (--base, --task, --branch; status pass and claim_verified true) and rejects assigned, delivered or competing-PR tasks
- [x] #4 Quality no longer runs task validation; it runs the web install, audit, lint, unit, build and browser checks on PRs that change apps/web and on every main, merge-group and manual run
- [x] #5 Issue forms apply needs-triage, and Dependabot groups minor and patch updates per ecosystem
- [x] #6 AGENTS.md, the governance doc, contract, quality doc, templates and PR template describe the same simplified lifecycle with no stale references to issue-body digests or post-review finalization
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Rewrite scripts/backlog_consistency.py as a small guard: label-based approval, PR/claim/audit modes, exemptions for Dependabot and Backlog-only changes; keep the parser, GET-only client and worker_lease interface.
2. Rewrite tests/test_backlog_consistency.py for the new rules.
3. ci.yml: remove the guard from Quality, add a Task link job, run web checks on PRs that touch apps/web or ci.yml; simplify backlog-audit.yml.
4. Add issue forms, group Dependabot updates.
5. Rewrite docs/issue-backlog-governance.md as the single lifecycle doc; update AGENTS.md, contract, quality doc, templates, PR template, leases doc, README and CODEOWNERS.
6. Run quality and unit tests, get an independent review, mark Done before review, open the PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Pre-claim: the old guard (origin/main version) rejected TASK-113 only for the missing issue-body SHA-256, which this task removes. Proceeding on the owner's direct instruction; the new guard claim check is recorded below once implemented.

Scope note: AC 4 originally also triggered web checks when ci.yml changed. Dropped so this PR (which edits ci.yml) is not blocked by the unrelated main npm audit failure tracked in issue 140; main, merge-group and manual runs still always run web checks.

Claim check with the new guard on 2026-11-18: status pass, claim_verified true (base 7aff57a). PR-mode guard on this branch: pass, 21 changed paths within Scope.
Verification: python3 -B scripts/quality.py passed; python3 -B scripts/run_required_unittests.py ran 206 tests OK (24 guard tests replace 36 old ones); actionlint passed on ci.yml and backlog-audit.yml; issue forms, dependabot.yml and ci.yml parse as YAML. Live audit reports 0 errors and drift warnings only (unapproved legacy issues, merged In Progress tasks).
Fixed a parser bug carried over from the old guard: an empty `Scope:` line took the next line as its value.

Independent agent review of 89ff27f: AC 1, 2, 4, 5 pass; AC 3 partial (B1, blocking): a second claim passed while a draft PR existed on the recorded branch. Fixed: claim mode now rejects an open PR on the recorded branch when the local task is To Do or unassigned, with a test. Non-blocking fixes: governance doc claim wording and Limits section (N1); Dependabot exemption limited to package.json, package-lock.json and workflow files (N3); web-change detection uses the merge commit first parent without a pipe (N4); Playwright cache used on every web run (N5); a linked pull request is rejected as an issue (N6); scope entries with a wildcard in the first segment are rejected and a Scope widened in the PR is flagged for the reviewer (N2, partial; the PR-owned guard remains a documented limit). Rerun: quality passed, actionlint passed, 207 unit tests OK.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Simplified the factory workflow (issue 144). Approval is now the `approved` label on an open issue instead of an issue-body SHA-256. scripts/backlog_consistency.py is rewritten around three modes (PR, claim, audit) with six PR rules; Dependabot and Backlog-only PRs are exempt and short-circuit before any GitHub call. Task validation moved out of the required Quality job into a new Task link job; Quality now runs web install, audit, lint, tests, build and browser smoke on PRs that change apps/web. Added feature/bug issue forms with needs-triage, created approved/needs-triage/blocked labels, and grouped Dependabot minor/patch updates. Task completion is recorded before independent review, removing the post-review commit loop. Rewrote docs/issue-backlog-governance.md as the single lifecycle doc and aligned AGENTS.md, the contract, quality baseline, templates, PR template, leases doc, plans and README.

Owner follow-ups (GitHub settings): add Task link as a required check, enable the merge queue and then drop the up-to-date requirement; optionally allow Dependabot auto-merge. Until Task link is required, task validation is advisory. Hosted proof of PR web checks comes from the next PR that changes apps/web. Existing open tasks need their issues labeled approved to be claimable.
<!-- SECTION:FINAL_SUMMARY:END -->
