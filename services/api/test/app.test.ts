import assert from 'node:assert/strict';
import { after, before, test } from 'node:test';
import { createLocalJWKSet, exportJWK, generateKeyPair, SignJWT } from 'jose';
import { buildApi } from '../src/app.js';
import { issuerForTenant, readApiConfig, type ApiConfig } from '../src/config.js';
import { MemoryAuthRepository, RetryableConnection } from '../src/repository.js';
import { createEntraAccessTokenVerifier } from '../src/token.js';

const tenantId = '11111111-1111-4111-8111-111111111111';
const apiClientId = '22222222-2222-4222-8222-222222222222';
const objectId = '33333333-3333-4333-8333-333333333333';
const organizationA = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
const organizationB = 'bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb';
const config: ApiConfig = {
  host: '127.0.0.1',
  port: 3000,
  tenantId,
  apiClientId,
  webOrigin: 'https://phonebuddy.example',
  sqlServer: 'phonebuddy.database.windows.net',
  sqlDatabase: 'phonebuddy',
  releaseVersion: 'test-release',
};

const { privateKey, publicKey } = await generateKeyPair('RS256');
const publicJwk = await exportJWK(publicKey);
const keySet = createLocalJWKSet({ keys: [{ ...publicJwk, kid: 'test-key', alg: 'RS256', use: 'sig' }] });
const verifyAccessToken = createEntraAccessTokenVerifier(config, keySet);
const repository = new MemoryAuthRepository();
const principal = { tenantId, objectId };
repository.addMembership(principal, organizationA, 'user');
repository.addMembership(principal, organizationB, 'admin');
const api = await buildApi({ config, repository, verifyAccessToken, logger: false });
let baseUrl = '';

async function token(options: { issuer?: string; audience?: string; expiresAt?: number; signer?: typeof privateKey } = {}): Promise<string> {
  const now = Math.floor(Date.now() / 1000);
  return new SignJWT({ tid: tenantId, oid: objectId })
    .setProtectedHeader({ alg: 'RS256', kid: 'test-key' })
    .setIssuer(options.issuer ?? issuerForTenant(tenantId))
    .setAudience(options.audience ?? apiClientId)
    .setIssuedAt(now)
    .setExpirationTime(options.expiresAt ?? now + 300)
    .sign(options.signer ?? privateKey);
}

async function issueTicket(organizationId = organizationA, accessToken?: string): Promise<string> {
  const bearer = accessToken ?? await token();
  const response = await api.inject({
    method: 'POST',
    url: '/api/ws-ticket',
    headers: { authorization: `Bearer ${bearer}`, origin: config.webOrigin },
    payload: { organizationId },
  });
  assert.equal(response.statusCode, 201, response.body);
  return response.json<{ ticket: string }>().ticket;
}

function websocketUrl(organizationId: string): string {
  const address = new URL(baseUrl);
  return `ws://${address.host}/api/organizations/${organizationId}/socket`;
}

async function expectRejectedSocket(organizationId: string, ticket: string): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    const socket = new WebSocket(websocketUrl(organizationId), [`phonebuddy-ticket.${ticket}`]);
    const timeout = setTimeout(() => {
      socket.close();
      reject(new Error('WebSocket rejection timed out.'));
    }, 2000);
    socket.addEventListener('open', () => {
      clearTimeout(timeout);
      socket.close();
      reject(new Error('WebSocket unexpectedly opened.'));
    }, { once: true });
    socket.addEventListener('error', () => {
      clearTimeout(timeout);
      resolve();
    }, { once: true });
  });
}

before(async () => {
  baseUrl = await api.listen({ host: '127.0.0.1', port: 0 });
});

after(async () => {
  await api.close();
});

test('API configuration fails closed on missing or unsafe settings', () => {
  assert.throws(() => readApiConfig({}), /Missing required setting/);
  assert.throws(() => readApiConfig({
    ENTRA_TENANT_ID: tenantId,
    ENTRA_API_CLIENT_ID: apiClientId,
    SQL_SERVER: 'phonebuddy.database.windows.net',
    SQL_DATABASE: 'phonebuddy',
    WEB_ORIGIN: 'http://phonebuddy.example',
  }), /WEB_ORIGIN/);
});

test('a failed SQL connection attempt is shared then cleared so a later request can retry', async () => {
  const connection = new RetryableConnection<{ id: number }>();
  let attempts = 0;
  const connect = async () => {
    attempts += 1;
    if (attempts === 1) throw new Error('transient connection failure');
    return { id: attempts };
  };

  const first = connection.get(connect);
  assert.equal(connection.get(connect), first);
  await assert.rejects(first, /transient connection failure/);
  assert.deepEqual(await connection.get(connect), { id: 2 });
  assert.equal(attempts, 2);
});

test('API validates token signature, issuer, audience, and expiration', async () => {
  const valid = await token();
  const response = await api.inject({ method: 'GET', url: '/api/me', headers: { authorization: `Bearer ${valid}` } });
  assert.equal(response.statusCode, 200);

  const wrongIssuer = await token({ issuer: 'https://attacker.example' });
  const wrongAudience = await token({ audience: '33333333-3333-4333-8333-333333333333' });
  const expired = await token({ expiresAt: Math.floor(Date.now() / 1000) - 30 });
  const { privateKey: otherKey } = await generateKeyPair('RS256');
  const badSignature = await token({ signer: otherKey });

  for (const invalid of [wrongIssuer, wrongAudience, expired, badSignature, 'not-a-token']) {
    const denied = await api.inject({ method: 'GET', url: '/api/me', headers: { authorization: `Bearer ${invalid}` } });
    assert.equal(denied.statusCode, 401, denied.body);
  }
  const missing = await api.inject({ method: 'GET', url: '/api/me' });
  assert.equal(missing.statusCode, 401);
});

test('organization memberships and roles come from the server-side membership store', async () => {
  const response = await api.inject({
    method: 'GET',
    url: '/api/me',
    headers: { authorization: `Bearer ${await token()}` },
  });
  assert.equal(response.statusCode, 200);
  assert.deepEqual(response.json().memberships, [
    { organizationId: organizationA, role: 'user' },
    { organizationId: organizationB, role: 'admin' },
  ]);

  const denied = await api.inject({
    method: 'POST',
    url: '/api/ws-ticket',
    headers: { authorization: `Bearer ${await token()}` },
    payload: { organizationId: 'cccccccc-cccc-4ccc-8ccc-cccccccccccc' },
  });
  assert.equal(denied.statusCode, 403);
});

test('ticket WebSocket access is scoped, short-lived, one-use, and rechecks membership', async () => {
  const ticket = await issueTicket(organizationA);
  await expectRejectedSocket(organizationB, ticket);

  const accepted = await new Promise<string>((resolve, reject) => {
    const socket = new WebSocket(websocketUrl(organizationA), [`phonebuddy-ticket.${ticket}`]);
    const timeout = setTimeout(() => reject(new Error('WebSocket response timed out.')), 2000);
    socket.addEventListener('message', event => {
      clearTimeout(timeout);
      resolve(String(event.data));
      socket.close();
    }, { once: true });
    socket.addEventListener('error', () => {
      clearTimeout(timeout);
      reject(new Error('Authorized WebSocket was rejected.'));
    }, { once: true });
  });
  assert.equal(JSON.parse(accepted).organizationId, organizationA);
  await expectRejectedSocket(organizationA, ticket);

  const revokedTicket = await issueTicket(organizationA);
  repository.revokeMembership(principal, organizationA);
  await expectRejectedSocket(organizationA, revokedTicket);
});

test('GET /ready is unauthenticated, reports the release version, and logs one health_request line', async () => {
  const lines: string[] = [];
  const probe = await buildApi({ config, repository, verifyAccessToken, logger: false, healthLog: line => lines.push(line) });
  try {
    const ready = await probe.inject({ method: 'GET', url: '/ready?secret=value', headers: { authorization: 'Bearer secret' } });
    assert.equal(ready.statusCode, 200);
    assert.deepEqual(ready.json(), { version: 'test-release', ready: true });
    const health = await probe.inject({ method: 'GET', url: '/health' });
    assert.equal(health.statusCode, 200);
    assert.equal(lines.length, 2);
    for (const line of lines) {
      const event = JSON.parse(line);
      assert.deepEqual(Object.keys(event), ['event', 'version', 'status', 'duration_ms']);
      assert.equal(event.event, 'health_request');
      assert.equal(event.version, 'test-release');
      assert.equal(event.status, 200);
      assert.equal(typeof event.duration_ms, 'number');
      assert.ok(!line.includes('secret'));
    }
    await probe.inject({ method: 'GET', url: '/api/me' });
    assert.equal(lines.length, 2);
  } finally {
    await probe.close();
  }
});

test('browser requests are accepted only from the configured WEB_ORIGIN', async () => {
  const allowed = await api.inject({ method: 'OPTIONS', url: '/api/me', headers: { origin: config.webOrigin } });
  assert.equal(allowed.statusCode, 204);
  assert.equal(allowed.headers['access-control-allow-origin'], config.webOrigin);
  const denied = await api.inject({ method: 'GET', url: '/api/me', headers: { origin: 'https://attacker.example' } });
  assert.equal(denied.statusCode, 403);
  assert.equal(denied.headers['access-control-allow-origin'], undefined);
});

test('API configuration defaults to port 8080 and reads RELEASE_VERSION', () => {
  const env = {
    ENTRA_TENANT_ID: tenantId,
    ENTRA_API_CLIENT_ID: apiClientId,
    SQL_SERVER: 'phonebuddy.database.windows.net',
    SQL_DATABASE: 'phonebuddy',
    WEB_ORIGIN: 'https://phonebuddy.example',
  };
  assert.equal(readApiConfig(env).port, 8080);
  assert.equal(readApiConfig(env).releaseVersion, 'unknown');
  assert.equal(readApiConfig({ ...env, RELEASE_VERSION: 'abc123' }).releaseVersion, 'abc123');
});
