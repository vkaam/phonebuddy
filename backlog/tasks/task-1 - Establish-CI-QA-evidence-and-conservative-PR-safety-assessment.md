---
id: TASK-1
title: Establish CI, QA evidence, and conservative PR safety assessment
status: Done
assignee:
  - '@codex'
created_date: '2026-10-29T18:48:00Z'
updated_date: '2026-10-29T19:00:00Z'
labels: []
dependencies: []
references:
  - docs/software-plan.md
  - .github/workflows/ci.yml
  - .github/workflows/pr-safety.yml
  - scripts/pr_safety.py
  - docs/quality-and-delivery.md
modified_files:
  - .github/workflows/ci.yml
  - scripts/quality.py
  - scripts/pr_safety.py
  - .github/workflows/pr-safety.yml
  - tests/test_pr_safety.py
  - .github/CODEOWNERS
  - .github/dependabot.yml
  - .github/pull_request_template.md
  - docs/quality-and-delivery.md
  - README.md
priority: high
type: chore
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
PhoneBuddy is planning-only and has no automated checks. Establish a runnable repository baseline and an explainable assessment so future PRs carry evidence and low-risk candidates can be distinguished from changes requiring review. Use the existing GitHub repository for this initial increment; cloud deployment and automatic merging remain inactive until their prerequisites are implemented.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 CI runs repository validation and safety-policy regression tests for pull requests, default-branch pushes, and merge queues with read-only permissions.
- [x] #2 A trusted-base PR assessment reports machine-readable reasons, rejects unknown or sensitive changes as auto-merge candidates, and never executes PR code or merges.
- [x] #3 QA and delivery documentation defines current checks, future platform test gates, required GitHub protections, and staged Azure promotion prerequisites without claiming unimplemented checks pass.
- [x] #4 Local validation and adversarial policy tests pass, and activation limitations are recorded.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add read-only GitHub CI for repository hygiene and policy regression tests.
2. Add trusted-base, advisory PR risk reporting with strict documentation allowlist and current CI evidence.
3. Document QA layers, GitHub activation, and Azure deployment prerequisites; add PR template and action update automation.
4. Run local tests, lint workflows, and record verified scope and activation limitations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented read-only CI, checksum-pinned actionlint/Gitleaks, trusted-base advisory risk reporting, current-head/current-merge CI evidence validation, independent human review checks, CODEOWNERS, Dependabot, PR evidence template, and QA/CD activation documentation. Local checks passed: 15 unittest tests with adversarial subcases, repository checks, actionlint 1.7.12, Gitleaks 8.30.1 on Git history and working directory, and diff whitespace checks. First hosted CI run 40935621130 passed every step including artifact upload.

Live API integration confirmed that GitHub attaches checks to the PR head. CI records the tested merge commit in its run title, which the collector compares against the current merge commit; a stale-merge regression case passes. The updated hosted run is being verified. GitHub confirms main has no protection and auto-merge is disabled; cloud deployments and merge execution remain inactive. Draft PR #1 also includes three pre-existing setup commits already on local main but not remote main; no prior work was rewritten. The bootstrap requires manual review, and the advisory workflow needs its trusted policy on main before subsequent live reports can run.

Updated hosted CI run 40935969858 passed. A second live collector exercise recognized successful Quality evidence for the exact current head and merge commit, with no missing/malformed-evidence fallback. The bootstrap still correctly receives manual-review.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added runnable GitHub CI, pinned workflow/secret scanners, adversarial risk-policy tests, trusted-base advisory PR reporting, ownership/update/template configuration, and explicit QA/CD activation documentation. Local checks and first hosted CI pass; merge execution, branch protection activation, and Azure deployments remain inactive. Draft PR: https://github.com/vkaam/phonebuddy/pull/1. The current bootstrap requires maintainer review and the safety workflow needs the policy on main before it can assess subsequent PRs.
<!-- SECTION:FINAL_SUMMARY:END -->
