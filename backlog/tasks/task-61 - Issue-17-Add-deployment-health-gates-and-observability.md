---
id: TASK-61
title: Issue 17 - Add deployment health gates and observability
status: To Do
assignee: []
created_date: '2026-11-02T16:36:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
references:
  - https://github.com/vkaam/phonebuddy/issues/17
priority: high
type: task
ordinal: 58000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/17
Approved revision: 2026-11-01T09:24:54Z; body SHA-256 8d4a38d23215c8706bc19f086c585b9ebcafe76dfe747de51edbbbd35951d749.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-17-1-deployment-health-gates
Scope: infra/**; .github/workflows/**; scripts/**; tests/**; docs/quality-and-delivery.md; docs/azure-delivery-policy.md; backlog/tasks/task-61 - Issue-17-Add-deployment-health-gates-and-observability.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted pilot runs inject unhealthy responses and missing telemetry, confirm alerts/failure evidence, and confirm healthy version/readiness passes after warm-up.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Telemetry, release annotations and alerts are provisioned in Bicep without logging secrets or call content.
- [ ] #2 Bounded readiness and smoke checks verify the deployed version and essential paths after warm-up.
- [ ] #3 Document error and latency thresholds and observation windows; missing telemetry blocks promotion and dependency outages are distinguishable.
- [ ] #4 Injected unhealthy responses and missing telemetry trigger failure evidence and alerts; healthy workloads pass.
<!-- AC:END -->
