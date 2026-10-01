"""lightpen.py - AR light-pen / light-painting overlay renderer (Pillow + numpy).

The Cell writes on the world in hand-drawn light. Every mark is a set of pen
strokes; each stroke is simulated as a moving pen (speed falls in corners and at
the ends), and the speed drives the width: slow = thick and hot, fast = thin.
Rendering builds a body mask (coloured), a core mask (white-hot), streaks
(light-wand bristles), a halo, a chromatic fringe, an afterglow trail, sparks
where the pen lifts, and a large soft light map that lights the base image.

All randomness is seeded (numpy Generator passed in).
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SS = 2  # supersampling for stroke masks

PINK = np.array([1.00, 0.13, 0.60], np.float32)
PINK_HALO = np.array([1.00, 0.10, 0.48], np.float32)
CYAN = np.array([0.30, 0.86, 1.00], np.float32)
WHITE = np.array([1.0, 1.0, 1.0], np.float32)
FONT_PATH = "C:/Windows/Fonts/bahnschrift.ttf"

BASE_DIR = ("C:/Users/noitu/Documents/Godot/rebel_cell/.claude/worktrees/art-pass/"
            "docs/concepts/")
OUT_DIR = BASE_DIR + "round3_overlay/o_d_light_pen/"


# ----------------------------------------------------------------- blur utils
def _box1d(a, r, axis):
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(a, pad, mode="edge")
    c = np.cumsum(p, axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def _blur_direct(a, sigma):
    w = math.sqrt(12 * sigma * sigma / 3 + 1)
    r = max(1, int(round((w - 1) / 2)))
    for _ in range(3):
        a = _box1d(a, r, 0)
        a = _box1d(a, r, 1)
    return a


def gblur(a, sigma):
    """Approximate gaussian blur of a 2D float array (downsampled for big sigma)."""
    if sigma <= 0.3:
        return a
    h, w = a.shape
    f = int(sigma / 3)
    if f >= 2:
        small = Image.fromarray(a.astype(np.float32), "F").resize(
            (max(1, w // f), max(1, h // f)), Image.BILINEAR, reducing_gap=None)
        s = np.asarray(small, np.float32)
        s = _blur_direct(s, sigma / f)
        return np.asarray(Image.fromarray(s, "F").resize((w, h), Image.BILINEAR), np.float32)
    return _blur_direct(a, sigma)


def shift(a, dx, dy):
    out = np.zeros_like(a)
    h, w = a.shape[:2]
    xs0, xs1 = max(0, -dx), min(w, w - dx)
    ys0, ys1 = max(0, -dy), min(h, h - dy)
    out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = a[ys0:ys1, xs0:xs1]
    return out


# ------------------------------------------------------------- glyph skeletons
# y = 0 top, 1 baseline. A 3rd element 'c' marks a sharp corner (spline break).
C = "c"
GLYPHS = {
    "A": ([[(0, 1), (0.32, 0, C), (0.64, 1)], [(0.14, 0.64), (0.52, 0.60)]], 0.66),
    "B": ([[(0.06, 1), (0.06, 0, C), (0.36, 0.0), (0.54, 0.12), (0.5, 0.36), (0.28, 0.47),
            (0.07, 0.48, C), (0.4, 0.5), (0.6, 0.67), (0.55, 0.9), (0.34, 1.0), (0.06, 1.0)]], 0.62),
    "C": ([[(0.6, 0.16), (0.42, 0.0), (0.16, 0.08), (0.02, 0.5), (0.14, 0.9), (0.4, 1.0),
            (0.62, 0.86)]], 0.64),
    "D": ([[(0.06, 0), (0.06, 1, C), (0.34, 0.98), (0.58, 0.76), (0.62, 0.36), (0.42, 0.06),
            (0.06, 0.0)]], 0.66),
    "E": ([[(0.55, 0.0), (0.06, 0.02, C), (0.06, 1, C), (0.57, 1.0)],
           [(0.06, 0.5), (0.44, 0.48)]], 0.6),
    "F": ([[(0.55, 0.0), (0.06, 0.02, C), (0.06, 1)], [(0.06, 0.5), (0.42, 0.48)]], 0.56),
    "G": ([[(0.6, 0.15), (0.4, 0), (0.12, 0.1), (0.02, 0.5), (0.15, 0.92), (0.42, 1.0),
            (0.62, 0.82), (0.63, 0.56, C), (0.36, 0.56)]], 0.68),
    "H": ([[(0.06, 0), (0.06, 1)], [(0.6, 0), (0.6, 1)], [(0.06, 0.5), (0.6, 0.48)]], 0.68),
    "I": ([[(0.1, 0), (0.1, 1)]], 0.22),
    "K": ([[(0.06, 0), (0.06, 1)], [(0.56, 0), (0.1, 0.56, C), (0.6, 1)]], 0.62),
    "L": ([[(0.06, 0), (0.06, 1, C), (0.5, 1)]], 0.54),
    "M": ([[(0.03, 1), (0.08, 0, C), (0.37, 0.64, C), (0.66, 0, C), (0.72, 1)]], 0.78),
    "N": ([[(0.06, 1), (0.06, 0, C), (0.58, 1, C), (0.58, 0)]], 0.66),
    "O": ([[(0.36, 0), (0.1, 0.14), (0.02, 0.55), (0.2, 0.95), (0.44, 0.98), (0.64, 0.62),
            (0.6, 0.18), (0.4, 0.0), (0.22, 0.06)]], 0.7),
    "P": ([[(0.06, 1), (0.06, 0, C), (0.38, 0), (0.56, 0.14), (0.55, 0.36), (0.36, 0.5),
            (0.06, 0.5)]], 0.6),
    "R": ([[(0.06, 1), (0.06, 0, C), (0.38, 0), (0.56, 0.14), (0.55, 0.36), (0.36, 0.5),
            (0.08, 0.5, C), (0.6, 1)]], 0.64),
    "S": ([[(0.56, 0.12), (0.35, 0), (0.1, 0.08), (0.08, 0.32), (0.3, 0.48), (0.52, 0.62),
            (0.56, 0.88), (0.3, 1.0), (0.02, 0.9)]], 0.6),
    "T": ([[(-0.06, 0.05), (0.3, 0.0), (0.72, -0.02)], [(0.33, 0), (0.31, 1)]], 0.66),
    "U": ([[(0.05, 0), (0.05, 0.7), (0.18, 0.97), (0.4, 0.98), (0.57, 0.7), (0.57, 0)]], 0.64),
    "V": ([[(0, 0), (0.31, 1, C), (0.62, 0)]], 0.62),
    "W": ([[(0, 0), (0.19, 1, C), (0.39, 0.34, C), (0.58, 1, C), (0.78, 0)]], 0.8),
    "Y": ([[(0, 0), (0.3, 0.5, C), (0.6, 0)], [(0.3, 0.5), (0.3, 1)]], 0.6),
    "!": ([[(0.12, 0), (0.09, 0.68)], [(0.07, 0.9), (0.12, 0.93), (0.1, 0.99), (0.05, 0.95), (0.08, 0.91)]], 0.26),
    "6": ([[(0.5, 0.04), (0.24, 0.1), (0.06, 0.45), (0.08, 0.85), (0.3, 1.0), (0.52, 0.88),
            (0.55, 0.62), (0.32, 0.5), (0.08, 0.64)]], 0.6),
    "2": ([[(0.04, 0.2), (0.25, 0.0), (0.5, 0.08), (0.52, 0.32), (0.3, 0.6), (0.02, 1.0, C),
            (0.58, 0.99)]], 0.62),
    "9": ([[(0.52, 0.36), (0.3, 0.5), (0.06, 0.38), (0.08, 0.1), (0.3, 0.0), (0.52, 0.12),
            (0.54, 0.42), (0.48, 1)]], 0.6),
    "0": ([[(0.3, 0), (0.06, 0.2), (0.04, 0.7), (0.28, 1.0), (0.52, 0.8), (0.54, 0.25),
            (0.32, 0.0)]], 0.6),
    "-": ([[(0.05, 0.55), (0.4, 0.53)]], 0.46),
    "/": ([[(0.42, 0), (0.0, 1)]], 0.46),
    ".": ([[(0.05, 0.9), (0.1, 0.93), (0.08, 0.99), (0.03, 0.95), (0.06, 0.91)]], 0.2),
    " ": ([], 0.34),
}


def _catmull(pts, n=20):
    pts = np.asarray(pts, np.float64)
    if len(pts) == 2:
        t = np.linspace(0, 1, n)[:, None]
        return pts[0] * (1 - t) + pts[1] * t
    p = np.vstack([pts[0] * 2 - pts[1], pts, pts[-1] * 2 - pts[-2]])
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        t = np.linspace(0, 1, n, endpoint=False)[:, None]
        t2, t3 = t * t, t * t * t
        seg = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 +
                     (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
        out.append(seg)
    out.append(p[-2][None])
    return np.vstack(out)


def smooth_path(pts, n=20):
    """Points (x,y) or (x,y,'c'); corners break the spline. Returns Nx2."""
    segs, cur = [], [pts[0][:2]]
    for q in pts[1:]:
        cur.append(q[:2])
        if len(q) > 2:
            segs.append(cur)
            cur = [q[:2]]
    if len(cur) > 1:
        segs.append(cur)
    out = []
    for i, s in enumerate(segs):
        c = _catmull(s, n)
        out.append(c if i == 0 else c[1:])
    return np.vstack(out)


def _rot(p, ang, cx, cy):
    ca, sa = math.cos(ang), math.sin(ang)
    x, y = p[:, 0] - cx, p[:, 1] - cy
    return np.stack([cx + x * ca - y * sa, cy + x * sa + y * ca], 1)


def write(text, x, y, h, rng, slant=0.2, track=0.1, rot_deg=0.0, jit=0.022,
          size_jit=0.05, base_wobble=0.03, line_gap=1.45, flick=0.07):
    """Lay out text in the stroke alphabet. (x, y) = top-left. Returns list of Nx2."""
    strokes = []
    ang = math.radians(rot_deg)
    lines = text.split("\n")
    for li, line in enumerate(lines):
        cx = x
        ly = y + li * h * line_gap
        for ch in line.upper():
            spec, adv = GLYPHS.get(ch, GLYPHS[" "])
            sc = 1.0 + rng.normal(0, size_jit)
            gh = h * sc
            dy = rng.normal(0, base_wobble) * h
            gslant = slant + rng.normal(0, 0.04)
            for st in spec:
                pts = []
                for q in st:
                    px = q[0] + rng.normal(0, jit)
                    py = q[1] + rng.normal(0, jit)
                    pts.append((px, py) + tuple(q[2:]))
                path = smooth_path(pts)
                gx = cx + path[:, 0] * gh + (1 - path[:, 1]) * gslant * gh
                gy = ly + dy + (1 - sc) * h + path[:, 1] * gh
                sp = np.stack([gx, gy], 1)
                if len(sp) > 4 and flick > 0:
                    # gestural overshoot: the pen keeps travelling as it lifts
                    d = sp[-1] - sp[-4]
                    nd = np.linalg.norm(d)
                    if nd > 1e-6:
                        d = d / nd
                        ext = np.array([sp[-1] + d * gh * flick * f for f in (0.35, 0.7, 1.0)])
                        sp = np.vstack([sp, ext])
                strokes.append(sp)
            cx += (adv + track) * gh
    if ang != 0.0 and strokes:
        for i, s in enumerate(strokes):
            strokes[i] = _rot(s, ang, x, y)
    return strokes


def text_width(text, h, track=0.1):
    return sum((GLYPHS.get(c, GLYPHS[" "])[1] + track) * h for c in text.upper())


# ------------------------------------------------------------- shape helpers
def loop(cx, cy, rx, ry, rng, turns=1.18, start_deg=-120, tilt_deg=-8, wob=0.05):
    """A hand-drawn overshooting ellipse loop."""
    n = 220
    t = np.linspace(0, 1, n)
    a = math.radians(start_deg) + t * turns * 2 * math.pi
    grow = 1.0 + (t - 0.5) * 0.12
    k = rng.normal(0, wob, 4)
    r = grow * (1 + k[0] * np.sin(a * 2 + k[1] * 6) + k[2] * np.sin(a * 3 + k[3] * 6))
    p = np.stack([cx + np.cos(a) * rx * r, cy + np.sin(a) * ry * r], 1)
    return _rot(p, math.radians(tilt_deg), cx, cy)


def curve(pts):
    return smooth_path(pts, 30)


def arrow(pts, head=26, rng=None, spread=28):
    """A curved shaft through pts plus a two-stroke open arrow head."""
    shaft = curve(pts)
    tip = shaft[-1]
    d = shaft[-1] - shaft[-8]
    ang = math.atan2(d[1], d[0])
    heads = []
    for s in (+1, -1):
        a = ang + math.pi + s * math.radians(spread + (rng.normal(0, 4) if rng is not None else 0))
        p2 = tip + np.array([math.cos(a), math.sin(a)]) * head
        heads.append(curve([tuple(p2), tuple(tip)]))
    return [shaft, heads[0], heads[1]]


def polyline(pts):
    return smooth_path(pts, 16)


# ------------------------------------------------------------- stroke physics
def _resample(path, ds=1.0):
    d = np.sqrt(((path[1:] - path[:-1]) ** 2).sum(1))
    s = np.concatenate([[0], np.cumsum(d)])
    L = s[-1]
    if L < 1e-3:
        return np.repeat(path[:1], 2, 0), 0.0
    n = max(2, int(L / ds) + 1)
    u = np.linspace(0, L, n)
    return np.stack([np.interp(u, s, path[:, 0]), np.interp(u, s, path[:, 1])], 1), L


class Stroke:
    def __init__(self, P, W, V, T, nib, rnd):
        self.P, self.W, self.V, self.T, self.nib, self.rnd = P, W, V, T, nib, rnd


def build(paths, h, wmin, wmax, rng, nib_deg=-38.0, px_speed=None, t0=0.0, lift_gap=0.08,
          end_speed=0.35):
    """Simulate a pen moving along each path. Returns (strokes, t_end)."""
    if px_speed is None:
        px_speed = 7.0 * h
    out = []
    t = t0
    acc = 1.0 / (1.2 * h)
    nib = np.array([math.cos(math.radians(nib_deg)), math.sin(math.radians(nib_deg))])
    for path in paths:
        P, L = _resample(np.asarray(path, np.float64), 1.0)
        n = len(P)
        k = max(2, int(h * 0.05))
        tan = np.zeros_like(P)
        tan[1:-1] = P[2:] - P[:-2]
        tan[0], tan[-1] = P[1] - P[0], P[-1] - P[-2]
        ang = np.arctan2(tan[:, 1], tan[:, 0])
        ia, ib = np.clip(np.arange(n) - k, 0, n - 1), np.clip(np.arange(n) + k, 0, n - 1)
        dturn = np.abs((ang[ib] - ang[ia] + np.pi) % (2 * np.pi) - np.pi)
        kappa = dturn / np.maximum(1, ib - ia)
        v = 1.0 / (1.0 + 2.5 * kappa * h)
        v = np.clip(v, 0.06, 1.0)
        v[0] = 0.08
        v[-1] = min(v[-1], end_speed)
        for i in range(1, n):
            v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * acc))
        for i in range(n - 2, -1, -1):
            v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * acc * 1.6))
        W = wmin + (wmax - wmin) * (1 - v) ** 1.2
        dt = 1.0 / (np.maximum(v, 0.05) * px_speed)
        T = t + np.concatenate([[0], np.cumsum(dt[1:])])
        t = T[-1] + lift_gap
        out.append(Stroke(P, W, v, T, nib, rng.random(8)))
    return out, t


def _noise1d(n, period, rng):
    m = int(n / period) + 3
    knots = rng.random(m)
    x = np.arange(n) / period
    i = x.astype(int)
    f = x - i
    f = f * f * (3 - 2 * f)
    return knots[i] * (1 - f) + knots[i + 1] * f


# ------------------------------------------------------------- rasterising
class Masks:
    """Supersampled L masks for one colour group."""

    def __init__(self, size):
        self.size = size
        W, H = size
        self.body = Image.new("L", (W * SS, H * SS), 0)
        self.streak = Image.new("L", (W * SS, H * SS), 0)
        self.core = Image.new("L", (W * SS, H * SS), 0)
        self.spark = Image.new("L", (W * SS, H * SS), 0)
        self.db = ImageDraw.Draw(self.body)
        self.dst = ImageDraw.Draw(self.streak)
        self.dc = ImageDraw.Draw(self.core)
        self.dsp = ImageDraw.Draw(self.spark)

    def arrays(self):
        def a(im):
            return np.asarray(im.reduce(SS), np.float32) / 255.0
        return a(self.body), a(self.streak), a(self.core), a(self.spark)


def raster(masks, strokes, rng, t_end=None, flicker=0.25, pulse=None, core_gain=1.0,
           sparks=True, spark_n=(2, 5), streaks=True, body_level=0.8, dry=1.0,
           streak_gain=1.0):
    """Draw strokes into masks. Returns pen-head (pos, width) if cut by t_end."""
    head = None
    for st in strokes:
        P, W, V, T = st.P, st.W, st.V, st.T
        n = len(P)
        cut = n
        if t_end is not None:
            cut = int(np.searchsorted(T, t_end))
            if cut < 2:
                continue
            if cut < n:
                head = (P[cut - 1], W[cut - 1])
        fl = 1.0 - flicker + flicker * _noise1d(n, 9.0, rng)
        if pulse is not None:
            s = np.arange(n, dtype=np.float32)
            fl = fl * (1.0 + pulse(st, s, n))
        tan = np.zeros_like(P)
        tan[1:-1] = P[2:] - P[:-2]
        tan[0], tan[-1] = P[1] - P[0], P[-1] - P[-2]
        tn = tan / np.maximum(1e-6, np.linalg.norm(tan, axis=1, keepdims=True))
        nib = st.nib
        nrm = np.stack([-tn[:, 1], tn[:, 0]], 1)
        # calligraphic nib: a stroke moving across the nib is wide, along it is narrow
        nibf = 0.3 + 0.7 * np.abs(tn[:, 0] * nib[1] - tn[:, 1] * nib[0])
        We = W * nibf
        # taper the very start / end a little (pen touching down / lifting)
        s_idx = np.arange(n)
        taper = np.clip(s_idx / max(3, min(W.max() * 0.6, n * 0.12)), 0.35, 1) * np.clip((n - 1 - s_idx) / max(3, min(W.max() * 0.9, n * 0.18)), 0.3, 1)
        We = We * taper
        kw = int(max(4, W.max() * 0.9))
        We = np.convolve(np.pad(We, kw, mode="edge"), np.ones(2 * kw + 1) / (2 * kw + 1), mode="valid")
        # dry-brush tail: over the last stretch the solid ribbon fades and splits into filaments
        dry_len = max(4.0, min(n * 0.16, W.max() * 2.2)) * dry
        dryf = np.clip((s_idx - (n - 1 - dry_len)) / max(1.0, dry_len), 0, 1) if dry > 0 else np.zeros(n)
        for i in range(0, cut):
            c = P[i] * SS
            r = max(0.6, We[i] * 0.5 * (1 - 0.35 * dryf[i])) * SS
            masks.db.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r],
                             fill=int(np.clip(255 * body_level * fl[i] * (1 - 0.9 * dryf[i]), 0, 255)))
            rc = max(0.45, We[i] * 0.11 + 0.3) * SS * (1 - 0.6 * dryf[i])
            lv = core_gain * (0.5 + 0.5 * (1 - V[i])) * (0.75 + 0.25 * fl[i]) * (1 - dryf[i])
            masks.dc.ellipse([c[0] - rc, c[1] - rc, c[0] + rc, c[1] + rc],
                             fill=int(np.clip(255 * lv, 0, 255)))
        W = We
        if streaks:
            # light-wand bristles: thin brighter filaments across the ribbon
            nb = 7
            for bi in range(nb):
                u = -0.42 + 0.84 * bi / (nb - 1) + rng.normal(0, 0.04)
                ns = _noise1d(n, 11.0 + 6 * rng.random(), rng)
                end_b = n - int(rng.random() * dry_len * 0.8)
                lim = min(cut, end_b)
                idx = list(range(0, lim, 2))
                pts = [tuple((P[i] + nrm[i] * W[i] * 0.5 * u * (1 + 0.9 * dryf[i])) * SS) for i in idx]
                for k in range(len(pts) - 1):
                    i = idx[k]
                    lv = int(255 * np.clip((0.3 + 0.7 * ns[i]) * fl[i] * streak_gain, 0, 1))
                    masks.dst.line([pts[k], pts[k + 1]], fill=lv, width=max(1, int(SS * 0.9)))
        if sparks and cut == n:
            d = tn[-1]
            k = rng.integers(spark_n[0], spark_n[1] + 1)
            for _ in range(k):
                a = math.atan2(d[1], d[0]) + rng.normal(0, 0.55)
                dist = rng.uniform(2, 14) * (W.max() / 16 + 0.4)
                ln = rng.uniform(2, 6) * (W.max() / 18 + 0.4)
                dv = np.array([math.cos(a), math.sin(a)])
                p0 = P[-1] + dv * dist
                p1 = p0 + dv * ln
                lv = int(255 * rng.uniform(0.5, 1.0))
                masks.dsp.line([tuple(p0 * SS), tuple(p1 * SS)], fill=lv, width=max(1, SS))
            for _ in range(k):
                p = P[-1] + rng.normal(0, 1, 2) * W.max() * 0.8 + d * rng.uniform(0, 18)
                r = rng.uniform(0.5, 1.3) * SS
                masks.dsp.ellipse([p[0] * SS - r, p[1] * SS - r, p[0] * SS + r, p[1] * SS + r],
                                  fill=int(255 * rng.uniform(0.3, 0.9)))
    return head


def compose(base, groups, light_gain=1.0, veil=0.35, extra_add=None, extra_veil=None):
    """base: HxWx3 float (0..1). groups: list of dicts with keys
    masks, color, halo (scale), trail (dx,dy), light (lightmap gain), core_tint.
    Returns composited HxWx3 float."""
    H, Wd = base.shape[:2]
    add = np.zeros_like(base)
    light = np.zeros_like(base)
    veil_m = np.zeros((H, Wd), np.float32)
    for g in groups:
        body, streak, core, spark = g["masks"].arrays()
        if g.get("keep") is not None:
            k = g["keep"]
            body, streak, core = body * k, streak * k, core * k
        if g.get("extra_spark") is not None:
            spark = np.maximum(spark, g["extra_spark"])
        gain = g.get("gain", 1.0)
        body, streak, core = body * gain, streak * gain, core * gain
        col = g.get("color", PINK)
        hs = g.get("halo", 1.0)
        body2 = np.maximum(body, streak * g.get("streak", 0.9))
        # afterglow trail (long-exposure ghosts)
        tr = g.get("trail", (0, 0))
        ghost = np.zeros_like(body)
        if tr != (0, 0):
            for k, a in ((1, 0.30), (2, 0.18), (3, 0.10), (4, 0.05)):
                ghost += a * gblur(shift(body, int(tr[0] * k), int(tr[1] * k)), 1.5 + 1.5 * k)
        halo = (0.55 * gblur(body, 2.5) + 0.38 * gblur(body, 8) + 0.26 * gblur(body, 22)) * hs
        corel = core + 0.5 * gblur(core, 1.6) + spark + 0.6 * gblur(spark, 2.0)
        sparkh = gblur(spark, 4) * 0.8
        # chromatic fringe
        fr = np.clip(gblur(shift(body, 2, 1), 1.2) - body, 0, 1)
        fb = np.clip(gblur(shift(body, -2, -1), 1.2) - body, 0, 1)
        ct = g.get("core_tint", WHITE)
        hot = np.clip((gblur(body, 2.5) - 0.62) / 0.38, 0, 1) * g.get("hot", 0.4)
        add += col[None, None] * (body2 * 1.15 + halo * 0.7 + ghost + sparkh)[..., None]
        add += ct[None, None] * hot[..., None] * 0.6
        add += ct[None, None] * corel[..., None] * 1.1
        add += np.array([1.0, 0.15, 0.25], np.float32) * fr[..., None] * 0.55
        add += np.array([0.15, 0.55, 1.0], np.float32) * fb[..., None] * 0.65
        lm = (gblur(body, 30) * 1.4 + gblur(body, 90) * 1.6) * g.get("light", 1.0)
        light += col[None, None] * lm[..., None]
        veil_m = np.maximum(veil_m, np.clip(gblur(body, 14) * 3.0, 0, 1) * g.get("veil", veil))
    if extra_veil is not None:
        veil_m = np.maximum(veil_m, extra_veil)
    if extra_add is not None:
        add = add + extra_add
    out = base * (1.0 - veil_m[..., None])
    # projected light: multiplicative on the facets (lights the base) + a little fill
    out = out * (1.0 + light * 2.6 * light_gain) + light * 0.035 * light_gain
    out = out + add
    return tonemap(out)


def tonemap(x):
    # bleed overflow into white, soft shoulder
    over = np.clip(x.max(-1, keepdims=True) - 1.0, 0, None)
    x = x + over * 0.12
    k = 0.78
    y = np.where(x < k, x, k + (1 - k) * (1 - np.exp(-(x - k) / (1 - k))))
    return np.clip(y, 0, 1)


def pen_head(img, pos, w, color=PINK, scale=1.0):
    """Add a glowing pen tip with star flare to an HxWx3 float image (in place, additive)."""
    H, Wd = img.shape[:2]
    m = np.zeros((H, Wd), np.float32)
    x, y = int(pos[0]), int(pos[1])
    if 0 <= x < Wd and 0 <= y < H:
        m[y, x] = 1.0
    r1 = gblur(m, 2.0 * scale) * (2 * math.pi * 4 * scale * scale) * 1.6
    r2 = gblur(m, 9 * scale) * (2 * math.pi * 81 * scale * scale) * 0.6
    r3 = gblur(m, 30 * scale) * (2 * math.pi * 900 * scale * scale) * 0.35
    fl = Image.new("L", (Wd, H), 0)
    d = ImageDraw.Draw(fl)
    L1, L2 = 120 * scale, 46 * scale
    for i in range(6):
        a = 1 - i / 6
        d.line([(x - L1 * a, y), (x + L1 * a, y)], fill=int(60 + 120 * (1 - a)), width=1)
    d.line([(x, y - L2), (x, y + L2)], fill=110, width=1)
    fla = gblur(np.asarray(fl, np.float32) / 255.0, 0.8)
    img += WHITE * (r1 * 1.2)[..., None] + color * (r2 + r3)[..., None] + \
        (WHITE * 0.5 + color * 0.5) * fla[..., None] * 0.9
    return img


# ------------------------------------------------------------- base editing
def load(path):
    return np.asarray(Image.open(path).convert("RGB"), np.float32) / 255.0


def save(arr, path):
    Image.fromarray((np.clip(arr, 0, 1) * 255 + 0.5).astype(np.uint8)).save(path)


def inpaint(img, mask, iters=400):
    """Diffusion inpaint (fills mask>0.5 from the surrounding pixels)."""
    ys, xs = np.where(mask > 0.5)
    if len(xs) == 0:
        return img
    pad = 6
    y0, y1 = max(0, ys.min() - pad), min(img.shape[0], ys.max() + pad + 1)
    x0, x1 = max(0, xs.min() - pad), min(img.shape[1], xs.max() + pad + 1)
    sub = img[y0:y1, x0:x1].copy()
    m = mask[y0:y1, x0:x1] > 0.5
    # init with mean of border
    sub[m] = sub[~m].mean(0)
    for it in range(iters):
        b = sub.copy()
        b[1:-1, 1:-1] = (sub[:-2, 1:-1] + sub[2:, 1:-1] + sub[1:-1, :-2] + sub[1:-1, 2:]) * 0.25
        sub[m] = b[m]
    img = img.copy()
    img[y0:y1, x0:x1] = sub
    return img


def dilate(mask, r):
    return (gblur(mask.astype(np.float32), r) > 0.02).astype(np.float32)


def font(size, var="Bold Condensed"):
    f = ImageFont.truetype(FONT_PATH, size)
    try:
        f.set_variation_by_name(var)
    except Exception:
        pass
    return f


def draw_text_rgba(size, xy, text, fnt, fill, anchor="mm"):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(im).text(xy, text, font=fnt, fill=fill, anchor=anchor)
    return im


def over(base, rgba):
    a = np.asarray(rgba, np.float32) / 255.0
    return base * (1 - a[..., 3:4]) + a[..., :3] * a[..., 3:4]


# ------------------------------------------------------------- dissolve
def dissolve_particles(masks_src, rng, progress, drift=(26, -60), n=2600, into=None, sweep=None):
    """Turn a rendered body mask into drifting light particles.
    Returns (eroded body multiplier HxW, particle Masks drawn into `into`)."""
    body, _, _, _ = masks_src.arrays()
    H, W = body.shape
    noise = gblur(rng.random((H, W)).astype(np.float32), 3)
    noise = (noise - noise.min()) / (noise.max() - noise.min() + 1e-6)
    if sweep is not None:  # dissolve runs along the writing direction (left first)
        xx = np.arange(W, dtype=np.float32)[None, :]
        noise = 0.5 * noise + 0.5 * np.clip((xx - sweep[0]) / (sweep[1] - sweep[0]), 0, 1)
    thr = progress
    keep = np.clip((noise - thr) / 0.08, 0, 1)
    ys, xs = np.nonzero(body > 0.3)
    if len(xs):
        idx = rng.choice(len(xs), size=min(n, len(xs)), replace=False)
        for i in idx:
            x, y = xs[i], ys[i]
            nv = noise[y, x]
            if nv > thr + 0.02:
                continue  # still part of the stroke
            age = np.clip((thr - nv) / 0.5, 0, 1)
            dx = drift[0] * age * rng.uniform(0.5, 1.4) + math.sin(y * 0.05 + age * 6) * 8 * age
            dy = drift[1] * age * rng.uniform(0.5, 1.5)
            px, py = (x + dx) * SS, (y + dy) * SS
            r = rng.uniform(0.6, 1.7) * (1 - 0.5 * age) * SS
            lv = int(255 * rng.uniform(0.5, 1.0) * (1 - age * 0.7))
            into.dsp.ellipse([px - r, py - r, px + r, py + r], fill=lv)
            if rng.random() < 0.25:
                into.dsp.line([(px, py), (px - dx * 0.25 * SS / 2, py - dy * 0.25 * SS / 2)],
                              fill=lv // 2, width=1)
    return keep


def brackets(x, y, w, h, rng, arm=0.28, over=10):
    """Four hand-drawn corner brackets (L shapes with overshoot) as light strokes."""
    out = []
    aw, ah = w * arm, h * arm
    j = lambda: rng.normal(0, 2.0)
    corners = [
        [(x + aw, y - 2 + j()), (x - over * 0.3, y + j(), C), (x + j(), y + ah)],
        [(x + w - aw, y + j()), (x + w + over * 0.3, y + 1 + j(), C), (x + w + j(), y + ah)],
        [(x + w + j(), y + h - ah), (x + w + j(), y + h + over * 0.3, C), (x + w - aw, y + h + j())],
        [(x + j(), y + h - ah), (x - 1 + j(), y + h + over * 0.3, C), (x + aw, y + h + 2 + j())],
    ]
    for c in corners:
        out.append(smooth_path(c, 24))
    return out


def inpaint_textured(img, mask, iters=500, shifts=((0, 36), (0, -36), (36, 0), (-36, 0), (0, 72),
                                                    (0, -72), (72, 0), (-72, 0), (50, 50), (-50, -50)),
                     valid=None):
    """Diffusion fill plus high-frequency texture (rain, facet edges) cloned from nearby."""
    low = inpaint(img, mask, iters)
    hf = np.stack([img[..., c] - gblur(img[..., c], 3.0) for c in range(3)], -1)
    m = mask > 0.5
    fill = np.zeros_like(img)
    done = np.zeros(m.shape, bool)
    for dx, dy in shifts:
        bad = m.astype(np.float32) if valid is None else np.maximum(m, ~valid).astype(np.float32)
        src_ok = ~shift(bad, dx, dy).astype(bool)
        src_hf = np.stack([shift(hf[..., c], dx, dy) for c in range(3)], -1)
        take = m & ~done & src_ok
        fill[take] = src_hf[take]
        done |= take
    out = low.copy()
    out[m] = np.clip(low[m] + fill[m], 0, 1)
    return out
