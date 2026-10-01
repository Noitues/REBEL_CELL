"""True low-poly icon kit (round 9 rebuild).

Shapes are straight-edged polygons on a 512-unit canvas (rendered at 2x = 1024 px).
Each polygon is ear-clipped into triangles, then split (shared, jittered midpoints; the
outline is never moved) until no edge is longer than the shape's facet size, so broad
planes get big facets and small features small ones. Each triangle takes one of 3 toon
bands from one top-left light (a pseudo-normal from its offset to the shape's centre)
plus a per-facet tone variation; ink strokes the silhouette; emissive shapes also paint
a soft glow layer.
"""
import math
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

U = 512          # canvas units
K = 2            # px per unit (1024 px images)
INK = (10, 6, 16)
LIGHT = (-0.6, -0.8)
BAHN = 'C:/Windows/Fonts/bahnschrift.ttf'


def mix(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def ramp6(c):
    k, w = (0, 0, 0), (255, 255, 255)
    return [mix(c, k, 0.78), mix(c, k, 0.52), mix(c, k, 0.24), c, mix(c, w, 0.3), mix(c, w, 0.62)]


def ramp(stops, t):
    t = max(0.0, min(1.0, t)) * (len(stops) - 1)
    i = min(int(t), len(stops) - 2)
    return mix(stops[i], stops[i + 1], t - i)


def hsh(*v):
    n = 2166136261
    for x in v:
        n = ((n ^ (int(x) & 0xffffffff)) * 16777619) & 0xffffffff
        n ^= n >> 13
    return (n & 0xffff) / 65535.0


# ------------------------------------------------------------------ geometry
def ngon(cx, cy, rx, ry=None, n=16, rot=-math.pi / 2):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(rot + 2 * math.pi * k / n), cy + ry * math.sin(rot + 2 * math.pi * k / n)) for k in range(n)]


def arc(cx, cy, rx, ry, a0, a1, n):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n)))
            for k in range(n + 1)]


def bar(a, b, w):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    return [(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def thick_path(pts, w):
    """A polyline as one polygon (left side out, right side back)."""
    L, Rr = [], []
    n = len(pts)
    for i in range(n):
        a = pts[max(0, i - 1)]
        b = pts[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy) or 1
        nx, ny = -dy / l * w / 2, dx / l * w / 2
        L.append((pts[i][0] + nx, pts[i][1] + ny))
        Rr.append((pts[i][0] - nx, pts[i][1] - ny))
    return L + Rr[::-1]


def flames(cx, base_y, w, h, n, seed, sharp=0.5):
    """Sharp triangular flame tongues standing on a flat base."""
    rng = random.Random(seed)
    pts = [(cx - w / 2, base_y)]
    for k in range(n):
        x0 = cx - w / 2 + w * k / n
        x1 = cx - w / 2 + w * (k + 1) / n
        env = math.sin(math.pi * (k + 0.5) / n) ** 0.6
        peak = base_y - h * env * rng.uniform(0.6, 1.0)
        valley = base_y - h * env * rng.uniform(0.15, 0.35) * sharp
        pts.append(((x0 + x1) / 2 + rng.uniform(-0.12, 0.12) * (x1 - x0), peak))
        if k < n - 1:
            pts.append((x1, valley))
    pts.append((cx + w / 2, base_y))
    return pts


# ------------------------------------------------------------------ triangulation
def _area(p):
    return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2


def _in_tri(p, a, b, c):
    def s(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])
    d1, d2, d3 = s(p, a, b), s(p, b, c), s(p, c, a)
    neg = d1 < 0 or d2 < 0 or d3 < 0
    pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (neg and pos)


def earclip(pts):
    P = list(pts)
    if _area(P) < 0:
        P = P[::-1]
    idx = list(range(len(P)))
    tris = []
    guard = 0
    while len(idx) > 3 and guard < 10000:
        guard += 1
        found = False
        for i in range(len(idx)):
            a, b, c = idx[i - 1], idx[i], idx[(i + 1) % len(idx)]
            pa, pb, pc = P[a], P[b], P[c]
            cross = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])
            if cross <= 1e-9:
                continue
            if any(_in_tri(P[j], pa, pb, pc) for j in idx if j not in (a, b, c)):
                continue
            tris.append((a, b, c))
            idx.pop(i)
            found = True
            break
        if not found:
            break
    if len(idx) == 3:
        tris.append(tuple(idx))
    return P, tris


def facets(pts, seg, seed):
    """Triangles (as point triples) covering polygon `pts`, edges <= seg, outline kept exact."""
    P, T = earclip(pts)
    V = list(P)
    n0 = len(P)
    outline = {tuple(sorted((i, (i + 1) % n0))) for i in range(n0)}
    mids = {}

    def mid(i, j):
        key = tuple(sorted((i, j)))
        if key in mids:
            return mids[key]
        a, b = V[i], V[j]
        m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        if key not in outline:
            L = math.hypot(b[0] - a[0], b[1] - a[1])
            j1 = (hsh(seed, int(m[0] * 7), int(m[1] * 7)) - 0.5) * L * 0.22
            j2 = (hsh(seed, int(m[1] * 5), int(m[0] * 3)) - 0.5) * L * 0.22
            m = (m[0] + j1, m[1] + j2)
        V.append(m)
        k = len(V) - 1
        mids[key] = k
        if key in outline:
            outline.add(tuple(sorted((i, k))))
            outline.add(tuple(sorted((k, j))))
        return k
    for _ in range(6):
        out = []
        changed = False
        for (a, b, c) in T:
            L = max(math.dist(V[a], V[b]), math.dist(V[b], V[c]), math.dist(V[c], V[a]))
            if L > seg:
                ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
                out += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
                changed = True
            else:
                out.append((a, b, c))
        T = out
        if not changed:
            break
    return [(V[a], V[b], V[c]) for a, b, c in T]


# ------------------------------------------------------------------ canvas
class Icon:
    def __init__(self):
        self.img = Image.new('RGBA', (U * K, U * K), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)
        self.glow = Image.new('RGB', (U * K, U * K), (0, 0, 0))
        self.gd = ImageDraw.Draw(self.glow)
        self.n = 0

    def _p(self, pts):
        return [(x * K, y * K) for x, y in pts]

    def ink(self, pts, w=7, closed=True, col=INK):
        n = len(pts)
        segs = n if closed else n - 1
        for i in range(segs):
            a, b = pts[i], pts[(i + 1) % n]
            self.d.line([(a[0] * K, a[1] * K), (b[0] * K, b[1] * K)], fill=col, width=int(w * K))
        r = w / 2
        for (x, y) in pts:
            self.d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=col)

    def poly(self, pts, col, seg=None, ink=7, emis=False, var=0.08, light=0.0, flat=False, centre=None):
        """A faceted, toon-banded, inked polygon in colour family `col`."""
        self.n += 1
        seed = self.n
        stops = ramp6(col)
        if ink:
            self.ink(pts, ink)
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        c = centre or ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2)
        r = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 or 1
        seg = seg or max(16.0, r * 0.62)
        for k, t in enumerate(facets(pts, seg, seed)):
            mx, my = (t[0][0] + t[1][0] + t[2][0]) / 3, (t[0][1] + t[1][1] + t[2][1]) / 3
            ox, oy = (mx - c[0]) / r, (my - c[1]) / r
            lam = 0.5 + light + 0.75 * (ox * LIGHT[0] + oy * LIGHT[1])
            if flat:
                lam = 0.5 + light
            band = 2 if lam > 0.62 else (1 if lam > 0.3 else 0)
            h = hsh(seed, k, 3)
            tv = (0.34, 0.6, 0.86)[band] + (h - 0.5) * 2 * var
            if hsh(seed, k, 5) < 0.14:
                tv += 0.09 if h < 0.5 else -0.09
            if emis:
                tv = 0.62 + 0.28 * (band / 2) + (h - 0.5) * 0.16
            colr = ramp(stops, tv)
            self.d.polygon(self._p(t), fill=colr, outline=colr)
        if emis:
            self.gd.polygon(self._p(pts), fill=ramp(stops, 0.75))
        if ink:   # re-stroke the outline thinly on top so the silhouette stays crisp over the facets
            self.ink(pts, max(2.0, ink * 0.45))
        return pts

    def group(self, polys, col, ink=7, **kw):
        """Several polygons read as one silhouette: all inks first, then all fills."""
        for p in polys:
            self.ink(p, ink)
        for p in polys:
            self.poly(p, col, ink=0, **kw)

    def solid(self, pts, col, ink=0):
        if ink:
            self.ink(pts, ink)
        self.d.polygon(self._p(pts), fill=col, outline=col)

    def line(self, a, b, w, col):
        self.d.line([(a[0] * K, a[1] * K), (b[0] * K, b[1] * K)], fill=col, width=int(w * K))

    def glowline(self, a, b, w, col):
        self.line(a, b, w, col)
        self.gd.line([(a[0] * K, a[1] * K), (b[0] * K, b[1] * K)], fill=col, width=int(w * 3 * K))

    def text(self, x, y, s, size, col, glow=False):
        f = ImageFont.truetype(BAHN, int(size * K))
        try:
            f.set_variation_by_name('Bold')
        except Exception:
            pass
        self.d.text((x * K, y * K), s, font=f, fill=col, anchor='mm', stroke_width=int(3 * K), stroke_fill=INK)
        if glow:
            self.gd.text((x * K, y * K), s, font=f, fill=col, anchor='mm')

    def star(self, cx, cy, r, col, n=4):
        pts = []
        for k in range(2 * n):
            rr = r if k % 2 == 0 else r * 0.32
            a = -math.pi / 2 + k * math.pi / n
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
        self.poly(pts, col, ink=3, emis=True, seg=999)

    def done(self):
        g = self.glow.filter(ImageFilter.GaussianBlur(26 * K / 2))
        ga = g.convert('L').point(lambda v: min(255, int(v * 1.5)))
        gl = g.convert('RGBA')
        # brighten the blurred colour to its emitter strength
        gl = Image.eval(gl, lambda v: min(255, int(v * 2.2)))
        gl.putalpha(ga)
        out = Image.alpha_composite(gl, self.img)
        return out
