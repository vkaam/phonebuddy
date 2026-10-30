---
id: TASK-4
title: Define Azure environments and automatic delivery policy
status: Done
assignee:
  - '@codex'
created_date: '2026-10-29T20:04:00Z'
updated_date: '2026-10-30T06:21:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - docs/azure-delivery-policy.md
modified_files:
  - docs/azure-delivery-policy.md
  - docs/quality-and-delivery.md
  - docs/software-plan.md
priority: high
type: task
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Establish pilot, test and production boundaries on the existing GitHub Actions baseline. The user requires automatic default-branch deployment, superseding prior routine manual release gates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Document subscriptions, geography, naming, owners, budgets and unresolved inputs for each enabled environment.
- [x] #2 Define ordered automatic default-branch delivery with health gates and PR review before merge; update conflicting delivery documentation.
- [x] #3 Define failure thresholds, observation windows, first-release behavior and recovery responsibilities.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inventory the existing environment and delivery assumptions, and distinguish confirmed inputs from unresolved subscription, geography, owner, and budget choices.
2. Document proposed pilot/dev, test, and production boundaries and the ordered automatic promotion policy, keeping independent PR review before merge.
3. Define measurable deployment health gates, observation windows, first-release failure behavior, and recovery ownership; update conflicting delivery statements.
4. Validate documentation and record evidence against each acceptance criterion.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Initial review found no Azure environments or identities configured in the repository; subscription IDs, regional availability, named owners, and budget amounts require owner input. The existing delivery baseline still calls for a manual production approval, conflicting with this task’s automatic delivery requirement. Implementation awaits review of the proposed policy decisions.

Environment register records unresolved inputs and enablement prerequisites; delivery policy specifies ordered automatic promotion, measurable initial gates and recovery ownership. Conflicting production approval statements were updated. Verified with python3 -B scripts/check.py (pass) and git diff --check; no environments or gates have been provisioned.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Defined the Azure environment register and automatic delivery, health gate and recovery policy, and aligned the existing plans. Local baseline and diff checks passed. Subscription, geography, budgets and named owners remain prerequisites; downstream tasks must implement and validate the gates.
<!-- SECTION:FINAL_SUMMARY:END -->
