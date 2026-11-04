## Problem and resulting behavior

Backlog task:

Primary GitHub Issue (use a neutral reference such as Refs #123 for a partial slice):

Approved issue revision and approval evidence:

Specification (use the [work specification template](../docs/templates/work-specification.md)
when a separate specification is useful):

Describe the trigger, scope, and resulting behavior.

## Evidence

Use the [acceptance evidence template](../docs/templates/acceptance-evidence.md)
here or link a completed record. Identify the tested source/configuration and map
results to Backlog criterion IDs; keep pending checks explicit.

- Commands/checks run and results (include failures and checks not run):
- CI run and artifact links for the current commit:
- Acceptance criteria demonstrated:
- Approved file scope, task/spec revision and authorized amendments:
- Independent agent reviewer, reviewed head, findings and resolution:
- Remaining issue-level tasks and issue/Backlog sync state:

## Risk and delivery

- Affected contracts, organization boundaries, dependencies, prompts/evals, or infrastructure:
- Deployment prerequisites, migration/rollback, and operational impact (or explain why none apply):
- PR safety report decision, head/base SHAs, and reasons:

Merge as soon as scoped acceptance, independent agent review, required
pre-merge checks and blocking findings are clear under effective GitHub rules.
Follow [Issue and Backlog governance](../docs/issue-backlog-governance.md).
Task completion is proposed on this branch until merge; avoid closing keywords
and auto-closing development links for intermediate PRs. After merge, reconcile
the task and issue, inspect default-branch CI/CD, and create linked follow-up
work for any failure.
