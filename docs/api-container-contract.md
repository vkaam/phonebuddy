# API container contract

The PhoneBuddy API (`services/api`) ships as a container image that the release
gate treats like the release-test stand-in (`infra/release-test`).

## Image

- Built from `services/api/Dockerfile` with `services/api` as the build context.
- Multi-stage build on a digest-pinned `node:22-alpine` base; the final image
  holds production dependencies and the compiled API only.
- Runs as the non-root user `65532:65532`. It needs no writable paths.
- Starts with `node dist/src/server.js`.

## Port

The API listens on `0.0.0.0:8080` (`PORT` defaults to 8080).

## Endpoints

- `GET /ready` and `GET /` need no authentication (the release gate alternates
  its probes between them) and return
  `{"version": "<RELEASE_VERSION>", "ready": true}` with status 200.
  `RELEASE_VERSION` is `unknown` when unset.
- `GET /health` needs no authentication and returns `{"status":"ok"}`.
- Every `/api/*` route requires an Entra access token issued for the API
  (signature, issuer, audience and expiry are checked), except the WebSocket
  route, which requires a one-use ticket. Browser requests with an `Origin`
  other than `WEB_ORIGIN` are rejected with 403.

## Log line

Each `/`, `/ready` or `/health` request writes exactly one JSON line to stdout and
nothing else about that request:

```json
{"event":"health_request","version":"<RELEASE_VERSION>","status":200,"duration_ms":0.4}
```

The line carries no request data (no path, query, headers, client address or
body).

## Environment variables

Settings come only from environment variables. None is a secret.

| Variable | Required | Meaning |
| --- | --- | --- |
| `ENTRA_TENANT_ID` | yes | Entra tenant GUID that issues accepted tokens |
| `ENTRA_API_CLIENT_ID` | yes | API application GUID; the required token audience |
| `WEB_ORIGIN` | yes | The one HTTPS origin allowed to call the API from a browser |
| `SQL_SERVER` | yes | Azure SQL server hostname (`*.database.windows.net`) |
| `SQL_DATABASE` | yes | Azure SQL database name |
| `SQL_MANAGED_IDENTITY_CLIENT_ID` | no | User-assigned managed identity GUID for SQL access |
| `RELEASE_VERSION` | no | Version reported by `/ready` and the log line |
| `PORT` | no | Listen port, default 8080 |

The API fails to start when a required setting is missing or invalid. Azure SQL
is reached with the managed identity; the API accepts no SQL password.
