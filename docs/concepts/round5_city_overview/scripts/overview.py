"""Round 5: the whole city, zoomed far out, in the chosen style (Cv2 facets + E cel shading).

One seeded city (irregular street grid, organic Voronoi districts with a mixed border band, the
REBEL_CELL fist roads, four HQ landmarks on plazas) rendered three ways:
  city_overview_night.png, city_overview_day.png, city_overview_map.png (+ hq_crops.png)
Usage: python overview.py            (all)      python overview.py day|night   (one)
"""
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter
import lowpoly
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, tri, line2, gradient, smog, rain,
                     finalize, NEON, layer, composite)
import city
from city import Cam, B, bil3, THEMES, FAM, NIGHT_FAM, clutter, LIGHT, v_norm, v_sub, v_cross, v_dot
import toon
from toon import ToonPainter, ink_line, ink_poly, hull, paint_texture
import kit  # adds mer/sol/hal/orb/metal families to city.FAM
import landmarks
import helix

OUT = os.path.dirname(HERE)
FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(OUT))), 'assets', 'fonts')
MARKER = os.path.join(FONTS, 'PermanentMarker-Regular.ttf')
BAHN = 'C:/Windows/Fonts/bahnschrift.ttf'

LXW, LYW = 220.0, 104.0      # world size (units)
SLAB = 3.5


def ramp_of(c):
    c = hexc(c) if isinstance(c, str) else c
    k, w = (0, 0, 0), (255, 255, 255)
    return [mix(c, k, 0.82), mix(c, k, 0.62), mix(c, k, 0.38), mix(c, k, 0.16), c, mix(c, w, 0.3), mix(c, w, 0.6)]


ACC_HEX = {'sol': '#3DFF8B', 'mer': '#FF8C1A', 'hal': '#8C7BFF', 'orb': '#7FA8FF', 'reb': '#E8141E', 'spr': '#E8A23A'}
ACC = {k: ramp_of(v) for k, v in ACC_HEX.items()}
DNAME = {'sol': 'SOLACE BIOSYSTEMS', 'mer': 'MERIDIAN FREIGHT', 'hal': 'HALCYON CIVIC', 'orb': 'ORBITAL COMMONS',
         'reb': 'REBEL_CELL', 'spr': 'THE SPRAWL'}

# district families: concrete pulled toward the accent
for k, c in ACC_HEX.items():
    FAM['d_' + k] = [mix(s, hexc(c), 0.3) for s in FAM['concrete']]
for k in list(FAM):
    if k not in NIGHT_FAM:
        NIGHT_FAM[k] = [mix(s, hexc('#04050c'), 0.35) for s in FAM[k]]
FAMS = {'sol': ['d_sol', 'concrete', 'corp', 'd_sol', 'oily'], 'mer': ['d_mer', 'rust', 'brick', 'd_mer', 'concrete'],
        'hal': ['d_hal', 'concrete', 'corp', 'd_hal'], 'orb': ['d_orb', 'corp', 'soot', 'd_orb'],
        'reb': ['brick', 'soot', 'rust', 'd_reb', 'concrete'], 'spr': ['soot', 'rust', 'oily', 'concrete', 'brick']}

SEEDS = [('orb', 34, 22), ('sol', 104, 17), ('hal', 180, 28), ('reb', 50, 76), ('mer', 166, 80),
         ('spr', 110, 54), ('spr', 6, 100), ('spr', 216, 4)]
HQ = {'sol': (104, 18), 'mer': (168, 82), 'hal': (182, 30), 'orb': (34, 24)}
HQ_NAME = {'sol': 'THE DOUBLE HELIX', 'mer': 'FREIGHT ZIGGURAT', 'hal': 'CIVIC PYRAMID', 'orb': 'ORBITAL TETHER'}
PLAZA_R = 13.0
OURS = (86.0, 64.0)
FIST_C = (50.0, 72.0)


# ------------------------------------------------------------------ districts
_rng = random.Random(5150)
_PH = [(_rng.uniform(0, 6.28), _rng.uniform(0.03, 0.07)) for _ in range(6)]


def warp(x, y):
    wx = x + 7 * math.sin(y * _PH[0][1] + _PH[0][0]) + 4 * math.sin((x + y) * _PH[1][1] + _PH[1][0])
    wy = y + 7 * math.sin(x * _PH[2][1] + _PH[2][0]) + 4 * math.sin((x - y) * _PH[3][1] + _PH[3][0])
    return wx, wy


def district_info(x, y):
    """(primary, secondary, margin): margin small = in the mixed border band."""
    wx, wy = warp(x, y)
    ds = []
    for k, sx, sy in SEEDS:
        dd = math.hypot((wx - sx) * 0.85, wy - sy)
        if k == 'spr':
            dd *= 1.35
        ds.append((dd, k))
    ds.sort()
    first = ds[0]
    sec = next(t for t in ds[1:] if t[1] != first[1])
    return first[1], sec[1], sec[0] - first[0]


def district_at(x, y, rng=None, band=4.0):
    p, s, m = district_info(x, y)
    if rng is not None and m < band and rng.random() < 0.5 * (1 - m / band):
        return s
    return p


# ------------------------------------------------------------------ fist roads
def fist_segments():
    segs = []
    fx, fy = FIST_C

    def P(x, y):
        return (fx + x, fy + y)
    poly = []
    for i in range(4):
        xa, xb = -12 + 6 * i, -6 + 6 * i
        poly += [P(xa, -8), P(xa + 1.2, -11.5), P(xb - 1.2, -11.5)]
    poly += [P(12, -8), P(12, 6), P(9, 9.5), P(6, 9.5)]
    poly += [P(6, 21), P(-6, 21), P(-6, 9.5), P(-9, 9.5), P(-12, 6), P(-12, -8)]
    for a, b in zip(poly, poly[1:]):
        segs.append((a, b))
    for x in (-6, 0, 6):
        segs.append((P(x, -8), P(x, -2.5)))
    segs.append((P(-12, -2.5), P(12, -2.5)))
    segs += [(P(-12, 3), P(3, 3)), (P(3, 3), P(6.5, -0.5))]
    return segs


FIST = fist_segments()
FIST_BOX = (FIST_C[0] - 17, FIST_C[1] - 16, FIST_C[0] + 17, FIST_C[1] + 25)


def seg_dist(px, py, a, b):
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def fist_dist(px, py):
    return min(seg_dist(px, py, a, b) for a, b in FIST)


def rect_fist_dist(x0, y0, x1, y1):
    pts = [(x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2), ((x0 + x1) / 2, y0),
           ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2), (x1, (y0 + y1) / 2)]
    return min(fist_dist(*p) for p in pts)


# ------------------------------------------------------------------ street grid
def spans(total, lo, hi, every, seed):
    rng = random.Random(seed)
    out, streets, x, k = [], [], 0.0, 0
    while x < total - lo:
        w = rng.uniform(lo, hi)
        if x + w > total:
            w = total - x
        out.append((x, x + w))
        x += w
        k += 1
        sw = 3.4 if k % every == 0 else 1.5
        streets.append((x, x + sw, sw > 2))
        x += sw
    return out, streets


XS, XST = spans(LXW, 4.8, 7.6, 4, 'cols')
YS, YST = spans(LYW, 4.2, 6.6, 3, 'rows')


def parcels_for(rng, x0, y0, x1, y1):
    w, d = x1 - x0, y1 - y0
    nx = max(1, int(w / rng.uniform(2.4, 3.6)))
    ny = max(1, int(d / rng.uniform(2.2, 3.4)))
    xs = [x0 + w * i / nx for i in range(nx + 1)]
    ys = [y0 + d * j / ny for j in range(ny + 1)]
    return [(xs[i], ys[j], xs[i + 1], ys[j + 1]) for i in range(nx) for j in range(ny)]


def buildings_for(rng, dk, a0, b0, a1, b1, bid, near_fist=False):
    """Primitive list for one parcel, by district."""
    ins = 0.22
    x0, y0, x1, y1 = a0 + ins, b0 + ins, a1 - ins, b1 - ins
    w, d = x1 - x0, y1 - y0
    fam = rng.choice(FAMS[dk])
    prims = []

    def box(xa, ya, xb, yb, za, zb, f=fam, taper=0.0, signs=0, win=True, k=0):
        p = B(xa, ya, xb, yb, za, zb, f, (bid, k), win=dk if win else None, taper=taper, signs=signs,
              graffiti=(dk in ('reb', 'spr') and zb < 5 and rng.random() < 0.3))
        p['pat'] = dk
        prims.append(p)
        return p
    sg = lambda h: rng.choice([0, 0, 1, 1, 2]) if h > 2.4 else 0
    if dk == 'orb':
        if rng.random() < 0.55:
            h = rng.uniform(12, 24)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            box(x0, y0, x1, y1, 0, 1.6, k=0)
            r = min(w, d) * 0.3
            box(cx - r, cy - r, cx + r, cy + r, 1.6, h, taper=0.45, k=1)
            prims.append(dict(k='pyr', x0=cx - r * 0.5, y0=cy - r * 0.5, x1=cx + r * 0.5, y1=cy + r * 0.5, z0=h,
                              z1=h + rng.uniform(1.5, 3.5), fam=fam, bid=(bid, 2)))
        else:
            h = rng.uniform(4, 9)
            box(x0, y0, x1, y1, 0, h, signs=sg(h))
            clutter(rng, prims, x0, y0, x1, y1, h, (bid, 9))
    elif dk == 'sol':
        if rng.random() < 0.6:
            r = min(w, d) * 0.48
            h = rng.uniform(5, 15)
            prims.append(dict(k='cyl', cx=(x0 + x1) / 2, cy=(y0 + y1) / 2, r=r, z0=0, z1=h, fam=fam, bid=bid, pat='sol'))
            if rng.random() < 0.4:
                prims.append(dict(k='cyl', cx=(x0 + x1) / 2, cy=(y0 + y1) / 2, r=r * 0.62, z0=h, z1=h + rng.uniform(2, 5),
                                  fam=fam, bid=(bid, 'c2'), pat='sol'))
        else:
            h = rng.uniform(4, 13)
            box(x0, y0, x1, y1, 0, h, signs=sg(h))
            clutter(rng, prims, x0, y0, x1, y1, h, (bid, 9))
    elif dk == 'hal':
        h1 = rng.uniform(3, 6)
        box(x0, y0, x1, y1, 0, h1, signs=sg(h1), k=0)
        if rng.random() < 0.75:
            h2 = h1 + rng.uniform(2.5, 5)
            box(x0 + w * 0.15, y0 + d * 0.15, x1 - w * 0.15, y1 - d * 0.15, h1, h2, k=1)
            if rng.random() < 0.5:
                h3 = h2 + rng.uniform(3, 6)
                box(x0 + w * 0.3, y0 + d * 0.3, x1 - w * 0.3, y1 - d * 0.3, h2, h3, taper=0.3, k=2)
                prims[-1]['ring'] = True
            else:
                prims[-1]['ring'] = True
    elif dk == 'mer':
        if rng.random() < 0.3 and w > 1.5:
            # container yard
            cols = ['mer', 'rust', 'oily', 'sol', 'mer', 'hal', 'd_mer']
            n = 0
            yy = y0
            while yy + 0.9 < y1:
                xx = x0
                while xx + 2.0 < x1:
                    for lvl in range(rng.choice([1, 1, 2])):
                        p = B(xx, yy, xx + 1.9, yy + 0.8, lvl * 0.8, lvl * 0.8 + 0.8, rng.choice(cols), (bid, 'ct', n),
                              grime=False)
                        p['pat'] = 'ctr'
                        prims.append(p)
                        n += 1
                    xx += 2.1
                yy += 1.0
        else:
            h = rng.uniform(1.4, 3.6)
            box(x0, y0, x1, y1, 0, h, signs=sg(h), k=0)
            if rng.random() < 0.35:
                box(x0 + w * 0.2, y0 + d * 0.1, x1 - w * 0.1, y1 - d * 0.3, h, h + rng.uniform(1.2, 2.6), k=1)
    else:   # reb / spr generic mix
        lo, hi = (0.8, 1.6) if near_fist else ((1.4, 6) if dk == 'reb' else (2.2, 10))
        h = rng.uniform(lo, hi)
        box(x0, y0, x1, y1, 0, h, signs=sg(h), k=0)
        if h > 5 and rng.random() < 0.45:
            box(x0 + w * 0.15, y0 + d * 0.15, x1 - w * 0.2, y1 - d * 0.2, h, h + rng.uniform(2, 5),
                f=rng.choice(['corp', 'concrete', 'oily']), k=1)
            h = prims[-1]['z1']
        if not near_fist:
            clutter(rng, prims, x0, y0, x1, y1, h, (bid, 9))
    return prims


def build_world():
    rng = random.Random(2077)
    items = []
    pads = []           # (x0,y0,x1,y1, district) lot pads
    bid = 0
    fx0, fy0, fx1, fy1 = FIST_BOX
    fcols = [i for i, (a, b) in enumerate(XS) if b > fx0 and a < fx1]
    frows = [j for j, (a, b) in enumerate(YS) if b > fy0 and a < fy1]
    fregion = (XS[fcols[0]][0], YS[frows[0]][0], XS[fcols[-1]][1], YS[frows[-1]][1])
    for i, (bx0, bx1) in enumerate(XS):
        for j, (by0, by1) in enumerate(YS):
            if i in fcols and j in frows:
                continue
            pads.append((bx0, by0, bx1, by1, district_at((bx0 + bx1) / 2, (by0 + by1) / 2)))
            for (a0, b0, a1, b1) in parcels_for(rng, bx0, by0, bx1, by1):
                cx, cy = (a0 + a1) / 2, (b0 + b1) / 2
                if any(math.hypot(cx - hx, cy - hy) < PLAZA_R + 1.5 for hx, hy in HQ.values()):
                    continue
                if math.hypot(cx - OURS[0], cy - OURS[1]) < 2.2:
                    continue
                dk = district_at(cx, cy, rng)
                prims = buildings_for(rng, dk, a0, b0, a1, b1, bid)
                bid += 1
                if prims:
                    items.append(dict(box=(a0, b0, a1, b1), prims=prims))
    # fist region: fine cells, roads = the fist outline only
    rx0, ry0, rx1, ry1 = fregion
    pads.append((rx0, ry0, rx1, ry1, 'fist'))
    cs = 2.3
    nx, ny = int((rx1 - rx0) / cs), int((ry1 - ry0) / cs)
    for i in range(nx):
        for j in range(ny):
            a0, b0 = rx0 + i * (rx1 - rx0) / nx, ry0 + j * (ry1 - ry0) / ny
            a1, b1 = a0 + (rx1 - rx0) / nx, b0 + (ry1 - ry0) / ny
            dist = rect_fist_dist(a0, b0, a1, b1)
            if dist < 1.6:
                continue
            dk = district_at((a0 + a1) / 2, (b0 + b1) / 2)
            if dk == 'spr':
                dk = 'reb'
            prims = buildings_for(rng, dk, a0, b0, a1, b1, bid, near_fist=dist < 5.5)
            bid += 1
            items.append(dict(box=(a0, b0, a1, b1), prims=prims))
    # the Cell's own small HQ
    ox, oy = OURS
    p = B(ox - 1.4, oy - 1.4, ox + 1.4, oy + 1.4, 0, 3.0, 'oily', 'ours', win='cell', signs=1)
    p['pat'] = 'cell'
    items.append(dict(box=(ox - 1.4, oy - 1.4, ox + 1.4, oy + 1.4), prims=[p, dict(k='beacon', x=ox, y=oy, z=3.4, col='cyan')]))
    # traffic lights at avenue crossings, lamps along avenues
    av_x = [(a + b) / 2 for a, b, big in XST if big and b < LXW]
    av_y = [(a + b) / 2 for a, b, big in YST if big and b < LYW]
    for x in av_x:
        for y in av_y:
            if any(math.hypot(x - hx, y - hy) < PLAZA_R for hx, hy in HQ.values()):
                continue
            items.append(dict(box=(x - 1.9, y - 1.9, x - 1.7, y - 1.7), prims=[dict(k='tlight', x=x - 1.8, y=y + 1.8, z=0)]))
    lamps = []
    for x in av_x:
        y = 2.0
        while y < LYW - 2:
            lamps.append((x + 1.6, y))
            y += 7.5
    for y in av_y:
        x = 3.0
        while x < LXW - 2:
            lamps.append((x, y + 1.6))
            x += 8.0
    lamps = [l for l in lamps if not (FIST_BOX[0] < l[0] < FIST_BOX[2] and FIST_BOX[1] < l[1] < FIST_BOX[3])]
    for l in lamps:
        items.append(dict(box=(l[0] - 0.1, l[1] - 0.1, l[0] + 0.1, l[1] + 0.1), prims=[dict(k='lamp', x=l[0], y=l[1])]))
    # plaza lamps + HQ landmark items
    for dk, (hx, hy) in HQ.items():
        for k in range(10):
            a = 2 * math.pi * k / 10
            lx, ly = hx + (PLAZA_R - 1.2) * math.cos(a), hy + (PLAZA_R - 1.2) * math.sin(a)
            items.append(dict(box=(lx - 0.1, ly - 0.1, lx + 0.1, ly + 0.1), prims=[dict(k='lamp', x=lx, y=ly, plaza=dk)]))
        items.append(dict(box=(hx - 1, hy - 1, hx + 1, hy + 1), prims=[dict(k='hq', dk=dk, x=hx, y=hy)]))
        sx, sy = hx + PLAZA_R * 0.55, hy + PLAZA_R * 0.82
        items.append(dict(box=(sx - 0.2, sy - 0.2, sx + 0.2, sy + 0.2),
                          prims=[dict(k='namesign', x=sx, y=sy, dk=dk)]))
    # beacons on the tallest roofs
    tall = []
    for it in items:
        for p in it['prims']:
            if p['k'] == 'box' and p['z1'] > 11:
                tall.append(p)
    tall.sort(key=lambda p: (-p['z1'], str(p['bid'])))
    for n, p in enumerate(tall[:40]):
        items.append(dict(box=(p['x0'], p['y0'], p['x1'], p['y1']),
                          prims=[dict(k='beacon', x=(p['x0'] + p['x1']) / 2, y=(p['y0'] + p['y1']) / 2, z=p['z1'] + 0.2,
                                      col='red')], after=True))
    return items, pads, lamps, fregion


# ------------------------------------------------------------------ camera
def make_cam():
    az, el = 13.0, 52.0
    c = Cam(az, el, 1.0, 0, 0)
    pts = [c.p(x, y, 0) for x in (0, LXW) for y in (0, LYW)] + [c.p(LXW, LYW, -SLAB), c.p(0, LYW, -SLAB)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    S = min(0.97 * W / (max(xs) - min(xs)), 0.84 * H / (max(ys) - min(ys)))
    ox = W / 2 - (max(xs) + min(xs)) / 2 * S
    oy = H * 0.975 - max(ys) * S
    return Cam(az, el, S, ox, oy)


class SubCam:
    def __init__(self, cam, ox, oy, k):
        self.c, self.ox, self.oy, self.k = cam, ox, oy, k
        self.d, self.ca, self.sa, self.ce, self.se, self.S = cam.d, cam.ca, cam.sa, cam.ce, cam.se, cam.S * k

    def p(self, x, y, z):
        return self.c.p(self.ox + x * self.k, self.oy + y * self.k, z * self.k)

    def depth(self, x, y):
        return self.c.depth(self.ox + x * self.k, self.oy + y * self.k)


# ------------------------------------------------------------------ painter
class OverviewPainter(ToonPainter):
    def __init__(self, img, cam, theme):
        super().__init__(img, cam, theme)
        self.hq_tops = {}

    def acc(self, dk, t):
        st = ACC.get(dk, NEON['cyan'] if dk == 'cell' else ACC['spr'])
        c = ramp(st, t)
        return c if self.night else mix(c, (90, 86, 74), 0.35)

    def facade_colfac(self, stops, bid, name, win, nv, grime):
        night = self.night

        def fac(base):
            def f(u, v, i, j, k, rc):
                t = base + 0.07 * (v - 0.5) + rc.uniform(-0.035, 0.035)
                if grime and hsh(bid, ord(name), i, 91) < 0.3 and v < 0.6:
                    t -= 0.06
                if win and j % 2 == 1 and j < nv - 1:
                    hv = hsh(bid, ord(name), i, j)
                    if night and hv < 0.3:
                        key = win if hsh(bid, i, j, 3) < 0.55 else 'spr'
                        st = ACC.get(key, NEON['cyan'] if key == 'cell' else ACC['spr'])
                        return ramp(st, 0.45 + 0.35 * rc.random())
                    if hv < 0.8:
                        return ramp(stops, t - 0.14)
                return ramp(stops, t)
            return f
        return fac

    def box(self, p):
        super().box(p)
        pat = p.get('pat')
        if pat:
            self.pattern(p, pat)

    def pattern(self, p, pat):
        cam, d = self.cam, self.d
        x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
        h = z1 - z0
        rng = random.Random(str(('pat', p['bid'])))
        front = lambda u, z: cam.p(x0 + (x1 - x0) * u, y1 + 0.02, z)
        side = lambda u, z: cam.p(x1 + 0.02, y1 - (y1 - y0) * u, z)
        night = self.night
        if pat == 'ctr':
            a, b = front(0.0, z0 + h * 0.5), front(1.0, z0 + h * 0.5)
            line2(d, a, b, 1.6, self.acc('mer', 0.75) if p['fam'] != 'mer' else (240, 232, 210))
            return
        if h < 0.9:
            return
        if pat == 'sol':
            for s in (0, 1):
                for t in range(int(h / 0.6)):
                    z = z0 + 0.4 + t * 0.6
                    if z > z1 - 0.3:
                        break
                    u = 0.5 + 0.32 * math.sin(t * 0.9 + s * math.pi)
                    x, y = front(u, z)
                    r = 1.6 if math.cos(t * 0.9 + s * math.pi) > 0 else 1.0
                    tri(d, [(x - r, y + r), (x + r, y + r), (x, y - r)], self.acc('sol', 0.6 if r > 1.2 else 0.3))
        elif pat == 'mer':
            z = z0 + h * 0.62
            for f in (front, side):
                a, b = f(0, z), f(1, z)
                line2(d, a, b, 3.2, self.acc('mer', 0.55))
                line2(d, (a[0], a[1] + 1.6), (b[0], b[1] + 1.6), 1.0, (236, 226, 204) if not night else self.acc('mer', 0.85))
        elif pat == 'hal':
            if p.get('ring') and hsh(p['bid'], 5) < 0.22:
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
                r = max(x1 - x0, y1 - y0) * 0.6
                pts = [cam.p(cx + r * math.cos(a), cy + r * math.sin(a), z1 + 1.0) for a in
                       [2 * math.pi * k / 20 for k in range(20)]]
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    line2(d, a, b, 3.4, (12, 10, 18))
                for a, b in zip(pts, pts[1:] + pts[:1]):
                    line2(d, a, b, 1.8, self.acc('hal', 0.7))
        elif pat == 'orb':
            for f, wdt in ((front, x1 - x0), (side, y1 - y0)):
                nu = max(1, int(wdt / 0.8))
                for i in range(nu):
                    for t in range(int(h / 1.2)):
                        if (i + t) % 2:
                            continue
                        x, y = f((i + 0.5) / nu, z0 + 0.6 + t * 1.2)
                        tri(d, [(x - 1.2, y), (x, y - 1.6), (x + 1.2, y)], self.acc('orb', 0.75))
        elif pat == 'reb':
            for k in range(2):
                z = z0 + h * rng.uniform(0.2, 0.8)
                off = rng.uniform(-0.15, 0.15)
                a, b = front(0.05 + off, z), front(0.95 + off, z)
                line2(d, a, b, 2.2, self.acc('reb', 0.6 if night else 0.45))
        if night and pat in ('sol', 'mer', 'hal', 'orb', 'reb', 'cell') and h > 2.5 and hsh(p['bid'], 77) < 0.3:
            # neon roof trim
            tx = (x1 - x0) * p['taper'] / 2
            ty = (y1 - y0) * p['taper'] / 2
            a, b, c = cam.p(x0 + tx, y1 - ty, z1), cam.p(x1 - tx, y1 - ty, z1), cam.p(x1 - tx, y0 + ty, z1)
            line2(d, a, b, 2.0, self.acc(pat, 0.72))
            line2(d, b, c, 2.0, self.acc(pat, 0.62))

    def cyl(self, p):
        cam, d = self.cam, self.d
        stops = self.th['fam'][p['fam']]
        cx, cy, r, z0, z1 = p['cx'], p['cy'], p['r'], p['z0'], p['z1']
        n = 12
        center = (cx, cy, (z0 + z1) / 2)
        ring = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
        nv = max(2, int((z1 - z0) / 1.6) * 2)
        for k in range(n):
            a, b = ring[k], ring[(k + 1) % n]
            q = [(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)]
            self.face(q, stops, (p['bid'], 'cy', k), 1, nv, center=center,
                      colfac=self.facade_colfac(stops, p['bid'], 'c', 'sol', nv, True))
        for k in range(n):
            a, b = ring[k], ring[(k + 1) % n]
            q = [(cx, cy, z1), (a[0], a[1], z1), (b[0], b[1], z1), (cx, cy, z1)]
            self.face(q, stops, (p['bid'], 'ct', k), 1, 1, normal=(0, 0, 1))
        top = [cam.p(x, y, z1) for x, y in ring]
        bot = [cam.p(x, y, z0) for x, y in ring]
        ink_poly(d, hull(top + bot), 3.2 if z1 - z0 > 1.2 else 2.0, (p['bid'], 'csil'))
        vis = [k for k in range(n) if math.sin(2 * math.pi * (k + 0.5) / n + math.radians(24)) > -0.2]
        for k in range(n):
            ink_line(d, top[k], top[(k + 1) % n], 1.4, (p['bid'], 'ctop', k))
        # helix dots on the visible side
        night = self.night
        h = z1 - z0
        for s in (0, 1):
            for t in range(int(h / 0.6)):
                z = z0 + 0.4 + t * 0.6
                ang = math.radians(60) + 0.9 * math.sin(t * 0.8 + s * math.pi)
                x, y = cam.p(cx + r * 1.02 * math.cos(ang), cy + r * 1.02 * math.sin(ang), z)
                big = math.cos(t * 0.8 + s * math.pi) > 0
                rr = 1.6 if big else 1.0
                tri(d, [(x - rr, y + rr), (x + rr, y + rr), (x, y - rr)], self.acc('sol', 0.62 if big else 0.32))
        a, b = top[int(n * 0.12)], top[int(n * 0.38)]
        line2(d, (a[0], a[1] + 2.5), (b[0], b[1] + 2.5), 1.6, toon.BEVEL)

    def item(self, it):
        for p in it['prims']:
            k = p['k']
            if k == 'cyl':
                self.cyl(p)
            elif k == 'lamp':
                self.lamp(p)
            elif k == 'tlight':
                self.tlight(p)
            elif k == 'beacon':
                self.beacon(p)
            elif k == 'hq':
                self.hq(p)
            elif k == 'namesign':
                self.namesign(p)
            else:
                super().item(dict(prims=[p]))

    def lamp(self, p):
        cam, d = self.cam, self.d
        x, y = p['x'], p['y']
        hgt = 2.2 if p.get('plaza') else 1.8
        a, b = cam.p(x, y, 0), cam.p(x, y, hgt)
        line2(d, a, b, 2.4, (14, 12, 16))
        line2(d, b, cam.p(x - 0.4, y, hgt), 2.0, (14, 12, 16))
        hx, hy = cam.p(x - 0.4, y, hgt - 0.05)
        col = ramp(NEON['sodium'], 0.85 if self.night else 0.5) if not p.get('plaza') else self.acc(p['plaza'], 0.8)
        tri(d, [(hx - 3, hy - 1), (hx + 3, hy - 1), (hx, hy + 3)], col)

    def tlight(self, p):
        cam, d = self.cam, self.d
        x, y = p['x'], p['y']
        a, b = cam.p(x, y, 0), cam.p(x, y, 2.1)
        line2(d, a, b, 2.2, (14, 12, 16))
        bx, by = b
        line2(d, (bx, by - 1), (bx, by + 13), 6.5, (14, 12, 16))
        for k, (col, on) in enumerate(((NEON['red'], hsh(x, y, 1) < 0.5), (NEON['amber'], False),
                                       (NEON['lime'], hsh(x, y, 1) >= 0.5))):
            c = ramp(col, 0.85 if on else 0.3)
            yy = by + 1 + k * 4.2
            tri(d, [(bx - 2, yy), (bx + 2, yy), (bx, yy + 3)], c)

    def beacon(self, p):
        sx, sy = self.cam.p(p['x'], p['y'], p['z'])
        st = NEON['red'] if p['col'] == 'red' else NEON['cyan']
        for k in range(6):
            a0 = 2 * math.pi * k / 6
            r = 7 if k % 2 == 0 else 4
            tri(self.d, [(sx, sy), (sx + r * math.cos(a0), sy + r * 0.8 * math.sin(a0)),
                         (sx + 4 * math.cos(a0 + 1.05), sy + 3 * math.sin(a0 + 1.05))],
                ramp(st, 0.85 if self.night else 0.55))

    def namesign(self, p):
        x, y, dk = p['x'], p['y'], p['dk']
        st = ACC[dk]
        self.box(B(x - 1.6, y - 0.15, x + 1.6, y + 0.15, 0.5, 1.6, 'soot', ('ns', dk), grime=False))
        q = [(x - 1.5, y + 0.17, 0.6), (x + 1.5, y + 0.17, 0.6), (x + 1.5, y + 0.17, 1.5), (x - 1.5, y + 0.17, 1.5)]
        cam = self.cam
        facet(self.d, lambda u, v: cam.p(*bil3(q, u, v)), 4, 1,
              lambda u, v, i, j, k, rc: ramp(st, (0.62 if self.night else 0.45) + rc.uniform(-0.06, 0.06)), ('nsf', dk), 0.2)

    def hq(self, p):
        dk, hx, hy = p['dk'], p['x'], p['y']
        if dk == 'sol':
            helix.CX, helix.CY = hx, hy
            helix.draw_hq(self)
            self.hq_tops[dk] = (self.hq_top[0], self.hq_top[1])
            return
        cam0 = self.cam
        self.cam = SubCam(cam0, hx, hy, 1.45)
        fn = {'mer': landmarks.ziggurat, 'hal': landmarks.pyramid, 'orb': landmarks.tether}[dk]
        fn(self)
        top = {'mer': 13.2, 'hal': 12.0, 'orb': 19.5}[dk]
        self.hq_tops[dk] = self.cam.p(0, 0, top)
        self.cam = cam0

    # helix needs oprism (from r2_city_wide_helix/wide.py DistrictPainter)
    def oprism(self, c, ang, L, D, z0, z1, stops, seed, colfac=None, ink=2.4, strip=None, nu=2, nv=2):
        cam = self.cam
        ca, sa = math.cos(ang), math.sin(ang)
        r, t = (ca, sa), (-sa, ca)

        def P(a, b, z):
            return (c[0] + r[0] * a + t[0] * b, c[1] + r[1] * a + t[1] * b, z)
        corners = [(-D / 2, -L / 2), (D / 2, -L / 2), (D / 2, L / 2), (-D / 2, L / 2)]
        center = (c[0], c[1], (z0 + z1) / 2)
        for k in range(4):
            a, b = corners[k], corners[(k + 1) % 4]
            q = [P(a[0], a[1], z0), P(b[0], b[1], z0), P(b[0], b[1], z1), P(a[0], a[1], z1)]
            self.face(q, stops, (seed, k), nu, nv, center=center, colfac=colfac)
        top = [P(*corners[k], z1) for k in range(4)]
        self.face(top, stops, (seed, 't'), 2, 2, center=center, gv=-0.1)
        pts = [cam.p(*P(a, b, z)) for a, b in corners for z in (z0, z1)]
        ink_poly(self.d, hull(pts), ink, (seed, 'sil'))


# ------------------------------------------------------------------ ground
def ground(cp, pads, lamps, fregion):
    cam, d, th, night = cp.cam, cp.d, cp.th, cp.night
    # slab sides
    q = [(0, LYW, -SLAB), (LXW, LYW, -SLAB), (LXW, LYW, 0), (0, LYW, 0)]
    cp.face(q, th['earth'], 'slab_f', 40, 2, normal=(0, 1, 0))
    q = [(LXW, LYW, -SLAB), (LXW, 0, -SLAB), (LXW, 0, 0), (LXW, LYW, 0)]
    cp.face(q, th['earth'], 'slab_s', 20, 2, normal=(1, 0, 0))

    def street(u, v, i, j, k, rc):
        t = 0.4 + 0.15 * (1 - v) + rc.uniform(-0.06, 0.06)
        if rc.random() < 0.08:
            t += 0.25
        return ramp(th['street'], t)
    q = [(0, LYW, 0), (LXW, LYW, 0), (LXW, 0, 0), (0, 0, 0)]
    facet(d, lambda u, v: cam.p(*bil3(q, u, v)), 120, 56, street, 'street', 0.35)
    for (x0, y0, x1, y1, dk) in pads:
        q = [(x0, y1, 0.02), (x1, y1, 0.02), (x1, y0, 0.02), (x0, y0, 0.02)]
        cp.face(q, th['lot'], ('pad', x0, y0), 2, 1, normal=(0, 0, 1))
        ink_poly(d, [cam.p(*c) for c in q], 1.1, ('padink', x0, y0))
    # avenue lane dashes
    for (a, b, big) in XST:
        if big and b < LXW:
            x = (a + b) / 2
            y = 0
            while y < LYW:
                line2(d, cam.p(x, y, 0.03), cam.p(x, y + 1.2, 0.03), 1.4, ramp(NEON['sodium'], 0.5 if night else 0.35))
                y += 3
    for (a, b, big) in YST:
        if big and b < LYW:
            y = (a + b) / 2
            x = 0
            while x < LXW:
                line2(d, cam.p(x, y, 0.03), cam.p(x + 1.2, y, 0.03), 1.4, ramp(NEON['sodium'], 0.5 if night else 0.35))
                x += 3
    # plazas
    for dk, (hx, hy) in HQ.items():
        st = FAM['concrete'] if not night else NIGHT_FAM['concrete']
        facet(d, lambda u, v, hx=hx, hy=hy: cam.p(hx + PLAZA_R * v * math.cos(u * 6.2832), hy + PLAZA_R * v * math.sin(u * 6.2832), 0.04),
              20, 4, lambda u, v, i, j, k, rc: toon.tint(ramp(st, toon.BANDS[2] - 0.05 * (i % 2) + rc.uniform(-0.03, 0.03)), 2),
              ('plz', dk), 0.2, wrap_u=True)
        ring = [cam.p(hx + PLAZA_R * math.cos(a), hy + PLAZA_R * math.sin(a), 0.04) for a in [k * 6.2832 / 32 for k in range(32)]]
        for a, b in zip(ring, ring[1:] + ring[:1]):
            line2(d, a, b, 3.0, cp.acc(dk, 0.6))
        ink_poly(d, ring, 2.4, ('plzink', dk))
    # fist roads: clean asphalt ribbons, red centre dashes, kerb ink
    for n, (a, b) in enumerate(FIST):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-6:
            continue
        dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        wd = 1.25
        ax, ay, bx, by = a[0] - dx * wd, a[1] - dy * wd, b[0] + dx * wd, b[1] + dy * wd
        q = [(ax - dy * wd, ay + dx * wd, 0.05), (bx - dy * wd, by + dx * wd, 0.05), (bx + dy * wd, by - dx * wd, 0.05),
             (ax + dy * wd, ay - dx * wd, 0.05)]
        facet(d, lambda u, v, q=q: cam.p(*bil3(q, u, v)), max(2, int(L / 2)), 1,
              lambda u, v, i, j, k, rc: ramp(th['street'], (0.62 if night else 0.2) + rc.uniform(-0.05, 0.05)), ('fist', n), 0.2)
    for n, (a, b) in enumerate(FIST):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        t = 0.0
        while t < L:
            p0 = cam.p(a[0] + dx * t, a[1] + dy * t, 0.06)
            p1 = cam.p(a[0] + dx * min(L, t + 0.9), a[1] + dy * min(L, t + 0.9), 0.06)
            line2(d, p0, p1, 3.2, ramp(ACC['reb'], 0.62 if night else 0.5))
            t += 1.6
    # night: light pools (lamps, district haze) and traffic trails, all translucent facets
    if night:
        lay, ld = layer(cp.img)
        for (x, y) in lamps:
            facet(ld, lambda u, v, x=x, y=y: cam.p(x - 0.4 + 2.2 * v * math.cos(u * 6.2832), y + 1.6 * v * math.sin(u * 6.2832), 0.05),
                  6, 2, lambda u, v, i, j, k, rc: ramp(NEON['sodium'], 0.6) + (int(120 * (1 - v)) + 15,), ('lp', x, y), 0.3,
                  wrap_u=True)
        rng = random.Random(31)
        for (x0, y0, x1, y1, dk) in pads:
            if dk in ('fist',) or rng.random() < 0.45:
                continue
            x, y = (x0 + x1) / 2 + rng.uniform(-2, 2), y1 + 0.7
            st = ACC[dk]
            facet(ld, lambda u, v, x=x, y=y: cam.p(x + 3.2 * v * math.cos(u * 6.2832), y + 1.1 * v * math.sin(u * 6.2832), 0.05),
                  7, 2, lambda u, v, i, j, k, rc, st=st: ramp(st, 0.55) + (int(95 * (1 - v)) + 20,), ('dp', x, y), 0.3,
                  wrap_u=True)
            # wet reflection streak
            q = [(x - 0.6, y, 0.05), (x + 0.6, y, 0.05), (x + 0.9, y + 1.6, 0.05), (x - 0.9, y + 1.6, 0.05)]
            facet(ld, lambda u, v, q=q: cam.p(*bil3(q, u, v)), 2, 3,
                  lambda u, v, i, j, k, rc, st=st: None if rc.random() < 0.25 else ramp(st, 0.7) + (int(150 * (1 - v)) + 20,),
                  ('rf', x, y), 0.3)
        for (a, b, big) in XST:
            if not big or b >= LXW:
                continue
            x = (a + b) / 2
            s = rng.uniform(0, 8)
            while s < LYW - 4:
                Lt = rng.uniform(3, 6)
                for lane, st in ((-0.6, NEON['sodium']), (0.6, NEON['red'])):
                    q = [(x + lane - 0.12, s, 0.07), (x + lane + 0.12, s, 0.07), (x + lane + 0.12, s + Lt, 0.07),
                         (x + lane - 0.12, s + Lt, 0.07)]
                    facet(ld, lambda u, v, q=q: cam.p(*bil3(q, u, v)), 1, 3,
                          lambda u, v, i, j, k, rc, st=st: ramp(st, 0.7) + (int(60 + 170 * v),), ('tr', x, s, lane), 0.1)
                s += Lt + rng.uniform(8, 16)
        cp.img = composite(cp.img, lay)
        cp.d = ImageDraw.Draw(cp.img)


# ------------------------------------------------------------------ backdrop
def backdrop(theme, cam):
    if theme == 'night':
        def bg(u, v):
            c = mix(hexc('#05040f'), hexc('#1c0f36'), v ** 0.8)
            return mix(c, hexc('#3a1240'), max(0, v - 0.4) * 0.7)
        sky = R('#080618', '#0e0a24', '#16102e', '#1e1638')
    else:
        def bg(u, v):
            c = mix(hexc('#6e6a58'), hexc('#b0a47a'), v ** 1.2)
            return mix(c, hexc('#2a2a22'), min(1, 0.6 * abs(u - 0.5) ** 2 * 4 * 0.5))
        sky = R('#4a4838', '#5c5946', '#6e6a54', '#807a60')
    img = gradient(bg).convert('RGB')
    d = ImageDraw.Draw(img)
    rng = random.Random(808)
    back_y = min(cam.p(0, 0, 0)[1], cam.p(LXW, 0, 0)[1])
    # distant skyline strip on the horizon
    x = -60
    while x < W + 60:
        w = rng.uniform(40, 110)
        top = back_y - rng.uniform(H * 0.02, H * 0.09)
        facet(d, bil([(x, top), (x + w, top), (x + w, back_y + 40), (x, back_y + 40)]), 1, 1,
              toner(sky, rng.uniform(0.3, 0.9), var=0.03, flip=0.02), ('sky', x), 0.3)
        if theme == 'night' and rng.random() < 0.6:
            ly = rng.uniform(top + 6, back_y)
            line2(d, (x + 4, ly), (x + w - 4, ly), 2, ramp(NEON[rng.choice(['sodium', 'magenta', 'cyan'])], 0.45))
        x += w * rng.uniform(0.7, 1.0)
    # the bay around the city: big calm water facets with neon glints at night
    wst = R('#04040c', '#070818', '#0c0f24', '#121830', '#1a223e') if theme == 'night' else         R('#3a3a30', '#4a4a3c', '#5a5848', '#6a6652', '#7a745c')
    facet(d, bil([(0, back_y + 20), (W, back_y + 20), (W, H), (0, H)]), 18, 8,
          toner(wst, 0.45, gv=0.3, var=0.06, flip=0.06), ('bay', theme), 0.35)
    return smog(img, ('bsm', theme), [(back_y - H * 0.08, H * 0.12, 60, 140)],
                THEMES[theme]['smog'])


# ------------------------------------------------------------------ render
def setup_theme(theme):
    if theme == 'night':
        toon.TINT = ((hexc('#120e3a'), 0.34), (hexc('#1a1446'), 0.12), (hexc('#8a7cff'), 0.1))
        toon.BEVEL = hexc('#8a7eb8')
        toon.WARM = hexc('#6a5ca8')
    else:
        toon.TINT = ((hexc('#343468'), 0.22), (hexc('#f2c88e'), 0.05), (hexc('#f2c88e'), 0.16))
        toon.BEVEL = hexc('#f6e2b4')
        toon.WARM = hexc('#f2c88e')


def render(theme):
    setup_theme(theme)
    cam = make_cam()
    items, pads, lamps, fregion = build_world()
    img = backdrop(theme, cam)
    cp = OverviewPainter(img, cam, theme)
    ground(cp, pads, lamps, fregion)
    for it in items:
        x0, y0, x1, y1 = it['box']
        it['depth'] = cam.depth((x0 + x1) / 2, (y0 + y1) / 2) + (0.5 if it.get('after') else 0)
    items.sort(key=lambda it: (it['depth'], str(it['box'])))
    for it in items:
        cp.item(it)
    img = paint_texture(cp.img)
    sm = THEMES[theme]['smog']
    img = smog(img, ('near', theme), [(H * 0.3, H * 0.14, 30, 80), (H * 0.62, H * 0.16, 30, 70)], sm)
    img = rain(img, ('rain', theme), n=2600, col=(150, 150, 140) if theme == 'day' else (160, 170, 205),
               alpha=(25, 60), length=(50, 130), width=(1.6, 2.6))
    out = finalize(img)
    tops = {k: v for k, v in cp.hq_tops.items()}
    return out, cam, tops


# ------------------------------------------------------------------ labels / overlay (final resolution)
def bfont(size, style='Bold'):
    f = ImageFont.truetype(BAHN, size)
    try:
        f.set_variation_by_name(style)
    except Exception:
        pass
    return f


def pill(d, x, y, line1, line2_, acc, anchor_down=True):
    f1, f2 = bfont(34), bfont(22, 'SemiBold')
    w = max(d.textlength(line1, font=f1), d.textlength(line2_, font=f2)) + 56
    h = 84
    x0, y0 = x - w / 2, y - h - (22 if anchor_down else 0)
    d.polygon([(x0 + 10, y0), (x0 + w, y0), (x0 + w - 10, y0 + h), (x0, y0 + h)], fill=(14, 12, 18))
    d.polygon([(x0 + 10, y0), (x0 + 26, y0), (x0 + 16, y0 + h), (x0, y0 + h)], fill=acc)
    pts = [(x0 + 10, y0), (x0 + w, y0), (x0 + w - 10, y0 + h), (x0, y0 + h), (x0 + 10, y0)]
    d.line(pts, fill=(5, 4, 8), width=4)
    if anchor_down:
        d.polygon([(x - 12, y0 + h), (x + 12, y0 + h), (x, y0 + h + 20)], fill=acc)
    d.text((x0 + 34, y0 + 30), line1, font=f1, fill=(240, 232, 214), anchor='lm')
    d.text((x0 + 34, y0 + 64), line2_, font=f2, fill=acc, anchor='lm')


def labels(img, cam, tops):
    d = ImageDraw.Draw(img)
    for dk, (x, y) in tops.items():
        pill(d, x, max(110, y - 10), HQ_NAME[dk], DNAME[dk] + '  HQ', hexc(ACC_HEX[dk]))
    fx, fy = cam.p(FIST_C[0], FIST_C[1] - 14, 4)
    pill(d, fx, fy, 'THE FIST', 'REBEL_CELL  //  roads, no tower', hexc(ACC_HEX['reb']))
    for (x, y) in ((110, 54), (12, 92), (210, 10)):
        sx, sy = cam.p(x, y, 9)
        pill(d, sx, sy, 'THE SPRAWL', 'neutral city', hexc('#c8bfa8'))
    return img


def map_overlay(img, cam):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cs = 2.0
    nx, ny = int(LXW / cs), int(LYW / cs)
    grid = {}
    for i in range(nx):
        for j in range(ny):
            grid[(i, j)] = district_info((i + 0.5) * cs, (j + 0.5) * cs)
    for (i, j), (p, s, m) in grid.items():
        q = [cam.p(i * cs, j * cs, 0.1), cam.p((i + 1) * cs, j * cs, 0.1), cam.p((i + 1) * cs, (j + 1) * cs, 0.1),
             cam.p(i * cs, (j + 1) * cs, 0.1)]
        col = hexc(ACC_HEX[p])
        if m < 4.0 and (i + j) % 2 == 0:
            col = hexc(ACC_HEX[s])      # the mixed border band: a checker of both districts
        d.polygon(q, fill=col + (78 if m >= 4.0 else 96,))
    out = Image.alpha_composite(img.convert('RGBA'), lay)
    d = ImageDraw.Draw(out)
    for (i, j), (p, s, m) in grid.items():
        for di, dj, e in ((1, 0, 'x'), (0, 1, 'y')):
            nb = grid.get((i + di, j + dj))
            if nb and nb[0] != p:
                if e == 'x':
                    a, b = cam.p((i + 1) * cs, j * cs, 0.1), cam.p((i + 1) * cs, (j + 1) * cs, 0.1)
                else:
                    a, b = cam.p(i * cs, (j + 1) * cs, 0.1), cam.p((i + 1) * cs, (j + 1) * cs, 0.1)
                d.line([a, b], fill=(8, 6, 10, 255), width=7)
                d.line([a, b], fill=(244, 238, 222, 255), width=2)
    return out


def ours_mark(img, cam):
    d = ImageDraw.Draw(img)
    x, y = cam.p(OURS[0], OURS[1], 1.5)
    rng = random.Random(9)
    pts = []
    for k in range(70):
        a = -0.4 + 2 * math.pi * 1.12 * k / 69
        rr = 1 + 0.06 * math.sin(k * 0.7) + rng.uniform(-0.02, 0.02)
        pts.append((x + 92 * rr * math.cos(a), y + 64 * rr * math.sin(a)))
    pen = (255, 228, 46)
    d.line([(p[0] + 3, p[1] + 3) for p in pts], fill=(10, 8, 12), width=11, joint='curve')
    d.line(pts, fill=pen, width=8, joint='curve')
    f = ImageFont.truetype(MARKER, 64)
    d.text((x + 100, y - 92), 'OURS', font=f, fill=(10, 8, 12), anchor='lm', stroke_width=0)
    d.text((x + 96, y - 96), 'OURS', font=f, fill=pen, anchor='lm')
    d.line([(x + 98, y - 60), (x + 66, y - 40)], fill=pen, width=6)
    return img


def legend(img):
    d = ImageDraw.Draw(img)
    x0, y0 = 60, 60
    keys = ['sol', 'mer', 'hal', 'orb', 'reb', 'spr']
    d.rectangle([x0, y0, x0 + 560, y0 + 70 + 52 * len(keys)], fill=(14, 12, 18))
    d.rectangle([x0, y0, x0 + 560, y0 + 70 + 52 * len(keys)], outline=(5, 4, 8), width=4)
    d.text((x0 + 26, y0 + 36), 'TERRITORY', font=bfont(36), fill=(240, 232, 214), anchor='lm')
    for n, k in enumerate(keys):
        y = y0 + 92 + n * 52
        d.rectangle([x0 + 26, y - 16, x0 + 70, y + 16], fill=hexc(ACC_HEX[k]))
        d.text((x0 + 90, y), DNAME[k], font=bfont(28, 'SemiBold'), fill=(230, 222, 204), anchor='lm')
    return img


def crops(night_img, cam, tops):
    mid = {'sol': 20, 'mer': 8, 'hal': 8, 'orb': 13}
    items = [(HQ_NAME[k], cam.p(HQ[k][0], HQ[k][1], mid[k])) for k in ('sol', 'mer', 'hal', 'orb')]
    items.append(('THE FIST (REBEL_CELL)', cam.p(FIST_C[0], FIST_C[1] + 3, 0)))
    cw, ch = 900, 820
    sheet = Image.new('RGB', (3 * cw + 4 * 30, 2 * (ch + 70) + 3 * 30), (20, 18, 24))
    d = ImageDraw.Draw(sheet)
    for n, (name, (x, y)) in enumerate(items):
        cy = y
        box = (int(x - cw / 2), int(cy - ch / 2), int(x + cw / 2), int(cy + ch / 2))
        c = night_img.crop(box)
        r, k = divmod(n, 3)
        if r == 1:
            k += 0.5
        px, py = int(30 + k * (cw + 30)), int(30 + r * (ch + 100))
        sheet.paste(c, (px, py))
        d.text((px + 6, py + ch + 34), name, font=bfont(34), fill=(236, 228, 210), anchor='lm')
    return sheet


def main(which=('night', 'day')):
    res = {}
    for th in which:
        img, cam, tops = render(th)
        res[th] = (img, cam, tops)
        if th == 'night':
            labels(img.copy(), cam, tops).save(os.path.join(OUT, 'city_overview_night.png'), optimize=True)
            crops(img, cam, tops).save(os.path.join(OUT, 'hq_crops.png'), optimize=True)
        else:
            labels(img.copy(), cam, tops).save(os.path.join(OUT, 'city_overview_day.png'), optimize=True)
            m = map_overlay(img, cam)
            m = labels(m.convert('RGB'), cam, tops)
            m = ours_mark(m, cam)
            m = legend(m)
            m.convert('RGB').save(os.path.join(OUT, 'city_overview_map.png'), optimize=True)
        print('done', th)


if __name__ == '__main__':
    main(tuple(sys.argv[1:]) or ('night', 'day'))
