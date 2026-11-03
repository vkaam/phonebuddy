---
id: TASK-57
title: Issue 13 - Bootstrap federated GitHub deployment identities
status: In Progress
assignee:
  - '@codex'
created_date: '2026-11-02T16:35:00Z'
updated_date: '2026-11-03T05:00:00Z'
labels:
  - infrastructure
  - cicd
dependencies:
  - TASK-5
  - TASK-69
references:
  - https://github.com/vkaam/phonebuddy/issues/13
  - https://github.com/vkaam/phonebuddy/pull/55
modified_files:
  - scripts/bootstrap_github_oidc.py
  - tests/test_azure_oidc_bootstrap.py
  - .github/workflows/azure-oidc-smoke.yml
  - infra/github-oidc.md
  - infra/README.md
  - >-
    backlog/tasks/task-57 -
    Issue-13-Bootstrap-federated-GitHub-deployment-identities.md
priority: high
type: task
ordinal: 54000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Need: Trusted workflows require environment-scoped Azure access without long-lived credentials.

Issue: https://github.com/vkaam/phonebuddy/issues/13
Approved revision: 2026-11-02T20:47:52Z; body SHA-256 31d3571e5b62e2fc8a4efa86f325d5f757bccc09f4516fc7f7cabf17d417305b.
Approval evidence: The human user directly authorized reconciliation in Codex on 2026-11-02 with “fix this”. This authorizes triage into a bounded execution task; it does not authorize Azure deployment or issue closure.
Branch: agent/gh-13-1-bootstrap-federated-identities
Scope: scripts/bootstrap_github_oidc.py; tests/test_azure_oidc_bootstrap.py; infra/github-oidc.md; infra/README.md; backlog/tasks/task-57 - Issue-13-Bootstrap-federated-GitHub-deployment-identities.md. Archived TASK-6 is historical and is not restored.
Verify: From repository root run python3 -B scripts/check.py; python3 -B scripts/run_required_unittests.py; python3 -B -m unittest discover -s tests -p test_azure_oidc_bootstrap.py -v; actionlint .github/workflows/azure-oidc-smoke.yml .github/workflows/ci.yml .github/workflows/pr-safety.yml; git diff --check. Node/npm, registry access and pinned Playwright Chromium are required for the complete local bundle. Hosted Quality and advisory checks must pass on the current PR head. External gates: review bootstrap/runbook; repository owner configures dev/test main-only GitHub environments; approved Azure federation/RBAC readback and trusted dev/test OIDC authentication/cross-environment denial runs. No live bootstrap is authorized by this reconciliation.
Spec: Implement only issue #13's approved identity and federation controls. Keep untrusted pull-request code outside the Azure credential path.

Triage amendment, 2026-11-02 (TASK-67): The current user reconciliation instruction authorizes retaining existing draft PR https://github.com/vkaam/phonebuddy/pull/55 and its actual branch, transferring the active claim from archived TASK-6 to TASK-57, and enumerating the exact source/test scope already implemented there. The issue requirements and all three unchecked acceptance criteria remain unchanged. This corrects migration bookkeeping; it grants no identity bootstrap, deployment, merge or issue-closing authority.

Revision reassessment 2026-11-02: the owner checked the three issue acceptance boxes. Replacing only those checks with unchecked reproduces the previously approved body SHA-256 e49bb04e65519b8d40380feda8a7e091f4d3f2c94b25766da0812a8cd0d684e5; requirement wording and scope are unchanged. Owner reports completion, but execution acceptance remains subject to the recorded verification gates.

Triage amendment 2026-11-02: Owner explicitly approved one shared service principal for dev and test, including mutual access to both nonproduction resource groups. Update the existing scoped bootstrap, workflow, tests and documentation accordingly. Verify both GitHub environment trusts and restrict Azure assignments to the two approved resource groups; test authentication from both environments and the untrusted-PR boundary. Cross-environment denial is no longer an acceptance requirement. Owner approval does not itself verify provisioning or authorize deployment.

Triage amendment 2026-11-02: The owner approved splitting the main-only OIDC smoke workflow into TASK-69 and PR #75 so TASK-57 can gather live evidence. TASK-57 depends on TASK-69 and retains the shared-principal bootstrap, tests and documentation; issue acceptance and live verification remain unchanged.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 One shared principal uses restricted repository and dev/test environment federation, with Azure roles scoped to the approved nonproduction resource groups.
- [ ] #2 Trusted workflow authentication succeeds from both environments; untrusted PRs cannot obtain the deployment identity. Shared dev/test access is explicitly documented.
- [ ] #3 Bootstrap and GitHub environment configuration are reproducible or explicitly documented; credentials never enter logs.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reconcile PR #55 with merged TASK-69 and retain the shared identity design. 2. Verify scoped Azure role/federation and GitHub environment configuration, and record both trusted authentication runs. 3. Validate implementation and current-head checks, then finalize provisionally subject to review and merge.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reconciled the active claim on 2026-11-02 under TASK-67. PR #55 is already open as a draft on agent/gh-13-1-bootstrap-federated-identities; do not start a second identity implementation. The historical TASK-6 record remains archived. Bootstrap approval, dev/test GitHub environment configuration, Azure FIC/RBAC readback and live OIDC authorization/denial evidence are still outstanding; no acceptance is checked.

Historical implementation evidence transferred from PR #55 / TASK-6 during TASK-67 reconciliation; these statements describe earlier PR revisions and do not complete the current live gates:

Implemented a dry-run-by-default Azure bootstrap script, dev/test environment OIDC smoke workflow, focused authorization policy tests, and a runbook with the repository-owner environment setup keys. Local verification: scripts/check.py and scripts/quality.py pass; full unittest suite passes (36 tests); git diff --check passes. actionlint is not installed locally and will be checked by PR CI. Azure identities and GitHub environments are not yet configured; the live OIDC success and cross-environment denial checks remain outstanding pending reviewed bootstrap and owner setup.

Published draft PR #55: https://github.com/vkaam/phonebuddy/pull/55. PR CI initially identified shellcheck SC2209 in the new workflow; fixed the assignment and reran on head 5bb5e4efe4231c0fae3ff0d103bf200a42957ad4. Quality and advisory risk checks both pass on that head. Bootstrap/runbook review, GitHub environment secrets/restrictions, Azure role/FIC readback, and live dev/test OIDC smoke runs remain outstanding.

Addressed both inline review findings in commit 921da72eb080e132968254a4cfc2573fac909bf3: bootstrap now validates the complete federated-credential list before any role assignment, and Azure CLI failures report only a sanitized exit status. Added regression coverage for unexpected/multiple trusts and command-argument redaction. Local full suite passes (38 tests), repository quality checks pass, and PR CI plus advisory risk checks pass on this revision. Both review threads were reacted to and resolved.

After integrating origin/main, local scripts/quality.py and all 40 Python tests passed; npm audit passed when rerun with network access. Local bundled browser verification could not launch because Playwright Chromium is not installed on this workstation; the hosted Quality check passed browser build/test and workflow lint on PR head 412d167fa6e97bd3c67685f30fa954d15df10e24, and advisory Risk report passed. PR #55 is current with main and review findings are resolved. TASK-6 remains In Progress pending reviewed Azure identity bootstrap, GitHub dev/test environment configuration, Azure federation/RBAC readback, and successful trusted dev/test OIDC smoke runs.

TASK-67 metadata reconciliation integrated main d015e6a into existing PR #55 without changing its five implementation files relative to the prior PR head. The full local scripts/check.py bundle passed on the integrated source (evidence: /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-93yvg6in/report.json). TASK-57 replaces the historical TASK-6 PR record; TASK-6 matches main and remains archived. Acceptance remains unchecked pending all existing live identity gates. Current-head hosted CI is required after push.

Verification 2026-11-02: owner reports acceptance setup complete. Read-only checks found dev and test GitHub environments and all three required Azure secret names, but GitHub reports no deployment branch policy for either. The signed-in Azure tenant returned zero exact-name matches for PhoneBuddy GitHub Deploy dev and test; this does not exclude differently named registrations or another tenant. No Azure OIDC authorization smoke workflow runs were found, and its workflow is not present on default branch; documented smoke requires main. Federation/RBAC and trusted success/cross-environment denial remain unverified. PR #55 head 6c94826 passed Quality run 41519243709 and advisory run 41519243907. Acceptance remains unchecked pending evidence and review; no bootstrap or environment mutation performed.

Further owner-supplied evidence: the named app registration was found in the active subscription tenant, which matches the supplied tenant. Read-only inspection found two GitHub Actions federated credentials on this single app, one for each dev/test environment, using repository-ID-qualified subjects and the Azure token-exchange audience. No role assignments for its service principal were returned in the active subscription. The task requires distinct environment identities and verified least-privilege roles; this inspection does not establish either. Main-only environment restrictions and live OIDC success/denial evidence remain unverified.

Owner-approved amendment implemented: shared app ID is explicit; bootstrap validates both exact GitHub environment trusts before granting Contributor on either selected foundation group; smoke verifies authentication from each environment and shared read access to both groups. Updated runbook documents shared write authority and review of existing app permissions. No Azure roles, secrets or branch policies have been changed. Live role readback, branch restrictions and both main-only smoke runs remain outstanding; task remains In Progress.

TASK-69 merged in PR #75. Owner configured main-only dev/test branch policies and supplied the shared principal; readback showed Contributor assignments at both foundation resource groups. Main workflow authenticated successfully for dev (https://github.com/vkaam/phonebuddy/actions/runs/41581057192) and test (https://github.com/vkaam/phonebuddy/actions/runs/41581143105); each run read both foundation groups. These runs prove authentication and read access, not absence of additional Azure privileges or external credentials.

2026-11-03 readback confirmed exactly the two expected repository-ID-qualified environment federations and Contributor role assignments for the shared principal at both approved foundation resource groups in the active subscription. Both GitHub environments restrict branches to main. The pre-existing shared app also has one password credential (value not inspected); its ownership and continued need require review and this task does not assert that the app is exclusively credential-free. The merged integration passed 71 Python tests, repository checks, actionlint, diff checks and the full local bundle (evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-0syh2srg/report.json). Acceptance and completion remain pending review of existing app access and current-head hosted checks.
<!-- SECTION:NOTES:END -->
