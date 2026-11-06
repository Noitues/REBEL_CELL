"""E "Jack-in" concept: core library.
Everything is composited over the real Godot plates (numpy float canvas + PIL supersampled masks).
Rebuild: python build.py  (frames)  then  python post.py  (strips, colour sims, sheet).
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
PLATES = 'D:/rc_scratch/tide_concepts/plates/'
OUT = 'D:/rc_art/art-pass/docs/concepts/tide_raid/H2_jack_in_settle/'

# camera crop of the 1920x1080 raid plate (uniform zoom; the Solace helix stays in frame)
ZOOM = 1.5
CEN = (722.0, 500.0)
DECAY_SHIFT = 22  # the `decay` scenario plates sit 22 px higher than the city_noraid plate


def T(p, dy=0.0):
    return np.array([(p[0] - CEN[0]) * ZOOM + W / 2, (p[1] + dy - CEN[1]) * ZOOM + H / 2])


def hexc(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


# ------------------------------------------------------------------ palette (NOTES.md lists the hex)
INK = hexc('070515')          # black-ICE body / night ink
VOID = hexc('0A0C24')
LATT = hexc('7FEFFF')         # data-shadow lattice (cyan-white)
LATT_D = hexc('2FB8E8')
TOW = hexc('7C88AE')          # pass 2: ICE towers = quiet steel slate
TOW_D = hexc('55608A')
D_BLUE = hexc('4690FF')       # DRONE (pass 2: lighter azure, higher value for the squint)
N_MAG = hexc('FF40D6')        # NETRUNNER (ruled)
E_YEL = hexc('FFEE3A')        # ENFORCER signal yellow (pass 2: paler, higher value)
TYPE_COL = {'D': D_BLUE, 'N': N_MAG, 'E': E_YEL}
TIER = {
    'UNTOUCHED': hexc('B8FFF2'),
    'HOLDS': hexc('19C9B4'),
    'SITES_LOST': hexc('F29A1A'),
    'DAMAGED': hexc('FF6A1A'),
    'BREACHED': hexc('FF3347'),
}
LIME = hexc('C6FF2E')         # focus halo ONLY (D25)
PLUM = hexc('1A0B1F')
PLUM_MID = hexc('4A1440')
VEIN = hexc('FF3FA8')
HOT = hexc('FFD6F0')
PAPER = hexc('F6F1E4')
GREASE_W = hexc('F6F1E4')     # DOWN mark: white china-marker slash + ring
GREASE_R = hexc('FF2A3A')     # TAKEN mark: red double X
WHITE = np.array([1, 1, 1], np.float32)

_FP = 'C:/Windows/Fonts/bahnschrift.ttf'
_FM = 'C:/Windows/Fonts/consolab.ttf'


import functools


@functools.lru_cache(maxsize=256)
def font(sz, mono=False, wght=700, wdth=75):
    f = ImageFont.truetype(_FM if mono else _FP, int(sz))
    if not mono:
        try:
            f.set_variation_by_axes([wght, wdth])
        except Exception:
            pass
    return f


# ------------------------------------------------------------------ canvas / masks
def blur(a, s):
    if s <= 0:
        return a
    im = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(s))
    return np.asarray(im, np.float32) / 255


def _clip(off, shape):
    """dst/src slices for pasting an (h,w) array at off=(x0,y0) into the frame."""
    x0, y0 = int(off[0]), int(off[1])
    h, w = shape
    cx0, cy0 = max(x0, 0), max(y0, 0)
    cx1, cy1 = min(x0 + w, W), min(y0 + h, H)
    if cx1 <= cx0 or cy1 <= cy0:
        return None
    return (slice(cy0, cy1), slice(cx0, cx1)), (slice(cy0 - y0, cy1 - y0), slice(cx0 - x0, cx1 - x0))


class Cv:
    def __init__(self, img):
        self.img = img.astype(np.float32).copy()

    def add(self, col, m, k=1.0, off=(0, 0)):
        c = _clip(off, m.shape)
        if c is None:
            return
        d, s_ = c
        self.img[d] += np.asarray(col, np.float32) * (m[s_] * k)[..., None]

    def over(self, col, m, k=1.0, off=(0, 0)):
        c = _clip(off, m.shape)
        if c is None:
            return
        d, s_ = c
        a = np.clip(m[s_] * k, 0, 1)[..., None]
        cc = np.asarray(col, np.float32)
        if cc.ndim == 3:
            cc = cc[s_]
        self.img[d] = self.img[d] * (1 - a) + cc * a

    def neon(self, m, col, core=1.0, g1=(4, .75), g2=(14, .5), white=0.0, off=(0, 0)):
        """additive light from a mask: core + two glow radii (+ optional white-hot core)."""
        self.add(col, m, core, off)
        if g1:
            self.add(col, blur(m, g1[0]), g1[1], off)
        if g2:
            self.add(col, blur(m, g2[0]), g2[1], off)
        if white:
            self.add(WHITE, np.clip(m * m, 0, 1), white, off)

    # Lyr helpers (local layers keep their own offset)
    def addL(self, L, col, k=1.0):
        self.add(col, L.m, k, L.off)

    def overL(self, L, col, k=1.0):
        self.over(col, L.m, k, L.off)

    def neonL(self, L, col, **kw):
        self.neon(L.m, col, off=L.off, **kw)

    def out(self):
        return np.clip(self.img, 0, 1)

    def save(self, path):
        im = Image.fromarray((self.out() * 255 + .5).astype(np.uint8))
        im.save(path)
        return im


class Lyr:
    """A supersampled PIL mask. Lyr() = full frame; Lyr(box) = local layer (x0,y0,x1,y1) padded for glow, drawn in
    frame coordinates. .m is the float mask, .off its frame offset."""

    def __init__(self, box=None, ss=2, pad=30):
        self.ss = ss
        if box is None:
            self.off = (0, 0)
            w, h = W, H
        else:
            x0 = int(max(0, math.floor(box[0] - pad)))
            y0 = int(max(0, math.floor(box[1] - pad)))
            x1 = int(min(W, math.ceil(box[2] + pad)))
            y1 = int(min(H, math.ceil(box[3] + pad)))
            self.off = (x0, y0)
            w, h = max(2, x1 - x0), max(2, y1 - y0)
        self.w, self.h = w, h
        self.im = Image.new('L', (w * ss, h * ss), 0)
        self.d = ImageDraw.Draw(self.im)

    def P(self, pts):
        s = self.ss
        ox, oy = self.off
        return [((float(x) - ox) * s, (float(y) - oy) * s) for x, y in pts]

    def line(self, pts, w=2, v=255, dash=None):
        s = self.ss
        P = self.P(pts)
        if dash:
            on, off = dash
            for a, b in zip(P[:-1], P[1:]):
                a = np.array(a); b = np.array(b)
                L = np.hypot(*(b - a))
                if L < 1e-6:
                    continue
                u = (b - a) / L
                t = 0
                while t < L:
                    t2 = min(t + on * s, L)
                    self.d.line([tuple(a + u * t), tuple(a + u * t2)], fill=v, width=max(1, int(w * s)))
                    t += (on + off) * s
        else:
            self.d.line(P, fill=v, width=max(1, int(w * s)), joint='curve')

    def poly(self, pts, v=255, outline=None, ow=1):
        P = self.P(pts)
        if outline is None:
            self.d.polygon(P, fill=v)
        else:
            self.d.polygon(P, fill=v if v is not None else None, outline=outline, width=int(ow * self.ss))

    def ell(self, c, rx, ry=None, v=255, outline=False, ow=2):
        ry = rx if ry is None else ry
        s = self.ss
        ox, oy = self.off
        box = ((c[0] - rx - ox) * s, (c[1] - ry - oy) * s, (c[0] + rx - ox) * s, (c[1] + ry - oy) * s)
        if outline:
            self.d.ellipse(box, outline=v, width=max(1, int(ow * s)))
        else:
            self.d.ellipse(box, fill=v)

    def rr(self, x0, y0, x1, y1, r, v=255, outline=False, ow=2):
        s = self.ss
        ox, oy = self.off
        box = ((x0 - ox) * s, (y0 - oy) * s, (x1 - ox) * s, (y1 - oy) * s)
        if outline:
            self.d.rounded_rectangle(box, r * s, outline=v, width=max(1, int(ow * s)))
        else:
            self.d.rounded_rectangle(box, r * s, fill=v)

    def arc(self, c, r, a0, a1, w=2, v=255):
        s = self.ss
        ox, oy = self.off
        self.d.arc(((c[0] - r - ox) * s, (c[1] - r - oy) * s, (c[0] + r - ox) * s, (c[1] + r - oy) * s), a0, a1, fill=v, width=max(1, int(w * s)))

    def text(self, xy, t, size, v=255, anchor='mm', mono=False, stroke=0):
        s = self.ss
        ox, oy = self.off
        f = font(size * s, mono)
        self.d.text(((xy[0] - ox) * s, (xy[1] - oy) * s), t, font=f, fill=v, anchor=anchor, stroke_width=int(stroke * s), stroke_fill=v)

    @property
    def m(self):
        im = self.im.reduce(self.ss) if self.ss > 1 else self.im
        return np.asarray(im, np.float32) / 255

    def full(self):
        out = np.zeros((H, W), np.float32)
        c = _clip(self.off, (self.h, self.w))
        if c:
            out[c[0]] = self.m[c[1]]
        return out


def pbox(pts, pad=0):
    a = np.asarray(pts, float).reshape(-1, 2)
    return (a[:, 0].min() - pad, a[:, 1].min() - pad, a[:, 0].max() + pad, a[:, 1].max() + pad)


def iso_diamond(c, a, k=0.643):
    return [(c[0], c[1] - a * k), (c[0] + a, c[1]), (c[0], c[1] + a * k), (c[0] - a, c[1])]


def ring_pts(c, r, n=48, k=0.643, a0=0, a1=360):
    return [(c[0] + r * math.cos(math.radians(a)), c[1] + r * k * math.sin(math.radians(a))) for a in np.linspace(a0, a1, n)]


# ------------------------------------------------------------------ geometry
def load(scn, beat):
    return json.load(open(PLATES + 'coords/%s_%s.json' % (scn, beat)))


def clean_poly(raw):
    """T() a raw street polyline and drop the (a,b,a) stub spurs. Returns pts array."""
    pts = [T(p) for p in raw]
    out = []
    i = 0
    while i < len(pts):
        p = pts[i]
        if out and np.hypot(*(p - out[-1])) < 0.6:
            i += 1
            continue
        if out and i + 1 < len(pts) and np.hypot(*(pts[i + 1] - out[-1])) < 0.6:
            i += 2
            continue
        out.append(p)
        i += 1
    return np.array(out)


def cum_len(pts):
    return np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])


def plen(pts):
    return float(cum_len(pts)[-1])


def at(pts, s):
    c = cum_len(pts)
    s = max(0.0, min(s, c[-1]))
    i = min(int(np.searchsorted(c, s, side='right') - 1), len(pts) - 2)
    seg = c[i + 1] - c[i]
    u = 0 if seg < 1e-9 else (s - c[i]) / seg
    p = pts[i] + (pts[i + 1] - pts[i]) * u
    ang = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
    return p, ang


def sub(pts, s0, s1, step=3.0):
    """polyline between arclengths s0..s1 (dense, in order)."""
    c = cum_len(pts)
    s0 = max(0, s0); s1 = min(c[-1], s1)
    if s1 <= s0:
        return np.array([at(pts, s0)[0]])
    ss = list(np.arange(s0, s1, step)) + [s1]
    return np.array([at(pts, s)[0] for s in ss])


def nearest_s(pts, p):
    best = (1e9, 0.0)
    cum = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        ab = b - a
        L = float(np.hypot(*ab))
        if L < 1e-6:
            continue
        u = float(np.clip(np.dot(p - a, ab) / L ** 2, 0, 1))
        q = a + ab * u
        d = float(np.hypot(*(p - q)))
        if d < best[0]:
            best = (d, cum + u * L)
        cum += L
    return best[1]


def smooth(pts, r=14.0):
    """round corners (iso streets are hard 60-degree turns; a worm bends round them)."""
    if len(pts) < 3:
        return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1], pts[i], pts[i + 1]
        la, lc = np.hypot(*(b - a)), np.hypot(*(c - b))
        rr = min(r, la * .45, lc * .45)
        p0 = b + (a - b) / max(la, 1e-6) * rr
        p2 = b + (c - b) / max(lc, 1e-6) * rr
        for t in np.linspace(0, 1, 7):
            out.append((1 - t) ** 2 * p0 + 2 * t * (1 - t) * b + t ** 2 * p2)
    out.append(pts[-1])
    arr = np.array(out)
    keep = [0]
    for i in range(1, len(arr)):
        if np.hypot(*(arr[i] - arr[keep[-1]])) > 0.8:
            keep.append(i)
    return arr[keep]


# ------------------------------------------------------------------ base city
_BASE = {}


def _hsv(a):
    mx = a.max(2); mn = a.min(2); d = mx - mn
    h = np.zeros_like(mx)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = d > 1e-6
    rc = m & (mx == r); gc = m & (mx == g) & ~rc; bc = m & ~rc & ~gc
    h[rc] = ((g - b)[rc] / d[rc]) % 6
    h[gc] = (b - r)[gc] / d[gc] + 2
    h[bc] = (r - g)[bc] / d[bc] + 4
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h * 60.0, s, mx


def _rgb(h, s, v):
    h = (h % 360) / 60.0
    c = v * s
    x = c * (1 - np.abs(h % 2 - 1))
    z = np.zeros_like(h)
    idx = np.floor(h).astype(int) % 6
    R = np.choose(idx, [c, x, z, z, x, c]); G = np.choose(idx, [x, c, c, x, z, z]); B = np.choose(idx, [z, z, x, c, c, x])
    m = v - c
    return np.stack([R + m, G + m, B + m], -1)


def base_city(scn='default', dim=0.90, sat=1.45):
    """The real Godot night plate (no net layer), cropped/zoomed and regraded F-style: night stays night but vivid
    (saturation up, mids down, windows bloom, indigo shadows). Window-yellow/orange is pulled toward warm white so
    the ONLY signal yellow on screen is the E beam and the ONLY orange is DAMAGED."""
    key = (scn, dim, sat)
    if key in _BASE:
        return _BASE[key].copy()
    a = np.asarray(Image.open(PLATES + 'city_noraid_nonet.png').convert('RGB'), np.float32) / 255
    if scn == 'decay':
        a = np.roll(a, -DECAY_SHIFT, 0)
    im = Image.fromarray((a * 255).astype(np.uint8))
    x0 = CEN[0] - W / 2 / ZOOM
    y0 = CEN[1] - H / 2 / ZOOM
    im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + W / ZOOM, y0 + H / ZOOM))
    im = im.filter(ImageFilter.UnsharpMask(1.4, 60, 2))
    a = np.asarray(im, np.float32) / 255
    from scipy.ndimage import gaussian_filter
    lum = (a * np.array([.3, .59, .11], np.float32)).sum(-1, keepdims=True)
    a = lum + (a - lum) * sat
    a = np.clip(a, 0, 1) ** 1.18 * dim + 0.012
    a[..., 2] += (1 - lum[..., 0]) * 0.02
    # yellow / orange windows -> warm white (keeps the glow, drops the signal hue)
    h, s_, v = _hsv(np.clip(a, 0, 1))
    band = np.clip(1 - np.abs(h - 42) / 34, 0, 1)
    s_ = s_ * (1 - .62 * band)
    a = _rgb(h, s_, v)
    lum2 = (a * np.array([.3, .59, .11], np.float32)).sum(-1, keepdims=True)
    bright = np.clip((lum2 - .30) / .30, 0, 1) * a
    bl = np.stack([gaussian_filter(bright[..., k], 4) * 1.1 + gaussian_filter(bright[..., k], 16) * 1.0 for k in range(3)], -1)
    a = 1 - (1 - a) * (1 - np.clip(bl, 0, 1))
    # the plate's bright zig-zag banner (bottom right) is not raid information: quiet it
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    q = np.clip((yy - 900) / 50, 0, 1) * np.clip((xx - 980) / 120, 0, 1)
    a = a * (1 - .72 * q)[..., None]
    _BASE[key] = np.clip(a, 0, 1).astype(np.float32)
    return _BASE[key].copy()


def finish(cv, vig=0.45, scan=0.10, fringe=2.0, seed=3):
    """jack-in post: vignette, scanlines, edge chromatic fringe, faint rain."""
    a = cv.out()
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    v = 1 - vig * np.clip(d - .55, 0, 1.2) ** 1.6
    a = a * v[..., None]
    if fringe:
        edge = np.clip(d - .75, 0, 1)
        sh = int(round(fringe))
        r = np.roll(a[..., 0], sh, 1)
        b = np.roll(a[..., 2], -sh, 1)
        k = np.clip(edge * 2.2, 0, 1)
        a[..., 0] = a[..., 0] * (1 - k) + r * k
        a[..., 2] = a[..., 2] * (1 - k) + b * k
    sl = 1 - scan * (np.mod(yy, 3) == 0)
    a = a * sl[..., None]
    rng = np.random.RandomState(seed)
    rl = Lyr(ss=1)
    for _ in range(170):
        x = rng.randint(0, W); y = rng.randint(0, H); L = rng.randint(14, 40)
        rl.line([(x, y), (x - L * .22, y + L)], 1, 70)
    a = a + np.array([.35, .5, .8], np.float32) * rl.m[..., None] * .10
    return np.clip(a, 0, 1)


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + .5).astype(np.uint8))
