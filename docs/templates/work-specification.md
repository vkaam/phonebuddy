# Work specification template

Use this template for a bounded PhoneBuddy increment. Replace placeholders with
facts; mark unknown inputs explicitly. Keep status, assignee, acceptance criteria,
implementation plan, and progress in Backlog through its CLI. Link any completed
specification from that task rather than maintaining a second task lifecycle here.

## Identity and problem

- Backlog task: TASK-…
- Primary GitHub Issue URL (open and labeled `approved`) and the issue-level
  outcome covered by this slice:
- Branch:
- Trigger and affected user/operator:
- Current behavior and concrete problem:
- Desired observable behavior:
- Relevant source files, contracts, and decisions:

## Scope

- Repository-relative paths or bounded globs for the task's `Scope`, including
  new files, tests, lockfiles/generated files and docs (Backlog records are
  always in scope):
- Included behaviors:
- Deferred behaviors:
- Dependencies and unresolved inputs (owner, resolution needed, blocked work):
- Material decisions requiring review before implementation:

## Acceptance cases

Copy criterion IDs from the Backlog task. Describe observable outcomes, including
failure cases, rather than implementation steps. Every criterion must be
checkable before merge; put live or post-merge proof in a follow-up task. If
scope must change, get the owner's agreement and record the amendment in the
task first; workers cannot expand scope or weaken required checks themselves.
Use synthetic data until real-data use is explicitly authorized.

| Criterion | Preconditions and input | Action | Expected result | Verification method |
| --- | --- | --- | --- | --- |
| AC-1 | … | … | … | Command, fixture, integration check, or human review |

Include relevant negative cases: unauthorized organization access, malformed
input, duplicate/retried events, dependency outage, and recovery. Explain why a
case is inapplicable rather than treating it as passed.

## Boundaries and operations

For each applicable area, state the affected contract, proposed behavior, and
verification. Mark other areas inapplicable with a reason.

- Identity, authorization, and organization ownership:
- SIP/media behavior and survival of AI failures:
- Transcription/recording notice, retention, deletion, and sensitive logs:
- Schema, API/event compatibility, migrations, and idempotency:
- Model/prompt/dataset versions, source evidence, and evaluation thresholds:
- Infrastructure, credentials, geography, quotas, and cost limits:
- Observability, rollout prerequisites, rollback/recovery, and incident owner:

## Verification and handoff

- Commands and fixtures available now:
- Exact deterministic commands, working directories and pinned prerequisites:
- External access or environment needed for pending checks:
- Task dependencies (`--dep TASK-n`):
- Follow-up tasks for post-merge, deployment or health proof:
- Independent review needed and unresolved findings:
- Evidence record: use the [acceptance evidence template](acceptance-evidence.md).

The [delivery baseline](../quality-and-delivery.md) defines available checks and
future platform gates. Repository CI alone cannot establish a platform gate.
Follow [the factory workflow](../issue-backlog-governance.md). This is a
specification linked from a CLI-managed task, not a replacement task schema.
Intermediate PRs use `Refs #N`; the PR that completes the issue uses `Closes #N`.
