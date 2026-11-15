import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateConfig } from '../src/config.js';

const valid = {
  apiBaseUrl: 'https://api.example.com',
  entraTenantId: '11111111-1111-4111-8111-111111111111',
  entraClientId: '22222222-2222-4222-8222-222222222222',
  apiScope: 'api://33333333-3333-4333-8333-333333333333/access_as_user',
};

test('accepts a public HTTPS API URL and local development URL', () => {
  assert.equal(validateConfig(valid).apiBaseUrl, 'https://api.example.com/');
  assert.equal(validateConfig({ ...valid, apiBaseUrl: 'http://localhost:3000' }).apiBaseUrl, 'http://localhost:3000/');
});

test('rejects missing, insecure, malformed and credential-bearing public config', () => {
  for (const value of [
    null,
    {},
    { ...valid, apiBaseUrl: 'not a URL' },
    { ...valid, apiBaseUrl: 'http://example.com' },
    { ...valid, apiBaseUrl: 'https://user:secret@example.com' },
    { ...valid, apiBaseUrl: 'https://example.com/?token=secret' },
    { ...valid, clientSecret: 'never-public' },
    { ...valid, apiScope: 'https://graph.microsoft.com/.default' },
    { ...valid, entraTenantId: 'common' },
    { ...valid, entraClientId: 'not-a-guid' },
  ]) {
    assert.throws(() => validateConfig(value));
  }
});
