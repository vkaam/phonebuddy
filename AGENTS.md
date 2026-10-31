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

## Taking Backlog work through review

When asked to work on the Backlog without a specific task, list the available
tasks and pick an eligible, unassigned item whose dependencies are satisfied.
Respect any requested priority or scope, and do not take over someone else's
active work. If no eligible item can be identified, report the blocker. When a
task is specified, read it and verify its eligibility before starting. Follow
the execution guide to claim it, record a plan, and keep progress in Backlog.

Carry the assigned work through a pull request, not just a local implementation:

1. Verify the acceptance criteria and record evidence using the finalization
   guide. Keep the task active while implementation or required verification is
   incomplete. Record the PR link and any outstanding blockers in the task.
2. Follow the publishing instructions below. Open or update the branch's PR with
   its task, scope, validation, and remaining limitations. Do not create a
   duplicate PR.
3. Monitor all checks on the PR's current head until they complete successfully.
   Inspect failures, fix issues within scope, run relevant local checks, commit
   and push, then monitor the new head again. Pending, cancelled, skipped,
   missing, stale, or otherwise inconclusive checks are not successful checks.
   If a check cannot be completed or fixed, report its name, state, and blocker;
   do not claim the PR is green.
4. Once the work and acceptance criteria are verified and the PR checks are
   green, complete the Backlog finalization steps. If those updates change the
   PR branch, commit and push them and verify checks again for the final head.
   Report the PR link, final check results, and any remaining review or other
   blockers. A green PR still requires the project's review and merge controls.

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
