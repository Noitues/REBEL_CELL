"""TACTICAL GLASS overlay engine (Pillow + numpy, seeded).

A mission-planning acrylic sheet laid over the Cv2 screen:
  * grease-pencil / china-marker strokes (bristle striations, broken edges, wax tooth,
    real height -> lit with a key light, specular sheen and an optional glint sweep)
  * crisp printed elements (stencil type, registration marks, ticks, range rings, waypoints)
  * masking / gaffer tape, laminated cards and ID badges
  * acrylic sheen: reflection band, streaks, finger smudges, haze
Everything renders at SS x supersampling and is box-downsampled.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from glyphs import G

SS = 2
W, H = 1920, 1080
FONTS = 'C:/Windows/Fonts/'

PINK = (1.00, 0.17, 0.56)
ORANGE = (1.00, 0.45, 0.07)
RED = (0.97, 0.13, 0.12)
WHITE = (0.95, 0.94, 0.89)
YELLOW = (1.00, 0.86, 0.16)


# ----------------------------------------------------------------------------- utils
def font(name, size, variation=None):
    f = ImageFont.truetype(FONTS + name, int(size))
    if variation:
        f.set_variation_by_name(variation)
    return f


def bahn(size, var='Bold Condensed'):
    return font('bahnschrift.ttf', size, var)


def stencil(size):
    return font('STENCIL.TTF', size)


def _box1(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(a, pad, mode='edge')
    c = np.cumsum(p, axis=axis, dtype=np.float64)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return ((hi - lo) / (2 * r + 1)).astype(np.float32)


def blur(a, sigma, axes=(0, 1)):
    """Gaussian approximation: three box passes."""
    if sigma <= 0.3:
        return a
    r = max(1, int(round((math.sqrt(4 * sigma * sigma + 1) - 1) / 2)))
    out = a
    for _ in range(3):
        for ax in axes:
            out = _box1(out, r, ax)
    return out


def noise(h, w, scale, rng):
    """Smooth value noise in [0,1]."""
    gh, gw = max(2, int(h / scale) + 3), max(2, int(w / scale) + 3)
    g = rng.random((gh, gw)).astype(np.float32)
    im = Image.fromarray(g, 'F').resize((int(gw * scale), int(gh * scale)), Image.BICUBIC)
    a = np.asarray(im, dtype=np.float32)[:h, :w]
    return np.clip(a, 0, 1)


def fbm(h, w, rng, scales=(64, 24, 8, 3), weights=(0.45, 0.28, 0.17, 0.10)):
    acc = np.zeros((h, w), np.float32)
    for s, wt in zip(scales, weights):
        acc += wt * noise(h, w, s, rng)
    return acc


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def resample(pts, step):
    p = np.asarray(pts, np.float64)
    if len(p) < 2:
        return p
    d = np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1))
    s = np.concatenate([[0], np.cumsum(d)])
    if s[-1] < 1e-6:
        return p[:1]
    n = max(2, int(s[-1] / step) + 1)
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, p[:, 0]), np.interp(t, s, p[:, 1])], 1)


def chaikin(p, it=2):
    p = np.asarray(p)
    for _ in range(it):
        if len(p) < 3:
            return p
        q = 0.75 * p[:-1] + 0.25 * p[1:]
        r = 0.25 * p[:-1] + 0.75 * p[1:]
        mid = np.empty((2 * len(q), 2))
        mid[0::2], mid[1::2] = q, r
        p = np.vstack([p[:1], mid, p[-1:]])
    return p


def path_len(p):
    p = np.asarray(p)
    return float(np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1)).sum()) if len(p) > 1 else 0.0


def cut_path(p, frac):
    p = np.asarray(p, np.float64)
    L = path_len(p)
    if frac >= 1 or L == 0:
        return p
    d = np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1))
    s = np.concatenate([[0], np.cumsum(d)])
    target = L * frac
    k = np.searchsorted(s, target)
    if k <= 0:
        return p[:1]
    t = (target - s[k - 1]) / max(1e-9, d[k - 1])
    end = p[k - 1] + (p[k] - p[k - 1]) * t
    return np.vstack([p[:k], end[None]])


def cut_strokes(strokes, progress):
    """Keep the first `progress` fraction (by drawn length) of a stroke list."""
    if progress >= 1:
        return strokes
    total = sum(path_len(s[0]) + 40 for s in strokes)  # +40: pen-lift time
    budget = total * progress
    out = []
    for s in strokes:
        L = path_len(s[0]) + 40
        if budget >= L:
            out.append(s)
            budget -= L
        else:
            f = max(0.0, (budget - 20) / max(1e-6, L - 40))
            if f > 0.02:
                out.append((cut_path(s[0], f),) + tuple(s[1:]))
            break
    return out


def rot(pts, ang, cx, cy):
    c, s = math.cos(ang), math.sin(ang)
    p = np.asarray(pts, np.float64) - (cx, cy)
    return np.stack([p[:, 0] * c - p[:, 1] * s + cx, p[:, 0] * s + p[:, 1] * c + cy], 1)


# ----------------------------------------------------------------------------- layer
class Layer:
    """Premultiplied RGBA overlay at SS resolution covering a screen rect."""

    def __init__(self, rng, x0=0, y0=0, w=W, h=H):
        self.x0, self.y0, self.w, self.h = x0, y0, w, h
        self.W2, self.H2 = w * SS, h * SS
        self.rgb = np.zeros((self.H2, self.W2, 3), np.float32)
        self.a = np.zeros((self.H2, self.W2), np.float32)
        self.wax = np.zeros((self.H2, self.W2), np.float32)
        self.height = np.zeros((self.H2, self.W2), np.float32)
        self.rng = rng
        self.grain = noise(self.H2, self.W2, 1.6, rng) * 0.6 + noise(self.H2, self.W2, 4.0, rng) * 0.4
        self.mid = noise(self.H2, self.W2, 18, rng)
        self.print_img = Image.new('RGBA', (self.W2, self.H2), (0, 0, 0, 0))
        self.pd = ImageDraw.Draw(self.print_img)

    # coordinate helpers --------------------------------------------------------
    def S(self, x, y):
        return ((x - self.x0) * SS, (y - self.y0) * SS)

    def over(self, x, y, rgb, a):
        """Composite premultiplied (rgb, a) arrays with top-left at SS coords x,y."""
        h, w = a.shape
        X0, Y0 = max(0, x), max(0, y)
        X1, Y1 = min(self.W2, x + w), min(self.H2, y + h)
        if X1 <= X0 or Y1 <= Y0:
            return None
        sx, sy = X0 - x, Y0 - y
        sa = a[sy:sy + Y1 - Y0, sx:sx + X1 - X0]
        sr = rgb[sy:sy + Y1 - Y0, sx:sx + X1 - X0]
        da = self.a[Y0:Y1, X0:X1]
        dr = self.rgb[Y0:Y1, X0:X1]
        self.rgb[Y0:Y1, X0:X1] = sr + dr * (1 - sa[..., None])
        self.a[Y0:Y1, X0:X1] = sa + da * (1 - sa)
        return (X0, Y0, X1, Y1, sx, sy)

    def paste(self, img, cx, cy, angle=0.0, height=0.25, cover_wax=True):
        """Paste an SS-resolution RGBA PIL image centred at screen cx,cy."""
        if angle:
            img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
        arr = np.asarray(img, np.float32) / 255.0
        a = arr[..., 3]
        rgb = arr[..., :3] * a[..., None]
        X, Y = self.S(cx, cy)
        x, y = int(X - img.width / 2), int(Y - img.height / 2)
        r = self.over(x, y, rgb, a)
        if r:
            X0, Y0, X1, Y1, sx, sy = r
            sa = a[sy:sy + Y1 - Y0, sx:sx + X1 - X0]
            if cover_wax:
                self.wax[Y0:Y1, X0:X1] *= (1 - sa)
            self.height[Y0:Y1, X0:X1] = np.maximum(self.height[Y0:Y1, X0:X1] * (1 - sa), sa * height)

    def flush_print(self):
        arr = np.asarray(self.print_img, np.float32) / 255.0
        a = arr[..., 3]
        self.over(0, 0, arr[..., :3] * a[..., None], a)
        self.print_img = Image.new('RGBA', (self.W2, self.H2), (0, 0, 0, 0))
        self.pd = ImageDraw.Draw(self.print_img)

    # wax ------------------------------------------------------------------------
    def wax_stroke(self, pts, width, color, density=1.0, seed_off=0, thickness=1.0, flick=True):
        rng = self.rng
        P = np.array([self.S(x, y) for x, y in pts], np.float64)
        P = resample(P, 1.4)
        if len(P) < 2:
            P = np.vstack([P, P + 0.8])
        wpx = width * SS
        m = int(wpx + 8)
        bx0, by0 = int(P[:, 0].min()) - m, int(P[:, 1].min()) - m
        bx1, by1 = int(P[:, 0].max()) + m, int(P[:, 1].max()) + m
        cw, ch = bx1 - bx0, by1 - by0
        Q = P - (bx0, by0)
        n = len(Q)
        seg = np.diff(Q, axis=0)
        seg = np.vstack([seg, seg[-1:]])
        tang = seg / np.maximum(1e-6, np.linalg.norm(seg, axis=1, keepdims=True))
        tang = blur(tang, 3, axes=(0,)) if n > 8 else tang
        tang /= np.maximum(1e-6, np.linalg.norm(tang, axis=1, keepdims=True))
        nor = np.stack([-tang[:, 1], tang[:, 0]], 1)
        s = np.linspace(0, 1, n)
        L = path_len(Q)
        sl = s * L
        press = 0.80 + 0.20 * smoothstep(0, min(14.0, L * 0.3 + 1e-3), sl)
        if flick:
            press *= 1.0 - 0.22 * smoothstep(L - min(24.0, L * 0.35), L + 1e-3, sl)
        knots = np.linspace(0, L, max(3, int(L / 40) + 2))
        press *= np.interp(sl, knots, 0.92 + 0.16 * rng.random(len(knots)))

        core = Image.new('L', (cw, ch), 0)
        bris = Image.new('L', (cw, ch), 0)
        dc, db = ImageDraw.Draw(core), ImageDraw.Draw(bris)
        step = 5
        for i in range(0, n - 1, step):
            j = min(n, i + step + 1)
            wv = max(1, int(wpx * 0.70 * press[i]))
            dc.line([tuple(q) for q in Q[i:j]], fill=255, width=wv, joint='curve')
        nb = int(np.clip(wpx / 2.3, 5, 24))
        bw = max(2, int(round(wpx / nb * 1.7)))
        for b in range(nb):
            u = (b / (nb - 1) - 0.5)
            off = u * wpx * 0.92 + rng.normal(0, 0.6)
            edge = abs(u) * 2
            kn = np.linspace(0, L, max(3, int(L / (16 + 26 * rng.random())) + 2))
            val = np.interp(sl, kn, rng.random(len(kn)))
            thr = 0.02 + 0.30 * edge ** 3.0
            on = val > thr
            offs = off * press
            B = Q + nor * offs[:, None]
            k = 0
            while k < n:
                if on[k]:
                    e = k
                    while e < n and on[e]:
                        e += 1
                    if e - k >= 2:
                        db.line([tuple(q) for q in B[k:e]], fill=255, width=bw, joint='curve')
                    k = e
                else:
                    k += 1
        c = np.asarray(core, np.float32) / 255.0
        b_ = np.asarray(bris, np.float32) / 255.0
        Mm = np.maximum(c * 0.74, b_)
        Mm = blur(Mm, 0.6)
        # clip grain crop (may be partly outside the layer)
        X0, Y0 = max(0, bx0), max(0, by0)
        X1, Y1 = min(self.W2, bx1), min(self.H2, by1)
        if X1 <= X0 or Y1 <= Y0:
            return
        g = np.full((ch, cw), 0.5, np.float32)
        md = np.full((ch, cw), 0.5, np.float32)
        g[Y0 - by0:Y1 - by0, X0 - bx0:X1 - bx0] = self.grain[Y0:Y1, X0:X1]
        md[Y0 - by0:Y1 - by0, X0 - bx0:X1 - bx0] = self.mid[Y0:Y1, X0:X1]
        # glass gives wax little tooth: rare pinholes, a crisp-but-ragged edge,
        # and striations (bristle gaps) running along the stroke
        tooth = smoothstep(0.06, 0.16, g)
        alpha = Mm * (0.80 + 0.20 * tooth)
        alpha = smoothstep(0.22, 0.62, alpha + (g - 0.5) * 0.18) * (0.74 + 0.26 * smoothstep(0.75, 1.0, Mm))
        alpha = np.clip(alpha * 1.08, 0, 1) * density
        col = np.array(color, np.float32)
        shade = (0.88 + 0.12 * md + 0.08 * b_)[..., None]
        rgb = np.clip(col[None, None, :] * shade, 0, 1) * alpha[..., None]
        r = self.over(bx0, by0, rgb, alpha)
        if r:
            X0, Y0, X1, Y1, sx, sy = r
            sa = alpha[sy:sy + Y1 - Y0, sx:sx + X1 - X0]
            sb = b_[sy:sy + Y1 - Y0, sx:sx + X1 - X0]
            self.wax[Y0:Y1, X0:X1] = sa + self.wax[Y0:Y1, X0:X1] * (1 - sa)
            h = sa * thickness * (0.85 + 0.15 * sb)
            self.height[Y0:Y1, X0:X1] = np.maximum(self.height[Y0:Y1, X0:X1], h)

    def strokes(self, strokes):
        for st in strokes:
            pts, width, color = st[0], st[1], st[2]
            self.wax_stroke(pts, width, color)

    # lighting -------------------------------------------------------------------
    def light(self, glint=None, glint_gain=1.0, spec_gain=1.0):
        hb = blur(self.height, 1.3 * SS)
        gy, gx = np.gradient(hb)
        k = 4.5
        nx, ny, nz = -gx * k, -gy * k, np.ones_like(hb)
        inv = 1 / np.sqrt(nx * nx + ny * ny + 1)
        nx, ny, nz = nx * inv, ny * inv, nz * inv
        Lv = np.array([-0.55, -0.62, 0.56])
        Lv /= np.linalg.norm(Lv)
        ndl = nx * Lv[0] + ny * Lv[1] + nz * Lv[2]
        Hv = Lv + np.array([0, 0, 1.0])
        Hv /= np.linalg.norm(Hv)
        ndh = np.clip(nx * Hv[0] + ny * Hv[1] + nz * Hv[2], 0, 1)
        spec = ndh ** 28
        wax = self.wax
        shade = 1 + 0.55 * (ndl - Lv[2])
        shade = 1 + (shade - 1) * wax
        self.rgb *= np.clip(shade, 0.55, 1.35)[..., None]
        sheen = (spec * 0.50 * spec_gain + 0.03) * wax * (0.8 + 0.4 * self.mid)
        if glint is not None:
            yy, xx = np.mgrid[0:self.H2, 0:self.W2].astype(np.float32)
            t = (xx / self.W2 * 0.78 + yy / self.H2 * 0.42) / 1.2
            band = np.exp(-((t - glint) / 0.035) ** 2)
            band2 = np.exp(-((t - glint + 0.06) / 0.012) ** 2) * 0.6
            sheen += (band + band2) * wax * (0.25 + 2.2 * spec + 0.5 * self.grain) * 0.55 * glint_gain
        add = sheen[..., None] * np.array([1.0, 0.98, 0.95], np.float32)
        self.rgb += add
        self.rgb = np.minimum(self.rgb, self.a[..., None] * 1.25)

    def down(self):
        """Downsample to 1x: returns (rgb premult, a)."""
        r = self.rgb.reshape(self.h, SS, self.w, SS, 3).mean((1, 3))
        a = self.a.reshape(self.h, SS, self.w, SS).mean((1, 3))
        return r, a


# ----------------------------------------------------------------------------- lettering
def letter_strokes(text, cx, cy, cap, width, color, rng, slant=0.16, angle=0.0, tracking=0.20,
                   wobble=0.012, line_gap=1.45, align='center'):
    """Hand-lettered single-stroke skeletons for `text` (lines split by '\\n')
    centred on cx, cy. Returns [(pts, width, color), ...] in writing order."""
    lines = text.split('\n')
    out = []
    nl = len(lines)
    advs = []
    for line in lines:
        adv = sum(G[c][0] + tracking for c in line) - tracking
        advs.append(adv)
    maxadv = max(advs)
    for li, line in enumerate(lines):
        adv = advs[li]
        if align == 'center':
            pen = -adv / 2
        elif align == 'left':
            pen = -maxadv / 2
        else:
            pen = maxadv / 2 - adv
        base_y = (li - (nl - 1) / 2) * line_gap - 0.5
        for ch in line:
            gw, sks = G[ch]
            sc = 1 + rng.normal(0, 0.035)
            gr = rng.normal(0, 0.035)
            dy = rng.normal(0, 0.025)
            for sk in sks:
                p = resample(sk, 0.05)
                if len(p) < 2:
                    p = np.vstack([p, p + 0.01])
                # overshoot ends a touch (fast confident hand)
                if len(p) > 3 and path_len(p) > 0.25:
                    d0 = p[0] - p[1]
                    d1 = p[-1] - p[-2]
                    p = np.vstack([p[0] + d0 / max(1e-6, np.linalg.norm(d0)) * 0.03, p,
                                   p[-1] + d1 / max(1e-6, np.linalg.norm(d1)) * 0.05])
                m = len(p)
                tt = np.linspace(0, 1, m)
                jx = sum(rng.normal(0, wobble) * np.sin(2 * math.pi * (f * tt + rng.random()))
                         for f in (0.6, 1.3))
                jy = sum(rng.normal(0, wobble) * np.sin(2 * math.pi * (f * tt + rng.random()))
                         for f in (0.7, 1.6))
                p = p + np.stack([jx, jy], 1)
                p = rot(p, gr, gw / 2, 0.5)
                p = p * sc
                x = p[:, 0] + (1 - p[:, 1]) * slant + pen
                y = p[:, 1] + base_y + dy
                q = np.stack([x * cap, y * cap], 1)
                q = rot(q, angle, 0, 0) + (cx, cy)
                q = chaikin(q, 2)
                out.append((q, width * (1 + rng.normal(0, 0.04)), color))
            pen += gw + tracking
    return out


def hand_circle(cx, cy, rx, ry, rng, turns=1.12, start=None, wobble=0.035, angle=0.0):
    if start is None:
        start = rng.uniform(-150, -100)
    n = int(120 * turns)
    a = np.radians(start + np.linspace(0, 360 * turns, n))
    drift = np.linspace(0, 1, n)
    rr = 1 + wobble * np.sin(a * 2 + rng.random() * 6) + 0.05 * drift * rng.choice([-1, 1])
    x, y = rx * rr * np.cos(a), ry * rr * np.sin(a)
    p = rot(np.stack([x, y], 1), angle, 0, 0) + (cx, cy)
    return p


def bezier(p0, p1, p2, n=60):
    t = np.linspace(0, 1, n)[:, None]
    p0, p1, p2 = map(np.asarray, (p0, p1, p2))
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2


def arrow_strokes(path, width, color, rng, head=26, dashed=False, dash=34, gap=20):
    """Hand arrow: the shaft (optionally hand-dashed) and two head flicks."""
    p = resample(path, 2)
    out = []
    if dashed:
        L = path_len(p)
        s = 0.0
        d = np.sqrt(((p[1:] - p[:-1]) ** 2).sum(1))
        cs = np.concatenate([[0], np.cumsum(d)])
        while s < L - 10:
            e = min(L - 6, s + dash * rng.uniform(0.85, 1.15))
            idx = (cs >= s) & (cs <= e)
            if idx.sum() >= 2:
                out.append((p[idx] + rng.normal(0, 0.6, (idx.sum(), 2)), width, color))
            s = e + gap * rng.uniform(0.8, 1.2)
    else:
        out.append((p, width, color))
    tip = p[-1]
    dv = p[-1] - p[-min(len(p), 8)]
    dv /= max(1e-6, np.linalg.norm(dv))
    for sgn in (1, -1):
        ang = math.radians(152 * sgn + rng.normal(0, 5))
        c, s_ = math.cos(ang), math.sin(ang)
        v = np.array([dv[0] * c - dv[1] * s_, dv[0] * s_ + dv[1] * c])
        hl = head * rng.uniform(0.9, 1.1)
        out.append((np.array([tip + v * hl, tip + v * hl * 0.4, tip]), width, color))
    return out


# ----------------------------------------------------------------------------- printed
def print_reg_mark(layer, x, y, r=14, col=(240, 238, 230, 150)):
    d = layer.pd
    X, Y = layer.S(x, y)
    R = r * SS
    lw = max(1, int(1.2 * SS))
    d.ellipse([X - R * 0.6, Y - R * 0.6, X + R * 0.6, Y + R * 0.6], outline=col, width=lw)
    d.line([X - R, Y, X + R, Y], fill=col, width=lw)
    d.line([X, Y - R, X, Y + R], fill=col, width=lw)


def print_ticks(layer, rng, col=(240, 238, 230, 95)):
    d = layer.pd
    f = bahn(11 * SS, 'SemiBold Condensed')
    lw = max(1, int(1 * SS))
    for i, x in enumerate(range(48, W, 48)):
        long = (i % 5 == 4)
        L = (11 if long else 5) * SS
        X, Y = layer.S(x, 0)
        d.line([X, Y, X, Y + L], fill=col, width=lw)
        X2, Y2 = layer.S(x, H)
        d.line([X2, Y2 - L, X2, Y2], fill=col, width=lw)
        if long:
            d.text((X + 3 * SS, Y + 4 * SS), chr(65 + i // 5), font=f, fill=col)
    for i, y in enumerate(range(48, H, 48)):
        long = (i % 5 == 4)
        L = (11 if long else 5) * SS
        X, Y = layer.S(W, y)
        d.line([X - L, Y, X, Y], fill=col, width=lw)
        X2, Y2 = layer.S(0, y)
        d.line([X2, Y2, X2 + L, Y2], fill=col, width=lw)
        if long:
            d.text((X - 18 * SS, Y + 2 * SS), '%02d' % (i // 5 + 1), font=f, fill=col)
    for (x, y) in [(30, 30), (W - 30, 30), (30, H - 30), (W - 30, H - 30)]:
        print_reg_mark(layer, x, y)


def print_dashed_circle(layer, cx, cy, r, col, width=1.6, dash=10, gap=8, ticks=0):
    d = layer.pd
    X, Y = layer.S(cx, cy)
    R = r * SS
    circ = 2 * math.pi * r
    n = int(circ / (dash + gap))
    lw = max(1, int(width * SS))
    for i in range(n):
        a0 = 2 * math.pi * i / n
        a1 = a0 + 2 * math.pi * dash / circ
        pts = [(X + R * math.cos(a), Y + R * math.sin(a)) for a in np.linspace(a0, a1, 6)]
        d.line(pts, fill=col, width=lw)
    for i in range(ticks):
        a = 2 * math.pi * i / ticks
        d.line([X + R * math.cos(a), Y + R * math.sin(a),
                X + (R + 9 * SS) * math.cos(a), Y + (R + 9 * SS) * math.sin(a)], fill=col, width=lw)


def print_text(layer, x, y, text, fnt, col, anchor='la'):
    X, Y = layer.S(x, y)
    layer.pd.text((X, Y), text, font=fnt, fill=col, anchor=anchor)


def print_waypoint(layer, x, y, label, col=(255, 222, 40, 255), r=15):
    d = layer.pd
    X, Y = layer.S(x, y)
    R = r * SS
    d.ellipse([X - R - 3 * SS, Y - R - 3 * SS, X + R + 3 * SS, Y + R + 3 * SS], fill=(14, 14, 16, 235))
    d.ellipse([X - R, Y - R, X + R, Y + R], fill=col)
    d.text((X, Y + 1 * SS), label, font=stencil(int(r * 1.35 * SS)), fill=(14, 14, 16, 255), anchor='mm')


def print_reticle(layer, cx, cy, r, col, gap=0.45):
    d = layer.pd
    X, Y = layer.S(cx, cy)
    R = r * SS
    lw = max(1, int(1.6 * SS))
    for a in (0, 90, 180, 270):
        c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line([X + c * R * gap, Y + s * R * gap, X + c * R * 1.0, Y + s * R * 1.0], fill=col, width=lw)
    # corner brackets
    b = R * 0.78
    k = R * 0.22
    for sx in (-1, 1):
        for sy in (-1, 1):
            d.line([X + sx * b, Y + sy * (b - k), X + sx * b, Y + sy * b, X + sx * (b - k), Y + sy * b],
                   fill=col, width=lw)


# ----------------------------------------------------------------------------- tape
def make_tape(w, h, rng, kind='masking'):
    """Torn strip of tape (SS resolution RGBA)."""
    W2, H2 = int(w * SS), int(h * SS)
    pad = 6 * SS
    im = Image.new('RGBA', (W2 + 2 * pad, H2 + 2 * pad), (0, 0, 0, 0))
    m = Image.new('L', im.size, 0)
    d = ImageDraw.Draw(m)
    left, right = [], []
    steps = max(4, H2 // (3 * SS))
    for i in range(steps + 1):
        yy = pad + H2 * i / steps
        left.append((pad + rng.uniform(-2.5, 2.5) * SS + (rng.random() < 0.3) * 3 * SS, yy))
        right.append((pad + W2 + rng.uniform(-2.5, 2.5) * SS - (rng.random() < 0.3) * 3 * SS, yy))
    poly = left + right[::-1]
    d.polygon(poly, fill=255)
    a = np.asarray(m, np.float32) / 255
    hh, ww = a.shape
    yy, xx = np.mgrid[0:hh, 0:ww].astype(np.float32)
    fib = noise(hh, ww, 2.0, rng)
    if kind == 'masking':
        base = np.array([0.86, 0.80, 0.64], np.float32)
        tex = 0.92 + 0.10 * noise(hh, ww, 14, rng) + 0.05 * (fib - 0.5)
        crep = 0.04 * np.sin(xx / (2.2 * SS) + noise(hh, ww, 6, rng) * 4)
        col = base[None, None] * (tex + crep)[..., None]
        opac = 0.86
    else:  # gaffer: dark cloth with weave and sheen
        base = np.array([0.12, 0.12, 0.13], np.float32)
        weave = 0.5 + 0.5 * np.sin(xx / (1.3 * SS)) * np.sin(yy / (1.3 * SS))
        tex = 0.85 + 0.25 * weave + 0.2 * noise(hh, ww, 10, rng)
        col = base[None, None] * tex[..., None]
        sheen = np.exp(-((yy / hh - 0.35) / 0.18) ** 2) * 0.10
        col = col + sheen[..., None]
        opac = 0.97
    # edge darkening (adhesive line) and soft border
    e = blur(a, 1.5 * SS)
    edge = np.clip((a - e) * 3, 0, 1)
    col = col * (1 - 0.25 * edge[..., None])
    col = np.clip(col, 0, 1)
    alpha = a * opac
    out = np.dstack([col, alpha])
    return Image.fromarray((out * 255).astype(np.uint8), 'RGBA')


# ----------------------------------------------------------------------------- lamination
def laminate(card, rng, margin=7, radius=14, glare=0.22, glare_pos=0.32, hole=None):
    """Wrap an SS RGBA card in a clear laminated pouch with gloss, glare and wear."""
    M, R = int(margin * SS), int(radius * SS)
    w, h = card.width + 2 * M, card.height + 2 * M
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    pouch = Image.new('L', (w, h), 0)
    ImageDraw.Draw(pouch).rounded_rectangle([0, 0, w - 1, h - 1], R, fill=255)
    pa = np.asarray(pouch, np.float32) / 255
    base = np.zeros((h, w, 4), np.float32)
    base[..., :3] = 0.88
    base[..., 3] = pa * 0.30
    im = Image.fromarray((base * 255).astype(np.uint8), 'RGBA')
    im.alpha_composite(card, (M, M))
    arr = np.asarray(im, np.float32) / 255
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # rim highlight
    e = blur(pa, 1.2 * SS)
    rim = np.clip((pa - e) * 4, 0, 1) + np.clip((e - blur(pa, 3 * SS)) * 2, 0, 1) * 0.3
    t = (xx / w * 0.6 + yy / h * 0.4)
    band = np.exp(-((t - glare_pos) / 0.07) ** 2) * glare + np.exp(-((t - glare_pos - 0.11) / 0.018) ** 2) * glare * 0.7
    spot = np.exp(-(((xx - w * 0.82) / (w * 0.10)) ** 2 + ((yy - h * 0.12) / (h * 0.06)) ** 2)) * 0.18
    scratches = np.zeros((h, w), np.float32)
    sc = Image.new('L', (w, h), 0)
    sd = ImageDraw.Draw(sc)
    for _ in range(14):
        x0, y0 = rng.uniform(0, w), rng.uniform(0, h)
        ang = rng.uniform(0, math.pi)
        L = rng.uniform(15, 70) * SS
        sd.line([x0, y0, x0 + math.cos(ang) * L, y0 + math.sin(ang) * L], fill=int(rng.uniform(40, 110)), width=1)
    scratches = np.asarray(sc, np.float32) / 255
    gl = (band + spot + scratches * 0.5 + rim * 0.55) * pa
    rgb = arr[..., :3] * (1 - gl[..., None] * 0.15) + gl[..., None] * np.array([1, 1, 1.02])
    a = np.clip(arr[..., 3] + gl * 0.6, 0, 1) * pa
    # orange-peel micro texture on the gloss
    op = noise(h, w, 3 * SS, rng)
    rgb = rgb + (op[..., None] - 0.5) * 0.025
    out = np.dstack([np.clip(rgb, 0, 1), a])
    img = Image.fromarray((out * 255).astype(np.uint8), 'RGBA')
    if hole:
        hx, hy, hw, hh = [v * SS for v in hole]
        cut = Image.new('L', img.size, 255)
        ImageDraw.Draw(cut).rounded_rectangle([hx - hw / 2, hy - hh / 2, hx + hw / 2, hy + hh / 2], hh / 2, fill=0)
        A = np.asarray(img).copy()
        A[..., 3] = (A[..., 3].astype(np.float32) * (np.asarray(cut, np.float32) / 255)).astype(np.uint8)
        img = Image.fromarray(A, 'RGBA')
        # slot rim
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([hx - hw / 2 - 1, hy - hh / 2 - 1, hx + hw / 2 + 1, hy + hh / 2 + 1], hh / 2,
                            outline=(235, 240, 245, 150), width=max(1, SS))
    return img


# ----------------------------------------------------------------------------- composite
def to_f(img):
    return np.asarray(img.convert('RGB'), np.float32) / 255.0


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGB')


def composite(base, layer, darken=0.30, shadow=0.42, sh_off=(4, 6), sh_blur=3.0):
    """Lay a Layer over the base (H,W,3 float); returns new array."""
    rgb, a = layer.down()
    x0, y0, w, h = layer.x0, layer.y0, layer.w, layer.h
    out = base.copy()
    reg = out[y0:y0 + h, x0:x0 + w]
    if darken > 0:
        dk = blur(np.minimum(1, a * 2.5), 16)
        reg *= (1 - darken * dk)[..., None]
    if shadow > 0:
        sh = blur(a, sh_blur)
        dx, dy = sh_off
        sh = np.roll(np.roll(sh, dy, 0), dx, 1)
        reg *= (1 - shadow * sh)[..., None]
    reg[:] = rgb + reg * (1 - a[..., None])
    return out


def acrylic(img, rng, smudges=(), streak_corner='tr', band_pos=0.30):
    """The sheet itself: haze, reflection band, edge streaks and finger smudges."""
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    out = img * 0.965 + np.array([0.010, 0.012, 0.016], np.float32)
    t = (xx / w * 0.72 + yy / h * 0.28)
    band = smoothstep(band_pos - 0.16, band_pos, t) * (1 - smoothstep(band_pos, band_pos + 0.035, t))
    band *= 0.055 * (0.55 + 0.45 * (1 - yy / h))
    out += band[..., None] * np.array([0.85, 0.92, 1.0], np.float32)
    # thin sharp streaks near a corner (light catching the acrylic)
    if streak_corner == 'tr':
        u = (xx - w) * 0.55 + yy * 0.83
        for off, k, wd in ((-260, 0.075, 2.2), (-300, 0.045, 1.2), (-420, 0.03, 6.0)):
            s = np.exp(-((u - off) / wd) ** 2) * np.clip(1 - (yy / (h * 0.55)), 0, 1)
            out += (s * k)[..., None]
    elif streak_corner == 'bl':
        u = xx * 0.55 + (yy - h) * 0.83
        for off, k, wd in ((260, 0.06, 2.2), (300, 0.035, 1.2)):
            s = np.exp(-((u - off) / wd) ** 2) * np.clip((yy - h * 0.45) / (h * 0.55), 0, 1)
            out += (s * k)[..., None]
    soft = None
    for (cx, cy, rx, ry, ang, kind) in smudges:
        if soft is None:
            soft = blur(out, 2.2)
        c, s = math.cos(ang), math.sin(ang)
        dx, dy = xx - cx, yy - cy
        u = (dx * c + dy * s) / rx
        v = (-dx * s + dy * c) / ry
        r = np.sqrt(u * u + v * v)
        fall = np.clip(1 - r, 0, 1) ** 0.8
        if kind == 'print':
            nz = noise(h, w, 30, rng) * 4
            ridge = 0.5 + 0.5 * np.sin(r * rx / 2.6 + nz)
            mask = fall * smoothstep(0.55, 0.9, ridge) * smoothstep(0.0, 0.25, 1 - r)
            haze = fall * 0.5
        else:  # wipe / palm smear: streaky directional haze
            st = noise(h, w, 1, rng)
            st = blur(st, 9, axes=(1,)) if False else st
            stx = np.sin(v * 40 + noise(h, w, 40, rng) * 6) * 0.5 + 0.5
            mask = fall * stx * 0.6
            haze = fall * 0.7
        out = out * (1 - (haze * 0.45)[..., None]) + soft * (haze * 0.45)[..., None]
        out += (mask * 0.085 + haze * 0.02)[..., None] * np.array([0.9, 0.95, 1.0], np.float32)
    return np.clip(out, 0, 1)
