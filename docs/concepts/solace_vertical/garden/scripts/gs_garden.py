"""Solace culture garden (EX-11): the three building directions, built with the district's mesh builders (sd_lib MB).

    A  "Glass ward"      porcelain clinic plinth + an iron-ribbed Victorian palm house in stepped glass tiers, domed glass crown
    B  "Culture stack"   stacked oval incubator trays (petri dishes) in hex cell skin, mint agar light, a cryo drum on top
    C  "Hanging mountain" a terraced green mountain in a glass diagrid shell, planter-walk ramp, mist waterfall core, seed pod crown

Local frame (BU): origin = centre of the 48 x 42 lot, +x = lot width, +y = back, front edge y = -21. The plaza apron is y -21..-7,
the building mass y -7..21 (28 deep), the glass door is at x 0, y -7. Everything is built into per-material MBs through `ctx.mb(key, smooth)`.

build(kind, ctx, ox, oy, detail, cut) -> dict(levels=...)   detail 0 map (cel), 1 street, 2 inside; cut = the front glazing is open (inside)

Keys used: plain (porcelain / iron / foliage by colour), tw (lit window walls), glass, glassB (very clear), neon / neon_s / neon_l (emission
x vertex prm.r), agar (mint emission, B only), water. No pink anywhere (the Bloom owns pink).
"""
import math
import random

import sd_lib as L

LIME = (0.588, 1.0, 0.275)
MINT = (0.20, 1.0, 0.56)          # B agar: cooler than the helix lime (hue about 145 vs 95 deg), nowhere near the Cell-lime yellow
WARM = (1.0, 0.80, 0.50)
CREAM = (1.0, 0.93, 0.74)
FRONT_Y = -21.0
PLAZA_Y = -7.0                    # the building front line
CY = 7.0                          # centre of the building mass in y
ARCH = 0.0


class Ctx:
    """What the builder needs from the scene script."""
    def __init__(self, mb, cel=False, seed=3, alias=None, celk=1.0):
        self._mb = mb
        self.celk = celk
        self.cel = cel
        self.seed = seed
        self.alias = alias or {}

    def mb(self, key, smooth=False):
        return self._mb(self.alias.get(key, key), smooth)


class G:
    def __init__(self, ctx, ox=0.0, oy=0.0, detail=1, cut=False):
        self.c, self.ox, self.oy, self.detail, self.cut = ctx, ox, oy, detail, cut
        cel = ctx.cel
        k = ctx.celk if cel else 1.0                       # the map's subordination tone: the garden sits under the HQ in luminance contrast
        self.PORC = tuple(c * k for c in ((0.88, 0.92, 0.90) if cel else (0.34, 0.36, 0.33)))
        self.PORC2 = tuple(c * k for c in ((0.72, 0.78, 0.76) if cel else (0.22, 0.24, 0.22)))
        self.IRON = tuple(c * (k if cel else 1.0) for c in ((0.17, 0.22, 0.21) if cel else (0.028, 0.034, 0.032)))
        self.GLASSC = (0.55, 1.0, 0.45, 1.0) if not cel else (0.30 * k, 0.74 * k, 0.50 * k, 1.0)
        self.LEAF = [(0.08, 0.30, 0.12), (0.12, 0.38, 0.14), (0.07, 0.26, 0.16)] if cel else [(0.05, 0.22, 0.07), (0.08, 0.29, 0.08), (0.04, 0.19, 0.09)]
        self.rr = random.Random(ctx.seed)
        self.k = k

    # ---- primitives (local coordinates, offset added)
    def mb(self, key, smooth=False):
        return self.c.mb(key, smooth)

    def box(self, key, x0, y0, z0, x1, y1, z1, col, prm=(0, 0, 0, 0.5), top=True):
        L.box(self.mb(key), x0 + self.ox, y0 + self.oy, z0, x1 + self.ox, y1 + self.oy, z1, col, prm, top)

    def prism(self, key, poly, z0, z1, col, prm=(0, 0, 0, 0.5), top=True):
        L.prism(self.mb(key), [(p[0] + self.ox, p[1] + self.oy) for p in poly], z0, z1, col, prm, top)

    def strip(self, key, a, b, w, z, col, prm):
        L.strip(self.mb(key), (a[0] + self.ox, a[1] + self.oy), (b[0] + self.ox, b[1] + self.oy), w, z, col, prm)

    def flat(self, key, pts, col, prm):
        L.flat_poly(self.mb(key), [(p[0] + self.ox, p[1] + self.oy, p[2]) for p in pts], col, prm)

    def tube(self, key, a, b, r, sides, col, prm=(0, 0, 0, 0.5), smooth=False):
        L.seg_tube(self.mb(key, smooth), (a[0] + self.ox, a[1] + self.oy, a[2]), (b[0] + self.ox, b[1] + self.oy, b[2]), r, sides, col, prm)

    def polytube(self, key, pts, r, sides, col, prm=(0, 0, 0, 0.5), smooth=True):
        """A tube along a polyline (local coords)."""
        P = [(p[0] + self.ox, p[1] + self.oy, p[2]) for p in pts]
        nr = []
        for i in range(len(P)):
            a = P[max(0, i - 1)]
            b = P[min(len(P) - 1, i + 1)]
            T = L._unit(L._sub(b, a))
            n = L._cross(T, (0, 0, 1))
            if L._len(n) < 1e-4:
                n = L._cross(T, (1, 0, 0))
            nr.append(L._unit(n))
        L.sweep(self.mb(key, smooth), P, nr, r, sides, col, prm)

    def elathe(self, key, cx, cy, profile, n, sx, col, prm, smooth=True, a0=0.0, a1=2 * math.pi, closed_ring=True):
        """Surface of revolution scaled by sx in x (an ellipse), over the angle range a0..a1 (a partial range = a cutaway). profile [(r, z)]."""
        mb = self.mb(key, smooth)
        R = max(p[0] for p in profile) or 1.0
        rings = []
        for (r, z) in profile:
            if r < 1e-6:
                rings.append(mb.v((cx + self.ox, cy + self.oy, z), col, prm, (0, z)))
            else:
                rings.append([mb.v((cx + self.ox + r * sx * math.cos(a0 + (a1 - a0) * k / n), cy + self.oy + r * math.sin(a0 + (a1 - a0) * k / n), z),
                                   col, prm, (2 * math.pi * R * sx * k / n * (a1 - a0) / (2 * math.pi), z)) for k in range(n + 1)])
        for i in range(len(profile) - 1):
            a, b = rings[i], rings[i + 1]
            for k in range(n):
                if isinstance(a, int) and isinstance(b, int):
                    continue
                if isinstance(a, int):
                    mb.f(a, b[k + 1], b[k])
                elif isinstance(b, int):
                    mb.f(a[k], a[k + 1], b)
                else:
                    mb.f(a[k], a[k + 1], b[k + 1], b[k])

    def eplate(self, key, cx, cy, z0, z1, rx, ry, n, col, prm=(0, 0, 0, 0.5), smooth=False, ring_only=False):
        """A flat oval slab (cap top and bottom) with side wall."""
        sx = rx / ry
        self.elathe(key, cx, cy, [(0.0, z0), (ry, z0), (ry, z1), (0.0, z1)], n, sx, col, prm, smooth)

    def ering(self, key, cx, cy, z, rx, ry, rt, n, sides, col, prm):
        sx = rx / ry
        prof = [(ry + rt * math.cos(2 * math.pi * k / sides), z + rt * math.sin(2 * math.pi * k / sides)) for k in range(sides + 1)]
        self.elathe(key, cx, cy, prof, n, sx, col, prm, True)

    def edome(self, key, cx, cy, z, rx, ry, h, n, col, prm, rings=6, smooth=True):
        sx = rx / ry
        prof = [(ry * math.cos(math.pi / 2 * k / rings), z + h * math.sin(math.pi / 2 * k / rings)) for k in range(rings + 1)]
        self.elathe(key, cx, cy, prof, n, sx, col, prm, smooth)

    def sphere(self, key, x, y, z, r, n, col, prm):
        L.sphere(self.mb(key, True), x + self.ox, y + self.oy, z, r, n, col, prm)

    def cyl(self, key, x, y, z0, z1, r, n, col, prm=(0, 0, 0, 0.5), cap=True, smooth=False):
        L.cyl(self.mb(key, smooth), x + self.ox, y + self.oy, z0, z1, r, n, col, prm, cap)

    def torus(self, key, x, y, z, R, rt, n, sides, col, prm):
        L.torus(self.mb(key, True), x + self.ox, y + self.oy, z, R, rt, n, sides, col, prm)

    # ---- small things
    def neon(self, key="neon"):
        return key

    def stair(self, x0, y, z0, x1, z1, w, col, rail=True, lit=LIME):
        """A straight stair along x on the glass front: treads from (x0, z0) up to (x1, z1), width w in y (centre y)."""
        n = max(3, int(abs(z1 - z0) / 0.55))
        for i in range(n):                                      # open treads (thin plates) on two stringers: light passes under
            xa = x0 + (x1 - x0) * i / n
            xb = x0 + (x1 - x0) * (i + 1) / n
            za = z0 + (z1 - z0) * (i + 1) / n
            self.box("plain", min(xa, xb), y - w / 2, za - 0.18, max(xa, xb), y + w / 2, za, col, top=True)
        for ys in (-1, 1):
            self.tube("plain", (x0, y + ys * w / 2, z0 - 0.1), (x1, y + ys * w / 2, z1 - 0.1), 0.13, 4, self.IRON)
        # lime tread nosing line on the stair's edge (one strip, a route read)
        self.tube("neon", (x0, y - w / 2 - 0.05, z0 + 0.55), (x1, y - w / 2 - 0.05, z1 + 0.15), 0.07, 4, lit, (1.0, 0, 0, 1))
        if rail:
            self.tube("plain", (x0, y - w / 2 - 0.1, z0 + 1.7), (x1, y - w / 2 - 0.1, z1 + 1.7), 0.07, 4, self.IRON)
            for i in range(0, n + 1, 3):
                xa = x0 + (x1 - x0) * i / n
                za = z0 + (z1 - z0) * i / n
                self.tube("plain", (xa, y - w / 2 - 0.1, za), (xa, y - w / 2 - 0.1, za + 1.7), 0.05, 4, self.IRON)

    def palm(self, x, y, z, h, s=1.0):
        """A small fan palm: trunk + a crown of leaf blades (flat cones)."""
        if self.detail == 0:
            L.lathe(self.mb("plain", True), x + self.ox, y + self.oy, [(0.0, z + h * 0.5), (1.6 * s, z + h * 0.62), (1.2 * s, z + h * 0.85), (0.0, z + h)], 6, self.LEAF[self.rr.randrange(3)], (0, 0, 0, 0.3))
            return
        self.cyl("plain", x, y, z, z + h * 0.78, 0.16 * s, 5, (0.10, 0.07, 0.04) if not self.c.cel else (0.3, 0.2, 0.16))
        col = self.LEAF[self.rr.randrange(3)]
        mb = self.mb("plain", False)
        for k in range(9):                                                       # fronds: flat blades that arch out and droop
            a = 2 * math.pi * k / 9 + self.rr.random() * 0.3
            ln = (2.0 + 0.7 * self.rr.random()) * s
            ca, sa = math.cos(a), math.sin(a)
            nx, ny = -sa, ca
            zb = z + h * 0.80
            P = [(0.0, 0.0), (ln * 0.35, 0.34 * s), (ln * 0.7, 0.26 * s), (ln, 0.0), (ln * 0.7, -0.26 * s), (ln * 0.35, -0.34 * s)]
            H = [0.0, 0.5, 0.35, -0.55, 0.35, 0.5]
            idx = [mb.v((x + self.ox + ca * u + nx * w, y + self.oy + sa * u + ny * w, zb + hh * s * 0.9), col, (0, 0, 0, 0.3)) for (u, w), hh in zip(P, H)]
            for q in range(1, 5):
                mb.f(idx[0], idx[q], idx[q + 1])

    def shrub(self, x, y, z, r, h=None):
        h = h or r * 0.9
        col = self.LEAF[self.rr.randrange(3)]
        L.lathe(self.mb("plain", True), x + self.ox, y + self.oy, [(0.0, z), (r, z + h * 0.15), (r * 0.85, z + h * 0.65), (0.0, z + h)], 6 if self.detail < 2 else 8, col, (0, 0, 0, 0.3))

    def planter(self, x0, y0, x1, y1, z, h=0.9, glow=True, shrubs=True, r=0.9):
        """A porcelain trough with shrubs and a lime light line."""
        self.box("plain", x0, y0, z, x1, y1, z + h, self.PORC, top=True)
        if glow:
            self.box("neon_l", x0 + 0.1, y0 + 0.1, z + h, x1 - 0.1, y1 - 0.1, z + h + 0.06, LIME, (0.8, 0, 0, 1))
        if shrubs and self.detail > 0:
            n = max(1, int(max(x1 - x0, y1 - y0) / (r * 1.7)))
            for i in range(n):
                t = (i + 0.5) / n
                self.shrub(x0 + (x1 - x0) * t if (x1 - x0) > (y1 - y0) else (x0 + x1) / 2, (y0 + y1) / 2 if (x1 - x0) > (y1 - y0) else y0 + (y1 - y0) * t, z + h, r * (0.8 + 0.5 * self.rr.random()))

    def railing(self, x0, y0, x1, y1, z, h=1.1):
        n = max(2, int(math.hypot(x1 - x0, y1 - y0) / 1.6))
        for i in range(n + 1):
            t = i / n
            self.tube("plain", (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z), (x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, z + h), 0.04, 4, self.IRON)
        self.tube("plain", (x0, y0, z + h), (x1, y1, z + h), 0.06, 4, self.IRON)

    def lamp_disc(self, x, y, z, r, col=CREAM, k=1.0):
        self.cyl("neon_l", x, y, z, z + 0.15, r, 12, col, (k * 0.35, 0, 0, 1))

    def tw(self, x0, y0, z0, x1, y1, z1, col, lit=0.8, lime=0.5, seed=0.3):
        self.box("tw", x0, y0, z0, x1, y1, z1, col, (lit, lime, 0.0, seed))


SLOT_N = {"I1": 3, "I2": 2, "I3": 3, "I4": 2, "I5": 1}          # nodes per inside layer (BRIEF: fight/fight/REST, fight/terminal, elite/fight/WORKSHOP, mainframe/elite, rack)


def slot_list(lev):
    """Room slots per level: [(x centre, width)] along the level's width (I5 = the one large slot). Slot order = node order; the last slot of I1 is the
    REST, the last of I3 the WORKSHOP."""
    out = {}
    for name, n in SLOT_N.items():
        x0, x1 = lev[name]["x"]
        if name == "I5":
            out[name] = [((x0 + x1) / 2, (x1 - x0) * 1.0)]
        else:
            w = min(9.0, (x1 - x0) / n - 1.8)
            out[name] = [(x0 + (i + 0.5) * (x1 - x0) / n, w) for i in range(n)]
    return out


# ===================================================================== A  Glass ward
A_TIERS = [  # (x half, y0, y1, z0, h)   five stepped tiers: I1 ground hall .. I4 glasshouse, the crown dome is I5
    (21.0, -6.0, 19.0, 2.2, 8.8),
    (17.0, -2.0, 18.0, 11.6, 8.0),
    (13.0, 2.0, 17.0, 20.2, 8.0),
    (9.0, 5.0, 16.0, 28.8, 8.2),
]


def build_A(g, detail, cut):
    c = g.c.cel
    lev = {}
    por, iron = g.PORC, g.IRON
    # clinic plinth: a porcelain base with a stepped front (three treads), lime hairline
    g.box("plain", -23.0, -8.5, 0.0, 23.0, 21.0, 2.2, por)
    for i in range(3):
        g.box("plain", -9.0 - i * 0.0, -8.5 - 0.0, 0.0, 9.0, -7.0 + 0 - i * 0.0, 0.0 + 0.0, por) if False else None
    g.box("plain", -6.5, -8.9, 0.0, 6.5, -6.0, 0.7, por)
    g.box("plain", -5.5, -9.2, 0.0, 5.5, -6.0, 0.35, por)
    g.box("neon_s", -23.0, -8.55, 2.0, 23.0, -8.45, 2.2, LIME, (1.0, 0, 0, 1))
    for xs in (-1, 1):                                  # clinic wings either side of the entrance: porcelain frontage bays with a lit green band
        g.box("plain", xs * 14.0 - 6.5, -8.5, 0.0, xs * 14.0 + 6.5, -7.8, 2.2, por)
    # the five tiers
    z_top = 0.0
    for k, (hx, y0, y1, z0, h) in enumerate(A_TIERS):
        z1 = z0 + h
        zc = z0 + h / 2
        lev["I%d" % (k + 1)] = dict(x=(-hx, hx), y=(y0, y1), z=(z0, z1))
        # slab / deck under the tier (porcelain), and the terrace deck in front of it
        if k > 0:
            ph = A_TIERS[k - 1]
            g.box("plain", -ph[0] - 0.6, ph[1] - 0.6, ph[3] + ph[4], ph[0] + 0.6, ph[2] + 0.4, z0, por)
            g.box("neon_s", -ph[0] - 0.6, ph[1] - 0.65, ph[3] + ph[4] + 0.35, ph[0] + 0.6, ph[1] - 0.55, ph[3] + ph[4] + 0.5, LIME, (0.9, 0, 0, 1))
        # glass skin: four glass walls (front omitted when cut)
        gl = "glass"
        g.box(gl, -hx, y1 - 0.05, z0, hx, y1, z1, g.GLASSC, (0.5, 0, 0, 0.5), top=False)             # back
        g.box(gl, -hx, y0, z0, -hx + 0.05, y1, z1, g.GLASSC, (0.5, 0, 0, 0.5), top=False)            # sides
        g.box(gl, hx - 0.05, y0, z0, hx, y1, z1, g.GLASSC, (0.5, 0, 0, 0.5), top=False)
        if not cut:
            g.box(gl, -hx, y0, z0, hx, y0 + 0.05, z1, g.GLASSC, (0.6, 0, 0, 0.5), top=False)
        # roof slab
        g.box("plain", -hx - 0.5, y0 - 0.5, z1, hx + 0.5, y1 + 0.5, z1 + 0.55, por)
        # iron frame: corner posts, mullions along the front and both sides, two transoms
        bays = max(3, int(round(2 * hx / 3.6)))
        bw = 2 * hx / bays
        for i in range(bays + 1):
            if detail == 0 and 0 < i < bays and i % 2:
                continue
            x = -hx + i * bw
            g.box("plain", x - 0.09, y0 - 0.12, z0, x + 0.09, y0 + 0.06, z1, iron)
        for zz in ((z0 + h * 0.5, z1 - 0.15) if detail else (z1 - 0.15,)):
            g.box("plain", -hx, y0 - 0.12, zz - 0.06, hx, y0 + 0.06, zz + 0.06, iron)
        for xs in (-hx, hx):
            for j in range((int((y1 - y0) / 3.2) + 1) if detail else 1):
                y = y0 + j * (y1 - y0) / max(1, int((y1 - y0) / 3.2))
                g.box("plain", xs - 0.08, y - 0.08, z0, xs + 0.08, y + 0.08, z1, iron)
        # Victorian arches over each front bay (an iron half-ring springing from the mullions), just under the roof slab
        if detail >= 1:
            for i in range(bays):
                xm = -hx + (i + 0.5) * bw
                pts = []
                for a in range(0, 13):
                    t = math.pi * a / 12
                    pts.append((xm + math.cos(t) * (bw / 2 - 0.1), y0 - 0.16, z1 - 1.9 + math.sin(t) * 1.7))
                g.polytube("plain", pts, 0.07, 4, iron)
        # lime eave line (the route's lit rim)
        g.box("neon_s", -hx - 0.5, y0 - 0.55, z1 + 0.2, hx + 0.5, y0 - 0.45, z1 + 0.38, LIME, (1.0, 0, 0, 1))
        # terrace in front of the tier above: planter row along the deck front edge + railing
        if k < len(A_TIERS) - 1:
            nz = z1 + 0.55
            hx2 = A_TIERS[k + 1][0]
            ny0 = A_TIERS[k + 1][1]
            g.planter(-hx + 1.0, y0 - 0.2 + (0.0), -hx + 5.5, y0 + 1.1, nz, 0.9, r=0.8) if False else None
            for (xa, xb) in ((-hx + 0.6, -hx2 - 3.0), (hx2 + 3.0, hx - 0.6)):
                if xb > xa:
                    g.planter(xa, y0 - 0.35, xb, y0 + 0.9, nz, 0.8, r=0.75)
            g.railing(-hx - 0.4, y0 - 0.5, hx + 0.4, y0 - 0.5, nz, 1.0) if detail >= 1 else None
            # the walkway through the planter row (same level): a lit strip centred on the terrace
            g.box("neon_l", -hx2 - 2.0, y0 + 1.2, nz, hx2 + 2.0, y0 + 1.35, nz + 0.05, LIME, (0.9, 0, 0, 1))
        # interior (detail >= 1): back wall with lit windows, floor lamps, planters + palms
        if detail >= 1:
            if cut or detail >= 1:
                g.tw(-hx + 0.1, y1 - 0.9, z0, hx - 0.1, y1 - 0.5, z1, por if k else g.PORC2, 0.85, 0.55, 0.2 + k * 0.17)
            for xx in (-1, 1):
                for j in range(2):
                    g.lamp_disc(xx * hx * 0.5, y0 + (y1 - y0) * (0.35 + 0.35 * j), z1 - 0.12, 1.5, CREAM if k != 3 else LIME, 1.0)
            if detail >= 2 or k in (0, 3):
                for i in range(max(2, int(hx / 3.4))):
                    g.planter(-hx + 1.5 + i * 7.0, y0 + 2.2, -hx + 4.2 + i * 7.0, y0 + 3.4, z0, 0.7, r=0.7) if False else None
                np_ = max(2, int(2 * hx / 5.5))
                for i in range(np_):
                    xx = -hx + (i + 0.5) * 2 * hx / np_
                    g.palm(xx, y0 + 3.0 + (i % 2) * 3.0, z0, 4.8 + 1.2 * ((i * 5) % 3) / 2.0, 1.0)
    # ----- the ground hall (I1) extras: reception and benches (clinic), the dose station
    z0 = A_TIERS[0][3]
    if detail >= 1:
        g.box("plain", -4.0, 8.0, z0, 4.0, 9.6, z0 + 1.1, por)
        g.box("neon_l", -4.0, 7.95, z0 + 1.1, 4.0, 8.05, z0 + 1.18, LIME, (1.0, 0, 0, 1))
        for i in range(-2, 3):
            g.box("plain", i * 7.0 - 2.0, 1.0, z0, i * 7.0 + 2.0, 2.0, z0 + 0.55, g.PORC2)
        g.cyl("neon_l", 12.0, 5.0, z0, z0 + 1.1, 1.0, 10, LIME, (0.9, 0, 0, 1))             # the ward-dose pylon (REST)
    # the glass door: lit, with a canopy and a lime frame
    g.box("neon_s", -3.2, -6.18, 2.2, -3.0, -6.05, 8.4, LIME, (1.0, 0, 0, 1))
    g.box("neon_s", 3.0, -6.18, 2.2, 3.2, -6.05, 8.4, LIME, (1.0, 0, 0, 1))
    g.box("neon_s", -3.2, -6.18, 8.3, 3.2, -6.05, 8.5, LIME, (1.0, 0, 0, 1))
    g.box("neon_l", -3.0, -6.12, 2.2, 3.0, -6.08, 8.3, CREAM, (1.5, 0, 0, 1))
    g.box("plain", -5.0, -9.2, 8.7, 5.0, -5.5, 9.2, por)
    for xs in (-1, 1):
        g.box("plain", xs * 4.7 - 0.15, -9.0, 0.0, xs * 4.7 + 0.15, -8.7, 8.7, por)
    # the stair along the glass front, alternating sides tier to tier (rising edges)
    ST = [(-16.5, -9.0, 2.2, 11.6), (14.0, 0.0, 11.6, 20.2), (-9.5, 4.0, 20.2, 28.8), (7.0, 7.0, 28.8, 37.4)]
    for i, (xa, _, za, zb) in enumerate(ST):
        hx, y0 = A_TIERS[i][0], A_TIERS[i][1]
        d = 1.0 if i % 2 == 0 else -1.0
        xa = (-hx + 1.2) if d > 0 else (hx - 1.2)
        xb = xa + d * min(13.0, 2 * hx - 4.0)
        g.stair(xa, y0 - 1.25, za + 0.5, xb, zb + 0.5, 1.6, por, detail >= 1)
    # the crown (I5): a domed glass vault with a lime-lit core, lantern and finial
    hx, y0, y1, z0, h = A_TIERS[3]
    zt = z0 + h + 0.55
    cx_, cy_ = 0.0, (y0 + y1) / 2 + 0.2
    lev["I5"] = dict(x=(-7.0, 7.0), y=(cy_ - 5.4, cy_ + 5.4), z=(zt, zt + 9.0), large=True)
    g.edome("glassB", cx_, cy_, zt, 7.4, 5.8, 8.6, 28 if not c else 16, g.GLASSC, (0.5, 0, 0, 0.5), 6)
    # iron ribs of the dome (meridians) and rings
    for m in range(16 if detail else 10):
        a = 2 * math.pi * m / (16 if detail else 10)
        pts = [(cx_ + math.cos(a) * 7.45 * math.cos(math.pi / 2 * q / 8), cy_ + math.sin(a) * 5.85 * math.cos(math.pi / 2 * q / 8), zt + 8.65 * math.sin(math.pi / 2 * q / 8)) for q in range(9)]
        g.polytube("plain", pts, 0.09, 4, iron)
    for q in (2, 4, 6):
        zz = zt + 8.6 * math.sin(math.pi / 2 * q / 8)
        s_ = math.cos(math.pi / 2 * q / 8)
        g.ering("plain", cx_, cy_, zz, 7.45 * s_, 5.85 * s_, 0.09, 28, 4, iron, (0, 0, 0, 0.5))
    # the vault core: a lime-lit sphere on a pedestal, a drawer ring (seed trays) around it
    g.cyl("plain", cx_, cy_, zt, zt + 1.2, 2.6, 16, g.PORC2)
    g.sphere("neon", cx_, cy_, zt + 3.6, 2.1, 14, LIME, (1.6, 0, 0, 1))
    g.torus("neon_s", cx_, cy_, zt + 3.6, 3.1, 0.12, 28, 5, LIME, (1.0, 0, 0, 1))
    if detail >= 1:
        for m in range(14):
            a = 2 * math.pi * m / 14
            g.box("neon_l", cx_ + math.cos(a) * 4.9 - 0.3, cy_ + math.sin(a) * 3.8 - 0.3, zt + 0.5, cx_ + math.cos(a) * 4.9 + 0.3, cy_ + math.sin(a) * 3.8 + 0.3, zt + 2.8, CREAM, (0.9, 0, 0, 1))
    g.cyl("plain", cx_, cy_, zt + 8.6, zt + 11.0, 0.55, 8, iron)
    g.sphere("neon", cx_, cy_, zt + 11.4, 0.55, 8, LIME, (1.6, 0, 0, 1))
    g.torus("neon_s", cx_, cy_, zt + 8.6, 1.1, 0.12, 16, 4, LIME, (1.0, 0, 0, 1))
    # the WORKSHOP alcove (I3, the last slot): a lit niche with a bench, a gold tool wall and hanging lamps
    hx3, y03, y13, z03, h3 = A_TIERS[2]
    xc, w = slot_list(lev)["I3"][2]
    ax0, ax1 = xc - w / 2, xc + w / 2
    lev["I3_workshop"] = dict(x=(ax0, ax1), y=(y03 + 4.0, y03 + 9.0), z=(z03, z03 + 4.2))
    if detail >= 1:
        GOLD = (1.0, 0.70, 0.22)
        g.box("plain", ax0, y03 + 3.0, z03, ax1, y03 + 9.5, z03 + 0.2, g.PORC2)
        g.box("neon_l", ax0 + 0.2, y03 + 9.1, z03 + 0.6, ax1 - 0.2, y03 + 9.35, z03 + 6.6, GOLD, (3.2, 0, 0, 1))           # the gold tool wall
        g.box("plain", ax0 + 0.6, y03 + 7.2, z03, ax1 - 0.6, y03 + 8.6, z03 + 1.2, iron)                                    # workbench
        g.box("neon_l", ax0 + 0.6, y03 + 7.2, z03 + 1.2, ax1 - 0.6, y03 + 8.6, z03 + 1.26, GOLD, (2.0, 0, 0, 1))
        for i in range(7):
            g.tube("plain", (ax0 + 0.9 + i * (w - 1.8) / 6, y03 + 9.0, z03 + 5.8), (ax0 + 0.9 + i * (w - 1.8) / 6, y03 + 9.0, z03 + 2.4 + 0.5 * (i % 3)), 0.07, 4, g.PORC)
        for xx in (ax0 + w * 0.3, ax0 + w * 0.7):
            g.lamp_disc(xx, y03 + 6.4, z03 + h3 - 0.15, 1.3, GOLD, 2.4)
    return lev


# ===================================================================== B  Culture stack
B_RX = [23.0, 20.2, 17.4, 14.6, 11.8]
B_RY = [14.0, 12.4, 10.8, 9.2, 7.6]
B_PITCH = 7.7
B_Z0 = 1.6


def _hex_edges(g, tray_k, cx, cy, rx, ry, z0, z1, a_skip, col, detail):
    """Hex (Eden) cell skin on an oval wall between z0 and z1: iron outlines + a few lit cells. a_skip = (a0, a1) angle range left open."""
    R = 1.35 if detail >= 1 else 2.0
    dz = math.sqrt(3) * R
    rr = random.Random(7 + tray_k)
    per = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
    ncol = max(8, int(per / (1.5 * R)))
    nrow = int((z1 - z0) / dz) + 1
    off = 0.06

    def P(th, z):
        return (cx + (rx + off) * math.cos(th), cy + (ry + off) * math.sin(th), z)

    def spd(th):
        return math.hypot(rx * math.sin(th), ry * math.cos(th))
    done = set()
    for i in range(ncol):
        th0 = 2 * math.pi * i / ncol
        if a_skip and a_skip[0] < th0 % (2 * math.pi) < a_skip[1]:
            continue
        for j in range(-1, nrow + 1):
            zc = z0 + (j + (0.5 if i % 2 else 0.0)) * dz + dz * 0.5
            pts = []
            for q in range(6):
                a = math.radians(60 * q)
                th = th0 + R * math.cos(a) / spd(th0)
                zz = min(max(zc + R * math.sin(a) * 0.98, z0), z1)
                pts.append(P(th, zz))
            for q in range(6):
                A_, B_ = pts[q], pts[(q + 1) % 6]
                if abs(A_[2] - B_[2]) < 1e-6 and abs(A_[2] - z0) < 1e-6 or abs(A_[2] - B_[2]) < 1e-6 and abs(A_[2] - z1) < 1e-6:
                    pass
                key = (round(A_[0], 2), round(A_[1], 2), round(A_[2], 2), round(B_[0], 2), round(B_[1], 2), round(B_[2], 2))
                if key in done:
                    continue
                done.add(key)
                if detail >= 1:
                    g.tube("plain", (A_[0] - g.ox * 0, A_[1], A_[2]), (B_[0], B_[1], B_[2]), 0.07, 4, col)
            if rr.random() < (0.16 if detail >= 1 else 0.30) and (z0 + 0.5 < zc < z1 - 0.5):
                # a lit hex cell panel (agar light showing through): a flat fan slightly proud of the wall
                c = P(th0, zc)
                rim = [P(th0 + (R * 0.84) * math.cos(math.radians(60 * q)) / spd(th0), zc + R * 0.84 * math.sin(math.radians(60 * q))) for q in range(6)]
                rim = [(p[0], p[1], p[2]) for p in rim]
                g.flat("agar", [c] + rim + [rim[0]], MINT, (1.0, 0, 0, 1))


def build_B(g, detail, cut):
    c = g.c.cel
    lev = {}
    por, iron = g.PORC, g.IRON
    cx, cy = 0.0, CY
    # base plinth (oval) with the entrance plateau
    g.eplate("plain", cx, cy, 0.0, B_Z0, 24.2, 15.2, 40, por)
    g.box("plain", -7.0, -9.2, 0.0, 7.0, -6.0, 0.9, por)
    g.box("plain", -5.6, -9.6, 0.0, 5.6, -6.0, 0.45, por)
    g.ering("neon_s", cx, cy, B_Z0 - 0.05, 24.2, 15.2, 0.1, 40, 4, MINT, (0.9, 0, 0, 1))
    for k in range(5):
        rx, ry = B_RX[k], B_RY[k]
        z0 = B_Z0 + k * B_PITCH
        h = 6.2
        zf = z0 + 0.7                      # tray floor top
        zl = z0 + h + 0.7                  # lid underside
        lev["I%d" % (k + 1)] = dict(x=(-rx, rx), y=(cy - ry, cy + ry), z=(zf, zl))
        # floor plate (steel porcelain), its lime-white rim
        g.eplate("plain", cx, cy, z0, zf, rx + 0.4, ry + 0.4, 36, por)
        g.ering("neon_s", cx, cy, zf - 0.02, rx + 0.42, ry + 0.42, 0.07, 36, 4, MINT, (1.0, 0, 0, 1))
        # agar disc (mint glow) + a raised petri rim inside
        g.eplate("agar", cx, cy, zf, zf + 0.05, rx - 1.6, ry - 1.4, 32, MINT, (0.55, 0, 0, 1)) if False else None
        g.elathe("agar", cx, cy, [(0.0, zf + 0.08), (ry - 1.5, zf + 0.08)], 32, (rx - 1.7) / (ry - 1.5), MINT, (0.95, 0, 0, 1), False)
        if detail >= 1:
            rr = random.Random(100 + k)
            for q in range(10 if detail == 1 else 16):             # colonies: small pale mint domes on the agar
                a = rr.random() * 2 * math.pi
                d = math.sqrt(rr.random()) * 0.8
                g.sphere("neon", cx + math.cos(a) * (rx - 3.0) * d, cy + math.sin(a) * (ry - 2.6) * d, zf + 0.15, 0.35 + 0.5 * rr.random(), 6, (0.75, 1.0, 0.85), (1.2, 0, 0, 1))
        # lid: glass plate over the tray with a steel rim ring (overhang)
        g.edome("glassB", cx, cy, zl, rx, ry, 0.7, 36, g.GLASSC, (0.5, 0, 0, 0.5), 2) if False else None
        g.eplate("plain", cx, cy, zl, zl + 0.5, rx + 0.5, ry + 0.5, 36, g.PORC2)
        # wall: hex cell skin on glass. open arc (front) when cut
        a_skip = (math.radians(215), math.radians(325)) if cut else None
        wall = "glassB"
        g.elathe(wall, cx, cy, [(ry, zf), (ry, zl)], 36, rx / ry, g.GLASSC, (0.5, 0, 0, 0.5), True, a0=(math.radians(325) if cut else 0.0),
                 a1=(math.radians(215) + 2 * math.pi if cut else 2 * math.pi), n=None) if False else None
        if cut:
            g.elathe(wall, cx, cy, [(ry, zf), (ry, zl)], 36, rx / ry, g.GLASSC, (0.5, 0, 0, 0.5), True, a0=math.radians(325), a1=math.radians(215) + 2 * math.pi)
        else:
            g.elathe(wall, cx, cy, [(ry, zf), (ry, zl)], 36, rx / ry, g.GLASSC, (0.5, 0, 0, 0.5), True)
        _hex_edges(g, k, cx, cy, rx, ry, zf, zl, a_skip, iron, detail)
        # eave: a mint line under the lid
        g.ering("neon_s", cx, cy, zl - 0.1, rx + 0.1, ry + 0.1, 0.06, 36, 4, MINT, (1.0, 0, 0, 1))
        # inside: petri racks (stacks of thin discs on a post), column, ceiling light
        if detail >= 1:
            g.ering("neon_l", cx, cy, zl - 0.2, rx - 2.2, ry - 2.0, 0.16, 28, 4, (0.85, 1.0, 0.92), (0.8, 0, 0, 1))
            g.eplate("neon_l", cx, cy, zl - 0.12, zl - 0.04, rx - 2.0, ry - 1.8, 28, MINT, (0.10, 0, 0, 1))
            for sx in (-1, 1):
                rxx = sx * (rx * 0.5)
                for q in range(6):
                    g.cyl("plain", rxx, cy + 1.0, zf + 0.2 + q * 0.62, zf + 0.26 + q * 0.62, 1.6, 12, g.GLASSC, (0, 0, 0, 0.5)) if False else None
                    g.cyl("neon_l", rxx, cy + 1.0, zf + 0.9 + q * 0.62, zf + 0.97 + q * 0.62, 1.5, 12, (0.8, 1.0, 0.9), (0.55, 0, 0, 1))
                g.cyl("plain", rxx, cy + 1.0, zf, zf + 4.8, 0.2, 6, iron)
        # the incubator stacking frame: posts on the oval, ring brackets per level (lab equipment read)
    for m in range(8 if detail >= 1 else 0):
        a = 2 * math.pi * (m + 0.5) / 8
        if cut and math.radians(215) < a < math.radians(325):
            a += math.radians(110) if a < math.radians(270) else -math.radians(110)
        px_, py_ = cx + math.cos(a) * (B_RX[0] + 1.3), cy + math.sin(a) * (B_RY[0] + 1.3)
        g.tube("plain", (px_, py_, B_Z0), (px_, py_, B_Z0 + 4 * B_PITCH + 6.9), 0.24, 6, g.PORC2)
        g.tube("neon_s", (px_ + 0.26, py_, B_Z0 + 0.5), (px_ + 0.26, py_, B_Z0 + 4 * B_PITCH + 6.4), 0.04, 4, MINT, (0.9, 0, 0, 1))
        g.tube("neon_s", (px_ * 1.0, py_, B_Z0 + 0.4), (px_, py_, B_Z0 + 5 * B_PITCH - 0.9), 0.05, 4, MINT, (0.9, 0, 0, 1)) if False else None
    # stair along the glass front, tray to tray (zigzag on the lid ledges)
    for k in range(4):
        z0 = B_Z0 + k * B_PITCH + 6.9 + 0.5
        d = 1.0 if k % 2 == 0 else -1.0
        rx, ry = B_RX[k], B_RY[k]
        xa = d * (-(rx - 5.0) * 0.55)
        ya = cy - ry * math.sqrt(max(0.05, 1 - (xa / rx) ** 2)) - 1.4
        g.stair(xa - d * 0.0, ya, z0 - 0.0, xa + d * 8.5, z0 + B_PITCH - 0.5, 1.6, por, detail >= 1)
    # the cryo drum (I5): sealed, banded, domed; a lit hatch
    zt = B_Z0 + 5 * B_PITCH - 0.6 + 0.5
    r = 6.6
    cyc = cy + 0.4
    lev["I5"] = dict(x=(-r, r), y=(cyc - r, cyc + r), z=(zt, zt + 9.5), large=True)
    g.eplate("plain", cx, cyc, zt - 0.5, zt, 8.3, 8.3, 28, g.PORC2)
    drum = [(0.0, zt), (r, zt), (r, zt + 9.0), (r * 0.82, zt + 10.4), (r * 0.45, zt + 11.3), (0.0, zt + 11.6)]
    if cut:
        g.elathe("plain", cx, cyc, drum, 28, 1.0, g.PORC, (0, 0, 0, 0.5), True, a0=math.radians(325), a1=math.radians(215) + 2 * math.pi)
        # cutaway interior: a vault ring of seed drawers around a mint core
        g.sphere("neon", cx, cyc, zt + 4.0, 2.4, 14, MINT, (1.9, 0, 0, 1))
        for m in range(18):
            a = 2 * math.pi * m / 18
            g.box("neon_l", cx + math.cos(a) * 4.6 - 0.35, cyc + math.sin(a) * 4.6 - 0.35, zt + 0.4, cx + math.cos(a) * 4.6 + 0.35, cyc + math.sin(a) * 4.6 + 0.35, zt + 7.8, (0.8, 1.0, 0.9), (0.8, 0, 0, 1))
        g.cyl("plain", cx, cyc, zt, zt + 0.5, 6.2, 20, g.PORC2)
    else:
        g.elathe("plain", cx, cyc, drum, 28, 1.0, g.PORC, (0, 0, 0, 0.5), True)
    for q in (3.0, 6.2):
        g.torus("plain", cx, cyc, zt + q, r + 0.08, 0.2, 28, 5, iron, (0, 0, 0, 0.5))
        g.torus("neon_s", cx, cyc, zt + q + 0.22, r + 0.05, 0.05, 28, 4, MINT, (1.0, 0, 0, 1))
    # hatch (front): a round pressure door, rim + wheel, glowing mint slit above
    hy_ = cyc - r - 0.1
    if not cut:
        for q in range(24):
            a0, a1 = 2 * math.pi * q / 24, 2 * math.pi * (q + 1) / 24
            g.tube("neon_s", (cx + math.cos(a0) * 2.2, hy_ - 0.1, zt + 4.4 + math.sin(a0) * 2.2), (cx + math.cos(a1) * 2.2, hy_ - 0.1, zt + 4.4 + math.sin(a1) * 2.2), 0.14, 4, MINT, (1.2, 0, 0, 1))
        g.box("neon", cx - 1.6, hy_ - 0.12, zt + 4.1, cx + 1.6, hy_ - 0.04, zt + 4.7, MINT, (1.7, 0, 0, 1))
    g.cyl("plain", cx, cyc, zt + 11.5, zt + 14.2, 0.2, 6, iron)
    g.sphere("neon", cx, cyc, zt + 14.5, 0.45, 8, MINT, (1.7, 0, 0, 1))
    # the WORKSHOP alcove (I3, the last slot): a bench bay with a gold tool wall
    k = 2
    rx, ry = B_RX[k], B_RY[k]
    z3 = B_Z0 + k * B_PITCH + 0.7
    xc, w = slot_list(lev)["I3"][2]
    yb = cy + ry * math.sqrt(max(0.05, 1 - (xc / rx) ** 2))
    lev["I3_workshop"] = dict(x=(xc - w / 2, xc + w / 2), y=(yb - 5.0, yb - 0.6), z=(z3, z3 + 4.0))
    if detail >= 1:
        GOLD = (1.0, 0.70, 0.22)
        g.box("neon_l", xc - w / 2 + 0.3, yb - 1.5, z3 + 0.6, xc + w / 2 - 0.3, yb - 1.25, z3 + 5.0, GOLD, (3.2, 0, 0, 1))
        g.box("plain", xc - w / 2 + 0.6, yb - 3.4, z3, xc + w / 2 - 0.6, yb - 2.0, z3 + 1.2, iron)
        g.box("neon_l", xc - w / 2 + 0.6, yb - 3.4, z3 + 1.2, xc + w / 2 - 0.6, yb - 2.0, z3 + 1.26, GOLD, (2.0, 0, 0, 1))
        for i in range(7):
            g.tube("plain", (xc - w / 2 + 0.9 + i * (w - 1.8) / 6, yb - 1.6, z3 + 4.6), (xc - w / 2 + 0.9 + i * (w - 1.8) / 6, yb - 1.6, z3 + 2.2 + 0.5 * (i % 3)), 0.07, 4, g.PORC)
    # the glass door: a hex-framed lit door at the front of tray 1
    g.box("neon_s", -2.4, -6.7, B_Z0, -2.2, -6.55, B_Z0 + 5.4, MINT, (1.0, 0, 0, 1)) if False else None
    dy_ = cy - B_RY[0] * math.sqrt(max(0.0, 1 - (0.0 / B_RX[0]) ** 2)) - 0.3
    g.box("neon_l", -3.0, dy_ - 0.05, B_Z0 + 0.7, 3.0, dy_ + 0.05, B_Z0 + 6.0, CREAM, (1.5, 0, 0, 1))
    for xs in (-3.2, 3.2):
        g.box("neon_s", xs - 0.1, dy_ - 0.12, B_Z0 + 0.7, xs + 0.1, dy_ + 0.0, B_Z0 + 6.1, MINT, (1.0, 0, 0, 1))
    g.box("neon_s", -3.3, dy_ - 0.12, B_Z0 + 6.0, 3.3, dy_ + 0.0, B_Z0 + 6.2, MINT, (1.0, 0, 0, 1))
    return lev


# ===================================================================== C  Hanging mountain
C_RX = [19.0, 15.8, 12.6, 9.4, 6.0]
C_RY = [11.0, 9.2, 7.4, 5.6, 3.8]
C_Z0 = 1.0
C_PITCH = 5.8


def build_C(g, detail, cut):
    c = g.c.cel
    lev = {}
    por, iron = g.PORC, g.IRON
    cx, cy = 0.0, CY
    rr = random.Random(21)
    rock = (0.30, 0.42, 0.34) if c else (0.05, 0.08, 0.06)
    lawn = (0.20, 0.56, 0.22) if c else (0.04, 0.20, 0.06)
    # plinth ring and the porcelain portico with the glass door
    g.eplate("plain", cx, cy, 0.0, C_Z0, 24.6, 15.6, 44, por)
    g.ering("neon_s", cx, cy, C_Z0 - 0.04, 24.6, 15.6, 0.08, 44, 4, LIME, (0.9, 0, 0, 1))
    g.box("plain", -5.0, -9.0, 0.0, 5.0, -6.3, 0.8, por)
    # the mountain: five terrace rings (cliff wall + planted top). I1 ground hall = the ring at the foot
    for k in range(5):
        rx, ry = C_RX[k], C_RY[k]
        z0 = C_Z0 + k * C_PITCH
        z1 = z0 + C_PITCH - 0.4
        lev["I%d" % (k + 1)] = dict(x=(-rx, rx), y=(cy - ry, cy + ry), z=(z0, z1), light=(0.0, cy - ry - 3.0, z1 + 2.2))
        g.eplate("plain", cx, cy, z0 - 0.02, z1, rx, ry, 36, rock, (0, 0, 0, 0.5), True)
        # strata lines (porcelain ledges) and a lit lime lip on the terrace edge
        g.ering("plain", cx, cy, z0 + C_PITCH * 0.5, rx + 0.05, ry + 0.05, 0.07, 36, 4, g.PORC2, (0, 0, 0, 0.5)) if detail >= 1 else None
        g.ering("neon_s", cx, cy, z1, rx, ry, 0.07, 36, 4, LIME, (0.8, 0, 0, 1))
        r_in = (C_RX[k + 1] if k < 4 else 0.0)
        g.elathe("plain", cx, cy, [(ry - 0.1, z1 + 0.04), ((C_RY[k + 1] if k < 4 else 0.0), z1 + 0.04)], 36, rx / ry, lawn, (0, 0, 0, 0.3), True)
        # planting on the terrace top: a ring of shrubs and a few palms (not on the front arc where the ramp runs on the first turn)
        if detail >= 1:
            nsh = int((rx + ry) * 0.9)
            for q in range(nsh):
                a = 2 * math.pi * q / nsh + rr.random() * 0.15
                rr_ = 0.82 + 0.12 * rr.random() if k < 4 else 0.6
                rrx = (C_RX[k + 1] if k < 4 else 1.5) + 1.4 + (rx - (C_RX[k + 1] if k < 4 else 1.5) - 1.8) * rr.random()
                rry = (C_RY[k + 1] if k < 4 else 1.0) + 1.0 + (ry - (C_RY[k + 1] if k < 4 else 1.0) - 1.4) * rr.random()
                x, y = cx + math.cos(a) * rrx, cy + math.sin(a) * rry
                if rr.random() < 0.35:
                    g.palm(x, y, z1, 3.0 + 2.0 * rr.random(), 0.9)
                else:
                    g.shrub(x, y, z1, 0.9 + 0.9 * rr.random(), 1.2 + 1.1 * rr.random())
        else:
            for q in range(10):
                a = 2 * math.pi * q / 10
                g.shrub((cx + math.cos(a) * (rx - 1.8)), cy + math.sin(a) * (ry - 1.4), z1, 1.6, 2.4)
    # waterfall core: a pale translucent column from the crown down the middle, foam rings, a pool at the foot
    zc0 = C_Z0 + 4 * C_PITCH + C_PITCH - 0.4
    g.cyl("water", cx, cy, C_Z0 + 0.4, zc0 + 6.0, 1.15, 14, (0.82, 1.0, 0.90, 1.0), (0.6, 0, 0, 1), cap=False, smooth=True)
    g.cyl("neon_l", cx, cy, C_Z0 + 0.4, zc0 + 6.0, 0.55, 10, (0.85, 1.0, 0.92), (0.7, 0, 0, 1), cap=False, smooth=True)
    for k in range(5):
        g.ering("neon_l", cx, cy, C_Z0 + k * C_PITCH + C_PITCH - 0.3, 1.9 + 0.3 * k, 1.6 + 0.2 * k, 0.12, 20, 4, (0.9, 1.0, 0.95), (0.7, 0, 0, 1))
    g.eplate("water", cx, cy, C_Z0 + 0.05, C_Z0 + 0.35, 6.5, 4.3, 24, (0.45, 0.85, 0.7), (0.3, 0, 0, 1))
    # the planter-walk ramp: a helical ribbon (two turns) around the mountain with a lit edge and a rail, from the door to the crown
    zt0, zt1 = C_Z0 + 0.4, C_Z0 + 4 * C_PITCH + C_PITCH - 0.2
    N = 120
    turns = 2.0
    cen, edge_i, edge_o = [], [], []
    for i in range(N + 1):
        t = i / N
        th = -math.pi / 2 - 0.55 + 2 * math.pi * turns * t * (-1.0)
        z = zt0 + (zt1 - zt0) * t
        # radius follows the mountain's radius at that height (between terrace radii), plus the walkway half-width
        kk = min(4, max(0, (z - C_Z0) / C_PITCH))
        i0 = int(kk)
        f = kk - i0
        rxa = C_RX[i0] + (C_RX[min(4, i0 + 1)] - C_RX[i0]) * f if i0 < 4 else C_RX[4]
        rya = C_RY[i0] + (C_RY[min(4, i0 + 1)] - C_RY[i0]) * f if i0 < 4 else C_RY[4]
        rxa += 1.6
        rya += 1.3
        cen.append((cx + math.cos(th) * rxa, cy + math.sin(th) * rya, z))
    for i in range(N):
        a, b = cen[i], cen[i + 1]
        # a flat walkway quad strip of width 2.2 (along the radial direction)
        for (p, q) in ((a, b),):
            dx, dy = p[0] - cx, p[1] - cy
            ln = math.hypot(dx, dy) or 1.0
            ux, uy = dx / ln, dy / ln
            dx2, dy2 = q[0] - cx, q[1] - cy
            ln2 = math.hypot(dx2, dy2) or 1.0
            u2x, u2y = dx2 / ln2, dy2 / ln2
            w = 1.1
            g.flat("plain", [(p[0] - ux * w, p[1] - uy * w, p[2]), (q[0] - u2x * w, q[1] - u2y * w, q[2]), (q[0] + u2x * w, q[1] + u2y * w, q[2]), (p[0] + ux * w, p[1] + uy * w, p[2])], por, (0, 0, 0, 0.5))
            g.flat("plain", [(p[0] + ux * w, p[1] + uy * w, p[2] - 0.35), (q[0] + u2x * w, q[1] + u2y * w, q[2] - 0.35), (q[0] - u2x * w, q[1] - u2y * w, q[2] - 0.35), (p[0] - ux * w, p[1] - uy * w, p[2] - 0.35)], por, (0, 0, 0, 0.5))
    g.polytube("neon_s", [(p[0] + (p[0] - cx) / (math.hypot(p[0] - cx, p[1] - cy) or 1) * 1.15, p[1] + (p[1] - cy) / (math.hypot(p[0] - cx, p[1] - cy) or 1) * 1.15, p[2] + 0.06) for p in cen[::2]], 0.07, 4, LIME, (1.0, 0, 0, 1))
    if detail >= 1:
        g.polytube("plain", [(p[0] + (p[0] - cx) / (math.hypot(p[0] - cx, p[1] - cy) or 1) * 1.15, p[1] + (p[1] - cy) / (math.hypot(p[0] - cx, p[1] - cy) or 1) * 1.15, p[2] + 1.0) for p in cen[::2]], 0.05, 4, iron)
    # the glass diagrid shell (an ellipsoid dome), front sector removed when cut (glazing-open)
    Hs = 35.0
    rxs, rys = 23.4, 14.6
    rings = 14
    SQ = 2.0 / 2.6                                                   # superellipse profile: a broad shoulder (Cloud Forest / Jewel), not an egg

    def shell(phi):
        return (math.cos(phi) ** SQ, math.sin(phi) ** SQ)
    prof = [(rys * shell(math.pi / 2 * q / rings)[0], C_Z0 + Hs * shell(math.pi / 2 * q / rings)[1]) for q in range(rings + 1)]
    if cut:
        g.elathe("glassB", cx, cy, prof, 44, rxs / rys, g.GLASSC, (0.45, 0, 0, 0.5), True, a0=math.radians(335), a1=math.radians(205) + 2 * math.pi)
    else:
        g.elathe("glassB", cx, cy, prof, 44, rxs / rys, g.GLASSC, (0.45, 0, 0, 0.5), True)
    nm = 24 if detail else 10
    for m in range(nm):
        a = 2 * math.pi * m / nm
        if cut and math.radians(205) < a < math.radians(335):
            continue
        pts = [(cx + math.cos(a) * (rxs + 0.06) * shell(math.pi / 2 * q / 14)[0], cy + math.sin(a) * (rys + 0.06) * shell(math.pi / 2 * q / 14)[0], C_Z0 + Hs * shell(math.pi / 2 * q / 14)[1]) for q in range(15)]
        g.polytube("plain", pts, 0.10, 4, iron)
    for q in (3, 6, 9, 12):
        s_ = shell(math.pi / 2 * q / 14)[0]
        zz = C_Z0 + Hs * shell(math.pi / 2 * q / 14)[1]
        if cut:
            g.elathe("plain", cx, cy, [(rys * s_ + 0.05 + 0.0, zz)], 2, 1.0, iron, (0, 0, 0, 0.5)) if False else None
        g.ering("plain", cx, cy, zz, (rxs + 0.06) * s_, (rys + 0.06) * s_, 0.09, 44, 4, iron, (0, 0, 0, 0.5)) if (not cut and detail) else None
    # oculus ring and the seed-pod vault (I5) in the crown
    g.ering("plain", cx, cy, C_Z0 + Hs - 0.3, 3.2, 3.2, 0.35, 20, 5, por, (0, 0, 0, 0.5)) if False else None
    zp = zc0 + 0.2
    lev["I5"] = dict(x=(-5.0, 5.0), y=(cy - 5.0, cy + 5.0), z=(zp, zp + 12.0), large=True)
    pod = [(0.0, zp), (2.8, zp + 0.5), (5.0, zp + 4.2), (4.6, zp + 7.8), (2.4, zp + 10.8), (0.0, zp + 12.2)]
    g.elathe("glassB", cx, cy, pod, 24, 1.0, (0.65, 1.0, 0.55, 1.0), (0.7, 0, 0, 1), True)
    g.sphere("neon", cx, cy, zp + 5.2, 2.6, 14, LIME, (1.9, 0, 0, 1))
    for m in range(8):
        a = 2 * math.pi * m / 8
        pts = [(cx + math.cos(a) * r_, cy + math.sin(a) * r_, z_) for (r_, z_) in [(0.1, zp), (2.9, zp + 0.5), (5.1, zp + 4.2), (4.7, zp + 7.8), (2.5, zp + 10.8), (0.1, zp + 12.3)]]
        g.polytube("plain", pts, 0.11, 4, g.PORC2)
    g.cyl("plain", cx, cy, zp + 12.0, zp + 14.2, 0.18, 6, iron)
    g.sphere("neon", cx, cy, zp + 14.5, 0.45, 8, LIME, (1.7, 0, 0, 1))
    # the WORKSHOP alcove (I3, the last slot): a niche on the terrace ring, bench + gold wall
    z3 = C_Z0 + 2 * C_PITCH + C_PITCH - 0.4
    xc, w = slot_list(lev)["I3"][2]
    lev["I3_workshop"] = dict(x=(xc - w / 2, xc + w / 2), y=(cy - 2.2, cy + 2.2), z=(z3, z3 + 3.6))
    if detail >= 1:
        GOLD = (1.0, 0.70, 0.22)
        yy = cy - C_RY[2] * math.sqrt(max(0.05, 1 - (xc / C_RX[2]) ** 2)) + 2.2
        g.box("neon_l", xc - w / 2 + 0.2, yy + 1.3, z3 + 0.4, xc + w / 2 - 0.2, yy + 1.55, z3 + 4.2, GOLD, (3.2, 0, 0, 1))
        g.box("plain", xc - w / 2 + 0.4, yy - 0.6, z3, xc + w / 2 - 0.4, yy + 0.8, z3 + 1.1, iron)
        g.box("neon_l", xc - w / 2 + 0.4, yy - 0.6, z3 + 1.1, xc + w / 2 - 0.4, yy + 0.8, z3 + 1.16, GOLD, (2.0, 0, 0, 1))
        for i in range(5):
            g.tube("plain", (xc - w / 2 + 0.7 + i * (w - 1.4) / 4, yy + 1.2, z3 + 3.8), (xc - w / 2 + 0.7 + i * (w - 1.4) / 4, yy + 1.2, z3 + 1.9 + 0.5 * (i % 3)), 0.07, 4, por)
    # the glass door: a portico with a lit door at the foot (front of the I1 ring)
    g.box("neon_l", -3.0, -6.45, C_Z0, 3.0, -6.38, C_Z0 + 6.0, CREAM, (1.5, 0, 0, 1))
    for xs in (-3.2, 3.2):
        g.box("neon_s", xs - 0.1, -6.55, C_Z0, xs + 0.1, -6.3, C_Z0 + 6.2, LIME, (1.0, 0, 0, 1))
    g.box("neon_s", -3.3, -6.55, C_Z0 + 6.0, 3.3, -6.3, C_Z0 + 6.2, LIME, (1.0, 0, 0, 1))
    g.box("plain", -5.0, -9.2, C_Z0 + 6.5, 5.0, -5.6, C_Z0 + 7.0, por)
    return lev


def build(kind, ctx, ox=0.0, oy=0.0, detail=1, cut=False):
    g = G(ctx, ox, oy, detail, cut)
    return {"A": build_A, "B": build_B, "C": build_C}[kind](g, detail, cut)


def height(kind):
    return {"A": 50.0, "B": 52.0, "C": 55.0}[kind]

# ===================================================================== the lot: paving + plaza apron (all directions)
def lot(ctx, ox=0.0, oy=0.0, detail=1, street=False):
    """The 48 x 42 lot slab, the plaza apron (y -21..-7) with planters, bollards and the lit walkway to the glass door.
    street=True also lays the 8 BU border street ring round the lot (the map frame; the Cycles scenes bring their own streets)."""
    g = G(ctx, ox, oy, detail, False)
    cel = ctx.cel
    pave = (0.74, 0.80, 0.78) if cel else (0.10, 0.11, 0.105)
    pave2 = (0.62, 0.70, 0.68) if cel else (0.075, 0.085, 0.08)
    if street:
        asph = (0.07, 0.06, 0.15) if cel else (0.018, 0.018, 0.03)
        for (x0, y0, x1, y1) in ((-32.0, -29.0, 32.0, -21.0), (-32.0, 21.0, 32.0, 29.0), (-32.0, -21.0, -24.0, 21.0), (24.0, -21.0, 32.0, 21.0)):
            g.box("ground", x0, y0, 0.0, x1, y1, 0.12, asph, (0.5, 1.0, 0, 1))
        for q in range(-7, 8):                                    # dashed centre line of the border street (front side)
            g.box("neon_l", q * 4.0 - 1.0, -25.08, 0.12, q * 4.0 + 1.0, -24.92, 0.16, LIME, (0.8, 0, 0, 1))
    if street:
        for (x0, y0, x1, y1) in ((-24.0, -21.15, 24.0, -20.85), (-24.0, 20.85, 24.0, 21.15), (-24.15, -21.0, -23.85, 21.0), (23.85, -21.0, 24.15, 21.0)):
            g.box("neon_s", x0, y0, 0.25, x1, y1, 0.33, LIME, (1.0, 0, 0, 1))
    g.box("ground", -24.0, -21.0, 0.0, 24.0, 21.0, 0.25, pave, (0.55, 0.45, 0, 1))
    g.box("ground", -24.0, -21.0, 0.25, 24.0, -7.0, 0.30, pave2, (0.5, 0.5, 0, 1))
    # lime inlay: the walkway to the door and the apron edge
    for xs in (-1, 1):
        g.box("neon_s", xs * 3.2 - 0.07, -21.0, 0.30, xs * 3.2 + 0.07, -7.0, 0.34, LIME, (0.8, 0, 0, 1))
    g.box("neon_s", -24.0, -21.05, 0.30, 24.0, -20.93, 0.34, LIME, (0.8, 0, 0, 1))
    if detail >= 1:
        g.flat("neon_l", [(-2.2, -7.0, 0.32), (2.2, -7.0, 0.32), (6.5, -21.0, 0.32), (-6.5, -21.0, 0.32)], CREAM, (0.28, 0, 0, 1))   # the door's light fan on the paving
        # planter rows: a front row either side of the walkway, a back row against the building (the walkway runs through them)
        for (xa, xb) in ((-20.0, -12.0), (12.0, 20.0)):
            g.planter(xa, -20.4, xb, -18.9, 0.30, 0.9, r=0.85)
        for (xa, xb) in ((-21.0, -6.0), (6.0, 21.0)):
            g.planter(xa, -10.9, xb, -9.2, 0.30, 0.9, r=0.9)
        for sx in (-1, 1):
            g.palm(sx * 22.0, -15.0, 0.30, 6.2, 1.2)
            g.palm(sx * 22.4, -19.0, 0.30, 5.0, 1.0)
        for i in range(5):                                        # light bollards flanking the walkway
            for sx in (-1, 1):
                y = -19.5 + i * 2.7
                g.cyl("plain", sx * 5.2, y, 0.30, 1.1, 0.16, 6, g.PORC)
                g.cyl("neon_s", sx * 5.2, y, 1.1, 1.22, 0.17, 6, CREAM, (1.0, 0, 0, 1))
    return g
