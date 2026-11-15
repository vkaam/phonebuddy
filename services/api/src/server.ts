import { buildApi } from './app.js';
import { readApiConfig } from './config.js';
import { SqlAuthRepository } from './repository.js';
import { createEntraAccessTokenVerifier } from './token.js';

const config = readApiConfig();
const repository = new SqlAuthRepository({
  server: config.sqlServer,
  database: config.sqlDatabase,
  managedIdentityClientId: config.sqlManagedIdentityClientId,
});
const app = await buildApi({
  config,
  repository,
  verifyAccessToken: createEntraAccessTokenVerifier(config),
});

try {
  await app.listen({ host: config.host, port: config.port });
} catch (error) {
  app.log.error({ err: error }, 'API failed to start');
  await app.close();
  process.exitCode = 1;
}
