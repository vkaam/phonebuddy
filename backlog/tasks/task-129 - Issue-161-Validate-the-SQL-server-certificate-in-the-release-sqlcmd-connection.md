---
id: TASK-129
title: >-
  Issue 161 - Validate the SQL server certificate in the release sqlcmd
  connection
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-22T20:46:00Z'
updated_date: '2026-11-22T20:47:00Z'
labels: []
dependencies: []
ordinal: 109000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/161
Branch: agent/gh-161-sqlcmd-tls
Scope: scripts/database_release.py; tests/test_database_release.py
Verify: python3 -B scripts/quality.py; python3 -B scripts/run_required_unittests.py

A Codex review thread after TASK-128 merged (PR 163, scripts/database_release.py) found that SqlcmdConnection never passes -N, so go-sqlcmd v1.10.0 does not validate the server certificate and a network interceptor could capture the Entra bearer token. go-sqlcmd v1.10.0 accepts -N true (cmd/sqlcmd/sqlcmd.go encryptConnectionAllowsTLS lists true) and -C is the flag that disables validation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Every SqlcmdConnection invocation (execute and query) passes -N true so encryption with certificate validation is required
- [ ] #2 No SqlcmdConnection invocation passes -C (trust server certificate)
- [ ] #3 A unit test asserts the argument list contains -N true and not -C for both execute and query
- [ ] #4 python3 -B scripts/quality.py and python3 -B scripts/run_required_unittests.py pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add -N true to SqlcmdConnection base args. 2. Test execute and query args contain -N true and not -C.
<!-- SECTION:PLAN:END -->
