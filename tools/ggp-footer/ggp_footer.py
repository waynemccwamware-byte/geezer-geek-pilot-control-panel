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

VERSION = 'v1.15 · 25-Nov-2026'

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

# v1.15 (25-Nov-2026): English/Español. The head block carries the shared language core (window.ggpLang, App Conventions
# "Language"): ?lang=en|es in the address wins and is saved on the device; else the saved choice; else on a phone or
# tablet the device's language (Spanish if it starts with es), and English on a computer. Each app is its own site,
# so its storage is its own: while a choice is saved, links to the suite's other sites carry ?lang= so it follows the
# user. Pages with es=True in APPS have a Spanish UI (html lang becomes es-MX); on the rest only the footer turns Spanish.
# Switching language saves and reloads the page. Spanish is Mexican Spanish (tú), dates stay dd-mmm-yyyy (25-nov-2026).
SITES = ['geezer-geek-pilot-control-panel', 'weather-history-probability', 'digital-autopilots-quiz', 'tec-route-lookup',
         'atc-chair-fly-trainer', 'days-flight-schedule', 'fuel-to-add', 'clearance-delivery', 'piston-ga-stats',
         'claude-foreflight-primer', 'airfield-kml-builder', 'emergency-airstrips-mexico']   # <name>.netlify.app
ES = {
    'back': '&larr; Volver a las apps de GeezerGeek Pilot',
    'airports': 'aeropuertos visitados',
    'reference': 'Material de referencia',
    'share': 'Comparte las apps de GeezerGeek Pilot con amigos pilotos',
    'feedback': 'Comentarios a GeezerGeek Pilot',
    'videos': 'Videos de introducción en YouTube (en inglés)',
    'share_text': 'Herramientas de planeación, meteorología, práctica de ATC y seguridad para pilotos de aviación general, de GeezerGeek Pilot.',
}
INSTALL_ES = {'Add this app to Home Screen': 'Agrega esta app a tu pantalla de inicio',
              'Add this app to Home Screen/Desktop': 'Agrega esta app a tu pantalla de inicio o escritorio',
              'Install this app': 'Instala esta app'}

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
# es: the page has a Spanish UI (v1.15); without it only the footer follows a Spanish choice.
# all_count: also hit the shared Tally counter wamware/ggp-all (default True), whose `visitor` is unique visitors
#   across every app (v1.12, Wayne 10-Nov-2026). Off for pages that are not apps (the stats page, the airports map).
APPS = {
    # count_base: estimated opens before the Tally counter started (20-Oct-2026); added to the shown number.
    'geezer-geek-pilot-control-panel': dict(file='site/index.html', back=False, count=True, count_base=300, count_href='stats/', es=True,
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
    # 14-Nov-2026: new app (on the Control Panel from v1.25)
    'airfield-kml-builder': dict(file='site/index.html', label='Mexican Airstrips for your EFB and Sim', es=True),
    # 23-Nov-2026: companion to Mexican Airstrips (Control Panel v1.32, Time, Route & Fuel Planning)
    'emergency-airstrips-mexico': dict(file='site/index.html', label='Planning Emergency Airstrips in Mexico', es=True),
    'airports-visited': dict(repo='geezer-geek-pilot-control-panel', file='site/airports/index.html', label='Airports Visited',
                             credit_link=False, all_count=False),   # the page the credit links to
    # v1.4: open-counts page, linked from the Control Panel's "Opened N times" (Wayne, 02-Nov-2026)
    'open-counts': dict(repo='geezer-geek-pilot-control-panel', file='site/stats/index.html', label='App Open Counts', all_count=False),
}

LANG_CORE = r'''
(function () {
  if (window.ggpLang) return;
  var KEY = 'ggp-lang', I18N = __I18N__, SITES = __SITES__;
  var q = null, saved = null, lang, explicit = false;
  try { q = new URLSearchParams(location.search).get('lang'); } catch (e) {}
  try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (q === 'en' || q === 'es') { lang = q; explicit = true; if (saved !== q) { try { localStorage.setItem(KEY, q); } catch (e) {} } }
  else if (saved === 'en' || saved === 'es') { lang = saved; explicit = true; }
  else {
    var ua = navigator.userAgent || '';
    var mobile = /iPhone|iPad|iPod|Android/i.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
    var first = (navigator.languages && navigator.languages[0]) || navigator.language || '';
    lang = mobile && /^es\b/i.test(first) ? 'es' : 'en';
  }
  var es = lang === 'es';
  if (I18N) document.documentElement.lang = es ? 'es-MX' : 'en';
  var MON = { en: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
              es: ['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'] };
  var ATTRS = ['title', 'placeholder', 'aria-label', 'alt', 'value', 'content'];
  var ours = function (host) { return SITES.indexOf(host.replace(/\.netlify\.app$/, '').replace(/^[a-z0-9-]+--/, '')) >= 0 && /\.netlify\.app$/.test(host); };
  var withLang = function (href) {
    try {
      var u = new URL(href, location.href);
      if (!/^https?:$/.test(u.protocol) || !ours(u.hostname)) return href;
      u.searchParams.set('lang', lang);
      return u.toString();
    } catch (e) { return href; }
  };
  var G = window.ggpLang = {
    lang: lang, es: es, explicit: explicit, i18n: I18N,
    // L('English', 'Español'): the string for the current language (Spanish missing → English)
    L: function (en, sp) { return es && sp != null ? sp : en; },
    // dd-mmm-yyyy: 25-Nov-2026 / 25-nov-2026. Takes a Date or 'YYYY-MM-DD…'.
    date: function (d) {
      var y, m, dd;
      if (d instanceof Date) { y = d.getFullYear(); m = d.getMonth(); dd = d.getDate(); }
      else { var x = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(d || '')); if (!x) return String(d || ''); y = +x[1]; m = +x[2] - 1; dd = +x[3]; }
      return (dd < 10 ? '0' : '') + dd + '-' + MON[lang][m] + '-' + y;
    },
    // any 25-Nov-2026 in a string, in the current language (25-nov-2026)
    dmy: function (str) {
      if (!es) return String(str == null ? '' : str);
      return String(str == null ? '' : str).replace(/\b(\d{1,2})-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-(\d{4})\b/g,
        function (m, d, mo, y) { return d + '-' + MON.es[MON.en.indexOf(mo)] + '-' + y; });
    },
    withLang: withLang,
    // Elements marked data-es="…" (innerHTML) or data-es-title, data-es-placeholder, … get their Spanish once.
    apply: function (root) {
      if (!es) return;
      root = root || document;
      var els = root.querySelectorAll('[data-es],' + ATTRS.map(function (a) { return '[data-es-' + a + ']'; }).join(','));
      for (var i = 0; i < els.length; i++) {
        var el = els[i];
        if (el.__ggpEs) continue;
        el.__ggpEs = true;
        if (el.hasAttribute('data-es') && (I18N || el.closest('.ggp-footer'))) el.innerHTML = el.getAttribute('data-es');
        for (var j = 0; j < ATTRS.length; j++) {
          var v = el.getAttribute('data-es-' + ATTRS[j]);
          if (v != null && (I18N || el.closest('.ggp-footer'))) el.setAttribute(ATTRS[j], v);
        }
      }
    },
    // Save the choice and reload in it (the page is drawn once per language).
    set: function (l) {
      if (l !== 'en' && l !== 'es') return;
      try { localStorage.setItem(KEY, l); } catch (e) {}
      if (l === 'es' && !es) { try { fetch('https://tally.yuki.sh/counters/wamware/ggp-es-picked', { method: 'POST', keepalive: true }); } catch (e) {} }
      if (l === lang && explicit) return;
      var u = new URL(location.href); u.searchParams.delete('lang');
      location.replace(u.toString());
    }
  };
  // English | Español switch: any .ggp-lang-switch holding buttons with data-ggp-lang="en" / "es".
  var mark = function () {
    var bs = document.querySelectorAll('.ggp-lang-switch [data-ggp-lang]');
    for (var i = 0; i < bs.length; i++) {
      var on = bs[i].getAttribute('data-ggp-lang') === lang;
      bs[i].setAttribute('aria-pressed', on ? 'true' : 'false');
      bs[i].classList.toggle('on', on);
    }
  };
  document.addEventListener('click', function (ev) {
    var t = ev.target instanceof Element ? ev.target : null;
    var b = t && t.closest('.ggp-lang-switch [data-ggp-lang]');
    if (b) { ev.preventDefault(); G.set(b.getAttribute('data-ggp-lang')); return; }
    // carry the choice to the suite's other sites (each keeps its own storage)
    var a = explicit && t && t.closest('a[href]');
    if (a) { var h = withLang(a.href); if (h !== a.href) a.href = h; }
  }, true);
  var links = function () {
    if (!explicit) return;
    var as = document.querySelectorAll('a[href]');
    for (var i = 0; i < as.length; i++) { var h = withLang(as[i].href); if (h !== as[i].href) as[i].href = h; }
  };
  document.addEventListener('DOMContentLoaded', function () { G.apply(); mark(); links(); });
  G.mark = mark;
})();
'''


LANG_CSS = '''
/* v1.15: English | Español switch (App Conventions "Language"); sits at the right end of the title row */
.ggp-lang-switch{ display:inline-flex; flex-shrink:0; border:1px solid #f5a623; border-radius:16px; overflow:hidden;
  font:600 12.5px/1 'IBM Plex Sans', system-ui, -apple-system, 'Segoe UI', sans-serif; }
.ggp-lang-switch button{ margin:0; padding:7px 12px; border:0; background:transparent; color:#f5a623; font:inherit; cursor:pointer; }
.ggp-lang-switch button + button{ border-left:1px solid #f5a623; }
.ggp-lang-switch button.on, .ggp-lang-switch button[aria-pressed="true"]{ background:#f5a623; color:#10141a; }
.ggp-lang-switch button:not(.on):hover{ background:rgba(245,166,35,.15); }
.ggp-lang-switch button:focus-visible{ outline:2px solid #e7e4dc; outline-offset:-3px; }
@media (max-width:400px){ .ggp-lang-switch button{ padding:7px 9px; font-size:12px; } }
@media print{ .ggp-lang-switch{ display:none !important; } }'''


def head_block(cfg):
    core = LANG_CORE.replace('__I18N__', 'true' if cfg.get('es') else 'false').replace(
        '__SITES__', '[' + ','.join(f"'{x}'" for x in SITES) + ']')
    return CSS.replace('/*__LANG_CSS__*/', LANG_CSS).replace('<!--__LANG_JS__-->', '<script>' + core + '</script>')


CSS = f'''<!-- GGP-FOOTER-CSS START {VERSION} · shared footer styles + language core, App Conventions §5b · master: Control Panel repo tools/ggp-footer -->
<!--__LANG_JS__-->
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
}}/*__LANG_CSS__*/
</style>
<!-- GGP-FOOTER-CSS END -->'''

JS = f'''<!-- GGP-FOOTER-JS START {VERSION} · shared footer script, App Conventions §6a/§6b · master: Control Panel repo tools/ggp-footer -->
<script>
(() => {{
  if (window.__ggpFooter) return;
  window.__ggpFooter = true;
  // Every app's footer share button shares the Control Panel, not the app itself.
  // v1.15: shared from a Spanish page, the link carries ?lang=es (Spanish preview card, Control Panel opens in Spanish)
  const SHARE_URL   = '{CONTROL_PANEL_URL}' + (window.ggpLang && window.ggpLang.es ? '?lang=es' : '');
  const SHARE_TITLE = window.ggpLang && window.ggpLang.es ? 'Apps de GeezerGeek Pilot' : '{SHARE_TITLE}';
  const L = (en, es) => (window.ggpLang ? window.ggpLang.L(en, es) : en);
  const SHARE_TEXT  = L('{SHARE_TEXT}', '{ES["share_text"]}');
  if (window.ggpLang) window.ggpLang.apply(document.querySelector('.ggp-footer') || document);
  const flash = (btn) => {{
    if (btn.dataset.ggpBusy) return;
    btn.dataset.ggpBusy = '1';
    const label = btn.querySelector('span') || btn;
    const original = label.textContent;
    label.textContent = label === btn ? L('Link copied!', '¡Enlace copiado!') : L('Link copied to clipboard!', '¡Enlace copiado al portapapeles!');
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
      note.innerHTML = L('No email app opened? Write to ', '¿No se abrió tu app de correo? Escribe a ') + '<b></b><button type="button">' + L('Copy address', 'Copiar dirección') + '</button>';
      note.querySelector('b').textContent = addr;
      note.querySelector('button').addEventListener('click', async (e) => {{
        try {{ await navigator.clipboard.writeText(addr); e.target.textContent = L('Copied', 'Copiada'); }}
        catch (err) {{ e.target.textContent = L('Select it above', 'Selecciónala arriba'); }}
      }});
      host.appendChild(note);
    }}, 1500);
  }});
  // v1.12: every app also hits one shared Tally counter, so its `visitor` = unique visitors across all apps
  // (the Open Counts page shows it as "unique since 10-Nov-2026"). Pages that are not apps carry
  // data-ggp-all="off" on their footer. The Quiz draws its footer later, so a missing footer still counts.
  if (!document.querySelector('.ggp-footer[data-ggp-all="off"]')) {{
    fetch('https://tally.yuki.sh/counters/wamware/ggp-all', {{ method: 'POST' }}).catch(() => {{ /* never block the app */ }});
    // v1.15: and, when the page opens in Spanish, wamware/ggp-es (opens in Spanish; its visitor = Spanish users)
    if (window.ggpLang && window.ggpLang.es)
      fetch('https://tally.yuki.sh/counters/wamware/ggp-es', {{ method: 'POST' }}).catch(() => {{}});
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
        const text = L('Opened ', 'Abierta ') + n.toLocaleString('en-US') + (n === 1 ? L(' time', ' vez') : L(' times', ' veces'));
        const href = countEl.dataset.href;   // v1.4: the count links to the open-counts page
        if (href) {{
          const a = document.createElement('a');
          a.href = href; a.textContent = text; a.title = L('Open counts for every app', 'Aperturas de cada app');
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
        lines.append(f'  <div class="ggp-back"><a href="{CONTROL_PANEL_URL}" data-es="{ES["back"]}">&larr; Back to GeezerGeek Pilot Apps</a></div>')
    for text, url in cfg.get('extras', []):
        lines.append(f'  <div class="ggp-extra"><a href="{url}" target="_blank" rel="noopener">{text}</a></div>')
    # v1.3: only "airports visited" is the link (Wayne, 29-Oct-2026)
    name = (f'Wayne McClelland (<a href="{AIRPORTS_URL}" target="_blank" rel="noopener" data-es="{ES["airports"]}">airports visited</a>)'
            if cfg.get('credit_link', True) else 'Wayne McClelland')
    lines.append(f'  <div class="ggp-credit">{name}, <a href="{YOUTUBE_URL}" target="_blank" rel="noopener">GeezerGeek Pilot</a>, '
                 f'<a href="{REFERENCE_URL}" target="_blank" rel="noopener" data-es="{ES["reference"]}">Reference Materials</a></div>')
    if cfg.get('count'):
        base = cfg.get('count_base', 0)
        attr = f' data-base="{base}"' if base else ''
        if cfg.get('count_href'):
            attr += f' data-href="{cfg["count_href"]}"'
        lines.append(f'  <div class="ggp-count" id="ggpCount"{attr}></div>')
    lines.append('  <div class="ggp-actions">')
    lines.append(f'    <button class="ggp-pill ggp-share" type="button">{SHARE_ICON}<span data-es="{ES["share"]}">{SHARE_LABEL}</span></button>')
    if cfg.get('feedback', True):
        app = cfg.get('label', cfg['key']).replace('"', '&quot;')
        lines.append(f'    <button class="ggp-pill ggp-feedback" type="button" data-app="{app}">{FEEDBACK_ICON}<span data-es="{ES["feedback"]}">{FEEDBACK_LABEL}</span></button>')
    if cfg.get('videos', True):
        lines.append(f'    <a class="ggp-pill ggp-videos" href="{VIDEOS_URL}" target="_blank" rel="noopener">{VIDEOS_ICON}<span data-es="{ES["videos"]}">{VIDEOS_LABEL}</span></a>')
    if cfg.get('install'):
        bid, label = cfg['install']
        lines.append(f'    <button class="ggp-pill" id="{bid}" type="button" style="display:none;">{INSTALL_ICON}<span data-es="{INSTALL_ES.get(label, label)}">{label}</span></button>')
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
    return {'css': head_block(cfg), 'html': footer_html(cfg), 'js': JS}


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
