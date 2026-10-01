"""The shared gritty low-poly megacity (stills 01-03).

A fixed seeded model (stacked mega-blocks, corp towers over a slum front row, walkways,
pipes, rooftop clutter, signs, cameras) is projected orthographically and drawn
back-to-front as triangulated faces toned from dirty ramps. The theme ('day', 'night',
'alert') only swaps ramps and adds overlays, so the three city stills share every
triangle.
"""
import math
import random
from PIL import Image, ImageDraw
from lowpoly import (SS, W, H, R, hexc, mix, ramp, hsh, toner, facet, bil, polar, panel, skew_rect, tri, gem,
                     gradient, text, text_w, NEON, line2, catenary, layer, composite, rain, smog)

# ------------------------------------------------------------------ layout
LOT_X, LOT_Y, ST = 5.0, 4.2, 1.8
NBX, NBY = 7, 4
LX = NBX * LOT_X + (NBX + 1) * ST
LY = NBY * LOT_Y + (NBY + 1) * ST
SLAB = 2.6


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
        self.d = (self.sa * self.ce, self.ca * self.ce, self.se)

    def p(self, x, y, z):
        rx = x * self.ca - y * self.sa
        ry = x * self.sa + y * self.ca
        return self.ox + rx * self.S, self.oy + (ry * self.se - z * self.ce) * self.S

    def depth(self, x, y):
        return x * self.sa + y * self.ca


def default_cam():
    az, el = 24.0, 38.0
    ca, sa = math.cos(math.radians(az)), math.sin(math.radians(az))
    se = math.sin(math.radians(el))
    S = 1880.0 / (LX * ca + LY * sa) * 0.74
    rx_min, rx_max = -LY * sa, LX * ca
    cx = 960 - (rx_min + rx_max) / 2 * S + 40
    ry_max = LX * sa + LY * ca
    oy = 1040 - ry_max * se * S - SLAB * 0.55 * S
    return Cam(az, el, S, cx, oy)


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


# ------------------------------------------------------------------ palettes
FAM = {
    'soot': R('#0a0c12', '#161a24', '#262b36', '#3a3f48', '#52555a', '#6e6d68', '#918b7e'),
    'rust': R('#120806', '#26120c', '#3e1e14', '#5a2c1a', '#764226', '#946040', '#b08766'),
    'oily': R('#070e10', '#10201f', '#1b3030', '#2a4441', '#3e5a55', '#5a746a', '#80927f'),
    'concrete': R('#111110', '#20201e', '#33322d', '#48463f', '#615e55', '#7e796d', '#a19a8a'),
    'corp': R('#05070d', '#0c121d', '#152032', '#223246', '#34485e', '#4e6478', '#74889a'),
    'brick': R('#100806', '#221210', '#381c18', '#4e2822', '#66382e', '#80503f', '#9c6e58'),
}


def tinted(fams, col, amt):
    c = hexc(col)
    return {k: [mix(s, c, amt) for s in v] for k, v in fams.items()}


NIGHT_FAM = tinted(FAM, '#04050c', 0.35)
ALERT_FAM = tinted(FAM, '#2a0408', 0.3)


def bg_day(u, v):
    base = mix(hexc('#6e6a58'), hexc('#a89c74'), v ** 1.3)
    base = mix(base, hexc('#b8a878'), max(0.0, 1 - abs(v - 0.62) * 3) * 0.35)
    e = abs(u - 0.5) * 2
    return mix(base, hexc('#23231e'), min(1, 0.7 * e ** 2.0 + 0.08))


def bg_night(u, v):
    base = mix(hexc('#04050a'), hexc('#161822'), v ** 0.8)
    base = mix(base, hexc('#3a2616'), max(0, v - 0.55) * 0.9)
    e = abs(u - 0.5) * 2
    return mix(base, hexc('#020204'), min(1, 0.8 * e ** 2.2))


def bg_alert(u, v):
    base = mix(hexc('#0a0204'), hexc('#3e0a12'), v ** 0.9)
    base = mix(base, hexc('#5a1018'), max(0, v - 0.6) * 1.0)
    e = abs(u - 0.5) * 2
    return mix(base, hexc('#030102'), min(1, 0.85 * e ** 2.2))


THEMES = {
    'day': dict(bg=bg_day, fam=FAM, tlo=0.12, thi=0.86,
                street=R('#0e0e10', '#1a1a1c', '#2a2a2a', '#3c3b38', '#5a5850', '#8a8676'),
                lot=R('#161512', '#26241f', '#38352e', '#4c4840', '#625d52'),
                earth=R('#0a0806', '#16100c', '#241a12', '#34261a', '#463422'),
                sky=R('#4a4838', '#6e6a52', '#8e8666', '#aaa07a'),
                skyline=R('#3a3a32', '#48463c', '#565244', '#64604e'),
                smog=R('#4a4632', '#6a6448', '#8a8260', '#a49a74'), night=False),
    'night': dict(bg=bg_night, fam=NIGHT_FAM, tlo=0.08, thi=0.6,
                  street=R('#020204', '#06060a', '#0c0c12', '#16161e', '#24222c', '#3a3440'),
                  lot=R('#040406', '#0a0a0e', '#121218', '#1c1b22', '#26242c'),
                  earth=R('#010102', '#040406', '#08080c', '#0e0e14', '#16151c'),
                  sky=R('#06070c', '#0e1018', '#161822', '#1e2030'),
                  skyline=R('#07080e', '#0c0e16', '#12141e', '#181a26'),
                  smog=R('#0e0e16', '#1a1a24', '#2a2632', '#3a3040'), night=True),
    'alert': dict(bg=bg_alert, fam=ALERT_FAM, tlo=0.08, thi=0.62,
                  street=R('#030102', '#080204', '#10040a', '#1c0810', '#2c0e18', '#44141e'),
                  lot=R('#040102', '#0a0306', '#12050a', '#1c0810', '#280c14'),
                  earth=R('#010001', '#040102', '#080204', '#0e0408', '#16060c'),
                  sky=R('#0a0204', '#1a0408', '#2a060e', '#3a0a12'),
                  skyline=R('#0c0204', '#140408', '#1c060c', '#240810'),
                  smog=R('#1a0408', '#2e080e', '#461018', '#5a1820'), night=True),
}

WIN_NEON = ['sodium', 'sodium', 'cyan', 'sodium', 'magenta', 'acid', 'cyan', 'sodium']
SIGN_NEON = ['magenta', 'acid', 'cyan', 'sodium', 'magenta', 'cyan']
GRAFF = ['acid', 'magenta', 'cyan', 'white', 'sodium']


# ------------------------------------------------------------------ model
def B(x0, y0, x1, y1, z0, z1, fam, bid, win=None, taper=0.0, signs=0, scaffold=False, graffiti=False, grime=True):
    return dict(k='box', x0=x0, y0=y0, x1=x1, y1=y1, z0=z0, z1=z1, fam=fam, bid=bid, win=win, taper=taper,
                signs=signs, scaffold=scaffold, graffiti=graffiti, grime=grime)


def clutter(rng, prims, x0, y0, x1, y1, z, bid):
    """Rooftop AC units, tanks and antennas."""
    w, d = x1 - x0, y1 - y0
    for n in range(rng.randint(1, 3)):
        s = rng.uniform(0.3, 0.55)
        ax = rng.uniform(x0 + 0.1, max(x0 + 0.11, x1 - s - 0.1))
        ay = rng.uniform(y0 + 0.1, max(y0 + 0.11, y1 - s - 0.1))
        prims.append(B(ax, ay, ax + s, ay + s * 0.8, z, z + rng.uniform(0.22, 0.45), 'concrete', (bid, 'ac', n),
                       grime=False))
    for n in range(rng.randint(0, 2)):
        ax = rng.uniform(x0 + 0.2, x1 - 0.2)
        ay = rng.uniform(y0 + 0.2, y1 - 0.2)
        prims.append(B(ax - 0.05, ay - 0.05, ax + 0.05, ay + 0.05, z, z + rng.uniform(1.0, 3.2), 'soot',
                       (bid, 'ant', n), grime=False))


def build_city():
    rng = random.Random(2077)
    items = []
    special = {(5, 0): 'spire', (1, 0): 'mega', (3, 1): 'dome', (6, 1): 'twins', (4, 2): 'billboard'}
    shanty = {(1, 3), (5, 3)}
    hrange = {0: (9.0, 15.0), 1: (6.0, 10.5), 2: (3.4, 6.8), 3: (1.2, 2.6)}
    fams = ['soot', 'soot', 'rust', 'oily', 'concrete', 'concrete', 'brick', 'brick']
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
                        h = srng.uniform(0.6, 1.5)
                        prims.append(B(a0, b0, a0 + srng.uniform(0.8, 1.05), b0 + srng.uniform(0.85, 1.1), 0, h,
                                       srng.choice(['rust', 'brick', 'oily', 'concrete']), (bid, i, j),
                                       signs=1 if srng.random() < 0.35 else 0, graffiti=srng.random() < 0.3))
                items.append(dict(box=(x0, y0, x1, y1), prims=prims))
                bid += 1
                continue
            if key in special:
                kind = special[key]
                prims = []
                boards = []
                if kind == 'spire':
                    m = 0.4
                    prims.append(B(x0 + m, y0 + m, x1 - m, y1 - m, 0, 22.0, 'corp', bid, win='cyan', taper=0.3))
                    iw, idp = (x1 - x0 - 2 * m) * 0.15, (y1 - y0 - 2 * m) * 0.15
                    prims.append(dict(k='pyr', x0=x0 + m + iw, y0=y0 + m + idp, x1=x1 - m - iw, y1=y1 - m - idp,
                                      z0=22.0, z1=25.5, fam='corp', bid=bid + 1))
                    prims.append(B(cx - 0.1, cy - 0.1, cx + 0.1, cy + 0.1, 25.0, 29.0, 'soot', bid + 2, grime=False))
                    boards.append(dict(k='board', x0=x0 + 0.9, x1=x1 - 0.9, y=y1 - 0.2, z0=13.0, z1=18.0, bid=bid + 3,
                                       motif='eye'))
                elif kind == 'mega':
                    # stacked mega-block: an old base, a newer block cantilevered on top, a tower on that
                    prims.append(B(x0 + 0.2, y0 + 0.2, x1 - 0.2, y1 - 0.2, 0, 6.5, 'brick', bid, win='sodium',
                                   signs=2, scaffold=True, graffiti=True))
                    prims.append(B(x0 - 0.3, y0 + 0.4, x1 + 0.2, y1 + 0.35, 6.5, 11.0, 'concrete', bid + 1,
                                   win='sodium', signs=1))
                    prims.append(B(x0 + 1.0, y0 + 0.9, x1 - 1.2, y1 - 0.8, 11.0, 17.0, 'oily', bid + 2, win='cyan'))
                    clutter(rng, prims, x0 + 1.0, y0 + 0.9, x1 - 1.2, y1 - 0.8, 17.0, bid + 3)
                elif kind == 'dome':
                    prims.append(B(x0 + 0.4, y0 + 0.4, x1 - 0.4, y1 - 0.4, 0, 1.6, 'concrete', bid, win='sodium',
                                   signs=1, graffiti=True))
                    prims.append(dict(k='dome', cx=cx, cy=cy, z0=1.6, r=1.95, fam='rust', bid=bid + 1))
                    prims.append(B(cx - 0.08, cy - 0.08, cx + 0.08, cy + 0.08, 3.4, 5.4, 'soot', bid + 2,
                                   grime=False))
                elif kind == 'twins':
                    mx = (x0 + x1) / 2
                    prims.append(B(x0 + 0.4, y0 + 0.6, mx - 0.4, y1 - 0.6, 0, 18.0, 'corp', bid, win='cyan',
                                   taper=0.06))
                    prims.append(B(mx - 0.4, cy - 0.4, mx + 0.4, cy + 0.4, 10.0, 11.2, 'soot', bid + 1))
                    prims.append(B(mx + 0.4, y0 + 0.6, x1 - 0.4, y1 - 0.6, 0, 15.5, 'corp', bid + 2, win='cyan',
                                   taper=0.06))
                    boards.append(dict(k='board', x0=x0 + 0.5, x1=mx - 0.3, y=y1 - 0.45, z0=12.0, z1=15.5,
                                       bid=bid + 4, motif='logo'))
                elif kind == 'billboard':
                    prims.append(B(x0 + 0.4, y0 + 0.5, x1 - 0.4, y1 - 0.5, 0, 4.4, 'rust', bid, win='sodium',
                                   signs=1, graffiti=True, scaffold=True))
                    for n, xx in enumerate((x0 + 0.9, cx - 0.1, x1 - 1.1)):
                        prims.append(B(xx, cy - 0.1, xx + 0.2, cy + 0.1, 4.4, 5.6, 'soot', bid + 1 + n, grime=False))
                    boards.append(dict(k='board', x0=x0 - 0.4, x1=x1 + 0.4, y=cy + 0.1, z0=5.4, z1=9.4, bid=bid + 5,
                                       motif='eye'))
                bid += 8
                items.append(dict(box=(x0, y0, x1, y1), prims=prims + boards))
                continue
            lo, hi = hrange[by]
            split = rng.choice([2, 4, 4, 4])
            if split == 2:
                mx = x0 + LOT_X * rng.uniform(0.4, 0.6)
                parcels = [(x0, y0, mx, y1), (mx, y0, x1, y1)]
            else:
                mx = x0 + LOT_X * rng.uniform(0.4, 0.6)
                my = y0 + LOT_Y * rng.uniform(0.4, 0.6)
                parcels = [(x0, y0, mx, my), (mx, y0, x1, my), (x0, my, mx, y1), (mx, my, x1, y1)]
            for (a0, b0, a1, b1) in parcels:
                h = rng.uniform(lo, hi)
                fam = rng.choice(fams)
                win = rng.choice(WIN_NEON)
                ins = 0.2
                nsig = 0
                if h > 2.2:
                    nsig = rng.choice([0, 1, 1, 2, 3])
                prims = [B(a0 + ins, b0 + ins, a1 - ins, b1 - ins, 0, h, fam, bid, win=win, signs=nsig,
                           scaffold=(3 < h < 9 and rng.random() < 0.2), graffiti=(h < 7 and rng.random() < 0.55))]
                top = h
                bx0, by0, bx1, by1 = a0 + ins, b0 + ins, a1 - ins, b1 - ins
                if h > 5.5 and rng.random() < 0.55:
                    # a newer tower built over the old one; sometimes it overhangs toward the street
                    over = rng.random() < 0.4
                    if over:
                        nx0, ny0, nx1, ny1 = bx0 + 0.3, by0 + 0.2, bx1 + 0.35, by1 + 0.35
                    else:
                        wv, dv = bx1 - bx0, by1 - by0
                        nx0, ny0, nx1, ny1 = bx0 + wv * 0.15, by0 + dv * 0.15, bx1 - wv * 0.2, by1 - dv * 0.2
                    h2 = top + rng.uniform(2.5, 6.5)
                    prims.append(B(nx0, ny0, nx1, ny1, top, h2, rng.choice(['corp', 'concrete', 'oily']), bid + 1,
                                   win=rng.choice(WIN_NEON), signs=1 if rng.random() < 0.4 else 0))
                    bx0, by0, bx1, by1, top = nx0, ny0, nx1, ny1, h2
                if rng.random() < 0.4 and h > 3:
                    px = bx1 - 0.02
                    py = by0 + (by1 - by0) * rng.uniform(0.3, 0.7)
                    prims.append(B(px, py, px + 0.14, py + 0.14, 0, h * 0.95, 'rust', bid + 2, grime=False))
                clutter(rng, prims, bx0, by0, bx1, by1, top, bid + 3)
                items.append(dict(box=(a0, b0, a1, b1), prims=prims))
                bid += 5
    # walkways over the y-running streets
    wrng = random.Random(31)
    for by in range(3):
        for bx in range(NBX - 1):
            if (bx, by) in special or (bx + 1, by) in special or wrng.random() < 0.45:
                continue
            ax1 = lot_rect(bx, by)[2]
            bx0 = lot_rect(bx + 1, by)[0]
            _, y0, _, y1 = lot_rect(bx, by)
            yc = wrng.uniform(y0 + 0.8, y1 - 0.8)
            z = {0: 5.0, 1: 3.6, 2: 2.3}[by] + wrng.uniform(0, 1.0)
            items.append(dict(box=(ax1, yc - 0.35, bx0, yc + 0.35),
                              prims=[B(ax1 - 0.1, yc - 0.35, bx0 + 0.1, yc + 0.35, z, z + 0.45, 'concrete',
                                       ('walk', bx, by), win='sodium', grime=False)]))
    # surveillance cameras on poles
    for n, ij in enumerate([(1, 2), (3, 3), (6, 2), (5, 2), (3, 1), (1, 4), (6, 4)]):
        x, y = inter(*ij)
        x += 0.55
        y += 0.55
        items.append(dict(box=(x - 0.1, y - 0.1, x + 0.1, y + 0.1), prims=[
            B(x - 0.05, y - 0.05, x + 0.05, y + 0.05, 0, 2.6, 'soot', ('pole', n), grime=False),
            B(x - 0.14, y - 0.12, x + 0.14, y + 0.34, 2.35, 2.62, 'concrete', ('camh', n), grime=False),
            dict(k='led', x=x, y=y + 0.36, z=2.48, bid=('led', n))]))
    return items


def alert_items():
    """Barricades and armoured vehicles (only under high suspicion)."""
    items = []
    # barricades across streets next to nodes
    for n, (ij, axis) in enumerate([((2, 3), 'x'), ((4, 2), 'y'), ((7, 3), 'y'), ((5, 1), 'x')]):
        x, y = inter(*ij)
        prims = []
        for k in range(-2, 3):
            if axis == 'x':
                bx, byy = x + 1.3, y + k * 0.36
                prims.append(dict(k='barrier', x0=bx - 0.12, y0=byy - 0.16, x1=bx + 0.12, y1=byy + 0.16, h=0.45,
                                  bid=('bar', n, k)))
            else:
                bx, byy = x + k * 0.36, y + 1.3
                prims.append(dict(k='barrier', x0=bx - 0.16, y0=byy - 0.12, x1=bx + 0.16, y1=byy + 0.12, h=0.45,
                                  bid=('bar', n, k)))
        bx0 = min(p['x0'] for p in prims)
        by0 = min(p['y0'] for p in prims)
        items.append(dict(box=(bx0, by0, bx0 + 0.3, by0 + 0.3), prims=prims))
    # armoured vehicles on the streets
    for n, (x, y, axis) in enumerate([(inter(3, 3)[0] - 0.1, inter(3, 3)[1], 'x'), (inter(6, 2)[0], inter(6, 2)[1] - 2.0, 'y'),
                                      (inter(1, 1)[0] + 2.4, inter(1, 1)[1], 'x'), (inter(5, 3)[0] + 2.2, inter(5, 3)[1], 'x')]):
        L, Wd = 2.3, 1.0
        if axis == 'x':
            x0, x1, y0, y1 = x - L / 2, x + L / 2, y - Wd / 2, y + Wd / 2
        else:
            x0, x1, y0, y1 = x - Wd / 2, x + Wd / 2, y - L / 2, y + L / 2
        items.append(dict(box=(x0, y0, x1, y1), prims=[
            B(x0, y0, x1, y1, 0.1, 0.75, 'soot', ('apc', n), grime=False),
            B(x0 + 0.25, y0 + 0.15, x1 - 0.25, y1 - 0.15, 0.75, 1.15, 'soot', ('apc2', n), taper=0.2, grime=False),
            dict(k='strobe', x=(x0 + x1) / 2, y=(y0 + y1) / 2, z=1.2, bid=('st', n))]))
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
NODE_RAMP = {'home': NEON['cyan'], 'site': NEON['cyan'], 'target': NEON['magenta'], 'shop': NEON['acid'],
             'boss': NEON['red']}
PATH_RAMP = R('#4a2204', '#9a4a08', '#e07a12', '#ffb040', '#fff0c0')


# ------------------------------------------------------------------ drawing
class CityPainter:
    def __init__(self, img, cam, theme):
        self.img = img
        self.d = ImageDraw.Draw(img)
        self.cam = cam
        self.th = THEMES[theme]
        self.theme = theme
        self.night = self.th['night']
        self.alert = theme == 'alert'
        self.reflect = []  # (x, y_front, width, neon, broken)

    def face(self, q, stops, seed, nu, nv, center=None, normal=None, colfac=None, gv=0.14, gu=0.0, var=0.07,
             tlo=None, thi=None, cull=True, jit=0.32, d=None):
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
        base = tlo + (thi - tlo) * (0.2 + 0.8 * lam)
        colfn = colfac(base) if colfac else toner(stops, base, gu, gv, var)
        cam = self.cam
        facet(d or self.d, lambda u, v: cam.p(*bil3(q, u, v)), nu, nv, colfn, seed, jit)
        return True

    def quad_w(self, q, colfn, seed, nu, nv, jit=0.3, d=None):
        cam = self.cam
        facet(d or self.d, lambda u, v: cam.p(*bil3(q, u, v)), nu, nv, colfn, seed, jit)

    # ---- backdrop skyline (distant megacity, hazy)
    def skyline(self):
        rng = random.Random(808)
        st = self.th['skyline']
        x = -40
        while x < W + 40:
            w = rng.uniform(40, 130)
            top = rng.uniform(40, 420)
            q = [(x, top), (x + w, top), (x + w, 1080), (x, 1080)]
            base = rng.uniform(0.3, 0.9)
            facet(self.d, bil(q), max(1, int(w / 40)), max(2, int((1080 - top) / 110)),
                  toner(st, base, gu=-0.2, var=0.08, flip=0.1), ('sky', x), 0.3)
            if self.night:
                lrng = random.Random(str(x))
                for _ in range(int(w * max(0, 600 - top) / 1500)):
                    lx = lrng.uniform(x + 4, x + w - 4)
                    ly = lrng.uniform(top + 6, 600)
                    c = ramp(NEON['sodium' if not self.alert else 'red'], lrng.uniform(0.35, 0.7))
                    tri(self.d, [(lx, ly), (lx + 5, ly), (lx + 2, ly + 4)], c)
            if rng.random() < 0.3:
                ax = x + w * rng.uniform(0.3, 0.7)
                line2(self.d, (ax, top), (ax, top - rng.uniform(30, 90)), 2, ramp(st, base))
            x += w * rng.uniform(0.6, 1.0)

    # ---- ground
    def ground(self, items):
        th = self.th
        q = [(0, LY, -SLAB), (LX, LY, -SLAB), (LX, LY, 0), (0, LY, 0)]
        self.face(q, th['earth'], 'slab_f', 30, 3, normal=(0, 1, 0), gv=0.3, gu=0.15, tlo=0.1, thi=0.9)
        q = [(LX, LY, -SLAB), (LX, 0, -SLAB), (LX, 0, 0), (LX, LY, 0)]
        self.face(q, th['earth'], 'slab_s', 14, 3, normal=(1, 0, 0), gv=0.3, tlo=0.2, thi=0.8)
        # wet street: dark facets with sky-coloured puddle shines
        night = self.night

        def street(u, v, i, j, k, rc):
            t = 0.35 + 0.25 * (1 - v) + rc.uniform(-0.1, 0.1)
            if rc.random() < 0.12:
                t += 0.35  # puddle shine
            return ramp(th['street'], t)
        self.quad_w([(0, LY, 0), (LX, LY, 0), (LX, 0, 0), (0, 0, 0)], street, 'street', 40, 20, 0.35)
        for by in range(NBY):
            for bx in range(NBX):
                x0, y0, x1, y1 = lot_rect(bx, by)
                q = [(x0, y1, 0.02), (x1, y1, 0.02), (x1, y0, 0.02), (x0, y0, 0.02)]
                self.face(q, th['lot'], ('lot', bx, by), 4, 3, normal=(0, 0, 1), var=0.1, tlo=0.2, thi=0.8)

    def reflections(self):
        """Faceted neon reflections on the wet street in front of lit signs."""
        lay, d = layer(self.img)
        for n, (x, yf, w, neon, broken) in enumerate(self.reflect):
            L = 1.5
            q = [(x - w / 2, yf + 0.15, 0.03), (x + w / 2, yf + 0.15, 0.03), (x + w / 2 * 1.3, yf + L, 0.03),
                 (x - w / 2 * 1.3, yf + L, 0.03)]
            st = NEON[neon]

            def cf(u, v, i, j, k, rc, st=st):
                if rc.random() < 0.3:
                    return None
                return ramp(st, 0.55 + rc.uniform(-0.2, 0.2)) + (int(150 * (1 - v) + rc.uniform(0, 50)),)
            self.quad_w([q[0], q[1], q[2], q[3]], cf, ('refl', n), 2, 3, 0.35, d=d)
        self.img = composite(self.img, lay)
        self.d = ImageDraw.Draw(self.img)

    # ---- boxes
    def box(self, p):
        th = self.th
        x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
        stops = th['fam'][p['fam']]
        bid = p['bid']
        tx = (x1 - x0) * p['taper'] / 2
        ty = (y1 - y0) * p['taper'] / 2
        h = z1 - z0
        center = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        top = [(x0 + tx, y1 - ty, z1), (x1 - tx, y1 - ty, z1), (x1 - tx, y0 + ty, z1), (x0 + tx, y0 + ty, z1)]
        front = [(x0, y1, z0), (x1, y1, z0), top[1], top[0]]
        side = [(x1, y1, z0), (x1, y0, z0), top[2], top[1]]
        nv = max(2, int(round(h / 0.9)))
        if nv % 2 == 1:
            nv += 1
        for name, q, wdt in (('f', front, x1 - x0), ('s', side, y1 - y0)):
            nu = max(1 if wdt < 0.5 else 2, int(round(wdt / 1.3)))
            colfac = self.facade_colfac(stops, bid, name, p['win'], nv, p['grime'])
            self.face(q, stops, (bid, name), nu, nv if p['win'] else max(1, nv // 2), center=center, colfac=colfac)
        self.face(top, stops, (bid, 't'), max(1, int(round((x1 - x0) / 1.3))), max(1, int(round((y1 - y0) / 1.3))),
                  center=center, gv=-0.1, gu=0.1, var=0.1)
        if p['scaffold']:
            self.scaffold(x0, x1, y1, z0, min(z1, z0 + 6.0), bid)
        if p['graffiti'] and h > 0.5:
            self.graffiti(x0, x1, y1, z0, min(z1, z0 + 1.2), bid)
        if p['signs'] and p['taper'] == 0:
            self.signs(p)

    def facade_colfac(self, stops, bid, name, win, nv, grime):
        night, alert = self.night, self.alert
        rust = FAM['rust']

        def fac(base):
            def f(u, v, i, j, k, rc):
                t = base + 0.26 * (v - 0.5) + rc.uniform(-0.06, 0.06)
                if rc.random() < 0.08:
                    t += 0.12 if rc.random() < 0.5 else -0.12
                if grime:
                    s = hsh(bid, ord(name), i, 91)
                    if s < 0.35 and v < 0.35 + s * 1.7:  # grime streak running down from above
                        t -= 0.13
                    if hsh(bid, ord(name), i // 2, j // 3, 5) < 0.12:  # rust stain
                        return mix(ramp(stops, t - 0.05), ramp(rust, t + 0.05), 0.6)
                if win and j % 2 == 1 and j < nv - 1:
                    hv = hsh(bid, ord(name), i, j)
                    if night:
                        lit = 0.22 if not alert else 0.2
                        if hv < lit:
                            if alert:
                                wn = 'red' if hsh(bid, 7) < 0.6 else 'sodium'
                            else:
                                wn = win if hsh(bid, i, j, 3) < 0.35 else 'sodium'
                            return ramp(NEON[wn], 0.25 + 0.4 * rc.random())
                        return ramp(stops, t - 0.14)
                    if hv < 0.8:
                        return ramp(stops, t - 0.2)
                return ramp(stops, t)
            return f
        return fac

    def signs(self, p):
        """Stacked vertical blade signs and shopfront bands; some are broken (missing facets)."""
        x0, y0, x1, y1, z0, z1, bid = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1'], p['bid']
        h = z1 - z0
        n = p['signs']
        for s in range(n):
            neon = SIGN_NEON[int(hsh(bid, s, 17) * len(SIGN_NEON))]
            broken = hsh(bid, s, 23) < 0.3
            on_side = hsh(bid, s, 29) < 0.3
            if h < 2.6:
                # shopfront band low on the facade
                za, zb = z0 + 0.35, z0 + 0.8
                ua, ub = 0.12, 0.88
                vertical = False
            else:
                wd = 0.45 + 0.3 * hsh(bid, s, 3)
                ln = min(h * 0.7, 1.6 + 2.6 * hsh(bid, s, 5))
                za = z0 + 0.6 + (h - ln - 0.8) * hsh(bid, s, 7)
                zb = za + ln
                span = (y1 - y0) if on_side else (x1 - x0)
                ua = 0.08 + 0.7 * hsh(bid, s, 11)
                ub = min(0.97, ua + wd / max(span, 0.1))
                vertical = True
            if on_side:
                xx = x1 + 0.06
                ya, yb = y1 - (y1 - y0) * ua, y1 - (y1 - y0) * ub
                q = [(xx, ya, za), (xx, yb, za), (xx, yb, zb), (xx, ya, zb)]
            else:
                yy = y1 + 0.06
                xa, xb = x0 + (x1 - x0) * ua, x0 + (x1 - x0) * ub
                q = [(xa, yy, za), (xb, yy, za), (xb, yy, zb), (xa, yy, zb)]
                if self.night and not broken and za < 4:
                    self.reflect.append(((xa + xb) / 2, y1, xb - xa, neon if not self.alert else 'red', broken))
            st = NEON[neon]
            night, alert, theme = self.night, self.alert, self.theme
            # dark backing plate
            self.quad_w(q, toner(FAM['soot'], 0.15, var=0.05), ('sgb', bid, s), 1, 1, 0.0)

            def cf(u, v, i, j, k, rc, st=st, broken=broken):
                if broken and rc.random() < 0.35:
                    return None
                if alert:
                    if rc.random() < 0.5:
                        return None
                    return ramp(NEON['red'], 0.35 + rc.uniform(-0.15, 0.25))
                if night:
                    t = 0.62 + rc.uniform(-0.25, 0.3)
                    if broken and rc.random() < 0.4:
                        t = 0.22
                    return ramp(st, t)
                return mix(ramp(st, 0.35 + rc.uniform(-0.1, 0.15)), hexc('#5a584e'), 0.6)
            if vertical:
                nvs = max(2, int((zb - za) / 0.45))
                self.quad_w(q, cf, ('sg', bid, s), 1, nvs, 0.3)
            else:
                self.quad_w(q, cf, ('sg', bid, s), max(2, int((ub - ua) * (x1 - x0) / 0.5)), 1, 0.3)

    def scaffold(self, x0, x1, y1, z0, z1, bid):
        cam = self.cam
        yy = y1 + 0.3
        col = ramp(FAM['rust'], 0.55 if not self.night else 0.3)
        col2 = ramp(FAM['rust'], 0.35 if not self.night else 0.18)
        xs = [x0 + (x1 - x0) * k / max(1, int((x1 - x0) / 0.9)) for k in range(int((x1 - x0) / 0.9) + 1)]
        zs = [z0 + k * 1.1 for k in range(int((z1 - z0) / 1.1) + 1)]
        for x in xs:
            line2(self.d, cam.p(x, yy, z0), cam.p(x, yy, zs[-1]), 1.8, col)
        for z in zs[1:]:
            line2(self.d, cam.p(xs[0], yy, z), cam.p(xs[-1], yy, z), 2.2, col)
        for a in range(len(xs) - 1):
            for b in range(len(zs) - 1):
                if (a + b) % 2 == 0:
                    line2(self.d, cam.p(xs[a], yy, zs[b]), cam.p(xs[a + 1], yy, zs[b + 1]), 1.3, col2)

    def graffiti(self, x0, x1, y1, z0, z1, bid):
        """Angular triangle glyphs (not letters) low on the facade."""
        rc = random.Random(str(('gf', bid)))
        yy = y1 + 0.03
        w = x1 - x0
        gw = min(w * 0.7, rc.uniform(0.8, 1.6))
        ga = x0 + rc.uniform(0.05, max(0.06, w - gw - 0.05))
        c1 = GRAFF[int(hsh(bid, 41) * len(GRAFF))]
        c2 = GRAFF[int(hsh(bid, 43) * len(GRAFF))]
        cam = self.cam
        for n in range(rc.randint(5, 9)):
            cxw = ga + rc.uniform(0, gw)
            cz = z0 + rc.uniform(0.15, 0.85) * (z1 - z0)
            s = rc.uniform(0.12, 0.32)
            a = rc.uniform(0, 2 * math.pi)
            pts = [cam.p(cxw + s * math.cos(a + t) * 1.4, yy, cz + s * math.sin(a + t) * 0.8) for t in (0, 2.5, 3.6)]
            st = NEON[c1 if n % 3 else c2]
            col = ramp(st, rc.uniform(0.4, 0.75))
            col = mix(col, hexc('#4a4840'), 0.35) if not self.night else mix(col, hexc('#0a0a10'), 0.45)
            tri(self.d, pts, col)

    def pyr(self, p):
        stops = self.th['fam'][p['fam']]
        x0, y0, x1, y1, z0, z1 = p['x0'], p['y0'], p['x1'], p['y1'], p['z0'], p['z1']
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        ap = (cx, cy, z1)
        center = (cx, cy, z0 + (z1 - z0) * 0.3)
        base = [(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)]
        for k in range(4):
            self.face([base[k], base[(k + 1) % 4], ap, ap], stops, ('pyr', p['bid'], k), 3, 3, center=center, gv=0.1)

    def dome(self, p):
        stops = self.th['fam'][p['fam']]
        cx, cy, z0, r, bid = p['cx'], p['cy'], p['z0'], p['r'], p['bid']
        center = (cx, cy, z0)
        cam = self.cam
        for a in range(5):
            la0, la1 = math.pi / 2 * a / 5, math.pi / 2 * (a + 1) / 5
            for b in range(16):
                lo0, lo1 = 2 * math.pi * b / 16, 2 * math.pi * (b + 1) / 16

                def P(la, lo):
                    return (cx + r * math.cos(la) * math.cos(lo), cy + r * math.cos(la) * math.sin(lo), z0 + r * math.sin(la))
                q = [P(la0, lo0), P(la0, lo1), P(la1, lo1), P(la1, lo0)]
                n = v_norm(v_sub(P((la0 + la1) / 2, (lo0 + lo1) / 2), center))
                if v_dot(n, cam.d) <= 0:
                    continue
                if self.night and a == 1 and b % 3 == 0:
                    st = NEON['red'] if self.alert else NEON['cyan']
                    self.quad_w(q, toner(st, 0.5, var=0.15), ('dm', bid, a, b), 1, 1, 0.0)
                    continue
                self.face(q, stops, ('dm', bid, a, b), 1, 1, normal=n, var=0.08, jit=0.0)

    def board(self, p):
        """Huge corp billboard, eye or logo motif."""
        x0, x1, y, z0, z1, bid, motif = p['x0'], p['x1'], p['y'], p['z0'], p['z1'], p['bid'], p['motif']
        q = [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
        self.face([(x0 - 0.15, y - 0.05, z0 - 0.2), (x1 + 0.15, y - 0.05, z0 - 0.2), (x1 + 0.15, y - 0.05, z1 + 0.15),
                   (x0 - 0.15, y - 0.05, z1 + 0.15)], self.th['fam']['soot'], ('bdf', bid), 3, 1, normal=(0, 1, 0))
        night, alert = self.night, self.alert

        def cf(u, v, i, j, k, rc):
            dx, dy = (u - 0.5) * 2, (v - 0.5) * 2
            if motif == 'eye':
                inside = abs(dx) * 0.55 + abs(dy) < 0.66
                pupil = abs(dx) * 1.3 + abs(dy) < 0.4
                core = abs(dx) * 3 + abs(dy) < 0.16
            else:  # logo: nested chevrons
                inside = abs(dx) * 0.8 + (dy + 0.2) < 0.7 and abs(dx) * 0.8 + (dy + 0.2) > 0.25
                pupil = abs(dx) * 0.8 + (dy - 0.3) < 0.35 and abs(dx) * 0.8 + (dy - 0.3) > 0.05
                core = False
            if rc.random() < 0.05:
                return ramp(FAM['soot'], 0.2)  # dead pixels
            if alert:
                st = NEON['red']
                return ramp(st, (0.85 if core else 0.65 if pupil else 0.42 if inside else 0.18) + rc.uniform(-0.1, 0.1))
            if night:
                if core:
                    return ramp(NEON['white'], 0.9)
                st = NEON['cyan'] if pupil else (NEON['magenta'] if inside else NEON['violet'])
                return ramp(st, (0.6 if inside or pupil else 0.25) + rc.uniform(-0.15, 0.2))
            st = NEON['cyan'] if pupil else (NEON['magenta'] if inside else NEON['white'])
            return mix(ramp(st, 0.45 + rc.uniform(-0.12, 0.12)), hexc('#56544a'), 0.5 if not (inside or pupil) else 0.25)
        self.quad_w(q, cf, ('bd', bid), max(6, int((x1 - x0) / 0.5)), max(4, int((z1 - z0) / 0.55)), 0.3)

    def barrier(self, p):
        x0, y0, x1, y1, h = p['x0'], p['y0'], p['x1'], p['y1'], p['h']
        center = ((x0 + x1) / 2, (y0 + y1) / 2, h / 2)
        top = [(x0, y1, h), (x1, y1, h), (x1, y0, h), (x0, y0, h)]

        def haz(base):
            def f(u, v, i, j, k, rc):
                st = NEON['sodium'] if (i + j) % 2 == 0 else FAM['soot']
                return ramp(st, base + rc.uniform(-0.05, 0.05))
            return f
        self.face([(x0, y1, 0), (x1, y1, 0), top[1], top[0]], None, (p['bid'], 'f'), 2, 2, center=center, colfac=haz)
        self.face([(x1, y1, 0), (x1, y0, 0), top[2], top[1]], None, (p['bid'], 's'), 2, 2, center=center, colfac=haz)
        self.face(top, FAM['soot'], (p['bid'], 't'), 1, 1, center=center)

    def item(self, it):
        for p in it['prims']:
            k = p['k']
            if k == 'box':
                self.box(p)
            elif k == 'pyr':
                self.pyr(p)
            elif k == 'dome':
                self.dome(p)
            elif k == 'board':
                self.board(p)
            elif k == 'barrier':
                self.barrier(p)
            elif k == 'led':
                sx, sy = self.cam.p(p['x'], p['y'], p['z'])
                st = NEON['red']
                tri(self.d, [(sx - 4, sy), (sx, sy - 4), (sx + 4, sy)], ramp(st, 0.9))
                tri(self.d, [(sx - 4, sy), (sx, sy + 4), (sx + 4, sy)], ramp(st, 0.6))
            elif k == 'strobe':
                sx, sy = self.cam.p(p['x'], p['y'], p['z'])
                for s, st in ((-1, NEON['red']), (1, NEON['blue'])):
                    tri(self.d, [(sx + s * 2, sy - 6), (sx + s * 14, sy - 3), (sx + s * 12, sy + 4)], ramp(st, 0.85))
                    tri(self.d, [(sx + s * 2, sy - 6), (sx + s * 12, sy + 4), (sx + s * 2, sy + 3)], ramp(st, 0.55))

    def cables(self, items):
        """Sagging cable bundles strung between neighbouring buildings."""
        rng = random.Random(555)
        anchors = []
        for it in items:
            for p in it['prims']:
                if p['k'] == 'box' and p['z1'] - p['z0'] > 4 and p['z0'] == 0 and p['win']:
                    z = p['z0'] + (p['z1'] - p['z0']) * rng.uniform(0.35, 0.85)
                    anchors.append((p['x1'], p['y1'], z))
        anchors.sort()
        col = ramp(FAM['soot'], 0.12 if self.night else 0.18)
        for n, a in enumerate(anchors):
            cands = [b for b in anchors if b is not a and 3.0 < math.hypot(b[0] - a[0], b[1] - a[1]) < 9.0]
            cands.sort(key=lambda b: (math.hypot(b[0] - a[0], b[1] - a[1]), b))
            for b in cands[:rng.choice([1, 1, 2])]:
                pa, pb = self.cam.p(*a), self.cam.p(*b)
                sag = rng.uniform(12, 45)
                for s in range(rng.randint(1, 3)):
                    pts = catenary(self.d, pa, (pb[0], pb[1] + s * 3), sag + s * 5, 1.6, col)
                if self.night and not self.alert and rng.random() < 0.2:
                    st = NEON[rng.choice(['sodium', 'magenta', 'acid'])]
                    for k in range(2, 11, 2):
                        x, y = pts[k]
                        tri(self.d, [(x - 3, y + 1), (x + 3, y + 1), (x, y + 6)], ramp(st, 0.75))

    # ---- overlay on the ground plane
    def ribbon(self, a, b, w, stops, seed, z=0.05, base=0.55):
        ax, ay = a
        bx, by = b
        L = math.hypot(bx - ax, by - ay)
        dx, dy = (bx - ax) / L, (by - ay) / L
        px, py = -dy * w, dx * w
        q = [(ax - px, ay - py, z), (bx - px, by - py, z), (bx + px, by + py, z), (ax + px, ay + py, z)]
        self.quad_w(q, toner(stops, base, var=0.12, flip=0.15), seed, max(2, int(L / 0.9)), 1, 0.35)

    def paths(self):
        for n, e in enumerate(EDGES):
            pts = [inter(*p) for p in e]
            for k in range(len(pts) - 1):
                a, b = pts[k], pts[k + 1]
                L = math.hypot(b[0] - a[0], b[1] - a[1])
                dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
                self.ribbon((a[0] - dx * 0.3, a[1] - dy * 0.3), (b[0] + dx * 0.3, b[1] + dy * 0.3), 0.3, PATH_RAMP,
                            ('path', n, k))

    def node_discs(self):
        cam = self.cam
        for name, ij, kind in NODES:
            x, y = inter(*ij)
            r = 1.35 if kind == 'home' else 1.0
            st = NODE_RAMP[kind]
            ringst = R('#060608', '#121216', '#222228', '#34343c')
            facet(self.d, lambda u, v: cam.p(x + r * (1 + 0.28 * v) * math.cos(u * 2 * math.pi),
                                             y + r * (1 + 0.28 * v) * math.sin(u * 2 * math.pi), 0.07),
                  6, 1, toner(ringst, 0.5, var=0.2), ('ndr', name), 0.0, wrap_u=True)
            facet(self.d, lambda u, v: cam.p(x + r * v * math.cos(u * 2 * math.pi), y + r * v * math.sin(u * 2 * math.pi), 0.08),
                  6, 2, toner(st, 0.6, var=0.14, flip=0.25, famt=0.2), ('nd', name), 0.15, wrap_u=True)

    def traffic(self):
        rng = random.Random(4242)
        cam = self.cam
        head = NEON['sodium'] if not self.alert else NEON['red']
        tail = NEON['red'] if not self.alert else NEON['blue']
        lanes = []
        for iy in range(NBY + 1):
            _, y = inter(0, iy)
            lanes.append(((0.3, y - 0.35), (LX - 0.3, y - 0.35), head))
            lanes.append(((LX - 0.3, y + 0.35), (0.3, y + 0.35), tail))
        for ix in range(NBX + 1):
            x, _ = inter(ix, 0)
            lanes.append(((x + 0.35, 0.3), (x + 0.35, LY - 0.3), head))
            lanes.append(((x - 0.35, LY - 0.3), (x - 0.35, 0.3), tail))
        for (a, b, st) in lanes:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            s = rng.uniform(0, 3.0)
            while s < L:
                cx, cy = a[0] + dx * s, a[1] + dy * s
                ln = 0.4
                pw = 0.14
                p1 = cam.p(cx + dx * ln, cy + dy * ln, 0.1)
                p2 = cam.p(cx - dy * pw, cy + dx * pw, 0.1)
                p3 = cam.p(cx + dy * pw, cy - dx * pw, 0.1)
                p0 = cam.p(cx - dx * ln * 0.8, cy - dy * ln * 0.8, 0.1)
                tri(self.d, [p1, p2, p3], ramp(st, rng.uniform(0.6, 0.9)))
                tri(self.d, [p2, p3, p0], ramp(st, rng.uniform(0.25, 0.45)))
                s += rng.uniform(5.0, 11.0)

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
                    tip = cam.p(cx + dx * 0.36, cy + dy * 0.36, 0.1)
                    l = cam.p(cx - dx * 0.24 - dy * 0.28, cy - dy * 0.24 + dx * 0.28, 0.1)
                    r = cam.p(cx - dx * 0.24 + dy * 0.28, cy - dy * 0.24 - dx * 0.28, 0.1)
                    m = cam.p(cx - dx * 0.08, cy - dy * 0.08, 0.1)
                    tri(self.d, [tip, l, m], ramp(PATH_RAMP, 0.95))
                    tri(self.d, [tip, m, r], ramp(PATH_RAMP, 0.7))
                    s += 1.25

    def pins(self):
        cam = self.cam
        for name, ij, kind in sorted(NODES, key=lambda n: (cam.depth(*inter(*n[1])), n[0])):
            x, y = inter(*ij)
            big = kind == 'home'
            hz = 3.4 if big else 2.6
            rr = 0.95 if big else 0.62
            st = NODE_RAMP[kind]
            if big:
                st = R('#0a3a50', '#1890b8', '#6ff0ff', '#e6ffff', '#ffffff')
            b0 = cam.p(x, y, 0.1)
            t0 = cam.p(x, y, hz)
            wpx = 3.0 if big else 2.2
            tri(self.d, [(b0[0] - wpx, b0[1]), (t0[0], t0[1]), (b0[0] + wpx, b0[1])], ramp(st, 0.5))
            tri(self.d, [(b0[0], b0[1]), (t0[0], t0[1]), (b0[0] + wpx, b0[1])], ramp(st, 0.3))
            c = (x, y, hz + rr * 1.3)
            top = (x, y, hz + rr * 2.8)
            bot = (x, y, hz)
            eq = [(x + rr * math.cos(a), y + rr * math.sin(a), hz + rr * 1.3) for a in
                  [math.radians(-24 + 90 * k) for k in range(4)]]
            for k in range(4):
                a, b = eq[k], eq[(k + 1) % 4]
                for apex, sd in ((top, 't'), (bot, 'b')):
                    self.face([a, b, apex, apex], st, ('pin', name, k, sd), 2, 2, center=c, tlo=0.2, thi=1.0,
                              var=0.05, jit=0.2)
            if kind == 'boss':
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
        panel(self.d, q, R('#062430', '#0a4458', '#10789a', '#20b0cc', '#8ff0ff'), 0.72, 'youlbl', nu=7, nv=2, gv=-0.25)
        tri(self.d, [(x - 12, y - 16.5), (x + 12, y - 16.5), (x, y)], ramp(NEON['cyan'], 0.75))
        tri(self.d, [(x, y - 16.5), (x + 12, y - 16.5), (x, y)], ramp(NEON['cyan'], 0.5))
        text(self.d, x + 5, y - 16 - h / 2, 'YOU ARE HERE', 23, hexc('#04121c'), anchor='mm')


def city_hud(d, theme):
    alert = theme == 'alert'
    level = {'day': 2, 'night': 3, 'alert': 5}[theme]
    plate = R('#060608', '#0e0e12', '#18181e', '#24242a', '#302f36')
    if alert:
        plate = R('#080204', '#14040a', '#220810', '#320c16', '#42101c')
    panel(d, skew_rect(36, 30, 470, 128, 16), plate, 0.5, 'hud_title', nu=8, nv=3, gv=-0.3)
    # strip of hazard tape along the plate
    for k in range(9):
        x = 52 + k * 22
        tri(d, [(x, 30), (x + 11, 30), (x - 4, 38)], ramp(NEON['sodium'], 0.6))
    text(d, 66, 46, 'KANAL WARD', 34, hexc('#e8dcc0'), style='Bold')
    sub = {'day': 'SECTOR 9 // SMOG INDEX 7', 'night': 'SECTOR 9 // CURFEW 02:00', 'alert': 'SECTOR 9 // CORP LOCKDOWN'}
    text(d, 66, 86, sub[theme], 17, hexc('#948c80'), style='SemiBold')
    text(d, 66, 114, 'SUSPICION', 18, hexc('#e0d0c0'), style='Bold')
    for k in range(5):
        x = 190 + k * 58
        on = k < level
        st = NEON['red'] if (alert or k >= 3) else NEON['sodium']
        if not on:
            st = R('#0e0e12', '#18181e', '#24242a', '#302f36')
        panel(d, [(x + 10, 110), (x + 52, 110), (x + 42, 138), (x, 138)], st, 0.6 if on else 0.4, ('susp', k, theme),
              nu=3, nv=1, gv=-0.3, var=0.1)
    lx, ly = 40, 958
    panel(d, skew_rect(lx, ly, 560, 86, 12), plate, 0.45, 'hud_leg', nu=8, nv=2, gv=-0.3)
    for k, (lab, kind) in enumerate([('TARGET', 'target'), ('SITE', 'site'), ('SHOP', 'shop'), ('BOSS', 'boss')]):
        x = lx + 38 + k * 134
        gem(d, x, ly + 43, 15, 20, NODE_RAMP[kind], ('lg', kind), n=4, base=0.6)
        text(d, x + 24, ly + 43, lab, 20, hexc('#e0d6c8'), anchor='lm')
    if alert:
        bw = 660
        q = skew_rect(960 - bw / 2 + 60, 34, bw, 70, -18)
        panel(d, q, NEON['red'], 0.42, 'alertbanner', nu=10, nv=2, gv=-0.3, var=0.1, flip=0.2)
        for k in range(14):
            x = 960 - bw / 2 + 50 + k * 48
            tri(d, [(x, 104), (x + 22, 104), (x + 10, 116)], ramp(NEON['sodium'], 0.65))
        text(d, 960 + 60, 69, 'LOCKDOWN  //  SWEEP IN PROGRESS', 32, hexc('#fff0e0'), anchor='mm', shadow=hexc('#3a0408'))


def night_sky_fx(img, cam, theme):
    """Corp searchlights raking the sky and a few patrol drones."""
    import alert_fx
    lay, d = layer(img)
    st = NEON['cyan'] if theme == 'night' else NEON['red']
    for n, (src3, tx, spread) in enumerate([((31.5, 3.0, 26.5), 500, 60), ((31.5, 3.0, 26.5), 1180, 50),
                                            ((39.0, 13.0, 18.0), 1760, 55)]):
        s = cam.p(*src3)
        q = [s, s, (tx + spread, -20), (tx - spread, -20)]
        facet(d, bil(q), 3, 6, toner(st, 0.7, gv=0.3, var=0.12, flip=0.2, alpha=(28, 70)), ('skyb', theme, n), 0.35)
    img = composite(img, lay)
    dd = ImageDraw.Draw(img)
    rng = random.Random(77)
    for n in range(6 if theme == 'night' else 0):
        alert_fx.drone(dd, rng.uniform(300, 1750), rng.uniform(120, 330), rng.uniform(10, 13), ('nd', n),
                       eye=NEON['cyan'])
    return img


def render_city(theme, overlay=True, hud=True, cam=None):
    th = THEMES[theme]
    img = gradient(th['bg']).convert('RGB')
    cam = cam or default_cam()
    cp = CityPainter(img, cam, theme)
    cp.skyline()
    cp.img = smog(cp.img, ('far', theme), [(520, 200, 70, 150), (760, 340, 150, 230)], th['smog'])
    cp.d = ImageDraw.Draw(cp.img)
    items = build_city()
    if theme == 'alert':
        items += alert_items()
    cp.ground(items)
    # collect sign reflections: run signs on a throwaway canvas pass to fill cp.reflect deterministically
    if cp.night:
        scratch = CityPainter(Image.new('RGB', (8, 8)), cam, theme)
        scratch.d = ImageDraw.Draw(Image.new('RGB', (8, 8)))
        for it in items:
            for p in it['prims']:
                if p['k'] == 'box' and p['signs'] and p['taper'] == 0:
                    scratch.signs(p)
        cp.reflect = scratch.reflect
        cp.reflections()
        cp.traffic()
    if overlay:
        cp.paths()
        cp.node_discs()
    for it in items:
        x0, y0, x1, y1 = it['box']
        it['depth'] = cam.depth((x0 + x1) / 2, (y0 + y1) / 2)
    items.sort(key=lambda it: (it['depth'], it['box']))
    for it in items:
        cp.item(it)
    cp.cables(items)
    img = cp.img
    if cp.night:
        img = night_sky_fx(img, cam, theme)
    sb = [(110, 130, 50, 130), (330, 160, 50, 130), (640, 180, 60, 140)] if theme == 'day' else [(300, 150, 40, 110), (640, 170, 50, 120)]
    img = smog(img, ('near', theme), sb, th['smog'])
    if theme == 'alert':
        import alert_fx
        img = alert_fx.apply(img, cam, items)
    if theme == 'day':
        img = rain(img, 'rain_day', n=700, col=(150, 150, 140), alpha=(30, 70))
    else:
        img = rain(img, ('rain', theme), n=1000, col=(150, 160, 190) if theme == 'night' else (200, 150, 160),
                   alpha=(35, 85))
    cp.img = img
    cp.d = ImageDraw.Draw(img)
    if overlay:
        cp.arrows()
        cp.pins()
    if hud:
        city_hud(cp.d, theme)
    return cp.img
