"""C War Table: shared library (geometry, drawing primitives, glyphs, plate grade).

All drawing happens on a 2x supersampled RGBA canvas (SS=2) with 1920x1080 coordinates
(callers pass 1x coordinates; helpers multiply).  Final frames are downsampled with LANCZOS.
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
PLATES = "D:/rc_scratch/tide_concepts/plates"
W, H = 1920, 1080
SS = 2

# ---- palette (hex) -----------------------------------------------------------------
INK = (27, 20, 36)            # cel ink
PAPER = (241, 232, 210)       # corp paper / token top
PAPER_L = (207, 196, 168)
PAPER_R = (182, 170, 142)
STOCK_CREAM = (242, 238, 228)
STOCK_YELLOW = (242, 220, 122)
STOCK_PINK = (244, 195, 207)
BEAM = {"D": (63, 140, 255), "N": (246, 241, 231), "E": (255, 210, 63)}
UNTOUCHED = (191, 251, 240)   # cool mint / cyan-white
HOLDS = (31, 184, 166)        # teal
LOST = (242, 154, 31)         # amber
DAMAGED = (255, 122, 26)      # orange
BREACH = (255, 59, 48)        # HARM red
PLUM = (26, 11, 31)
PLUM2 = (58, 22, 62)
VEIN = (255, 63, 160)
HOTFRONT = (255, 150, 215)
LIME = (212, 255, 0)          # focus halo only
CRT_BG = (8, 18, 36)
CRT_EDGE = (92, 225, 255)
FELT = (14, 24, 27)

# ---- camera transform (plate px -> frame px) --------------------------------------
S = 1.85
CEN = (703.0, 555.0)
ORG = (960.0, 540.0)
ISO_K = 0.643  # sin(pitch 40): ground circle -> ellipse ratio
TH = 10.0  # token slab height (px per tier)
TR = 27   # token radius


def T(p):
    return ((p[0] - CEN[0]) * S + ORG[0], (p[1] - CEN[1]) * S + ORG[1])


def font(name, size):
    f = {"anton": "Anton-Regular.ttf", "marker": "PermanentMarker-Regular.ttf",
         "mono": "ShareTechMono-Regular.ttf"}[name]
    return ImageFont.truetype(os.path.join(HERE, f), int(size * SS))


# ---- data ---------------------------------------------------------------------------
def load_geo():
    d = json.load(open(f"{PLATES}/coords/default_forecast.json"))
    nodes = {}
    for l in d["links"]:
        p = l["polyline"]
        if p:
            nodes[l["a"]] = tuple(p[0])
            nodes[l["b"]] = tuple(p[-1])
    # beam site paths (core first, home last)
    return d, nodes


# ---- canvas -------------------------------------------------------------------------
class Canvas:
    def __init__(self, base_rgb):
        self.img = base_rgb.convert("RGBA")  # 2x

    def layer(self):
        return Image.new("RGBA", self.img.size, (0, 0, 0, 0))

    def merge(self, lay):
        self.img = Image.alpha_composite(self.img, lay)

    def final(self):
        return self.img.convert("RGB").resize((W, H), Image.LANCZOS)


def sc(v):
    if isinstance(v, (list, tuple)):
        return [sc(x) for x in v]
    return v * SS


def pts2(pts):
    return [(x * SS, y * SS) for x, y in pts]


# ---- geometry ----------------------------------------------------------------------
_ANG = [0, 32.8, 90, 147.2, 180, 212.8, 270, 327.2]


def _dir(a):
    r = math.radians(a)
    return (math.cos(r), math.sin(r))


def dogleg(P, Q):
    """Octilinear route (0/90 + the two iso diagonals) from P to Q: 1 straight or 2 legs."""
    dx, dy = Q[0] - P[0], Q[1] - P[1]
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return [P]
    phi = math.degrees(math.atan2(dy, dx)) % 360
    for a in _ANG:
        if abs(((phi - a + 180) % 360) - 180) < 0.7:
            return [P, Q]
    angs = _ANG + [360]
    for i in range(len(_ANG)):
        a0, a1 = angs[i], angs[i + 1]
        if a0 <= phi <= a1:
            d0, d1 = _dir(a0), _dir(a1 % 360)
            det = d0[0] * d1[1] - d0[1] * d1[0]
            al = (dx * d1[1] - dy * d1[0]) / det
            be = (d0[0] * dy - d0[1] * dx) / det
            legs = [(d0, al), (d1, be)]
            # longer leg first
            if be > al:
                legs = legs[::-1]
            m = (P[0] + legs[0][0][0] * legs[0][1], P[1] + legs[0][0][1] * legs[0][1])
            return [P, m, Q]
    return [P, Q]


def route(nodes_xy, key=None):
    out = [nodes_xy[0]]
    for a, b in zip(nodes_xy[:-1], nodes_xy[1:]):
        seg = dogleg(a, b)
        out += seg[1:]
    return out


def offset_poly(pts, d):
    if abs(d) < 1e-6 or len(pts) < 2:
        return list(pts)
    n = len(pts)
    segs = []
    for i in range(n - 1):
        dx, dy = pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]
        L = math.hypot(dx, dy) or 1
        segs.append((dx / L, dy / L))
    out = []
    for i in range(n):
        if i == 0:
            t = segs[0]
            nx, ny = -t[1], t[0]
            out.append((pts[i][0] + nx * d, pts[i][1] + ny * d))
        elif i == n - 1:
            t = segs[-1]
            nx, ny = -t[1], t[0]
            out.append((pts[i][0] + nx * d, pts[i][1] + ny * d))
        else:
            t0, t1 = segs[i - 1], segs[i]
            n0, n1 = (-t0[1], t0[0]), (-t1[1], t1[0])
            mx, my = n0[0] + n1[0], n0[1] + n1[1]
            ml = math.hypot(mx, my)
            if ml < 1e-6:
                out.append((pts[i][0] + n0[0] * d, pts[i][1] + n0[1] * d))
            else:
                mx, my = mx / ml, my / ml
                k = 1.0 / max(0.5, (mx * n0[0] + my * n0[1]))
                out.append((pts[i][0] + mx * d * k, pts[i][1] + my * d * k))
    return out


def fillet(pts, r=14, steps=7):
    if len(pts) < 3:
        return list(pts)
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        v0 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l0, l2 = math.hypot(*v0), math.hypot(*v2)
        if l0 < 1e-6 or l2 < 1e-6:
            continue
        rr = min(r, l0 * 0.45, l2 * 0.45)
        a = (p1[0] + v0[0] / l0 * rr, p1[1] + v0[1] / l0 * rr)
        b = (p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr)
        for k in range(steps + 1):
            t = k / steps
            x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * p1[0] + t * t * b[0]
            y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * p1[1] + t * t * b[1]
            out.append((x, y))
    out.append(pts[-1])
    return out


def arclen(pts):
    ls = [0.0]
    for a, b in zip(pts[:-1], pts[1:]):
        ls.append(ls[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return ls


def point_at(pts, ls, s):
    s = max(0, min(ls[-1], s))
    for i in range(len(pts) - 1):
        if ls[i + 1] >= s:
            seg = ls[i + 1] - ls[i] or 1
            t = (s - ls[i]) / seg
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t
            y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t
            ang = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
            return (x, y), ang
    return pts[-1], 0.0


def sub_path(pts, ls, s0, s1):
    out = []
    p, _ = point_at(pts, ls, s0)
    out.append(p)
    for i in range(len(pts)):
        if s0 < ls[i] < s1:
            out.append(pts[i])
    p, _ = point_at(pts, ls, s1)
    out.append(p)
    return out


# ---- noise / textures ---------------------------------------------------------------
def snoise(shape, sigma, seed):
    rng = np.random.default_rng(seed)
    a = gaussian_filter(rng.random(shape).astype(np.float32), sigma, mode="wrap")
    a = (a - a.min()) / (a.max() - a.min() + 1e-6)
    return a


# ---- plate grade --------------------------------------------------------------------
_plate_cache = {}


def warped_plate():
    if "p" in _plate_cache:
        return _plate_cache["p"]
    im = Image.open(f"{PLATES}/city_noraid_nonet.png").convert("RGB")
    # out = (in - CEN)*S + ORG  =>  in = (out - ORG)/S + CEN
    a = 1.0 / S
    c = CEN[0] - ORG[0] / S
    f = CEN[1] - ORG[1] / S
    w = im.transform((W, H), Image.AFFINE, (a, 0, c, 0, a, f), resample=Image.BICUBIC)
    w = w.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    _plate_cache["p"] = w
    return w


def grade_plate(bloom=None, dim=1.0):
    """Toy-bright diorama grade + tilt-shift. bloom = (body, front, depth) arrays or None."""
    img = np.asarray(warped_plate()).astype(np.float32) / 255.0
    # exposure + saturation + a touch of contrast
    lum = (img * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    img = lum + (img - lum) * 1.25
    img = np.clip(img * 1.55 + 0.02, 0, 1.4)
    img = img ** 0.92
    # warm lamp pool + cool rim: multiply field
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    lamp = np.exp(-(((xx - 960) / 900) ** 2 + ((yy - 480) / 300) ** 2))
    tint = np.stack([1.10 + 0.06 * lamp, 1.0 + 0.03 * lamp, 0.96 - 0.04 * lamp], 2)
    img = img * (0.30 + 0.78 * lamp[..., None]) * tint
    # window bloom
    hi = np.clip(img - 0.78, 0, 1)
    glow = np.stack([gaussian_filter(hi[..., i], 5) for i in range(3)], 2)
    img = img + glow * 1.6
    img = np.clip(img, 0, 1)
    if bloom is not None:
        img = apply_bloom(img, bloom)
    img = img * dim
    # tilt-shift: variable blur by |y - focus|
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    levels = [pil] + [pil.filter(ImageFilter.GaussianBlur(r)) for r in (2.2, 4.5, 8.0)]
    la = [np.asarray(l).astype(np.float32) for l in levels]
    fy0, fy1 = 380, 700
    d = np.where(yy < fy0, fy0 - yy, np.where(yy > fy1, yy - fy1, 0)) / 230.0
    d = np.clip(d, 0, 1) * 3.0
    out = np.zeros_like(la[0])
    for i in range(4):
        wgt = np.clip(1 - np.abs(d - i), 0, 1)[..., None]
        out += la[i] * wgt
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ---- Bloom (necrosis): plum body, pink Voronoi veins, hot hairline front --------------
def bloom_field(seeds, seed=7):
    """seeds: list of (x,y,radius) in frame px. Returns field f (<1 inside) in ground metric."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    warp = (snoise((H, W), 22, seed) - 0.5) * 0.55 + (snoise((H, W), 7, seed + 1) - 0.5) * 0.22
    f = np.full((H, W), 9.0, np.float32)
    for (sx, sy, r) in seeds:
        d = np.sqrt((xx - sx) ** 2 + ((yy - sy) / ISO_K) ** 2) / r
        f = np.minimum(f, d)
    return f + warp * 0.6 * np.clip(f, 0, 1.4)  # warp the front, not the core


def make_bloom(seeds, seed=7):
    f = bloom_field(seeds, seed)
    return {"f": f, "seed": seed}


def apply_bloom(img, bl):
    f = bl["f"]
    seed = bl["seed"]
    inside = np.clip((1.0 - f) * 40.0, 0, 1)  # hard edge
    depth = np.clip(1.0 - f, 0, 1)
    # windows dying behind the front: near front keep some light, deeper goes dark
    keep = 0.30 * np.clip(1 - depth * 4.0, 0, 1) + 0.06
    lum = (img * [0.299, 0.587, 0.114]).sum(2, keepdims=True)
    body = np.array(PLUM, np.float32) / 255.0
    dead = body * 0.9 + (lum * 0.30) * np.array([0.8, 0.45, 1.0], np.float32)
    flick = (snoise((H, W), 1.4, seed + 5) > 0.74).astype(np.float32)[..., None]
    lit = img * np.array([1.0, 0.45, 0.8], np.float32) * 0.55 * flick * np.clip(1 - depth * 2.5, 0, 1)[..., None]
    mixed = dead + lit * 0.9
    k = (inside * (0.80 + 0.2 * (1 - keep)))[..., None]
    img = img * (1 - k) + mixed * k
    # Voronoi veins
    rng = np.random.default_rng(seed + 11)
    ys, xs = np.nonzero(inside > 0.5)
    if len(xs) > 50:
        npts = max(12, int(len(xs) / 2600))
        px = rng.choice(len(xs), npts, replace=False)
        pts = np.stack([xs[px], ys[px] * 1.0], 1).astype(np.float32)
        tree = cKDTree(pts)
        sub = np.stack([xs, ys], 1).astype(np.float32)
        dd, _ = tree.query(sub, k=2)
        edge = (dd[:, 1] - dd[:, 0]) < 0.9
        vein = np.zeros((H, W), np.float32)
        vein[ys[edge], xs[edge]] = 1.0
        vein = gaussian_filter(vein, 0.5)
        vein = np.clip(vein * 2.4, 0, 1)
        vcol = np.array(VEIN, np.float32) / 255.0
        vgain = (0.55 + 0.45 * np.clip(1 - depth * 3, 0, 1))[..., None]
        img = img + (vcol * vein[..., None] * vgain - img * vein[..., None] * 0.2) * 0.9
        img = np.clip(img, 0, 1.2)
    # hot hairline front + glow
    front = np.exp(-((f - 1.0) / 0.012) ** 2)
    glow = np.exp(-((f - 1.0) / 0.05) ** 2) * (f > 0.985)
    hot = np.array(HOTFRONT, np.float32) / 255.0
    img = img + hot * front[..., None] * 1.0 + np.array(VEIN, np.float32) / 255.0 * glow[..., None] * 0.35
    return np.clip(img, 0, 1.3)


# ---- table, slab ---------------------------------------------------------------------
SLAB = (64, 116, 1856, 872)  # x0,y0,x1,y1 (1x)
SLAB_THICK = 22


def make_base(bloom=None, dim=1.0, table_lamp=True):
    rng = np.random.default_rng(3)
    # felt table
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    felt = np.zeros((H, W, 3), np.float32)
    base = np.array(FELT, np.float32) / 255.0
    n = snoise((H, W), 1.2, 4)
    felt[:] = base
    felt *= (0.85 + 0.35 * n[..., None])
    lamp = np.exp(-(((xx - 960) / 1100) ** 2 + ((yy - 560) / 700) ** 2))
    felt *= (0.35 + 1.1 * lamp[..., None])
    felt[..., 0] *= 1.0 + 0.15 * lamp
    # cutting-mat grid
    grid = np.zeros((H, W), np.float32)
    grid[:, ::48] += 1
    grid[::48, :] += 1
    gblur = gaussian_filter(grid, 0.7)
    felt += (np.array([0.10, 0.20, 0.20], np.float32)) * gblur[..., None] * 0.35 * (0.4 + lamp[..., None])
    felt = np.clip(felt, 0, 1)
    table = Image.fromarray((felt * 255).astype(np.uint8)).resize((W * SS, H * SS), Image.BICUBIC)
    cv = table.convert("RGBA")
    # slab shadow
    x0, y0, x1, y1 = SLAB
    sh = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(sh).rounded_rectangle(sc([x0 + 6, y0 + 16, x1 + 14, y1 + SLAB_THICK + 26]), radius=24 * SS, fill=210)
    sh = sh.filter(ImageFilter.GaussianBlur(16 * SS))
    cv = Image.alpha_composite(cv, Image.merge("RGBA", (Image.new("L", sh.size, 0),) * 3 + (sh,)))
    d = ImageDraw.Draw(cv)
    # foam-board edge (front + sides)
    d.rounded_rectangle(sc([x0 - 4, y0 + 6, x1 + 4, y1 + SLAB_THICK]), radius=12 * SS, fill=(30, 26, 38, 255))
    d.rounded_rectangle(sc([x0 - 2, y0 + 8, x1 + 2, y1 + SLAB_THICK - 2]), radius=11 * SS, fill=(226, 218, 200, 255))
    # foam layers (cut face)
    for k in range(3):
        yk = y1 + 5 + k * 5.5
        d.line(sc([(x0 + 10, yk), (x1 - 10, yk)]), fill=(170, 160, 140, 255), width=SS)
    d.line(sc([(x0 + 12, y1 + SLAB_THICK - 1), (x1 - 12, y1 + SLAB_THICK - 1)]), fill=(27, 20, 36, 255), width=2 * SS)
    # plate
    plate = grade_plate(bloom, dim).resize((W * SS, H * SS), Image.BICUBIC)
    m = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle(sc([x0, y0, x1, y1]), radius=10 * SS, fill=255)
    cv.paste(plate.convert("RGBA"), (0, 0), m)
    d = ImageDraw.Draw(cv)
    # slab rim: ink line + inner bevel highlight
    d.rounded_rectangle(sc([x0, y0, x1, y1]), radius=10 * SS, outline=INK + (255,), width=3 * SS)
    d.rounded_rectangle(sc([x0 + 3, y0 + 3, x1 - 3, y1 - 3]), radius=8 * SS, outline=(255, 244, 220, 70), width=SS)
    # slab vignette on plate (edge falloff)
    vg = Image.new("L", (W * SS, H * SS), 0)
    ImageDraw.Draw(vg).rounded_rectangle(sc([x0 + 40, y0 + 40, x1 - 40, y1 - 40]), radius=60 * SS, fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(60 * SS))
    dark = Image.new("RGBA", vg.size, (6, 4, 14, 255))
    inv = ImageChops.invert(vg).point(lambda v: int(v * 0.62))
    dark.putalpha(ImageChops.multiply(inv, m))
    cv = Image.alpha_composite(cv, dark)
    return cv


# ---- primitives ------------------------------------------------------------------------
def rgba(c, a=255):
    return (int(c[0]), int(c[1]), int(c[2]), int(a))


def ink_line(d, pts, w, fill, ink_w=2.5, ink=INK, alpha=255):
    P = pts2(pts)
    d.line(P, fill=rgba(ink, alpha), width=int((w + ink_w * 2) * SS), joint="curve")
    r = (w + ink_w * 2) * SS / 2
    for p in (P[0], P[-1]):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=rgba(ink, alpha))
    d.line(P, fill=rgba(fill, alpha), width=int(w * SS), joint="curve")
    r = w * SS / 2
    for p in (P[0], P[-1]):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=rgba(fill, alpha))


def line_w(d, pts, w, fill, alpha=255):
    P = pts2(pts)
    d.line(P, fill=rgba(fill, alpha), width=max(1, int(w * SS)), joint="curve")
    r = w * SS / 2
    for p in (P[0], P[-1]):
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=rgba(fill, alpha))


def dashed(pts, on, off):
    ls = arclen(pts)
    out = []
    s = 0.0
    while s < ls[-1]:
        e = min(ls[-1], s + on)
        out.append(sub_path(pts, ls, s, e))
        s = e + off
    return out


def ellipse_pts(cx, cy, rx, ry, a0=0, a1=360, n=90):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts.append((cx + rx * math.cos(a), cy + ry * math.sin(a)))
    return pts


def hexpts(cx, cy, r, squash=ISO_K, rot=0):
    return [(cx + r * math.cos(math.radians(60 * i + rot)), cy + r * squash * math.sin(math.radians(60 * i + rot)))
            for i in range(6)]


def shape_glyph(d, kind, cx, cy, s, fill, ink=INK, ink_w=1.6, alpha=255):
    """D = circle, N = triangle, E = square (Mini Metro passenger shapes)."""
    if kind == "D":
        pts = None
        d.ellipse(sc([cx - s, cy - s, cx + s, cy + s]), fill=rgba(fill, alpha), outline=rgba(ink, alpha), width=int(ink_w * SS))
    elif kind == "N":
        pts = [(cx, cy - s * 1.15), (cx + s * 1.1, cy + s * 0.85), (cx - s * 1.1, cy + s * 0.85)]
        d.polygon(pts2(pts), fill=rgba(fill, alpha), outline=rgba(ink, alpha), width=int(ink_w * SS))
    else:
        d.rounded_rectangle(sc([cx - s * 0.95, cy - s * 0.95, cx + s * 0.95, cy + s * 0.95]), radius=int(2 * SS),
                            fill=rgba(fill, alpha), outline=rgba(ink, alpha), width=int(ink_w * SS))


# ---- glyph atlas (verbs, icons) ------------------------------------------------------
def g_shield(d, cx, cy, s, fill, ink=INK, ink_w=0):
    pts = [(-1, -0.95), (1, -0.95), (1, 0.15), (0, 1.15), (-1, 0.15)]
    P = [(cx + x * s, cy + y * s) for x, y in pts]
    d.polygon(pts2(P), fill=rgba(fill), outline=rgba(ink) if ink_w else None, width=int(ink_w * SS))


def g_shift(d, cx, cy, s, fill):
    arc = ellipse_pts(cx, cy + s * 0.1, s * 0.9, s * 0.8, 200, 20 + 360 - 360 + 0, 40)
    arc = ellipse_pts(cx, cy + s * 0.15, s * 0.85, s * 0.85, 190, 380, 36)
    line_w(d, arc, s * 0.34, fill)
    e = arc[-1]
    tri = [(e[0] - s * 0.55, e[1] - s * 0.05), (e[0] + s * 0.55, e[1] - s * 0.05), (e[0], e[1] + s * 0.7)]
    d.polygon(pts2(tri), fill=rgba(fill))


def g_jam(d, cx, cy, s, fill):
    pts = [(cx - s, cy + s * 0.5), (cx - s * 0.5, cy - s * 0.7), (cx, cy + s * 0.5), (cx + s * 0.5, cy - s * 0.7), (cx + s, cy + s * 0.5)]
    line_w(d, pts, s * 0.34, fill)


def g_house(d, cx, cy, s, fill, ink=INK):
    roof = [(cx - s * 1.1, cy - s * 0.05), (cx, cy - s * 1.0), (cx + s * 1.1, cy - s * 0.05)]
    d.polygon(pts2(roof), fill=rgba(fill))
    d.rectangle(sc([cx - s * 0.75, cy - s * 0.1, cx + s * 0.75, cy + s * 0.9]), fill=rgba(fill))
    d.rectangle(sc([cx - s * 0.22, cy + s * 0.25, cx + s * 0.22, cy + s * 0.9]), fill=rgba(ink))


def g_flame(d, cx, cy, s, fill):
    pts = [(cx, cy - s * 1.1), (cx + s * 0.55, cy - s * 0.2), (cx + s * 0.75, cy + s * 0.35), (cx + s * 0.35, cy + s * 0.95),
           (cx - s * 0.35, cy + s * 0.95), (cx - s * 0.75, cy + s * 0.35), (cx - s * 0.45, cy - s * 0.3), (cx - s * 0.15, cy + s * 0.0)]
    d.polygon(pts2(pts), fill=rgba(fill))


def g_wrench(d, cx, cy, s, fill, ink=INK):
    line_w(d, [(cx - s * 0.8, cy + s * 0.8), (cx + s * 0.45, cy - s * 0.45)], s * 0.42, fill)
    d.ellipse(sc([cx + s * 0.1, cy - s * 1.0, cx + s * 1.0, cy - s * 0.1]), fill=rgba(fill))
    d.polygon(pts2([(cx + s * 0.45, cy - s * 0.55), (cx + s * 1.0, cy - s * 1.15), (cx + s * 1.1, cy - s * 0.35)]), fill=rgba(ink))


def g_skull(d, cx, cy, s, fill, ink=INK):
    d.ellipse(sc([cx - s * 0.95, cy - s * 1.05, cx + s * 0.95, cy + s * 0.55]), fill=rgba(fill))
    d.rounded_rectangle(sc([cx - s * 0.55, cy + s * 0.2, cx + s * 0.55, cy + s * 1.05]), radius=int(s * 0.18 * SS), fill=rgba(fill))
    for ex in (-0.42, 0.42):
        d.ellipse(sc([cx + s * ex - s * 0.3, cy - s * 0.4, cx + s * ex + s * 0.3, cy + s * 0.2]), fill=rgba(ink))
    d.polygon(pts2([(cx, cy + s * 0.05), (cx - s * 0.14, cy + s * 0.4), (cx + s * 0.14, cy + s * 0.4)]), fill=rgba(ink))
    for tx in (-0.3, -0.1, 0.1, 0.3):
        d.line(sc([(cx + s * tx, cy + s * 0.65), (cx + s * tx, cy + s * 1.02)]), fill=rgba(ink), width=max(1, int(s * 0.07 * SS)))


def g_helix(d, cx, cy, s, fill, ink=INK):
    a, b = [], []
    for i in range(25):
        t = i / 24
        y = cy - s + t * 2 * s
        x = math.sin(t * 2 * math.pi * 1.5) * s * 0.55
        a.append((cx + x, y))
        b.append((cx - x, y))
    line_w(d, a, s * 0.22, fill)
    line_w(d, b, s * 0.22, ink)
    for i in range(2, 24, 4):
        d.line(sc([a[i], b[i]]), fill=rgba(ink), width=max(1, int(s * 0.1 * SS)))


def g_crosshair(d, cx, cy, s, fill):
    d.ellipse(sc([cx - s, cy - s, cx + s, cy + s]), outline=rgba(fill), width=int(s * 0.22 * SS))
    for a in (0, 90, 180, 270):
        r = math.radians(a)
        d.line(sc([(cx + math.cos(r) * s * 0.55, cy + math.sin(r) * s * 0.55), (cx + math.cos(r) * s * 1.35, cy + math.sin(r) * s * 1.35)]),
               fill=rgba(fill), width=int(s * 0.22 * SS))
    d.ellipse(sc([cx - s * 0.18, cy - s * 0.18, cx + s * 0.18, cy + s * 0.18]), fill=rgba(fill))


def g_flag(d, cx, cy, s, fill, ink=INK):
    d.line(sc([(cx - s * 0.6, cy + s), (cx - s * 0.6, cy - s)]), fill=rgba(ink), width=int(s * 0.2 * SS))
    d.polygon(pts2([(cx - s * 0.6, cy - s), (cx + s, cy - s * 0.4), (cx - s * 0.6, cy + s * 0.2)]), fill=rgba(fill))


def g_envelope(d, cx, cy, w, h, fill, ink=INK):
    d.rectangle(sc([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2]), fill=rgba(fill), outline=rgba(ink), width=int(1.6 * SS))
    d.line(sc([(cx - w / 2, cy - h / 2), (cx, cy + h * 0.1), (cx + w / 2, cy - h / 2)]), fill=rgba(ink), width=int(1.4 * SS))


def grease_x(lay, cx, cy, s, color, seed=1, w=4.2, alpha=235):
    """D28 grease-pencil X: two jittery waxy strokes with grain."""
    rng = random.Random(seed)
    d = ImageDraw.Draw(lay)
    for (a, b) in (((-1, -1), (1, 1)), ((1, -1), (-1, 1))):
        pts = []
        for i in range(7):
            t = i / 6
            x = cx + (a[0] + (b[0] - a[0]) * t) * s + rng.uniform(-1.2, 1.2)
            y = cy + (a[1] + (b[1] - a[1]) * t) * s * 0.9 + rng.uniform(-1.2, 1.2)
            pts.append((x, y))
        line_w(d, pts, w, color, alpha)
        line_w(d, [(x + 1.1, y - 0.8) for x, y in pts], w * 0.45, tuple(min(255, c + 60) for c in color), int(alpha * 0.5))


def grease_circle(lay, cx, cy, rx, ry, color, seed=1, w=3.6, alpha=235, turns=1.12):
    rng = random.Random(seed)
    d = ImageDraw.Draw(lay)
    pts = []
    n = 40
    for i in range(int(n * turns) + 1):
        a = math.radians(-70 + 360 * turns * i / (n * turns))
        k = 1 + 0.05 * math.sin(a * 2 + seed) + rng.uniform(-0.015, 0.015) + 0.06 * i / (n * turns)
        pts.append((cx + rx * k * math.cos(a), cy + ry * k * math.sin(a)))
    line_w(d, pts, w, color, alpha)


# ---- text / stamps -----------------------------------------------------------------------
def text_mask(txt, fnt, tracking=0):
    w = int(sum(fnt.getlength(c) + tracking * SS for c in txt)) + 8
    h = int(fnt.size * 1.5)
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    x = 4
    for c in txt:
        d.text((x, 2), c, font=fnt, fill=255)
        x += fnt.getlength(c) + tracking * SS
    bbox = m.getbbox()
    return m.crop(bbox) if bbox else m


def paste_rot(cv, im, pos, angle, anchor=(0.5, 0.5)):
    """Paste RGBA sprite im centred at pos (1x coords) rotated by angle (deg ccw on screen)."""
    r = im.rotate(angle, expand=True, resample=Image.BICUBIC)
    ox = r.width * anchor[0]
    oy = r.height * anchor[1]
    tmp = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    tmp.paste(r, (int(pos[0] * SS - ox), int(pos[1] * SS - oy)), r)
    return Image.alpha_composite(cv, tmp)


def stamp_sprite(word, color, size=64, glyph=None, seed=3, border=True, tracking=2):
    """Rubber stamp: Anton text in a double rounded frame, ink-eroded, mis-registered ghost print."""
    fnt = font("anton", size)
    tm = text_mask(word, fnt, tracking)
    gw = 0
    pad = int(size * 0.34 * SS)
    gl = int(size * 1.15 * SS) if glyph else 0
    wd = tm.width + pad * 2 + (gl + pad // 2 if glyph else 0)
    ht = max(tm.height, gl) + pad * 2
    m = Image.new("L", (wd, ht), 0)
    d = ImageDraw.Draw(m)
    if border:
        d.rounded_rectangle([0, 0, wd - 1, ht - 1], radius=int(size * 0.16 * SS), outline=255, width=int(size * 0.07 * SS))
        d.rounded_rectangle([int(size * .13 * SS)] * 2 + [wd - 1 - int(size * .13 * SS), ht - 1 - int(size * .13 * SS)],
                            radius=int(size * 0.1 * SS), outline=255, width=int(size * 0.025 * SS))
    x = pad
    if glyph:
        gm = Image.new("RGBA", (gl, gl), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gm)
        glyph(gd, gl / SS / 2, gl / SS / 2, gl / SS * 0.4, (255, 255, 255), (0, 0, 0))
        m.paste(gm.convert("L").point(lambda v: 255 if v > 0 else 0), (x, (ht - gl) // 2))
        x += gl + pad // 2
    m.paste(tm, (x, (ht - tm.height) // 2), tm)
    # ink erosion
    rng = np.random.default_rng(seed)
    n = snoise((ht, wd), 1.1, seed)
    n2 = snoise((ht, wd), 5, seed + 1)
    arr = np.asarray(m).astype(np.float32)
    arr *= np.clip(((n * 0.6 + n2 * 0.7) - 0.18) * 6, 0, 1)
    m = Image.fromarray(arr.astype(np.uint8))
    out = Image.new("RGBA", (wd + 8, ht + 8), (0, 0, 0, 0))
    ghost = Image.new("RGBA", m.size, rgba(color, 255))
    ghost.putalpha(m.point(lambda v: int(v * 0.32)))
    out.paste(ghost, (7, 6), ghost)
    main = Image.new("RGBA", m.size, rgba(color, 255))
    main.putalpha(m)
    out.paste(main, (2, 2), main)
    return out


def paper_tag(w, h, seed=2, color=(236, 228, 206)):
    """Corp paper tag: manila rectangle, clipped corner, punched hole, string, barcode strip."""
    W2, H2 = int(w * SS), int(h * SS)
    pad = 10 * SS
    im = Image.new("RGBA", (W2 + pad * 2, H2 + pad * 2 + 20 * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    ox, oy = pad, pad + 14 * SS
    cut = int(26 * SS)
    poly = [(ox + cut, oy), (ox + W2, oy), (ox + W2, oy + H2), (ox, oy + H2), (ox, oy + cut)]
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).polygon([(x + 6 * SS, y + 8 * SS) for x, y in poly], fill=(0, 0, 0, 120))
    sh = sh.filter(ImageFilter.GaussianBlur(5 * SS))
    im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    d.polygon(poly, fill=rgba(color), outline=rgba(INK), width=int(2.2 * SS))
    d.ellipse([ox + 14 * SS, oy + 12 * SS, ox + 28 * SS, oy + 26 * SS], fill=(20, 16, 24, 255), outline=rgba(INK))
    d.line([(ox + 21 * SS, oy + 19 * SS), (ox + 70 * SS, oy - 12 * SS), (ox + 110 * SS, oy - 6 * SS)], fill=(120, 90, 60, 255), width=int(2.5 * SS))
    # barcode strip + helix mark (Solace)
    rng = random.Random(seed)
    x = ox + 14 * SS
    yb = oy + H2 - 20 * SS
    while x < ox + W2 * 0.55:
        bw = rng.choice([1, 1, 2, 3]) * SS
        d.rectangle([x, yb, x + bw, yb + 12 * SS], fill=rgba(INK, 200))
        x += bw + rng.choice([1, 2, 3]) * SS
    g_helix(d, (ox + W2 - 26 * SS) / SS, (oy + 28 * SS) / SS, 13, (122, 170, 110), INK)
    return im, (ox + W2 / 2, oy + H2 / 2)


# ---- tokens --------------------------------------------------------------------------------
def token_sprite(tier=1, state="healthy", R=27, exploit=False, seed=0):
    """Hex-stack board-game token (ziggurat: tier = layers). Returns (RGBA sprite, base anchor).
    Anchor = ground contact centre in sprite px (2x)."""
    k = SS
    th = TH
    Wd, Hd = int(150 * k), int(150 * k)
    im = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, cy = Wd / 2, Hd - 30 * k
    top, sl, sr = PAPER, PAPER_L, PAPER_R
    if state == "taken":
        top, sl, sr = (44, 18, 52), (26, 10, 32), (18, 7, 24)
    if state == "down":
        top, sl, sr = (196, 188, 170), (160, 152, 136), (140, 132, 118)
    # contact shadow
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - R * 1.15 * k, cy - R * 0.5 * k + 3 * k, cx + R * 1.25 * k, cy + R * 0.62 * k + 6 * k], fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(3 * k))
    im = Image.alpha_composite(im, sh)
    d = ImageDraw.Draw(im)
    y = cy
    for j in range(tier):
        r = R * (1 - 0.13 * j) * k
        pts_top = hexpts(cx, y - th * k, r)
        pts_bot = hexpts(cx, y, r)
        # visible side faces (lower half)
        for i in (0, 1, 2):
            a, b = pts_bot[i], pts_bot[(i + 1) % 6]
            a2, b2 = pts_top[i], pts_top[(i + 1) % 6]
            d.polygon([a, b, b2, a2], fill=rgba(sr if i == 0 else (sl if i == 2 else tuple(int((p + q) / 2) for p, q in zip(sl, sr)))),
                      outline=rgba(INK), width=int(1.5 * k))
        d.polygon(pts_top, fill=rgba(top), outline=rgba(INK), width=int(1.6 * k))
        y -= th * k
    top_y = y
    sprite_top = (cx, top_y)
    if state == "taken":
        rng = random.Random(seed + 4)
        for _ in range(4):
            a0 = rng.uniform(0, 6.28)
            pts = [(cx + math.cos(a0) * r0 * k, top_y + math.sin(a0) * r0 * k * ISO_K)
                   for r0 in (2, 6, 10 + rng.uniform(-2, 3), 14)]
            line_w(d, [(x / k, y_ / k) for x, y_ in pts], 1.5, VEIN, 235)
    if exploit and state != "taken":
        e = [(cx, top_y - 7 * k), (cx + 5 * k, top_y), (cx, top_y + 7 * k * 0.6), (cx - 5 * k, top_y)]
        d.polygon(e, fill=rgba((92, 225, 255)), outline=rgba(INK), width=int(1.2 * k))
    return im, (cx, cy), sprite_top


def put_token(cv, pos, tier, state="healthy", exploit=False, seed=0, rot=0.0, scale=1.0, dx=0, dy=0, R=27):
    im, anc, top = token_sprite(tier, state, R=R, exploit=exploit, seed=seed)
    if state == "down":
        # knocked over: rotate about the right-hand base corner, then settle
        px = anc[0] + R * 0.9 * SS
        py = anc[1]
        big = Image.new("RGBA", (im.width * 2, im.height * 2), (0, 0, 0, 0))
        big.paste(im, (im.width // 2, im.height // 2))
        r = big.rotate(-72, resample=Image.BICUBIC, center=(px + im.width // 2, py + im.height // 2))
        tmp = Image.new("RGBA", cv.size, (0, 0, 0, 0))
        tmp.paste(r, (int(pos[0] * SS + 8 * SS - (px + im.width // 2)), int(pos[1] * SS - (py + im.height // 2))), r)
        return Image.alpha_composite(cv, tmp)
    tmp = Image.new("RGBA", cv.size, (0, 0, 0, 0))
    tmp.paste(im, (int(pos[0] * SS - anc[0] + dx * SS), int(pos[1] * SS - anc[1] + dy * SS)), im)
    return Image.alpha_composite(cv, tmp)


def token_top(pos, tier, R=27):
    return (pos[0], pos[1] - TH * tier)


# ---- sticker cards ------------------------------------------------------------------------
def sticker(verb, ctype, stock=STOCK_CREAM, w=118, h=150, label=True):
    """Vinyl sticker card: white die-cut border, glyph, beam-shape corner badge. RGBA sprite (2x)."""
    k = SS
    pad = 12 * k
    im = Image.new("RGBA", (int(w * k) + pad * 2, int(h * k) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(12 * k)
    d.rounded_rectangle([pad - 5 * k, pad - 5 * k, pad + w * k + 5 * k, pad + h * k + 5 * k], radius=r + 4 * k, fill=(250, 250, 246, 255),
                        outline=rgba(INK), width=int(1.5 * k))
    d.rounded_rectangle([pad, pad, pad + w * k, pad + h * k], radius=r, fill=rgba(stock), outline=rgba(INK), width=int(2 * k))
    cx, cy = pad / k + w / 2, pad / k + h / 2 - (6 if label else 0)
    s = w * 0.27
    if verb == "GUARD":
        g_shield(d, cx, cy, s, INK)
        g_shield(d, cx, cy, s * 0.62, BEAM[ctype] if ctype != "N" else (210, 205, 195))
    elif verb == "SHIFT":
        g_shift(d, cx, cy, s, INK)
    else:
        g_jam(d, cx, cy, s, INK)
    shape_glyph(d, ctype, pad / k + 20, pad / k + 22, 10.5, BEAM[ctype], ink_w=2)
    if label:
        f = font("anton", 17)
        tm = text_mask(verb, f, 1)
        im.paste(Image.new("RGBA", tm.size, rgba(INK)), (int(im.width / 2 - tm.width / 2), int(pad + h * k - 28 * k)), tm)
    return im


def put_sticker(cv, sprite, pos, angle=0, scale=1.0, shadow=True, lift=1.0):
    sp = sprite
    if scale != 1.0:
        sp = sprite.resize((int(sprite.width * scale), int(sprite.height * scale)), Image.LANCZOS)
    if shadow:
        sh = Image.new("RGBA", sp.size, (0, 0, 0, 0))
        sh.putalpha(sp.getchannel("A").point(lambda v: int(v * 0.55)))
        sh = sh.filter(ImageFilter.GaussianBlur(3 * SS * lift))
        sh = Image.merge("RGBA", (Image.new("L", sh.size, 0),) * 3 + (sh.getchannel("A"),))
        cv = paste_rot(cv, sh, (pos[0] + 4 * lift, pos[1] + 6 * lift), angle)
    return paste_rot(cv, sp, pos, angle)


# ---- colour-blind sim --------------------------------------------------------------------
_M = {
    "deutan": np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    "tritan": np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def cvd(img, kind):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255
    lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    out = lin @ _M[kind].T
    out = np.clip(out, 0, 1)
    srgb = np.where(out <= 0.0031308, out * 12.92, 1.055 * out ** (1 / 2.4) - 0.055)
    return Image.fromarray((np.clip(srgb, 0, 1) * 255).astype(np.uint8))
