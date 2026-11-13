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

VERSION = 'v1.14 · 13-Nov-2026'

CONTROL_PANEL_URL = 'https://geezer-geek-pilot-control-panel.netlify.app/'
# v1.14: the Control Panel's /reference function serves the Reference Materials Doc as an inline PDF
# (print layout, light pages, stays out of the Google Docs app on iPhone) — Wayne, 13-Nov-2026
REFERENCE_URL = CONTROL_PANEL_URL + 'reference'
YOUTUBE_URL = 'https://youtube.com/@GeezerGeekPilot'
AIRPORTS_URL = CONTROL_PANEL_URL + 'airports/'   # Wayne's airports-visited map (v1.2)
# v1.6: feedback opens the user's email app (mailto) addressed to Wayne; the address is assembled in the
# script, not written in the page, to keep it away from address scrapers. (v1.5's Netlify form retired.)
FEEDBACK_USER, FEEDBACK_DOMAIN = 'waynemcc', 'wamware.com'
# v1.9: YouTube playlist of app intro videos (Wayne, 08-Nov-2026; playlist "GeezerGeek Pilot Apps", 4 videos when checked)
VIDEOS_URL = 'https://www.youtube.com/playlist?list=PLZEU99ONr5bE'
VIDEOS_LABEL = 'YouTube intros to the apps'
FEEDBACK_LABEL = 'Feedback to GeezerGeek Pilot'   # v1.7: matches the Control Panel button

SHARE_LABEL = 'Share GeezerGeek Pilot Apps with pilot friends'
SHARE_TITLE = 'GeezerGeek Pilot Apps'
SHARE_TEXT = 'Planning, weather, ATC-practice and safety tools for GA pilots, from GeezerGeek Pilot.'

SHARE_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/>'
              '<circle cx="18" cy="19" r="3"/><line x1="8.6" y1="10.5" x2="15.4" y2="6.5"/>'
              '<line x1="8.6" y1="13.5" x2="15.4" y2="17.5"/></svg>')
FEEDBACK_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                 'stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>')
VIDEOS_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
               'stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="5" width="20" height="14" rx="4"/>'
               '<polygon points="10 9 15 12 10 15" fill="currentColor"/></svg>')
INSTALL_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
                'stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v13"/><polyline points="7 8 12 3 17 8"/>'
                '<path d="M5 12v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7"/></svg>')

# Per-app settings. back: show the back link. count: show the open counter (Control Panel only;
# the apps keep counting silently in their own scripts). extras: app-specific links shown under the
# back link. install: (button id, label) for an app that has its own install code.
# repo: the repo folder, when the key is not the repo name (a second page in one repo).
# feedback: show the Send feedback pill (default True); it opens an email to Wayne naming the app (label).
# videos: show the YouTube intros pill (default True; off on the Control Panel, which has its own button).
# label: the app's name as it should appear in the feedback email's subject.
# all_count: also hit the shared Tally counter wamware/ggp-all (default True), whose `visitor` is unique visitors
#   across every app (v1.12, Wayne 10-Nov-2026). Off for pages that are not apps (the stats page, the airports map).
APPS = {
    # count_base: estimated opens before the Tally counter started (20-Oct-2026); added to the shown number.
    'geezer-geek-pilot-control-panel': dict(file='site/index.html', back=False, count=True, count_base=300, count_href='stats/',
                                            feedback=False, videos=False, label='GeezerGeek Pilot Apps',   # has its own feedback button under the purpose line
                                            install=('installBtn', 'Add this app to Home Screen')),
    'weather-history-probability': dict(file='site/index.html', label='Weather History and Probability'),
    'digital-autopilots-quiz': dict(file='site/index.html', label='Know the Score(board)? – a Quiz'),
    'tec-route-lookup': dict(file='public/index.html', label='TEC Route Lookup',
                             install=('installBtnFooter', 'Add this app to Home Screen/Desktop')),
    'atc-chair-fly-trainer': dict(file='site/index.html', label='ATC Chair-Fly Trainer', extras=[
        ('Write-up on Simple Chair-Flying Exercise for Listen, Set, Read Back',
         'https://docs.google.com/document/d/1DKgs6nKMK6VDG0y59rxrQ6QCxwCi_waNuai61etXfFM/preview')]),
    'days-flight-schedule': dict(file='site/index.html', label="Day's Flight Schedule", install=('installBtn', 'Install this app')),
    'fuel-to-add': dict(file='site/index.html', label='How Much Fuel to Add?'),
    'clearance-delivery': dict(file='site/index.html', label='Clearance Delivery Trainer'),
    'piston-ga-stats': dict(file='site/index.html', label='GA Accident Stats'),
    'claude-foreflight-primer': dict(file='site/index.html', label='Claude + ForeFlight Primer'),
    'airports-visited': dict(repo='geezer-geek-pilot-control-panel', file='site/airports/index.html', label='Airports Visited',
                             credit_link=False, all_count=False),   # the page the credit links to
    # v1.4: open-counts page, linked from the Control Panel's "Opened N times" (Wayne, 02-Nov-2026)
    'open-counts': dict(repo='geezer-geek-pilot-control-panel', file='site/stats/index.html', label='App Open Counts', all_count=False),
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
.ggp-footer .ggp-count a{{ color:inherit; text-decoration:none; border-bottom:1px dotted var(--ggp-bezel-hi); padding-bottom:1px; }}
.ggp-footer .ggp-count a:hover{{ color:var(--ggp-amber); border-bottom-color:var(--ggp-amber); }}
.ggp-footer .ggp-actions{{ display:flex; flex-wrap:wrap; justify-content:center; gap:8px; margin-top:12px; }}
.ggp-footer .ggp-pill{{
  display:inline-flex; align-items:center; gap:7px; margin:0; padding:8px 16px;
  border:1px solid var(--ggp-bezel-hi); border-radius:20px; background:transparent; color:var(--ggp-muted);
  font:inherit; font-size:12.5px; line-height:1.2; cursor:pointer; transition:color .15s ease, border-color .15s ease;
}}
.ggp-footer a.ggp-pill{{ text-decoration:none; }}
/* v1.6: shown under a feedback button when no email app opened */
.ggp-fb-note{{ flex-basis:100%; margin:10px auto 0; max-width:460px; padding:10px 12px; border:1px solid #3a4454; border-radius:6px;
  font:12px/1.5 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; color:#8b93a1; text-align:center; }}
.ggp-fb-note b{{ color:#e7e4dc; font-weight:500; user-select:all; }}
.ggp-fb-note button{{ margin-left:8px; padding:3px 10px; border:1px solid #3a4454; border-radius:12px; background:transparent;
  color:#f5a623; font:inherit; cursor:pointer; }}
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
  // v1.6 feedback: any element with class ggp-feedback opens an email to Wayne naming its data-app.
  // If no email app takes over within ~1.5 s (page still focused), show the address with a Copy button.
  document.addEventListener('click', (ev) => {{
    const btn = ev.target instanceof Element ? ev.target.closest('.ggp-feedback') : null;
    if (!btn) return;
    ev.preventDefault();
    const addr = ['{FEEDBACK_USER}', '{FEEDBACK_DOMAIN}'].join('@');
    const app = btn.dataset.app || document.title;
    const subject = 'GeezerGeek feedback: ' + app;
    // v1.8: subject only, empty body (no page link or device string), per Wayne
    let left = false;
    const onLeave = () => {{ left = true; }};
    window.addEventListener('blur', onLeave, {{ once: true }});
    document.addEventListener('visibilitychange', onLeave, {{ once: true }});
    window.location.href = 'mailto:' + addr + '?subject=' + encodeURIComponent(subject);
    setTimeout(() => {{
      window.removeEventListener('blur', onLeave);
      document.removeEventListener('visibilitychange', onLeave);
      if (left || !document.hasFocus()) return;           // an email app opened
      const host = btn.parentElement;
      if (host.querySelector('.ggp-fb-note')) return;
      const note = document.createElement('div');
      note.className = 'ggp-fb-note';
      note.setAttribute('role', 'status');
      note.innerHTML = 'No email app opened? Write to <b></b><button type="button">Copy address</button>';
      note.querySelector('b').textContent = addr;
      note.querySelector('button').addEventListener('click', async (e) => {{
        try {{ await navigator.clipboard.writeText(addr); e.target.textContent = 'Copied'; }}
        catch (err) {{ e.target.textContent = 'Select it above'; }}
      }});
      host.appendChild(note);
    }}, 1500);
  }});
  // v1.12: every app also hits one shared Tally counter, so its `visitor` = unique visitors across all apps
  // (the Open Counts page shows it as "unique since 10-Nov-2026"). Pages that are not apps carry
  // data-ggp-all="off" on their footer. The Quiz draws its footer later, so a missing footer still counts.
  if (!document.querySelector('.ggp-footer[data-ggp-all="off"]')) {{
    fetch('https://tally.yuki.sh/counters/wamware/ggp-all', {{ method: 'POST' }}).catch(() => {{ /* never block the app */ }});
  }}
  // Open counter: shown only where the footer has #ggpCount (the Control Panel). Apps count silently.
  const countEl = document.getElementById('ggpCount');
  if (countEl) {{
    // v1.13: Tally (now "Tallyflare") moved to /counters/<ns>/<key>: POST records a visit and returns the
    // counts, GET only reads. The old hits URLs return 404 since ~11-Nov-2026; counts carried over.
    fetch('https://tally.yuki.sh/counters/wamware/geezer-geek-pilot-control-panel', {{ method: 'POST' }})
      .then(r => r.json())
      .then(d => {{
        const base = parseInt(countEl.dataset.base, 10) || 0;  // pre-Tally opens, App Conventions §6b
        const n = d && typeof d.visit === 'number' ? d.visit + base : null;
        if (typeof n !== 'number') return;
        const text = 'Opened ' + n.toLocaleString() + (n === 1 ? ' time' : ' times');
        const href = countEl.dataset.href;   // v1.4: the count links to the open-counts page
        if (href) {{
          const a = document.createElement('a');
          a.href = href; a.textContent = text; a.title = 'Open counts for every app';
          countEl.replaceChildren(a);
        }} else countEl.textContent = text;
      }})
      .catch(() => {{ /* counter is a nice-to-have, never block the app */ }});
  }}
}})();
</script>
<!-- GGP-FOOTER-JS END -->'''


def footer_html(cfg):
    lines = [f'<!-- GGP-FOOTER START {VERSION} · shared footer, App Conventions §5a · master: Control Panel repo tools/ggp-footer -->',
             '<footer class="ggp-footer"' + ('' if cfg.get('all_count', True) else ' data-ggp-all="off"') + '>']
    if cfg.get('back', True):
        lines.append(f'  <div class="ggp-back"><a href="{CONTROL_PANEL_URL}">&larr; Back to GeezerGeek Pilot Apps</a></div>')
    for text, url in cfg.get('extras', []):
        lines.append(f'  <div class="ggp-extra"><a href="{url}" target="_blank" rel="noopener">{text}</a></div>')
    # v1.3: only "airports visited" is the link (Wayne, 29-Oct-2026)
    name = (f'Wayne McClelland (<a href="{AIRPORTS_URL}" target="_blank" rel="noopener">airports visited</a>)'
            if cfg.get('credit_link', True) else 'Wayne McClelland')
    lines.append(f'  <div class="ggp-credit">{name}, <a href="{YOUTUBE_URL}" target="_blank" rel="noopener">GeezerGeek Pilot</a>, '
                 f'<a href="{REFERENCE_URL}" target="_blank" rel="noopener">Reference Materials</a></div>')
    if cfg.get('count'):
        base = cfg.get('count_base', 0)
        attr = f' data-base="{base}"' if base else ''
        if cfg.get('count_href'):
            attr += f' data-href="{cfg["count_href"]}"'
        lines.append(f'  <div class="ggp-count" id="ggpCount"{attr}></div>')
    lines.append('  <div class="ggp-actions">')
    lines.append(f'    <button class="ggp-pill ggp-share" type="button">{SHARE_ICON}<span>{SHARE_LABEL}</span></button>')
    if cfg.get('feedback', True):
        app = cfg.get('label', cfg['key']).replace('"', '&quot;')
        lines.append(f'    <button class="ggp-pill ggp-feedback" type="button" data-app="{app}">{FEEDBACK_ICON}<span>{FEEDBACK_LABEL}</span></button>')
    if cfg.get('videos', True):
        lines.append(f'    <a class="ggp-pill ggp-videos" href="{VIDEOS_URL}" target="_blank" rel="noopener">{VIDEOS_ICON}<span>{VIDEOS_LABEL}</span></a>')
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
        path = root / cfg.get('repo', app) / cfg['file']
        if not path.exists():
            print(f'{app}: MISSING {path}')
            status = 1
            continue
        src = path.read_text(encoding='utf-8')
        want = render(dict(cfg, key=app))
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
