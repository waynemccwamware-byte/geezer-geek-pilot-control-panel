#!/usr/bin/env python3
"""GeezerGeek Pilot shared footer — master copy (App Conventions §5, §6a, §6b).

Every GeezerGeek Pilot app carries three marker-delimited blocks written by this script:

  <!-- GGP-FOOTER-CSS START ... -->  ...  <!-- GGP-FOOTER-CSS END -->   just before </head>
  <!-- GGP-FOOTER START ... -->      ...  <!-- GGP-FOOTER END -->       where the footer sits
  <!-- GGP-FOOTER-JS START ... -->   ...  <!-- GGP-FOOTER-JS END -->    just before </body>

Edit the templates below (never the copies inside the apps), bump VERSION, then run:

  python3 ggp_footer.py /path/to/folder-holding-all-app-repos           # rewrite the blocks
  python3 ggp_footer.py /path/to/folder-holding-all-app-repos --check   # report drift only

Each app repo must be cloned side by side under that folder, named as on GitHub.
The script only replaces text between existing markers; adding the markers to a new app is a
one-time manual step (see README.md).
"""
import re
import sys
from pathlib import Path

VERSION = 'v1 · 20-Oct-2026'

CONTROL_PANEL_URL = 'https://geezer-geek-pilot-control-panel.netlify.app/'
REFERENCE_URL = 'https://docs.google.com/document/d/1chfDa3JBCjsGykGjwrAFwOqMAS7d3_dIY9ieROLCIyU/preview'
YOUTUBE_URL = 'https://youtube.com/@GeezerGeekPilot'

SHARE_LABEL = 'Share GeezerGeek Pilot Apps with pilot friends'
SHARE_TITLE = 'GeezerGeek Pilot Apps'
SHARE_TEXT = 'Planning, weather, ATC-practice and safety tools for GA pilots, from GeezerGeek Pilot.'

SHARE_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/>'
              '<circle cx="18" cy="19" r="3"/><line x1="8.6" y1="10.5" x2="15.4" y2="6.5"/>'
              '<line x1="8.6" y1="13.5" x2="15.4" y2="17.5"/></svg>')
INSTALL_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                'stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13"/><polyline points="7 8 12 3 17 8"/>'
                '<path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>')

# Per-app settings. back: show the back link. count: show the open counter (Control Panel only;
# the apps keep counting silently in their own scripts). extras: app-specific links shown under the
# back link. install: (button id, label) for an app that has its own install code.
APPS = {
    'geezer-geek-pilot-control-panel': dict(file='site/index.html', back=False, count=True,
                                            install=('installBtn', 'Add this app to Home Screen')),
    'weather-history-probability': dict(file='site/index.html'),
    'digital-autopilots-quiz': dict(file='site/index.html'),
    'tec-route-lookup': dict(file='public/index.html',
                             install=('installBtnFooter', 'Add this app to Home Screen/Desktop')),
    'atc-chair-fly-trainer': dict(file='site/index.html', extras=[
        ('Write-up on Simple Chair-Flying Exercise for Listen, Set, Read Back',
         'https://docs.google.com/document/d/1DKgs6nKMK6VDG0y59rxrQ6QCxwCi_waNuai61etXfFM/preview')]),
    'days-flight-schedule': dict(file='site/index.html', install=('installBtn', 'Install this app')),
    'fuel-to-add': dict(file='site/index.html'),
    'clearance-delivery': dict(file='site/index.html'),
    'piston-ga-stats': dict(file='site/index.html'),
}

CSS = f'''<!-- GGP-FOOTER-CSS START {VERSION} · shared footer styles, App Conventions §5b · master: Control Panel repo tools/ggp-footer -->
<style>
.ggp-footer{{
  --ggp-amber:#f5a623; --ggp-muted:#8b93a1; --ggp-bezel:#2a323f; --ggp-bezel-hi:#3a4454;
  box-sizing:border-box; width:100%; max-width:640px; margin:28px auto 0; padding:16px 0 8px;
  border-top:1px solid var(--ggp-bezel); text-align:center;
  font-family:'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif;
  font-size:11px; line-height:1.5; color:var(--ggp-muted);
}}
.ggp-footer *, .ggp-footer *::before, .ggp-footer *::after{{ box-sizing:border-box; }}
.ggp-footer .ggp-back{{ margin:0 0 12px; }}
.ggp-footer .ggp-back a{{
  display:inline-block; padding:6px 14px; border:1px solid var(--ggp-bezel-hi); border-radius:5px;
  background:var(--ggp-bezel); color:var(--ggp-amber); font-size:12px; font-weight:500; text-decoration:none;
}}
.ggp-footer .ggp-back a:hover{{ background:var(--ggp-bezel-hi); color:var(--ggp-amber); text-decoration:none; }}
.ggp-footer .ggp-extra{{ margin:0 0 6px; text-wrap:balance; }}
.ggp-footer .ggp-credit{{ margin:0; }}
.ggp-footer .ggp-extra a, .ggp-footer .ggp-credit a{{
  color:var(--ggp-muted); text-decoration:none; border-bottom:1px solid var(--ggp-bezel-hi); padding-bottom:1px;
}}
.ggp-footer .ggp-extra a:hover, .ggp-footer .ggp-credit a:hover{{ color:var(--ggp-amber); border-bottom-color:var(--ggp-amber); }}
.ggp-footer .ggp-count{{ margin-top:6px; }}
.ggp-footer .ggp-count:empty{{ display:none; }}
.ggp-footer .ggp-actions{{ display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin-top:12px; }}
.ggp-footer .ggp-pill{{
  display:inline-flex; align-items:center; gap:7px; margin:0; padding:8px 16px;
  border:1px solid var(--ggp-bezel-hi); border-radius:20px; background:transparent; color:var(--ggp-muted);
  font:inherit; font-size:12.5px; line-height:1.2; cursor:pointer; transition:color .15s ease, border-color .15s ease;
}}
.ggp-footer .ggp-pill:hover{{ color:var(--ggp-amber); border-color:var(--ggp-amber); background:transparent; }}
.ggp-footer .ggp-pill svg{{ width:15px; height:15px; flex-shrink:0; }}
.ggp-footer .ggp-pill span{{ text-wrap:balance; }}
@media (max-width:400px){{ .ggp-footer .ggp-pill{{ font-size:12px; padding:8px 12px; gap:6px; }} }}
.ggp-footer a:focus-visible, .ggp-footer .ggp-pill:focus-visible{{ outline:2px solid var(--ggp-amber); outline-offset:2px; }}
@media print{{
  .ggp-footer .ggp-back, .ggp-footer .ggp-extra, .ggp-footer .ggp-count, .ggp-footer .ggp-actions{{ display:none !important; }}
  .ggp-footer{{ border-top:0; margin-top:8px; padding-top:0; }}
}}
</style>
<!-- GGP-FOOTER-CSS END -->'''

JS = f'''<!-- GGP-FOOTER-JS START {VERSION} · shared footer script, App Conventions §6a/§6b · master: Control Panel repo tools/ggp-footer -->
<script>
(() => {{
  if (window.__ggpFooter) return;
  window.__ggpFooter = true;
  // Every app's footer share button shares the Control Panel, not the app itself.
  const SHARE_URL   = '{CONTROL_PANEL_URL}';
  const SHARE_TITLE = '{SHARE_TITLE}';
  const SHARE_TEXT  = '{SHARE_TEXT}';
  const flash = (btn) => {{
    if (btn.dataset.ggpBusy) return;
    btn.dataset.ggpBusy = '1';
    const label = btn.querySelector('span') || btn;
    const original = label.textContent;
    label.textContent = label === btn ? 'Link copied!' : 'Link copied to clipboard!';
    setTimeout(() => {{ label.textContent = original; delete btn.dataset.ggpBusy; }}, 2200);
  }};
  // One listener on the document, so it also covers footers an app draws later and any other
  // button given the ggp-share class.
  document.addEventListener('click', async (ev) => {{
    const btn = ev.target instanceof Element ? ev.target.closest('.ggp-share') : null;
    if (!btn) return;
    ev.preventDefault();
    if (navigator.share) {{
      try {{ await navigator.share({{ title: SHARE_TITLE, text: SHARE_TEXT, url: SHARE_URL }}); return; }}
      catch (err) {{ if (err && err.name === 'AbortError') return; /* else fall through */ }}
    }}
    try {{
      await navigator.clipboard.writeText(SHARE_URL);
      flash(btn);
    }} catch (err) {{
      window.location.href = 'mailto:?subject=' + encodeURIComponent(SHARE_TITLE)
        + '&body=' + encodeURIComponent(SHARE_TEXT + ' ' + SHARE_URL);
    }}
  }});
  // Open counter: shown only where the footer has #ggpCount (the Control Panel). Apps count silently.
  const countEl = document.getElementById('ggpCount');
  if (countEl) {{
    fetch('https://tally.yuki.sh/hits/wamware/geezer-geek-pilot-control-panel.json')
      .then(r => r.json())
      .then(d => {{
        const n = d && d.visit;
        if (typeof n === 'number') countEl.textContent = 'Opened ' + n.toLocaleString() + (n === 1 ? ' time' : ' times');
      }})
      .catch(() => {{ /* counter is a nice-to-have, never block the app */ }});
  }}
}})();
</script>
<!-- GGP-FOOTER-JS END -->'''


def footer_html(cfg):
    lines = [f'<!-- GGP-FOOTER START {VERSION} · shared footer, App Conventions §5a · master: Control Panel repo tools/ggp-footer -->',
             '<footer class="ggp-footer">']
    if cfg.get('back', True):
        lines.append(f'  <div class="ggp-back"><a href="{CONTROL_PANEL_URL}">&larr; Back to GeezerGeek Pilot Apps</a></div>')
    for text, url in cfg.get('extras', []):
        lines.append(f'  <div class="ggp-extra"><a href="{url}" target="_blank" rel="noopener">{text}</a></div>')
    lines.append(f'  <div class="ggp-credit">Wayne McClelland, <a href="{YOUTUBE_URL}" target="_blank" rel="noopener">GeezerGeek Pilot</a>, '
                 f'<a href="{REFERENCE_URL}" target="_blank" rel="noopener">Reference Materials</a></div>')
    if cfg.get('count'):
        lines.append('  <div class="ggp-count" id="ggpCount"></div>')
    lines.append('  <div class="ggp-actions">')
    lines.append(f'    <button class="ggp-pill ggp-share" type="button">{SHARE_ICON}<span>{SHARE_LABEL}</span></button>')
    if cfg.get('install'):
        bid, label = cfg['install']
        lines.append(f'    <button class="ggp-pill" id="{bid}" type="button" style="display:none;">{INSTALL_ICON}<span>{label}</span></button>')
    lines.append('  </div>')
    lines.append('</footer>')
    lines.append('<!-- GGP-FOOTER END -->')
    return '\n'.join(lines)


BLOCKS = [
    ('css', re.compile(r'<!-- GGP-FOOTER-CSS START.*?<!-- GGP-FOOTER-CSS END -->', re.S)),
    ('html', re.compile(r'<!-- GGP-FOOTER START.*?<!-- GGP-FOOTER END -->', re.S)),
    ('js', re.compile(r'<!-- GGP-FOOTER-JS START.*?<!-- GGP-FOOTER-JS END -->', re.S)),
]


def render(cfg):
    return {'css': CSS, 'html': footer_html(cfg), 'js': JS}


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    root = Path(argv[1])
    check = '--check' in argv
    status = 0
    for app, cfg in APPS.items():
        path = root / app / cfg['file']
        if not path.exists():
            print(f'{app}: MISSING {path}')
            status = 1
            continue
        src = path.read_text(encoding='utf-8')
        want = render(cfg)
        out = src
        problems = []
        for key, rx in BLOCKS:
            found = rx.findall(out)
            if len(found) != 1:
                problems.append(f'{key} block found {len(found)}x')
                continue
            out = rx.sub(lambda m: want[key], out, count=1)
        if problems:
            print(f'{app}: {"; ".join(problems)}')
            status = 1
            continue
        if out == src:
            print(f'{app}: up to date')
        elif check:
            print(f'{app}: DRIFT (run without --check to rewrite)')
            status = 1
        else:
            path.write_text(out, encoding='utf-8')
            print(f'{app}: updated')
    return status


if __name__ == '__main__':
    sys.exit(main(sys.argv))
