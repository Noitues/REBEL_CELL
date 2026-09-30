"""The shared low-poly city (stills 01-03, and the combat backdrop).

A fixed, seeded city model (street grid, parcels, five landmarks) is projected with
an orthographic camera and drawn back-to-front; each visible face is a triangulated
quad whose triangle tones come from a ramp. The theme ('day', 'night', 'alert') only
changes colours and adds overlays, so the three city stills share every triangle.
"""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, panel,
                     skew_rect, tri, gem, gradient, text, text_w, NEON)

# ------------------------------------------------------------------ layout
LOT_X, LOT_Y, ST = 5.0, 4.2, 1.8
NBX, NBY = 7, 4
LX = NBX * LOT_X + (NBX + 1) * ST
LY = NBY * LOT_Y + (NBY + 1) * ST
SLAB = 2.6  # slab thickness under the city


def lot_rect(bx, by):
    x0 = ST + bx * (LOT_X + ST)
    y0 = ST + by * (LOT_Y + ST)
    return x0, y0, x0 + LOT_X, y0 + LOT_Y


def inter(ix, iy):
    return ST / 2 + ix * (LOT_X + ST), ST / 2 + iy * (LOT_Y + ST)


class Cam:
    def __init__(self, az, el, S, ox, oy):
        self.ca, self.sa = math.cos(math.radians(az)), math.sin(math.radians(az))
        self.ce, self.se = math.cos(math.radians(el)), math.sin(math.radians(el))
        self.S, self.ox, self.oy = S, ox, oy
        self.d = (self.sa * self.ce, self.ca * self.ce, self.se)  # towards camera

    def p(self, x, y, z):
        rx = x * self.ca - y * self.sa
        ry = x * self.sa + y * self.ca
        return self.ox + rx * self.S, self.oy + (ry * self.se - z * self.ce) * self.S

    def depth(self, x, y):
        return x * self.sa + y * self.ca


def default_cam(scale=1.0, ox=40.0, oy=-10.0):
    az, el = 24.0, 38.0
    ca, sa = math.cos(math.radians(az)), math.sin(math.radians(az))
    se = math.sin(math.radians(el))
    width_u = LX * ca + LY * sa
    S = 1880.0 / width_u * scale * 0.86
    # centre the ground footprint horizontally, sit it low in frame
    rx_min, rx_max = -LY * sa, LX * ca
    cx = 960 - (rx_min + rx_max) / 2 * S + ox
    ry_max = LX * sa + LY * ca
    oy_ = 1040 - (ry_max * se) * S - SLAB * 0.55 * S + oy
    return Cam(az, el, S, cx, oy_)


LIGHT = (-0.45, 0.55, 0.78)
_l = math.sqrt(sum(c * c for c in LIGHT))
LIGHT = tuple(c / _l for c in LIGHT)


def v_sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def v_dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def v_norm(a):
    l = math.sqrt(v_dot(a, a)) or 1.0
    return (a[0] / l, a[1] / l, a[2] / l)


def bil3(q, u, v):
    return tuple((1 - u) * (1 - v) * q[0][k] + u * (1 - v) * q[1][k] + u * v * q[2][k] + (1 - u) * v * q[3][k]
                 for k in range(3))


# ------------------------------------------------------------------ themes
DAY_FAM = {
    'warm': R('#2b0a24', '#6e1433', '#b8243a', '#e0473a', '#f07a3a', '#f6a94e', '#f9d98e'),
    'rose': R('#260a2e', '#5b1745', '#9c2552', '#d6435e', '#ef7a6e', '#f7b394', '#fbe1c0'),
    'gold': R('#3a1410', '#7a2b18', '#b8521e', '#e0862a', '#f2b544', '#f8d879', '#fcf0c0'),
    'teal': R('#0c1f33', '#153b52', '#1f6170', '#2f8f8f', '#5fbca8', '#a3dcc3', '#e2f4e0'),
    'plum': R('#1a0a26', '#3a1440', '#5e1f58', '#8a3066', '#b8506e', '#e08a7e', '#f6c8a0'),
}
NIGHT_FAM = {
    'warm': R('#05041a', '#0e0a2c', '#1c1242', '#2e1a58', '#48226c', '#6e2e7e', '#a04488'),
    'rose': R('#08031a', '#140828', '#261040', '#3c1656', '#5a1e68', '#842a78', '#b8448a'),
    'gold': R('#060818', '#10122c', '#1c1c40', '#2c2656', '#44306a', '#64407a', '#8e5a8a'),
    'teal': R('#020a1a', '#061630', '#0c2446', '#12365c', '#1a4e72', '#28708a', '#48a0a8'),
    'plum': R('#06041a', '#100a2a', '#1c1040', '#2a1652', '#3e1e64', '#5a2a74', '#843c84'),
}
ALERT_ALL = R('#040103', '#10030a', '#220612', '#380a1c', '#521026', '#701830', '#98283a')
ALERT_FAM = {k: ALERT_ALL for k in DAY_FAM}


def bg_day(u, v):
    top, bot = hexc('#7fb4a9'), hexc('#bba77e')
    base = mix(top, bot, v ** 1.2)
    e = abs(u - 0.45) * 2
    return mix(base, hexc('#18293a'), min(1, 0.75 * e ** 2.2 + 0.1 * v))


def bg_night(u, v):
    base = mix(hexc('#060920'), hexc('#241450'), v ** 0.9)
    base = mix(base, hexc('#4a1a5e'), max(0, v - 0.55) * 1.2)
    e = abs(u - 0.5) * 2
    return mix(base, hexc('#03040e'), min(1, 0.8 * e ** 2.4))


def bg_alert(u, v):
    base = mix(hexc('#100206'), hexc('#5a0a16'), v ** 0.9)
    base = mix(base, hexc('#8a1a22'), max(0, v - 0.6) * 1.1)
    e = abs(u - 0.5) * 2
    return mix(base, hexc('#050103'), min(1, 0.85 * e ** 2.2))


THEMES = {
    'day': dict(bg=bg_day, fam=DAY_FAM, tlo=0.14, thi=0.92,
                street=R('#1a1226', '#2c1d33', '#40293f', '#5a3a4a', '#7a5256'),
                lot=R('#3a2030', '#5e3040', '#8a4a4a', '#b0705a', '#d09a6e', '#e8c48c'),
                earth=R('#12071a', '#2a0c24', '#4d1330', '#7a1f36', '#a8303a'),
                plaza=DAY_FAM['teal'], night=False),
    'night': dict(bg=bg_night, fam=NIGHT_FAM, tlo=0.06, thi=0.62,
                  street=R('#04030e', '#0a0818', '#141026', '#1e1834', '#2a2044'),
                  lot=R('#06051a', '#0e0c28', '#181438', '#241c48', '#342656'),
                  earth=R('#020108', '#070414', '#0e0820', '#180c2c', '#261238'),
                  plaza=NIGHT_FAM['teal'], night=True),
    'alert': dict(bg=bg_alert, fam=ALERT_FAM, tlo=0.08, thi=0.66,
                  street=R('#030102', '#0a0206', '#16040c', '#240812', '#360c18'),
                  lot=R('#050103', '#0e0308', '#1a0510', '#2a0818', '#3c0c20'),
                  earth=R('#010001', '#050103', '#0c0206', '#16040a', '#22060e'),
                  plaza=ALERT_ALL, night=True),
}

WIN_NEON_NIGHT = ['magenta', 'cyan', 'amber', 'cyan', 'magenta', 'violet', 'lime']


# ------------------------------------------------------------------ model
def build_city():
    rng = random.Random(1977)
    items = []  # each: dict(depth, prims)
    special = {(5, 0): 'spire', (1, 0): 'zigg', (3, 1): 'dome', (6, 1): 'twins', (4, 2): 'billboard'}
    plazas = {(1, 3), (5, 3)}
    hrange = {0: (6.5, 11.0), 1: (3.8, 7.0), 2: (2.2, 4.2), 3: (0.8, 1.6)}
    fams = ['warm'] * 5 + ['rose'] * 2 + ['gold'] * 2 + ['teal'] * 2 + ['plum']
    bid = 0
    for by in range(NBY):
        for bx in range(NBX):
            x0, y0, x1, y1 = lot_rect(bx, by)
            key = (bx, by)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if key in plazas:
                items.append(dict(depth=-1e9, ground=True, prims=[('plaza', x0, y0, x1, y1, bid)]))
                bid += 1
                continue
            if key in special:
                kind = special[key]
                prims = []
                m = 0.5
                if kind == 'spire':
                    prims.append(('box', x0 + m, y0 + m, x1 - m, y1 - m, 0, 16.5, 'teal', 'cyan', 0.34, bid, False))
                    ix0, iy0 = x0 + m + (x1 - x0 - 2 * m) * 0.17, y0 + m + (y1 - y0 - 2 * m) * 0.17
                    ix1, iy1 = x1 - m - (x1 - x0 - 2 * m) * 0.17, y1 - m - (y1 - y0 - 2 * m) * 0.17
                    prims.append(('pyr', ix0, iy0, ix1, iy1, 16.5, 20.5, 'teal', bid + 1))
                    prims.append(('box', cx - 0.12, cy - 0.12, cx + 0.12, cy + 0.12, 20.0, 23.5, 'teal', None, 0, bid + 2, False))
                elif kind == 'zigg':
                    steps = [(0.3, 0, 4.6), (1.0, 4.6, 8.0), (1.6, 8.0, 10.6)]
                    for n, (ins, za, zb) in enumerate(steps):
                        prims.append(('box', x0 + ins, y0 + ins, x1 - ins, y1 - ins, za, zb, 'gold', 'amber', 0, bid + n, n == 0))
                    prims.append(('pyr', x0 + 1.9, y0 + 1.9, x1 - 1.9, y1 - 1.9, 10.6, 12.2, 'gold', bid + 5))
                elif kind == 'dome':
                    prims.append(('box', x0 + 0.4, y0 + 0.4, x1 - 0.4, y1 - 0.4, 0, 1.4, 'plum', 'violet', 0, bid, False))
                    prims.append(('dome', cx, cy, 1.4, 1.95, 'rose', bid + 1))
                    prims.append(('box', cx - 0.08, cy - 0.08, cx + 0.08, cy + 0.08, 3.2, 4.8, 'rose', None, 0, bid + 2, False))
                elif kind == 'twins':
                    mx = (x0 + x1) / 2
                    prims.append(('box', x0 + 0.4, y0 + 0.6, mx - 0.4, y1 - 0.6, 0, 13.0, 'rose', 'magenta', 0.08, bid, True))
                    prims.append(('box', mx - 0.4, cy - 0.4, mx + 0.4, cy + 0.4, 7.6, 8.6, 'plum', 'magenta', 0, bid + 1, False))
                    prims.append(('box', mx + 0.4, y0 + 0.6, x1 - 0.4, y1 - 0.6, 0, 11.2, 'rose', 'magenta', 0.08, bid + 2, False))
                elif kind == 'billboard':
                    prims.append(('box', x0 + 0.4, y0 + 0.5, x1 - 0.4, y1 - 0.5, 0, 3.4, 'warm', 'amber', 0, bid, False))
                    prims.append(('box', x0 + 1.1, cy - 0.1, x0 + 1.3, cy + 0.1, 3.4, 4.2, 'plum', None, 0, bid + 1, False))
                    prims.append(('box', x1 - 1.3, cy - 0.1, x1 - 1.1, cy + 0.1, 3.4, 4.2, 'plum', None, 0, bid + 2, False))
                    prims.append(('board', x0 + 0.7, x1 - 0.7, cy + 0.1, 4.0, 6.6, bid + 3))
                bid += 6
                items.append(dict(depth=0, box=(x0, y0, x1, y1), prims=prims))
                continue
            # ordinary parcels
            lo, hi = hrange[by]
            split = rng.choice([1, 2, 2, 4, 4])
            if split == 1:
                parcels = [(x0, y0, x1, y1)]
            elif split == 2:
                mx = x0 + LOT_X * rng.uniform(0.4, 0.6)
                parcels = [(x0, y0, mx, y1), (mx, y0, x1, y1)]
            else:
                mx = x0 + LOT_X * rng.uniform(0.4, 0.6)
                my = y0 + LOT_Y * rng.uniform(0.4, 0.6)
                parcels = [(x0, y0, mx, my), (mx, y0, x1, my), (x0, my, mx, y1), (mx, my, x1, y1)]
            for (a0, b0, a1, b1) in parcels:
                h = rng.uniform(lo, hi)
                if by == 0 and rng.random() < 0.3:
                    h *= 1.25
                fam = rng.choice(fams)
                win = rng.choice(WIN_NEON_NIGHT)
                ins = 0.28
                sign = h > 3.0 and rng.random() < 0.45
                taper = 0.0 if rng.random() < 0.8 else 0.12
                prims = [('box', a0 + ins, b0 + ins, a1 - ins, b1 - ins, 0, h, fam, win, taper, bid, sign)]
                if h > 5 and rng.random() < 0.5:  # rooftop block
                    w = (a1 - a0 - 2 * ins)
                    d = (b1 - b0 - 2 * ins)
                    prims.append(('box', a0 + ins + w * 0.25, b0 + ins + d * 0.25, a1 - ins - w * 0.3, b1 - ins - d * 0.3,
                                  h, h + rng.uniform(0.6, 1.4), fam, None, 0, bid + 1, False))
                items.append(dict(depth=0, box=(a0, b0, a1, b1), prims=prims))
                bid += 2
    return items


NODES = [
    ('home', (2, 3), 'home'),
    ('a', (4, 3), 'site'),
    ('b', (4, 2), 'target'),
    ('c', (7, 3), 'shop'),
    ('d', (2, 1), 'site'),
    ('e', (5, 1), 'target'),
    ('boss', (7, 1), 'boss'),
    ('f', (0, 2), 'target'),
]
EDGES = [
    [(2, 3), (4, 3)],
    [(4, 3), (4, 2)],
    [(4, 3), (7, 3)],
    [(2, 3), (2, 1)],
    [(2, 3), (2, 2), (0, 2)],
    [(4, 2), (4, 1), (5, 1)],
    [(5, 1), (7, 1)],
    [(7, 3), (7, 1)],
    [(2, 1), (0, 1), (0, 2)],
]
NODE_RAMP = {'home': NEON['cyan'], 'site': NEON['cyan'], 'target': NEON['magenta'], 'shop': NEON['lime'],
             'boss': NEON['red']}
PATH_RAMP = R('#6a3a08', '#b8700e', '#f0a820', '#ffd860', '#fff4c0')


# ------------------------------------------------------------------ drawing
class CityPainter:
    def __init__(self, img, cam, theme):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.cam = cam
        self.th = THEMES[theme]
        self.theme = theme

    # generic world quad, back-face culled, lambert tone
    def face(self, q, stops, seed, nu, nv, center=None, normal=None, colfac=None, gv=0.14, gu=0.0, var=0.07,
             tlo=None, thi=None, cull=True, jit=0.32):
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
        lam = max(0.0, v_dot(n, LIGHT))
        tlo = self.th['tlo'] if tlo is None else tlo
        thi = self.th['thi'] if thi is None else thi
        base = tlo + (thi - tlo) * (0.18 + 0.82 * lam)
        colfn = colfac(base) if colfac else toner(stops, base, gu, gv, var)
        cam = self.cam
        facet(self.d, lambda u, v: cam.p(*bil3(q, u, v)), nu, nv, colfn, seed, jit)
        return True

    # ---- ground
    def ground(self, items):
        th = self.th
        # slab sides
        q = [(0, LY, -SLAB), (LX, LY, -SLAB), (LX, LY, 0), (0, LY, 0)]
        self.face(q, th['earth'], 'slab_f', 30, 3, normal=(0, 1, 0), gv=0.25, gu=0.2, tlo=0.1, thi=0.95)
        q = [(LX, LY, -SLAB), (LX, 0, -SLAB), (LX, 0, 0), (LX, LY, 0)]
        self.face(q, th['earth'], 'slab_s', 14, 3, normal=(1, 0, 0), gv=0.25, tlo=0.2, thi=0.9)
        # street bed
        q = [(0, LY, 0), (LX, LY, 0), (LX, 0, 0), (0, 0, 0)]
        self.face(q, th['street'], 'street', 34, 16, normal=(0, 0, 1), gv=-0.2, gu=0.1, var=0.1,
                  tlo=0.15, thi=0.85)
        # lots (sidewalk pads)
        for by in range(NBY):
            for bx in range(NBX):
                x0, y0, x1, y1 = lot_rect(bx, by)
                q = [(x0, y1, 0.02), (x1, y1, 0.02), (x1, y0, 0.02), (x0, y0, 0.02)]
                self.face(q, th['lot'], ('lot', bx, by), 4, 3, normal=(0, 0, 1), var=0.09, tlo=0.2, thi=0.85)
        # plazas
        for it in items:
            for p in it['prims']:
                if p[0] == 'plaza':
                    self.plaza(*p[1:])

    def plaza(self, x0, y0, x1, y1, bid):
        th = self.th
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        q = [(x0 + 0.3, y1 - 0.3, 0.04), (x1 - 0.3, y1 - 0.3, 0.04), (x1 - 0.3, y0 + 0.3, 0.04), (x0 + 0.3, y0 + 0.3, 0.04)]
        self.face(q, th['plaza'], ('plz', bid), 5, 4, normal=(0, 0, 1), var=0.1, tlo=0.25, thi=0.8)
        # a faceted fountain / holo-plinth
        cam = self.cam
        r = 1.1
        if th['night']:
            st = NEON['cyan'] if self.theme == 'night' else NEON['red']
            cf = toner(st, 0.55, var=0.15, flip=0.2)
        else:
            cf = toner(DAY_FAM['warm'], 0.6, var=0.1)
        facet(self.d, lambda u, v: cam.p(cx + r * v * math.cos(u * 2 * math.pi), cy + r * v * math.sin(u * 2 * math.pi), 0.06),
              8, 2, cf, ('plzc', bid), 0.2, wrap_u=True)

    # ---- boxes
    def box(self, x0, y0, x1, y1, z0, z1, fam, win, taper, bid, sign):
        th = self.th
        stops = th['fam'][fam]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        tx = (x1 - x0) * taper / 2
        ty = (y1 - y0) * taper / 2
        h = z1 - z0
        w_x, w_y = x1 - x0, y1 - y0
        center = (cx, cy, (z0 + z1) / 2)
        top = [(x0 + tx, y1 - ty, z1), (x1 - tx, y1 - ty, z1), (x1 - tx, y0 + ty, z1), (x0 + tx, y0 + ty, z1)]
        front = [(x0, y1, z0), (x1, y1, z0), top[1], top[0]]
        side = [(x1, y1, z0), (x1, y0, z0), top[2], top[1]]
        nv = max(2, int(round(h / 1.0)))
        if nv % 2 == 1:
            nv += 1
        for name, q, wdt in (('f', front, w_x), ('s', side, w_y)):
            nu = max(2, int(round(wdt / 1.3)))
            colfac = self.facade_colfac(stops, bid, name, win, nv, nu) if win else None
            self.face(q, stops, (bid, name), nu, nv if win else max(1, nv // 2), center=center, colfac=colfac)
        self.face(top, stops, (bid, 't'), max(2, int(round(w_x / 1.3))), max(2, int(round(w_y / 1.3))),
                  center=center, gv=-0.1, gu=0.1)
        if sign and h > 3.0:
            self.sign(x0, x1, y1, z0, z1, bid)

    def facade_colfac(self, stops, bid, name, win, nv, nu):
        night = self.th['night']
        alert = self.theme == 'alert'

        def fac(base):
            def f(u, v, i, j, k, rc):
                t = base + 0.16 * (v - 0.5) + rc.uniform(-0.07, 0.07)
                if rc.random() < 0.1:
                    t += 0.16 if rc.random() < 0.5 else -0.16
                if j % 2 == 1 and j < nv - 1:
                    hv = hsh(bid, ord(name), i // 2, j)
                    if night:
                        lit_p = 0.62 if not alert else 0.5
                        if hv < lit_p:
                            if alert:
                                wn = 'red' if hsh(bid, 7) < 0.7 else 'amber'
                            else:
                                wn = win if hsh(bid, i, j, 3) < 0.8 else 'amber'
                            return ramp(NEON[wn], 0.35 + 0.6 * rc.random())
                        return ramp(stops, t - 0.1)
                    else:
                        if hv < 0.75:
                            return ramp(stops, t - 0.2)
                return ramp(stops, t)
            return f
        return fac

    def sign(self, x0, x1, y1, z0, z1, bid):
        """Vertical blade sign on the front face."""
        h = z1 - z0
        u0 = 0.1 + 0.5 * hsh(bid, 11)
        sx0 = x0 + (x1 - x0) * u0
        sx1 = sx0 + min(0.7, (x1 - x0) * 0.22)
        za, zb = z0 + h * 0.3, z0 + h * 0.85
        yy = y1 + 0.05
        q = [(sx0, yy, za), (sx1, yy, za), (sx1, yy, zb), (sx0, yy, zb)]
        if self.theme == 'night':
            st = NEON[['magenta', 'cyan', 'amber', 'lime'][int(hsh(bid, 5) * 4)]]
            cf = toner(st, 0.62, var=0.2, flip=0.25, famt=0.2)
        elif self.theme == 'alert':
            cf = toner(NEON['red'], 0.55, var=0.2, flip=0.25)
        else:
            cf = toner(DAY_FAM['teal'], 0.35, var=0.1, gv=0.2)
        cam = self.cam
        facet(self.d, lambda u, v: cam.p(*bil3(q, u, v)), 1, max(2, int((zb - za) / 0.6)), cf, ('sign', bid), 0.3)

    def pyr(self, x0, y0, x1, y1, z0, z1, fam, bid):
        stops = self.th['fam'][fam]
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ap = (cx, cy, z1)
        center = (cx, cy, z0 + (z1 - z0) * 0.3)
        base = [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)]
        for k in range(4):
            a, b = base[k], base[(k + 1) % 4]
            q = [a, b, ap, ap]
            self.face(q, stops, ('pyr', bid, k), 3, 3, center=center, gv=0.1)

    def dome(self, cx, cy, z0, r, fam, bid):
        stops = self.th['fam'][fam]
        nlat, nlon = 5, 16
        center = (cx, cy, z0)
        cam = self.cam
        for a in range(nlat):
            la0 = math.pi / 2 * a / nlat
            la1 = math.pi / 2 * (a + 1) / nlat
            for b in range(nlon):
                lo0 = 2 * math.pi * b / nlon
                lo1 = 2 * math.pi * (b + 1) / nlon

                def P(la, lo):
                    return (cx + r * math.cos(la) * math.cos(lo), cy + r * math.cos(la) * math.sin(lo), z0 + r * math.sin(la))
                q = [P(la0, lo0), P(la0, lo1), P(la1, lo1), P(la1, lo0)]
                lam_mid = ((la0 + la1) / 2, (lo0 + lo1) / 2)
                n = v_norm(v_sub(P(*lam_mid), center))
                if v_dot(n, cam.d) <= 0:
                    continue
                if self.th['night'] and (a == 1) and b % 2 == 0:
                    st = NEON['violet'] if self.theme == 'night' else NEON['red']
                    facet(self.d, lambda u, v, q=q: cam.p(*bil3(q, u, v)), 1, 1, toner(st, 0.6, var=0.15),
                          ('dm', bid, a, b), 0.0)
                    continue
                self.face(q, stops, ('dm', bid, a, b), 1, 1, normal=n, var=0.05, jit=0.0)

    def board(self, x0, x1, y, z0, z1, bid):
        cam = self.cam
        q = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
        # frame (thin back plate)
        self.face([(x0 - 0.15, y - 0.05, z0 - 0.15), (x1 + 0.15, y - 0.05, z0 - 0.15), (x1 + 0.15, y - 0.05, z1 + 0.15),
                   (x0 - 0.15, y - 0.05, z1 + 0.15)], self.th['fam']['plum'], ('bdf', bid), 2, 1, normal=(0, 1, 0))
        night = self.th['night']
        alert = self.theme == 'alert'

        def cf(u, v, i, j, k, rc):
            # an abstract eye glyph in triangles
            dx, dy = (u - 0.5) * 2, (v - 0.5) * 2
            inside = abs(dx) * 0.55 + abs(dy) < 0.62
            pupil = abs(dx) * 1.2 + abs(dy) < 0.42
            if alert:
                st = NEON['red'] if not pupil else NEON['amber']
                return ramp(st, (0.75 if pupil else (0.5 if inside else 0.25)) + rc.uniform(-0.15, 0.15))
            if night:
                st = NEON['magenta'] if not inside else NEON['cyan']
                if pupil:
                    st = NEON['amber']
                return ramp(st, 0.55 + rc.uniform(-0.25, 0.3))
            st = DAY_FAM['teal'] if not inside else DAY_FAM['gold']
            if pupil:
                st = DAY_FAM['warm']
            return ramp(st, 0.55 + rc.uniform(-0.15, 0.15))
        facet(self.d, lambda u, v: cam.p(*bil3(q, u, v)), 9, 4, cf, ('bd', bid), 0.3)

    def item(self, it):
        for p in it['prims']:
            kind = p[0]
            if kind == 'box':
                self.box(*p[1:])
            elif kind == 'pyr':
                self.pyr(*p[1:])
            elif kind == 'dome':
                self.dome(*p[1:])
            elif kind == 'board':
                self.board(*p[1:])

    # ---- overlay on the ground plane
    def ribbon(self, a, b, w, stops, seed, z=0.05, base=0.55):
        ax, ay = a
        bx, by = b
        L = math.hypot(bx - ax, by - ay)
        dx, dy = (bx - ax) / L, (by - ay) / L
        px, py = -dy * w, dx * w
        q = [(ax - px, ay - py, z), (bx - px, by - py, z), (bx + px, by + py, z), (ax + px, ay + py, z)]
        cam = self.cam
        facet(self.d, lambda u, v: cam.p(*bil3(q, u, v)), max(2, int(L / 0.9)), 1,
              toner(stops, base, gu=0.0, var=0.12, flip=0.15), seed, 0.35)

    def paths(self):
        pr = PATH_RAMP
        for n, e in enumerate(EDGES):
            pts = [inter(*p) for p in e]
            for k in range(len(pts) - 1):
                a, b = pts[k], pts[k + 1]
                # extend by half width so corners close
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                a2 = (a[0] - dx * 0.3, a[1] - dy * 0.3)
                b2 = (b[0] + dx * 0.3, b[1] + dy * 0.3)
                self.ribbon(a2, b2, 0.3, pr, ('path', n, k))

    def node_discs(self):
        cam = self.cam
        for name, ij, kind in NODES:
            x, y = inter(*ij)
            r = 1.35 if kind == 'home' else 1.0
            st = NODE_RAMP[kind]
            ringst = R('#0a0a14', '#1a1a2a', '#2c2c40', '#44445a')
            facet(self.d, lambda u, v: cam.p(x + r * (1 + 0.28 * v) * math.cos(u * 2 * math.pi),
                                             y + r * (1 + 0.28 * v) * math.sin(u * 2 * math.pi), 0.07),
                  6, 1, toner(ringst, 0.5, var=0.2), ('ndr', name), 0.0, wrap_u=True)
            facet(self.d, lambda u, v: cam.p(x + r * v * math.cos(u * 2 * math.pi), y + r * v * math.sin(u * 2 * math.pi), 0.08),
                  6, 2, toner(st, 0.62, var=0.14, flip=0.25, famt=0.2), ('nd', name), 0.15, wrap_u=True)

    def traffic(self):
        """Night: streams of tiny headlight / taillight triangles on the streets."""
        rng = random.Random(4242)
        cam = self.cam
        alert = self.theme == 'alert'
        head = NEON['amber'] if not alert else NEON['red']
        tail = NEON['red'] if not alert else NEON['amber']
        lanes = []
        for iy in range(NBY + 1):
            x0, y = inter(0, iy)
            lanes.append(((0.3, y - 0.35), (LX - 0.3, y - 0.35), head))
            lanes.append(((LX - 0.3, y + 0.35), (0.3, y + 0.35), tail))
        for ix in range(NBX + 1):
            x, _ = inter(ix, 0)
            lanes.append(((x + 0.35, 0.3), (x + 0.35, LY - 0.3), head))
            lanes.append(((x - 0.35, LY - 0.3), (x - 0.35, 0.3), tail))
        for (a, b, st) in lanes:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            s = rng.uniform(0, 1.5)
            while s < L:
                cx, cy = a[0] + dx * s, a[1] + dy * s
                ln = rng.uniform(0.35, 0.6)
                pw = 0.16
                p1 = cam.p(cx + dx * ln, cy + dy * ln, 0.1)
                p2 = cam.p(cx - dy * pw, cy + dx * pw, 0.1)
                p3 = cam.p(cx + dy * pw, cy - dx * pw, 0.1)
                p0 = cam.p(cx - dx * ln * 0.8, cy - dy * ln * 0.8, 0.1)
                tri(self.d, [p1, p2, p3], ramp(st, rng.uniform(0.6, 0.95)))
                tri(self.d, [p2, p3, p0], ramp(st, rng.uniform(0.3, 0.55)))
                s += rng.uniform(1.8, 4.6)

    # ---- UI layer (always on top)
    def arrows(self):
        cam = self.cam
        for n, e in enumerate(EDGES):
            pts = [inter(*p) for p in e]
            for k in range(len(pts) - 1):
                a, b = pts[k], pts[k + 1]
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                s = 1.7
                while s < L - 1.4:
                    cx, cy = a[0] + dx * s, a[1] + dy * s
                    tip = cam.p(cx + dx * 0.34, cy + dy * 0.34, 0.1)
                    l = cam.p(cx - dx * 0.22 - dy * 0.26, cy - dy * 0.22 + dx * 0.26, 0.1)
                    r = cam.p(cx - dx * 0.22 + dy * 0.26, cy - dy * 0.22 - dx * 0.26, 0.1)
                    m = cam.p(cx - dx * 0.08, cy - dy * 0.08, 0.1)
                    tri(self.d, [tip, l, m], ramp(PATH_RAMP, 0.95))
                    tri(self.d, [tip, m, r], ramp(PATH_RAMP, 0.72))
                    s += 1.25

    def pins(self):
        cam = self.cam
        order = sorted(NODES, key=lambda n: cam.depth(*inter(*n[1])))
        for name, ij, kind in order:
            x, y = inter(*ij)
            big = kind == 'home'
            hz = 3.4 if big else 2.6
            rr = 0.95 if big else 0.62
            st = NODE_RAMP[kind]
            if big:
                st = R('#0a4a6a', '#18a8d0', '#6ff4ff', '#e6ffff', '#ffffff')
            # stem
            b0 = cam.p(x, y, 0.1)
            t0 = cam.p(x, y, hz)
            wpx = 3.0 if big else 2.2
            tri(self.d, [(b0[0] - wpx, b0[1]), (t0[0], t0[1]), (b0[0] + wpx, b0[1])], ramp(st, 0.5))
            tri(self.d, [(b0[0], b0[1]), (t0[0], t0[1]), (b0[0] + wpx, b0[1])], ramp(st, 0.3))
            # octahedron crystal
            c = (x, y, hz + rr * 1.3)
            top = (x, y, hz + rr * 2.8)
            bot = (x, y, hz)
            eq = [(x + rr * math.cos(a), y + rr * math.sin(a), hz + rr * 1.3) for a in
                  [math.radians(-24 + 90 * k) for k in range(4)]]
            for k in range(4):
                a, b = eq[k], eq[(k + 1) % 4]
                for apex, sd in ((top, 't'), (bot, 'b')):
                    q = [a, b, apex, apex]
                    self.face(q, st, ('pin', name, k, sd), 2, 2, center=c, tlo=0.2, thi=1.0, var=0.05, jit=0.2)
            if kind == 'boss':
                # spikes crown for the boss node
                pt = cam.p(*top)
                for s in (-1, 1):
                    tri(self.d, [(pt[0] + s * 6, pt[1] + 6), (pt[0] + s * 20, pt[1] - 18), (pt[0] + s * 13, pt[1] + 10)],
                        ramp(st, 0.8 if s < 0 else 0.5))
            if big:
                pt = cam.p(*top)
                self.label_you(pt[0], pt[1] - 14)

    def label_you(self, x, y):
        w, h = 214, 44
        q = skew_rect(x - w / 2, y - h - 16, w, h, 10)
        panel(self.d, q, R('#062a3a', '#0a4a64', '#1080a0', '#20b8d0', '#8ff4ff'), 0.72, 'youlbl', nu=7, nv=2, gv=-0.25)
        tri(self.d, [(x - 12, y - 16.5), (x + 12, y - 16.5), (x, y)], ramp(NEON['cyan'], 0.75))
        tri(self.d, [(x, y - 16.5), (x + 12, y - 16.5), (x, y)], ramp(NEON['cyan'], 0.5))
        text(self.d, x + 5, y - 16 - h / 2, 'YOU ARE HERE', 23, hexc('#04121c'), anchor='mm')


def city_hud(d, theme):
    alert = theme == 'alert'
    night = theme != 'day'
    level = {'day': 1, 'night': 2, 'alert': 5}[theme]
    plate = R('#08060e', '#120e1e', '#1e1830', '#2c2442', '#3c3054')
    if alert:
        plate = R('#080204', '#16040a', '#260812', '#380c1a', '#4a1022')
    # title plate
    panel(d, skew_rect(36, 30, 470, 128, 16), plate, 0.5, 'hud_title', nu=8, nv=3, gv=-0.3)
    text(d, 66, 44, 'KANAL WARD', 34, hexc('#f9e3b0'), style='Bold')
    text(d, 66, 84, 'SECTOR 9 // NIGHT SHIFT' if night else 'SECTOR 9 // DAY CYCLE', 17, hexc('#a89cc0'), style='SemiBold')
    text(d, 66, 114, 'SUSPICION', 18, hexc('#f0d8c8'), style='Bold')
    for k in range(5):
        x = 190 + k * 58
        on = k < level
        st = NEON['red'] if alert else (NEON['amber'] if k < 3 else NEON['red'])
        if not on:
            st = R('#14101c', '#221c30', '#302840', '#3e3450')
        q = [(x + 10, 110), (x + 52, 110), (x + 42, 138), (x, 138)]
        panel(d, q, st, 0.6 if on else 0.4, ('susp', k, theme), nu=3, nv=1, gv=-0.3, var=0.1)
    # legend
    lx, ly = 40, 958
    panel(d, skew_rect(lx, ly, 560, 86, 12), plate, 0.45, 'hud_leg', nu=8, nv=2, gv=-0.3)
    entries = [('TARGET', 'target'), ('SITE', 'site'), ('SHOP', 'shop'), ('BOSS', 'boss')]
    for k, (lab, kind) in enumerate(entries):
        x = lx + 38 + k * 134
        gem(d, x, ly + 43, 15, 20, NODE_RAMP[kind], ('lg', kind), n=4, base=0.6)
        text(d, x + 24, ly + 43, lab, 20, hexc('#efe0d0'), anchor='lm')
    if alert:
        bw = 640
        q = skew_rect(960 - bw / 2 + 60, 34, bw, 70, -18)
        panel(d, q, NEON['red'], 0.45, 'alertbanner', nu=10, nv=2, gv=-0.3, var=0.1, flip=0.2)
        text(d, 960 + 60, 69, 'LOCKDOWN  //  SWEEP IN PROGRESS', 32, hexc('#fff0e0'), anchor='mm', shadow=hexc('#3a0408'))


def render_city(theme, overlay=True, hud=True, cam=None):
    th = THEMES[theme]
    img = gradient(th['bg']).convert('RGB')
    cam = cam or default_cam()
    cp = CityPainter(img, cam, theme)
    items = build_city()
    cp.ground(items)
    if th['night']:
        cp.traffic()
    if overlay:
        cp.paths()
        cp.node_discs()
    solids = [it for it in items if 'box' in it]
    for it in solids:
        x0, y0, x1, y1 = it['box']
        it['depth'] = cam.depth((x0 + x1) / 2, (y0 + y1) / 2)
    solids.sort(key=lambda it: it['depth'])
    for it in solids:
        cp.item(it)
    if theme == 'alert':
        import alert_fx
        img = alert_fx.apply(img, cam, cp, items)
        cp.img = img
        cp.d = ImageDraw.Draw(img)
    if overlay:
        cp.arrows()
        cp.pins()
    if hud:
        city_hud(cp.d, theme)
    return cp.img
