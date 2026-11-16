import { test } from 'node:test';
import assert from 'node:assert/strict';
import { sessionForAuthUpdate } from '../src/session.js';

test('silent renewal preserves the no-membership message and sign-out action', () => {
  const auth = {};
  const account = { username: 'user@example.test' };
  const current = { status: 'noMembership', auth, account, memberships: [] };
  const renewed = sessionForAuthUpdate(current, { status: 'signedIn', account }, auth, true);

  assert.equal(renewed.status, 'noMembership');
  assert.deepEqual(renewed.memberships, []);
  assert.equal(renewed.account, account);
});

test('unresolved or expired auth state stays behind the workspace gate', () => {
  const auth = {};
  const account = { username: 'user@example.test' };
  const pending = sessionForAuthUpdate({ status: 'loading' }, { status: 'signedIn', account }, auth, false);
  const expired = sessionForAuthUpdate({ status: 'signedIn' }, { status: 'reauthenticationRequired', account }, auth, true);

  assert.equal(pending.status, 'loading');
  assert.equal(expired.status, 'reauthenticationRequired');
});
