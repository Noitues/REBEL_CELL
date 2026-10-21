"""LOOK Solace S2 (2026-10-21): the concept's helix HQ and C's porcelain cross-plan hospital, as landmark builders.

exec'd by landmark_build_v1.py (same globals: Acc accumulators SOLID / LIT / NEON / WIN, rng, HEROES26, SITES26) for the
Solace jobs. Geometry follows art-pass docs/concepts/solace_vertical/district/scripts/sd_main.py (helix(), oval_window(),
plaza(), plinth_build(), hospital() with direction C), re-expressed as Acc faces so the landmark roles apply:
lm_lit = the lit lime tube skin, lm_toon = decks / porcelain, lm_neon = rungs, rings, window frames, cross, lm_win = window faces.
No beam, no centre tower, no chaser, no sign text. Plinth: its own node `solace_hq__plinth`, exported switched off (scale 0).
"""
import math

LIME = (0.55, 1.0, 0.30)
PINKC = (1.0, 0.30, 0.65)
TUBE = (0.27, 0.54, 0.15)
TUBE_TONE = (0.80, 1.0)           # per-face brightness of the lit skin (baked: lm_neon has no tone ramp), the cel facets
DECK = (0.52, 0.58, 0.55)
PORC = (0.84, 0.82, 0.74)
GLASS_LEAF = (0.20, 0.50, 0.17)
BID = (0.0, 0.0, 0.0)

HELIX_R, HELIX_RT, HELIX_Z0, HELIX_Z1 = 7.5, 3.4, 2.5, 86.0
FLOOR_H = 4.2
PAD_R = 27.5                      # the plain round pad (the HQ lot holds 30 BU of radius)
PLINTH_TIERS = ((35.0, 1.1), (29.5, 2.2), (24.0, 3.3))
PLINTH_STAIR_FOOT = 36.0
PLINTH_NODE = "plinth"
STRAND_SIDES, STRAND_STEPS = 10, 56
WIN_N = 14


def _vsub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _vadd(a, b): return (a[0] + b[0], a[1] + b[1], a[2] + b[2])
def _vmul(a, s): return (a[0] * s, a[1] * s, a[2] * s)
def _vdot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _vcrs(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _vunit(a):
    n = math.sqrt(_vdot(a, a)) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def _bid():
    return (rng.random(), rng.random(), rng.random())


def _prism(acc, poly, z0, z1, col, top=True, bottom=False):
    """Extruded convex CCW polygon: side quads (+ cap fans)."""
    b = _bid()
    n = len(poly)
    for i in range(n):
        a, c = poly[i], poly[(i + 1) % n]
        acc.face([(a[0], a[1], z0), (c[0], c[1], z0), (c[0], c[1], z1), (a[0], a[1], z1)], col, b)
    if top:
        for k in range(1, n - 1):
            acc.face([(poly[0][0], poly[0][1], z1), (poly[k][0], poly[k][1], z1), (poly[k + 1][0], poly[k + 1][1], z1)], col, b)
    if bottom:
        for k in range(1, n - 1):
            acc.face([(poly[0][0], poly[0][1], z0), (poly[k + 1][0], poly[k + 1][1], z0), (poly[k][0], poly[k][1], z0)], col, b)


def _rect(cx, cy, hw, hd):
    return [(cx - hw, cy - hd), (cx + hw, cy - hd), (cx + hw, cy + hd), (cx - hw, cy + hd)]


def _ngon(cx, cy, r, n):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _lathe(acc, profile, n, col, cx=0.0, cy=0.0):
    """Surface of revolution, profile [(r, z)] bottom to top, outward facing for a profile that rises/turns CCW (r, z)."""
    b = _bid()
    rings = [[(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z) for k in range(n)] for r, z in profile]
    for i in range(len(profile) - 1):
        a, c = rings[i], rings[i + 1]
        for k in range(n):
            k2 = (k + 1) % n
            if profile[i][0] < 1e-6:
                acc.face([a[0], c[k2], c[k]], col, b)
            elif profile[i + 1][0] < 1e-6:
                acc.face([a[k], a[k2], c[0]], col, b)
            else:
                acc.face([a[k], a[k2], c[k2], c[k]], col, b)


def _torus(acc, R, rt, z, n, sides, col):
    _lathe(acc, [(R + rt * math.cos(2 * math.pi * k / sides), z + rt * math.sin(2 * math.pi * k / sides)) for k in range(sides + 1)], n, col)


def _flat_disc(acc, r, z, n, col):
    b = _bid()
    pts = [(r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z) for k in range(n)]
    for k in range(1, n - 1):
        acc.face([pts[0], pts[k], pts[k + 1]], col, b)


def _sweep(acc, pts, nrms, rt, sides, col):
    rings = []
    for i, c in enumerate(pts):
        T = _vunit(_vsub(pts[min(i + 1, len(pts) - 1)], pts[max(i - 1, 0)]))
        nr = _vunit(_vsub(nrms[i], _vmul(T, _vdot(nrms[i], T))))
        bn = _vunit(_vcrs(T, nr))
        rings.append([tuple(c[j] + (nr[j] * math.cos(2 * math.pi * m / sides) + bn[j] * math.sin(2 * math.pi * m / sides)) * rt for j in range(3))
                      for m in range(sides)])
    b = _bid()
    for i in range(len(pts) - 1):
        for m in range(sides):
            m2 = (m + 1) % sides
            k = TUBE_TONE[0] + (TUBE_TONE[1] - TUBE_TONE[0]) * rng.random()
            acc.face([rings[i][m], rings[i][m2], rings[i + 1][m2], rings[i + 1][m]], (col[0] * k, col[1] * k, col[2] * k), b)
    # the bottom cap (up the strand's start) closed with a fan; the top is capped by the strand's own crown dome
    for m in range(1, sides - 1):
        acc.face([rings[0][0], rings[0][m + 1], rings[0][m]], col, b)


def _cpos(ph, z):
    t = 2 * math.pi * (z - HELIX_Z0) / (HELIX_Z1 - HELIX_Z0) + ph
    return (HELIX_R * math.cos(t), HELIX_R * math.sin(t), z)


def _oval_window(ctr, T, n, f, side, wrng):
    """A sideways oval on the tube: its outline horizontal / vertical in the world (rays along -n onto the tube)."""
    rt = HELIX_RT
    ca, cb = 1.85, 1.15
    th = (-n[1], n[0], 0.0)

    def hit(dx, dz):
        q0 = (ctr[0] + n[0] * (rt + 3.0) + th[0] * dx, ctr[1] + n[1] * (rt + 3.0) + th[1] * dx, ctr[2] + dz)
        w = _vsub(q0, ctr)
        wp = _vsub(w, _vmul(T, _vdot(w, T)))
        d = (-n[0], -n[1], 0.0)
        dp = _vsub(d, _vmul(T, _vdot(d, T)))
        A, B, C = _vdot(dp, dp), 2 * _vdot(wp, dp), _vdot(wp, wp) - rt * rt
        disc = B * B - 4 * A * C
        if disc < 0:
            return None
        s = (-B - math.sqrt(disc)) / (2 * A)
        P = _vadd(q0, _vmul(d, s))
        r_ = _vsub(P, ctr)
        return P, _vunit(_vsub(r_, _vmul(T, _vdot(r_, T))))
    ring = []
    for k in range(WIN_N):
        a = 2 * math.pi * k / WIN_N
        h1 = hit(ca * math.cos(a), cb * math.sin(a))
        h2 = hit(ca * 1.14 * math.cos(a), cb * 1.2 * math.sin(a))
        if h1 is None or h2 is None:
            return
        ring.append((h1, h2))
    node = (f % 5 == 2 and side > 0)          # every fifth outward window is a bright lime node
    v = wrng.random()
    if node:
        wcol = LIME
    elif v < 0.45:
        wcol = (1.0, 0.78, 0.42)              # warm
    elif v < 0.9:
        wcol = (0.78, 1.0, 0.55)              # lime
    else:
        wcol = (1.0, 0.45, 0.75)              # pink
    k_ = 0.55 + 0.45 * wrng.random()
    wcol = (wcol[0] * k_, wcol[1] * k_, wcol[2] * k_) if not node else wcol
    lift = 0.07
    P = lambda h, e: _vadd(h[0], _vmul(h[1], e))  # noqa: E731
    ch = hit(0.0, 0.0)
    acc = NEON if node else WIN
    cen = P(ch, lift)
    for k in range(WIN_N):
        k2 = (k + 1) % WIN_N
        acc.face([cen, P(ring[k][0], lift), P(ring[k2][0], lift)][::1], wcol, BID, fj=wrng.random())
    fcol = LIME if (node or f % 2 == 0) else (0.8, 1.0, 0.85)
    for k in range(WIN_N):
        k2 = (k + 1) % WIN_N
        NEON.face([P(ring[k][0], 0.1), P(ring[k2][0], 0.1), P(ring[k2][1], 0.1), P(ring[k][1], 0.1)], fcol, BID)


def solace_helix():
    """The helix (2026-10-16 rulings): two strands of one full turn, flush bow-tie decks, two oval windows per floor per strand."""
    wrng = random.Random(SEED + 99)
    # ground: the plain round pad and its ring lights (grade-level faces: the id_ground split)
    with IDG.ground():
        _flat_disc(SOLID, PAD_R, 0.04, 40, (0.50, 0.58, 0.54))
        for R_, col in ((18.0, PINKC), (24.0, LIME)):
            b = _bid()
            n = 40
            for k in range(n):
                a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
                p = lambda a, r: (r * math.cos(a), r * math.sin(a), 0.08)  # noqa: E731
                NEON.face([p(a0, R_ - 0.2), p(a1, R_ - 0.2), p(a1, R_ + 0.2), p(a0, R_ + 0.2)][::-1], col, b)
    _lathe(SOLID, [(12.0, 0.04), (12.0, 0.4)], 32, (0.72, 0.80, 0.76))     # the helix drum
    _torus(NEON, 12.05, 0.28, 0.45, 40, 4, LIME)
    for ph, ring_col in ((0.0, LIME), (math.pi, PINKC)):
        pts, nr = [], []
        for k in range(STRAND_STEPS + 1):
            z = HELIX_Z0 + (HELIX_Z1 - HELIX_Z0) * k / STRAND_STEPS
            c = _cpos(ph, z)
            pts.append(c)
            nr.append(_vunit((c[0], c[1], 0.0)))
        _sweep(NEON, pts, nr, HELIX_RT, STRAND_SIDES, TUBE)
        top = _cpos(ph, HELIX_Z1)
        prof = [(HELIX_RT * math.cos(math.pi / 2 * k / 3), HELIX_Z1 + HELIX_RT * math.sin(math.pi / 2 * k / 3)) for k in range(4)]
        _lathe(NEON, prof, STRAND_SIDES, TUBE, top[0], top[1])
        # an own-colour lit ring round each strand top
        b = _bid()
        n = STRAND_SIDES * 2
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            r0, r1 = HELIX_RT + 0.02, HELIX_RT + 0.4
            q = lambda a, r: (top[0] + r * math.cos(a), top[1] + r * math.sin(a), HELIX_Z1 + 0.05)  # noqa: E731
            NEON.face([q(a0, r0), q(a1, r0), q(a1, r1), q(a0, r1)][::-1], ring_col, b)
    # the pink crown ring and its lime inner ring, floating over the strand tops
    _torus(NEON, 11.5, 0.42, HELIX_Z1 + 4.0, 40, 5, PINKC)
    _torus(NEON, 9.2, 0.2, HELIX_Z1 + 4.0, 40, 4, LIME)
    nfl = int((HELIX_Z1 - HELIX_Z0 - 3.0) / FLOOR_H)
    for f in range(nfl):
        zf = HELIX_Z0 + 3.0 + f * FLOOR_H
        a, c = _cpos(0.0, zf), _cpos(math.pi, zf)
        d = _vunit(_vsub(c, a))
        s = (-d[1], d[0], 0.0)
        m = _vmul(_vadd(a, c), 0.5)
        pts6 = [_vadd(a, _vmul(s, 2.6)), _vadd(m, _vmul(s, 0.7)), _vadd(c, _vmul(s, 2.6)),
                _vsub(c, _vmul(s, 2.6)), _vsub(m, _vmul(s, 0.7)), _vsub(a, _vmul(s, 2.6))]
        poly = [(p[0], p[1]) for p in pts6]
        if sum(poly[i][0] * poly[(i + 1) % 6][1] - poly[(i + 1) % 6][0] * poly[i][1] for i in range(6)) < 0:
            poly = poly[::-1]
        # the bow-tie is not convex: fan from its centre (a star-shaped polygon about m)
        cen = (m[0], m[1])
        b = _bid()
        for i in range(6):
            p0, p1 = poly[i], poly[(i + 1) % 6]
            LIT.face([(cen[0], cen[1], zf), (p0[0], p0[1], zf), (p1[0], p1[1], zf)], DECK, b)
            LIT.face([(p0[0], p0[1], zf - 0.5), (p1[0], p1[1], zf - 0.5), (p1[0], p1[1], zf), (p0[0], p0[1], zf)], DECK, b)
        col = LIME if f % 2 == 0 else PINKC                      # base-pair rungs: lime / pink alternate
        for i in range(6):
            p0, p1 = poly[i], poly[(i + 1) % 6]
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            L = math.hypot(dx, dy) or 1.0
            nx, ny = -dy / L * 0.22, dx / L * 0.22
            NEON.face([(p0[0] - nx, p0[1] - ny, zf + 0.04), (p1[0] - nx, p1[1] - ny, zf + 0.04),
                       (p1[0] + nx, p1[1] + ny, zf + 0.04), (p0[0] + nx, p0[1] + ny, zf + 0.04)][::-1], col, b)
        for ph in (0.0, math.pi):
            ctr = _cpos(ph, zf + 1.95)
            T = _vunit(_vsub(_cpos(ph, zf + 2.15), _cpos(ph, zf + 1.75)))
            rad = _vunit((ctr[0], ctr[1], 0.0))
            for side in (-1, 1):                                   # -1 inward (to the walkway), +1 outward
                _oval_window(ctr, T, _vmul(rad, side), f, side, wrng)


def solace_plinth():
    """Round 5's plinth: three circular tiers (35 / 29.5 / 24 BU) and four stair flights at N, E, S, W. Own node, off by default
    (the HQ lot may not hold a 70 BU circle: A-069)."""
    col = (0.62, 0.66, 0.64)
    scol = tuple(min(1.0, c * 1.25) for c in col)
    base = 0.2
    for r, h in PLINTH_TIERS:
        _lathe(SOLID, [(r, base), (r, base + h)], 48, col)
        _flat_disc(SOLID, r, base + h, 48, col) if r == PLINTH_TIERS[-1][0] else None
        _torus(NEON, r - 0.1, 0.22, base + h + 0.02, 48, 4, LIME)
    top = base + PLINTH_TIERS[-1][1]
    _torus(NEON, 17.0, 0.2, top + 0.03, 48, 4, PINKC)
    r0, r1, ns, hw = PLINTH_TIERS[-1][0] - 0.2, PLINTH_STAIR_FOOT, 16, 5.2
    run, rise = (r1 - r0) / ns, (top - 0.24) / ns
    for q in range(4):
        c_, s_ = round(math.cos(q * math.pi / 2)), round(math.sin(q * math.pi / 2))
        for k in range(ns):
            a, b = r0 + k * run, r0 + (k + 1) * run
            z1 = top - k * rise
            if c_ != 0:
                x0, x1 = sorted((a * c_, b * c_))
                _prism(SOLID, _rect((x0 + x1) / 2, 0.0, (x1 - x0) / 2, hw), base, z1, scol)
            else:
                y0, y1 = sorted((a * s_, b * s_))
                _prism(SOLID, _rect(0.0, (y0 + y1) / 2, hw, (y1 - y0) / 2), base, z1, scol)
        for sg in (-1, 1):
            pa = (r0 * c_ - s_ * hw * sg, r0 * s_ + c_ * hw * sg, top + 0.1)
            pb = (r1 * c_ - s_ * hw * sg, r1 * s_ + c_ * hw * sg, 0.45)
            beam(pa, pb, 0.26, LIME, acc=NEON)


# ------------------------------------------------------------------ the hospital (direction C: porcelain cross plan)
HOSP_HL, HOSP_HD = 22.0, 5.6        # wing half-length / half-depth; the Site build scales x0.8 -> 17.6 BU inside the 36 BU lot block
HOSP_H, HOSP_TOWER_H = 14.0, 22.0


def _band_walls(x0, y0, x1, y1, z0, z1, skip=()):
    """Leaf-green glass bands on the four walls of a box (a floor-height strip every 3 BU), slightly proud of the wall."""
    o = 0.07
    walls = [((x0, y0 - o), (x1, y0 - o)), ((x1 + o, y0), (x1 + o, y1)), ((x1, y1 + o), (x0, y1 + o)), ((x0 - o, y1), (x0 - o, y0))]
    nb = int((z1 - z0 - 1.0) / 3.0)
    for wi, ((ax, ay), (bx, by)) in enumerate(walls):
        if wi in skip:
            continue
        L = math.hypot(bx - ax, by - ay)
        ux, uy = (bx - ax) / L, (by - ay) / L
        for k in range(nb):
            zb = z0 + 1.6 + k * 3.0
            ins = 0.8
            p0, p1 = (ax + ux * ins, ay + uy * ins), (bx - ux * ins, by - uy * ins)
            NEON.face([(p0[0], p0[1], zb), (p1[0], p1[1], zb), (p1[0], p1[1], zb + 1.3), (p0[0], p0[1], zb + 1.3)],
                      GLASS_LEAF if (k + wi) % 3 else (0.28, 0.62, 0.20), BID)


def solace_hospital():
    """C's hospital: a porcelain cross plan (two crossing wings, a taller centre block, roof trims, a helipad) with the lit
    green cross standing over the roof, facing the camera diagonal (Blender -45 deg = glTF +x +z)."""
    hl, hd = HOSP_HL, HOSP_HD
    for (hw, dd) in ((hl, hd), (hd, hl)):
        _prism(SOLID, _rect(0.0, 0.0, hw, dd), 0.0, HOSP_H, PORC)
        _prism(SOLID, _rect(0.0, 0.0, hw + 0.5, dd + 0.5), HOSP_H, HOSP_H + 0.8, (0.62, 0.60, 0.54))
    # glass bands: on the wing end walls and long walls of each arm (the crossing interior is hidden by the other wing anyway)
    _band_walls(-hl, -hd, hl, hd, 0.0, HOSP_H, skip=())
    _band_walls(-hd, -hl, hd, hl, 0.0, HOSP_H, skip=())
    # the taller centre block
    tw = 7.6
    _prism(SOLID, _rect(0.0, 0.0, tw, tw), HOSP_H, HOSP_TOWER_H, PORC)
    _band_walls(-tw, -tw, tw, tw, HOSP_H, HOSP_TOWER_H)
    _prism(SOLID, _rect(0.0, 0.0, tw + 0.6, tw + 0.6), HOSP_TOWER_H, HOSP_TOWER_H + 0.8, (0.62, 0.60, 0.54))
    # roof trims (lime lines on the parapets)
    zt = HOSP_H + 0.85
    for (hw, dd) in ((hl, hd), (hd, hl)):
        for (a, b) in (((-hw, -dd), (hw, -dd)), ((hw, -dd), (hw, dd)), ((hw, dd), (-hw, dd)), ((-hw, dd), (-hw, -dd))):
            beam((a[0], a[1], zt), (b[0], b[1], zt), 0.3, (0.32, 0.66, 0.20), acc=NEON)
    # helipad on the tower roof and the standing cross
    zr = HOSP_TOWER_H + 0.85
    pad = [(4.6 * math.cos(2 * math.pi * k / 20), 4.6 * math.sin(2 * math.pi * k / 20), zr) for k in range(20)]
    b = _bid()
    for k in range(1, 19):
        SOLID.face([pad[0], pad[k], pad[k + 1]], (0.20, 0.26, 0.23), b)
    n = 20
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        q = lambda a, r: (r * math.cos(a), r * math.sin(a), zr + 0.06)  # noqa: E731
        NEON.face([q(a0, 4.1), q(a1, 4.1), q(a1, 4.6), q(a0, 4.6)][::-1], LIME, b)
    for (x0, y0, x1, y1) in ((-2.2, -1.8, -1.4, 1.8), (1.4, -1.8, 2.2, 1.8), (-1.4, -0.4, 1.4, 0.4)):
        NEON.face([(x0, y0, zr + 0.08), (x1, y0, zr + 0.08), (x1, y1, zr + 0.08), (x0, y1, zr + 0.08)][::-1], (0.95, 1.0, 0.95), b)
    # the lit cross over the roof, a slab facing the iso camera diagonal
    ang = math.radians(-45.0)
    ca, sa = math.cos(ang), math.sin(ang)
    cz, size, th, depth = zr + 7.0, 8.4, 2.8, 0.45

    def P(h, v, d):
        return (-sa * h + ca * d, ca * h + sa * d, cz + v)
    hs, ts = size / 2, th / 2
    for (h0, h1, v0, v1) in ((-hs, hs, -ts, ts), (-ts, ts, -hs, hs)):
        c8 = [P(h0, v0, -depth), P(h1, v0, -depth), P(h1, v1, -depth), P(h0, v1, -depth),
              P(h0, v0, depth), P(h1, v0, depth), P(h1, v1, depth), P(h0, v1, depth)]
        for qd in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
            NEON.face([c8[i] for i in qd][::-1] if qd[0] == 0 and qd[1] == 1 and qd[2] == 2 else [c8[i] for i in qd], (0.50, 0.95, 0.25), BID)
    beam((0, 0, zr), (0, 0, cz - hs), 0.6, (0.6, 0.6, 0.6))


HEROES26["solace"] = solace_helix
SITES26[("solace", "")] = solace_hospital
