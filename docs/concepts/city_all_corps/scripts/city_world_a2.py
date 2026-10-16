"""City-all-corps round 4 (exec'd by city_build.py in place of city_world.py when the layout is A2): the ground, parks, the
suburbs (the districts' buildings come from zoning_a2.py), the industry / informal housing / cemetery cells, the street
glow, arterial traffic, the sea and sea bed, the drowned quarter behind its dams, dams / barrier / sea walls, the corporate
walls and the landmark glyphs.  Roads, rails and the port are in city_transit_a2.py.

Cell classes (a2_fields.npz): 0 water  1 drowned  2 corridor  3 park  4 plaza  5 cemetery  6 industry  7 informal  8 airport
9 port  10 spaceport  11 district  12 suburb  13 outside the outer ring.
"""
import numpy as _np
FLD = RU.a2_fields()
CLS, DISTN = FLD["cls"], FLD["dist"]
GI0, GJ0, GN = FLD["i0"], FLD["j0"], FLD["n"]
DLAND = _np.load(os.path.join(CP.SCR, "a2_dland.npy"))
A2P = CP.A2
A2D = O["a2"]
CORE_PER, SUB_PER = A2P["core_period"], A2P["sub_period"]
L1_EDGE = 0.0
RR = random.Random(CP.SEEDS["ring"])
PORT_ = None


def cls_at(ci, cj):
    return int(CLS[min(max(cj - GJ0, 0), GN - 1), min(max(ci - GI0, 0), GN - 1)])


def dland_at(ci, cj):
    return float(DLAND[min(max(cj - GJ0, 0), GN - 1), min(max(ci - GI0, 0), GN - 1)])


def ground_at(x, y):
    """sea / lagoon floor z at a world point (the street is 0)."""
    c = (int(math.floor(x / U + CX)), int(math.floor(-y / U + CY)))
    if c in WET_CELLS:
        return -WET_CELLS[c]
    if cls_at(*c) == 0:
        s0_, s1_ = WAT["sea_bed"]
        return -(s0_ + (s1_ - s0_) * min(1.0, dland_at(*c) / 25.0))
    return 0.0


def cell_w(ci, cj):
    """the lot cell's world rectangle."""
    (x0, y0), (x1, y1) = W((ci, cj)), W((ci + 1, cj + 1))
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


# ------------------------------------------------------------------ the ground (land cells in runs; class colours on top)
GM = 170
GCOL = (0.075, 0.075, 0.08) if DAYM else (0.12, 0.12, 0.15)
CLS_COL = {3: PK["lawn"], 4: PK["paved"], 5: sc(PK["lawn"], 0.55), 6: (0.075, 0.075, 0.085), 7: (0.07, 0.065, 0.06), 8: (0.10, 0.10, 0.11),
           9: (0.12, 0.115, 0.11), 10: (0.14, 0.135, 0.13)}
if not DAYM:
    CLS_COL = {3: sc(PK["lawn"], 0.8), 4: (0.13, 0.125, 0.15), 5: sc(PK["lawn"], 0.5), 6: (0.09, 0.09, 0.11), 7: (0.09, 0.08, 0.08),
               8: (0.12, 0.12, 0.14), 9: (0.13, 0.125, 0.12), 10: (0.15, 0.145, 0.14)}
for cj in range(GJ0 - GM, GJ0 + GN + GM):
    run, runc = None, None
    for ci in range(GI0 - GM, GI0 + GN + GM + 1):
        c_ = cls_at(ci, cj) if ci < GI0 + GN + GM else 0
        landc = c_ not in (0, 1)
        if landc and run is None:
            run = ci
        elif not landc and run is not None:
            x0_, y0_, x1_, y1_ = cell_w(run, cj)[0], cell_w(run, cj)[1], cell_w(ci - 1, cj)[2], cell_w(ci - 1, cj)[3]
            GROUND.face([(x0_, y0_, -0.03), (x1_, y0_, -0.03), (x1_, y1_, -0.03), (x0_, y1_, -0.03)], GCOL)
            run = None
    run, runc = None, None
    for ci in range(GI0, GI0 + GN + 1):                      # class colours (runs of one class)
        c_ = cls_at(ci, cj) if ci < GI0 + GN else -1
        if c_ != runc:
            if run is not None and runc in CLS_COL:
                xa, ya, _, _ = cell_w(run, cj)
                _, _, xb, yb = cell_w(ci - 1, cj)
                GROUND.face([(xa, ya, 0.01), (xb, ya, 0.01), (xb, yb, 0.01), (xa, yb, 0.01)], CLS_COL[runc])
            run, runc = ci, c_
print("GROUND %.1fs" % (time.time() - T0), flush=True)


# ------------------------------------------------------------------ parks: tree clumps on the park cells
def park_trees(x0, y0, x1, y1, rr, n_clump, n_tree):
    for _ in range(n_clump):
        cx_, cy_ = rr.uniform(x0 + 1.0, x1 - 1.0), rr.uniform(y0 + 1.0, y1 - 1.0)
        for _ in range(rr.randint(*n_tree)):
            r_ = rr.uniform(*PK["r"]) * 1.15
            tx, ty = cx_ + rr.uniform(-2.0, 2.0), cy_ + rr.uniform(-2.0, 2.0)
            bar(SURF, (tx, ty, 0.0), (tx, ty, r_ * 1.1), 0.22, (0.16, 0.12, 0.09))
            dome(SMOOTH, tx, ty, r_ * 1.6, r_, sc(rr.choice(PK["tree_cols"]), rr.uniform(0.8, 1.15)), n=7, rings=2, hemi=False)


n_tree = 0
for cj in range(GJ0, GJ0 + GN):
    for ci in range(GI0, GI0 + GN):
        c_ = cls_at(ci, cj)
        if c_ == 3 and RU._hash01(7740, ci, cj) < 0.55:
            x0_, y0_, x1_, y1_ = cell_w(ci, cj)
            park_trees(x0_, y0_, x1_, y1_, random.Random(7741 * 100003 + ci * 1009 + cj), 2, (3, 5))
            n_tree += 1
        elif c_ == 4 and RU._hash01(7742, ci, cj) < 0.3:
            x0_, y0_, x1_, y1_ = cell_w(ci, cj)
            park_trees(x0_, y0_, x1_, y1_, random.Random(7743 * 100003 + ci * 1009 + cj), 1, (2, 3))
print("PARKS cells", n_tree, "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ the suburbs (ring style, 3-cell blocks), industry, informal housing
RING_COLS = [(1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)]
RING_NEON = [(1.0, 0.3, 0.7), (0.3, 0.85, 1.0), (0.7, 0.45, 1.0), (1.0, 0.6, 0.2)]
RING_MAT = [(0.22, 0.21, 0.26), (0.27, 0.22, 0.24), (0.30, 0.28, 0.25), (0.20, 0.22, 0.25), (0.33, 0.31, 0.30), (0.26, 0.20, 0.18)]
HQ_AB = {k: RU.ab(*v) for k, v in O["hq"].items()}
SUBU = A2P["sub_u"]
CONV = 1.5
n_ring = n_ring_city = n_ind = n_inf = 0


def sub_cell_ok(lx, ly):
    c_ = cls_at(int(math.floor(lx)), int(math.floor(ly)))
    if c_ == 12:
        return True
    return c_ == 13 and RU._hash01(7744, int(math.floor(lx)), int(math.floor(ly))) < 0.07


for gx in range(-99, GI0 + GN, SUB_PER):
    for gy in range(-99, GJ0 + GN, SUB_PER):
        cells_ = [(gx + ox + 0.5, gy + oy + 0.5, ox, oy, 1.0) for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1))]
        blk_ok = all(sub_cell_ok(c_[0], c_[1]) for c_ in cells_)
        if blk_ok and RU._hash01(7715, gx, gy) < CP.RING_PARK["p"]:
            park(W((gx, gy)), W((gx + 2, gy + 2)), random.Random(7716 * 100003 + gx * 1009 + gy))
            continue
        if RU._hash01(7713, gx, gy) < CP.URBAN["ring_merge"] and blk_ok:
            cells_ = [(gx + 1.0, gy + 1.0, 0, 0, 2.0)]
        for (lx, ly, ox, oy, msz) in cells_:
            if msz < 1.5 and not sub_cell_ok(lx, ly):
                continue
            a_, b_ = RU.ab(lx, ly)
            uu_ = RU.urban_u(a_, b_)
            far = 40.0 * max(0.0, 1.0 - uu_ / SUBU)
            if RR.random() < 0.05:
                continue
            cx_, cy_ = W((lx, ly))
            h = CP.URBAN["ring_h_k"] * min(60.0, RR.lognormvariate(math.log(6.0 + 0.03 * far), 0.6) * (0.85 if msz > 1.5 else 1.0))
            w_ = RR.uniform(0.62, 0.9) * U / 2 * (msz * 0.92 if msz > 1.5 else 1.0)
            d_ = RR.uniform(0.62, 0.9) * U / 2 * (msz * 0.92 if msz > 1.5 else 1.0)
            rkey = 800000 + (gx + 200) * 1000 + (gy + 200) + (ox + 2 * oy) * 7919
            if uu_ > 0.01 and RU._hash01(7714, gx, gy, ox, oy) < uu_ * CONV:
                hc = RR.lognormvariate(math.log(CP.URBAN["ring_city_h"][0]), CP.URBAN["ring_city_h"][1])
                hh = min(60.0, h + (hc - h) * min(1.0, uu_ * 1.5))
                w8, w08 = RU.district_weights(a_, b_, HQ_AB, uu_)
                lq = [[lx - w_ / U, ly - d_ / U], [lx + w_ / U, ly - d_ / U], [lx + w_ / U, ly + d_ / U], [lx - w_ / U, ly + d_ / U]]
                building(dict(q=lq, z0=0.0, h=hh / KH, ts=1.0, key=rkey, terr=RU.draw_district(rkey, w8, w08, salt=1), u=uu_,
                              c=[lx, ly], wet=0, sub=0.0, art=0, border=0))
                n_ring_city += 1
                continue
            pts = [(cx_ - w_, cy_ - d_), (cx_ + w_, cy_ - d_), (cx_ + w_, cy_ + d_), (cx_ - w_, cy_ + d_)]
            col = sc(RING_MAT[int(RR.random() * len(RING_MAT))], RR.uniform(0.85, 1.15))
            rtop = None
            if DAYM:
                col = sc(RU.pick(CP.DAY_MATS["sprawl"], RU._hash01(7717, gx, gy, ox, oy)), RR.uniform(0.85, 1.15))
                rtop = RU.pick(CP.DAY_ROOFS, RU._hash01(7718, gx, gy, ox, oy))
            prism(SURF, pts, 0, h, col, wc=RR.choice(RING_COLS), wl=CP.OUTLINE["ring_wl"] / (1.0 + far / 80.0) * (1.0 + 2.0 * uu_), wm=0,
                  bid=RR.random(), top_col=rtop)
            if RR.random() < CP.OUTLINE["ring_lamp_p"]:
                box(NEON, cx_ - 0.25, cy_ - 0.25, h + 0.05, cx_ + 0.25, cy_ + 0.25, h + 0.45, (1.0, 0.68, 0.32))
            if RR.random() < CP.OUTLINE["ring_trim_p"]:
                c2 = sc(RR.choice(RING_NEON), CP.OUTLINE["out_k"])
                for i in range(4):
                    bar(NEON, (pts[i][0], pts[i][1], h + 0.08), (pts[(i + 1) % 4][0], pts[(i + 1) % 4][1], h + 0.08), 0.2, c2)
            ROOFS.append((cx_, cy_, h, rkey, "ring", 0))
            n_ring += 1
# industry (class 6): low wide sheds, tanks, a chimney with a red light now and then; informal housing (class 7): dense small stacked boxes
INDM = [(0.20, 0.22, 0.25), (0.26, 0.24, 0.22), (0.18, 0.2, 0.2)]
INFM = [(0.34, 0.20, 0.12), (0.30, 0.30, 0.32), (0.40, 0.26, 0.14), (0.26, 0.22, 0.22)]
RI = random.Random(CP.SEEDS["ring"] + 5)
for cj in range(GJ0, GJ0 + GN):
    for ci in range(GI0, GI0 + GN):
        c_ = cls_at(ci, cj)
        if c_ == 6 and ci % 3 != 2 and cj % 3 != 2:
            x0_, y0_, x1_, y1_ = cell_w(ci, cj)
            h = RI.uniform(2.5, 9.0)
            if RI.random() < 0.18:
                cyl(SMOOTH, (x0_ + x1_) / 2, (y0_ + y1_) / 2, 0.0, RI.uniform(3.0, 7.0), U * 0.32, 14, sc((0.55, 0.55, 0.56), RI.uniform(0.7, 1.1)))
            else:
                box(SURF, x0_ + 0.3, y0_ + 0.3, 0.0, x1_ - 0.3, y1_ - 0.3, h, sc(RI.choice(INDM), RI.uniform(0.9, 1.2)), wc=(1.0, 0.6, 0.25), wl=0.22,
                    wm=0, bid=RI.random())
            if RI.random() < 0.08:
                cx_, cy_ = (x0_ + x1_) / 2, (y0_ + y1_) / 2
                cyl(SURF, cx_, cy_, 0.0, RI.uniform(14.0, 24.0), 0.6, 8, (0.3, 0.3, 0.32))
                box(NEON, cx_ - 0.3, cy_ - 0.3, 24.0, cx_ + 0.3, cy_ + 0.3, 24.6, (1.0, 0.1, 0.06))
            n_ind += 1
        elif c_ == 7:
            x0_, y0_, x1_, y1_ = cell_w(ci, cj)
            for (ox, oy) in ((0, 0), (1, 0), (0, 1), (1, 1)):
                if RI.random() < 0.12:
                    continue
                bx0, by0 = x0_ + ox * (x1_ - x0_) / 2 + 0.25, y0_ + oy * (y1_ - y0_) / 2 + 0.25
                bx1, by1 = bx0 + (x1_ - x0_) / 2 - 0.5, by0 + (y1_ - y0_) / 2 - 0.5
                h = RI.uniform(1.5, 5.5)
                box(SURF, bx0, by0, 0.0, bx1, by1, h, sc(RI.choice(INFM), RI.uniform(0.85, 1.2)), wc=RI.choice(RING_COLS), wl=0.55, wm=0, bid=RI.random())
                if RI.random() < 0.08:
                    box(NEON, bx0 + 0.2, by0 + 0.2, h, bx1 - 0.2, by1 - 0.2, h + 0.12, sc(RI.choice(RING_NEON), 0.5))
                n_inf += 1
print("SUBURBS ring %d city-ring %d industry %d informal %d %.1fs" % (n_ring, n_ring_city, n_ind, n_inf, time.time() - T0), flush=True)

# ------------------------------------------------------------------ the street glow (dim lane lights along every street line)
RL = random.Random(CP.SEEDS["ring"] + 1)
n_glow = 0
for per, cset in ((CORE_PER, (11,)), (SUB_PER, (12, 13))):
    for axis in (0, 1):
        for line in range(-100, GI0 + GN):
            if line % per != per - 1:
                continue
            run = None
            for s_ in range(GI0 - 1, GI0 + GN + 1):
                ci, cj = (s_, line) if axis == 0 else (line, s_)
                ok_ = cls_at(ci, cj) in cset and (cset != (13,) or RU._hash01(7745, ci, cj) < 0.07)
                if ok_ and run is None:
                    run = s_
                if run is not None and (not ok_ or s_ == GI0 + GN):
                    e_ = s_
                    if e_ - run >= 2:
                        a_, b_ = RU.ab(*((run + e_) / 2.0, line + 0.5) if axis == 0 else (line + 0.5, (run + e_) / 2.0))
                        uu_ = RU.urban_u(a_, b_)
                        major = (line % (per * 2) == per - 1)
                        c = RL.choice([(1.0, 0.62, 0.3), (1.0, 0.7, 0.4), (0.5, 0.75, 1.0), (1.0, 0.4, 0.7)])
                        k_ = RL.uniform(0.12, 0.26) * (CP.OUTLINE["ring_major_k"] if major else CP.OUTLINE["ring_minor_k"]) * (1.0 + 4.0 * uu_) * 1.6
                        if per == CORE_PER:
                            k_ *= 3.0                       # the districts' own streets: a touch brighter than the suburbs'
                        p0 = W((run, line + 0.5)) if axis == 0 else W((line + 0.5, run))
                        p1 = W((e_, line + 0.5)) if axis == 0 else W((line + 0.5, e_))
                        strip(NEON, p0, p1, 0.5, 0.05, sc(c, k_))
                        n_glow += 1
                    run = None
print("STREET GLOW", n_glow, "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ arterial traffic (ground level)
RT2 = random.Random(CP.SEEDS["streaks"] + 3)
for r_ in A2D["roads"]:
    if r_["cls"] != "arterial":
        continue
    P_ = [W(p) for p in r_["pts"]]
    if len(P_) < 2:
        continue
    for off, col in ((0.45, (1.0, 0.93, 0.82)), (1.05, (1.0, 0.85, 0.6)), (-0.45, (1.0, 0.1, 0.06)), (-1.05, (1.0, 0.18, 0.08))):
        for k in range(len(P_) - 1):
            a, b = P_[k], P_[k + 1]
            L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
            dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
            if RT2.random() < 0.38:
                continue
            nx, ny = -dy * off, dx * off
            aa_, bb_ = RU.ab(*r_["pts"][k])
            fall = 0.35 + 0.65 * RU.urban_u(aa_, bb_)
            t0_, t1_ = RT2.uniform(0.0, 0.3) * L, RT2.uniform(0.7, 1.0) * L
            traffic((a[0] + dx * t0_ + nx, a[1] + dy * t0_ + ny), (a[0] + dx * t1_ + nx, a[1] + dy * t1_ + ny), 0.12, col, RT2.uniform(0.45, 1.1) * fall)
print("ARTERIALS %.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ Tethys: the drowned quarter's seabed + levee (behind the dams)
TE = DIST["tethys"]
HULL = (0.16, 0.19, 0.24)
CONC = (0.17, 0.17, 0.19)


def cell_sub(i, j):
    return WET_CELLS.get((i, j))


def corner_sub(i, j):
    v = [cell_sub(i - di, j - dj) for di in (0, 1) for dj in (0, 1)]
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else 1.0


for (i, j), s in sorted(WET_CELLS.items()):
    cs = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
    SEABED.face([(*W(c), -corner_sub(*c)) for c in cs], (0.12, 0.13, 0.14), None, wet=1)
    for (di, dj, e0, e1) in ((1, 0, (i + 1, j), (i + 1, j + 1)), (-1, 0, (i, j + 1), (i, j)), (0, 1, (i + 1, j + 1), (i, j + 1)),
                             (0, -1, (i, j), (i + 1, j))):
        if (i + di, j + dj) in WET_CELLS:
            continue
        p0, p1 = W(e0), W(e1)
        z_lo = -max(corner_sub(*e0), corner_sub(*e1)) - 0.5
        uv, L = quad_uv(p0, p1, z_lo, WAT["levee_h"])
        SURF.face([(p0[0], p0[1], z_lo), (p1[0], p1[1], z_lo), (p1[0], p1[1], WAT["levee_h"]), (p0[0], p0[1], WAT["levee_h"])], CONC, uv, wet=1)
        SURF.face([(p0[0], p0[1], WAT["levee_h"]), (p1[0], p1[1], WAT["levee_h"]), (p1[0], p1[1], WAT["levee_h"] - 0.01),
                   (p0[0], p0[1], WAT["levee_h"] - 0.01)], CONC)
        mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
        if (i + j) % 2 == 0:
            box(NEON, mid[0] - 0.2, mid[1] - 0.2, WAT["levee_h"], mid[0] + 0.2, mid[1] + 0.2, WAT["levee_h"] + 0.35, (1.0, 0.85, 0.55))
WALL_Z0 = -max(WET_CELLS.values()) - 12.0 if WET_CELLS else -40.0

# ------------------------------------------------------------------ the sea: one water plane + the sea bed (tiles by distance from the land)
s0, s1 = WAT["sea_bed"]
SEAX = 3600.0
WATER.face([(-SEAX, -SEAX, ZW), (SEAX, -SEAX, ZW), (SEAX, SEAX, ZW), (-SEAX, SEAX, ZW)], (0, 0, 0))
TS = 4
for cj in range(GJ0 - 40, GJ0 + GN + 40, TS):
    for ci in range(GI0 - 40, GI0 + GN + 40, TS):
        if all(cls_at(ci + di, cj + dj) not in (0, 1) for di in range(TS) for dj in range(TS)):
            continue
        def sbz(cc, jj):
            return -(s0 + (s1 - s0) * min(1.0, dland_at(cc, jj) / 25.0))
        xa, ya = W((ci, cj))
        xb, yb = W((ci + TS, cj + TS))
        pts_ = [(xa, ya, sbz(ci, cj)), (xb, ya, sbz(ci + TS, cj)), (xb, yb, sbz(ci + TS, cj + TS)), (xa, yb, sbz(ci, cj + TS))]
        SEABED.face(pts_, (0.17, 0.19, 0.20), None, wet=1)
# a catch-all floor under everything (no holes between the tiles) and a deep floor out to the horizon
SEABED.face([(-SEAX, -SEAX, -s1), (SEAX, -SEAX, -s1), (SEAX, SEAX, -s1), (-SEAX, SEAX, -s1)], (0.17, 0.19, 0.20), None, wet=1)
#
for (xa, ya, xb, yb) in ((-SEAX, -SEAX, SEAX, -700.0), (-SEAX, 700.0, SEAX, SEAX), (-SEAX, -700.0, -700.0, 700.0), (700.0, -700.0, SEAX, 700.0)):
    SEABED.face([(xa, ya, -s1), (xb, ya, -s1), (xb, yb, -s1), (xa, yb, -s1)], (0.17, 0.19, 0.20), None, wet=1)
print("SEA %.1fs" % (time.time() - T0), flush=True)


# ------------------------------------------------------------------ dams, the bay barrier, sea walls: wall strips along the polylines
def wall_line(pts_lots, z_lo, z_hi, w, col, lamp=True, hue=None, step=6.0):
    P_ = [W(p) for p in pts_lots]
    arc = 0.0
    nxt = 0.0
    for k in range(len(P_) - 1):
        a, b = P_[k], P_[k + 1]
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if L < 1e-6:
            continue
        dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
        nx, ny = -dy * w / 2, dx * w / 2
        q = [(a[0] - nx, a[1] - ny), (b[0] - nx, b[1] - ny), (b[0] + nx, b[1] + ny), (a[0] + nx, a[1] + ny)]
        prism(SURF, q, z_lo, z_hi, col, top_col=sc(col, 0.8), wet=1 if z_lo < ZW else 0)
        if hue is not None:
            bar(NEON, (a[0] - nx, a[1] - ny, z_hi - 0.5), (b[0] - nx, b[1] - ny, z_hi - 0.5), 0.2, hue)
        while lamp and nxt < arc + L:
            t = nxt - arc
            x, y = a[0] + dx * t, a[1] + dy * t
            box(NEON, x - 0.2, y - 0.2, z_hi, x + 0.2, y + 0.2, z_hi + 0.4, (1.0, 0.86, 0.6))
            nxt += step
        arc += L


for d_ in A2D["dams"]:
    if d_["kind"] == "dam":
        wall_line(d_["pts"], WALL_Z0 + 8.0, WAT["levee_h"] + 1.0, 1.6, (0.30, 0.31, 0.35), hue=TE["hue"])
    else:                                                    # the Bay Barrier leaves (a storm barrier across the mouth)
        wall_line(d_["pts"], -s0 - 4.0, 5.0, 2.4, (0.34, 0.35, 0.39), hue=TE["sec"], step=8.0)
for d_ in A2D["sea_walls"]:
    wall_line(d_["pts"], -s0, 2.2, 0.9, (0.26, 0.27, 0.31), lamp=False)
# the corporate walls: a low wall round each corp enclave with a warm gate light at every gate
for corp, wd in sorted(A2D["walls"].items()):
    if corp not in DIST:
        continue
    wall_line(wd["pts"] + [wd["pts"][0]], 0.0, 2.4, 0.7, sc(DIST[corp]["mat"][0], 0.9), lamp=False, hue=sc(DIST[corp]["hue"], 0.7))
    for g_ in wd["gates"]:
        gx_, gy_ = W(g_)
        box(NEON, gx_ - 0.6, gy_ - 0.6, 0.0, gx_ + 0.6, gy_ + 0.6, 3.2, sc(DIST[corp]["hue"], 1.2))
print("DEFENCES %.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ the landmark glyphs of the plan (a few read from the air)
RGl = random.Random(CP.SEEDS["landmark"] + 9)
for gl in A2D["glyphs"]:
    kd = gl["kind"]
    gx_, gy_ = W(gl["pos"])
    ci_, cj_ = int(math.floor(gl["pos"][0])), int(math.floor(gl["pos"][1]))
    if cls_at(ci_, cj_) in (0, 1):
        continue
    if kd == "arcology":
        hh = RGl.uniform(40.0, 70.0)
        cyl(SMOOTH, gx_, gy_, 0.0, hh, 3.2, 18, (0.30, 0.32, 0.36), wc=(1.0, 0.85, 0.55), wl=0.7, wm=1, bid=RGl.random())
        ring_line(NEON, gx_, gy_, hh + 0.1, 3.3, 0.3, (1.0, 0.8, 0.5), n=18)
    elif kd == "megastructure":
        hh = RGl.uniform(60.0, 95.0)
        box(SURF, gx_ - 2.4, gy_ - 2.4, 0.0, gx_ + 2.4, gy_ + 2.4, hh, (0.26, 0.27, 0.32), wc=(0.6, 0.85, 1.0), wl=0.5, wm=0, bid=RGl.random())
        box(NEON, gx_ - 2.5, gy_ - 2.5, hh, gx_ + 2.5, gy_ + 2.5, hh + 0.4, (0.5, 0.8, 1.0))
    elif kd == "stadium":
        ring_line(NEON, gx_, gy_, 4.0, 5.0, 0.4, (1.0, 0.95, 0.85), n=28)
        annulus(SURF, gx_, gy_, 3.0, 3.6, 5.2, (0.3, 0.3, 0.34), n=28)
    elif kd == "power":
        for m in range(3):
            cyl(SURF, gx_ + (m - 1) * 2.2, gy_, 0.0, 18.0 + m * 3, 0.9, 10, (0.3, 0.3, 0.32))
            box(NEON, gx_ + (m - 1) * 2.2 - 0.3, gy_ - 0.3, 18.0 + m * 3, gx_ + (m - 1) * 2.2 + 0.3, gy_ + 0.3, 18.6 + m * 3, (1.0, 0.1, 0.06))
    elif kd == "datacentre":
        box(SURF, gx_ - 2.2, gy_ - 1.6, 0.0, gx_ + 2.2, gy_ + 1.6, 4.0, (0.2, 0.22, 0.28), wc=(0.4, 0.8, 1.0), wl=0.8, wm=0, bid=RGl.random())
        box(NEON, gx_ - 2.2, gy_ - 1.6, 4.0, gx_ + 2.2, gy_ + 1.6, 4.15, (0.3, 0.7, 1.0))
    elif kd == "hospital":
        box(NEON, gx_ - 0.9, gy_ - 0.25, 6.0, gx_ + 0.9, gy_ + 0.25, 6.3, (1.0, 0.1, 0.1))
        box(NEON, gx_ - 0.25, gy_ - 0.9, 6.0, gx_ + 0.25, gy_ + 0.9, 6.3, (1.0, 0.1, 0.1))
for mk in A2D["markets"]:
    gx_, gy_ = W(mk["pos"])
    if cls_at(int(math.floor(mk["pos"][0])), int(math.floor(mk["pos"][1]))) in (0, 1):
        continue
    for m in range(9):
        mx_, my_ = gx_ + RGl.uniform(-3, 3), gy_ + RGl.uniform(-3, 3)
        box(NEON, mx_, my_, 0.1, mx_ + 0.8, my_ + 0.8, 0.9, sc(RGl.choice(RING_NEON), 0.7))
print("WORLD A2 done %.1fs" % (time.time() - T0), flush=True)
