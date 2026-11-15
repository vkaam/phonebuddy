import { createRemoteJWKSet, jwtVerify, type JWTPayload, type JWTVerifyGetKey } from 'jose';
import { issuerForTenant, jwksUrlForTenant, type ApiConfig } from './config.js';
import type { Principal } from './repository.js';

const guid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export type AccessTokenVerifier = (token: string) => Promise<Principal>;

export class UnauthorizedError extends Error {
  constructor() {
    super('A valid PhoneBuddy access token is required.');
    this.name = 'UnauthorizedError';
  }
}

export function principalFromClaims(payload: JWTPayload, configuredTenantId: string): Principal {
  const tenantId = payload.tid;
  const objectId = payload.oid;
  if (typeof tenantId !== 'string' || typeof objectId !== 'string' ||
      !guid.test(tenantId) || !guid.test(objectId) ||
      tenantId.toLowerCase() !== configuredTenantId.toLowerCase()) {
    throw new UnauthorizedError();
  }
  return { tenantId: tenantId.toLowerCase(), objectId: objectId.toLowerCase() };
}

export function createEntraAccessTokenVerifier(
  config: ApiConfig,
  keys: JWTVerifyGetKey = createRemoteJWKSet(jwksUrlForTenant(config.tenantId)),
): AccessTokenVerifier {
  const issuer = issuerForTenant(config.tenantId);
  return async (token: string): Promise<Principal> => {
    try {
      const { payload } = await jwtVerify(token, keys, {
        algorithms: ['RS256'],
        audience: config.apiClientId,
        issuer,
        requiredClaims: ['exp', 'iat', 'tid', 'oid'],
        clockTolerance: 0,
      });
      return principalFromClaims(payload, config.tenantId);
    } catch {
      throw new UnauthorizedError();
    }
  };
}

export function bearerToken(header: string | undefined): string {
  const match = header?.match(/^Bearer ([A-Za-z0-9._~-]+)$/i);
  if (!match) throw new UnauthorizedError();
  return match[1];
}
