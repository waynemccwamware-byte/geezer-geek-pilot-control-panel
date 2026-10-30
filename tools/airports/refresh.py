#!/usr/bin/env python3
"""Airports Visited — refresh site/airports/index.html from ForeFlight logbook pages.

Run from the Control Panel repo root:

  python3 tools/airports/refresh.py PAGE.json [PAGE.json ...] [--oa airports.csv] [--full] [--dry-run]

PAGE.json  one or more list_logbook_entries results from the ForeFlight connector, saved as-is
           (the JSON with "entries" and "airports"). A monthly run fetches entries from
           (last_run - 60 days) to today; entries already counted are skipped by logbook_entry_id.
--oa       OurAirports airports.csv (github.com/davidmegginson/ourairports-data). Needed only when a
           page has an airport that neither ForeFlight nor airports.json already knows.
--full     rebuild the airport list from the pages alone (pass every page of the logbook).
--dry-run  report only; write nothing.

Files (all in tools/airports/, not published):
  airports.json  [id, name, city, region, country, lat, lon, first-visit year, flights, route-only]
  state.json     last_run (date of the last refresh) and window_ids (entry IDs already counted that
                 fall in the look-back window). No flight dates are stored: the repo is public and
                 the page shows years only (Wayne's decision, 29-Oct-2026).
  geo.json       Natural Earth base map (world-atlas 2.0.2 countries-50m + us-atlas 3.0.1 states-10m)
  template.html  the page; __AIR__, __GEO__, __SPAN__, __SNAP__ are filled in here.

Limits: an entry edited or deleted after it was counted is not re-counted; an entry back-dated more
than 60 days before the previous run is missed. Run --full with every logbook page to start clean.
"""
import csv, collections, datetime, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
PAGE = REPO / 'site' / 'airports' / 'index.html'
LOOKBACK_DAYS = 60

# ---- rules (Wayne, 29-Oct-2026) ----
SIM_TAILS = {'REDBIRD FMX ABOVE ALL', "ROMAN'S"}      # simulator / AATD sessions, left out
SKIP_RX = re.compile(r'x.?plane|track ?log', re.I)    # X-Plane and track-log entries, left out
# airports ForeFlight's logbook lookup lacks; values from the connector's get_airport (29-Oct-2026)
EXTRA = {
 'XSBY': ['Scorpion Bay Airport', 'San Juanico', 'Baja California Sur', 'Mexico', 26.258347, -112.498272],
 'XFTE': ['El Fuerte', '', 'Sinaloa', 'Mexico', 26.398199, -108.612000],
 'MX0016': ['Bahía Tortugas Airfield', 'Bahía Tortugas', 'Baja California Sur', 'Mexico', 27.706336, -114.912922],
 'MX0375': ['Guachochi', 'Guachochi', 'Chihuahua', 'Mexico', 26.842652, -107.061353],
 # get_airport 30-Oct-2026, per Wayne: PASO in the Alaska entries is Seldovia; KDMG was meant as KDMN
 'PASO': ['Seldovia', 'Seldovia', 'Alaska', 'United States', 59.443906, -151.705042],
 'KDMN': ['Deming Municipal', 'Deming', 'New Mexico', 'United States', 32.262389, -107.719000],
}
ALIAS = {'ABREOJOS': 'MX-AJS', 'LAGUNA': 'MX-0007', 'XSQA': 'MX-1384'}   # logged token -> OurAirports ident
RENAME = {'TORTUGAS': 'MX0016', 'MMXL': 'MMML', 'KDMG': 'KDMN', 'U77': 'KSPK', 'RRTS': 'KRTS'}   # per Wayne 29/30-Oct-2026                          # logged token -> ID to count it under
NAME = {'LAGUNA': 'Laguna San Ignacio Airstrip'}                          # display name override

CC = {'US': 'United States', 'MX': 'Mexico', 'CA': 'Canada', 'PA': 'Panama', 'NI': 'Nicaragua', 'BS': 'Bahamas',
      'TC': 'Turks and Caicos', 'DO': 'Dominican Republic', 'GT': 'Guatemala', 'BZ': 'Belize', 'HN': 'Honduras',
      'CR': 'Costa Rica', 'SV': 'El Salvador', 'CU': 'Cuba', 'CO': 'Colombia', 'JM': 'Jamaica'}
US = dict(AL='Alabama', AK='Alaska', AZ='Arizona', AR='Arkansas', CA='California', CO='Colorado', CT='Connecticut',
          DE='Delaware', FL='Florida', GA='Georgia', HI='Hawaii', ID='Idaho', IL='Illinois', IN='Indiana', IA='Iowa',
          KS='Kansas', KY='Kentucky', LA='Louisiana', ME='Maine', MD='Maryland', MA='Massachusetts', MI='Michigan',
          MN='Minnesota', MS='Mississippi', MO='Missouri', MT='Montana', NE='Nebraska', NV='Nevada', NH='New Hampshire',
          NJ='New Jersey', NM='New Mexico', NY='New York', NC='North Carolina', ND='North Dakota', OH='Ohio',
          OK='Oklahoma', OR='Oregon', PA='Pennsylvania', RI='Rhode Island', SC='South Carolina', SD='South Dakota',
          TN='Tennessee', TX='Texas', UT='Utah', VT='Vermont', VA='Virginia', WA='Washington', WV='West Virginia',
          WI='Wisconsin', WY='Wyoming', DC='District of Columbia')
MXR = dict(AGU='Aguascalientes', BCN='Baja California', BCS='Baja California Sur', CAM='Campeche', CHP='Chiapas',
           CHH='Chihuahua', COA='Coahuila', COL='Colima', DUR='Durango', GUA='Guanajuato', GRO='Guerrero',
           HID='Hidalgo', JAL='Jalisco', MEX='México', MIC='Michoacán', MOR='Morelos', NAY='Nayarit',
           NLE='Nuevo León', OAX='Oaxaca', PUE='Puebla', QUE='Querétaro', ROO='Quintana Roo', SLP='San Luis Potosí',
           SIN='Sinaloa', SON='Sonora', TAB='Tabasco', TAM='Tamaulipas', TLA='Tlaxcala', VER='Veracruz',
           YUC='Yucatán', ZAC='Zacatecas', CMX='Ciudad de México')
OTHER = {('Bahamas', 'EX'): 'Exuma', ('Nicaragua', 'RI'): 'Rivas', ('Panama', '1'): 'Bocas del Toro',
         ('Panama', '8'): 'Panamá', ('Dominican Republic', '18'): 'Puerto Plata', ('Turks and Caicos', 'SC'): ''}


def region(ctry, rg):
    if ctry == 'United States' and rg in US: return US[rg]
    if ctry == 'Mexico' and rg in MXR: return MXR[rg]
    return OTHER.get((ctry, rg), rg)


def toks(s):
    s = re.sub(r'\([^)]*\)', '', (s or '').upper())
    return [x for x in re.split(r'[\s,\-\.]+', s) if x]


def load_oa(path):
    OA, alt = {}, collections.defaultdict(list)
    if not path: return OA, alt
    for r in csv.DictReader(open(path, encoding='utf-8')):
        if r['type'] in ('heliport', 'balloonport'): continue
        rec = [r['name'], r['municipality'], r['iso_region'].split('-', 1)[-1], CC.get(r['iso_country'], r['iso_country']),
               float(r['latitude_deg']), float(r['longitude_deg'])]
        OA[r['ident']] = rec
        for k in ('icao_code', 'gps_code', 'local_code'):
            if r[k]: alt[r[k]].append((r['iso_country'], rec))
    return OA, alt


def main(argv):
    args = [a for a in argv[1:] if not a.startswith('--')]
    full = '--full' in argv; dry = '--dry-run' in argv
    oa_path = None
    if '--oa' in argv:
        oa_path = argv[argv.index('--oa') + 1]; args.remove(oa_path)
    if not args: print(__doc__); return 2

    entries, A = [], {}
    for p in args:
        d = json.load(open(p, encoding='utf-8'))
        entries += d.get('entries', [])
        for k, v in (d.get('airports') or {}).items():
            A[k] = [v.get('name'), v.get('city'), v.get('state'), v.get('country'), v.get('latitude'), v.get('longitude')]
    A.update(EXTRA)

    state = json.load(open(HERE / 'state.json')) if (HERE / 'state.json').exists() and not full else {'window_ids': []}
    seen_ids = set(state.get('window_ids', []))
    # entries before the look-back window were counted by earlier runs (their IDs are no longer kept)
    win_start = '' if full or 'last_run' not in state else (
        datetime.date.fromisoformat(state['last_run']) - datetime.timedelta(days=LOOKBACK_DAYS)).isoformat()
    known = {} if full else {a[0]: a for a in json.load(open(HERE / 'airports.json', encoding='utf-8'))}
    OA, OAalt = load_oa(oa_path)

    def oa(t):
        if t in ALIAS: return OA.get(ALIAS[t])
        if re.fullmatch(r'[A-Z]{4}', t) and t[0] not in 'KM': return None   # e.g. PASO is a fix, not Seldovia AK
        if t in OA: return OA[t]
        c = OAalt.get(t, []); near = [x for k, x in c if k in ('US', 'MX', 'CA')]
        return (near or [x for k, x in c] or [None])[0]

    def resolve(t, endpt):
        if '/' in t: return None, 'radial/DME'
        if re.fullmatch(r'[VJTQ]\d+', t): return None, 'airway'
        if t in A: return A[t], 'ff'
        if t in known: return 'known', 'known'
        if not endpt and re.fullmatch(r'[A-Z]{3}', t): return None, 'navaid'
        if not endpt and re.fullmatch(r'[A-Z]{5}', t) and not t.startswith(('K', 'M')): return None, 'fix'
        if not OA: return None, 'needs OurAirports (--oa)'
        r = oa(t); return (r, 'oa') if r else (None, 'unresolved')

    counted, skipped, unresolved, new_ids = 0, collections.Counter(), collections.defaultdict(set), []
    vis = {}   # id -> {'rec','yr','n','end'} for airports touched by this run
    for e in entries:
        eid = e.get('logbook_entry_id'); ac = e.get('aircraft') or {}
        if eid in seen_ids or (e.get('date') or '') < win_start: skipped['already counted'] += 1; continue
        blob = ' '.join([e.get('remarks') or '', ac.get('tail_number') or '', ac.get('make_model') or '', str(e.get('tags', ''))])
        why = ('simulator' if ac.get('tail_number') in SIM_TAILS else 'no route' if 'route' not in e
               else 'no flight time' if not e.get('total_hours') else 'not approved' if e.get('status') != 'approved'
               else 'X-Plane/track log' if SKIP_RX.search(blob) else None)
        new_ids.append(eid)
        if why: skipped[why] += 1; continue
        counted += 1
        r = e['route']; date = e['date']; yr = int(date[:4])
        here = set()
        for t, endpt in [(r.get('from', ''), 1), (r.get('to', ''), 1)] + [(x, 0) for x in toks(r.get('elements', ''))]:
            t = RENAME.get(t.strip().upper(), t.strip().upper())
            if not t: continue
            rec, how = resolve(t, endpt)
            if rec is None: unresolved[how].add(f'{t} ({date[:4]})'); continue
            if t in here: continue
            here.add(t)
            if rec != 'known' and t in NAME: rec = [NAME[t]] + list(rec[1:])
            v = vis.setdefault(t, {'rec': rec, 'yr': yr, 'n': 0, 'end': 0})
            v['yr'] = min(v['yr'], yr); v['n'] += 1; v['end'] += endpt

    added, bumped = [], []
    out = dict(known)
    for t, v in vis.items():
        if t in out:
            a = list(out[t]); old_yr = a[7]
            a[7] = min(a[7], v['yr']); a[8] += v['n']; a[9] = 0 if (v['end'] or not a[9]) else 1
            out[t] = a; bumped.append(f"{t} (+{v['n']}{', first visit now %d' % a[7] if a[7] != old_yr else ''})")
        else:
            rec = v['rec']
            if rec == 'known': continue
            ctry = rec[3] or ''
            out[t] = [t, rec[0], rec[1] or '', region(ctry, rec[2] or ''), ctry, round(rec[4], 5), round(rec[5], 5),
                      v['yr'], v['n'], 0 if v['end'] else 1]
            added.append(f"{t} {rec[0]} ({v['yr']})")

    rows = sorted(out.values(), key=lambda a: (a[7], a[0]))
    today = datetime.date.today()
    print(f'entries read {len(entries)}; flights counted {counted}; skipped {dict(skipped)}')
    print(f'airports now {len(rows)} (added {len(added)})')
    for a in added: print('  NEW', a)
    for b in bumped: print('  +', b)
    for how, ts in unresolved.items():
        if how not in ('navaid', 'fix', 'airway', 'radial/DME'): print(f'  NOT ON MAP ({how}):', ', '.join(sorted(ts)))
    if dry: print('dry run: nothing written'); return 0

    json.dump(rows, open(HERE / 'airports.json', 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    cutoff = (today - datetime.timedelta(days=LOOKBACK_DAYS + 31)).isoformat()   # keep IDs the next window can see
    window = sorted(set(state.get('window_ids', [])) | set(new_ids)) if not full else sorted(set(new_ids))
    dates = {e.get('logbook_entry_id'): e.get('date', '') for e in entries}
    window = [i for i in window if dates.get(i, '') >= cutoff]
    json.dump({'last_run': today.isoformat(), 'window_ids': window}, open(HERE / 'state.json', 'w'), indent=0)

    t = (HERE / 'template.html').read_text(encoding='utf-8')
    air = [a[:9] for a in rows]
    snap = today.strftime('%d-%b-%Y')
    t = (t.replace('__AIR__', json.dumps(air, ensure_ascii=False, separators=(',', ':')))
          .replace('__GEO__', (HERE / 'geo.json').read_text(encoding='utf-8'))
          .replace('__SPAN__', f"{min(a[7] for a in air)}–{max(a[7] for a in air)}").replace('__SNAP__', snap))
    # keep the shared footer blocks the live page already has (written by tools/ggp-footer)
    live = PAGE.read_text(encoding='utf-8')
    for tag in ('GGP-FOOTER-CSS', 'GGP-FOOTER', 'GGP-FOOTER-JS'):
        rx = re.compile(r'<!-- %s START.*?<!-- %s END -->' % (tag, tag), re.S)
        m = rx.search(live)
        if m: t = rx.sub(lambda _: m.group(0), t, count=1)
    PAGE.write_text(t, encoding='utf-8')
    print(f'wrote {PAGE.relative_to(REPO)} (snapshot {snap})')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
