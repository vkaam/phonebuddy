---
id: TASK-71
title: Verify Azure pilot hosting through CI CD
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-03T17:55:00Z'
updated_date: '2026-11-12T11:58:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-59
  - TASK-62
references:
  - https://github.com/vkaam/phonebuddy/issues/15
modified_files:
  - backlog/tasks/task-71 - Verify-Azure-pilot-hosting-through-CI-CD.md
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Inspect the approved issue and trusted release configuration and identify source-bound evidence. 2. Execute two authorized pilot deployments through the trusted default-branch workflow and collect source, artifact, health, access, cleanup and cost evidence. 3. Run the declared checks, record evidence and remaining gaps, and publish the scoped PR for independent review and required checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
2026-11-12: Owner explicitly authorized both pilot deployments and a one-task exception to the durable lease requirement for TASK-71 in this Codex conversation. Live eligibility check passed against origin/main 6e58aa0bc47c8ff56a96834efef882e36e418c8f with claim_verified true. This exception does not establish a durable lease.

Pilot verification 2026-11-12: Trusted release run https://github.com/vkaam/phonebuddy/actions/runs/43176157247 attempt 2 is in progress against main 6e58aa0bc47c8ff56a96834efef882e36e418c8f; Bicep apply and exact-source revision verification succeeded, health observation pending. Readback found registry admin disabled, vault public access disabled and RBAC/purge protection enabled, and workload pull identity has AcrPull only at the registry scope. The shared France Central dev group budget reports EUR 1.767225 current monthly spend against EUR 10, not an isolated hosting cost. The group also contains data services and must not be deleted as task cleanup. No Static Web App was found in the subscription; the trusted workflow explicitly sets deployStaticSite=false, so the approved issue requirement remains unmet and needs triage. Local Bicep baseline passed. scripts/check.py failed on Windows due to npm invocation and a skipped Bash test; separate web tests also failed under local Node 26 and require investigation. No acceptance criterion is claimed complete.

Draft PR: https://github.com/vkaam/phonebuddy/pull/113. Static Web App gap and ongoing deployment were reported on issue #15: https://github.com/vkaam/phonebuddy/issues/15#issuecomment-6822788292.

Deployment update: run 43176157247 attempt 2 succeeded, including the 600-second health gate and exact revision verification; an independent HTTPS /ready probe returned ready=true and version 6e58aa0bc47c8ff56a96834efef882e36e418c8f. Its job log identifies source CI artifact release-image-43176003060-1 and locked registry digest sha256:58ae726e33f66d50171668ee9f38b2c1bc237689b7c39bd03cb634b43664d706. Attempt 3 has started as the authorized repeat. Attempt 2 logged upload of artifact 13941833351, but it became unavailable (HTTP 404) after rerun; do not claim its artifact is retained. Web lint, build and npm audit passed separately; the local Windows full baseline remains failed/incomplete.
<!-- SECTION:NOTES:END -->
