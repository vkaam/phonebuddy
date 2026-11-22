import { createHash, randomBytes } from 'node:crypto';
import Fastify, { LogController, type FastifyInstance, type FastifyRequest } from 'fastify';
import websocket from '@fastify/websocket';
import { bearerToken, UnauthorizedError, type AccessTokenVerifier } from './token.js';
import type { ApiConfig } from './config.js';
import type { AuthRepository, Principal, SocketTicketIdentity } from './repository.js';

const guid = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const ticketLifetimeMs = 30_000;
const ticketProtocolPrefix = 'phonebuddy-ticket.';

export interface ApiDependencies {
  config: ApiConfig;
  repository: AuthRepository;
  verifyAccessToken: AccessTokenVerifier;
  now?: () => Date;
  logger?: boolean;
  /** Receives one JSON line per /, /ready or /health request. Defaults to stdout. */
  healthLog?: (line: string) => void;
}

const healthPaths = new Set(['/', '/ready', '/health']);

function isHealthRequest(url: string | undefined): boolean {
  return healthPaths.has((url ?? '').split('?')[0]);
}

function ticketHash(ticket: string): string {
  return createHash('sha256').update(ticket, 'utf8').digest('hex');
}

function websocketTicket(request: FastifyRequest): string | undefined {
  const header = request.headers['sec-websocket-protocol'];
  const values = Array.isArray(header) ? header : header?.split(',') ?? [];
  const item = values.map(value => value.trim()).find(value => value.startsWith(ticketProtocolPrefix));
  const ticket = item?.slice(ticketProtocolPrefix.length);
  return ticket && /^[A-Za-z0-9_-]{40,64}$/.test(ticket) ? ticket : undefined;
}

export async function buildApi(dependencies: ApiDependencies): Promise<FastifyInstance> {
  const { config, repository, verifyAccessToken } = dependencies;
  const now = dependencies.now ?? (() => new Date());
  const principals = new WeakMap<FastifyRequest, Principal>();
  const socketIdentities = new WeakMap<FastifyRequest, SocketTicketIdentity>();
  const app = Fastify({
    logger: dependencies.logger === false ? false : {
      redact: ['req.headers.authorization', 'req.headers.sec-websocket-protocol'],
    },
    // Health probes emit only the single health_request line below.
    logController: new LogController({ disableRequestLogging: request => isHealthRequest(request.url) }),
  });
  const healthLog = dependencies.healthLog ?? (line => { process.stdout.write(`${line}\n`); });

  app.addHook('onResponse', async (request, reply) => {
    if (!isHealthRequest(request.url)) return;
    healthLog(JSON.stringify({
      event: 'health_request',
      version: config.releaseVersion,
      status: reply.statusCode,
      duration_ms: Math.round(reply.elapsedTime * 1000) / 1000,
    }));
  });

  await app.register(websocket, { options: { maxPayload: 16 * 1024 } });

  app.addHook('onRequest', async (request, reply) => {
    const origin = request.headers.origin;
    if (origin && origin !== config.webOrigin) {
      return reply.code(403).send({ error: 'origin_not_allowed' });
    }
    if (origin) {
      reply.header('Access-Control-Allow-Origin', config.webOrigin);
      reply.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
      reply.header('Access-Control-Allow-Headers', 'authorization, content-type');
      reply.header('Vary', 'Origin');
    }
    if (request.method === 'OPTIONS') return reply.code(204).send();
  });

  const authenticate = async (request: FastifyRequest, reply: { code(status: number): { send(body: unknown): unknown } }): Promise<Principal | undefined> => {
    try {
      const principal = await verifyAccessToken(bearerToken(request.headers.authorization));
      principals.set(request, principal);
      return principal;
    } catch (error) {
      if (!(error instanceof UnauthorizedError)) request.log.warn({ err: error }, 'Access token rejected');
      await reply.code(401).send({ error: 'unauthorized' });
      return undefined;
    }
  };

  app.get('/health', async () => ({ status: 'ok' }));
  // The release gate alternates probes between /ready and /, expecting the same payload.
  const ready = async () => ({ version: config.releaseVersion, ready: true });
  app.get('/ready', ready);
  app.get('/', ready);

  app.get('/api/me', async (request, reply) => {
    const principal = await authenticate(request, reply);
    if (!principal) return;
    const memberships = await repository.membershipsFor(principal);
    return {
      memberships: memberships.map(({ organizationId, role }) => ({ organizationId, role })),
    };
  });

  app.post<{ Body: { organizationId?: unknown } }>('/api/ws-ticket', async (request, reply) => {
    const principal = await authenticate(request, reply);
    if (!principal) return;
    const organizationId = request.body?.organizationId;
    if (typeof organizationId !== 'string' || !guid.test(organizationId)) {
      return reply.code(400).send({ error: 'invalid_organization_id' });
    }
    const membership = await repository.membershipFor(principal, organizationId);
    if (!membership) return reply.code(403).send({ error: 'forbidden' });

    const ticket = randomBytes(32).toString('base64url');
    const expiresAt = new Date(now().getTime() + ticketLifetimeMs);
    const created = await repository.createSocketTicket(ticketHash(ticket), principal, organizationId, expiresAt);
    if (!created) return reply.code(403).send({ error: 'forbidden' });
    return reply.code(201).send({ ticket, expiresAt: expiresAt.toISOString() });
  });

  app.get<{ Params: { organizationId: string } }>('/api/organizations/:organizationId/socket', {
    websocket: true,
    preValidation: async (request, reply) => {
      const organizationId = request.params.organizationId;
      const ticket = websocketTicket(request);
      if (!guid.test(organizationId) || !ticket) return reply.code(401).send({ error: 'unauthorized' });
      const identity = await repository.consumeSocketTicket(ticketHash(ticket), organizationId, now());
      if (!identity) return reply.code(403).send({ error: 'forbidden' });
      socketIdentities.set(request, identity);
    },
  }, (socket, request) => {
    const identity = socketIdentities.get(request);
    if (!identity) {
      socket.close(1008, 'unauthorized');
      return;
    }
    socket.send(JSON.stringify({ type: 'authenticated', organizationId: identity.organizationId }));
  });

  app.setErrorHandler((error, request, reply) => {
    request.log.error({ err: error }, 'API request failed');
    if (!reply.sent) reply.code(503).send({ error: 'service_unavailable' });
  });
  app.addHook('onClose', async () => repository.close?.());
  return app;
}
