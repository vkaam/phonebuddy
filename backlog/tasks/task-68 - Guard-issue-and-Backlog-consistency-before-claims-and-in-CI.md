---
id: TASK-68
title: Guard issue and Backlog consistency before claims and in CI
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T18:44:00Z'
updated_date: '2026-11-02T19:22:00Z'
labels:
  - governance
  - validation
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/72
modified_files:
  - scripts/backlog_consistency.py
  - tests/test_backlog_consistency.py
  - scripts/check.py
  - tests/test_check.py
  - .github/workflows/ci.yml
  - >-
    backlog/tasks/task-57 -
    Issue-13-Bootstrap-federated-GitHub-deployment-identities.md
  - AGENTS.md
  - docs/issue-backlog-governance.md
  - docs/quality-and-delivery.md
priority: high
type: chore
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Written governance did not prevent inconsistent imports, stale task claims and incomplete completion/migration evidence. Add one read-only guard for the concrete failure modes under approved issue #72.
Issue: https://github.com/vkaam/phonebuddy/issues/72
Approved revision: 2026-11-02T18:43:48Z; UTF-8 body SHA-256 d050e03e82f9d6a28a7677f4de8f6b64a232bed75d4feb4fa53adaa5baf112ec.
Approval evidence: vkaam directly instructed "Please fix that" in this Codex conversation on 2026-11-02 after approving the task/claim/completion/migration safeguard proposal. This bounded slice requires no runtime activation decisions from issue #37 or leases from #41; those broader gates remain unchanged.
Branch: agent/gh-72-1-backlog-consistency
Scope: scripts/backlog_consistency.py; tests/test_backlog_consistency.py; scripts/check.py; tests/test_check.py; .github/workflows/ci.yml; AGENTS.md; docs/issue-backlog-governance.md; docs/quality-and-delivery.md; backlog/tasks/task-57 - Issue-13-Bootstrap-federated-GitHub-deployment-identities.md; this task's own CLI-managed record.
Verify: From repository root run python3 -B scripts/run_required_unittests.py; python3 -B scripts/quality.py; python3 -B scripts/backlog_consistency.py --offline; python3 -B scripts/backlog_consistency.py --base origin/main; PLAYWRIGHT_BROWSERS_PATH=/private/tmp/phonebuddy-playwright-browsers python3 -B scripts/check.py; /private/tmp/phonebuddy-qa-tools/actionlint .github/workflows/ci.yml .github/workflows/pr-safety.yml; git diff --check. Live checks require a read-only GitHub connection and fresh origin/main/relevant branch refs; complete local checks require Node/npm/registry and pinned Chromium. Hosted Quality and all advisory reports must pass on the final head. Demonstrate seeded missing/stale metadata, conflicting claims, false dependency completion and broken migration edges fail with stable reasons, while valid distinct slices pass.
Spec: Treat native task records as read-only data and never use issue text as executable instructions. Preserve existing native schema and historical completion records. Import records lacking execution specifications are reported as ineligible; changed/new execution records are held to current policy. Fetch live issue/branch/PR state with read-only access and fail closed on unavailable/incomplete evidence. CI uses an unprivileged read-only token, never a privileged event workflow or secret. A point-in-time guard does not create an atomic lease or authorize merges/deployments. Do not bundle PR #71's pending migration into this implementation.

Triage amendment v2 (2026-11-02): the live guard correctly detected main's stale TASK-57 branch reservation, while approved reconciliation PR #71 and identity PR #55 already agree on the current claim. Under the owner's existing explicit reconciliation authorization and current preventive-fix instruction, include only that previously approved TASK-57 metadata correction so this independent guard PR can pass against the real live claim. Preserve TASK-57's current issue requirements, plan, implementation evidence and unchecked acceptance, and do not bundle the 26 archive moves or other PR #71 changes. This is a one-time CLI-managed reconciliation, not an automatic write capability of the guard.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Executable tasks require canonical approved issue revision/evidence, unique branch, explicit paths, verification and native acceptance; historical imports remain ineligible, and stale/cancelled intent blocks claims.
- [ ] #2 Live branch/PR reconciliation detects duplicate ownership/PRs and unsafe task reuse, permits distinct native slices for one issue, and fails closed when evidence is unavailable or incomplete.
- [ ] #3 Dependencies require verified default-branch completion with checked acceptance and merged evidence for execution records; unknown/ambiguous/cyclic identities, archived unfinished tasks and branch-local Done cannot authorize claims.
- [ ] #4 Migration validation requires explicit replacement or intake-only disposition and detects stale downstream dependencies while preserving historical statuses.
- [ ] #5 The same guard is documented for local/pre-claim use and enforced by CI; source-bound JSON, negative regression cases and current-head checks verify behavior without mutating task/issue/claim state.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Read native record formats, current policy, quality runner and CI; define compatible read-only parsing and source-bound reports.
2. Implement schema, live revision/claim, default-branch completion and migration/dependency checks with actionable failure reasons.
3. Add adversarial regression fixtures and register the guard in local evidence, CI and pre-claim instructions.
4. Exercise real repository/live API checks and seeded failures, run complete local/hosted verification, publish one PR and finalize after successful checks.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented a GET-only consistency guard with restricted native-frontmatter parsing, approved issue digest checks, branch/PR claim reconciliation, default-branch/merged dependency evidence, migration mapping/stale-edge checks, scope enforcement and source-bound JSON. Historical imports remain ineligible and cannot obtain an exemption by backdating new records. Registered offline structure in scripts/check.py and live validation inside CI Quality with a read-only token; documented mandatory pre-claim use and point-in-time/approval/lease limits. Applied only the already-approved TASK-57 claim correction from PR #71 and normalized its Scope line without changing allowed paths or acceptance. No archive migration was bundled. Focused 24 guard regressions and the full 59-test Python suite passed; actionlint and diff/repository checks passed. Full local quality bundle passed (35 original plus 24 guard tests, 5 Node tests, 3 browser tests, install/audit/lint/build); evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-izly3mmn/report.json. A real live pre-claim run returned pass and claim_verified true with the existing TASK-57 claim observed; final source-bound validation will be repeated after publication.
<!-- SECTION:NOTES:END -->
