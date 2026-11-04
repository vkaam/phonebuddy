---
id: TASK-76
title: Issue 85 - Simplify agent review and merge-first completion governance
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-04T05:57:00Z'
updated_date: '2026-11-04T06:10:00Z'
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
- [ ] #1 Repository instructions and governance permit independent agent PR review and acceptance validation without a per-PR human approval gate.
- [ ] #2 Issue and native Backlog task states are linked and reconciled at each transition, including partial multi-task issues and visible sync failures.
- [ ] #3 A merged PR to the default branch is sufficient to mark its scoped task Done and close its issue once all required tasks merge; post-merge defects create linked new issues/tasks.
- [ ] #4 PR instructions favor early merge after required checks and blocking findings, followed by default-branch CI/CD observation.
- [ ] #5 Conflicting policy, templates, and advisory code agree on the new authority model; focused tests and repository checks pass.
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
<!-- SECTION:NOTES:END -->
