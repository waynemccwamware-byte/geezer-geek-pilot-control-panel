# GGP shared footer (master)

`ggp_footer.py` holds the one and only copy of the footer used by every GeezerGeek Pilot app
(App Conventions §5, §6a, §6b). It is not published: Netlify serves only `site/`.

Each app's `index.html` carries three marker-delimited blocks that this script rewrites:

| Block | Where | Contents |
|---|---|---|
| `GGP-FOOTER-CSS` | just before `</head>` | footer styles (own color values, so the Quiz and the Control Panel match) |
| `GGP-FOOTER` | where the footer sits | back link, optional app links, credit line, share pill, optional install pill |
| `GGP-FOOTER-JS` | just before `</body>` | share script (always shares the Control Panel) and the Control Panel's open counter |

What the blocks do:
- The share pill ("Share GeezerGeek Pilot Apps with pilot friends") shares
  https://geezer-geek-pilot-control-panel.netlify.app/ from every app. Any other button given the
  class `ggp-share` does the same (the Quiz's top-bar and debrief buttons). Shares of data, such as
  Weather's "Share Analysis Results" or Piston's "Share comparison", are app code and are not touched.
- Only the Control Panel shows "Opened N times" (Tally, `wamware/geezer-geek-pilot-control-panel`).
  The apps keep their own counter code and count silently. Since v1.4 the count is a subtle link
  (`count_href`) to `site/stats/`, a public page that reads every app's counter without bumping it.
- v1.6: a feedback pill ("Feedback to GeezerGeek Pilot" from v1.7) opens the user's email app with a message to Wayne, subject
  "GeezerGeek feedback: <label>" and an empty body (v1.8). If no email app opens, it shows the address with a Copy button.
  The address is assembled in the script, not written in the page. The Control Panel has its own
  button under the purpose line (class `ggp-feedback`, same handler) instead (`feedback=False`).
- The Control Panel maps the footer's colors to its light/dark tokens with one rule in its own CSS
  (`body .ggp-footer { --ggp-amber: var(--amber); … }`).

## Changing the footer

1. Clone all nine app repos side by side in one folder.
2. Edit the templates or `APPS` in `ggp_footer.py` and bump `VERSION`.
3. `python3 ggp_footer.py <folder>` rewrites the blocks; `--check` only reports drift.
4. Commit and push each repo; every push redeploys that site.
5. Update §5/§6 and the change log in the App Conventions doc.

## Adding a new app

Add it to `APPS`, then put empty markers in its `index.html` and run the script:

```html
<!-- GGP-FOOTER-CSS START --><!-- GGP-FOOTER-CSS END -->   (before </head>)
<!-- GGP-FOOTER START --><!-- GGP-FOOTER END -->           (where the footer goes)
<!-- GGP-FOOTER-JS START --><!-- GGP-FOOTER-JS END -->     (before </body>)
```
