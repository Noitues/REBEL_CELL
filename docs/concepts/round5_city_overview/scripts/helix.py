"""Double-helix HQ: two separate chunky helical towers 180 degrees apart around a hollow core,
joined by enclosed skybridges through the core.

Each strand is a continuous ramped band of floors (inner radius RI, outer RO, vertical thickness T,
climbing PITCH per turn), cut into short curved segments. Draw order: far-half segments, then the
bridges, then near-half segments (each group sorted by the 3D view key), so the bridges sit between
the strands and nothing overlaps wrongly.
"""
import math
from lowpoly import SS, R, hexc, mix, ramp, hsh, toner, facet, tri, line2, NEON
from city import FAM, bil3
from toon import ink_line, ink_poly, hull, BEVEL, tint, band_of, BANDS

CX, CY = 43.4, 1.9          # helix axis (back-right of the district, entrance plaza toward node (7,1))
RI, RO = 2.7, 5.5           # hollow core radius / outer radius (band depth 2.8)
T = 2.7                     # vertical band thickness (3 floors)
FLOOR = 0.9
PITCH = 16.0                # height gained per full turn
TURNS = 2.45
Z0 = 1.2                    # plaza podium height
SEG = 24                    # segments per turn
STRIPS = (NEON['cyan'], NEON['magenta'])


def z_at(theta):
    return Z0 + PITCH * theta / (2 * math.pi)


def top_z():
    return z_at(TURNS * 2 * math.pi) + T


def draw_hq(dp):
    cam = dp.cam
    d = dp.d
    corp, conc = FAM['corp'], FAM['concrete']
    # ---- entrance plaza podium
    plaza_r = 6.4
    ring = [(CX + plaza_r * math.cos(a), CY + plaza_r * math.sin(a)) for a in [2 * math.pi * k / 16 for k in range(16)]]
    top = [(x, y, Z0) for x, y in ring]
    for k in range(16):
        a, b = ring[k], ring[(k + 1) % 16]
        q = [(a[0], a[1], 0), (b[0], b[1], 0), (b[0], b[1], Z0), (a[0], a[1], Z0)]
        dp.face(q, conc, ('plz', k), 1, 1, center=(CX, CY, Z0 / 2))
    facet(d, lambda u, v: cam.p(CX + plaza_r * v * math.cos(u * 2 * math.pi), CY + plaza_r * v * math.sin(u * 2 * math.pi), Z0),
          16, 3, lambda u, v, i, j, k, rc: tint(ramp(conc, BANDS[2] - 0.05 + rc.uniform(-0.04, 0.04)), 2), 'plz_top', 0.2,
          wrap_u=True)
    ink_poly(d, hull([cam.p(x, y, z) for x, y in ring for z in (0, Z0)]), 4.0, 'plz_ink')
    # lit entrance slot facing the boss node
    ea = math.atan2(6.9 - CY, 48.5 - CX)
    facet(d, lambda u, v: cam.p(CX + (RO + (plaza_r - RO) * v) * math.cos(ea - 0.22 + 0.44 * u),
                                CY + (RO + (plaza_r - RO) * v) * math.sin(ea - 0.22 + 0.44 * u), Z0 + 0.02),
          3, 2, lambda u, v, i, j, k, rc: ramp(NEON['cyan'], 0.55 + rc.uniform(-0.1, 0.15)), 'hq_entry', 0.2)
    # ---- strand segments
    n_seg = int(TURNS * SEG)
    dth = 2 * math.pi / SEG
    near, far = [], []
    view = (cam.sa, cam.ca)
    for s in range(2):
        for k in range(n_seg):
            t0, t1 = k * dth, (k + 1) * dth
            a0, a1 = t0 + s * math.pi, t1 + s * math.pi
            am = (a0 + a1) / 2
            zm = (z_at(t0) + z_at(t1)) / 2 + T / 2
            xm, ym = CX + (RI + RO) / 2 * math.cos(am), CY + (RI + RO) / 2 * math.sin(am)
            key = cam.depth(xm, ym) * cam.ce + zm * cam.se
            seg = (key, s, k, t0, t1, a0, a1)
            (near if math.cos(am) * view[0] + math.sin(am) * view[1] > 0 else far).append(seg)
    far.sort()
    near.sort()
    # bridges: evenly spaced heights, spanning the core along strand A's bearing at that height
    bridges = []
    # place them where the strands sit left/right of the viewer, so each bridge shows in the open gap
    # choose the bearing so the near-side band sits just below each bridge and the gap above it is open
    psi = math.atan2(cam.ca, cam.sa)
    open_off = (PITCH / 2 - T / 2 - 0.3) / PITCH * 2 * math.pi
    th = (psi - open_off) % math.pi
    m = 0
    while th < TURNS * 2 * math.pi - 0.3:
        zb = z_at(th) + T / 2 - 0.8
        bridges.append((th, zb, m))
        th += math.pi
        m += 1
    for seg in far:
        segment(dp, seg)
    for th, zb, m in bridges:
        bridge(dp, th, zb, m)
    for seg in near:
        segment(dp, seg)
    # crowns: masts on each strand top
    tops = []
    for s in range(2):
        a = TURNS * 2 * math.pi + s * math.pi
        x, y = CX + (RI + RO) / 2 * math.cos(a), CY + (RI + RO) / 2 * math.sin(a)
        zt = top_z()
        b0, t0 = cam.p(x, y, zt), cam.p(x, y, zt + 4.0)
        ink_line(d, b0, t0, 4.4, ('mast', s))
        line2(d, b0, t0, 1.8, ramp(FAM['soot'], 0.6))
        tri(d, [(t0[0] - 5, t0[1]), (t0[0] + 5, t0[1]), (t0[0], t0[1] - 9)], ramp(NEON['red'], 0.9))
        tops.append(t0)
    pts = [cam.p(CX + RO * math.cos(a), CY + RO * math.sin(a), z) for a in [k * 0.3 for k in range(21)] for z in (0, top_z() + 4)]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    dp.hq_bbox = (min(xs) - 60, min(ys) - 90, max(xs) + 60, max(ys) + 40)
    dp.hq_top = (sum(t[0] for t in tops) / 2, min(t[1] for t in tops))


def win_fac(stops, s, k, rows):
    def fac(base):
        def f(u, v, i, j, kk, rc):
            t = base + rc.uniform(-0.03, 0.03)
            if j % 2 == 1:   # window band
                if hsh(s, k, i, j, 5) < 0.12:
                    return ramp(NEON['sodium'], 0.42)
                return ramp(FAM['oily'], t - 0.14)
            return ramp(stops, t)
        return f
    return fac


def segment(dp, seg):
    key, s, k, t0, t1, a0, a1 = seg
    cam = dp.cam
    d = dp.d
    stops = FAM['corp'] if s == 0 else FAM['brick']
    zb0, zb1 = z_at(t0), z_at(t1)

    def P(r, a, z):
        return (CX + r * math.cos(a), CY + r * math.sin(a), z)
    center = (CX + (RI + RO) / 2 * math.cos((a0 + a1) / 2), CY + (RI + RO) / 2 * math.sin((a0 + a1) / 2),
              (zb0 + zb1) / 2 + T / 2)
    rows = int(round(T / FLOOR)) * 2
    outer = [P(RO, a0, zb0), P(RO, a1, zb1), P(RO, a1, zb1 + T), P(RO, a0, zb0 + T)]
    inner = [P(RI, a1, zb1), P(RI, a0, zb0), P(RI, a0, zb0 + T), P(RI, a1, zb1 + T)]
    topq = [P(RI, a0, zb0 + T), P(RO, a0, zb0 + T), P(RO, a1, zb1 + T), P(RI, a1, zb1 + T)]
    vis_o = dp.face(outer, stops, ('ho', s, k), 2, rows, center=(CX, CY, center[2]), colfac=win_fac(stops, s, k, rows))
    vis_i = dp.face(inner, stops, ('hi', s, k), 1, rows // 2, normal=None,
                    center=(CX + 50 * math.cos((a0 + a1) / 2), CY + 50 * math.sin((a0 + a1) / 2), center[2]),
                    colfac=win_fac(stops, s, k + 99, rows // 2))
    dp.face(topq, stops, ('ht', s, k), 2, 1, center=(center[0], center[1], center[2] - 5), gv=-0.1)
    # balconies (floor lips) and neon strip on the outer face
    if vis_o:
        for f in range(1, int(round(T / FLOOR))):
            z0, z1 = zb0 + f * FLOOR, zb1 + f * FLOOR
            pa, pb = cam.p(*P(RO + 0.08, a0, z0)), cam.p(*P(RO + 0.08, a1, z1))
            line2(d, (pa[0], pa[1] + 1.6), (pb[0], pb[1] + 1.6), 1.8, hexc('#1c1816'))
            line2(d, pa, pb, 1.6, BEVEL)
        za, zc = zb0 + T - 0.35, zb1 + T - 0.35
        line2(d, cam.p(*P(RO + 0.05, a0, za)), cam.p(*P(RO + 0.05, a1, zc)), 3.4, ramp(STRIPS[s], 0.8))
        ink_line(d, cam.p(*outer[0]), cam.p(*outer[1]), 3.6, ('hob', s, k))
        if k % 3 == 0:
            ink_line(d, cam.p(*outer[0]), cam.p(*outer[3]), 1.4, ('hos', s, k))
    if vis_i:
        ink_line(d, cam.p(*inner[0]), cam.p(*inner[1]), 2.4, ('hib', s, k))
    # top edges (outer and inner) — continuous spiral ink lines
    ink_line(d, cam.p(*topq[1]), cam.p(*topq[2]), 3.6, ('hto', s, k))
    ink_line(d, cam.p(*topq[0]), cam.p(*topq[3]), 2.6, ('hti', s, k))
    to = cam.p(*topq[1]), cam.p(*topq[2])
    line2(d, (to[0][0], to[0][1] + 3), (to[1][0], to[1][1] + 3), 1.6, BEVEL)
    if k == 0:   # start cap of each strand
        cap = [P(RI, a0, zb0), P(RO, a0, zb0), P(RO, a0, zb0 + T), P(RI, a0, zb0 + T)]
        dp.face(cap, stops, ('hcap', s), 2, 2, center=center)
        ink_poly(d, [cam.p(*c) for c in cap], 3.0, ('hcapi', s))
    if k == int(TURNS * SEG) - 1:
        cap = [P(RI, a1, zb1), P(RO, a1, zb1), P(RO, a1, zb1 + T), P(RI, a1, zb1 + T)]
        dp.face(cap, stops, ('hcap2', s), 2, 2, center=center)
        ink_poly(d, [cam.p(*c) for c in cap], 3.0, ('hcapj', s))


def bridge(dp, th, zb, m):
    """Enclosed skybridge across the hollow core, from strand A's inner face to strand B's."""
    conc = FAM['concrete']

    def fac(base):
        def f(u, v, i, j, k, rc):
            t = base + rc.uniform(-0.03, 0.03)
            if j == 1:
                return ramp(NEON['cyan'], 0.55 + rc.uniform(-0.1, 0.1)) if (i % 2 == 0) else ramp(conc, t - 0.05)
            return ramp(conc, t)
        return f
    dp.oprism((CX, CY), th, 2.4, 2 * RI + 0.6, zb, zb + 1.6, conc, ('hbr', m), colfac=fac, ink=3.0, nu=4, nv=3)
