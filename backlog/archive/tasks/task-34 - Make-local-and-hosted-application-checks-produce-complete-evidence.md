---
id: TASK-34
title: Make local and hosted application checks produce complete evidence
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
updated_date: '2026-11-02T18:21:00Z'
labels:
  - factory
  - autonomy
  - historical-import
  - needs-triage
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/39
documentation:
  - docs/autonomous-development-plan.md
priority: high
type: chore
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
scripts/check.py currently runs only repository Python checks, while hosted Quality also tests and builds the React shell. There is no lint command, browser behavior suite, or npm dependency update entry. A green local bundle is insufficient input for an autonomous coding decision.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 One documented command runs the applicable locked web install, configuration tests, strict type check, build, lint and browser route, missing-config and keyboard smoke tests, as well as baseline checks; local and hosted evidence explicitly identify extra platform-only gates.
- [ ] #2 Each required check records source identity, command, toolchain and dependency versions, outcomes and logs; missing, skipped, timed-out and failed applicable checks cannot produce a complete passing bundle.
- [ ] #3 Dependency vulnerability and update coverage includes npm as well as Actions, with a reviewed handling policy for findings; adding a component requires an explicit check registration and domain tests rather than silently inheriting web coverage.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migration reconciliation, 2026-11-02 (TASK-67): This record is the historical issue import, not an approved executable slice. Canonical human intent is https://github.com/vkaam/phonebuddy/issues/39 (observed 2026-11-01T09:25:59Z; UTF-8 body SHA-256 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2). Preserve its unchecked historical criteria and native dependency history; current issue acceptance supersedes the imported snapshot. New application work requires fresh atomic CLI-managed tasks with approved requirements, explicit paths and verification, plus dependency remapping through triage. Archival does not satisfy this unfinished task or its dependent issue gates. Implementation slices TASK-48 through TASK-54 are merged in PRs #56/#57/#63/#64/#66/#67/#68. Aggregate issue #39 acceptance remains incomplete: explicitly documenting component-specific check registration is still outstanding; local web coverage cannot stand in for new domains.
<!-- SECTION:NOTES:END -->
