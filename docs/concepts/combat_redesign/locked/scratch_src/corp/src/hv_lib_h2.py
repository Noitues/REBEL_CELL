"""hv_lib: drawing + compositing primitives for the hover plates (VISUAL_PLAN H).
 Lit      : the lit-region mask (everything outside drops to k 0.38 value, desaturated)
 pencil   : N family grease-pencil stroke (PLAN yellow, 3 px ink edge, wax grain, no glow)
 channel  : L5 arrowed outline (16 px channel, two 3 px edges, 10 px chevrons at a 24 px pitch, 22 px arrowhead)
 hand     : P family painted stroke (pink, tapered, wobble)
"""
import sys, math, random
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from cv_lib import L2, ppx, C, W, H, INK, anton, mono, plex
import wr_geo as GEO
import cv_board as CB
import plan_patch_h as PP

PINK = (255, 61, 168)
PINK_HI = (255, 150, 210)
PLAN = (255, 226, 0)
HARM = (255, 68, 51)
SOAKC = (70, 78, 255)
GAIN = (123, 224, 123)
SCHED = (255, 140, 26)
ENAMEL = (217, 225, 234)
LIME = (212, 255, 0)
PAPER = (242, 238, 228)
INKC = (12, 10, 22)
VIOLET = (160, 60, 255)
GOLD = (255, 196, 40)
CYAN = (92, 225, 255)
TEXT_MID = (175, 192, 214)


# ------------------------------------------------------------------------------------------------ geometry
def seg_pts(a, b, n=None):
    n = n or max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / 4))
    return [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(n + 1)]


def arc(r, a0, a1, n=None):
    n = n or max(6, int(abs(a1 - a0) / 2))
    return [ppx(C, r, a0 + (a1 - a0) * i / n) for i in range(n + 1)]


def smooth(pts, passes=2):
    p = list(pts)
    for _ in range(passes):
        q = [p[0]]
        for i in range(len(p) - 1):
            a, b = p[i], p[i + 1]
            q.append((a[0] * 0.75 + b[0] * 0.25, a[1] * 0.75 + b[1] * 0.25))
            q.append((a[0] * 0.25 + b[0] * 0.75, a[1] * 0.25 + b[1] * 0.75))
        q.append(p[-1])
        p = q
    return p


def resample(pts, step=3.0):
    out = [pts[0]]
    acc = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        ln = math.hypot(b[0] - a[0], b[1] - a[1])
        if ln == 0:
            continue
        d = step - acc
        while d <= ln:
            t = d / ln
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
            d += step
        acc = (acc + ln) % step if False else (ln - (d - step))
        acc = ln - (d - step)
    if math.hypot(out[-1][0] - pts[-1][0], out[-1][1] - pts[-1][1]) > 0.5:
        out.append(pts[-1])
    return out


def normals(pts):
    ns = []
    for i in range(len(pts)):
        a = pts[max(0, i - 2)]
        b = pts[min(len(pts) - 1, i + 2)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        ns.append((-dy / ln, dx / ln))
    return ns


def tangent_at_end(pts, k=6):
    a = pts[max(0, len(pts) - 1 - k)]
    b = pts[-1]
    ln = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
    return ((b[0] - a[0]) / ln, (b[1] - a[1]) / ln)


# ------------------------------------------------------------------------------------------------ strokes
def pencil(L, pts, w=7.0, col=PLAN, ink=3.0, seed=1, grain=True, cap=True):
    """N: grease pencil. wax stroke w px with a 3 px ink edge, 8 percent wax grain, no glow."""
    pts = resample(smooth(pts, 1), 2.0)
    L.line(pts, INKC, w + 2 * ink)
    L.line(pts, col, w)
    if cap:
        for p in (pts[0], pts[-1]):
            L.ellipse([p[0] - w / 2 - ink, p[1] - w / 2 - ink, p[0] + w / 2 + ink, p[1] + w / 2 + ink], fill=INKC)
        for p in (pts[0], pts[-1]):
            L.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)
    if grain:
        rnd = random.Random(seed)
        dk = tuple(int(c * 0.72) for c in col)
        for p, n in zip(pts[::2], normals(pts)[::2]):
            if rnd.random() < 0.55:
                o = (rnd.random() - 0.5) * (w - 2)
                x, y = p[0] + n[0] * o, p[1] + n[1] * o
                L.ellipse([x - 0.7, y - 0.7, x + 0.7, y + 0.7], fill=dk)


def pencil_poly(L, poly, w=4.0, col=PLAN, ink=2.4, seed=2):
    pp = list(poly) + [poly[0]]
    pencil(L, pp, w, col, ink, seed, True, cap=False)


def hand(L, pts, w=7.0, col=PINK, ink=2.4, seed=3, taper=True, wobble=1.3):
    """P: painted stroke: tapered 3-9 px, 1.5 px wobble, rough second pass"""
    rnd = random.Random(seed)
    base = resample(smooth(pts, 1), 2.5)
    n = len(base)
    ns = normals(base)
    ph = rnd.random() * 6
    pp = []
    for i, (p, nn) in enumerate(zip(base, ns)):
        wob = math.sin(i * 0.33 + ph) * wobble
        pp.append((p[0] + nn[0] * wob, p[1] + nn[1] * wob))
    # tapered: draw successive segments with a varying width
    for i in range(n - 1):
        t = i / max(1, n - 2)
        tw = w * (0.55 + 0.45 * math.sin(math.pi * min(1, t * 1.15 + 0.08))) if taper else w
        L.line([pp[i], pp[i + 1]], INKC, tw + 2 * ink)
    for i in range(n - 1):
        t = i / max(1, n - 2)
        tw = w * (0.55 + 0.45 * math.sin(math.pi * min(1, t * 1.15 + 0.08))) if taper else w
        L.line([pp[i], pp[i + 1]], col, tw)
        L.ellipse([pp[i][0] - tw / 2, pp[i][1] - tw / 2, pp[i][0] + tw / 2, pp[i][1] + tw / 2], fill=col)
    # dry-brush streak
    hi = tuple(min(255, int(c * 0.5 + 255 * 0.5)) for c in col)
    for i in range(0, n - 1, 3):
        if rnd.random() < 0.6:
            nn = ns[i]
            o = (rnd.random() - 0.5) * w * 0.5
            L.line([(pp[i][0] + nn[0] * o, pp[i][1] + nn[1] * o), (pp[min(n - 1, i + 3)][0] + nn[0] * o, pp[min(n - 1, i + 3)][1] + nn[1] * o)], hi, 1.2)


def channel(L, pts, col=PLAN, w=16.0, head=22.0, ink=True, fill=(10, 8, 20, 120), chev=True, tail_dot=False, seed=1, edge=3.0, chev_col=None):
    """L5 arrowed outline: an outline channel (two 3 px edges, translucent floor), inner chevrons 10 px at 24 px pitch pointing the way of travel, 22 px arrowhead."""
    P0 = resample(smooth(pts, 2), 3.0)
    if len(P0) < 4:
        P0 = resample(pts, 3.0)
    tip = P0[-1]
    t = tangent_at_end(P0, 5)
    # stop the channel body where the head starts
    cut = head * 0.78
    body = []
    for p in P0:
        if math.hypot(p[0] - tip[0], p[1] - tip[1]) >= cut or True:
            body.append(p)
    # trim body tail
    acc = 0.0
    i = len(body) - 1
    while i > 0 and acc < cut:
        acc += math.hypot(body[i][0] - body[i - 1][0], body[i][1] - body[i - 1][1])
        i -= 1
    body = body[:i + 1]
    ns = normals(body)
    hw = w / 2
    left = [(p[0] + n[0] * hw, p[1] + n[1] * hw) for p, n in zip(body, ns)]
    right = [(p[0] - n[0] * hw, p[1] - n[1] * hw) for p, n in zip(body, ns)]
    L.poly(left + right[::-1], fill=fill)
    for e in (left, right):
        L.line(e, INKC, edge + 4.5)
    for e in (left, right):
        L.line(e, col, edge)
    # start cap
    L.line([left[0], right[0]], INKC, edge + 4.5)
    L.line([left[0], right[0]], col, edge)
    # chevrons
    if chev:
        cc = chev_col or col
        acc = 12.0
        for j in range(1, len(body)):
            d = math.hypot(body[j][0] - body[j - 1][0], body[j][1] - body[j - 1][1])
            acc += d
            if acc >= 24.0:
                acc = 0.0
                p, n = body[j], ns[j]
                tx, ty = n[1], -n[0]          # forward = (-n.y?) tangent from normal (n = (-dy, dx) -> forward = (dx, dy) = (n[1], -n[0]))
                a = (p[0] - tx * 5 + n[0] * 4.2, p[1] - ty * 5 + n[1] * 4.2)
                b = (p[0] + tx * 4, p[1] + ty * 4)
                c = (p[0] - tx * 5 - n[0] * 4.2, p[1] - ty * 5 - n[1] * 4.2)
                L.line([a, b, c], INKC, 3.4 + 3.0)
                L.line([a, b, c], cc, 3.4)
    # arrowhead
    nx, ny = -t[1], t[0]
    base = (tip[0] - t[0] * head, tip[1] - t[1] * head)
    hw2 = w * 0.95
    hp = [(base[0] + nx * hw2, base[1] + ny * hw2), tip, (base[0] - nx * hw2, base[1] - ny * hw2)]
    L.poly(hp, fill=col + (255,), outline=INKC, w=3.0)
    inner = [(base[0] + nx * hw2 * 0.46 + t[0] * 4, base[1] + ny * hw2 * 0.46 + t[1] * 4), (tip[0] - t[0] * 7, tip[1] - t[1] * 7),
             (base[0] - nx * hw2 * 0.46 + t[0] * 4, base[1] - ny * hw2 * 0.46 + t[1] * 4)]
    L.poly(inner, fill=(10, 8, 20, 230))
    if tail_dot:
        p = P0[0]
        L.ellipse([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6], fill=INKC)
        L.ellipse([p[0] - 3.6, p[1] - 3.6, p[0] + 3.6, p[1] + 3.6], fill=col)


# ------------------------------------------------------------------------------------------------ lit mask + dim
class Lit:
    def __init__(self, ss=2):
        self.ss = ss
        self.im = Image.new('L', (W * ss, H * ss), 0)
        self.d = ImageDraw.Draw(self.im)

    def poly(self, pts, grow=0.0):
        s = self.ss
        pp = [(x * s, y * s) for x, y in pts]
        self.d.polygon(pp, fill=255)
        if grow:
            self.d.line(pp + [pp[0]], fill=255, width=int(grow * 2 * s), joint='curve')

    def box(self, x0, y0, x1, y1, r=6):
        s = self.ss
        self.d.rounded_rectangle([x0 * s, y0 * s, x1 * s, y1 * s], radius=r * s, fill=255)

    def disc(self, r, c=C):
        s = self.ss
        self.d.ellipse([(c[0] - r) * s, (c[1] - r) * s, (c[0] + r) * s, (c[1] + r) * s], fill=255)

    def annulus(self, r0, r1, c=C):
        s = self.ss
        self.d.ellipse([(c[0] - r1) * s, (c[1] - r1) * s, (c[0] + r1) * s, (c[1] + r1) * s], fill=255)
        self.d.ellipse([(c[0] - r0) * s, (c[1] - r0) * s, (c[0] + r0) * s, (c[1] + r0) * s], fill=0)

    def wedge(self, r0, r1, a0, a1, grow=3.0):
        n = max(8, int(abs(a1 - a0) / 2))
        pts = [ppx(C, r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)] + [ppx(C, r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
        self.poly(pts, grow)

    def sector(self, s, r0, r1, half=30.0, grow=3.0):
        self.wedge(r0, r1, 60 * s - half, 60 * s + half, grow)

    def mask(self):
        m = self.im.resize((W, H), Image.LANCZOS)
        return m.filter(ImageFilter.GaussianBlur(1.1))


def dim_image(img, m, k=0.40, desat=0.45):
    """lit where m = 255; elsewhere value x k (VISUAL_PLAN H: k 0.38 / ~0.4) and chroma x desat"""
    a = np.asarray(img.convert('RGB')).astype(np.float32)
    g = a.mean(axis=2, keepdims=True) * 0.0 + (a[..., 0:1] * 0.3 + a[..., 1:2] * 0.59 + a[..., 2:3] * 0.11)
    d = (g + (a - g) * desat) * k
    mm = (np.asarray(m).astype(np.float32) / 255.0)[..., None]
    out = a * mm + d * (1 - mm)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ------------------------------------------------------------------------------------------------ cells and units
def cell_poly_unit(u):
    import wr2_units as WU2
    return WU2.WU.u_poly(u)


def cell_poly_empty(dep, s, w=1):
    return GEO.cell_poly(dep, 60 * s - 30, 60 * (s + w - 1) + 30, kind='empty')


def cell_band(dep):
    return CB.ring_geom(dep)


def unit_ang(u):
    """mid angle of a unit's cell (deg), handles wrap"""
    a0 = 60 * u['s']
    a1 = 60 * (u['s'] + u['w'] - 1)
    return (a0 + a1) / 2.0


def unit_center(u, r=None):
    ri, ro = CB.ring_geom(u['dep'])
    return ppx(C, r or (ri + ro) / 2, unit_ang(u))


def tint_poly(L, poly, col, alpha):
    """alpha-composite a flat colour over poly on the layer (not overwrite)"""
    k = L.k
    t = Image.new('RGBA', L.im.size, (0, 0, 0, 0))
    ImageDraw.Draw(t).polygon([(x * k, y * k) for x, y in poly], fill=tuple(col) + (int(alpha),))
    L.im.alpha_composite(t)


def alpha_layer(layer, a):
    im = layer.im if hasattr(layer, 'im') else layer
    im = im.copy()
    im.putalpha(im.split()[3].point(lambda v: int(v * a)))
    return im


# ------------------------------------------------------------------------------------------------ text chips (review annotations, plate chrome)
def chip(L, x, y, s, size=18, col=PAPER, bg=(10, 12, 20, 235), kind='mono', edge=None, pad=9, anchor='l'):
    tw = L.tw(s, size, kind)
    w, h = tw + pad * 2, size + pad * 1.2
    x0 = x if anchor == 'l' else x - w
    L.rect([x0, y, x0 + w, y + h], fill=bg, outline=edge, w=1.6, r=4)
    L.text((x0 + pad, y + h / 2 + 1), s, size, kind, fill=col, anchor='lm')
    return (x0, y, x0 + w, y + h)


def _lit_line(self, p0, p1, w=18, grow=0):
    s = self.ss
    self.d.line([(p0[0] * s, p0[1] * s), (p1[0] * s, p1[1] * s)], fill=255, width=int(w * s))
    for p in (p0, p1):
        self.d.ellipse([(p[0] - w / 2) * s, (p[1] - w / 2) * s, (p[0] + w / 2) * s, (p[1] + w / 2) * s], fill=255)


Lit.line = _lit_line


def starburst(L, x, y, r, col=PINK, core=(255, 255, 255), n=12, ink=3.0, seed=4, inner=0.52):
    """X FX-D hit frame: a comic starburst panel (spiky, hand-cut) with a white core"""
    rnd = random.Random(seed)
    pts = []
    for i in range(n * 2):
        a = math.pi * i / n + 0.15
        rr = r * (1.0 if i % 2 == 0 else inner) * (0.88 + 0.24 * rnd.random())
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    L.poly(pts, fill=col + (255,), outline=INKC, w=ink)
    pts2 = []
    for i in range(n * 2):
        a = math.pi * i / n + 0.15
        rr = r * 0.55 * (1.0 if i % 2 == 0 else 0.5)
        pts2.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    L.poly(pts2, fill=core + (255,))


def speed_lines(L, x, y, ang_deg, n=5, r0=26, r1=62, col=PINK, w=2.6, seed=5, spread=34):
    rnd = random.Random(seed)
    for i in range(n):
        a = math.radians(ang_deg + (i - (n - 1) / 2) * spread / max(1, n - 1) + (rnd.random() - 0.5) * 4)
        a0 = r0 + rnd.random() * 8
        a1 = r1 + rnd.random() * 10
        p0 = (x + a0 * math.cos(a), y + a0 * math.sin(a))
        p1 = (x + a1 * math.cos(a), y + a1 * math.sin(a))
        L.line([p0, p1], INKC, w + 3.2)
        L.line([p0, p1], col, w)


# ------------------------------------------------------------------------------------------------ round 2 marks
def _ink_then(L, polys, col, w, ink_extra=3.2):
    for p in polys:
        L.line(p, INKC, w + ink_extra)
    for p in polys:
        L.line(p, col, w)


def band_corners(L, ri, ro, a0, a1, w=2.0, leg=12.0, col=LIME):
    """FOCUS (VISUAL_PLAN E / H): four corner brackets only, 12 px legs, 2 px legal / 3.5 px aimed.  Never a full outline. (ri, ro, a0, a1) = a ring-band cell"""
    polys = []
    for r, dr in ((ri, 1), (ro, -1)):
        for a, da in ((a0, 1), (a1, -1)):
            pc = ppx(C, r, a)
            pr = ppx(C, r + dr * leg, a)
            n = 4
            pa = [ppx(C, r, a + da * math.degrees(leg / r) * i / n) for i in range(n, -1, -1)]
            polys.append([pr, pc] + pa[::-1][1:][::-1] if False else [pr, pc] + [ppx(C, r, a + da * math.degrees(leg / r) * i / n) for i in range(1, n + 1)])
    _ink_then(L, polys, col, w)


def rect_corners(L, box, w=2.0, leg=12.0, pad=3.0, col=LIME):
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    polys = []
    for (x, y, dx, dy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        polys.append([(x + dx * leg, y), (x, y), (x, y + dy * leg)])
    _ink_then(L, polys, col, w)


def pencil_oval(L, cx, cy, rx, ry, seed=1, w=3.4, ink=1.8, turns=1.12, col=PLAN, drift=0.07):
    """a hand-drawn grease-pencil ring (overshoots its start, drifts outward) = 'this number changes under the plan'"""
    rnd = random.Random(seed)
    t0 = -2.2 + rnd.random() * 0.8
    n = 64
    pts = []
    for i in range(int(n * turns) + 1):
        f = i / (n * turns)
        t = t0 + 2 * math.pi * turns * f
        k = 1.0 + drift * f + 0.018 * math.sin(3.1 * t + seed)
        pts.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)))
    pencil(L, pts, w=w, col=col, ink=ink, seed=seed, grain=True, cap=False)


def pencil_box(L, box, seed=1, w=3.2, ink=1.7, col=PLAN, pad=3.0):
    x0, y0, x1, y1 = box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad
    rnd = random.Random(seed)
    j = lambda: (rnd.random() - 0.5) * 2.2
    pts = [(x0 + j(), y0 + j()), (x1 + j(), y0 + j()), (x1 + 2 + j(), y1 + j()), (x0 + j(), y1 + 1 + j()), (x0 + j(), y0 - 3 + j())]
    pencil(L, pts, w=w, col=col, ink=ink, seed=seed, grain=True, cap=False)


def lamp(L, x, y, r, col):
    L.ellipse([x - r, y - r, x + r, y + r], fill=col)
