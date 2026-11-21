---
id: TASK-118
title: Correct owner-settings guidance for a personal repository
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-21T12:08:00Z'
updated_date: '2026-11-21T12:09:00Z'
labels: []
dependencies: []
priority: medium
type: task
ordinal: 101000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/150
Branch: agent/gh-merge-queue-doc
Scope: docs/issue-backlog-governance.md; docs/quality-and-delivery.md
Verify: python3 -B scripts/quality.py; python3 -B scripts/backlog_consistency.py --base origin/main --pr

The owner looked for the merge queue setting the docs describe and could not find it: GitHub offers merge queues only for organization-owned repositories, and this repository belongs to a personal account. The docs also suggest Code Owner review without saying it would block PRs authored by the only code owner.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 docs/issue-backlog-governance.md and docs/quality-and-delivery.md describe only settings available to this personal-account repository, including the trade-off of turning off the up-to-date requirement without a merge queue
- [ ] #2 The Code Owner review guidance says a second maintainer must be added to CODEOWNERS before enabling it
- [ ] #3 No document on the branch instructs the owner to enable a merge queue
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Replace the merge-queue item in the governance doc owner-settings list with the up-to-date trade-off, and add the single-code-owner warning.
2. Correct the GitHub activation paragraph in the quality doc.
3. Run quality and the PR guard; finish the record; independent review; merge.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Claim check 2026-11-21: pass, claim_verified true.
<!-- SECTION:NOTES:END -->
