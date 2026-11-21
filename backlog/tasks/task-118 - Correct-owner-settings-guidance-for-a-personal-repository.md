---
id: TASK-118
title: Correct owner-settings guidance for a personal repository
status: Done
assignee:
  - '@claude'
created_date: '2026-11-21T12:08:00Z'
updated_date: '2026-11-21T12:11:00Z'
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
- [x] #1 docs/issue-backlog-governance.md and docs/quality-and-delivery.md describe only settings available to this personal-account repository, including the trade-off of turning off the up-to-date requirement without a merge queue
- [x] #2 The Code Owner review guidance says a second maintainer must be added to CODEOWNERS before enabling it
- [x] #3 No document on the branch instructs the owner to enable a merge queue
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

Verified the repository owner is a User account (gh api repos/vkaam/phonebuddy owner.type), so the merge queue rule is not offered. Updated the owner-settings list in docs/issue-backlog-governance.md (exact settings paths, up-to-date trade-off, auto-merge per PR, Code Owner review warning) and the GitHub activation paragraphs in docs/quality-and-delivery.md. grep finds no remaining instruction to enable a merge queue; scripts/quality.py passed.

Independent review of 3b8991d found one blocking issue: the owner had already applied the settings (ruleset updated 2026-11-21 12:00 UTC: Task link required, up-to-date off; auto-merge allowed), so the docs listed done items as to-dos. Rewrote the governance section as "Repository settings" describing the current state, marked Task link as required in the checks table, updated the quality doc paragraph, and stated that the release gate is the whole main CI run. Verified live with gh api; quality.py passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Corrected the owner-settings guidance: GitHub offers merge queues only for organization-owned repositories, and this one belongs to a personal account. The workflow doc now lists only settings that exist here, with menu paths: add Task link as a required check, optionally turn off the up-to-date requirement (with the trade-off explained), optionally allow auto-merge, and hold off on Code Owner review until a second maintainer is in CODEOWNERS. The quality baseline matches.
<!-- SECTION:FINAL_SUMMARY:END -->
