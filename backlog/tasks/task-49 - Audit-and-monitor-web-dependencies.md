---
id: TASK-49
title: Audit and monitor web dependencies
status: Done
assignee:
  - '@codex'
created_date: '2026-11-01T14:59:00Z'
updated_date: '2026-11-01T15:02:00Z'
labels:
  - factory
dependencies:
  - TASK-48
references:
  - https://github.com/vkaam/phonebuddy/issues/39
  - .github/dependabot.yml
  - .github/workflows/ci.yml
  - apps/web/package.json
  - apps/web/package-lock.json
  - scripts/check.py
  - tests/test_check.py
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
modified_files:
  - apps/web/package.json
  - apps/web/package-lock.json
  - scripts/check.py
  - tests/test_check.py
  - .github/workflows/ci.yml
  - .github/dependabot.yml
  - docs/quality-and-delivery.md
  - docs/agentic-development-contract.md
priority: high
type: chore
ordinal: 48000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/39
Approved issue revision: 2026-11-01T09:25:59Z; SHA-256 of UTF-8 issue body 43d9b91dacf902c20690fe34cdcedf3e6ae30ef6dfd402dfbf6e74105cb4f5d2. Approval: user approved issue #39 work and instructed continuation in this Codex chat on 2026-11-01.
Branch: agent/gh-39-2-npm-security
Scope: .github/dependabot.yml, .github/workflows/ci.yml, apps/web/package.json, apps/web/package-lock.json, scripts/check.py, tests/test_check.py, docs/quality-and-delivery.md, docs/agentic-development-contract.md and this task record only.
Dependency: TASK-48 completed on main via PR #56; archived TASK-34 remains historical and is not restored or treated as complete.
Verify from repository root: python3 -B -m unittest discover -s tests -v; python3 -B scripts/check.py; npm --prefix apps/web audit; git diff --check. Hosted Quality and PR safety checks must pass on the final PR head. Node, npm and registry access are required; registry errors fail the audit.
Spec: Add locked npm audit to local and hosted checks, enable Dependabot npm updates, document finding handling and limits, and update Vite from 6.3.5 to the non-major version 6.4.5 to address the currently reported high-severity advisory. Do not weaken checks or change application behavior. Other issue #39 outcomes remain outstanding.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Local and hosted verification run npm audit against the locked web dependencies; findings or an unavailable audit cause failure and leave accessible evidence.
- [x] #2 The current Vite high-severity audit finding is addressed without a major version upgrade; locked install, web tests and build pass.
- [x] #3 Dependabot proposes npm updates, and documentation describes how owners review findings and handle unresolved or unavailable scans.
- [x] #4 Declared verification and hosted checks pass; remaining browser, lint and issue-wide evidence gaps remain explicit.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Upgrade Vite to the non-major patched release and refresh its lockfile. 2. Add fail-closed npm audit with retained evidence locally and in hosted CI; enable weekly npm updates. 3. Document owner triage of findings and unavailable scans and retain other outstanding gates. 4. Run the declared checks, publish the PR and monitor its final head.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Local validation: 34 Python tests passed; npm audit reports zero vulnerabilities after updating Vite 6.3.5 to 6.4.5; python3 -B scripts/check.py passed all nine checks with unchanged source, evidence /private/var/folders/zs/9bq4j3rx3wng_vzz52w8hrf80000gn/T/phonebuddy-quality-myth52wo/report.json; git diff --check passed. CI, independent review, lint and browser smoke remain outstanding.

Draft PR: https://github.com/vkaam/phonebuddy/pull/57. Implementation commit 8461323; hosted checks and independent review pending. Issue #39 remains open for lint, browser smoke and remaining evidence requirements.

Hosted Quality https://github.com/vkaam/phonebuddy/actions/runs/41319088961 and PR safety advisory https://github.com/vkaam/phonebuddy/actions/runs/41319087569 passed on head 02f34bbd5f01fee481a5128f1fea81c1c9e80b66. Final task metadata commit requires fresh checks. Independent human review and merge remain outstanding; branch-local Done is provisional.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added local and hosted npm auditing with retained logs, weekly Dependabot npm updates, a Vite security update, and owner handling guidance. The local nine-check bundle, zero-vulnerability audit, 34 Python tests and pre-finalization hosted checks passed. Independent review and merge remain outstanding; broader issue #39 is not complete.
<!-- SECTION:FINAL_SUMMARY:END -->
