---
id: TASK-71
title: Verify Azure pilot hosting through CI CD
status: To Do
assignee: []
created_date: '2026-11-03T17:55:00Z'
updated_date: '2026-11-03T17:56:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
  - TASK-62
references:
  - https://github.com/vkaam/phonebuddy/issues/15
priority: high
type: task
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Verify issue 15 hosting from merged source through trusted CI/CD after implementation and deployment automation are complete.

Issue: https://github.com/vkaam/phonebuddy/issues/15
Approved revision: 2026-11-01T09:24:49Z; body SHA-256 3990d679f2058124599c9c0e4d518017736c3f9c5e1b3e238c381d3c7ee7c60d.
Approval evidence: The user approved splitting TASK-59 into implementation and post-CI/CD verification in this Codex chat on 2026-11-03. This does not authorize deployment, merge or issue closure.
Branch: agent/gh-15-2-pilot-hosting-verification
Scope: backlog/tasks/task-71 - Verify-Azure-pilot-hosting-through-CI-CD.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py; after explicit deployment authorization, use the trusted default-branch CI/CD workflow in the designated pilot, deploy twice, check version and readiness, and retain deployment, access-scope, cleanup and cost evidence. Required hosted checks and independent review apply to the verification PR.
Spec: TASK-59 implementation and TASK-62 automation must be completed on default branch. Application changes require separate triage. Issue-level acceptance remains unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The approved pilot resources and required networking are provisioned from the merged hosting source through the trusted CI/CD path, and deployment evidence identifies the source and artifacts.
- [ ] #2 The release-test workload is reachable over HTTPS, returns the expected version and exposes readiness without secrets.
- [ ] #3 Readback demonstrates scoped runtime access and restricted administration; repeat deployment, cleanup boundaries and baseline cost are evidenced.
<!-- AC:END -->
