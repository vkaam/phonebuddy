import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateConfig } from '../src/config.js';

test('accepts a public HTTPS API URL and local development URL', () => {
  assert.equal(validateConfig({ apiBaseUrl: 'https://api.example.com' }).apiBaseUrl, 'https://api.example.com/');
  assert.equal(validateConfig({ apiBaseUrl: 'http://localhost:3000' }).apiBaseUrl, 'http://localhost:3000/');
});

test('rejects missing, insecure, malformed and credential-bearing URLs', () => {
  for (const value of [null, {}, { apiBaseUrl: 'not a URL' }, { apiBaseUrl: 'http://example.com' }, { apiBaseUrl: 'https://user:secret@example.com' }, { apiBaseUrl: 'https://example.com/?token=secret' }]) {
    assert.throws(() => validateConfig(value));
  }
});
