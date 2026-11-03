---
id: TASK-59
title: Issue 15 - Provision Azure pilot application hosting
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-03T17:28:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-57
references:
  - https://github.com/vkaam/phonebuddy/issues/15
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - infra/modules/hosting.bicep
  - https://github.com/vkaam/phonebuddy/pull/77
modified_files:
  - infra/release-test/server.py
  - infra/release-test/Dockerfile
  - infra/hosting.bicep
  - infra/release-test/README.md
  - tests/test_release_test.py
  - scripts/check_bicep.py
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Design a resource-group-scoped hosting module with a Container Apps environment and versioned readiness workload, Basic registry, Static Web App, RBAC-enabled Key Vault, managed identities and the networking required by those services. Use managed identity for registry pulls and grant only the required registry role; keep registry admin and vault public secret exposure disabled. 2. Add deterministic, environment-scoped names and tags, secret-free outputs and safeguards, and document the deployment, access, cleanup and cost boundaries. 3. Validate compiled templates and failure cases with the required local checks. 4. After explicit authorization of the design and live deployment, review what-if, deploy twice to the designated pilot, and verify version, readiness, access, cleanup and cost evidence. 5. Publish and monitor the PR; leave acceptance open until every live gate is verified.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Dependencies TASK-5 and TASK-57 are completed on origin/main. No existing TASK-59 PR was found. The proposed hosting and identity design requires review before implementation; live deployment is not yet authorized by the recorded intake.

2026-11-03: User approved the proposed hosting design in this chat. Live deployment remains separately unauthorized. Live claim verification passed against origin/main f26280e1206885bb12ebe1fafcfe4d2e867562c8; no competing claim was found.

Implemented a draft staged hosting template and release-test endpoint. Pinned Bicep build/lint and baseline security checks pass; focused HTTP test passes with loopback access. Azure deployment, image publication, readback, cost and cleanup evidence are not authorized or performed. The template does not enforce image digest/registry or nonempty release version, and needs further hardening and review before live use. The Container Apps environment uses managed public networking; the vault has no private endpoint or secret access. Acceptance remains open.

Draft PR #77: https://github.com/vkaam/phonebuddy/pull/77. Full local baseline passed on the implementation source (phonebuddy-quality-kv8ftewf); pinned Bicep checks and focused endpoint test passed. Docker daemon unavailable; image build not verified. Live Azure gates and template hardening remain outstanding.

2026-11-03: Docker image built from a digest-pinned base and /ready returned the expected version from inside the container. The host-forwarded probe returned an empty reply and does not establish host reachability. Hosting template now constructs the image from the provisioned registry and a required 64-character digest, and requires a nonempty version; the compiled-template check verifies these constraints. The vault remains inaccessible on public networking with no runtime secrets or private endpoint; private secret access requires a separately reviewed design. Live deployment and evidence remain outstanding.
<!-- SECTION:NOTES:END -->
