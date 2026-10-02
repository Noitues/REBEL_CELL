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

    HELIS = [((-420, 40), 210, -1), ((380, -60), 230, 1), ((120, 150), 200, 1)]
    DRONES = [((-250, -250), 135, 1), ((250, -300), 130, -1), ((-500, -120), 140, 1), ((520, 100), 125, -1),
              ((-80, -300), 120, 1)]

    def craft_list(self):
        """Helicopters and drones over the area: (kind, target city px, altitude city px, side, seed)."""
        out = []
        for n, ((dx, dy), alt, side) in enumerate(self.HELIS):
            out.append(('heli', (self.sx + dx, self.sy + dy), alt, side, n))
        for n, ((dx, dy), alt, side) in enumerate(self.DRONES):
            out.append(('drone', (self.sx + dx, self.sy + dy), alt, side, 10 + n))
        return out

    def craft_at(self, kind, tx, ty, alt, side):
        """Screen point of the craft's belly (the spotlight's apex)."""
        return self.v.p(tx + side * (60 if kind == 'heli' else 36), ty - alt)

    def glow_dot(self, d, x, y, col, r):
        d.ellipse([(x - r * 2.4) * SS, (y - r * 2.4) * SS, (x + r * 2.4) * SS, (y + r * 2.4) * SS], fill=col + (70,))
        tri(d, [(x - r, y), (x, y - r * 1.2), (x + r, y)], mix(col, (255, 255, 255), 0.45))
        tri(d, [(x - r, y), (x, y + r * 1.2), (x + r, y)], col)

    def _poly(self, d, pts, col):
        d.polygon([(p[0] * SS, p[1] * SS) for p in pts], fill=col)

    def heli(self, d, x, y, L, side, seed):
        """A police helicopter, belly at (x, y), L px long: faceted cel body, ink, rotor blur, nav lights."""
        night = self.theme == 'night'
        s = L / 3.6

        def P(px, py):
            return (x + px * s * side, y + py * s)

        def Q(pts):
            return [P(*p) for p in pts]
        if night:
            lit, mid, dark = hexc('#9eb0cc'), hexc('#62728e'), hexc('#2a3246')
        else:
            lit, mid, dark = hexc('#d6dde6'), hexc('#8e9aac'), hexc('#4a5568')
        body = Q([(1.0, -0.35), (0.7, -0.78), (-0.2, -0.88), (-0.9, -0.62), (-1.0, -0.22), (-0.5, 0.0), (0.6, 0.0)])
        boom = Q([(-0.9, -0.64), (-2.55, -0.7), (-2.55, -0.55), (-0.9, -0.4)])
        fin = Q([(-2.3, -0.66), (-2.65, -1.12), (-2.45, -0.6)])
        if night:   # soft back-glow so it separates from the lit city
            cx, cy = P(-0.7, -0.6)
            d.ellipse([(cx - L * 0.75) * SS, (cy - L * 0.32) * SS, (cx + L * 0.75) * SS, (cy + L * 0.32) * SS],
                      fill=(150, 170, 255, 46))
        # rotor disc as a translucent motion blur
        rc = P(-0.1, -1.02)
        rx, ry = 2.3 * s, 0.36 * s
        d.ellipse([(rc[0] - rx) * SS, (rc[1] - ry) * SS, (rc[0] + rx) * SS, (rc[1] + ry) * SS],
                  fill=(230, 236, 255, 58) if night else (60, 64, 76, 70))
        for f in (0.62, 0.86):
            d.arc([(rc[0] - rx * f) * SS, (rc[1] - ry * f) * SS, (rc[0] + rx * f) * SS, (rc[1] + ry * f) * SS], 200, 330,
                  fill=(240, 244, 255, 150) if night else (30, 32, 40, 150), width=max(1, int(s * 0.05 * SS)))
        # tail, fuselage in three bands, livery stripe, canopy
        self._poly(d, boom, mid)
        self._poly(d, fin, mid)
        self._poly(d, body, mid)
        self._poly(d, Q([(0.7, -0.78), (-0.2, -0.88), (-0.9, -0.62), (0.3, -0.56)]), lit)
        self._poly(d, Q([(-1.0, -0.22), (-0.5, 0.0), (0.6, 0.0), (0.9, -0.22)]), dark)
        self._poly(d, Q([(-0.95, -0.42), (0.95, -0.42), (0.98, -0.32), (-0.98, -0.32)]), (236, 240, 248))
        self._poly(d, Q([(-0.95, -0.36), (0.95, -0.36), (0.97, -0.32), (-0.97, -0.32)]), BLUE)
        canopy = Q([(1.0, -0.35), (0.7, -0.78), (0.32, -0.74), (0.46, -0.32)])
        self._poly(d, canopy, (110, 200, 236) if night else (90, 150, 190))
        self._poly(d, Q([(0.86, -0.5), (0.68, -0.72), (0.56, -0.7)]), (230, 250, 255))
        # skids, mast, tail rotor
        w = max(1.2, s * 0.08)
        line2(d, P(-0.75, 0.2), P(0.85, 0.2), w * 1.3, (16, 14, 20))
        for sx_ in (-0.45, 0.45):
            line2(d, P(sx_, 0.0), P(sx_ - 0.05, 0.2), w, (16, 14, 20))
        line2(d, P(-0.1, -0.88), rc, w * 1.2, (16, 14, 20))
        tr = P(-2.5, -0.68)
        d.ellipse([(tr[0] - 0.42 * s) * SS, (tr[1] - 0.42 * s) * SS, (tr[0] + 0.42 * s) * SS, (tr[1] + 0.42 * s) * SS],
                  fill=(230, 236, 255, 50) if night else (50, 54, 64, 60))
        # ink: silhouette thick, inner parts thinner
        ink_w = max(1.8, s * 0.11) * (1.25 if night else 1.0)
        toon.ink_poly(d, body, ink_w, ('hb', seed))
        toon.ink_poly(d, boom, ink_w * 0.8, ('hbm', seed))
        toon.ink_poly(d, fin, ink_w * 0.8, ('hf', seed))
        toon.ink_poly(d, canopy, ink_w * 0.6, ('hc', seed))
        # nav lights: red port, green starboard, white strobe on the fin, the searchlight under the belly
        r = max(2.0, s * 0.13)
        self.glow_dot(d, *P(-0.55, -0.45), RED, r)
        self.glow_dot(d, *P(0.62, -0.45), (60, 230, 110), r)
        self.glow_dot(d, *P(-2.6, -1.12), (255, 255, 255), r * 1.2)
        self.glow_dot(d, *P(0.0, 0.0), (250, 252, 255), r * 1.3)

    def drone(self, d, x, y, D, side, seed):
        """A quad-rotor drone, D px across, its belly light at (x, y)."""
        night = self.theme == 'night'
        if night:
            lit, mid, dark = hexc('#a8b4c8'), hexc('#6a7690'), hexc('#2c3446')
        else:
            lit, mid, dark = hexc('#dde2ea'), hexc('#97a2b2'), hexc('#4e586a')
        cy = y - D * 0.18
        if night:
            d.ellipse([(x - D * 0.75) * SS, (cy - D * 0.4) * SS, (x + D * 0.75) * SS, (cy + D * 0.4) * SS],
                      fill=(150, 170, 255, 40))
        arms = [(-0.5, -0.22), (0.5, -0.22), (-0.38, 0.12), (0.38, 0.12)]
        for ax_, ay_ in arms:
            line2(d, (x, cy), (x + ax_ * D, cy + ay_ * D), max(1.4, D * 0.07), (16, 14, 20))
        for ax_, ay_ in arms:
            rx, ry = D * 0.24, D * 0.08
            px, py = x + ax_ * D, cy + ay_ * D - D * 0.04
            d.ellipse([(px - rx) * SS, (py - ry) * SS, (px + rx) * SS, (py + ry) * SS],
                      fill=(230, 236, 255, 80) if night else (50, 54, 64, 80),
                      outline=(16, 14, 20), width=max(1, int(D * 0.03 * SS)))
        body = [(x - D * 0.24, cy), (x - D * 0.12, cy - D * 0.14), (x + D * 0.12, cy - D * 0.14), (x + D * 0.24, cy),
                (x + D * 0.12, cy + D * 0.13), (x - D * 0.12, cy + D * 0.13)]
        self._poly(d, body, mid)
        self._poly(d, body[:4], lit)
        self._poly(d, [body[0], body[3], body[4], body[5]], dark)
        toon.ink_poly(d, body, max(1.4, D * 0.07) * (1.2 if night else 1.0), ('db', seed))
        self.glow_dot(d, x + D * 0.1 * side, cy - D * 0.05, RED if seed % 2 else BLUE, max(1.8, D * 0.08))
        self.glow_dot(d, x, y, (250, 252, 255), max(1.6, D * 0.07))

    def draw_aircraft(self, img):
        v = self.v
        d = ImageDraw.Draw(img, 'RGBA')
        L = max(54.0, 38.0 * v.k)
        D = max(26.0, 15.5 * v.k)
        crafts = sorted(self.craft_list(), key=lambda c: c[1][1] - c[2])
        for kind, (tx, ty), alt, side, seed in crafts:
            ax, ay = self.craft_at(kind, tx, ty, alt, side)
            if kind == 'heli':
                self.heli(d, ax, ay, L, side, seed)
            else:
                self.drone(d, ax, ay, D, side, seed)
        return img

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
            ax, ay = self.craft_at(kind, tx, ty, hgt, side)
            r = (78 if kind == 'heli' else 40) * v.s
            left, right = (gx - r, gy), (gx + r, gy)
            facet(ld, bil([(ax - 2 * v.k, ay), (ax + 2 * v.k, ay), right, left]), 3, 6,
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
            pg.ellipse([(gx - 40 * v.k) * SS, (gy - 20 * v.k) * SS, (gx + 40 * v.k) * SS, (gy + 20 * v.k) * SS],
                       fill=(150, 160, 180) if night else (90, 95, 105))
        img = self.bloom(img, pglow, 16, 1.0 if night else 0.75)
        img = self.bloom(img, pglow, 60, 0.55 if night else 0.35)
        return img

    def finish(self, img):
        img = self.haze(img)
        if self.susp:
            img = self.draw_aircraft(img.convert('RGB'))
        return img

    def haze(self, img):
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
