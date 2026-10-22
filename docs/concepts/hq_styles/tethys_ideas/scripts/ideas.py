"""Five massing blockouts for the Tethys HQ (A jelly bloom, B coral spire, C whale fall, D man o' war, E manta).
Each idea_X(ns, hx, hy, rng, ang0) builds the whole HQ out of big simple shapes; landmark(ns) picks one by env IDEA.
Helpers (bell, siphonophore chain) come from the abyssal scripts (the designer liked the jellyfish bells)."""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "tethys_abyssal", "scripts")))
import tethys_preset as TP  # noqa: E402
import abyssal as AB  # noqa: E402
from tkit import tube  # noqa: E402

# a populated drowned city under the HQ: the zoning copy with the lot filled (fill_city.py) and no trench round the station
if os.environ.get("FILL_ZONED"):
    TP.ZONED_BASE = os.environ["FILL_ZONED"]
    TP.DEPTH = dict(TP.DEPTH, trench_r=0.0, blend=0.1)

U = (0.7071, 0.7071)       # screen right
V = (-0.7071, 0.7071)      # up the screen (away from the camera)
PHOTO, DIVE = TP.PHOTO, TP.DIVE
sc = AB._sc


def loc(hx, hy, x, y):
    return hx + U[0] * x + V[0] * y, hy + U[1] * x + V[1] * y


def ellipsoid(ns, acc, hx, hy, c, a, b, h, colf, n=28, rings=9, lower=True, glass=None, wet_z=None):
    """a (half) ellipsoid with semi axes a (screen-right), b (up-screen), h (vertical) at local centre c = (x, y, z)."""
    cx, cy = loc(hx, hy, c[0], c[1])
    lo = -rings if lower else 0
    for k in range(lo, rings):
        p0, p1 = math.pi / 2 * k / rings, math.pi / 2 * (k + 1) / rings
        for i in range(n):
            t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            pts = []
            for (p, t) in ((p0, t0), (p0, t1), (p1, t1), (p1, t0)):
                x, y = a * math.cos(p) * math.cos(t), b * math.cos(p) * math.sin(t)
                wx, wy = loc(cx - cx, cy - cy, x, y)
                pts.append((cx + wx + 0.0, cy + wy + 0.0, c[2] + h * math.sin(p)))
            if abs(pts[2][2] - pts[3][2]) < 1e-9 and abs(pts[0][2] - pts[1][2]) < 1e-9 and math.cos(p1) < 1e-6:
                pts = pts[:3]
            col = colf((p0 + p1) / 2, (t0 + t1) / 2, pts)
            wet = 1 if wet_z is not None and max(q[2] for q in pts) < wet_z else 0
            acc.face(pts, col, None, wet=wet)
            if glass is not None:
                glass.face([(q[0], q[1], q[2]) for q in pts], (0.8, 0.9, 1.0), None, wet=wet)


def landing(ns, hx, hy, ang0, r_end, target_xy=None):
    """the arrival: a plain pier head where the causeway lands, and a deck from it toward the HQ."""
    ZW = ns["ZW"]
    ax, ay = hx + r_end * math.cos(ang0), hy + r_end * math.sin(ang0)
    ns["box"](ns["SURF"], ax - 2.6, ay - 2.6, ZW - 0.6, ax + 2.6, ay + 2.6, ZW + 0.9, (0.55, 0.62, 0.68))
    ns["ring_line"](ns["NEON"], ax, ay, ZW + 0.95, 2.4, 0.2, sc(PHOTO, 1.0), n=12)
    tx, ty = target_xy if target_xy else (hx, hy)
    ns["bar"](ns["SURF"], (ax, ay, ZW + 0.7), (tx, ty, ZW + 0.7), 1.8, (0.55, 0.62, 0.68))
    return ax, ay


def drifters(ns, hx, hy, rng, ang0, n, rmin, rmax, zlo, zhi, Rr=(2.6, 4.6), gk=0.55, tl=(8, 13)):
    """the jelly-bell building: the Tethys district signature type. A handful stand on columns round the HQ (not part of it)."""
    ZW = ns["ZW"]
    gat = ns.get("ground_at")
    n = max(n, 8)
    for k in range(n):
        a = ang0 + 2 * math.pi * (k + rng.uniform(0.15, 0.85)) / n
        r = rng.uniform(48.0, 74.0)
        if abs((a - ang0 + math.pi) % (2 * math.pi) - math.pi) < 0.6:
            r = min(r, 54.0)
        x, y = hx + r * math.cos(a), hy + r * math.sin(a)
        R = rng.uniform(3.8, 5.6)
        rim = ZW + rng.uniform(6.0, 10.0)
        bed = gat(x, y) if gat else -60.0
        tube(ns["SMOOTH"], (x, y, bed), (x, y, rim), 1.0, 8, (0.46, 0.42, 0.56), wet=1)
        ns["ring_line"](ns["SURF"], x, y, ZW + 0.2, 1.6, 0.4, (0.5, 0.5, 0.6), n=12)
        AB.bell(ns, x, y, rim, R, rng, tents=12, tlen=rng.uniform(5.0, 8.0), hue=(0, 1, 2, 4)[rng.randrange(4)], tall=0.85, gk=0.9)


def lights(ns, hx, hy, zc, warm_at=None, warm_p=3.0e5):
    spot = ns["spot_at"]
    spot((hx, hy, zc), (hx + 0.7071 * 70 - 25, hy - 0.7071 * 70 - 10, ns["ZW"] + 95.0), (0.70, 0.92, 1.0), 0.9e6, 34.0)
    spot((hx, hy, zc - 4.0), (hx - 0.7071 * 60, hy + 0.7071 * 60, ns["ZW"] + 60.0), TP.ABYSS, 0.45e6, 40.0)
    if warm_at:
        spot((warm_at[0] + 6.0, warm_at[1] - 6.0, warm_at[2] + 16.0), warm_at, DIVE, warm_p, 45.0)


# ------------------------------------------------------------------------------------------------ A
def idea_A(ns, hx, hy, rng, ang0):
    ZW = ns["ZW"]
    NEON, GLASS, SURF = ns["NEON"], ns["GLASS"], ns["SURF"]
    R, zr = 27.0, ZW + 17.0
    AB.bell(ns, hx, hy, zr, R, rng, tents=24, tlen=30.0, hue=1, tall=0.95, gk=1.3)
    H = 0.95 * R
    for zf, k in ((4.0, 1.0), (9.0, 0.9), (14.0, 0.8), (19.0, 0.7)):         # lit floors inside the dome
        f = (zf / H) ** (1 / 0.72)
        a = math.acos(max(0.0, min(1.0, f)))
        rr = R * math.sin(a) ** 0.92 * 0.97
        ns["ring_line"](NEON, hx, hy, zr + zf, rr, 0.35, sc(DIVE, 1.1 * k), n=36)
    ns["cyl"](NEON, hx, hy, zr - 4.0, zr + 20.0, 2.2, 12, sc(DIVE, 1.6))          # the core tower
    # tentacle stilts and lift shafts: thick glowing tubes down to the seabed
    gat = ns.get("ground_at")
    for k in range(10):
        a = 2 * math.pi * (k + 0.5) / 10
        x0, y0 = hx + 0.86 * R * math.cos(a), hy + 0.86 * R * math.sin(a)
        pts = []
        for q in range(9):
            f = q / 8
            pts.append((x0 + 2.0 * math.sin(f * 5 + k) * f + 3.0 * f * math.cos(a), y0 + 2.0 * math.cos(f * 4 + k) * f + 3.0 * f * math.sin(a),
                        zr - 1.2 - f * 70.0))
        for q in range(8):
            tube(GLASS, pts[q], pts[q + 1], 1.1 - 0.5 * q / 8, 8, (0.7, 0.9, 1.0), wet=1 if pts[q][2] < ZW else 0)
            tube(NEON, pts[q], pts[q + 1], 0.28, 6, sc(PHOTO, 0.9), wet=1 if pts[q][2] < ZW else 0)
    drifters(ns, hx, hy, rng, ang0, 9, 40.0, 56.0, 5.0, 13.0)
    ax, ay = landing(ns, hx, hy, ang0, 38.0, (hx + 8 * math.cos(ang0), hy + 8 * math.sin(ang0)))
    lights(ns, hx, hy, zr + 6.0, (hx, hy, zr + 8.0), 4.0e5)
    return zr + H, (hx, hy, zr + 8.0)


# ------------------------------------------------------------------------------------------------ B
def idea_B(ns, hx, hy, rng, ang0):
    ZW = ns["ZW"]
    SM, NEON = ns["SMOOTH"], ns["NEON"]
    pods = []

    def branch(p, d, L, r, depth, col):
        e = (p[0] + d[0] * L, p[1] + d[1] * L, p[2] + d[2] * L)
        for q in range(2):
            a = tuple(p[m] + (e[m] - p[m]) * q / 2 for m in range(3))
            b = tuple(p[m] + (e[m] - p[m]) * (q + 1) / 2 for m in range(3))
            tube(SM, a, b, r * (1 - 0.15 * q), 8, col, wet=1 if b[2] < ZW else 0)
        for _ in range(2 + int(r * 0.9)):                       # polyp windows
            f = rng.uniform(0.15, 0.95)
            pc = tuple(p[m] + (e[m] - p[m]) * f for m in range(3))
            a = rng.uniform(0, 6.28)
            h = max(0.22, r * 0.28)
            ox, oy = pc[0] + math.cos(a) * r * 1.02, pc[1] + math.sin(a) * r * 1.02
            ns["box"](NEON, ox - h, oy - h, pc[2] - h, ox + h, oy + h, pc[2] + h, sc(DIVE if rng.random() < 0.7 else PHOTO, 0.9), wet=1 if pc[2] < ZW else 0)
        if depth == 0:
            ns["dome"](NEON, e[0], e[1], e[2], max(0.5, r * 1.3), sc(PHOTO, 1.0), n=8, rings=3)
            return
        nk = 3 if depth >= 3 else 2
        for k in range(nk):
            ph = rng.uniform(0, 6.28)
            sp = 1.05 if depth >= 3 else 1.15
            nd = (d[0] + math.cos(ph) * sp, d[1] + math.sin(ph) * sp, d[2] + 0.15)
            nl = math.sqrt(sum(c * c for c in nd))
            nd = tuple(c / nl for c in nd)
            c2 = tuple(min(1.0, c + 0.06) for c in col)
            branch(e, nd, L * 0.80, r * 0.68, depth - 1, c2)
            if depth == 2 and rng.random() < 0.8:
                pods.append(e)
    base = (hx, hy, ZW - 8.0)
    ellipsoid(ns, SM, hx, hy, (0, 0, ZW - 8.0), 17.0, 17.0, 11.0, lambda p, t, q: (0.80, 0.42, 0.46) if int(t * 5) % 2 else (0.70, 0.34, 0.40), n=24, rings=5, lower=False, wet_z=ZW)
    branch(base, (0.0, 0.0, 1.0), 13.0, 3.6, 4, (0.74, 0.28, 0.32))
    drifters(ns, hx, hy, rng, ang0, 7, 42.0, 56.0, 3.0, 8.0, gk=0.5)
    landing(ns, hx, hy, ang0, 38.0, (hx + 14 * math.cos(ang0), hy + 14 * math.sin(ang0)))
    lights(ns, hx, hy, ZW + 16.0, (hx, hy, ZW + 22.0), 3.0e5)
    return ZW + 34.0, (hx, hy, ZW + 22.0)


# ------------------------------------------------------------------------------------------------ C
def idea_C(ns, hx, hy, rng, ang0):
    ZW = ns["ZW"]
    SM, SURF, NEON = ns["SMOOTH"], ns["SURF"], ns["NEON"]
    bone, bone2 = (0.86, 0.82, 0.72), (0.68, 0.64, 0.56)
    z0 = ZW + 1.4

    def P(x, y, z):
        px, py = loc(hx, hy, x, y)
        return (px, py, z)

    def spine_y(x):
        return 3.0 * math.sin(x * 0.07)
    # deck (the rooms) along the spine
    for x in range(-34, 18, 4):
        a, b = P(x, spine_y(x), z0 - 0.5), P(x + 4, spine_y(x + 4), z0 - 0.5)
        w = 5.0 + 6.0 * math.sin(math.pi * min(1.0, max(0.0, (x + 34) / 52.0)))
        ns["bar"](SURF, a, b, w * 2.0, (0.20, 0.24, 0.28))
        if (x // 4) % 2 == 0:
            ns["bar"](NEON, P(x, spine_y(x) + w * 0.6, z0 + 0.1), P(x + 4, spine_y(x + 4) + w * 0.6, z0 + 0.1), 0.35, sc(DIVE, 1.1))
            ns["bar"](NEON, P(x, spine_y(x) - w * 0.6, z0 + 0.1), P(x + 4, spine_y(x + 4) - w * 0.6, z0 + 0.1), 0.35, sc(DIVE, 1.1))
    # the vertebral column
    for x in range(-48, 18, 3):
        s = 1.0 + 0.5 * (min(0.0, x + 34) / -14.0 * -1)
        r = 1.3 * (0.55 + 0.45 * min(1.0, (x + 52) / 30.0))
        p = P(x, spine_y(x), z0 + 0.6)
        ns["cyl"](SM, p[0], p[1], z0 - 0.4, z0 + 2.2, r, 8, bone2)
        ns["bar"](SM, (p[0], p[1], z0 + 2.0), (p[0], p[1], z0 + 4.0 + r), 0.5, bone2)
    # the ribs: an arcade of arches across the deck
    glow = []
    for x in range(-28, 14, 4):
        f = (x + 28) / 42.0
        w = 4.0 + 9.0 * math.sin(math.pi * (0.1 + 0.8 * f)) ** 0.8
        hh = 5.0 + 8.0 * math.sin(math.pi * (0.1 + 0.8 * f)) ** 0.9
        yc = spine_y(x)
        pts = [P(x, yc + w * math.sin(t), z0 + hh * (math.cos(t) ** 0.6) - 0.0 if abs(t) < 1.57 else z0) for t in [(-1.5708 + 3.1416 * k / 16) for k in range(17)]]
        for k in range(16):
            ns["bar"](SM, pts[k], pts[k + 1], 1.0 - 0.3 * abs(k - 8) / 8.0 * 0 + 0.0, bone)
        for k in range(3):
            q = pts[rng.randrange(2, 15)]
            glow.append(q)
    for q in glow:
        col = (PHOTO, (1.0, 0.25, 0.7), (0.3, 0.8, 1.0))[rng.randrange(3)]
        ns["dome"](NEON, q[0], q[1], q[2], rng.uniform(0.6, 1.0), sc(col, 1.4), n=8, rings=3)
    # the skull: the target hall
    sx = 22.0
    ellipsoid(ns, SURF, hx, hy, (sx, spine_y(sx), z0 - 0.5), 13.0, 8.5, 7.5, lambda p, t, q: bone if p > 0.3 else bone2, n=24, rings=6, lower=False)
    for sy in (-1, 1):                      # eye sockets / windows, glowing warm
        a = P(sx + 9.0, sy * 6.0 + spine_y(sx), z0 + 3.2)
        ns["box"](NEON, a[0] - 1.1, a[1] - 1.1, a[2] - 1.0, a[0] + 1.1, a[1] + 1.1, a[2] + 1.2, sc(DIVE, 2.4))
    for k in range(6):                       # the mouth slot: a warm hall under the brow
        a = P(sx + 4.0 + k * 2.2, spine_y(sx) - 8.0, z0 + 1.5)
        ns["box"](NEON, a[0] - 0.9, a[1] - 0.9, a[2] - 0.5, a[0] + 0.9, a[1] + 0.9, a[2] + 0.7, sc(DIVE, 2.0))
    jaw0, jaw1 = P(sx - 8.0, spine_y(sx) - 7.0, z0 - 0.2), P(sx + 20.0, spine_y(sx) - 3.5, z0 - 0.2)
    ns["bar"](SM, jaw0, jaw1, 2.6, bone)
    ns["spot"] if False else None
    drifters(ns, hx, hy, rng, ang0, 6, 42.0, 56.0, 3.0, 8.0, gk=0.5)
    landing(ns, hx, hy, ang0, 38.0, P(0, spine_y(0), z0)[:2])
    sk = P(sx, spine_y(sx), z0 + 3.0)
    lights(ns, hx, hy, ZW + 10.0, sk, 5.0e5)
    return z0 + 16.0, sk


# ------------------------------------------------------------------------------------------------ D
def idea_D(ns, hx, hy, rng, ang0):
    ZW = ns["ZW"]
    NEON, GLASS, SM = ns["NEON"], ns["GLASS"], ns["SMOOTH"]
    a, b, h = 28.0, 8.0, 10.0
    zc = ZW + 1.0

    def colf(p, t, q):
        x = math.cos(t)
        f = 0.5 + 0.5 * x
        g = f ** 3
        base = (0.20 + 0.75 * g, 0.38 - 0.1 * g, 1.0 - 0.3 * g)      # blue-violet, pink only at the bow
        return sc(base, 0.22 + 0.45 * max(0.0, math.sin(p)))
    ellipsoid(ns, NEON, hx, hy, (0, 0, zc), a, b, h, colf, n=36, rings=8, lower=True, glass=GLASS, wet_z=ZW)
    # the crest: a scalloped sail along the top
    n = 40
    for i in range(n):
        f0, f1 = i / n, (i + 1) / n
        xs = [-a * 0.9 + 1.8 * a * f for f in (f0, f1)]
        hs = [19.0 * math.sin(math.pi * f) ** 0.7 * (1 + 0.22 * math.sin(f * 22)) for f in (f0, f1)]
        zt = [zc + h * math.sqrt(max(0.0, 1 - (x / a) ** 2)) - 0.5 for x in xs]
        p00, p10 = loc(hx, hy, xs[0], 0.0), loc(hx, hy, xs[1], 0.0)
        col = sc((1.0, 0.25 + 0.4 * f0, 0.85), 1.6)
        for dy in (-0.15, 0.15):
            q0, q1 = loc(hx, hy, xs[0], dy), loc(hx, hy, xs[1], dy)
            NEON.face([(q0[0], q0[1], zt[0]), (q1[0], q1[1], zt[1]), (q1[0], q1[1], zt[1] + hs[1]), (q0[0], q0[1], zt[0] + hs[0])], col, None)
    # the route: chains of hanging pods and long tentacles down into the water
    for k in range(9):
        x = -19.0 + 4.7 * k
        y = rng.uniform(-4.0, 4.0)
        L = rng.uniform(34.0, 52.0)
        px, py = loc(hx, hy, x, y)
        drift = rng.uniform(-6.0, 6.0)
        pts = []
        for q in range(18):
            f = q / 17
            pts.append((px + drift * f * U[0] + 2.0 * math.sin(f * 6 + k), py + drift * f * U[1] + 2.0 * math.cos(f * 5 + k), zc - 4.0 - L * f))
        AB.siphon_poly(ns, pts, rng, 1.2, hang=True, gk=0.9)
    for k in range(5):                                       # long blue tentacles
        px, py = loc(hx, hy, rng.uniform(-18, 18), rng.uniform(-5, 5))
        pts = [(px + 5 * math.sin(q * 0.5 + k) * q / 20, py + 5 * math.cos(q * 0.4 + k) * q / 20, zc - 4.0 - q * 3.2) for q in range(21)]
        for q in range(20):
            ns["bar"](NEON, pts[q], pts[q + 1], 0.32, sc((0.25, 0.4, 1.0), 0.8), wet=1)
    drifters(ns, hx, hy, rng, ang0, 5, 42.0, 56.0, 0.8, 2.0, Rr=(2.0, 3.4), gk=0.5)
    landing(ns, hx, hy, ang0, 38.0, (hx + 14 * math.cos(ang0), hy + 14 * math.sin(ang0)))
    lights(ns, hx, hy, zc + 8.0, (hx, hy, zc + 6.0), 3.0e5)
    return zc + h + 11.0, (hx, hy, zc + 6.0)


# ------------------------------------------------------------------------------------------------ E
def idea_E(ns, hx, hy, rng, ang0):
    ZW = ns["ZW"]
    SURF, NEON, GLASS, SM = ns["SURF"], ns["NEON"], ns["GLASS"], ns["SMOOTH"]
    from tkit import obox
    flap = float(os.environ.get("FLAP", "0.0"))
    bank = float(os.environ.get("BANK", "0.14"))
    phi = math.radians(float(os.environ.get("LOOP_PHI", "-90.0")))     # where the manta is on its loop (-90 = the dam side, heading screen-right)
    zd = ZW + 10.0
    SC = 0.82
    # the loop: an ellipse round the compound, parallel to the dam walls (the dam runs along the screen-horizontal on the camera side)
    rx, ry = 66.0, 34.0
    cx_l, cy_l = loc(hx, hy, 0.0, 26.0)

    def loop_pt(f):
        return cx_l + U[0] * rx * math.cos(f) + V[0] * ry * math.sin(f), cy_l + U[1] * rx * math.cos(f) + V[1] * ry * math.sin(f)
    sx0, sy0 = loop_pt(math.radians(-90.0))
    sh = (hx - sx0, hy - sy0)               # the loop is shifted so that phi = -90 passes through the HQ spot
    mx, my = loop_pt(phi)
    mx, my = mx + sh[0], my + sh[1]
    tvx, tvy = -rx * math.sin(phi), ry * math.cos(phi)             # tangent in (U, V) coordinates (counter-clockwise from above)
    tl = math.hypot(tvx, tvy)
    Fw = ((U[0] * tvx + V[0] * tvy) / tl, (U[1] * tvx + V[1] * tvy) / tl)
    Rw = (Fw[1], -Fw[0])
    yaw = math.atan2(Fw[1], Fw[0])

    def L(x, y):
        return mx + (Rw[0] * x + Fw[0] * y) * SC, my + (Rw[1] * x + Fw[1] * y) * SC

    def zf(x):
        return zd + flap * abs(x) * 0.30 + bank * x * 0.30

    right = [(0, 22), (5, 26), (9, 21), (15, 18), (30, 13), (50, 2), (64, -12), (44, -14), (26, -18), (14, -20), (7, -22), (0, -23)]
    left = [(-x, y) for (x, y) in reversed(right[1:-1])]
    outline = right + left
    n = len(outline)
    P2 = [L(x, y) for (x, y) in outline]
    ZZ = [zf(x) for (x, y) in outline]
    for i in range(n):
        j = (i + 1) % n
        a, b = P2[i], P2[j]
        za, zb = ZZ[i], ZZ[j]
        col = (0.13, 0.17, 0.24) if (i % 2) else (0.11, 0.15, 0.21)
        SURF.face([(mx, my, zd + 1.0), (a[0], a[1], za + 1.0), (b[0], b[1], zb + 1.0)], col, None)
        SURF.face([(a[0], a[1], za + 1.0), (a[0], a[1], za - 1.2), (b[0], b[1], zb - 1.2), (b[0], b[1], zb + 1.0)], (0.24, 0.30, 0.38), None)
        SURF.face([(mx, my, zd - 1.2), (b[0], b[1], zb - 1.2), (a[0], a[1], za - 1.2)], (0.34, 0.40, 0.46), None)
        ns["bar"](NEON, (a[0], a[1], za + 1.05), (b[0], b[1], zb + 1.05), 0.40, sc(PHOTO, 1.3))
    # cephalic fins: two long curled horns at the head, clearly separate from the wings
    for sx in (-1, 1):
        pts = [(sx * (4.0 + 1.5 * k), 24.0 + 3.2 * k, zd + 0.3 + 0.12 * k) for k in range(10)]
        pts = [L(x, y) + (z,) for (x, y, z) in pts]
        for k in range(9):
            ns["bar"](SURF, pts[k], pts[k + 1], 3.0 * (1 - k / 10.0) + 0.4, (0.20, 0.26, 0.34))
        ns["bar"](NEON, pts[0], pts[-1], 0.22, sc(PHOTO, 1.4))
    # a few pale dorsal marks and two short rows of window lights, kept off the clean wing outline
    for sx in (-1, 1):
        for k in range(3):
            x, y = sx * (12.0 + 3.4 * k), 13.0 - 1.4 * k
            p = L(x, y)
            ns["box"](SURF, p[0] - 1.3, p[1] - 1.3, zf(x) + 0.95, p[0] + 1.3, p[1] + 1.3, zf(x) + 1.3, (0.80, 0.84, 0.88))
        for k in range(6):
            x, y = sx * (20.0 + 4.0 * k), 6.0 - 1.4 * k
            p = L(x, y)
            ns["box"](NEON, p[0] - 0.7, p[1] - 0.7, zf(x) + 0.95, p[0] + 0.7, p[1] + 0.7, zf(x) + 1.3, sc(DIVE, 1.1))
    # the tower cluster: low, grouped along the spine and centre (a flying arcology, so it still reads as a ray first)
    base = zd + 1.0
    towers = [(0, 0, 5.0, 5.5, 14.0), (0, -8, 3.6, 3.6, 8.0), (0, 8, 3.6, 3.6, 8.5), (-5, 2, 3.0, 3.0, 6.0), (5, 2, 3.0, 3.0, 6.5),
              (-4, -6, 2.6, 2.6, 5.0), (4, -6, 2.6, 2.6, 5.5), (0, 14, 2.6, 2.6, 4.5), (0, -14, 2.6, 2.6, 4.0)]
    for (x, y, w, d, h) in towers:
        p = L(x, y)
        obox(SURF, p[0], p[1], base, w * SC, d * SC, h, yaw, (0.10, 0.13, 0.19))
        for fz in range(1, int(h / 1.8)):                     # lit floors: thin bands round the tower
            obox(NEON, p[0], p[1], base + fz * 1.8, w * SC * 1.04, d * SC * 1.04, 0.22, yaw, sc(DIVE if (fz + int(x)) % 3 else PHOTO, 0.9), top=False)
        obox(NEON, p[0], p[1], base + h, w * SC * 1.02, d * SC * 1.02, 0.18, yaw, sc(PHOTO, 0.6))
    pc = L(0, 0)
    obox(NEON, pc[0], pc[1], base + 14.0 + 0.25, 3.0 * SC, 3.2 * SC, 1.6, yaw, sc(DIVE, 2.6))                  # the glowing crown: the target
    ns["ring_line"](NEON, pc[0], pc[1], base + 12.0, 4.4, 0.25, sc(DIVE, 1.4), n=20)
    ns["bar"](NEON, (pc[0], pc[1], base + 15.8), (pc[0], pc[1], base + 21.0), 0.18, sc(PHOTO, 1.8))
    # thruster pods under the wings, photophore glow at the rear (they poke out past the trailing edge)
    for (x, y) in ((-26, -9), (26, -9), (-13, -14), (13, -14)):
        p0, p1 = L(x, y + 7.0), L(x, y - 7.0)
        zp = zf(x) - 3.4
        tube(SURF, (p0[0], p0[1], zp), (p1[0], p1[1], zp), 2.1, 10, (0.30, 0.36, 0.44))
        p2 = L(x, y - 8.5)
        tube(NEON, (p1[0], p1[1], zp), (p2[0], p2[1], zp), 1.9, 10, sc(PHOTO, 2.6))
        ns["ring_line"](NEON, p2[0], p2[1], zp, 2.6, 0.16, sc(PHOTO, 1.6), n=14)
        ns["spot_at"]((p2[0], p2[1], ZW), (p2[0], p2[1], zp), PHOTO, 6.0e4, 70.0)
    # the tail: a segmented mechanical tail, curling down and trailing to one side
    prev = L(0, -23)
    pz = zd - 0.3
    for k in range(1, 15):
        x, y = 6.0 * math.sin(k * 0.45) * k / 12.0, -23.0 - 3.6 * k
        q = L(x, y)
        z = zd - 0.3 - 0.45 * k
        r = 1.5 * (1 - k / 17.0) + 0.2
        tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 8, (0.17, 0.22, 0.30) if k % 2 else (0.24, 0.30, 0.38))
        ns["box"](NEON, q[0] - r * 0.9, q[1] - r * 0.9, z - r * 0.5, q[0] + r * 0.9, q[1] + r * 0.9, z + r * 0.5, sc(PHOTO, 1.5))
        prev, pz = q, z
    # downwash: ripple rings on the water under the body, and the wake foam along the loop behind the manta
    for k, rr in enumerate((13.0, 19.0, 26.0, 34.0)):
        ns["ring_line"](NEON, mx + 6.0, my - 6.0, ZW + 0.13, rr, 0.24, sc((0.75, 0.95, 1.0), 0.75 - 0.15 * k), n=48)
    prevw = None
    for k in range(0, 40):
        f = phi - math.radians(1.6) * k
        wx, wy = loop_pt(f)
        wx, wy = wx + sh[0], wy + sh[1]
        if prevw:
            ns["bar"](NEON, prevw, (wx, wy, ZW + 0.14), 0.55 * (1 - k / 44.0), sc((0.8, 0.95, 1.0), 0.8 * (1 - k / 40.0) + 0.05))
        prevw = (wx, wy, ZW + 0.14)
    for sx in (-1, 1):
        p = L(sx * 64.0, -12.0)
        for rr in (2.0, 4.0, 6.5):
            ns["ring_line"](NEON, p[0], p[1], ZW + 0.12, rr, 0.16, sc((0.8, 0.95, 1.0), 0.5), n=20)
    # the loop itself: a faint dashed line on the water, parallel to the dam walls
    for k in range(90):
        if k % 2:
            continue
        a0, a1 = loop_pt(2 * math.pi * k / 90), loop_pt(2 * math.pi * (k + 1) / 90)
        ns["bar"](NEON, (a0[0] + sh[0], a0[1] + sh[1], ZW + 0.12), (a1[0] + sh[0], a1[1] + sh[1], ZW + 0.12), 0.35, sc(PHOTO, 0.5))
    import json
    sj = os.environ.get("SHADOW_JSON")
    if sj:
        json.dump(dict(outline=[list(p) for p in P2], zd=zd, ZW=ZW, centre=[mx, my], tail=[list(prev)], fwd=list(Fw)), open(sj, "w"))
    # cool cyan uplight from the water onto the belly
    ns["spot_at"]((mx, my, ZW - 6.0), (mx, my, zd - 1.2), (0.30, 0.95, 1.0), 2.5e5, 60.0)
    landing(ns, hx, hy, ang0, 38.0, (hx + 10 * math.cos(ang0), hy + 10 * math.sin(ang0)))
    drifters(ns, hx, hy, rng, ang0, 8, 48.0, 74.0, 6.0, 10.0)
    c = (pc[0], pc[1], base + 15.0)
    lights(ns, hx, hy, zd + 4.0, c, 4.0e5)
    return zd + 22.0, c


def idea_M(ns, hx, hy, rng, ang0):
    """MANTA detail pass: curved triangular wings with drooping tips and a rounded leading edge, horn-like head fins, a slim whip tail
    with a segmented mechanical section, a stepped lit arcology on the spine, wing-edge lights and pads, trailing-edge thrusters,
    natural downwash ripples and spray, the wake along the loop, a cyan belly uplight."""
    ZW = ns["ZW"]
    SURF, NEON, GLASS, SM = ns["SURF"], ns["NEON"], ns["GLASS"], ns["SMOOTH"]
    from tkit import obox, frustum
    flap = float(os.environ.get("FLAP", "0.0"))
    bank = float(os.environ.get("BANK", "0.14"))
    phi = math.radians(float(os.environ.get("LOOP_PHI", "-90.0")))
    zd = ZW + 10.0
    SC = 0.95
    rx, ry = 66.0, 34.0
    cx_l, cy_l = loc(hx, hy, 0.0, 26.0)

    def loop_pt(f):
        return cx_l + U[0] * rx * math.cos(f) + V[0] * ry * math.sin(f), cy_l + U[1] * rx * math.cos(f) + V[1] * ry * math.sin(f)
    sx0, sy0 = loop_pt(math.radians(-90.0))
    sh = (hx - sx0 + V[0] * 6.0, hy - sy0 + V[1] * 6.0)
    mx, my = loop_pt(phi)
    mx, my = mx + sh[0], my + sh[1]
    tvx, tvy = -rx * math.sin(phi), ry * math.cos(phi)
    tl = math.hypot(tvx, tvy)
    Fw = ((U[0] * tvx + V[0] * tvy) / tl, (U[1] * tvx + V[1] * tvy) / tl)
    Rw = (Fw[1], -Fw[0])
    yaw = math.atan2(Fw[1], Fw[0])

    def L(x, y):
        return mx + (Rw[0] * x + Fw[0] * y) * SC, my + (Rw[1] * x + Fw[1] * y) * SC

    def zf(x):
        return zd + flap * abs(x) * 0.30 + bank * x * 0.30 - 5.5 * (abs(x) / 66.0) ** 2.2        # the tips droop

    def y_te(x):
        s = max(0.0, min(1.0, (66.0 - abs(x)) / 52.0))
        return -12.0 - 3.0 * s + 5.0 * math.sin(math.pi * s) ** 1.2

    # ---- the wings: a rounded leading edge, pointed drooping tips, a concave trailing edge
    right = [(0, 24), (4, 23.5), (8, 21.5)]
    for k in range(0, 15):
        t = k / 14.0
        right.append((9 + 57 * t, 21 - 33 * t ** 1.5))
    for k in range(1, 15):
        s = k / 14.0
        right.append((66 - 52 * s, -12.0 - 3.0 * s + 5.0 * math.sin(math.pi * s) ** 1.2))
    right += [(9, -17), (6, -21), (0, -23)]
    left = [(-x, y) for (x, y) in reversed(right[1:-1])]
    outline = right + left
    n = len(outline)
    P2 = [L(x, y) for (x, y) in outline]
    ZZ = [zf(x) for (x, y) in outline]
    IN = [L(0.5 * x, 0.5 * y) for (x, y) in outline]
    IZ = [zf(0.5 * x) for (x, y) in outline]
    tones = [(0.16, 0.20, 0.28), (0.14, 0.18, 0.26), (0.18, 0.22, 0.30)]
    for i in range(n):
        j = (i + 1) % n
        a, b, a2, b2 = P2[i], P2[j], IN[i], IN[j]
        col = tones[(i // 2) % 3]
        SURF.face([(mx, my, zd + 1.0), (a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0)], tones[0], None)
        SURF.face([(a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0), (b[0], b[1], ZZ[j] + 1.0), (a[0], a[1], ZZ[i] + 1.0)], col, None)
        SURF.face([(a[0], a[1], ZZ[i] + 1.0), (a[0], a[1], ZZ[i] - 1.1), (b[0], b[1], ZZ[j] - 1.1), (b[0], b[1], ZZ[j] + 1.0)], (0.26, 0.32, 0.40), None)
        SURF.face([(a[0], a[1], ZZ[i] - 1.1), (b[0], b[1], ZZ[j] - 1.1), (b2[0], b2[1], IZ[j] - 1.1), (a2[0], a2[1], IZ[i] - 1.1)], (0.34, 0.40, 0.46), None)
        SURF.face([(mx, my, zd - 1.1), (b2[0], b2[1], IZ[j] - 1.1), (a2[0], a2[1], IZ[i] - 1.1)], (0.34, 0.40, 0.46), None)
        ns["bar"](NEON, (a[0], a[1], ZZ[i] + 1.05), (b[0], b[1], ZZ[j] + 1.05), 0.34, sc(PHOTO, 1.2))
        # panel seams: a faint ring at 0.75 of the outline
        c0, c1 = L(0.75 * outline[i][0], 0.75 * outline[i][1]), L(0.75 * outline[j][0], 0.75 * outline[j][1])
        ns["bar"](NEON, (c0[0], c0[1], zf(0.75 * outline[i][0]) + 1.03), (c1[0], c1[1], zf(0.75 * outline[j][0]) + 1.03), 0.12, sc(PHOTO, 0.28))
    nle0 = 3
    for k in range(0, 15, 1):                       # leading-edge running lights
        for sx in (-1, 1):
            x, y = right[nle0 + k]
            p = L(sx * x, y)
            ns["box"](NEON, p[0] - 0.35, p[1] - 0.35, zf(x) + 1.05, p[0] + 0.35, p[1] + 0.35, zf(x) + 1.45, sc(DIVE if k % 2 else (1.0, 1.0, 1.0), 1.4))
    for sx in (-1, 1):                              # spars and landing pads
        for k in range(6):
            f = k / 5.0
            a = L(sx * 12.0, 8.0 - 12.0 * f)
            b = L(sx * (56.0 - 10.0 * f), -4.0 - 8.0 * f)
            ns["bar"](NEON, (a[0], a[1], zf(12.0) + 1.04), (b[0], b[1], zf(56.0 - 10 * f) + 1.04), 0.14, sc(PHOTO, 0.3))
        for (px_, py_) in ((24, 7), (36, 1), (46, -6)):
            p = L(sx * px_, py_)
            z0 = zf(px_) + 1.0
            ns["cyl"](SURF, p[0], p[1], z0, z0 + 0.15, 2.6 * SC, 16, (0.34, 0.38, 0.44))
            ns["ring_line"](NEON, p[0], p[1], z0 + 0.18, 2.4 * SC, 0.14, sc(PHOTO, 1.1), n=16)
            ns["bar"](NEON, (p[0] - 0.9, p[1], z0 + 0.2), (p[0] + 0.9, p[1], z0 + 0.2), 0.12, sc(DIVE, 1.0))
    # ---- cephalic fins: two horn-like curled head lobes
    for sx in (-1, 1):
        pts = []
        for k in range(12):
            y = 22.0 + 3.0 * k
            x = sx * (5.0 + 0.7 * k + 0.16 * k * k)
            pts.append(L(x, y) + (zd + 0.4 + 0.10 * k,))
        for k in range(11):
            ns["bar"](SURF, pts[k], pts[k + 1], 4.2 * (1 - k / 12.0) + 0.6, (0.22, 0.28, 0.36))
        for k in range(11):
            ns["bar"](NEON, pts[k], pts[k + 1], 0.2, sc(PHOTO, 1.3))
    # ---- the tail: a segmented mechanical section, then a slim whip
    prev = L(0, -23)
    pz = zd - 0.6
    for k in range(1, 28):
        x, y = 7.0 * math.sin(k * 0.38) * min(1.0, k / 12.0), -23.0 - 3.3 * k
        q = L(x, y)
        z = zd - 0.6 - 0.28 * k
        if k <= 8:
            r = 1.7 - 0.1 * k
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 8, (0.18, 0.24, 0.32) if k % 2 else (0.26, 0.32, 0.40))
            ns["box"](NEON, q[0] - r * 0.95, q[1] - r * 0.95, z - r * 0.35, q[0] + r * 0.95, q[1] + r * 0.95, z + r * 0.35, sc(PHOTO, 1.4))
        else:
            r = 0.45 * (1 - (k - 8) / 22.0) + 0.1
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 6, (0.20, 0.26, 0.34))
        prev, pz = q, z
    ns["dome"](NEON, prev[0], prev[1], pz, 0.5, sc(PHOTO, 2.4), n=8, rings=3, hemi=False)
    # ---- the arcology: stepped and lit, kept inside the body
    base = zd + 1.0
    tiers = [(0, 0, 15, 22, 3.0), (0, 0, 11, 17, 7.0), (0, 0, 7.5, 12, 12.0), (0, 0, 4.6, 6.2, 19.0)]
    side = [(0, 13, 4, 4, 8.5), (0, -13, 4, 4, 7.5), (-6, 6, 3, 3, 6.5), (6, 6, 3, 3, 7.0), (-6, -6, 3, 3, 5.5), (6, -6, 3, 3, 6.0), (0, 18, 3, 3, 4.5), (0, -18, 3, 3, 4.0)]
    wrng = random.Random(41)

    def tower(x, y, w, d, h):
        p = L(x, y)
        obox(SURF, p[0], p[1], base, w * SC, d * SC, h, yaw, (0.10, 0.13, 0.19))
        ax, ay = math.cos(yaw), math.sin(yaw)
        bx, by = -ay, ax
        hl, hw = d * SC / 2.0, w * SC / 2.0
        for fz in range(1, int(h / 1.7)):
            z = base + fz * 1.7
            obox(NEON, p[0], p[1], z, d * SC * 1.03, w * SC * 1.03, 0.12, yaw, sc(PHOTO, 0.22), top=False)
            for (nx, ny, hx_, u_ax, span) in ((ax, ay, hl, (bx, by), hw), (-ax, -ay, hl, (bx, by), hw), (bx, by, hw, (ax, ay), hl), (-bx, -by, hw, (ax, ay), hl)):
                u = -span + 0.9
                while u < span - 0.5:
                    if wrng.random() < 0.42:
                        wx, wy = p[0] + nx * (hx_ + 0.03) + u_ax[0] * u, p[1] + ny * (hx_ + 0.03) + u_ax[1] * u
                        obox(NEON, wx, wy, z + 0.5, 0.42, 0.42, 0.55, yaw, sc(DIVE if wrng.random() < 0.7 else PHOTO, 0.8), top=False)
                    u += 1.35
        obox(NEON, p[0], p[1], base + h, d * SC * 1.02, w * SC * 1.02, 0.16, yaw, sc(PHOTO, 0.5), top=False)
        return p
    for (x, y, w, d, h) in side + tiers:
        tower(x, y, w, d, h)
    pc = L(0, 0)
    hc = 19.0
    obox(SURF, pc[0], pc[1], base + hc, 2.8 * SC, 3.2 * SC, 7.0, yaw, (0.12, 0.16, 0.22))                # the crown tower
    obox(NEON, pc[0], pc[1], base + hc + 7.0, 3.0 * SC, 3.4 * SC, 1.6, yaw, sc(DIVE, 2.8))
    ns["ring_line"](NEON, pc[0], pc[1], base + hc + 5.0, 3.6, 0.2, sc(DIVE, 1.4), n=20)
    ns["bar"](NEON, (pc[0], pc[1], base + hc + 8.6), (pc[0], pc[1], base + hc + 14.0), 0.18, sc(PHOTO, 2.0))
    # ---- thrusters on the trailing edge, angled out, photophore teal
    thr = []
    for sx in (-1, 1):
        for xx in (16.0, 34.0):
            x = sx * xx
            y = y_te(xx)
            dirx, diry = sx * 0.35, -1.0
            dl = math.hypot(dirx, diry)
            dirx, diry = dirx / dl, diry / dl
            p0 = L(x - dirx * 3.0, y - diry * 3.0)
            p1 = L(x + dirx * 8.0, y + diry * 8.0)
            zp = zf(xx * sx) - 0.2
            tube(SURF, (p0[0], p0[1], zp + 0.2), (p1[0], p1[1], zp), 2.4, 10, (0.30, 0.36, 0.44))
            p2 = L(x + dirx * 9.6, y + diry * 9.6)
            tube(NEON, (p1[0], p1[1], zp), (p2[0], p2[1], zp - 0.1), 2.0, 10, sc(PHOTO, 2.0))
            ns["ring_line"](NEON, p2[0], p2[1], zp - 0.1, 2.8, 0.18, sc(PHOTO, 1.8), n=14)
            frustum(NEON, p2[0], p2[1], ZW + 0.4, zp - 0.4, 1.6, 0.9, 12, sc(PHOTO, 0.28))                # the jet column down to the water
            ns["spot_at"]((p2[0], p2[1], ZW + 0.5), (p2[0], p2[1], zp), PHOTO, 8.0e4, 70.0)
            thr.append((p2[0], p2[1]))
    # ---- water: soft, irregular downwash ripples and spray, the wake along the loop, the faint dashed loop
    wr = random.Random(77)
    for (tx, ty) in thr:
        for rr in (3.5, 6.5, 10.0):
            ph = wr.uniform(0, 6.28)
            prevq = None
            for k in range(0, 33):
                th = 2 * math.pi * k / 32
                rad = rr * (1 + 0.16 * math.sin(3 * th + ph) + 0.08 * math.sin(7 * th + 2 * ph))
                q = (tx + rad * math.cos(th), ty + rad * math.sin(th), ZW + 0.12)
                if prevq and wr.random() < 0.72:
                    ns["bar"](NEON, prevq, q, 0.22, sc((0.75, 0.95, 1.0), 0.40 - 0.08 * (rr / 4.0)))
                prevq = q
        for k in range(16):                           # spray
            a = wr.uniform(0, 6.28)
            d = wr.uniform(0.5, 6.0)
            z = ZW + wr.uniform(0.2, 2.6)
            r = wr.uniform(0.15, 0.4)
            ns["dome"](NEON, tx + d * math.cos(a), ty + d * math.sin(a), z, r, sc((0.8, 0.96, 1.0), 1.3), n=6, rings=2, hemi=False)
    for (rr, ex) in ((22.0, 1.25), (32.0, 1.2)):      # a broad, broken swell under the whole body
        ph = wr.uniform(0, 6.28)
        prevq = None
        for k in range(0, 49):
            th = 2 * math.pi * k / 48
            rad = rr * (1 + 0.10 * math.sin(2 * th + ph) + 0.05 * math.sin(5 * th))
            lx, ly = rad * ex * math.cos(th), rad * math.sin(th)
            q = (mx + Rw[0] * lx + Fw[0] * ly, my + Rw[1] * lx + Fw[1] * ly, ZW + 0.1)
            if prevq and wr.random() < 0.6:
                ns["bar"](NEON, prevq, q, 0.30, sc((0.75, 0.95, 1.0), 0.22))
            prevq = q
    prevw = None
    for k in range(0, 40):
        f = phi - math.radians(1.6) * k
        wx, wy = loop_pt(f)
        wx, wy = wx + sh[0], wy + sh[1]
        if prevw:
            ns["bar"](NEON, prevw, (wx, wy, ZW + 0.14), 0.50 * (1 - k / 44.0), sc((0.8, 0.95, 1.0), 0.65 * (1 - k / 40.0) + 0.05))
        prevw = (wx, wy, ZW + 0.14)
    for k in range(90):
        if k % 2:
            continue
        a0, a1 = loop_pt(2 * math.pi * k / 90), loop_pt(2 * math.pi * (k + 1) / 90)
        ns["bar"](NEON, (a0[0] + sh[0], a0[1] + sh[1], ZW + 0.12), (a1[0] + sh[0], a1[1] + sh[1], ZW + 0.12), 0.33, sc(PHOTO, 0.45))
    import json
    sj = os.environ.get("SHADOW_JSON")
    if sj:
        json.dump(dict(outline=[list(p) for p in P2], zd=zd, ZW=ZW, centre=[mx, my], tail=[list(prev)], fwd=list(Fw)), open(sj, "w"))
    ns["spot_at"]((mx, my, ZW - 6.0), (mx, my, zd - 1.2), (0.30, 0.95, 1.0), 3.0e5, 60.0)       # cool cyan uplight from the water onto the belly
    landing(ns, hx, hy, ang0, 38.0, (hx + 10 * math.cos(ang0), hy + 10 * math.sin(ang0)))
    drifters(ns, hx, hy, rng, ang0, 8, 48.0, 74.0, 6.0, 10.0)
    c = (pc[0], pc[1], base + hc + 8.0)
    lights(ns, hx, hy, zd + 4.0, c, 4.5e5)
    return zd + 36.0, c


def idea_N(ns, hx, hy, rng, ang0):
    """MANTA v3: flat broad wings (span about 2x the body, bank about 10 degrees, no droop), short paddle cephalic lobes, a long mostly straight
    tail with a gentle C, pale teal-blue skin with a neon outline, white kakau-style bands and niho mano rows, a Hawaiian arcology (heiau
    terraces, hale with steep thatched roofs, lanai, a tall crown hale), teal trailing-edge thrusters, patchy bioluminescent algae in the water."""
    ZW = ns["ZW"]
    SURF, NEON, GLASS, SM = ns["SURF"], ns["NEON"], ns["GLASS"], ns["SMOOTH"]
    from tkit import obox, frustum
    flap = float(os.environ.get("FLAP", "0.0"))
    bank = float(os.environ.get("BANK", "0.1736"))                        # tan(10 deg): about 10 degrees of bank
    phi = math.radians(float(os.environ.get("LOOP_PHI", "-90.0")))
    zd = ZW + 10.0
    SC = 1.0
    rx, ry = 66.0, 34.0
    cx_l, cy_l = loc(hx, hy, 0.0, 26.0)

    def loop_pt(f):
        return cx_l + U[0] * rx * math.cos(f) + V[0] * ry * math.sin(f), cy_l + U[1] * rx * math.cos(f) + V[1] * ry * math.sin(f)
    sx0, sy0 = loop_pt(math.radians(-90.0))
    sh = (hx - sx0 + V[0] * 4.0, hy - sy0 + V[1] * 4.0)
    mx, my = loop_pt(phi)
    mx, my = mx + sh[0], my + sh[1]
    tvx, tvy = -rx * math.sin(phi), ry * math.cos(phi)
    tl = math.hypot(tvx, tvy)
    Fw = ((U[0] * tvx + V[0] * tvy) / tl, (U[1] * tvx + V[1] * tvy) / tl)
    Rw = (Fw[1], -Fw[0])
    yaw = math.atan2(Fw[1], Fw[0])

    def L(x, y):
        return mx + (Rw[0] * x + Fw[0] * y) * SC, my + (Rw[1] * x + Fw[1] * y) * SC

    def zf(x):
        return zd + flap * abs(x) * 0.30 + bank * x

    HS = 52.0                                                          # half span; body length 47 -> span about 2.2 x body

    def y_te(x):
        s = max(0.0, min(1.0, (HS - abs(x)) / 40.0))
        return -9.0 - 2.0 * s + 3.5 * math.sin(math.pi * s) ** 1.2

    BODY = (0.40, 0.56, 0.64)                                           # a lighter, desaturated Tethys teal-blue
    tones = [(0.40, 0.56, 0.64), (0.37, 0.53, 0.62), (0.43, 0.59, 0.66)]
    WHITE = (0.92, 0.95, 0.98)
    EDGE = sc(PHOTO, 1.9)
    # ---- the wing planform
    right = [(0, 24), (4, 23.5), (8, 21.5)]
    le = []
    for k in range(0, 15):
        t = k / 14.0
        le.append((9 + (HS - 9) * t, 21 - 30 * t ** 1.5))
    right += le
    for k in range(1, 15):
        s = k / 14.0
        right.append((HS - 40 * s, y_te(HS - 40 * s)))
    right += [(9, -17), (6, -21), (0, -23)]
    left = [(-x, y) for (x, y) in reversed(right[1:-1])]
    outline = right + left
    n = len(outline)
    P2 = [L(x, y) for (x, y) in outline]
    ZZ = [zf(x) for (x, y) in outline]
    IN = [L(0.5 * x, 0.5 * y) for (x, y) in outline]
    IZ = [zf(0.5 * x) for (x, y) in outline]
    for i in range(n):
        j = (i + 1) % n
        a, b, a2, b2 = P2[i], P2[j], IN[i], IN[j]
        col = tones[(i // 2) % 3]
        SURF.face([(mx, my, zd + 1.0), (a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0)], tones[0], None)
        SURF.face([(a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0), (b[0], b[1], ZZ[j] + 1.0), (a[0], a[1], ZZ[i] + 1.0)], col, None)
        SURF.face([(a[0], a[1], ZZ[i] + 1.0), (a[0], a[1], ZZ[i] - 1.0), (b[0], b[1], ZZ[j] - 1.0), (b[0], b[1], ZZ[j] + 1.0)], (0.50, 0.64, 0.70), None)
        SURF.face([(a[0], a[1], ZZ[i] - 1.0), (b[0], b[1], ZZ[j] - 1.0), (b2[0], b2[1], IZ[j] - 1.0), (a2[0], a2[1], IZ[i] - 1.0)], (0.55, 0.68, 0.74), None)
        SURF.face([(mx, my, zd - 1.0), (b2[0], b2[1], IZ[j] - 1.0), (a2[0], a2[1], IZ[i] - 1.0)], (0.55, 0.68, 0.74), None)
        ns["bar"](NEON, (a[0], a[1], ZZ[i] + 1.04), (b[0], b[1], ZZ[j] + 1.04), 0.38, EDGE)           # the continuous neon outline
    # ---- white kakau-style patterning on the dorsal skin (generic bands, shark-tooth rows, lozenges, chevrons)
    zt = 1.045

    def PZ(x, y):
        p = L(x, y)
        return (p[0], p[1], zf(x) + zt)

    def strip(a, b, w):
        pa, pb = PZ(*a), PZ(*b)
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        dl = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / dl * w / 2, dx / dl * w / 2
        SURF.face([(pa[0] - nx, pa[1] - ny, pa[2]), (pa[0] + nx, pa[1] + ny, pa[2]), (pb[0] + nx, pb[1] + ny, pb[2]), (pb[0] - nx, pb[1] - ny, pb[2])], WHITE, None)

    def poly(pts):
        SURF.face([PZ(*p) for p in pts], WHITE, None)

    def inward(p, k=1.0):
        v = (0.0 - p[0], 3.0 - p[1])
        d = math.hypot(*v) or 1.0
        return (v[0] / d * k, v[1] / d * k)
    for sx in (-1, 1):
        base_pts = []
        for (x, y) in le:
            iv = inward((x, y), 1.8)
            base_pts.append((sx * (x + iv[0]), y + iv[1]))
        for k in range(len(le) - 1):                       # niho mano: a row of shark-tooth triangles along the leading edge
            a, b = base_pts[k], base_pts[k + 1]
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            iv = inward((abs(mid[0]), mid[1]), 3.6 * (1 - 0.45 * k / 14.0))
            apex = (mid[0] + sx * iv[0], mid[1] + iv[1])
            poly([a, b, apex])
            strip(a, b, 0.7)
        for k in range(len(le) - 1):                       # a second, inner band following the wing curve
            a, b = le[k], le[k + 1]
            ia, ib = inward(a, 8.6), inward(b, 8.6)
            strip((sx * (a[0] + ia[0]), a[1] + ia[1]), (sx * (b[0] + ib[0]), b[1] + ib[1]), 0.8)
        tipc = (sx * (HS - 1.0), -8.0)                      # a solid triangle cap at the tip
        poly([tipc, (sx * le[11][0], le[11][1] - 3.0), (sx * (HS - 9.0), y_te(HS - 9.0) + 2.0)])
        for k in range(4):                                   # lozenges (diamond rows) along the wing
            cxl, cyl = 16.0 + 8.0 * k, 3.5 - 2.2 * k
            poly([(sx * (cxl - 2.6), cyl), (sx * cxl, cyl + 3.4), (sx * (cxl + 2.6), cyl), (sx * cxl, cyl - 3.4)])
        for j in range(3):                                   # nested chevrons pointing forward on the rear body
            strip((sx * 6.5, -18.5 - 2.6 * j), (0, -13.0 - 2.6 * j), 0.9)
    # ---- short paddle-like cephalic lobes (about 1/7 of the body), curled forward and inward
    for sx in (-1, 1):
        lobe = [(sx * 2.0, 23.3), (sx * 6.6, 22.6), (sx * 6.2, 27.6), (sx * 4.6, 30.0), (sx * 3.0, 28.4)]
        LP = [L(x, y) for (x, y) in lobe]
        for i in range(len(lobe)):
            j = (i + 1) % len(lobe)
            SURF.face([(mx, my, zd + 1.0)] * 0 or [(LP[i][0], LP[i][1], zf(lobe[i][0]) + 1.0), (LP[j][0], LP[j][1], zf(lobe[j][0]) + 1.0),
                                                     (LP[j][0], LP[j][1], zf(lobe[j][0]) + 0.0), (LP[i][0], LP[i][1], zf(lobe[i][0]) + 0.0)], BODY, None)
            ns["bar"](NEON, (LP[i][0], LP[i][1], zf(lobe[i][0]) + 1.04), (LP[j][0], LP[j][1], zf(lobe[j][0]) + 1.04), 0.24, EDGE)
        cen = L(sx * 4.5, 26.0)
        SURF.face([(p[0], p[1], zf(q[0]) + 1.0) for p, q in zip(LP, lobe)], tones[1], None)
    # ---- the tail: segmented mechanical root, then a slim whip, long and almost straight with a gentle C
    prev = L(0, -23)
    pz = zd - 0.6
    for k in range(1, 31):
        u = k / 30.0
        x, y = 5.0 * math.sin(math.pi * u), -23.0 - 2.1 * k
        q = L(x, y)
        z = zd - 0.6 - 0.10 * k
        if k <= 6:
            r = 1.6 - 0.1 * k
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 8, (0.46, 0.60, 0.68) if k % 2 else (0.40, 0.54, 0.62))
            ns["box"](NEON, q[0] - r * 0.9, q[1] - r * 0.9, z - r * 0.3, q[0] + r * 0.9, q[1] + r * 0.9, z + r * 0.3, sc(PHOTO, 1.1))
        else:
            r = 0.42 * (1 - (k - 6) / 26.0) + 0.1
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 6, (0.44, 0.58, 0.66))
        ns["bar"](NEON, (prev[0], prev[1], pz + 0.25), (q[0], q[1], z + 0.25), 0.10, EDGE)
        prev, pz = q, z
    ns["dome"](NEON, prev[0], prev[1], pz, 0.45, sc(PHOTO, 1.8), n=8, rings=3, hemi=False)
    # ---- the Hawaiian arcology: heiau terraces, hale with steep thatched roofs, lanai decks, a tall crown hale
    base = zd - 1.0
    stone = [(0.10, 0.09, 0.09), (0.12, 0.10, 0.10), (0.09, 0.08, 0.08)]
    terr = [(14.0, 22.0), (10.5, 16.0), (7.0, 10.5)]            # (across, along) widths of the three heiau tiers
    th = 1.7
    wrng = random.Random(23)

    def dots(p, w, d, z0, h):
        ax, ay = math.cos(yaw), math.sin(yaw)
        bx, by = -ay, ax
        for (nx, ny, off, ux, uy, span) in ((ax, ay, d * SC / 2, bx, by, w * SC / 2), (-ax, -ay, d * SC / 2, bx, by, w * SC / 2),
                                            (bx, by, w * SC / 2, ax, ay, d * SC / 2), (-bx, -by, w * SC / 2, ax, ay, d * SC / 2)):
            u = -span + 0.9
            while u < span - 0.5:
                if wrng.random() < 0.45:
                    obox(NEON, p[0] + nx * (off + 0.03) + ux * u, p[1] + ny * (off + 0.03) + uy * u, z0 + 0.7, 0.4, 0.4, 0.45, yaw, sc(DIVE, 0.8), top=False)
                u += 1.4
    z = base
    pc = L(0, 0)
    for i, (w, d) in enumerate(terr):
        obox(SURF, pc[0], pc[1], z, d * SC, w * SC, th, yaw, stone[i])
        obox(NEON, pc[0], pc[1], z + th - 0.2, d * SC * 1.01, w * SC * 1.01, 0.2, yaw, sc(DIVE, 0.7), top=False)            # lit terrace lip (lanai edge)
        dots(pc, w, d, z, th)
        z += th

    def hale(x, y, w, d, hw, hr, z0, glow=0.6, ridge_glow=1.0):
        p = L(x, y)
        ax, ay = math.cos(yaw), math.sin(yaw)
        bx, by = -ay, ax

        def C(sx, sy, e=0.0):
            return (p[0] + bx * sx * (w / 2 + e) * SC + ax * sy * (d / 2 + e) * SC, p[1] + by * sx * (w / 2 + e) * SC + ay * sy * (d / 2 + e) * SC)
        obox(NEON, p[0], p[1], z0, d * 0.92 * SC, w * 0.92 * SC, hw, yaw, sc(DIVE, glow), top=False)                   # the lit open interior
        for sx_ in (-1, 1):
            for sy_ in (-1, 1):
                c = C(sx_, sy_)
                ns["bar"](SURF, (c[0], c[1], z0), (c[0], c[1], z0 + hw + 0.2), 0.32, (0.24, 0.15, 0.09))                # posts
        e = 1.1
        zr0, zr1 = z0 + hw, z0 + hw + hr
        roof = (0.30, 0.21, 0.12)
        for sx_ in (-1, 1):                                                                                         # the two steep thatch slopes
            a0, a1 = C(sx_, -1, e), C(sx_, 1, e)
            r0, r1 = C(0, -1, e), C(0, 1, e)
            SURF.face([(a0[0], a0[1], zr0), (a1[0], a1[1], zr0), (r1[0], r1[1], zr1), (r0[0], r0[1], zr1)], roof, None)
        for sy_ in (-1, 1):                                                                                         # the gable ends, lit
            a0, a1, r = C(-1, sy_, e), C(1, sy_, e), C(0, sy_, e)
            NEON.face([(a0[0], a0[1], zr0), (a1[0], a1[1], zr0), (r[0], r[1], zr1)], sc(DIVE, 0.5 * ridge_glow), None)
        r0, r1 = C(0, -1, e), C(0, 1, e)
        ns["bar"](NEON, (r0[0], r0[1], zr1 + 0.05), (r1[0], r1[1], zr1 + 0.05), 0.22, sc(DIVE, 1.3 * ridge_glow))      # the ridge line
        return zr1
    zt2 = base + th * 3
    # crown hale on the top tier, four small hale on the middle tier, a row of small hale on the lowest tier
    hale(0, 0, 4.2, 6.2, 3.6, 8.0, zt2, glow=0.9, ridge_glow=1.5)
    zt1 = base + th * 2
    for (x, y) in ((-3.0, 4.2), (3.0, 4.2), (-3.0, -4.2), (3.0, -4.2)):
        hale(x, y, 2.4, 3.4, 1.6, 3.4, zt1, glow=0.55)
    zt0 = base + th
    for (x, y) in ((-4.2, 7.4), (4.2, 7.4), (-4.2, -7.4), (4.2, -7.4)):
        hale(x, y, 2.2, 3.0, 1.4, 2.8, zt0, glow=0.5)
    for sx_ in (-1, 1):                                          # lauhala / kapa screens: pattern panels on the terrace edges
        for k in range(3):
            p = L(sx_ * 5.8, -4.0 + 4.0 * k)
            for q in range(5):
                ns["bar"](NEON, (p[0] + math.cos(yaw) * (q - 2) * 0.5 - math.sin(yaw) * sx_ * 0.0, p[1] + math.sin(yaw) * (q - 2) * 0.5, base + th + 0.3),
                          (p[0] + math.cos(yaw) * (q - 1) * 0.5, p[1] + math.sin(yaw) * (q - 1) * 0.5, base + th + 1.5), 0.08, sc(DIVE, 0.9))
    pcrown = L(0, 0)
    ns["bar"](NEON, (pcrown[0], pcrown[1], zt2 + 12.5), (pcrown[0], pcrown[1], zt2 + 15.0), 0.14, sc(PHOTO, 1.4))
    # ---- thrusters on the trailing edge, angled out, teal glow kept moderate so it does not wash out
    thr = []
    for sx_ in (-1, 1):
        for xx in (12.0, 28.0):
            x = sx_ * xx
            y = y_te(xx)
            dirx, diry = sx_ * 0.35, -1.0
            dl = math.hypot(dirx, diry)
            dirx, diry = dirx / dl, diry / dl
            p0 = L(x - dirx * 3.0, y - diry * 3.0)
            p1 = L(x + dirx * 7.0, y + diry * 7.0)
            zp = zf(x) - 0.2
            tube(SURF, (p0[0], p0[1], zp + 0.2), (p1[0], p1[1], zp), 2.2, 10, (0.50, 0.62, 0.70))
            p2 = L(x + dirx * 8.4, y + diry * 8.4)
            tube(NEON, (p1[0], p1[1], zp), (p2[0], p2[1], zp - 0.1), 1.9, 10, sc(PHOTO, 1.6))
            ns["ring_line"](NEON, p2[0], p2[1], zp - 0.1, 2.6, 0.16, sc(PHOTO, 1.3), n=14)
            frustum(NEON, p2[0], p2[1], ZW + 0.4, zp - 0.4, 1.7, 0.9, 12, sc(PHOTO, 0.22))
            ns["spot_at"]((p2[0], p2[1], ZW + 0.5), (p2[0], p2[1], zp), PHOTO, 8.0e4, 70.0)
            thr.append((p2[0], p2[1]))
    # ---- bioluminescent algae: patchy teal-cyan glow in the water under and around the body and along the wake, with sparkle
    ar = random.Random(91)
    centres = [(mx, my, 24.0, 160)]
    for (tx, ty) in thr:
        centres.append((tx, ty, 8.0, 50))
    for k in range(0, 40, 3):
        f = phi - math.radians(1.6) * k
        wx, wy = loop_pt(f)
        centres.append((wx + sh[0], wy + sh[1], 5.0 + 0.1 * k, 34))
    for (cx_, cy_, sg, cnt) in centres:
        for _ in range(cnt):
            px_, py_ = ar.gauss(cx_, sg), ar.gauss(cy_, sg)
            rr = ar.uniform(0.35, 1.3)
            nv = ar.randint(6, 9)
            ph = ar.uniform(0, 6.28)
            deep = ar.random() < 0.55
            z = ZW - ar.uniform(0.6, 2.5) if deep else ZW + 0.1
            strength = (0.16 if deep else 0.07) * ar.uniform(0.4, 1.5)
            pts = []
            for q in range(nv):
                th_ = 2 * math.pi * q / nv
                rad = rr * (0.6 + 0.4 * ar.random())
                pts.append((px_ + rad * math.cos(th_ + ph), py_ + rad * 0.8 * math.sin(th_ + ph), z))
            NEON.face(pts, sc((0.35, 0.95, 0.95), strength * 3.0), None, wet=1 if deep else 0)
            if not deep and ar.random() < 0.22:
                ns["box"](NEON, px_ - 0.12, py_ - 0.12, ZW + 0.12, px_ + 0.12, py_ + 0.12, ZW + 0.3, sc((0.7, 1.0, 1.0), 1.6))
    # the faint dashed loop line on the water (parallel to the dam walls)
    for k in range(90):
        if k % 2:
            continue
        a0, a1 = loop_pt(2 * math.pi * k / 90), loop_pt(2 * math.pi * (k + 1) / 90)
        ns["bar"](NEON, (a0[0] + sh[0], a0[1] + sh[1], ZW + 0.12), (a1[0] + sh[0], a1[1] + sh[1], ZW + 0.12), 0.30, sc(PHOTO, 0.40))
    import json
    sj = os.environ.get("SHADOW_JSON")
    if sj:
        json.dump(dict(outline=[list(p) for p in P2], zd=zd, ZW=ZW, centre=[mx, my], tail=[list(prev)], fwd=list(Fw)), open(sj, "w"))
    ns["spot_at"]((mx, my, ZW - 6.0), (mx, my, zd - 1.2), (0.30, 0.95, 1.0), 3.0e5, 60.0)
    landing(ns, hx, hy, ang0, 38.0, (hx + 10 * math.cos(ang0), hy + 10 * math.sin(ang0)))
    drifters(ns, hx, hy, rng, ang0, 8, 48.0, 74.0, 6.0, 10.0)
    c = (pcrown[0], pcrown[1], zt2 + 6.0)
    lights(ns, hx, hy, zd + 4.0, c, 4.5e5)
    return zt2 + 15.0, c


def idea_P(ns, hx, hy, rng, ang0):
    """MANTA v4: the same ray (flat broad wings, 10 degree bank, neon outline, straight-C tail) with rounded wing tips, head lobes that flow out of the
    head outline, two integrated tail-root thrusters, bold white kakau fields across the whole back, a COMPOUND of nine hale-biodomes (steep hale roof
    profiles as glass gridshells with bronze kapa-lattice frames, warm lit interiors with tropical planting, lava-stone heiau plinths, walkways and lanai
    decks) and a soft emissive algae haze in the water surface layer with a few swirls in the wake."""
    ZW = ns["ZW"]
    SURF, NEON, GLASS, SM = ns["SURF"], ns["NEON"], ns["GLASS"], ns["SMOOTH"]
    from tkit import obox, frustum
    flap = float(os.environ.get("FLAP", "0.0"))
    bank = float(os.environ.get("BANK", "0.1736"))
    phi = math.radians(float(os.environ.get("LOOP_PHI", "-90.0")))
    zd = ZW + 10.0
    SC = 1.0
    rx, ry = 66.0, 34.0
    cx_l, cy_l = loc(hx, hy, 0.0, 26.0)

    def loop_pt(f):
        return cx_l + U[0] * rx * math.cos(f) + V[0] * ry * math.sin(f), cy_l + U[1] * rx * math.cos(f) + V[1] * ry * math.sin(f)
    sx0, sy0 = loop_pt(math.radians(-90.0))
    sh = (hx - sx0 + V[0] * 4.0, hy - sy0 + V[1] * 4.0)
    mx, my = loop_pt(phi)
    mx, my = mx + sh[0], my + sh[1]
    tvx, tvy = -rx * math.sin(phi), ry * math.cos(phi)
    tl = math.hypot(tvx, tvy)
    Fw = ((U[0] * tvx + V[0] * tvy) / tl, (U[1] * tvx + V[1] * tvy) / tl)
    Rw = (Fw[1], -Fw[0])
    yaw = math.atan2(Fw[1], Fw[0])

    def L(x, y):
        return mx + (Rw[0] * x + Fw[0] * y) * SC, my + (Rw[1] * x + Fw[1] * y) * SC

    def zf(x):
        return zd + flap * abs(x) * 0.30 + bank * x

    HS = 52.0

    def y_te(x):
        s = max(0.0, min(1.0, (HS - 1.0 - abs(x)) / 39.0))
        return -12.0 - 1.5 * s + 3.5 * math.sin(math.pi * s) ** 1.2

    BODY = (0.40, 0.56, 0.64)
    tones = [(0.40, 0.56, 0.64), (0.37, 0.53, 0.62), (0.43, 0.59, 0.66)]
    WHITE = (0.92, 0.95, 0.98)
    GLOWW = sc((0.85, 0.95, 1.0), 0.75)
    EDGE = sc(PHOTO, 1.9)
    # ---- planform: the head lobes are part of the outline (they flow out of the head), rounded wing tips
    right = [(0, 22.0), (1.6, 22.5), (2.5, 24.8), (3.4, 26.8), (4.6, 28.2), (5.8, 27.2), (6.5, 25.2), (7.2, 23.2)]
    le = []
    for k in range(0, 15):
        t = k / 14.0
        le.append((9 + (HS - 1.0 - 9) * t, 21 - 28 * t ** 1.5))
    right += le
    for a_ in (60, 30, 0, -30, -60):                                    # the rounded tip
        right.append((HS - 1.0 + 2.2 * math.cos(math.radians(a_)), -9.5 + 2.5 * math.sin(math.radians(a_)) * (1 if a_ >= 0 else 1)))
    for k in range(1, 15):
        s = k / 14.0
        right.append((HS - 1.0 - 39 * s, y_te(HS - 1.0 - 39 * s)))
    right += [(9, -17), (6, -21), (0, -23)]
    left = [(-x, y) for (x, y) in reversed(right[1:-1])]
    outline = right + left
    n = len(outline)
    P2 = [L(x, y) for (x, y) in outline]
    ZZ = [zf(x) for (x, y) in outline]
    IN = [L(0.5 * x, 0.5 * y) for (x, y) in outline]
    IZ = [zf(0.5 * x) for (x, y) in outline]
    for i in range(n):
        j = (i + 1) % n
        a, b, a2, b2 = P2[i], P2[j], IN[i], IN[j]
        col = tones[(i // 2) % 3]
        SURF.face([(mx, my, zd + 1.0), (a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0)], tones[0], None)
        SURF.face([(a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0), (b[0], b[1], ZZ[j] + 1.0), (a[0], a[1], ZZ[i] + 1.0)], col, None)
        SURF.face([(a[0], a[1], ZZ[i] + 1.0), (a[0], a[1], ZZ[i] - 1.0), (b[0], b[1], ZZ[j] - 1.0), (b[0], b[1], ZZ[j] + 1.0)], (0.50, 0.64, 0.70), None)
        SURF.face([(a[0], a[1], ZZ[i] - 1.0), (b[0], b[1], ZZ[j] - 1.0), (b2[0], b2[1], IZ[j] - 1.0), (a2[0], a2[1], IZ[i] - 1.0)], (0.55, 0.68, 0.74), None)
        SURF.face([(mx, my, zd - 1.0), (b2[0], b2[1], IZ[j] - 1.0), (a2[0], a2[1], IZ[i] - 1.0)], (0.55, 0.68, 0.74), None)
        ns["bar"](NEON, (a[0], a[1], ZZ[i] + 1.04), (b[0], b[1], ZZ[j] + 1.04), 0.38, EDGE)
    # ---- white kakau fields across the whole back (bold: edge teeth, three wing bands with zig-zag and lozenge fields, a dorsal chain, rear chevrons)
    zt = 1.045

    def PZ(x, y):
        p = L(x, y)
        return (p[0], p[1], zf(x) + zt)

    def strip(a, b, w):
        pa, pb = PZ(*a), PZ(*b)
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        dl = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / dl * w / 2, dx / dl * w / 2
        NEON.face([(pa[0] - nx, pa[1] - ny, pa[2]), (pa[0] + nx, pa[1] + ny, pa[2]), (pb[0] + nx, pb[1] + ny, pb[2]), (pb[0] - nx, pb[1] - ny, pb[2])], GLOWW, None)

    def poly(pts):
        NEON.face([PZ(*p) for p in pts], GLOWW, None)

    def inw(p, k):
        v = (0.0 - p[0], 3.0 - p[1])
        d = math.hypot(*v) or 1.0
        return (v[0] / d * k, v[1] / d * k)

    def band(sx, k, w):
        pts = []
        for (x, y) in le:
            iv = inw((x, y), k)
            pts.append((sx * (x + iv[0]), y + iv[1]))
        for q in range(len(pts) - 1):
            strip(pts[q], pts[q + 1], w)
        return pts
    for sx in (-1, 1):
        b1 = band(sx, 1.8, 0.8)
        for q in range(len(le) - 1):                      # niho mano along the leading edge
            a, b = b1[q], b1[q + 1]
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            iv = inw((abs(mid[0]), mid[1]), 3.4 * (1 - 0.45 * q / 14.0))
            poly([a, b, (mid[0] + sx * iv[0], mid[1] + iv[1])])
        b2 = band(sx, 9.0, 1.1)
        b3 = band(sx, 16.0, 1.1)
        b4 = band(sx, 23.0, 1.1)
        for q in range(0, len(le) - 1):                   # zig-zag teeth between the second and third bands
            a, b = b2[q], b2[q + 1]
            c = b3[q]
            d_ = b3[q + 1]
            if q % 2 == 0:
                poly([a, b, ((c[0] + d_[0]) / 2, (c[1] + d_[1]) / 2)])
            else:
                poly([c, d_, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)])
        for q in range(0, len(le) - 2, 2):                # lozenges between the third and fourth bands
            a, c = b3[q + 1], b4[q + 1]
            mid = ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2)
            poly([(mid[0] - sx * 2.4, mid[1]), (mid[0], mid[1] + 3.0), (mid[0] + sx * 2.4, mid[1]), (mid[0], mid[1] - 3.0)])
        for j in range(3):                                # big chevrons along the trailing zone, pointing forward
            strip((sx * (24.0 + 6.0 * j), -2.0 - 2.0 * j), (sx * (14.0 + 3.0 * j), -9.0 - 1.2 * j), 1.0)
        poly([(sx * (HS - 3.0), -9.5), (sx * le[11][0], le[11][1] - 2.0), (sx * (HS - 10.0), y_te(HS - 10.0) + 1.5)])
    for k in range(6):                                    # dorsal chain of lozenges down the midline
        cyl = 17.0 - 6.0 * k
        poly([(-2.2, cyl), (0, cyl + 3.0), (2.2, cyl), (0, cyl - 3.0)])
    # ---- the tail: segmented mechanical root, slim whip, long and mostly straight with one gentle C, neon centre line
    prev = L(0, -23)
    pz = zd - 0.6
    for k in range(1, 31):
        u = k / 30.0
        x, y = 5.0 * math.sin(math.pi * u), -23.0 - 2.1 * k
        q = L(x, y)
        z = zd - 0.6 - 0.10 * k
        if k <= 6:
            r = 1.6 - 0.1 * k
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 8, (0.46, 0.60, 0.68) if k % 2 else (0.40, 0.54, 0.62))
            ns["box"](NEON, q[0] - r * 0.9, q[1] - r * 0.9, z - r * 0.3, q[0] + r * 0.9, q[1] + r * 0.9, z + r * 0.3, sc(PHOTO, 1.1))
        else:
            r = 0.42 * (1 - (k - 6) / 26.0) + 0.1
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 6, (0.44, 0.58, 0.66))
        ns["bar"](NEON, (prev[0], prev[1], pz + 0.25), (q[0], q[1], z + 0.25), 0.10, EDGE)
        prev, pz = q, z
    ns["dome"](NEON, prev[0], prev[1], pz, 0.45, sc(PHOTO, 1.8), n=8, rings=3, hemi=False)
    # ---- the compound: nine hale-biodomes on lava-stone heiau plinths, with walkways and lanai decks
    stone = (0.09, 0.08, 0.08)
    bronze = (0.58, 0.46, 0.27)
    plr = random.Random(5)

    def hale(x, y, w, d, hw, hr, yaw_off, kind, glow, tiers=1, base_dz=0.0):
        """a futuristic hale: stone plinth, lit interior with planting, a steep glass gridshell roof on a bronze kapa-lattice frame."""
        p = L(x, y)
        yw = yaw + yaw_off
        ax, ay = math.cos(yw), math.sin(yw)
        bx, by = -ay, ax
        zb0 = zf(x) + 1.0 - 0.6 + base_dz
        z0 = zb0
        for t in range(tiers):
            ex_ = 2.2 + 2.2 * (tiers - 1 - t)
            obox(SURF, p[0], p[1], z0, (d + ex_) * SC, (w + ex_) * SC, 1.3, yw, stone)
            obox(NEON, p[0], p[1], z0 + 1.15, (d + ex_) * SC * 1.01, (w + ex_) * SC * 1.01, 0.18, yw, sc(DIVE, 0.9), top=False)       # lit terrace lip
            z0 += 1.3

        def C(sx, sy, e=0.0):
            return (p[0] + bx * sx * (w / 2 + e) + ax * sy * (d / 2 + e), p[1] + by * sx * (w / 2 + e) + ay * sy * (d / 2 + e))
        # warm interior: a floor glow and an inner roof-shaped glow volume
        obox(NEON, p[0], p[1], z0, d * 0.94, w * 0.94, 0.18, yw, sc(DIVE, 0.6 * glow))
        zr0, zr1 = z0 + hw, z0 + hw + hr
        k_in = 0.86
        if kind == "gable":
            for sx_ in (-1, 1):
                a0, a1, r0, r1 = C(sx_ * k_in, -k_in), C(sx_ * k_in, k_in), C(0, k_in), C(0, -k_in)
                NEON.face([(a0[0], a0[1], z0), (a1[0], a1[1], z0), (a1[0], a1[1], zr0), (a0[0], a0[1], zr0)], sc(DIVE, 0.42 * glow), None)
                NEON.face([(a0[0], a0[1], zr0), (a1[0], a1[1], zr0), (r1[0], r1[1], zr1 - 0.4), (r0[0], r0[1], zr1 - 0.4)], sc(DIVE, 0.30 * glow), None)
            for sy_ in (-1, 1):
                g0, g1, rr = C(-k_in, sy_ * k_in), C(k_in, sy_ * k_in), C(0, sy_ * k_in)
                NEON.face([(g0[0], g0[1], z0), (g1[0], g1[1], z0), (g1[0], g1[1], zr0), (g0[0], g0[1], zr0)], sc(DIVE, 0.42 * glow), None)
                NEON.face([(g0[0], g0[1], zr0), (g1[0], g1[1], zr0), (rr[0], rr[1], zr1 - 0.4)], sc(DIVE, 0.36 * glow), None)
        else:                                                                                                     # hip: a short ridge
            ridge = 0.3
            for (sx_, sy_) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                pass
            q0, q1 = C(0, -ridge * k_in), C(0, ridge * k_in)
            for sx_ in (-1, 1):
                a0, a1 = C(sx_ * k_in, -k_in), C(sx_ * k_in, k_in)
                NEON.face([(a0[0], a0[1], zr0), (a1[0], a1[1], zr0), (q1[0], q1[1], zr1 - 0.4), (q0[0], q0[1], zr1 - 0.4)], sc(DIVE, 0.30 * glow), None)
            for sy_ in (-1, 1):
                g0, g1 = C(-k_in, sy_ * k_in), C(k_in, sy_ * k_in)
                qq = q1 if sy_ > 0 else q0
                NEON.face([(g0[0], g0[1], zr0), (g1[0], g1[1], zr0), (qq[0], qq[1], zr1 - 0.4)], sc(DIVE, 0.36 * glow), None)
            for sx_ in (-1, 1):
                for sy_ in (-1, 1):
                    c = C(sx_ * k_in, sy_ * k_in)
                    NEON.face([(c[0], c[1], z0), (C(sx_ * k_in, 0)[0], C(sx_ * k_in, 0)[1], z0), (C(sx_ * k_in, 0)[0], C(sx_ * k_in, 0)[1], zr0), (c[0], c[1], zr0)], sc(DIVE, 0.4 * glow), None)
        # tropical planting seen through the glass
        for _ in range(max(4, int(w * d / 5.0))):
            sx_, sy_ = plr.uniform(-0.7, 0.7), plr.uniform(-0.7, 0.7)
            c = C(sx_, sy_)
            ph = plr.uniform(0.9, min(2.6, hw + hr * 0.35))
            ns["bar"](SM, (c[0], c[1], z0 + 0.1), (c[0], c[1], z0 + ph), 0.16, (0.20, 0.14, 0.08))
            for q in range(5):
                a_ = 2 * math.pi * q / 5 + plr.uniform(0, 1)
                ns["bar"](SM, (c[0], c[1], z0 + ph), (c[0] + 0.9 * math.cos(a_), c[1] + 0.9 * math.sin(a_), z0 + ph - 0.35), 0.28, (0.10, 0.40, 0.16))
        # the glass gridshell: A-frame slopes (gable) or four hip slopes, a bronze kapa-style diagonal lattice, a lit ridge
        e = 0.8
        glass = (0.8, 0.92, 1.0)
        if kind == "gable":
            for sx_ in (-1, 1):
                a0, a1, r0, r1 = C(sx_, -1, e), C(sx_, 1, e), C(0, 1, e), C(0, -1, e)
                GLASS.face([(a0[0], a0[1], zr0), (a1[0], a1[1], zr0), (r0[0], r0[1], zr1), (r1[0], r1[1], zr1)], glass, None)
                nst = max(4, int(d * 0.9))
                for i in range(nst):
                    f0, f1 = -1 + 2 * i / nst, -1 + 2 * (i + 1) / nst
                    pa, pb = C(sx_, f0, e), C(sx_, f1, e)
                    ra, rb = C(0, f0, e), C(0, f1, e)
                    ns["bar"](SM, (pa[0], pa[1], zr0), (ra[0], ra[1], zr1), 0.16, bronze)                                  # rafters
                    ns["bar"](SM, (pa[0], pa[1], zr0), (rb[0], rb[1], zr1), 0.10, bronze)                                  # lattice diagonals
                    ns["bar"](SM, (pb[0], pb[1], zr0), (ra[0], ra[1], zr1), 0.10, bronze)
                for lv in (0.33, 0.66):                                                                                     # purlins
                    pa, pb = C(sx_ * (1 - lv), -1, e * (1 - lv)), C(sx_ * (1 - lv), 1, e * (1 - lv))
                    ns["bar"](SM, (pa[0], pa[1], zr0 + hr * lv), (pb[0], pb[1], zr0 + hr * lv), 0.10, bronze)
            for sy_ in (-1, 1):
                g0, g1, rr = C(-1, sy_, e), C(1, sy_, e), C(0, sy_, e)
                GLASS.face([(g0[0], g0[1], zr0), (g1[0], g1[1], zr0), (rr[0], rr[1], zr1)], glass, None)
                ns["bar"](SM, (g0[0], g0[1], zr0), (rr[0], rr[1], zr1), 0.18, bronze)
                ns["bar"](SM, (g1[0], g1[1], zr0), (rr[0], rr[1], zr1), 0.18, bronze)
                ns["bar"](SM, (g0[0], g0[1], zr0), (g1[0], g1[1], zr0), 0.16, bronze)
            r0, r1 = C(0, -1, e), C(0, 1, e)
            ns["bar"](NEON, (r0[0], r0[1], zr1 + 0.05), (r1[0], r1[1], zr1 + 0.05), 0.24, sc(DIVE, 1.5 * glow))
            for sx_ in (-1, 1):
                a0, a1 = C(sx_, -1, e), C(sx_, 1, e)
                ns["bar"](NEON, (a0[0], a0[1], zr0), (a1[0], a1[1], zr0), 0.14, sc(DIVE, 0.9))
        else:
            ridge = 0.3
            q0, q1 = C(0, -ridge, e * 0.5), C(0, ridge, e * 0.5)
            corners = [C(-1, -1, e), C(1, -1, e), C(1, 1, e), C(-1, 1, e)]
            for i in range(4):
                a, b = corners[i], corners[(i + 1) % 4]
                top_a = q0 if i in (0, 1) else q1
                top_b = q0 if (i + 1) % 4 in (0, 1) else q1
                if i in (0, 2):
                    GLASS.face([(a[0], a[1], zr0), (b[0], b[1], zr0), (top_b[0], top_b[1], zr1)], glass, None)
                else:
                    GLASS.face([(a[0], a[1], zr0), (b[0], b[1], zr0), (top_b[0], top_b[1], zr1), (top_a[0], top_a[1], zr1)], glass, None)
                ns["bar"](SM, (a[0], a[1], zr0), (b[0], b[1], zr0), 0.16, bronze)
                ns["bar"](SM, (a[0], a[1], zr0), (top_a[0], top_a[1], zr1), 0.18, bronze)
                m_ = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                ns["bar"](SM, (m_[0], m_[1], zr0), (top_a[0] * 0.5 + top_b[0] * 0.5, top_a[1] * 0.5 + top_b[1] * 0.5, zr1), 0.10, bronze)
            ns["bar"](NEON, (q0[0], q0[1], zr1 + 0.05), (q1[0], q1[1], zr1 + 0.05), 0.24, sc(DIVE, 1.5 * glow))
        return p, zr1
    layout = [
        # (x, y, w, d, wall, ridge, yaw offset, kind, glow, tiers)
        (0.0, 3.0, 7.0, 12.0, 3.0, 12.5, 0.0, "gable", 1.4, 2),       # the hero: a tall hale-biodome
        (0.0, -11.5, 4.4, 7.0, 1.8, 6.0, 0.0, "gable", 0.9, 1),
        (-9.0, 11.0, 5.0, 5.0, 1.8, 6.5, 0.0, "hip", 0.9, 1),
        (9.0, 11.0, 5.0, 5.0, 1.8, 6.5, 0.0, "hip", 0.9, 1),
        (-10.0, -3.0, 3.6, 6.2, 1.6, 5.2, 0.0, "gable", 0.8, 1),
        (10.0, -3.0, 3.6, 6.2, 1.6, 5.2, 0.0, "gable", 0.8, 1),
        (-23.0, 3.0, 4.0, 7.0, 1.6, 5.6, math.pi / 2, "gable", 0.8, 1),
        (23.0, 3.0, 4.0, 7.0, 1.6, 5.6, math.pi / 2, "gable", 0.8, 1),
        (36.0, -2.5, 3.6, 3.6, 1.4, 4.6, 0.0, "hip", 0.8, 1),
    ]
    centres = []
    for (x, y, w, d, hw, hr, yo, kind, gl, tiers) in layout:
        pc_, ztop = hale(x, y, w, d, hw, hr, yo, kind, gl, tiers)
        centres.append((x, y, ztop))
    hero_top = centres[0][2]
    # walkways and lanai decks between the buildings
    def walk(a, b, w=1.3):
        pa, pb = L(a[0], a[1]), L(b[0], b[1])
        za, zb_ = zf(a[0]) + 1.1, zf(b[0]) + 1.1
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        dl = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / dl * w / 2, dx / dl * w / 2
        SURF.face([(pa[0] - nx, pa[1] - ny, za), (pa[0] + nx, pa[1] + ny, za), (pb[0] + nx, pb[1] + ny, zb_), (pb[0] - nx, pb[1] - ny, zb_)], (0.12, 0.11, 0.11), None)
        for sg in (-1, 1):
            ns["bar"](NEON, (pa[0] + sg * nx, pa[1] + sg * ny, za + 0.04), (pb[0] + sg * nx, pb[1] + sg * ny, zb_ + 0.04), 0.09, sc(DIVE, 0.8))
    for (i, j) in ((0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (2, 6), (3, 7), (7, 8)):
        walk(layout[i][:2], layout[j][:2])
    for (x, y) in ((4.5, 12.0), (-4.5, -6.0), (-16.0, 6.0), (16.0, 6.0), (30.0, 0.0)):             # lanai decks
        p = L(x, y)
        obox(NEON, p[0], p[1], zf(x) + 1.05, 3.0, 3.0, 0.15, yaw, sc(DIVE, 0.35))
        obox(SURF, p[0], p[1], zf(x) + 1.0, 3.2, 3.2, 0.1, yaw, stone)
    pcrown = L(0, 3.0)
    ns["bar"](NEON, (pcrown[0], pcrown[1], hero_top), (pcrown[0], pcrown[1], hero_top + 2.6), 0.14, sc(PHOTO, 1.4))
    # ---- two integrated thrusters at the tail root: cowls on the back, glowing slots on the trailing edge, jet columns to the water
    thr = []
    for sx_ in (-1, 1):
        cx_, cy_ = sx_ * 5.8, -15.5
        cp = L(cx_, cy_)
        ns["dome"](SURF, cp[0], cp[1], zf(cx_) + 1.0, 3.0, (0.47, 0.62, 0.70), n=14, rings=4, zscale=0.35)
        sp = L(sx_ * 5.4, -20.2)
        obox(NEON, sp[0], sp[1], zf(sx_ * 5.4) - 0.3, 3.4, 3.8, 0.5, yaw, sc(PHOTO, 1.6))
        ns["ring_line"](NEON, sp[0], sp[1], zf(sx_ * 5.4) + 0.28, 2.3, 0.14, sc(PHOTO, 1.0), n=14)
        frustum(NEON, sp[0], sp[1], ZW + 0.4, zf(sx_ * 5.4) - 0.5, 1.8, 1.0, 12, sc(PHOTO, 0.2))
        ns["spot_at"]((sp[0], sp[1], ZW + 0.5), (sp[0], sp[1], zd), PHOTO, 8.0e4, 70.0)
        thr.append((sp[0], sp[1]))
    # ---- living glow: a soft emissive teal haze in the water surface layer (one coloured grid, no discs), brighter swirls in the wake
    ar = random.Random(91)
    wake = []
    for k in range(0, 40, 2):
        f = phi - math.radians(1.6) * k
        wx, wy = loop_pt(f)
        wake.append((wx + sh[0], wy + sh[1], 5.0 + 0.12 * k))
    srcs = [(mx, my, 24.0, 1.0)] + [(tx, ty, 9.0, 0.9) for (tx, ty) in thr] + [(wx, wy, sg, 0.55) for (wx, wy, sg) in wake]
    ph1, ph2, ph3 = ar.uniform(0, 6.28), ar.uniform(0, 6.28), ar.uniform(0, 6.28)
    import numpy as np
    WP, HP = 224, 140
    x0, y0, wbu, hbu = mx - 68.0, my - 46.0, 136.0, 92.0
    xs_ = x0 + (np.arange(WP) + 0.5) * wbu / WP
    ys_ = y0 + (np.arange(HP) + 0.5) * hbu / HP
    GX, GY = np.meshgrid(xs_, ys_)
    g = np.zeros_like(GX)
    for (sx_, sy_, sg, wgt) in srcs:
        g += wgt * np.exp(-((GX - sx_) ** 2 + (GY - sy_) ** 2) / (2 * sg * sg))
    nz = 0.5 + 0.5 * np.sin(GX * 0.21 + ph1) * np.sin(GY * 0.17 + ph2) + 0.25 * np.sin((GX + GY) * 0.43 + ph3)
    v = g * np.clip(nz - 0.2, 0.0, None)
    t_ = np.clip((v - 0.03) / 0.55, 0.0, 1.0)
    ns["HAZE"] = dict(arr=(0.75 * t_ * t_ * (3 - 2 * t_)).astype(np.float32), x0=x0, y0=y0, wbu=wbu, hbu=hbu)
    for sw in range(6):                                    # a few brighter swirls in the wake
        wx, wy, sg = wake[min(len(wake) - 1, 2 + sw * 3)]
        r0 = ar.uniform(2.0, 3.5)
        ph = ar.uniform(0, 6.28)
        prevq = None
        for q in range(0, 20):
            th_ = ph + q * 0.45
            rad = r0 * (0.35 + 0.045 * q)
            pt = (wx + rad * math.cos(th_), wy + rad * math.sin(th_), ZW + 0.12)
            if prevq:
                ns["bar"](NEON, prevq, pt, 0.18, sc((0.45, 1.0, 1.0), 0.5 * (1 - q / 24.0)))
            prevq = pt
    for _ in range(22):                                    # a few sparkles
        wx, wy, sg = wake[ar.randrange(len(wake))]
        px_, py_ = ar.gauss(wx, sg), ar.gauss(wy, sg)
        ns["box"](NEON, px_ - 0.1, py_ - 0.1, ZW + 0.1, px_ + 0.1, py_ + 0.1, ZW + 0.25, sc((0.75, 1.0, 1.0), 1.4))
    for k in range(90):
        if k % 2:
            continue
        a0, a1 = loop_pt(2 * math.pi * k / 90), loop_pt(2 * math.pi * (k + 1) / 90)
        ns["bar"](NEON, (a0[0] + sh[0], a0[1] + sh[1], ZW + 0.12), (a1[0] + sh[0], a1[1] + sh[1], ZW + 0.12), 0.30, sc(PHOTO, 0.40))
    import json
    sj = os.environ.get("SHADOW_JSON")
    if sj:
        json.dump(dict(outline=[list(p) for p in P2], zd=zd, ZW=ZW, centre=[mx, my], tail=[list(prev)], fwd=list(Fw)), open(sj, "w"))
    ns["spot_at"]((mx, my, ZW - 6.0), (mx, my, zd - 1.2), (0.30, 0.95, 1.0), 3.0e5, 60.0)
    landing(ns, hx, hy, ang0, 38.0, (hx + 10 * math.cos(ang0), hy + 10 * math.sin(ang0)))
    drifters(ns, hx, hy, rng, ang0, 8, 48.0, 74.0, 6.0, 10.0)
    c = (pcrown[0], pcrown[1], hero_top - 6.0)
    lights(ns, hx, hy, zd + 4.0, c, 5.5e5)
    return hero_top + 3.0, c




def idea_Q(ns, hx, hy, rng, ang0):
    """MANTA v5 (v4 plus pili-grass thatch roofs, brown timber walls, warm 2700 K light spill, wider lit walkways, stronger algae): the same ray (flat broad wings, 10 degree bank, neon outline, straight-C tail) with rounded wing tips, head lobes that flow out of the
    head outline, two integrated tail-root thrusters, bold white kakau fields across the whole back, a COMPOUND of nine hale-biodomes (steep hale roof
    profiles as glass gridshells with bronze kapa-lattice frames, warm lit interiors with tropical planting, lava-stone heiau plinths, walkways and lanai
    decks) and a soft emissive algae haze in the water surface layer with a few swirls in the wake."""
    DIVE = (1.0, 0.64, 0.30)
    ZW = ns["ZW"]
    SURF, NEON, GLASS, SM = ns["SURF"], ns["NEON"], ns["GLASS"], ns["SMOOTH"]
    from tkit import obox, frustum
    flap = float(os.environ.get("FLAP", "0.0"))
    bank = float(os.environ.get("BANK", "0.1736"))
    phi = math.radians(float(os.environ.get("LOOP_PHI", "-90.0")))
    zd = ZW + 10.0
    SC = 1.0
    rx, ry = 66.0, 34.0
    cx_l, cy_l = loc(hx, hy, 0.0, 26.0)

    def loop_pt(f):
        return cx_l + U[0] * rx * math.cos(f) + V[0] * ry * math.sin(f), cy_l + U[1] * rx * math.cos(f) + V[1] * ry * math.sin(f)
    sx0, sy0 = loop_pt(math.radians(-90.0))
    sh = (hx - sx0 + V[0] * 4.0, hy - sy0 + V[1] * 4.0)
    mx, my = loop_pt(phi)
    mx, my = mx + sh[0], my + sh[1]
    tvx, tvy = -rx * math.sin(phi), ry * math.cos(phi)
    tl = math.hypot(tvx, tvy)
    Fw = ((U[0] * tvx + V[0] * tvy) / tl, (U[1] * tvx + V[1] * tvy) / tl)
    Rw = (Fw[1], -Fw[0])
    yaw = math.atan2(Fw[1], Fw[0])

    def L(x, y):
        return mx + (Rw[0] * x + Fw[0] * y) * SC, my + (Rw[1] * x + Fw[1] * y) * SC

    def zf(x):
        return zd + flap * abs(x) * 0.30 + bank * x

    HS = 52.0

    def y_te(x):
        s = max(0.0, min(1.0, (HS - 1.0 - abs(x)) / 39.0))
        return -12.0 - 1.5 * s + 3.5 * math.sin(math.pi * s) ** 1.2

    BODY = (0.40, 0.56, 0.64)
    tones = [(0.40, 0.56, 0.64), (0.37, 0.53, 0.62), (0.43, 0.59, 0.66)]
    WHITE = (0.92, 0.95, 0.98)
    GLOWW = sc((0.85, 0.95, 1.0), 0.75)
    EDGE = sc(PHOTO, 1.9)
    # ---- planform: the head lobes are part of the outline (they flow out of the head), rounded wing tips
    right = [(0, 22.0), (1.6, 22.5), (2.5, 24.8), (3.4, 26.8), (4.6, 28.2), (5.8, 27.2), (6.5, 25.2), (7.2, 23.2)]
    le = []
    for k in range(0, 15):
        t = k / 14.0
        le.append((9 + (HS - 1.0 - 9) * t, 21 - 28 * t ** 1.5))
    right += le
    for a_ in (60, 30, 0, -30, -60):                                    # the rounded tip
        right.append((HS - 1.0 + 2.2 * math.cos(math.radians(a_)), -9.5 + 2.5 * math.sin(math.radians(a_)) * (1 if a_ >= 0 else 1)))
    for k in range(1, 15):
        s = k / 14.0
        right.append((HS - 1.0 - 39 * s, y_te(HS - 1.0 - 39 * s)))
    right += [(9, -17), (6, -21), (0, -23)]
    left = [(-x, y) for (x, y) in reversed(right[1:-1])]
    outline = right + left
    n = len(outline)
    P2 = [L(x, y) for (x, y) in outline]
    ZZ = [zf(x) for (x, y) in outline]
    IN = [L(0.5 * x, 0.5 * y) for (x, y) in outline]
    IZ = [zf(0.5 * x) for (x, y) in outline]
    for i in range(n):
        j = (i + 1) % n
        a, b, a2, b2 = P2[i], P2[j], IN[i], IN[j]
        col = tones[(i // 2) % 3]
        SURF.face([(mx, my, zd + 1.0), (a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0)], tones[0], None)
        SURF.face([(a2[0], a2[1], IZ[i] + 1.0), (b2[0], b2[1], IZ[j] + 1.0), (b[0], b[1], ZZ[j] + 1.0), (a[0], a[1], ZZ[i] + 1.0)], col, None)
        SURF.face([(a[0], a[1], ZZ[i] + 1.0), (a[0], a[1], ZZ[i] - 1.0), (b[0], b[1], ZZ[j] - 1.0), (b[0], b[1], ZZ[j] + 1.0)], (0.50, 0.64, 0.70), None)
        SURF.face([(a[0], a[1], ZZ[i] - 1.0), (b[0], b[1], ZZ[j] - 1.0), (b2[0], b2[1], IZ[j] - 1.0), (a2[0], a2[1], IZ[i] - 1.0)], (0.55, 0.68, 0.74), None)
        SURF.face([(mx, my, zd - 1.0), (b2[0], b2[1], IZ[j] - 1.0), (a2[0], a2[1], IZ[i] - 1.0)], (0.55, 0.68, 0.74), None)
        ns["bar"](NEON, (a[0], a[1], ZZ[i] + 1.04), (b[0], b[1], ZZ[j] + 1.04), 0.38, EDGE)
    # ---- white kakau fields across the whole back (bold: edge teeth, three wing bands with zig-zag and lozenge fields, a dorsal chain, rear chevrons)
    zt = 1.045

    def PZ(x, y):
        p = L(x, y)
        return (p[0], p[1], zf(x) + zt)

    def strip(a, b, w):
        pa, pb = PZ(*a), PZ(*b)
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        dl = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / dl * w / 2, dx / dl * w / 2
        NEON.face([(pa[0] - nx, pa[1] - ny, pa[2]), (pa[0] + nx, pa[1] + ny, pa[2]), (pb[0] + nx, pb[1] + ny, pb[2]), (pb[0] - nx, pb[1] - ny, pb[2])], GLOWW, None)

    def poly(pts):
        NEON.face([PZ(*p) for p in pts], GLOWW, None)

    def inw(p, k):
        v = (0.0 - p[0], 3.0 - p[1])
        d = math.hypot(*v) or 1.0
        return (v[0] / d * k, v[1] / d * k)

    def band(sx, k, w):
        pts = []
        for (x, y) in le:
            iv = inw((x, y), k)
            pts.append((sx * (x + iv[0]), y + iv[1]))
        for q in range(len(pts) - 1):
            strip(pts[q], pts[q + 1], w)
        return pts
    for sx in (-1, 1):
        b1 = band(sx, 1.8, 0.8)
        for q in range(len(le) - 1):                      # niho mano along the leading edge
            a, b = b1[q], b1[q + 1]
            mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            iv = inw((abs(mid[0]), mid[1]), 3.4 * (1 - 0.45 * q / 14.0))
            poly([a, b, (mid[0] + sx * iv[0], mid[1] + iv[1])])
        b2 = band(sx, 9.0, 1.1)
        b3 = band(sx, 16.0, 1.1)
        b4 = band(sx, 23.0, 1.1)
        for q in range(0, len(le) - 1):                   # zig-zag teeth between the second and third bands
            a, b = b2[q], b2[q + 1]
            c = b3[q]
            d_ = b3[q + 1]
            if q % 2 == 0:
                poly([a, b, ((c[0] + d_[0]) / 2, (c[1] + d_[1]) / 2)])
            else:
                poly([c, d_, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)])
        for q in range(0, len(le) - 2, 2):                # lozenges between the third and fourth bands
            a, c = b3[q + 1], b4[q + 1]
            mid = ((a[0] + c[0]) / 2, (a[1] + c[1]) / 2)
            poly([(mid[0] - sx * 2.4, mid[1]), (mid[0], mid[1] + 3.0), (mid[0] + sx * 2.4, mid[1]), (mid[0], mid[1] - 3.0)])
        for j in range(3):                                # big chevrons along the trailing zone, pointing forward
            strip((sx * (24.0 + 6.0 * j), -2.0 - 2.0 * j), (sx * (14.0 + 3.0 * j), -9.0 - 1.2 * j), 1.0)
        poly([(sx * (HS - 3.0), -9.5), (sx * le[11][0], le[11][1] - 2.0), (sx * (HS - 10.0), y_te(HS - 10.0) + 1.5)])
    for k in range(6):                                    # dorsal chain of lozenges down the midline
        cyl = 17.0 - 6.0 * k
        poly([(-2.2, cyl), (0, cyl + 3.0), (2.2, cyl), (0, cyl - 3.0)])
    # ---- the tail: segmented mechanical root, slim whip, long and mostly straight with one gentle C, neon centre line
    prev = L(0, -23)
    pz = zd - 0.6
    for k in range(1, 31):
        u = k / 30.0
        x, y = 5.0 * math.sin(math.pi * u), -23.0 - 2.1 * k
        q = L(x, y)
        z = zd - 0.6 - 0.10 * k
        if k <= 6:
            r = 1.6 - 0.1 * k
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 8, (0.46, 0.60, 0.68) if k % 2 else (0.40, 0.54, 0.62))
            ns["box"](NEON, q[0] - r * 0.9, q[1] - r * 0.9, z - r * 0.3, q[0] + r * 0.9, q[1] + r * 0.9, z + r * 0.3, sc(PHOTO, 1.1))
        else:
            r = 0.42 * (1 - (k - 6) / 26.0) + 0.1
            tube(SURF, (prev[0], prev[1], pz), (q[0], q[1], z), r, 6, (0.44, 0.58, 0.66))
        ns["bar"](NEON, (prev[0], prev[1], pz + 0.25), (q[0], q[1], z + 0.25), 0.10, EDGE)
        prev, pz = q, z
    ns["dome"](NEON, prev[0], prev[1], pz, 0.45, sc(PHOTO, 1.8), n=8, rings=3, hemi=False)
    # ---- the compound: nine hale-biodomes on lava-stone heiau plinths, with walkways and lanai decks
    stone = (0.09, 0.08, 0.08)
    bronze = (0.58, 0.46, 0.27)
    thr_rng = random.Random(12)
    WALL = (0.24, 0.13, 0.06)
    WALL2 = (0.28, 0.16, 0.08)
    TH = [(0.22, 0.34, 0.05), (0.20, 0.30, 0.04), (0.27, 0.38, 0.07), (0.16, 0.26, 0.04)]
    plr = random.Random(5)

    def hale(x, y, w, d, hw, hr, yaw_off, kind, glow, tiers=1, base_dz=0.0):
        """a futuristic hale: stone plinth, lit interior with planting, a steep glass gridshell roof on a bronze kapa-lattice frame."""
        p = L(x, y)
        yw = yaw + yaw_off
        ax, ay = math.cos(yw), math.sin(yw)
        bx, by = -ay, ax
        zb0 = zf(x) + 1.0 - 0.6 + base_dz
        z0 = zb0
        for t in range(tiers):
            ex_ = 2.2 + 2.2 * (tiers - 1 - t)
            obox(SURF, p[0], p[1], z0, (d + ex_) * SC, (w + ex_) * SC, 1.3, yw, stone)
            obox(NEON, p[0], p[1], z0 + 1.15, (d + ex_) * SC * 1.01, (w + ex_) * SC * 1.01, 0.18, yw, sc(DIVE, 0.9), top=False)       # lit terrace lip
            z0 += 1.3

        def C(sx, sy, e=0.0):
            return (p[0] + bx * sx * (w / 2 + e) + ax * sy * (d / 2 + e), p[1] + by * sx * (w / 2 + e) + ay * sy * (d / 2 + e))
        # warm interior: a floor glow and an inner roof-shaped glow volume
        obox(NEON, p[0], p[1], z0, d * 0.94, w * 0.94, 0.18, yw, sc(DIVE, 0.6 * glow))
        zr0, zr1 = z0 + hw, z0 + hw + hr
        k_in = 0.86
        if kind == "gable":
            for sx_ in (-1, 1):
                a0, a1, r0, r1 = C(sx_ * k_in, -k_in), C(sx_ * k_in, k_in), C(0, k_in), C(0, -k_in)
                NEON.face([(a0[0], a0[1], z0), (a1[0], a1[1], z0), (a1[0], a1[1], zr0), (a0[0], a0[1], zr0)], sc(DIVE, 0.42 * glow), None)
                NEON.face([(a0[0], a0[1], zr0), (a1[0], a1[1], zr0), (r1[0], r1[1], zr1 - 0.4), (r0[0], r0[1], zr1 - 0.4)], sc(DIVE, 0.30 * glow), None)
            for sy_ in (-1, 1):
                g0, g1, rr = C(-k_in, sy_ * k_in), C(k_in, sy_ * k_in), C(0, sy_ * k_in)
                NEON.face([(g0[0], g0[1], z0), (g1[0], g1[1], z0), (g1[0], g1[1], zr0), (g0[0], g0[1], zr0)], sc(DIVE, 0.42 * glow), None)
                NEON.face([(g0[0], g0[1], zr0), (g1[0], g1[1], zr0), (rr[0], rr[1], zr1 - 0.4)], sc(DIVE, 0.36 * glow), None)
        else:                                                                                                     # hip: a short ridge
            ridge = 0.3
            for (sx_, sy_) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                pass
            q0, q1 = C(0, -ridge * k_in), C(0, ridge * k_in)
            for sx_ in (-1, 1):
                a0, a1 = C(sx_ * k_in, -k_in), C(sx_ * k_in, k_in)
                NEON.face([(a0[0], a0[1], zr0), (a1[0], a1[1], zr0), (q1[0], q1[1], zr1 - 0.4), (q0[0], q0[1], zr1 - 0.4)], sc(DIVE, 0.30 * glow), None)
            for sy_ in (-1, 1):
                g0, g1 = C(-k_in, sy_ * k_in), C(k_in, sy_ * k_in)
                qq = q1 if sy_ > 0 else q0
                NEON.face([(g0[0], g0[1], zr0), (g1[0], g1[1], zr0), (qq[0], qq[1], zr1 - 0.4)], sc(DIVE, 0.36 * glow), None)
            for sx_ in (-1, 1):
                for sy_ in (-1, 1):
                    c = C(sx_ * k_in, sy_ * k_in)
                    NEON.face([(c[0], c[1], z0), (C(sx_ * k_in, 0)[0], C(sx_ * k_in, 0)[1], z0), (C(sx_ * k_in, 0)[0], C(sx_ * k_in, 0)[1], zr0), (c[0], c[1], zr0)], sc(DIVE, 0.4 * glow), None)
        # tropical planting seen through the glass
        for _ in range(max(4, int(w * d / 5.0))):
            sx_, sy_ = plr.uniform(-0.7, 0.7), plr.uniform(-0.7, 0.7)
            c = C(sx_, sy_)
            ph = plr.uniform(0.9, min(2.6, hw + hr * 0.35))
            ns["bar"](SM, (c[0], c[1], z0 + 0.1), (c[0], c[1], z0 + ph), 0.16, (0.20, 0.14, 0.08))
            for q in range(5):
                a_ = 2 * math.pi * q / 5 + plr.uniform(0, 1)
                ns["bar"](SM, (c[0], c[1], z0 + ph), (c[0] + 0.9 * math.cos(a_), c[1] + 0.9 * math.sin(a_), z0 + ph - 0.35), 0.28, (0.10, 0.40, 0.16))
        # timber walls (brown), a lit doorway on the gable end, amber window slits
        tw = 0.38
        for sx_ in (-1, 1):
            c = C(sx_ * 0.97, 0.0)
            obox(SURF, c[0], c[1], z0, d * 0.96, tw, hw, yw, WALL if sx_ > 0 else WALL2)
            for kk in range(max(1, int(d / 3.2))):
                f = -0.5 + (kk + 0.5) / max(1, int(d / 3.2))
                cw = (c[0] + ax * f * d * 0.9, c[1] + ay * f * d * 0.9)
                obox(NEON, cw[0] + bx * sx_ * 0.05, cw[1] + by * sx_ * 0.05, z0 + hw * 0.35, 0.9, tw * 1.05, hw * 0.4, yw, sc(DIVE, 1.5 * glow), top=False)
        dw = 1.3 if w > 2.5 else 0.0
        for sy_ in (-1, 1):
            c = C(0.0, sy_ * 0.97)
            seg = (w - dw) / 2.0
            for sg in (-1, 1):
                off = sg * (dw / 2 + seg / 2)
                obox(SURF, c[0] + bx * off, c[1] + by * off, z0, seg, tw, hw, yw + math.pi / 2, WALL if sg > 0 else WALL2)
            if dw:
                obox(NEON, c[0], c[1], z0, dw * 0.95, tw * 0.8, hw * 0.86, yw + math.pi / 2, sc(DIVE, 3.8 * glow), top=False)           # the doorway glow
                ns["spot_at"]((c[0] + ax * sy_ * 6.0, c[1] + ay * sy_ * 6.0, z0), (c[0], c[1], z0 + hw * 0.6), DIVE, 3.5e3 * glow, 100.0)    # spill from the door
        # the glass gridshell: A-frame slopes (gable) or four hip slopes, a bronze kapa-style diagonal lattice, a lit ridge
        e = 0.8
        glass = (0.8, 0.92, 1.0)
        def slope(E0, E1, T0, T1, zlo, zhi, split=0.72, nl=8):
            """pili-grass thatch in layered strips on the lower part of a slope (eave E0-E1 up to top T0-T1), a glass strip above (a lit ridge band)."""
            def pt(Ea, Ta, f, z_a, z_b):
                return (Ea[0] + (Ta[0] - Ea[0]) * f, Ea[1] + (Ta[1] - Ea[1]) * f, z_a + (z_b - z_a) * f)
            for l_ in range(nl):
                f0, f1 = split * l_ / nl, split * (l_ + 1) / nl
                col = TH[thr_rng.randrange(4)] if l_ % 2 == 0 else TH[(l_ // 2 + 1) % 2]
                SURF.face([pt(E0, T0, f0, zlo, zhi), pt(E1, T1, f0, zlo, zhi), pt(E1, T1, f1, zlo, zhi), pt(E0, T0, f1, zlo, zhi)], col, None)
                ns["bar"](SM, pt(E0, T0, f1, zlo, zhi), pt(E1, T1, f1, zlo, zhi), 0.07, (0.30, 0.28, 0.08))            # the layer line
            g0, g1, g2, g3 = pt(E0, T0, split, zlo, zhi), pt(E1, T1, split, zlo, zhi), (T1[0], T1[1], zhi), (T0[0], T0[1], zhi)
            GLASS.face([g0, g1, g2, g3], glass, None)
            NEON.face([(g0[0], g0[1], g0[2] + 0.02), (g1[0], g1[1], g1[2] + 0.02), (g2[0], g2[1], g2[2] - 0.05), (g3[0], g3[1], g3[2] - 0.05)], sc(DIVE, 0.6 * glow), None)
        if kind == "gable":
            for sx_ in (-1, 1):
                a0, a1, r0, r1 = C(sx_, -1, e), C(sx_, 1, e), C(0, 1, e), C(0, -1, e)
                slope(a0, a1, r1, r0, zr0, zr1)
                nst = max(4, int(d * 0.9))
                for i in range(nst):
                    f0, f1 = -1 + 2 * i / nst, -1 + 2 * (i + 1) / nst
                    pa, pb = C(sx_, f0, e), C(sx_, f1, e)
                    ra, rb = C(0, f0, e), C(0, f1, e)
                    ns["bar"](SM, (pa[0], pa[1], zr0), (ra[0], ra[1], zr1), 0.16, bronze)                                  # rafters
                    ns["bar"](SM, (pa[0], pa[1], zr0), (rb[0], rb[1], zr1), 0.10, bronze)                                  # lattice diagonals
                    ns["bar"](SM, (pb[0], pb[1], zr0), (ra[0], ra[1], zr1), 0.10, bronze)
                for lv in (0.33, 0.66):                                                                                     # purlins
                    pa, pb = C(sx_ * (1 - lv), -1, e * (1 - lv)), C(sx_ * (1 - lv), 1, e * (1 - lv))
                    ns["bar"](SM, (pa[0], pa[1], zr0 + hr * lv), (pb[0], pb[1], zr0 + hr * lv), 0.10, bronze)
            for sy_ in (-1, 1):
                g0, g1, rr = C(-1, sy_, e), C(1, sy_, e), C(0, sy_, e)
                GLASS.face([(g0[0], g0[1], zr0), (g1[0], g1[1], zr0), (rr[0], rr[1], zr1)], glass, None)
                ns["bar"](SM, (g0[0], g0[1], zr0), (rr[0], rr[1], zr1), 0.18, bronze)
                ns["bar"](SM, (g1[0], g1[1], zr0), (rr[0], rr[1], zr1), 0.18, bronze)
                ns["bar"](SM, (g0[0], g0[1], zr0), (g1[0], g1[1], zr0), 0.16, bronze)
            r0, r1 = C(0, -1, e), C(0, 1, e)
            ns["bar"](NEON, (r0[0], r0[1], zr1 + 0.05), (r1[0], r1[1], zr1 + 0.05), 0.24, sc(DIVE, 1.5 * glow))
            for sx_ in (-1, 1):
                a0, a1 = C(sx_, -1, e), C(sx_, 1, e)
                ns["bar"](NEON, (a0[0], a0[1], zr0), (a1[0], a1[1], zr0), 0.14, sc(DIVE, 0.9))
        else:
            ridge = 0.3
            q0, q1 = C(0, -ridge, e * 0.5), C(0, ridge, e * 0.5)
            corners = [C(-1, -1, e), C(1, -1, e), C(1, 1, e), C(-1, 1, e)]
            for i in range(4):
                a, b = corners[i], corners[(i + 1) % 4]
                top_a = q0 if i in (0, 1) else q1
                top_b = q0 if (i + 1) % 4 in (0, 1) else q1
                slope(a, b, top_a, top_b, zr0, zr1, split=0.66, nl=6)
                ns["bar"](SM, (a[0], a[1], zr0), (b[0], b[1], zr0), 0.16, bronze)
                ns["bar"](SM, (a[0], a[1], zr0), (top_a[0], top_a[1], zr1), 0.18, bronze)
                m_ = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
                ns["bar"](SM, (m_[0], m_[1], zr0), (top_a[0] * 0.5 + top_b[0] * 0.5, top_a[1] * 0.5 + top_b[1] * 0.5, zr1), 0.10, bronze)
            ns["bar"](NEON, (q0[0], q0[1], zr1 + 0.05), (q1[0], q1[1], zr1 + 0.05), 0.24, sc(DIVE, 1.5 * glow))
        return p, zr1
    layout = [
        # (x, y, w, d, wall, ridge, yaw offset, kind, glow, tiers)
        (0.0, 3.0, 7.0, 12.0, 3.0, 12.5, 0.0, "gable", 1.4, 2),       # the hero: a tall hale-biodome
        (0.0, -11.5, 4.4, 7.0, 1.8, 6.0, 0.0, "gable", 0.9, 1),
        (-9.0, 11.0, 5.0, 5.0, 1.8, 6.5, 0.0, "hip", 0.9, 1),
        (9.0, 11.0, 5.0, 5.0, 1.8, 6.5, 0.0, "hip", 0.9, 1),
        (-10.0, -3.0, 3.6, 6.2, 1.6, 5.2, 0.0, "gable", 0.8, 1),
        (10.0, -3.0, 3.6, 6.2, 1.6, 5.2, 0.0, "gable", 0.8, 1),
        (-23.0, 3.0, 4.0, 7.0, 1.6, 5.6, math.pi / 2, "gable", 0.8, 1),
        (23.0, 3.0, 4.0, 7.0, 1.6, 5.6, math.pi / 2, "gable", 0.8, 1),
        (36.0, -2.5, 3.6, 3.6, 1.4, 4.6, 0.0, "hip", 0.8, 1),
    ]
    centres = []
    for (x, y, w, d, hw, hr, yo, kind, gl, tiers) in layout:
        pc_, ztop = hale(x, y, w, d, hw, hr, yo, kind, gl, tiers)
        centres.append((x, y, ztop))
        ns["spot_at"]((pc_[0], pc_[1], zf(x) + 1.0), (pc_[0], pc_[1], ztop + 2.0), DIVE, (5.5e4 if tiers == 2 else 1.9e4), 110.0)
    hero_top = centres[0][2]
    # walkways and lanai decks between the buildings
    def walk(a, b, w=2.5):
        pa, pb = L(a[0], a[1]), L(b[0], b[1])
        za, zb_ = zf(a[0]) + 1.1, zf(b[0]) + 1.1
        dx, dy = pb[0] - pa[0], pb[1] - pa[1]
        dl = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / dl * w / 2, dx / dl * w / 2
        SURF.face([(pa[0] - nx, pa[1] - ny, za), (pa[0] + nx, pa[1] + ny, za), (pb[0] + nx, pb[1] + ny, zb_), (pb[0] - nx, pb[1] - ny, zb_)], (0.12, 0.11, 0.11), None)
        for sg in (-1, 1):
            ns["bar"](NEON, (pa[0] + sg * nx, pa[1] + sg * ny, za + 0.04), (pb[0] + sg * nx, pb[1] + sg * ny, zb_ + 0.04), 0.16, sc(DIVE, 1.5))
            for lk_ in range(1, int(dl / 3.0)):
                f_ = lk_ * 3.0 / dl
                ns["box"](NEON, pa[0] + dx * f_ + sg * nx - 0.18, pa[1] + dy * f_ + sg * ny - 0.18, za + 0.05, pa[0] + dx * f_ + sg * nx + 0.18, pa[1] + dy * f_ + sg * ny + 0.18, za + 0.5, sc(DIVE, 2.2))
    for (i, j) in ((0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (2, 6), (3, 7), (7, 8)):
        walk(layout[i][:2], layout[j][:2])
    for (x, y) in ((4.5, 12.0), (-4.5, -6.0), (-16.0, 6.0), (16.0, 6.0), (30.0, 0.0)):             # lanai decks
        p = L(x, y)
        obox(NEON, p[0], p[1], zf(x) + 1.05, 4.6, 4.6, 0.15, yaw, sc(DIVE, 0.6))
        obox(SURF, p[0], p[1], zf(x) + 1.0, 5.0, 5.0, 0.1, yaw, stone)
    pcrown = L(0, 3.0)
    ns["bar"](NEON, (pcrown[0], pcrown[1], hero_top), (pcrown[0], pcrown[1], hero_top + 2.6), 0.14, sc(PHOTO, 1.4))
    # ---- two integrated thrusters at the tail root: cowls on the back, glowing slots on the trailing edge, jet columns to the water
    thr = []
    for sx_ in (-1, 1):
        cx_, cy_ = sx_ * 5.8, -15.5
        cp = L(cx_, cy_)
        ns["dome"](SURF, cp[0], cp[1], zf(cx_) + 1.0, 3.0, (0.47, 0.62, 0.70), n=14, rings=4, zscale=0.35)
        sp = L(sx_ * 5.4, -20.2)
        obox(NEON, sp[0], sp[1], zf(sx_ * 5.4) - 0.3, 3.4, 3.8, 0.5, yaw, sc(PHOTO, 2.8))
        ns["ring_line"](NEON, sp[0], sp[1], zf(sx_ * 5.4) + 0.28, 2.3, 0.14, sc(PHOTO, 1.7), n=14)
        frustum(NEON, sp[0], sp[1], ZW + 0.4, zf(sx_ * 5.4) - 0.5, 1.8, 1.0, 12, sc(PHOTO, 0.2))
        ns["spot_at"]((sp[0], sp[1], ZW + 0.5), (sp[0], sp[1], zd), PHOTO, 8.0e4, 70.0)
        thr.append((sp[0], sp[1]))
    # ---- living glow: a soft emissive teal haze in the water surface layer (one coloured grid, no discs), brighter swirls in the wake
    ar = random.Random(91)
    wake = []
    for k in range(0, 40, 2):
        f = phi - math.radians(1.6) * k
        wx, wy = loop_pt(f)
        wake.append((wx + sh[0], wy + sh[1], 5.0 + 0.12 * k))
    srcs = ([(mx, my, 24.0, 1.0)] + [(tx, ty, 9.0, 0.9) for (tx, ty) in thr] + [(wx, wy, sg, 0.9) for (wx, wy, sg) in wake]
            + [(L(a_, b_)[0], L(a_, b_)[1], 10.0, 0.6) for (a_, b_) in ((30, 0), (-30, 0), (0, 27), (16, -17), (-16, -17), (44, -6), (-44, -6))])
    ph1, ph2, ph3 = ar.uniform(0, 6.28), ar.uniform(0, 6.28), ar.uniform(0, 6.28)
    import numpy as np
    WP, HP = 224, 140
    x0, y0, wbu, hbu = mx - 68.0, my - 46.0, 136.0, 92.0
    xs_ = x0 + (np.arange(WP) + 0.5) * wbu / WP
    ys_ = y0 + (np.arange(HP) + 0.5) * hbu / HP
    GX, GY = np.meshgrid(xs_, ys_)
    g = np.zeros_like(GX)
    for (sx_, sy_, sg, wgt) in srcs:
        g += wgt * np.exp(-((GX - sx_) ** 2 + (GY - sy_) ** 2) / (2 * sg * sg))
    nz = 0.5 + 0.5 * np.sin(GX * 0.21 + ph1) * np.sin(GY * 0.17 + ph2) + 0.25 * np.sin((GX + GY) * 0.43 + ph3)
    v = g * np.clip(nz - 0.2, 0.0, None)
    t_ = np.clip((v - 0.03) / 0.55, 0.0, 1.0)
    ns["HAZE"] = dict(arr=(0.9 * t_ * t_ * (3 - 2 * t_)).astype(np.float32), x0=x0, y0=y0, wbu=wbu, hbu=hbu)
    for sw in range(6):                                    # a few brighter swirls in the wake
        wx, wy, sg = wake[min(len(wake) - 1, 2 + sw * 3)]
        r0 = ar.uniform(2.0, 3.5)
        ph = ar.uniform(0, 6.28)
        prevq = None
        for q in range(0, 20):
            th_ = ph + q * 0.45
            rad = r0 * (0.35 + 0.045 * q)
            pt = (wx + rad * math.cos(th_), wy + rad * math.sin(th_), ZW + 0.12)
            if prevq:
                ns["bar"](NEON, prevq, pt, 0.18, sc((0.45, 1.0, 1.0), 0.5 * (1 - q / 24.0)))
            prevq = pt
    for _ in range(22):                                    # a few sparkles
        wx, wy, sg = wake[ar.randrange(len(wake))]
        px_, py_ = ar.gauss(wx, sg), ar.gauss(wy, sg)
        ns["box"](NEON, px_ - 0.1, py_ - 0.1, ZW + 0.1, px_ + 0.1, py_ + 0.1, ZW + 0.25, sc((0.75, 1.0, 1.0), 1.4))
    for k in range(90):
        if k % 2:
            continue
        a0, a1 = loop_pt(2 * math.pi * k / 90), loop_pt(2 * math.pi * (k + 1) / 90)
        ns["bar"](NEON, (a0[0] + sh[0], a0[1] + sh[1], ZW + 0.12), (a1[0] + sh[0], a1[1] + sh[1], ZW + 0.12), 0.30, sc(PHOTO, 0.40))
    import json
    sj = os.environ.get("SHADOW_JSON")
    if sj:
        json.dump(dict(outline=[list(p) for p in P2], zd=zd, ZW=ZW, centre=[mx, my], tail=[list(prev)], fwd=list(Fw)), open(sj, "w"))
    ns["spot_at"]((mx, my, ZW - 6.0), (mx, my, zd - 1.2), (0.30, 0.95, 1.0), 3.0e5, 60.0)
    landing(ns, hx, hy, ang0, 38.0, (hx + 10 * math.cos(ang0), hy + 10 * math.sin(ang0)))
    drifters(ns, hx, hy, rng, ang0, 8, 48.0, 74.0, 6.0, 10.0)
    c = (pcrown[0], pcrown[1], hero_top - 6.0)
    lights(ns, hx, hy, zd + 4.0, c, 5.5e5)
    return hero_top + 3.0, c




def water_haze(ns):
    """a single textured emissive layer in the water surface material: the algae haze field (ns["HAZE"]) baked to an image and added as emission."""
    H = ns.get("HAZE")
    if not H:
        return
    import bpy
    import numpy as np
    arr = H["arr"]
    hh, ww = arr.shape
    img = bpy.data.images.new("algae_haze", ww, hh, alpha=False, float_buffer=True)
    img.colorspace_settings.name = "Non-Color"
    px = np.zeros((hh, ww, 4), np.float32)
    px[..., 0] = px[..., 1] = px[..., 2] = arr
    px[..., 3] = 1.0
    img.pixels.foreach_set(px.ravel())
    img.update()
    nt = ns["MS"]["water"].node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.vector_type = "POINT"
    mp.inputs["Location"].default_value = (-H["x0"] / H["wbu"], -H["y0"] / H["hbu"], 0.0)
    mp.inputs["Scale"].default_value = (1.0 / H["wbu"], 1.0 / H["hbu"], 1.0)
    nt.links.new(geo.outputs["Position"], mp.inputs["Vector"])
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.extension = "CLIP"
    tex.interpolation = "Linear"
    nt.links.new(mp.outputs["Vector"], tex.inputs["Vector"])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(tex.outputs["Color"], bw.inputs["Color"])
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.30, 0.92, 0.95, 1.0)
    nt.links.new(bw.outputs["Val"], em.inputs["Strength"])
    ad = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(src, ad.inputs[0])
    nt.links.new(em.outputs["Emission"], ad.inputs[1])
    nt.links.new(ad.outputs["Shader"], out.inputs["Surface"])
    print("HAZE added to the water material", arr.shape, float(arr.max()), flush=True)


IDEAS = dict(A=idea_A, B=idea_B, C=idea_C, D=idea_D, E=idea_E, M=idea_M, N=idea_N, P=idea_P, Q=idea_Q)


def landmark(ns):
    """drop-in for landmark_v2: builds the idea chosen by env IDEA and returns the info dict the base build expects."""
    PR = TP.PIER
    hx, hy = ns["W"](ns["O"]["hq"]["tethys"])
    gat = ns.get("ground_at")
    bed = gat(hx, hy) if gat else -110.0
    rng = random.Random(TP.SEEDS["pier"])
    lk = ns["O"].get("tethys_lock") if isinstance(ns.get("O"), dict) else None
    ang0 = math.atan2(lk["P"][1] - hy, lk["P"][0] - hx) if lk else math.radians(PR["arm0"])
    key = os.environ.get("IDEA", "A")
    top, tgt = IDEAS[key](ns, hx, hy, rng, ang0)
    ZW = ns["ZW"]
    rooms = {"main_deck": tgt, "crown": (hx, hy, top), "server": (hx, hy, ZW - 30.0), "collar": (hx, hy, ZW + 0.5)}
    for k in range(5):
        rooms["deck_%d" % (k + 1)] = (hx, hy, ZW - 8.0 - 5.0 * k)
    return dict(label=(hx, hy, top + 6.0), crown=(hx, hy, top), hue=TP.ABYSS, rooms=rooms, server=(hx, hy, ZW - 30.0), pods=[], footprint=PR["lot_r"],
                centre=(hx, hy), bed=bed, top=top)
