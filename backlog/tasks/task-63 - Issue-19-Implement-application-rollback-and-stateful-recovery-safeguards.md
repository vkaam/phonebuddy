---
id: TASK-63
title: Issue 19 - Implement application rollback and stateful recovery safeguards
status: To Do
assignee: []
created_date: '2026-11-02T16:36:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-61
  - TASK-62
references:
  - https://github.com/vkaam/phonebuddy/issues/19
priority: high
type: task
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Complete the human-approved Azure outcome described by this issue as one bounded execution slice.

Issue: https://github.com/vkaam/phonebuddy/issues/19
Approved revision: 2026-11-01T09:24:59Z; body SHA-256 816b8bcb2f162508a7fcc9d14a3bfbcb71cfd174cbab82a86415f58f69519029.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-19-1-release-recovery
Scope: .github/workflows/**; apps/web/**; infra/**; scripts/**; tests/**; docs/quality-and-delivery.md; backlog/tasks/task-63 - Issue-19-Implement-application-rollback-and-stateful-recovery-safeguards.md
Verify: From repository root run python3 -B scripts/check.py, python3 -B scripts/check_bicep.py and actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml. Hosted controlled failure injection verifies release recovery and alerts; first release and incompatible schema cases stop safely. An authorized operator exercises the immutable-release manual recovery path.
Spec: Preserve the issue's approved acceptance. Do not broaden scope or weaken review. External Azure and hosted checks are explicit acceptance gates and must be evidenced on the current source.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Failed candidate health restores eligible last-known-good application, frontend assets and configuration and verifies recovery.
- [ ] #2 Last-known-good state advances only after successful observation and is protected from concurrent runs and retries.
- [ ] #3 First deployment without a prior release, incompatible schemas and failed recovery stop promotion and alert; bounded retries prevent rollback loops.
- [ ] #4 Expand/contract database compatibility is enforced; destructive infrastructure or database rollback and backup restore are never blindly automated.
- [ ] #5 An authorized manual recovery workflow selects immutable releases and records operator and evidence; failure injection demonstrates automatic rollback.
<!-- AC:END -->
