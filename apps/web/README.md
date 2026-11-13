# PhoneBuddy web shell

Use Node 22 or newer. Run `npm ci`, `npm test`, and `npm run build` in this
directory, or `npm run dev` for local development. The static artifact is
`dist/`; it uses hash routes and does not require a server-side fallback.

The first preview starts without an API endpoint or `config.json`. Calling,
backend integration and authentication are not available; call controls remain
disabled. The existing configuration validator and example are retained for
future integration, but the preview does not load them. Any future browser
configuration is public: never put credentials or secrets in it.

The protected-main release workflow builds the web artifact and deploys it to
the dev Azure Static Web App's default HTTPS hostname after main Quality passes.
Later trusted main releases update the same preview. See
[Azure delivery policy](../../docs/azure-delivery-policy.md) for release and
recovery details. This preview is not deployed to test or production.
