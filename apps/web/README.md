# PhoneBuddy web shell

Use Node 22 or newer. Run `npm ci`, `npm test`, and `npm run build` in this
directory, or `npm run dev` for local development. The static artifact is
`dist/`; it uses hash routes and does not require a server-side fallback.

The app reads a public `config.json` from the site root. For local development,
copy `config.example.json` to `public/config.json` and set `apiBaseUrl`,
`entraTenantId`, `entraClientId`, and the exposed API `apiScope`. The example
uses `http://localhost:3000`; it is only valid for local development. These
values identify public services and an Entra SPA registration; never put
credentials, client secrets, access tokens, or API keys in this file. Entra
redirect URIs must include the site origin. The SPA uses MSAL authorization
code with PKCE and keeps its cache in session storage.

The protected-main CI build reads the dev values from repository Actions
Variables named `PHONEBUDDY_DEV_API_BASE_URL`,
`PHONEBUDDY_DEV_ENTRA_TENANT_ID`, `PHONEBUDDY_DEV_ENTRA_CLIENT_ID`, and
`PHONEBUDDY_DEV_API_SCOPE`. Add them under **Settings → Secrets and variables →
Actions → Variables**. They are public configuration, not secrets. The generator
writes `dist/config.json` only when all four values pass validation and the API
URL is HTTPS. Otherwise it removes any stale config from the artifact, so the
published shell stays in its clear unconfigured state. Do not use the local
localhost URL for a hosted release.

The current dev preview is
[thankful-wave-01ad93d0f.3.azurestaticapps.net](https://thankful-wave-01ad93d0f.3.azurestaticapps.net).
Set the API base URL to the separately hosted API origin only after that HTTPS
endpoint exists. Future test and production builds must use their own
environment-specific variables and artifacts; do not reuse dev values.

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
