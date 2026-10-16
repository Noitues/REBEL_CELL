"""City-all-corps (exec'd by city_build.py, same namespace): the city ring, Tethys' sea / seawall / drowned quarter,
the Aurelian aqueduct. Landmarks are in landmarks.py; materials, lights and the render in city_render.py."""

# ------------------------------------------------------------------ the city ring beyond the map (hq_kit.city_ring rules)
RR = random.Random(CP.SEEDS["ring"])
L1_EDGE = 92.0            # inside this L1 radius (lots) the map is always the game's own layout
MAP_CELLS = set()          # the map's own lot cells (street tiles + building footprints): the ring never overlaps them
for _t in O["tiles"]:
    MAP_CELLS.add((_t["i"], _t["j"]))
for _b in O["buildings"]:
    for _p in _b["q"]:
        MAP_CELLS.add((int(math.floor(_p[0])), int(math.floor(_p[1]))))
RING_COLS = [(1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)]
RING_NEON = [(1.0, 0.3, 0.7), (0.3, 0.85, 1.0), (0.7, 0.45, 1.0), (1.0, 0.6, 0.2)]
n_ring = 0
for gx in range(-246, 258, 3):        # 3-lot blocks: 2 lots of buildings + a 1-lot street (the game's grid continues)
    for gy in range(-246, 258, 3):
        for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
            lx, ly = gx + ox + 0.5, gy + oy + 0.5
            far = abs(lx - CX) + abs(ly - CY) - L1_EDGE
            if far <= 0 or (int(math.floor(lx)), int(math.floor(ly))) in WET_CELLS or any((int(math.floor(lx)) + di, int(math.floor(ly)) + dj) in MAP_CELLS for di in (-1, 0, 1) for dj in (-1, 0, 1)):
                continue
            a_, b_ = ((lx - CX) - (ly - CY)) / R2, -((lx - CX) + (ly - CY)) / R2
            if b_ > bwall(a_) - 1.2 or abs(a_) > 200 or b_ < -200:
                continue
            if RR.random() < 0.12:
                continue
            cx_, cy_ = W((lx, ly))
            h = min(60.0, RR.lognormvariate(math.log(6.0 + 0.03 * far), 0.6))
            w_ = RR.uniform(0.62, 0.9) * U / 2
            d_ = RR.uniform(0.62, 0.9) * U / 2
            pts = [(cx_ - w_, cy_ - d_), (cx_ + w_, cy_ - d_), (cx_ + w_, cy_ + d_), (cx_ - w_, cy_ + d_)]
            col = (0.22, 0.21, 0.26) if RR.random() < 0.7 else (0.27, 0.22, 0.24)
            prism(SURF, pts, 0, h, col, wc=RR.choice(RING_COLS), wl=0.09 / (1.0 + far / 50.0), wm=0, bid=RR.random())
            if RR.random() < CP.OUTLINE["ring_trim_p"]:
                c2 = RR.choice(RING_NEON)
                for i in range(4):
                    bar(NEON, (pts[i][0], pts[i][1], h + 0.08), (pts[(i + 1) % 4][0], pts[(i + 1) % 4][1], h + 0.08), 0.2, c2)
            if h > 22 and RR.random() < 0.4:
                box(NEON, cx_ - 0.3, cy_ - 0.3, h, cx_ + 0.3, cy_ + 0.3, h + 0.5, (1.0, 0.06, 0.04))
            ROOFS.append((cx_, cy_, h, 800000 + gx * 1000 + gy, "ring", 0))
            n_ring += 1
# the ring's streets: every block edge outside the map carries a dim lane glow (the street-light rivers, always on)
RL = random.Random(CP.SEEDS["ring"] + 1)
for gx in range(-246, 258, 3):
    for gy in range(-246, 258, 3):
        for (p0, p1) in (((gx + 2, gy), (gx + 2, gy + 3)), ((gx, gy + 2), (gx + 3, gy + 2))):
            mx_, my_ = (p0[0] + p1[0]) / 2 + 0.5 * (p0[0] == p1[0]), (p0[1] + p1[1]) / 2 + 0.5 * (p0[1] == p1[1])
            far = abs(mx_ - CX) + abs(my_ - CY) - L1_EDGE
            a_, b_ = ((mx_ - CX) - (my_ - CY)) / R2, -((mx_ - CX) + (my_ - CY)) / R2
            if far <= 2 or b_ > bwall(a_) - 1.0 or abs(a_) > 200 or b_ < -200:
                continue
            if (int(math.floor(mx_)), int(math.floor(my_))) in MAP_CELLS or (int(math.floor(mx_)), int(math.floor(my_))) in WET_CELLS:
                continue
            o = (0.5, 0.0) if p0[0] == p1[0] else (0.0, 0.5)
            q0, q1 = W((p0[0] + o[0], p0[1] + o[1])), W((p1[0] + o[0], p1[1] + o[1]))
            c = RL.choice([(1.0, 0.62, 0.3), (1.0, 0.7, 0.4), (0.5, 0.75, 1.0), (1.0, 0.4, 0.7)])
            major = (p0[0] % 6 == 2) if p0[0] == p1[0] else (p0[1] % 6 == 2)     # every other street is a main road
            strip(NEON, q0, q1, 0.5, 0.05, sc(c, RL.uniform(0.12, 0.26) * (CP.OUTLINE["ring_major_k"] if major else CP.OUTLINE["ring_minor_k"]) / (1.0 + far / 60.0)))
print("RING", n_ring, "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ Tethys: the drowned quarter's seabed + levee
TE = DIST["tethys"]
HULL = (0.16, 0.19, 0.24)
CONC = (0.17, 0.17, 0.19)          # dark wet concrete (art review 6)


def cell_sub(i, j):
    return WET_CELLS.get((i, j))


def corner_sub(i, j):
    """seabed depth at the lot corner (i, j): the mean of the wet cells around it (dry neighbours pull to the levee)."""
    v = [cell_sub(i - di, j - dj) for di in (0, 1) for dj in (0, 1)]
    v = [x for x in v if x is not None]
    return sum(v) / len(v)


for (i, j), s in sorted(WET_CELLS.items()):
    cs = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
    SEABED.face([(*W(c), -corner_sub(*c)) for c in cs], (0.12, 0.13, 0.14), None, wet=1)
    WATER.face([(*W(c), ZW) for c in cs], (0, 0, 0))
    # the levee: a wall on every wet cell edge that faces a dry cell (on land; the sea side has the seawall)
    for (di, dj, e0, e1) in ((1, 0, (i + 1, j), (i + 1, j + 1)), (-1, 0, (i, j + 1), (i, j)), (0, 1, (i + 1, j + 1), (i, j + 1)),
                             (0, -1, (i, j), (i + 1, j))):
        if (i + di, j + dj) in WET_CELLS:
            continue
        a_, b_ = ((i + di + 0.5 - CX) - (j + dj + 0.5 - CY)) / R2, -((i + di + 0.5 - CX) + (j + dj + 0.5 - CY)) / R2
        if b_ > bwall(a_) - 0.5:
            continue
        p0, p1 = W(e0), W(e1)
        z_lo = -max(corner_sub(*e0), corner_sub(*e1)) - 0.5
        uv, L = quad_uv(p0, p1, z_lo, WAT["levee_h"])
        SURF.face([(p0[0], p0[1], z_lo), (p1[0], p1[1], z_lo), (p1[0], p1[1], WAT["levee_h"]), (p0[0], p0[1], WAT["levee_h"])],
                  CONC, uv, wet=1)
        SURF.face([(p0[0], p0[1], WAT["levee_h"]), (p1[0], p1[1], WAT["levee_h"]), (p1[0], p1[1], WAT["levee_h"] - 0.01),
                   (p0[0], p0[1], WAT["levee_h"] - 0.01)], CONC)
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        if (i + j) % 2 == 0:
            box(NEON, mid[0] - 0.2, mid[1] - 0.2, WAT["levee_h"], mid[0] + 0.2, mid[1] + 0.2, WAT["levee_h"] + 0.35, (1.0, 0.85, 0.55))
# drowned streets: dark lane lines on the seabed (the old road markings), caustics do the rest
for t in O["tiles"]:
    if not t["wet"] or not t["ab"]:
        continue
    a, b = W(t["ab"][0]), W(t["ab"][1])
    strip(SEABED, a, b, 0.3, -t["sub"] + 0.05, (0.32, 0.33, 0.30), wet=1)

# ------------------------------------------------------------------ the sea: past the curved wall to the horizon
s0, s1 = WAT["sea_bed"]
RSEA = random.Random(CP.SEEDS["sea"])
WALL_W = 7.0 / U                       # the wall's thickness in lots
N_A, N_B = 120, 30
A_SPAN = 1600.0                        # lots across
B_SPAN = WAT["sea_out"] / U


def sea_v(a, t):
    bb = bwall(a) + WALL_W + B_SPAN * t ** 1.8
    zb = -(s0 + (s1 - s0) * min(1.0, (bb - bwall(a)) / 60.0))
    return bb, zb


for ia in range(N_A):
    for ib in range(N_B):
        a0 = -A_SPAN / 2 + A_SPAN * ia / N_A
        a1 = -A_SPAN / 2 + A_SPAN * (ia + 1) / N_A
        t0, t1 = ib / N_B, (ib + 1) / N_B
        vs = [(a0, t0), (a1, t0), (a1, t1), (a0, t1)]
        pb = [(a_, *sea_v(a_, t_)) for (a_, t_) in vs]
        SEABED.face([(*w_ab(a_, bb), zb) for (a_, bb, zb) in pb], (0.17, 0.19, 0.20), None, wet=1)
        WATER.face([(*w_ab(a_, bb), ZW) for (a_, bb, zb) in pb], (0, 0, 0))
# drowned ruins in the bay (the old shoreline the sea took, inside the wall) and a few on the shelf outside
for k in range(260):
    a_ = RSEA.uniform(-110, 110)
    if bwall(a_) - B_COAST < 3.0 and RSEA.random() < 0.7:
        continue
    inside = RSEA.random() < 0.8 and bwall(a_) - B_COAST > 3.0
    b_ = RSEA.uniform(B_COAST + 1.0, bwall(a_) - 1.2) if inside else bwall(a_) + WALL_W + RSEA.uniform(2.0, 20.0)
    x, y = w_ab(a_, b_)
    cell = (int(math.floor(x / U + CX)), int(math.floor(-y / U + CY)))
    if inside and cell not in WET_CELLS:
        continue
    zb = -WET_CELLS[cell] if inside else -(s0 + (s1 - s0) * min(1.0, (b_ - bwall(a_)) / 60.0))
    h = RSEA.uniform(8, 30) if inside else RSEA.uniform(4, 24)
    w_ = RSEA.uniform(2.5, 5.5)
    pts = [(x - w_, y - w_), (x + w_, y - w_), (x + w_, y + w_), (x - w_, y + w_)]
    prism(SURF, pts, zb, min(zb + h, ZW - 0.6), DIST["tethys"]["mat"][k % 3], ts=RSEA.uniform(0.85, 1.0), wc=(1.0, 0.91, 0.72),
          wl=0.40 if inside else 0.04, wm=2, bid=RSEA.random(), wet=1)

# ------------------------------------------------------------------ the curved seawall + pump towers along it
WALL_Z0 = -max(WET_CELLS.values()) - 12.0
A0, A1, DA = -190.0, 190.0, 2.5
pts_in = [w_ab(a, bwall(a)) for a in [A0 + DA * k for k in range(int((A1 - A0) / DA) + 1)]]
pts_out = [w_ab(a, bwall(a) + WALL_W) for a in [A0 + DA * k for k in range(int((A1 - A0) / DA) + 1)]]
for k in range(len(pts_in) - 1):
    q = [pts_in[k], pts_in[k + 1], pts_out[k + 1], pts_out[k]]
    prism(SURF, q, WALL_Z0, WAT["wall_h"], (0.30, 0.31, 0.35), wc=(1.0, 0.91, 0.72), wl=0.05, wm=2, bid=0.3, wet=1,
          top_col=(0.24, 0.24, 0.28))
# walkway lamps every 6 BU along the crest, the photophore + hue lines on the sea face, pumps every 66 BU of arc
arc = 0.0
next_lamp, next_pump = 0.0, 0.0
PUMPS = []
for k in range(len(pts_in) - 1):
    p0, p1 = pts_in[k], pts_in[k + 1]
    o0, o1 = pts_out[k], pts_out[k + 1]
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    bar(NEON, (o0[0], o0[1], ZW + 1.6), (o1[0], o1[1], ZW + 1.6), 0.3, TE["sec"])
    bar(NEON, (o0[0], o0[1], WAT["wall_h"] - 0.6), (o1[0], o1[1], WAT["wall_h"] - 0.6), 0.22, TE["hue"])
    while next_lamp < arc + L:
        t = (next_lamp - arc) / L
        x = p0[0] + (p1[0] - p0[0]) * t + (o0[0] - p0[0]) * 0.15
        y = p0[1] + (p1[1] - p0[1]) * t + (o0[1] - p0[1]) * 0.15
        box(NEON, x - 0.2, y - 0.2, WAT["wall_h"], x + 0.2, y + 0.2, WAT["wall_h"] + 0.4, (1.0, 0.86, 0.6))
        next_lamp += 6.0
    while next_pump < arc + L:
        t = (next_pump - arc) / L
        x = p0[0] + (p1[0] - p0[0]) * t + (o0[0] - p0[0]) * 0.5
        y = p0[1] + (p1[1] - p0[1]) * t + (o0[1] - p0[1]) * 0.5
        kk = len(PUMPS)
        ht = 20.0 + 6.0 * ((kk * 7) % 3)
        cyl(SURF, x, y, WAT["wall_h"], WAT["wall_h"] + ht, 3.2, 12, HULL, wc=(1.0, 0.91, 0.72), wl=0.2, wm=2, bid=kk / 50.0)
        for zr in (0.3, 0.6, 0.9):
            ring_line(NEON, x, y, WAT["wall_h"] + ht * zr, 3.3, 0.35, TE["hue"], n=12)
        cyl(SURF, x, y, WAT["wall_h"] + ht, WAT["wall_h"] + ht + 1.2, 3.8, 12, HULL)
        box(NEON, x - 0.4, y - 0.4, WAT["wall_h"] + ht + 1.2, x + 0.4, y + 0.4, WAT["wall_h"] + ht + 2.0, (0.78, 0.15, 0.3))
        nx_o, ny_o = (o0[0] - p0[0]), (o0[1] - p0[1])
        bar(SURF, (x + nx_o * 0.6, y + ny_o * 0.6, -s0), (x + nx_o * 0.6, y + ny_o * 0.6, WAT["wall_h"]), 2.0, HULL, wet=1)
        PUMPS.append((x, y, WAT["wall_h"] + ht + 2.0))
        next_pump += 66.0
    arc += L
print("WATER built %.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ the Aurelian aqueduct (two arch tiers + the data channel)
AU = DIST["aurelian"]
TRAV = AU["mat"][0]
aq0, aq1 = W(O["aqueduct"][0]), W(O["aqueduct"][1])
Laq = math.hypot(aq1[0] - aq0[0], aq1[1] - aq0[1])
ux, uy = (aq1[0] - aq0[0]) / Laq, (aq1[1] - aq0[1]) / Laq
nx_, ny_ = -uy, ux
P1, P2, H1, H2 = 7.0, 3.5, 12.0, 6.5


def aq_at(s, off=0.0):
    return (aq0[0] + ux * s + nx_ * off, aq0[1] + uy * s + ny_ * off)


k = 0
s = 0.0
while s <= Laq + 0.01:
    p = aq_at(s)
    box(SURF, p[0] - 1.1, p[1] - 1.1, 0, p[0] + 1.1, p[1] + 1.1, H1, TRAV, wc=(1.0, 0.8, 0.5), wl=0.0, wm=3, bid=0.5)
    ROOFS.append((p[0], p[1], H1 + H2, 700000 + k, "aqueduct", 0))
    s += P1
    k += 1
for side in (-1.1, 1.1):           # the arch spandrels: a slab over each bay, curved underside by steps
    for kk in range(int(Laq / P1)):
        sa, sb = kk * P1 + 1.1, (kk + 1) * P1 - 1.1
        steps = 6
        for m in range(steps):
            t0, t1 = m / steps, (m + 1) / steps
            za = H1 - 2.6 * math.sin(math.pi * t0)
            zb = H1 - 2.6 * math.sin(math.pi * t1)
            pa, pb = aq_at(sa + (sb - sa) * t0, side), aq_at(sa + (sb - sa) * t1, side)
            SURF.face([(pa[0], pa[1], za), (pb[0], pb[1], zb), (pb[0], pb[1], H1 + 1.0), (pa[0], pa[1], H1 + 1.0)], TRAV)
box_q = [aq_at(0, -1.2), aq_at(Laq, -1.2), aq_at(Laq, 1.2), aq_at(0, 1.2)]
prism(SURF, box_q, H1, H1 + 1.0, sc(TRAV, 0.95))
s = P2 / 2
while s < Laq:                       # the upper tier: small piers
    p = aq_at(s)
    box(SURF, p[0] - 0.6, p[1] - 0.6, H1 + 1.0, p[0] + 0.6, p[1] + 0.6, H1 + H2, TRAV)
    s += P2
prism(SURF, [aq_at(0, -1.4), aq_at(Laq, -1.4), aq_at(Laq, 1.4), aq_at(0, 1.4)], H1 + H2, H1 + H2 + 1.2, sc(TRAV, 0.95))
# the data channel on top: a verdigris stream with seeded packets (gilt)
strip(NEON, aq_at(0), aq_at(Laq), 1.3, H1 + H2 + 1.25, sc(AU["sec"], 0.9))   # gilt data stream (verdigris only on domes)
RP = random.Random(6107)
for kk in range(int(Laq / 5)):
    s = RP.uniform(0, Laq - 2)
    strip(NEON, aq_at(s), aq_at(s + RP.uniform(0.8, 2.2)), 1.5, H1 + H2 + 1.3, (1.0, 0.85, 0.5))
for side in (-1.45, 1.45):
    bar(NEON, (*aq_at(0, side), H1 + H2 + 1.2), (*aq_at(Laq, side), H1 + H2 + 1.2), 0.16, AU["sec"])
print("AQUEDUCT %.0f BU %.1fs" % (Laq, time.time() - T0), flush=True)

# ------------------------------------------------------------------ the Meridian freight rail (zoning L4): gate -> viaduct -> port
RA = CP.RAIL
ME = DIST["meridian"]
_mx, _my = W(O["hq"]["meridian"])
_S = RA["wall_s"]                                               # the container wall line (the fortress S)
rpts = [(_mx + RA["gate_u"], _my + _S - 2.4)] + [W(p) for p in O["rail"]]     # from inside the north gate
_a_end, _b_end = ab_w(*rpts[-1])
rpts.append(w_ab(_a_end, bwall(_a_end) + 0.6))                # the jetty out over the bay water to the seawall port
# resample at 3.5 BU, with the arc length
RP = [(rpts[0][0], rpts[0][1], 0.0)]
for k in range(len(rpts) - 1):
    (x0, y0), (x1, y1) = rpts[k], rpts[k + 1]
    L = math.hypot(x1 - x0, y1 - y0)
    n_ = max(1, int(L / 3.5))
    for m in range(1, n_ + 1):
        t = m / n_
        RP.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, RP[-1][2] + L / n_))
RAIL_LEN = RP[-1][2]


def rail_z(s):
    """up from the yard (0.7) to the deck (deck_z) over ramp BU, down to the terminal on the seawall at the end."""
    t = min(1.0, max(0.0, (s - 4.0) / RA["ramp"]))
    up = 0.7 + (RA["deck_z"] - 0.7) * t * t * (3 - 2 * t)
    t2 = min(1.0, max(0.0, (RAIL_LEN - s) / RA["end_ramp"]))
    zt = WAT["wall_h"] + 0.7
    return min(up, zt + (RA["deck_z"] - zt) * t2 * t2 * (3 - 2 * t2))


def ground_at(x, y):
    c = (int(math.floor(x / U + CX)), int(math.floor(-y / U + CY)))
    return -WET_CELLS[c] if c in WET_CELLS else 0.0


DECK = (0.30, 0.27, 0.25)
next_pier, next_sig = 8.0, 20.0
for k in range(len(RP) - 1):
    x0, y0, s0_ = RP[k]
    x1, y1, s1_ = RP[k + 1]
    z0_, z1_ = rail_z(s0_), rail_z(s1_)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * 1.4, dx / L * 1.4
    # the deck (a sloped slab), the two rails, the orange rail glow along both edges
    SURF.face([(x0 - nx, y0 - ny, z0_), (x1 - nx, y1 - ny, z1_), (x1 + nx, y1 + ny, z1_), (x0 + nx, y0 + ny, z0_)], DECK)
    for side in (-1, 1):
        SURF.face([(x0 + side * nx, y0 + side * ny, z0_ - 0.9), (x1 + side * nx, y1 + side * ny, z1_ - 0.9),
                   (x1 + side * nx, y1 + side * ny, z1_), (x0 + side * nx, y0 + side * ny, z0_)], sc(DECK, 0.8))
        bar(SURF, (x0 + side * nx * 0.4, y0 + side * ny * 0.4, z0_ + 0.12), (x1 + side * nx * 0.4, y1 + side * ny * 0.4, z1_ + 0.12),
            0.12, (0.55, 0.55, 0.6))
        if s0_ > 6.0:
            bar(NEON, (x0 + side * nx * 1.02, y0 + side * ny * 1.02, z0_ - 0.25), (x1 + side * nx * 1.02, y1 + side * ny * 1.02, z1_ - 0.25),
                0.12, sc((1.0, 0.5, 0.12), 0.55))
    while next_pier < s1_:
        t = (next_pier - s0_) / max(1e-6, s1_ - s0_)
        px, py, pz = x0 + dx * t, y0 + dy * t, z0_ + (z1_ - z0_) * t
        if pz > 2.0:
            gz = ground_at(px, py)
            box(SURF, px - 0.6, py - 0.6, gz, px + 0.6, py + 0.6, pz - 0.9, sc(DECK, 0.9), wet=1 if gz < 0 else 0)
        next_pier += RA["pier_step"]
    while next_sig < s1_:                                     # orange signal lamps on short masts
        t = (next_sig - s0_) / max(1e-6, s1_ - s0_)
        px, py, pz = x0 + dx * t + nx * 1.1, y0 + dy * t + ny * 1.1, z0_ + (z1_ - z0_) * t
        bar(SURF, (px, py, pz), (px, py, pz + 2.2), 0.14, (0.3, 0.3, 0.32))
        box(NEON, px - 0.25, py - 0.25, pz + 2.2, px + 0.25, py + 0.25, pz + 2.7, (1.0, 0.45, 0.08))
        next_sig += RA["signal_step"]


def rail_at(s):
    for k in range(len(RP) - 1):
        if RP[k][2] <= s <= RP[k + 1][2]:
            t = (s - RP[k][2]) / max(1e-6, RP[k + 1][2] - RP[k][2])
            return (RP[k][0] + (RP[k + 1][0] - RP[k][0]) * t, RP[k][1] + (RP[k + 1][1] - RP[k][1]) * t, rail_z(s))
    return RP[-1][0], RP[-1][1], rail_z(s)


# two moving trains as light streaks (long exposure): a lit head, a warm trail; one with its container wagons
for (sc0, ln, wagons) in ((0.30, 34.0, True), (0.72, 26.0, False)):
    s_head = RAIL_LEN * sc0
    m = 24
    for kk in range(m):
        sa, sb = s_head - ln * kk / m, s_head - ln * (kk + 1) / m
        pa, pb = rail_at(sa), rail_at(sb)
        k_ = (1.0 - kk / m) ** 1.5
        bar(STREAK, (pa[0], pa[1], pa[2] + 0.6), (pb[0], pb[1], pb[2] + 0.6), 0.35, sc((1.0, 0.75, 0.42), 0.4 + 0.8 * k_))
    ph = rail_at(s_head)
    box(STREAK, ph[0] - 0.4, ph[1] - 0.4, ph[2] + 0.3, ph[0] + 0.4, ph[1] + 0.4, ph[2] + 1.1, (1.0, 0.95, 0.85))
    if wagons:
        CCW = [(0.62, 0.24, 0.08), (0.12, 0.34, 0.36), (0.55, 0.12, 0.08), (0.75, 0.42, 0.10)]
        for kk in range(6):
            s1w, s2w = s_head - 1.0 - kk * 3.2, s_head - 1.0 - kk * 3.2 - 2.8
            pa, pb = rail_at(s1w), rail_at(s2w)
            bar(SURF, (pa[0], pa[1], pa[2] + 1.0), (pb[0], pb[1], pb[2] + 1.0), 1.4, CCW[kk % 4])
# the port terminal on the seawall at the jetty's end: a container gantry over stacks, orange work lamps
_ex, _ey, _ = RP[-1][0], RP[-1][1], 0
_tz = WAT["wall_h"]
for (ox, oy) in ((-6, -6), (6, -6), (6, 6), (-6, 6)):
    bar(SURF, (_ex + ox, _ey + oy, _tz), (_ex + ox, _ey + oy, _tz + 16), 0.8, (0.95, 0.42, 0.08))
bar(SURF, (_ex - 6, _ey - 6, _tz + 16), (_ex + 6, _ey - 6, _tz + 16), 1.0, (0.95, 0.42, 0.08))
bar(SURF, (_ex - 6, _ey + 6, _tz + 16), (_ex + 6, _ey + 6, _tz + 16), 1.0, (0.95, 0.42, 0.08))
RPT = random.Random(6108)
for kk in range(10):
    bx_, by_ = _ex + RPT.uniform(-5, 4), _ey + RPT.uniform(-5, 4)
    lv = RPT.randint(0, 2)
    box(SURF, bx_, by_, _tz + lv * 0.95, bx_ + 2.4, by_ + 0.9, _tz + (lv + 1) * 0.95, RPT.choice(((0.62, 0.24, 0.08), (0.12, 0.34, 0.36), (0.55, 0.12, 0.08))))
for (ox, oy) in ((-6, -6), (6, 6)):
    box(NEON, _ex + ox - 0.4, _ey + oy - 0.4, _tz + 16.5, _ex + ox + 0.4, _ey + oy + 0.4, _tz + 17.1, (1.0, 0.55, 0.15))
# the polyline for the HQ kit (source of truth: this street-tile search): world BU, the corners with their deck z
_rc = [rpts[0]] + [W(p) for p in O["rail"]] + [rpts[-1]]
_rs, _acc = [0.0], 0.0
for _k in range(1, len(_rc)):
    _acc += math.hypot(_rc[_k][0] - _rc[_k - 1][0], _rc[_k][1] - _rc[_k - 1][1])
    _rs.append(_acc)
json.dump(dict(note="Meridian freight line, city_all_corps zoning L4 (street-tile BFS; source of truth for city and HQ). "
               "World BU (x east, y north, z up); origin = the city centre lot; points run gate -> seawall terminal.",
               hq_centre=[_mx, _my], gate=dict(wall="north", centre=[_mx + RA["gate_u"], _my + _S], width=6.0, height=5.2),
               deck_z=RA["deck_z"], side_cap=RA["side_cap"], ramp=RA["ramp"], end_ramp=RA["end_ramp"], length=RAIL_LEN,
               points=[[round(p[0], 3), round(p[1], 3), round(rail_z(s), 3)] for p, s in zip(_rc, _rs)],
               corners_lots=O["rail"]), open(RA["rail_json"], "w"), indent=1)
print("RAIL %.0f BU, %d corners -> %s" % (RAIL_LEN, len(O["rail"]), RA["rail_json"]), flush=True)
