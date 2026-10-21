"""Abyssal bioluminescent restyle of the Tethys pier city (exploration; the base pipeline is patched at run time, never edited).

Shapes (all write into the city accumulators SURF / SMOOTH / NEON / GLASS):
  nautilus()   a chambered, nacre planispiral shell (the main HQ and the inner pods) with a lit aperture and trailing tentacles
  bell()       a jellyfish bell (outer / mid pods): emissive ribbed skin, glass shell, hanging tentacles
  coral_column / crust / kelp   coral, barnacle and kelp crust on stilts, plinths and the breakwater
  siphon_walk  a siphonophore chain as the pier link (spine, paired bells, hanging zooids)
  lure         an anglerfish lure on a long stalk (main crown and the lot-edge fence)
  radiolarian  a spiked lattice sphere
"""
import math
import random

import tethys_preset as TP

NACRE = [(0.95, 0.56, 0.76), (0.46, 0.86, 0.88), (0.60, 0.50, 0.98), (0.95, 0.78, 0.46), (0.86, 0.50, 0.90)]
CORAL = [(0.62, 0.16, 0.30), (0.80, 0.34, 0.20), (0.26, 0.52, 0.56), (0.52, 0.28, 0.66), (0.86, 0.62, 0.52), (0.90, 0.30, 0.46)]
GLOW = [(1.0, 0.18, 0.62), (0.15, 0.92, 1.0), (1.0, 0.58, 0.14), (0.55, 0.30, 1.0), (0.30, 1.0, 0.62)]
PHOTO, DIVE = TP.PHOTO, TP.DIVE


def _mix(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def _pal(pal, x):
    n = len(pal)
    x = x % n
    i = int(x)
    return _mix(pal[i], pal[(i + 1) % n], x - i)


def _sc(c, k):
    return tuple(v * k for v in c)


def _bez(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u ** 3 * p0[i] + 3 * u * u * t * p1[i] + 3 * u * t * t * p2[i] + t ** 3 * p3[i] for i in range(3))


def _chain(acc, pts, w0, w1, col, bar, wet=0):
    n = len(pts) - 1
    for i in range(n):
        w = w0 + (w1 - w0) * i / max(1, n - 1)
        bar(acc, pts[i], pts[i + 1], w, col, wet=wet)


# ------------------------------------------------------------------------------------------------ crust
def coral_bit(ns, x, y, z, rng, scale=1.0, wet=1, glow=0.18):
    SM, NEON = ns["SMOOTH"], ns["NEON"]
    k = rng.random()
    col = CORAL[rng.randrange(len(CORAL))]
    s = scale * rng.uniform(0.7, 1.4)
    if k < 0.40:
        ns["dome"](SM, x, y, z, 0.38 * s, col, n=7, rings=3, wet=wet, zscale=0.8)
    elif k < 0.72:
        tip = _sc(GLOW[rng.randrange(len(GLOW))], 1.1)
        for _ in range(rng.randint(3, 4)):
            a = rng.uniform(0, 2 * math.pi)
            L = rng.uniform(0.9, 1.7) * s
            p1 = (x + math.cos(a) * 0.45 * s, y + math.sin(a) * 0.45 * s, z + L)
            ns["bar"](SM, (x, y, z), p1, 0.13 * s, col, wet=wet)
            if rng.random() < glow * 2.2:
                ns["box"](NEON, p1[0] - 0.09, p1[1] - 0.09, p1[2] - 0.05, p1[0] + 0.09, p1[1] + 0.09, p1[2] + 0.13, tip, wet=wet)
    elif k < 0.86:
        ns["cyl"](SM, x, y, z, z + 0.9 * s, 0.17 * s, 6, _mix(col, (0.7, 0.6, 0.5), 0.3), wet=wet)
    else:
        for _ in range(4):
            ns["cyl"](SM, x + rng.uniform(-0.25, 0.25), y + rng.uniform(-0.25, 0.25), z, z + 0.2 * s, 0.13 * s, 5, (0.66, 0.66, 0.60), wet=wet)
    if rng.random() < glow:
        g = GLOW[rng.randrange(len(GLOW))]
        ns["box"](NEON, x - 0.1, y - 0.1, z + 0.15, x + 0.1, y + 0.1, z + 0.4, _sc(g, 1.3), wet=wet)


def kelp(ns, x, y, z0, h, rng, w=0.45):
    """a kelp blade: a wavering ribbon of crossed quads rising from the holdfast (z0 .. z0 + h)."""
    SM = ns["SMOOTH"]
    n = max(4, int(h / 1.1))
    ph = rng.uniform(0, 6.28)
    a = rng.uniform(0, math.pi)
    ca, sa = math.cos(a), math.sin(a)
    col = _mix((0.16, 0.30, 0.10), (0.42, 0.40, 0.10), rng.random() * 0.8)
    sway = rng.uniform(0.4, 1.0)
    pts = []
    for i in range(n + 1):
        f = i / n
        z = z0 + h * f
        o = sway * f * math.sin(ph + z * 0.55) * 1.5
        pts.append((x + o * math.cos(a + 1.57), y + o * math.sin(a + 1.57), z, w * (1 - 0.55 * f)))
    for i in range(n):
        p, q = pts[i], pts[i + 1]
        for (cx_, sx_) in ((ca, sa), (-sa, ca)):
            ns["SMOOTH"].face([(p[0] - cx_ * p[3], p[1] - sx_ * p[3], p[2]), (p[0] + cx_ * p[3], p[1] + sx_ * p[3], p[2]),
                               (q[0] + cx_ * q[3], q[1] + sx_ * q[3], q[2]), (q[0] - cx_ * q[3], q[1] - sx_ * q[3], q[2])],
                              col, None, wet=1)


def crust_ring(ns, cx, cy, r, z0, z1, n, rng, scale=1.0):
    ZW = ns["ZW"]
    for _ in range(n):
        a = rng.uniform(0, 2 * math.pi)
        z = rng.uniform(z0, z1)
        coral_bit(ns, cx + (r + rng.uniform(-0.1, 0.2)) * math.cos(a), cy + (r + rng.uniform(-0.1, 0.2)) * math.sin(a), z, rng, scale,
                  wet=1 if z < ZW else 0)


def stilts(ns, cx, cy, s, zb, bed, PR, main, rng):
    SM = ns["SMOOTH"]
    ZW = ns["ZW"]
    M = PR["main"]
    n = M["stilts"] if main else (4 if s > 0.3 else 3)
    sr = M["stilt_r"] * s
    for k in range(n):
        a = 2 * math.pi * (k + 0.5) / n
        x, y = cx + sr * math.cos(a), cy + sr * math.sin(a)
        rad = (0.95 if main else 0.30 + 0.55 * s)
        from tkit import frustum
        frustum(SM, x, y, bed, zb + 0.4, rad * 1.5, rad * 0.95, 10, (0.15, 0.12, 0.19), wet=1)
        # the crust: dense at the waterline, thinning down; coral and barnacles wrap the column
        ncr = 46 if main else int(12 + 40 * s)
        for _ in range(ncr):
            z = ZW + 2.8 - rng.expovariate(1 / (7.0 if main else 4.5))
            if z < ZW - 22:
                continue
            aa = rng.uniform(0, 2 * math.pi)
            r_ = rad * 1.05 + 0.06
            coral_bit(ns, x + r_ * math.cos(aa), y + r_ * math.sin(aa), z, rng, 1.3 if main else 1.0, wet=1 if z < ZW else 0)
        for _ in range(3 if main else 2):
            kelp(ns, x + rng.uniform(-0.4, 0.4), y + rng.uniform(-0.4, 0.4), ZW - rng.uniform(8, 20), rng.uniform(7, 16), rng)


# ------------------------------------------------------------------------------------------------ nautilus
def nautilus(ns, C, R, jitter, rng, tent=10, tent_len=14.0, alpha=0.62, turns=2.25, aperture_deg=198.0, alb=0.62):
    """a nautilus shell standing on edge, its flank tilted toward the camera. C = centre (x, y, z). Returns (top z, aperture xyz)."""
    SM, NEON = ns["SMOOTH"], ns["NEON"]
    bar = ns["bar"]
    a0 = math.radians(-45.0) + jitter
    ch = (math.cos(a0), math.sin(a0))
    lat = (-math.sin(a0), math.cos(a0), 0.0)
    n3 = (ch[0] * math.cos(alpha), ch[1] * math.cos(alpha), math.sin(alpha))
    e2 = (-ch[0] * math.sin(alpha), -ch[1] * math.sin(alpha), math.cos(alpha))
    th_end = math.radians(aperture_deg)
    g = 3.1
    b = math.log(g) / (2 * math.pi)
    off = (0.20 * R * math.cos(th_end), 0.20 * R * math.sin(th_end))

    def W(x, y, w):
        x, y = x - off[0], y - off[1]
        return (C[0] + lat[0] * x + e2[0] * y + n3[0] * w, C[1] + lat[1] * x + e2[1] * y + n3[1] * w, C[2] + lat[2] * x + e2[2] * y + n3[2] * w)

    NS_ = int(26 * turns) if R > 8 else int(16 * turns)
    NP = 16 if R > 8 else 10
    top = -1e9
    rings = []
    for i in range(NS_ + 1):
        t = i / NS_
        th = th_end - 2 * math.pi * turns * (1 - t)
        Ro = R * math.exp(-b * 2 * math.pi * turns * (1 - t))
        rho = 0.37 * Ro
        rc = Ro - rho
        cx_, cy_ = rc * math.cos(th), rc * math.sin(th)
        ur, vr = (math.cos(th), math.sin(th))
        ring = []
        for j in range(NP):
            ps = 2 * math.pi * j / NP
            # ellipse with a keel: wider flank, narrower outer rim
            rr = rho * math.cos(ps)
            ww = 0.88 * rho * math.sin(ps) * (1.0 - 0.18 * max(0.0, math.cos(ps)))
            ring.append(W(cx_ + ur * rr, cy_ + vr * rr, ww))
            top = max(top, ring[-1][2])
        rings.append((ring, th, Ro, rho, (cx_, cy_)))
    for i in range(NS_):
        r0, r1 = rings[i], rings[i + 1]
        th = r0[1]
        stripe = (int((th - th_end) / 0.17) % 2 == 0)
        for j in range(NP):
            j2 = (j + 1) % NP
            ps = 2 * math.pi * (j + 0.5) / NP
            outer = math.cos(ps) > 0.55
            x = i / NS_ * 5.0 + 0.9 * math.sin(ps)
            col = _pal(NACRE, x + rng.uniform(-0.05, 0.05))
            if outer:
                col = (0.36, 0.14, 0.20) if stripe else (0.84, 0.72, 0.62)
            # nacre sheen: lighter toward the flank centre
            col = _mix(col, (0.95, 0.92, 0.96), 0.18 * abs(math.sin(ps)))
            SM.face([r0[0][j], r0[0][j2], r1[0][j2], r1[0][j]], _sc(col, alb), None, (0, 0, 0), 0.0, 3, 0.0, 0)
        # septa (chamber walls): a thin glowing line across the front flank every ~12 steps
        if i % 3 == 0 and i > NS_ * 0.35:
            pts_ = []
            for jj in (3, 4, 5):    # across the viewer-side flank (sin ps > 0)
                pts_.append(r0[0][jj] if jj < NP else r0[0][0])
            kk = NP // 4
            pts_ = [r0[0][(kk + d) % NP] for d in (-2, -1, 0, 1, 2)]
            ln = [tuple(p[m] + n3[m] * 0.04 for m in range(3)) for p in pts_]
            for u in range(len(ln) - 1):
                bar(NEON, ln[u], ln[u + 1], 0.10 * R / 14 + 0.05, _sc(_mix(PHOTO, (1.0, 0.8, 0.95), (i / NS_)), 0.55))
            sp_ = ln[2]      # the siphuncle: the glowing duct that pierces every septum
            hh_ = 0.16 * R / 14 + 0.08
            ns['box'](NEON, sp_[0] - hh_, sp_[1] - hh_, sp_[2] - hh_, sp_[0] + hh_, sp_[1] + hh_, sp_[2] + hh_, _sc(PHOTO, 2.2))
    # the aperture: a lit mouth (warm dive-light) with a pearl lip, tentacles trailing from it
    ring, th, Ro, rho, c = rings[-1]
    cen = W(c[0], c[1], 0.0)
    for j in range(NP):
        j2 = (j + 1) % NP
        NEON.face([ring[j], ring[j2], cen], _sc(DIVE, 1.6), None)
    for j in range(NP):
        j2 = (j + 1) % NP
        bar(NEON, ring[j], ring[j2], 0.18 + 0.02 * R, _sc(PHOTO, 1.3))
    tan = (-math.sin(th), math.cos(th))
    tdir = (lat[0] * tan[0] + e2[0] * tan[1], lat[1] * tan[0] + e2[1] * tan[1], lat[2] * tan[0] + e2[2] * tan[1])
    for m in range(tent):
        ps = 2 * math.pi * m / tent
        p0 = ring[int(ps / (2 * math.pi) * NP) % NP]
        L = tent_len * rng.uniform(0.6, 1.1)
        ph = rng.uniform(0, 6.28)
        pts = []
        for q in range(15):
            f = q / 14
            drop = L * f
            sw = 0.9 * f * math.sin(ph + f * 5.5)
            pts.append((p0[0] + tdir[0] * 1.6 * f * 3 + lat[0] * sw, p0[1] + tdir[1] * 1.6 * f * 3 + lat[1] * sw, p0[2] + tdir[2] * 1.2 * f - drop))
        col = _mix(GLOW[m % len(GLOW)], (1, 1, 1), 0.3) if m % 4 else (1.0, 0.10, 0.08)
        for q in range(14):
            bar(NEON, pts[q], pts[q + 1], 0.16 * (1 - 0.5 * q / 14) + 0.04, _sc(col, 0.5 + 1.2 * (q / 14) ** 2))
        e = pts[-1]
        ns["box"](NEON, e[0] - 0.22, e[1] - 0.22, e[2] - 0.22, e[0] + 0.22, e[1] + 0.22, e[2] + 0.22, _sc(col, 3.0))
    # the lure points: highest point of the outer whorl
    return top, cen, W, n3, e2, lat


def lure(ns, base, sway_dir, h, arch, rng, big=True, hue=None):
    """an anglerfish illicium: a stalk rising from base, arching toward sway_dir, ending in a bright bulb."""
    SM, NEON, bar = ns["SMOOTH"], ns["NEON"], ns["bar"]
    p0 = base
    p1 = (base[0], base[1], base[2] + h * 0.8)
    p2 = (base[0] + sway_dir[0] * arch * 0.6, base[1] + sway_dir[1] * arch * 0.6, base[2] + h * 1.1)
    p3 = (base[0] + sway_dir[0] * arch, base[1] + sway_dir[1] * arch, base[2] + h * 0.82)
    pts = [_bez(p0, p1, p2, p3, i / 12) for i in range(13)]
    w = 0.30 if big else 0.10
    _chain(SM, pts, w, w * 0.4, (0.10, 0.09, 0.13), bar)
    e = pts[-1]
    col = hue or DIVE
    r = 0.9 if big else 0.32
    ns["dome"](NEON, e[0], e[1], e[2], r, _sc(col, 4.5 if big else 2.6), n=10, rings=4, hemi=False, zscale=1.0)
    ns["ring_line"](NEON, e[0], e[1], e[2] - 0.2, r * 1.9, 0.05 if not big else 0.09, _sc(PHOTO, 1.2), n=18)
    return e


def radiolarian(ns, c, r, rng, spikes=26):
    """a Haeckel radiolarian: three orthogonal lattice rings sets, radiating spines, a lit core."""
    NEON, bar = ns["NEON"], ns["bar"]
    col = _sc(PHOTO, 1.2)

    def pt(a, b, k):
        return (c[0] + r * (a), c[1] + r * (b), c[2] + r * (k))
    n = 24
    for plane in range(3):
        for off in (-0.55, 0.0, 0.55):
            rr = math.sqrt(1 - off * off)
            prev = None
            for i in range(n + 1):
                t = 2 * math.pi * i / n
                u, v = rr * math.cos(t), rr * math.sin(t)
                q = (u, v, off) if plane == 0 else ((off, u, v) if plane == 1 else (u, off, v))
                q = pt(*q)
                if prev:
                    bar(NEON, prev, q, 0.10, col)
                prev = q
    for i in range(spikes):
        z = rng.uniform(-1, 1)
        a = rng.uniform(0, 2 * math.pi)
        s_ = math.sqrt(1 - z * z)
        d = (s_ * math.cos(a), s_ * math.sin(a), z)
        bar(NEON, pt(*d), pt(*(d[0] * 1.55, d[1] * 1.55, d[2] * 1.55)), 0.09, _sc(PHOTO, 0.9))
        e = pt(*(d[0] * 1.58, d[1] * 1.58, d[2] * 1.58))
        ns["box"](NEON, e[0] - 0.11, e[1] - 0.11, e[2] - 0.11, e[0] + 0.11, e[1] + 0.11, e[2] + 0.11, _sc(GLOW[i % 5], 2.2))
    ns["dome"](NEON, c[0], c[1], c[2], 0.4 * r, _sc(DIVE, 1.6), n=10, rings=4, hemi=False)


# ------------------------------------------------------------------------------------------------ bell
def bell(ns, cx, cy, zr, R, rng, tents=14, tlen=9.0, hue=0, tall=0.85):
    SM, NEON, GLASS, bar = ns["SMOOTH"], ns["NEON"], ns["GLASS"], ns["bar"]
    nm = 36 if R > 3.0 else 24
    nr = 9
    H = tall * R
    base = GLOW[(1, 1, 1, 0, 3, 2, 1)[hue % 7]]
    rib_col = _mix(base, (1, 1, 1), 0.35)
    prof = []
    for k in range(nr + 1):
        t = k / nr
        a = t * math.pi / 2
        prof.append((R * math.sin(a) ** 0.92, zr + H * math.cos(a) ** 0.72 - (0.0)))
    prof.append((R * 1.07, zr - 0.10 * R))
    lobes = 8
    for k in range(len(prof) - 1):
        (r0, z0), (r1, z1) = prof[k], prof[k + 1]
        t = (k + 0.5) / nr
        glow = 0.05 + 1.25 * min(1.0, t) ** 3.2
        for i in range(nm):
            ta, tb = 2 * math.pi * i / nm, 2 * math.pi * (i + 1) / nm
            sc0 = 1 + 0.07 * math.cos(lobes * ta) * (min(1.0, t * 1.0) ** 4)
            sc1 = 1 + 0.07 * math.cos(lobes * tb) * (min(1.0, t * 1.0) ** 4)
            rib = (i % 3 == 0)
            c_ = _sc(_mix(base, rib_col, 0.5 if rib else 0.0), glow * (2.1 if rib else 0.55) * 0.55)
            pts = [(cx + r0 * sc0 * math.cos(ta), cy + r0 * sc0 * math.sin(ta), z0), (cx + r0 * sc1 * math.cos(tb), cy + r0 * sc1 * math.sin(tb), z0),
                   (cx + r1 * sc1 * math.cos(tb), cy + r1 * sc1 * math.sin(tb), z1), (cx + r1 * sc0 * math.cos(ta), cy + r1 * sc0 * math.sin(ta), z1)]
            if r0 < 1e-4:
                pts = pts[1:]
            NEON.face(pts, c_, None)
            if rib and k % 2 == 1:           # the glass catch (gloss) over the skin
                GLASS.face([(p[0] * 1.0, p[1], p[2] + 0.0) for p in pts], (0.8, 0.9, 1.0), None)
    # lappets: scalloped fringe hanging from the margin (Haeckel's discomedusae)
    for i in range(nm):
        ta, tb = 2 * math.pi * i / nm, 2 * math.pi * (i + 1) / nm
        tm = 0.5 * (ta + tb)
        rr0 = R * 1.07
        NEON.face([(cx + rr0 * math.cos(ta), cy + rr0 * math.sin(ta), zr - 0.10 * R), (cx + rr0 * math.cos(tb), cy + rr0 * math.sin(tb), zr - 0.10 * R),
                   (cx + rr0 * 1.04 * math.cos(tm), cy + rr0 * 1.04 * math.sin(tm), zr - 0.10 * R - 0.28 * R)], _sc(rib_col, 0.9), None)
    # rim ring
    ns["ring_line"](NEON, cx, cy, zr - 0.10 * R, R * 1.07, 0.10 + 0.03 * R, _sc(rib_col, 2.0), n=nm)
    # oral arms / manubrium: ruffled glowing tubes hanging from the underside
    for m in range(4):
        a = 2 * math.pi * m / 4 + 0.4
        pts = []
        for q in range(8):
            f = q / 7
            pts.append((cx + 0.22 * R * math.cos(a) + 0.35 * math.sin(f * 7 + m) * (f + 0.2), cy + 0.22 * R * math.sin(a) + 0.35 * math.cos(f * 6 + m) * (f + 0.2),
                        zr + 0.1 * R - f * 0.7 * R))
        _chain(NEON, pts, 0.28, 0.12, _sc(_mix(base, (1, 0.7, 0.8), 0.5), 0.9), bar)
    # marginal tentacles trailing into the water, with bright bead tips
    for m in range(tents):
        a = 2 * math.pi * m / tents + rng.uniform(-0.15, 0.15)
        L = tlen * rng.uniform(0.55, 1.15)
        ph = rng.uniform(0, 6.28)
        x0, y0 = cx + R * 1.06 * math.cos(a), cy + R * 1.06 * math.sin(a)
        pts = []
        for q in range(13):
            f = q / 12
            o = 0.7 * f * math.sin(ph + f * 4.0)
            pts.append((x0 + math.cos(a) * 0.5 * f * R * 0.5 + o * math.cos(a + 1.57), y0 + math.sin(a) * 0.5 * f * R * 0.5 + o * math.sin(a + 1.57),
                        zr - 0.1 * R - L * f))
        col = _mix(base, (1, 1, 1), 0.25)
        for q in range(12):
            bar(NEON, pts[q], pts[q + 1], 0.13 * (1 - 0.5 * q / 12) + 0.03, _sc(col, 0.5 + 1.6 * (q / 12) ** 2))
        for q in (4, 8, 12):
            e = pts[q]
            cc_ = (1.0, 0.08, 0.06) if (m % 5 == 0 and q == 12) else col
            ns["box"](NEON, e[0] - 0.16, e[1] - 0.16, e[2] - 0.16, e[0] + 0.16, e[1] + 0.16, e[2] + 0.16, _sc(cc_, 2.4 + 0.5 * q / 4))


# ------------------------------------------------------------------------------------------------ the replaced _stack
def stack(ns, cx, cy, s, hs, zb, bed, PR, bid, full=True, main=False):
    SM, SURF, NEON = ns["SMOOTH"], ns["SURF"], ns["NEON"]
    ZW = ns["ZW"]
    rng = random.Random(int(bid * 100003) + 91)
    stilts(ns, cx, cy, s, zb, bed, PR, main, rng)
    u = s / 0.8
    from tkit import frustum
    rb = 13.4 * s * (0.74 if main else 0.80)
    ek = PR["emit_k"]
    # the plinth: a reef-crusted, nacre-lined mound under the shell / bell
    hp = max(2.1, 6.6 * u) if (main or full) else (1.6 if s > 0.2 else 1.3)
    if main:
        prof = [(rb * 1.04, zb), (rb * 1.18, zb + 1.6), (rb * 1.00, zb + 3.4), (rb * 0.86, zb + 5.2), (rb * 0.74, zb + hp)]
    else:
        prof = [(rb * 1.06, zb), (rb * 1.12, zb + hp * 0.45), (rb * 0.86, zb + hp)]
    nseg = 36 if main else 18
    for k in range(len(prof) - 1):
        (r0, z0), (r1, z1) = prof[k], prof[k + 1]
        frustum(SURF, cx, cy, z0, z1, r0, r1, nseg, _pal(NACRE, k * 1.3 + bid * 7), wc=_sc(DIVE, 0.9), wl=0.55, wm=2, bid=bid)
    ztop = zb + hp
    # crust on the plinth: coral, barnacles
    for k in range(len(prof) - 1):
        (r0, z0), (r1, z1) = prof[k], prof[k + 1]
        nn = int((46 if main else 14) * (1 if main else 1))
        for _ in range(nn):
            f = rng.random()
            z, r = z0 + (z1 - z0) * f, r0 + (r1 - r0) * f
            a = rng.uniform(0, 2 * math.pi)
            coral_bit(ns, cx + (r + 0.05) * math.cos(a), cy + (r + 0.05) * math.sin(a), z, rng, 1.25 if main else 0.9, wet=1 if z < ZW else 0, glow=0.30)
    # cuttlefish colour-shift panels: a band of chromatophore cells round the plinth (main + inner)
    if main or full:
        np_ = 30 if main else 12
        for k in range(np_):
            a0 = 2 * math.pi * k / np_
            a1 = 2 * math.pi * (k + 0.82) / np_
            rr = prof[2][0] * 1.0 + 0.1 if main else prof[1][0] + 0.08
            zc = (zb + 2.4) if main else (zb + hp * 0.5)
            hh = 0.55 if main else 0.35
            col = _pal(GLOW, k * 0.37 + rng.uniform(0, 0.2))
            NEON.face([(cx + rr * math.cos(a0), cy + rr * math.sin(a0), zc - hh), (cx + rr * math.cos(a1), cy + rr * math.sin(a1), zc - hh),
                       (cx + rr * math.cos(a1), cy + rr * math.sin(a1), zc + hh), (cx + rr * math.cos(a0), cy + rr * math.sin(a0), zc + hh)],
                      _sc(col, 0.55 + 0.5 * rng.random()), None)
    info = {}
    if main:
        R = 15.5
        zc = ztop + R * 0.80 * 0.95 + 0.8
        top, ap, W, n3, e2, lat = nautilus(ns, (cx, cy, zc), R, 0.0, rng, tent=12, tent_len=19.0, alb=0.46)
        # buttress ribs (Calatrava / Oxman): pale boned arches from the plinth up under the shell
        for q in range(7):
            th_ = -math.pi * (0.12 + 0.76 * q / 6)
            T = W(0.82 * R * math.cos(th_), 0.82 * R * math.sin(th_), 0.0)
            dx_, dy_ = T[0] - cx, T[1] - cy
            dl = math.hypot(dx_, dy_) or 1.0
            B = (cx + dx_ / dl * rb * 0.72, cy + dy_ / dl * rb * 0.72, ztop - 0.3)
            c1 = (B[0] + dx_ / dl * 3.0, B[1] + dy_ / dl * 3.0, B[2] + 4.0)
            c2 = (T[0], T[1], T[2] - 4.5)
            pts_ = [_bez(B, c1, c2, T, i / 10) for i in range(11)]
            _chain(SM, pts_, 0.85, 0.35, (0.70, 0.62, 0.72), ns['bar'])
        for dz_ in (-0.95, 0.95):
            ns['ring_line'](SURF, cx, cy, zb + 2.4 + dz_, prof[2][0] + 0.12, 0.28, (0.74, 0.68, 0.76), n=40)
        # the lure: an arched stalk over the shell, a warm bulb that is also the key light
        tp = W(0.0, R * 0.98, 0.0)
        ch = (n3[0], n3[1])
        e = lure(ns, (tp[0], tp[1], tp[2] - 0.5), (ch[0] * 0.9 + 0.0, ch[1] * 0.9), 16.0, 9.0, rng, big=True)
        ns["spot_at"]((cx - 6.0, cy + 6.0, zc - 2.0), (e[0], e[1], e[2] - 0.8), DIVE, 2.5e5, 55.0)
        ns["spot_at"]((cx, cy, zc), (cx + 0.7071 * 30, cy - 0.7071 * 30, zc + 24.0), (0.55, 0.85, 1.0), 2.0e5, 40.0)
        # a radiolarian screen beside the shell, a diatom wheel on its far side
        radiolarian(ns, W(R * 0.95, -R * 0.2, 7.5), 3.9, rng)
        radiolarian(ns, W(-R * 0.55, -R * 0.82, 6.5), 2.4, rng, spikes=16)
        return top, zc, e[2]
    if full:       # inner pods: small nautilus
        R = 12.0 * u + 0.5
        zc = ztop + R * 0.80 * 0.95 + 0.4
        top, ap, W, n3, e2, lat = nautilus(ns, (cx, cy, zc), R, rng.uniform(-0.45, 0.45), rng, tent=6, tent_len=7.5 + 4 * u)
        tp = W(0.0, R * 0.98, 0.0)
        e = lure(ns, (tp[0], tp[1], tp[2] - 0.2), (n3[0] * 0.8, n3[1] * 0.8), 5.0, 2.8, rng, big=False, hue=GLOW[1])
        return top, zc, e[2]
    # outer and mid pods: jellyfish bells
    R = 14.0 * u * (0.98 if s > 0.2 else 1.05)
    rim = ztop + 0.35
    bell(ns, cx, cy, rim, R, rng, tents=14 if s > 0.2 else 10, tlen=9.0 + 4 * (s > 0.2), hue=int(rng.random() * 5))
    top = rim + 0.85 * R
    return top, rim, top + 0.2


def walk(ns, p0, p1, rt, zw, bed_at, PR):
    """a siphonophore chain: a lit spine on the deck line, paired bells, hanging zooids; a dark thin deck keeps it a path."""
    from tkit import seg_box
    SURF, SM, NEON, bar, sc_ = ns["SURF"], ns["SMOOTH"], ns["NEON"], ns["bar"], ns["sc"]
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    if L < 0.5:
        return
    ux, uy = dx / L, dy / L
    vx, vy = -uy, ux
    rng = random.Random(int(abs(p0[0] * 131 + p0[1] * 17 + p1[0] * 7)) % 10007)
    seg_box(SURF, p0, p1, 1.5 * rt, zw - 0.45, zw, (0.26, 0.22, 0.32))
    n = max(3, int(L / (1.9 * rt)))
    spine = []
    for m in range(n + 1):
        f = m / n
        spine.append((p0[0] + dx * f, p0[1] + dy * f, zw + 0.85 * rt + 0.35 * math.sin(f * L * 0.9)))
    for i in range(n):
        col = _pal(GLOW, i * 0.31 + rng.random() * 0.1)
        bar(NEON, spine[i], spine[i + 1], 0.22 * rt, _sc(_mix(col, (1, 1, 1), 0.2), 0.8))
    for m in range(n + 1):
        f = m / n
        c = spine[m]
        col = _pal(GLOW, m * 0.31)
        for side in (-1, 1):
            bx, by = c[0] + vx * side * 0.95 * rt, c[1] + vy * side * 0.95 * rt
            bz = c[2] + 0.1
            r = 0.62 * rt * (1.0 if m % 2 == 0 else 0.8)
            ns["dome"](NEON, bx, by, bz, r, _sc(col, 1.1), n=8, rings=3, zscale=0.9)
            ns["ring_line"](NEON, bx, by, bz + 0.02, r * 1.02, 0.05, _sc(_mix(col, (1, 1, 1), 0.5), 1.6), n=8)
        if m % 3 == 1:        # a zooid hanging below the deck, tentacle filament
            zx, zy = c[0] + vx * rng.choice((-1, 1)) * 1.0 * rt, c[1] + vy * rng.choice((-1, 1)) * 1.0 * rt
            ln = rng.uniform(2.5, 5.5)
            prev = (zx, zy, zw - 0.4)
            for q in range(1, 7):
                pnt = (zx + 0.4 * math.sin(q * 1.1 + m), zy + 0.4 * math.cos(q * 1.1 + m), zw - 0.4 - ln * q / 6)
                bar(NEON, prev, pnt, 0.12, _sc(col, 0.5 + 0.35 * q))
                prev = pnt
            ns["box"](NEON, prev[0] - 0.2, prev[1] - 0.2, prev[2] - 0.2, prev[0] + 0.2, prev[1] + 0.2, prev[2] + 0.2, _sc(col, 3.0))
    # piles: coral-crusted
    s_ = 3.0
    from tkit import tube
    while s_ < L - 2.0:
        x, y = p0[0] + ux * s_, p0[1] + uy * s_
        tube(SM, (x, y, bed_at(x, y)), (x, y, zw - 0.45), 0.34, 6, (0.15, 0.12, 0.19), wet=1)
        for _ in range(9):
            z = ns["ZW"] + 1.5 - rng.expovariate(1 / 4.0)
            a = rng.uniform(0, 6.28)
            coral_bit(ns, x + 0.4 * math.cos(a), y + 0.4 * math.sin(a), z, rng, 0.8, wet=1 if z < ns["ZW"] else 0)
        s_ += 9.0


def crust_breakwater(ns, x0, y0, x1, y1, rng):
    """coral reef crust and hanging kelp along a breakwater segment."""
    ZW = ns["ZW"]
    L = math.hypot(x1 - x0, y1 - y0)
    n = int(L / 0.7)
    for i in range(n):
        f = rng.random()
        x, y = x0 + (x1 - x0) * f, y0 + (y1 - y0) * f
        ox, oy = rng.uniform(-1.1, 1.1), rng.uniform(-1.1, 1.1)
        z = rng.uniform(ZW - 3.6, ZW + 1.1)
        coral_bit(ns, x + 0.5 * ox, y + 0.5 * oy, z, rng, 1.1, wet=1 if z < ZW else 0, glow=0.35)
    for i in range(int(L / 3.5)):
        f = rng.random()
        kelp(ns, x0 + (x1 - x0) * f + rng.uniform(-0.6, 0.6), y0 + (y1 - y0) * f + rng.uniform(-0.6, 0.6), ZW - rng.uniform(7, 14), rng.uniform(6, 11), rng)


def buoy(ns, x, y, k, ZW, hx, hy):
    rng = random.Random(7000 + k)
    d = (x - hx, y - hy)
    L = math.hypot(*d) or 1.0
    d = (d[0] / L, d[1] / L)
    big = (k % 6 == 0)
    h = rng.uniform(5.5, 8.5) if big else rng.uniform(2.2, 3.4)
    lure(ns, (x, y, ZW - 0.6), d, h, 1.8 if big else 0.9, rng, big=False, hue=(DIVE if big else GLOW[k % 5])) if not big else \
        _big_lure(ns, x, y, ZW, d, h, rng)
    for _ in range(5):
        a = rng.uniform(0, 6.28)
        coral_bit(ns, x + 0.4 * math.cos(a), y + 0.4 * math.sin(a), ZW - rng.uniform(0.2, 2.5), rng, 0.7, wet=1)


def _big_lure(ns, x, y, ZW, d, h, rng):
    lure(ns, (x, y, ZW - 0.6), d, h, 2.4, rng, big=True, hue=DIVE)
