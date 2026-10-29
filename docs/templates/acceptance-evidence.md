# Acceptance evidence template

Complete one record per tested candidate. Replace placeholders; do not label a
planned check as passed. Link the record from the Backlog task and PR. Keep secrets,
SIP credentials, raw call audio, and transcript content out of routine evidence;
use synthetic fixtures or approved access-controlled artifacts.

## Candidate identity

- Backlog task and specification:
- PR URL (or local-only):
- Recorded at (UTC):
- Author/operator:
- Source head SHA and base SHA:
- Tested merge SHA, when testing a PR merge:
- Local changes beyond that SHA: none, or attach the exact reviewed patch and its digest:
- CI workflow revision, run URL, run ID, and attempt (or not run):
- Environment, runtime/tool versions, and configuration version:
- Build/image/artifact names and SHA-256 digests (or inapplicable with reason):
- Fixture/dataset, prompt, model/deployment, and schema versions as applicable:

Evidence applies only to the source and configuration identified here. After a
change, rerun affected checks and issue a new record; retain previous results.
CI reruns must include the attempt so artifacts cannot be confused.

## Acceptance mapping

Use Backlog criterion IDs. Status must be `pass`, `fail`, `not run`, `blocked`, or
`inapplicable`. Every row needs a result or explanation. Pending and blocked work
remains unchecked in Backlog; inapplicable checks require a concrete scope reason.

| Criterion | Status | Command/procedure and fixture | Actual result | Evidence link/path | Limitation or blocker |
| --- | --- | --- | --- | --- | --- |
| AC-1 | not run | … | No result yet | … | … |

## Check results

Record exact reproducible commands, working directory, prerequisites, exit codes,
test counts/failures, and artifact locations. For measurements, include sample
size, units, distributions, and dataset/configuration versions. Human checks need
a named reviewer, procedure, observation, and date. Redact sensitive output.

| Check | Status | Command/procedure | Result and evidence |
| --- | --- | --- | --- |
| Repository validation | not run | python3 -B scripts/quality.py | … |
| Safety-policy regressions | not run | python3 -B -m unittest discover -s tests -v | … |
| Hosted Quality | not run | Link exact run and attempt | … |
| Applicable platform gates | not run | Select from delivery baseline | … |

## Review and delivery

- Independent reviewer, reviewed SHA, findings, and resolution evidence:
- Remaining failed/blocked/not-run checks, owner, and next action:
- Advisory safety decision and reasons, policy/head/base SHAs (or unavailable):
- Deployment status and environment (including explicitly not deployed):
- Migration, rollout, health, and rollback/recovery evidence where applicable:
- Artifact retention deadline and durable evidence location if needed:

Passing checks do not authorize merging or deployment. Apply the
[delivery baseline](../quality-and-delivery.md) and current repository protections.
No missing platform evidence can be replaced by a green repository check.
