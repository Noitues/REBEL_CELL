"""sg_gfx: the street-graffiti toolkit (numpy + scipy + PIL only).
Everything is drawn on float32 RGBA canvases at a supersample factor ss and downsampled at the end.
"The hand": spray grain + soft edge + overspray dots, wobbly marker strokes, extruded drops, torn paper, tape, drips."""
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage as ndi

FD = 'D:/rc_art/art-pass/assets/fonts/'
_fc = {}


def font(name, px):
    k = (name, int(px))
    if k not in _fc:
        _fc[k] = ImageFont.truetype(FD + name, max(4, int(px)))
    return _fc[k]


ANTON = 'Anton-Regular.ttf'
MARKER = 'PermanentMarker-Regular.ttf'
MONO = 'ShareTechMono-Regular.ttf'

# ---- palette (VISUAL_PLAN E) + the one street secondary ink (chrome)
def hx(s):
    s = s.lstrip('#')
    return np.array([int(s[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255.0


PINK = hx('FF3DA8'); PINK_HI = hx('FF8AD0'); PINK_LO = hx('C21A7C'); PINK_DK = hx('6A0C45'); PINK_DD = hx('2E0620')
INK = hx('0C0A16'); PAPER = hx('F2EEE4'); ZINE = hx('111111'); CHROME = hx('C9D3E0'); CHROME_DK = hx('7F8DA3'); WHITE = hx('FFFFFF')
HARM = hx('FF4433'); GAIN = hx('7BE07B'); SOAK = hx('464EFF'); PLAN = hx('FFE200'); CYAN = hx('5CE1FF'); VIOLET = hx('A03CFF')
WALL = hx('221D2A'); WALL_HI = hx('3A3344'); NAVY = hx('050D1C')


class Cv:
    """a local canvas: screen rect (x0,y0,w,h) at supersample ss.  .a is float32 (H,W,4) straight alpha."""

    def __init__(self, x0, y0, w, h, ss=3):
        self.x0, self.y0, self.w, self.h, self.ss = x0, y0, w, h, ss
        self.H, self.W = int(round(h * ss)), int(round(w * ss))
        self.a = np.zeros((self.H, self.W, 4), np.float32)

    def p(self, x, y):
        return ((x - self.x0) * self.ss, (y - self.y0) * self.ss)

    def grid(self):
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        return xx / self.ss + self.x0, yy / self.ss + self.y0     # screen coords per pixel

    def paint(self, alpha, color, op=1.0):
        over(self.a, alpha * op, color)

    def to_image(self, scale=1):
        a = self.a
        pm = a[..., :3] * a[..., 3:4]
        im = np.concatenate([pm, a[..., 3:4]], -1)
        t = Image.fromarray((np.clip(im, 0, 1) * 65535).astype(np.uint16)[..., 0], 'I;16') if False else None
        # premultiplied downsample (box over ss x ss) for clean edges
        ss = max(1, int(self.ss // scale))
        H, W = self.H // ss * ss, self.W // ss * ss
        im = im[:H, :W].reshape(H // ss, ss, W // ss, ss, 4).mean((1, 3))
        al = im[..., 3:4]
        rgb = np.where(al > 1e-5, im[..., :3] / np.maximum(al, 1e-5), 0)
        out = np.concatenate([rgb, al], -1)
        return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')


def over(dst, alpha, color):
    """straight-alpha 'over'.  alpha (H,W) or scalar, color (3,) or (H,W,3)."""
    alpha = np.clip(alpha, 0, 1).astype(np.float32)
    if alpha.ndim == 2:
        a = alpha[..., None]
    else:
        a = alpha
    col = np.asarray(color, np.float32)
    da = dst[..., 3:4]
    oa = a + da * (1 - a)
    num = col * a + dst[..., :3] * da * (1 - a)
    dst[..., :3] = np.where(oa > 1e-6, num / np.maximum(oa, 1e-6), dst[..., :3])
    dst[..., 3:4] = oa


def lerp(a, b, t):
    return a + (b - a) * t


# ------------------------------------------------------------------ noise
def vnoise(h, w, cell, seed, octaves=1, persist=0.5):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = max(1.0, cell / (2 ** o))
        gh, gw = int(h / c) + 4, int(w / c) + 4
        g = r.random((gh, gw)).astype(np.float32)
        z = ndi.zoom(g, (h / c / (gh - 3) * (gh - 3) / gh * 1.0 + 0.0, 1.0), order=1) if False else None
        zy, zx = c, c
        big = ndi.zoom(g, (zy, zx), order=3, mode='reflect')
        out += big[:h, :w] * amp
        tot += amp
        amp *= persist
    out /= tot
    out = (out - out.min()) / max(1e-6, (out.max() - out.min()))
    return out


def warp(arr, amp, scale, seed):
    """displace by smooth noise (px).  arr (H,W) or (H,W,C)."""
    h, w = arr.shape[:2]
    dx = (vnoise(h, w, scale, seed, 2) - 0.5) * 2 * amp
    dy = (vnoise(h, w, scale, seed + 77, 2) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    co = [yy + dy, xx + dx]
    if arr.ndim == 2:
        return ndi.map_coordinates(arr, co, order=1, mode='nearest')
    return np.stack([ndi.map_coordinates(arr[..., c], co, order=1, mode='nearest') for c in range(arr.shape[2])], -1)


# ------------------------------------------------------------------ mask ops (float 0..1)
def blur(m, s):
    return ndi.gaussian_filter(m, s) if s > 0 else m


def grow(m, px):
    if px <= 0:
        return m
    d = ndi.distance_transform_edt(m < 0.5)
    return np.clip(px + 0.5 - d, 0, 1).astype(np.float32)


def shrink(m, px):
    if px <= 0:
        return m
    d = ndi.distance_transform_edt(m >= 0.5)
    return np.clip(d - px + 0.5, 0, 1).astype(np.float32)


def shift(m, dx, dy):
    return ndi.shift(m, (dy, dx), order=1, mode='constant')


def extrude(m, dx, dy, steps=None):
    n = steps or int(max(abs(dx), abs(dy)) * 1.0) + 1
    out = m.copy()
    for i in range(1, n + 1):
        out = np.maximum(out, shift(m, dx * i / n, dy * i / n))
    return out


def pil_mask(h, w, fn):
    im = Image.new('L', (w, h), 0)
    fn(ImageDraw.Draw(im))
    return np.asarray(im, np.float32) / 255.0


def poly(cv, pts):
    P = [cv.p(*q) for q in pts]
    return pil_mask(cv.H, cv.W, lambda d: d.polygon(P, fill=255))


def circle(cv, x, y, r):
    cx, cy = cv.p(x, y)
    R = r * cv.ss
    return pil_mask(cv.H, cv.W, lambda d: d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=255))


def blur_aa(m, ss):
    return ndi.gaussian_filter(m, 0.45 * ss)


# ------------------------------------------------------------------ the hand: spray
def spray(cv, m, color, seed=1, grain=0.55, soft=0.9, over_s=7.0, over_d=0.5, clip=None, op=1.0, over_op=0.8, over_alpha=None):
    """spray-paint a mask: soft edge, grain, overspray dots falling off outside the shape."""
    ss = cv.ss
    r = np.random.default_rng(seed)
    core = blur(m, soft * ss * 0.8)
    n = ndi.gaussian_filter(r.random(m.shape).astype(np.float32), 0.55 * ss)
    n = (n - n.mean()) / (n.std() + 1e-6)
    sup = np.clip(blur(m, 1.6 * ss) * 4.0, 0, 1)
    a = np.clip(core + sup * grain * 0.16 * n * (0.30 + 3.0 * core * (1 - core) + 0.35 * core), 0, 1)
    if over_d > 0:
        od = np.clip(blur(m, over_s * ss) * 2.6, 0, 1) * (1 - np.clip(m * 1.0, 0, 1))
        dots = (r.random(m.shape) < od * over_d * 0.55 / (ss * ss) * 3.0).astype(np.float32)
        dots = np.clip(ndi.gaussian_filter(dots, 0.55 * ss) * 5.0, 0, 1) * over_op * (0.45 + 0.55 * r.random(m.shape))
        a = np.maximum(a, dots)
    if clip is not None:
        a = a * clip
    cv.paint(a, color, op)
    return a


def fill_flat(cv, m, color, op=1.0, soft=0.45):
    cv.paint(blur(m, soft * cv.ss), color, op)


def paint_grad(cv, m, c0, c1, t, seed=1, grain=0.35, op=1.0, soft=0.7):
    """spray with a colour fade: t (H,W) in 0..1 picks c0..c1 per pixel"""
    col = lerp(c0[None, None, :], c1[None, None, :], np.clip(t, 0, 1)[..., None])
    return spray(cv, m, col, seed=seed, grain=grain, soft=soft, over_d=0, op=op)


# ------------------------------------------------------------------ strokes and shapes
def smooth_path(pts, n=14):
    pts = np.asarray(pts, np.float32)
    if len(pts) < 3:
        t = np.linspace(0, 1, n)
        return np.stack([lerp(pts[0, 0], pts[-1, 0], t), lerp(pts[0, 1], pts[-1, 1], t)], 1)
    P = np.vstack([pts[0], pts, pts[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out, np.float32)


def stroke_mask(cv, pts, w0, w1=None, wob=0.0, seed=0, smooth=True, taper=(0.0, 0.0), step=0.7):
    """a tapered, wobbling marker / paint-pen stroke through screen points; widths in px (screen)."""
    w1 = w0 if w1 is None else w1
    P = smooth_path(pts) if smooth and len(pts) > 2 else np.asarray(pts, np.float32)
    # resample by arclength
    seg = np.hypot(*(np.diff(P, axis=0).T))
    L = np.concatenate([[0], np.cumsum(seg)])
    n = max(2, int(L[-1] / step))
    s = np.linspace(0, L[-1], n)
    X = np.interp(s, L, P[:, 0]); Y = np.interp(s, L, P[:, 1])
    r = np.random.default_rng(seed)
    if wob > 0:
        dx, dy = np.gradient(X), np.gradient(Y)
        nl = np.hypot(dx, dy) + 1e-6
        nx, ny = -dy / nl, dx / nl
        k = max(3, int(n / 9))
        off = ndi.zoom(r.standard_normal(max(4, k)), n / max(4, k), order=3)[:n] * wob
        X = X + nx * off; Y = Y + ny * off
    t = np.linspace(0, 1, n)
    wd = lerp(w0, w1, t)
    if taper[0] > 0:
        wd = wd * np.clip(t / taper[0], 0.18, 1) ** 0.6
    if taper[1] > 0:
        wd = wd * np.clip((1 - t) / taper[1], 0.18, 1) ** 0.6
    im = Image.new('L', (cv.W, cv.H), 0)
    d = ImageDraw.Draw(im)
    for x, y, w in zip(X, Y, wd):
        cx, cy = cv.p(x, y)
        R = w * cv.ss / 2
        d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    return np.asarray(im, np.float32) / 255.0


def drip_mask(cv, x, y, length, width, seed=0):
    r = np.random.default_rng(seed)
    pts = [(x + math.sin(i * 0.8 + seed) * 0.5, y + length * i / 6) for i in range(7)]
    m = stroke_mask(cv, pts, width * 0.62, width * 0.5, smooth=True)
    bx, by = x + math.sin(6 * 0.8 + seed) * 0.5, y + length
    bulb = circle(cv, bx, by, width * 0.72)
    m = np.maximum(m, bulb)
    neck = stroke_mask(cv, [(x, y - 2), (x, y + length * 0.3)], width * 1.1, width * 0.6, smooth=False)
    return np.maximum(m, neck)


def hatch_mask(cv, region, angles=(45, 135), pitch=5.0, width=1.6, jitter=0.5, seed=0, bbox=None):
    """hand-drawn hatch lines (screen px units) clipped to region.  Each line slightly off-true."""
    ss = cv.ss
    r = np.random.default_rng(seed)
    im = Image.new('L', (cv.W, cv.H), 0)
    d = ImageDraw.Draw(im)
    diag = math.hypot(cv.w, cv.h)
    cx, cy = cv.w / 2, cv.h / 2
    for ai, ang in enumerate(angles):
        th = math.radians(ang)
        dx, dy = math.cos(th), math.sin(th)
        nx, ny = -dy, dx
        k = -diag / 2
        while k < diag / 2:
            kk = k + r.normal(0, jitter)
            ox, oy = cx + nx * kk, cy + ny * kk
            ang_j = r.normal(0, 0.8) * math.pi / 180
            ddx, ddy = math.cos(th + ang_j), math.sin(th + ang_j)
            x0, y0 = ox - ddx * diag, oy - ddy * diag
            x1, y1 = ox + ddx * diag, oy + ddy * diag
            d.line([(x0 * ss, y0 * ss), (x1 * ss, y1 * ss)], fill=255, width=max(1, int(width * ss * (0.85 + 0.3 * r.random()))))
            k += pitch * (0.9 + 0.2 * r.random())
    m = np.asarray(im, np.float32) / 255.0
    return m * region


def text_mask(cv, txt, x, y, fontname, px, anchor='mm', skew=0.0, rot=0.0, track=0.0, wob=0.0, seed=0, stroke=0):
    """render text into a mask at screen position (x,y)."""
    ss = cv.ss
    f = font(fontname, px * ss)
    # lay out char by char for tracking
    widths = [f.getlength(ch) for ch in txt]
    tw = sum(widths) + track * ss * (len(txt) - 1)
    asc, desc = f.getmetrics()
    pad = int(px * ss * 0.8)
    Wt, Ht = int(tw + 2 * pad), int(asc + desc + 2 * pad)
    im = Image.new('L', (Wt, Ht), 0)
    d = ImageDraw.Draw(im)
    xx = pad
    for ch, wch in zip(txt, widths):
        d.text((xx, pad), ch, font=f, fill=255, stroke_width=int(stroke * ss))
        xx += wch + track * ss
    # bbox centre
    bb = im.getbbox() or (0, 0, Wt, Ht)
    cxm, cym = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    if skew:
        im = im.transform(im.size, Image.AFFINE, (1, skew, -skew * cym, 0, 1, 0), resample=Image.BICUBIC)
    if rot:
        im = im.rotate(-rot, resample=Image.BICUBIC, center=(cxm, cym))
    a = np.asarray(im, np.float32) / 255.0
    if wob > 0:
        a = warp(a, wob * ss, 9 * ss, seed)
    out = np.zeros((cv.H, cv.W), np.float32)
    px0, py0 = cv.p(x, y)
    ox, oy = int(round(px0 - cxm)), int(round(py0 - cym))
    if anchor == 'lm':
        ox = int(round(px0 - bb[0]))
    elif anchor == 'rm':
        ox = int(round(px0 - bb[2]))
    ys0, xs0 = max(0, oy), max(0, ox)
    ys1, xs1 = min(cv.H, oy + a.shape[0]), min(cv.W, ox + a.shape[1])
    if ys1 > ys0 and xs1 > xs0:
        out[ys0:ys1, xs0:xs1] = a[ys0 - oy:ys1 - oy, xs0 - ox:xs1 - ox]
    return out


def tag_text(cv, txt, x, y, px, fontname=ANTON, fill=PINK, fill2=None, ink=INK, rim=CHROME, drop=PINK_DK, drop_off=(3.2, 3.6), outline=2.4,
             rim_w=1.6, skew=0.0, rot=0.0, track=0.0, wob=0.5, seed=0, anchor='mm', hi=True, op=1.0, shadow=True):
    """a graffiti 'tag' line: 3D extruded drop, ink keyline, chrome rim, spray-gradient fill, highlight glint."""
    ss = cv.ss
    m = text_mask(cv, txt, x, y, fontname, px, anchor, skew, rot, track, wob, seed)
    out_o = grow(m, (outline + rim_w) * ss)
    if shadow:
        ex = extrude(out_o, drop_off[0] * ss, drop_off[1] * ss)
        cv.paint(blur(ex, 0.5 * ss), drop, op)
        # ink core of the drop (shade)
        cv.paint(blur(np.clip(ex - out_o, 0, 1) * 0.5, 0.4 * ss), INK, op)
    cv.paint(blur(out_o, 0.4 * ss), INK, op)
    if rim_w > 0:
        cv.paint(blur(grow(m, rim_w * ss), 0.35 * ss), rim, op)
    cv.paint(blur(grow(m, 0.0), 0.35 * ss), INK, op * 0.0)
    ys = np.arange(cv.H)[:, None] * np.ones((1, cv.W), np.float32)
    bb = np.argwhere(m > 0.5)
    if len(bb):
        y0, y1 = bb[:, 0].min(), bb[:, 0].max()
        t = np.clip((ys - y0) / max(1, y1 - y0), 0, 1)
    else:
        t = np.zeros_like(ys)
    c2 = fill2 if fill2 is not None else fill * 0.78
    col = lerp(fill[None, None, :], c2[None, None, :], t[..., None] ** 1.4)
    cv.paint(blur(m, 0.35 * ss), col, op)
    if hi:
        g = np.clip(m - shift(m, 1.7 * ss, 1.9 * ss), 0, 1) * m
        cv.paint(blur(g, 0.3 * ss), WHITE, op * 0.85)
    return m


# ------------------------------------------------------------------ surfaces
def wall(cv, region, seed=3, base=WALL, hi=WALL_HI, strength=1.0):
    """concrete / painted-over wall: fbm tonal variation, speckle, buff streaks."""
    ss = cv.ss
    n1 = vnoise(cv.H, cv.W, 38 * ss, seed, 3)
    n2 = vnoise(cv.H, cv.W, 5 * ss, seed + 1, 2)
    sp = np.random.default_rng(seed).random((cv.H, cv.W)).astype(np.float32)
    sp = ndi.gaussian_filter(sp, 0.5 * ss)
    sp = (sp - sp.mean()) / sp.std()
    t = np.clip(0.38 + (n1 - 0.5) * 0.9 * strength + (n2 - 0.5) * 0.5 * strength + sp * 0.07 * strength, 0, 1)
    col = lerp(base[None, None, :], hi[None, None, :], t[..., None])
    cv.paint(region, col)


def paper(w, h, seed=0, ss=3, base=PAPER, wrinkle=1.0, stain=0.5):
    """wheat-paste paper: warm tone, fibre noise, wrinkle ridges, glue sheen.  returns (h*ss,w*ss,3)"""
    H, W = int(h * ss), int(w * ss)
    n1 = vnoise(H, W, 46 * ss, seed, 3)
    ridge = 1 - np.abs(vnoise(H, W, 30 * ss, seed + 5, 3) - 0.5) * 2
    ridge = np.clip((ridge - 0.78) / 0.22, 0, 1)
    ridge = ndi.gaussian_filter(ridge, 0.9 * ss) * wrinkle
    fib = np.random.default_rng(seed).random((H, W)).astype(np.float32)
    fib = ndi.gaussian_filter(fib, 0.6 * ss)
    fib = (fib - fib.mean()) / (fib.std() + 1e-6)
    shade = 1.0 + (n1 - 0.5) * 0.10 - ridge * 0.07 + fib * 0.012
    warm = np.array([1.0, 0.985, 0.94], np.float32)
    col = base[None, None, :] * shade[..., None] * (1 - stain * 0.06 * (n1[..., None] - 0.4) * (1 - warm[None, None, :] + 0.2))
    # tea stain / glue stain
    st = np.clip((vnoise(H, W, 70 * ss, seed + 9, 2) - 0.62) * 3, 0, 1) * stain
    col = col * (1 - st[..., None] * np.array([0.04, 0.09, 0.18], np.float32))
    return np.clip(col, 0, 1), ridge


def torn_mask(w, h, rough=3.0, seed=0, ss=3, fibre=2.2):
    """torn rectangle mask (core) + fibre rim mask.  w,h in px at 1x."""
    H, W = int(h * ss), int(w * ss)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    dmin = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)) / ss
    n = 0.62 * vnoise(H, W, 14 * ss, seed, 2) + 0.38 * vnoise(H, W, 3.2 * ss, seed + 3, 1)
    thr = (n * rough * 2.0) + 0.6
    fib_n = vnoise(H, W, 1.4 * ss, seed + 8, 1)
    core = np.clip((dmin - thr - fibre) * ss * 0.8 + 0.5, 0, 1)
    full = np.clip((dmin - thr + 0.4 * fib_n * fibre) * ss * 0.8 + 0.5, 0, 1)
    return core, full


def tape_mask(cv, x0, y0, x1, y1, seed=0, zig=1.6):
    """a strip of masking tape between two screen points (width = distance perpendicular defined by h param in caller)."""
    raise NotImplementedError


def fbm_cv(cv, cell, seed, octaves=3):
    return vnoise(cv.H, cv.W, cell * cv.ss, seed, octaves)
