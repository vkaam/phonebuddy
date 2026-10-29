---
id: TASK-1
title: Establish CI, QA evidence, and conservative PR safety assessment
status: In Progress
assignee:
  - '@codex'
created_date: '2026-10-29T18:48:00Z'
updated_date: '2026-10-29T18:56:00Z'
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
- [ ] #1 CI runs repository validation and safety-policy regression tests for pull requests, default-branch pushes, and merge queues with read-only permissions.
- [ ] #2 A trusted-base PR assessment reports machine-readable reasons, rejects unknown or sensitive changes as auto-merge candidates, and never executes PR code or merges.
- [ ] #3 QA and delivery documentation defines current checks, future platform test gates, required GitHub protections, and staged Azure promotion prerequisites without claiming unimplemented checks pass.
- [ ] #4 Local validation and adversarial policy tests pass, and activation limitations are recorded.
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
Implemented read-only CI, checksum-pinned actionlint/Gitleaks, trusted-base advisory risk reporting, current-head/current-merge CI evidence validation, independent review checks, CODEOWNERS, Dependabot, PR evidence template, and QA/CD activation documentation. Local checks passed: 15 unittest tests (with adversarial subcases), repository checks, actionlint 1.7.12, Gitleaks 8.30.1 full Git history and working directory, and git diff --check. GitHub API confirms main has no branch protection and allow_auto_merge=false. No cloud credentials, deployable application, or infrastructure exists; deployment and merge execution are deliberately inactive. Preparing a draft PR to verify hosted CI; bootstrap risk workflow needs these files on main before live PR assessments can run.
<!-- SECTION:NOTES:END -->
