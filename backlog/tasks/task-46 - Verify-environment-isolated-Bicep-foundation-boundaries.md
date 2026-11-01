---
id: TASK-46
title: Verify environment-isolated Bicep foundation boundaries
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T11:26:00Z'
updated_date: '2026-11-01T11:33:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-45
references:
  - https://github.com/vkaam/phonebuddy/issues/12
  - infra/main.bicep
  - infra/modules/foundation.bicep
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - infra/README.md
  - https://github.com/vkaam/phonebuddy/pull/52
modified_files:
  - >-
    backlog/tasks/task-46 -
    Verify-environment-isolated-Bicep-foundation-boundaries.md
  - scripts/check_bicep.py
  - tests/test_bicep_preflight.py
  - infra/README.md
priority: high
type: task
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
This task verifies and documents the existing foundation-only isolation boundaries for approved GitHub issue #12; no application capacity or Azure resources will be provisioned. Approved issue revision: https://github.com/vkaam/phonebuddy/issues/12 updated 2026-11-01T09:24:47Z; body SHA-256 294ffca40d3b855da99756164687afc214bf018536d424f3fd98f1647ddc2c7c. Approval evidence: direct user instruction in this conversation on 2026-11-01 to continue the remaining infrastructure ticket. Branch: agent/gh-12-2-verify-dev-isolation. Scope: infra/main.bicep; infra/modules/foundation.bicep; infra/environments/dev.bicepparam; infra/environments/test.bicepparam; infra/environments/prod.bicepparam; scripts/check_bicep.py; tests/test_bicep_preflight.py; infra/README.md; and this task record through Backlog CLI. Verify: BICEP=/private/tmp/phonebuddy-bicep-0.34.44 python3 -B scripts/check_bicep.py; python3 -B -m unittest tests/test_bicep_preflight.py; git diff --check; required GitHub PR Quality check. Test/prod deployment is out of scope because their subscriptions and approved owner, budget and region are unresolved. Environment selection must fail closed; foundation resource-group names, tags and deployment scopes must distinguish dev/test/prod; outputs must expose no secrets; documentation must state no billable application capacity exists and test/prod need separate approvals.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Pinned Bicep checks validate all environment parameter files and prove exact environment selection, distinct deterministic foundation resource-group identity, and a secret-free output surface.
- [x] #2 Automated preflight checks cover mismatches and unresolved values; configured dev passes while test and prod remain not deployment-ready.
- [x] #3 The deployment guide documents the verified isolation boundary, absence of application capacity, and separate approvals and cleanup constraints for test/prod.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Compile the pinned Bicep templates and inspect the current environment-specific resource-group identity and output surface.
2. Add deterministic preflight checks and unit coverage for distinct dev/test/prod resource-group identities, exact parameter-file selection, and outputs that contain no secrets.
3. Update the foundation guide to state the tested boundary and the inputs and cleanup gates still required for test/prod.
4. Run pinned Bicep validation, focused unit tests, and diff checks; record any unsupported deployment evidence explicitly.
5. Open one PR for TASK-46, monitor required checks on the final head, and record verified completion through Backlog CLI.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a compiled-template contract check for the environment-specific deployment and resource-group names, environment tag, exact foundation input set, and sole resource-group-name output. Added positive and negative unit cases, including secret inputs/outputs and environment mismatch/unresolved values. Updated infra/README.md to describe the verified naming boundary, current dev resource-group-only deployment, and unresolved test/prod gates. Verification: pinned Bicep baseline passed; 9 focused unit tests passed; dev deployment-readiness passed; test and prod deployment-readiness both failed as expected on unresolved location; git diff --check passed. No Azure resources or billable application capacity were provisioned.

Draft PR #52 is open for TASK-46. The current PR checks must pass on the final published head before proposed completion.

Current published head 9180e6b8331e64ad2cc3ecafe046d224c2022f32 passed required Quality and advisory Risk report checks. Finalization updates only the CLI-managed task record; checks on that final head remain required.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Verified and documented the Bicep foundation boundary: each environment has a distinct deployment/resource-group identity and environment tag, only the resource-group name is exposed, and test/prod remain blocked until their inputs are approved. Pinned Bicep validation and all 9 focused unit tests passed; dev deployment readiness passed while test/prod failed closed on unresolved inputs. No application capacity or additional Azure resources were provisioned. PR #52 carries this change for review.
<!-- SECTION:FINAL_SUMMARY:END -->
