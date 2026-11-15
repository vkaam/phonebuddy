import { BrowserCacheLocation, PublicClientApplication } from '@azure/msal-browser';

function isInteractionRequired(error) {
  return error?.name === 'InteractionRequiredAuthError' ||
    ['interaction_required', 'login_required', 'consent_required'].includes(error?.errorCode);
}

export function createAuthService(client, { apiScope, postLogoutRedirectUri }) {
  let snapshot = { status: 'loading', account: null };
  const listeners = new Set();
  const publish = (status, account = snapshot.account) => {
    snapshot = { status, account };
    for (const listener of listeners) listener(snapshot);
  };

  async function acquireToken(account) {
    const result = await client.acquireTokenSilent({ account, scopes: [apiScope] });
    if (!result?.accessToken) throw new Error('Entra did not return an API access token.');
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
        if (isInteractionRequired(error)) publish('reauthenticationRequired', snapshot.account);
        throw error;
      }
    },
    requireSignIn() {
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
