# PhoneBuddy web shell

Use Node 22 or newer. Run `npm ci`, `npm test`, and `npm run build` in this
directory, or `npm run dev` for local development. The static artifact is
`dist/`; it uses hash routes and does not require a server-side fallback.

The app reads a public `config.json` from the site root. Copy
`config.example.json` to `config.json` and set `apiBaseUrl`, `entraTenantId`,
`entraClientId`, and the exposed API `apiScope`. These values identify public
services and an Entra SPA registration; never put credentials, client secrets,
access tokens, or API keys in this file. Entra redirect URIs must include the
site origin. The SPA uses MSAL authorization code with PKCE and keeps its cache
in session storage.

After sign-in the browser sends an API access token to `/api/me` over HTTPS.
The workspace opens only after the API confirms an active organization
membership. The membership role is displayed in the account area; a user with
no active membership sees an access message and can sign out. Local builds
without `config.json` display a clear setup state and keep calling controls
disabled.

Configure the API with `ENTRA_TENANT_ID`, `ENTRA_API_CLIENT_ID`, `WEB_ORIGIN`,
`SQL_SERVER`, and `SQL_DATABASE`. The API uses Azure SQL's default credential
chain (managed identity in Azure); apply `services/api/migrations/001_identity.sql`
using an authorized database deployment process and provision membership rows
through the approved admin workflow. The API and SPA configuration must use the
same tenant, API audience/scope, and allowed web origin. No app registration,
consent, cloud deployment, or production data is part of this task.

The protected-main release workflow builds the web artifact and deploys it to
the dev Azure Static Web App's default HTTPS hostname after main Quality passes.
Later trusted main releases update the same preview. See
[Azure delivery policy](../../docs/azure-delivery-policy.md) for release and
recovery details. This preview is not deployed to test or production.
