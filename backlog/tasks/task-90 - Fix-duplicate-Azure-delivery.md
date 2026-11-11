---
id: TASK-90
title: Fix duplicate Azure delivery
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T18:05:00Z'
updated_date: '2026-11-11T18:24:00Z'
labels: []
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/105
modified_files:
  - backlog/tasks/task-90 - Fix-duplicate-Azure-delivery.md
  - .github/workflows/azure-deploy.yml
  - tests/test_bicep_ci_boundary.py
  - tests/test_deployment_policy.py
priority: low
type: bug
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: A repeated delivery can fail when an immutable image tag already exists because the ACR tag query expects objects but receives strings.

Issue: https://github.com/vkaam/phonebuddy/issues/105
Approved revision: 2026-11-11T18:04:24Z; body SHA-256 a8f1aa6aca896b074222f04e010eea6eb2c296d0d6825ceae38933a2abeceecb.
Approval evidence: The owner requested a low-priority follow-up in Codex on 2026-11-11.
Branch: agent/gh-105-duplicate-delivery
Scope: .github/workflows/azure-deploy.yml; tests/test_deployment_policy.py; tests/test_bicep_ci_boundary.py; backlog/tasks/task-90 - Fix-duplicate-Azure-delivery.md
Verify: python3 -B scripts/check.py; python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/azure-deploy.yml .github/workflows/pr-safety.yml. Record hosted duplicate-delivery evidence when Azure is available.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Duplicate delivery detects and reuses a matching immutable image after verification; writable or mismatched images fail closed.
- [ ] #2 An absent tag follows the normal publication path, with automated tests covering both lookup paths.
- [ ] #3 Relevant local and hosted checks pass and safe duplicate delivery evidence is recorded when Azure is available.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the release workflow and existing tests for tag detection and immutable image verification. 2. Correct tag detection and add meaningful coverage for existing and absent tags and fail-closed verification. 3. Run the declared local checks and publish the existing draft PR. 4. Obtain independent review, required hosted checks and available duplicate-delivery evidence before finalizing.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
The ACR lookup now requests detailed tag objects before filtering by name. Focused policy and workflow tests pass locally; the behavioral promotion-step test requires Bash and is skipped on this Windows host. Full scripts/check.py failed locally and check_bicep.py could not find Bicep; hosted checks and duplicate-delivery Azure evidence remain required. Independent review identified the missing workflow-level coverage, which is now added but awaits execution in hosted CI.

PR #106 head 5097d99e4edd7608c8f62df07fa1c29ca6232923 passed hosted Quality run 43076192295 attempt 2, including the Linux behavioral tests, actionlint and Bicep validation. An independent agent reviewed that exact tree and found no additional scoped defects; live Azure duplicate-delivery evidence remains outstanding. The current host has no Azure CLI or Docker.
<!-- SECTION:NOTES:END -->
