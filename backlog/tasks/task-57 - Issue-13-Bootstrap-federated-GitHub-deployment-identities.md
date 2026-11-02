---
id: TASK-57
title: Issue 13 - Bootstrap federated GitHub deployment identities
status: To Do
assignee: []
created_date: '2026-11-02T16:35:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
references:
  - https://github.com/vkaam/phonebuddy/issues/13
priority: high
type: task
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Trusted workflows require environment-scoped Azure access without long-lived credentials.

Issue: https://github.com/vkaam/phonebuddy/issues/13
Approved revision: 2026-11-01T09:24:42Z; body SHA-256 e49bb04e65519b8d40380feda8a7e091f4d3f2c94b25766da0812a8cd0d684e5.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded execution task; it does not authorize Azure deployment or issue closure.
Branch: agent/gh-13-1-azure-deploy-identities
Scope: .github/workflows/**; infra/**; docs/azure-delivery-policy.md; this task's own CLI-managed record.
Verify: From repository root run actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml and python3 -B scripts/check.py. Hosted GitHub/Azure checks must prove trusted OIDC login, fork denial and cross-environment write denial in a designated non-production environment; record run links and identity/role evidence without credentials.
Spec: Implement only issue #13's approved identity and federation controls. Keep untrusted pull-request code outside the Azure credential path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Distinct environment identities use restricted repository and environment federation with least-privilege Azure roles.
- [ ] #2 Trusted workflow authentication succeeds while fork PR access and cross-environment writes are rejected.
- [ ] #3 Bootstrap and GitHub environment configuration are reproducible or explicitly documented; credentials never enter logs.
<!-- AC:END -->
