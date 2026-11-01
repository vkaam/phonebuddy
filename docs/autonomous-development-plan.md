# Autonomous development: readiness and gap-closure plan

Assessment date: 31 October 2026. Repository baseline:
`b0d0a9492c8413e48ecd186c0f757de4b44b85f1` on `main`, refreshed after
the Bicep foundation merged during assessment publication.
Assessment task: TASK-31. The Backlog is the execution plan of record;
TASK-32 through TASK-42 capture the missing factory work.

PhoneBuddy supports agent-assisted development today. It has useful CI and
evidence controls, but no demonstrated unattended task-to-PR runtime, independent
agent review, automated merger, or automated release path. The largest gap is
the execution and recovery loop around the model. Adding another model alone
will not close it.

This document proposes work and qualification gates. It does not activate a
runner, change repository protections, authorize unattended merging, or establish
that Azure resources are absent outside this repository.

## What autonomy should mean

Start with an approved, bounded work item and measure the whole lifecycle:
selection, specification, implementation, tests, review, PR maintenance, merge,
release, health observation, and reconciliation to the Backlog. The controller
must also recover from interruption and stop usefully when it cannot proceed.
Business prioritization, ambiguous requirements, spending authority and changes
to the controller's own permissions need an accountable owner.

| Stage | Work the system completes without another operator prompt | Remaining human boundary |
| --- | --- | --- |
| Current: assisted | CI runs after a person or interactive agent publishes a change. | Someone starts and supervises development, handles review and merge, and supplies cloud prerequisites. |
| A: unattended PR production | Select an opted-in task, implement, verify, independently review, repair CI and feedback, and maintain one reviewable PR. | Independent human review and merge authorization remain mandatory. |
| B: delivery after approval | A trusted merger handles eligible approved PRs; a protected pipeline deploys immutable artifacts and verifies health or recovers. | Human approval of each PR under the current contract; exceptional changes and incidents. |
| C: bounded end-to-end autonomy | An explicitly approved change class completes the same path, including merge and release, without per-PR human intervention. | Policy, sensitive changes, missing inputs, exceeded limits and unresolved incidents. |

Stage C is a proposed policy expansion. The
[software plan](software-plan.md) and [delivery baseline](quality-and-delivery.md)
currently require independent human review and prohibit coding agents from
merging. Native auto-merge waits for required reviews and checks; enabling it
does not remove that boundary. See
[GitHub's auto-merge contract](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/automatically-merging-a-pull-request).
Unrestricted autonomy over every kind of change is not a qualification target.

## Evidence and current gaps

The following distinguishes observed implementation from proposed architecture.
GitHub settings were read live on the assessment date. Azure subscriptions,
deployed services, model access and billing were not audited.

| Capability | Evidence now | Gap and consequence |
| --- | --- | --- |
| Work instructions and acceptance | `AGENTS.md`, Backlog tasks, work specification and acceptance evidence templates exist. | No unattended intake, approved task-selection policy, immutable specification snapshot or durable run ownership. Instructions require an executing agent. |
| Source and delivery control plane | GitHub is in use; software-plan section 8 proposes Azure DevOps with GitHub as an alternative. | Decide one source of truth before connecting queues, identities and callbacks. Migration is not required to start. |
| Hosted checks | `ci.yml` runs Python checks/tests, locked web install, configuration tests, TypeScript/build, actionlint and Gitleaks on disposable hosted runners. Main CI succeeded for the refreshed baseline. | No web lint command, browser behavior suite or npm dependency scan/update configuration. The new standalone Bicep compiler check is not wired into CI; TASK-7 owns that integration. API, storage, SIP/media and AI evaluation gates do not exist yet. |
| Local evidence | `scripts/check.py` binds Python baseline results to source manifests and digests. | It omits the web checks performed in CI; passing it does not establish application correctness. It inherits host permissions and cannot bound child process trees. |
| Effective GitHub protection | Active `Standard main` ruleset targets the default branch, requires PRs, resolved conversations and strict `Quality` from GitHub Actions, blocks deletion/force-push, and lists no bypass actors. | Approval count is **0**; Code Owner review, stale-approval dismissal and last-push approval are **off**. This differs from the documented human-review policy. Classic branch-protection returns 404, which must not be mistaken for absence of ruleset protection. |
| Review and merge policy | `scripts/pr_safety.py` reads trusted-base policy, checks current commits and CI, and always emits `merge_authorized: false`. | Its positive classification only covers small allowlisted documentation changes with human approval. It provides neither implementation review nor merge execution. Repository auto-merge is off. |
| Ownership | `CODEOWNERS` names `@vkaam` for several sensitive paths. | Only one owner is named; availability of a second independent maintainer is unverified. Future factory paths and the new plan need explicit policy ownership. |
| Coding and review runtime | Software-plan section 8 proposes Azure orchestration, disposable VMs, Foundry inference and separate reviewer contexts. No `factory/` implementation is present. | No provisioned runner path, model/tool proof, sandbox isolation, short-lived gateway authorization or independent review runtime is demonstrated by repository evidence. |
| Scheduling and repair | The interactive workflow describes task claiming, PR repair and check monitoring. | No persistent scheduler, leases, idempotency, retry accounting, conflict reconciliation or restart/resume controller implements it. |
| Factory operations | Local bundles use temporary storage; hosted evidence is retained for 14 days. | No durable factory audit store, retention policy, aggregate cost enforcement, kill switch, resource reaper, operator alerts or service owner is implemented here. |
| Release and recovery | Delivery and recovery contracts are documented. PR #8 added modular Bicep resource-group/tag foundations, environment parameters and a standalone pinned compiler/preflight check. TASK-5 through TASK-14 cover infrastructure and delivery. | TASK-5 remains assigned and In Progress: parameters contain unresolved inputs and disposable/repeat deployment and isolation evidence remain incomplete. There is no deployment workflow or proven promotion/rollback. Do not equate merged foundation source with provisioned environments or completed dependencies. |
| Architecture discovery | `.groma/config.json` selects no scanners; `groma view --plain` reports no components. | Architecture ownership links cannot currently guide an agent. Scanner setup and any authorized curation belong in the context/bootstrap work; the assessment did not create or edit a map. |

Other observed settings: Actions are enabled, the default workflow token is
read-only, and workflow PR approvals are disabled. Repository-wide action
allowlisting and SHA pinning are not enforced by settings, although the current
workflow files pin actions. These are evidence to reconcile in the policy work,
not proof that future workflows will preserve the same restrictions.

The [successful refreshed-baseline main CI](https://github.com/vkaam/phonebuddy/actions/runs/41230966338)
and [active ruleset](https://github.com/vkaam/phonebuddy/rules/26155764) ground the
refreshed snapshot. [TASK-5's foundation PR](https://github.com/vkaam/phonebuddy/pull/8)
merged during publication; its Backlog status remains In Progress with live
Azure evidence blocked. The assessment branch integrates that main update and
requires fresh CI. The web shell is merged, despite older
prose in `quality-and-delivery.md` saying no application exists. Future agents
must reconcile dated documentation with source, live PRs and run evidence.

## Proposed implementation contract

Keep GitHub and Backlog as the initial control plane, subject to TASK-32's
reviewed decision. Reuse the existing CI and PR conventions. Keep the proposed
Azure factory boundary separate from product environments; prove model access
and tool execution before investing in a larger platform. Do not make the
first unattended PR depend on the complete softphone or all production hosting.

Use the deterministic state machine already proposed in the software plan:

`eligible -> leased -> specified -> implementing -> verifying -> reviewing -> PR-ready`

Failures transition to bounded repair, waiting-for-owner, or failed with retained
evidence. Stage B adds waiting-for-approval, merge, deployment and observation;
Stage C only removes per-PR approval for a separately approved class. Track PR
readiness and deployed health as distinct facts so Done cannot imply a release
that has not happened. Existing Backlog statuses can remain simple while the
factory records its more detailed run states separately.

The trusted controller owns leases, policy and limits. Untrusted repository
commands run in disposable sandboxes. A tool gateway mediates narrowly scoped
repository/model actions; a separate trusted merger handles approved merge
requests, and deployment identities remain in protected delivery jobs. Issue
text, repository content, diffs, dependency scripts and test output are data,
never authority to change permissions or trusted instructions. Validate typed
tool requests against policy outside the model. Scope identities independently;
[Foundry identity documentation](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/agent-identity)
describes identity-based downstream access, but tenant availability and the
selected runtime still require a practical proof.

Start sequentially, with one leased task per runner and one controller-owned PR
per task. Add concurrent work only after leases, contract/file ownership and
integration behavior have been tested. Planner, implementer and reviewer are
separate contexts with different permissions; they do not need a recursively
delegating agent platform. The reviewer verifies the final diff and reruns
evidence independently. A stronger model or another review pass is useful only
if qualification shows it catches defects or reduces interventions at acceptable
cost.

## Sequenced work

All new execution tasks are unassigned and To Do. Their detailed acceptance
criteria and dependencies are stored in Backlog; this table gives the delivery
order and intended outcome, not an implementation commitment.

| Order | Task and outcome | Direct dependencies | Proposed accountable role |
| --- | --- | --- | --- |
| 1 | TASK-32: approve the autonomy contract, control plane, ownership and prerequisites. | None | Maintainer and platform owner |
| 1 | TASK-34: close local/CI application evidence gaps, including browser behavior and dependency coverage. | None | Application/quality engineer |
| 2 | TASK-33: align effective GitHub protections and independent policy ownership with the current contract. | TASK-32 | Repository administrator and second maintainer |
| 2 | TASK-35: prove model/tool execution in a disposable isolated runner with cleanup. | TASK-32 | Platform engineer |
| 2 | TASK-36: persist scheduling, task/PR reconciliation, leases and recovery. | TASK-32 | Factory engineer |
| 3 | TASK-37: deliver bounded implementation, CI repair and PR-feedback handling. | TASK-34, TASK-35, TASK-36 | Factory engineer |
| 3 | TASK-39: enforce budgets, audit retention, cancellation and actionable operations. | TASK-32, TASK-35, TASK-36 | Platform/operations owner |
| 4 | TASK-38: independently review the final diff using separately executed verification. | TASK-34, TASK-35, TASK-37 | Quality/security engineer |
| 5 | TASK-40: qualify unattended PR production on fixtures and a real PhoneBuddy task. | TASK-33, TASK-37, TASK-38, TASK-39 | Factory owner and independent evaluator |
| 6 | TASK-41: merge eligible human-approved PRs through a trusted controller. | TASK-33, TASK-40 | Repository/platform owner |
| 7 | TASK-42: qualify an explicitly approved class without per-PR human approval, including release and recovery. | TASK-13, TASK-40, TASK-41 | Maintainers and service owner |

TASK-32 includes build/test instructions, architecture context and the Groma
coverage decision. If setup reports a first scan, ask whether to curate it as
required by `AGENTS.md`; do not treat scanner output as an authored architecture.
TASK-33 should update dated protection claims and ownership coverage after its
settings are actually verified. No existing task's assignee, status or scope was
changed by this assessment.

Run the existing product delivery track alongside the factory:

- Complete TASK-5's remaining deployment evidence after merged PR #8, then use TASK-6 through TASK-9 for deployment
  identities, infrastructure validation, hosting and data/model foundations.
- Use TASK-10 through TASK-13 for health gates, immutable automatic promotion,
  recovery and live end-to-end drills. These are prerequisites for claiming
  autonomous delivery, but not for demonstrating unattended PR production.
- Use TASK-14 and TASK-16 through TASK-30 for telephony infrastructure and product
  capability with domain-specific tests. Require the applicable isolation,
  controlled SIP/media, transcription and summary gates before autonomous changes
  in those areas; TASK-30 remains the complete pilot acceptance gate.

TASK-9 provisions product Speech/Foundry foundations. Factory inference must
have its own scope and permission boundary; reuse provisioning patterns where
appropriate without giving a coding runner the product's data or identities.
TASK-35 owns that factory proof rather than duplicating the application task.

## Qualification and expansion gates

These are proposed acceptance targets to review, not measured performance.

| Gate | Evidence required to advance |
| --- | --- |
| Reproducible baseline | One command covers applicable application checks; hosted extras are explicit. Missing or stale evidence cannot pass. |
| Stage A | At least 10 distinct fixture tasks across docs, fixes and small features; at least 8 reach a reviewable PR without operator prompts or code edits. At least one real eligible PhoneBuddy task follows the same path. Report every failure and intervention. |
| Isolation and recovery | All seeded mandatory defects and unauthorized actions are blocked. Exercise prompt injection, forged/stale evidence, policy modification, reviewer/API outage, exhausted limits, duplicate events, controller restart and sandbox loss. No duplicate PR/claim, leaked credential or surviving sandbox remains. |
| Stage B | Live current-source CI/review enforcement and permitted merge are demonstrated; TASK-13 proves automatic deployment and recovery, with health and release evidence retained. |
| Stage C | A reviewed policy defines the exact allowed code classes. Evaluate in shadow mode, then at least 10 supervised eligible PRs with at least 90% needing no manual code/prompt repair. Block every seeded critical defect/policy violation. Run a seven-day bounded pilot and review interventions, escaped defects, lead time, spend and recovery before expansion. |

Track reviewable-PR completion rate, time to useful PR, manual interventions,
repair attempts, cost per accepted PR, escaped defects and recovery time. Include
denominators, failed/cancelled runs, model/prompt/check versions and source
identities. A small pilot is evidence for a bounded rollout, not proof of general
correctness. Budget alerts alone are insufficient: the controller/gateway must
reject additional work when approved aggregate limits are exhausted.

Do not weaken branch-wide review requirements merely to make Stage C pass.
[GitHub rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
can enforce required reviews and trusted checks. Conditional per-change review
needs a separately reviewed, enforceable design compatible with those rules;
a classifier, bot self-approval or blanket bypass is insufficient. Keep policy,
credentials, organization isolation, telephony, retention, migrations,
infrastructure and evaluation-threshold changes under human review initially.

## Decisions and practical starting point

TASK-32 should record these inputs before enabling the affected capabilities:

| Decision/input | Recommendation or outstanding fact | What it blocks |
| --- | --- | --- |
| Control plane | Retain GitHub + Backlog initially; resolve the Azure DevOps proposal explicitly. | Durable integrations and identity design. |
| Authority | Approve Stage A first; keep existing human review until a later policy decision. | Unattended merge and expansion of eligible classes. |
| Owners | Name a factory owner, escalation contact and second independent maintainer. | Reliable escalation and enforceable independent human review. |
| Factory Azure access | Tenant/subscription, EU region, quota, tool-capable coding/review model access and scoped bootstrap identity are unverified. | Live sandbox/inference proof, not local planning or check improvements. |
| Limits | Approve per-run and daily spend, token/compute/time/retry limits and evidence retention. No monetary ceiling is inferred here. | Unattended cloud execution. |
| Domain acceptance | Approve pilot browsers, fixtures, isolation/media/evaluation gates and release ownership as components arrive. | Autonomy in those domains and production enablement. |

Begin with TASK-32 and TASK-34. After the contract is approved, implement the
smallest TASK-35/TASK-36/TASK-37 slice that produces one useful PR; retain human
review while adding the independent reviewer and operations controls. Do not
wait for the complete product, and do not build a generic agent platform first.

For planning capacity, allow roughly 4–7 engineer-weeks for Stage A and the
approved-PR merger with experienced contributors: 2–4 days for scope/checks and
protection decisions, 1–2 weeks for runner and durable control, 1–2 weeks for the
coding/review/operations loop, and 1–2 weeks for qualification and merge handling.
These are rough effort ranges, not elapsed delivery promises; some work can
overlap. Azure access, independent review availability, existing deployment work
and the Stage C seven-day pilot add lead time. Re-estimate after the first real
task and measured model/tool behavior. Full production autonomy has no credible
date until those prerequisites are resolved.

## Reproducing the assessment

Inspect source at the recorded commit and read the current versions before
implementation. The key read-only commands used were:

```sh
backlog instructions overview
backlog task list --plain
backlog task view TASK-5 --plain
groma agent-instructions
groma agent-instructions inspect
groma view --plain
gh api repos/vkaam/phonebuddy
gh api repos/vkaam/phonebuddy/rulesets/26155764
gh api repos/vkaam/phonebuddy/branches/main/protection
gh api repos/vkaam/phonebuddy/actions/permissions
gh api repos/vkaam/phonebuddy/actions/permissions/workflow
gh pr view 8
gh run list --branch main --limit 5
```

Read-only GitHub CLI calls supplied administrative settings that the connected
GitHub tools do not expose. A protection-endpoint 404 was cross-checked against
the active ruleset. Re-read effective settings at execution time: both policies
and source can change after this snapshot.
