---
id: TASK-59
title: Issue 15 - Provision Azure pilot application hosting
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:36:00Z'
updated_date: '2026-11-03T17:57:00Z'
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
  - TASK-71
modified_files:
  - infra/release-test/server.py
  - infra/release-test/Dockerfile
  - infra/hosting.bicep
  - infra/release-test/README.md
  - tests/test_release_test.py
  - scripts/check_bicep.py
  - backlog/tasks/task-71 - Verify-Azure-pilot-hosting-through-CI-CD.md
priority: high
type: task
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Implement the hosting foundation for issue #15 so it can be reviewed and merged before trusted CI/CD verification.

Issue: https://github.com/vkaam/phonebuddy/issues/15
Approved revision: 2026-11-01T09:24:49Z; body SHA-256 3990d679f2058124599c9c0e4d518017736c3f9c5e1b3e238c381d3c7ee7c60d.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded native task; it does not authorize deployment, merge or issue closure.
Branch: agent/gh-15-1-azure-pilot-hosting
Scope: infra/**; scripts/**; tests/**; docs/azure-delivery-policy.md; docs/quality-and-delivery.md; backlog/tasks/task-59 - Issue-15-Provision-Azure-pilot-application-hosting.md; backlog/tasks/task-71 - Verify-Azure-pilot-hosting-through-CI-CD.md.
Verify: From repository root run python3 -B scripts/check.py and python3 -B scripts/check_bicep.py; build the release-test image with Docker and exercise its readiness response and version. Required hosted checks and independent review apply on the final PR head. Live deployment and evidence are tracked in TASK-71 after TASK-62.
Spec: User-approved triage split on 2026-11-03: TASK-59 covers the hosting implementation and local verification; TASK-71 retains all live Azure acceptance after TASK-62. Issue-level acceptance remains unchanged. No deployment, merge or issue closure is authorized by the split.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The Bicep hosting template compiles and describes the Container Apps environment, registry, Static Web App, Key Vault, identity and required service networking with documented access boundaries.
- [x] #2 The release-test image builds and its readiness endpoint returns a configured version without secrets; the template uses the intended registry and a digest-qualified image reference.
- [ ] #3 The implementation documents administration, deployment prerequisites, cleanup boundaries and cost considerations, and the required local and hosted checks pass.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement the staged hosting resources and versioned release-test workload. 2. Verify compiled security and image contracts, build and exercise the container, and document boundaries. 3. Publish PR #77 for independent review with TASK-71 retaining live deployment evidence after TASK-62.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Dependencies TASK-5 and TASK-57 are completed on origin/main. No existing TASK-59 PR was found. The proposed hosting and identity design requires review before implementation; live deployment is not yet authorized by the recorded intake.

2026-11-03: User approved the proposed hosting design in this chat. Live deployment remains separately unauthorized. Live claim verification passed against origin/main f26280e1206885bb12ebe1fafcfe4d2e867562c8; no competing claim was found.

Implemented a draft staged hosting template and release-test endpoint. Pinned Bicep build/lint and baseline security checks pass; focused HTTP test passes with loopback access. Azure deployment, image publication, readback, cost and cleanup evidence are not authorized or performed. The template does not enforce image digest/registry or nonempty release version, and needs further hardening and review before live use. The Container Apps environment uses managed public networking; the vault has no private endpoint or secret access. Acceptance remains open.

Draft PR #77: https://github.com/vkaam/phonebuddy/pull/77. Full local baseline passed on the implementation source (phonebuddy-quality-kv8ftewf); pinned Bicep checks and focused endpoint test passed. Docker daemon unavailable; image build not verified. Live Azure gates and template hardening remain outstanding.

2026-11-03: Docker image built from a digest-pinned base and /ready returned the expected version from inside the container. The host-forwarded probe returned an empty reply and does not establish host reachability. Hosting template now constructs the image from the provisioned registry and a required 64-character digest, and requires a nonempty version; the compiled-template check verifies these constraints. The vault remains inaccessible on public networking with no runtime secrets or private endpoint; private secret access requires a separately reviewed design. Live deployment and evidence remain outstanding.

Triage amendment 2026-11-03: The user explicitly approved splitting implementation from live verification so the reviewed hosting PR can merge before CI/CD deployment. TASK-59 is limited to hosting source, local verification and review; a separate issue #15 task will retain deployment, reachability, access, repeatability, cleanup and cost acceptance after TASK-62. Issue-level acceptance is unchanged. This amendment authorizes adding that CLI-created follow-up task record to PR #77; no deployment, merge or issue closure is authorized.

Split verification: compiled Bicep and contract checks passed; the digest-pinned image built locally and its readiness endpoint returned local-check inside the container. Full local baseline passed after task metadata corrections (phonebuddy-quality-j89ii9ny). TASK-71 retains live provisioning, external reachability, access readback, repeat deployment, cleanup and cost. Host-forwarded local probe returned an empty response; this is not evidence of deployed reachability. Final hosted checks and independent review remain required.
<!-- SECTION:NOTES:END -->
