"""Round 6 views: the restyled game city by day and night, calm and under local suspicion.

Suspicion is local to the player's district (Solace, round the helix of the title crop):
red/blue police strobes on street corners and rooftops with their light spilling over the
nearby streets and facades, helicopters and drones overhead with spotlight cones and bright
pools on the ground. The rest of the city stays as it is (no global wash).
Usage: python views.py [<city_layout.json>]        -> ../views/*.png, ../views/views_sheet.jpg
"""
import json
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageFont
import lowpoly
from lowpoly import SS, hexc, mix, ramp, facet, bil, tri, line2, poly_fpos, R
import toon
import restyle
from restyle import Restyler, View, labels, h01, c255

OUT = os.path.join(os.path.dirname(HERE), 'views')
RED, BLUE = (255, 34, 56), (42, 107, 255)
BEAM = (216, 232, 255)
GUN = R('#06050a', '#100c14', '#1c1622', '#2c2434', '#40364a')


def set_theme(theme):
    if theme == 'day':
        restyle.BANDS = (0.36, 0.58, 0.80)
        toon.TINT = ((hexc('#343468'), 0.22), (hexc('#f2c88e'), 0.05), (hexc('#f2c88e'), 0.16))
        toon.BEVEL = hexc('#f6e2b4')
        restyle.TH.update(darken=0.0, neon=0.62, win=0.03, glow=0.42, ground=hexc('#3c3a31'), street=hexc('#1e1d1f'),
                          ground_mix=(92, 88, 70), vary=True)
    else:
        restyle.BANDS = (0.30, 0.50, 0.70)
        toon.TINT = ((hexc('#120e3a'), 0.30), (hexc('#1a1446'), 0.10), (hexc('#8a7cff'), 0.08))
        toon.BEVEL = hexc('#9a8ec8')
        restyle.TH.update(darken=0.28, neon=1.0, win=0.22, glow=1.05, ground=None, street=None, ground_mix=(24, 22, 40),
                          vary=True)


class ViewRestyler(Restyler):
    def __init__(self, data, view, theme, suspicion):
        super().__init__(data, view)
        self.theme, self.susp = theme, suspicion
        sol = next(t for t in data['territories'] if t['id'] == 'solace')
        self.sx, self.sy = sol['screen']           # Solace HQ, city px
        self.roofs = []

    def local(self, x, y, k=1.0):
        """True inside the suspicion area (an iso ellipse round Solace's HQ, city px)."""
        return ((x - self.sx) / (1250 * k)) ** 2 + ((y - self.sy) / (640 * k)) ** 2 < 1.0

    def roof_hook(self, ci, top, hh):
        if not self.susp or ci < 0:
            return
        ctx = self.ctxs[ci]
        bx, by = ctx['base'][0], ctx['base'][1]
        if ctx['kind'] == 'bld' and self.local(bx, by) and hh > 24 * self.v.k and h01(ci, 91) < 0.16:
            cx = sum(p[0] for p in top) / len(top)
            cy = sum(p[1] for p in top) / len(top)
            self.roofs.append((cx, cy, ci))

    # ---- suspicion overlay
    def corners(self):
        out = []
        for st in self.d['streets']:
            if st['ai'] and st['aj']:
                p = st['p']
                x = sum(p[0::2]) / 4
                y = sum(p[1::2]) / 4
                if self.local(x, y) and h01(st['i'], st['j'], 92) < 0.55:
                    out.append((x, y, st['i'], st['j']))
        return out

    def strobe(self, d, pg, x, y, seed, big=1.0):
        k = self.v.k * big
        for s, col in ((-1, RED), (1, BLUE)):
            cx = x + s * 3.2 * k
            tri(d, [(cx - 2.6 * k, y), (cx, y - 3.2 * k), (cx + 2.6 * k, y)], mix(col, (255, 255, 255), 0.45))
            tri(d, [(cx - 2.6 * k, y), (cx, y + 2.2 * k), (cx + 2.6 * k, y)], col)
            r = 26 * k
            pg.ellipse([(cx + s * 8 * k - r) * SS, (y - r * 0.6) * SS, (cx + s * 8 * k + r) * SS, (y + r * 0.6) * SS],
                       fill=mix(col, (0, 0, 0), 0.25))

    def spill_pool(self, d, x, y, col, r, seed):
        v = self.v
        alpha = 70 if self.theme == 'night' else 46
        facet(d, lambda u, vv: (x + r * vv * math.cos(u * 6.2832), y + r * 0.5 * vv * math.sin(u * 6.2832)), 8, 2,
              lambda u, vv, i, j, k, rc: col + (int(alpha * (1 - vv) + rc.uniform(0, 14)),), ('sp', seed), 0.3, wrap_u=True)

    def craft_list(self):
        """Helicopters and drones over the area: (kind, target city px, height city px, side, seed)."""
        cs = sorted(self.corners(), key=lambda c: (c[2], c[3]))
        if not cs:
            return []
        rng = random.Random(606)
        picks = []
        want = [('heli', -1), ('heli', 1), ('drone', 1), ('drone', -1), ('drone', 1), ('drone', -1)]
        for n, (kind, side) in enumerate(want):
            # targets spread round the HQ: nearest corner to a ring point
            a = 2 * math.pi * n / len(want) + 0.4
            px, py = self.sx + 520 * math.cos(a), self.sy + 300 * math.sin(a) + 120
            tx, ty, _, _ = min(cs, key=lambda c: (c[0] - px) ** 2 + (c[1] - py) ** 2)
            hgt = rng.uniform(210, 260) if kind == 'heli' else rng.uniform(130, 170)
            picks.append((kind, (tx, ty), hgt, side, n))
        return picks

    def heli(self, d, x, y, s, side, seed):
        rng = random.Random(seed)

        def P(px, py):
            return (x + px * s * side, y + py * s)
        body = [P(-1.0, -0.2), P(0.2, -0.45), P(0.9, -0.1), P(0.6, 0.35), P(-0.6, 0.35)]
        c = P(0, 0)
        for k in range(len(body)):
            tri(d, [body[k], body[(k + 1) % len(body)], c], ramp(GUN, 0.3 + 0.6 * rng.random()))
        tri(d, [P(0.2, -0.45), P(0.9, -0.1), P(0.45, -0.05)], (120, 170, 220))
        tri(d, [P(-0.9, -0.15), P(-2.4, -0.25), P(-0.8, 0.2)], ramp(GUN, 0.55))
        tri(d, [P(-2.4, -0.25), P(-2.6, -0.8), P(-2.2, -0.2)], ramp(GUN, 0.7))
        line2(d, P(-2.2, -0.6), P(2.0, -0.42), max(1.2, s * 0.07), ramp(GUN, 0.9))
        toon.ink_poly(d, body, max(1.0, s * 0.06), ('hk', seed))
        for (px, py, col) in ((-2.4, -0.3, RED), (0.5, 0.36, BLUE)):
            q = P(px, py)
            r = max(2, s * 0.16)
            tri(d, [(q[0] - r, q[1]), (q[0], q[1] - r), (q[0] + r, q[1])], col)
            tri(d, [(q[0] - r, q[1]), (q[0], q[1] + r), (q[0] + r, q[1])], mix(col, (0, 0, 0), 0.3))
        return P(0.3, 0.35)

    def drone(self, d, x, y, s, seed):
        pts = [(x, y - s), (x + s * 1.3, y), (x, y + s * 0.7), (x - s * 1.3, y)]
        for k, t in enumerate((0.85, 0.45, 0.3, 0.65)):
            tri(d, [pts[k], pts[(k + 1) % 4], (x, y)], ramp(GUN, t))
        for sx in (-1, 1):
            a = (x + sx * s * 1.3, y)
            line2(d, a, (a[0] + sx * s * 0.9, a[1] - s * 0.4), max(1, s * 0.12), ramp(GUN, 0.9))
        toon.ink_poly(d, pts, max(1.0, s * 0.08), ('dk', seed))
        tri(d, [(x - s * 0.4, y + s * 0.1), (x + s * 0.4, y + s * 0.1), (x, y + s * 0.5)], RED)
        return (x, y + s * 0.5)

    def after_standing(self, img, bg):
        if not self.susp:
            return img
        v = self.v
        night = self.theme == 'night'
        # red/blue spill pools on streets and facades near the strobes (translucent facets)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay, 'RGBA')
        corners = self.corners()
        for n, (x, y, i, j) in enumerate(corners):
            ox, oy = v.p(x, y)
            col = RED if (i + j) % 2 else BLUE
            self.spill_pool(ld, ox, oy, col, 70 * v.k, ('c', i, j))
        for n, (x, y, ci) in enumerate(self.roofs):
            self.spill_pool(ld, x, y + 10 * v.k, RED if n % 2 else BLUE, 40 * v.k, ('r', ci))
        # spotlight cones and ground pools
        crafts = self.craft_list()
        cone_a = (96, 30) if night else (48, 14)
        for kind, (tx, ty), hgt, side, seed in crafts:
            gx, gy = v.p(tx, ty)
            ax, ay = v.p(tx + side * 120 * (0.6 if kind == 'drone' else 1.0), ty - hgt)
            r = (78 if kind == 'heli' else 52) * v.s
            left, right = (gx - r, gy), (gx + r, gy)
            facet(ld, bil([(ax - 3 * v.k, ay), (ax + 3 * v.k, ay), right, left]), 3, 6,
                  lambda u, vv, i, j, k, rc: BEAM + (int(cone_a[0] * (1 - vv) + cone_a[1] + rc.uniform(0, 10)),),
                  ('cone', seed), 0.3)
            pa = 150 if night else 120
            facet(ld, lambda u, vv: (gx + r * vv * math.cos(u * 6.2832), gy + r * 0.5 * vv * math.sin(u * 6.2832)), 12, 3,
                  lambda u, vv, i, j, k, rc: (250, 252, 255, int(pa * (1 - vv * 0.6) + rc.uniform(0, 20))), ('pool', seed),
                  0.25, wrap_u=True)
        img = Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')
        d = ImageDraw.Draw(img, 'RGBA')
        pglow = Image.new('RGB', img.size, (0, 0, 0))
        pg = ImageDraw.Draw(pglow)
        for n, (x, y, i, j) in enumerate(corners):
            ox, oy = v.p(x, y)
            # a pole with its light bar
            line2(d, (ox + 14 * v.k, oy), (ox + 14 * v.k, oy - 16 * v.k), 1.4 * v.k, (12, 10, 16))
            self.strobe(d, pg, ox + 14 * v.k, oy - 17 * v.k, ('cs', i, j))
        for (x, y, ci) in self.roofs:
            self.strobe(d, pg, x, y - 2 * v.k, ('rs', ci), big=1.15)
        for kind, (tx, ty), hgt, side, seed in crafts:
            gx, gy = v.p(tx, ty)
            ax, ay = v.p(tx + side * 120 * (0.6 if kind == 'drone' else 1.0), ty - hgt)
            pg.ellipse([(gx - 40 * v.k) * SS, (gy - 20 * v.k) * SS, (gx + 40 * v.k) * SS, (gy + 20 * v.k) * SS],
                       fill=(150, 160, 180) if night else (90, 95, 105))
            if kind == 'heli':
                self.heli(d, ax, ay - 6 * v.k, 22 * v.k, side, seed)
            else:
                self.drone(d, ax, ay - 4 * v.k, 10 * v.k, seed)
            for col, dx in ((RED, -1), (BLUE, 1)):
                r = 18 * v.k
                pg.ellipse([(ax + dx * 6 * v.k - r) * SS, (ay - r) * SS, (ax + dx * 6 * v.k + r) * SS, (ay + r) * SS],
                           fill=mix(col, (0, 0, 0), 0.4))
        img = self.bloom(img, pglow, 16, 1.0 if night else 0.75)
        img = self.bloom(img, pglow, 60, 0.55 if night else 0.35)
        return img

    def finish(self, img):
        if self.theme != 'day':
            return img
        # smog: a yellow haze thickening toward the top of the frame, a few big translucent bands
        v = self.v
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(lay, 'RGBA')
        smog = (200, 182, 120)
        col = Image.new('L', (1, 64))
        for y in range(64):
            vv = y / 63
            col.putpixel((0, y), int(120 * max(0.0, 1 - vv / 0.6) ** 1.6 + 24))
        lay.paste(Image.new('RGBA', img.size, smog + (255,)), (0, 0), col.resize(img.size, Image.BICUBIC))
        img = Image.alpha_composite(img.convert('RGBA'), lay)
        lay = Image.new('RGBA', img.size, (0, 0, 0, 0))     # the bands on their own layer (no alpha overwrite)
        ld = ImageDraw.Draw(lay)
        rng = random.Random(77)
        for n in range(4):
            y = rng.uniform(0.15, 0.85) * v.h
            hgt = rng.uniform(0.06, 0.12) * v.h
            facet(ld, bil([(-20, y), (v.w + 20, y - hgt * 0.2), (v.w + 20, y + hgt * 0.8), (-20, y + hgt)]), 12, 2,
                  lambda u, vv, i, j, k, rc: smog + (int(rc.uniform(10, 34) * (1 - abs(vv - 0.5) * 2)),), ('band', n), 0.4)
        return Image.alpha_composite(img.convert('RGBA'), lay).convert('RGB')


def views(data):
    os.makedirs(OUT, exist_ok=True)
    vw = data['view']
    sol = next(t for t in data['territories'] if t['id'] == 'solace')
    sx, sy = sol['screen']
    crops = []
    for name, theme, susp in (('restyle_day', 'day', False), ('restyle_night', 'night', False),
                              ('restyle_suspicion_day', 'day', True), ('restyle_suspicion_night', 'night', True)):
        set_theme(theme)
        full = View(0, 0, vw['zoom'], vw['w'], vw['h'])
        lowpoly.W, lowpoly.H = full.w, full.h
        img = ViewRestyler(data, full, theme, susp).render()
        img = labels(img, data, full)
        img.resize((2560, 1440), Image.LANCZOS).save(os.path.join(OUT, name + '_full.png'), optimize=True)
        tv = View(sx - 960 / 1.5, sy - 760 / 1.5, 1.5, 1920, 1080)
        lowpoly.W, lowpoly.H = tv.w, tv.h
        crop = ViewRestyler(data, tv, theme, susp).render()
        crop.save(os.path.join(OUT, name + '_crop.png'), optimize=True)
        crops.append((name, crop))
        print('wrote', name)
    tw, th = 960, 540
    sheet = Image.new('RGB', (2 * tw + 60, 2 * (th + 60) + 40), (16, 15, 20))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype('C:/Windows/Fonts/bahnschrift.ttf', 28)
    for n, (name, im) in enumerate(crops):
        r, c = divmod(n, 2)
        x, y = 20 + c * (tw + 20), 60 + r * (th + 60)
        sheet.paste(im.resize((tw, th), Image.LANCZOS), (x, y))
        d.text((x, y - 24), name.replace('restyle_', '').replace('_', ' ').upper(), font=f, fill=(236, 228, 210), anchor='lm')
    sheet.save(os.path.join(OUT, 'views_sheet.jpg'), quality=90)
    print('wrote views_sheet.jpg')


if __name__ == '__main__':
    p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(HERE), 'city_layout.json')
    views(json.load(open(p)))
