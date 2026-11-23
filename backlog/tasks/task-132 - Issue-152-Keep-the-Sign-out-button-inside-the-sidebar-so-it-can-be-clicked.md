---
id: TASK-132
title: Issue 152 - Keep the Sign out button inside the sidebar so it can be clicked
status: Done
assignee:
  - '@claude'
created_date: '2026-11-23T17:47:00Z'
updated_date: '2026-11-23T17:47:00Z'
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
- [x] #1 The account block shrinks with an ellipsis on long emails and keeps the Sign out button on one line inside the sidebar
- [x] #2 The Sign out button is the element hit at its centre point and a click reaches it, for short and very long emails at desktop widths
- [x] #3 A test asserts the button is rendered and wired to auth.signOut and that the layout rules keeping it inside the 244px sidebar exist, and the web test, lint, build and quality checks pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Reproduce in headless Chromium with the real CSS. 2. Let the account text shrink with an ellipsis and pin the button. 3. Add a structure/CSS test.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reproduced with the unmodified src/style.css in headless Chromium and a fake signed-in sidebar fixture: Sign out button x 228-268 vs sidebar right edge 244, elementFromPoint at its centre returns MAIN, click not delivered. After fix: button x 161-221, hit is the button, click delivered at 1280/900/761px, for a short and a 90-char email. auth.signOut() in auth.js reviewed: publishes redirecting then logoutRedirect with origin as postLogoutRedirectUri; no change needed.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Root cause: the long email made the flex row overflow, so the Sign out button wrapped and extended past the 244px sidebar under .workspace, which received the click. Fix: the account text is a shrinkable flex child (min-width:0, ellipsis, nowrap, title shows the full email) and the avatar and button no longer shrink (button nowrap). Verified in headless Chromium for short and long emails at desktop widths; the 760px-and-below layout hides the account block as before. Added apps/web/tests/sidebar-layout.test.mjs. npm test, lint, build and scripts/quality.py pass. Risk: the email shows about 80px before the ellipsis; a stacked layout could be considered later. Live proof after deploy is separate.
<!-- SECTION:FINAL_SUMMARY:END -->
