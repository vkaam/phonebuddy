const guid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export interface ApiConfig {
  host: string;
  port: number;
  tenantId: string;
  apiClientId: string;
  webOrigin: string;
  sqlServer: string;
  sqlDatabase: string;
  sqlManagedIdentityClientId?: string;
}

function required(env: NodeJS.ProcessEnv, key: string): string {
  const value = env[key]?.trim();
  if (!value) throw new Error(`Missing required setting ${key}.`);
  return value;
}

export function readApiConfig(env: NodeJS.ProcessEnv = process.env): ApiConfig {
  const tenantId = required(env, 'ENTRA_TENANT_ID');
  const apiClientId = required(env, 'ENTRA_API_CLIENT_ID');
  const sqlServer = required(env, 'SQL_SERVER');
  const sqlDatabase = required(env, 'SQL_DATABASE');
  const webOrigin = required(env, 'WEB_ORIGIN');
  const parsedOrigin = new URL(webOrigin);

  if (!guid.test(tenantId)) throw new Error('ENTRA_TENANT_ID must be a tenant GUID.');
  if (!guid.test(apiClientId)) throw new Error('ENTRA_API_CLIENT_ID must be an application GUID.');
  if (env.SQL_MANAGED_IDENTITY_CLIENT_ID && !guid.test(env.SQL_MANAGED_IDENTITY_CLIENT_ID)) {
    throw new Error('SQL_MANAGED_IDENTITY_CLIENT_ID must be an application GUID.');
  }
  if (parsedOrigin.origin !== webOrigin ||
      (parsedOrigin.protocol !== 'https:' && !['localhost', '127.0.0.1'].includes(parsedOrigin.hostname))) {
    throw new Error('WEB_ORIGIN must be one HTTPS origin (HTTP is allowed for local development).');
  }
  if (!/^[a-zA-Z0-9.-]+\.database\.windows\.net$/.test(sqlServer)) {
    throw new Error('SQL_SERVER must be an Azure SQL server hostname.');
  }
  if (!/^[a-zA-Z0-9_-]{1,128}$/.test(sqlDatabase)) {
    throw new Error('SQL_DATABASE must be a database name.');
  }
  const port = Number(env.PORT ?? 3000);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('PORT must be between 1 and 65535.');

  return {
    host: env.HOST?.trim() || '0.0.0.0',
    port,
    tenantId,
    apiClientId,
    webOrigin,
    sqlServer,
    sqlDatabase,
    sqlManagedIdentityClientId: env.SQL_MANAGED_IDENTITY_CLIENT_ID?.trim() || undefined,
  };
}

export function issuerForTenant(tenantId: string): string {
  if (!guid.test(tenantId)) throw new Error('Tenant ID must be a GUID.');
  return `https://login.microsoftonline.com/${tenantId}/v2.0`;
}

export function jwksUrlForTenant(tenantId: string): URL {
  if (!guid.test(tenantId)) throw new Error('Tenant ID must be a GUID.');
  return new URL(`https://login.microsoftonline.com/${tenantId}/discovery/v2.0/keys`);
}
