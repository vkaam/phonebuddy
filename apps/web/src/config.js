/** Public browser configuration. Never include secrets or credentials. */
export function validateConfig(value) {
  if (!value || typeof value !== 'object' || typeof value.apiBaseUrl !== 'string') {
    throw new Error('Set apiBaseUrl in the public config.json file.');
  }
  let url;
  try { url = new URL(value.apiBaseUrl); } catch {
    throw new Error('Set apiBaseUrl to an absolute HTTPS URL in config.json.');
  }
  if (url.username || url.password || url.search || url.hash ||
      (url.protocol !== 'https:' && !(url.protocol === 'http:' && ['localhost', '127.0.0.1'].includes(url.hostname)))) {
    throw new Error('Use an HTTPS apiBaseUrl without credentials, query or fragment (HTTP is allowed for localhost).');
  }
  return { apiBaseUrl: url.href };
}
