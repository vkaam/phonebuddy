---
id: TASK-133
title: Add Claude Code GitHub workflows
status: Done
assignee:
  - '@claude'
created_date: '2026-11-23T18:01:00Z'
updated_date: '2026-11-23T18:32:00Z'
labels: []
dependencies: []
ordinal: 113000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/169
Branch: add-claude-github-actions-1795456799524
Scope: .github/workflows/claude.yml; .github/workflows/claude-code-review.yml
Verify: python3 scripts/quality.py; python3 -B scripts/run_required_unittests.py

The Claude Code GitHub App installer opened PR #168 with workflows that let maintainers mention Claude and get automatic PR reviews. The workflows must meet repository policy (actions pinned to immutable commits) and be tracked through the factory workflow.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Both workflows pin every action to a full commit SHA and python3 scripts/quality.py passes
- [x] #2 Task link and Quality checks pass on the PR head
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Pinned actions/checkout and anthropics/claude-code-action to full commit SHAs in both Claude workflows so scripts/quality.py passes. Dropped the synchronize trigger from the review workflow after review feedback, since the plugin skips PRs it already commented on. Verified: quality.py and 270 required unit tests pass; Quality and Task link pass in CI. Review of the final head is recorded on the PR.
<!-- SECTION:FINAL_SUMMARY:END -->
