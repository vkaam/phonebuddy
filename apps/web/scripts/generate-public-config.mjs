import { mkdir, rm, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { validateConfig } from '../src/config.js';

const settingNames = [
  'PHONEBUDDY_DEV_API_BASE_URL',
  'PHONEBUDDY_DEV_ENTRA_TENANT_ID',
  'PHONEBUDDY_DEV_ENTRA_CLIENT_ID',
  'PHONEBUDDY_DEV_API_SCOPE',
];

export function createPublicConfig(env) {
  const missing = settingNames.filter(name => typeof env[name] !== 'string' || !env[name].trim());
  if (missing.length) return { status: 'unconfigured', missing };

  const candidate = {
    apiBaseUrl: env.PHONEBUDDY_DEV_API_BASE_URL,
    entraTenantId: env.PHONEBUDDY_DEV_ENTRA_TENANT_ID,
    entraClientId: env.PHONEBUDDY_DEV_ENTRA_CLIENT_ID,
    apiScope: env.PHONEBUDDY_DEV_API_SCOPE,
  };

  try {
    const config = validateConfig(candidate);
    if (new URL(config.apiBaseUrl).protocol !== 'https:') {
      return { status: 'invalid', reason: 'The hosted API URL must use HTTPS.' };
    }
    return { status: 'configured', config };
  } catch (error) {
    return { status: 'invalid', reason: error.message };
  }
}

export async function writePublicConfig(outputPath, env) {
  const destination = resolve(outputPath);
  await rm(destination, { force: true });

  const result = createPublicConfig(env);
  if (result.status !== 'configured') return result;

  await mkdir(dirname(destination), { recursive: true });
  await writeFile(destination, `${JSON.stringify(result.config, null, 2)}\n`, { mode: 0o644 });
  return result;
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const outputPath = process.argv[2] ?? 'dist/config.json';
  const result = await writePublicConfig(outputPath, process.env);
  if (result.status === 'unconfigured') {
    console.log(`No public runtime config generated; missing ${result.missing.join(', ')}.`);
  } else if (result.status === 'invalid') {
    console.log(`No public runtime config generated; settings are invalid: ${result.reason}`);
  } else {
    console.log(`Generated public runtime config at ${resolve(outputPath)}.`);
  }
}
