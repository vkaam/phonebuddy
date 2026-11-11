---
id: TASK-89
title: Record Azure Foundry as an authorized factory model option
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T15:42:00Z'
updated_date: '2026-11-11T15:52:00Z'
labels:
  - factory
  - autonomy
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/37
  - docs/agentic-development-contract.md
modified_files:
  - docs/agentic-development-contract.md
  - >-
    backlog/tasks/task-89 -
    Record-Azure-Foundry-as-an-authorized-factory-model-option.md
priority: high
type: docs
ordinal: 80000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The factory contract records the owner-selected signed-in Codex subscription path and says paid OpenAI API use is not authorized. The owner has now approved Azure Foundry as an additional option. Record this decision before any factory inference integration so the implementation can preserve the approved identity, data, and spending boundaries.

Issue: https://github.com/vkaam/phonebuddy/issues/37
Approved requirements revision: 2026-11-04T06:22:57Z; body SHA-256 e89fb516577a1895faad3736db993a071936a91605451ac43357ba337c217deb.
Approval evidence: The owner directly instructed in this Codex conversation: “No, we can use azure foundry as well.” This authorizes Azure Foundry as an additional model option. Existing TASK-73 approval still prohibits paid OpenAI API usage. This does not authorize reusing the product Foundry identity or data for factory runs, provisioning new factory resources, or any unbounded spend.
Branch: agent/gh-37-6-azure-foundry-option
Scope: docs/agentic-development-contract.md; this task record through Backlog CLI
Verify: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py; python3 -B scripts/backlog_consistency.py --offline; git diff --check; PR Quality must pass, including the browser tests. The local all-in-one check is not usable here because the required Playwright browser binary is unavailable in this environment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The contract records Azure Foundry as an additional owner-approved inference option alongside subscription Codex while keeping paid OpenAI API use unauthorized.
- [x] #2 The contract distinguishes approval of the Foundry option from verified factory access, resource isolation, model choice, retention, and spending limits; it does not grant the coding runner product data or deployment permissions.
- [ ] #3 The task and changed document stay within their declared scope and pass the declared local checks.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the current runtime-decision table and deployment evidence for existing dev/test Foundry resources. 2. Record Azure Foundry as an additional allowed model option, preserving subscription Codex and the prohibition on paid OpenAI API usage. 3. State that approval of the option does not grant the factory product identity/data, production access, new resources, or unbounded spend; keep model selection, isolation, and enforceable limits open. 4. Run the task-declared checks, verify scope, and publish one PR.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated the factory runtime decision to add owner-approved Azure Foundry while retaining subscription Codex, the no-paid-OpenAI-API direction, and the separate factory identity/resource, production-access, and limit gates.

AC1-2 verified against docs/agentic-development-contract.md: Azure Foundry is an additional owner-approved option; paid OpenAI API remains unauthorized; approval grants no product data/identity, production access, factory provisioning or unbounded spend. Local verification: scripts/quality.py passed; scripts/run_required_unittests.py passed in report /tmp/phonebuddy-quality-uz8jm7wt/report.json; scripts/backlog_consistency.py --offline passed; git diff --check passed. The full scripts/check.py bundle failed only because this environment has no Playwright Chromium headless-shell binary; browser tests did not execute. Hosted Quality including browser tests remains required on the PR head.

Adjusted the declared local verification to the documentation-relevant checks plus required hosted Quality because this worktree has no Playwright Chromium binary and the all-in-one local bundle cannot run the browser suite. Hosted Quality on PR #104 did execute the browser suite and passed.
<!-- SECTION:NOTES:END -->
