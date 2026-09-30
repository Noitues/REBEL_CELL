"""Screen-wide cel-shaded city with the playable district in focus and a double-helix HQ.

Style = r2_blend_EC_on_Cv2_day (Cv2 facets + E's 3-band toon light, wobbly ink, painted grime).
- The city fills the frame: blocks and streets continue past every edge (same camera as v2).
- Only the current district (7x4 lots) is full colour; every other block is grey, translucent,
  thin light ink, against a pale backdrop. A heavy ink line marks the district boundary.
- Building heights come from a seeded clustered height field (not graded by row); lots in front of
  path segments are capped so the route stays visible.
- HQ: an extra-large double helix of chunky rotated floor slabs (window bands, balcony lips, ink),
  enclosed skybridges across the core, a cyan/magenta light strip spiralling up each strand.
  The final route node (boss) sits at its base.
Usage: python wide.py   (writes ../city_day.png)
"""
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageChops
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, skew_rect, tri, gem, gradient, line2,
                     text, smog, rain, finalize, NEON, panel, layer, composite)
import city
from city import (CityPainter, THEMES, FAM, LIGHT, LX, LY, ST, LOT_X, LOT_Y, lot_rect, inter, NBX, NBY, B,
                  clutter, default_cam, city_hud, v_sub, v_cross, v_dot, v_norm, bil3, NODES, EDGES, WIN_NEON)
from toon import ToonPainter, ink_line, ink_poly, hull, paint_texture, INK, BEVEL, band_of, BANDS, tint

LIGHT_INK = hexc('#8a857a')
PALE_TOP = hexc('#a79d78')
PALE_BOT = hexc('#d2cbb8')


# ------------------------------------------------------------------ heights
def make_field():
    rng = random.Random(4099)
    cl = []
    for _ in range(26):
        cl.append((rng.uniform(-50, LX + 50), rng.uniform(-60, LY + 40), rng.uniform(4, 11), rng.uniform(4, 10)))

    def f(x, y):
        return 1.8 + sum(a * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (r * r)) for cx, cy, a, r in cl)
    return f


HF = make_field()


def caps():
    """Height caps on district lots so the route stays readable."""
    cap = {}

    def put(k, v):
        cap[k] = min(cap.get(k, 99.0), v)
    # keys: (bx, by, edge) where edge 'b' = parcels on the lot's back edge, 'l' = on its left edge
    for e in EDGES:
        for (a, b) in zip(e, e[1:]):
            if a[1] == b[1]:  # along street iy: back-edge parcels of the lots in front (by = iy)
                for bx in range(min(a[0], b[0]), max(a[0], b[0])):
                    put((bx, a[1], 'b'), 2.6)
            else:              # along street ix: left-edge parcels of the lots to the right (bx = ix)
                for by in range(min(a[1], b[1]), max(a[1], b[1])):
                    put((a[0], by, 'l'), 4.5)
    for _, (ix, iy), _k in NODES:
        put((ix - 1, iy, 'b'), 3.0)
        put((ix, iy, 'b'), 3.0)
        put((ix, iy, 'l'), 3.0)
    # keep the HQ's neighbours low so the helix reads
    for k in ((5, 0, 'b'), (5, 0, 'l'), (5, 0, 'a'), (6, 1, 'a'), (5, 1, 'a'), (6, 2, 'a'), (6, 3, 'a')):
        put(k, 3.5)
    return cap


# ------------------------------------------------------------------ model
FAMS = ['soot', 'soot', 'rust', 'oily', 'concrete', 'concrete', 'brick', 'brick']
HQ_LOT = (6, 0)


def parcels_for(rng, x0, y0, x1, y1):
    split = rng.choice([2, 4, 4, 4])
    if split == 2:
        mx = x0 + (x1 - x0) * rng.uniform(0.4, 0.6)
        return [(x0, y0, mx, y1), (mx, y0, x1, y1)]
    mx = x0 + (x1 - x0) * rng.uniform(0.4, 0.6)
    my = y0 + (y1 - y0) * rng.uniform(0.4, 0.6)
    return [(x0, y0, mx, my), (mx, y0, x1, my), (x0, my, mx, y1), (mx, my, x1, y1)]


def build_district():
    rng = random.Random(2077)
    cap = caps()
    items = []
    special = {(1, 0): 'mega', (3, 1): 'dome', (4, 2): 'billboard', (5, 0): 'hq', (6, 0): 'hqzone'}
    shanty = {(1, 3), (5, 3)}
    bid = 0
    for by in range(NBY):
        for bx in range(NBX):
            x0, y0, x1, y1 = lot_rect(bx, by)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            key = (bx, by)
            if key in shanty:
                prims = []
                srng = random.Random(f'shanty{bx}{by}')
                for i in range(4):
                    for j in range(3):
                        if srng.random() < 0.15:
                            continue
                        a0 = x0 + 0.2 + i * 1.18 + srng.uniform(-0.1, 0.1)
                        b0 = y0 + 0.2 + j * 1.3 + srng.uniform(-0.1, 0.1)
                        prims.append(B(a0, b0, a0 + srng.uniform(0.8, 1.05), b0 + srng.uniform(0.85, 1.1), 0,
                                       srng.uniform(0.6, 1.5), srng.choice(['rust', 'brick', 'oily', 'concrete']),
                                       (bid, i, j), signs=1 if srng.random() < 0.35 else 0,
                                       graffiti=srng.random() < 0.3))
                items.append(dict(box=(x0, y0, x1, y1), prims=prims))
                bid += 1
                continue
            if key in special:
                kind = special[key]
                prims = []
                if kind == 'hq':
                    from helix import CX, CY
                    items.append(dict(box=(CX - 1, CY - 1, CX + 1, CY + 1), prims=[dict(k='hq')]))
                    continue
                if kind == 'hqzone':
                    continue
                if kind == 'mega':
                    prims.append(B(x0 + 0.2, y0 + 0.2, x1 - 0.2, y1 - 0.2, 0, 6.5, 'brick', bid, win='sodium', signs=2,
                                   scaffold=True, graffiti=True))
                    prims.append(B(x0 - 0.3, y0 + 0.4, x1 + 0.2, y1 + 0.35, 6.5, 11.0, 'concrete', bid + 1,
                                   win='sodium', signs=1))
                    prims.append(B(x0 + 1.0, y0 + 0.9, x1 - 1.2, y1 - 0.8, 11.0, 17.0, 'oily', bid + 2, win='cyan'))
                    clutter(rng, prims, x0 + 1.0, y0 + 0.9, x1 - 1.2, y1 - 0.8, 17.0, bid + 3)
                elif kind == 'dome':
                    prims.append(B(x0 + 0.4, y0 + 0.4, x1 - 0.4, y1 - 0.4, 0, 1.6, 'concrete', bid, win='sodium',
                                   signs=1, graffiti=True))
                    prims.append(dict(k='dome', cx=cx, cy=cy, z0=1.6, r=1.95, fam='rust', bid=bid + 1))
                elif kind == 'billboard':
                    prims.append(B(x0 + 0.4, y0 + 0.5, x1 - 0.4, y1 - 0.5, 0, 2.4, 'rust', bid, win='sodium',
                                   signs=1, graffiti=True))
                    for n, xx in enumerate((x0 + 0.9, cx - 0.1, x1 - 1.1)):
                        prims.append(B(xx, cy - 0.1, xx + 0.2, cy + 0.1, 2.4, 3.2, 'soot', bid + 1 + n, grime=False))
                    prims.append(dict(k='board', x0=x0 - 0.2, x1=x1 + 0.2, y=cy + 0.1, z0=3.0, z1=6.4, bid=bid + 5,
                                      motif='eye'))
                bid += 8
                items.append(dict(box=(x0, y0, x1, y1), prims=prims))
                continue
            for (a0, b0, a1, b1) in parcels_for(rng, x0, y0, x1, y1):
                h = HF((a0 + a1) / 2, (b0 + b1) / 2) * rng.uniform(0.5, 1.5) * 1.3
                if rng.random() < 0.12:
                    h *= 1.9
                h = max(0.9, min(16.0, h))
                c = cap.get((bx, by, 'a'), 99.0)
                if abs(b0 - y0) < 1e-6:
                    c = min(c, cap.get((bx, by, 'b'), 99.0))
                if abs(a0 - x0) < 1e-6:
                    c = min(c, cap.get((bx, by, 'l'), 99.0))
                capped = c < 99.0
                h = min(h, c * rng.uniform(0.75, 1.0))
                ins = 0.2
                nsig = rng.choice([0, 1, 1, 2, 3]) if h > 2.2 else 0
                prims = [B(a0 + ins, b0 + ins, a1 - ins, b1 - ins, 0, h, rng.choice(FAMS), bid,
                           win=rng.choice(WIN_NEON), signs=nsig, scaffold=(3 < h < 9 and rng.random() < 0.2),
                           graffiti=(h < 7 and rng.random() < 0.55))]
                top = h
                bx0, by0, bx1, by1 = a0 + ins, b0 + ins, a1 - ins, b1 - ins
                if h > 5.5 and rng.random() < 0.5 and not capped:
                    wv, dv = bx1 - bx0, by1 - by0
                    if rng.random() < 0.4:
                        nx0, ny0, nx1, ny1 = bx0 + 0.3, by0 + 0.2, bx1 + 0.35, by1 + 0.35
                    else:
                        nx0, ny0, nx1, ny1 = bx0 + wv * 0.15, by0 + dv * 0.15, bx1 - wv * 0.2, by1 - dv * 0.2
                    h2 = top + rng.uniform(2.5, 6.0)
                    prims.append(B(nx0, ny0, nx1, ny1, top, h2, rng.choice(['corp', 'concrete', 'oily']), bid + 1,
                                   win=rng.choice(WIN_NEON), signs=1 if rng.random() < 0.4 else 0))
                    bx0, by0, bx1, by1, top = nx0, ny0, nx1, ny1, h2
                if rng.random() < 0.35 and h > 3:
                    px = bx1 - 0.02
                    py = by0 + (by1 - by0) * rng.uniform(0.3, 0.7)
                    prims.append(B(px, py, px + 0.14, py + 0.14, 0, h * 0.95, 'rust', bid + 2, grime=False))
                clutter(rng, prims, bx0, by0, bx1, by1, top, bid + 3)
                items.append(dict(box=(a0, b0, a1, b1), prims=prims))
                bid += 5
    for n, ij in enumerate([(1, 2), (3, 3), (6, 2), (5, 2), (3, 1), (1, 4), (6, 4)]):
        x, y = inter(*ij)
        x += 0.55
        y += 0.55
        items.append(dict(box=(x - 0.1, y - 0.1, x + 0.1, y + 0.1), prims=[
            B(x - 0.05, y - 0.05, x + 0.05, y + 0.05, 0, 2.6, 'soot', ('pole', n), grime=False),
            B(x - 0.14, y - 0.12, x + 0.14, y + 0.34, 2.35, 2.62, 'concrete', ('camh', n), grime=False),
            dict(k='led', x=x, y=y + 0.36, z=2.48, bid=('led', n))]))
    return items


def build_outer(cam):
    """Every lot outside the district, kept only when it can reach the screen."""
    rng = random.Random(911)
    back, front = [], []
    for by in range(-12, NBY + 7):
        for bx in range(-9, NBX + 9):
            if 0 <= bx < NBX and 0 <= by < NBY:
                continue
            x0, y0, x1, y1 = lot_rect(bx, by)
            pts = [cam.p(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (0, 22)]
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            if max(xs) < -20 or min(xs) > W + 20 or max(ys) < -20 or min(ys) > H + 20:
                continue
            lrng = random.Random(f'outer{bx},{by}')
            prims = []
            near_hq = math.hypot((x0 + x1) / 2 - 43.4, (y0 + y1) / 2 - 1.9) < 10.5
            for (a0, b0, a1, b1) in parcels_for(lrng, x0, y0, x1, y1):
                h = max(0.8, min(18.0, HF((a0 + a1) / 2, (b0 + b1) / 2) * lrng.uniform(0.45, 1.35)))
                if near_hq:
                    h = min(h, 1.6)
                prims.append(B(a0 + 0.2, b0 + 0.2, a1 - 0.2, b1 - 0.2, 0, h, lrng.choice(FAMS), ('o', bx, by, a0, b0),
                               win='sodium', grime=False))
                if h > 7 and lrng.random() < 0.4:
                    w, d = a1 - a0 - 0.4, b1 - b0 - 0.4
                    prims.append(B(a0 + 0.2 + w * 0.2, b0 + 0.2 + d * 0.2, a1 - 0.2 - w * 0.2, b1 - 0.2 - d * 0.2, h,
                                   h + lrng.uniform(2, 5), lrng.choice(FAMS), ('o2', bx, by, a0, b0), win='sodium',
                                   grime=False))
            it = dict(box=(x0, y0, x1, y1), prims=prims)
            (front if (by >= NBY or bx >= NBX) else back).append(it)
    return back, front


# ------------------------------------------------------------------ painters
class GhostPainter(ToonPainter):
    """Grey, thin-inked rendering for the city outside the district."""

    def __init__(self, img, cam):
        super().__init__(img, cam, 'day')
        self.ghost = True

    def box(self, p):
        CityPainter.box(self, p)
        cam = self.cam
        x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
        pts = [cam.p(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
        hp = hull(pts)
        for k in range(len(hp)):
            line2(self.d, hp[k], hp[(k + 1) % len(hp)], 1.1, LIGHT_INK)
        tp = [cam.p(x0, y1, z1), cam.p(x1, y1, z1), cam.p(x1, y0, z1)]
        line2(self.d, tp[0], tp[1], 0.8, LIGHT_INK)
        line2(self.d, tp[1], tp[2], 0.8, LIGHT_INK)
        line2(self.d, cam.p(x1, y1, z0), tp[1], 0.8, LIGHT_INK)


class DistrictPainter(ToonPainter):
    def item(self, it):
        for p in it['prims']:
            if p['k'] == 'hq':
                self.hq(p)
        super().item(dict(prims=[p for p in it['prims'] if p['k'] != 'hq']))

    # ---- oriented prism (for the rotated helix floors and bridges)
    def oprism(self, c, ang, L, D, z0, z1, stops, seed, colfac=None, ink=2.4, strip=None, nu=2, nv=2):
        cam = self.cam
        ca, sa = math.cos(ang), math.sin(ang)
        r = (ca, sa)            # radial / length axis
        t = (-sa, ca)           # tangential axis

        def P(a, b, z):
            return (c[0] + r[0] * a + t[0] * b, c[1] + r[1] * a + t[1] * b, z)
        corners = [(-D / 2, -L / 2), (D / 2, -L / 2), (D / 2, L / 2), (-D / 2, L / 2)]
        center = (c[0], c[1], (z0 + z1) / 2)
        for k in range(4):
            a, b = corners[k], corners[(k + 1) % 4]
            q = [P(a[0], a[1], z0), P(b[0], b[1], z0), P(b[0], b[1], z1), P(a[0], a[1], z1)]
            drawn = self.face(q, stops, (seed, k), nu, nv, center=center, colfac=colfac)
            if drawn and strip is not None:
                # light strip along the outward faces
                zz = z0 + (z1 - z0) * 0.62
                pa, pb = cam.p(*P(a[0], a[1], zz)), cam.p(*P(b[0], b[1], zz))
                n = (q[1][0] - q[0][0], q[1][1] - q[0][1])
                mid = ((q[0][0] + q[1][0]) / 2 - c[0], (q[0][1] + q[1][1]) / 2 - c[1])
                if mid[0] * strip[1][0] + mid[1] * strip[1][1] > 0:
                    line2(self.d, pa, pb, 3.2, ramp(strip[0], 0.8))
        top = [P(*corners[k], z1) for k in range(4)]
        self.face(top, stops, (seed, 't'), 2, 2, center=center, gv=-0.1)
        pts = [cam.p(*P(a, b, z)) for a, b in corners for z in (z0, z1)]
        ink_poly(self.d, hull(pts), ink, (seed, 'sil'))
        tp = [cam.p(*q) for q in top]
        # bevel on the top edge nearest the viewer
        best = max(range(4), key=lambda k: tp[k][1] + tp[(k + 1) % 4][1])
        a, b = tp[best], tp[(best + 1) % 4]
        line2(self.d, (a[0], a[1] + 2.4), (b[0], b[1] + 2.4), 1.6, BEVEL)

    def hq(self, p):
        from helix import draw_hq
        draw_hq(self)

    def district_ground(self):
        cam = self.cam
        th = self.th

        def street(u, v, i, j, k, rc):
            t = 0.35 + 0.25 * (1 - v) + rc.uniform(-0.1, 0.1)
            if rc.random() < 0.12:
                t += 0.35
            return ramp(th['street'], t)
        q = [(0, LY, 0), (LX, LY, 0), (LX, 0, 0), (0, 0, 0)]
        facet(self.d, lambda u, v: cam.p(*bil3(q, u, v)), 40, 20, street, 'street', 0.35)
        for by in range(NBY):
            for bx in range(NBX):
                x0, y0, x1, y1 = lot_rect(bx, by)
                q = [(x0, y1, 0.02), (x1, y1, 0.02), (x1, y0, 0.02), (x0, y0, 0.02)]
                self.face(q, th['lot'], ('lot', bx, by), 4, 3, normal=(0, 0, 1), var=0.1, tlo=0.2, thi=0.8)
                ink_poly(self.d, [cam.p(*c) for c in q], 1.4, ('lotink', bx, by))


def ghost_ground(gp):
    cam = gp.cam
    q = [(-120, LY + 80, 0), (LX + 120, LY + 80, 0), (LX + 120, -120, 0), (-120, -120, 0)]
    facet(gp.d, lambda u, v: cam.p(*bil3(q, u, v)), 60, 50,
          lambda u, v, i, j, k, rc: (int(150 + rc.uniform(-8, 8)),) * 3, 'gground', 0.35)
    for by in range(-12, NBY + 7):
        for bx in range(-9, NBX + 9):
            if 0 <= bx < NBX and 0 <= by < NBY:
                continue
            x0, y0, x1, y1 = lot_rect(bx, by)
            pts = [cam.p(x0, y1, 0.02), cam.p(x1, y1, 0.02), cam.p(x1, y0, 0.02), cam.p(x0, y0, 0.02)]
            if max(p[0] for p in pts) < -50 or min(p[0] for p in pts) > W + 50 or max(p[1] for p in pts) < -50 \
                    or min(p[1] for p in pts) > H + 50:
                continue
            g = int(172 + 10 * hsh(bx, by, 3))
            gp.d.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=(g, g, g - 6), outline=(g, g, g - 6))
            for k in range(4):
                line2(gp.d, pts[k], pts[(k + 1) % 4], 0.9, LIGHT_INK)


LAST_BBOX = [None]


def render():
    cam = default_cam()
    pale = gradient(lambda u, v: mix(PALE_TOP, PALE_BOT, min(1.0, v * 1.6))).convert('RGB')
    # ---- A: the grey city behind and around the district
    A = pale.copy()
    gp = GhostPainter(A, cam)
    ghost_ground(gp)
    back, front = build_outer(cam)
    for it in back:
        x0, y0, x1, y1 = it['box']
        it['depth'] = cam.depth((x0 + x1) / 2, (y0 + y1) / 2)
    back.sort(key=lambda it: (it['depth'], it['box']))
    for it in back:
        gp.item(it)
    A = Image.blend(gp.img, pale, 0.5)
    # ---- B: the district in full colour
    Bimg = Image.new('RGBA', A.size, (0, 0, 0, 0))
    dp = DistrictPainter(Bimg, cam, 'day')
    dp.district_ground()
    ink_poly(dp.d, [cam.p(0, 0, 0), cam.p(LX, 0, 0), cam.p(LX, LY, 0), cam.p(0, LY, 0)], 5.0, 'district_edge')
    dp.paths()
    dp.node_discs()
    items = build_district()
    for it in items:
        x0, y0, x1, y1 = it['box']
        it['depth'] = cam.depth((x0 + x1) / 2, (y0 + y1) / 2)
    items.sort(key=lambda it: (it['depth'], it['box']))
    for it in items:
        dp.item(it)
    dp.cables([it for it in items])
    # painterly texture on the district only
    rgb = paint_texture(dp.img.convert('RGB'))
    rgb.putalpha(dp.img.getchannel('A'))
    img = Image.alpha_composite(A.convert('RGBA'), rgb)
    # heavy ink at the district boundary (where colour stops)
    # ---- C: grey city in front of the district, translucent over it
    Cimg = Image.new('RGBA', A.size, (0, 0, 0, 0))
    cp2 = GhostPainter(Cimg, cam)
    for it in front:
        x0, y0, x1, y1 = it['box']
        it['depth'] = cam.depth((x0 + x1) / 2, (y0 + y1) / 2)
    front.sort(key=lambda it: (it['depth'], it['box']))
    for it in front:
        cp2.item(it)
    a = cp2.img.getchannel('A').point(lambda v: int(v * 0.5))
    Cimg = cp2.img
    Cimg.putalpha(a)
    img = Image.alpha_composite(img, Cimg).convert('RGB')
    img = smog(img, ('near', 'day'), [(80, 160, 30, 80), (420, 180, 30, 70)], THEMES['day']['smog'])
    img = rain(img, 'rain_day', n=700, col=(150, 150, 140), alpha=(30, 65))
    # ---- UI
    dp.img = img
    dp.d = ImageDraw.Draw(img)
    dp.arrows()
    dp.pins()
    d = dp.d
    # HQ label
    x, y = dp.hq_top
    y = max(y - 10, 80)
    w, h = 120, 50
    q = skew_rect(x - w / 2, y - h - 14, w, h, 10)
    panel(d, q, NEON['red'], 0.45, 'hq_lbl', nu=4, nv=1, gv=-0.25)
    ink_poly(d, q, 3.2, 'hq_lbl_ink')
    tri(d, [(x - 10, y - 14.5), (x + 10, y - 14.5), (x, y)], ramp(NEON['red'], 0.6))
    text(d, x + 5, y - 14 - h / 2, 'HQ', 32, hexc('#fff0e0'), anchor='mm', shadow=hexc('#3a0408'))
    LAST_BBOX[0] = dp.hq_bbox
    city_hud(d, 'day')
    ink_poly(d, skew_rect(36, 30, 470, 128, 16), 3.6, 'hud_ink')
    ink_poly(d, skew_rect(40, 958, 560, 86, 12), 3.6, 'leg_ink')
    return img


if __name__ == '__main__':
    root = os.path.dirname(HERE)
    img = render()
    finalize(img).save(os.path.join(root, 'city_day.png'), optimize=True)
    x0, y0, x1, y1 = LAST_BBOX[0]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(W, x1), min(H, y1)
    img.crop((int(x0 * SS), int(y0 * SS), int(x1 * SS), int(y1 * SS))).save(os.path.join(root, 'hq_closeup.png'),
                                                                        optimize=True)
    print('wrote city_day.png and hq_closeup.png')
