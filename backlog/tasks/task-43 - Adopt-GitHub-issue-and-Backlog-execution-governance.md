---
id: TASK-43
title: Adopt GitHub issue and Backlog execution governance
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T09:47:00Z'
updated_date: '2026-11-01T09:58:00Z'
labels:
  - factory
  - governance
dependencies: []
references:
  - https://github.com/vkaam/phonebuddy/issues/37
  - https://github.com/vkaam/phonebuddy/pull/48
documentation:
  - docs/issue-backlog-governance.md
modified_files:
  - docs/issue-backlog-governance.md
  - AGENTS.md
  - docs/autonomous-development-plan.md
  - docs/software-plan.md
  - docs/quality-and-delivery.md
  - docs/templates/work-specification.md
  - docs/templates/acceptance-evidence.md
  - .github/pull_request_template.md
  - .github/CODEOWNERS
  - README.md
priority: high
type: docs
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Human-approved on 1 November 2026 in this chat: adopt GitHub Issues for high-level intent and native Backlog.md for atomic execution, incorporating the reviewed governance corrections. This documentation slice contributes to issue #37 without completing its broader runtime, owner, and access decisions.

Issue: https://github.com/vkaam/phonebuddy/issues/37
Issue revision: 2026-11-01T09:52:42Z; SHA-256 e89fb516577a1895faad3736db993a071936a91605451ac43357ba337c217deb. Human approval: 1 November 2026 instruction in this chat to update the reviewed governance; this snapshot includes those explicitly authorized issue amendments.
Branch: agent/gh-37-1-governance
Scope: AGENTS.md; docs/issue-backlog-governance.md; docs/software-plan.md; docs/autonomous-development-plan.md; docs/quality-and-delivery.md; docs/templates/work-specification.md; docs/templates/acceptance-evidence.md; .github/pull_request_template.md; .github/CODEOWNERS; README.md; this task's CLI-managed record. Authorized external scope: governance requirements in GitHub issues #37, #41, #42, #45, #46, #47, preserving existing intent and dependencies.
Verify: from repository root, python3 -B scripts/check.py; git diff --check; verify the staged diff excludes pre-existing migration paths and compare their saved hashes; verify updated issue bodies against their prior content.
Spec: Preserve native Backlog IDs and CLI ownership, human issue authority, staged review controls, and unrelated migration changes. Document runtime controls as required future implementation rather than claiming they exist.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Repository instructions and templates consistently separate human-owned issue intent from CLI-managed atomic execution, including issue revision, scope, verification and acceptance evidence.
- [x] #2 Governance defines approved intake, idempotent decomposition, dependency and lease handling, controlled amendments, branch-local completion and aggregate issue closure without changing merge authority.
- [x] #3 The autonomy and software plans and relevant GitHub issue requirements align with the governance; archived migration records and unrelated working-tree changes remain unchanged.
- [x] #4 Documentation and native task records pass relevant local checks and current-head hosted CI and are published through a reviewable PR that references the parent issue without closing it.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Preserve the existing migration and pin issue context; adopt the human-approved dual-plane governance in repository instructions and a detailed policy document.
2. Align the plans, specification/evidence/PR templates and policy ownership, using native Backlog task IDs and CLI edits throughout.
3. Amend only the relevant GitHub issue requirements, preserving their existing descriptions, dependencies and acceptance states; refresh the approved parent snapshot.
4. Validate documentation, native metadata and preserved migration hashes, publish only this slice, monitor final-head CI and finalize the execution task without closing its parent issue.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated governance acceptance requirements in issues #37, #41, #42, #45, #46 and #47 under the user instruction. Preserved original acceptance states and all dependency/block/reference sections; imported Backlog lifecycle metadata is explicitly historical. Parent issue stays open. Refreshed the approved requirements snapshot after these authorized amendments.

AC1/AC2: reviewed AGENTS, detailed governance, plan and specification/evidence/PR templates for native task schema, approved revisions, bounded scope, amendments, leases and aggregate closure. Native TASK-43 metadata validated through CLI JSON. AC3: six relevant GitHub issue bodies re-read and verified, original criteria/states and dependency sections preserved; adopted GitHub direction supersedes the Azure DevOps proposal. All 72 pre-existing migration paths match their preservation hashes. Local scripts/check.py passed repository checks and 24 Python tests with stable source; git diff --check passed. Runtime enforcement is explicitly future work. AC4 awaits publication and final-head hosted CI.

Published draft PR https://github.com/vkaam/phonebuddy/pull/48 with neutral Refs #37 linkage; it does not close the parent. The existing archive migration remains unstaged and unchanged. Hosted checks are pending; maintainer review and runtime enforcement remain outstanding.

AC4: draft PR #48 published with no auto-closing issue references (GitHub GraphQL closingIssuesReferences empty). Commit c79253a passed Quality (CI run 41295294958) and advisory reporting (41295294979), verified by commit-bound check-run API. Final Backlog metadata will be committed and pushed, then all checks reverified for the final head. Parent issue #37 and all five related issues remain open; maintainer review is outstanding. Existing archive migration stays unstaged.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Adopted the user-approved GitHub Issues control plane and native Backlog execution governance across AGENTS, the detailed policy, plans, quality guidance and templates, with policy owner coverage. Updated governance requirements in issues #37, #41, #42, #45, #46 and #47 while preserving existing criteria, dependencies and open states. TASK-43 is the atomic issue-linked execution slice; its completion remains proposed until PR merge and does not close #37. Local repository checks and 24 Python tests passed, native metadata and issue linkage validated, all 72 pre-existing migration paths preserved, and initial hosted Quality/advisory reporting passed. PR: https://github.com/vkaam/phonebuddy/pull/48. Maintainer review and future runtime enforcement remain outstanding; no protection, merge or deployment authority changed.
<!-- SECTION:FINAL_SUMMARY:END -->
