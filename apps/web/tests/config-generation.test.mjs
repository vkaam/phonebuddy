import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createPublicConfig, writePublicConfig } from '../scripts/generate-public-config.mjs';

const valid = {
  PHONEBUDDY_DEV_API_BASE_URL: 'https://api.dev.example.com',
  PHONEBUDDY_DEV_ENTRA_TENANT_ID: 'c6e0e022-d1c1-4dbf-9ff6-e4567e725fd2',
  PHONEBUDDY_DEV_ENTRA_CLIENT_ID: '5eade0d8-9047-4efb-87f6-1051b81700d2',
  PHONEBUDDY_DEV_API_SCOPE: 'api://5eade0d8-9047-4efb-87f6-1051b81700d2/access_as_user',
};

test('creates a normalized allow-listed public config from dev values', () => {
  const result = createPublicConfig({ ...valid, CLIENT_SECRET: 'must-not-be-copied' });

  assert.equal(result.status, 'configured');
  assert.deepEqual(result.config, {
    apiBaseUrl: 'https://api.dev.example.com/',
    entraTenantId: valid.PHONEBUDDY_DEV_ENTRA_TENANT_ID,
    entraClientId: valid.PHONEBUDDY_DEV_ENTRA_CLIENT_ID,
    apiScope: valid.PHONEBUDDY_DEV_API_SCOPE,
  });
  assert.deepEqual(Object.keys(result.config), ['apiBaseUrl', 'entraTenantId', 'entraClientId', 'apiScope']);
});

test('leaves the site unconfigured when any required value is absent', () => {
  for (const key of Object.keys(valid)) {
    const env = { ...valid };
    delete env[key];
    assert.deepEqual(createPublicConfig(env), { status: 'unconfigured', missing: [key] });
  }
});

test('rejects invalid, local-only, and credential-bearing hosted API URLs', () => {
  for (const apiBaseUrl of [
    'not-a-url',
    'http://api.dev.example.com',
    'http://localhost:3000',
    'https://user:secret@api.dev.example.com',
    'https://api.dev.example.com/?token=secret',
  ]) {
    assert.equal(createPublicConfig({ ...valid, PHONEBUDDY_DEV_API_BASE_URL: apiBaseUrl }).status, 'invalid');
  }
});

test('rejects invalid Entra identifiers and API scopes', () => {
  for (const env of [
    { ...valid, PHONEBUDDY_DEV_ENTRA_TENANT_ID: 'common' },
    { ...valid, PHONEBUDDY_DEV_ENTRA_CLIENT_ID: 'not-a-guid' },
    { ...valid, PHONEBUDDY_DEV_API_SCOPE: 'https://graph.microsoft.com/.default' },
  ]) {
    assert.equal(createPublicConfig(env).status, 'invalid');
  }
});

test('removes stale config when settings are missing or invalid and writes only valid public values', async () => {
  const directory = await mkdtemp(join(tmpdir(), 'phonebuddy-web-config-'));
  const output = join(directory, 'dist', 'config.json');
  try {
    await mkdir(join(directory, 'dist'));
    await writeFile(output, '{"stale":true}\n');
    assert.equal((await writePublicConfig(output, {})).status, 'unconfigured');
    await assert.rejects(readFile(output));

    await writeFile(output, '{"stale":true}\n');
    assert.equal((await writePublicConfig(output, { ...valid, PHONEBUDDY_DEV_ENTRA_TENANT_ID: 'common' })).status, 'invalid');
    await assert.rejects(readFile(output));

    assert.equal((await writePublicConfig(output, valid)).status, 'configured');
    assert.deepEqual(JSON.parse(await readFile(output, 'utf8')), createPublicConfig(valid).config);
  } finally {
    await rm(directory, { recursive: true, force: true });
  }
});
