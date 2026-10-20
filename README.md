# GeezerGeek Pilot Apps (Control Panel)

GeezerGeek Pilot app — launcher for all the GeezerGeek Pilot apps.
Live: https://geezer-geek-pilot-control-panel.netlify.app/

- `site/` — what Netlify publishes (icons/icon-192.png, icons/icon-512-maskable.png, icons/icon-512.png, index.html, manifest.json, qr-code.png, qr.html, sw.js)
- `netlify.toml` — publish dir; no build step
- `tools/ggp-footer/` — master copy of the shared footer used by every app (not published; see its README)

Every push to `main` redeploys the site.
