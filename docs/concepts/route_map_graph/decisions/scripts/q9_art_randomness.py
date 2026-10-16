"""Q9 decision sheet: what 'art randomness' is, shown on a small one-city block (CPU isometric massing, PIL).

The lots, streets and the three route buildings are the game's (fixed here). Everything else on the block - which
building type sits on a lot, its height, sign placement and style, lit windows, colour mix, roof clutter - comes from
named art streams: art_seed(stream, *keys) = FNV-1a 64 over the JSON of [layout_seed, "art/" + stream, *keys]
(PIPELINE_SPEC 3.5), expanded with splitmix64 (trivial to match in GDScript). Each lot draws a FIXED list of numbers
from its stream; the variance preset only maps those numbers, so one seed at LOW / MEDIUM / HIGH is the same city,
calmer or wilder.

python q9_art_randomness.py -> ../Q9_art_randomness.png (+ ../Q9_art_randomness.json)
"""
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

import sheetlib as L  # noqa: E402

OUT = os.path.dirname(HERE)
M64 = 0xFFFFFFFFFFFFFFFF


# ------------------------------------------------------------------ the art streams
def fnv1a64(data):
    h = 0xCBF29CE484222325
    for c in data:
        h ^= c
        h = (h * 0x100000001B3) & M64
    return h


def art_seed(layout_seed, stream, *keys):
    return fnv1a64(json.dumps([layout_seed, "art/" + stream, *keys], separators=(",", ":")).encode("utf-8"))


class Stream:
    """splitmix64 over an art seed: next() in [0, 1)."""

    def __init__(self, seed):
        self.s = seed & M64

    def next(self):
        self.s = (self.s + 0x9E3779B97F4A7C15) & M64
        z = self.s
        z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
        z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
        z ^= z >> 31
        return (z >> 11) / float(1 << 53)

    def draws(self, n):
        return [self.next() for _ in range(n)]


def gauss(u1, u2):
    return math.sqrt(-2.0 * math.log(max(1e-12, u1))) * math.cos(2 * math.pi * u2)


# ------------------------------------------------------------------ presets
VARIANCE = {
    "LOW": dict(height_var=0.08, type_mix=0.15, sign_density=0.45, colour_mix=0.05, window_var=0.03, clutter=0.4),
    "MEDIUM": dict(height_var=0.30, type_mix=0.60, sign_density=1.00, colour_mix=0.25, window_var=0.12, clutter=1.0),
    "HIGH": dict(height_var=0.65, type_mix=1.00, sign_density=2.20, colour_mix=0.65, window_var=0.30, clutter=2.2),
}
# MEDIUM = today's one-city rules (M44/onecity_scene.py): 30 % lit windows, shop bands on 55 % of street faces, blade
# signs on 16 %, roof trim 42 %, water tanks 18 %, roof holos 16 %, territory tint 0.28.
BASE = dict(lit=0.30, shop=0.55, blade=0.16, trim=0.42, tank=0.18, holo=0.16)
TYPES = ["slab", "tower", "stepped", "podium", "lowrise"]
DOMINANT = "slab"
BODY = [(0.15, 0.15, 0.19), (0.19, 0.17, 0.22), (0.13, 0.16, 0.20), (0.20, 0.19, 0.20), (0.16, 0.14, 0.17)]
INK_HOME = [(0.30, 0.90, 1.00), (1.00, 0.30, 0.75)]                  # the district's two neons (cyan / magenta)
INK_FOREIGN = [(0.83, 1.00, 0.00), (1.00, 0.55, 0.10), (1.00, 0.22, 0.25), (0.25, 1.00, 0.55), (0.70, 0.45, 1.00),
               (1.00, 0.85, 0.30)]
WIN = [(1.0, 0.82, 0.55), (0.75, 0.88, 1.0), (1.0, 0.95, 0.85), (0.6, 1.0, 0.95)]
TERR_TINT = (0.35, 0.20, 0.45)

# ------------------------------------------------------------------ the game's layout (fixed)
NX, NY, LOT = 7, 5, 10.0
X_STREET_AFTER, X_STREET = 3, 7.0          # a cross street after lot column 3
Y_STREET_AFTER, Y_STREET = 1, 7.0          # a back street after lot row 1
FRONT = 9.0                                # the front street (the route street) in front of row NY-1
FLOOR = 1.6
ROUTE = {(2, NY - 1): 22.0, (3, NY - 1): 27.0, (4, NY - 1): 19.0}     # route columns: the game sets type and height


def lot_box(i, j):
    x0 = i * LOT + (X_STREET if i > X_STREET_AFTER else 0)
    y0 = j * LOT + (Y_STREET if j > Y_STREET_AFTER else 0)
    return x0 + 0.6, y0 + 0.6, x0 + LOT - 0.6, y0 + LOT - 0.6


EXT_X = NX * LOT + X_STREET
EXT_Y = NY * LOT + Y_STREET + FRONT


# ------------------------------------------------------------------ generation
def gen_lot(seed, var, i, j):
    """One lot: a fixed list of draws from art/building:(i,j), mapped by the variance preset."""
    u = Stream(art_seed(seed, "building", i, j)).draws(48)
    v = VARIANCE[var]
    route_h = ROUTE.get((i, j))
    # type
    if route_h:
        typ = "slab"
    elif u[0] < 1.0 - v["type_mix"]:
        typ = DOMINANT
    else:
        typ = TYPES[int(u[1] * len(TYPES))]
    # height: a zone field (taller toward the back) times a log-normal spread
    zone = 1.0 - (i * 0.4 + j) / (NX * 0.4 + NY - 1.4)
    h0 = 13.0 + 24.0 * zone
    g = gauss(u[2], u[3])
    h = h0 * math.exp(v["height_var"] * g - v["height_var"] ** 2 / 2)
    h *= {"tower": 1.3, "lowrise": 0.32, "stepped": 1.1}.get(typ, 1.0)
    h = route_h if route_h else max(3.2, min(62.0, h))
    h = max(2, round(h / FLOOR)) * FLOOR
    # colour mix
    body = BODY[int(u[4] * len(BODY))]
    tint = 0.28 * min(1.0, v["colour_mix"] / 0.25) * u[5]
    jit = (v["colour_mix"] * 0.25) * (u[6] - 0.5)
    body = tuple(min(1, max(0, b * (1 - tint) + t * tint * 0.45 + jit * (k - 1) * 0.3)) for k, (b, t) in enumerate(zip(body, TERR_TINT)))
    foreign = u[7] < v["colour_mix"]
    ink = INK_FOREIGN[int(u[8] * len(INK_FOREIGN))] if foreign else INK_HOME[int(u[9] * 2)]
    ink2 = INK_FOREIGN[int(u[10] * len(INK_FOREIGN))] if u[11] < v["colour_mix"] else INK_HOME[1 - int(u[9] * 2)]
    # windows: per-building lit share, plus whole dark floors
    lit = BASE["lit"] + v["window_var"] * 2.0 * (u[12] - 0.5) * 2.0
    lit = max(0.03, min(0.85, lit))
    sd = v["sign_density"]
    cl = v["clutter"]
    x0, y0, x1, y1 = lot_box(i, j)
    parts = []
    if typ == "slab":
        parts.append((x0, y0, x1, y1, 0.0, h))
    elif typ == "tower":
        k = 0.18 + 0.1 * u[13]
        w = (x1 - x0) * k
        parts.append((x0 + w, y0 + w, x1 - w, y1 - w, 0.0, h))
    elif typ == "stepped":
        n = 2 + int(u[13] * 2)
        for s in range(n):
            ins = s * 1.4
            parts.append((x0 + ins, y0 + ins, x1 - ins, y1 - ins, h * s / n, h * (s + 1) / n))
    elif typ == "podium":
        ph = FLOOR * (2 + int(u[13] * 3))
        parts.append((x0, y0, x1, y1, 0.0, ph))
        w = (x1 - x0) * 0.25
        parts.append((x0 + w, y0 + w * 0.6, x1 - w * 0.6, y1 - w, ph, max(ph + 4, h)))
    else:
        parts.append((x0, y0, x1, y1, 0.0, h))
    top = parts[-1]
    tx0, ty0, tx1, ty1, _, zt = top
    dressing = dict(
        shop_y=u[14] < min(1, BASE["shop"] * sd), shop_x=u[15] < min(1, BASE["shop"] * sd),
        blade=[(u[16 + 3 * b] < min(0.9, BASE["blade"] * sd * 1.6), u[17 + 3 * b], u[18 + 3 * b]) for b in range(3)],
        sign_style=int(u[25] * 3),                      # 0 vertical blade, 1 stacked panels, 2 wide box sign
        trim=u[26] < min(1, BASE["trim"] * (0.6 + 0.4 * sd)),
        tank=u[27] < min(0.9, BASE["tank"] * cl) and zt < 40 and typ != "tower",
        ac=int(u[28] * (1 + 2.0 * cl)),
        ac_pos=u[29:35],
        holo=u[35] < min(0.9, BASE["holo"] * sd) and zt > 14,
        holo_col=INK_FOREIGN[int(u[36] * len(INK_FOREIGN))] if u[37] < v["colour_mix"] else INK_HOME[int(u[38] * 2)],
        antenna=zt > 26 and u[39] < 0.45 * min(1.5, cl),
        tank_pos=(u[40], u[41]),
    )
    return dict(i=i, j=j, typ=typ, h=h, body=body, ink=ink, ink2=ink2, lit=lit, parts=parts, d=dressing,
                route=bool(route_h), wseed=art_seed(seed, "room_wall", i, j))


def gen_city(seed, var):
    return [gen_lot(seed, var, i, j) for j in range(NY) for i in range(NX)]


# ------------------------------------------------------------------ isometric drawing
class Iso:
    def __init__(self, w, h, s, ox, oy):
        self.w, self.h, self.s, self.ox, self.oy = w, h, s, ox, oy
        self.img = Image.new("RGB", (w, h))
        self.emit = Image.new("RGB", (w, h))
        self.d = ImageDraw.Draw(self.img)
        self.e = ImageDraw.Draw(self.emit)

    def p(self, x, y, z):
        return ((x - y) * 0.866 * self.s + self.ox, (x + y) * 0.42 * self.s - z * self.s * 0.92 + self.oy)

    def poly(self, pts3, col, emit=None, outline=None):
        pts = [self.p(*q) for q in pts3]
        c = tuple(int(max(0, min(1, v)) * 255) for v in col)
        self.d.polygon(pts, fill=c, outline=outline)
        if emit is None:
            self.e.polygon(pts, fill=(0, 0, 0))
        else:
            self.e.polygon(pts, fill=tuple(int(max(0, min(1, v)) * 255) for v in emit))

    def line(self, a, b, col, w, emit=True):
        pa, pb = self.p(*a), self.p(*b)
        c = tuple(int(max(0, min(1, v)) * 255) for v in col)
        self.d.line([pa, pb], fill=c, width=w)
        self.e.line([pa, pb], fill=c if emit else (0, 0, 0), width=w)


def shade(c, k):
    return tuple(min(1, v * k) for v in c)


def draw_box(R, b, x0, y0, x1, y1, z0, z1, wins=True):
    col = b["body"]
    fogk = 0.75 + 0.25 * ((x0 + y0) / (EXT_X + EXT_Y))           # far blocks a touch lower in value
    face_y = [(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)]
    face_x = [(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)]
    R.poly(face_y, shade(col, 0.95 * fogk))
    R.poly(face_x, shade(col, 0.62 * fogk))
    R.poly([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], shade(col, 1.35 * fogk))
    if not wins:
        return
    ws = Stream(b["wseed"] ^ (int(z0 * 10) * 7919))
    nfl = int((z1 - z0 - 0.4) / FLOOR)
    for face, (a0, a1) in (("y", (x0, x1)), ("x", (y0, y1))):
        ncol = int((a1 - a0 - 0.6) / 1.5)
        for f in range(nfl):
            dark_floor = ws.next() < 0.12 + b["lit"] * -0.1
            for c in range(ncol):
                r1, r2 = ws.next(), ws.next()
                if dark_floor or r1 > b["lit"]:
                    wc = (0.07, 0.07, 0.09)
                    em = None
                else:
                    wc = shade(WIN[int(r2 * len(WIN))], (0.55 + 0.45 * r2) * (0.8 if face == "x" else 1.0))
                    em = shade(wc, 0.5)
                t0 = a0 + 0.5 + c * 1.5
                z = z0 + 0.5 + f * FLOOR
                if face == "y":
                    q = [(t0, y1 + 0.01, z), (t0 + 0.8, y1 + 0.01, z), (t0 + 0.8, y1 + 0.01, z + 0.85), (t0, y1 + 0.01, z + 0.85)]
                else:
                    q = [(x1 + 0.01, t0, z), (x1 + 0.01, t0 + 0.8, z), (x1 + 0.01, t0 + 0.8, z + 0.85), (x1 + 0.01, t0, z + 0.85)]
                R.poly(q, wc, emit=em)


def draw_lot(R, b):
    D = b["d"]
    for (x0, y0, x1, y1, z0, z1) in b["parts"]:
        draw_box(R, b, x0, y0, x1, y1, z0, z1)
    x0, y0, x1, y1, z0, z1 = b["parts"][0]
    # street level: shop bands
    if D["shop_y"] and z0 == 0:
        R.poly([(x0 + 0.4, y1 + 0.05, 0.25), (x1 - 0.4, y1 + 0.05, 0.25), (x1 - 0.4, y1 + 0.05, 1.3), (x0 + 0.4, y1 + 0.05, 1.3)],
               shade(b["ink2"], 0.9), emit=shade(b["ink2"], 0.8))
    if D["shop_x"] and z0 == 0:
        R.poly([(x1 + 0.05, y0 + 0.4, 0.25), (x1 + 0.05, y1 - 0.4, 0.25), (x1 + 0.05, y1 - 0.4, 1.3), (x1 + 0.05, y0 + 0.4, 1.3)],
               shade(b["ink"], 0.7), emit=shade(b["ink"], 0.6))
    # signs on the street (+y) face of the lowest part, style per building
    hmax = z1 if len(b["parts"]) == 1 else b["parts"][0][5]
    if b["route"]:                                      # the route column's hero blade sign: rule-placed, not random
        L_ = max(4.5, hmax - 1.6)
        for k in range(max(3, int(hmax / 1.4)) // 2):
            za = 2.2 + k * 2.0
            if za + 1.6 > L_:
                break
            c = INK_HOME[k % 2] if k % 3 else shade(INK_HOME[k % 2], 1.4)
            R.poly([(x0 + 0.3, y1, za), (x0 + 0.3, y1 + 2.2, za), (x0 + 0.3, y1 + 2.2, za + 1.6), (x0 + 0.3, y1, za + 1.6)], c, emit=c)
    else:
        for k, (on, a, bb) in enumerate(D["blade"]):
            if not on or hmax < 5:
                continue
            t = x0 + 1.0 + a * (x1 - x0 - 2.0)
            zb = 2.0 + bb * max(0.5, min(hmax - 4.0, 9.0))
            c = b["ink"] if k % 2 == 0 else b["ink2"]
            st = D["sign_style"]
            if st == 0:                                 # vertical blade
                R.poly([(t, y1, zb), (t, y1 + 1.4, zb), (t, y1 + 1.4, zb + 3.2), (t, y1, zb + 3.2)], c, emit=c)
            elif st == 1:                               # stacked panels
                for m in range(3):
                    zz = zb + m * 1.25
                    cc = c if m % 2 == 0 else shade(c, 0.6)
                    R.poly([(t, y1, zz), (t, y1 + 1.8, zz), (t, y1 + 1.8, zz + 1.0), (t, y1, zz + 1.0)], cc, emit=cc)
            else:                                       # flat box sign on the face
                w = min(3.0, x1 - t - 0.3)
                if w > 1.0:
                    R.poly([(t, y1 + 0.3, zb), (t + w, y1 + 0.3, zb), (t + w, y1 + 0.3, zb + 1.4), (t, y1 + 0.3, zb + 1.4)], c, emit=c)
    # roof
    tx0, ty0, tx1, ty1, tz0, zt = b["parts"][-1]
    if D["trim"]:
        for a, c in (((tx0, ty1, zt), (tx1, ty1, zt)), ((tx1, ty0, zt), (tx1, ty1, zt)),
                     ((tx0, ty0, zt), (tx1, ty0, zt)), ((tx0, ty0, zt), (tx0, ty1, zt))):
            R.line(a, c, b["ink"], 2)
    pos = D["ac_pos"]
    for k in range(min(3, D["ac"])):
        ax = tx0 + 0.5 + pos[2 * k] * max(0.1, tx1 - tx0 - 2.0)
        ay = ty0 + 0.5 + pos[2 * k + 1] * max(0.1, ty1 - ty0 - 1.6)
        draw_box(R, dict(b, body=(0.3, 0.3, 0.34)), ax, ay, ax + 1.1, ay + 0.9, zt, zt + 0.7, wins=False)
    if D["tank"]:
        cx = tx0 + 1.5 + D["tank_pos"][0] * max(0.1, tx1 - tx0 - 3.0)
        cy = ty0 + 1.5 + D["tank_pos"][1] * max(0.1, ty1 - ty0 - 3.0)
        for dx, dy in ((-0.5, 0.5), (0.5, 0.5), (0.5, -0.5)):
            R.line((cx + dx, cy + dy, zt), (cx + dx, cy + dy, zt + 1.0), (0.2, 0.2, 0.24), 2, emit=False)
        draw_box(R, dict(b, body=(0.42, 0.33, 0.26)), cx - 0.8, cy - 0.8, cx + 0.8, cy + 0.8, zt + 1.0, zt + 2.6, wins=False)
        R.poly([(cx - 0.8, cy - 0.8, zt + 2.6), (cx + 0.8, cy - 0.8, zt + 2.6), (cx + 0.8, cy + 0.8, zt + 2.6), (cx - 0.8, cy + 0.8, zt + 2.6)],
               (0.5, 0.4, 0.32))
    if D["holo"]:
        cx, cy = (tx0 + tx1) / 2, (ty0 + ty1) / 2
        a = min(3.2, (tx1 - tx0) * 0.45)
        R.line((cx, cy, zt), (cx, cy, zt + 1.2), (0.2, 0.2, 0.24), 2, emit=False)
        c = D["holo_col"]
        R.poly([(cx - a, cy + a, zt + 1.2), (cx + a, cy - a, zt + 1.2), (cx + a, cy - a, zt + 1.2 + a * 1.1),
                (cx - a, cy + a, zt + 1.2 + a * 1.1)], shade(c, 0.85), emit=shade(c, 0.8))
    if D["antenna"]:
        cx, cy = (tx0 + tx1) / 2 + 0.7, (ty0 + ty1) / 2 - 0.7
        R.line((cx, cy, zt), (cx, cy, zt + 5.0), (0.3, 0.3, 0.35), 2, emit=False)
        R.line((cx, cy, zt + 5.0), (cx, cy, zt + 5.5), (1, 0.15, 0.15), 4)


def render(seed, var, w=760, h=560, ss=2):
    W, H = w * ss, h * ss
    s = 6.2 * ss
    R = Iso(W, H, s, ox=W * 0.5 - (EXT_X - EXT_Y) * 0.866 * s / 2, oy=H * 0.40)
    # sky
    a = np.zeros((H, W, 3), np.float32)
    yy = np.linspace(0, 1, H)[:, None]
    for k, (c0, c1) in enumerate(zip((0.05, 0.035, 0.09), (0.16, 0.08, 0.19))):
        a[..., k] = c0 + (c1 - c0) * yy ** 1.6
    R.img = Image.fromarray((a * 255).astype(np.uint8))
    R.d = ImageDraw.Draw(R.img)
    # ground, streets, lane light
    R.poly([(0, 0, 0), (EXT_X, 0, 0), (EXT_X, EXT_Y, 0), (0, EXT_Y, 0)], (0.06, 0.06, 0.08))
    xs = (X_STREET_AFTER + 1) * LOT
    ys = (Y_STREET_AFTER + 1) * LOT
    yf = EXT_Y - FRONT
    for q, lane in (([(xs, 0, 0), (xs + X_STREET, 0, 0), (xs + X_STREET, yf, 0), (xs, yf, 0)], "y"),
                    ([(0, ys, 0), (EXT_X, ys, 0), (EXT_X, ys + Y_STREET, 0), (0, ys + Y_STREET, 0)], "x"),
                    ([(0, yf, 0), (EXT_X, yf, 0), (EXT_X, EXT_Y, 0), (0, EXT_Y, 0)], "x")):
        R.poly(q, (0.09, 0.085, 0.11))
    for k, c in enumerate(((1.0, 0.35, 0.3), (0.9, 0.9, 1.0))):     # the front street's traffic streaks (fixed)
        yv = yf + 3.0 + k * 3.0
        for m in range(6):
            x_ = 4 + m * 12.5 + k * 5
            R.line((x_, yv, 0.05), (x_ + 5.5, yv, 0.05), c, 3)
    city = gen_city(seed, var)
    for b in sorted(city, key=lambda b: (b["i"] + b["j"], b["i"])):
        if b["route"]:
            x0, y0, x1, y1 = lot_box(b["i"], b["j"])
            R.poly([(x0 - 0.3, y0 - 0.3, 0.02), (x1 + 0.3, y0 - 0.3, 0.02), (x1 + 0.3, y1 + 0.3, 0.02), (x0 - 0.3, y1 + 0.3, 0.02)],
                   (0.83, 1.0, 0.0), emit=(0.4, 0.5, 0.0))
        draw_lot(R, b)
    # route markers: the game's, fixed - a lime outline on the route building's street face
    for b in city:
        if b["route"]:
            x0, y0, x1, y1, z0, z1 = b["parts"][0]
            for a_, c_ in (((x0, y1, 0), (x1, y1, 0)), ((x1, y1, 0), (x1, y1, z1)), ((x0, y1, z1), (x1, y1, z1)), ((x0, y1, 0), (x0, y1, z1))):
                R.line(a_, c_, (0.83, 1.0, 0.0), 3)
    base = np.asarray(R.img, np.float32) / 255
    em = R.emit
    g1 = np.asarray(em.filter(ImageFilter.GaussianBlur(4 * ss)), np.float32) / 255
    g2 = np.asarray(em.filter(ImageFilter.GaussianBlur(14 * ss)), np.float32) / 255
    out = base + g1 * 0.55 + g2 * 0.7
    out = 1 - np.exp(-out * 1.15)                                    # soft display knee
    img = Image.fromarray((np.clip(out / (1 - math.exp(-1.15)), 0, 1) * 255).astype(np.uint8))
    return img.resize((w, h), Image.LANCZOS), city


def summary(city):
    from collections import Counter
    nr = [b for b in city if not b["route"]]
    hs = [b["h"] for b in nr]
    types = Counter(b["typ"] for b in nr)
    signs = sum(sum(1 for on, *_ in b["d"]["blade"] if on) for b in nr) + sum(b["d"]["holo"] for b in nr)
    foreign = sum(1 for b in nr if b["ink"] in INK_FOREIGN)
    return dict(h_min=min(hs), h_max=max(hs), h_cv=float(np.std(hs) / np.mean(hs)), types=dict(sorted(types.items())),
                signs=signs, foreign_ink=foreign, n=len(nr))


# ------------------------------------------------------------------ the sheet
SEEDS = [40417, 77231, 91002]


def main():
    Wd, PAD = 2400, 14
    pw, ph = 770, 560
    gap = (Wd - 2 * PAD - 3 * pw) // 2
    renders = {}
    for sd in SEEDS:
        renders[(sd, "MEDIUM")] = render(sd, "MEDIUM")
    for var in ("LOW", "HIGH"):
        renders[(SEEDS[0], var)] = render(SEEDS[0], var)
    again = render(SEEDS[0], "MEDIUM")[0]
    h1 = hashlib.md5(renders[(SEEDS[0], "MEDIUM")][0].tobytes()).hexdigest()
    h2 = hashlib.md5(again.tobytes()).hexdigest()
    same = h1 == h2
    print("rebuild identical:", same, h1)

    head = 300
    rowh = 60 + ph + 120
    foot = 270
    sheet = Image.new("RGB", (Wd, head + 2 * rowh + foot), L.BG)
    d = ImageDraw.Draw(sheet)
    f_t, f_h, f_b, f_s, f_m = L.font(44, True), L.font(26, True), L.font(22), L.font(19), L.font(19, mono=True)
    d.text((PAD + 10, 18), "Q9  ART RANDOMNESS  -  what it is, and what the settings do", font=f_t, fill=L.INK)
    L.para(d, (PAD + 10, 80),
           "Art randomness is the per-game variation in how the city LOOKS, kept apart from gameplay randomness. With the new "
           "direction the whole city is generated per game seed. The game's seed decides the rules side: the lots, the streets, the route and its rooms (here the three buildings outlined "
           "in lime, which never change below). From that same seed the game derives separate art seeds, and those decide "
           "only the dressing: which building type stands on each lot, how tall it is, where the signs go and in what "
           "style, which windows are lit, how much the colours mix, and the roof clutter (water tanks, AC units, "
           "antennas, holo billboards). The same seed always rebuilds the same city; a new game gets a new-looking city. "
           "Art never reads or advances the game's random streams, so changing a look can never change a fight, a "
           "reward or a route.", f_b, Wd - 40, fill=L.INK)
    L.para(d, (PAD + 10, 242),
           "Block below: one small one-city block, isometric massing drawn in Python (no render), lots, streets and route held fixed so only the art streams change. "
           "Rebuild check: seed %d at MEDIUM rendered twice gives %s images (md5 %s)."
           % (SEEDS[0], "identical" if same else "DIFFERENT", h1[:12]), f_s, Wd - 40, fill=L.DIM)
    y = head
    rows = [("(a)  SAME SETTINGS (MEDIUM), THREE SEEDS  -  three games, three different-looking blocks",
             [(sd, "MEDIUM", "seed %d" % sd) for sd in SEEDS]),
            ("(b)  ONE SEED (%d), THREE VARIANCE LEVELS  -  the same city, calmer or wilder" % SEEDS[0],
             [(SEEDS[0], v, v + ("  (= today's rules)" if v == "MEDIUM" else "")) for v in ("LOW", "MEDIUM", "HIGH")])]
    js = {}
    for title, cells in rows:
        d.text((PAD + 10, y + 10), title, font=f_h, fill=L.LIME)
        y2 = y + 60
        for c, (sd, var, lab) in enumerate(cells):
            x = PAD + c * (pw + gap)
            img, city = renders[(sd, var)]
            sheet.paste(img, (x, y2))
            d.rectangle((x, y2, x + pw - 1, y2 + ph - 1), outline=(70, 70, 90), width=2)
            d.text((x + 12, y2 + 10), lab, font=f_h, fill=L.INK, stroke_width=3, stroke_fill=(0, 0, 0))
            sm = summary(city)
            js["%d|%s" % (sd, var)] = sm
            v = VARIANCE[var]
            t1 = "heights %.0f-%.0f BU (spread %.0f %%)   types %s" % (sm["h_min"], sm["h_max"], sm["h_cv"] * 100,
                                                                     " ".join("%s %d" % (k[:5], n) for k, n in sm["types"].items()))
            t2 = "signs %d   foreign-colour inks %d / %d" % (sm["signs"], sm["foreign_ink"], sm["n"])
            t3 = "height_var %.2f  type_mix %.2f  sign_density %.2f" % (v["height_var"], v["type_mix"], v["sign_density"])
            t4 = "colour_mix %.2f  window_var %.2f  clutter %.1f" % (v["colour_mix"], v["window_var"], v["clutter"])
            for k, t in enumerate((t1, t2, t3, t4)):
                d.text((x + 4, y2 + ph + 8 + k * 26), t, font=f_m, fill=L.INK if k < 2 else L.DIM)
        y += rowh
    d.line((PAD, y, Wd - PAD, y), fill=(60, 60, 75), width=2)
    y += 18
    d.text((PAD + 10, y), "THE SETTINGS", font=f_h, fill=L.INK)
    L.para(d, (PAD + 10, y + 40),
           "height_var: spread of building heights around the district's height field. type_mix: how often a lot leaves the "
           "district's main building type. sign_density: scales blade signs (16 %), shop bands (55 %) and roof holos (16 %). "
           "colour_mix: share of signs and inks taken from other corps' colours, and the body tint. window_var: how much "
           "the lit-window share (30 %) differs per building. clutter: roof tanks, AC units, antennas. Each lot draws one "
           "fixed list of numbers from its own art stream, so the settings reshape a city without reshuffling it.",
           f_b, Wd / 2 - 60, fill=L.INK)
    rx = Wd / 2 + 20
    d.text((rx, y), "RECOMMENDATION", font=f_h, fill=L.LIME)
    L.para(d, (rx, y + 40),
           "Default to MEDIUM (today's rules): height_var 0.30, type_mix 0.60, sign_density 1.0, colour_mix 0.25, "
           "window_var 0.12, clutter 1.0. LOW reads as a model kit; HIGH loses the district identity and buries the "
           "route columns among signs and towers. Put the values in the art preset per district, so the Sprawl can sit "
           "toward HIGH (sign_density 1.4, colour_mix 0.4) and corp districts toward LOW around their HQ, which matches "
           "'colour by proximity to the nearest HQ'. Approve Q9 as proposed: art seeds come from the game seed, exported "
           "in derive_<run>.json, never from the game's streams.",
           f_b, Wd / 2 - 50, fill=L.INK)
    sheet.save(os.path.join(OUT, "Q9_art_randomness.png"), optimize=True)
    js["rebuild_identical"] = same
    json.dump(dict(variance=VARIANCE, base=BASE, seeds=SEEDS, blocks=js), open(os.path.join(OUT, "Q9_art_randomness.json"), "w"),
              indent=1)


if __name__ == "__main__":
    main()
