"""AAA-2 r2: alternate building shapes (exec'd into scene_aaa.py right after the geometry kit, so box / beam / windows /
roof_trim / Acc / rng are in scope).

Designer note 5: round / cylindrical towers, fat wide blocks, stepped ziggurats, adjoining buildings on shared walls or
podiums, curved facades. Everything here is a prism: a footprint polygon (counter-clockwise seen from above, so the
walls face out) extruded between two heights. The mid row and far city get their windows from the surface shader
(u = x + y, so the grid wraps round a drum); the route row gets explicit window quads (drum_windows).

Two helpers keep the shared build stream (4207) identical, so every V3 building, room and link stays where it was:
  Sink()      build the ORIGINAL geometry into throw-away accumulators (the faces still draw from rng exactly as
              before), then build the replacement;
  OwnRng(s)   build the replacement from its own seed and give the shared stream back untouched.
"""


from contextlib import nullcontext as _nullctx  # noqa: E402


class Sink:
    """Swap SOLID / NEON / WIN for throw-away accumulators (rng draws unchanged: facet_quad still sees acc is SOLID)."""

    def __enter__(self):
        global SOLID, NEON, WIN
        self.keep = (SOLID, NEON, WIN)
        SOLID, NEON, WIN = Acc("sink_s"), Acc("sink_n"), Acc("sink_w")
        return self

    def __exit__(self, *a):
        global SOLID, NEON, WIN
        for acc in (SOLID, NEON, WIN):
            acc.bm.free()
        SOLID, NEON, WIN = self.keep
        return False


class OwnRng:
    """Build from an own seed; the shared stream continues exactly where it was."""

    def __init__(self, seed):
        self.seed = seed

    def __enter__(self):
        self.st = rng.getstate()
        rng.seed(self.seed)
        return self

    def __exit__(self, *a):
        rng.setstate(self.st)
        return False


# ------------------------------------------------------------------ footprints (CCW from above)
def fp_circle(cx, cy, rx, ry=None, n=32, a0=0.0):
    ry = rx if ry is None else ry
    return [(cx + rx * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def fp_rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def fp_curved(x0, y0, x1, y1, bulge, n=14):
    """A block whose street face is an arc (bulge > 0 toward the camera, < 0 a concave crescent)."""
    pts = [(x0 + (x1 - x0) * k / n, y0 - bulge * math.sin(math.pi * k / n)) for k in range(n + 1)]
    return pts + [(x1, y1), (x0, y1)]


def fp_round_corners(x0, y0, x1, y1, r, n=5):
    """A fat block with rounded street corners."""
    pts = []
    for (cx, cy, a0) in ((x0 + r, y0 + r, math.pi), (x1 - r, y0 + r, 1.5 * math.pi)):
        for k in range(n + 1):
            a = a0 + 0.5 * math.pi * k / n
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts + [(x1, y1), (x0, y1)]


def fp_scale(fp, k, cx=None, cy=None):
    cx = sum(p[0] for p in fp) / len(fp) if cx is None else cx
    cy = sum(p[1] for p in fp) / len(fp) if cy is None else cy
    return [(cx + (p[0] - cx) * k, cy + (p[1] - cy) * k) for p in fp]


def prism(fp, z0, z1, col, acc=None, top=True, bottom=False, bid=None, walls=None):
    """Extrude a footprint. walls: optional set of edge indices to build (None = all)."""
    acc = acc or SOLID
    bid = bid or rid()
    n = len(fp)
    for k in range(n):
        if walls is not None and k not in walls:
            continue
        a, b = fp[k], fp[(k + 1) % n]
        acc.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], col, bid)
    if top:
        acc.face([(p[0], p[1], z1) for p in fp], col, bid)
    if bottom:
        acc.face([(p[0], p[1], z0) for p in reversed(fp)], col, bid)
    return bid


def ring_trim(fp, z, col, w=0.25, closed=True, front_only=False, cy=None):
    """A neon (or solid) band along a footprint outline at height z."""
    n = len(fp)
    for k in range(n if closed else n - 1):
        a, b = fp[k], fp[(k + 1) % n]
        if front_only and cy is not None and (a[1] + b[1]) / 2 > cy:
            continue
        beam((a[0], a[1], z), (b[0], b[1], z), w, col, acc=NEON)


def ziggurat(x0, y0, x1, y1, h, tiers, col, inset=2.2, trim=None, curved=0.0):
    """Stepped massing: tier k is inset k * inset on every side; heights fall off so the crown is slim."""
    z = 0.0
    fr = (0.44, 0.22, 0.15, 0.11, 0.08)[:tiers]
    hs = [h * f / sum(fr) for f in fr]
    for k, th in enumerate(hs):
        a, b, c, d = x0 + k * inset, y0 + k * inset * 0.8, x1 - k * inset, y1 - k * inset * 0.6
        fp = fp_curved(a, b, c, d, curved * (1 - 0.2 * k)) if curved else fp_rect(a, b, c, d)
        bid = prism(fp, z, z + th, tuple(v * (1.0 - 0.04 * k) for v in col))
        if trim and k < tiers - 1:
            ring_trim(fp[:len(fp) - 2] if curved else [fp[0], fp[1]], z + th + 0.1, tuple(v * 0.5 for v in trim), 0.2,
                      closed=False)
        z += th
    if trim:
        ring_trim(fp, z + 0.1, trim, 0.25)
    return z


def round_tower(cx, cy, r, h, col, crown=None, n=28, setbacks=((0.62, 0.86), (0.86, 0.72)), spire_h=10.0):
    """A drum tower with two slimmer drums on top (setback rings), a crown band and a spire."""
    prism(fp_circle(cx, cy, r, n=n), 0.0, h * setbacks[0][0], col)
    z = h * setbacks[0][0]
    rr = r
    for k, (zf, rk) in enumerate(setbacks):
        z1 = h * (setbacks[k + 1][0] if k + 1 < len(setbacks) else 1.0)
        rr = r * rk
        prism(fp_circle(cx, cy, rr, n=n), z, z1, tuple(v * 0.94 for v in col))
        if crown:
            ring_trim(fp_circle(cx, cy, rr + 0.15, n=n), z - 0.2, tuple(v * 0.45 for v in crown), 0.18)
        z = z1
    if crown:
        ring_trim(fp_circle(cx, cy, rr + 0.1, n=n), z + 0.1, crown, 0.25)
    if spire_h:
        spire(cx, cy, z, spire_h)
    return z




def curved_block(x0, y0, x1, y1, h, col, bulge, trim, n=16):
    """A fat block with a curved (convex) street facade, floor bands following the curve, roof plant behind."""
    fp = fp_curved(x0, y0, x1, y1, bulge, n)
    prism(fp, 0.0, h, col)
    front = fp[:n + 1]
    z = 8.0
    while z < h - 2:
        ring_trim([(p[0], p[1] - 0.15) for p in front], z, (0.26, 0.25, 0.3), 0.3, closed=False)      # solid-ish band
        z += 8.0
    ring_trim([(p[0], p[1] - 0.1) for p in front], h + 0.1, trim, 0.28, closed=False)
    for k in range(3):
        box(x0 + 3 + k * 7, y0 + 5, h, x0 + 7 + k * 7, y0 + 9, h + 2.4, (0.3, 0.3, 0.34), facet=False)


def terraced_run(x0, y0, x1, y1, heights, col, trim):
    """Adjoining blocks on shared walls, stepping down left to right, each roof a lit terrace with a parapet."""
    n = len(heights)
    w = (x1 - x0) / n
    for k, h in enumerate(heights):
        a, b = x0 + k * w, x0 + (k + 1) * w
        tone = tuple(v * (1.0 - 0.05 * k) for v in col)
        prism(fp_rect(a, y0 + k * 1.2, b, y1), 0.0, h, tone)
        # terrace parapet and a warm planter strip on the stepped roof
        box(a + 0.3, y0 + k * 1.2, h, b - 0.3, y0 + k * 1.2 + 0.4, h + 1.1, tuple(v * 0.8 for v in tone), facet=False)
        quad_y(NEON, a + 1.0, h + 1.2, b - 1.0, h + 1.45, y0 + k * 1.2 + 0.5, tuple(v * 0.45 for v in trim))
        if k:
            # the shared wall shows as a slim pilaster where the run steps down
            box(a - 0.4, y0 + k * 1.2 - 0.4, 0.0, a + 0.4, y0 + k * 1.2, heights[k - 1] + 0.6, tuple(v * 0.7 for v in col),
                facet=False)


def far_alt(shape, x, yy, w, h0, h, c, layer):
    """A far-city building in a non-box shape (same plot, height and colour as the box it replaces)."""
    if shape == "cyl":
        r = w * 0.5
        prism(fp_circle(x + r, yy + r, r, n=24), 0.0, h0, c)
        if h > h0 + 0.5:
            prism(fp_circle(x + r, yy + r, r * 0.55, n=20), h0, h, c)
    elif shape == "zig":
        ziggurat(x, yy, x + w, yy + w, h, 4, c, inset=w * 0.09)
    else:   # fat: wider and lower, rounded street corners
        prism(fp_round_corners(x - w * 0.3, yy, x + w * 1.3, yy + w * 0.9, w * 0.3), 0.0, h * 0.62, c)


def cut_drum(_x0, _x1, _dy, _st, _rf, _col, _trim, _N=44, seed=9302):
    """A route column as a CUT DRUM: radius = half the column's plan diagonal (so it contains the column's box).
    Storeys without a route room are full drum storeys (ribbon windows, ribs, projecting floor plates); storeys in _rf
    (a set of floor indices) keep only the back half of the drum, sliced flat at the column's front plane y = _dy, so a
    room box built there shows in the cut. Returns (cx, cy, r, top)."""
    _cx, _cy = (_x0 + _x1) / 2, _dy + DEPTH / 2
    _R = math.hypot((_x1 - _x0) / 2, DEPTH / 2) + 0.15
    _top = _st * FH
    _WARM = [(1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)]

    def _ang(k):
        return -math.pi / 2 + 2 * math.pi * (k + 0.5) / _N

    def _pt(a, r=_R):
        return (_cx + r * math.cos(a), _cy + r * math.sin(a))

    dr = random.Random(seed)
    circ = [_pt(_ang(k)) for k in range(_N)]
    a_cut = math.asin(max(-1.0, min(1.0, (_dy + 0.02 - _cy) / _R)))     # the angle where the drum meets y = DY
    arc = [_pt(a_cut + (math.pi - 2 * a_cut) * t / 30) for t in range(31)]
    for f in range(_st):
        za, zb = f * FH, (f + 1) * FH
        if f in _rf:
            # the cut storey: only the back half of the drum, open at y = DY (the V3 room box sits inside it)
            for a, b in zip(arc, arc[1:]):
                SOLID.face([(a[0], a[1], za), (b[0], b[1], za), (b[0], b[1], zb), (a[0], a[1], zb)], _col, (0.3, 0.6, 0.2))
            continue
        z1 = zb if f < _st - 1 else _top + 0.8
        prism(circ, za, z1, tuple(v * (0.97 + 0.03 * (f % 2)) for v in _col), top=(f == _st - 1), bottom=(f > 0))
        # ribbon windows: two rows per storey on the facets that face the street or the sides
        for k in range(_N):
            a0, a1 = _ang(k), _ang(k + 1)
            am = (a0 + a1) / 2
            if math.sin(am) > 0.45:
                continue
            for zw0, zw1 in ((za + 1.5, za + 3.4), (za + 4.7, za + 6.6)):
                if f == 0 and zw0 < 4.0:
                    continue
                p0 = _pt(a0 + (a1 - a0) * 0.16, _R + 0.06)
                p1 = _pt(a0 + (a1 - a0) * 0.84, _R + 0.06)
                q = [(p0[0], p0[1], zw0), (p1[0], p1[1], zw0), (p1[0], p1[1], zw1), (p0[0], p0[1], zw1)]
                if dr.random() < 0.40:
                    c = dr.choice(_WARM)
                    s = (0.5 + 0.5 * dr.random()) * 0.5
                    WIN.face(q, (c[0] * s, c[1] * s, c[2] * s), (0, 0, 0))
                else:
                    SOLID.face(q, (0.05, 0.055, 0.07), (0.2, 0.2, 0.3))
            # vertical ribs every second facet (they make the curvature read)
            if k % 2 == 0:
                p = _pt(a0, _R + 0.12)
                beam((p[0], p[1], za + 0.3), (p[0], p[1], z1 - 0.3), 0.16, tuple(v * 0.6 for v in _col))
        if f == 0:
            # street floor: a lit shop band round the front of the drum and an awning ring
            for k in range(_N):
                a0, a1 = _ang(k), _ang(k + 1)
                if math.sin((a0 + a1) / 2) > -0.55:
                    continue
                p0, p1 = _pt(a0, _R + 0.07), _pt(a1, _R + 0.07)
                NEON.face([(p0[0], p0[1], 0.5), (p1[0], p1[1], 0.5), (p1[0], p1[1], 3.4), (p0[0], p0[1], 3.4)],
                          (0.16 * 0.5, 0.83 * 0.5, 1.0 * 0.5), (0, 0, 0))
            prism(fp_circle(_cx, _cy, _R + 1.2, n=_N), 3.8, 4.2, (0.15, 0.4, 0.5), top=True, bottom=True)
    # projecting floor plates at every floor line (full ring; across a cut storey it is the slab edge)
    for f in range(1, _st + 1):
        z = f * FH if f < _st else _top + 0.8
        prism(fp_circle(_cx, _cy, _R + 0.35, n=_N), z - 0.22, z + 0.22, tuple(v * 0.75 for v in _col), top=True, bottom=True)
    ring_trim(fp_circle(_cx, _cy, _R + 0.4, n=_N), _top + 1.15, _trim, 0.28)
    # (the old box edge's blade sign is not rebuilt: on the drum's shoulders it would sit right behind the alley links)
    # roof plant on the back half
    for k in range(3):
        rx, ry = _cx - 4 + k * 3.6, _cy + 2.5 + dr.uniform(0, 2.5)
        box(rx, ry, _top + 0.8, rx + 1.8, ry + 1.2, _top + 2.0, (0.42, 0.42, 0.45), facet=False)
    tube((_cx + 4.0, _cy + 4.0, _top + 2.8), (_cx + 4.0, _cy + 4.0, _top + 6.4), 1.4, (0.36, 0.3, 0.26), n=10)
    return _cx, _cy, _R, _top
