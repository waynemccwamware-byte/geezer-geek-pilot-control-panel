#!/usr/bin/env python3
"""Animated "New" card for Planning Emergency Airstrips in Mexico (Control Panel v1.33, 23-Nov-2026, Wayne).
Wide card (viewBox 400 x 104), SVG/SMIL, 12 s loop. Route KSDM MMPE XSQA, 25 NM corridor, runway >= 2,000 ft + current
permit (ICAO: official list), as in tools/new-card/emergency-airstrips-route.py.
Timeline: 0-2.5 s finished picture (the still frame the page shows at 0.8 s for Reduce Motion or after New expires),
2.5-3.0 fade out, 3.0-4.4 the route types itself into the box, 4.6-8.6 the line draws KSDM -> MMPE -> SQA with each
airstrip appearing as the line passes it and the count going up, 8.8 the longest gap flashes red, hold to 12 s.
Land: Natural Earth 50 m land (public domain), github.com/nvkelso/natural-earth-vector geojson/ne_50m_land.geojson.
Run: emergency-airstrips-animated.py afac.json mx-icao.json mx-icao-runways.json ne_50m_land.geojson > card.svg
pip: shapely."""
import json, math, sys
from shapely.geometry import LineString, Point, shape, box
from shapely.ops import substring
afac = json.load(open(sys.argv[1]))['records']
icao = json.load(open(sys.argv[2]))['airports']
irw = json.load(open(sys.argv[3]))['runways']
land = json.load(open(sys.argv[4]))['features']
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
    if route.distance(Point(q)) <= COR and r['des'] != 'SQA':
        paved = any(k in (r['surf'] or '').upper() for k in ('ASFALT', 'CONCRET', 'PAVIMENTO'))
        pts.append((q, r['des'], paved, False))
for a in icao:
    w = irw.get(a['code']); q = P(a['lat'], a['lon'])
    if a['code'] == 'MMPE' or not a['sam'] or not w or (w[1] or 0) < 2000: continue
    if route.distance(Point(q)) <= COR: pts.append((q, a['code'], True, True))

# ---- frame: map on the left, text panel on the right
VW, VH = 400, 104
minx, miny, maxx, maxy = corr.buffer(14).bounds   # room round the corridor for the labels
mx0, my0, mh = 6, 6, VH - 12
s = mh / (maxy - miny)
mw = round(min(250, (maxx - minx) * s + 24), 1)
ox = mx0 + (mw - (maxx - minx) * s) / 2 - minx * s
oy = my0 + mh + miny * s
T = lambda x, y: (round(ox + x * s, 1), round(oy - y * s, 1))
inv = lambda X, Y: ((X - ox) / s, (oy - Y) / s)
def d_of(coords, close=False):
    return 'M' + ' L'.join(f'{a} {b}' for a, b in (T(*c) for c in coords)) + (' Z' if close else '')

# ---- timeline
DUR = 12.0
HOLD_END, FADE_END = 2.5, 3.0
TYPE0, TYPE1 = 3.0, 4.4
DRAW0, DRAW1 = 4.6, 8.6
GAP_T = 8.8
L = route.length
t_at = lambda along: DRAW0 + (DRAW1 - DRAW0) * along / L
kt = lambda *ts: ';'.join(f'{min(max(t / DUR, 0), 1):.4f}' for t in ts)
def appear(t, extra=''):
    """opacity: on, fade out at 2.5-3.0, back on at t (0.15 s)."""
    return (f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" '
            f'keyTimes="{kt(0, HOLD_END, FADE_END, t, t + 0.15, DUR)}" values="1;1;0;0;1;1"/>{extra}')

out = [f'<svg class="app-preview preview-wide" viewBox="0 0 {VW} {VH}" role="img" aria-label="Animated: the route KSDM MMPE XSQA is typed in and drawn across northwest Mexico with its 25 NM corridor; ten airstrips appear as the line passes them, and the longest stretch with no airstrip, 99 NM, shows in red">',
       f'<rect width="{VW}" height="{VH}" fill="#0b1620"/>',
       f'<clipPath id="eamMap"><rect x="{mx0}" y="{my0}" width="{mw}" height="{mh}" rx="3"/></clipPath>']
# land (static), clipped to the map box
x0, y0 = inv(mx0, my0 + mh); x1, y1 = inv(mx0 + mw, my0)
lb = box(x0, y0, x1, y1)
def proj_geom(g):
    import shapely
    return shapely.transform(g, lambda c: c * [60 * cx, 60])
land_d = []
for f in land:
    g = shape(f['geometry'])
    if not g.intersects(box(-125, 20, -100, 40)): continue
    g = proj_geom(g).intersection(lb.buffer(5))
    if g.is_empty: continue
    for poly in (g.geoms if hasattr(g, 'geoms') else [g]):
        if poly.geom_type != 'Polygon' or poly.area < 1: continue
        land_d.append(d_of(poly.exterior.coords, True))
out.append(f'<g clip-path="url(#eamMap)"><rect x="{mx0}" y="{my0}" width="{mw}" height="{mh}" fill="#0e2a3a"/>'
           f'<path d="{" ".join(land_d)}" fill="#24251c" stroke="#3b3c2c" stroke-width="0.6"/>')
# corridor: fades in while the line draws
out.append(f'<path d="{d_of(corr.exterior.coords, True)}" fill="#f5a623" fill-opacity="0.07" stroke="#f5a623" stroke-width="1" stroke-dasharray="3 2.5">'
           f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, HOLD_END, FADE_END, DRAW0, DRAW0 + 1.2, DUR)}" values="1;1;0;0;1;1"/></path>')
# route line: draws at a steady speed (pathLength 1)
xs = [T(*P(*p)) for p in W]
out.append(f'<polyline points="{" ".join(f"{a},{b}" for a, b in xs)}" pathLength="1" fill="none" stroke="#f5a623" stroke-width="2" stroke-linecap="round" stroke-dasharray="1 1">'
           f'<animate attributeName="stroke-dashoffset" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, HOLD_END, FADE_END, DRAW0, DRAW1, DUR)}" values="0;0;1;1;0;0"/>'
           f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, HOLD_END, FADE_END, FADE_END + 0.01, DUR)}" values="1;1;0;1;1"/></polyline>')
# longest gap (route airports count, as in the app)
along = sorted([0, L] + [route.project(Point(q)) for q, *_ in pts] + [route.project(Point(P(*mmpe)))])
g = max(zip(along, along[1:]), key=lambda t: t[1] - t[0])
seg = substring(route, g[0], g[1])
gap_pts = " ".join(f"{a},{b}" for a, b in (T(*c) for c in seg.coords))
out.append(f'<polyline points="{gap_pts}" fill="none" stroke="#e0705f" stroke-width="3" stroke-linecap="round">'
           f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, HOLD_END, FADE_END, GAP_T, GAP_T + 0.2, GAP_T + 0.5, GAP_T + 0.8, GAP_T + 1.1, DUR)}" values="1;1;0;0;1;0.25;1;1;1"/>'
           f'<animate attributeName="stroke-width" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, GAP_T, GAP_T + 0.4, GAP_T + 1.1, DUR)}" values="3;3;5.5;3;3"/></polyline>')
# airstrips, in route order, each appearing as the line passes it
order = sorted(pts, key=lambda p: route.project(Point(p[0])))
times = []
for q, code, paved, isicao in order:
    x, y = T(*q); t = t_at(route.project(Point(q))); times.append(t)
    if isicao: shp = f'<rect x="{x - 2.8}" y="{y - 2.8}" width="5.6" height="5.6" rx="1" fill="#7fd6ee" stroke="#0b1620" stroke-width="0.8">'
    else: shp = f'<circle cx="{x}" cy="{y}" r="3" fill="{"#b9c2cf" if paved else "#c08a52"}" stroke="#0b1620" stroke-width="0.8">'
    tag = 'rect' if isicao else 'circle'
    # a ring that pings out as each one appears
    out.append(f'<circle cx="{x}" cy="{y}" r="3" fill="none" stroke="#e7e4dc" stroke-width="0.8" opacity="0">'
               f'<animate attributeName="r" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, t, t + 0.6, DUR)}" values="3;3;9;9"/>'
               f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, t, t + 0.05, t + 0.6, DUR)}" values="0;0;0.8;0;0"/></circle>')
    out.append(shp + appear(t) + f'</{tag}>')
# route waypoints and labels
for i, ((x, y), n) in enumerate(zip(xs, NAMES)):
    t = t_at(route.project(Point(P(*W[i])))) if i else DRAW0
    dy = -5 if n != 'SQA' else 9
    out.append(f'<g>{appear(t)}<circle cx="{x}" cy="{y}" r="3.2" fill="#f5a623" stroke="#0b1620" stroke-width="0.9"/>'
               f'<text x="{x}" y="{y + dy}" font-family="monospace" font-size="8" font-weight="700" fill="#f5a623" text-anchor="middle" stroke="#0b1620" stroke-width="2.2" paint-order="stroke">{n}</text></g>')
out.append('</g>')

# ---- right panel
px = round(mx0 + mw + 16)
route_txt = 'KSDM MMPE XSQA'
cw = 8 * 0.6  # monospace advance at 8 px
tw = len(route_txt) * cw
out.append(f'<text x="{px}" y="14" font-family="monospace" font-size="6.5" fill="#8b93a1" letter-spacing="0.6">ROUTE</text>')
out.append(f'<rect x="{px}" y="18" width="{VW - px - 8}" height="17" rx="3" fill="#10141a" stroke="#3a4454"/>')
out.append(f'<clipPath id="eamType"><rect x="{px + 5}" y="18" height="17" width="{tw + 1}">'
           f'<animate attributeName="width" dur="{DUR}s" repeatCount="indefinite" keyTimes="{kt(0, HOLD_END, FADE_END, TYPE0, TYPE1, DUR)}" values="{tw + 1};{tw + 1};0;0;{tw + 1};{tw + 1}" calcMode="discrete"/>'
           '</rect></clipPath>')
# discrete typing: one keyframe per character
ks, vs = [0, HOLD_END, FADE_END], [tw + 1, tw + 1, 0]
for i in range(1, len(route_txt) + 1):
    ks.append(TYPE0 + (TYPE1 - TYPE0) * i / len(route_txt)); vs.append(round(i * cw, 2))
out[-1] = (f'<clipPath id="eamType"><rect x="{px + 5}" y="18" height="17" width="{tw + 1}">'
           f'<animate attributeName="width" dur="{DUR}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt(*ks)}" values="{";".join(str(v) for v in vs)}"/>'
           '</rect></clipPath>')
out.append(f'<text x="{px + 5}" y="29.6" font-family="monospace" font-size="8" fill="#e7e4dc" clip-path="url(#eamType)">{route_txt}</text>')
# caret: follows the typing, blinks while idle, gone in the finished picture
cks, cxs = [0, FADE_END], [px + 5 + tw + 1, px + 5]
for i in range(1, len(route_txt) + 1):
    cks.append(TYPE0 + (TYPE1 - TYPE0) * i / len(route_txt)); cxs.append(round(px + 5 + i * cw + 0.5, 2))
out.append(f'<rect x="{px + 5}" y="22.5" width="1" height="9" fill="#f5a623" opacity="0">'
           f'<animate attributeName="x" dur="{DUR}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt(*cks)}" values="{";".join(str(v) for v in cxs)}"/>'
           f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt(0, FADE_END, 3.5, 3.8, 4.1, DRAW0)}" values="0;1;1;1;1;0"/></rect>')
# count: one text per value, each shown while it is current
n = len(order)
for k in range(n + 1):
    t_on = FADE_END if k == 0 else times[k - 1]
    t_off = times[k] if k < n else None
    if k < n:
        a = (f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" calcMode="discrete" '
             f'keyTimes="{kt(0, FADE_END, t_off)}" values="0;1;0"/>') if k == 0 else \
            (f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" calcMode="discrete" '
             f'keyTimes="{kt(0, t_on, t_off)}" values="0;1;0"/>')
        op = '0'
    else:
        a = (f'<animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" calcMode="discrete" '
             f'keyTimes="{kt(0, HOLD_END + 0.25, t_on)}" values="1;0;1"/>')
        op = '1'
    out.append(f'<text x="{px}" y="56" font-family="monospace" font-size="12" font-weight="700" fill="#e7e4dc" opacity="{op}">{k}<tspan font-size="9" font-weight="400"> airstrip{"" if k == 1 else "s"}</tspan>{a}</text>')
out.append(f'<text x="{px}" y="66" font-family="sans-serif" font-size="7" fill="#8b93a1">within {COR} NM of the route</text>')
gapnm = 99   # the app's own figure for this route and filters (see emergency-airstrips-route.py)
out.append(f'<g>{appear(GAP_T)}<text x="{px}" y="86" font-family="monospace" font-size="12" font-weight="700" fill="#e0705f">{gapnm} NM<tspan font-size="9" font-weight="400"> gap</tspan></text>'
           f'<text x="{px}" y="96" font-family="sans-serif" font-size="7" fill="#8b93a1">longest with no airstrip, in red</text></g>')
out.append('</svg>')
print('\n'.join(out))
