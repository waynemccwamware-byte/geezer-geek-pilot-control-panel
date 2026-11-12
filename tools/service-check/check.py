#!/usr/bin/env python3
"""GeezerGeek Pilot daily service check + counter history (run by .github/workflows/service-check.yml).

Checks, read-only (nothing here bumps a counter or changes an app's data):
  1. every app page loads and still carries the shared footer
  2. every Tally counter answers (GET /counters/wamware/<key> only reads)
  3. each app's own Netlify function answers with real data, and FAA data is inside its cycle
  4. the outside sources the apps or their functions pull from (FAA, NOAA, CDNs)

  python3 check.py                       # checks only; report to stdout, exit 1 if anything failed
  python3 check.py --history FILE.json   # also append today's counter snapshot to FILE.json

Standard library only. Each request is retried once after 20 s so a brief blip doesn't raise an alarm.
"""
import datetime as dt
import json
import sys
import time
import urllib.error
import urllib.request

UA = 'Mozilla/5.0 (GeezerGeek Pilot daily service check; +https://geezer-geek-pilot-control-panel.netlify.app/)'
TALLY = 'https://tally.yuki.sh/counters/wamware/'

APPS = {   # Tally key -> live site
    'geezer-geek-pilot-control-panel': 'https://geezer-geek-pilot-control-panel.netlify.app/',
    'claude-foreflight-primer': 'https://claude-foreflight-primer.netlify.app/',
    'piston-ga-stats': 'https://piston-ga-stats.netlify.app/',
    'weather-history-probability': 'https://weather-history-probability.netlify.app/',
    'digital-autopilots-quiz': 'https://digital-autopilots-quiz.netlify.app/',
    'tec-route-lookup': 'https://tec-route-lookup.netlify.app/',
    'clearance-delivery': 'https://clearance-delivery.netlify.app/',
    'atc-chair-fly-trainer': 'https://atc-chair-fly-trainer.netlify.app/',
    'days-flight-schedule': 'https://days-flight-schedule.netlify.app/',
    'fuel-to-add': 'https://fuel-to-add.netlify.app/',
}
COUNTERS = list(APPS) + ['ggp-all']   # ggp-all: shared counter, its visitor = unique visitors across all apps

# Outside sources (a small ranged GET, so big files aren't downloaded)
UPSTREAMS = [
    ('FAA preferred routes CSV (TEC Route Lookup)', 'https://www.fly.faa.gov/rmt/data_file/prefroutes_db.csv'),
    ('FAA NASR subscription page (Clearance Delivery FAA update)',
     'https://www.faa.gov/air_traffic/flight_info/aeronav/aero_data/NASR_Subscription/'),
    ('NOAA GHCNh station list (Weather)',
     'https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh-station-list.csv'),
    ('jsPDF on jsDelivr (Day\'s Flight Schedule PDF)', 'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js'),
    ('Chart.js on cdnjs (Weather charts)', 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js'),
]


def get(url, ranged=False, tries=2):
    """Return (status, body text). status 0 = no answer at all."""
    last = (0, '')
    for i in range(tries):
        headers = {'User-Agent': UA}
        if ranged:
            headers['Range'] = 'bytes=0-2047'
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=45) as r:
                return r.status, r.read(400_000).decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            last = (e.code, '')
        except Exception as e:   # timeout, DNS, TLS
            last = (0, f'{type(e).__name__}: {e}')
        if i + 1 < tries:
            time.sleep(20)
    return last


def get_json(url):
    status, body = get(url)
    try:
        return status, json.loads(body) if status == 200 else None
    except ValueError:
        return status, None


def main(argv):
    today = dt.date.today()
    results = []   # (group, name, ok, detail)

    def add(group, name, ok, detail=''):
        results.append((group, name, ok, detail))

    # 1. app pages
    for key, url in APPS.items():
        status, body = get(url)
        ok = status == 200 and 'ggp-footer' in body
        add('Apps', url.split('//')[1].split('.')[0], ok,
            f'HTTP {status}' + ('' if ok or status != 200 else ', page loaded but the shared footer is missing'))

    # 2. Tally counters (also the history snapshot)
    snapshot = {}
    for key in COUNTERS:
        status, d = get_json(TALLY + key)
        ok = bool(d) and isinstance(d.get('visit'), int) and isinstance(d.get('visitor'), int)
        if ok:
            snapshot[key] = [d['visit'], d['visitor']]
        add('Tally counters', key, ok, f"{d['visit']} opens, {d['visitor']} visitors" if ok else f'HTTP {status}')

    # 3. the apps' own Netlify functions
    status, d = get_json('https://tec-route-lookup.netlify.app/.netlify/functions/tec-lookup?action=destinations&origin=SBA')
    ok = bool(d) and len(d.get('destinations') or []) > 5
    detail = f'HTTP {status}'
    if ok:
        until = (d.get('effectiveUntil') or '')[:10]
        detail = f"{len(d['destinations'])} destinations from SBA, FAA data good until {until}"
        if until and until < today.isoformat():
            ok, detail = False, f'FAA route data expired {until}: open TEC Route Lookup and refresh'
    add('App functions', 'TEC Route Lookup (tec-lookup)', ok, detail)

    status, d = get_json('https://weather-history-probability.netlify.app/.netlify/functions/fetch-station'
                         f'?action=resolve&icao=KSBA&startYear={today.year - 2}&endYear={today.year - 1}')
    cands = (d or {}).get('candidates') or []
    ok = bool(cands and cands[0].get('id'))
    add('App functions', 'Weather (fetch-station, KSBA via NOAA)', ok,
        f"station {cands[0]['id']}" if ok else f'HTTP {status}, no station found')

    status, d = get_json('https://clearance-delivery.netlify.app/.netlify/functions/nasr-freq?action=get')
    meta = (d or {}).get('meta') or {}
    ok = bool(meta.get('airports'))
    detail = f'HTTP {status}, no stored FAA frequency data'
    if ok:
        until = meta.get('until', '')
        detail = f"{meta['airports']} airports, FAA cycle {meta.get('effective')} to {until}"
        if until and until < today.isoformat():
            ok, detail = False, f"FAA frequency cycle ended {until}: press Update FAA data in Clearance Delivery"
    add('App functions', 'Clearance Delivery (nasr-freq)', ok, detail)

    # 4. outside sources
    for name, url in UPSTREAMS:
        status, _ = get(url, ranged=True)
        add('Outside sources', name, status in (200, 206), f'HTTP {status}')

    # report
    failed = [r for r in results if not r[2]]
    lines = [f'**{len(failed)} of {len(results)} checks failed**' if failed else f'**All {len(results)} checks passed**', '']
    for group in dict.fromkeys(r[0] for r in results):
        lines += [f'### {group}', '', '| | Check | Result |', '|---|---|---|']
        lines += [f"| {'✅' if ok else '❌'} | {name} | {detail} |" for g, name, ok, detail in results if g == group]
        lines.append('')
    print('\n'.join(lines))

    # history
    if '--history' in argv:
        path = argv[argv.index('--history') + 1]
        try:
            with open(path) as f:
                hist = json.load(f)
        except (OSError, ValueError):
            hist = {'rows': []}
        hist['about'] = ('Daily Tally readings for the GeezerGeek Pilot apps: c[key] = [opens, visitors], raw Tally '
                         'values (no pre-Tally bases). Written by tools/service-check/check.py on the main branch.')
        if snapshot:
            hist['rows'].append({'t': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'c': snapshot})
        with open(path, 'w') as f:
            json.dump(hist, f, separators=(',', ':'))
            f.write('\n')

    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
