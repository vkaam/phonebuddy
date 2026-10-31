# PhoneBuddy web shell

Use Node 22 or newer. Run `npm ci`, `npm test`, and `npm run build` in this
directory. The static artifact is `dist/`; it uses hash routes and does not
require a server-side fallback. For local development, copy
`config.example.json` to `public/config.json` and run `npm run dev`. Remove the
local config when finished; it is ignored by Git.

At deployment, provide `config.json` alongside `index.html` with an
`apiBaseUrl` using HTTPS (HTTP is allowed only for localhost). This file is
public to every browser: never put credentials or secrets in it. The shell
validates configuration at startup and displays an actionable error if it is
missing or invalid. The example is not a production endpoint. The shell does
not yet connect to the API, authenticate users, or place calls; those features
belong to subsequent tasks. Do not publish this shell as a functional phone.
