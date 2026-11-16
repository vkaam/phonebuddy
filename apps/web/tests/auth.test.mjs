import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createAuthService } from '../src/auth.js';

function fakeClient({ account = null, redirectResult = null, tokenError = null, tokenErrorAfter = 1, expiresOn = null } = {}) {
  const calls = [];
  let silentCalls = 0;
  let activeAccount = account;
  return {
    calls,
    async initialize() { calls.push(['initialize']); },
    async handleRedirectPromise() { calls.push(['handleRedirectPromise']); return redirectResult; },
    getActiveAccount() { return activeAccount; },
    getAllAccounts() { return account ? [account] : []; },
    setActiveAccount(value) { calls.push(['setActiveAccount', value]); activeAccount = value; },
    async acquireTokenSilent(request) {
      calls.push(['acquireTokenSilent', request]);
      silentCalls += 1;
      if (tokenError && silentCalls >= tokenErrorAfter) throw tokenError;
      return { accessToken: 'synthetic-api-access-token', expiresOn };
    },
    async loginRedirect(request) { calls.push(['loginRedirect', request]); },
    async logoutRedirect(request) { calls.push(['logoutRedirect', request]); },
  };
}

test('initialization handles Entra redirect and keeps account state in the auth service', async () => {
  const account = { homeAccountId: 'account-1', username: 'user@example.test' };
  const client = fakeClient({ redirectResult: { account } });
  const auth = createAuthService(client, { apiScope: 'api://api-id/access_as_user', postLogoutRedirectUri: 'https://app.example' });
  const snapshots = [];
  auth.subscribe(value => snapshots.push(value.status));

  const result = await auth.initialize();
  assert.equal(result.status, 'signedIn');
  assert.equal(result.account, account);
  assert.deepEqual(snapshots, ['loading', 'signedIn']);
  assert.equal(await auth.getAccessToken(), 'synthetic-api-access-token');
  assert.deepEqual(client.calls.find(([name]) => name === 'acquireTokenSilent')[1].scopes, ['api://api-id/access_as_user']);
});

test('expired or interaction-required sessions are marked for sign-in again', async () => {
  const account = { homeAccountId: 'account-1', username: 'user@example.test' };
  const client = fakeClient({ account, tokenError: { name: 'InteractionRequiredAuthError', errorCode: 'interaction_required' } });
  const auth = createAuthService(client, { apiScope: 'scope', postLogoutRedirectUri: 'https://app.example' });
  const result = await auth.initialize();
  assert.equal(result.status, 'reauthenticationRequired');

  auth.requireSignIn();
  assert.equal(auth.getSnapshot().status, 'reauthenticationRequired');
  await assert.rejects(auth.getAccessToken(), error => error?.name === 'InteractionRequiredAuthError' && error.errorCode === 'interaction_required');
});

test('session is cleared and reauthentication is requested when silent renewal expires', async () => {
  const account = { homeAccountId: 'account-1', username: 'user@example.test' };
  const client = fakeClient({
    account,
    tokenError: { name: 'InteractionRequiredAuthError', errorCode: 'interaction_required' },
    tokenErrorAfter: 2,
    expiresOn: new Date(Date.now() + 25),
  });
  const auth = createAuthService(client, { apiScope: 'scope', postLogoutRedirectUri: 'https://app.example' });
  const needsSignIn = new Promise(resolve => {
    const unsubscribe = auth.subscribe(snapshot => {
      if (snapshot.status === 'reauthenticationRequired') { unsubscribe(); resolve(snapshot); }
    });
  });

  assert.equal((await auth.initialize()).status, 'signedIn');
  const expired = await needsSignIn;
  assert.equal(expired.account, account);
  assert.equal(auth.getSnapshot().status, 'reauthenticationRequired');
});

test('sign-out uses the current account and the configured redirect URI', async () => {
  const account = { homeAccountId: 'account-1', username: 'user@example.test' };
  const client = fakeClient({ account });
  const auth = createAuthService(client, { apiScope: 'scope', postLogoutRedirectUri: 'https://app.example' });
  await auth.initialize();
  await auth.signOut();
  assert.deepEqual(client.calls.at(-1), ['logoutRedirect', { account, postLogoutRedirectUri: 'https://app.example' }]);
  assert.equal(auth.getSnapshot().status, 'redirecting');
});

test('sign-in requests the API scope through the redirect flow', async () => {
  const client = fakeClient();
  const auth = createAuthService(client, { apiScope: 'api://api-id/access_as_user', postLogoutRedirectUri: 'https://app.example' });
  await auth.signIn();
  assert.deepEqual(client.calls.at(-1), ['loginRedirect', { scopes: ['api://api-id/access_as_user'] }]);
  assert.equal(auth.getSnapshot().status, 'redirecting');
});
