---
id: TASK-6
title: Bootstrap federated GitHub deployment identities
status: In Progress
assignee:
  - '@codex'
created_date: '2026-10-29T20:04:00Z'
updated_date: '2026-11-01T14:22:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-4
  - TASK-5
references:
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - https://github.com/vkaam/phonebuddy/issues/13
modified_files:
  - backlog/tasks/task-6 - Bootstrap-federated-GitHub-deployment-identities.md
  - scripts/bootstrap_github_oidc.py
  - .github/workflows/azure-oidc-smoke.yml
  - tests/test_azure_oidc_bootstrap.py
  - infra/github-oidc.md
  - infra/README.md
priority: high
type: task
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Bootstrap environment-scoped GitHub Actions identities for approved issue #13.

Approved issue revision: https://github.com/vkaam/phonebuddy/issues/13 updated 2026-11-01T09:24:42Z; body SHA-256 e49bb04e65519b8d40380feda8a7e091f4d3f2c94b25766da0812a8cd0d684e5. Approval evidence: direct user approval in this conversation on 2026-11-01 to execute Issue #13 as written.

Branch: agent/gh-13-1-bootstrap-federated-identities.
Scope: a reproducible Azure bootstrap script and runbook; a trusted, environment-scoped OIDC smoke workflow; focused policy tests; and this task record through Backlog CLI. Bootstrap separate environment principals, bind only the repository/environment GitHub OIDC subject, and grant Azure access only at each approved environment resource-group scope. Do not add client secrets or production resource permissions. Production remains without Azure write access until an approved production scope exists.

Verify with the focused Python tests, repository quality checks, workflow lint, Azure FIC/role-assignment readback, and a trusted GitHub workflow run that succeeds only for its allowed environment and is denied on fork/cross-environment probes. Manual environment setup values must remain out of source and logs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Distinct environment identities use restricted repository and environment federation with least-privilege Azure roles.
- [ ] #2 Trusted workflow authentication succeeds while fork PR access and cross-environment writes are rejected.
- [ ] #3 Bootstrap and GitHub environment configuration are reproducible or explicitly documented; credentials never enter logs.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect current environment resource groups, Azure permissions, workflows and exact GitHub OIDC environment claims. 2. Implement a secret-free, idempotent bootstrap script and runbook for distinct federated identities with environment-scoped Azure role assignments. 3. Add a trusted main-only GitHub OIDC smoke workflow and regression tests that deny fork and cross-environment access. 4. Run local checks and, after reviewed setup, bootstrap/read back identities without printing private identifiers. 5. Ask the repository owner to enter the environment-scoped GitHub values if the available connector cannot configure environments, then exercise the smoke workflow. 6. Record evidence and complete TASK-6 only after the live authentication and denial tests pass; publish one PR and monitor its checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a dry-run-by-default Azure bootstrap script, dev/test environment OIDC smoke workflow, focused authorization policy tests, and a runbook with the repository-owner environment setup keys. Local verification: scripts/check.py and scripts/quality.py pass; full unittest suite passes (36 tests); git diff --check passes. actionlint is not installed locally and will be checked by PR CI. Azure identities and GitHub environments are not yet configured; the live OIDC success and cross-environment denial checks remain outstanding pending reviewed bootstrap and owner setup.

Published draft PR #55: https://github.com/vkaam/phonebuddy/pull/55. PR CI initially identified shellcheck SC2209 in the new workflow; fixed the assignment and reran on head 5bb5e4efe4231c0fae3ff0d103bf200a42957ad4. Quality and advisory risk checks both pass on that head. Bootstrap/runbook review, GitHub environment secrets/restrictions, Azure role/FIC readback, and live dev/test OIDC smoke runs remain outstanding.
<!-- SECTION:NOTES:END -->
