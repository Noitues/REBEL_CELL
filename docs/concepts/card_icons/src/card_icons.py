"""card_icons: one pictogram per Campaign B card (content/b/card/*.tres, keyed by proto_id), in the raid glyph grammar
(glyphs_hq.py / raid_icons.py, bible 3.5) and the B-107 reward plates' card art (screens_b107 reward_loss.net_card: a
bold white pictogram with a soft dark drop on the kind-colour gradient band): one flat white silhouette on a 512 grid,
few dark cut-outs; strokes >= 40/512, cut-outs >= 24/512; saved 256 px, white on transparent, alpha = coverage, the
full 512 canvas (the drawer draws the whole texture into its box).

    python card_icons.py <godot_root> <icon_dir> <sheet_png> [only_id ...]
        -> <icon_dir>/card_<proto lower>.png for every card, <icon_dir>/manifest.json, <sheet_png> (the review sheet)
"""
import json, math, os, re, sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageFilter

S = 512
W = 44          # the default stroke (>= 40/512)


# ---------------------------------------------------------------- primitives (512 grid, L masks; f = 255 fill, 0 cut)
def disc(d, c, r, f=255):
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=f)


def ring(d, c, ro, ri, f=255):
    disc(d, c, ro, f); disc(d, c, ri, 255 - f)


def bar(d, a, b, w=W, f=255, cap=False):
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0; n = math.hypot(dx, dy) or 1
    px, py = -dy / n * w / 2, dx / n * w / 2
    d.polygon([(x0 + px, y0 + py), (x1 + px, y1 + py), (x1 - px, y1 - py), (x0 - px, y0 - py)], fill=f)
    if cap:
        disc(d, a, w / 2, f); disc(d, b, w / 2, f)


def path(d, pts, w=W, f=255):
    for a, b in zip(pts, pts[1:]):
        bar(d, a, b, w, f)
    for p in pts[1:-1]:
        disc(d, p, w / 2, f)


def rr(d, box, r, f=255):
    d.rounded_rectangle(box, radius=r, fill=f)


def rect(d, box, f=255):
    d.rectangle(box, fill=f)


def poly(d, pts, f=255):
    d.polygon([tuple(p) for p in pts], fill=f)


def arc(d, c, r, a0, a1, w=W, f=255):
    """an arc band centred on radius r (PIL angles: degrees clockwise from +x)"""
    ro = r + w / 2
    d.arc([c[0] - ro, c[1] - ro, c[0] + ro, c[1] + ro], a0, a1, fill=f, width=int(w))


def pol(c, r, a):
    t = math.radians(a)
    return (c[0] + r * math.cos(t), c[1] + r * math.sin(t))


def head(d, tip, ang, ln=110, wd=130, f=255):
    """an arrow head with its tip at `tip`, pointing along `ang` (degrees, screen)"""
    t = math.radians(ang); ux, uy = math.cos(t), math.sin(t); nx, ny = -uy, ux
    bx, by = tip[0] - ux * ln, tip[1] - uy * ln
    poly(d, [tip, (bx + nx * wd / 2, by + ny * wd / 2), (bx - nx * wd / 2, by - ny * wd / 2)], f)


def arrow(d, a, b, w=W, ln=110, wd=130, f=255):
    t = math.atan2(b[1] - a[1], b[0] - a[0])
    e = (b[0] - math.cos(t) * ln * 0.8, b[1] - math.sin(t) * ln * 0.8)
    bar(d, a, e, w, f)
    head(d, b, math.degrees(t), ln, wd, f)


def carrow(d, c, r, a0, a1, w=W, ln=100, wd=130, f=255, cw=True):
    """a curved arrow on radius r from a0 to a1 (clockwise when cw), head at a1"""
    if cw:
        arc(d, c, r, a0, a1, w, f)
        tip = pol(c, r, a1 + math.degrees(ln / r) * 0.9)
        head(d, tip, a1 + 90 + math.degrees(ln / r) * 0.45, ln, wd, f)
    else:
        arc(d, c, r, a1, a0, w, f)
        tip = pol(c, r, a1 - math.degrees(ln / r) * 0.9)
        head(d, tip, a1 - 90 - math.degrees(ln / r) * 0.45, ln, wd, f)


def star(c, ro, ri, n, a0=-90):
    return [pol(c, ro if k % 2 == 0 else ri, a0 + 180 * k / n) for k in range(2 * n)]


def chaikin(pts, n=3):
    for _ in range(n):
        out = []
        for i in range(len(pts)):
            p, q = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * p[0] + 0.25 * q[0], 0.75 * p[1] + 0.25 * q[1]), (0.25 * p[0] + 0.75 * q[0], 0.25 * p[1] + 0.75 * q[1])]
        pts = out
    return pts


def unit(pts, c, sx, sy=None):
    sy = sx if sy is None else sy
    return [(c[0] + x * sx, c[1] + y * sy) for x, y in pts]


def rot_pts(pts, deg, c):
    t = math.radians(deg); cs, sn = math.cos(t), math.sin(t)
    return [(c[0] + (x - c[0]) * cs - (y - c[1]) * sn, c[1] + (x - c[0]) * sn + (y - c[1]) * cs) for x, y in pts]


# ---------------------------------------------------------------- motifs (each draws in absolute coords)
FLAME = [(0, -1), (0.22, -0.55), (0.48, -0.78), (0.62, -0.25), (0.72, 0.25), (0.55, 0.72), (0.2, 0.95), (-0.2, 0.95),
         (-0.55, 0.72), (-0.72, 0.25), (-0.62, -0.12), (-0.42, -0.42), (-0.3, -0.08), (-0.12, -0.55)]
FLAME_CORE = [(0, -0.05), (0.3, 0.45), (0.2, 0.74), (-0.2, 0.74), (-0.3, 0.45)]


def flame(d, c, s, core=True, f=255):
    poly(d, chaikin(unit(FLAME, c, s), 2), f)
    if core:
        poly(d, chaikin(unit(FLAME_CORE, c, s), 2), 255 - f)


def drop(d, c, s, f=255):
    pts = [(0, -1)] + [(0.62 * math.cos(math.radians(t)), 0.36 + 0.62 * math.sin(math.radians(t))) for t in range(-28, 209, 8)]
    poly(d, chaikin(unit(pts, c, s), 1), f)


def bolt(d, c, s, f=255):
    pts = [(0.25, -1), (-0.55, 0.12), (-0.05, 0.12), (-0.3, 1), (0.6, -0.2), (0.08, -0.2), (0.38, -1)]
    poly(d, unit(pts, c, s), f)


def virus(d, c, r, f=255, spikes=8, holes=True, a0=0):
    core = r * 0.6
    disc(d, c, core, f)
    for k in range(spikes):
        a = a0 + 360 * k / spikes
        bar(d, pol(c, core * 0.8, a), pol(c, r * 0.86, a), max(40, r * 0.2), f)
        disc(d, pol(c, r * 0.84, a), max(26, r * 0.16), f)
    if holes:
        for p in ((-0.3, -0.22), (0.3, -0.12), (-0.05, 0.32)):
            disc(d, (c[0] + p[0] * core, c[1] + p[1] * core), max(14, core * 0.17), 255 - f)


def bomb(d, c, r, f=255, spark=True):
    disc(d, c, r, f)
    cap = pol(c, r * 0.95, -50)
    poly(d, rot_pts([(cap[0] - 34, cap[1] - 30), (cap[0] + 34, cap[1] - 30), (cap[0] + 34, cap[1] + 30), (cap[0] - 34, cap[1] + 30)], 40, cap), f)
    disc(d, (c[0] - r * 0.38, c[1] - r * 0.38), r * 0.17, 255 - f)
    if spark:
        tip = pol(c, r * 1.35, -42)
        arc(d, (tip[0] - 40, tip[1] + 50), 50, 190, 300, 30, f)
        poly(d, star((tip[0] + 18, tip[1] - 6), 62, 24, 6), f)


def skull(d, c, s, f=255):
    disc(d, (c[0], c[1] - 0.18 * s), 0.82 * s, f)
    rr(d, [c[0] - 0.5 * s, c[1] + 0.2 * s, c[0] + 0.5 * s, c[1] + 0.92 * s], 0.16 * s, f)
    for x in (-0.34, 0.34):
        disc(d, (c[0] + x * s, c[1] + 0.02 * s), 0.22 * s, 255 - f)
    poly(d, [(c[0], c[1] + 0.26 * s), (c[0] - 0.12 * s, c[1] + 0.46 * s), (c[0] + 0.12 * s, c[1] + 0.46 * s)], 255 - f)
    for x in (-0.18, 0.18):
        rect(d, [c[0] + x * s - 0.06 * s, c[1] + 0.66 * s, c[0] + x * s + 0.06 * s, c[1] + 0.94 * s], 255 - f)


def gear(d, c, r, n=8, hole=0.32, f=255, a0=0):
    disc(d, c, r * 0.76, f)
    tw = 2 * math.pi * r * 0.75 / n * 0.5
    for k in range(n):
        a = a0 + 360 * k / n
        bar(d, pol(c, r * 0.6, a), pol(c, r, a), tw, f)
    if hole:
        disc(d, c, r * hole, 255 - f)


def shield(d, c, s, split=True, f=255):
    pts = [(-0.78, -0.86), (0, -1.0), (0.78, -0.86), (0.78, 0.0), (0.5, 0.55), (0, 1.0), (-0.5, 0.55), (-0.78, 0.0)]
    poly(d, chaikin(unit(pts, c, s), 1), f)
    if split:
        inner = [(0.08, -0.72), (0.58, -0.66), (0.58, -0.02), (0.36, 0.42), (0.08, 0.66)]
        poly(d, chaikin(unit(inner, c, s), 1), 255 - f)


def heart(d, c, s, f=255):
    disc(d, (c[0] - 0.42 * s, c[1] - 0.28 * s), 0.5 * s, f)
    disc(d, (c[0] + 0.42 * s, c[1] - 0.28 * s), 0.5 * s, f)
    poly(d, [(c[0] - 0.88 * s, c[1] - 0.12 * s), (c[0] + 0.88 * s, c[1] - 0.12 * s), (c[0], c[1] + 0.9 * s)], f)


def clockface(d, c, r, h=(-90, 0), f=255, w=W):
    ring(d, c, r, r - w, f)
    bar(d, c, pol(c, r * 0.55, h[0]), w * 0.9, f, True)
    bar(d, c, pol(c, r * 0.7, h[1]), w * 0.9, f, True)


def padlock(d, c, s, hole=True, f=255):
    arc(d, (c[0], c[1] - 0.25 * s), 0.52 * s, 180, 360, 0.24 * s, f)
    rect(d, [c[0] - 0.76 * s, c[1] - 0.3 * s, c[0] - 0.28 * s, c[1] - 0.2 * s], f)
    rect(d, [c[0] + 0.28 * s, c[1] - 0.3 * s, c[0] + 0.76 * s, c[1] - 0.2 * s], f)
    rr(d, [c[0] - 0.8 * s, c[1] - 0.22 * s, c[0] + 0.8 * s, c[1] + 0.9 * s], 0.14 * s, f)
    if hole:
        disc(d, (c[0], c[1] + 0.22 * s), 0.16 * s, 255 - f)
        poly(d, [(c[0] - 0.08 * s, c[1] + 0.25 * s), (c[0] + 0.08 * s, c[1] + 0.25 * s), (c[0] + 0.12 * s, c[1] + 0.6 * s), (c[0] - 0.12 * s, c[1] + 0.6 * s)], 255 - f)


def eye(d, c, s, f=255, pupil=True):
    pts = [pol((c[0], c[1] + 0.9 * s), 1.35 * s, a) for a in range(-142, -37, 6)] + \
          [pol((c[0], c[1] - 0.9 * s), 1.35 * s, a) for a in range(38, 143, 6)]
    poly(d, pts, f)
    ring(d, c, 0.42 * s, 0.25 * s, 255 - f)
    if not pupil:
        disc(d, c, 0.25 * s, 255 - f)


def magnifier(d, c, r, w=W + 6, f=255, ang=45):
    ring(d, c, r, r - w, f)
    bar(d, pol(c, r - 6, ang), pol(c, r * 2.0, ang), w * 1.25, f, True)


def key(d, a, b, w=W + 4, f=255):
    """a key, bow at a, tip at b"""
    t = math.atan2(b[1] - a[1], b[0] - a[0]); ux, uy = math.cos(t), math.sin(t); nx, ny = -uy, ux
    ring(d, a, 92, 42, f)
    bar(d, (a[0] + ux * 80, a[1] + uy * 80), b, w, f)
    for o in (0.0, 0.22):
        p = (b[0] - ux * (30 + o * 300), b[1] - uy * (30 + o * 300))
        bar(d, p, (p[0] + nx * 70, p[1] + ny * 70), 40, f)


def bricks(d, box, rows=3, f=255, gap=24):
    x0, y0, x1, y1 = box
    rect(d, box, f)
    h = (y1 - y0) / rows
    for i in range(1, rows):
        rect(d, [x0, y0 + i * h - gap / 2, x1, y0 + i * h + gap / 2], 255 - f)
    for i in range(rows):
        off = 0.5 if i % 2 else 0.0
        for k in range(3):
            x = x0 + (x1 - x0) * (k + off) / 2.0
            if x0 + 30 < x < x1 - 30:
                rect(d, [x - gap / 2, y0 + i * h, x + gap / 2, y0 + (i + 1) * h], 255 - f)


def bullet(d, c, s, ang=-90, f=255):
    """a cartridge pointing along ang, length 2s"""
    pts = [(-1, -0.32), (0.25, -0.32), (0.55, -0.26), (0.85, -0.12), (1, 0), (0.85, 0.12), (0.55, 0.26), (0.25, 0.32), (-1, 0.32)]
    p = unit(pts, c, s)
    poly(d, rot_pts(p, ang, c), f)
    poly(d, rot_pts([(c[0] + 0.08 * s, c[1] - 0.4 * s), (c[0] + 0.2 * s, c[1] - 0.4 * s), (c[0] + 0.2 * s, c[1] + 0.4 * s), (c[0] + 0.08 * s, c[1] + 0.4 * s)], ang, c), 255 - f)


def cloud(d, c, s, f=255):
    for p, r in (((-0.5, 0.12), 0.38), ((0.0, -0.15), 0.52), ((0.5, 0.1), 0.4)):
        disc(d, (c[0] + p[0] * s, c[1] + p[1] * s), r * s, f)
    rr(d, [c[0] - 0.88 * s, c[1] + 0.05 * s, c[0] + 0.9 * s, c[1] + 0.5 * s], 0.22 * s, f)


def card(d, box, r=26, f=255, corner=True):
    rr(d, box, r, f)
    if corner:
        x0, y0, x1, y1 = box
        rr(d, [x0 + 30, y0 + 30, x0 + 30 + (x1 - x0) * 0.26, y0 + 30 + (x1 - x0) * 0.26], 10, 255 - f)


def turret(d, c, s, ang=-50, f=255):
    poly(d, [(c[0] - 0.9 * s, c[1] + 0.9 * s), (c[0] + 0.9 * s, c[1] + 0.9 * s), (c[0] + 0.62 * s, c[1] + 0.45 * s), (c[0] - 0.62 * s, c[1] + 0.45 * s)], f)
    d.pieslice([c[0] - 0.62 * s, c[1] - 0.2 * s, c[0] + 0.62 * s, c[1] + 1.0 * s], 180, 360, fill=f)
    bar(d, (c[0], c[1] + 0.3 * s), pol((c[0], c[1] + 0.3 * s), 1.15 * s, ang), 0.3 * s, f)


def chain_link(d, c, w2, h2, ang=0, th=40, f=255):
    lay = Image.new('L', (S, S), 0); dd = ImageDraw.Draw(lay)
    rr(dd, [c[0] - w2, c[1] - h2, c[0] + w2, c[1] + h2], h2, 255)
    rr(dd, [c[0] - w2 + th, c[1] - h2 + th, c[0] + w2 - th, c[1] + h2 - th], h2 - th, 0)
    return lay.rotate(-ang, resample=Image.BICUBIC, center=c)


# ---------------------------------------------------------------- the canvas
class G:
    def __init__(self):
        self.m = Image.new('L', (S, S), 0)
        self.d = ImageDraw.Draw(self.m)

    def put(self, lay, gap=0):
        if gap:
            k = lay
            for _ in range(int(math.ceil(gap / 4))):
                k = k.filter(ImageFilter.MaxFilter(9))
            self.m = ImageChops.subtract(self.m, k)
        self.m = ImageChops.lighter(self.m, lay)
        self.d = ImageDraw.Draw(self.m)

    def sub(self, fn, gap=0, rot=0, center=(256, 256)):
        lay = Image.new('L', (S, S), 0)
        fn(ImageDraw.Draw(lay))
        if rot:
            lay = lay.rotate(rot, resample=Image.BICUBIC, center=center)
        self.put(lay, gap)

    def cut(self, fn):
        lay = Image.new('L', (S, S), 0)
        fn(ImageDraw.Draw(lay))
        self.m = ImageChops.subtract(self.m, lay)
        self.d = ImageDraw.Draw(self.m)

    def rotate(self, deg, center=(256, 256)):
        self.m = self.m.rotate(deg, resample=Image.BICUBIC, center=center)
        self.d = ImageDraw.Draw(self.m)


C = (256, 256)
ICONS = {}   # proto id -> (idea, fn(g))


def icon(pid, idea):
    def wrap(fn):
        ICONS[pid] = (idea, fn)
        return fn
    return wrap


# ================================================================ the cards
# ---- ATTACK and its archetypes -----------------------------------------------------------------
@icon('BREACH', 'arrow punched through a wall slab')
def _(g):
    d = g.d
    bricks(d, [200, 40, 312, 472], 4)
    g.cut(lambda d: rect(d, [176, 196, 336, 316]))
    g.sub(lambda d: arrow(d, (30, 256), (490, 256), 64, 150, 200), gap=20)


@icon('TWIN', 'two arrows through a wall slab')
def _(g):
    bricks(g.d, [210, 40, 302, 472], 4)
    g.cut(lambda d: (rect(d, [186, 100, 326, 210]), rect(d, [186, 302, 326, 412])))
    g.sub(lambda d: (arrow(d, (30, 156), (490, 156), 52, 130, 170), arrow(d, (30, 356), (490, 356), 52, 130, 170)), gap=18)


@icon('FORTIFY', 'brick wall with a plus')
def _(g):
    bricks(g.d, [36, 200, 476, 470], 3)
    g.sub(lambda d: (rect(d, [216, 30, 296, 200]), rect(d, [170, 76, 342, 156])), gap=0)


@icon('NUDGE', 'wheel pointer between two small arrows')
def _(g):
    d = g.d
    poly(d, [(256, 470), (176, 250), (336, 250)])
    disc(d, (256, 230), 82)
    disc(d, (256, 230), 30, 0)
    carrow(d, (256, 300), 220, 245, 205, 46, 90, 120, cw=False)
    carrow(d, (256, 300), 220, 295, 335, 46, 90, 120, cw=True)


@icon('ABLATIVE', 'three armour plates stacked, an up arrow')
def _(g):
    d = g.d
    for i, y in enumerate((340, 250, 160)):
        rr(d, [60 + i * 20, y, 360 - i * 20, y + 70], 22)
    head(d, (430, 60), -90, 120, 150)
    rect(d, [404, 150, 456, 420])


@icon('ACIDRAIN', 'cloud with three drops')
def _(g):
    cloud(g.d, (256, 170), 230)
    for x, y in ((140, 400), (256, 440), (372, 400)):
        g.sub(lambda d, x=x, y=y: drop(d, (x, y), 70), gap=14)


@icon('AUDIT', 'balance scales')
def _(g):
    d = g.d
    rect(d, [232, 70, 280, 430])
    rect(d, [140, 420, 372, 470])
    bar(d, (70, 140), (442, 140), 44)
    disc(d, (256, 90), 40)
    for x in (112, 400):
        bar(d, (x, 150), (x - 66, 300), 26); bar(d, (x, 150), (x + 66, 300), 26)
        d.pieslice([x - 96, 230, x + 96, 380], 0, 180, fill=255)


@icon('BARBED', 'strand with barbs')
def _(g):
    d = g.d
    bar(d, (24, 300), (488, 210), 40)
    for x in (110, 256, 402):
        y = 300 - (x - 24) * 90 / 464
        poly(d, star((x, y), 104, 30, 4, -20))


@icon('BATTERY', 'battery with a plus')
def _(g):
    d = g.d
    rr(d, [60, 140, 430, 372], 34)
    rect(d, [430, 206, 476, 306])
    rr(d, [104, 184, 386, 328], 14, 0)
    rect(d, [222, 206, 268, 306]); rect(d, [194, 234, 296, 278])
    rect(d, [310, 206, 360, 306])


@icon('BLACKOUT', 'light bulb, switched off (slash)')
def _(g):
    d = g.d
    disc(d, (256, 200), 150)
    poly(d, [(170, 290), (342, 290), (318, 370), (194, 370)])
    rr(d, [190, 380, 322, 420], 12); rr(d, [204, 430, 308, 470], 12)
    g.cut(lambda d: bar(d, (60, 440), (452, 48), 90))
    g.sub(lambda d: bar(d, (70, 430), (442, 58), 44))


@icon('BOOTSTRAP', 'boot with a pull strap')
def _(g):
    d = g.d
    poly(d, [(150, 70), (310, 70), (310, 300), (440, 330), (470, 380), (470, 440), (110, 440), (110, 300), (150, 260)])
    rect(d, [100, 444, 480, 476])
    ring(d, (330, 96), 56, 26)
    rect(d, [150, 150, 310, 172], 0)


@icon('BUFFER', 'heart inside a bubble')
def _(g):
    d = g.d
    ring(d, C, 230, 186)
    heart(d, (256, 262), 110)
    disc(d, (170, 150), 22, 0)


@icon('CALIBRATION', 'calipers')
def _(g):
    d = g.d
    rect(d, [60, 90, 470, 150])
    poly(d, [(60, 150), (130, 150), (130, 300), (60, 420)])
    rect(d, [270, 60, 360, 180])
    poly(d, [(270, 180), (340, 180), (340, 300), (270, 420)])
    for x in (170, 210, 400, 430):
        rect(d, [x, 100, x + 14, 130], 0)


@icon('CASCADE', 'blocks tumbling down a stair')
def _(g):
    d = g.d
    for i in range(3):
        rect(d, [40 + i * 150, 120 + i * 120, 190 + i * 150, 160 + i * 120 + 70])
    g.sub(lambda d: rr(d, [80, 30, 170, 110], 10), gap=0, rot=20, center=(125, 70))
    g.sub(lambda d: rr(d, [230, 140, 320, 220], 10), gap=0, rot=-25, center=(275, 180))
    g.sub(lambda d: rr(d, [380, 260, 470, 340], 10), gap=0, rot=15, center=(425, 300))


@icon('COUNTERMEASURE', 'boomerang turning back')
def _(g):
    d = g.d
    poly(d, chaikin([(60, 420), (230, 80), (300, 60), (330, 120), (180, 400), (460, 380), (470, 440), (400, 470), (90, 470)], 2))
    g.cut(lambda d: disc(d, (290, 110), 20))


@icon('DAISY', 'daisy flower')
def _(g):
    d = g.d
    for k in range(8):
        a = 360 * k / 8
        p = pol((256, 230), 150, a)
        g.sub(lambda d, p=p, a=a: d.ellipse([p[0] - 72, p[1] - 44, p[0] + 72, p[1] + 44], fill=255), rot=-a, center=p)
    g.cut(lambda d: disc(d, (256, 230), 96))
    g.sub(lambda d: disc(d, (256, 230), 70))
    g.sub(lambda d: rect(d, [240, 380, 272, 490]))


@icon('DEBUG', 'beetle bug')
def _(g):
    d = g.d
    d.ellipse([150, 170, 362, 460], fill=255)
    disc(d, (256, 150), 70)
    rect(d, [244, 230, 268, 460], 0)
    for y, dy in ((250, -40), (320, 0), (390, 40)):
        bar(d, (170, y), (60, y + dy), 36, cap=True); bar(d, (342, y), (452, y + dy), 36, cap=True)
    bar(d, (226, 100), (180, 40), 30, cap=True); bar(d, (286, 100), (332, 40), 30, cap=True)


@icon('DEEPSCAN', 'radar sweep')
def _(g):
    d = g.d
    ring(d, C, 230, 188)
    ring(d, C, 140, 100)
    d.pieslice([26, 26, 486, 486], 200, 270, fill=255)
    disc(d, C, 40)
    disc(d, (346, 330), 30)


@icon('DEFRAG', 'scattered blocks sorted into a row')
def _(g):
    d = g.d
    for x, y in ((50, 60), (210, 110), (370, 50), (120, 200)):
        rect(d, [x, y, x + 90, y + 90])
    for x in (40, 160, 280, 400):
        rect(d, [x, 380, x + 80, 470])
    head(d, (256, 362), 90, 70, 120)
    rect(d, [236, 300, 276, 300])


@icon('DISARM', 'pistol cut by a slash')
def _(g):
    d = g.d
    rect(d, [70, 150, 420, 220])
    poly(d, [(90, 216), (180, 216), (160, 400), (60, 386)])
    rect(d, [180, 216, 250, 240]); rect(d, [226, 216, 250, 290]); rect(d, [170, 270, 250, 292])
    rect(d, [400, 130, 440, 160])
    g.cut(lambda d: bar(d, (60, 470), (470, 40), 92))
    g.sub(lambda d: bar(d, (80, 450), (450, 60), 44))


@icon('DISSOLVE', 'block melting into drips')
def _(g):
    d = g.d
    rr(d, [80, 50, 432, 260], 30)
    for x, y1 in ((110, 350), (220, 440), (330, 380)):
        rect(d, [x, 240, x + 60, y1]); disc(d, (x + 30, y1), 46)
    rect(d, [130, 90, 220, 120], 0)


@icon('EXPOSE', 'open eye')
def _(g):
    eye(g.d, C, 210)


@icon('FACTORYRESET', 'factory with a reset arrow')
def _(g):
    d = g.d
    poly(d, [(40, 470), (40, 260), (150, 330), (150, 260), (260, 330), (260, 260), (370, 330), (370, 120), (440, 120), (440, 470)])
    for x in (80, 190, 300):
        rect(d, [x, 380, x + 40, 420], 0)
    carrow(d, (150, 140), 86, 200, 100, 40, 70, 100)


@icon('FALSEFLAG', 'waving flag on a pole')
def _(g):
    d = g.d
    rect(d, [80, 40, 126, 480])
    poly(d, chaikin([(126, 60), (250, 40), (330, 90), (450, 70), (450, 270), (330, 290), (250, 240), (126, 260)], 2))
    g.cut(lambda d: poly(d, [(220, 110), (360, 120), (360, 220), (220, 210)]))
    g.sub(lambda d: poly(d, [(250, 140), (330, 146), (330, 192), (250, 186)]))


@icon('FEINT', 'dashed arrow faking left, going right')
def _(g):
    d = g.d
    for a0 in (200, 236, 272):
        arc(d, (256, 300), 170, a0, a0 + 24, 44)
    carrow(d, (256, 300), 170, 308, 350, 44, 110, 150)
    disc(d, (256, 300), 50)


@icon('FIELDREPAIR', 'medkit case with a cross')
def _(g):
    d = g.d
    rr(d, [40, 140, 472, 450], 36)
    rr(d, [180, 70, 332, 150], 20); rr(d, [214, 104, 298, 150], 4, 0)
    rect(d, [226, 200, 286, 400], 0); rect(d, [156, 270, 356, 330], 0)


@icon('FIREBREAK', 'flame stopped by a bar')
def _(g):
    flame(g.d, (256, 210), 190)
    g.sub(lambda d: rect(d, [30, 380, 482, 450]), gap=24)


@icon('FRACTURE', 'shattered square, pieces apart')
def _(g):
    d = g.d
    poly(d, [(50, 50), (250, 50), (210, 180), (290, 260), (200, 470), (50, 470)])
    poly(d, [(300, 50), (462, 50), (462, 280), (350, 250), (270, 175)])
    poly(d, [(340, 300), (462, 330), (462, 470), (260, 470)])


@icon('HIJACK', 'grappling hook')
def _(g):
    d = g.d
    rect(d, [232, 50, 280, 360])
    ring(d, (256, 60), 50, 22)
    for s in (-1, 1):
        arc(d, (256 + s * 120, 330), 120, 0 if s < 0 else 90, 90 if s < 0 else 180, 44)
        poly(d, [(256 + s * 230, 330), (256 + s * 270, 230), (256 + s * 200, 300)])
    disc(d, (256, 440), 30)


@icon('HOTBOOT', 'power symbol with a flame tip')
def _(g):
    d = g.d
    arc(d, (256, 290), 170, -50, 230, 54)
    rect(d, [228, 120, 284, 300])
    flame(d, (256, 90), 70, core=False)


@icon('INCUBATE', 'egg with a virus inside')
def _(g):
    d = g.d
    d.ellipse([110, 40, 402, 470], fill=255)
    g.cut(lambda d: virus(d, (256, 290), 130, holes=False))
    g.sub(lambda d: disc(d, (256, 290), 48))


@icon('JAM', 'gear with a bar jammed in')
def _(g):
    gear(g.d, (220, 280), 190, 9)
    g.sub(lambda d: bar(d, (60, 60), (470, 440), 60), gap=22)


@icon('LASERSIGHT', 'laser beam ending in a dot with rays')
def _(g):
    d = g.d
    rr(d, [30, 330, 200, 410], 16)
    bar(d, (200, 360), (360, 200), 34)
    disc(d, (390, 170), 54)
    for a in (-135, -45, 45, 135, 0, -90):
        bar(d, pol((390, 170), 80, a), pol((390, 170), 120, a), 26)


@icon('LEECH', 'two fangs over a drop')
def _(g):
    d = g.d
    d.pieslice([40, -100, 472, 200], 0, 180, fill=255)
    for x in (160, 352):
        poly(d, [(x - 52, 90), (x + 52, 90), (x, 260)])
    drop(d, (256, 380), 100)


@icon('LOCKON', 'lock-on brackets round a dot')
def _(g):
    d = g.d
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = 256 + sx * 190, 256 + sy * 190
            rect(d, [min(cx, cx - sx * 140), min(cy, cy - sy * 44), max(cx, cx - sx * 140), max(cy, cy - sy * 44)])
            rect(d, [min(cx, cx - sx * 44), min(cy, cy - sy * 140), max(cx, cx - sx * 44), max(cy, cy - sy * 140)])
    disc(d, C, 70)


@icon('OPENWIDE', 'double doors swung open')
def _(g):
    d = g.d
    poly(d, [(40, 60), (210, 110), (210, 400), (40, 450)])
    poly(d, [(472, 60), (302, 110), (302, 400), (472, 450)])
    disc(d, (176, 256), 18, 0); disc(d, (336, 256), 18, 0)
    rect(d, [226, 100, 286, 410], 0)


@icon('OVERCLOCK', 'speed gauge, needle at the top')
def _(g):
    d = g.d
    arc(d, (256, 320), 190, 180, 360, 54)
    for a in (200, 230, 260, 290, 320):
        bar(d, pol((256, 320), 110, a), pol((256, 320), 140, a), 30)
    bar(d, (256, 320), pol((256, 320), 170, -35), 44)
    disc(d, (256, 320), 52)
    rect(d, [60, 400, 452, 450])


@icon('OVERDRIVE', 'rocket')
def _(g):
    d = g.d
    pts = [(256, 30), (320, 110), (330, 330), (182, 330), (192, 110)]
    poly(d, chaikin(pts, 1))
    poly(d, [(182, 220), (110, 330), (110, 380), (182, 340)]); poly(d, [(330, 220), (402, 330), (402, 380), (330, 340)])
    disc(d, (256, 180), 34, 0)
    flame(d, (256, 410), 70, core=False)


@icon('OVERLOAD', 'plug sparking')
def _(g):
    d = g.d
    rr(d, [110, 200, 290, 330], 30)
    rect(d, [290, 220, 400, 250]); rect(d, [290, 280, 400, 310])
    bar(d, (130, 300), (40, 470), 44)
    bolt(d, (410, 120), 90)


@icon('PATCH', 'bandage plaster crossed')
def _(g):
    g.sub(lambda d: rr(d, [40, 190, 472, 322], 66), rot=45)
    g.cut(lambda d: rr(d, [196, 196, 316, 316], 20))
    g.sub(lambda d: rr(d, [40, 190, 472, 322], 66), gap=22, rot=-45)
    g.cut(lambda d: [disc(d, (256 + x, 256 + y), 13) for x, y in ((-30, -30), (30, -30), (-30, 30), (30, 30))])


@icon('PAYLOAD', 'crate with a virus mark')
def _(g):
    d = g.d
    poly(d, [(256, 40), (470, 140), (470, 380), (256, 480), (42, 380), (42, 140)])
    bar(d, (256, 250), (256, 480), 26, 0); bar(d, (42, 140), (256, 250), 26, 0); bar(d, (470, 140), (256, 250), 26, 0)
    g.cut(lambda d: virus(d, (150, 330), 74, holes=False))


@icon('REDLINE', 'thermometer at the top')
def _(g):
    d = g.d
    rr(d, [196, 30, 316, 380], 60)
    disc(d, (256, 400), 90)
    rr(d, [234, 70, 278, 380], 22, 0)
    disc(d, (256, 400), 46, 0)
    for y in (100, 170, 240):
        rect(d, [330, y, 400, y + 30])
    g.sub(lambda d: (rect(d, [246, 80, 266, 380]), disc(d, (256, 400), 28)))


@icon('REVERSE', 'two arrows, opposite ways')
def _(g):
    d = g.d
    arrow(d, (60, 170), (470, 170), 56, 130, 170)
    arrow(d, (452, 350), (42, 350), 56, 130, 170)


@icon('ROOTKIT', 'tree with deep roots under a ground line')
def _(g):
    d = g.d
    disc(d, (256, 110), 90)
    rect(d, [234, 140, 278, 250])
    rect(d, [40, 230, 472, 270])
    for a, b in (((256, 270), (256, 470)), ((256, 300), (120, 440)), ((256, 300), (392, 440)), ((150, 400), (70, 380)), ((362, 400), (442, 380))):
        bar(d, a, b, 40, cap=True)


@icon('ROT', 'mushroom')
def _(g):
    d = g.d
    d.pieslice([40, 70, 472, 450], 180, 360, fill=255)
    rr(d, [190, 250, 322, 470], 40)
    for p in ((150, 180), (260, 130), (360, 190)):
        disc(d, p, 32, 0)


@icon('RUSTBOMB', 'hex nut flaking rust')
def _(g):
    d = g.d
    poly(d, [pol((236, 236), 200, a) for a in range(0, 360, 60)])
    disc(d, (236, 236), 84, 0)
    for p in ((420, 400), (350, 460), (460, 300)):
        g.sub(lambda d, p=p: rect(d, [p[0] - 30, p[1] - 30, p[0] + 30, p[1] + 30]), gap=0, rot=30, center=p)


@icon('SALVAGE', 'horseshoe magnet')
def _(g):
    d = g.d
    arc(d, (256, 230), 150, 180, 360, 96)
    rect(d, [58, 230, 154, 400]); rect(d, [358, 230, 454, 400])
    rect(d, [58, 400, 154, 470]); rect(d, [358, 400, 454, 470])
    rect(d, [58, 380, 154, 404], 0); rect(d, [358, 380, 454, 404], 0)


@icon('SALVO', 'three missiles rising')
def _(g):
    d = g.d
    for x, y in ((110, 160), (256, 60), (402, 160)):
        poly(d, [(x, y), (x + 44, y + 70), (x + 44, y + 260), (x - 44, y + 260), (x - 44, y + 70)])
        poly(d, [(x - 44, y + 190), (x - 80, y + 280), (x - 44, y + 260)]); poly(d, [(x + 44, y + 190), (x + 80, y + 280), (x + 44, y + 260)])


@icon('SCRAMBLE', 'shuffle arrows')
def _(g):
    d = g.d
    path(d, [(40, 150), (170, 150), (330, 360), (400, 360)], 48)
    head(d, (490, 360), 0, 110, 160)
    g.sub(lambda d: (path(d, [(40, 360), (170, 360), (330, 150), (400, 150)], 48), head(d, (490, 150), 0, 110, 160)), gap=24)


@icon('SHOCK', 'lightning bolt')
def _(g):
    bolt(g.d, C, 230)


@icon('SHRED', 'paper fed into a shredder, strips out')
def _(g):
    d = g.d
    rect(d, [130, 30, 382, 160])
    rect(d, [170, 70, 340, 92], 0); rect(d, [170, 112, 300, 134], 0)
    rr(d, [40, 180, 472, 290], 20)
    for x in (110, 190, 270, 350):
        rect(d, [x, 300, x + 50, 470 - (x % 3) * 20])


@icon('SIPHON', 'funnel with a drop')
def _(g):
    d = g.d
    poly(d, [(40, 60), (472, 60), (296, 260), (296, 380), (216, 420), (216, 260)])
    rect(d, [100, 100, 412, 130], 0)
    drop(d, (256, 410), 0) if False else disc(d, (256, 460), 34)


@icon('SLEDGE', 'sledgehammer')
def _(g):
    g.sub(lambda d: (rr(d, [120, 40, 392, 170], 20), rect(d, [226, 170, 286, 480]), rect(d, [226, 200, 286, 230], 0)), rot=-30, center=(256, 260))


@icon('SPLICE', 'two cable ends joining')
def _(g):
    d = g.d
    bar(d, (30, 330), (150, 256), 48)
    rr(d, [140, 200, 260, 312], 18)
    rect(d, [260, 220, 300, 238]); rect(d, [260, 274, 300, 292])
    rr(d, [310, 200, 400, 312], 18)
    rect(d, [310, 222, 340, 290], 0)
    bar(d, (400, 256), (480, 180), 48)
    head(d, (256, 120), 0, 0, 0)


@icon('SPOTLIGHT', 'spotlight lamp and beam')
def _(g):
    d = g.d
    g.sub(lambda d: (rr(d, [40, 70, 220, 200], 30), rect(d, [210, 50, 250, 220])), rot=-30, center=(140, 140))
    g.sub(lambda d: poly(d, [(250, 150), (220, 230), (430, 470), (490, 300)]), gap=20)
    rect(d, [100, 250, 140, 470]); rect(d, [50, 440, 190, 480])


@icon('STALL', 'pause bars in a ring')
def _(g):
    d = g.d
    ring(d, C, 230, 186)
    rr(d, [170, 140, 230, 372], 10); rr(d, [282, 140, 342, 372], 10)


@icon('SURGE', 'zig-zag arrow up')
def _(g):
    d = g.d
    path(d, [(40, 440), (180, 280), (270, 360), (420, 160)], 56)
    head(d, (480, 70), -55, 140, 180)


@icon('SWEEP', 'broom')
def _(g):
    g.sub(lambda d: (rect(d, [232, 20, 280, 290]), poly(d, [(170, 280), (342, 280), (420, 480), (92, 480)]),
                     rect(d, [190, 330, 210, 480], 0), rect(d, [302, 330, 322, 480], 0), rect(d, [246, 330, 266, 480], 0)),
          rot=25, center=(256, 256))


@icon('TETHERLINE', 'two weights tethered by a cord')
def _(g):
    d = g.d
    disc(d, (110, 380), 80); disc(d, (402, 132), 80)
    for t in (0.3, 0.5, 0.7):
        p = (110 + (402 - 110) * t, 380 + (132 - 380) * t)
        d.ellipse([p[0] - 46, p[1] - 28, p[0] + 46, p[1] + 28], fill=255)
    bar(d, (110, 380), (402, 132), 30)
    disc(d, (110, 380), 30, 0); disc(d, (402, 132), 30, 0)


@icon('VIRUS', 'virus: spiked core with knobbed spikes')
def _(g):
    virus(g.d, C, 236, spikes=8)


@icon('WEAKEN', 'down arrow snapped in two')
def _(g):
    d = g.d
    rect(d, [206, 30, 306, 190])
    poly(d, [(206, 190), (306, 170), (306, 200), (206, 220)], 0) if False else None
    g.sub(lambda d: (rect(d, [206, 230, 306, 330]), head(d, (256, 490), 90, 170, 300)), gap=0, rot=-12, center=(256, 330))
    g.cut(lambda d: poly(d, [(190, 180), (330, 160), (330, 210), (190, 240)]))


@icon('WORM', 'segmented worm')
def _(g):
    d = g.d
    for i, t in enumerate(np.linspace(0, 1, 6)):
        x = 70 + 370 * t; y = 300 + 90 * math.sin(t * 2.5 * math.pi)
        disc(d, (x, y), 64 if i < 5 else 80)
        if i < 5:
            disc(d, (x + 30, y), 12, 0) if False else None
    g.cut(lambda d: disc(d, (460, 300 + 90 * math.sin(2.5 * math.pi)), 18))


@icon('SKIM', 'two cards fanned')
def _(g):
    g.sub(lambda d: card(d, [90, 90, 290, 400], corner=False), rot=14, center=(190, 245))
    g.sub(lambda d: card(d, [220, 110, 420, 420]), gap=22, rot=-12, center=(320, 265))


@icon('PROBE', 'magnifier')
def _(g):
    magnifier(g.d, (210, 210), 160, 54)
    g.d.ellipse([140, 140, 200, 200], fill=255)


@icon('RECURSION', 'spiral')
def _(g):
    d = g.d
    pts = []
    for k in range(0, 700, 6):
        t = math.radians(k); r = 40 + k * 0.27
        pts.append((256 + r * math.cos(t), 256 + r * math.sin(t)))
    path(d, pts, 46)
    head(d, (256 + 240 * math.cos(math.radians(700)) + 20, 256 + 230 * math.sin(math.radians(700)) + 60), 140, 0, 0)


@icon('RECYCLE', 'three chasing arrows in a triangle')
def _(g):
    d = g.d
    v = [pol(C, 210, a) for a in (-90, 30, 150)]
    for i in range(3):
        a, b = v[i], v[(i + 1) % 3]
        p = (a[0] + (b[0] - a[0]) * 0.18, a[1] + (b[1] - a[1]) * 0.18)
        q = (a[0] + (b[0] - a[0]) * 0.78, a[1] + (b[1] - a[1]) * 0.78)
        arrow(d, p, q, 50, 100, 130)


@icon('SYSCALL', 'terminal window with a prompt')
def _(g):
    d = g.d
    rr(d, [30, 70, 482, 442], 30)
    rect(d, [62, 140, 450, 410], 0)
    for x in (80, 120, 160):
        disc(d, (x, 105), 14, 0)
    path(d, [(110, 200), (190, 260), (110, 320)], 44)
    rect(d, [230, 320, 380, 364])


@icon('MINDMELD', 'two heads, minds joined')
def _(g):
    d = g.d
    for s in (-1, 1):
        cx = 256 + s * 120
        disc(d, (cx, 220), 110)
        poly(d, [(cx - 90, 260), (cx + 90, 260), (cx + 110, 470), (cx - 110, 470)])
    g.cut(lambda d: rect(d, [234, 40, 278, 480]))
    g.sub(lambda d: (disc(d, (256, 200), 52)), gap=20)


@icon('ARCHIVE', 'archive box with a label slot')
def _(g):
    d = g.d
    rect(d, [40, 70, 472, 170])
    rect(d, [70, 190, 442, 460])
    rr(d, [190, 240, 322, 290], 14, 0)


@icon('BROADCAST', 'antenna mast with waves both ways')
def _(g):
    d = g.d
    bar(d, (256, 200), (160, 480), 40); bar(d, (256, 200), (352, 480), 40)
    rect(d, [190, 380, 322, 410])
    disc(d, (256, 170), 46)
    for r in (110, 190):
        arc(d, (256, 170), r, 140, 220, 40); arc(d, (256, 170), r, -40, 40, 40)


@icon('DATASPIKE', 'bar chart with one tall spike')
def _(g):
    d = g.d
    for x, h in ((50, 120), (140, 180), (320, 150), (410, 90)):
        rect(d, [x, 460 - h, x + 60, 460])
    poly(d, [(256, 30), (300, 460), (212, 460)])
    rect(d, [30, 460, 482, 490])


@icon('MOMENTUM', 'ball rolling with speed lines')
def _(g):
    d = g.d
    disc(d, (330, 300), 150)
    for y, x0 in ((210, 40), (300, 20), (390, 60)):
        rr(d, [x0, y - 22, 160, y + 22], 22)
    arc(d, (330, 300), 90, 200, 300, 34, 0)


@icon('RAMPAGE', 'fist with impact lines')
def _(g):
    d = g.d
    rr(d, [110, 120, 400, 400], 60)
    for y in (180, 250, 320):
        rect(d, [300, y - 12, 400, y + 12], 0)
    rr(d, [60, 300, 200, 400], 40)
    for a in (-60, -30, 0):
        bar(d, pol((256, 260), 200, a), pol((256, 260), 250, a), 40)


@icon('RICOCHET', 'arrow bouncing off a line')
def _(g):
    d = g.d
    rect(d, [30, 420, 482, 470])
    path(d, [(40, 60), (256, 380)], 50)
    disc(d, (256, 380), 25)
    arrow(d, (256, 380), (470, 60), 50, 120, 160)


@icon('SNOWBALL', 'three balls growing')
def _(g):
    d = g.d
    disc(d, (70, 400), 44); disc(d, (180, 360), 80); disc(d, (350, 280), 150)
    disc(d, (300, 230), 30, 0)


@icon('WARPATH', 'crossed swords')
def _(g):
    def sword(d):
        poly(d, [(236, 30), (276, 30), (290, 70), (290, 340), (222, 340), (222, 70)])
        poly(d, [(256, 0), (290, 70), (222, 70)])
        rr(d, [150, 330, 362, 376], 16); rect(d, [232, 376, 280, 470]); disc(d, (256, 480), 30)
    g.sub(sword, rot=40)
    g.sub(sword, gap=22, rot=-40)


@icon('DOMINO', 'domino tiles toppling')
def _(g):
    d = g.d
    g.sub(lambda d: (rr(d, [60, 120, 200, 440], 20), disc(d, (130, 200), 24, 0), disc(d, (130, 360), 24, 0), rect(d, [80, 270, 180, 290], 0)), rot=0)
    g.sub(lambda d: (rr(d, [230, 120, 370, 440], 20), disc(d, (300, 200), 24, 0), rect(d, [250, 270, 350, 290], 0)), gap=0, rot=-25, center=(370, 440))
    rect(g.d, [30, 450, 482, 486])


@icon('FOLLOWUP', 'two chevrons, one after the other')
def _(g):
    d = g.d
    path(d, [(60, 80), (230, 256), (60, 432)], 76)
    path(d, [(260, 80), (430, 256), (260, 432)], 76)


@icon('OPPORTUNIST', 'four-leaf clover')
def _(g):
    d = g.d
    for a in (-135, -45, 45, 135):
        p = pol((256, 230), 100, a)
        heart_c = p
        g.sub(lambda d, p=p, a=a: heart(d, (256, 160), 100), rot=-(a + 90), center=(256, 230)) if False else None
        disc(d, pol((256, 230), 120, a - 18), 82); disc(d, pol((256, 230), 120, a + 18), 82)
    disc(d, (256, 230), 70)
    bar(d, (256, 300), (330, 480), 40)
    g.cut(lambda d: (bar(d, (80, 230), (432, 230), 24), bar(d, (256, 50), (256, 300), 24)))


# ---- BLOCK -----------------------------------------------------------------------------------------
@icon('GUARD', 'split shield (the plate SANITIZE shield)')
def _(g):
    shield(g.d, C, 230)


@icon('BARRICADE', 'two shields side by side')
def _(g):
    shield(g.d, (150, 256), 140, split=False)
    g.sub(lambda d: shield(d, (360, 256), 140, split=False), gap=22)
    g.cut(lambda d: (disc(d, (150, 230), 34), disc(d, (360, 230), 34)))


@icon('BASTION', 'crenellated tower')
def _(g):
    d = g.d
    rect(d, [130, 90, 382, 470])
    for x in (130, 236, 330):
        rect(d, [x, 30, x + 52, 100])
    rr(d, [226, 360, 286, 470], 30, 0)
    rect(d, [240, 170, 272, 250], 0)


@icon('BREAKWATER', 'wave breaking on a wall')
def _(g):
    d = g.d
    rect(d, [360, 60, 450, 470])
    pts = [(30, 470), (30, 330), (80, 250), (160, 190), (260, 180), (330, 230), (330, 300), (280, 270), (230, 280), (250, 330), (330, 360), (340, 470)]
    poly(d, chaikin(pts, 2))


@icon('BULKHEAD', 'hatch door with a wheel')
def _(g):
    d = g.d
    rr(d, [70, 30, 442, 482], 70)
    rr(d, [120, 80, 392, 432], 50, 0)
    ring(d, C, 110, 70)
    bar(d, (146, 256), (366, 256), 30); bar(d, (256, 146), (256, 366), 30)
    rect(d, [30, 120, 80, 200]); rect(d, [30, 312, 80, 392])


@icon('BULWARK', 'castle rampart, wide')
def _(g):
    d = g.d
    rect(d, [30, 200, 482, 440])
    for x in (30, 140, 250, 360):
        rect(d, [x, 130, x + 72, 210])
    rr(d, [200, 320, 312, 440], 50, 0)
    rect(d, [200, 380, 312, 440], 0)


@icon('IRONCURTAIN', 'heavy curtain with a valance')
def _(g):
    d = g.d
    rect(d, [30, 30, 482, 120])
    for x in (40, 150, 260, 370):
        rect(d, [x, 130, x + 90, 470])
    g.cut(lambda d: d.pieslice([120, 300, 392, 640], 180, 360, fill=255))


@icon('MIRRORPLATE', 'hand mirror with a shine')
def _(g):
    d = g.d
    d.ellipse([100, 30, 412, 360], fill=255)
    rr(d, [226, 350, 286, 480], 26)
    arc(d, (256, 195), 110, 200, 250, 30, 0)


@icon('SANCTUARY', 'temple: pediment and columns')
def _(g):
    d = g.d
    poly(d, [(256, 30), (482, 150), (30, 150)])
    rect(d, [50, 170, 462, 210])
    for x in (70, 175, 285, 390):
        rect(d, [x, 220, x + 52, 410])
    rect(d, [30, 420, 482, 470])


@icon('SANDBAG', 'stacked sandbags')
def _(g):
    d = g.d
    for x0, y in ((40, 360), (180, 360), (320, 360), (110, 250), (250, 250), (180, 140)):
        g.sub(lambda d, x0=x0, y=y: rr(d, [x0, y, x0 + 152, y + 104], 46), gap=14)


@icon('SPILLWAY', 'dam with water pouring over')
def _(g):
    d = g.d
    poly(d, [(250, 470), (290, 150), (470, 150), (470, 470)])
    pts = [(30, 160), (230, 160), (300, 110), (330, 160), (300, 220), (250, 470), (180, 470), (220, 230), (30, 230)]
    g.sub(lambda d: poly(d, chaikin(pts, 2)), gap=20)


@icon('BUFFER_', 'unused')
def _(g):
    pass


del ICONS['BUFFER_']


# ---- CHAIN ------------------------------------------------------------------------------------------
@icon('EXPLOIT', 'keyhole')
def _(g):
    d = g.d
    rr(d, [70, 30, 442, 482], 50)
    disc(d, (256, 200), 80, 0)
    poly(d, [(220, 230), (292, 230), (330, 420), (182, 420)], 0)


# ---- DELAY ------------------------------------------------------------------------------------------
@icon('TIMEBOMB', 'round bomb with a clock face')
def _(g):
    bomb(g.d, (230, 290), 180)
    g.cut(lambda d: clockface(d, (230, 290), 110, (-90, 20), w=30))


@icon('ACIDCHARGE', 'drop-shaped charge with a lit fuse')
def _(g):
    d = g.d
    drop(d, (230, 270), 210)
    disc(d, (230, 340), 50, 0)
    bar(d, (300, 110), (380, 70), 30)
    poly(d, star((420, 60), 70, 26, 6))


@icon('CLUSTER', 'three bombs in a cluster')
def _(g):
    bomb(g.d, (150, 340), 110, spark=False)
    g.sub(lambda d: bomb(d, (330, 350), 100, spark=False), gap=16)
    g.sub(lambda d: bomb(d, (250, 170), 100, spark=True), gap=16)


@icon('DEADLINE', 'alarm clock')
def _(g):
    d = g.d
    clockface(d, (256, 280), 180, (-90, 30), w=48)
    disc(d, (256, 280), 136, 0); clockface(d, (256, 280), 180, (-90, 30), w=48)
    for s in (-1, 1):
        d.pieslice([256 + s * 150 - 70, 40, 256 + s * 150 + 70, 180], 180, 360, fill=255)
    bar(d, (130, 440), (90, 490), 40); bar(d, (382, 440), (422, 490), 40)


@icon('SHORTFUSE', 'stick of dynamite, short fuse lit')
def _(g):
    d = g.d
    g.sub(lambda d: (rr(d, [150, 120, 362, 470], 20), rect(d, [150, 190, 362, 214], 0), rect(d, [150, 380, 362, 404], 0)), rot=-15)
    bar(g.d, (300, 130), (330, 70), 30)
    poly(g.d, star((350, 50), 70, 26, 7))


@icon('SLOWBURN', 'candle')
def _(g):
    d = g.d
    rr(d, [170, 220, 342, 470], 14)
    rect(d, [130, 450, 382, 490])
    flame(d, (256, 120), 100)
    poly(d, [(170, 220), (220, 220), (220, 300), (196, 330), (170, 300)], 255)
    rect(d, [246, 210, 266, 230])


@icon('TIMELOCK', 'hourglass')
def _(g):
    d = g.d
    rect(d, [90, 30, 422, 80]); rect(d, [90, 432, 422, 482])
    poly(d, [(120, 80), (392, 80), (290, 256), (392, 432), (120, 432), (222, 256)])
    poly(d, [(170, 120), (342, 120), (256, 220)], 0)
    poly(d, [(256, 330), (330, 400), (182, 400)], 0) if False else poly(d, [(256, 300), (350, 410), (162, 410)], 0)
    poly(d, [(256, 330), (320, 400), (192, 400)])


@icon('TRIPWIRE', 'taut wire between stakes, a burst under')
def _(g):
    d = g.d
    for x in (60, 452):
        poly(d, [(x - 30, 120), (x + 30, 120), (x + 30, 360), (x, 420), (x - 30, 360)])
    rect(d, [60, 170, 452, 206])
    poly(d, star((256, 340), 140, 60, 8))


@icon('DEADCODE_', 'unused')
def _(g):
    pass


del ICONS['DEADCODE_']


# ---- DISABLE ----------------------------------------------------------------------------------------
@icon('CORDON', 'two stanchions with a rope')
def _(g):
    d = g.d
    for x in (100, 412):
        rect(d, [x - 26, 130, x + 26, 430]); disc(d, (x, 120), 44)
        rr(d, [x - 80, 420, x + 80, 470], 16)
    arc(d, (256, 70), 200, 30, 150, 40)


@icon('DEADLOCK', 'padlock with a cross')
def _(g):
    padlock(g.d, (256, 250), 230, hole=False)
    g.cut(lambda d: (bar(d, (190, 240), (322, 400), 40), bar(d, (322, 240), (190, 400), 40)))


@icon('FLATLINE', 'heart trace going flat')
def _(g):
    d = g.d
    path(d, [(30, 280), (140, 280), (190, 120), (250, 420), (300, 280), (482, 280)], 46)


@icon('LOCKDOWN', 'cell bars')
def _(g):
    d = g.d
    rect(d, [30, 40, 482, 92]); rect(d, [30, 420, 482, 472])
    for x in (60, 160, 260, 360):
        rect(d, [x, 92, x + 50, 420])
    rect(d, [30, 230, 482, 270])


@icon('SIGNALLOSS', 'signal fan with a slash')
def _(g):
    d = g.d
    disc(d, (256, 410), 46)
    for r in (140, 240):
        arc(d, (256, 410), r, 225, 315, 52)
    g.cut(lambda d: bar(d, (60, 60), (452, 452), 90))
    g.sub(lambda d: bar(d, (70, 70), (442, 442), 44))


@icon('SOFTSPOT', 'feather')
def _(g):
    def feather(d):
        poly(d, chaikin([(256, 20), (360, 150), (340, 330), (256, 420), (172, 330), (152, 150)], 2))
        rect(d, [244, 120, 268, 490])
    g.sub(feather, rot=-35)
    g.cut(lambda d: [bar(d, (256 + 30, 200 + i * 60), (380, 160 + i * 60), 20) for i in range(3)])


@icon('SPOOF', 'domino eye mask')
def _(g):
    d = g.d
    poly(d, chaikin([(30, 200), (130, 150), (256, 190), (382, 150), (482, 200), (460, 320), (360, 360), (256, 300), (152, 360), (52, 320)], 2))
    d.ellipse([110, 210, 220, 290], fill=0); d.ellipse([292, 210, 402, 290], fill=0)


@icon('SHORTFUSE_', 'unused')
def _(g):
    pass


del ICONS['SHORTFUSE_']


# ---- DRAW -------------------------------------------------------------------------------------------
# (ARCHIVE, BROADCAST, DATASPIKE, MINDMELD, PROBE, RECURSION, RECYCLE, SKIM, SYSCALL above)


# ---- ENERGY -----------------------------------------------------------------------------------------
@icon('DISCHARGE', 'bolt striking into a burst')
def _(g):
    d = g.d
    poly(d, star((256, 410), 120, 54, 9))
    g.sub(lambda d: bolt(d, (256, 190), 170), gap=22)


@icon('DYNAMO', 'gear with a bolt in it')
def _(g):
    gear(g.d, C, 236, 10, hole=0)
    g.cut(lambda d: disc(d, C, 140))
    g.sub(lambda d: bolt(d, C, 110))


@icon('FLYWHEEL', 'spoked wheel with motion arcs')
def _(g):
    d = g.d
    ring(d, (276, 256), 200, 150)
    disc(d, (276, 256), 50)
    for a in (0, 60, 120):
        bar(d, pol((276, 256), 170, a), pol((276, 256), 170, a + 180), 34)
    for a0 in (150, 180):
        pass
    arc(d, (276, 256), 236, 140, 210, 30)


@icon('GRIDTIE', 'power pylon')
def _(g):
    d = g.d
    bar(d, (256, 30), (140, 480), 40); bar(d, (256, 30), (372, 480), 40)
    rect(d, [60, 120, 452, 160]); rect(d, [110, 230, 402, 266])
    bar(d, (200, 266), (330, 440), 30); bar(d, (312, 266), (182, 440), 30)
    for x in (70, 442):
        rect(d, [x - 14, 160, x + 14, 210])


@icon('REACTOR', 'cooling tower with steam')
def _(g):
    d = g.d
    poly(d, [(150, 180), (362, 180), (330, 300), (390, 470), (122, 470), (182, 300)])
    cloud(d, (256, 100), 120)
    rect(d, [180, 380, 332, 400], 0)


# ---- FIRE -------------------------------------------------------------------------------------------
@icon('BURST', 'two rounds side by side')
def _(g):
    bullet(g.d, (170, 256), 220)
    g.sub(lambda d: bullet(d, (342, 256), 220), gap=20)


@icon('COVERFIRE', 'umbrella over rounds')
def _(g):
    d = g.d
    d.pieslice([30, 40, 482, 400], 180, 360, fill=255)
    for x in (110, 256, 402):
        disc(d, (x, 220), 46, 0)
    rect(d, [236, 200, 276, 420])
    arc(d, (206, 420), 50, 0, 180, 40)


@icon('CROSSFIRE', 'two rounds crossing')
def _(g):
    g.sub(lambda d: bullet(d, C, 230, -90), rot=45)
    g.sub(lambda d: bullet(d, C, 230, -90), gap=22, rot=-45)


@icon('FOCUSEDFIRE', 'round into a bullseye')
def _(g):
    d = g.d
    ring(d, (330, 256), 170, 126)
    disc(d, (330, 256), 76)
    g.sub(lambda d: bullet(d, (150, 256), 130, 0), gap=22)


@icon('GUNLINE', 'three turrets in a row')
def _(g):
    for x in (100, 256, 412):
        g.sub(lambda d, x=x: turret(d, (x, 330), 80, -70), gap=10)
    rect(g.d, [20, 420, 492, 460])


@icon('HARDPOINT', 'turret on a reinforced pad with a plus')
def _(g):
    d = g.d
    turret(d, (200, 250), 160, -40)
    rect(d, [30, 410, 370, 470])
    rect(d, [380, 280, 430, 470]); rect(d, [330, 350, 482, 400])


@icon('KILLZONE', 'skull in a dashed zone')
def _(g):
    d = g.d
    for a in range(0, 360, 45):
        arc(d, C, 216, a + 6, a + 34, 40)
    skull(d, (256, 236), 130)


@icon('SUPPRESSION', 'ammo belt')
def _(g):
    d = g.d
    path(d, [(30, 420), (200, 300), (482, 300)], 40)
    for x in (100, 180, 260, 340, 420):
        y = 300 if x >= 200 else 420 - (x - 30) * 120 / 170
        bullet(d, (x, y - 110), 110, -90)


# ---- MARK -------------------------------------------------------------------------------------------
@icon('TAG', 'tag label with a hole')
def _(g):
    g.sub(lambda d: (poly(d, [(60, 160), (330, 160), (470, 256), (330, 352), (60, 352)]), disc(d, (360, 256), 34, 0)), rot=30)


@icon('COLLECTOR', 'key ring with three tags')
def _(g):
    d = g.d
    ring(d, (256, 110), 90, 54)
    for a, c2 in ((-30, (130, 360)), (0, (256, 390)), (30, (382, 360))):
        g.sub(lambda d, c2=c2: (rr(d, [c2[0] - 56, c2[1] - 90, c2[0] + 56, c2[1] + 90], 20), disc(d, (c2[0], c2[1] - 50), 20, 0)), gap=16, rot=a, center=(256, 180))


@icon('DEATHWARRANT', 'scroll with a seal')
def _(g):
    d = g.d
    rr(d, [90, 40, 422, 120], 40)
    rect(d, [120, 80, 392, 430])
    rr(d, [90, 400, 422, 480], 40)
    for y in (150, 210, 270):
        rect(d, [160, y, 352, y + 26], 0)
    g.sub(lambda d: poly(d, star((330, 350), 80, 60, 10)), gap=16)


@icon('DETONATE', 'plunger detonator')
def _(g):
    d = g.d
    rr(d, [90, 260, 422, 470], 20)
    rect(d, [232, 120, 280, 260])
    rr(d, [110, 80, 402, 140], 30)
    rect(d, [130, 310, 382, 340], 0)
    bar(d, (422, 400), (490, 300), 30)


@icon('DOSSIER', 'folder with a tab')
def _(g):
    d = g.d
    poly(d, [(30, 90), (200, 90), (240, 140), (482, 140), (482, 450), (30, 450)])
    rect(d, [30, 180, 482, 210], 0)
    rr(d, [300, 250, 440, 400], 16, 0)
    rr(d, [326, 276, 414, 374], 10)


@icon('EXECUTE', 'axe')
def _(g):
    g.sub(lambda d: (rect(d, [236, 40, 280, 490]), poly(d, chaikin([(280, 60), (420, 30), (470, 170), (420, 300), (280, 250)], 1)),
                     disc(d, (258, 60), 30)), rot=-25)


@icon('HUNTER', 'quadcopter hunter drone')
def _(g):
    d = g.d
    for sx in (-1, 1):
        for sy in (-1, 1):
            c2 = (256 + sx * 140, 256 + sy * 140)
            bar(d, C, c2, 44)
            ring(d, c2, 90, 48)
    disc(d, C, 84)
    disc(d, C, 30, 0)


@icon('KILLLIST', 'list with crosses')
def _(g):
    d = g.d
    rr(d, [60, 30, 452, 482], 30)
    for i, y in enumerate((110, 230, 350)):
        bar(d, (100, y - 30), (160, y + 30), 26, 0); bar(d, (160, y - 30), (100, y + 30), 26, 0)
        rect(d, [200, y - 18, 410, y + 18], 0)


@icon('PROFILE', 'ID card: portrait and lines')
def _(g):
    d = g.d
    rr(d, [20, 90, 492, 420], 30)
    disc(d, (150, 210), 60, 0)
    d.pieslice([70, 270, 230, 430], 180, 360, fill=0)
    rect(d, [60, 350, 240, 380], 255)
    for y in (180, 250, 320):
        rect(d, [270, y, 450, y + 30], 0)


@icon('SPOTLIGHT_', 'unused')
def _(g):
    pass


del ICONS['SPOTLIGHT_']


# ---- POS --------------------------------------------------------------------------------------------
@icon('ANCHOR', 'anchor')
def _(g):
    d = g.d
    ring(d, (256, 80), 56, 26)
    rect(d, [232, 130, 280, 440])
    rect(d, [150, 170, 362, 210])
    arc(d, (256, 270), 190, 20, 160, 46)
    head(d, (40, 300), -110, 90, 110); head(d, (472, 300), -70, 90, 110)


@icon('CALIBRATE', 'dial knob with ticks')
def _(g):
    d = g.d
    disc(d, (256, 290), 150)
    rect(d, [240, 160, 272, 250], 0)
    for a in range(200, 341, 35):
        bar(d, pol((256, 290), 180, a), pol((256, 290), 230, a), 34)


@icon('CROSSHAIR', 'crosshair (the plate STATIC SHOCK reticle)')
def _(g):
    d = g.d
    ring(d, C, 178, 132)
    for a in (0, 90, 180, 270):
        bar(d, pol(C, 100, a), pol(C, 240, a), 48)
    disc(d, C, 40)


@icon('ORBITAL', 'satellite with a beam down')
def _(g):
    d = g.d
    g.sub(lambda d: (rr(d, [200, 60, 312, 200], 20), rect(d, [40, 100, 190, 160]), rect(d, [322, 100, 472, 160]),
                     rect(d, [100, 100, 116, 160], 0), rect(d, [396, 100, 412, 160], 0)), rot=-10)
    poly(d, [(236, 220), (276, 220), (330, 480), (182, 480)])
    g.cut(lambda d: (rect(d, [150, 300, 362, 320]), rect(d, [150, 380, 362, 400])))


@icon('PINCER', 'pincer claw closing')
def _(g):
    d = g.d
    poly(d, chaikin([(40, 470), (60, 260), (140, 110), (270, 50), (350, 80), (230, 150), (170, 260), (150, 470)], 2))
    poly(d, chaikin([(472, 470), (452, 300), (400, 200), (330, 190), (380, 260), (370, 470)], 2))


@icon('PINPOINT', 'map pin')
def _(g):
    d = g.d
    pts = [(0, 1)] + [(0.62 * math.cos(math.radians(t)), -0.32 + 0.62 * math.sin(math.radians(t))) for t in range(150, 391, 8)]
    poly(d, chaikin(unit(pts, (256, 250), 230), 1))
    disc(d, (256, 180), 64, 0)


@icon('SHOVE', 'block shoved by a big arrow')
def _(g):
    d = g.d
    rect(d, [340, 110, 470, 400])
    arrow(d, (30, 256), (310, 256), 90, 150, 240)
    rect(d, [20, 420, 492, 460])


@icon('SIGHTLINE', 'binoculars')
def _(g):
    d = g.d
    for x in (140, 372):
        disc(d, (x, 330), 110)
        rr(d, [x - 70, 90, x + 70, 330], 30)
        disc(d, (x, 330), 50, 0)
    rect(d, [200, 160, 312, 250])


@icon('TRIANGULATE', 'triangle with dots at the corners')
def _(g):
    d = g.d
    v = [pol((256, 280), 210, a) for a in (-90, 30, 150)]
    path(d, v + [v[0]], 36)
    for p in v:
        disc(d, p, 62)
    disc(d, (256, 280), 40)


# ---- POWER ------------------------------------------------------------------------------------------
@icon('AEGIS', 'round shield with a star boss')
def _(g):
    d = g.d
    ring(d, C, 236, 196)
    disc(d, C, 160)
    poly(d, star(C, 110, 46, 5), 0)


@icon('CATALYST', 'flask bubbling')
def _(g):
    d = g.d
    poly(d, [(200, 60), (312, 60), (312, 200), (452, 450), (60, 450), (200, 200)])
    rect(d, [180, 40, 332, 80])
    poly(d, [(170, 320), (342, 320), (330, 300), (182, 300)], 0)
    disc(d, (220, 390), 26, 0); disc(d, (300, 370), 18, 0)


@icon('CONVERGENCE', 'four arrows meeting at a point')
def _(g):
    d = g.d
    for a in (45, 135, 225, 315):
        arrow(d, pol(C, 250, a), pol(C, 70, a), 44, 90, 120)
    disc(d, C, 40)


@icon('FEEDBACK', 'infinity loop')
def _(g):
    d = g.d
    ring(d, (150, 256), 120, 74)
    ring(d, (362, 256), 120, 74)
    g.cut(lambda d: rect(d, [230, 180, 282, 332]))
    g.sub(lambda d: (bar(d, (190, 170), (322, 342), 46), bar(d, (190, 342), (322, 170), 46)))


@icon('FOOTHOLD', 'footprint')
def _(g):
    d = g.d
    d.ellipse([140, 170, 330, 470], fill=255)
    for p, r in (((140, 130), 40), ((210, 90), 38), ((280, 80), 36), ((340, 100), 32), ((380, 150), 28)):
        disc(d, p, r)
    rect(d, [140, 340, 330, 364], 0)


@icon('FUSION', 'atom: nucleus and three orbits')
def _(g):
    def orbit(d):
        d.ellipse([20, 180, 492, 332], fill=255)
        d.ellipse([70, 216, 442, 296], fill=0)
    for a in (0, 60, 120):
        g.sub(orbit, rot=a)
    g.sub(lambda d: disc(d, C, 66), gap=22)


@icon('METRONOME', 'metronome')
def _(g):
    d = g.d
    poly(d, [(200, 40), (312, 40), (430, 470), (82, 470)])
    poly(d, [(220, 110), (292, 110), (360, 400), (152, 400)], 0)
    g.sub(lambda d: (rect(d, [236, 100, 276, 420]), rr(d, [216, 170, 296, 230], 10)), gap=0, rot=-22, center=(256, 420))


@icon('OVERFLOW', 'glass overflowing')
def _(g):
    d = g.d
    poly(d, [(110, 140), (402, 140), (360, 470), (152, 470)])
    poly(d, [(150, 180), (362, 180), (330, 430), (182, 430)], 0)
    rect(d, [180, 260, 334, 430])
    cloud(d, (256, 110), 120)
    drop(d, (440, 330), 60)


@icon('OVERWATCH', 'watchtower')
def _(g):
    d = g.d
    poly(d, [(256, 20), (420, 110), (92, 110)])
    rect(d, [120, 110, 392, 220])
    rect(d, [170, 130, 342, 190], 0)
    bar(d, (170, 220), (110, 480), 40); bar(d, (342, 220), (402, 480), 40)
    bar(d, (140, 330), (372, 330), 34)
    bar(d, (170, 230), (380, 470), 26); bar(d, (342, 230), (132, 470), 26)


@icon('SLIPSTREAM', 'paper plane')
def _(g):
    d = g.d
    poly(d, [(30, 250), (482, 60), (300, 460), (230, 320)])
    poly(d, [(230, 320), (482, 60), (220, 440)], 0)
    poly(d, [(250, 340), (440, 110), (230, 430)])


@icon('TEMPOENGINE', 'piston in a cylinder')
def _(g):
    d = g.d
    rect(d, [120, 30, 392, 80])
    rect(d, [120, 80, 160, 330]); rect(d, [352, 80, 392, 330])
    rr(d, [180, 150, 332, 250], 14)
    rect(d, [180, 180, 332, 194], 0)
    bar(d, (256, 230), (330, 420), 50)
    ring(d, (330, 430), 60, 24)


# ---- SPLASH -----------------------------------------------------------------------------------------
@icon('BARRAGE', 'three shells falling')
def _(g):
    for x, y in ((120, 180), (256, 300), (392, 180)):
        g.sub(lambda d, x=x, y=y: bullet(d, (x, y), 130, 90), gap=14)
    g.d.rectangle([30, 450, 482, 482], fill=255)


@icon('FALLOUT', 'radiation trefoil')
def _(g):
    d = g.d
    for a in (-90, 30, 150):
        d.pieslice([30, 30, 482, 482], a - 30, a + 30, fill=255)
    disc(d, C, 96, 0)
    disc(d, C, 56)


@icon('FIRESTORM', 'three flames')
def _(g):
    flame(g.d, (256, 210), 190)
    g.sub(lambda d: flame(d, (110, 340), 130), gap=20)
    g.sub(lambda d: flame(d, (402, 340), 130), gap=20)


@icon('SCATTER', 'shot spreading from a point')
def _(g):
    d = g.d
    disc(d, (60, 256), 50)
    for a, r in ((-40, 300), (-14, 360), (14, 360), (40, 300), (0, 230)):
        p = pol((60, 256), r, a)
        disc(d, p, 46)
        bar(d, pol((60, 256), 90, a), pol((60, 256), r - 80, a), 26)


@icon('SHOCKWAVE', 'ripple rings from a point')
def _(g):
    d = g.d
    disc(d, (256, 400), 60)
    for r in (140, 230):
        arc(d, (256, 400), r, 200, 340, 48)
    rect(d, [30, 450, 482, 482])


@icon('SHRAPNEL', 'frag grenade with fragments')
def _(g):
    d = g.d
    d.ellipse([110, 150, 350, 440], fill=255)
    rect(d, [180, 110, 280, 160])
    for y in (230, 300, 370):
        rect(d, [110, y, 350, y + 20], 0)
    rect(d, [220, 160, 240, 440], 0)
    for p in ((420, 120), (440, 260), (400, 400), (330, 60)):
        g.sub(lambda d, p=p: poly(d, [(p[0], p[1] - 40), (p[0] + 34, p[1] + 26), (p[0] - 34, p[1] + 26)]), gap=0, rot=20, center=p)


# ---- VIRUS ------------------------------------------------------------------------------------------
@icon('CONTAGION', 'virus passing to a small one')
def _(g):
    virus(g.d, (200, 300), 190)
    g.sub(lambda d: virus(d, (400, 110), 100, holes=False), gap=20)


@icon('NECROSIS', 'virus struck out (dead)')
def _(g):
    virus(g.d, C, 236, holes=False)
    g.cut(lambda d: (bar(d, (190, 190), (322, 322), 40), bar(d, (322, 190), (190, 322), 40)))


@icon('OUTBREAK', 'virus with arrows bursting out')
def _(g):
    d = g.d
    virus(d, C, 130, spikes=6, holes=False)
    for a in (45, 135, 225, 315):
        arrow(d, pol(C, 160, a), pol(C, 250, a), 40, 70, 100)


@icon('PANDEMIC', 'globe with a virus')
def _(g):
    d = g.d
    ring(d, (220, 290), 200, 160)
    rect(d, [20, 270, 420, 310]); rect(d, [200, 90, 240, 490])
    d.arc([110, 90, 330, 490], 0, 360, fill=255, width=36)
    g.sub(lambda d: virus(d, (390, 120), 110, holes=False), gap=22)


@icon('SPORE', 'dandelion puff')
def _(g):
    d = g.d
    disc(d, (256, 230), 50)
    for k in range(10):
        a = -90 + 36 * k
        bar(d, pol((256, 230), 50, a), pol((256, 230), 170, a), 22)
        disc(d, pol((256, 230), 190, a), 34)
    rect(d, [244, 270, 268, 490])


@icon('TOXIN', 'poison bottle')
def _(g):
    d = g.d
    rect(d, [210, 30, 302, 110])
    poly(d, [(220, 110), (292, 110), (292, 160), (410, 240), (410, 470), (102, 470), (102, 240), (220, 160)])
    g.cut(lambda d: skull(d, (256, 300), 100))
    g.sub(lambda d: (disc(d, (220, 300), 22), disc(d, (292, 300), 22)))


# ---- junk -------------------------------------------------------------------------------------------
@icon('BURN', 'flame (junk)')
def _(g):
    flame(g.d, (256, 260), 230)


@icon('DEADCODE', 'tombstone (junk)')
def _(g):
    d = g.d
    d.pieslice([90, 40, 422, 372], 180, 360, fill=255)
    rect(d, [90, 206, 422, 440])
    rect(d, [40, 430, 472, 480])
    rect(d, [234, 110, 278, 320], 0); rect(d, [170, 160, 342, 200], 0)


@icon('GLITCH', 'square sliced and offset (junk)')
def _(g):
    d = g.d
    for i, (y0, y1, dx) in enumerate(((60, 150, -50), (170, 250, 60), (270, 330, -20), (350, 450, 40))):
        rect(d, [110 + dx, y0, 400 + dx, y1])
    rect(d, [200, 190, 260, 230], 0)


@icon('HANDSHAKE', 'two hooks clasped (junk)')
def _(g):
    d = g.d
    arc(d, (190, 256), 110, 270, 450, 54)
    rect(d, [30, 120, 190, 174])
    g.sub(lambda d: (arc(d, (322, 256), 110, 90, 270, 54), rect(d, [322, 338, 482, 392])), gap=18)


@icon('LEAK', 'pipe dripping (junk)')
def _(g):
    d = g.d
    rect(d, [30, 70, 330, 170])
    rr(d, [250, 50, 360, 190], 20)
    rect(d, [270, 190, 340, 250])
    drop(d, (305, 390), 100)


@icon('TOLL', 'coin with a slot (junk)')
def _(g):
    d = g.d
    disc(d, C, 220)
    ring(d, C, 170, 140, 0)
    rect(d, [230, 140, 282, 372], 0)


# ---- uniques ----------------------------------------------------------------------------------------
@icon('U_BLOCK', 'KINETIC WALL: honeycomb wall')
def _(g):
    d = g.d
    for cx, cy in ((136, 150), (256, 150), (376, 150), (196, 254), (316, 254), (136, 358), (256, 358), (376, 358), (76, 254), (436, 254)):
        poly(d, [pol((cx, cy), 66, a) for a in range(30, 390, 60)])


@icon('U_CHAIN', 'UNBROKEN LINE: chain links')
def _(g):
    g.put(chain_link(None, (140, 340), 120, 64, -40, 44))
    g.put(chain_link(None, (256, 256), 120, 64, -40, 44), gap=0)
    g.put(chain_link(None, (372, 172), 120, 64, -40, 44))


@icon('U_DEAD', 'DEAD HAND: open hand')
def _(g):
    d = g.d
    rr(d, [140, 230, 380, 470], 70)
    for x, top in ((150, 120), (210, 60), (270, 50), (330, 90)):
        rr(d, [x, top, x + 48, 300], 24)
    g.sub(lambda d: rr(d, [60, 200, 108, 380], 24), rot=35, center=(140, 330))
    g.cut(lambda d: (bar(d, (205, 300), (205, 240), 14), bar(d, (265, 300), (265, 240), 14), bar(d, (325, 300), (325, 240), 14)))


@icon('U_DISABLE', 'DEAD AIR: microphone, muted')
def _(g):
    d = g.d
    rr(d, [186, 30, 326, 300], 70)
    arc(d, (256, 230), 120, 0, 180, 36)
    rect(d, [238, 370, 274, 450]); rect(d, [170, 440, 342, 474])
    g.cut(lambda d: bar(d, (60, 440), (452, 60), 90))
    g.sub(lambda d: bar(d, (70, 430), (442, 70), 44))


@icon('U_DOUBLE', 'DOUBLE TAP: two exclamation marks')
def _(g):
    d = g.d
    for x in (170, 342):
        poly(d, [(x - 56, 40), (x + 56, 40), (x + 34, 340), (x - 34, 340)])
        disc(d, (x, 430), 50)


@icon('U_ECHO', 'ECHO CHAMBER: nested frames receding')
def _(g):
    d = g.d
    for i, r in enumerate((236, 160, 90)):
        rect(d, [256 - r, 256 - r, 256 + r, 256 + r])
        rect(d, [256 - r + 40, 256 - r + 40, 256 + r - 40, 256 + r - 40], 0)
    disc(d, C, 30)


@icon('U_ENERGY', 'FIRST STRIKE: sword point up')
def _(g):
    d = g.d
    poly(d, [(256, 20), (310, 90), (310, 330), (202, 330), (202, 90)])
    rr(d, [110, 320, 402, 372], 20); rect(d, [228, 372, 284, 460]); disc(d, (256, 470), 36)
    rect(d, [246, 100, 266, 310], 0)


@icon('U_FIRE', 'CROSSFIRE NEXUS: hub with linked nodes')
def _(g):
    d = g.d
    for a in range(-90, 270, 60):
        bar(d, C, pol(C, 196, a), 36)
        disc(d, pol(C, 196, a), 50)
    disc(d, C, 90)
    disc(d, C, 36, 0)


@icon('U_KEY', 'MASTER KEY: key')
def _(g):
    key(g.d, (130, 130), (450, 450), 56)


@icon('U_MARK', 'SPREADING BRAND: branding iron')
def _(g):
    d = g.d
    bar(d, (60, 460), (280, 240), 40)
    rr(d, [30, 410, 130, 490], 20)
    poly(d, star((360, 160), 150, 66, 5, -60))
    disc(d, (360, 160), 40, 0)


@icon('U_PLAGUE', 'PLAGUE HEART: heart with virus spikes')
def _(g):
    d = g.d
    heart(d, (256, 270), 170)
    for a in (-150, -90, -30, 20, 160, 90):
        p = pol((256, 230), 220, a)
        bar(d, (256, 240), p, 40); disc(d, p, 30)
    heart(d, (256, 270), 170)
    disc(d, (200, 230), 26, 0); disc(d, (300, 270), 20, 0)


@icon('U_PTR', 'TARGETING SUITE: monitor with a crosshair')
def _(g):
    d = g.d
    rr(d, [30, 50, 482, 380], 30)
    rect(d, [70, 90, 442, 340], 0)
    ring(d, (256, 215), 90, 56)
    rect(d, [244, 110, 268, 320]); rect(d, [150, 203, 362, 227])
    rect(d, [226, 380, 286, 440]); rect(d, [140, 430, 372, 470])


@icon('U_SPLASH', 'WILDFIRE: burning pine')
def _(g):
    d = g.d
    poly(d, [(256, 160), (420, 440), (92, 440)])
    rect(d, [226, 430, 286, 490])
    g.sub(lambda d: flame(d, (256, 140), 120), gap=20)


@icon('U_TWICE', 'TWIN SOUL: yin-yang')
def _(g):
    d = g.d
    ring(d, C, 236, 198)
    d.pieslice([58, 58, 454, 454], 90, 270, fill=255)
    disc(d, (256, 157), 99, 0)
    disc(d, (256, 355), 99)
    disc(d, (256, 157), 32); disc(d, (256, 355), 32, 0)


# ================================================================ pass 2: redraws after the first sheet (override above)
@icon('BARRICADE', 'two shields overlapping')
def _(g):
    shield(g.d, (176, 276), 168, split=False)
    g.sub(lambda d: shield(d, (340, 240), 168, split=False), gap=22)


@icon('BREAKWATER', 'wave curling against a wall, spray over')
def _(g):
    d = g.d
    rect(d, [30, 360, 330, 470])
    arc(d, (200, 300), 120, 180, 360, 80)
    poly(d, [(80, 300), (160, 300), (160, 380), (80, 380)])
    disc(d, (290, 330), 44)
    g.sub(lambda d: (rect(d, [372, 150, 470, 470]), drop(d, (420, 70), 60)), gap=22)


@icon('COUNTERMEASURE', 'arrow turning back off a shield')
def _(g):
    d = g.d
    bar(d, (40, 386), (190, 386), 50)
    arc(d, (190, 256), 130, 270, 450, 50)
    bar(d, (190, 126), (150, 126), 50)
    head(d, (40, 126), 180, 120, 160)
    g.sub(lambda d: shield(d, (432, 256), 76, split=False), gap=20)


@icon('DISARM', 'pistol cut by a slash')
def _(g):
    d = g.d
    rect(d, [40, 110, 470, 200])
    poly(d, [(70, 196), (196, 196), (166, 450), (36, 430)])
    rect(d, [196, 196, 290, 226]); rect(d, [262, 196, 290, 290]); rect(d, [186, 268, 290, 294])
    rect(d, [440, 84, 470, 112])
    g.cut(lambda d: bar(d, (40, 480), (480, 30), 96))
    g.sub(lambda d: bar(d, (60, 460), (460, 50), 46))


@icon('FACTORYRESET', 'factory: saw-tooth roof, two chimneys')
def _(g):
    d = g.d
    poly(d, [(30, 470), (30, 250), (150, 330), (150, 250), (270, 330), (270, 250), (380, 330), (380, 60), (450, 60), (450, 470)])
    rect(d, [300, 140, 350, 300])
    for x in (70, 190, 300):
        rect(d, [x, 380, x + 46, 424], 0)


@icon('FLATLINE', 'heart trace going flat')
def _(g):
    path(g.d, [(20, 300), (150, 300), (205, 80), (275, 450), (330, 300), (492, 300)], 58)


@icon('FEINT', 'dashed arrow faking left, going right')
def _(g):
    d = g.d
    for a0 in (190, 230, 270):
        arc(d, (256, 340), 200, a0, a0 + 26, 54)
    carrow(d, (256, 340), 200, 308, 350, 54, 130, 170)
    disc(d, (256, 340), 60)


@icon('FALSEFLAG', 'waving flag on a pole')
def _(g):
    d = g.d
    rect(d, [70, 40, 124, 480])
    poly(d, chaikin([(124, 60), (250, 30), (330, 90), (460, 60), (460, 290), (330, 320), (250, 260), (124, 290)], 2))


@icon('GUNLINE', 'three turrets in a row')
def _(g):
    for x in (96, 256, 416):
        g.sub(lambda d, x=x: turret(d, (x, 290), 100, -75), gap=12)
    rect(g.d, [10, 400, 502, 450])


@icon('HANDSHAKE', 'two speech bubbles (junk)')
def _(g):
    d = g.d
    rr(d, [30, 50, 330, 280], 70); poly(d, [(90, 260), (170, 260), (70, 370)])
    g.sub(lambda d: (rr(d, [180, 200, 482, 420], 70), poly(d, [(340, 400), (420, 400), (450, 490)])), gap=24)


@icon('HIJACK', 'grappling hook')
def _(g):
    d = g.d
    rect(d, [226, 70, 286, 330])
    ring(d, (256, 70), 56, 24)
    arc(d, (146, 300), 110, 0, 160, 56)
    arc(d, (366, 300), 110, 20, 180, 56)
    poly(d, [(20, 360), (70, 330), (40, 230)])
    poly(d, [(492, 360), (442, 330), (472, 230)])
    disc(d, (256, 400), 40)


@icon('HARDPOINT', 'turret on a pad with a plus')
def _(g):
    d = g.d
    turret(d, (200, 230), 190, -35)
    rect(d, [20, 430, 400, 480])
    g.sub(lambda d: (rect(d, [400, 50, 450, 230]), rect(d, [335, 115, 500, 165])), gap=18)


@icon('MINDMELD', 'brain')
def _(g):
    d = g.d
    for p, r in (((170, 180), 100), ((256, 140), 100), ((342, 180), 100), ((130, 290), 96), ((382, 290), 96),
                 ((256, 300), 110), ((196, 370), 80), ((316, 370), 80)):
        disc(d, p, r)
    rect(d, [244, 40, 268, 460], 0)
    arc(d, (170, 270), 64, 200, 340, 24, 0)
    arc(d, (342, 270), 64, 200, 340, 24, 0)
    arc(d, (196, 160), 50, 20, 160, 24, 0)
    arc(d, (316, 160), 50, 20, 160, 24, 0)


@icon('MIRRORPLATE', 'mirror panel, an arrow bouncing off')
def _(g):
    d = g.d
    rr(d, [30, 40, 170, 472], 22)
    bar(d, (60, 210), (140, 130), 26, 0); bar(d, (60, 300), (140, 220), 26, 0)
    path(d, [(470, 70), (220, 256)], 52)
    disc(d, (220, 256), 26)
    arrow(d, (220, 256), (480, 440), 52, 120, 170)


@icon('NECROSIS', 'skull crowned with virus knobs')
def _(g):
    d = g.d
    for k in range(8):
        a = 22.5 + 360 * k / 8
        bar(d, pol((256, 236), 150, a), pol((256, 236), 220, a), 40)
        disc(d, pol((256, 236), 220, a), 32)
    g.sub(lambda d: skull(d, (256, 236), 150), gap=22)


@icon('ORBITAL', 'satellite with a beam down')
def _(g):
    d = g.d
    rr(d, [196, 30, 316, 150], 20)
    rect(d, [24, 60, 186, 120]); rect(d, [326, 60, 488, 120])
    rect(d, [96, 60, 116, 120], 0); rect(d, [396, 60, 416, 120], 0)
    g.sub(lambda d: (poly(d, [(220, 170), (292, 170), (400, 430), (112, 430)]), rect(d, [60, 440, 452, 480]),
                     rect(d, [100, 260, 412, 284], 0), rect(d, [100, 340, 412, 364], 0)), gap=0)


@icon('OVERLOAD', 'plug sparking')
def _(g):
    d = g.d
    rr(d, [130, 170, 320, 340], 34)
    rect(d, [320, 196, 450, 236]); rect(d, [320, 274, 450, 314])
    bar(d, (160, 300), (40, 480), 56)
    g.sub(lambda d: bolt(d, (420, 90), 84), gap=18)


@icon('PINCER', 'tongs pinching')
def _(g):
    d = g.d
    path(d, [(110, 480), (300, 170), (330, 80), (280, 40)], 52)
    g.sub(lambda d: path(d, [(402, 480), (212, 170), (182, 80), (232, 40)], 52), gap=20)
    disc(d, (256, 245), 40); disc(d, (256, 245), 16, 0)


@icon('RAMPAGE', 'charging bull head')
def _(g):
    d = g.d
    poly(d, chaikin([(160, 170), (352, 170), (330, 380), (296, 460), (216, 460), (182, 380)], 2))
    for s in (-1, 1):
        pts = [(256 + s * 66, 170), (256 + s * 150, 180), (256 + s * 210, 120), (256 + s * 220, 30), (256 + s * 170, 100), (256 + s * 90, 120), (256 + s * 60, 150)]
        poly(d, chaikin(pts, 2))
    disc(d, (212, 280), 24, 0); disc(d, (300, 280), 24, 0)
    disc(d, (232, 410), 16, 0); disc(d, (280, 410), 16, 0)


@icon('REACTOR', 'cooling tower with steam')
def _(g):
    d = g.d
    poly(d, chaikin([(120, 200), (392, 200), (350, 330), (430, 480), (82, 480), (162, 330)], 1))
    g.sub(lambda d: cloud(d, (256, 100), 150), gap=18)


@icon('ROOTKIT', 'tree with deep roots under a ground line')
def _(g):
    d = g.d
    cloud(d, (256, 90), 150)
    rect(d, [230, 150, 282, 250])
    rect(d, [30, 236, 482, 276])
    for a, b in (((256, 276), (256, 470)), ((256, 300), (110, 440)), ((256, 300), (402, 440)), ((160, 410), (50, 380)), ((352, 410), (462, 380))):
        bar(d, a, b, 42, cap=True)


@icon('SNOWBALL', 'three balls growing')
def _(g):
    d = g.d
    disc(d, (60, 420), 42)
    g.sub(lambda d: disc(d, (170, 370), 76), gap=16)
    g.sub(lambda d: disc(d, (345, 270), 150), gap=16)
    disc(g.d, (300, 220), 30, 0)


@icon('SPILLWAY', 'reservoir, dam, water pouring over')
def _(g):
    d = g.d
    poly(d, [(20, 200), (70, 170), (120, 200), (170, 170), (200, 190), (200, 470), (20, 470)])
    g.sub(lambda d: poly(d, [(220, 150), (300, 150), (400, 470), (220, 470)]), gap=22)
    g.sub(lambda d: path(d, [(250, 110), (370, 130), (440, 240), (480, 470)], 46), gap=22)


@icon('SPLICE', 'plug meeting a socket')
def _(g):
    d = g.d
    bar(d, (20, 420), (130, 300), 56)
    rr(d, [90, 190, 250, 340], 26)
    rect(d, [250, 216, 330, 246]); rect(d, [250, 284, 330, 314])
    rr(d, [350, 190, 480, 340], 26)
    rect(d, [350, 216, 400, 246], 0); rect(d, [350, 284, 400, 314], 0)
    bar(d, (430, 320), (492, 440), 56)


@icon('SPOTLIGHT', 'spotlight lamp and its beam')
def _(g):
    d = g.d
    disc(d, (140, 150), 110)
    ring(d, (140, 150), 70, 46, 0)
    rect(d, [116, 250, 164, 450]); rr(d, [50, 440, 230, 486], 16)
    g.sub(lambda d: poly(d, [(190, 110), (250, 230), (420, 480), (490, 300)]), gap=22)


@icon('TOLL', 'stack of coins (junk)')
def _(g):
    for y in (400, 310, 220):
        g.sub(lambda d, y=y: (d.ellipse([70, y - 80, 442, y + 70], fill=255)), gap=20)
    g.d.ellipse([170, 170, 342, 260], fill=0)
    g.d.ellipse([200, 190, 312, 240], fill=255)


@icon('BUFFER', 'cushion with a heart cut')
def _(g):
    d = g.d
    poly(d, chaikin([(30, 80), (256, 130), (482, 80), (430, 256), (482, 432), (256, 382), (30, 432), (82, 256)], 2))
    heart(d, (256, 270), 100, 0)


@icon('WORM', 'segmented worm')
def _(g):
    d = g.d
    pts = [(50 + 340 * t, 300 + 90 * math.sin(t * 2 * math.pi)) for t in np.linspace(0, 1, 40)]
    path(d, pts, 100)
    disc(d, (50, 300), 50)
    disc(d, (410, 300), 76)
    for t in (0.18, 0.36, 0.54, 0.72, 0.9):
        x = 50 + 340 * t; y = 300 + 90 * math.sin(t * 2 * math.pi)
        dy = 90 * 2 * math.pi * math.cos(t * 2 * math.pi) / 340
        n = math.hypot(1, dy)
        tx, ty = 1 / n, dy / n
        bar(d, (x - ty * 70, y + tx * 70), (x + ty * 70, y - tx * 70), 24, 0)
    disc(d, (430, 280), 18, 0)


@icon('U_SPLASH', 'WILDFIRE: burning pine')
def _(g):
    d = g.d
    poly(d, [(256, 160), (460, 450), (52, 450)])
    rect(d, [222, 440, 290, 500])
    g.sub(lambda d: flame(d, (256, 130), 115), gap=20)


@icon('U_ENERGY', 'FIRST STRIKE: sword point up')
def _(g):
    d = g.d
    poly(d, [(256, 10), (334, 90), (334, 320), (178, 320), (178, 90)])
    rect(d, [244, 100, 268, 300], 0)
    rr(d, [86, 316, 426, 376], 22); rect(d, [222, 376, 290, 456]); disc(d, (256, 466), 40)


# ================================================================ pass 3: legibility and 16 px twins
@icon('BREAKWATER', 'waves breaking on a wall')
def _(g):
    d = g.d
    for y in (190, 300, 410):
        pts = [(30 + t * 300, y + 34 * math.sin(t * 3 * math.pi)) for t in np.linspace(0, 1, 30)]
        path(d, pts, 46)
    g.sub(lambda d: rect(d, [380, 100, 470, 480]), gap=24)
    g.sub(lambda d: (drop(d, (300, 80), 56), drop(d, (210, 60), 40)), gap=0)


@icon('HIJACK', 'grappling hook on a rope')
def _(g):
    d = g.d
    rect(d, [226, 120, 286, 360])
    ring(d, (256, 110), 52, 22)
    path(d, [(256, 58), (300, 30), (360, 50), (420, 20)], 34)
    arc(d, (146, 330), 110, 0, 160, 56)
    arc(d, (366, 330), 110, 20, 180, 56)
    poly(d, [(20, 390), (70, 360), (40, 260)])
    poly(d, [(492, 390), (442, 360), (472, 260)])
    path(d, [(256, 350), (256, 470)], 56)
    poly(d, [(200, 470), (312, 470), (256, 400)], 0)
    poly(d, [(256, 500), (206, 440), (306, 440)])


@icon('MIRRORPLATE', 'round mirror, an arrow bouncing off')
def _(g):
    d = g.d
    disc(d, (140, 256), 120)
    bar(d, (90, 250), (160, 180), 26, 0); bar(d, (110, 320), (190, 240), 26, 0)
    g.sub(lambda d: (path(d, [(480, 70), (290, 256)], 52), disc(d, (290, 256), 26), arrow(d, (290, 256), (490, 440), 52, 120, 170)), gap=22)


@icon('PINCER', 'crab claw')
def _(g):
    d = g.d
    arc(d, (290, 220), 150, 45, 325, 96)
    poly(d, [(380, 70), (470, 110), (400, 130)])
    poly(d, [(380, 370), (470, 330), (400, 310)])
    bar(d, (190, 330), (70, 480), 96)


@icon('SPILLWAY', 'dam: water spills from the high side to the low side')
def _(g):
    d = g.d
    poly(d, [(210, 470), (240, 200), (290, 200), (320, 470)])
    for y, x0, x1 in ((240, 30, 200), (330, 30, 200), (420, 360, 490)):
        pts = [(x0 + t * (x1 - x0), y + 22 * math.sin(t * 2 * math.pi)) for t in np.linspace(0, 1, 20)]
        path(d, pts, 42)
    g.sub(lambda d: carrow(d, (265, 200), 150, 200, 330, 46, 100, 130), gap=20)


@icon('WORM', 'segmented worm')
def _(g):
    d = g.d
    pts = [(60 + 330 * t, 300 + 90 * math.sin(t * 2 * math.pi)) for t in np.linspace(0, 1, 40)]
    path(d, pts, 116)
    disc(d, (60, 300), 58)
    disc(d, (400, 300), 84)
    for t in (0.25, 0.5, 0.75):
        x = 60 + 330 * t; y = 300 + 90 * math.sin(t * 2 * math.pi)
        dy = 90 * 2 * math.pi * math.cos(t * 2 * math.pi) / 330
        n = math.hypot(1, dy)
        tx, ty = 1 / n, dy / n
        bar(d, (x - ty * 80, y + tx * 80), (x + ty * 80, y - tx * 80), 24, 0)
    disc(d, (420, 280), 20, 0)


@icon('DEEPSCAN', 'radar dish with waves')
def _(g):
    d = g.d
    d.pieslice([40, 90, 340, 390], 135, 315, fill=255)
    f = pol((190, 240), 190, -45)
    bar(d, (190, 240), f, 32); disc(d, f, 34)
    bar(d, (190, 320), (190, 470), 50); rect(d, [100, 450, 280, 490])
    for r in (80, 140):
        arc(d, f, r, -110, 20, 36)


@icon('U_BLOCK', 'KINETIC WALL: honeycomb wall')
def _(g):
    d = g.d
    for i in range(4):
        poly(d, [pol((76 + i * 120, 200), 66, a) for a in range(30, 390, 60)])
        poly(d, [pol((136 + i * 120 - (120 if i == 3 else 0) * 0, 304), 66, a) for a in range(30, 390, 60)]) if i < 3 else None
    for i in range(3):
        poly(d, [pol((136 + i * 120, 304), 66, a) for a in range(30, 390, 60)])


@icon('DEADCODE', 'tilted tombstone with a crack (junk)')
def _(g):
    d = g.d
    d.pieslice([120, 40, 392, 312], 180, 360, fill=255)
    rect(d, [120, 176, 392, 430])
    rect(d, [244, 100, 268, 260], 0); rect(d, [190, 140, 322, 164], 0)
    poly(d, [(330, 176), (300, 280), (340, 330), (310, 430), (290, 430), (318, 330), (280, 280), (312, 176)], 0)
    g.rotate(-12, (256, 430))
    rect(g.d, [30, 430, 482, 480])


@icon('KILLLIST', 'clipboard list with crosses')
def _(g):
    d = g.d
    rr(d, [90, 70, 422, 490], 30)
    for y in (180, 290, 400):
        bar(d, (130, y - 30), (190, y + 30), 26, 0); bar(d, (190, y - 30), (130, y + 30), 26, 0)
        rect(d, [225, y - 18, 390, y + 18], 0)
    g.sub(lambda d: rr(d, [180, 20, 332, 100], 20), gap=18)


@icon('DEATHWARRANT', 'scroll with a seal')
def _(g):
    def scroll(d):
        rr(d, [90, 40, 422, 120], 40)
        rect(d, [120, 80, 392, 430])
        rr(d, [90, 400, 422, 480], 40)
        for y in (150, 210, 270):
            rect(d, [160, y, 352, y + 26], 0)
    g.sub(scroll, rot=-20)
    g.sub(lambda d: poly(d, star((350, 360), 84, 62, 10)), gap=16)


@icon('OPENWIDE', 'double doors swung open, light between')
def _(g):
    d = g.d
    poly(d, [(30, 40), (170, 100), (170, 410), (30, 470)])
    poly(d, [(482, 40), (342, 100), (342, 410), (482, 470)])
    disc(d, (140, 256), 18, 0); disc(d, (372, 256), 18, 0)
    poly(d, star((256, 256), 130, 40, 4, -90))


@icon('U_ENERGY', 'FIRST STRIKE: sword point up')
def _(g):
    def sword(d):
        poly(d, [(256, 10), (334, 90), (334, 320), (178, 320), (178, 90)])
        rect(d, [244, 100, 268, 300], 0)
        rr(d, [86, 316, 426, 376], 22); rect(d, [222, 376, 290, 456]); disc(d, (256, 466), 40)
    g.sub(sword, rot=-35)


@icon('REACTOR', 'cooling tower with steam')
def _(g):
    d = g.d
    poly(d, chaikin([(110, 220), (402, 220), (340, 340), (450, 490), (62, 490), (172, 340)], 1))
    rect(d, [150, 400, 362, 420], 0)
    g.sub(lambda d: cloud(d, (256, 100), 170), gap=20)


@icon('PANDEMIC', 'globe with a virus')
def _(g):
    d = g.d
    ring(d, (210, 300), 190, 150)
    rect(d, [20, 280, 400, 320]); rect(d, [190, 110, 230, 490])
    d.arc([110, 110, 310, 490], 0, 360, fill=255, width=38)
    g.sub(lambda d: virus(d, (380, 130), 130, holes=False), gap=22)


@icon('TOLL', 'coin stack and a standing coin (junk)')
def _(g):
    for y in (420, 340, 260):
        g.sub(lambda d, y=y: d.ellipse([30, y - 70, 300, y + 60], fill=255), gap=18)
    g.sub(lambda d: (d.ellipse([290, 120, 482, 420], fill=255), rect(d, [374, 190, 398, 350], 0)), gap=22)


@icon('EXPLOIT', 'keyhole in a round plate')
def _(g):
    d = g.d
    disc(d, C, 236)
    disc(d, (256, 200), 74, 0)
    poly(d, [(222, 230), (290, 230), (326, 410), (186, 410)], 0)


@icon('FUSION', 'atom: nucleus and three orbits')
def _(g):
    def orbit(d):
        d.ellipse([16, 168, 496, 344], fill=255)
        d.ellipse([72, 222, 440, 290], fill=0)
    for a in (0, 60, 120):
        g.sub(orbit, rot=a)
    g.sub(lambda d: disc(d, C, 66), gap=22)


@icon('SYSCALL', 'terminal window with a prompt')
def _(g):
    d = g.d
    rr(d, [30, 70, 482, 442], 30)
    rect(d, [74, 150, 438, 400], 0)
    for x in (90, 140, 190):
        disc(d, (x, 110), 16, 0)
    path(d, [(120, 200), (200, 260), (120, 320)], 46)
    rect(d, [235, 310, 385, 356])


@icon('BURST', 'two rounds fanned out')
def _(g):
    g.sub(lambda d: bullet(d, (256, 270), 210), rot=16, center=(256, 470))
    g.sub(lambda d: bullet(d, (256, 270), 210), gap=22, rot=-16, center=(256, 470))


@icon('ARCHIVE', 'shelf of binders, one leaning')
def _(g):
    d = g.d
    for x0, x1, top in ((30, 120, 110), (140, 220, 60), (240, 320, 140)):
        rect(d, [x0, top, x1, 440])
        rect(d, [x0 + 20, top + 40, x1 - 20, top + 64], 0)
    g.sub(lambda d: (rect(d, [350, 90, 430, 440]), rect(d, [370, 130, 410, 154], 0)), rot=-18, center=(430, 440))
    rect(g.d, [20, 450, 492, 490])


@icon('BARRICADE', 'road barricade: striped plank on legs')
def _(g):
    d = g.d
    rect(d, [30, 130, 482, 240])
    for x in (60, 170, 280, 390):
        poly(d, [(x, 230), (x + 30, 140), (x + 70, 140), (x + 40, 230)], 0)
    poly(d, [(90, 240), (150, 240), (120, 470), (50, 470)])
    poly(d, [(362, 240), (422, 240), (462, 470), (392, 470)])
    rect(d, [96, 320, 416, 364])


@icon('BULWARK', 'castle rampart, wide')
def _(g):
    d = g.d
    rect(d, [20, 250, 492, 450])
    for x in (20, 120, 220, 320, 420):
        rect(d, [x, 180, x + 72, 260])
    rr(d, [206, 340, 306, 450], 46, 0)
    rect(d, [206, 400, 306, 450], 0)


@icon('SKIM', 'two cards fanned')
def _(g):
    g.sub(lambda d: card(d, [70, 100, 270, 410], corner=False), rot=22, center=(170, 255))
    g.sub(lambda d: card(d, [240, 100, 440, 410]), gap=22, rot=-20, center=(340, 255))


@icon('DOSSIER', 'folder with a mugshot clipped on, tilted')
def _(g):
    d = g.d
    poly(d, [(40, 120), (200, 120), (240, 170), (472, 170), (472, 440), (40, 440)])
    rect(d, [40, 205, 472, 230], 0)
    rr(d, [290, 270, 430, 410], 16, 0)
    disc(d, (360, 320), 30)
    d.pieslice([310, 350, 410, 450], 180, 360, fill=255)
    g.rotate(14)


@icon('WORM', 'segmented worm (caterpillar body, head with an eye)')
def _(g):
    for i in range(5):
        x = 60 + i * 76; y = 320 + 60 * math.sin(i * 1.3)
        g.sub(lambda d, x=x, y=y, i=i: disc(d, (x, y), 44 + i * 4), gap=12)
    g.sub(lambda d: (disc(d, (420, 250), 76), bar(d, (400, 190), (370, 90), 26, cap=True), bar(d, (450, 190), (480, 100), 26, cap=True)), gap=14)
    g.cut(lambda d: disc(d, (440, 240), 18))


# ================================================================ content, files, checks, sheet
def read_cards(root):
    out = []
    d = os.path.join(root, 'content', 'b', 'card')
    for fn in sorted(os.listdir(d)):
        if not fn.endswith('.tres'):
            continue
        txt = open(os.path.join(d, fn), encoding='utf-8', errors='replace').read()

        def f(name):
            m = re.search(r'^%s = "?(.*?)"?$' % name, txt, re.M)
            return m.group(1) if m else ''
        out.append({'proto': f('proto_id'), 'id': f('id').strip('&"'), 'name': f('display_name'), 'kind': f('kind'),
                    'rarity': f('rarity'), 'junk': f('junk') == 'true', 'unique': f('unique') == 'true',
                    'arch': f('archetype_name')})
    return out


def fname(pid):
    return 'card_' + pid.lower()


def render(pid):
    g = G()
    ICONS[pid][1](g)
    return g.m


def alpha_of(path):
    return np.asarray(Image.open(path).convert('RGBA').split()[3]).astype(np.float32) / 255.0


def soft16(a):
    g = Image.fromarray((a * 255).astype(np.uint8), 'L')
    bb = g.getbbox(); g = g.crop(bb); k = 15 / max(g.size)
    g = g.resize((max(1, int(round(g.width * k))), max(1, int(round(g.height * k)))), Image.LANCZOS)
    c = Image.new('L', (16, 16), 0); c.paste(g, ((16 - g.width) // 2, (16 - g.height) // 2))
    return np.asarray(c.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 255


def twin_check(alphas):
    s = {k: soft16(a) for k, a in alphas.items()}
    res = {}
    for k, a in s.items():
        best = (0.0, '')
        for o, b in s.items():
            if o == k:
                continue
            iou = float(np.minimum(a, b).sum() / max(np.maximum(a, b).sum(), 1e-6))
            if iou > best[0]:
                best = (iou, o)
        res[k] = best
    return res


def thin_check(m512):
    """share of the silhouette lost to an opening with a 37 px square (strokes thinner than ~40/512) and share of the
    background filled by a closing with a 21 px square (cut-outs thinner than ~24/512)"""
    a = np.asarray(m512) > 127

    def step(x, square, grow):
        p = np.pad(x, 1, constant_values=not grow)
        nb = [p[1:-1, :-2], p[1:-1, 2:], p[:-2, 1:-1], p[2:, 1:-1], x]
        if square:
            nb += [p[:-2, :-2], p[:-2, 2:], p[2:, :-2], p[2:, 2:]]
        out = nb[0]
        for q in nb[1:]:
            out = (out | q) if grow else (out & q)
        return out

    def morph(x, r, grow):
        for i in range(r):
            x = step(x, i % 2 == 0, grow)
        return x
    o = morph(morph(a, 18, False), 18, True)                 # opening: an octagon of ~37 px across
    lost = (a & ~o).sum() / max(1, a.sum())
    cl = morph(morph(a, 10, True), 10, False)                # closing: ~21 px
    filled = (cl & ~a).sum() / max(1, a.sum())
    return float(lost), float(filled)


# ---- the card-face look (BRewardCard / the plate's net_card): kind band gradient, white pictogram, dark drop
DROP = (0.04, 0.06)       # drop offset (share of the box)
DROP_ALPHA = 0.5
INK = (12, 10, 22)


def sample(a, x0, y0, box, w, h):
    ys, xs = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
    n = a.shape[0]
    if box < n * 0.5:     # minified: Godot samples the mipmaps (the drawer's texture has them)
        f = 1
        while n // (f * 2) >= box:
            f *= 2
        k = n // f
        a = a[:k * f, :k * f].reshape(k, f, k, f).mean(axis=(1, 3)); n = k
    u = (xs - x0) / box; v = (ys - y0) / box
    inside = (u >= 0) & (u < 1) & (v >= 0) & (v < 1)
    tx = np.clip(u * n - 0.5, 0, n - 1); ty = np.clip(v * n - 0.5, 0, n - 1)
    ix = np.floor(tx).astype(int); iy = np.floor(ty).astype(int)
    fx = tx - ix; fy = ty - iy
    ix1 = np.minimum(ix + 1, n - 1); iy1 = np.minimum(iy + 1, n - 1)
    c = (a[iy, ix] * (1 - fx) * (1 - fy) + a[iy, ix1] * fx * (1 - fy) + a[iy1, ix] * (1 - fx) * fy + a[iy1, ix1] * fx * fy)
    return np.where(inside, c, 0.0)


def draw_icon(cv, a, at, box, fill=(250, 248, 242)):
    h, w, _ = cv.shape
    x0, y0 = at[0] - box / 2, at[1] - box / 2
    c = sample(a, x0 + box * DROP[0], y0 + box * DROP[1], box, w, h)[..., None] * DROP_ALPHA
    cv[:] = cv * (1 - c) + np.array(INK, np.float32) / 255 * c
    c = sample(a, x0, y0, box, w, h)[..., None]
    cv[:] = cv * (1 - c) + np.array(fill, np.float32) / 255 * c


def band(kc, w, h):
    top = np.array(kc, np.float32) / 255 * 0.8; bot = np.array(kc, np.float32) / 255 * 0.22
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    return np.repeat(top * (1 - t) + bot * t, w, axis=1)


KIND_COL = {'ATTACK': (255, 61, 168), 'BLOCK': (61, 123, 255), 'CHAIN': (76, 217, 100), 'DELAY': (154, 160, 170),
            'DISABLE': (176, 124, 255), 'DRAW': (255, 226, 0), 'ENERGY': (255, 226, 0), 'FIRE': (255, 61, 168),
            'MARK': (255, 106, 61), 'POS': (176, 124, 255), 'POWER': (255, 154, 46), 'SPLASH': (255, 61, 168),
            'VIRUS': (76, 217, 100)}


def face(a, kind, size, box):
    w, h = size
    cv = band(KIND_COL.get(kind, (176, 124, 255)), w, h)
    draw_icon(cv, a, (w / 2, h / 2), box)
    return Image.fromarray((np.clip(cv, 0, 1) * 255).astype(np.uint8), 'RGB')


BG = (22, 20, 30); CELL = (34, 32, 44); TXT = (236, 236, 240); DIM = (160, 160, 176); RED = (255, 90, 90); AMB = (255, 190, 60)
FACE = (176, 81, 60)       # BRewardCard art field (720p): 176 x 81, icon box 60
HAND = (40, 40, 34)        # the fight hand sticker's icon box (34 px)
MINI = (40, 36, 28)        # BRewardCard mini tile: icon box 28


def sheet(cards, alphas, tw, thin, out, fonts):
    fa = ImageFont.truetype(os.path.join(fonts, 'Anton-Regular.ttf'), 21)
    fh = ImageFont.truetype(os.path.join(fonts, 'Anton-Regular.ttf'), 36)
    fm = ImageFont.truetype(os.path.join(fonts, 'ShareTechMono-Regular.ttf'), 14)
    cols, cw, ch = 8, 300, 240
    rows = (len(cards) + cols - 1) // cols
    Wd, Hd = cols * cw + 24, 120 + rows * ch + 20
    sh = Image.new('RGB', (Wd, Hd), BG); d = ImageDraw.Draw(sh)
    d.text((16, 10), 'Card pictograms: %d cards (content/b/card), one 256 px white pictogram each' % len(cards), font=fh, fill=TXT)
    d.text((16, 60), 'each: the reward card art field 1:1 (176 x 81, icon box 60, kind band, dark drop) | fight hand icon box 1:1 '
                     '(34 px) | reward mini tile 1:1 (28 px) | the art field at 1080p (icon box 90).', font=fm, fill=DIM)
    d.text((16, 80), 'IoU = max soft IoU at 16 px against every other card (16 px rule: < 0.68 passes, amber >= 0.6).  '
                     'thin = share of the silhouette thinner than ~40/512.', font=fm, fill=DIM)
    for i, c in enumerate(cards):
        x, y = 12 + (i % cols) * cw, 110 + (i // cols) * ch
        k = c['proto']
        d.rounded_rectangle([x, y, x + cw - 10, y + ch - 10], radius=8, fill=CELL)
        a = alphas[k]
        sh.paste(face(a, c['kind'], FACE[:2], FACE[2]), (x + 8, y + 36))
        sh.paste(face(a, c['kind'], HAND[:2], HAND[2]), (x + 192, y + 36))
        sh.paste(face(a, c['kind'], MINI[:2], MINI[2]), (x + 240, y + 38))
        sh.paste(face(a, c['kind'], (176, 112), 90), (x + 8, y + 120))
        d.text((x + 8, y + 4), c['name'] or k, font=fa, fill=TXT)
        d.text((x + 192, y + 84), c['kind'], font=fm, fill=DIM)
        d.text((x + 192, y + 102), k.lower()[:14], font=fm, fill=DIM)
        iou, who = tw[k]
        d.text((x + 192, y + 150), 'IoU %.2f' % iou, font=fm, fill=RED if iou >= 0.68 else (AMB if iou >= 0.6 else DIM))
        d.text((x + 192, y + 166), who.lower()[:13], font=fm, fill=DIM)
        d.text((x + 192, y + 190), 'thin %.2f' % thin[k][0], font=fm, fill=AMB if thin[k][0] > 0.06 else DIM)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sh.save(out)


if __name__ == '__main__':
    root, icon_dir, out = sys.argv[1:4]
    only = set(sys.argv[4:])
    fonts = os.path.join(root, 'assets', 'fonts')
    cards = read_cards(root)
    protos = [c['proto'] for c in cards]
    missing = [p for p in protos if p not in ICONS]
    extra = [p for p in ICONS if p not in protos]
    print('cards %d, icons %d, missing %s, extra %s' % (len(protos), len(ICONS), missing, extra))
    os.makedirs(icon_dir, exist_ok=True)
    alphas, thin, files = {}, {}, {}
    for c in cards:
        p = c['proto']
        if p not in ICONS:
            continue
        ipath = os.path.join(icon_dir, fname(p) + ".png")
        if not only or p in only or not os.path.exists(ipath):
            m = render(p)
            thin[p] = thin_check(m)
            im = Image.new('RGBA', (256, 256), (255, 255, 255, 0)); im.putalpha(m.resize((256, 256), Image.LANCZOS))
            im.save(ipath)
        else:
            thin[p] = thin_check(Image.open(ipath).split()[3].resize((512, 512), Image.BICUBIC))
        alphas[p] = alpha_of(ipath)
        files[p] = fname(p) + '.png'
    tw = twin_check(alphas)
    shown = [c for c in cards if c['proto'] in alphas]
    sheet(shown, alphas, tw, thin, out, fonts)
    man = {'schema': 'rebel_cell.art_export/1', 'asset': 'card_icons',
           'about': 'One pictogram per Campaign B card (content/b/card, keyed by proto_id): 256 px, white on transparent (alpha = '
                    'coverage), the full 512 grid canvas; drawn by CardIcons with a dark drop on the card kind band. Generated; '
                    'do not edit by hand.',
           'source': 'art-pass docs/concepts/card_icons/src/card_icons.py',
           'files': {files[c['proto']]: '%s (%s): %s' % (c['name'], c['kind'], ICONS[c['proto']][0]) for c in shown}}
    json.dump(man, open(os.path.join(icon_dir, 'manifest.json'), 'w', encoding='utf-8'), indent=1, sort_keys=True)
    bad = sorted([(tw[k][0], k, tw[k][1]) for k in tw], reverse=True)
    for v, k, o in bad[:25]:
        print('IoU %.2f %-14s ~ %s' % (v, k, o))
    print('thin >0.06:', sorted([(round(v[0], 2), k) for k, v in thin.items() if v[0] > 0.06], reverse=True))
