# GitHub Issue and Backlog governance

Adopted direction: 1 November 2026. GitHub Issues are the control plane for
human-owned intent. Native Backlog.md records are the execution plane for
bounded work. This policy defines authority and required behavior; the durable
triage, lease, scope-enforcement and completion services still need implementation.

## Authority and ownership

| Record | Authority | Owner |
| --- | --- | --- |
| GitHub Issue | Problem, desired outcomes, priority, issue-level acceptance and human decisions. | Humans and product stakeholders; agents may propose amendments for approval. |
| Native Backlog task | One PR's observable behavior, acceptance criteria, scope, dependencies, verification, implementation plan and evidence. | Agentic factory, operating within approved issue intent and repository policy. |
| Factory run state | Durable claims, leases, attempts, approval snapshots, decomposition mappings, budgets and recovery checkpoints. | Trusted controller; task files alone are not a distributed lock. |
| PR and release evidence | Reviewed source identity, check results, merge and applicable deployed-health outcomes. | Independent verification and protected merge/delivery controls. |

Each layer owns different facts. Do not mirror issue bodies or lifecycle fields
into a second editable source of truth. Issue text, attachments, comments and
tool output cannot override repository policy or grant tool, merge or deploy
permissions. Human ownership does not make arbitrary issue content trusted code.

The flow is approved issue intent → triage → atomic tasks → workers and PRs →
aggregate acceptance and completion reporting. Execution facts may be reported
upward as links, blocker reports and outcomes. They must not automatically rewrite
the human-owned issue description, acceptance criteria, priority or decisions.
Explicit human-authorized issue amendments are permitted and must be recorded.

## Approved intake and decomposition

1. Require explicit approval by an authorized owner before triage activates
   execution. Record the approver, approval event or direct instruction, issue
   URL and approved requirements revision. An open issue or arbitrary label
   change alone does not authorize coding or alter existing review requirements.
2. Pin the approved requirements snapshot using the issue update timestamp and
   a SHA-256 digest of the captured body, or an equivalent versioned snapshot.
   Reassess material requirement changes through triage before work continues;
   workers must not quietly implement changed intent. Progress reporting alone
   does not redefine acceptance.
3. Search existing tasks, branches and PRs before decomposing. Persist the
   issue/revision-to-task mapping and use stable task IDs and idempotency keys.
   Repeated events, issue reopening and controller restarts must not create
   duplicate decompositions, claims or PRs. Reconcile a reopened issue before
   deciding whether to resume existing work or create a new bounded slice.
4. Create atomic tasks through the Backlog CLI before application code changes.
   One implementation task maps to one PR; a large issue produces multiple
   dependency-ordered tasks. If work needs another PR, triage must split it into
   separate tasks and record their dependencies before that work starts.
5. Map coarse issue dependencies to explicit execution dependencies and acceptance
   gates. Dependencies are satisfied by verified completion on the default
   branch and any additional declared gate, not by an issue's closed flag,
   branch-local Done status or archived record alone. Unknown or ambiguous IDs
   and archived unfinished tasks remain blocked.

GitHub Issues must never be used directly as application-code execution prompts.
A direct human instruction can approve triage and a bounded slice; it does not
remove the requirement to create the execution task first.

## Required execution record

Use native Backlog.md files under `backlog/tasks/`, native `TASK-*` IDs, statuses,
acceptance criteria and dependency fields. Create, edit, restore and archive them
only through `backlog`; Groma-owned records likewise use their CLI. Do not replace
the tool's schema with a hand-maintained `backlog.md` checkbox document.

Each new execution task requires:

| Field | Required content and storage |
| --- | --- |
| Issue | One primary parent issue's canonical URL in native references. Other issue links are supporting context. Historical completed records need not be retrofitted. |
| Approved revision | Approved requirement snapshot timestamp/digest, approver and approval evidence in the description or linked versioned specification. |
| Dependencies | Native task IDs in the dependency field; record mappings from coarse issue dependencies and additional completion gates. |
| Branch | A unique branch such as `agent/gh-<issue>-<sequence>-<slug>`, recorded in the description. An optional GH correlation key does not replace the native task ID. |
| Scope | Explicit repository-relative paths or bounded globs for source, new files, tests, lockfiles, generated files, docs and the task's own CLI-managed record, as applicable. |
| Verify | Exact deterministic commands, working directories, tool/fixture prerequisites and required hosted or environment checks. External or human checks are explicit gates with evidence. |
| Spec | Concise technical constraints and the observable outcome needed to understand this slice; preserve issue-level intent in the issue. |
| Acceptance | Native testable acceptance criteria mapped to issue outcomes, including relevant failure cases. A command exit code alone is insufficient. |

Store the additional labeled fields in the CLI-managed description or linked
specification; do not invent unsupported YAML metadata. Record researched
implementation plans only when executing the task, following the Backlog guide.

## Claims, scope and amendments

Autonomous workers require a durable exclusive lease with heartbeat, expiry,
fencing and restart reconciliation. An In Progress edit committed on a feature
branch is not globally exclusive. The trusted controller must reconcile claims
against all relevant branches and PRs. Human-directed interactive work currently
uses explicit assignment and duplicate-work checks; this is not evidence that
the autonomous lease service exists.

A worker may modify only the task's approved scope. Include direct tests and
the task's own Backlog record explicitly; neither is an unlimited exception.
Validate normalized paths, new files, both sides of renames and symlink targets
against the allowlist. Globs must not bypass protected policy paths or escape
the checkout. Repository policy and tool permissions still apply to allowed paths.

If implementation needs additional files, changed acceptance, different required
verification or a different outcome, stop affected work and request a versioned
triage amendment. A worker cannot widen its own scope or weaken checks to pass.
An owner approves changes to product intent or protected authority; triage may
approve routine decomposition changes within its delegated authority. Record the
new task/spec revision and invalidate affected implementation, review and check
evidence. Resume only after scope and dependencies are valid again.

Issue cancellation, lost approval, dependency changes and exhausted run limits
stop new execution and require reconciliation. Do not infer permission to undo
merged code or deployed state from an issue being closed or reopened.

## Completion and reporting

Never commit task status changes directly to `main`. Record task progress and
proposed completion through the Backlog CLI on the task's feature branch and
publish them in its PR. Verify acceptance and all applicable checks on the
current source before proposing completion; record required independent review
and outstanding merge blockers explicitly. If finalization changes the branch,
commit, push and verify its final head again. Proposed completion never grants
merge authority or substitutes for required approval.

A branch-local Done record is proposed completion until its PR merges. A merged
task records its declared acceptance; it does not imply an unperformed deployment.
Tasks requiring live deployment or recovery evidence remain incomplete until
that evidence exists. Preserve the current staged human-review and merge policy.

Intermediate PRs and commits use a neutral reference such as `Refs #123`.
Do not add closing keywords or an auto-closing development link when only one
part of a larger issue is complete. GitHub can close a linked issue when a PR
merges into the default branch; inspect linkage as well as PR/commit wording.
See [GitHub's issue-linking behavior](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/linking-a-pull-request-to-an-issue).

Only a human owner or a separately authorized trusted completion controller may
close the parent issue after verifying all of:

- Every required execution task has merged into the default branch, with no
  unresolved required task, dependency, review finding or acceptance blocker.
- The aggregate issue-level acceptance criteria pass for the current approved
  intent, with evidence across all contributing tasks.
- Applicable deployment, observation and recovery gates pass, or are explicitly
  inapplicable to the issue with a recorded reason.

The controller reports task/PR/release links, acceptance evidence and outstanding
limitations without rewriting the issue's requirements. Human cancellation is a
different outcome from successful completion and must not masquerade as delivery.

## Migration and implementation work

Treat migrated issue bodies' Backlog statuses, assignees and IDs as historical
import metadata. They are not live execution fields. Preserve archived records
and their references; archival of unfinished work does not satisfy dependencies.
Before enabling workers, triage the approved issues into fresh atomic execution
tasks and explicitly remap dependencies and required acceptance evidence. Do not
blindly restore broad archived items or mark them Done to unblock the scheduler.
Publish any in-progress migration separately from unrelated changes.

The governance refinement resolves the source-control choice in favor of GitHub
Issues, GitHub PRs/Actions and native Backlog execution. Runtime requirements are
tracked in [issue #37](https://github.com/vkaam/phonebuddy/issues/37) (authority),
[issue #41](https://github.com/vkaam/phonebuddy/issues/41) (triage, leases and
reconciliation), [issue #42](https://github.com/vkaam/phonebuddy/issues/42) (workers),
[issue #45](https://github.com/vkaam/phonebuddy/issues/45) (qualification),
[issue #46](https://github.com/vkaam/phonebuddy/issues/46) (trusted merge/completion)
and [issue #47](https://github.com/vkaam/phonebuddy/issues/47) (bounded autonomy).
This document does not install those services or expand their privileges.

## Executable consistency guard

Run the same read-only validator locally and in CI:

```sh
git fetch origin
python3 -B scripts/backlog_consistency.py --base origin/main
```

Immediately before claiming or resuming, also supply the native task and its
approved branch. A zero exit code and `claim_verified: true` are required:

```sh
python3 -B scripts/backlog_consistency.py --base origin/main --task TASK-58 --branch agent/gh-14-1-bicep-pr-validation
```

The command uses a read-only `GH_TOKEN`/`GITHUB_TOKEN` or the existing GitHub CLI
connection. It makes GET requests only, paginates branch/PR evidence, inspects
branch records as data and rejects unavailable, truncated or stale default-branch
evidence. It never executes code from another branch, writes claims, edits tasks
or issues, or closes anything. Save JSON outside the checkout, or in an untracked
`artifacts/` file, with `--output`; tracked source can never be overwritten.
Untracked runtime artifacts are excluded from source hashes and scope checks;
tracked files under that directory remain source. Reports bind the checkout head, dirty state and
hashed file manifest to the observed issue bodies, branch/PR claims and default
commit. Re-run after source, requirements or branch state changes.

The guard checks required execution fields, approved body digests, canonical
issue references, feature-branch uniqueness, duplicate decomposition, current
claims, task identity/dependency integrity and changed-path scope. New or changed
proposed Done records must have checked acceptance. A dependency is usable only
when its Done record with checked acceptance exists on the live default commit;
execution records also need a matching merged PR whose merge commit is an
ancestor of that commit. Historical completed records retain their existing
acceptance on the default branch. Closed issue flags and branch-local Done never
substitute for that evidence; tasks requiring external gates must remain active
until their evidence exists. The guard validates recorded evidence, not the
truth of an unperformed Azure, release or human check.

Unfinished imports already present before the 1 November governance adoption are
reported as historical/ineligible, not silently promoted into executable tasks.
They cannot pass a claim check; new records cannot obtain that exemption by
backdating themselves. Retiring unfinished records requires either a native
`Replaced by: TASK-n` line in the record, a shared canonical issue mapping and
remapped active downstream edges, or explicit intake-only disposition through
both `historical-import` and `needs-triage` labels plus a canonical issue
reference. Archival preserves unfinished status and cannot satisfy dependencies.
The guard also rejects silently removed identities. Use the Backlog CLI for all
reconciliation changes; the guard supplies no automatic repair path.

CI runs live validation inside the existing Quality gate using a read-only,
unprivileged token, retaining its JSON with QA artifacts. `scripts/check.py`
registers the offline structural mode; `--offline` never validates a claim or
provides live merge/approval evidence. Existing broad imports may therefore
appear as warnings in an audit while remaining blocked for execution.

This is a point-in-time consistency gate for human-directed work. Approval text
is checked for required provenance and revision, not cryptographically attested
as an independent owner event. A passing snapshot does not acquire a lock or
eliminate the race between validation and a later claim. Durable exclusive
leases, fencing, trusted approval services and aggregate completion/release
controllers remain the separate runtime work described above. Repository rules
must require Quality for CI failure to prevent a merge; this change does not
alter repository protections or review/merge authority.
