"""Animated 3-D card for Mexican Airstrips (Control Panel New group): SQA runway 16/34, left pattern at TPA, visual
approaches with 2 NM / 5 NM fixes, ridge behind. Perspective computed per frame in Python; SVG animates between frames."""
import math
W, H = 400, 104
N, DUR = 22, 16.0                   # frames per swing; seconds for a full there-and-back
ELEV_FT = 1240                       # rough field elevation used only to turn the app's MSL labels into heights
ft = lambda msl: (msl - ELEV_FT) / 3.281
HALF = 650.0                         # half the 1,300 m runway
NM = 1852.0
TPA = ft(2210)
RCAM, ELV, TY, FOC, ROW, AZ0, SW = 5200.0, 7.0, 1500.0, 300.0, 68.0, -10.0, 22.0
HORIZ = ROW - FOC * math.tan(math.radians(ELV))
def cam(az):
    R, el = RCAM, math.radians(ELV); T = (0.0, TY, 0.0)
    C = (T[0] + R * math.sin(az) * math.cos(el), T[1] - R * math.cos(az) * math.cos(el), T[2] + R * math.sin(el))
    f = [T[i] - C[i] for i in range(3)]; n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]
    r = [f[1], -f[0], 0.0]; n = math.hypot(r[0], r[1]); r = [v / n for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    def P(p):
        d = [p[i] - C[i] for i in range(3)]; zc = sum(d[i] * f[i] for i in range(3)); assert zc > 200, (p, zc)
        return (W / 2 + FOC * sum(d[i] * r[i] for i in range(3)) / zc, ROW - FOC * sum(d[i] * u[i] for i in range(3)) / zc)
    return P
# scene, world metres: x east, y north, z up; runway on the y axis, 34 end north (as in the app's 3-D view)
S, Nn = (0, -HALF, 0), (0, HALF, 0)
PW = 0.5 * NM                        # the app's pattern (site/index.html patterns()): downwinds PW either side of the centerline,
pattern = [(-PW, -HALF - PW, TPA), (PW, -HALF - PW, TPA), (PW, HALF + PW, TPA), (-PW, HALF + PW, TPA)]   # base turns PW past each end,
finals = [[(0, -HALF - PW, TPA), (0, -HALF, TPA)], [(0, HALF + PW, TPA), (0, HALF, TPA)]]              # finals on the centerline; all at TPA as in view3d.js
app34 = [(0, HALF, 0), (0, HALF + 2 * NM, ft(1890)), (0, HALF + 5 * NM, ft(2840))]   # drawn beyond the 34 label, as the app does
app16 = [(0, -HALF, 0), (0, -HALF - 1.2 * NM, ft(1890) * 0.6)]
ridge = [(x, 26000 + 3000 * math.sin(x / 5300.0), 700 + 420 * math.sin(x / 2900.0 + 1) + 260 * math.sin(x / 1100.0)) for x in range(-38000, 38001, 1900)]
labels = [('34 2NM 1,890′', app34[1], '#f5a623', 'L'), ('34 5NM 2,840′', app34[2], '#f5a623', 'R'), ('TPA 2,210′', (-PW, 0, TPA), '#e7e4dc', 'L')]
ends = [('16', S), ('34', Nn)]
eas = lambda t: 0.5 - 0.5 * math.cos(math.pi * t)
azs = [math.radians(AZ0 - SW / 2 + SW * eas(i / (N - 1))) for i in range(N)]
azs = azs + azs[-2:0:-1]                                     # there and back, seamless loop
frames = [cam(a) for a in azs]
fmt = lambda v: f'{v:.1f}'
def poly(pts, P, close=False):
    q = [P(p) for p in pts]; return 'M' + ' L'.join(f'{fmt(x)} {fmt(y)}' for x, y in q) + (' Z' if close else '')
def anim(attr, vals): return f'<animate attributeName="{attr}" dur="{DUR}s" repeatCount="indefinite" values="{";".join(vals)}"/>'
def path_el(pts, close=False, **a):
    vals = [poly(pts, P, close) for P in frames]
    at = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())
    return f'<path d="{vals[0]}" {at}>{anim("d", vals)}</path>'
def ground_poly(P):
    far = [P((x, 60000, 0)) for x in (-90000, 90000)]
    return f'M-20 {fmt(far[0][1])} L420 {fmt(far[1][1])} L420 110 L-20 110 Z'
out = [f'<svg class="app-preview preview-wide" viewBox="0 0 {W} {H}" role="img" aria-label="A remote airstrip in a slowly turning 3-D view: runway 16/34, the dashed traffic pattern at 2,210 feet, and visual approach paths with 2 and 5 NM fixes">',
       f'<rect width="{W}" height="{H}" fill="#0d1117"/>',
       '<defs><linearGradient id="mxaSky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#22324a"/></linearGradient></defs>',
       f'<rect width="{W}" height="{HORIZ:.1f}" fill="url(#mxaSky)"/>',
       f'<rect y="{HORIZ:.1f}" width="{W}" height="{H - HORIZ:.1f}" fill="#2a2a1f"/>']
ridge_pts = ridge + [(38000, 26000, 0), (-38000, 26000, 0)]
out.append(path_el(ridge_pts, True, fill='#3a3a28', stroke='#565640', stroke_width='0.8'))
out.append(path_el([(-160, -HALF - 120, 0), (160, -HALF - 120, 0), (160, HALF + 120, 0), (-160, HALF + 120, 0)], True, fill='#caa47f', fill_opacity='0.18', stroke='#caa47f', stroke_width='0.6'))   # airfield box
out.append(path_el(pattern, True, fill='none', stroke='#4fc3f7', stroke_width='1.6', stroke_dasharray='5 4'))
for leg in finals: out.append(path_el(leg, False, fill='none', stroke='#4fc3f7', stroke_width='1.6', stroke_dasharray='5 4'))
out.append(path_el(app16, False, fill='none', stroke='#f5a623', stroke_width='2', stroke_dasharray='7 4'))
out.append(path_el(app34, False, fill='none', stroke='#f5a623', stroke_width='1.6', stroke_dasharray='6 4'))
out.append(path_el([S, Nn], False, fill='none', stroke='#ffffff', stroke_width='2.2', stroke_linecap='round'))
def tag(text, pt, color, w, side):
    off = 4 if side == 'R' else -4 - w
    xs = [fmt(P(pt)[0] + off) for P in frames]; ys = [fmt(P(pt)[1] - 13) for P in frames]
    tx = [fmt(P(pt)[0] + off + 3) for P in frames]; ty = [fmt(P(pt)[1] - 4.5) for P in frames]
    return (f'<rect x="{xs[0]}" y="{ys[0]}" width="{w}" height="12" rx="2" fill="#10141a" fill-opacity="0.9">{anim("x", xs)}{anim("y", ys)}</rect>'
            f'<text x="{tx[0]}" y="{ty[0]}" font-family="IBM Plex Mono, monospace" font-size="8" font-weight="600" fill="{color}">{anim("x", tx)}{anim("y", ty)}{text}</text>')
for text, pt, color, side in labels: out.append(tag(text, pt, color, round(6 + 4.85 * len(text), 1), side))
for text, pt in ends:
    xs = [fmt(P(pt)[0] - 7) for P in frames]; ys = [fmt(P(pt)[1] - 6) for P in frames]
    tx = [fmt(P(pt)[0]) for P in frames]; ty = [fmt(P(pt)[1] + 3) for P in frames]
    out.append(f'<rect x="{xs[0]}" y="{ys[0]}" width="14" height="11" fill="#10141a" stroke="#e7e4dc" stroke-width="0.5">{anim("x", xs)}{anim("y", ys)}</rect>'
               f'<text x="{tx[0]}" y="{ty[0]}" font-family="IBM Plex Mono, monospace" font-size="7.5" fill="#e7e4dc" text-anchor="middle">{anim("x", tx)}{anim("y", ty)}{text}</text>')
out.append('</svg>')
svg = '\n'.join(out); open('/home/claude/card/card3d.svg', 'w').write(svg); print(len(svg), 'bytes')
