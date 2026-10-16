"""City-all-corps round 4 (exec'd by city_build.py after city_world_a2.py): the A2 transport.

ROADS: the rings (R1 / R2), motorways and truck roads are elevated decks along the plan's polylines (tunnel runs are cut: a
portal ramp down into the ground), with piers, sodium lamp masts, dense traffic. Interchanges: every ramp of the plan
(diamond / stack / cloverleaf) is a curved one-way deck between its two roads (z eased between the road heights), with edge
lights, lamps, traffic and a slip lane at each elevated end.
RAILS: freight (viaduct, up to the Meridian HQ's north flank, down to the port terminus), commuter and metro viaducts
(tunnel runs cut), lit trains as light streaks, stations.
PORT (Port of Meridian): terminal platform, container stacks, five piers with gantry cranes, ships moored between them, yard
tracks, light masts.  AIRPORT: runways with edge lights, a terminal.
"""
HWY = CP.HIGHWAY
HW_CONC = (0.34, 0.33, 0.32)
RH = random.Random(CP.SEEDS["streaks"] + 21)
HW_LANES = ((HWY["lane_off"][0], (1.0, 0.93, 0.82)), (HWY["lane_off"][1], (1.0, 0.86, 0.62)),
            (-HWY["lane_off"][0], (1.0, 0.1, 0.06)), (-HWY["lane_off"][1], (1.0, 0.16, 0.07)))


class Path:
    """a polyline in world BU with arc length; at(s) -> (point, unit tangent)."""

    def __init__(self, pts_lots, closed=False):
        P = [W(p) for p in pts_lots]
        if closed and P[0] != P[-1]:
            P = P + [P[0]]
        self.P = P
        self.S = [0.0]
        for i in range(1, len(P)):
            self.S.append(self.S[-1] + math.hypot(P[i][0] - P[i - 1][0], P[i][1] - P[i - 1][1]))
        self.L = self.S[-1]
        self.closed = closed

    def at(self, s):
        if self.closed:
            s = s % self.L
        s = min(max(s, 0.0), self.L)
        lo, hi = 0, len(self.S) - 1
        while hi - lo > 1:
            m = (lo + hi) // 2
            if self.S[m] <= s:
                lo = m
            else:
                hi = m
        a, b = self.P[lo], self.P[hi]
        seg = max(1e-9, self.S[hi] - self.S[lo])
        t = (s - self.S[lo]) / seg
        d = ((b[0] - a[0]) / seg, (b[1] - a[1]) / seg)
        return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t), d

    def off(self, s, o):
        p, d = self.at(s)
        return (p[0] - d[1] * o, p[1] + d[0] * o)

    def nearest(self, x, y):
        best = (1e18, 0.0)
        for i in range(len(self.P) - 1):
            a, b = self.P[i], self.P[i + 1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            l2 = dx * dx + dy * dy
            t = 0.0 if l2 < 1e-12 else min(1.0, max(0.0, ((x - a[0]) * dx + (y - a[1]) * dy) / l2))
            d = math.hypot(x - a[0] - dx * t, y - a[1] - dy * t)
            if d < best[0]:
                best = (d, self.S[i] + math.sqrt(l2) * t)
        return best[1], best[0]


def deck(path, zf, width, conc, edge_col, edge_k, step=3.0, thick=1.3, parapet=0.55):
    hw = width / 2.0
    s = 0.0
    while s < path.L - 1e-3:
        s2 = min(path.L, s + step)
        za, zb = zf(s), zf(s2)
        a0, a1, b0, b1 = path.off(s, -hw), path.off(s, hw), path.off(s2, -hw), path.off(s2, hw)
        SURF.face([(a0[0], a0[1], za), (b0[0], b0[1], zb), (b1[0], b1[1], zb), (a1[0], a1[1], za)], conc)
        SURF.face([(a0[0], a0[1], za - thick), (a1[0], a1[1], za - thick), (b1[0], b1[1], zb - thick), (b0[0], b0[1], zb - thick)], sc(conc, 0.6))
        for sd in (-1, 1):
            e0, e1 = path.off(s, sd * hw), path.off(s2, sd * hw)
            SURF.face([(e0[0], e0[1], za - thick), (e1[0], e1[1], zb - thick), (e1[0], e1[1], zb + parapet), (e0[0], e0[1], za + parapet)], sc(conc, 0.82))
            f0, f1 = path.off(s, sd * (hw - 0.08)), path.off(s2, sd * (hw - 0.08))
            bar(NEON, (f0[0], f0[1], za + parapet - 0.1), (f1[0], f1[1], zb + parapet - 0.1), 0.12, sc(edge_col, edge_k))
        s = s2


def piers(path, zf, step, size, conc, thick=1.3, round_=False, start=None):
    s = step / 2 if start is None else start
    while s < path.L:
        z_ = zf(s)
        if z_ > 3.0:
            c, _ = path.at(s)
            gz = ground_at(c[0], c[1])
            if gz < -1.0:                                              # over the water: the pier stands on the bed
                box(SURF, c[0] - size, c[1] - size, gz, c[0] + size, c[1] + size, z_ - thick, sc(conc, 0.9), wet=1)
            elif round_:
                cyl(SURF, c[0], c[1], 0.0, z_ - thick, size, 8, sc(conc, 0.85))
            else:
                box(SURF, c[0] - size, c[1] - size, 0.0, c[0] + size, c[1] + size, z_ - thick, sc(conc, 0.9))
        s += step


def lanes_traffic(path, zf, lanes, rng, slen, gap, w=0.2, k0=1.0):
    n = 0
    for (off, col) in lanes:
        s = -rng.uniform(0, 10)
        while s < path.L:
            ln = rng.uniform(*slen)
            g_ = rng.uniform(*gap)
            kk = rng.uniform(0.6, 1.3) * k0
            sa, sb = max(0.0, s), min(path.L, s + ln)
            if sb > sa + 0.5:
                ss = sa
                while ss < sb - 0.05:
                    se = min(sb, ss + 3.0)
                    traffic(path.off(ss, off), path.off(se, off), zf((ss + se) / 2) + 0.15, col, kk, w=w)
                    ss = se
                n += 1
            s += ln + g_
    return n


T0b = time.time()
n_tr = 0
ROAD_Z = {}           # road id -> [(Path, zf)] (runs)
ROAD_NAME = {r_["name"]: r_["id"] for r_ in A2D["roads"]}
RAMPLEN = HWY["ramp"]


def runs_of(pts, tunnels, closed):
    """split a polyline into runs outside the tunnel sub-polylines (points matched by rounded lot coordinates)."""
    tun = {(round(p[0], 1), round(p[1], 1)) for t in tunnels for p in t}
    runs, cur = [], []
    for p in pts:
        if (round(p[0], 1), round(p[1], 1)) in tun:
            if len(cur) > 1:
                runs.append(cur)
            cur = []
        else:
            cur.append(p)
    if len(cur) > 1:
        runs.append(cur)
    return runs


def road_run_z(path, zt, ends=True):
    L_ = path.L

    def zf(s, zt=zt, L_=L_):
        if not ends:
            return zt
        t = min(1.0, s / RAMPLEN, (L_ - s) / RAMPLEN)
        t = max(0.0, t)
        return 0.3 + (zt - 0.3) * t * t * (3 - 2 * t)
    return zf


for r_ in A2D["roads"]:
    if r_["cls"] not in ("ring", "motorway", "truck"):
        continue
    zt = r_["z"]
    width = r_["w"]
    runs = runs_of(r_["pts"], r_["tunnels"], r_["closed"])
    lst = []
    for run in runs:
        closed = r_["closed"] and len(runs) == 1 and len(run) >= len(r_["pts"]) - 1
        hp_ = Path(run, closed=closed)
        if hp_.L < 8.0:
            continue
        zf = road_run_z(hp_, zt, ends=not closed)
        lst.append((hp_, zf))
        deck(hp_, zf, width, HW_CONC, HWY["edge_col"], HWY["edge_k"])
        piers(hp_, zf, HWY["pier_step"], 0.8, HW_CONC)
        s = HWY["lamp_step"] / 2
        while s < hp_.L:
            c, d_ = hp_.at(s)
            z_ = zf(s)
            if z_ > 2.0:
                bar(SURF, (c[0], c[1], z_), (c[0], c[1], z_ + 2.6), 0.12, (0.3, 0.3, 0.32))
                for sd in (-1, 1):
                    q_ = hp_.off(s, sd * 0.7)
                    box(NEON, q_[0] - 0.18, q_[1] - 0.18, z_ + 2.4, q_[0] + 0.18, q_[1] + 0.18, z_ + 2.6, HWY["lamp_col"])
            s += HWY["lamp_step"]
        n_tr += lanes_traffic(hp_, zf, HW_LANES, RH, HWY["streak_len"], HWY["gap"], k0=0.9)
    ROAD_Z[r_["id"]] = lst
print("ROADS", len(ROAD_Z), "traffic draws", n_tr, "%.1fs" % (time.time() - T0), flush=True)


def road_z_at(rid, x, y):
    """-> (z, Path, s) of the road run nearest the world point."""
    best = None
    for (p_, zf_) in ROAD_Z.get(rid, []):
        s_, d_ = p_.nearest(x, y)
        if best is None or d_ < best[0]:
            best = (d_, p_, zf_, s_)
    if best is None:
        return 0.12, None, None, None
    return best[2](best[3]), best[1], best[2], best[3]


# ------------------------------------------------------------------ interchange ramps
RMP = dict(w=3.0, thick=0.8, lamp_step=9.0, lane_len=22.0, lane_w=1.5)
RR3 = random.Random(CP.SEEDS["streaks"] + 41)
n_ramp = 0
for ix in A2D["interchanges"]:
    ids = [ROAD_NAME[nm] for nm in ix["roads"] if nm in ROAD_NAME and ROAD_NAME[nm] in ROAD_Z]
    for rp_pts in ix["ramps"]:
        rp = Path(rp_pts)
        if rp.L < 6.0 or not ids:
            continue
        ends = []
        for pt in (rp_pts[0], rp_pts[-1]):
            x_, y_ = W(pt)
            cands = [(road_z_at(rid, x_, y_), rid) for rid in ids]
            cands = [(c_, rid) for (c_, rid) in cands if c_[1] is not None]
            if not cands:
                ends.append((0.12, None, None, None))
                continue
            best = min(cands, key=lambda t: t[0][1].nearest(x_, y_)[1])
            ends.append(best[0])
        z0, z1 = ends[0][0], ends[1][0]

        def rzf(s, z0=z0, z1=z1, L_=rp.L):
            t = min(1.0, max(0.0, s / L_))
            return z0 + (z1 - z0) * t * t * (3 - 2 * t)
        deck(rp, rzf, RMP["w"], HW_CONC, HWY["edge_col"], HWY["edge_k"] * 0.8, step=3.0, thick=RMP["thick"], parapet=0.35)
        piers(rp, rzf, 8.0, 0.45, HW_CONC, thick=RMP["thick"])
        s = RMP["lamp_step"] / 2
        k_ = 0
        while s < rp.L:
            z_ = rzf(s)
            if z_ > 1.5:
                q_ = rp.off(s, (1 if k_ % 2 else -1) * (RMP["w"] / 2 - 0.1))
                bar(SURF, (q_[0], q_[1], z_), (q_[0], q_[1], z_ + 2.0), 0.1, (0.3, 0.3, 0.32))
                box(NEON, q_[0] - 0.16, q_[1] - 0.16, z_ + 1.9, q_[0] + 0.16, q_[1] + 0.16, z_ + 2.1, HWY["lamp_col"])
            k_ += 1
            s += RMP["lamp_step"]
        n_tr += lanes_traffic(rp, rzf, ((0.6, (1.0, 0.9, 0.7)), (-0.6, (1.0, 0.55, 0.3))), RR3, (4.0, 12.0), (3.0, 16.0), w=0.18)
        for ei, (zz, rd, rzfn, s_e) in enumerate(ends):                       # slip lanes at the ends on elevated roads
            if rd is None or zz < 3.0:
                continue
            at_start = ei == 0
            pe, te = rd.at(s_e)
            pr, dr = rp.at(min(max((6.0 if at_start else rp.L - 6.0), 0.0), rp.L))
            fwd = 1.0 if (dr[0] * te[0] + dr[1] * te[1]) >= 0 else -1.0
            side = 1.0 if ((pr[0] - pe[0]) * (-te[1]) + (pr[1] - pe[1]) * te[0]) > 0 else -1.0
            a_s, b_s = (s_e - fwd * RMP["lane_len"], s_e) if at_start else (s_e, s_e + fwd * RMP["lane_len"])
            lo, hi = (a_s, b_s) if a_s < b_s else (b_s, a_s)
            if not rd.closed:
                lo, hi = max(lo, 0.0), min(hi, rd.L)
            off0 = HWY["width"] / 2.0 + RMP["lane_w"] / 2.0 + 0.05
            ss = lo
            while ss < hi - 1e-3:
                se = min(hi, ss + 3.0)
                za, zb = rzfn(ss), rzfn(se)
                a0, a1 = rd.off(ss, side * (off0 - RMP["lane_w"] / 2)), rd.off(ss, side * (off0 + RMP["lane_w"] / 2))
                b0, b1 = rd.off(se, side * (off0 - RMP["lane_w"] / 2)), rd.off(se, side * (off0 + RMP["lane_w"] / 2))
                SURF.face([(a0[0], a0[1], za), (b0[0], b0[1], zb), (b1[0], b1[1], zb), (a1[0], a1[1], za)], HW_CONC)
                SURF.face([(a0[0], a0[1], za - 0.9), (a1[0], a1[1], za - 0.9), (b1[0], b1[1], zb - 0.9), (b0[0], b0[1], zb - 0.9)], sc(HW_CONC, 0.6))
                f0, f1 = rd.off(ss, side * (off0 + RMP["lane_w"] / 2 - 0.08)), rd.off(se, side * (off0 + RMP["lane_w"] / 2 - 0.08))
                bar(NEON, (f0[0], f0[1], za + 0.2), (f1[0], f1[1], zb + 0.2), 0.12, sc(HWY["edge_col"], HWY["edge_k"]))
                ss = se
        n_ramp += 1
print("RAMPS", n_ramp, "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ rails: freight, commuter, metro viaducts + trains + stations
RAILZ = {}
RAIL_SPEC = dict(freight=dict(w=2.8, thick=1.1, col=(0.30, 0.27, 0.25), edge=(1.0, 0.5, 0.12), ek=0.9, z=17.5, step=7.0),
                 commuter=dict(w=2.4, thick=0.9, col=(0.34, 0.32, 0.34), edge=(1.0, 0.45, 0.85), ek=0.7, z=CP.A2["z"]["commuter"], step=8.0),
                 metro=dict(w=2.0, thick=0.9, col=(0.40, 0.40, 0.42), edge=(0.55, 0.95, 1.0), ek=1.0, z=CP.A2["z"]["metro"], step=9.0))
HQM = W(O["hq"]["meridian"])
TR_RNG = random.Random(CP.SEEDS["streaks"] + 61)
CCW = [(0.62, 0.24, 0.08), (0.12, 0.34, 0.36), (0.55, 0.12, 0.08), (0.75, 0.42, 0.10)]
n_rail = 0
for rl in A2D["rails"]:
    spec = RAIL_SPEC[rl["kind"]]
    if rl["name"] == "yard track":
        continue
    runs = runs_of(rl["pts"], rl["tunnels"], rl["closed"])
    lst = []
    for run in runs:
        rp = Path(run, closed=False)
        if rp.L < 10.0:
            continue

        def zf(s, rp=rp, spec=spec, kind=rl["kind"]):
            L_ = rp.L
            if kind == "freight":
                # level at the viaduct height beside the Meridian HQ, coming down to the ground far from it and to the port platform
                p_, _ = rp.at(s)
                dh = math.hypot(p_[0] - HQM[0], p_[1] - HQM[1])
                t = 1.0 - min(1.0, max(0.0, (dh - 90.0) / 260.0))
                z_ = 0.7 + (spec["z"] - 0.7) * t * t * (3 - 2 * t)
                tt = min(1.0, max(0.0, s / 70.0), max(0.0, (L_ - s) / 45.0))
                z_ = min(z_, 0.7 + (spec["z"] - 0.7) * tt)
                return max(z_, CP.PORT["z"] + 0.7 if (L_ - s) < 45.0 else 0.7)
            t = max(0.0, min(1.0, s / 50.0, (L_ - s) / 50.0))
            return 0.7 + (spec["z"] - 0.7) * t * t * (3 - 2 * t)
        lst.append((rp, zf))
        deck(rp, zf, spec["w"], spec["col"], spec["edge"], spec["ek"], step=3.0, thick=spec["thick"], parapet=0.25)
        piers(rp, zf, spec["step"], 0.5, spec["col"], thick=spec["thick"], round_=True)
        if rl["kind"] == "freight":
            s = 20.0
            while s < rp.L:                                          # orange signal lamps
                c, d_ = rp.at(s)
                px, py = c[0] - d_[1] * 1.6, c[1] + d_[0] * 1.6
                z_ = zf(s)
                bar(SURF, (px, py, z_), (px, py, z_ + 2.0), 0.14, (0.3, 0.3, 0.32))
                box(NEON, px - 0.22, py - 0.22, z_ + 2.0, px + 0.22, py + 0.22, z_ + 2.5, (1.0, 0.45, 0.08))
                s += 36.0
        # trains: lit heads with a warm trail (and container wagons on the freight)
        ntr = 3 if rl["kind"] == "freight" else 2
        for k_ in range(ntr):
            s_head = rp.L * (k_ + TR_RNG.uniform(0.15, 0.7)) / ntr
            ln = 30.0 if rl["kind"] == "freight" else 20.0
            m = 20
            for kk in range(m):
                sa, sb = s_head - ln * kk / m, s_head - ln * (kk + 1) / m
                pa, _ = rp.at(sa)
                pb, _ = rp.at(sb)
                k2 = (1.0 - kk / m) ** 1.5
                bar(STREAK, (pa[0], pa[1], zf(sa) + 0.6), (pb[0], pb[1], zf(sb) + 0.6), 0.6, sc(spec["edge"], 0.5 + 0.9 * k2))
            ph, _ = rp.at(s_head)
            box(STREAK, ph[0] - 0.4, ph[1] - 0.4, zf(s_head) + 0.3, ph[0] + 0.4, ph[1] + 0.4, zf(s_head) + 1.1, (1.0, 0.95, 0.85))
            if rl["kind"] == "freight":
                for kk in range(5):
                    s1w, s2w = s_head - 1.0 - kk * 3.2, s_head - 1.0 - kk * 3.2 - 2.8
                    pa, _ = rp.at(s1w)
                    pb, _ = rp.at(s2w)
                    bar(SURF, (pa[0], pa[1], zf(s1w) + 1.0), (pb[0], pb[1], zf(s2w) + 1.0), 1.4, CCW[kk % 4])
        n_rail += 1
    RAILZ[rl["id"]] = lst
print("RAILS", n_rail, "%.1fs" % (time.time() - T0), flush=True)
# stations: a platform + canopy at the nearest point of its line
for st in A2D["stations"]:
    lid = next((rl["id"] for rl in A2D["rails"] if rl["name"] in st["lines"] and rl["id"] in RAILZ and RAILZ[rl["id"]]), None)
    if lid is None:
        continue
    sx, sy = W(st["pos"])
    best = min(((p_.nearest(sx, sy)[1], p_, zf_, p_.nearest(sx, sy)[0]) for (p_, zf_) in RAILZ[lid]), key=lambda t: t[0])
    d_, p_, zf_, s_ = best
    if d_ > 6.0:
        continue
    (cx_, cy_), (tx, ty) = p_.at(s_)
    z_ = zf_(s_)
    if z_ < 1.0:
        z_ = 0.7
    nx, ny = -ty, tx
    kind = next((rl["kind"] for rl in A2D["rails"] if rl["id"] == lid), "commuter")
    sp = RAIL_SPEC[kind]
    L_, W_ = (9.0, 2.6) if kind != "metro" else (7.0, 2.0)
    q_ = [(cx_ - tx * L_ / 2 - nx * W_, cy_ - ty * L_ / 2 - ny * W_), (cx_ + tx * L_ / 2 - nx * W_, cy_ + ty * L_ / 2 - ny * W_),
          (cx_ + tx * L_ / 2 + nx * W_, cy_ + ty * L_ / 2 + ny * W_), (cx_ - tx * L_ / 2 + nx * W_, cy_ - ty * L_ / 2 + ny * W_)]
    prism(SURF, q_, z_ + 2.6, z_ + 3.0, (0.55, 0.57, 0.62))
    for i in range(4):
        bar(NEON, (q_[i][0], q_[i][1], z_ + 2.55), (q_[(i + 1) % 4][0], q_[(i + 1) % 4][1], z_ + 2.55), 0.16, sc(sp["edge"], 1.3))
    for sd in (-1, 1):
        bar(NEON, (cx_ - tx * L_ / 2 + nx * sd * 1.4, cy_ - ty * L_ / 2 + ny * sd * 1.4, z_ + 0.2),
            (cx_ + tx * L_ / 2 + nx * sd * 1.4, cy_ + ty * L_ / 2 + ny * sd * 1.4, z_ + 0.2), 0.22, sc((1.0, 0.92, 0.75), 0.8))
print("STATIONS %.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ the PORT of Meridian
PO = A2D["port"]
PZ = CP.PORT["z"] * 0.5
RPo = random.Random(CP.SEEDS["landmark"] + 77)
CCP = [(0.72, 0.30, 0.08), (0.58, 0.22, 0.08), (0.14, 0.36, 0.38), (0.45, 0.42, 0.40), (0.80, 0.46, 0.10), (0.62, 0.12, 0.08),
       (0.20, 0.30, 0.50), (0.85, 0.80, 0.70)]
poly_w = [W(p) for p in PO["poly"]]
prism(SURF, poly_w, -4.0, PZ, (0.36, 0.35, 0.33), top_col=(0.30, 0.29, 0.28), wet=0)
yard_w = [W(p) for p in PO["yard"]]
xs_p, ys_p = [p[0] for p in poly_w], [p[1] for p in poly_w]


def in_poly_w(x, y, q):
    ins = False
    n = len(q)
    for i in range(n):
        (x0, y0), (x1, y1) = q[i], q[(i + 1) % n]
        if (y0 > y) != (y1 > y) and x < (x1 - x0) * (y - y0) / ((y1 - y0) or 1e-12) + x0:
            ins = not ins
    return ins


# container stacks: blocks on a 6.5 x 2.6 BU grid inside the terminal, aisles every 4th row
gx_ = min(xs_p) + 3.0
n_cont = 0
while gx_ < max(xs_p) - 3.0:
    gy_ = min(ys_p) + 3.0
    row = 0
    while gy_ < max(ys_p) - 3.0:
        row += 1
        if row % 5 != 0 and in_poly_w(gx_, gy_, poly_w) and in_poly_w(gx_ + 6.0, gy_ + 2.4, poly_w) and RPo.random() > 0.1:
            for lv in range(RPo.randint(1, 4)):
                box(SURF, gx_, gy_, PZ + lv * 0.95, gx_ + 5.6, gy_ + 2.2, PZ + lv * 0.95 + 0.9, RPo.choice(CCP))
            n_cont += 1
        gy_ += 2.9
    gx_ += 6.4
# rail yard tracks (the plan's yard tracks) and the freight terminus
for rl in A2D["rails"]:
    if rl["name"] == "yard track":
        pp = [W(p) for p in rl["pts"]]
        for k in range(len(pp) - 1):
            bar(SURF, (pp[k][0], pp[k][1], PZ + 0.15), (pp[k + 1][0], pp[k + 1][1], PZ + 0.15), 0.4, (0.42, 0.40, 0.38))
# the piers: platforms running into the bay (bearing 270 = west), cranes on both sides, ships moored between them
PIER_D = []
for pr in PO["piers"]:
    bx, by = W(pr["base"])
    th = math.radians(pr["bearing"])                       # compass: clockwise from north (world x east, y north)
    ux, uy = math.sin(th), math.cos(th)
    nx, ny = -uy, ux
    Lp, Wp = pr["length"] * U, pr["width"] * U
    q_ = [(bx - nx * Wp / 2, by - ny * Wp / 2), (bx + ux * Lp - nx * Wp / 2, by + uy * Lp - ny * Wp / 2),
          (bx + ux * Lp + nx * Wp / 2, by + uy * Lp + ny * Wp / 2), (bx + nx * Wp / 2, by + ny * Wp / 2)]
    prism(SURF, q_, -WAT["sea_bed"][0] * 0.5, PZ, (0.36, 0.35, 0.33), top_col=(0.30, 0.29, 0.28), wet=1)
    PIER_D.append((bx, by, ux, uy, nx, ny, Lp, Wp))
    for sd in (-1, 1):                                     # quay-edge lights and gantry cranes
        for m in range(1, 5):
            t = Lp * m / 5.0
            px, py = bx + ux * t + nx * sd * (Wp / 2 - 1.2), by + uy * t + ny * sd * (Wp / 2 - 1.2)
            col_ = (0.92, 0.40, 0.08) if m % 2 else (0.88, 0.88, 0.86)
            for dd in (-1.0, 1.0):
                for ee in (-1.0, 1.0):
                    lx_, ly_ = px + ux * dd * 1.2 + nx * sd * ee * 0.9, py + uy * dd * 1.2 + ny * sd * ee * 0.9
                    bar(SURF, (lx_, ly_, PZ), (lx_, ly_, PZ + 11.0), 0.55, col_)
            bar(SURF, (px - ux * 1.2, py - uy * 1.2, PZ + 11.0), (px + ux * 1.2, py + uy * 1.2, PZ + 11.0), 0.7, col_)
            bm0 = (px + nx * sd * (-4.5), py + ny * sd * (-4.5), PZ + 12.0)
            bm1 = (px + nx * sd * 7.5, py + ny * sd * 7.5, PZ + 12.0)
            bar(SURF, bm0, bm1, 0.8, col_)
            box(NEON, bm1[0] - 0.3, bm1[1] - 0.3, PZ + 12.3, bm1[0] + 0.3, bm1[1] + 0.3, PZ + 12.9, (1.0, 0.55, 0.15))
            hk = (px + nx * sd * 5.0, py + ny * sd * 5.0)
            bar(SURF, (hk[0], hk[1], PZ + 12.0), (hk[0], hk[1], PZ + 6.5), 0.1, (0.2, 0.2, 0.22))
            box(SURF, hk[0] - 0.9, hk[1] - 0.35, PZ + 5.6, hk[0] + 0.9, hk[1] + 0.35, PZ + 6.5, RPo.choice(CCP))
# ships moored between the piers
for k in range(len(PIER_D) - 1):
    b0, b1 = PIER_D[k], PIER_D[k + 1]
    mx_, my_ = (b0[0] + b1[0]) / 2 + b0[2] * b0[6] * 0.55, (b0[1] + b1[1]) / 2 + b0[3] * b0[6] * 0.55
    gap = math.hypot(b1[0] - b0[0], b1[1] - b0[1]) - b0[7]
    if gap < 14.0:
        continue
    ux, uy = b0[2], b0[3]
    Lh, Bh = 20.0, min(4.5, gap * 0.3)
    hull = []
    for m in range(13):
        t = -1.0 + 2.0 * m / 12
        taper = 1.0 if t < 0.7 else max(0.15, 1.0 - (t - 0.7) / 0.3 * 0.85)
        hull.append((t * Lh, taper))
    nx, ny = b0[4], b0[5]
    top = [(mx_ + ux * u_ + nx * Bh * tp, my_ + uy * u_ + ny * Bh * tp) for (u_, tp) in hull] + \
          [(mx_ + ux * u_ - nx * Bh * tp, my_ + uy * u_ - ny * Bh * tp) for (u_, tp) in reversed(hull)]
    prism(SURF, top, ZW - 4.0, ZW + 3.0, RPo.choice([(0.16, 0.18, 0.22), (0.45, 0.10, 0.08), (0.10, 0.20, 0.30)]), top_col=(0.30, 0.30, 0.30), wet=1)
    br = [(mx_ - ux * Lh * 0.92 + nx * Bh * 0.9, my_ - uy * Lh * 0.92 + ny * Bh * 0.9), (mx_ - ux * Lh * 0.7 + nx * Bh * 0.9, my_ - uy * Lh * 0.7 + ny * Bh * 0.9),
          (mx_ - ux * Lh * 0.7 - nx * Bh * 0.9, my_ - uy * Lh * 0.7 - ny * Bh * 0.9), (mx_ - ux * Lh * 0.92 - nx * Bh * 0.9, my_ - uy * Lh * 0.92 - ny * Bh * 0.9)]
    prism(SURF, br, ZW + 3.0, ZW + 9.0, (0.85, 0.85, 0.83), wc=(1.0, 0.86, 0.6), wl=0.6, wm=0, bid=0.3 + k * 0.1)
    u_ = -Lh * 0.62
    while u_ < Lh * 0.62:
        for lane in (-0.55, 0.0, 0.55):
            for lv in range(RPo.randint(1, 4)):
                cx_, cy_ = mx_ + ux * u_ + nx * lane * Bh, my_ + uy * u_ + ny * lane * Bh
                box(SURF, cx_ - 1.2, cy_ - 0.8, ZW + 3.0 + lv * 0.95, cx_ + 1.2, cy_ + 0.8, ZW + 3.9 + lv * 0.95, RPo.choice(CCP)) if abs(ux) > 0.7 else \
                    box(SURF, cx_ - 0.8, cy_ - 1.2, ZW + 3.0 + lv * 0.95, cx_ + 0.8, cy_ + 1.2, ZW + 3.9 + lv * 0.95, RPo.choice(CCP))
        u_ += 2.6
    box(NEON, mx_ - ux * Lh * 0.82 - 0.3, my_ - uy * Lh * 0.82 - 0.3, ZW + 9.0, mx_ - ux * Lh * 0.82 + 0.3, my_ - uy * Lh * 0.82 + 0.3, ZW + 9.6, (1.0, 0.95, 0.85))
# yard light masts (sodium spots at night)
for k in range(14):
    p_ = (min(xs_p) + 4.0 + (max(xs_p) - min(xs_p) - 8.0) * ((k * 0.381) % 1.0), min(ys_p) + 4.0 + (max(ys_p) - min(ys_p) - 8.0) * ((k * 0.617) % 1.0))
    if not in_poly_w(p_[0], p_[1], poly_w):
        continue
    bar(SURF, (p_[0], p_[1], PZ), (p_[0], p_[1], PZ + 14.0), 0.35, (0.4, 0.4, 0.42))
    box(NEON, p_[0] - 0.7, p_[1] - 0.7, PZ + 14.0, p_[0] + 0.7, p_[1] + 0.7, PZ + 14.5, (1.0, 0.65, 0.3))
    if not DAYM:
        LIGHT_SPOTS.append(dict(loc=(p_[0], p_[1], PZ + 14.0), tgt=(p_[0], p_[1], PZ), col=(1.0, 0.7, 0.4), power=6.0e4, cone=110.0, blend=0.6, k=1.0))
print("PORT containers", n_cont, "piers", len(PIER_D), "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ the AIRPORT: runways with edge lights + a terminal
AP = A2D["airport"]
for rw in AP["runways"]:
    cx_, cy_ = W(rw["c"])
    th = math.radians(rw["bearing"])
    ux, uy = math.sin(th), math.cos(th)
    nx, ny = -uy, ux
    Lr = rw["length"] * U / 2
    q_ = [(cx_ - ux * Lr - nx * 1.4, cy_ - uy * Lr - ny * 1.4), (cx_ + ux * Lr - nx * 1.4, cy_ + uy * Lr - ny * 1.4),
          (cx_ + ux * Lr + nx * 1.4, cy_ + uy * Lr + ny * 1.4), (cx_ - ux * Lr + nx * 1.4, cy_ - uy * Lr + ny * 1.4)]
    GROUND.face([(x, y, 0.03) for (x, y) in q_], (0.05, 0.05, 0.06))
    for sd in (-1, 1):
        t = -Lr
        while t < Lr:
            px, py = cx_ + ux * t + nx * sd * 1.4, cy_ + uy * t + ny * sd * 1.4
            box(NEON, px - 0.12, py - 0.12, 0.05, px + 0.12, py + 0.12, 0.25, (0.9, 0.95, 1.0) if sd > 0 else (1.0, 0.9, 0.7))
            t += 3.0
    strip(NEON, (cx_ - ux * Lr * 0.9, cy_ - uy * Lr * 0.9), (cx_ + ux * Lr * 0.9, cy_ + uy * Lr * 0.9), 0.12, 0.06, (0.55, 0.55, 0.6))
tc = W(AP["centre"])
for k_ in range(5):
    box(SURF, tc[0] - 14 + k_ * 5.4, tc[1] - 6.0, 0.0, tc[0] - 9.6 + k_ * 5.4, tc[1] + 6.0, 3.0 + (k_ % 2), (0.30, 0.32, 0.36), wc=(0.7, 0.85, 1.0), wl=0.6, wm=1,
        bid=k_ * 0.2)
box(NEON, tc[0] - 14, tc[1] - 6.1, 3.5, tc[0] + 13, tc[1] - 5.9, 3.65, (0.7, 0.9, 1.0))
print("TRANSIT A2 done %.1fs" % (time.time() - T0), flush=True)
