---
id: TASK-132
title: Issue 152 - Keep the Sign out button inside the sidebar so it can be clicked
status: In Progress
assignee:
  - '@claude'
created_date: '2026-11-23T17:47:00Z'
labels:
  - bug
dependencies: []
ordinal: 112000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Issue: https://github.com/vkaam/phonebuddy/issues/152
Branch: agent/gh-152-signout-layout
Scope: apps/web/src/**, apps/web/tests/**
Verify: cd apps/web && npm test && npm run lint && npm run build; python3 -B scripts/quality.py

On the hosted dev app the signed-in sidebar shows a long account email, and the Sign out button wraps onto two lines and sits across the 244px sidebar border. Measured in headless Chromium, the button spans x 228-268 while the sidebar ends at 244, so its centre is under the workspace area and the click lands on main, never on the button. Sign-out therefore does nothing, which blocks the issue 152 sign-out requirement.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 The account block shrinks with an ellipsis on long emails and keeps the Sign out button on one line inside the sidebar
- [ ] #2 The Sign out button is the element hit at its centre point and a click reaches it, for short and very long emails at desktop widths
- [ ] #3 A test asserts the button is rendered and wired to auth.signOut and that the layout rules keeping it inside the 244px sidebar exist, and the web test, lint, build and quality checks pass
<!-- AC:END -->
