"""Live Nav concept: core drawing library (numpy SDF ribbons + PIL supersampled sprites).
Everything is composited over the real Godot plates using the coords JSON.
"""
import json, math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
PLATES = 'D:/rc_scratch/tide_concepts/plates/'
OUT = 'D:/rc_art/art-pass/docs/concepts/tide_raid/A_live_nav/'

# map camera: uniform zoom + crop of the 1920x1080 plate (documented in NOTES)
ZOOM = 1.55
CEN = (705.0, 535.0)


def T(p):
    return np.array([(p[0] - CEN[0]) * ZOOM + W / 2, (p[1] - CEN[1]) * ZOOM + H / 2])


def hexc(h, a=1.0):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], np.float32)


# ---------------------------------------------------------------- palette
INK = hexc('0C0720')
PAPER = hexc('F6F1E4')
NAVY = hexc('0A1330')
CYAN_UI = hexc('5BE3FF')
D_BLUE = hexc('3D86FF')        # DRONE ribbon
N_MAG = hexc('FF40D6')         # NETRUNNER ribbon (ruled)
E_CHALK = hexc('F4F7FF')       # ENFORCER ribbon
TIER = {
    'UNTOUCHED': hexc('B8FFF2'),   # mint cyan-white
    'HOLDS': hexc('19C9B4'),       # teal
    'SITES_LOST': hexc('FFB21E'),  # amber
    'DAMAGED': hexc('FF6A1A'),     # orange
    'BREACHED': hexc('FF3347'),    # HARM red
}
LIME = hexc('C6FF2E')          # focus halo only (D25)
PLUM = hexc('1A0B1F')
PLUM_MID = hexc('4A1440')
VEIN = hexc('FF3FA8')
HOT = hexc('FFD6F0')
GREASE_Y = hexc('FFD800')
GREASE_R = hexc('FF2A2A')
WIRE = hexc('62E6FF')
TYPE_COL = {'D': D_BLUE, 'N': N_MAG, 'E': E_CHALK}

try:
    _FONT_PATH = 'C:/Windows/Fonts/bahnschrift.ttf'
    ImageFont.truetype(_FONT_PATH, 20)
except Exception:
    _FONT_PATH = 'C:/Windows/Fonts/segoeuib.ttf'


def font(sz, weight=700, wdth=75):
    f = ImageFont.truetype(_FONT_PATH, int(sz))
    try:
        f.set_variation_by_axes([weight, wdth])
    except Exception:
        pass
    return f


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, img):
        self.img = img.astype(np.float32)

    def over(self, col, a, box=None):
        """col: (3,) or (h,w,3); a: (h,w) alpha; box=(x0,y0) offset into the canvas."""
        h, w = a.shape
        x0, y0 = (0, 0) if box is None else box
        # clip
        cx0, cy0 = max(x0, 0), max(y0, 0)
        cx1, cy1 = min(x0 + w, W), min(y0 + h, H)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        a = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0, None]
        if getattr(col, 'ndim', 1) == 3:
            col = col[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
        dst = self.img[cy0:cy1, cx0:cx1]
        self.img[cy0:cy1, cx0:cx1] = dst * (1 - a) + col * a

    def add(self, col, a, box=None):
        h, w = a.shape
        x0, y0 = (0, 0) if box is None else box
        cx0, cy0 = max(x0, 0), max(y0, 0)
        cx1, cy1 = min(x0 + w, W), min(y0 + h, H)
        if cx1 <= cx0 or cy1 <= cy0:
            return
        a = a[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0, None]
        self.img[cy0:cy1, cx0:cx1] += np.asarray(col) * a

    def sprite(self, spr, x, y, shadow=0.0, sh_off=(3, 5), sh_blur=4):
        """spr: float RGBA (h,w,4) 0..1 ; x,y top-left."""
        if shadow > 0:
            al = spr[..., 3]
            pad = sh_blur * 3
            big = np.pad(al, pad)
            im = Image.fromarray((big * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sh_blur))
            sa = np.asarray(im, np.float32) / 255 * shadow
            self.over(INK, sa, (int(x - pad + sh_off[0]), int(y - pad + sh_off[1])))
        self.over(spr[..., :3], spr[..., 3], (int(x), int(y)))

    def save(self, path, q=None):
        out = np.clip(self.img, 0, 1)
        im = Image.fromarray((out * 255 + 0.5).astype(np.uint8))
        im.save(path)
        return im


# ---------------------------------------------------------------- base city
_BASE_CACHE = {}


def grade(a, strength=1.0):
    """Daytime-vibrant 'blue hour' street grade of the night plate (floats 0..1).
    Violet tower bodies are rotated to a lit steel-blue so roads, parks and lit windows carry the colour."""
    im = Image.fromarray((np.clip(a ** 0.64, 0, 1) * 255).astype('uint8')).convert('HSV')
    h = np.asarray(im, np.float32)
    Hh, S, V = h[..., 0], h[..., 1], h[..., 2]
    w = np.clip(1 - np.abs(Hh - 198) / 34, 0, 1)
    H2 = Hh - w * 40
    S2 = S * (1 - w * .42)
    V2 = np.clip(V * (1 + w * .55), 0, 255)
    out = np.stack([H2 % 256, np.clip(S2, 0, 255), V2], -1).astype('uint8')
    g = np.asarray(Image.fromarray(out, 'HSV').convert('RGB'), np.float32) / 255
    l = (g * [.299, .587, .114]).sum(2, keepdims=True)
    g = np.clip(l + (g - l) * 1.55, 0, 1)
    g = g * g * (3 - 2 * g) * .5 + g * .5
    g = np.clip(g * 1.1, 0, 1)
    return a * (1 - strength) + g * strength


def base_city(scn='decay', focus=True):
    key = (scn, focus)
    if key in _BASE_CACHE:
        return _BASE_CACHE[key].copy()
    a = np.asarray(Image.open(PLATES + 'city_noraid_nonet.png').convert('RGB'), np.float32) / 255
    if scn == 'decay':
        a = np.roll(a, -22, 0)
    g = grade(a)
    im = Image.fromarray((np.clip(g, 0, 1) * 255).astype(np.uint8))
    x0 = CEN[0] - W / 2 / ZOOM
    y0 = CEN[1] - H / 2 / ZOOM
    im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + W / ZOOM, y0 + H / ZOOM))
    im = im.filter(ImageFilter.UnsharpMask(1.6, 70, 2))
    arr = np.asarray(im, np.float32) / 255
    soft = np.asarray(im.filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255
    arr = arr * .62 + soft * .38
    arr = (arr - .5) * .86 + .5 + .02
    if focus:
        # area-of-interest falloff like a nav map: the corridor stays vivid, the rest eases back
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        d = np.sqrt(((xx - 930) / 1100) ** 2 + ((yy - 560) / 560) ** 2)
        v = np.clip(1 - 0.42 * np.clip(d - 0.55, 0, 1.2) ** 1.2, 0.55, 1)[..., None]
        arr = arr * v
        # top haze
        hz = np.clip(1 - yy / 330, 0, 1)[..., None] ** 1.6 * 0.30
        arr = arr * (1 - hz) + np.array([0.62, 0.55, 0.85]) * hz * 0.7
    # lit windows / signs bloom like a live night map
    lum = arr.max(2)
    sat_ = arr.max(2) - arr.min(2)
    hot = np.clip(lum - .80, 0, 1) * np.clip(sat_ * 3 + .25, 0, 1)
    hot_im = Image.fromarray((np.clip(hot * 4, 0, 1) * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(5))
    arr = arr + np.asarray(hot_im, np.float32)[..., None] / 255 * arr * .9
    arr = np.clip(arr, 0, 1)
    _BASE_CACHE[key] = arr
    return arr.copy()


# ---------------------------------------------------------------- geometry
def load(scn, beat):
    return json.load(open(PLATES + 'coords/%s_%s.json' % (scn, beat)))


def node_map(d):
    nm = {}
    for l in d['links']:
        pl = l['polyline']
        if not pl:
            continue
        nm.setdefault(l['a'], pl[0])
        nm.setdefault(l['b'], pl[-1])
    return {k: T(v) for k, v in nm.items()}


def clean_poly(raw, nodes):
    """Remove stub spurs (a,b,a), return screen pts + visits {site_id: arclength at junction}."""
    pts = [np.array(T(p)) for p in raw]
    out = []
    spurs = []  # (index in out of junction, tip)
    i = 0
    while i < len(pts):
        p = pts[i]
        if out and np.hypot(*(p - out[-1])) < 0.6:
            i += 1
            continue
        if len(out) >= 1 and i + 1 < len(pts) and np.hypot(*(pts[i + 1] - out[-1])) < 0.6:
            spurs.append((len(out) - 1, p))
            i += 2
            continue
        out.append(p)
        i += 1
    arr = np.array(out)
    cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(arr, axis=0).T))])
    visits = {}
    for idx, tip in spurs:
        best = min(nodes.items(), key=lambda kv: np.hypot(*(kv[1] - tip)))
        visits[best[0]] = float(cum[idx])
    return arr, visits


def seg_key(a, b):
    ka = (round(a[0] / 2), round(a[1] / 2))
    kb = (round(b[0] / 2), round(b[1] / 2))
    return (ka, kb) if ka <= kb else (kb, ka)


def lane_offsets(polys, widths, gap=3.0):
    """polys: list of pts arrays (ordered by draw priority). Returns offset polylines so
    beams sharing a street run side by side like transit lines."""
    users = {}
    for bi, pts in enumerate(polys):
        for i in range(len(pts) - 1):
            users.setdefault(seg_key(pts[i], pts[i + 1]), []).append(bi)
    res = []
    for bi, pts in enumerate(polys):
        new = []
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            k = seg_key(a, b)
            us = users[k]
            tot = sum(widths[u] for u in us) + gap * (len(us) - 1)
            pos = -tot / 2
            for u in us:
                if u == bi:
                    off = pos + widths[u] / 2
                    break
                pos += widths[u] + gap
            ka, kb = k
            ca = np.array(ka, float) * 2
            cb = np.array(kb, float) * 2
            dvec = cb - ca
            n = np.array([-dvec[1], dvec[0]])
            nl = np.hypot(*n)
            n = n / nl if nl > 0 else n
            new.append((a + n * off, b + n * off))
        out = []
        for a, b in new:
            if not out or np.hypot(*(a - out[-1])) > 0.5:
                out.append(a)
            out.append(b)
        res.append(np.array(out))
    return res


def poly_len(pts):
    return float(np.sum(np.hypot(*np.diff(pts, axis=0).T)))


def point_at(pts, s):
    cum = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    s = max(0, min(s, cum[-1]))
    i = int(np.searchsorted(cum, s, side='right') - 1)
    i = min(i, len(pts) - 2)
    seg = cum[i + 1] - cum[i]
    u = 0 if seg == 0 else (s - cum[i]) / seg
    p = pts[i] + (pts[i + 1] - pts[i]) * u
    ang = math.atan2(pts[i + 1][1] - pts[i][1], pts[i + 1][0] - pts[i][0])
    return p, ang


def nearest_s(pts, p):
    """arclength of the polyline point closest to p"""
    best = (1e9, 0)
    cum = 0
    for a, b in zip(pts[:-1], pts[1:]):
        ab = b - a
        L = np.hypot(*ab)
        if L < 1e-6:
            continue
        u = np.clip(np.dot(p - a, ab) / L ** 2, 0, 1)
        q = a + ab * u
        d = np.hypot(*(p - q))
        if d < best[0]:
            best = (d, cum + u * L)
        cum += L
    return best[1]


def sdf(pts, box):
    x0, y0, x1, y1 = box
    X, Y = np.meshgrid(np.arange(x0, x1, dtype=np.float32) + .5, np.arange(y0, y1, dtype=np.float32) + .5)
    best = np.full(X.shape, 1e9, np.float32)
    S = np.zeros(X.shape, np.float32)
    Tt = np.zeros(X.shape, np.float32)
    cum = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        abx, aby = float(b[0] - a[0]), float(b[1] - a[1])
        L2 = abx * abx + aby * aby
        if L2 < 1e-6:
            continue
        L = math.sqrt(L2)
        u = np.clip(((X - a[0]) * abx + (Y - a[1]) * aby) / L2, 0, 1)
        dx = X - (a[0] + u * abx)
        dy = Y - (a[1] + u * aby)
        d = np.sqrt(dx * dx + dy * dy)
        m = d < best
        cr = abx * (Y - a[1]) - aby * (X - a[0])
        best = np.where(m, d, best)
        S = np.where(m, cum + u * L, S)
        Tt = np.where(m, np.sign(cr) * d, Tt)
        cum += L
    return best, S, Tt


def bbox_of(pts, pad):
    x0 = int(max(0, np.min(pts[:, 0]) - pad))
    y0 = int(max(0, np.min(pts[:, 1]) - pad))
    x1 = int(min(W, np.max(pts[:, 0]) + pad))
    y1 = int(min(H, np.max(pts[:, 1]) + pad))
    return x0, y0, x1, y1


def cov(x):
    return np.clip(x + 0.5, 0, 1)


def ribbon(cv, pts, typ, w, fill=None, bands=None, phase=0.0, alpha=1.0, smin=None, smax=None,
           casing=3.0, halo=True, flat=False, dash=(22, 12), chev=30, glow=True):
    """Route ribbon. typ D dashed, N double line, E solid + chevrons. bands = [(s_end, rgb), ...]
    colours the ribbon like ETA traffic. smin/smax clip along the route."""
    box = bbox_of(pts, w + casing + 60)
    x0, y0, x1, y1 = box
    d, S, Tt = sdf(pts, box)
    fillc = TYPE_COL[typ] if fill is None else fill
    if bands is not None:
        ends = np.array([b[0] for b in bands], np.float32)
        cols = np.array([b[1] for b in bands], np.float32)
        idx = np.clip(np.searchsorted(ends, S), 0, len(bands) - 1)
        fillc = cols[idx]
    gate = np.ones_like(S)
    if smin is not None:
        gate *= cov(S - smin)
    if smax is not None:
        gate *= cov(smax - S)
    hw = w / 2
    sp = S + phase
    if typ == 'D':
        P = dash[0] + dash[1]
        m = np.mod(sp, P)
        dmask = cov(dash[0] - m) * cov(m)
        dmask_c = cov(dash[0] + 2 * casing - np.mod(sp + casing, P)) * cov(np.mod(sp + casing, P))
        body = cov(hw - d) * dmask
        cas = cov(hw + casing - d) * dmask_c
        hal = cov(hw + casing + 4 - d) * 0.0 + np.clip(1 - (d - hw - casing) / 6, 0, 1) * 0.30
    elif typ == 'N':
        lw = max(w * 0.34, 3.5)
        cen = hw - lw / 2
        dd = np.abs(np.abs(Tt) - cen)
        body = cov(lw / 2 - dd)
        cas = cov(lw / 2 + casing - dd)
        hal = np.clip(1 - (d - hw - casing) / 6, 0, 1) * 0.30
    else:
        body = cov(hw - d)
        cas = cov(hw + casing - d)
        hal = np.clip(1 - (d - hw - casing) / 6, 0, 1) * 0.30
    if not halo:
        hal = hal * 0
    g = gate * alpha
    if glow and alpha > .5 and fill is not False:
        gl = blur_local(body * gate, 8)
        gl2 = blur_local(body * gate, 22)
        gc = fillc if fillc.ndim == 1 else fillc.reshape(-1, 3).mean(0)
        gc = np.asarray(gc, np.float32)
        gk = .45 if typ == 'E' else 1.0
        cv.add(gc * .75, gl * .9 * alpha * gk, (x0, y0))
        cv.add(gc * .6, gl2 * 1.2 * alpha * gk, (x0, y0))
    # white-ish light edge so ribbons separate from busy cel city
    cv.over(np.array([1, 1, 1], np.float32), hal * g * 0.9, (x0, y0))
    cv.over(INK, cas * g, (x0, y0))
    if typ == 'N':
        cv.over(fillc if fillc.ndim == 1 else fillc, body * g, (x0, y0))
        # hot white core in each line: shape + contrast on plum
        core = cov(max(w * 0.12, 1.2) - np.abs(np.abs(Tt) - cen))
        cv.over(np.array([1, 1, 1], np.float32), core * g * 0.9, (x0, y0))
    elif typ == 'E':
        cv.over(fillc, body * g, (x0, y0))
        P = chev
        sl = np.mod(sp, P)
        tgt = P * 0.62 - 0.95 * np.abs(Tt)
        cm = cov(2.6 - np.abs(sl - tgt)) * cov(hw - 1.5 - d)
        cv.over(INK * 0.9 + 0.1 * fillc if fillc.ndim == 1 else INK, cm * g * 0.85, (x0, y0))
    else:
        cv.over(fillc, body * g, (x0, y0))
        cv.over(np.array([1, 1, 1], np.float32), cov(max(hw * 0.28, 1.0) - np.abs(Tt)) * dmask * g * 0.55, (x0, y0))


def blur_local(a, s):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(s)), np.float32) / 255


def wire(cv, pts, w=3.8, col=WIRE, alpha=0.9, glow=True):
    box = bbox_of(pts, 24)
    x0, y0, x1, y1 = box
    d, S, Tt = sdf(pts, box)
    if glow:
        cv.add(col * 0.5, np.clip(1 - d / 11, 0, 1) ** 2 * 0.35 * alpha, (x0, y0))
    cv.over(INK, cov(w / 2 + 1.6 - d) * 0.85 * alpha, (x0, y0))
    cv.over(col, cov(w / 2 - d) * alpha, (x0, y0))
    cv.over(np.array([1, 1, 1], np.float32), cov(w / 5 - d) * 0.8 * alpha, (x0, y0))


# ---------------------------------------------------------------- sprites
class D:
    """Supersampled PIL drawing wrapper (coords in sprite px, floats ok)."""

    def __init__(self, w, h, ss=4):
        self.w, self.h, self.ss = w, h, ss
        self.im = Image.new('RGBA', (int(w * ss), int(h * ss)), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _c(self, c, a=1.0):
        c = np.asarray(c)
        if c.dtype != np.uint8 and c.max() <= 1.0 + 1e-6:
            c = c * 255
        return (int(c[0]), int(c[1]), int(c[2]), int(255 * a))

    def _p(self, pts):
        return [(float(x) * self.ss, float(y) * self.ss) for x, y in pts]

    def line(self, pts, w, col, a=1.0, round_=True):
        P = self._p(pts)
        self.d.line(P, fill=self._c(col, a), width=max(1, int(w * self.ss)), joint='curve')
        if round_:
            r = w * self.ss / 2
            for x, y in (P[0], P[-1]):
                self.d.ellipse((x - r, y - r, x + r, y + r), fill=self._c(col, a))

    def poly(self, pts, fill=None, out=None, ow=1, a=1.0):
        P = self._p(pts)
        if fill is not None:
            self.d.polygon(P, fill=self._c(fill, a))
        if out is not None:
            self.line(list(pts) + [pts[0]], ow, out, a)

    def ell(self, cx, cy, rx, ry=None, fill=None, out=None, ow=1, a=1.0):
        ry = rx if ry is None else ry
        s = self.ss
        box = ((cx - rx) * s, (cy - ry) * s, (cx + rx) * s, (cy + ry) * s)
        if fill is not None:
            self.d.ellipse(box, fill=self._c(fill, a))
        if out is not None:
            self.d.ellipse(box, outline=self._c(out, a), width=max(1, int(ow * s)))

    def rr(self, x0, y0, x1, y1, r, fill=None, out=None, ow=1, a=1.0):
        s = self.ss
        box = (x0 * s, y0 * s, x1 * s, y1 * s)
        if fill is not None:
            self.d.rounded_rectangle(box, r * s, fill=self._c(fill, a))
        if out is not None:
            self.d.rounded_rectangle(box, r * s, outline=self._c(out, a), width=max(1, int(ow * s)))

    def arc(self, cx, cy, r, a0, a1, w, col, a=1.0):
        s = self.ss
        self.d.arc(((cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s), a0, a1,
                   fill=self._c(col, a), width=max(1, int(w * s)))

    def text(self, x, y, t, f, col, anchor='mm', a=1.0, stroke=0, stroke_col=None):
        s = self.ss
        ff = font(f.size / 1.0 * 1.0, 700, 75) if False else f
        self.d.text((x * s, y * s), t, font=ff, fill=self._c(col, a), anchor=anchor,
                    stroke_width=int(stroke * s), stroke_fill=self._c(stroke_col if stroke_col is not None else INK))

    def out(self, scale=1.0):
        im = self.im.resize((int(self.w * scale), int(self.h * scale)), Image.LANCZOS)
        a = np.asarray(im, np.float32) / 255
        return a


def sfont(sz, ss=4, weight=700, wdth=75):
    return font(sz * ss, weight, wdth)


# ---------------------------------------------------------------- glyph atlas (simple vector glyphs)
def g_shield(d, cx, cy, r, col, out=INK, ow=1.6):
    pts = [(cx - r, cy - r * .85), (cx + r, cy - r * .85), (cx + r, cy + r * .1), (cx, cy + r * 1.05), (cx - r, cy + r * .1)]
    d.poly(pts, col, out, ow)


def g_detour(d, cx, cy, r, col, out=INK, ow=1.6):
    # street-sign hard turn: curved arrow
    d.arc(cx, cy + r * .2, r * .8, 180, 360, r * .38, out)
    d.arc(cx, cy + r * .2, r * .8, 180, 360, r * .2, col)
    d.poly([(cx + r * .8 - r * .5, cy + r * .1), (cx + r * .8 + r * .5, cy + r * .1), (cx + r * .8, cy + r * .75)], col, out, ow * .8)


def g_jam(d, cx, cy, r, col, out=INK, ow=1.6):
    pts = [(cx - r, cy + r * .3), (cx - r * .5, cy - r * .6), (cx, cy + r * .5), (cx + r * .5, cy - r * .6), (cx + r, cy + r * .3)]
    d.line(pts, r * .5, out)
    d.line(pts, r * .28, col)


def g_house(d, cx, cy, r, col, out=INK, ow=1.6):
    d.poly([(cx - r, cy - r * .05), (cx, cy - r), (cx + r, cy - r * .05), (cx + r * .78, cy - r * .05), (cx + r * .78, cy + r * .85),
            (cx - r * .78, cy + r * .85), (cx - r * .78, cy - r * .05)], col, out, ow)
    d.rr(cx - r * .22, cy + r * .2, cx + r * .22, cy + r * .85, 0.5, out)


def g_flame(d, cx, cy, r, col, out=INK, ow=1.4):
    pts = [(cx, cy - r), (cx + r * .55, cy - r * .1), (cx + r * .6, cy + r * .45), (cx + r * .25, cy + r * .95), (cx - r * .25, cy + r * .95),
           (cx - r * .6, cy + r * .45), (cx - r * .4, cy), (cx - r * .15, cy + r * .2)]
    d.poly(pts, col, out, ow)


def g_type(d, typ, cx, cy, r, col, out=INK, ow=1.6):
    if typ == 'D':   # triangle
        d.poly([(cx, cy - r), (cx + r * .95, cy + r * .75), (cx - r * .95, cy + r * .75)], col, out, ow)
    elif typ == 'N':  # square
        d.poly([(cx - r * .8, cy - r * .8), (cx + r * .8, cy - r * .8), (cx + r * .8, cy + r * .8), (cx - r * .8, cy + r * .8)], col, out, ow)
    else:            # circle
        d.ell(cx, cy, r * .85, fill=col, out=out, ow=ow)


def g_skull(d, cx, cy, r, col, eye=INK):
    d.ell(cx, cy - r * .12, r * .88, r * .8, fill=col)
    d.rr(cx - r * .5, cy + r * .3, cx + r * .5, cy + r * .95, r * .12, col)
    d.ell(cx - r * .33, cy - r * .1, r * .24, fill=eye)
    d.ell(cx + r * .33, cy - r * .1, r * .24, fill=eye)
    for k in (-.2, .2):
        d.line([(cx + k * r, cy + r * .55), (cx + k * r, cy + r * .95)], r * .1, eye, round_=False)


def g_x(d, cx, cy, r, col, w=None, out=INK):
    w = r * .42 if w is None else w
    for c, ww in ((out, w + 2.4), (col, w)):
        d.line([(cx - r, cy - r), (cx + r, cy + r)], ww, c)
        d.line([(cx + r, cy - r), (cx - r, cy + r)], ww, c)


def g_site(d, kind, cx, cy, r, col):
    """POI icon badge. kind: stack (T1), diamond (T2 exploit), nut (T2), core (T3)"""
    if kind == 'stack':   # corp tower: tall block + low wing + window slots
        d.rr(cx - r * .62, cy - r * .95, cx + r * .32, cy + r * .95, 0.8, col)
        d.rr(cx + r * .32, cy - r * .1, cx + r * .95, cy + r * .95, 0.8, col)
        for yy in (-.55, -.05, .45):
            d.rr(cx - r * .4, cy + yy * r, cx + r * .1, cy + yy * r + r * .22, 0.4, INK)
    elif kind == 'diamond':
        d.poly([(cx, cy - r), (cx + r * .85, cy), (cx, cy + r), (cx - r * .85, cy)], col)
        d.poly([(cx, cy - r * .42), (cx + r * .36, cy), (cx, cy + r * .42), (cx - r * .36, cy)], INK)
    elif kind == 'nut':
        pts = [(cx + r * math.cos(math.radians(60 * i + 30)), cy + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]
        d.poly(pts, col)
        d.ell(cx, cy, r * .32, fill=INK)
    else:
        d.ell(cx, cy, r, out=col, ow=r * .26)
        d.ell(cx, cy, r * .52, out=col, ow=r * .22)
        d.ell(cx, cy, r * .16, fill=col)


def g_helix(d, cx, cy, r, col):
    pts1 = [(cx + math.sin(t / 6 * math.pi * 2) * r * .55, cy - r + t / 6 * r * 2) for t in range(0, 7)]
    pts2 = [(cx - math.sin(t / 6 * math.pi * 2) * r * .55, cy - r + t / 6 * r * 2) for t in range(0, 7)]
    d.line(pts1, r * .22, col)
    d.line(pts2, r * .22, col)
    for t in (1, 3, 5):
        y = cy - r + t / 6 * r * 2
        d.line([(cx - r * .45, y), (cx + r * .45, y)], r * .14, col, round_=False)


def g_chev(d, cx, cy, r, col, w=None):
    w = r * .45 if w is None else w
    d.line([(cx - r * .5, cy - r), (cx + r * .5, cy), (cx - r * .5, cy + r)], w + 2.2, INK)
    d.line([(cx - r * .5, cy - r), (cx + r * .5, cy), (cx - r * .5, cy + r)], w, col)


def g_nogo(d, cx, cy, r, col):
    d.ell(cx, cy, r, fill=col, out=INK, ow=1.8)
    d.rr(cx - r * .62, cy - r * .16, cx + r * .62, cy + r * .16, 0.8, PAPER)


def g_wrench(d, cx, cy, r, col):
    d.line([(cx - r * .7, cy + r * .7), (cx + r * .35, cy - r * .35)], r * .42, INK)
    d.line([(cx - r * .7, cy + r * .7), (cx + r * .35, cy - r * .35)], r * .26, col)
    d.ell(cx + r * .5, cy - r * .5, r * .5, fill=INK)
    d.ell(cx + r * .5, cy - r * .5, r * .34, fill=col)
    d.poly([(cx + r * .5, cy - r * .5), (cx + r * 1.1, cy - r * .95), (cx + r * .95, cy - r * .2)], INK)


def g_snow(d, cx, cy, r, col):
    for k in range(3):
        a = math.radians(60 * k)
        d.line([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))], r * .3, INK)
    for k in range(3):
        a = math.radians(60 * k)
        d.line([(cx - r * math.cos(a), cy - r * math.sin(a)), (cx + r * math.cos(a), cy + r * math.sin(a))], r * .16, col)


def g_plus(d, cx, cy, r, col):
    d.line([(cx - r, cy), (cx + r, cy)], r * .55 + 2, INK)
    d.line([(cx, cy - r), (cx, cy + r)], r * .55 + 2, INK)
    d.line([(cx - r, cy), (cx + r, cy)], r * .55, col)
    d.line([(cx, cy - r), (cx, cy + r)], r * .55, col)


def g_check(d, cx, cy, r, col):
    pts = [(cx - r * .8, cy), (cx - r * .2, cy + r * .65), (cx + r * .85, cy - r * .6)]
    d.line(pts, r * .5 + 2.4, INK)
    d.line(pts, r * .5, col)


def g_broom(d, cx, cy, r, col):  # CLEAN an INFECTED card: sweep
    d.line([(cx - r * .8, cy + r * .8), (cx + r * .5, cy - r * .5)], r * .3, INK)
    d.line([(cx - r * .8, cy + r * .8), (cx + r * .5, cy - r * .5)], r * .16, col)
    d.poly([(cx + r * .2, cy - r * .8), (cx + r * .95, cy - r * .1), (cx + r * .1, cy + r * .1), (cx - r * .1, cy - r * .6)], col, INK, 1.2)


def g_fork(d, cx, cy, r, col):  # hunter: one of two streets
    d.line([(cx, cy + r), (cx, cy)], r * .36 + 2, INK)
    d.line([(cx, cy), (cx - r * .8, cy - r)], r * .36 + 2, INK)
    d.line([(cx, cy), (cx + r * .8, cy - r)], r * .36 + 2, INK)
    d.line([(cx, cy + r), (cx, cy)], r * .36, col)
    d.line([(cx, cy), (cx - r * .8, cy - r)], r * .36, col)
    d.line([(cx, cy), (cx + r * .8, cy - r)], r * .36, col)


def g_pin_body(d, cx, tipy, r, fill, out=INK, ow=2.0):
    """teardrop pin, tip at (cx, tipy), head circle radius r above."""
    cyh = tipy - r * 2.05
    ang = math.radians(32)
    pts = [(cx, tipy)]
    for t in np.linspace(math.pi / 2 + ang, math.pi * 2.5 - ang, 34):
        pts.append((cx + math.cos(t) * r, cyh - math.sin(t) * r))
    d.poly(pts, fill, out, ow)
    return cyh


# ---------------------------------------------------------------- misc fx helpers
def blur(a, s):
    return np.asarray(Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(s)), np.float32) / 255


def noise_field(seed, sc, shape=(H, W)):
    rng = np.random.RandomState(seed)
    small = rng.rand(int(shape[0] / sc) + 3, int(shape[1] / sc) + 3).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((int(shape[1] + 3 * sc), int(shape[0] + 3 * sc)), Image.BICUBIC)
    return np.asarray(im, np.float32)[:shape[0], :shape[1]] / 255
