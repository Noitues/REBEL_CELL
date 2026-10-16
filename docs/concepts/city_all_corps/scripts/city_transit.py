"""City-all-corps round 3b (exec'd by city_build.py after city_world.py, same namespace): designer notes on transport.

Every path is a smooth curve from zoning (Catmull-Rom samples in lots; no 90-degree turns), its corridor already
cleared of buildings.
HUB (CP.HUB): a ground-level truck ring road round the Meridian HQ lot, four lanes of traffic, kerb lamps.
SPOKES (CP.SPOKES / HIGHWAY): elevated highways that leave the hub ring tangentially, ramp up to their deck height and
run out into the sprawl (the port spur ramps down into the port). Deck slabs, girders, parapets with a cool edge light,
piers, sodium lamp masts, dense traffic (night: light trails; day: cars), thinning past the map edge.
METRO (CP.METRO): the smooth elevated loop, round piers, cyan edge lights, stations, lit trains.
PORT (CP.PORT): the rail terminus on a coast stretch away from the drowned quarter: a raised terminal platform with a
quay wall, container stacks, rail yard tracks, ship-to-shore gantry cranes along the quay, ships moored outside, masts.
"""


class Path:
    """a polyline in world BU with arc length; at(s) -> (point, unit tangent)."""

    def __init__(self, pts_lots, closed=False):
        P = [W(p) for p in pts_lots]
        if closed:
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


def deck(path, zf, width, conc, edge_col, edge_k, step=3.0, thick=1.3, parapet=0.55):
    """an elevated deck along a path: slabs, soffit, side girders, parapet edge lights (z from zf(s))."""
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
            if round_:
                cyl(SURF, c[0], c[1], 0.0, z_ - thick, size, 8, sc(conc, 0.85))
            else:
                box(SURF, c[0] - size, c[1] - size, 0.0, c[0] + size, c[1] + size, z_ - thick, sc(conc, 0.9))
        s += step


def lanes_traffic(path, zf, lanes, rng, slen, gap, thin=None, w=0.2):
    """traffic draws along a path: lanes = [(offset, colour), ...]; thinning past the map edge if thin is set."""
    n = 0
    for (off, col) in lanes:
        s = -rng.uniform(0, 10)
        while s < path.L:
            ln = rng.uniform(*slen)
            g_ = rng.uniform(*gap)
            kk = rng.uniform(0.6, 1.3)
            kr = rng.random()
            sa, sb = max(0.0, s), min(path.L, s + ln)
            fall = 1.0
            if thin:
                cm, _ = path.at((sa + sb) / 2)
                lmx, lmy = cm[0] / U + CX, -cm[1] / U + CY
                fall = math.exp(-max(0.0, abs(lmx - CX) + abs(lmy - CY) - L1_EDGE) / thin)
            if sb > sa + 0.5 and kr < fall:
                ss = sa
                while ss < sb - 0.05:
                    se = min(sb, ss + 3.0)
                    traffic(path.off(ss, off), path.off(se, off), zf((ss + se) / 2) + 0.15, col, kk * (0.4 + 0.6 * fall), w=w)
                    ss = se
                n += 1
            s += ln + g_
    return n


HWY = CP.HIGHWAY
RH = random.Random(CP.SEEDS["streaks"] + 21)
HW_CONC = (0.34, 0.33, 0.32)
HW_LANES = ((HWY["lane_off"][0], (1.0, 0.93, 0.82)), (HWY["lane_off"][1], (1.0, 0.86, 0.62)),
            (-HWY["lane_off"][0], (1.0, 0.1, 0.06)), (-HWY["lane_off"][1], (1.0, 0.16, 0.07)))

# ------------------------------------------------------------------ the Meridian hub: a ground truck ring road
n_tr = 0
if O.get("hub"):
    HB = CP.HUB
    hubp = Path(O["hub"]["pts"], closed=True)
    hz0 = lambda s: 0.12                                            # noqa: E731
    s = 0.0
    hw = HB["w"] / 2.0
    while s < hubp.L - 1e-3:
        s2 = min(hubp.L, s + 3.0)
        a0, a1, b0, b1 = hubp.off(s, -hw), hubp.off(s, hw), hubp.off(s2, -hw), hubp.off(s2, hw)
        GROUND.face([(a0[0], a0[1], 0.06), (b0[0], b0[1], 0.06), (b1[0], b1[1], 0.06), (a1[0], a1[1], 0.06)], (0.07, 0.07, 0.075))
        for sd in (-1, 1):
            e0, e1 = hubp.off(s, sd * (hw - 0.2)), hubp.off(s2, sd * (hw - 0.2))
            strip(NEON, e0, e1, 0.14, 0.08, sc((1.0, 0.75, 0.4), 0.35))
        s = s2
    s = 4.0
    while s < hubp.L:                                               # kerb lamps on both sides
        for sd in (-1, 1):
            c = hubp.off(s, sd * (hw + 0.4))
            bar(SURF, (c[0], c[1], 0.0), (c[0], c[1], 2.4), 0.12, (0.3, 0.3, 0.32))
            box(NEON, c[0] - 0.2, c[1] - 0.2, 2.3, c[0] + 0.2, c[1] + 0.2, 2.6, HWY["lamp_col"])
        s += 9.0
    lanes = ((HB["lanes"][0], (1.0, 0.93, 0.82)), (HB["lanes"][1], (1.0, 0.8, 0.5)), (-HB["lanes"][0], (1.0, 0.1, 0.06)), (-HB["lanes"][1], (1.0, 0.2, 0.08)))
    n_tr += lanes_traffic(hubp, hz0, lanes, RH, (5.0, 18.0), (1.0, 8.0), w=0.3)

# ------------------------------------------------------------------ through highways (pass alongside the hub), the perimeter ring, ramps
ROAD_Z = {}                                                          # name -> (Path, z function): the ramps read the deck heights


def road_furniture(hp_, hz, width):
    """deck, piers, lamp masts (sodium heads) for one elevated road."""
    deck(hp_, hz, width, HW_CONC, HWY["edge_col"], HWY["edge_k"])
    piers(hp_, hz, HWY["pier_step"], 0.8, HW_CONC)
    s = HWY["lamp_step"] / 2
    while s < hp_.L:
        c, d_ = hp_.at(s)
        z_ = hz(s)
        if z_ > 2.0:
            bar(SURF, (c[0], c[1], z_), (c[0], c[1], z_ + 2.6), 0.12, (0.3, 0.3, 0.32))
            for sd in (-1, 1):
                q_ = hp_.off(s, sd * 0.7)
                box(NEON, q_[0] - 0.18, q_[1] - 0.18, z_ + 2.4, q_[0] + 0.18, q_[1] + 0.18, z_ + 2.6, HWY["lamp_col"])
        s += HWY["lamp_step"]


for _hw in O.get("highways", []):
    hp_ = Path(_hw["pts"])
    zt = _hw["z"]
    Lh = hp_.L
    ramp = HWY["ramp"] * 1.6

    def hz(s, zt=zt, Lh=Lh, ramp=ramp, port=_hw.get("to_port")):
        t = min(1.0, s / ramp)
        if port:                                                    # the port spur comes down into the yard
            t = min(t, (Lh - s) / ramp)
        else:
            t = min(t, (Lh - s) / HWY["ramp"])
        t = max(0.0, t)
        return 0.3 + (zt - 0.3) * t * t * (3 - 2 * t)
    ROAD_Z[_hw["name"]] = (hp_, hz)
    road_furniture(hp_, hz, HWY["width"])
    n_tr += lanes_traffic(hp_, hz, HW_LANES, RH, HWY["streak_len"], HWY["gap"], thin=HWY["thin"])
if O.get("ring"):                                                   # the perimeter ring: a closed deck round the city core
    RGo = O["ring"]
    rp_ = Path(RGo["pts"], closed=True)
    rz_ = RGo["z"]
    rzf = lambda s: rz_                                             # noqa: E731
    ROAD_Z["ring"] = (rp_, rzf)
    deck(rp_, rzf, HWY["width"] + 0.6, HW_CONC, HWY["edge_col"], HWY["edge_k"])
    piers(rp_, rzf, HWY["pier_step"], 0.8, HW_CONC)
    s = HWY["lamp_step"] / 2
    while s < rp_.L:
        c, d_ = rp_.at(s)
        bar(SURF, (c[0], c[1], rz_), (c[0], c[1], rz_ + 2.6), 0.12, (0.3, 0.3, 0.32))
        for sd in (-1, 1):
            q_ = rp_.off(s, sd * 0.7)
            box(NEON, q_[0] - 0.18, q_[1] - 0.18, rz_ + 2.4, q_[0] + 0.18, q_[1] + 0.18, rz_ + 2.6, HWY["lamp_col"])
        s += HWY["lamp_step"]
    n_tr += lanes_traffic(rp_, rzf, HW_LANES, RH, HWY["streak_len"], HWY["gap"], thin=None)

# ---- R2 the ramps: curved one-way decks between two roads (hub / ground at z 0.12), edge lights, lamps, traffic, and a slip
# (speed-change) lane alongside the road at each end on an elevated deck
RMP = CP.RAMPS


def road_z_at(name, pt_lot):
    if name not in ROAD_Z:
        return 0.12, None
    p_, zf_ = ROAD_Z[name]
    x_, y_ = W(pt_lot)
    best = min(range(0, int(p_.L) + 1), key=lambda s: (math.hypot(p_.at(s)[0][0] - x_, p_.at(s)[0][1] - y_), s))
    return zf_(best), best


RR = random.Random(CP.SEEDS["streaks"] + 41)
n_ramp = 0
for rm in O.get("ramps", []):
    rp = Path(rm["pts"])
    if rp.L < 6.0:
        continue
    z0, s0r = road_z_at(rm["ends"][0], rm["pts"][0])
    z1, s1r = road_z_at(rm["ends"][1], rm["pts"][-1])

    def rzf(s, z0=z0, z1=z1, L_=rp.L):
        t = min(1.0, max(0.0, s / L_))
        return z0 + (z1 - z0) * t * t * (3 - 2 * t)
    deck(rp, rzf, RMP["w"], HW_CONC, HWY["edge_col"], HWY["edge_k"] * 0.8, step=3.0, thick=RMP["thick"], parapet=0.35)
    piers(rp, rzf, 8.0, 0.45, HW_CONC, thick=RMP["thick"])
    s = RMP["lamp_step"] / 2
    k_ = 0
    while s < rp.L:
        c, d_ = rp.at(s)
        z_ = rzf(s)
        if z_ > 1.5:
            q_ = rp.off(s, (1 if k_ % 2 else -1) * (RMP["w"] / 2 - 0.1))
            bar(SURF, (q_[0], q_[1], z_), (q_[0], q_[1], z_ + 2.0), 0.1, (0.3, 0.3, 0.32))
            box(NEON, q_[0] - 0.16, q_[1] - 0.16, z_ + 1.9, q_[0] + 0.16, q_[1] + 0.16, z_ + 2.1, HWY["lamp_col"])
        k_ += 1
        s += RMP["lamp_step"]
    n_tr += lanes_traffic(rp, rzf, ((0.6, (1.0, 0.9, 0.7)), (-0.6, (1.0, 0.55, 0.3))), RR, (4.0, 12.0), (3.0, 16.0), w=0.18)
    # slip lanes at the ends on elevated roads
    for (nm_, s_e, at_start) in ((rm["ends"][0], s0r, True), (rm["ends"][1], s1r, False)):
        if nm_ not in ROAD_Z or s_e is None:
            continue
        rd, rzfn = ROAD_Z[nm_]
        pe, te = rd.at(s_e)
        sr = 0.0 if at_start else rp.L
        pr, dr = rp.at(min(max(sr + (6.0 if at_start else -6.0), 0.0), rp.L))
        fwd = 1.0 if (dr[0] * te[0] + dr[1] * te[1]) >= 0 else -1.0       # the ramp's travel direction vs the road's
        side = 1.0 if ((pr[0] - pe[0]) * (-te[1]) + (pr[1] - pe[1]) * te[0]) > 0 else -1.0
        a_s, b_s = (s_e - fwd * RMP["lane_len"], s_e) if at_start else (s_e, s_e + fwd * RMP["lane_len"])
        lo, hi = (a_s, b_s) if a_s < b_s else (b_s, a_s)
        off0 = HWY["width"] / 2.0 + RMP["lane_w"] / 2.0 + 0.05
        ss = lo
        while ss < hi - 1e-3:
            se = min(hi, ss + 3.0)
            za, zb = rzfn(ss), rzfn(se)
            if rd.closed is False and (ss < 0 or se > rd.L):
                ss = se
                continue
            a0, a1 = rd.off(ss, side * (off0 - RMP["lane_w"] / 2)), rd.off(ss, side * (off0 + RMP["lane_w"] / 2))
            b0, b1 = rd.off(se, side * (off0 - RMP["lane_w"] / 2)), rd.off(se, side * (off0 + RMP["lane_w"] / 2))
            SURF.face([(a0[0], a0[1], za), (b0[0], b0[1], zb), (b1[0], b1[1], zb), (a1[0], a1[1], za)], HW_CONC)
            SURF.face([(a0[0], a0[1], za - 0.9), (a1[0], a1[1], za - 0.9), (b1[0], b1[1], zb - 0.9), (b0[0], b0[1], zb - 0.9)], sc(HW_CONC, 0.6))
            f0, f1 = rd.off(ss, side * (off0 + RMP["lane_w"] / 2 - 0.08)), rd.off(se, side * (off0 + RMP["lane_w"] / 2 - 0.08))
            bar(NEON, (f0[0], f0[1], za + 0.2), (f1[0], f1[1], zb + 0.2), 0.12, sc(HWY["edge_col"], HWY["edge_k"]))
            ss = se
    n_ramp += 1
print("RING + ROADS", len(ROAD_Z), "ramps", n_ramp, "traffic draws", n_tr, "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ the elevated METRO loop (smooth)
MT = CP.METRO
if O.get("metro"):
    mpath = Path(O["metro"]["pts"], closed=O["metro"].get("closed", True))
    MCONC = (0.40, 0.40, 0.42)
    mz = MT["z"]
    mzf = lambda s: mz                                              # noqa: E731
    deck(mpath, mzf, MT["width"], MCONC, MT["edge_col"], MT["edge_k"], thick=0.9, parapet=0.25)
    for sd in (-1, 1):
        s = 0.0
        while s < mpath.L - 1e-3:
            s2 = min(mpath.L, s + 3.0)
            a_, b_ = mpath.off(s, sd * 0.55), mpath.off(s2, sd * 0.55)
            bar(SURF, (a_[0], a_[1], mz + 0.1), (b_[0], b_[1], mz + 0.1), 0.1, (0.55, 0.55, 0.6))
            s = s2
    piers(mpath, mzf, MT["pier_step"], 0.5, MCONC, thick=0.9, round_=True)
    Ls, Ws = MT["station"]
    mw = MT["width"] / 2.0
    for st in O["metro"]["stations"]:
        sx, sy = W(st)
        s_best = min(range(0, int(mpath.L), 2), key=lambda s: (round(math.hypot(mpath.at(s)[0][0] - sx, mpath.at(s)[0][1] - sy), 3), s))
        (sx, sy), (mux, muy) = mpath.at(s_best)
        mnx, mny = -muy, mux
        for sd in (-1, 1):
            cx_, cy_ = sx + mnx * sd * (mw + 0.9), sy + mny * sd * (mw + 0.9)
            q_ = [(cx_ - mux * Ls / 2 - mnx * 0.9, cy_ - muy * Ls / 2 - mny * 0.9), (cx_ + mux * Ls / 2 - mnx * 0.9, cy_ + muy * Ls / 2 - mny * 0.9),
                  (cx_ + mux * Ls / 2 + mnx * 0.9, cy_ + muy * Ls / 2 + mny * 0.9), (cx_ - mux * Ls / 2 + mnx * 0.9, cy_ - muy * Ls / 2 + mny * 0.9)]
            prism(SURF, q_, mz - 0.9, mz + 0.1, MCONC)
            bar(NEON, (cx_ - mux * Ls / 2, cy_ - muy * Ls / 2, mz + 0.15), (cx_ + mux * Ls / 2, cy_ + muy * Ls / 2, mz + 0.15), 0.25,
                sc((1.0, 0.92, 0.75), 0.8))
        hw_ = Ws / 2 * 1.4
        q_ = [(sx - mux * Ls / 2 - mnx * hw_, sy - muy * Ls / 2 - mny * hw_), (sx + mux * Ls / 2 - mnx * hw_, sy + muy * Ls / 2 - mny * hw_),
              (sx + mux * Ls / 2 + mnx * hw_, sy + muy * Ls / 2 + mny * hw_), (sx - mux * Ls / 2 + mnx * hw_, sy - muy * Ls / 2 + mny * hw_)]
        prism(SURF, q_, mz + 3.4, mz + 3.8, (0.62, 0.64, 0.68))
        for i in range(4):
            bar(NEON, (q_[i][0], q_[i][1], mz + 3.35), (q_[(i + 1) % 4][0], q_[(i + 1) % 4][1], mz + 3.35), 0.16, sc(MT["edge_col"], 1.0))
    RMt = random.Random(CP.SEEDS["streaks"] + 31)
    for k_ in range(MT["trains"]):
        s_head = mpath.L * (k_ + RMt.uniform(0.1, 0.6)) / MT["trains"]
        for cc in range(MT["cars"]):
            sa = s_head - cc * (MT["car_len"] + 0.35)
            for piece in range(3):
                pa, d_ = mpath.at(sa - piece * MT["car_len"] / 3)
                pb, _ = mpath.at(sa - (piece + 1) * MT["car_len"] / 3)
                bar(SURF, (pa[0], pa[1], mz + 0.95), (pb[0], pb[1], mz + 0.95), 1.6, (0.78, 0.80, 0.84))
                tnx, tny = -d_[1], d_[0]
                for sd in (-1, 1):
                    bar(NEON, (pa[0] + tnx * sd * 0.82, pa[1] + tny * sd * 0.82, mz + 1.15), (pb[0] + tnx * sd * 0.82, pb[1] + tny * sd * 0.82, mz + 1.15),
                        0.42, sc(MT["train_col"], 1.5))
    print("METRO %.0f BU, %d stations" % (mpath.L, len(O["metro"]["stations"])), flush=True)

# ------------------------------------------------------------------ the PORT (the freight terminus)
if O.get("port"):
    PT = O["port"]
    PZ = CP.PORT["z"]
    RPo = random.Random(CP.SEEDS["landmark"] + 77)
    CCP = [(0.72, 0.30, 0.08), (0.58, 0.22, 0.08), (0.14, 0.36, 0.38), (0.45, 0.42, 0.40), (0.80, 0.46, 0.10), (0.62, 0.12, 0.08),
           (0.20, 0.30, 0.50), (0.85, 0.80, 0.70)]
    A0p, A1p = PT["a0"], PT["a1"]
    na_ = 40
    # the raised platform: yard + quay, a quay wall down to the sea bed on the water side, a retaining face landward
    for k in range(na_):
        a0_, a1_ = A0p + (A1p - A0p) * k / na_, A0p + (A1p - A0p) * (k + 1) / na_
        q_ = [w_ab(a0_, bwall(a0_) - PT["depth"]), w_ab(a1_, bwall(a1_) - PT["depth"]), w_ab(a1_, bwall(a1_) + PT["quay"]),
              w_ab(a0_, bwall(a0_) + PT["quay"])]
        prism(SURF, q_, -s0, PZ, (0.36, 0.35, 0.33), top_col=(0.30, 0.29, 0.28), wet=0)
        e0, e1 = w_ab(a0_, bwall(a0_) + PT["quay"] - 0.03), w_ab(a1_, bwall(a1_) + PT["quay"] - 0.03)
        bar(NEON, (e0[0], e0[1], PZ - 0.4), (e1[0], e1[1], PZ - 0.4), 0.25, sc((1.0, 0.7, 0.3), 0.6))
    # the end walls of the platform (the seawall meets it)
    for a_e in (A0p, A1p):
        q_ = [w_ab(a_e - 0.4, bwall(a_e) - 0.2), w_ab(a_e + 0.4, bwall(a_e) - 0.2), w_ab(a_e + 0.4, bwall(a_e) + PT["quay"] + 0.6),
              w_ab(a_e - 0.4, bwall(a_e) + PT["quay"] + 0.6)]
        prism(SURF, q_, WALL_Z0, WAT["wall_h"], (0.30, 0.31, 0.35))

    def pab(a_, db_):
        """a point on the platform: across a, db lots landward (-) / seaward (+) of the wall line."""
        return w_ab(a_, bwall(a_) + db_)
    # container stacks: rows parallel to the quay in the yard, blocks with aisles, 1-4 high
    for row in range(CP.PORT["stack_rows"]):
        db_ = -PT["depth"] + 3.2 + row * 1.25
        if db_ > PT["quay"] - 2.6:
            break
        a_ = A0p + 1.5
        while a_ < A1p - 2.0:
            if RPo.random() < 0.12:
                a_ += 1.2
                continue
            for lane in (-0.17, 0.0, 0.17):          # a block three containers wide
                c0, c1 = pab(a_, db_ + lane), pab(a_ + 0.42, db_ + lane)
                dx, dy = c1[0] - c0[0], c1[1] - c0[1]
                L_ = math.hypot(dx, dy)
                ux_, uy_ = dx / L_, dy / L_
                nx_, ny_ = -uy_, ux_
                for lv in range(RPo.randint(1, 4)):
                    z0_ = PZ + lv * 0.95
                    q_ = [(c0[0] - nx_ * 0.45, c0[1] - ny_ * 0.45), (c0[0] + ux_ * 2.4 - nx_ * 0.45, c0[1] + uy_ * 2.4 - ny_ * 0.45),
                          (c0[0] + ux_ * 2.4 + nx_ * 0.45, c0[1] + uy_ * 2.4 + ny_ * 0.45), (c0[0] + nx_ * 0.45, c0[1] + ny_ * 0.45)]
                    prism(SURF, q_, z0_, z0_ + 0.9, RPo.choice(CCP))
            a_ += 2.6 / U * 1.0 + 0.02
    # rail yard tracks along the landward edge (the line arrives here)
    for k in range(4):
        db_ = -PT["depth"] + 1.0 + k * 0.45
        prev = None
        for m in range(41):
            a_ = A0p + 2.0 + (A1p - A0p - 4.0) * m / 40
            p_ = pab(a_, db_)
            if prev:
                bar(SURF, (prev[0], prev[1], PZ + 0.12), (p_[0], p_[1], PZ + 0.12), 0.35, (0.42, 0.40, 0.38))
            prev = p_
        for m in range(3):                       # waiting wagons
            a_ = A0p + 6.0 + RPo.uniform(0, A1p - A0p - 16.0)
            pa_, pb_ = pab(a_, db_), pab(a_ + 3.0, db_)
            bar(SURF, (pa_[0], pa_[1], PZ + 1.0), (pb_[0], pb_[1], PZ + 1.0), 1.3, RPo.choice(CCP))
    # ship-to-shore gantry cranes along the quay: legs straddling the quay edge, the boom out over the ships
    CR = (0.92, 0.40, 0.08)
    CRW = (0.88, 0.88, 0.86)
    ncr = CP.PORT["cranes"]
    for k in range(ncr):
        a_ = A0p + 3.0 + (A1p - A0p - 6.0) * (k + 0.5) / ncr
        col_ = CR if k % 2 == 0 else CRW
        legs = []
        for da_ in (-0.9, 0.9):
            for db_ in (PT["quay"] - 3.2, PT["quay"] - 0.6):
                p_ = pab(a_ + da_, db_)
                legs.append(p_)
                bar(SURF, (p_[0], p_[1], PZ), (p_[0], p_[1], PZ + 24.0), 0.9, col_)
        for i, j in ((0, 2), (1, 3), (0, 1), (2, 3)):
            bar(SURF, (legs[i][0], legs[i][1], PZ + 24.0), (legs[j][0], legs[j][1], PZ + 24.0), 0.9, col_)
            bar(SURF, (legs[i][0], legs[i][1], PZ + 8.0), (legs[j][0], legs[j][1], PZ + 8.0), 0.6, col_)
        bo0, bo1 = pab(a_, PT["quay"] - 6.5), pab(a_, PT["quay"] + 6.5)          # the boom: landward tail .. seaward tip
        bar(SURF, (bo0[0], bo0[1], PZ + 26.0), (bo1[0], bo1[1], PZ + 26.0), 1.2, col_)
        apx = pab(a_, PT["quay"] - 1.9)
        bar(SURF, (legs[0][0], legs[0][1], PZ + 24.0), (apx[0], apx[1], PZ + 33.0), 0.5, col_)
        bar(SURF, (legs[3][0], legs[3][1], PZ + 24.0), (apx[0], apx[1], PZ + 33.0), 0.5, col_)
        bar(SURF, (apx[0], apx[1], PZ + 33.0), (bo1[0], bo1[1], PZ + 26.6), 0.25, (0.3, 0.3, 0.32))
        cab = pab(a_, PT["quay"] + 1.5)
        box(SURF, cab[0] - 1.0, cab[1] - 1.0, PZ + 23.0, cab[0] + 1.0, cab[1] + 1.0, PZ + 25.4, (0.82, 0.82, 0.80), wc=(1.0, 0.85, 0.6), wl=0.9, wm=0, bid=0.5)
        box(NEON, apx[0] - 0.4, apx[1] - 0.4, PZ + 33.0, apx[0] + 0.4, apx[1] + 0.4, PZ + 33.7, (1.0, 0.08, 0.06))
        box(NEON, bo1[0] - 0.4, bo1[1] - 0.4, PZ + 26.6, bo1[0] + 0.4, bo1[1] + 0.4, PZ + 27.2, (1.0, 0.55, 0.15))
        hk = pab(a_, PT["quay"] + 4.0 + (k % 3))                     # a container on the spreader
        bar(SURF, (hk[0], hk[1], PZ + 25.4), (hk[0], hk[1], PZ + 14.0), 0.12, (0.2, 0.2, 0.22))
        box(SURF, hk[0] - 1.2, hk[1] - 0.45, PZ + 12.6, hk[0] + 1.2, hk[1] + 0.45, PZ + 14.0, RPo.choice(CCP))
    # ships moored along the quay (hull, superstructure at the stern, deck stacks)
    nsh = CP.PORT["ships"]
    for k in range(nsh):
        a_c = A0p + (A1p - A0p) * (k + 0.5) / nsh + RPo.uniform(-1.0, 1.0)
        Ls_ = RPo.uniform(9.5, 12.5) * 0.5                           # half length in lots (along a)
        bm_ = 1.15                                                   # half beam (lots)
        db_c = PT["quay"] + bm_ + 0.35
        hull = []
        for m in range(13):
            t = -1.0 + 2.0 * m / 12
            taper = 1.0 if t < 0.7 else max(0.15, 1.0 - (t - 0.7) / 0.3 * 0.85)
            hull.append((t * Ls_, taper))
        top = [pab(a_c + u, db_c + bm_ * tp) for (u, tp) in hull] + [pab(a_c + u, db_c - bm_ * tp) for (u, tp) in reversed(hull)]
        hcol = RPo.choice([(0.16, 0.18, 0.22), (0.45, 0.10, 0.08), (0.10, 0.20, 0.30)])
        prism(SURF, top, ZW - 4.0, ZW + 4.5, hcol, top_col=(0.30, 0.30, 0.30), wet=1)
        br = [pab(a_c - Ls_ * 0.92, db_c - bm_ * 0.9), pab(a_c - Ls_ * 0.72, db_c - bm_ * 0.9), pab(a_c - Ls_ * 0.72, db_c + bm_ * 0.9),
              pab(a_c - Ls_ * 0.92, db_c + bm_ * 0.9)]
        prism(SURF, br, ZW + 4.5, ZW + 15.0, (0.85, 0.85, 0.83), wc=(1.0, 0.86, 0.6), wl=0.6, wm=0, bid=0.2 + k * 0.1)
        u_ = -Ls_ * 0.66
        while u_ < Ls_ * 0.6:                                         # deck stacks (bays across the beam)
            for lane in (-0.6, 0.0, 0.6):
                for lv in range(RPo.randint(1, 4)):
                    c0 = pab(a_c + u_, db_c + lane * bm_)
                    c1 = pab(a_c + u_ + 0.4, db_c + lane * bm_)
                    dx, dy = c1[0] - c0[0], c1[1] - c0[1]
                    L_ = math.hypot(dx, dy)
                    ux_, uy_ = dx / L_, dy / L_
                    nx_, ny_ = -uy_, ux_
                    z0_ = ZW + 4.5 + lv * 0.95
                    q_ = [(c0[0] - nx_ * 1.2, c0[1] - ny_ * 1.2), (c0[0] + ux_ * 2.3 - nx_ * 1.2, c0[1] + uy_ * 2.3 - ny_ * 1.2),
                          (c0[0] + ux_ * 2.3 + nx_ * 1.2, c0[1] + uy_ * 2.3 + ny_ * 1.2), (c0[0] + nx_ * 1.2, c0[1] + ny_ * 1.2)]
                    prism(SURF, q_, z0_, z0_ + 0.9, RPo.choice(CCP))
            u_ += 0.45
        mast = pab(a_c - Ls_ * 0.82, db_c)
        box(NEON, mast[0] - 0.3, mast[1] - 0.3, ZW + 15.0, mast[0] + 0.3, mast[1] + 0.3, ZW + 15.6, (1.0, 0.95, 0.85))
    # light masts round the yard (sodium heads)
    for k in range(9):
        a_ = A0p + 2.0 + (A1p - A0p - 4.0) * k / 8
        p_ = pab(a_, -PT["depth"] * 0.5)
        bar(SURF, (p_[0], p_[1], PZ), (p_[0], p_[1], PZ + 16.0), 0.35, (0.4, 0.4, 0.42))
        box(NEON, p_[0] - 0.7, p_[1] - 0.7, PZ + 16.0, p_[0] + 0.7, p_[1] + 0.7, PZ + 16.5, (1.0, 0.65, 0.3))
        if not DAYM:
            LIGHT_SPOTS.append(dict(loc=(p_[0], p_[1], PZ + 16.0), tgt=(p_[0], p_[1], PZ), col=(1.0, 0.7, 0.4), power=6.0e4, cone=110.0,
                                    blend=0.6, k=1.0))
    print("PORT a %.0f..%.0f, %d cranes, %d ships" % (A0p, A1p, ncr, nsh), flush=True)
