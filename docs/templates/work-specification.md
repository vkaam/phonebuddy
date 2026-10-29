# Work specification template

Use this template for a bounded PhoneBuddy increment. Replace placeholders with
facts; mark unknown inputs explicitly. Keep status, assignee, acceptance criteria,
implementation plan, and progress in Backlog through its CLI. Link any completed
specification from that task rather than maintaining a second task lifecycle here.

## Identity and problem

- Backlog task: TASK-…
- Trigger and affected user/operator:
- Current behavior and concrete problem:
- Desired observable behavior:
- Relevant source files, contracts, and decisions:

## Scope

- Included behaviors:
- Deferred behaviors:
- Dependencies and unresolved inputs (owner, resolution needed, blocked work):
- Material decisions requiring review before implementation:

## Acceptance cases

Copy criterion IDs from the Backlog task. Describe observable outcomes, including
failure cases, rather than implementation steps. Update Backlog first if scope
changes. Use synthetic data until real-data use is explicitly authorized.

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
- External access or environment needed for pending checks:
- Independent review needed and unresolved findings:
- Evidence record: use the [acceptance evidence template](acceptance-evidence.md).

The [delivery baseline](../quality-and-delivery.md) defines available checks and
future platform gates. Repository CI alone cannot establish a platform gate.
