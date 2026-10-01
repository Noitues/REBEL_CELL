"""E's cel shading on C v2's gritty DAY city.

Same city model, camera, facet density and overlay as r2c_geo_vector_gritty/01_city_day. Only the
rendering treatment changes:
  - banded toon light: every face is quantised into 3 tone steps (lit / mid / shadow) from one light
    direction; triangles keep a small variation inside their band; shadows cool, lit faces warm;
  - hand-drawn ink: thick wobbly silhouette outlines per building / prop (convex hull of the projected
    primitive), thinner lines on the visible interior edges, heavy outline on the slab;
  - bevel highlights along lit top edges;
  - hand-painted grime: rust streaks down from roof edges, water stains, chipped paint (solid,
    painter-ordered), then a painterly speckle / brush texture over the scene (not the UI).
Usage: python toon.py   (writes ../city_day.png)
"""
import math
import os
import random
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from PIL import Image, ImageDraw, ImageChops
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, skew_rect, tri, gradient, line2, smog,
                     rain, finalize, NEON)
import city
from city import (CityPainter, THEMES, FAM, LIGHT, SLAB, LX, LY, lot_rect, NBX, NBY, build_city, default_cam,
                  city_hud, v_sub, v_cross, v_dot, v_norm, bil3)

INK = hexc('#15110f')
WARM = hexc('#f2c88e')
COOL = hexc('#343468')
BANDS = (0.34, 0.56, 0.78)       # shadow / mid / lit ramp positions
TINT = ((COOL, 0.22), (WARM, 0.05), (WARM, 0.16))
BEVEL = hexc('#f6e2b4')


def band_of(lam):
    return 2 if lam > 0.55 else (1 if lam > 0.22 else 0)


def tint(col, band):
    c, a = TINT[band]
    return col if c is None else mix(col, c, a)


def hull(pts):
    pts = sorted(set((round(p[0], 3), round(p[1], 3)) for p in pts))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, up = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(up) >= 2 and cross(up[-2], up[-1], p) <= 0:
            up.pop()
        up.append(p)
    return lo[:-1] + up[:-1]


def ink_line(d, a, b, w, seed, col=INK):
    """A slightly wobbly, hand-drawn ink stroke with round joints."""
    rng = random.Random(str(seed))
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L < 0.5:
        return
    n = max(1, int(L / 22))
    nx, ny = -(b[1] - a[1]) / L, (b[0] - a[0]) / L
    pts = []
    for k in range(n + 1):
        t = k / n
        j = 0.0 if k in (0, n) else rng.uniform(-0.8, 0.8)
        pts.append((a[0] + (b[0] - a[0]) * t + nx * j, a[1] + (b[1] - a[1]) * t + ny * j))
    for k in range(n):
        ww = w * rng.uniform(0.85, 1.15)
        line2(d, pts[k], pts[k + 1], ww, col)
        x, y = pts[k + 1]
        r = ww / 2
        d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=col)
    x, y = pts[0]
    r = w / 2
    d.ellipse([(x - r) * SS, (y - r) * SS, (x + r) * SS, (y + r) * SS], fill=col)


def ink_poly(d, pts, w, seed, closed=True):
    m = len(pts)
    for k in range(m if closed else m - 1):
        ink_line(d, pts[k], pts[(k + 1) % m], w, (seed, k))


class ToonPainter(CityPainter):
    def __init__(self, img, cam, theme):
        super().__init__(img, cam, theme)
        self.toon = True

    # ---- banded light
    def face(self, q, stops, seed, nu, nv, center=None, normal=None, colfac=None, gv=0.14, gu=0.0, var=0.07,
             tlo=None, thi=None, cull=True, jit=0.32, d=None):
        if not self.toon:
            return super().face(q, stops, seed, nu, nv, center, normal, colfac, gv, gu, var, tlo, thi, cull, jit, d)
        if normal is None:
            n = v_norm(v_cross(v_sub(q[1], q[0]), v_sub(q[3], q[0])))
            if v_dot(n, n) < 0.5:
                n = v_norm(v_cross(v_sub(q[2], q[1]), v_sub(q[0], q[1])))
            if center is not None:
                mid = bil3(q, 0.5, 0.5)
                if v_dot(n, v_sub(mid, center)) < 0:
                    n = (-n[0], -n[1], -n[2])
        else:
            n = normal
        if cull and v_dot(n, self.cam.d) <= 1e-6:
            return False
        band = band_of(v_dot(n, LIGHT))
        base = BANDS[band]
        inner = colfac(base) if colfac else toner(stops, base, gu * 0.25, gv * 0.25, 0.035, flip=0.03)

        def colfn(u, v, i, j, k, rc):
            c = inner(u, v, i, j, k, rc)
            return None if c is None else tint(c, band)
        cam = self.cam
        facet(d or self.d, lambda u, v: cam.p(*bil3(q, u, v)), nu, nv, colfn, seed, jit)
        self.last_band = band
        return True

    def facade_colfac(self, stops, bid, name, win, nv, grime):
        """v2's facade shading with the vertical gradient flattened so it stays inside its band."""
        rust = FAM['rust']

        def fac(base):
            def f(u, v, i, j, k, rc):
                t = base + 0.07 * (v - 0.5) + rc.uniform(-0.035, 0.035)
                if grime:
                    s = hsh(bid, ord(name), i, 91)
                    if s < 0.35 and v < 0.35 + s * 1.7:
                        t -= 0.06
                if win and j % 2 == 1 and j < nv - 1 and hsh(bid, ord(name), i, j) < 0.8:
                    return ramp(stops, t - 0.14)
                return ramp(stops, t)
            return f
        return fac

    # ---- ink, bevels and grime per primitive
    def box(self, p):
        super().box(p)
        cam = self.cam
        x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
        tx = (x1 - x0) * p['taper'] / 2
        ty = (y1 - y0) * p['taper'] / 2
        top = [(x0 + tx, y1 - ty, z1), (x1 - tx, y1 - ty, z1), (x1 - tx, y0 + ty, z1), (x0 + tx, y0 + ty, z1)]
        bot = [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)]
        big = (z1 - z0) > 1.2 and max(x1 - x0, y1 - y0) > 0.6
        stops = self.th['fam'][p['fam']]
        if big and p['grime']:
            self.grime(p, top, stops)
        tp = [cam.p(*c) for c in top]
        bp = [cam.p(*c) for c in bot]
        # bevel highlight along the lit top edges (front and side)
        if big:
            for a, b in ((tp[0], tp[1]), (tp[1], tp[2])):
                line2(self.d, (a[0], a[1] + 3.2), (b[0], b[1] + 3.2), 2.0, BEVEL)
            line2(self.d, (tp[3][0], tp[3][1] + 3), (tp[0][0], tp[0][1] + 3), 1.6, mix(BEVEL, WARM, 0.4))
        # interior visible edges: thinner ink
        wi = 1.9 if big else 1.2
        ink_line(self.d, tp[0], tp[1], wi, (p['bid'], 'e1'))
        ink_line(self.d, tp[1], tp[2], wi, (p['bid'], 'e2'))
        ink_line(self.d, bp[1], tp[1], wi, (p['bid'], 'e3'))
        # silhouette: thick
        ink_poly(self.d, hull(tp + bp), 4.0 if big else 2.2, (p['bid'], 'sil'))

    def grime(self, p, top, stops):
        """Hand-painted rust streaks, water stains and chipped paint on the visible walls."""
        cam = self.cam
        rng = random.Random(str(('grime', p['bid'])))
        x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
        h = z1 - z0
        rust = hexc('#5e3018')
        faces = (('f', lambda u, z: (x0 + (x1 - x0) * u, y1 + 0.01, z), x1 - x0, 1),
                 ('s', lambda u, z: (x1 + 0.01, y1 - (y1 - y0) * u, z), y1 - y0, 0))
        for name, P, width, band in faces:
            base = tint(ramp(stops, BANDS[band]), band)
            # rust streaks from the roof edge and from ledges
            for k in range(max(1, int(width * 1.4))):
                u = rng.uniform(0.06, 0.94)
                zt = z1 - 0.05 if rng.random() < 0.6 else z0 + h * rng.uniform(0.3, 0.8)
                ln = h * rng.uniform(0.18, 0.55)
                wd = rng.uniform(0.05, 0.12) / max(width, 0.1)
                c = mix(base, rust, rng.uniform(0.5, 0.72))
                tri(self.d, [cam.p(*P(u - wd, zt)), cam.p(*P(u + wd, zt)), cam.p(*P(u + rng.uniform(-0.02, 0.02), zt - ln))], c)
                tri(self.d, [cam.p(*P(u - wd * 0.5, zt)), cam.p(*P(u + wd * 0.4, zt)),
                             cam.p(*P(u, zt - ln * 0.55))], mix(base, rust, 0.75))
            # water stain near the base
            if rng.random() < 0.6:
                u0 = rng.uniform(0.15, 0.85)
                zc = z0 + h * rng.uniform(0.05, 0.25)
                pts = []
                for m in range(7):
                    a = 2 * math.pi * m / 7
                    r = rng.uniform(0.18, 0.35)
                    pts.append(cam.p(*P(u0 + math.cos(a) * r / max(width, 0.1), zc + math.sin(a) * r * 0.8)))
                pp = [(q[0] * SS, q[1] * SS) for q in pts]
                c = mix(base, hexc('#1a1814'), 0.22)
                self.d.polygon(pp, fill=c, outline=c)
            # chipped paint flecks near the corners
            for k in range(rng.randint(2, 5)):
                u = rng.choice([rng.uniform(0.0, 0.12), rng.uniform(0.88, 1.0)])
                z = z0 + h * rng.uniform(0.1, 0.95)
                s = rng.uniform(0.06, 0.12)
                c = mix(base, hexc('#d8ccb0'), 0.45)
                tri(self.d, [cam.p(*P(u, z)), cam.p(*P(min(1, u + s / max(width, .1)), z - s * 0.4)),
                             cam.p(*P(u + s * 0.3 / max(width, .1), z - s))], c)

    def pyr(self, p):
        super().pyr(p)
        cam = self.cam
        x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
        pts = [cam.p(x, y, z0) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
        apex = cam.p((x0 + x1) / 2, (y0 + y1) / 2, z1)
        ink_line(self.d, cam.p(x1, y1, z0), apex, 1.8, (p['bid'], 'pe'))
        ink_line(self.d, cam.p(x0, y1, z0), apex, 1.8, (p['bid'], 'pe2'))
        ink_poly(self.d, hull(pts + [apex]), 4.0, (p['bid'], 'psil'))

    def dome(self, p):
        super().dome(p)
        cam = self.cam
        pts = []
        for a in range(0, 6):
            la = math.pi / 2 * a / 5
            for b in range(24):
                lo = 2 * math.pi * b / 24
                pts.append(cam.p(p['cx'] + p['r'] * math.cos(la) * math.cos(lo),
                                 p['cy'] + p['r'] * math.cos(la) * math.sin(lo), p['z0'] + p['r'] * math.sin(la)))
        ink_poly(self.d, hull(pts), 3.6, (p['bid'], 'dsil'))

    def board(self, p):
        super().board(p)
        cam = self.cam
        x0, x1, y, z0, z1 = p['x0'] - 0.15, p['x1'] + 0.15, p['y'], p['z0'] - 0.2, p['z1'] + 0.15
        pts = [cam.p(x0, y, z0), cam.p(x1, y, z0), cam.p(x1, y, z1), cam.p(x0, y, z1)]
        ink_poly(self.d, pts, 3.6, (p['bid'], 'bsil'))

    def signs(self, p):
        super().signs(p)

    def ground(self, items):
        self.toon = True
        super().ground(items)
        cam = self.cam
        # heavy ink round the slab, thin ink on the lot kerbs
        corners = [cam.p(x, y, z) for x in (0, LX) for y in (0, LY) for z in (0, -SLAB)]
        ink_poly(self.d, hull(corners), 5.0, 'slab')
        ink_line(self.d, cam.p(0, LY, 0), cam.p(LX, LY, 0), 2.4, 'slab_lip1')
        ink_line(self.d, cam.p(LX, LY, 0), cam.p(LX, 0, 0), 2.4, 'slab_lip2')
        ink_line(self.d, cam.p(LX, LY, 0), cam.p(LX, LY, -SLAB), 2.4, 'slab_lip3')
        for by in range(NBY):
            for bx in range(NBX):
                x0, y0, x1, y1 = lot_rect(bx, by)
                pts = [cam.p(x0, y0, 0.02), cam.p(x1, y0, 0.02), cam.p(x1, y1, 0.02), cam.p(x0, y1, 0.02)]
                ink_poly(self.d, pts, 1.4, ('lot', bx, by))

    def pins(self):
        self.toon = False
        super().pins()
        self.toon = True

    def label_you(self, x, y):
        super().label_you(x, y)
        w, h = 214, 44
        ink_poly(self.d, skew_rect(x - w / 2, y - h - 16, w, h, 10), 3.2, 'you_ink')


def paint_texture(img, seed=('paint', 1)):
    """Painterly speckle + soft brush blotches, applied with an overlay blend (mean-neutral)."""
    rng = random.Random(str(seed))
    fw, fh = 960, 540
    fine = Image.frombytes('L', (fw, fh), bytes(rng.randrange(112, 146) for _ in range(fw * fh)))
    fine = fine.resize(img.size, Image.BILINEAR)
    cw, ch = 160, 90
    blot = Image.frombytes('L', (cw, ch), bytes(rng.randrange(106, 150) for _ in range(cw * ch)))
    blot = blot.resize((cw * 3, ch), Image.BICUBIC).resize(img.size, Image.BICUBIC)  # horizontal brush drag
    tex = Image.blend(fine, blot, 0.55).convert('RGB')
    return ImageChops.overlay(img, tex)


def render():
    th = THEMES['day']
    img = gradient(th['bg']).convert('RGB')
    cam = default_cam()
    cp = ToonPainter(img, cam, 'day')
    cp.skyline()
    cp.img = smog(cp.img, ('far', 'day'), [(520, 200, 70, 150), (760, 340, 150, 230)], th['smog'])
    cp.d = ImageDraw.Draw(cp.img)
    items = build_city()
    cp.ground(items)
    cp.paths()
    cp.node_discs()
    for it in items:
        x0, y0, x1, y1 = it['box']
        it['depth'] = cam.depth((x0 + x1) / 2, (y0 + y1) / 2)
    items.sort(key=lambda it: (it['depth'], it['box']))
    for it in items:
        cp.item(it)
    cp.cables(items)
    img = paint_texture(cp.img)
    img = smog(img, ('near', 'day'), [(110, 130, 40, 100), (330, 160, 40, 100), (640, 180, 50, 110)], th['smog'])
    img = rain(img, 'rain_day', n=700, col=(150, 150, 140), alpha=(30, 70))
    cp.img = img
    cp.d = ImageDraw.Draw(img)
    cp.arrows()
    cp.pins()
    city_hud(cp.d, 'day')
    ink_poly(cp.d, skew_rect(36, 30, 470, 128, 16), 3.6, 'hud_ink')
    ink_poly(cp.d, skew_rect(40, 958, 560, 86, 12), 3.6, 'leg_ink')
    return cp.img


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(HERE), 'city_day.png')
    finalize(render()).save(out, optimize=True)
    print('wrote', out)
