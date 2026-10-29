---
id: TASK-2
title: Add reusable work specification and acceptance evidence templates
status: Done
assignee:
  - '@codex'
created_date: '2026-10-29T19:25:00Z'
updated_date: '2026-10-29T19:26:00Z'
labels: []
dependencies: []
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - docs/templates/work-specification.md
  - docs/templates/acceptance-evidence.md
  - .github/pull_request_template.md
modified_files:
  - docs/templates/work-specification.md
  - docs/templates/acceptance-evidence.md
  - docs/quality-and-delivery.md
  - .github/pull_request_template.md
priority: high
type: docs
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The CI baseline exists, but the Phase 0 delivery loop lacks a reusable specification and evidence format. Provide concrete authoring templates tied to Backlog and existing CI without introducing cloud or product decisions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Work specification captures bounded behavior, measurable acceptance cases, relevant risks, and unresolved inputs while Backlog remains the plan of record.
- [x] #2 Evidence template binds results to tested source and configuration, maps each criterion to reproducible evidence, and distinguishes failed, pending, and inapplicable checks.
- [x] #3 Templates are discoverable from delivery documentation and PR authoring, and repository checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add work specification and evidence Markdown templates aligned with existing Phase 0 guidance. 2. Link them from delivery guidance and the PR template. 3. Validate local links and repository checks, inspect the diff, and record evidence.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
AC1: Reviewed specification fields for behavior, bounded scope, acceptance cases, negative cases, operational boundaries, and unresolved inputs; lifecycle and plans remain in Backlog. AC2: Reviewed evidence fields for head/base/tested merge, local patch, configuration and artifact identities, reproducible commands, criterion mapping, and explicit pass/fail/not-run/blocked/inapplicable states. AC3: Delivery guide and PR template link both templates; Python repository validation including local Markdown links passed, all 15 safety regression tests passed, and git diff --check passed. Documentation-only change; hosted CI and independent review not run for this working tree.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added reusable work specification and acceptance evidence templates and linked them from delivery guidance and PR authoring. They tie bounded acceptance cases to source/configuration-specific results while keeping Backlog authoritative. Repository validation, 15 existing regression tests, and whitespace checks pass. Changes remain local; hosted verification and independent review are pending.
<!-- SECTION:FINAL_SUMMARY:END -->
