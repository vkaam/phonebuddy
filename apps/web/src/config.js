/** Public browser configuration. Never include secrets or credentials. */
export function validateConfig(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value) || typeof value.apiBaseUrl !== 'string') {
    throw new Error('Set apiBaseUrl and Entra settings in the public config.json file.');
  }
  if (['clientSecret', 'client_secret', 'accessToken', 'refreshToken', 'apiKey'].some(key => Object.hasOwn(value, key))) {
    throw new Error('The public config.json file cannot contain secrets or tokens.');
  }
  let url;
  try { url = new URL(value.apiBaseUrl); } catch {
    throw new Error('Set apiBaseUrl to an absolute HTTPS URL in config.json.');
  }
  if (url.username || url.password || url.search || url.hash ||
      (url.protocol !== 'https:' && !(url.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(url.hostname)))) {
    throw new Error('Use an HTTPS apiBaseUrl without credentials, query or fragment (HTTP is allowed for localhost).');
  }
  const guid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
  if (typeof value.entraTenantId !== 'string' || !guid.test(value.entraTenantId)) {
    throw new Error('Set entraTenantId to the Entra tenant GUID in config.json.');
  }
  if (typeof value.entraClientId !== 'string' || !guid.test(value.entraClientId)) {
    throw new Error('Set entraClientId to the public SPA client GUID in config.json.');
  }
  if (typeof value.apiScope !== 'string' || !/^api:\/\/[0-9a-f-]{36}\/[A-Za-z0-9._-]+$/i.test(value.apiScope)) {
    throw new Error('Set apiScope to the exposed PhoneBuddy API scope in config.json.');
  }
  return {
    apiBaseUrl: url.href,
    entraTenantId: value.entraTenantId.toLowerCase(),
    entraClientId: value.entraClientId.toLowerCase(),
    apiScope: value.apiScope,
  };
}
