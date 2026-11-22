# Dev sign-in and API setup runbook

This runbook recreates PhoneBuddy dev sign-in from documented steps (issue 152).
It covers the Entra app registrations, the public Actions Variables, the first
pilot membership row and what a user without membership sees. It contains no
secret, token, client secret or real tenant or client ID. Put real values only
in the owner's records and in the public Actions Variables named below.

## Owner decisions

Decided on 2026-11-22 (recorded in TASK-121 and TASK-122):

1. **Who may sign in to dev.** Only the owner and invited guests of the
   nonproduction tenant. Grant a membership row only to those accounts.
2. **How the Entra app registrations are made.** The deployment will create
   them (TASK-121, not built yet). Until that task lands, create them by hand
   with sections 1 and 2; the values they produce are the same ones the
   deployment will publish.

Still open:

3. **Who runs the membership SQL** and with which database identity. The API's
   own identity should only read membership rows, and insert, update and
   delete WebSocket ticket rows. It must not be used to insert memberships.
   The Container App currently runs as the user-assigned identity
   `id-pb-dev-pull`, which has no Azure SQL access yet (TASK-120).
4. **How guests are invited and provisioned** (TASK-122): the invitation steps
   and the provisioning path for their membership rows are not written yet.

## Environments and separation

- `dev`, `test` and `prod` each get their own Entra app registrations, API
  origin, Azure SQL database, membership rows, managed identities and public
  configuration. Do not reuse a registration, client ID, scope or membership
  row across environments, and never put production data or credentials in dev
  or test. See `docs/azure-delivery-policy.md` for the environment register.
- This runbook configures dev only. Only `PHONEBUDDY_DEV_*` Variables are used
  and the release workflow deploys only dev. Test and production
  need their own registrations and their own, differently named Variables.
- Entra registrations for dev and test live in the nonproduction tenant. The
  production tenant is unresolved; do not register production there.
- No secret, access token, refresh token or client secret is committed,
  logged, put in an Actions Variable or placed in `config.json`. The SPA is a
  public client (authorization code with PKCE) and needs no secret. The API
  validates tokens against the tenant's public keys and reaches Azure SQL with
  a managed identity, not a password.

## Prerequisites

- The nonproduction tenant ID (a GUID).
- The dev API's HTTPS origin, for example the dev Container App hostname once
  it exists. The hosted API URL must be HTTPS; `http://localhost:3000` is for
  local development only.
- The dev Static Web App origin, currently
  `https://thankful-wave-01ad93d0f.3.azurestaticapps.net`.
- Permission in the tenant to create app registrations and grant consent. This
  is the owner's step (decision 2).

## 1. Register the API

In the Entra admin center for the nonproduction tenant, under App registrations:

1. Create a registration named for dev, for example `PhoneBuddy API (dev)`,
   single tenant. No redirect URI and no client secret.
2. Expose an API. Set the Application ID URI to `api://<API client ID>` (the
   config validator requires the scope in the form `api://<guid>/<name>`). Add
   one delegated scope, for example `access`, that users can consent to. The
   resulting scope is `api://<API client ID>/access`; this is the
   `PHONEBUDDY_DEV_API_SCOPE` value.
3. In the manifest, set `requestedAccessTokenVersion` to `2`. The API accepts
   only v2 tokens: the issuer must be
   `https://login.microsoftonline.com/<tenant ID>/v2.0` and the audience must
   equal the API client ID GUID exactly. A v1 token fails validation.
4. Record the API client ID. It becomes the API's `ENTRA_API_CLIENT_ID`.

The API also requires `tid` and `oid` claims, and `tid` must equal its
`ENTRA_TENANT_ID`, so only tokens from that one tenant are accepted.

## 2. Register the SPA

1. Create a second registration, for example `PhoneBuddy web (dev)`, single
   tenant.
2. Add a platform of type **Single-page application** with the redirect URI
   set to the exact dev Static Web App origin, with no path and no trailing
   slash (the app uses `window.location.origin` for sign-in and sign-out). Add
   a local development origin only if the owner wants local sign-in against
   dev; keep it out of any hosted test or production registration.
3. Under API permissions, add the delegated `access` scope of the API
   registration and grant consent for the tenant, or let users consent on
   first sign-in if tenant policy allows it. Add no other permissions.
4. Do not create a client secret or certificate.
5. Record the SPA client ID. It is `PHONEBUDDY_DEV_ENTRA_CLIENT_ID`.

If the Static Web App hostname changes, the redirect URI must change with it.

## 3. Set the public Actions Variables

In the GitHub repository under **Settings, Secrets and variables, Actions,
Variables** (not Secrets), create these four **repository** variables. The
web build reads them and its job has no environment, so they cannot live only
on the `dev` environment. They are public configuration:

| Variable | Value |
| --- | --- |
| `PHONEBUDDY_DEV_API_BASE_URL` | The dev API HTTPS origin |
| `PHONEBUDDY_DEV_ENTRA_TENANT_ID` | The nonproduction tenant ID |
| `PHONEBUDDY_DEV_ENTRA_CLIENT_ID` | The SPA client ID |
| `PHONEBUDDY_DEV_API_SCOPE` | `api://<API client ID>/access` (the scope you exposed) |

On the next trusted main release, `apps/web/scripts/generate-public-config.mjs`
validates all four and writes `config.json` into the artifact. If any value is
missing or invalid it removes any stale config and the site stays on its
unconfigured shell. Set the four only after the API HTTPS endpoint and both
registrations exist. The API address only exists after the first successful
dev release, so set `PHONEBUDDY_DEV_API_BASE_URL` last, then release again.
The config is built into the main build, so the next release needs a new main
commit: rerunning CI for the same commit rebuilds a different image, and the
release refuses it.

## 4. Configure the API

The release deploys the API settings from Actions Variables; you do not set
them on the Container App by hand. Create these five variables, at repository
level or on the `dev` environment (the deploy job runs in `dev`, so either
works). They are plain public values:

| Variable | Container App setting | Value |
| --- | --- | --- |
| `PHONEBUDDY_DEV_ENTRA_TENANT_ID` | `ENTRA_TENANT_ID` | The tenant ID (shared with section 3) |
| `PHONEBUDDY_DEV_ENTRA_API_CLIENT_ID` | `ENTRA_API_CLIENT_ID` | The API client ID |
| `PHONEBUDDY_DEV_SQL_SERVER` | `SQL_SERVER` | The full `<name>.database.windows.net` hostname |
| `PHONEBUDDY_DEV_SQL_DATABASE` | `SQL_DATABASE` | The dev database name |
| `PHONEBUDDY_DEV_SQL_MANAGED_IDENTITY_CLIENT_ID` | `SQL_MANAGED_IDENTITY_CLIENT_ID` | The Client ID (not Object ID) of the identity the app runs as |

`WEB_ORIGIN` is not a variable: the template sets it to the dev Static Web App
origin, which becomes the CORS origin. Before any deploy, the release checks
these values and stops with a message naming each missing, placeholder or
malformed one. GUIDs must be valid (version 1 to 8, RFC 4122 variant), the
same rule the API applies at startup. Apply
`services/api/migrations/001_identity.sql` to the dev database as the database
migration owner, and grant the app's identity only the access it needs (see
open decision 3), before expecting sign-in to work.

## 5. Grant a pilot user access

Sign-in alone does not grant access. The API authorizes only a principal
(tenant ID plus object ID from the token) that has an active row in
`dbo.OrganizationMembership`. There is no admin interface, so the database
owner inserts the row. Use the user's object ID from the Entra admin center
(Users, Object ID), the tenant ID, and an organization ID you choose (a new
GUID per pilot organization; keep these in the owner's records):

```sql
INSERT INTO dbo.OrganizationMembership (OrganizationId, TenantId, ObjectId, Role)
VALUES ('<organization GUID>', '<tenant GUID>', '<user object ID GUID>', N'user');
```

`Role` is `user` or `admin`. `IsActive` defaults to 1 and `CreatedAt` is set
automatically. The primary key is organization, tenant and object ID, so the
same user can be a member of several organizations. To revoke, set
`IsActive = 0` rather than deleting, because WebSocket ticket rows reference
the membership. Run this with the owner's own database identity, never by
embedding SQL credentials anywhere, and only for accounts named under open
decision 1.

## 6. What a user without membership sees

A user whose Entra sign-in succeeds but who has no active membership row gets
an empty membership list from `/api/me`. The web app then shows "No workspace
access yet" with the message that the account is signed in but is not an
active member of a PhoneBuddy organization, and a Sign out button. It does not
open the workspace. The API also rejects WebSocket ticket requests for an
organization without a matching active membership, regardless of any
organization ID the browser sends. A user who cannot sign in at all (not in the
tenant, no consent) is stopped by Entra before reaching the app. The fix for a
no-access user is a membership row, not a code or config change.

## 7. Verify

1. Open the dev site. With no config it shows the setup state; with the
   Variables set and a release done it shows the sign-in page.
2. Sign in as a pilot user with a membership row: the workspace opens and the
   role shows in the account area.
3. Sign in as an account without a row: the "No workspace access yet" screen
   shows.
4. Confirm `config.json` in the deployed site holds only the four public
   values and no secret.

Live results from these checks are post-merge evidence recorded separately
from the documentation change.
