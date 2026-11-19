<!-- groma:start -->
## Groma

This project uses Groma. Before you scan, inspect, or curate architecture, or change files for a Backlog task, run `groma agent-instructions` and read the guide it names for that job. When it reports a first scan, ask the user whether they want you to curate the architecture. Do not edit Groma-owned architecture files directly.
<!-- groma:end -->

<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.55.3 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**At the beginning of each conversation in this project, run `backlog instructions overview` before answering or taking action. Re-read it only if you have not read it yet in the current conversation.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->

## Factory workflow

Follow [the factory workflow](docs/issue-backlog-governance.md). In short:

- GitHub Issues hold approved intent. An issue is approved while it is open and
  labeled `approved`. Only the owner adds that label, unless the owner tells you
  to in the conversation. Never rewrite an issue's requirements; report progress
  in comments.
- Each piece of work is one Backlog task, one branch and one PR. A task's
  description starts with `Issue:`, `Branch:`, `Scope:` and `Verify:` lines and
  has acceptance criteria that can be checked before merge. Post-merge or live
  proof is a separate follow-up task.
- Change only paths in the task's `Scope` (Backlog records are always allowed).
  Ask the owner before widening scope and record the amendment in the task.

## Picking up work

When asked to work on the Backlog without a specific task, pick an unassigned
To Do task whose issue is approved and whose dependencies are Done. Respect any
requested priority and never take over someone else's task. If nothing is
eligible, report why.

Before claiming or resuming a task, run:

```sh
git fetch origin
python3 -B scripts/backlog_consistency.py --base origin/main --task TASK-ID --branch RECORDED-BRANCH
```

Require exit code 0 and `"claim_verified": true`. Then set the task In Progress
and assign yourself through the CLI, push the branch and open a draft PR with
`[TASK-ID]` in the title straight away. That draft PR is your claim.

## Taking work through review and merge

1. Implement within scope and run the task's `Verify` commands.
2. Before asking for review, finish the task record: check each criterion that
   has evidence, write the final summary and set it Done, following the
   finalization guide. Commit that with the work.
3. Have an independent agent review the final head, rerun the checks and
   validate each criterion. The author never approves their own work. Record the
   review on the PR with the reviewed commit SHA.
4. Watch `Quality` and `Task link` on the current head until they pass. Pending,
   cancelled, skipped or missing required checks are not passing. If you cannot
   fix a failure within scope, report the check name, state and blocker.
5. Mark the PR ready and merge as soon as checks pass and blocking findings are
   resolved. Use `Closes #N` on the PR that completes an issue and `Refs #N` on
   intermediate PRs.
6. After merge, watch main CI/CD. A failure becomes a new issue and task; do not
   reopen merged work.

## Addressing pull request feedback

When a review comment has been fixed and verified, react with a thumbs-up to
the comment and resolve its conversation. Leave conversations unresolved when
the feedback is not fully addressed, and report any blocker.

## Publishing changes

After completing requested repository changes, including Backlog updates, run the
appropriate checks, commit the task's changes, and push the working branch.
This is standing user authorization; do not ask again for routine commit/push.
Preserve unrelated work, never force-push by default, and report any blocked push.
Whenever requested work creates a new branch, push it and open a pull request
against the repository's default branch. This is standing user authorization;
do not ask again for routine PR creation. Reuse an existing open PR for the branch
instead of creating a duplicate. Use a draft PR when work is still in progress,
and include scope, validation results, and remaining limitations in its description.
Before creating a PR, fetch the latest `origin/main` and bring the work branch
up to date with it. Resolve any conflicts, rerun relevant checks on the integrated
result, and push before opening the PR. Prefer merging `origin/main` into an
already-pushed branch to preserve shared history; do not force-push by default.
Verify that the fetched main commit is an ancestor of the PR branch before creation.
Do not merge or deploy solely because changes have been committed and pushed.
