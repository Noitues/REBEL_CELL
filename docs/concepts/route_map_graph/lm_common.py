"""Shared helpers of the standalone landmark modules (halcyon / solace / orbital / rebel_cell _landmark.py): one copy.

    place(K, origin, k)       wrap an HQ-kit K so a kit-unit build lands in the one city (as meridian_landmark.place)
    Recorder                  pure-python accumulator with the city_build.Acc.face contract (used by the .glb export)
    prims                     pure-python ports of the city_build.py primitives (prism, box, cyl, dome, bar, strip,
                              ring_line, annulus, circle, sc, mixc); the export and the HQ-scale shim run the same
                              canonical city code on them, so the model stays ONE model (spec 8.6b)
    make_ctx(...)             a city-style ctx (SimpleNamespace) over any set of accumulators
    kit_ctx(K, k)             a city-style ctx whose faces land in the HQ kit's accumulators, scaled by k (city BU ->
                              kit units); lights are not created (the HQ scene has its own rig)
Pure python, no bpy, no numpy. The primitives are verified face-for-face against the city's own (landmarks dumps).
"""
import math
from types import SimpleNamespace

K_UNITS = 0.2375          # HQ kit storey 8 BU -> city floor 1.9 BU (spec 8.6)
HQ_EMIT_K = 3.0           # emission strength of NEON faces in the kit's emitter accumulators (art value)


# ------------------------------------------------------------------ placing a kit-unit build into the city
class _AccProxy:
    def __init__(self, acc, f):
        self._acc, self._f = acc, f

    def face(self, pts, col, k=0.0):
        self._acc.face([self._f(p) for p in pts], col, k)

    def __getattr__(self, n):
        return getattr(self._acc, n)


def place(K, origin=(0.0, 0.0, 0.0), k=K_UNITS):
    """A copy of K whose accumulators and lights are moved to origin and scaled by k (same as meridian_landmark.place)."""
    ox, oy, oz = origin

    def f(p):
        return (p[0] * k + ox, p[1] * k + oy, p[2] * k + oz)
    K2 = SimpleNamespace(**vars(K))
    K2.A = {n: _AccProxy(a, f) for n, a in K.A.items()}
    K2.Acc = lambda *a, **kw: _AccProxy(K.Acc(*a, **kw), f)

    def add_light(name, kind, loc, energy, col, aim=None, size=0.5, size_y=None, **kw):
        return K.add_light(name, kind, f(loc), energy * k * k, col, aim=None if aim is None else f(aim), size=size * k,
                           size_y=None if size_y is None else size_y * k, **kw)
    K2.add_light = add_light
    K2.place_f = f
    return K2


# ------------------------------------------------------------------ the city accumulator contract
class Recorder:
    """city_build.Acc.face, verbatim contract: per-face col / wc / wl / wm / bid / wet; horizontal faces face up."""

    def __init__(self, name, smooth=False):
        self.name, self.smooth = name, smooth
        self.V, self.F, self.UV = [], [], []
        self.col, self.wc, self.wl, self.wm, self.bid, self.wet = [], [], [], [], [], []

    def face(self, pts, col, uv=None, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0):
        pts = [tuple(p) for p in pts]
        if len(pts) >= 3 and max(p[2] for p in pts) - min(p[2] for p in pts) < 1e-6:
            ar = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
            if ar < 0:
                pts = list(reversed(pts))
                if uv is not None:
                    uv = list(reversed(uv))
        n0 = len(self.V)
        self.V.extend(pts)
        self.F.append(tuple(range(n0, n0 + len(pts))))
        self.UV.extend(uv if uv is not None else [(0.0, 0.0)] * len(pts))
        self.col.append(tuple(col))
        self.wc.append(tuple(wc))
        self.wl.append(wl)
        self.wm.append(wm)
        self.bid.append(bid)
        self.wet.append(wet)


class KitAcc:
    """Adapter: the city .face(pts, col, uv, wc, wl, wm, bid, wet) onto a kit accumulator .face(pts, col, k)."""

    def __init__(self, acc, s, emit=0.0):
        self.acc, self.s, self.emit = acc, s, emit

    def face(self, pts, col, uv=None, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0):
        s = self.s
        self.acc.face([(p[0] * s, p[1] * s, p[2] * s) for p in pts], col, self.emit)


# ------------------------------------------------------------------ vector helpers
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _norm(a):
    L = math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])
    return (a[0] / L, a[1] / L, a[2] / L)


# ------------------------------------------------------------------ the city_build.py primitives, pure python
def quad_uv(p0, p1, z0, z1, u0=0.0, sx=1.0, sy=1.0):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    return [(u0 * sx, z0 * sy), ((u0 + L) * sx, z0 * sy), ((u0 + L) * sx, z1 * sy), (u0 * sx, z1 * sy)], L


def prism(acc, pts, z0, z1, col, ts=1.0, top=True, bottom=False, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0, top_col=None,
          uvs=(1.0, 1.0), vz0=None):
    n = len(pts)
    cx, cy = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    tp = [(cx + (x - cx) * ts, cy + (y - cy) * ts) for (x, y) in pts]
    u = 0.0
    vb = z0 if vz0 is None else vz0
    for i in range(n):
        j = (i + 1) % n
        a, c = pts[i], pts[j]
        uv, L = quad_uv(a, c, vb, vb + (z1 - z0), u, *uvs)
        acc.face([(a[0], a[1], z0), (c[0], c[1], z0), (tp[j][0], tp[j][1], z1), (tp[i][0], tp[i][1], z1)], col, uv,
                 wc, wl, wm if L > 0.9 else 3, bid, wet)
        u += L
    if top:
        acc.face([(x, y, z1) for (x, y) in tp], top_col or col, None, wc, 0, 3, bid, wet)
    if bottom:
        acc.face([(x, y, z0) for (x, y) in reversed(pts)], col, None, wc, 0, 3, bid, wet)
    return tp


def box(acc, x0, y0, z0, x1, y1, z1, col, **kw):
    return prism(acc, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, col, **kw)


def circle(cx, cy, r, n, a0=0.0, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def cyl(acc, cx, cy, z0, z1, r, n, col, ts=1.0, **kw):
    return prism(acc, circle(cx, cy, r, n), z0, z1, col, ts=ts, **kw)


def dome(acc, cx, cy, z, r, col, n=16, rings=6, hemi=True, wet=0, bid=0.0, zscale=1.0, emit=None):
    lo = 0 if hemi else -rings
    for k in range(lo, rings):
        a0, a1 = math.pi / 2 * k / rings, math.pi / 2 * (k + 1) / rings
        r0, r1 = r * math.cos(a0), r * math.cos(a1)
        z0, z1 = z + r * math.sin(a0) * zscale, z + r * math.sin(a1) * zscale
        for i in range(n):
            t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            pts = [(cx + r0 * math.cos(t0), cy + r0 * math.sin(t0), z0), (cx + r0 * math.cos(t1), cy + r0 * math.sin(t1), z0),
                   (cx + r1 * math.cos(t1), cy + r1 * math.sin(t1), z1), (cx + r1 * math.cos(t0), cy + r1 * math.sin(t0), z1)]
            if r1 < 1e-4:
                pts = pts[:3]
            acc.face(pts, col, None, (0, 0, 0), 0, 3, bid, wet)


def bar(acc, p0, p1, w, col, **kw):
    d = _sub(p1, p0)
    if math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2) < 1e-6:
        return
    d = _norm(d)
    up = (0.0, 0.0, 1.0) if abs(d[2]) < 0.95 else (1.0, 0.0, 0.0)
    s = _norm(_cross(d, up))
    s = (s[0] * w / 2, s[1] * w / 2, s[2] * w / 2)
    t = _norm(_cross(d, s))
    t = (t[0] * w / 2, t[1] * w / 2, t[2] * w / 2)
    cs = [(s[0] + t[0], s[1] + t[1], s[2] + t[2]), (-s[0] + t[0], -s[1] + t[1], -s[2] + t[2]),
          (-s[0] - t[0], -s[1] - t[1], -s[2] - t[2]), (s[0] - t[0], s[1] - t[1], s[2] - t[2])]
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(p0[m] + cs[i][m] for m in range(3)), tuple(p0[m] + cs[j][m] for m in range(3)),
                  tuple(p1[m] + cs[j][m] for m in range(3)), tuple(p1[m] + cs[i][m] for m in range(3))], col, None, **kw)


def strip(acc, p0, p1, w, z, col, **kw):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    acc.face([(p0[0] - nx, p0[1] - ny, z), (p1[0] - nx, p1[1] - ny, z), (p1[0] + nx, p1[1] + ny, z), (p0[0] + nx, p0[1] + ny, z)],
             col, None, **kw)


def ring_line(acc, cx, cy, z, r, w, col, n=48, ry=None, **kw):
    ry = r if ry is None else ry
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        bar(acc, (cx + r * math.cos(t0), cy + ry * math.sin(t0), z), (cx + r * math.cos(t1), cy + ry * math.sin(t1), z), w, col, **kw)


def annulus(acc, cx, cy, z, r0, r1, col, n=48, k0=1.0, k1=1.0, z1=None, **kw):
    z1 = z if z1 is None else z1
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        acc.face([(cx + r0 * math.cos(t0), cy + r0 * k0 * math.sin(t0), z1), (cx + r0 * math.cos(t1), cy + r0 * k0 * math.sin(t1), z1),
                  (cx + r1 * math.cos(t1), cy + r1 * k1 * math.sin(t1), z), (cx + r1 * math.cos(t0), cy + r1 * k1 * math.sin(t0), z)],
                 col, None, **kw)


def mixc(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def sc(c, k):
    return tuple(v * k for v in c)


# ------------------------------------------------------------------ ctx builders
def make_ctx(corp, hq, district, accs, camdir, spots=None, cp=None, footprint=None, station=None, hq_lot=(0, 0), seed=0, **extra):
    """A landmarks.landmark_ctx-compatible namespace over the given accumulators (SURF, SMOOTH, NEON, GLASS, STREAK)."""
    spots = [] if spots is None else spots

    def spot_at(target, frm, col, power, cone=30.0):
        spots.append(dict(loc=frm, tgt=target, col=col, power=power, cone=cone))
    d = dict(corp=corp, hq=tuple(hq), hq_lot=tuple(hq_lot), footprint=footprint, mode="main", district=district, seed=seed,
             zw=0.0, wet_cells=set(), camdir=tuple(camdir), SURF=accs["SURF"], SMOOTH=accs["SMOOTH"], NEON=accs["NEON"],
             GLASS=accs.get("GLASS"), STREAK=accs.get("STREAK"), prism=prism, box=box, cyl=cyl, dome=dome, bar=bar,
             strip=strip, ring_line=ring_line, annulus=annulus, circle=circle, sc=sc, mixc=mixc, spot_at=spot_at,
             light_spots=spots, station={} if station is None else station, W=None, O=None, CP=cp)
    d.update(extra)
    return SimpleNamespace(**d)


def kit_ctx(K, corp, district, camdir=(0.0, -1.0), cp=None, k=1.0 / K_UNITS):
    """A city ctx at the HQ centre (0, 0) whose faces go to the kit accumulators, city BU x k -> kit units. SURF / SMOOTH
    -> A["civic"], NEON -> A["trim"] (emission HQ_EMIT_K), GLASS -> A["glass"]. Lights are collected, not created."""
    A = K.A
    accs = dict(SURF=KitAcc(A["civic"], k), SMOOTH=KitAcc(A["civic"], k), NEON=KitAcc(A["trim"], k, HQ_EMIT_K),
                GLASS=KitAcc(A["glass"], k), STREAK=KitAcc(A["trim"], k, HQ_EMIT_K))
    return make_ctx(corp, (0.0, 0.0), district, accs, camdir, cp=cp)
