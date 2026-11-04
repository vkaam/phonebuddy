---
id: TASK-76
title: Issue 85 - Simplify agent review and merge-first completion governance
status: Done
assignee:
  - '@codex'
created_date: '2026-11-04T05:57:00Z'
updated_date: '2026-11-04T06:17:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/85
  - docs/issue-backlog-governance.md
  - AGENTS.md
  - docs/agentic-development-contract.md
  - docs/quality-and-delivery.md
  - docs/autonomous-development-plan.md
  - .github/pull_request_template.md
  - scripts/pr_safety.py
  - tests/test_pr_safety.py
  - docs/azure-delivery-policy.md
  - docs/software-plan.md
  - https://github.com/vkaam/phonebuddy/pull/86
modified_files:
  - >-
    backlog/tasks/task-76 -
    Issue-85-Simplify-agent-review-and-merge-first-completion-governance.md
  - AGENTS.md
  - docs/issue-backlog-governance.md
  - docs/agentic-development-contract.md
  - docs/quality-and-delivery.md
  - docs/autonomous-development-plan.md
  - .github/pull_request_template.md
  - scripts/pr_safety.py
  - tests/test_pr_safety.py
  - docs/azure-delivery-policy.md
  - docs/software-plan.md
priority: high
type: task
ordinal: 70000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The owner approved a lighter development workflow on 2026-11-04: agents may review PRs and validate acceptance, a merge to main completes the scoped task, and post-merge failures become new linked work. Older governance still mandates human approval and release gates for issue closure, leaving conflicting instructions.

Issue: https://github.com/vkaam/phonebuddy/issues/85
Approved revision: 2026-11-04T05:55:56Z; body SHA-256 6b335858ff98cb632f8ac349b703d899ed890e1ba1999025dc9cd055a2ad1168.
Approval evidence: Direct owner instruction in Codex on 2026-11-04: agents may review PRs and validate acceptance; a merge to main completes scoped work; post-merge failures become new linked work.
Branch: agent/gh-85-1-merge-first-governance
Scope: AGENTS.md; docs/issue-backlog-governance.md; docs/agentic-development-contract.md; docs/quality-and-delivery.md; docs/autonomous-development-plan.md; docs/azure-delivery-policy.md; docs/software-plan.md; .github/pull_request_template.md; scripts/pr_safety.py; tests/test_pr_safety.py; backlog/tasks/task-76 - Issue-85-Simplify-agent-review-and-merge-first-completion-governance.md
Verify: From repository root run python3 -B -m unittest tests.test_pr_safety and python3 -B scripts/check.py. Verify the live issue/task/PR mapping and current hosted PR checks.
Spec: Keep intent approval in GitHub Issues and atomic execution in native Backlog tasks. Define a practical event-driven sync contract: task and issue updates are reconciled after each transition, mismatch is visible, merge to the default branch completes task and issue when all required tasks merge, and post-merge failures create linked work. Respect effective branch rules and required pre-merge checks; do not claim deployment health from merge.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Repository instructions and governance permit independent agent PR review and acceptance validation without a per-PR human approval gate.
- [x] #2 Issue and native Backlog task states are linked and reconciled at each transition, including partial multi-task issues and visible sync failures.
- [x] #3 A merged PR to the default branch is sufficient to mark its scoped task Done and close its issue once all required tasks merge; post-merge defects create linked new issues/tasks.
- [x] #4 PR instructions favor early merge after required checks and blocking findings, followed by default-branch CI/CD observation.
- [x] #5 Conflicting policy, templates, and advisory code agree on the new authority model; focused tests and repository checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Replace the old human review and post-merge acceptance rules with independent agent review, agent acceptance validation, merge-based scoped completion, and follow-up tickets for later failures.
2. Define exact issue/Backlog synchronization points, multi-task issue behavior, reconciliation failures, and post-merge CI/CD reporting in the authoritative governance and agent instructions.
3. Align the operating contract, quality guide, autonomy plan, PR template, and PR safety advisory with the adopted policy.
4. Run focused tests, full repository checks, live consistency validation, and hosted PR checks; record evidence and publish the branch.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Triage amendment (2026-11-04): the Azure delivery policy and software plan also prescribe the superseded human review and post-release closure gates. The owner's direct issue #85 instruction covers these policy documents; added their exact paths to scope before editing. Required checks and acceptance are unchanged.

PR #86 is open as a draft on f324a83a55cea71ef9617fd24f6ad77a719ad645. Local focused tests passed (16), full scripts/check.py passed all 12 checks (report /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-uhjey2a9/report.json), git diff --check passed, and live claim consistency passed with claim_verified: true. Independent agent final-diff review and hosted checks are pending. Effective main rules require PR, resolved threads and strict Quality, with zero approving reviews.

Verified on PR #86 head 718e083bb4d6f51d0a5dc29503a31e53941d17b9: AGENTS.md and governance permit independent agent review and acceptance validation, and the effective main rules require zero approving reviews (AC1). Advisory code and policy documents align; 16 focused tests passed, full scripts/check.py passed all 12 local checks at /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-uhjey2a9/report.json, live consistency passed, and hosted Quality plus Risk report passed on this head (AC5). Independent reviewer /root/independent_review found no actionable findings and independently passed focused tests, scripts/quality.py, offline consistency and git diff --check. Issue #85 comments link TASK-76 claim, scope amendment and PR publication. The documented multi-task and failed-sync behavior, actual merge-based completion, and post-merge CI/CD observation have not been exercised yet; AC2-4 remain unchecked. Durable automatic reconciliation remains future factory work.

Independent reviewer /root/independent_review rechecked c0b33cbc34e3ec96194cc8576da3594fa0aac6c3 and confirmed no actionable findings. For TASK-76's stated governance Spec, AC2-4 validate the adopted process contract, not deployment of the still-unbuilt durable reconciler or a live post-merge run. AC2 is evidenced by docs/issue-backlog-governance.md:69-82 and issue #85's task/PR transition comments; these define multi-task status and visible retry on sync failure. AC3 is evidenced by governance:84-101, which explicitly defines merge-based scoped completion and new linked work for defects. AC4 is evidenced by governance:57-67 and :90-101, AGENTS.md and the PR template, which require early merge after required checks and post-merge CI/CD observation. The unbuilt automatic reconciler and unexercised future failure scenarios remain disclosed as limitations; checking these policy criteria does not claim those systems exist.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Adopted the owner's 4 November 2026 policy in AGENTS.md, governance, factory/delivery plans and PR template: independent agents can review PRs and validate scoped acceptance; small ready PRs merge after required checks; a default-branch merge completes its task and closes its issue when all required tasks merge; post-merge CI/CD failures become linked new work. Updated the PR safety advisory to remove human approval as a risk-classifier input and added focused regression coverage. Verified 16 focused tests, all 12 local baseline checks, live task consistency, hosted Quality and advisory checks on c0b33cbc, and independent agent review with no actionable findings. Effective main rules require zero approving reviews. Automatic durable issue/Backlog reconciliation and a merger service remain unimplemented; the process contract requires visible transition reporting and retry. Final task-record commit and its hosted checks must be verified before merge.
<!-- SECTION:FINAL_SUMMARY:END -->
