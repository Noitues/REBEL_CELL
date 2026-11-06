"""Circuit Board concept (round 2, direction D): drawing library.
PIL 2x supersampled layers composited over the real Godot plates (numpy float canvas).
Layer kinds: over (alpha), add (additive + bloom), shadow (blurred dark), all optionally masked.
"""
import json, math, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
SS = 2
PLATES = 'D:/rc_scratch/tide_concepts/plates/'
OUT = 'D:/rc_art/art-pass/docs/concepts/tide_raid/D_circuit_board/'

# map camera: uniform zoom + crop of the 1920x1080 plate (documented in NOTES)
ZOOM = 1.6
SRC_C = (700.0, 520.0)
DST_C = (930.0, 540.0)
# ground lattice of the shipped net, in plate px (unit vectors for +p and +q)
LU, LV = 13.75, 8.84


def T(p):
    return ((p[0] - SRC_C[0]) * ZOOM + DST_C[0], (p[1] - SRC_C[1]) * ZOOM + DST_C[1])


PV = (LU * ZOOM, LV * ZOOM)        # +p lattice step on screen (right-down)
QV = (-LU * ZOOM, LV * ZOOM)       # +q lattice step on screen (left-down)


def hx(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def A(c, a):
    return (c[0], c[1], c[2], int(max(0, min(255, a))))


def mix(a, b, t):
    return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))


# ---------------------------------------------------------------- palette
COPPER = hx('C8723C')          # etched copper (dim traces)
COPPER_HI = hx('FFB070')       # copper highlight
TIN = hx('C8D6E0')             # tin pins / pads
INK = hx('07060F')
GRAPH = hx('1C1E2A')           # chip body
GRAPH_TOP = hx('2E3244')
D_BLUE = hx('3F8BFF')          # DRONE: sine
N_MAG = hx('FF40D6')           # NETRUNNER: square (ruled hex)
E_YEL = hx('FFE21A')           # ENFORCER: sawtooth (signal yellow, ruled)
TYPE_COL = {'D': D_BLUE, 'N': N_MAG, 'E': E_YEL}
TIERC = {
    'UNTOUCHED': hx('B8FFF2'),   # mint cyan-white
    'HOLDS': hx('19C9B4'),       # teal
    'SITES_LOST': hx('FFB21E'),  # amber
    'DAMAGED': hx('FF6A1A'),     # orange
    'BREACHED': hx('FF2D44'),    # HARM red
    'CITY_LOST': hx('F3E6F2'),
}
LIME = hx('C6FF2E')            # focus halo only (D25)
PLUM = hx('1B0B22')
PLUM_MID = hx('4A1444')
VEIN = hx('E04A9A')
VEIN_HOT = hx('FFA6D8')
WHITE = (255, 255, 255)
PAPER = hx('F2ECDD')
CRT = hx('0B1D2A')
CYAN = hx('62E6FF')

_FP = 'C:/Windows/Fonts/bahnschrift.ttf'
_FM = 'C:/Windows/Fonts/consolab.ttf'
_fc = {}


def font(sz, mono=False):
    k = (int(sz), mono)
    if k not in _fc:
        f = ImageFont.truetype(_FM if mono else _FP, int(sz * SS))
        if not mono:
            try:
                f.set_variation_by_axes([700, 75])
            except Exception:
                pass
        _fc[k] = f
    return _fc[k]


# ---------------------------------------------------------------- geometry
def rs(pts, step=3.0):
    """resample a polyline at ~step px"""
    out = [tuple(pts[0])]
    for a, b in zip(pts[:-1], pts[1:]):
        d = math.dist(a, b)
        n = max(1, int(d / step))
        for i in range(1, n + 1):
            t = i / n
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return out


def cum(pts):
    c = [0.0]
    for a, b in zip(pts[:-1], pts[1:]):
        c.append(c[-1] + math.dist(a, b))
    return c


def plen(pts):
    return cum(pts)[-1]


def at(pts, s, cl=None):
    cl = cl or cum(pts)
    s = max(0, min(cl[-1], s))
    lo, hi = 0, len(pts) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if cl[m] <= s:
            lo = m
        else:
            hi = m
    seg = cl[hi] - cl[lo]
    t = 0 if seg == 0 else (s - cl[lo]) / seg
    p = (pts[lo][0] + (pts[hi][0] - pts[lo][0]) * t, pts[lo][1] + (pts[hi][1] - pts[lo][1]) * t)
    dx, dy = pts[hi][0] - pts[lo][0], pts[hi][1] - pts[lo][1]
    n = math.hypot(dx, dy) or 1
    return p, (dx / n, dy / n)


def sub(pts, s0, s1):
    cl = cum(pts)
    s0 = max(0, s0)
    s1 = min(cl[-1], s1)
    out = [at(pts, s0, cl)[0]]
    for p, c in zip(pts, cl):
        if s0 < c < s1:
            out.append(p)
    out.append(at(pts, s1, cl)[0])
    return out


def offset(pts, d):
    """offset a polyline by d px to the left of travel with mitre joins"""
    n = len(pts)
    if n < 2:
        return list(pts)
    nm = []
    for a, b in zip(pts[:-1], pts[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nm.append((dy / l, -dx / l))
    out = [(pts[0][0] + nm[0][0] * d, pts[0][1] + nm[0][1] * d)]
    for i in range(1, n - 1):
        a, b = nm[i - 1], nm[i]
        mx, my = a[0] + b[0], a[1] + b[1]
        l2 = mx * mx + my * my
        if l2 < 1e-6:
            out.append((pts[i][0] + a[0] * d, pts[i][1] + a[1] * d))
        else:
            k = 2 * d / l2
            kx, ky = mx * k, my * k
            lim = 2.2 * abs(d)
            lk = math.hypot(kx, ky)
            if lk > lim:
                kx, ky = kx * lim / lk, ky * lim / lk
            out.append((pts[i][0] + kx, pts[i][1] + ky))
    out.append((pts[-1][0] + nm[-1][0] * d, pts[-1][1] + nm[-1][1] * d))
    return out


def clean_spurs(pts, eps=0.6, keep=()):
    """drop A,B,A out-and-back stubs and duplicate points"""
    p = [tuple(q) for q in pts]
    ch = True
    while ch:
        ch = False
        q = [p[0]]
        i = 1
        while i < len(p):
            if math.dist(p[i], q[-1]) < eps:
                i += 1
                ch = True
                continue
            if len(q) >= 2 and math.dist(p[i], q[-2]) < eps and not any(math.dist(q[-1], k) < 1.5 for k in keep):
                q.pop()
                i += 1
                ch = True
                continue
            q.append(p[i])
            i += 1
        p = q
    return p


def waveform(pts, kind, amp, wl, phase=0.0, d0=0.0, env=None):
    """lateral oscilloscope offset of a polyline. kind: sine / square / saw"""
    base = rs(pts, 2.0)
    cl = cum(base)
    out = []
    for i, p in enumerate(base):
        if i == 0:
            dx, dy = base[1][0] - p[0], base[1][1] - p[1]
        else:
            dx, dy = p[0] - base[i - 1][0], p[1] - base[i - 1][1]
        l = math.hypot(dx, dy) or 1
        nx, ny = dy / l, -dx / l
        u = (cl[i] / wl + phase) % 1.0
        if kind == 'sine':
            v = math.sin(u * 2 * math.pi)
        elif kind == 'square':
            v = 1.0 if u < 0.5 else -1.0
        else:
            v = 2 * u - 1 if u < 0.92 else 1 - (u - 0.92) / 0.08 * 2 - 0  # ramp then drop
            if u >= 0.92:
                v = 1 - (u - 0.92) / 0.08 * 2
        e = 1.0 if env is None else env(cl[i], cl[-1])
        o = d0 + amp * v * e
        out.append((p[0] + nx * o, p[1] + ny * o))
    return out


def wave_kind(t):
    return {'D': 'sine', 'N': 'square', 'E': 'saw'}[t]


# ---------------------------------------------------------------- plate / graph
def load_coords(scn, beat):
    return json.load(open(f'{PLATES}coords/{scn}_{beat}.json'))


def build_graph(cd):
    """node positions (plate px) and cleaned link polylines keyed (a,b)"""
    nodes, links = {}, {}
    for l in cd['links']:
        p = l['polyline']
        if not p:
            continue
        p = clean_spurs(p)
        nodes.setdefault(l['a'], tuple(p[0]))
        nodes.setdefault(l['b'], tuple(p[-1]))
        links[(l['a'], l['b'])] = p
        links[(l['b'], l['a'])] = p[::-1]
    return nodes, links


def iso_route(a, b):
    """lattice route between two plate points when no link exists (chamfer + axis)"""
    dp = ((b[0] - a[0]) / LU + (b[1] - a[1]) / LV) / 2
    dq = ((b[1] - a[1]) / LV - (b[0] - a[0]) / LU) / 2
    dp, dq = round(dp), round(dq)
    pts = [a]
    cur = a
    # axis move along p then q
    for (sp, sq) in ((dp, 0), (0, dq)):
        cur = (cur[0] + (sp - sq) * LU, cur[1] + (sp + sq) * LV)
        pts.append(cur)
    return pts


def route(site_path, nodes, links, keep_sites=()):
    out = []
    for a, b in zip(site_path[:-1], site_path[1:]):
        seg = links.get((a, b))
        if seg is None:
            seg = iso_route(nodes[a], nodes[b])
        if out and math.dist(out[-1], seg[0]) < 1.0:
            seg = seg[1:]
        out += seg
    keep = [nodes[k] for k in keep_sites if k in nodes]
    return [T(p) for p in clean_spurs(out, keep=keep)]


def grade_base(path, strength=1.0):
    """zoom the plate and re-grade it: deeper night, bolder windows, solder-mask cool shadows"""
    cp = 'D:/rc_scratch/tide_concepts/d_work/cache_' + os.path.basename(path) + '.npy'
    if os.path.exists(cp):
        return np.load(cp)
    im = Image.open(path).convert('RGB')
    x0 = SRC_C[0] - DST_C[0] / ZOOM
    y0 = SRC_C[1] - DST_C[1] / ZOOM
    im = im.transform((W, H), Image.AFFINE, (1 / ZOOM, 0, x0, 0, 1 / ZOOM, y0), Image.BICUBIC)
    a = np.asarray(im, np.float32) / 255.0
    lum = a.mean(2, keepdims=True)
    # windows / lit things = bright pixels: keep them vivid, crush the mid greys
    lit = np.clip((lum - 0.40) / 0.28, 0, 1)
    dark = a * np.array([0.62, 0.58, 0.86], np.float32) + 0.012
    vivid = np.clip((a - lum) * 1.7 + lum, 0, 1) * 1.05
    out = dark * (1 - lit) + vivid * lit
    out = out * (0.92 + 0.0 * strength)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.55 * (((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.47) / (H * 0.7)) ** 2)
    out = out * np.clip(v, 0.25, 1)[..., None]
    r = np.clip(out * 255, 0, 255)
    np.save(cp, r)
    return r


# ---------------------------------------------------------------- frame
class Frame:
    def __init__(self, base):
        self.a = base.astype(np.float32).copy()
        self.kind = None
        self.im = None

    def L(self, kind='over', bloom=0.0, op=1.0, mask=None, blur=0.0):
        self.flush()
        self.kind, self.bloom, self.op, self.mask, self.blurr = kind, bloom, op, mask, blur
        if kind == 'add':
            self.im = Image.new('RGB', (W * SS, H * SS), (0, 0, 0))
        else:
            self.im = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.bb = [1e9, 1e9, -1e9, -1e9]
        return self

    def _m(self, pts, pad=0.0):
        for p in pts:
            if p[0] - pad < self.bb[0]: self.bb[0] = p[0] - pad
            if p[1] - pad < self.bb[1]: self.bb[1] = p[1] - pad
            if p[0] + pad > self.bb[2]: self.bb[2] = p[0] + pad
            if p[1] + pad > self.bb[3]: self.bb[3] = p[1] + pad

    def flush(self):
        if self.kind is None:
            return
        if self.bb[0] > self.bb[2]:
            self.kind = None
            self.im = None
            return
        pad = 70 if (self.bloom > 0 or self.blurr) else 4
        x0 = max(0, int(self.bb[0] - pad) // 2 * 2)
        y0 = max(0, int(self.bb[1] - pad) // 2 * 2)
        x1 = min(W, (int(self.bb[2] + pad) + 2) // 2 * 2)
        y1 = min(H, (int(self.bb[3] + pad) + 2) // 2 * 2)
        if x1 <= x0 or y1 <= y0:
            self.kind = None
            self.im = None
            return
        cr = self.im.crop((x0 * SS, y0 * SS, x1 * SS, y1 * SS))
        reg = self.a[y0:y1, x0:x1]
        mk = None if self.mask is None else self.mask[y0:y1, x0:x1, None]
        if self.kind == 'add':
            im = cr.reduce(SS)
            rgb = np.asarray(im, np.float32)
            if self.bloom > 0:
                half = im.reduce(2)
                g = 0
                for r, w in ((1.5, 0.7), (5, 0.55), (14, 0.5)):
                    b = half.filter(ImageFilter.GaussianBlur(r)).resize(im.size, Image.BILINEAR)
                    g = g + np.asarray(b, np.float32) * w
                rgb = rgb + self.bloom * g
            rgb = rgb * self.op
            if mk is not None:
                rgb = rgb * mk
            self.a[y0:y1, x0:x1] = 255 - (255 - reg) * (255 - np.clip(rgb, 0, 255)) / 255.0
        else:
            im = cr.convert('RGBa').reduce(SS)
            if self.blurr:
                im = im.filter(ImageFilter.GaussianBlur(self.blurr))
            arr = np.asarray(im, np.float32)
            al = arr[..., 3:4] / 255.0 * self.op
            pm = arr[..., :3] * self.op
            if mk is not None:
                al = al * mk
                pm = pm * mk
            self.a[y0:y1, x0:x1] = reg * (1 - al) + pm
        self.kind = None
        self.im = None

    def img(self):
        self.flush()
        return Image.fromarray(np.clip(self.a, 0, 255).astype(np.uint8))

    # ---- primitives (screen px, 1920 space)
    def line(self, pts, w, col, cap=True):
        self._m(pts, w / 2 + 1)
        pp = [(p[0] * SS, p[1] * SS) for p in pts]
        if len(pp) < 2:
            return
        self.d.line(pp, fill=col, width=max(1, int(round(w * SS))), joint='curve')
        if cap and w >= 2.5:
            r = w * SS / 2
            for p in (pp[0], pp[-1]):
                self.d.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=col)

    def dline(self, pts, w, col, dash=10, gap=8, phase=0.0):
        pts = rs(pts, 2.0)
        cl = cum(pts)
        s = -phase
        L = cl[-1]
        while s < L:
            a, b = max(0, s), min(L, s + dash)
            if b > a:
                self.line(sub(pts, a, b), w, col)
            s += dash + gap

    def poly(self, pts, fill=None, outline=None, w=1):
        self._m(pts, w + 1)
        pp = [(p[0] * SS, p[1] * SS) for p in pts]
        if fill is not None:
            self.d.polygon(pp, fill=fill)
        if outline is not None:
            self.d.line(pp + [pp[0]], fill=outline, width=max(1, int(round(w * SS))), joint='curve')

    def ell(self, c, rx, ry=None, fill=None, outline=None, w=1):
        ry = rx if ry is None else ry
        self._m([(c[0] - rx, c[1] - ry), (c[0] + rx, c[1] + ry)], w + 1)
        self.d.ellipse(((c[0] - rx) * SS, (c[1] - ry) * SS, (c[0] + rx) * SS, (c[1] + ry) * SS),
                       fill=fill, outline=outline, width=max(1, int(round(w * SS))))

    def arc(self, c, rx, ry, a0, a1, w, col):
        self._m([(c[0] - rx, c[1] - ry), (c[0] + rx, c[1] + ry)], w + 1)
        self.d.arc(((c[0] - rx) * SS, (c[1] - ry) * SS, (c[0] + rx) * SS, (c[1] + ry) * SS),
                   a0, a1, fill=col, width=max(1, int(round(w * SS))))

    def rr(self, box, r, fill=None, outline=None, w=1):
        x0, y0, x1, y1 = box
        self._m([(x0, y0), (x1, y1)], w + 1)
        self.d.rounded_rectangle((x0 * SS, y0 * SS, x1 * SS, y1 * SS), r * SS, fill=fill, outline=outline,
                                 width=max(1, int(round(w * SS))))

    def px(self, x, y, sz, col):
        self._m([(x, y), (x + sz, y + sz)], 1)
        self.d.rectangle((x * SS, y * SS, (x + sz) * SS, (y + sz) * SS), fill=col)

    def txt(self, xy, s, size, col, anchor='mm', mono=False, stroke=0, scol=(0, 0, 0)):
        self._m([xy], size * len(s) * 0.7 + 10)
        self.d.text((xy[0] * SS, xy[1] * SS), s, font=font(size, mono), fill=col, anchor=anchor,
                    stroke_width=int(stroke * SS), stroke_fill=scol)


# ---------------------------------------------------------------- iso helpers
def gpt(c, a, b):
    """screen point of a ground offset (a along +p, b along +q lattice units*13.75/8.84 scaled)"""
    return (c[0] + a * PV[0] + b * QV[0], c[1] + a * PV[1] + b * QV[1])


def ground_ring(c, r, n=64, a0=0, a1=2 * math.pi):
    """ellipse on the ground plane (circle seen through the iso camera): ry = rx*0.643"""
    return [(c[0] + math.cos(a0 + (a1 - a0) * i / n) * r, c[1] + math.sin(a0 + (a1 - a0) * i / n) * r * 0.643)
            for i in range(n + 1)]


def box(f, c, s, h, top, left, right, edge=None, pins=None, pin_n=5, ew=1.2):
    """extruded slab on the ground. s: half size in lattice units. returns the top-face corners"""
    N = gpt(c, -s, -s)
    E = gpt(c, s, -s)
    S = gpt(c, s, s)
    Wc = gpt(c, -s, s)
    up = lambda p: (p[0], p[1] - h)
    if pins:  # pins first (they sit under the body)
        for (p0, p1, out) in ((Wc, S, QV), (S, E, PV), (N, Wc, (-PV[0], -PV[1])), (N, E, (-QV[0], -QV[1]))):
            for i in range(pin_n):
                t = (i + 0.5) / pin_n
                q = (p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t)
                f.line([q, (q[0] + out[0] * 0.42, q[1] + out[1] * 0.42)], 2.6, pins, cap=False)
    f.poly([Wc, S, up(S), up(Wc)], left)
    f.poly([S, E, up(E), up(S)], right)
    tp = [up(N), up(E), up(S), up(Wc)]
    f.poly(tp, top)
    if edge:
        f.poly(tp, None, edge, ew)
        f.line([up(Wc), up(S), up(E)], ew, edge, cap=False)
    return tp


def cyl(f, c, r, h, body, top, rim=None):
    """vertical cylinder standing on the ground at c (screen)"""
    ry = r * 0.643
    f.ell((c[0], c[1]), r, ry, fill=body)
    f.poly([(c[0] - r, c[1]), (c[0] - r, c[1] - h), (c[0] + r, c[1] - h), (c[0] + r, c[1])], body)
    f.ell((c[0], c[1] - h), r, ry, fill=top, outline=rim, w=1.2)


# ---------------------------------------------------------------- glyphs
def glyph(f, name, c, r, col, w=None, fill=None):
    """simple bold icon set drawn with lines/polys. r = radius in px"""
    x, y = c
    w = w or max(2, r * 0.22)
    if name == 'sine':
        pts = [(x - r + 2 * r * i / 24, y - math.sin(i / 24 * 2 * math.pi) * r * 0.55) for i in range(25)]
        f.line(pts, w, col)
    elif name == 'square':
        k = r * 0.55
        f.line([(x - r, y + k), (x - r, y - k), (x - r / 3, y - k), (x - r / 3, y + k), (x + r / 3, y + k),
                (x + r / 3, y - k), (x + r, y - k), (x + r, y + k)], w, col)
    elif name == 'saw':
        k = r * 0.6
        f.line([(x - r, y + k), (x - r / 2, y - k), (x - r / 2, y + k), (x, y - k), (x, y + k), (x + r / 2, y - k),
                (x + r / 2, y + k), (x + r, y - k)], w, col)
    elif name in ('D', 'N', 'E'):
        glyph(f, wave_kind(name), c, r, col, w)
    elif name == 'heart':
        pts = []
        for i in range(41):
            t = i / 40 * 2 * math.pi
            hx_ = 16 * math.sin(t) ** 3
            hy_ = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
            pts.append((x + hx_ / 17 * r, y + hy_ / 17 * r + r * 0.05))
        f.poly(pts, fill, col, w)
    elif name == 'crack_heart':
        glyph(f, 'heart', c, r, col, w, fill)
        f.line([(x + r * .1, y - r * .75), (x - r * .25, y - r * .15), (x + r * .2, y + r * .15), (x - r * .1, y + r * .8)],
               w * 0.9, (8, 6, 16))
    elif name == 'shield':
        pts = [(x - r * .8, y - r * .8), (x, y - r), (x + r * .8, y - r * .8), (x + r * .75, y + r * .1),
               (x, y + r), (x - r * .75, y + r * .1)]
        f.poly(pts, fill, col, w)
    elif name == 'ring':
        f.ell(c, r, r, fill, col, w)
    elif name == 'broken_link':
        f.line([(x - r, y + r * .3), (x - r * .25, y - r * .1)], w * 1.3, col)
        f.line([(x + r * .25, y + r * .1), (x + r, y - r * .3)], w * 1.3, col)
        f.line([(x - r * .15, y - r * .8), (x + r * .15, y - r * .45)], w, col)
        f.line([(x - r * .15, y + r * .45), (x + r * .15, y + r * .8)], w, col)
    elif name == 'x':
        f.line([(x - r, y - r), (x + r, y + r)], w * 1.2, col)
        f.line([(x + r, y - r), (x - r, y + r)], w * 1.2, col)
    elif name == 'wrench':
        f.line([(x - r * .8, y + r * .8), (x + r * .35, y - r * .35)], w * 1.5, col)
        f.ell((x + r * .45, y - r * .45), r * .5, r * .5, None, col, w * 1.1)
        f.poly([(x + r * .3, y - r * .9), (x + r * .55, y - r * .45), (x + r * .85, y - r * .7)], (0, 0, 0, 0))
    elif name == 'flame':
        pts = [(x, y - r), (x + r * .55, y - r * .1), (x + r * .6, y + r * .45), (x, y + r),
               (x - r * .6, y + r * .45), (x - r * .5, y - r * .05), (x - r * .15, y + r * .1)]
        f.poly(pts, fill or col, None)
    elif name == 'house':
        f.poly([(x - r, y), (x, y - r), (x + r, y), (x + r * .75, y), (x + r * .75, y + r * .8), (x - r * .75, y + r * .8),
                (x - r * .75, y)], fill or col)
    elif name == 'chev':
        f.line([(x - r * .5, y - r * .8), (x + r * .4, y), (x - r * .5, y + r * .8)], w * 1.3, col)
    elif name == 'dchev':
        glyph(f, 'chev', (x - r * .45, y), r, col, w)
        glyph(f, 'chev', (x + r * .35, y), r, col, w)
    elif name == 'skull':
        f.ell((x, y - r * .15), r * .85, r * .8, fill or col)
        f.rr((x - r * .5, y + r * .35, x + r * .5, y + r * .95), r * .15, fill or col)
        f.ell((x - r * .33, y - r * .1), r * .24, r * .26, (8, 4, 14))
        f.ell((x + r * .33, y - r * .1), r * .24, r * .26, (8, 4, 14))
        f.poly([(x, y + r * .08), (x - r * .1, y + r * .3), (x + r * .1, y + r * .3)], (8, 4, 14))
        for k in (-.25, 0, .25):
            f.line([(x + r * k, y + r * .55), (x + r * k, y + r * .92)], r * .08, (8, 4, 14), cap=False)
    elif name == 'lock':
        f.arc((x, y - r * .25), r * .5, r * .55, 180, 360, w, col)
        f.line([(x - r * .5, y - r * .25), (x - r * .5, y - r * .05)], w, col, cap=False)
        f.line([(x + r * .5, y - r * .25), (x + r * .5, y - r * .05)], w, col, cap=False)
        f.rr((x - r * .75, y - r * .05, x + r * .75, y + r * .85), r * .15, fill or col)
    elif name == 'unlock':
        f.arc((x + r * .4, y - r * .45), r * .5, r * .55, 180, 360, w, col)
        f.line([(x - r * .1, y - r * .45), (x - r * .1, y - r * .05)], w, col, cap=False)
        f.rr((x - r * .75, y - r * .05, x + r * .75, y + r * .85), r * .15, fill or col)
    elif name == 'plus':
        f.line([(x - r, y), (x + r, y)], w * 1.3, col)
        f.line([(x, y - r), (x, y + r)], w * 1.3, col)
    elif name == 'diamond':
        f.poly([(x, y - r), (x + r * .7, y), (x, y + r), (x - r * .7, y)], fill or col)
    elif name == 'card_plus':
        f.rr((x - r * .6, y - r * .8, x + r * .6, y + r * .8), r * .15, None, col, w)
        glyph(f, 'plus', (x, y), r * .35, col, w * .8)
    elif name == 'arrow':
        f.line([(x - r, y), (x + r * .8, y)], w, col)
        f.poly([(x + r, y), (x + r * .35, y - r * .5), (x + r * .35, y + r * .5)], col)


# component illustrations ----------------------------------------------------
def fuse_flat(f, c, s, col=TIN, glass=(150, 200, 230), blown=False):
    """glass cartridge fuse seen from the side. s ~ half length px"""
    x, y = c
    f.rr((x - s, y - s * .34, x + s, y + s * .34), s * .3, fill=(*glass, 150), outline=(230, 245, 255), w=max(1.2, s * .07))
    for sx in (-1, 1):
        f.rr((x + sx * s - s * .22 if sx > 0 else x - s - s * .02, y - s * .38,
              x + s + s * .02 if sx > 0 else x - s + s * .22, y + s * .38), s * .08, fill=col)
    if blown:
        f.line([(x - s * .7, y), (x - s * .25, y - s * .08)], max(1.2, s * .08), (255, 240, 210))
        f.line([(x + s * .25, y + s * .08), (x + s * .7, y)], max(1.2, s * .08), (255, 240, 210))
    else:
        f.line([(x - s * .7, y), (x - s * .35, y - s * .15), (x, y + s * .15), (x + s * .35, y - s * .15),
                (x + s * .7, y)], max(1.4, s * .09), (255, 220, 150))


def jumper_flat(f, c, s, col=TIN, wire=(255, 255, 255)):
    x, y = c
    pts = [(x - s + 2 * s * i / 20, y + s * .45 - math.sin(i / 20 * math.pi) * s * 1.15) for i in range(21)]
    f.line(pts, max(2.5, s * .16), wire)
    for sx in (-1, 1):
        f.ell((x + sx * s, y + s * .48), s * .24, s * .15, col)


def cap_flat(f, c, s, body=(30, 60, 140), stripe=(200, 220, 255)):
    x, y = c
    f.line([(x - s * .3, y + s * .5), (x - s * .3, y + s * 1.0)], 2.4, TIN, cap=False)
    f.line([(x + s * .3, y + s * .5), (x + s * .3, y + s * 1.0)], 2.4, TIN, cap=False)
    f.rr((x - s * .55, y - s * .85, x + s * .55, y + s * .55), s * .18, fill=body, outline=(120, 160, 230), w=1.4)
    f.rr((x - s * .55, y - s * .85, x - s * .3, y + s * .55), s * .1, fill=stripe)
    f.ell((x + s * .05, y - s * .85), s * .5, s * .16, (70, 95, 160))


# ---------------------------------------------------------------- misc
def fbm(shape, seed, octaves=5, base=6):
    rng = np.random.RandomState(seed)
    h, w = shape
    out = np.zeros(shape, np.float32)
    amp = 1.0
    tot = 0
    for o in range(octaves):
        n = base * 2 ** o
        g = rng.rand(n + 1, int(n * w / h) + 2).astype(np.float32)
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        out += np.asarray(im, np.float32) / 255 * amp
        tot += amp
        amp *= 0.5
    return out / tot
