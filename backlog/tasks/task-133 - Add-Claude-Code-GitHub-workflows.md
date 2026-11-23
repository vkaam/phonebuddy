---
id: TASK-133
title: Add Claude Code GitHub workflows
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-23T18:01:00Z'
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
- [ ] #1 Both workflows pin every action to a full commit SHA and python3 scripts/quality.py passes
- [ ] #2 Task link and Quality checks pass on the PR head
<!-- AC:END -->
