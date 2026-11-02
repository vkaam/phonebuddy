---
id: TASK-59
title: Issue 15 - Provision Azure pilot application hosting
status: To Do
assignee: []
created_date: '2026-11-02T16:36:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-57
references:
  - https://github.com/vkaam/phonebuddy/issues/15
priority: high
type: task
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/15
Approved revision: 2026-11-01T09:24:49Z; body SHA-256 3990d679f2058124599c9c0e4d518017736c3f9c5e1b3e238c381d3c7ee7c60d.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-15-1-azure-pilot-hosting
Scope: infra/**; scripts/**; tests/**; docs/azure-delivery-policy.md; docs/quality-and-delivery.md; backlog/tasks/task-59 - Issue-15-Provision-Azure-pilot-application-hosting.md
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py. In the authorized pilot environment, deploy twice and verify the minimal release-test workload's expected version and readiness endpoint; retain deployment, access-scope, cleanup and cost evidence.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Bicep provisions Container Apps environment, registry, Static Web App, Key Vault, identities and required networking.
- [ ] #2 A minimal version-identifying release-test workload is reachable and exposes readiness without secrets.
- [ ] #3 Runtime access is scoped, administration is restricted, and repeat deployment, cleanup boundaries and baseline cost are demonstrated.
<!-- AC:END -->
