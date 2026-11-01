---
id: TASK-44
title: Document the factory operating contract and bootstrap runbook
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T10:18:00Z'
updated_date: '2026-11-01T11:16:00Z'
labels:
  - factory
  - autonomy
dependencies:
  - TASK-43
references:
  - https://github.com/vkaam/phonebuddy/issues/37
documentation:
  - docs/issue-backlog-governance.md
modified_files:
  - docs/agentic-development-contract.md
priority: high
type: docs
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/37
Issue revision: 2026-11-01T09:52:42Z; SHA-256 e89fb516577a1895faad3736db993a071936a91605451ac43357ba337c217deb. Approval evidence: direct user instruction in this Codex chat on 2026-11-01 to start implementing the first guardrails and agentic-development ticket.
Branch: agent/gh-37-2-contract-bootstrap
Scope: docs/agentic-development-contract.md and the native Backlog task record only.
Verify: from repository root, python3 -B scripts/check.py; git diff --check; manually verify runbook commands and trusted sources against the checkout and confirm the Groma scanner statement against .groma/config.json.
Spec: Document the operating authority, eligible-work boundary, trusted instructions, tool/path and approval boundaries, stop/resume/escalation rules, known owner/model/runtime status and unresolved prerequisites. Include a reproducible bootstrap flow with current build/check commands and architecture-context/Groma coverage. Do not install a runtime, change repository protections, expand merge authority, run a first Groma scan, or curate architecture.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 The contract states GitHub Issues as the intent control plane and native Backlog tasks as the execution plane, and separates unattended PR creation, human-approved merging, and any future separately approved no-per-PR-approval lane.
- [x] #2 Eligible work, trusted instruction hierarchy, allowed tools and paths, approval gates, stop/resume conditions, and escalation ownership are explicit; unknown scope is ineligible and no new authority is implied.
- [x] #3 Known facts are distinct from unresolved factory owner, independent reviewer, model access, tenant/subscription, region, quota, and spend/retention limits; the document invents no approval.
- [x] #4 The bootstrap runbook lists verified local and hosted check commands, trusted project instructions, architecture context sources, and configured Groma scanner coverage without running a first scan or curating architecture.
- [x] #5 The document stays within approved file scope and passes its declared repository checks.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Record the operating contract from approved repository policy and label unknown owners/access/limits as unresolved. 2. Write a single scoped bootstrap and contract document using commands and sources verified in the checkout, including configured Groma scanner coverage. 3. Record the changed path immediately, then run the task-declared checks and prepare a draft PR with outstanding review gates stated.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added the scoped operating contract and bootstrap runbook; repository and Groma configuration facts are labeled with their source, and unresolved owner/access/limit decisions remain explicit.

Verification: python3 -B scripts/check.py passed and emitted /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-wt483w9a/report.json; git diff --check passed. CI workflow and web commands were checked against .github/workflows/ci.yml; Groma coverage was checked against .groma/config.json (scanners: []). Human review is still required for proposed policy and unresolved factory owner/model/tenant/region/quota/budget decisions.

Dependency reconciliation: TASK-43 is Done and merged in the verified default-branch baseline (169f9e5). The migrated TASK-32 record is not restored or treated as a dependency; TASK-44 is a fresh issue-linked slice.

Published draft PR https://github.com/vkaam/phonebuddy/pull/49. Head 1cd6c2fca5a2c379b593d1478da115c4409c0995 is one commit above the freshly fetched main 169f9e553401f172f806bbb83c29092214229df7; GitHub compare lists only docs/agentic-development-contract.md and this task record. The PR is draft and issue #37 remains open. Outstanding: maintainer review and decisions on factory/escalation owners, model access, tenant/subscription, region, quota, budgets, and evidence retention; no runtime or merge authority is enabled.

User confirmation: PR https://github.com/vkaam/phonebuddy/pull/49 was accepted and merged into main at 91e662e. Current main contains docs/agentic-development-contract.md; python3 -B scripts/check.py and git show --check origin/main passed after merge. Hosted Quality and Risk report (advisory) passed on the final reported PR branch head 77dd81517ec7425bdd88ea1c9dc1973822c82b80. User authorized a metadata-only follow-up PR to publish task finalization after the merge. The unresolved runtime, owner, model access, tenant, region, quota, budget, and retention decisions remain outside this documentation task and issue #37 remains open.

Finalization validation on the branch carrying the Done status: python3 -B scripts/check.py passed; evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-eujymakf/report.json. git diff --check passed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Documented the agentic-development operating boundary and bootstrap runbook, including eligible-work rules, trusted context, scoped tools and paths, approval and escalation gates, known policy ownership, unresolved cloud/runtime inputs, current local and hosted verification, and the configured Groma scanner coverage. Verified the full source checks locally and hosted Quality plus advisory risk reporting on the PR branch. PR #49 was accepted and merged to main at 91e662e. No runtime, permissions, protections, merge authority, or parent issue state changed; issue #37 remains open for its remaining acceptance. A metadata-only follow-up PR is authorized to publish this task status after the implementation merge.
<!-- SECTION:FINAL_SUMMARY:END -->
