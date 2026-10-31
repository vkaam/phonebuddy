---
id: TASK-34
title: Make local and hosted application checks produce complete evidence
status: To Do
assignee: []
created_date: '2026-10-31T18:40:00Z'
labels:
  - factory
  - autonomy
dependencies: []
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
