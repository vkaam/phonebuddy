---
id: TASK-85
title: 'Issue 18 follow-up: Fix live Azure telemetry query'
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-11T12:17:00Z'
updated_date: '2026-11-11T12:34:00Z'
labels:
  - infrastructure
  - cicd
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/18
  - https://github.com/vkaam/phonebuddy/pull/97
  - https://github.com/vkaam/phonebuddy/pull/98
  - backlog/tasks/task-84
modified_files:
  - backlog/tasks/task-85 - Issue-18-follow-up-Fix-live-Azure-telemetry-query.md
  - scripts/health_gate.py
  - tests/test_health_gate.py
  - docs/azure-delivery-policy.md
priority: high
type: bug
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: The first two source-bound CI releases completed Bicep what-if and apply, and each passed 100 health requests with zero errors, but the Log Analytics telemetry gate failed. The second release (run 43007682723, main commit a355139d5c46096551232fe0197449753fa3318b) retained evidence artifact 13850061029 with telemetry event count 0 and diagnostic category cli_error, exit code 1, error_code null. PR #98 added bounded provider error-code extraction but the real Azure CLI failure still has no safe code, so identify the exact KQL/CLI failure and correct the live telemetry query before promoting a release.

Issue: https://github.com/vkaam/phonebuddy/issues/18
Approved revision: 2026-11-01T09:24:57Z; body SHA-256 eb438edc998e814bc7b7a9f879559a475e10b6ec63532edd171590ed8826e449.
Approval evidence: User authorized merging and fixing a deployment failure: “We can merge it and fix it if it fails there.”
Branch: agent/gh-18-3-live-telemetry-query-fix
Scope: scripts/health_gate.py; tests/test_health_gate.py; docs/azure-delivery-policy.md; backlog/tasks/task-85 - Issue-18-follow-up-Fix-live-Azure-telemetry-query.md
Verify: python3 -B scripts/run_required_unittests.py; BICEP=/tmp/bicep python3 -B scripts/check_bicep.py; actionlint .github/workflows/ci.yml .github/workflows/azure-deploy.yml .github/workflows/pr-safety.yml; hosted main CI and Azure release must prove exact-source Bicep deployment and a passing telemetry gate with at least 100 version-matched events and zero unhealthy events.
Change control: Any further files require a recorded triage amendment.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The actual live Log Analytics CLI/query failure is identified and corrected, with regression coverage that matches the deployed workspace schema and query behavior.
- [ ] #2 Diagnostics expose only bounded, safe provider metadata and never raw query output, workspace identifiers, or tokens.
- [ ] #3 Required local checks and PR checks pass, and a main-triggered exact-source Bicep release records at least 100 version-matched telemetry events with zero unhealthy events.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Compare the live failure evidence and current query with prior trusted health-gate work and official Azure Monitor Container Apps table/query documentation. 2. Identify the exact table or KQL/CLI incompatibility and verify the corrected query against the documented deployed schema. 3. Add focused regression tests and update the delivery policy without exposing raw provider output. 4. Run required unit, Bicep and actionlint checks and publish a single scoped PR. 5. After merge, verify the next source-bound main CI deployment has a passing 600-second health window and at least 100 version-matched telemetry events with zero unhealthy events; keep the task active until then.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Research confirms the configured Bicep route is Azure Monitor with Dedicated diagnostic tables, matching the documented ContainerAppConsoleLogs schema (ContainerAppName and Log); that configuration predates this release. The current artifact still reports cli_error/exit 1/error_code null. Earlier trusted run 42904952753 classified the same query as throttled, while later runs show an unclassified CLI failure. The current diagnostic parser examines stderr only, so the next scoped change will inspect both CLI output streams and emit only allowlisted provider codes/fixed categories; raw output remains excluded.

Scoped diagnostics now inspect bounded prefixes of both stderr and stdout; reports include only an allowlisted error code, fixed category, exit code and which stream carried the output. Known throttling codes are classified for existing bounded retries. Focused health-gate tests pass (17 tests); required repository unit suite passes (130 tests), Bicep checks pass, actionlint passes, and git diff --check passes. The exact live Azure error remains unproven until the updated diagnostic runs in the source-bound main deployment; keep the task active.
<!-- SECTION:NOTES:END -->
