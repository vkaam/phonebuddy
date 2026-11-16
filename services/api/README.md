# PhoneBuddy API

The Fastify API validates Entra access tokens, resolves organization memberships
from Azure SQL, and issues one-use WebSocket tickets. It does not trust an
organization ID supplied by the browser without checking the authenticated
principal's active membership.

## Configuration

Set `ENTRA_TENANT_ID`, `ENTRA_API_CLIENT_ID`, `WEB_ORIGIN`, `SQL_SERVER`, and
`SQL_DATABASE`. These values identify public endpoints and resources; do not
put secrets or access tokens in them. For a user-assigned managed identity,
also set `SQL_MANAGED_IDENTITY_CLIENT_ID`. The API uses Entra default
credentials for Azure SQL and does not accept SQL passwords.

Run the versioned SQL in `migrations/` with the database migration owner before
starting the API. The app identity needs only the database permissions required
to read and update membership and WebSocket ticket rows. Memberships store the
Entra tenant and object IDs separately from the application organization ID.
Only an authorized provisioning process should create or deactivate membership
rows; this task does not add an admin membership-management interface.

The browser uses `@azure/msal-browser` with authorization code and PKCE. Its
public `config.json` contains the tenant ID, client ID, API scope, and API URL;
it must never contain a client secret. Configure the API CORS origin to the
exact deployed web origin.

## Local development

Use synthetic Entra identities and an in-memory membership repository in tests.
The API package commands are `npm install`, `npm test`, and `npm start`. No live
Azure SQL connection, Entra app registration, or deployed service is required
for the local test suite.
