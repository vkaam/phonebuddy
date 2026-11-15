import { BrowserCacheLocation, PublicClientApplication } from '@azure/msal-browser';

function isInteractionRequired(error) {
  return error?.name === 'InteractionRequiredAuthError' ||
    ['interaction_required', 'login_required', 'consent_required'].includes(error?.errorCode);
}

export function createAuthService(client, { apiScope, postLogoutRedirectUri }) {
  let snapshot = { status: 'loading', account: null };
  let expiryTimer;
  const listeners = new Set();
  const publish = (status, account = snapshot.account) => {
    snapshot = { status, account };
    for (const listener of listeners) listener(snapshot);
  };

  function clearExpiryTimer() {
    if (expiryTimer) clearTimeout(expiryTimer);
    expiryTimer = undefined;
  }

  async function acquireToken(account) {
    const result = await client.acquireTokenSilent({ account, scopes: [apiScope] });
    if (!result?.accessToken) throw new Error('Entra did not return an API access token.');
    clearExpiryTimer();
    const expiresAt = result.expiresOn instanceof Date ? result.expiresOn.getTime() : Number.NaN;
    if (Number.isFinite(expiresAt)) {
      expiryTimer = setTimeout(async () => {
        expiryTimer = undefined;
        try {
          await acquireToken(account);
          publish('signedIn', account);
        } catch {
          publish('reauthenticationRequired', account);
        }
      }, Math.max(0, expiresAt - Date.now()));
    }
    return result.accessToken;
  }

  return {
    getSnapshot: () => snapshot,
    subscribe(listener) {
      listeners.add(listener);
      listener(snapshot);
      return () => listeners.delete(listener);
    },
    async initialize() {
      await client.initialize();
      const result = await client.handleRedirectPromise();
      const account = result?.account ?? client.getActiveAccount() ?? client.getAllAccounts()[0] ?? null;
      if (!account) {
        publish('signedOut', null);
        return snapshot;
      }
      client.setActiveAccount(account);
      try {
        await acquireToken(account);
        publish('signedIn', account);
      } catch (error) {
        if (!isInteractionRequired(error)) throw error;
        clearExpiryTimer();
        publish('reauthenticationRequired', account);
      }
      return snapshot;
    },
    async signIn() {
      publish('redirecting', null);
      await client.loginRedirect({ scopes: [apiScope] });
    },
    async signOut() {
      const account = snapshot.account;
      clearExpiryTimer();
      publish('redirecting', null);
      await client.logoutRedirect({ account, postLogoutRedirectUri });
    },
    async getAccessToken() {
      if (!snapshot.account) throw new Error('Sign in to continue.');
      try {
        const accessToken = await acquireToken(snapshot.account);
        publish('signedIn', snapshot.account);
        return accessToken;
      } catch (error) {
        if (isInteractionRequired(error)) {
          clearExpiryTimer();
          publish('reauthenticationRequired', snapshot.account);
        }
        throw error;
      }
    },
    requireSignIn() {
      clearExpiryTimer();
      if (snapshot.account) publish('reauthenticationRequired', snapshot.account);
    },
  };
}

export function createMsalAuthService(config) {
  const redirectUri = window.location.origin;
  const client = new PublicClientApplication({
    auth: {
      clientId: config.entraClientId,
      authority: `https://login.microsoftonline.com/${config.entraTenantId}`,
      redirectUri,
      postLogoutRedirectUri: redirectUri,
    },
    cache: {
      cacheLocation: BrowserCacheLocation.SessionStorage,
      storeAuthStateInCookie: false,
    },
  });
  return createAuthService(client, { apiScope: config.apiScope, postLogoutRedirectUri: redirectUri });
}
