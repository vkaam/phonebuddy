# Quality and delivery baseline

This increment starts Phase 0 of the [software plan](software-plan.md) on the
existing GitHub repository. It does not decide a future Azure DevOps migration.
There is no application, infrastructure, cloud identity, or deployed environment
yet. A green baseline check validates the repository and its safety policy; it
does not establish calling, isolation, transcription, or summary quality.

## Checks available now

For each bounded increment, use the
[work specification template](templates/work-specification.md) to define behavior
and acceptance cases, and the
[acceptance evidence template](templates/acceptance-evidence.md) to record results.
Follow [Issue and Backlog governance](issue-backlog-governance.md): GitHub Issues
own human-approved intent and aggregate acceptance; native Backlog tasks own
atomic execution. Record the approved issue revision, approval evidence, explicit
file scope, verification commands and task acceptance before coding.
Keep the Backlog task as the execution plan of record: link specifications and evidence
through the CLI, and map evidence to its acceptance criterion IDs. Small changes
can include the completed evidence directly in the PR body; larger changes can
link a dedicated record. Record failed and pending checks as well as successes.
These templates support the Phase 0 delivery loop; cloud execution and independent
review still require their own evidence.

Task completion on a feature branch is provisional until merge. Intermediate PRs
must use neutral issue references; a human owner or authorized trusted completion
controller closes the issue only after all required tasks merge, aggregate
acceptance passes and applicable release health is verified. Progress/evidence
reporting does not authorize rewriting human-owned requirements. Runtime triage,
leases and enforcement remain future factory work; these instructions do not
claim that automation is installed.

Run from the repository root with Python 3.9 or newer:

```sh
python3 -B scripts/quality.py
python3 -B -m unittest discover -s tests -v
```

Or run the baseline and web checks and save a local evidence bundle (requires
Node.js 20 or newer, npm, registry access, and Playwright's pinned Chromium).
Install the browser after installing the locked web dependencies:

```sh
cd apps/web
npm ci --no-audit --no-fund
npx playwright install chromium
cd ../..
```

On Linux, system browser libraries may also be required; CI installs them with
`npx playwright install --with-deps chromium`. Then run from the repository root:

```sh
python3 -B scripts/check.py
```

The command prints a unique directory under the system temporary directory.
Use `--output-parent /existing/directory` to choose another location outside the
checkout, and `--timeout 120` to set each check's timeout (1–600 seconds).
It returns a nonzero exit code for failed, timed-out, or unlaunchable checks,
source identity errors, or source changes detected between checks. The runner
also records Node and npm versions, performs `npm ci --no-audit --no-fund`,
records installed dependency versions, audits the lockfile with `npm audit`,
lints web JavaScript and TypeScript with `npm run lint`, and runs web tests,
Chromium route/config/keyboard smoke tests, and `npm run build` (which includes
TypeScript checking). The browser tests use controlled config responses and do
not prove telephony or backend behavior. A missing browser fails the bundle.
Checks continue after a
failure, but any failed or missing step fails the bundle. Each invocation creates
a fresh directory. The install replaces `apps/web/node_modules`.

`report.json` records the head SHA, Git status, before/after file manifests and
their SHA-256 digests, Python/platform version, exact commands, working directory,
durations, exit codes, and log digests. Manifests include tracked and non-ignored
untracked files, deleted files, modes, and symlink targets as hashes. Ignored
files and external dependencies are excluded. Concurrent edits reverted before
the final snapshot cannot be detected; run against a stable checkout. The report
identifies local dirty source but does not archive a patch or reproduce it by
itself: preserve the reviewed patch separately or rerun after committing.

This is a partial local baseline, not a complete issue #39 evidence bundle, an
isolation boundary, or a hosted CI result. Actionlint and Gitleaks are not run
by this command;
the report lists these outstanding gates. A passing bundle does not establish
that those checks passed.
It runs repository Python code with the caller's existing permissions and
environment. The timeout bounds each direct check process, not arbitrary child
process trees. Run untrusted code only in the disposable environment described
above and in the software plan. The runner does not perform actionlint, Gitleaks,
cloud checks, independent review, merging, or deployment. Logs are raw check
output; inspect/redact before sharing, preserve needed evidence outside temporary
storage, and delete bundles when no longer needed. Temporary storage may be
cleaned by the operating system; local bundles have no automatic retention policy.

The `CI` workflow runs on every PR (without path filters), pushes to `main`,
manual dispatch, and merge groups. Its single stable check is `Quality`. It:

- Checks UTF-8 text, final newlines, trailing whitespace, conflict markers,
  local Markdown file links, and immutable action references. Anchor existence
  and remote link availability are not checked.
- Runs adversarial safety-policy regression tests, including stale evidence,
  missing metadata, review vetoes, forks, symlinks, renames, and sensitive files.
- Validates workflow syntax and expressions with actionlint 1.7.12.
- Scans reachable Git history with Gitleaks 8.30.1, redacting detected secrets.
  Local uncommitted changes need a separate `gitleaks dir --redact .` scan.
- Retains test logs, workflow validation output, and redacted secret-scan evidence
  for 14 days, identified by run ID and attempt. Failed steps fail `Quality`.

Actions use immutable revisions; downloaded tools have pinned SHA-256 hashes.
Dependabot proposes weekly action and web npm updates. The local bundle and
hosted Quality run `npm audit` against the locked web dependency graph; any
reported severity or registry failure fails the check. CI retains the audit
log with its QA evidence. A maintainer reviews each finding, affected usage,
and proposed update, applies a verified fix, and reruns the checks. If a fix is
unavailable or the registry cannot be reached, record the finding or outage,
impact, owner and remediation plan; do not present the check as passing or
silently suppress it. A clean audit reflects the registry's current advisory
data, not proof that dependencies have no vulnerabilities.
Tool versions/checksums require
reviewed updates in the workflow. CI has a read-only token, no Azure credentials,
no privileged connections, no shared cache, and a ten-minute job limit.
Run untrusted PRs only on GitHub-hosted disposable runners.

## Interpreting PR safety

`PR safety / Risk report (advisory)` reads metadata and executes the current
default-branch policy. It never checks out PR code, consumes PR artifacts,
restores PR caches, posts approvals, or merges. It runs on PR changes/reviews
and after associated CI runs complete. A CI run with no associated PR produces
no recommendation. An assessment on the initial bootstrap PR cannot execute
until these files exist on `main`; review that PR manually.

Find the decision in the Actions run summary and `pr-safety-<run>-<attempt>`
artifact. JSON contains the decision, reasons, policy SHA, head/base SHAs,
generation time, and remaining controls. A green advisory job means the report
was produced; read its `decision` field. Never require this advisory job as a
branch-protection check or interpret a successful job as permission to merge.

The only `low-risk-candidate` is an open, non-draft PR into the current default
branch, from this repository, with clean mergeability and all of:

- At most ten added/modified regular, non-executable text files and 200 total
  added/deleted lines, with complete patches and matching file counts.
- Only `README.md` or lowercase Markdown in `docs/usage/`. Agent/security
  instruction filenames are excluded. Every unknown path requires review.
- A successful `Quality` check for this PR's current head, from the CI workflow
  whose run title records the current test merge commit (`CI <github.sha>`).
  Failed, skipped, stale, missing,
  wrong-workflow, or unknown evidence requires review.
- A current independent human approval from a repository collaborator/member/
  owner, no active changes-requested review, and no `do-not-merge`,
  `no-auto-merge`, `needs-review`, or `security` label.

All other changes receive `manual-review`, including code, tests, lockfiles,
contracts, database migrations, identities, organization isolation, telephony,
recording/retention, Azure configuration, prompts/evaluation thresholds,
architecture plans, delivery instructions, and the safety policy itself.
The classifier measures bounded change risk; it does not verify the truth of
documentation or prove absence of defects. An agent/LLM review is supplementary.

Every report has `merge_authorized: false`. No merge automation is installed.
A later merger must re-read live head/base identities, current approvals,
resolved conversations, required checks, and the protected policy immediately
before using native GitHub auto-merge. It must stop on changes or unknown state,
and must never bypass rules. Saved JSON is not an authorization token. Policy
changes require maintainer review, including when a PR claims to be low risk.

To reproduce a report with saved API-shaped evidence:

```sh
python3 scripts/pr_safety.py --input /tmp/pr-evidence.json --output /tmp/pr-safety.json
```

For read-only live collection, a maintainer can run `--collect <PR-number>`
from a trusted default-branch checkout with `GH_TOKEN` and `GITHUB_REPOSITORY`
set. Never run the collector from an untrusted PR checkout. API failures produce
`manual-review`, not a positive recommendation.

## GitHub activation

Observed on 29 October 2026: the public repository's default branch is `main`,
branch protection is absent, and repository auto-merge is disabled. Local files
do not change these settings. After this bootstrap is reviewed and CI has run:

1. Protect `main`: require a PR, at least one independent approval, Code Owner
   approval, dismissal of stale approvals, approval of the most recent push by
   someone other than its pusher, and resolved review conversations.
2. Require the `Quality` status check from GitHub Actions, with branches up to
   date before merge (or use a protected merge queue). Include administrators,
   prohibit force pushes/deletions, and avoid bypass actors.
3. Verify `.github/CODEOWNERS` resolves to maintainers with write access. It
   currently names `@vkaam` for delivery/security-sensitive paths. Add another
   maintainer before relying on independent approval for that owner's PRs.
4. Keep fork workflow approval enabled, default workflow permissions read-only,
   and workflow approval/PR-creation rights disabled. Enable GitHub secret
   scanning and push protection where available as additional controls.
5. Exercise one successful documentation PR, one deliberately failed CI PR, and
   one policy-change PR. Confirm the latter two cannot bypass protection and
   that the trusted report binds to the current commits.
6. Leave repository auto-merge disabled until a separately reviewed merger
   enforces this contract. Native auto-merge can also be enabled manually per
   PR after policy review; the advisory report does not enable it.

GitHub's [required-check behavior](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
accepts skipped/neutral checks in some cases, so the evaluator specifically
requires `success`. The merge-group trigger ensures required CI can run in a
future merge queue. Protect policy files and keep privileged event handlers
on trusted code; see [secure use of Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions).

## Platform QA gates to implement with each component

These gates are pending; no placeholder job currently claims they pass.

| Component/change | Evidence required before pilot release |
| --- | --- |
| React/Fastify/worker | Locked install, formatting/lint, strict TypeScript, build, meaningful unit/contract tests, dependency scan and container image scan |
| Identity and storage | Real SQL/queue integration, cross-organization list/detail/export/WebSocket/blob/job negatives, pooled-session isolation, idempotent retries, migrations and restore/deletion replay |
| Browser calling | Chosen pilot browsers, injected-audio UI tests, controlled SIP peer, inbound/outbound, hold/resume, DTMF, hangup and failure states |
| Gateway/media | Two-way audio under NAT and forced TURN, separate leg capture, 60-minute call/token-refresh tests, 10 concurrent calls, overload, draining/reconnect and AI-outage survival |
| Transcription | Versioned approved Dutch/English/Flemish/code-switching/noisy/narrowband corpus; WER baseline and provisional ≤20% target; p95 final-segment visibility ≤3 seconds |
| Summary/prompt/model | Schema/source ownership validation, supported claims, no fabricated owners/deadlines in release fixtures, precision/recall and held-out human scoring (≥90% useful), p95 completion ≤60 seconds for calls ≤30 minutes |
| Bicep/configuration | Format/lint/build, parameter/policy validation, authenticated what-if, reviewed material changes, deployment smoke checks and rollback evidence |
| Release operations | Retention/deletion, secret/log hygiene, cost bounds, capacity/restore tests, alerts, incident owner, and provider-specific acceptance before Fonzer enablement |

Persist test counts, failures, dataset/config versions, measured distributions,
commit and artifact digests, and CI run links with each release candidate.
Define coverage thresholds from meaningful domain risks once executable code
exists; a global coverage percentage alone does not qualify a PR for auto-merge.

## CD rollout contract

The [Azure delivery policy](azure-delivery-policy.md) defines environment
prerequisites, automatic promotion, initial health gates, and recovery. No Azure
deployment workflow or environment is enabled yet. After protected-main CI,
the intended pipeline promotes the same immutable artifacts through dev, test,
and production with separate least-privilege federated identities. Independent
PR review occurs before merge; routine production approval is not a promotion
gate. Failed or unknown checks stop promotion. Stateful recovery and gateway
session draining must follow the policy; artifact rollback alone does not undo
schema or data changes.
