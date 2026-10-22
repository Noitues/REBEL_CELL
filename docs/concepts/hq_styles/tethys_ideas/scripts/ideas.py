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


IDEAS = dict(A=idea_A, B=idea_B, C=idea_C, D=idea_D, E=idea_E)


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
