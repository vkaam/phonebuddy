# Issue and Backlog reconciliation — 2 November 2026

Reconciled all 37 GitHub issues (36 open, one closed) against default-branch
`d015e6a15d368c2ad1ef61b5d465b3cb43b35f24`, all 65 existing native task
records, relevant branches and the three open PRs (#55, #60, #61).
TASK-67 records the owner-authorized reconciliation and its review evidence.
This document is a dated audit, not another editable issue/task lifecycle source.
Use GitHub and Backlog for live state.

## Corrections

- Archived 26 unfinished imported records (TASK-16–TASK-30 and
  TASK-32–TASK-42) through Backlog CLI after adding their canonical issue
  references and explicit historical/needs-triage annotations. Preserved their
  To Do statuses, acceptance check states, IDs and native dependency history.
  They lacked approved atomic execution specifications; six factory snapshots
  also predated current governance acceptance. Archival does not complete them.
- Preserved already-archived TASK-5–TASK-14 and completed execution evidence.
  Existing Azure replacements TASK-57–TASK-65 retain their approved issue
  snapshots and dependency mapping from PR #70.
- Claimed TASK-57 for the existing identity work on
  `agent/gh-13-1-bootstrap-federated-identities`, draft
  [PR #55](https://github.com/vkaam/phonebuddy/pull/55), instead of scheduling a
  duplicate identity implementation. Its amended specification enumerates the
  six exact implementation/test/task paths; acceptance remains unchecked.
  Reconcile that PR's TASK-6 modification to TASK-57 while preserving the
  implementation.
- Retained original issue requirements and states. Progress reports link merge
  evidence and outstanding gates. Open issues with merged slices are not
  automatically complete; closure remains with the owner or an authorized
  completion controller.
- Preserved the original checkout's uncommitted archive moves by working in an
  isolated local clone. The managed-worktree tool could not resolve this
  repository, so it could not create a managed checkout.

## Complete issue mapping

Historical TASK identifiers in migrated issue titles are import provenance;
the current execution records can have different IDs.

| GitHub issue | Native records | Validated disposition |
| --- | --- | --- |
| [#12](https://github.com/vkaam/phonebuddy/issues/12) | TASK-5 (archived Done), TASK-45–TASK-47 | Closed; foundation evidence merged (#50/#52/#53/#54). |
| [#13](https://github.com/vkaam/phonebuddy/issues/13) | TASK-57; historical TASK-6 | In Progress, @codex; existing draft PR #55. Live identity gates pending. |
| [#14](https://github.com/vkaam/phonebuddy/issues/14) | TASK-58; historical TASK-7 | To Do; dependency-ready. |
| [#15](https://github.com/vkaam/phonebuddy/issues/15) | TASK-59; historical TASK-8 | To Do; blocked by declared native dependencies. |
| [#16](https://github.com/vkaam/phonebuddy/issues/16) | TASK-60; historical TASK-9 | To Do; blocked by declared native dependencies. |
| [#17](https://github.com/vkaam/phonebuddy/issues/17) | TASK-61; historical TASK-10 | To Do; blocked by declared native dependencies. |
| [#18](https://github.com/vkaam/phonebuddy/issues/18) | TASK-62; historical TASK-11 | To Do; blocked by declared native dependencies. |
| [#19](https://github.com/vkaam/phonebuddy/issues/19) | TASK-63; historical TASK-12 | To Do; blocked by declared native dependencies. |
| [#20](https://github.com/vkaam/phonebuddy/issues/20) | TASK-64; historical TASK-13 | To Do; blocked by declared native dependencies. |
| [#21](https://github.com/vkaam/phonebuddy/issues/21) | TASK-65; historical TASK-14 | To Do; blocked by declared native dependencies. |
| [#22](https://github.com/vkaam/phonebuddy/issues/22) | Historical TASK-16 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#23](https://github.com/vkaam/phonebuddy/issues/23) | Historical TASK-17 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#24](https://github.com/vkaam/phonebuddy/issues/24) | Historical TASK-19 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#25](https://github.com/vkaam/phonebuddy/issues/25) | Historical TASK-18 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#26](https://github.com/vkaam/phonebuddy/issues/26) | Historical TASK-20 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#27](https://github.com/vkaam/phonebuddy/issues/27) | Historical TASK-21 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#28](https://github.com/vkaam/phonebuddy/issues/28) | Historical TASK-22 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#29](https://github.com/vkaam/phonebuddy/issues/29) | Historical TASK-23 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#30](https://github.com/vkaam/phonebuddy/issues/30) | Historical TASK-24 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#31](https://github.com/vkaam/phonebuddy/issues/31) | Historical TASK-25 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#32](https://github.com/vkaam/phonebuddy/issues/32) | Historical TASK-27 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#33](https://github.com/vkaam/phonebuddy/issues/33) | Historical TASK-26 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#34](https://github.com/vkaam/phonebuddy/issues/34) | Historical TASK-28 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#35](https://github.com/vkaam/phonebuddy/issues/35) | Historical TASK-29 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#36](https://github.com/vkaam/phonebuddy/issues/36) | Historical TASK-30 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#37](https://github.com/vkaam/phonebuddy/issues/37) | TASK-43, TASK-44, TASK-66; historical TASK-32 | Governance/runbook/reconciliation merged. Runtime, owner/model access and cloud-input decisions remain incomplete. |
| [#38](https://github.com/vkaam/phonebuddy/issues/38) | Historical TASK-33 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#39](https://github.com/vkaam/phonebuddy/issues/39) | TASK-48–TASK-54; historical TASK-34 | Seven implementation slices merged. Aggregate acceptance still has the component-registration documentation gap. |
| [#40](https://github.com/vkaam/phonebuddy/issues/40) | Historical TASK-35 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#41](https://github.com/vkaam/phonebuddy/issues/41) | Historical TASK-36 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#42](https://github.com/vkaam/phonebuddy/issues/42) | Historical TASK-37 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#43](https://github.com/vkaam/phonebuddy/issues/43) | Historical TASK-38 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#44](https://github.com/vkaam/phonebuddy/issues/44) | Historical TASK-39 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#45](https://github.com/vkaam/phonebuddy/issues/45) | Historical TASK-40 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#46](https://github.com/vkaam/phonebuddy/issues/46) | Historical TASK-41 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#47](https://github.com/vkaam/phonebuddy/issues/47) | Historical TASK-42 | Open issue intake. Archived unfinished import; fresh atomic triage required before implementation. |
| [#65](https://github.com/vkaam/phonebuddy/issues/65) | TASK-56 | Merged PR #69; cold/warm measurements and checks recorded. Owner aggregate acceptance/closure remains. |

## Verification and remaining gates

The existing full local command passed against the clean default-branch source:

```sh
PLAYWRIGHT_BROWSERS_PATH=/private/tmp/phonebuddy-playwright-browsers python3 -B scripts/check.py
```

Evidence bundle:
`/private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-f1idvx3a/report.json`.
It records the unchanged source manifest, commands, versions and hashed logs:
35 Python tests, 5 required Node tests, 3 Chromium smoke tests, locked install,
npm audit, lint and build all pass. The first sandboxed attempt failed registry
access/browser launch; the authorized run with those prerequisites passed.
Local evidence remains a local baseline and does not replace hosted-only gates.

Current-main [Quality run 41498099939](https://github.com/vkaam/phonebuddy/actions/runs/41498099939)
succeeded on `d015e6a`. The advisory workflow on that main push was skipped;
that is not successful PR-check evidence. The reconciliation PR and updated
identity PR require their own successful final-head checks.

Issue #39 implementation is merged through PRs
[#56](https://github.com/vkaam/phonebuddy/pull/56),
[#57](https://github.com/vkaam/phonebuddy/pull/57),
[#63](https://github.com/vkaam/phonebuddy/pull/63),
[#64](https://github.com/vkaam/phonebuddy/pull/64),
[#66](https://github.com/vkaam/phonebuddy/pull/66),
[#67](https://github.com/vkaam/phonebuddy/pull/67) and
[#68](https://github.com/vkaam/phonebuddy/pull/68).
Its aggregate acceptance is still incomplete: the final clause of AC3 requires
explicit check registration and domain tests when a new component is added.
Current documentation lists future domain gates but does not explicitly state
that registration requirement. Triage a bounded documentation/aggregate-evidence
slice before claiming full completion. Do not restart the seven merged slices.

Issue #65 implementation is merged through
[PR #69](https://github.com/vkaam/phonebuddy/pull/69).
TASK-56 and `docs/quality-and-delivery.md` retain source-bound cold/warm timing
evidence, cache invalidation/trust constraints and passing checks. A cache miss
and cache hits both exercised the checks. The workload caches Playwright's
headless shell; npm caching was rejected after measurement. Owner aggregate
acceptance and issue closure are still distinct from the merged task.

Issue #37 retains merged governance/runbook slices TASK-43 and TASK-44
(PRs #48/#49/#51) and Azure migration reconciliation TASK-66 (PR #70).
The remaining runtime/model-access/owner/cloud decisions must be resolved before
the broader autonomy issue can complete. An archived unfinished prerequisite
continues to block dependent issue work; never mark it Done just to unblock a
scheduler.

These changes affect task records and this audit only. Application deployment,
health/recovery gates are inapplicable to the reconciliation itself; their
declared gates remain required for infrastructure/application tasks.

## Continuing development

1. Continue TASK-57 through existing draft PR #55. Required external gates remain
   reviewed Azure bootstrap, owner-configured main-only dev/test environments,
   federation/RBAC readback and successful trusted OIDC success/denial runs.
   Do not start a second identity PR.
2. TASK-58 (issue #14) is the only unassigned dependency-ready execution task
   after this reconciliation. Its pinned requirements, paths, verification and
   hosted/Azure gates remain in its native record.
3. TASK-59–TASK-65 remain blocked by their native predecessors. Issue #39 needs
   the bounded registration/aggregate-evidence slice described above; other
   product/factory issues require fresh atomic triage from current human intent.
4. Review and merge the reconciliation PR through normal controls, then update
   the development checkout from main while preserving unrelated local work.
   Branch-local task completion remains provisional until merge.
