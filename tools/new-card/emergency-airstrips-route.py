#!/usr/bin/env python3
"""Control Panel card graphic for Planning Emergency Airstrips in Mexico (v1.32, 23-Nov-2026).
Route KSDM MMPE XSQA (Wayne's pick), 25 NM corridor, filters runway >= 2,000 ft + current permit (ICAO: official list),
as in Wayne's 23-Nov-2026 screenshot of the app. Needs the AFAC list JSON (the app's /.netlify/functions/afac output),
mx-icao.json, mx-icao-runways.json. Prints the <svg> to paste into site/index.html. pip: shapely."""
import json, math, sys
from shapely.geometry import LineString
from shapely.ops import transform
afac = json.load(open(sys.argv[1]))['records']
icao = json.load(open(sys.argv[2]))['airports']
irw = json.load(open(sys.argv[3]))['runways']
R = 3440.065
ksdm = (32.572306, -116.979889)              # Brown Field (OurAirports)
mmpe = next((a['lat'], a['lon']) for a in icao if a['code'] == 'MMPE')
sqa = next((r['lat'], r['lon']) for r in afac if r['des'] == 'SQA')
W = [ksdm, mmpe, sqa]; NAMES = ['KSDM', 'MMPE', 'SQA']
lat0 = sum(p[0] for p in W) / 3; cx = math.cos(math.radians(lat0))
P = lambda la, lo: (lo * 60 * cx, la * 60)     # NM, local equirectangular
route = LineString([P(*p) for p in W]); COR = 25
corr = route.buffer(COR, 32)
pts = []
for r in afac:
    if r['lat'] is None or (r['len_m'] or 0) < 610 or not (r['status'] or '').startswith('VIGENTE'): continue
    q = P(r['lat'], r['lon'])
    if route.distance(__import__('shapely.geometry', fromlist=['Point']).Point(q)) <= COR and r['des'] != 'SQA':
        paved = any(k in (r['surf'] or '').upper() for k in ('ASFALT', 'CONCRET', 'PAVIMENTO'))
        pts.append((q, r['des'], paved, False))
for a in icao:
    w = irw.get(a['code']); q = P(a['lat'], a['lon'])
    if a['code'] == 'MMPE' or not a['sam'] or not w or (w[1] or 0) < 2000: continue
    if route.distance(__import__('shapely.geometry', fromlist=['Point']).Point(q)) <= COR: pts.append((q, a['code'], True, True))
# frame
minx, miny, maxx, maxy = corr.bounds
VW, VH, pad = 200, 64, 7
s = min((VW * 0.62) / (maxx - minx), (VH - 2 * pad) / (maxy - miny))
ox = 8 - minx * s; oy = pad + maxy * s
T = lambda x, y: (round(ox + x * s, 1), round(oy - y * s, 1))
def path(coords): return 'M' + ' L'.join(f'{a} {b}' for a, b in (T(*c) for c in coords)) + ' Z'
out = [f'<svg class="app-preview preview-strip" viewBox="0 0 {VW} {VH}" role="img" aria-label="Route KSDM to MMPE to SQA with its 25 NM corridor outlined, the airstrips inside it marked, and the longest stretch with no airstrip in red">',
       f'<rect width="{VW}" height="{VH}" fill="#0f1a1f"/>',
       f'<path d="{path(corr.exterior.coords)}" fill="#f5a623" fill-opacity="0.06" stroke="#f5a623" stroke-width="1" stroke-dasharray="3 2.5"/>']
xs = [T(*P(*p)) for p in W]
out.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in xs)}" fill="none" stroke="#f5a623" stroke-width="1.6"/>')
# longest gap along the route (route airports count)
along = sorted([0, route.length] + [route.project(__import__('shapely.geometry', fromlist=['Point']).Point(q)) for q, *_ in pts] + [route.project(__import__('shapely.geometry', fromlist=['Point']).Point(P(*mmpe)))])
g = max(zip(along, along[1:]), key=lambda t: t[1] - t[0])
from shapely.ops import substring
seg = substring(route, g[0], g[1])
out.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in (T(*c) for c in seg.coords))}" fill="none" stroke="#e0705f" stroke-width="2.4"/>')
for q, code, paved, isicao in pts:
    x, y = T(*q)
    if isicao: out.append(f'<rect x="{x-2.2}" y="{y-2.2}" width="4.4" height="4.4" rx="0.8" fill="#7fd6ee" stroke="#10141a" stroke-width="0.7"/>')
    else: out.append(f'<circle cx="{x}" cy="{y}" r="2.3" fill="{"#b9c2cf" if paved else "#c08a52"}" stroke="#10141a" stroke-width="0.7"/>')
for (x, y), n in zip(xs, NAMES):
    out.append(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#f5a623" stroke="#10141a" stroke-width="0.8"/>')
    dy = -4 if n != 'SQA' else 7
    out.append(f'<text x="{x}" y="{y + dy}" font-family="monospace" font-size="6.5" font-weight="700" fill="#f5a623" text-anchor="middle">{n}</text>')
tx = 8 + (maxx - minx) * s + 8
gapnm = 99   # the app's own figure for this route and filters (its per-leg projection gives 99; this one-frame projection 100)
out += [f'<text x="{tx}" y="20" font-family="monospace" font-size="7.5" fill="#e7e4dc">{len(pts)} airstrips</text>',
        f'<text x="{tx}" y="29" font-family="sans-serif" font-size="6.5" fill="#8b93a1">within {COR} NM</text>',
        f'<text x="{tx}" y="44" font-family="monospace" font-size="7.5" fill="#e0705f">{gapnm} NM gap</text>',
        f'<text x="{tx}" y="53" font-family="sans-serif" font-size="6.5" fill="#8b93a1">longest, in red</text>', '</svg>']
print('\n'.join(out))
