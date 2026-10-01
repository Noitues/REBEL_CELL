"""CIRCUIT BOARD slice family (round 5, slug s_a_circuit).

Pure Pillow + numpy. Every slice is a wedge tile rendered in its own local frame
(wedge pointing up, wheel centre below the tile), then rotated onto the wheel.
Layers per tile: faceted PCB substrate -> copper / pads / vias / SMD chips / silkscreen
(height-shaded, lit) -> emissive neon traces (program behaviour, time t in [0,1) loops)
-> calm plate under the icon -> neon rim -> white glyph + Anton number with dark outline.
"""
import math
import os
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\noitu\Documents\Godot\rebel_cell\.claude\worktrees\art-pass"
OUT = os.path.join(ROOT, "docs", "concepts", "round5_slices", "s_a_circuit")
FONTS = os.path.join(ROOT, "assets", "fonts")
F_NUM = os.path.join(FONTS, "Anton-Regular.ttf")
F_SILK = os.path.join(FONTS, "ShareTechMono-Regular.ttf")
F_SUB = os.path.join(FONTS, "IBMPlexSansCondensed-Medium.ttf")

R_OUT = 360
R_IN = 130


def hexc(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


# name, slice type, colour, glyph, demo value
PROGRAMS = {
    "EXPLOIT": ("ATTACK", "#FF3DA8", "attack", 6),
    "ZERO-DAY": ("CRITICAL", "#FF5AD2", "crit", 12),
    "FIREWALL": ("DEFEND", "#5CE1FF", "defend", 5),
    "SANDBOX": ("SHIELD", "#36F0D0", "shield", 4),
    "PROXY": ("EVADE", "#7BE07B", "evade", 3),
    "PATCH": ("HEAL", "#5CFF9C", "heal", 4),
    "VIRUS": ("AFFLICT", "#C85AFF", "afflict", 3),
    "TROJAN": ("DEPLOY", "#B08CFF", "deploy", 2),
    "NULL": ("MISS", "#6A6A6A", "miss", None),
}
ORDER = ["EXPLOIT", "ZERO-DAY", "FIREWALL", "SANDBOX", "PROXY", "PATCH", "VIRUS", "TROJAN", "NULL"]
MERIDIAN = hexc("#FF8C1A")
WHITE = np.array([1.0, 1.0, 1.0], np.float32)
COPPER = np.array([0.72, 0.43, 0.20], np.float32)
GOLD = np.array([0.88, 0.70, 0.32], np.float32)
INK = (14, 10, 22)


# ----------------------------------------------------------------------------- numpy utils
def _box1d(a, r, axis):
    if r <= 0:
        return a
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(a, pad, mode="edge")
    c = np.cumsum(p, axis=axis, dtype=np.float64)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a, sigma):
    """Approximate gaussian blur (3 box passes), float arrays, 2D or HxWxC."""
    if sigma <= 0.3:
        return a
    w = math.sqrt(4 * sigma * sigma + 1)
    r = max(1, int(round((w - 1) / 2)))
    out = a.astype(np.float32)
    for _ in range(3):
        out = _box1d(out, r, 0)
        out = _box1d(out, r, 1)
    return out


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def L(img):
    return np.asarray(img, np.float32) / 255.0


def tonemap(c):
    k = 0.78
    return np.where(c < k, c, k + (1 - k) * (1 - np.exp(-(c - k) / (1 - k))))


# ----------------------------------------------------------------------------- geometry
class Wedge:
    """One slice tile in its local frame: axis vertical, outward = up."""

    def __init__(self, ticks, ro=R_OUT, ri=R_IN, ss=2, gap=3.0):
        self.ticks = ticks
        self.ss = ss
        self.half = math.radians(6 * ticks)
        self.Ro = ro * ss
        self.Ri = ri * ss
        self.scale = ro / R_OUT * ss          # px per master px
        self.gap = gap * ss
        pad = int(4 * ss)
        hw = self.Ro * math.sin(self.half)
        self.w = int(math.ceil(2 * hw)) + 2 * pad
        self.h = int(math.ceil(self.Ro - self.Ri * math.cos(self.half))) + 2 * pad
        self.cx = self.w / 2.0
        self.cy = pad + self.Ro
        ys, xs = np.mgrid[0:self.h, 0:self.w].astype(np.float32)
        self.X = xs + 0.5
        self.Y = ys + 0.5
        dx = self.X - self.cx
        dy = self.Y - self.cy
        self.rr = np.hypot(dx, dy)
        self.ang = np.arctan2(dx, -dy)
        lat = self.rr * np.sin(self.half - np.abs(self.ang))
        self.d = np.minimum(np.minimum(self.rr - self.Ri, self.Ro - self.rr), lat) - self.gap / 2
        self.mask = np.clip(self.d / ss + 0.5, 0, 1).astype(np.float32)
        self.span = self.Ro - self.Ri
        self.s_field = (self.rr - self.Ri) / self.span

    def u(self, v):
        """master px -> local px"""
        return v * self.scale

    def Rs(self, s):
        return self.Ri + s * self.span

    def P(self, f, s):
        a = -math.pi / 2 + f * self.half
        r = self.Rs(s)
        return (self.cx + r * math.cos(a), self.cy + r * math.sin(a))

    def XY(self, u, s):
        """lateral offset u (local px) from axis, height at radius Rs(s) on the axis"""
        return (self.cx + u, self.cy - self.Rs(s))

    def hw(self, s):
        return self.Rs(s) * math.sin(self.half)

    def chord(self, s):
        return 2 * self.Rs(s) * math.sin(self.half)

    def dist(self, x, y):
        dx, dy = x - self.cx, y - self.cy
        rr = math.hypot(dx, dy)
        a = math.atan2(dx, -dy)
        lat = rr * math.sin(self.half - abs(a))
        return min(rr - self.Ri, self.Ro - rr, lat) - self.gap / 2

    def inside(self, x, y, margin=0.0):
        return self.dist(x, y) >= margin

    def inset_loop(self, off, n_arc=48):
        """closed polygon following the tile border, inset by `off` local px"""
        pts = []
        ro, ri = self.Ro - off, self.Ri + off
        # angular inset for the radial edges at a given radius
        def a_lim(r):
            return self.half - math.asin(min(0.99, (off + self.gap / 2) / r))
        for k in range(n_arc + 1):
            a = -a_lim(ro) + 2 * a_lim(ro) * k / n_arc
            pts.append((self.cx + ro * math.sin(a), self.cy - ro * math.cos(a)))
        for k in range(n_arc + 1):
            a = a_lim(ri) - 2 * a_lim(ri) * k / n_arc
            pts.append((self.cx + ri * math.sin(a), self.cy - ri * math.cos(a)))
        pts.append(pts[0])
        return pts

    def blank(self):
        return Image.new("L", (self.w, self.h), 0)


class Path:
    def __init__(self, pts):
        self.pts = [tuple(p) for p in pts]
        self.cum = [0.0]
        for a, b in zip(self.pts, self.pts[1:]):
            self.cum.append(self.cum[-1] + math.dist(a, b))
        self.length = max(self.cum[-1], 1e-6)

    def at(self, f):
        f = min(max(f, 0.0), 1.0)
        target = f * self.length
        for i in range(1, len(self.cum)):
            if self.cum[i] >= target:
                seg = self.cum[i] - self.cum[i - 1]
                k = 0 if seg <= 0 else (target - self.cum[i - 1]) / seg
                a, b = self.pts[i - 1], self.pts[i]
                return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)
        return self.pts[-1]

    def sub(self, f0, f1):
        f0, f1 = max(0.0, f0), min(1.0, f1)
        if f1 <= f0:
            return []
        out = [self.at(f0)]
        for i, c in enumerate(self.cum):
            if f0 * self.length < c < f1 * self.length:
                out.append(self.pts[i])
        out.append(self.at(f1))
        return out


def line(draw, pts, width, fill=255):
    if len(pts) < 2:
        return
    w = max(1, int(round(width)))
    draw.line(pts, fill=fill, width=w, joint="curve")
    r = w / 2.0
    for p in (pts[0], pts[-1]):
        draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def disc(draw, p, r, fill=255):
    draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=fill)


def ring(draw, p, r, w, fill=255):
    draw.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], outline=fill, width=max(1, int(round(w))))


def packet(draw, path, f, trail, width, peak=255, steps=8):
    """bright head at f with a fading trail behind it"""
    for k in range(steps, 0, -1):
        a = f - trail * k / steps
        b = f - trail * (k - 1) / steps
        seg = path.sub(a, b)
        if len(seg) >= 2:
            line(draw, seg, width, int(peak * (1 - (k - 1) / steps) ** 1.5))
    if 0 <= f <= 1:
        disc(draw, path.at(f), width * 0.9, peak)


DIRS = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in range(0, 360, 45)]


def route(W, rng, start, nseg=3, seg=(10, 40), d0=None, margin=5.0, prefer_up=True):
    """45-degree routed trace that stays inside the wedge."""
    x, y = start
    pts = [(x, y)]
    if d0 is None:
        d0 = rng.choice([5, 6, 7, 6, 2] if prefer_up else range(8))  # 6 = up
    d = d0
    m = W.u(margin)
    for i in range(nseg):
        Lm = W.u(rng.uniform(*seg))
        dx, dy = DIRS[d]
        steps = int(Lm / max(1.0, W.ss))
        nx, ny = x, y
        for _ in range(steps):
            tx, ty = nx + dx * W.ss, ny + dy * W.ss
            if not W.inside(tx, ty, m):
                break
            nx, ny = tx, ty
        if math.dist((nx, ny), (x, y)) < W.u(3):
            break
        x, y = nx, ny
        pts.append((x, y))
        d = (d + rng.choice([-1, 1])) % 8
    return pts


# ----------------------------------------------------------------------------- base board
class Board:
    """Static PCB content + per-program emissive behaviour."""

    name = "BASE"
    hue_sub = 0.12       # how much the program colour tints the substrate
    facet_amt = 1.0
    dead = False

    def __init__(self, W, col, seed=1, lod=0, corp=False):
        self.W = W
        self.col = col
        self.lod = lod
        self.rng = random.Random(seed)
        self.seed = seed
        self.corp = corp
        self.traces = []      # (pts, width_master)
        self.pads = []        # (p, r_master)
        self.vias = []        # (p, r_master)
        self.chips = []       # (x0,y0,x1,y1, pins_axis)
        self.smd = []         # (p, horizontal)
        self.silk_txt = []    # (p, text, size_master)
        self.silk_poly = []   # list of pts
        self.packet_paths = []
        self.build()
        self._base_cache = {}

    # ---- content
    def filler(self, n, seg=(10, 40), nseg=3, width=1.7, keep_out=None, pads=True):
        W, rng = self.W, self.rng
        made = 0
        tries = 0
        while made < n and tries < n * 20:
            tries += 1
            f = rng.uniform(-0.95, 0.95)
            s = rng.uniform(0.02, 0.98)
            p = W.P(f, s)
            if not W.inside(*p, W.u(6)):
                continue
            if keep_out and keep_out(p):
                continue
            pts = route(W, rng, p, nseg=rng.randint(max(1, nseg - 1), nseg + 1), seg=seg)
            if len(pts) < 2:
                continue
            self.traces.append((pts, width))
            if pads:
                self.pads.append((pts[0], 2.6))
                if rng.random() < 0.6:
                    self.vias.append((pts[-1], 2.4))
                else:
                    self.pads.append((pts[-1], 2.4))
            made += 1

    def scatter_smd(self, n, keep_out=None):
        W, rng = self.W, self.rng
        for _ in range(n * 6):
            if n <= 0:
                break
            p = W.P(rng.uniform(-0.85, 0.85), rng.uniform(0.05, 0.95))
            if not W.inside(*p, W.u(8)) or (keep_out and keep_out(p)):
                continue
            self.smd.append((p, rng.random() < 0.5))
            n -= 1

    def chip(self, cx, cy, wm, hm, pins=4, label=None):
        W = self.W
        w, h = W.u(wm), W.u(hm)
        self.chips.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, pins))
        if label:
            self.silk_txt.append(((cx, cy + h / 2 + W.u(5)), label, 6))

    def build(self):
        self.filler(14)

    def icon_centre(self):
        return self.W.P(0, 0.6)

    def keep_icon(self, scale=1.0):
        W = self.W
        gx, gy = self.icon_centre()
        ax = W.chord(0.6) * 0.22 * scale
        ay = W.span * 0.26 * scale

        def ko(p):
            return ((p[0] - gx) / ax) ** 2 + ((p[1] - gy) / ay) ** 2 < 1.0
        return ko

    # ---- static raster
    def static_masks(self):
        W = self.W
        cu, pad, hole, chipm, pin, silk = (W.blank() for _ in range(6))
        dc, dp, dh, dch, dpi, ds = (ImageDraw.Draw(i) for i in (cu, pad, hole, chipm, pin, silk))
        for pts, wd in self.traces:
            line(dc, pts, W.u(wd))
        for p, r in self.pads:
            disc(dp, p, W.u(r))
        for p, r in self.vias:
            disc(dp, p, W.u(r))
            disc(dh, p, W.u(r * 0.45))
        for (x0, y0, x1, y1, pins) in self.chips:
            dch.rectangle([x0, y0, x1, y1], fill=255)
            n = pins
            pl = W.u(3.2)
            pw = W.u(1.6)
            for k in range(n):
                yy = y0 + (y1 - y0) * (k + 0.5) / n
                dpi.rectangle([x0 - pl, yy - pw / 2, x0, yy + pw / 2], fill=255)
                dpi.rectangle([x1, yy - pw / 2, x1 + pl, yy + pw / 2], fill=255)
            ds.rectangle([x0 - W.u(5), y0 - W.u(3), x1 + W.u(5), y1 + W.u(3)], outline=150, width=max(1, int(W.u(0.8))))
            disc(ds, (x0 + W.u(2.2), y0 + W.u(2.2)), W.u(1.0), 200)
        for p, horiz in self.smd:
            a, b = (W.u(3.4), W.u(1.7)) if horiz else (W.u(1.7), W.u(3.4))
            dch.rectangle([p[0] - a, p[1] - b, p[0] + a, p[1] + b], fill=170)
            if horiz:
                dpi.rectangle([p[0] - a - W.u(1), p[1] - b, p[0] - a + W.u(1.4), p[1] + b], fill=255)
                dpi.rectangle([p[0] + a - W.u(1.4), p[1] - b, p[0] + a + W.u(1), p[1] + b], fill=255)
            else:
                dpi.rectangle([p[0] - a, p[1] - b - W.u(1), p[0] + a, p[1] - b + W.u(1.4)], fill=255)
                dpi.rectangle([p[0] - a, p[1] + b - W.u(1.4), p[0] + a, p[1] + b + W.u(1)], fill=255)
        for pts in self.silk_poly:
            ds.line(pts, fill=170, width=max(1, int(W.u(0.8))))
        for p, txt, sz in self.silk_txt:
            if self.lod:
                continue
            fnt = ImageFont.truetype(F_SILK, max(6, int(W.u(sz))))
            ds.text(p, txt, font=fnt, fill=170, anchor="mm")
        self.extra_static(dc, dp, dh, dch, dpi, ds)
        return [L(i) for i in (cu, pad, hole, chipm, pin, silk)]

    def extra_static(self, dc, dp, dh, dch, dpi, ds):
        pass

    def substrate(self):
        W = self.W
        rng = random.Random(self.seed * 7 + 3)
        img = Image.new("L", (W.w, W.h), 128)
        dr = ImageDraw.Draw(img)
        step = W.u(26)
        cols = int(W.w / step) + 3
        rows = int(W.h / step) + 3
        grid = [[(i * step - step + rng.uniform(-0.38, 0.38) * step,
                  j * step - step + rng.uniform(-0.38, 0.38) * step) for i in range(cols)] for j in range(rows)]
        for j in range(rows - 1):
            for i in range(cols - 1):
                a, b, c, d = grid[j][i], grid[j][i + 1], grid[j + 1][i], grid[j + 1][i + 1]
                dr.polygon([a, b, d], fill=int(128 + rng.uniform(-30, 30)))
                dr.polygon([a, d, c], fill=int(128 + rng.uniform(-30, 30)))
        fac = (L(img) - 0.5) * 2 * self.facet_amt
        nrng = np.random.default_rng(self.seed)
        weave = blur(nrng.standard_normal((W.h, W.w)).astype(np.float32), 0.7 * W.ss) * 0.5
        base = np.array([0.060, 0.048, 0.080], np.float32) + self.col * self.hue_sub
        lum = 1.0 + 0.26 * fac[..., None] + 0.05 * weave[..., None]
        sub = base[None, None, :] * lum
        # ~12% copper-tone facets as on the MODEM plate
        cop = (fac > 0.62).astype(np.float32)[..., None] * 0.35
        sub = sub * (1 - cop) + (base * 0.6 + COPPER * 0.05)[None, None, :] * cop * lum
        return sub

    # ---- shading
    def shaded_base(self, light_rot=0.0):
        key = round(light_rot, 3)
        if key in self._base_cache:
            return self._base_cache[key]
        W = self.W
        cu, pad, hole, chipm, pin, silk = self.static_masks()
        self._masks = (cu, pad, hole, chipm, pin, silk)
        sub = self.substrate()
        # bevel height from the tile border, plus embossed features
        bev = smooth(0, W.u(9), W.d)
        H = bev * 3.0 + blur(cu, 0.6 * W.ss) * 0.9 + blur(pad, 0.6 * W.ss) * 1.2 + blur(chipm, 0.8 * W.ss) * 2.0 + pin * 0.8 - hole * 0.8
        gy, gx = np.gradient(H)
        k = 1.4 / W.ss
        nx, ny, nz = -gx * k, -gy * k, np.ones_like(H)
        nn = np.sqrt(nx * nx + ny * ny + nz * nz)
        nx, ny, nz = nx / nn, ny / nn, nz / nn
        a = math.radians(-135) - light_rot  # top-left light in world, counter-rotated into the tile
        lx, ly, lz = math.cos(a) * 0.62, math.sin(a) * 0.62, 0.78
        ndl = nx * lx + ny * ly + nz * lz
        shade = np.clip(1.0 + 1.6 * (ndl - lz), 0.35, 1.8)
        hx, hy, hz = lx, ly, lz + 1.0
        hn = math.sqrt(hx * hx + hy * hy + hz * hz)
        spec = np.clip((nx * hx + ny * hy + nz * hz) / hn, 0, 1) ** 36

        if self.dead:
            cu_col = np.array([0.20, 0.22, 0.19], np.float32)
            pad_col = np.array([0.36, 0.36, 0.32], np.float32)
        elif self.corp:
            cu_col = COPPER * 0.42 + MERIDIAN * 0.08
            pad_col = GOLD * 0.9
        else:
            cu_col = COPPER * 0.36 + self.col * 0.10
            pad_col = GOLD * 0.85
        rgb = sub.copy()
        m = cu[..., None]
        rgb = rgb * (1 - m) + cu_col[None, None, :] * m
        m = pad[..., None]
        rgb = rgb * (1 - m) + pad_col[None, None, :] * m
        m = hole[..., None]
        rgb = rgb * (1 - m) + np.array([0.01, 0.01, 0.015])[None, None, :] * m
        m = chipm[..., None]
        chip_col = np.array([0.055, 0.055, 0.065], np.float32) if not self.corp else np.array([0.08, 0.07, 0.065], np.float32)
        rgb = rgb * (1 - m) + chip_col[None, None, :] * m
        m = pin[..., None]
        rgb = rgb * (1 - m) + np.array([0.62, 0.62, 0.64])[None, None, :] * m
        silk_col = np.array([0.80, 0.80, 0.76], np.float32) * (0.35 if self.dead else 0.55)
        m = (silk * 0.75)[..., None]
        rgb = rgb * (1 - m) + silk_col[None, None, :] * m
        metal = np.clip(pad + pin + cu * 0.4, 0, 1)
        rgb = rgb * shade[..., None] + (spec * metal * 0.9)[..., None] * np.array([1.0, 0.92, 0.75])
        self._base_cache[key] = rgb.astype(np.float32)
        return self._base_cache[key]

    # ---- behaviour
    def idle_packets(self, t, draw, n=3, peak=170):
        W = self.W
        for i, pth in enumerate(self.packet_paths[:n]):
            f = (t * (1.0 + 0.3 * i) + i * 0.37) % 1.0
            packet(draw, pth, f * 1.3 - 0.15, 0.35, W.u(1.8), peak)

    def emit(self, t):
        """list of (mask float HxW, rgb, gain)"""
        return []

    def post(self, rgb, t):
        return rgb

    def rim_col(self):
        return self.col

    def rim_gain(self, t):
        return 1.0


# ----------------------------------------------------------------------------- glyphs
def glyph_masks(kind, size):
    """white mask + ink detail mask for a glyph of `size` px (box), square images."""
    S = int(size * 1.5) + 4
    c = S / 2.0
    r = size / 2.0
    wm = Image.new("L", (S, S), 0)
    im = Image.new("L", (S, S), 0)
    dw = ImageDraw.Draw(wm)
    di = ImageDraw.Draw(im)

    def P(x, y):
        return (c + x * r, c + y * r)

    if kind == "attack":
        dw.polygon([P(-0.2, 0.32), P(-0.2, -0.5), P(0, -1.0), P(0.2, -0.5), P(0.2, 0.32)], fill=255)
        dw.rectangle([P(-0.6, 0.3), P(0.6, 0.48)], fill=255)
        dw.rectangle([P(-0.13, 0.48), P(0.13, 0.84)], fill=255)
        disc(dw, P(0, 0.9), r * 0.15)
        di.line([P(0, -0.72), P(0, 0.22)], fill=255, width=max(1, int(r * 0.08)))
    elif kind == "crit":
        pts = []
        for k in range(16):
            rr = 1.0 if k % 2 == 0 else 0.42
            a = 2 * math.pi * k / 16 - math.pi / 2
            pts.append(P(math.cos(a) * rr, math.sin(a) * rr))
        dw.polygon(pts, fill=255)
    elif kind == "defend":
        dw.polygon([P(-0.78, -0.72), P(0, -0.95), P(0.78, -0.72), P(0.78, 0.05), P(0, 0.98), P(-0.78, 0.05)], fill=255)
        di.line([P(0, -0.68), P(0, 0.62)], fill=255, width=max(1, int(r * 0.12)))
    elif kind == "shield":
        pts = [P(math.cos(2 * math.pi * k / 6 - math.pi / 2) * 0.98, math.sin(2 * math.pi * k / 6 - math.pi / 2) * 0.98) for k in range(6)]
        dw.polygon(pts, fill=255)
        di.rectangle([P(-0.36, -0.36), P(0.36, 0.36)], outline=255, width=max(1, int(r * 0.15)))
    elif kind == "evade":
        w = max(2, int(r * 0.32))
        for dx in (-0.42, 0.28):
            dw.line([P(dx - 0.3, -0.7), P(dx + 0.25, 0), P(dx - 0.3, 0.7)], fill=255, width=w, joint="curve")
    elif kind == "heal":
        t = 0.3
        dw.rectangle([P(-t, -0.9), P(t, 0.9)], fill=255)
        dw.rectangle([P(-0.9, -t), P(0.9, t)], fill=255)
    elif kind == "afflict":
        pts = [P(0, -1.0)]
        for k in range(17):
            a = -math.pi * 0.17 + math.pi * 1.34 * k / 16
            pts.append(P(math.cos(a) * 0.62, 0.3 + math.sin(a) * 0.62))
        dw.polygon(pts, fill=255)
        disc(di, P(-0.2, 0.32), r * 0.11)
        disc(di, P(0.2, 0.32), r * 0.11)
    elif kind == "deploy":
        w = max(2, int(r * 0.2))
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            dw.line([P(0, 0), P(sx * 0.62, sy * 0.55)], fill=255, width=w)
            dw.ellipse([P(sx * 0.62 - 0.36, sy * 0.55 - 0.14), P(sx * 0.62 + 0.36, sy * 0.55 + 0.14)], fill=255)
        dw.rounded_rectangle([P(-0.34, -0.3), P(0.34, 0.34)], radius=r * 0.12, fill=255)
        disc(di, P(0, 0.02), r * 0.11)
    elif kind == "miss":
        dw.ellipse([P(-0.72, -0.72), P(0.72, 0.72)], outline=255, width=max(2, int(r * 0.26)))
        dw.line([P(-0.85, 0.85), P(0.85, -0.85)], fill=255, width=max(2, int(r * 0.24)))
    elif kind == "crane":
        w = max(2, int(r * 0.2))
        dw.line([P(-0.6, 0.95), P(-0.6, -0.8), P(0.85, -0.8)], fill=255, width=w)
        dw.line([P(0.55, -0.8), P(0.55, 0.0)], fill=255, width=max(1, w // 2))
        dw.rectangle([P(0.3, 0.0), P(0.8, 0.35)], outline=255, width=max(1, w // 2))
        dw.line([P(-0.95, 0.95), P(-0.25, 0.95)], fill=255, width=w)
    return L(wm), L(im)


def dilate(m, rad):
    if rad <= 0:
        return m
    b = blur(m, rad * 0.6)
    return np.clip((b - 0.015) / 0.05, 0, 1)


def draw_icon_layer(W, kind, value, scale=1.0, layout=None):
    """RGBA float layer (H,W,4) with the glyph and number, upright in the tile frame."""
    ss = W.ss
    gc = W.P(0, 0.6)
    chord = W.chord(0.6)
    gsize = chord * 0.37 * scale
    gsize = min(gsize, W.span * 0.32 * scale)
    nh = gsize * 1.05          # number digit height (same as glyph or larger)
    out_w = max(2.0, gsize * 0.12)
    beside = layout == "beside" or (layout is None and W.ticks >= 5)
    layer = np.zeros((W.h, W.w, 4), np.float32)

    txt = None if value is None else str(value)
    # number raster
    num_img = None
    if txt:
        fs = int(nh / 0.88)   # Anton digits are 0.88 em tall
        fnt = ImageFont.truetype(F_NUM, fs)
        sw = max(1, int(round(out_w)))
        bb = ImageDraw.Draw(Image.new("L", (4, 4))).textbbox((0, 0), txt, font=fnt, stroke_width=sw)
        tw, th = bb[2] - bb[0] + 4 * sw, bb[3] - bb[1] + 4 * sw
        fill = Image.new("L", (tw, th), 0)
        strk = Image.new("L", (tw, th), 0)
        ImageDraw.Draw(strk).text((tw / 2, th / 2), txt, font=fnt, anchor="mm", fill=255, stroke_width=sw, stroke_fill=255)
        ImageDraw.Draw(fill).text((tw / 2, th / 2), txt, font=fnt, anchor="mm", fill=255)
        bx = strk.getbbox()
        fill, strk = fill.crop(bx), strk.crop(bx)   # centre on the inked digits, not the font box
        num_img = (L(fill), L(strk))
        num_w = fill.width - 2 * sw
    if kind is None:
        return layer
    gw, gi = glyph_masks(kind, gsize)
    go = np.clip(dilate(gw, out_w), 0, 1)

    if txt is None:
        g_pos = gc
        n_pos = None
    elif beside:
        total = gsize + gsize * 0.18 + num_w
        g_pos = (gc[0] - total / 2 + gsize / 2, gc[1])
        n_pos = (gc[0] + total / 2 - num_w / 2, gc[1])
    else:
        total = gsize + gsize * 0.16 + nh
        g_pos = (gc[0], gc[1] - total / 2 + gsize / 2)
        n_pos = (gc[0], gc[1] + total / 2 - nh / 2)

    def stamp(arr_fill, arr_out, arr_ink, pos):
        hgt, wid = arr_fill.shape
        x0 = int(round(pos[0] - wid / 2))
        y0 = int(round(pos[1] - hgt / 2))
        xs0, ys0 = max(0, x0), max(0, y0)
        xs1, ys1 = min(W.w, x0 + wid), min(W.h, y0 + hgt)
        if xs1 <= xs0 or ys1 <= ys0:
            return
        sl = (slice(ys0, ys1), slice(xs0, xs1))
        a = (slice(ys0 - y0, ys1 - y0), slice(xs0 - x0, xs1 - x0))
        f = arr_fill[a]
        o = arr_out[a]
        # soft drop shadow
        shadow = blur(arr_out, 2.5 * ss)[a] * 0.55
        sh = np.zeros_like(layer[..., 3])
        sh[sl] = shadow
        sh = np.roll(np.roll(sh, int(1.5 * ss), 0), int(1.0 * ss), 1)
        lay_a = layer[..., 3]
        layer[..., :3] *= (1 - sh[..., None])
        layer[..., 3] = lay_a + sh * (1 - lay_a)
        ink = np.array(INK, np.float32) / 255
        reg = layer[sl]
        reg[..., :3] = reg[..., :3] * (1 - o[..., None]) + ink * o[..., None]
        reg[..., 3] = reg[..., 3] + o * (1 - reg[..., 3])
        reg[..., :3] = reg[..., :3] * (1 - f[..., None]) + 0.98 * f[..., None]
        if arr_ink is not None:
            k = arr_ink[a] * f
            reg[..., :3] = reg[..., :3] * (1 - k[..., None]) + ink * k[..., None]
        layer[sl] = reg

    stamp(gw, go, gi, g_pos)
    if num_img is not None:
        stamp(num_img[0], num_img[1], None, n_pos)
    return layer


# ----------------------------------------------------------------------------- tile render
def render_tile(board, t=0.0, light_rot=0.0, value="auto", kind="auto", icon=True,
                icon_scale=1.0, calm=0.55, out_rgba=True):
    W = board.W
    rgb = board.shaded_base(light_rot).copy()
    E_tot = np.zeros((W.h, W.w, 3), np.float32)
    core = np.zeros((W.h, W.w), np.float32)
    for m, col, gain in board.emit(t):
        if m is None:
            continue
        E_tot += m[..., None] * col[None, None, :] * gain
        core += m * gain
    if E_tot.any():
        g1 = blur(E_tot, 2.2 * W.ss)
        g2 = blur(E_tot, 8.0 * W.ss)
        rgb = rgb + E_tot * 1.25 + g1 * 0.9 + g2 * 0.55
        rgb = rgb + (np.clip(core - 0.55, 0, 2) * 0.9)[..., None]  # white-hot cores
    rgb = board.post(rgb, t)
    # calm plate under the icon
    if icon and calm > 0:
        gx, gy = board.icon_centre()
        ax = W.chord(0.6) * 0.36 * icon_scale
        ay = W.span * 0.36 * icon_scale
        if W.ticks >= 5:
            ax *= 1.25
        g = np.exp(-(((W.X - gx) / ax) ** 2 + ((W.Y - gy) / ay) ** 2) ** 1.4)
        rgb = rgb * (1 - calm * g)[..., None]
    # neon rim
    rc = board.rim_col()
    rg = board.rim_gain(t)
    band = smooth(0, W.u(0.6), W.d) * (1 - smooth(W.u(1.6), W.u(2.6), W.d))
    inner = np.exp(-np.clip(W.d, 0, None) / W.u(5)) * (W.d > 0)
    rgb = rgb * (1 - 0.6 * band[..., None]) + band[..., None] * (rc * 1.4 + 0.3) * rg + inner[..., None] * rc * 0.32 * rg
    rgb = tonemap(np.clip(rgb, 0, 4))
    alpha = W.mask.copy()
    if icon:
        k = PROGRAM_KIND(board) if kind == "auto" else kind
        v = board_value(board) if value == "auto" else value
        lay = draw_icon_layer(W, k, v, icon_scale)
        a = lay[..., 3:4]
        rgb = rgb * (1 - a) + lay[..., :3] * a
    out = np.dstack([np.clip(rgb, 0, 1), alpha])
    if not out_rgba:
        return out
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def PROGRAM_KIND(board):
    return getattr(board, "glyph", None)


def board_value(board):
    return getattr(board, "value", None)


# ----------------------------------------------------------------------------- program boards
class Exploit(Board):
    def build(self):
        W, rng = self.W, self.rng
        self.breach = W.P(0, 0.93)
        bx, by = self.breach
        self.paths = []
        starts = [(-0.92, 0.10), (-0.55, 0.0), (0.55, 0.0), (0.92, 0.10), (-0.95, 0.5), (0.95, 0.5), (-0.25, 0.0), (0.25, 0.0)]
        for f, s in starts:
            p0 = W.P(f, s + 0.04)
            # rise straight, then a sharp diagonal straight to the breach
            rise = W.u(rng.uniform(8, 30))
            p1 = (p0[0], p0[1] - rise)
            pts = [p0, p1, (bx + (p1[0] - bx) * 0.06, by + (p1[1] - by) * 0.06)]
            self.paths.append(Path(pts))
            self.traces.append((pts, 1.9))
            self.pads.append((p0, 2.8))
        self.vias.append((self.breach, 4.0))
        self.filler(12, keep_out=self.keep_icon(1.0))
        self.scatter_smd(3, keep_out=self.keep_icon(1.0))
        self.silk_txt.append((W.P(0.55, 0.86), "BRK", 6))
        for pts, _ in self.traces[len(starts):]:
            self.packet_paths.append(Path(pts))

    def emit(self, t):
        W = self.W
        m = W.blank()
        d = ImageDraw.Draw(m)
        for i, pth in enumerate(self.paths):
            line(d, pth.pts, W.u(1.9), 90)
        for i, pth in enumerate(self.paths):
            f = ((t * 2 + i * 0.13) % 1.0) ** 1.6       # accelerate into the breach
            packet(d, pth, f, 0.45, W.u(2.4), 255)
        self.idle_packets(t, d, 2, 110)
        out = [(L(m), self.col, 1.0)]
        # spark: twice a loop, rays from the breach
        sp = W.blank()
        ds = ImageDraw.Draw(sp)
        ph = (t * 2) % 1.0
        burst = max(0.0, 1 - ph / 0.35) if ph < 0.35 else 0.0
        bx, by = self.breach
        rng = random.Random(int(t * 2) + 11)
        if burst > 0:
            for k in range(11):
                a = rng.uniform(0, 2 * math.pi)
                ln = W.u(rng.uniform(8, 26)) * (0.5 + (1 - burst))
                ds.line([(bx, by), (bx + math.cos(a) * ln, by + math.sin(a) * ln)], fill=int(255 * burst), width=max(1, int(W.u(1.1))))
            disc(ds, (bx, by), W.u(5) * burst + W.u(2), int(255 * burst))
        disc(ds, (bx, by), W.u(2.2), 200)
        out.append((L(sp), np.array([1.0, 0.75, 0.9], np.float32), 1.6))
        self._burst = burst
        return out

    def post(self, rgb, t):
        b = getattr(self, "_burst", 0.0)
        if b > 0.25:  # glitch: tear a few rows sideways on the breach frame
            rng = np.random.default_rng(int(t * 1000))
            for _ in range(3):
                y0 = int(rng.uniform(0, self.W.h - 10))
                hgt = int(self.W.u(rng.uniform(2, 6)))
                rgb[y0:y0 + hgt] = np.roll(rgb[y0:y0 + hgt], int(self.W.u(rng.uniform(-5, 5))), 1)
        return rgb


class ZeroDay(Board):
    def build(self):
        W, rng = self.W, self.rng
        cx, cy = W.P(0, 0.15)
        self.cc = (cx, cy)
        self.chip(cx, cy, 30, 22, pins=4)
        self.silk_txt.append(((cx, cy - W.u(17)), "0DAY", 6))
        self.paths = []
        x0, y0, x1, y1, _ = self.chips[0]
        for k in range(4):
            yy = y0 + (y1 - y0) * (k + 0.5) / 4
            for side in (-1, 1):
                sx = x1 + W.u(3) if side > 0 else x0 - W.u(3)
                pts = [(sx, yy)]
                x, y = sx, yy
                # run out sideways, then 45 up, then straight up toward the rim
                out = W.u(4 + 5 * k)
                x += side * out
                pts.append((x, y))
                up = W.u(10 + 6 * k)
                x += side * up
                y -= up
                pts.append((x, y))
                # climb near the edge
                for _ in range(400):
                    if not W.inside(x + side * W.ss, y - W.ss, W.u(6 + 4 * (3 - k))):
                        break
                    x += side * W.ss * 0.35
                    y -= W.ss
                pts.append((x, y))
                yy2 = y
                while W.inside(x, y - W.ss, W.u(5)):
                    y -= W.ss
                pts.append((x, y))
                self.paths.append(Path(pts))
                self.traces.append((pts, 1.6))
                self.pads.append((pts[-1], 2.4))
        self.filler(10, keep_out=self.keep_icon(1.0))

    def emit(self, t):
        W = self.W
        m = W.blank()
        d = ImageDraw.Draw(m)
        # rare cascade: once per loop
        c = (t - 0.45) / 0.4
        if 0 <= c <= 1.15:
            for i, pth in enumerate(self.paths):
                f = c * 1.15 - (i % 4) * 0.05
                fade = 1.0 if c < 0.85 else max(0.0, 1 - (c - 0.85) / 0.3)
                seg = pth.sub(0, min(1, f))
                if len(seg) >= 2:
                    line(d, seg, W.u(2.0), int(235 * fade))
                if 0 < f < 1:
                    disc(d, pth.at(f), W.u(2.6), 255)
                elif f >= 1:
                    disc(d, pth.pts[-1], W.u(3.0), int(255 * fade))
        out = [(L(m), self.col, 1.0)]
        # the white-hot core, always on, flickering
        core = W.blank()
        dc = ImageDraw.Draw(core)
        fl = 0.8 + 0.2 * math.sin(t * 2 * math.pi * 3) + (0.25 if 0.45 < t < 0.6 else 0)
        cx, cy = self.cc
        disc(dc, (cx, cy), W.u(7.5), int(min(255, 140 * fl)))
        disc(dc, (cx, cy), W.u(4.0), 255)
        out.append((L(core), np.array([1.0, 0.55, 0.9], np.float32), 1.5 * fl))
        return out

    def rim_gain(self, t):
        c = (t - 0.45) / 0.4
        return 1.0 + (1.2 if 0.75 < c < 1.0 else 0.0)


class Firewall(Board):
    def build(self):
        W = self.W
        pitch = W.u(6.5)
        hwmax = W.hw(1.0)
        n = int(hwmax / pitch)
        self.lanes = []
        brick = W.u(26)
        for i in range(-n, n + 1):
            x = W.cx + i * pitch
            pts = [(x, W.cy - W.Ro), (x, W.cy - W.Ri * math.cos(W.half) + W.u(4))]
            self.traces.append((pts, 1.6))
            self.lanes.append(x)
        # staggered via pads: a brick wall of traces
        row = 0
        y = W.cy - W.Ro + W.u(10)
        while y < W.cy - W.Ri * 0.95:
            off = (row % 2) * 2
            for i in range(-n + off, n + 1, 4):
                x = W.cx + i * pitch
                if W.inside(x, y, W.u(5)):
                    self.pads.append(((x, y), 2.2))
            y += brick / 2
            row += 1

    def emit(self, t):
        W = self.W
        m = W.blank()
        d = ImageDraw.Draw(m)
        for pts, _ in self.traces:
            line(d, pts, W.u(1.4), 105)
        base = L(m)
        # scanning bar sweeping outward (radial)
        sbar = (t * 1.0) % 1.0
        s = W.s_field
        bar = np.exp(-((s - (sbar * 1.3 - 0.15)) / 0.06) ** 2)
        lit = base * (1 + 2.8 * bar)
        # heat shimmer: per-row sideways wobble
        rows = np.arange(W.h, dtype=np.float32)
        off = (np.sin(rows / W.u(7) + t * 2 * math.pi * 2) * W.u(1.3) * (0.4 + 0.6 * (1 - s.mean(axis=1)))).astype(np.int32)
        idx = (np.arange(W.w)[None, :] - off[:, None]) % W.w
        lit = np.take_along_axis(lit, idx, axis=1)
        out = [(lit, self.col, 1.0), (bar * 0.25 * W.mask, np.array([0.7, 0.95, 1.0], np.float32), 1.0)]
        return out


class Sandbox(Board):
    def build(self):
        W = self.W
        self.ring_pts = W.inset_loop(W.u(7))
        self.ring = Path(self.ring_pts)
        n = int(self.ring.length / W.u(13))
        self.stitch = [self.ring.at(k / n) for k in range(n)]
        for p in self.stitch:
            self.vias.append((p, 2.0))
        self.silk_txt.append((W.P(-0.6, 0.06), "GND", 6))

    def extra_static(self, dc, dp, dh, dch, dpi, ds):
        W = self.W
        line(dc, self.ring_pts, W.u(2.2))
        # ground plane: hatched pour inside the guard ring
        hatch = Image.new("L", (W.w, W.h), 0)
        dhh = ImageDraw.Draw(hatch)
        step = W.u(7)
        k = -W.h
        while k < W.w + W.h:
            dhh.line([(k, 0), (k + W.h, W.h)], fill=255, width=max(1, int(W.u(1.0))))
            dhh.line([(k + W.h, 0), (k, W.h)], fill=255, width=max(1, int(W.u(1.0))))
            k += step
        hm = L(hatch) * (self.W.d > W.u(12))
        self.hatch = hm
        dc.bitmap((0, 0), Image.fromarray((hm * 255).astype(np.uint8)), fill=255)

    def emit(self, t):
        W = self.W
        m = W.blank()
        d = ImageDraw.Draw(m)
        line(d, self.ring_pts, W.u(2.0), 170)
        ph = t % 1.0
        # stitching vias blink in sequence around the ring
        n = len(self.stitch)
        for i, p in enumerate(self.stitch):
            v = max(0.0, 1 - abs(((i / n) - ph + 0.5) % 1.0 - 0.5) / 0.12)
            if v > 0:
                disc(d, p, W.u(2.4), int(255 * v))
        out = [(L(m), self.col, 1.0)]
        # containment pulse: a wave travelling inward across the ground plane
        depth = W.d / W.u(70)
        p = (t * 1.0) % 1.0
        wave = np.exp(-((depth - p * 1.2) / 0.08) ** 2) * (1 - p)
        out.append((self.hatch * wave * 0.9, self.col, 1.0))
        return out

    def rim_gain(self, t):
        return 1.0 + 0.6 * max(0.0, 1 - (t % 1.0) / 0.15)


class Proxy(Board):
    def build(self):
        W, rng = self.W, self.rng
        self.via = W.P(0, 0.91)
        vx, vy = self.via
        self.vias.append((self.via, 4.4))
        self.paths = []
        for side in (-1, 1):
            for lane in (0, 1):
                f_side = side * (0.52 + 0.26 * lane)
                p0 = W.P(side * (0.12 + 0.12 * lane), 0.02)
                p1 = (p0[0], p0[1] - W.u(12))
                p2 = W.P(f_side, 0.22)
                p3 = W.P(f_side, 0.80)
                rad = W.u(11 + 6 * lane)
                p4 = (vx + side * rad, vy + rad * 0.3)
                p5 = (vx + side * rad * 0.7, vy - rad * 0.7)
                p6 = (vx + side * W.u(3) * (1 + lane), W.cy - W.Ro + W.u(3))
                pts = [p0, p1, p2, p3, p4, p5, p6]
                self.paths.append(Path(pts))
                self.traces.append((pts, 1.7))
                self.pads.append((p0, 2.6))
        # the dead direct route: dashed silkscreen up the axis
        a = W.P(0, 0.05)
        b = (vx, vy + W.u(8))
        n = 12
        for k in range(n):
            if k % 2 == 0:
                self.silk_poly.append([(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n),
                                       (a[0] + (b[0] - a[0]) * (k + 1) / n, a[1] + (b[1] - a[1]) * (k + 1) / n)])
        self.silk_txt.append(((vx + W.u(18), vy + W.u(2)), "X", 7))
        self.filler(9, keep_out=self.keep_icon(1.2))

    def emit(self, t):
        W = self.W
        m = W.blank()
        d = ImageDraw.Draw(m)
        for pth in self.paths:
            line(d, pth.pts, W.u(1.5), 70)
        g = W.blank()
        dg = ImageDraw.Draw(g)
        for i, pth in enumerate(self.paths):
            f = (t * 2 + i * 0.25) % 1.0
            packet(d, pth, f, 0.3, W.u(2.4), 255)
            # slippery: a faint ghost lagging behind, offset sideways
            gp = pth.at(max(0, f - 0.12))
            disc(dg, (gp[0] + W.u(2.5), gp[1]), W.u(2.0), 110)
        vx, vy = self.via
        ring(d, (vx, vy), W.u(7.5), W.u(1.4), int(140 + 110 * abs(math.sin(t * 4 * math.pi))))
        return [(L(m), self.col, 1.0), (L(g), np.array([0.6, 1.0, 0.85], np.float32), 0.8)]


class Patch(Board):
    def build(self):
        W = self.W
        self.paths = []
        self.bridges = []
        for side in (-1, 1):
            f = side * 0.66
            pts = [W.P(side * 0.2, 0.02), W.P(side * 0.2, 0.08), W.P(f, 0.28), W.P(f, 0.97)]
            pth = Path(pts)
            # break the copper around 82% along
            gap0, gap1 = 0.74, 0.80
            self.traces.append((pth.sub(0, gap0), 1.9))
            self.traces.append((pth.sub(gap1, 1), 1.9))
            self.pads.append((pts[0], 2.6))
            self.pads.append((pts[-1], 2.6))
            self.paths.append(pth)
            self.bridges.append(pth.at((gap0 + gap1) / 2))
        self.filler(11, keep_out=self.keep_icon(1.0))
        self.scatter_smd(2, keep_out=self.keep_icon(1.0))
        for b in self.bridges:
            self.silk_txt.append(((b[0], b[1] + self.W.u(12)), "+", 9))

    def emit(self, t):
        W = self.W
        sold = W.blank()
        ds = ImageDraw.Draw(sold)
        form = min(1.0, t / 0.22)
        for b in self.bridges:
            r = W.u(2.0 + 3.0 * form)
            ds.ellipse([b[0] - r * 0.8, b[1] - r, b[0] + r * 0.8, b[1] + r], fill=255)
        self._sold = L(sold)
        m = W.blank()
        d = ImageDraw.Draw(m)
        out = []
        if t < 0.25:  # repair spark at the bridge
            for b in self.bridges:
                disc(d, b, W.u(4) * (1 - t / 0.25) + W.u(1), int(255 * (1 - t / 0.25)))
        f = (t - 0.22) / 0.62
        if f > 0:
            fade = 1.0 if t < 0.85 else max(0.0, 1 - (t - 0.85) / 0.15)
            for pth in self.paths:
                seg = pth.sub(0, min(1, f))
                if len(seg) >= 2:
                    line(d, seg, W.u(1.9), int(160 * fade))
                if f < 1:
                    packet(d, pth, f, 0.15, W.u(2.6), 255)
        self.idle_packets(t, d, 2, 90)
        out.append((L(m), self.col, 1.0))
        return out

    def post(self, rgb, t):
        m = self._sold[..., None]
        solder = np.array([0.78, 0.80, 0.82], np.float32)
        hi = blur(self._sold, self.W.u(1.5))[..., None]
        return rgb * (1 - m) + (solder * (0.55 + 0.6 * hi)) * m


class Virus(Board):
    def build(self):
        W = self.W
        self.node = W.P(-0.62, 0.86)
        self.filler(20, keep_out=None, seg=(10, 34))
        self.scatter_smd(4)
        self.chip(*W.P(0.5, 0.25), 18, 14, pins=3)
        self.vias.append((self.node, 4.0))
        self.silk_txt.append(((self.node[0], self.node[1] + W.u(11)), "P0", 6))
        nx, ny = self.node
        self.D = np.hypot(W.X - nx, W.Y - ny)
        self.Dmax = float((self.D * (W.mask > 0)).max())

    def emit(self, t):
        W = self.W
        cu = self._masks[0] if hasattr(self, "_masks") else None
        if cu is None:
            self.shaded_base()
            cu = self._masks[0]
        front = t * 1.25 * self.Dmax
        infected = (self.D < front).astype(np.float32)
        edge = np.exp(-((self.D - front) / W.u(9)) ** 2)
        fade = 1.0 if t < 0.85 else max(0.0, 1 - (t - 0.85) / 0.15)
        tr = (cu + self._masks[1] * 0.6) * (infected * 0.55 + edge * 1.2) * fade
        out = [(tr, self.col, 1.0)]
        # corruption blocks along the front
        g = W.blank()
        dg = ImageDraw.Draw(g)
        rng = random.Random(int(t * 24))
        nx, ny = self.node
        for _ in range(9):
            a = rng.uniform(0, 2 * math.pi)
            r = front + W.u(rng.uniform(-8, 4))
            x, y = nx + math.cos(a) * r, ny + math.sin(a) * r
            dg.rectangle([x, y, x + W.u(rng.uniform(2, 9)), y + W.u(rng.uniform(1, 3))], fill=int(200 * fade))
        disc(dg, self.node, W.u(4 + 1.5 * math.sin(t * 6 * math.pi)), 255)
        out.append((L(g) * W.mask, self.col, 1.0))
        self._stain = infected * fade
        return out

    def post(self, rgb, t):
        st = blur(self._stain, self.W.u(3))[..., None]
        return rgb * (1 - 0.25 * st) + st * self.col * 0.05


class Trojan(Board):
    hue_sub = 0.08

    def build(self):
        W = self.W
        self.cc = W.P(0, 0.16)
        self.filler(18, keep_out=self.keep_icon(1.0), seg=(12, 30))
        self.scatter_smd(4, keep_out=self.keep_icon(1.0))
        cx, cy = self.cc
        self.hw_ = W.u(15)
        self.hh_ = W.u(10)
        self.silk_txt.append(((cx, cy + W.u(17)), "U7  N/C", 6))
        # hidden payload traces from the chip to the rim
        self.paths = []
        for side in (-1, 1):
            pts = [(cx + side * self.hw_, cy), (cx + side * W.u(26), cy - W.u(10)), W.P(side * 0.62, 0.40), W.P(side * 0.62, 0.97)]
            self.paths.append(Path(pts))
        for pts, _ in self.traces[:6]:
            self.packet_paths.append(Path(pts))

    def unpack(self, t):
        if t < 0.2:
            return 0.0
        if t < 0.38:
            return (t - 0.2) / 0.18
        if t < 0.86:
            return 1.0
        return max(0.0, 1 - (t - 0.86) / 0.1)

    def emit(self, t):
        W = self.W
        u = self.unpack(t)
        m = W.blank()
        d = ImageDraw.Draw(m)
        self.idle_packets(t, d, 3, 70)
        cx, cy = self.cc
        if u > 0:
            # payload: hidden traces fill toward the rim
            for pth in self.paths:
                f = min(1.0, max(0.0, (t - 0.32) / 0.4))
                seg = pth.sub(0, f)
                if len(seg) >= 2:
                    line(d, seg, W.u(1.6), int(170 * u))
                if 0 < f < 1:
                    disc(d, pth.at(f), W.u(2.4), 255)
            die = W.blank()
            dd = ImageDraw.Draw(die)
            dd.rectangle([cx - self.hw_ * 0.55 * u, cy - self.hh_ * 0.55, cx + self.hw_ * 0.55 * u, cy + self.hh_ * 0.55], fill=int(200 * u))
            blink = 1.0 if (int(t * 16) % 2 == 0 and t > 0.38) else 0.25
            disc(dd, (cx + self.hw_ * 0.75, cy - self.hh_ * 0.75), W.u(2.2), int(255 * blink * u))
            extra = [(L(die), self.col, 1.3)]
        else:
            extra = []
        self._u = u
        return [(L(m), self.col, 1.0)] + extra

    def post(self, rgb, t):
        """the innocent lid: two halves slide apart while unpacking"""
        W = self.W
        u = getattr(self, "_u", 0.0)
        cx, cy = self.cc
        lid = W.blank()
        dl = ImageDraw.Draw(lid)
        slide = self.hw_ * 0.62 * u
        dl.rectangle([cx - self.hw_ - slide, cy - self.hh_, cx - slide, cy + self.hh_], fill=255)
        dl.rectangle([cx + slide, cy - self.hh_, cx + self.hw_ + slide, cy + self.hh_], fill=255)
        pins = W.blank()
        dp = ImageDraw.Draw(pins)
        for k in range(4):
            yy = cy - self.hh_ + 2 * self.hh_ * (k + 0.5) / 4
            ext = W.u(3 + 3 * u)
            dp.rectangle([cx - self.hw_ - slide - ext, yy - W.u(0.8), cx - self.hw_ - slide, yy + W.u(0.8)], fill=255)
            dp.rectangle([cx + self.hw_ + slide, yy - W.u(0.8), cx + self.hw_ + slide + ext, yy + W.u(0.8)], fill=255)
        lm, pm = L(lid)[..., None], L(pins)[..., None]
        rgb = rgb * (1 - pm) + np.array([0.6, 0.6, 0.62]) * pm
        lidc = np.array([0.075, 0.07, 0.085], np.float32)
        rgb = rgb * (1 - lm) + lidc * lm
        return rgb


class Null(Board):
    hue_sub = 0.0
    facet_amt = 0.6
    dead = True

    def build(self):
        W = self.W
        self.filler(12, seg=(12, 34))
        self.scatter_smd(3)
        self.burn = W.P(0.30, 0.26)
        # the burnt trace runs through the scorch
        a = W.P(-0.7, 0.10)
        b = W.P(0.85, 0.55)
        pts = [a, (a[0] + W.u(16), a[1] - W.u(16)), self.burn, (self.burn[0] + W.u(20), self.burn[1] - W.u(20)), b]
        self.traces.append((pts, 2.2))
        self.pads.append((a, 2.8))
        self.pads.append((b, 2.8))
        self.silk_txt.append((W.P(-0.5, 0.8), "NC", 6))

    def substrate(self):
        sub = super().substrate()
        g = sub.mean(axis=2, keepdims=True)
        return g * 0.9 + 0.01

    def shaded_base(self, light_rot=0.0):
        key = round(light_rot, 3)
        if key in self._base_cache:
            return self._base_cache[key]
        rgb = super().shaded_base(light_rot)
        W = self.W
        bx, by = self.burn
        rng = np.random.default_rng(5)
        n = blur(rng.standard_normal((W.h, W.w)).astype(np.float32), W.u(3)) * 3
        D = np.hypot(W.X - bx, W.Y - by) / W.u(20) + n * 0.45
        char = np.clip(1.3 - D, 0, 1) ** 0.7
        halo = np.clip(2.6 - D, 0, 1) * (1 - char)
        ring_ = np.exp(-((D - 1.35) / 0.25) ** 2)          # heat-discoloured rim of the scorch
        rgb = rgb * (1 - char[..., None] * 0.95)
        rgb = rgb * (1 - halo[..., None] * 0.3) + halo[..., None] * np.array([0.16, 0.09, 0.035])
        rgb = rgb + ring_[..., None] * np.array([0.20, 0.10, 0.03])
        # blistered, lifted copper flecks inside the char
        fl = (blur(rng.standard_normal((W.h, W.w)).astype(np.float32), W.u(0.8)) > 0.55).astype(np.float32) * char
        rgb = rgb + fl[..., None] * np.array([0.22, 0.13, 0.07])
        rgb = rgb.astype(np.float32)
        self._base_cache[key] = rgb
        return rgb

    def post(self, rgb, t):
        rng = np.random.default_rng(int(t * 30) + 1)
        gr = rng.standard_normal(rgb.shape[:2]).astype(np.float32) * 0.012
        return rgb + gr[..., None]

    def rim_col(self):
        return np.array([0.30, 0.30, 0.30], np.float32)

    def rim_gain(self, t):
        return 0.55


CLASSES = {"EXPLOIT": Exploit, "ZERO-DAY": ZeroDay, "FIREWALL": Firewall, "SANDBOX": Sandbox,
           "PROXY": Proxy, "PATCH": Patch, "VIRUS": Virus, "TROJAN": Trojan, "NULL": Null}


def make_board(name, ticks=3, ro=R_OUT, ri=R_IN, ss=2, seed=None, value="default", lod=0):
    stype, hx, glyph, val = PROGRAMS[name]
    W = Wedge(ticks, ro, ri, ss)
    b = CLASSES[name](W, hexc(hx), seed=seed if seed is not None else (ORDER.index(name) * 31 + ticks), lod=lod)
    b.glyph = glyph
    b.value = val if value == "default" else value
    b.pname = name
    return b


# ----------------------------------------------------------------------------- enemy board
class CorpBoard(Board):
    """Meridian Freight: machined, uniform polar-grid board in corp orange,
    container-stripe silkscreen on the outer band; type only by glyph + thin accent."""
    hue_sub = 0.0
    facet_amt = 0.0

    def __init__(self, W, accent, seed=1, lod=0):
        self.accent = accent
        super().__init__(W, MERIDIAN, seed=seed, lod=lod, corp=True)

    def build(self):
        W = self.W
        # concentric arc traces at a fixed radial pitch
        self.arcs = []
        pitch = W.u(15)
        r = W.Ri + W.u(14)
        while r < W.Ro - W.u(30):
            a_lim = W.half - math.asin(min(0.99, (W.u(6) + W.gap / 2) / r))
            pts = [(W.cx + r * math.sin(-a_lim + 2 * a_lim * k / 40), W.cy - r * math.cos(-a_lim + 2 * a_lim * k / 40)) for k in range(41)]
            self.traces.append((pts, 1.4))
            self.arcs.append((r, Path(pts)))
            r += pitch
        # radial spokes on a fixed angular pitch (2 degrees), pads on the grid
        step = math.radians(4)
        n = int(W.half / step)
        for i in range(-n, n + 1):
            a = i * step
            if abs(a) > W.half - math.radians(1.2):
                continue
            p0 = (W.cx + W.Ri * math.sin(a), W.cy - W.Ri * math.cos(a))
            r1 = W.Ro - W.u(30)
            p1 = (W.cx + r1 * math.sin(a), W.cy - r1 * math.cos(a))
            if i % 2 == 0:
                self.traces.append(([p0, p1], 1.0))
            for j, (rr, _) in enumerate(self.arcs):
                if (i + j) % 2 == 0:
                    self.pads.append(((W.cx + rr * math.sin(a), W.cy - rr * math.cos(a)), 1.9))

    def substrate(self):
        W = self.W
        base = np.array([0.075, 0.062, 0.058], np.float32) + MERIDIAN * 0.025
        # machined: fine concentric lathe rings
        lathe = np.sin(W.rr / W.u(1.3)) * 0.04 + np.sin(W.rr / W.u(7.0)) * 0.02
        return base[None, None, :] * (1 + lathe[..., None])

    def extra_static(self, dc, dp, dh, dch, dpi, ds):
        W = self.W
        # container stripes: 45-degree silkscreen band at the outer edge
        stripes = Image.new("L", (W.w, W.h), 0)
        dst = ImageDraw.Draw(stripes)
        step = W.u(9)
        k = -W.h
        while k < W.w + W.h:
            dst.polygon([(k, 0), (k + step * 0.5, 0), (k + step * 0.5 + W.h, W.h), (k + W.h, W.h)], fill=255)
            k += step
        band = ((W.rr > W.Ro - W.u(24)) & (W.rr < W.Ro - W.u(6))).astype(np.float32)
        self.stripe = L(stripes) * band
        self.stripe_band = band

    def shaded_base(self, light_rot=0.0):
        key = round(light_rot, 3)
        if key in self._base_cache:
            return self._base_cache[key]
        rgb = super().shaded_base(light_rot).copy()
        st = self.stripe[..., None]
        bd = self.stripe_band[..., None]
        rgb = rgb * (1 - bd * 0.5) + bd * np.array([0.05, 0.04, 0.035])
        rgb = rgb * (1 - st) + st * MERIDIAN * 0.62
        # the thin type accent along the inner edge
        acc = ((self.W.rr > self.W.Ri + self.W.u(3)) & (self.W.rr < self.W.Ri + self.W.u(6.5))).astype(np.float32)
        self._acc = acc
        self._base_cache[key] = rgb.astype(np.float32)
        return self._base_cache[key]

    def emit(self, t):
        W = self.W
        m = W.blank()
        d = ImageDraw.Draw(m)
        n = len(self.arcs)
        for j, (r, pth) in enumerate(self.arcs):
            # a regular clock: one arc lit at a time, marching inward like a conveyor
            ph = (t * 2 * n - (n - 1 - j)) % n
            v = max(0.0, 1 - ph / 2.0)
            line(d, pth.pts, W.u(1.4), int(50 + 170 * v))
        out = [(L(m), MERIDIAN, 0.8)]
        out.append((self._acc * W.mask, self.accent, 2.4))
        return out


def make_corp_board(name, ticks=3, ro=R_OUT, ri=R_IN, ss=2, value="default", seed=3, lod=0):
    stype, hx, glyph, val = PROGRAMS[name]
    W = Wedge(ticks, ro, ri, ss)
    b = CorpBoard(W, hexc(hx), seed=seed, lod=lod)
    b.glyph = glyph
    b.value = val if value == "default" else value
    b.pname = name
    return b
