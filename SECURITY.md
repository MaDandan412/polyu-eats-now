# Security and personal configuration

The application is a public, read-only directory of restaurant availability. It does not handle payment, store merchant login credentials or provide a private account area.

Funnel publicly shares the configured web app. Only sharing its URL with friends does not restrict visitors. Do not point Funnel at your home directory or expose private content through this application's static files or API. Private deployments need an authentication layer.

Do not commit `.env`, `.runtime`, account tokens, TLS private keys, logs, browser profiles or user-specific Tailscale state. The repository includes only `.env.example`. Favorites and language selection are local browser preferences, not server-side accounts.

If you find a vulnerability, do not post exploit details, secrets or private data in a public issue. Use GitHub's private vulnerability reporting feature if enabled; otherwise use a private contact route already supplied by the maintainer. This project currently has no dedicated published security email. Only test systems you own or have permission to assess; merchant ordering systems are outside this project's authorization.

Public HTTPS certificate logs contain hostnames; they do not grant file access. Refer to [Tailscale HTTPS documentation](https://tailscale.com/docs/how-to/set-up-https-certificates) and [Funnel documentation](https://tailscale.com/docs/features/tailscale-funnel).
