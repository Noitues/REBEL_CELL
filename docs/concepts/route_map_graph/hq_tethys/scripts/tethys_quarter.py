"""hq_tethys: the drowned quarter's DAM, the DOCK LOCK and causeway, and the drowned-street clutter.

Two layers:
  * pure Python (no bpy): Frame (lots <-> world, the bay wall), dam_line() (the dam polyline from the zoning data),
    prep_zoned() (removes the buildings the dam, the lock and the causeway stand on; optional occlusion cut);
  * builders that write into a city_all_corps build namespace `ns` (the exec namespace of city_build.py, after
    city_world.py ran): build_dam(ns), build_clutter(ns). They only call ns's accumulators (SURF, SMOOTH, NEON, GLASS,
    WATER, SEABED, GROUND) and spot_at, so they run in any build that has them.

Rules (all numbers in tethys_preset):
  DAM LINE  the drowned quarter's land boundary = wet cell edges that face a dry cell landward of the seawall; for each
            a step the minimum b within +-win, then a moving-average smooth; it ends where the boundary meets the coast
  PROFILE   vertical wet face down into the water; crest road between parapets at crest_z; a stepped dry face (upper
            slope, berm catwalk, lower slope) down to the toe; counterfort ribs on the lower slope every rib_step
  GATES     a sluice gate bay every gate_step of arc (not near the lock or the ends); every gate_open_every-th is open
            (white water down a spillway chute into the toe canal); every pump_every-th carries a pump house + penstocks
  LOCK      the DOCK LOCK on the HQ's axis (the dam point nearest the HQ): a chamber through the dam, mitre gates at both
            ends, a control tower, a dock basin on the dry side; the causeway runs from its upper gate to the HQ lot
  CLUTTER   per drowned street tile (seeded by the tile): kerbs, dashed lanes, cars (some flipped, a few with a dead
            man's headlight still lit), street lamps (some lit, some leaning), signs and billboards, debris,
            containers and buses, kelp cables with photophore tips; per drowned building face: shop fronts and blade signs
"""
import json
import math
import random

import tethys_preset as TP
from tkit import catenary, cap, frustum, local_box, loft, obox, seg_box, slab, tube, unit2

R2 = math.sqrt(2)


class Frame:
    """lots <-> world BU, the (a, b) map frame and the bay wall (city_build's conventions)."""

    def __init__(self, O, U=6.0):
        self.O, self.U = O, U
        self.CX, self.CY = O["centre"]
        self.BC, self.BAY = O["b_coast"], O["bay"]

    def W(self, p):
        return ((p[0] - self.CX) * self.U, -(p[1] - self.CY) * self.U)

    def ab_lot(self, lx, ly):
        dx, dy = lx - self.CX, ly - self.CY
        return (dx - dy) / R2, -(dx + dy) / R2

    def ab_w(self, x, y):
        return self.ab_lot(x / self.U + self.CX, -y / self.U + self.CY)

    def w_ab(self, a, b):
        return self.W((self.CX + (a - b) / R2, self.CY + (-a - b) / R2))

    def bwall(self, a):
        B = self.BAY
        v = self.BC + B["depth"] * math.exp(-((a - B["ac"]) / B["width"]) ** 2)
        if abs(a - B["ac"]) > B["head_start"]:
            v += B["head_k"] * (abs(a - B["ac"]) - B["head_start"]) ** 2
        return v


def dam_line(O, D=None):
    """-> dict(P [(x, y)] world, N [(nx, ny)] unit toward the water, T tangents, S arc length, A the a per point)."""
    D = D or TP.DAM
    F = Frame(O)
    S = {(c[0], c[1]) for c in O["lagoon_cells"]}
    edges = []
    for (i, j) in sorted(S):
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            if (i + di, j + dj) in S:
                continue
            a_, b_ = F.ab_lot(i + di + 0.5, j + dj + 0.5)
            if b_ > F.bwall(a_) - 0.5:
                continue
            # the edge midpoint (between the wet cell and its dry neighbour)
            edges.append(F.ab_lot(i + 0.5 + di * 0.5, j + 0.5 + dj * 0.5))
    a0, a1 = D["a_range"]
    A, B = [], []
    a = a0
    while a <= a1 + 1e-6:
        near = [e[1] for e in edges if abs(e[0] - a) <= D["win"]]
        if near:
            A.append(a)
            B.append(min(near))
        a += D["a_step"]
    for _ in range(2):                                  # moving-average smooth (rounds the corners of the U)
        m = D["smooth"]
        B = [sum(B[max(0, k - m):k + m + 1]) / len(B[max(0, k - m):k + m + 1]) for k in range(len(B))]
    P = [F.w_ab(a_, b_) for a_, b_ in zip(A, B)]
    T, N = [], []
    for k in range(len(P)):
        p0, p1 = P[max(0, k - 1)], P[min(len(P) - 1, k + 1)]
        tx, ty = unit2(p1[0] - p0[0], p1[1] - p0[1])
        nx, ny = -ty, tx
        q0, q1 = F.w_ab(A[k], B[k]), F.w_ab(A[k], B[k] + 1.0)          # +b = toward the water
        if nx * (q1[0] - q0[0]) + ny * (q1[1] - q0[1]) < 0:
            nx, ny = -nx, -ny
        T.append((tx, ty))
        N.append((nx, ny))
    Sx = [0.0]
    for k in range(1, len(P)):
        Sx.append(Sx[-1] + math.hypot(P[k][0] - P[k - 1][0], P[k][1] - P[k - 1][1]))
    return dict(P=P, N=N, T=T, S=Sx, A=A, B=B)


def signed_dist(L, x, y):
    """(d, s): signed distance (BU, + toward the water) from the dam line, and the arc position of the nearest point;
    d is None past the line's ends."""
    best = None
    P, N = L["P"], L["N"]
    for k in range(len(P) - 1):
        ax, ay = P[k]
        bx, by = P[k + 1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy or 1.0
        t = ((x - ax) * dx + (y - ay) * dy) / L2
        if t < -0.05 or t > 1.05:
            continue
        t = min(1.0, max(0.0, t))
        px, py = ax + dx * t, ay + dy * t
        dd = math.hypot(x - px, y - py)
        if best is None or dd < best[0]:
            nx = N[k][0] + (N[k + 1][0] - N[k][0]) * t
            ny = N[k][1] + (N[k + 1][1] - N[k][1]) * t
            sgn = 1.0 if (x - px) * nx + (y - py) * ny >= 0 else -1.0
            best = (dd, sgn * dd, L["S"][k] + math.sqrt(L2) * t)
    if best is None:
        return None, None
    return best[1], best[2]


def lock_pose(O, L):
    """The DOCK LOCK: the dam point nearest the HQ. -> dict(k, P, N, T, s)."""
    F = Frame(O)
    hx, hy = F.W(O["hq"]["tethys"])
    k = min(range(len(L["P"])), key=lambda i: (math.hypot(L["P"][i][0] - hx, L["P"][i][1] - hy), i))
    return dict(k=k, P=L["P"][k], N=L["N"][k], T=L["T"][k], s=L["S"][k], hq=(hx, hy))


def causeway(O, L, lk=None):
    """The causeway: from the lock's upper gate to the HQ lot edge (world p0, p1)."""
    lk = lk or lock_pose(O, L)
    D, PR = TP.DAM, TP.PIER
    p0 = (lk["P"][0] + lk["N"][0] * (D["wet"] + 0.4), lk["P"][1] + lk["N"][1] * (D["wet"] + 0.4))
    hx, hy = lk["hq"]
    ux, uy = unit2(hx - p0[0], hy - p0[1])
    # it lands on the end pod of the pier that points at the lock (tethys_landmark: arm 0 aims at the lock)
    Lc = math.hypot(hx - p0[0], hy - p0[1]) - (PR["outer"]["r"] + PR["main"]["skirt"][1] * PR["outer"]["s"] - 0.6)
    return p0, (p0[0] + ux * Lc, p0[1] + uy * Lc)


def _seg_dist(px, py, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1.0
    t = min(1.0, max(0.0, ((px - a[0]) * dx + (py - a[1]) * dy) / L2))
    return math.hypot(px - a[0] - dx * t, py - a[1] - dy * t)


def reshape_depth(O, KH, P=None):
    """THE DEPTH RULE (tethys_preset.DEPTH): a shallow drowned street grid, the trench only round the station.
    Rewrites the depths of the lagoon cells, wet tiles, wet plazas and wet buildings in place. -> stats."""
    P = P or TP.DEPTH
    F = Frame(O)
    hx, hy = F.W(O["hq"]["tethys"])
    bs = O["b_split"]
    ZW = 2.5

    def new_depth(x, y, orig):
        a, b = F.ab_w(x, y)
        t = min(1.0, max(0.0, (b - bs) / max(1.0, F.bwall(a) - bs)))
        sh = P["shallow"][0] + (P["shallow"][1] - P["shallow"][0]) * t
        d = math.hypot(x - hx, y - hy)
        u = min(1.0, max(0.0, (P["trench_r"] + P["blend"] - d) / P["blend"]))
        w = u * u * (3 - 2 * u)
        return sh + (max(orig, sh) - sh) * w
    for c in O["lagoon_cells"]:
        x, y = F.W((c[0] + 0.5, c[1] + 0.5))
        c[2] = new_depth(x, y, c[2])
    for t in O["tiles"] + O["plazas"]:
        if t.get("wet"):
            q = [F.W(p) for p in t["q"]]
            t["sub"] = new_depth(sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q), t.get("sub", 0.0))
    cut = emerge = 0
    for b in O["buildings"]:
        if not b.get("wet"):
            continue
        q = [F.W(p) for p in b["q"]]
        cx, cy = sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q)
        b["sub"] = new_depth(cx, cy, b.get("sub", 0.0))
        base = b["z0"] * KH - b["sub"]
        top = base + b["h"] * KH
        r = random.Random(TP.SEEDS["clutter"] * 31 + b["key"])
        if top > ZW - P["top_gap"][0]:
            if r.random() < P["emerge"] and math.hypot(cx - hx, cy - hy) > P["clear_r"]:
                emerge += 1
                continue
            b["h"] = max(1.0, (ZW - r.uniform(*P["top_gap"]) - base) / KH)
            cut += 1
    return dict(depth_cut=cut, depth_emerge=emerge)


def prep_zoned(src, dst, occ=None, KH=None):
    """Write a copy of the zoning with the depth rule applied (reshape_depth) and the buildings the dam / lock /
    causeway stand on removed. occ: an optional callable(building_world_dict) -> new height in BU (the overview's
    occlusion cut) or None. -> stats dict."""
    O = json.load(open(src))
    F = Frame(O)
    dstats = reshape_depth(O, KH or O.get("KH"))
    L = dam_line(O)
    lk = lock_pose(O, L)
    c0, c1 = causeway(O, L, lk)
    D, LK = TP.DAM, TP.LOCK
    KH = KH or O.get("KH")
    keep, gone, cut = [], 0, 0
    for b in O["buildings"]:
        q = [F.W(p) for p in b["q"]]
        cx, cy = sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q)
        pts = q + [(cx, cy)] + [((q[i][0] + q[(i + 1) % len(q)][0]) / 2, (q[i][1] + q[(i + 1) % len(q)][1]) / 2) for i in range(len(q))]
        drop = False
        for (x, y) in pts:
            d, _ = signed_dist(L, x, y)
            if d is not None:
                if not b.get("wet") and D["clear_dry"][0] <= d <= D["clear_dry"][1]:
                    drop = True
                if b.get("wet") and -20.0 <= d <= D["clear_wet"]:
                    drop = True
            # the lock + basin zone (local frame of the lock)
            ux = (x - lk["P"][0]) * lk["N"][0] + (y - lk["P"][1]) * lk["N"][1]
            vx = (x - lk["P"][0]) * lk["T"][0] + (y - lk["P"][1]) * lk["T"][1]
            if LK["basin"] - 8.0 <= ux <= D["wet"] + 4.0 and abs(vx) <= LK["basin_w"] / 2 + LK["clear"]:
                drop = True
            if b.get("wet") and _seg_dist(x, y, c0, c1) < TP.CAUSEWAY["w"] + 4.0:
                drop = True
        if drop:
            gone += 1
            continue
        if occ is not None and not b.get("wet"):
            top = b["z0"] * KH + b["h"] * KH
            nh = occ(dict(x=cx, y=cy, top=top, hx=(max(p[0] for p in q) - min(p[0] for p in q)) / 2,
                          hy=(max(p[1] for p in q) - min(p[1] for p in q)) / 2))
            if nh is not None and nh < top - 0.5:
                b["h"] = max(0.5, (nh - b["z0"] * KH) / KH)
                b["occ_cut"] = 1
                cut += 1
        keep.append(b)
    O["buildings"] = keep
    O["tethys_dam"] = dict(P=L["P"], N=L["N"], T=L["T"], S=L["S"], A=L["A"], B=L["B"])
    O["tethys_lock"] = lk
    O["tethys_causeway"] = [c0, c1]
    json.dump(O, open(dst, "w"))
    return dict(removed=gone, occ_cut=cut, kept=len(keep), dam_pts=len(L["P"]), dam_len=L["S"][-1], **dstats)


# ===================================================================== Blender-side builders (ns = the build namespace)
def _dam_from_ns(ns):
    O = ns["O"]
    L = O.get("tethys_dam") or dam_line(O)
    lk = O.get("tethys_lock") or lock_pose(O, L)
    return L, lk


def build_dam(ns):
    """The inner dam, its gates, catwalks, lights, the toe canal and apron, the DOCK LOCK and the causeway.
    Returns dict(lock=room anchor xyz, gates=[xyz], causeway=(p0, p1))."""
    D, LK, CW, PR = TP.DAM, TP.LOCK, TP.CAUSEWAY, TP.PIER
    SURF, SMOOTH, NEON, GLASS, WATER, GROUND = (ns[k] for k in ("SURF", "SMOOTH", "NEON", "GLASS", "WATER", "GROUND"))
    box, bar, ring_line, sc, spot_at = ns["box"], ns["bar"], ns["ring_line"], ns["sc"], ns["spot_at"]
    ZW = ns["ZW"]
    L, lk = _dam_from_ns(ns)
    P, N, T, S, A = L["P"], L["N"], L["T"], L["S"], L["A"]
    rr = random.Random(TP.SEEDS["dam"])
    cz, wet, cd = D["crest_z"], D["wet"], D["crest_dry"]
    b0o, b1o, bz = D["berm"]
    prof = [(D["toe"], -0.3), (D["toe"], 0.0), (b1o, bz), (b0o, bz), (cd, cz), (wet, cz), (wet, D["base_z"])]
    # edge colours: 0 toe lip, 1 lower slope, 2 berm, 3 upper slope, 4 crest, 5 wet face
    cols = [D["conc_dark"], D["conc"], D["conc_dark"], D["conc"], (0.13, 0.13, 0.15), D["conc_dark"]]
    half = LK["w"] / 2 + LK["wall"]
    s_lock = lk["s"]
    # the loft, in two runs either side of the lock chamber
    runs = [[k for k in range(len(P)) if S[k] <= s_lock - half], [k for k in range(len(P)) if S[k] >= s_lock + half]]
    for run in runs:
        if len(run) < 2:
            continue
        Pr, Nr = [P[k] for k in run], [N[k] for k in run]
        loft(SURF, Pr, Nr, prof, lambda e: cols[e], wet_of_edge=lambda e: 1 if e == 5 else 0, s_of=[S[k] for k in run])
        for k in (run[0], run[-1]):
            cap(SURF, P[k], N[k], prof, D["conc"])
        # parapets (both crest edges) and the crest road's dashed centre line
        loft(SURF, Pr, Nr, [(wet - 0.55, cz), (wet - 0.55, cz + D["parapet"]), (wet, cz + D["parapet"])], lambda e: D["conc"])
        loft(SURF, Pr, Nr, [(cd + 0.5, cz), (cd + 0.5, cz + D["parapet"]), (cd, cz + D["parapet"])], lambda e: D["conc"])
        # the wet-face catwalk (cantilevered grating) and its handrail
        loft(SURF, Pr, Nr, [(wet, D["catwalk_z"] - 0.18), (wet + D["catwalk_w"], D["catwalk_z"] - 0.18),
                            (wet + D["catwalk_w"], D["catwalk_z"])], lambda e: D["steel"])
        loft(SURF, Pr, Nr, [(wet + D["catwalk_w"] - 0.05, D["catwalk_z"] + 1.0), (wet + D["catwalk_w"] - 0.05, D["catwalk_z"] + 1.1)],
             lambda e: (0.55, 0.52, 0.30))
        # the berm catwalk handrail (dry face)
        loft(SURF, Pr, Nr, [(b1o + 0.1, bz + 1.0), (b1o + 0.1, bz + 1.1)], lambda e: (0.55, 0.52, 0.30))
        # hazard band along the dry parapet top (amber, low) and the wet-face waterline gauge line (cool)
        loft(NEON, Pr, Nr, [(cd + 0.02, cz + D["parapet"] - 0.12), (cd - 0.02, cz + D["parapet"] - 0.36)],
             lambda e: sc(TP.HAZARD, 0.35))
    # the toe canal, the apron road and their lamps along the whole line (skipping the lock basin)
    for k in range(len(P) - 1):
        if abs(S[k] - s_lock) < LK["basin_w"] / 2 + 2.0:
            continue
        a, c = P[k], P[k + 1]
        na, nc = N[k], N[k + 1]

        def at(p, n, o):
            return (p[0] + n[0] * o, p[1] + n[1] * o)
        c0, c1 = D["canal"]
        q = [at(a, na, c0), at(c, nc, c0), at(c, nc, c1), at(a, na, c1)]
        WATER.face([(x, y, 0.28) for (x, y) in q], (0, 0, 0))
        GROUND.face([(x, y, 0.02) for (x, y) in q], (0.05, 0.06, 0.07))
        for o in (c0, c1):
            p0, p1 = at(a, na, o), at(c, nc, o)
            SURF.face([(p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), (p1[0], p1[1], 0.55), (p0[0], p0[1], 0.55)], D["conc_dark"])
        r0, r1 = c1 - 0.2, D["apron"][1]
        q = [at(a, na, r0), at(c, nc, r0), at(c, nc, r1), at(a, na, r1)]
        GROUND.face([(x, y, 0.025) for (x, y) in q], (0.10, 0.10, 0.11))
        p0, p1 = at(a, na, r1 + 0.3), at(c, nc, r1 + 0.3)
        NEON.face([(p0[0], p0[1], 0.04), (p1[0], p1[1], 0.04), (p1[0], p1[1], 0.06), (p0[0], p0[1], 0.06)], sc(TP.HAZARD, 0.25))
    # lamps, warning lights, ribs, masts along the arc
    gates = []
    n_g = int(S[-1] / D["gate_step"])
    for g in range(n_g):
        s = D["gate_step"] * (g + 0.5)
        if abs(s - s_lock) < 30.0 or s < 14.0 or s > S[-1] - 14.0:
            continue
        gates.append((g, s))
    gate_s = [s for _, s in gates]

    def frame_at(s):
        k = max(0, min(len(P) - 2, next((i for i in range(len(S) - 1) if S[i] <= s <= S[i + 1]), len(P) - 2)))
        t = (s - S[k]) / max(1e-6, S[k + 1] - S[k])
        p = (P[k][0] + (P[k + 1][0] - P[k][0]) * t, P[k][1] + (P[k + 1][1] - P[k][1]) * t)
        n = unit2(N[k][0] + (N[k + 1][0] - N[k][0]) * t, N[k][1] + (N[k + 1][1] - N[k][1]) * t)
        tt = unit2(T[k][0] + (T[k + 1][0] - T[k][0]) * t, T[k][1] + (T[k + 1][1] - T[k][1]) * t)
        a_ = A[k] + (A[k + 1] - A[k]) * t
        return p, n, tt, a_

    def busy(s, pad):
        return abs(s - s_lock) < half + pad or any(abs(s - gs) < D["gate_w"] / 2 + D["pier_w"] + pad for gs in gate_s)

    s = 2.0
    i = 0
    while s < S[-1] - 1.0:
        p, n, t, a_ = frame_at(s)
        if not busy(s, 0.5):
            # amber warning lights on the dry parapet (every lamp_step; every third brighter: the strobe)
            x, y = p[0] + n[0] * (cd + 0.25), p[1] + n[1] * (cd + 0.25)
            k_ = 1.0 if i % 3 == 0 else 0.45
            box(NEON, x - 0.18, y - 0.18, cz + D["parapet"], x + 0.18, y + 0.18, cz + D["parapet"] + 0.32, sc((1.0, 0.55, 0.10), k_))
            if i % 2 == 0:              # cool catwalk lamps on the wet face
                x, y = p[0] + n[0] * (wet + 0.3), p[1] + n[1] * (wet + 0.3)
                box(NEON, x - 0.15, y - 0.15, D["catwalk_z"] + 1.6, x + 0.15, y + 0.15, D["catwalk_z"] + 1.9, (0.80, 0.92, 1.0))
                bar(SURF, (x, y, D["catwalk_z"]), (x, y, D["catwalk_z"] + 1.6), 0.08, D["steel"])
            if i % 3 == 1:              # berm catwalk lamps (sodium)
                x, y = p[0] + n[0] * (b1o + 0.3), p[1] + n[1] * (b1o + 0.3)
                box(NEON, x - 0.14, y - 0.14, bz + 1.1, x + 0.14, y + 0.14, bz + 1.35, sc(TP.SODIUM, 0.8))
            # handrail posts
            for o, zz in ((wet + D["catwalk_w"] - 0.05, D["catwalk_z"]), (b1o + 0.1, bz)):
                x, y = p[0] + n[0] * o, p[1] + n[1] * o
                bar(SURF, (x, y, zz), (x, y, zz + 1.05), 0.07, (0.55, 0.52, 0.30))
        s += D["lamp_step"]
        i += 1
    # counterfort ribs on the lower slope
    s = D["rib_step"] / 2
    while s < S[-1]:
        if not busy(s, 1.0):
            p, n, t, _ = frame_at(s)
            slab(SURF, p, t, n, [(b1o, bz + 0.5), (D["toe"] - D["rib_out"], 0.0), (b1o + 0.6, 0.0)], D["rib_w"], D["conc"])
        s += D["rib_step"]
    # floodlight masts on the crest: a sodium flood aimed down the dry face and onto the apron
    s = D["mast_step"] / 2
    while s < S[-1]:
        p, n, t, a_ = frame_at(s)
        if not busy(s, 2.0):
            x, y = p[0] + n[0] * (cd + 0.9), p[1] + n[1] * (cd + 0.9)
            bar(SURF, (x, y, cz), (x, y, cz + D["mast_h"]), 0.25, D["steel"])
            hx_, hy_ = x - n[0] * 0.8, y - n[1] * 0.8
            box(NEON, hx_ - 0.5, hy_ - 0.5, cz + D["mast_h"], hx_ + 0.5, hy_ + 0.5, cz + D["mast_h"] + 0.5, (1.0, 0.85, 0.62))
            if D["flood_window"][0] <= a_ <= D["flood_window"][1]:
                spot_at((p[0] + n[0] * (D["toe"] - 4.0), p[1] + n[1] * (D["toe"] - 4.0), 2.0), (hx_, hy_, cz + D["mast_h"] + 0.2),
                        TP.SODIUM, D["flood_power"], D["flood_cone"])
        s += D["mast_step"]
    # uplights from the apron road onto the dry face (warm wash; the dam is the lit wall between the city and the water)
    s = D["up_step"] / 2
    while s < S[-1]:
        p, n, t, a_ = frame_at(s)
        if D["up_window"][0] <= a_ <= D["up_window"][1] and abs(s - s_lock) > LK["basin_w"] / 2 + 3.0:
            spot_at((p[0] + n[0] * (b1o + 0.5), p[1] + n[1] * (b1o + 0.5), bz + 2.0),
                    (p[0] + n[0] * (D["apron"][1] + 1.0), p[1] + n[1] * (D["apron"][1] + 1.0), 0.9), TP.SODIUM, D["up_power"], D["up_cone"])
            x, y = p[0] + n[0] * (D["apron"][1] + 1.0), p[1] + n[1] * (D["apron"][1] + 1.0)
            box(SURF, x - 0.35, y - 0.35, 0.0, x + 0.35, y + 0.35, 0.6, D["steel"])
            box(NEON, x - 0.25, y - 0.25, 0.6, x + 0.25, y + 0.25, 0.75, sc(TP.SODIUM, 0.9))
        s += D["up_step"]
    # sluice gate bays
    gate_pts = []
    for (g, s) in gates:
        p, n, t, a_ = frame_at(s)
        is_open = g % D["gate_open_every"] == 1
        gw, pw = D["gate_w"], D["pier_w"]
        for side in (-1, 1):
            v0 = side * gw / 2
            v1 = side * (gw / 2 + pw)
            # a raked pier (buttress nose down the dry face), a cap block on its crest end
            vc = (v0 + v1) / 2
            pc = (p[0] + t[0] * vc, p[1] + t[1] * vc)
            slab(SURF, pc, t, n, [(D["toe"] - 1.6, -0.5), (wet + 1.6, -6.0), (wet + 1.6, D["pier_z"]), (cd - 1.5, D["pier_z"]),
                                  (b1o - 0.8, bz + 1.2), (D["toe"] - 1.6, 1.4)], pw, D["conc"])
            local_box(SURF, p, t, n, cd - 1.2, wet + 1.1, min(v0, v1) + 0.3, max(v0, v1) - 0.3, D["pier_z"],
                      D["pier_z"] + 1.2, D["conc_dark"])
            # red beacon on the pier top, the waterline gauge on the pier's wet nose
            vm = side * (gw / 2 + pw / 2)
            x, y = p[0] + t[0] * vm + n[0] * (wet + 0.6), p[1] + t[1] * vm + n[1] * (wet + 0.6)
            box(NEON, x - 0.3, y - 0.3, D["pier_z"] + 1.2, x + 0.3, y + 0.3, D["pier_z"] + 1.8, TP.RED)
            xg, yg = p[0] + t[0] * vm + n[0] * (wet + 1.65), p[1] + t[1] * vm + n[1] * (wet + 1.65)
            for m in range(-6, 7):
                zz = ZW + m * 1.0
                w_ = 0.9 if m % 5 == 0 else 0.45
                NEON.face([(xg - t[0] * w_ / 2, yg - t[1] * w_ / 2, zz), (xg + t[0] * w_ / 2, yg + t[1] * w_ / 2, zz),
                           (xg + t[0] * w_ / 2, yg + t[1] * w_ / 2, zz + 0.12), (xg - t[0] * w_ / 2, yg - t[1] * w_ / 2, zz + 0.12)],
                          (0.85, 0.9, 1.0) if m != 0 else TP.RED, None, wet=1)
        # the gate leaf (steel) at the wet face, the hazard stripe on its top, the hoist gantry + house over the bay
        top = D["gate_top"] if not is_open else D["gate_top"] + 6.5
        zb = -6.0 if not is_open else ZW + 0.4
        local_box(SURF, p, t, n, wet - 0.2, wet + 0.6, -gw / 2, gw / 2, zb, top, D["steel"], wet=1)
        for m in range(8):
            v0 = -gw / 2 + gw * m / 8
            col = sc(TP.HAZARD, 0.55) if m % 2 == 0 else (0.02, 0.02, 0.02)
            local_box(NEON if m % 2 == 0 else SURF, p, t, n, wet - 0.25, wet + 0.65, v0, v0 + gw / 8, top - 0.5, top, col)
        local_box(SURF, p, t, n, wet - 1.2, wet + 1.2, -gw / 2 - 0.2, gw / 2 + 0.2, D["pier_z"] - 2.5, D["pier_z"] - 1.2, D["steel"])
        local_box(SURF, p, t, n, wet - 1.8, wet + 0.6, -2.0, 2.0, D["pier_z"] - 1.2, D["pier_z"] + 1.0, (0.62, 0.48, 0.14),
                  wc=TP.DIVE, wl=0.6, wm=0, bid=0.5)
        for m in (-1, 1):                                    # hoist cables down to the leaf
            x, y = p[0] + t[0] * m * gw * 0.3 + n[0] * wet, p[1] + t[1] * m * gw * 0.3 + n[1] * wet
            bar(SURF, (x, y, top), (x, y, D["pier_z"] - 2.5), 0.1, (0.1, 0.1, 0.1))
        # spillway chute on the dry face (open: white water, the foam pool at the toe; closed: a dark culvert grate)
        chute = [(wet - 0.5, cz - 1.5), (cd, cz - 1.5), (b0o, bz - 0.3), (b1o, bz - 0.3), (D["toe"], 0.4), (D["toe"] - 2.6, 0.32)]
        if is_open:
            # white water: the chute floor (dark wet concrete) under narrow streaks of uneven brightness along the flow
            Pc = [(p[0] + t[0] * v, p[1] + t[1] * v) for v in (-gw / 2 + 0.3, gw / 2 - 0.3)]
            for e in range(len(chute) - 1):
                (o0, z0), (o1, z1) = chute[e], chute[e + 1]
                SURF.face([(Pc[0][0] + n[0] * o0, Pc[0][1] + n[1] * o0, z0 + 0.05), (Pc[1][0] + n[0] * o0, Pc[1][1] + n[1] * o0, z0 + 0.05),
                           (Pc[1][0] + n[0] * o1, Pc[1][1] + n[1] * o1, z1 + 0.05), (Pc[0][0] + n[0] * o1, Pc[0][1] + n[1] * o1, z1 + 0.05)],
                          (0.10, 0.12, 0.13))
            ns_ = 11
            for m in range(ns_):
                v0 = -gw / 2 + 0.5 + (gw - 1.0) * m / ns_
                v1 = v0 + (gw - 1.0) / ns_ * rr.uniform(0.35, 0.7)
                k_ = rr.uniform(*D["chute_k"])
                for e in range(len(chute) - 1):
                    (o0, z0), (o1, z1) = chute[e], chute[e + 1]
                    ke = k_ * (1.0 + 0.6 * (e >= 3)) * rr.uniform(0.7, 1.2)      # brighter where it breaks at the berm + toe
                    q0 = (p[0] + t[0] * v0, p[1] + t[1] * v0)
                    q1 = (p[0] + t[0] * v1, p[1] + t[1] * v1)
                    NEON.face([(q0[0] + n[0] * o0, q0[1] + n[1] * o0, z0 + 0.12), (q1[0] + n[0] * o0, q1[1] + n[1] * o0, z0 + 0.12),
                               (q1[0] + n[0] * o1, q1[1] + n[1] * o1, z1 + 0.12), (q0[0] + n[0] * o1, q0[1] + n[1] * o1, z1 + 0.12)],
                              sc((0.72, 0.93, 1.0), ke))
            for m in range(10):                              # foam blobs in the canal
                vv, oo = rr.uniform(-gw / 2, gw / 2), rr.uniform(D["canal"][1], D["canal"][0])
                x, y = p[0] + t[0] * vv + n[0] * oo, p[1] + t[1] * vv + n[1] * oo
                box(NEON, x - 0.4, y - 0.4, 0.3, x + 0.4, y + 0.4, 0.45, sc((0.75, 0.92, 1.0), rr.uniform(0.08, 0.25)))
        else:
            Pc = [(p[0] + t[0] * v, p[1] + t[1] * v) for v in (-gw / 2 + 0.3, gw / 2 - 0.3)]
            for e in range(len(chute) - 1):
                (o0, z0), (o1, z1) = chute[e], chute[e + 1]
                SURF.face([(Pc[0][0] + n[0] * o0, Pc[0][1] + n[1] * o0, z0 + 0.05), (Pc[1][0] + n[0] * o0, Pc[1][1] + n[1] * o0, z0 + 0.05),
                           (Pc[1][0] + n[0] * o1, Pc[1][1] + n[1] * o1, z1 + 0.05), (Pc[0][0] + n[0] * o1, Pc[0][1] + n[1] * o1, z1 + 0.05)],
                          (0.16, 0.17, 0.18))
            local_box(SURF, p, t, n, D["toe"] - 0.4, D["toe"] + 0.2, -2.6, 2.6, 0.0, 3.2, (0.05, 0.05, 0.06))
            x, y = p[0] + n[0] * (D["toe"] - 0.5), p[1] + n[1] * (D["toe"] - 0.5)
            box(NEON, x - 0.25, y - 0.25, 3.4, x + 0.25, y + 0.25, 3.9, TP.RED)
        # the crest bridge over the bay (the road continues)
        local_box(SURF, p, t, n, cd, wet, -gw / 2, gw / 2, cz - 0.8, cz, (0.13, 0.13, 0.15))
        if (g // 1) % D["pump_every"] == 0:
            # a pump house beside the bay on the crest, three penstocks down the dry face to a pump hall at the toe
            v0 = gw / 2 + pw + 1.0
            local_box(SURF, p, t, n, cd - 0.2, wet - 0.8, v0, v0 + 9.0, cz, cz + 5.5, D["conc_dark"], wc=TP.DIVE, wl=0.55,
                      wm=0, bid=0.3 + 0.07 * g)
            local_box(NEON, p, t, n, cd - 0.25, wet - 0.75, v0, v0 + 9.0, cz + 5.5, cz + 5.7, sc(TP.ABYSS, 0.6))
            for m in range(3):
                vv = v0 + 1.6 + m * 2.9
                a3 = (p[0] + t[0] * vv + n[0] * (cd - 0.6), p[1] + t[1] * vv + n[1] * (cd - 0.6), cz + 1.2)
                b3 = (p[0] + t[0] * vv + n[0] * (b0o - 0.4), p[1] + t[1] * vv + n[1] * (b0o - 0.4), bz + 1.1)
                c3 = (p[0] + t[0] * vv + n[0] * (b1o - 0.6), p[1] + t[1] * vv + n[1] * (b1o - 0.6), bz + 1.1)
                d3 = (p[0] + t[0] * vv + n[0] * (D["toe"] - 2.5), p[1] + t[1] * vv + n[1] * (D["toe"] - 2.5), 1.0)
                for (u_, w_) in ((a3, b3), (b3, c3), (c3, d3)):
                    tube(SMOOTH, u_, w_, 0.65, 8, (0.30, 0.31, 0.33))
        gate_pts.append((p[0] + n[0] * wet, p[1] + n[1] * wet, D["pier_z"]))

    # ------------------------------------------------------------ the DOCK LOCK (local frame of the lock pose)
    p, n, t = lk["P"], lk["N"], lk["T"]
    w2 = LK["w"] / 2
    for side in (-1, 1):
        v0, v1 = side * w2, side * (w2 + LK["wall"])
        lo, hi = min(v0, v1), max(v0, v1)
        local_box(SURF, p, t, n, D["toe"], wet + 1.0, lo, hi, D["base_z"], cz + 0.6, D["conc"])         # through the dam
        local_box(SURF, p, t, n, LK["down"] - 1.0, D["toe"], lo, hi, -4.0, 3.2, D["conc"])            # the chamber walls
        for u_ in (wet - 1.2, LK["down"] + 0.6):          # traffic lights at both gates (red: the ward is lapsed)
            x, y = p[0] + n[0] * u_ + t[0] * side * (w2 + LK["wall"] / 2), p[1] + n[1] * u_ + t[1] * side * (w2 + LK["wall"] / 2)
            ztop = cz + 0.6 if u_ > D["toe"] else 3.2
            bar(SURF, (x, y, ztop), (x, y, ztop + 2.2), 0.2, D["steel"])
            box(NEON, x - 0.28, y - 0.28, ztop + 2.2, x + 0.28, y + 0.28, ztop + 2.75, TP.RED)
            box(NEON, x - 0.22, y - 0.22, ztop + 1.5, x + 0.22, y + 0.22, ztop + 1.95, sc((0.2, 1.0, 0.4), 0.12))
    local_box(SURF, p, t, n, LK["down"] - 1.0, wet + 1.0, -w2, w2, -4.0, -3.0, D["conc_dark"])        # chamber floor
    q = [(p[0] + n[0] * u_ + t[0] * v_, p[1] + n[1] * u_ + t[1] * v_) for (u_, v_) in
         ((LK["down"], -w2), (wet - 0.4, -w2), (wet - 0.4, w2), (LK["down"], w2))]
    WATER.face([(x, y, LK["chamber_z"]) for (x, y) in q], (0, 0, 0))
    # mitre gates (V pointing upstream) at both ends; hazard stripes on the leaves' tops
    for (u_, ztop) in ((wet - 0.3, cz - 0.4), (LK["down"] + 0.2, 3.0)):
        for side in (-1, 1):
            a3 = (p[0] + n[0] * (u_ - 1.6) + t[0] * side * w2, p[1] + n[1] * (u_ - 1.6) + t[1] * side * w2)
            b3 = (p[0] + n[0] * u_, p[1] + n[1] * u_)
            seg_box(SURF, a3, b3, 0.55, -3.0, ztop, D["steel"], wet=1)
            seg_box(NEON, a3, b3, 0.6, ztop, ztop + 0.18, sc(TP.HAZARD, 0.55))
    # the crest road bridge over the chamber
    local_box(SURF, p, t, n, cd, wet - 2.0, -w2, w2, cz - 0.7, cz, (0.13, 0.13, 0.15))
    # the control tower (dry side, beside the chamber): lit floors, a glass cab, the hue ring, a red beacon
    vt = w2 + LK["wall"] + 4.2
    tc = (p[0] + n[0] * (D["toe"] - 4.0) + t[0] * vt, p[1] + n[1] * (D["toe"] - 4.0) + t[1] * vt)
    local_box(SURF, tc, t, n, -2.6, 2.6, -2.6, 2.6, 0.0, LK["tower_h"], (0.22, 0.24, 0.28), wc=TP.DIVE, wl=0.7, wm=0, bid=0.77)
    local_box(GLASS, tc, t, n, -3.3, 3.3, -3.3, 3.3, LK["tower_h"], LK["tower_h"] + 3.0, (0.6, 0.85, 1.0))
    local_box(NEON, tc, t, n, -2.4, 2.4, -2.4, 2.4, LK["tower_h"] + 0.05, LK["tower_h"] + 0.15, sc(TP.DIVE, 0.8))
    local_box(SURF, tc, t, n, -3.5, 3.5, -3.5, 3.5, LK["tower_h"] + 3.0, LK["tower_h"] + 3.6, (0.22, 0.24, 0.28))
    ring_line(NEON, tc[0], tc[1], LK["tower_h"] + 3.65, 4.7, 0.3, TP.ABYSS, n=24)
    bar(SURF, (tc[0], tc[1], LK["tower_h"] + 3.6), (tc[0], tc[1], LK["tower_h"] + 9.0), 0.2, D["steel"])
    box(NEON, tc[0] - 0.35, tc[1] - 0.35, LK["tower_h"] + 9.0, tc[0] + 0.35, tc[1] + 0.35, LK["tower_h"] + 9.7, TP.RED)
    spot_at((tc[0], tc[1], LK["tower_h"] / 2), (tc[0] - n[0] * 30.0, tc[1] - n[1] * 30.0, 30.0), (0.85, 0.92, 1.0), 6.0e4, 30.0)
    # the dock basin (dry side): quay walls, the water, a moored sub, quay lamps
    u0, u1, bw = LK["basin"], LK["down"] - 1.0, LK["basin_w"] / 2
    for side in (-1, 1):
        local_box(SURF, p, t, n, u0 - 1.2, u1, side * bw, side * (bw + 1.2), -3.0, 0.6, D["conc"])
    local_box(SURF, p, t, n, u0 - 1.2, u0, -bw, bw, -3.0, 0.6, D["conc"])
    local_box(SURF, p, t, n, u0, u1, -bw, bw, -3.0, -2.5, D["conc_dark"])
    q = [(p[0] + n[0] * u_ + t[0] * v_, p[1] + n[1] * u_ + t[1] * v_) for (u_, v_) in ((u0, -bw), (u1, -bw), (u1, bw), (u0, bw))]
    WATER.face([(x, y, LK["basin_z"]) for (x, y) in q], (0, 0, 0))
    sx, sy = p[0] + n[0] * (u0 + u1) / 2 - t[0] * 3.5, p[1] + n[1] * (u0 + u1) / 2 - t[1] * 3.5
    yaw = math.atan2(n[1], n[0])
    obox(SMOOTH, sx, sy, -0.9, 11.0, 2.4, 1.8, yaw, (0.20, 0.23, 0.28))
    obox(SURF, sx, sy, 0.9, 3.0, 1.3, 1.4, yaw, (0.20, 0.23, 0.28))
    obox(NEON, sx, sy, 0.86, 11.2, 2.5, 0.12, yaw, sc(TP.ABYSS, 0.9))
    for (dv, col) in ((-1, (1.0, 0.1, 0.1)), (1, (0.1, 1.0, 0.3))):
        box(NEON, sx + t[0] * dv * 0.7 - 0.12, sy + t[1] * dv * 0.7 - 0.12, 2.3, sx + t[0] * dv * 0.7 + 0.12, sy + t[1] * dv * 0.7 + 0.12, 2.55, col)
    for m in range(4):
        u_ = u0 + (u1 - u0) * (m + 0.5) / 4
        for side in (-1, 1):
            x, y = p[0] + n[0] * u_ + t[0] * side * (bw + 0.6), p[1] + n[1] * u_ + t[1] * side * (bw + 0.6)
            bar(SURF, (x, y, 0.6), (x, y, 4.2), 0.14, D["steel"])
            box(NEON, x - 0.2, y - 0.2, 4.2, x + 0.2, y + 0.2, 4.5, sc(TP.SODIUM, 0.9))
    lock_room = (p[0] + n[0] * (D["toe"] - 4.0) + t[0] * vt, p[1] + n[1] * (D["toe"] - 4.0) + t[1] * vt, LK["tower_h"] + 1.5)

    # ------------------------------------------------------------ the causeway: lock -> the HQ lot
    O = ns["O"]
    c0, c1 = O.get("tethys_causeway") or causeway(O, L, lk)
    dx, dy = c1[0] - c0[0], c1[1] - c0[1]
    Lc = math.hypot(dx, dy)
    ux, uy = dx / Lc, dy / Lc
    vx, vy = -uy, ux
    z = CW["z"]
    seg_box(SURF, c0, c1, CW["w"], z - 0.6, z, (0.26, 0.28, 0.32))
    for side in (-1, 1):
        a3 = (c0[0] + vx * side * CW["w"] / 2, c0[1] + vy * side * CW["w"] / 2, z + 1.0)
        b3 = (c1[0] + vx * side * CW["w"] / 2, c1[1] + vy * side * CW["w"] / 2, z + 1.0)
        bar(SURF, a3, b3, 0.1, (0.5, 0.52, 0.56))
        a3 = (a3[0], a3[1], z - 0.3)
        b3 = (b3[0], b3[1], z - 0.3)
        bar(NEON, a3, b3, 0.12, sc(TP.ABYSS, 0.7))
    # the glass tube walkway on the HQ's lee side, ribs every 3 BU
    tsd = 1
    ta = (c0[0] + vx * tsd * (CW["w"] / 2 + CW["tube_r"]), c0[1] + vy * tsd * (CW["w"] / 2 + CW["tube_r"]), z + CW["tube_r"] - 0.4)
    tb = (c1[0] + vx * tsd * (CW["w"] / 2 + CW["tube_r"]), c1[1] + vy * tsd * (CW["w"] / 2 + CW["tube_r"]), z + CW["tube_r"] - 0.4)
    tube(GLASS, ta, tb, CW["tube_r"], 12, (0.6, 0.85, 1.0))
    seg_box(SURF, (ta[0], ta[1]), (tb[0], tb[1]), CW["tube_r"] * 1.8, z - 0.6, z - 0.35, (0.26, 0.28, 0.32))
    nr = int(Lc / 3.0)
    for m in range(nr + 1):
        f = m / max(1, nr)
        cx_, cy_ = ta[0] + (tb[0] - ta[0]) * f, ta[1] + (tb[1] - ta[1]) * f
        # a rib ring around the tube (in the plane normal to the causeway)
        prev = None
        for kk in range(13):
            ang = math.pi * 2 * kk / 12
            pp = (cx_ + vx * math.cos(ang) * (CW["tube_r"] + 0.05), cy_ + vy * math.cos(ang) * (CW["tube_r"] + 0.05), ta[2] + math.sin(ang) * (CW["tube_r"] + 0.05))
            if prev:
                bar(NEON if m % 2 == 0 else SURF, prev, pp, 0.08, sc(TP.ABYSS, 0.5) if m % 2 == 0 else (0.5, 0.55, 0.6))
            prev = pp
    m = 0
    s_ = 2.0
    ground_at = ns.get("ground_at")
    while s_ < Lc:
        x, y = c0[0] + ux * s_, c0[1] + uy * s_
        gz = ground_at(x, y) if ground_at else -40.0
        for side in (-1, 1):
            px_, py_ = x + vx * side * (CW["w"] / 2 - 0.5), y + vy * side * (CW["w"] / 2 - 0.5)
            tube(SMOOTH, (px_, py_, gz), (px_, py_, z - 0.6), 0.45, 8, (0.26, 0.28, 0.32), wet=1)
        if m % 1 == 0:
            side = 1 if m % 2 else -1
            px_, py_ = x + vx * side * (CW["w"] / 2 - 0.2), y + vy * side * (CW["w"] / 2 - 0.2)
            bar(SURF, (px_, py_, z), (px_, py_, z + 3.4), 0.12, (0.4, 0.42, 0.46))
            box(NEON, px_ - 0.2, py_ - 0.2, z + 3.4, px_ + 0.2, py_ + 0.2, z + 3.7, TP.PHOTO if side > 0 else TP.DIVE)
        s_ += CW["pile_step"]
        m += 1
    return dict(lock=lock_room, gates=gate_pts, causeway=(c0, c1), lock_pose=lk)


# ===================================================================== the drowned streets
def build_clutter(ns):
    """Clutter on every drowned street tile within CLUTTER.reach of the HQ, and fronts on every drowned building."""
    C = TP.CLUTTER
    SURF, SMOOTH, NEON, SEABED = (ns[k] for k in ("SURF", "SMOOTH", "NEON", "SEABED"))
    box, bar, sc, W = ns["box"], ns["bar"], ns["sc"], ns["W"]
    O, ZW = ns["O"], ns["ZW"]
    L = O.get("tethys_dam") or dam_line(O)
    hx, hy = W(O["hq"]["tethys"])
    lk = O.get("tethys_lock")
    c0, c1 = O.get("tethys_causeway") or (None, None)
    n_items = dict(tiles=0, cars=0, lamps=0, signs=0, kelp=0, debris=0, fronts=0)
    for tl in O["tiles"]:
        if not tl["wet"] or not tl["ab"]:
            continue
        a, b = W(tl["ab"][0]), W(tl["ab"][1])
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        if math.hypot(mx - hx, my - hy) > C["reach"] or math.hypot(mx - hx, my - hy) < TP.PIER["lot_r"] + 2:
            continue
        d, _ = signed_dist(L, mx, my)
        if d is not None and d < TP.DAM["clear_wet"] - 4.0:
            continue
        z0 = -tl["sub"]
        if z0 > ZW - 1.0:
            continue
        r = random.Random(TP.SEEDS["clutter"] * 1000003 + tl["i"] * 7919 + tl["j"])
        Lt = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
        ux, uy = (b[0] - a[0]) / Lt, (b[1] - a[1]) / Lt
        vx, vy = -uy, ux
        yaw = math.atan2(uy, ux)
        n_items["tiles"] += 1
        # kerbs both sides, a dashed centre line, pale lane edges (the caustics land on them)
        for side in (-1, 1):
            o = side * C["half"]
            pa = (a[0] + vx * o, a[1] + vy * o)
            pb = (b[0] + vx * o, b[1] + vy * o)
            seg_box(SURF, pa, pb, C["kerb_w"], z0, z0 + C["kerb_h"], (0.36, 0.36, 0.36), wet=1)
        for m in range(3):
            f0, f1 = (m + 0.15) / 3, (m + 0.55) / 3
            pa = (a[0] + (b[0] - a[0]) * f0, a[1] + (b[1] - a[1]) * f0)
            pb = (a[0] + (b[0] - a[0]) * f1, a[1] + (b[1] - a[1]) * f1)
            seg_box(SEABED, pa, pb, 0.22, z0 + 0.02, z0 + 0.06, (0.62, 0.58, 0.40), wet=1)
        # cars
        for kk in range(C["car_n"]):
            if r.random() > C["car_p"] / (kk + 1):
                continue
            f = r.uniform(0.1, 0.9)
            lane = r.choice((-1.3, 1.3))
            cx_ = a[0] + (b[0] - a[0]) * f + vx * lane
            cy_ = a[1] + (b[1] - a[1]) * f + vy * lane
            yw = yaw + (math.pi if lane < 0 else 0.0) + r.uniform(-0.35, 0.35)
            col = r.choice(C["car_cols"])
            flip = r.random() < C["car_flip"]
            roll = math.pi if flip else r.uniform(-0.08, 0.08)
            if flip:
                obox(SURF, cx_, cy_, z0 + 0.35, 2.1, 1.0, 0.5, yw, col, roll=roll, wet=1)
                obox(SURF, cx_, cy_, z0, 1.1, 0.8, 0.36, yw, sc(col, 0.7), roll=roll, wet=1)
            else:
                obox(SURF, cx_, cy_, z0 + 0.12, 2.1, 1.0, 0.45, yw, col, roll=roll, wet=1)
                obox(SURF, cx_ - math.cos(yw) * 0.1, cy_ - math.sin(yw) * 0.1, z0 + 0.57, 1.1, 0.82, 0.36, yw, (0.05, 0.07, 0.09), roll=roll, wet=1)
                if r.random() < C["car_lit"]:          # the dead man's headlights, still on
                    for s_ in (-0.3, 0.3):
                        hx_ = cx_ + math.cos(yw) * 1.06 - math.sin(yw) * s_
                        hy_ = cy_ + math.sin(yw) * 1.06 + math.cos(yw) * s_
                        box(NEON, hx_ - 0.1, hy_ - 0.1, z0 + 0.32, hx_ + 0.1, hy_ + 0.1, z0 + 0.48, (1.0, 0.92, 0.75), wet=1)
            n_items["cars"] += 1
        # a bus or a container on its side
        if r.random() < C["bus_p"]:
            f = r.uniform(0.2, 0.8)
            obox(SURF, a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, z0 + 0.1, 5.2, 1.3, 1.4, yaw + r.uniform(-0.5, 0.5),
                 (0.55, 0.42, 0.10), roll=r.choice((0.0, math.pi / 2)), wet=1)
        if r.random() < C["container_p"]:
            f = r.uniform(0.2, 0.8)
            obox(SURF, a[0] + (b[0] - a[0]) * f + vx * r.uniform(-1.5, 1.5), a[1] + (b[1] - a[1]) * f + vy * r.uniform(-1.5, 1.5),
                 z0, 2.4, 1.0, 1.0, yaw + r.uniform(-1.2, 1.2), r.choice([(0.62, 0.24, 0.08), (0.12, 0.34, 0.36), (0.55, 0.12, 0.08)]),
                 roll=r.uniform(-0.3, 0.3), wet=1)
        # street lamps (some still lit, some leaning), with a sagging cable to the next
        lamp_tops = []
        if r.random() < C["lamp_p"]:
            for side in (-1, 1):
                if r.random() < 0.6:
                    f = r.uniform(0.2, 0.8)
                    x = a[0] + (b[0] - a[0]) * f + vx * side * (C["half"] + 0.3)
                    y = a[1] + (b[1] - a[1]) * f + vy * side * (C["half"] + 0.3)
                    lean = r.uniform(0.2, 0.9) if r.random() < C["lamp_lean"] else r.uniform(0.0, 0.06)
                    top = (x - vx * side * math.sin(lean) * C["lamp_h"], y - vy * side * math.sin(lean) * C["lamp_h"],
                           z0 + math.cos(lean) * C["lamp_h"])
                    bar(SURF, (x, y, z0), top, 0.14, (0.22, 0.23, 0.25), wet=1)
                    arm = (top[0] - vx * side * 1.1, top[1] - vy * side * 1.1, top[2] - 0.1)
                    bar(SURF, top, arm, 0.1, (0.22, 0.23, 0.25), wet=1)
                    lit = r.random() < C["lamp_lit"]
                    box(NEON if lit else SURF, arm[0] - 0.22, arm[1] - 0.22, arm[2] - 0.25, arm[0] + 0.22, arm[1] + 0.22, arm[2],
                        sc((1.0, 0.72, 0.42), 0.9) if lit else (0.3, 0.3, 0.3), wet=1)
                    lamp_tops.append(top)
                    n_items["lamps"] += 1
            if len(lamp_tops) == 2 and r.random() < C["cable_p"] * 2:
                catenary(SURF, lamp_tops[0], lamp_tops[1], 1.2, 0.06, (0.08, 0.08, 0.09), n=6, wet=1)
        # street signs / billboards
        if r.random() < C["sign_p"]:
            side = r.choice((-1, 1))
            f = r.uniform(0.1, 0.9)
            x = a[0] + (b[0] - a[0]) * f + vx * side * (C["half"] + 0.2)
            y = a[1] + (b[1] - a[1]) * f + vy * side * (C["half"] + 0.2)
            bar(SURF, (x, y, z0), (x, y, z0 + 3.0), 0.09, (0.3, 0.3, 0.3), wet=1)
            obox(SURF, x, y, z0 + 2.4, 1.3, 0.06, 0.45, yaw, (0.10, 0.36, 0.20), wet=1)
            n_items["signs"] += 1
        if r.random() < C["board_p"]:
            side = r.choice((-1, 1))
            f = r.uniform(0.2, 0.8)
            x = a[0] + (b[0] - a[0]) * f + vx * side * (C["half"] + 0.8)
            y = a[1] + (b[1] - a[1]) * f + vy * side * (C["half"] + 0.8)
            hb = r.uniform(4.5, 7.5)
            for s_ in (-1.8, 1.8):
                bar(SURF, (x + ux * s_, y + uy * s_, z0), (x + ux * s_, y + uy * s_, z0 + hb), 0.2, (0.25, 0.25, 0.27), wet=1)
            lit = r.random() < C["board_lit"]
            obox(NEON if lit else SURF, x, y, z0 + hb, 5.0, 0.15, 2.4, yaw + r.uniform(-0.15, 0.15),
                 sc(r.choice(C["neon"]), 0.55) if lit else (0.2, 0.2, 0.22), pitch=r.uniform(-0.1, 0.1), wet=1)
            n_items["signs"] += 1
        # debris
        for kk in range(r.randint(*C["debris_n"])):
            f = r.uniform(0.05, 0.95)
            o = r.uniform(-C["half"], C["half"])
            sz = r.uniform(0.25, 0.8)
            obox(SURF, a[0] + (b[0] - a[0]) * f + vx * o, a[1] + (b[1] - a[1]) * f + vy * o, z0, sz * r.uniform(1, 2.2), sz,
                 sz * r.uniform(0.3, 0.8), r.uniform(0, math.pi), r.choice([(0.32, 0.30, 0.28), (0.24, 0.22, 0.20), (0.40, 0.38, 0.34)]),
                 roll=r.uniform(-0.4, 0.4), wet=1)
            n_items["debris"] += 1
        # kelp cables: loose data / power lines drifting up like kelp, algae tufts, photophore fibre ends
        if z0 < ZW - 4.0:
            for kk in range(r.randint(*C["kelp_n"])):
                f = r.uniform(0.05, 0.95)
                o = r.choice((-1, 1)) * r.uniform(C["half"] - 0.3, C["half"] + 1.2)
                x0 = a[0] + (b[0] - a[0]) * f + vx * o
                y0 = a[1] + (b[1] - a[1]) * f + vy * o
                ht = min(ZW - 1.2 - z0, r.uniform(5.0, 22.0))
                ph = r.uniform(0, 6.28)
                dirx, diry = math.cos(ph), math.sin(ph)
                prev = (x0, y0, z0)
                segs = 7
                for m in range(1, segs + 1):
                    tt = m / segs
                    sway = math.sin(tt * 3.2 + ph) * 1.2 * tt + tt * tt * 2.2
                    pp = (x0 + dirx * sway, y0 + diry * sway, z0 + ht * tt)
                    bar(SURF, prev, pp, 0.13, (0.07, 0.12, 0.10), wet=1)
                    if m % 2 == 0:
                        lf = (pp[0] + diry * 0.7, pp[1] - dirx * 0.7, pp[2] - 0.6)
                        SURF.face([prev, pp, lf], (0.10, 0.22, 0.14), None, wet=1)
                    prev = pp
                if r.random() < C["kelp_tip"]:
                    box(NEON, prev[0] - 0.13, prev[1] - 0.13, prev[2] - 0.05, prev[0] + 0.13, prev[1] + 0.13, prev[2] + 0.22,
                        sc(TP.PHOTO, C["kelp_k"]), wet=1)
                n_items["kelp"] += 1
    # drowned buildings: shop fronts at the old street level and blade signs (some still lit)
    for bd in O["buildings"]:
        if not bd.get("wet"):
            continue
        q = [W(p) for p in bd["q"]]
        cx_, cy_ = sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q)
        if math.hypot(cx_ - hx, cy_ - hy) > C["reach"]:
            continue
        z0 = bd["z0"] * ns["KH"] - bd.get("sub", 0.0)
        if z0 > ZW - 1.5:
            continue
        r = random.Random(TP.SEEDS["signs"] * 1000003 + bd["key"])
        top = z0 + bd["h"] * ns["KH"]
        for i in range(len(q)):
            pa, pb = q[i], q[(i + 1) % len(q)]
            Le = math.hypot(pb[0] - pa[0], pb[1] - pa[1])
            if Le < 2.0:
                continue
            nx, ny = (pb[1] - pa[1]) / Le, -(pb[0] - pa[0]) / Le
            if nx * (pa[0] - cx_) + ny * (pa[1] - cy_) < 0:
                nx, ny = -nx, -ny
            if r.random() < C["shop_p"]:
                lit = r.random() < C["shop_lit"]
                col = sc(r.choice([(1.0, 0.78, 0.5), (0.5, 0.9, 1.0), (1.0, 0.5, 0.75)]), 0.75) if lit else (0.06, 0.07, 0.08)
                (NEON if lit else SURF).face([(pa[0] + nx * 0.06, pa[1] + ny * 0.06, z0 + 0.15), (pb[0] + nx * 0.06, pb[1] + ny * 0.06, z0 + 0.15),
                                              (pb[0] + nx * 0.06, pb[1] + ny * 0.06, z0 + 1.2), (pa[0] + nx * 0.06, pa[1] + ny * 0.06, z0 + 1.2)],
                                             col, None, wet=1)
                n_items["fronts"] += 1
            if r.random() < C["blade_p"] and top - z0 > 5.0:
                f = r.uniform(0.15, 0.85)
                px_, py_ = pa[0] + (pb[0] - pa[0]) * f, pa[1] + (pb[1] - pa[1]) * f
                zb = z0 + r.uniform(1.6, 3.0)
                zt = min(top - 0.3, zb + r.uniform(2.5, 6.0))
                out = r.uniform(0.6, 1.2)
                lit = r.random() < C["blade_lit"]
                col = sc(r.choice(C["neon"]), 0.8) if lit else (0.16, 0.16, 0.18)
                (NEON if lit else SURF).face([(px_ + nx * 0.1, py_ + ny * 0.1, zb), (px_ + nx * out, py_ + ny * out, zb),
                                              (px_ + nx * out, py_ + ny * out, zt), (px_ + nx * 0.1, py_ + ny * 0.1, zt)], col, None, wet=1)
                n_items["fronts"] += 1
    print("TETHYS clutter", n_items, flush=True)
    return n_items


# ===================================================================== wildlife: the fish shoals
def build_shoal(ns, r, centre, kind, R, zlim, axis=0.0, spin=1, n=None):
    """One shoal into the SMOOTH / NEON accumulators (seeded by rng r). -> fish count. Shared by the streets (here), the
    stilts and the piers (tethys_landmark.build_pier_shoals)."""
    from tkit import fish, shoal_sim
    W = TP.WILDLIFE["fish"]
    SMOOTH, NEON, sc = ns["SMOOTH"], ns["NEON"], ns["sc"]
    n = n or r.randint(*W["n"])
    c_top, c_bot = r.choices(W["cols"], weights=W["col_w"])[0]
    pts = shoal_sim(r, n, centre, kind, R, zlim, steps=W["steps"], axis=axis, spin=spin)
    for (x, y, z, yw, pt) in pts:
        Lf = r.uniform(*W["length"])
        k = r.uniform(0.85, 1.12)
        g = sc(TP.PHOTO, W["glint_k"]) if r.random() < W["glint_p"] else None
        fish(SMOOTH, NEON, (x, y, z), yw, pt, Lf, tuple(min(1.0, c * k) for c in c_top), tuple(min(1.0, c * k) for c in c_bot), g,
             sc(TP.PHOTO, W["belly_glow"]))
    return len(pts)


def build_street_shoals(ns):
    """Fish shoals over the drowned streets within WILDLIFE.fish.street_reach of the HQ (seeded by the tile): balls
    milling round a lamp or a car, rings, and streams drifting down a street, 2-9 BU over the street bed and always
    below the surface. -> counts."""
    W = TP.WILDLIFE["fish"]
    O, ZW, Wf = ns["O"], ns["ZW"], ns["W"]
    hx, hy = Wf(O["hq"]["tethys"])
    L = O.get("tethys_dam") or dam_line(O)
    kinds = [k for k, _ in W["kinds"]]
    kw = [w for _, w in W["kinds"]]
    cnt = dict(street_shoals=0, street_fish=0)
    cand = []
    for tl in O["tiles"]:
        if not tl["wet"] or not tl["ab"]:
            continue
        a, b = Wf(tl["ab"][0]), Wf(tl["ab"][1])
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        d0 = math.hypot(mx - hx, my - hy)
        if not (W["street_reach"][0] <= d0 <= W["street_reach"][1]):
            continue
        d, _ = signed_dist(L, mx, my)
        if d is not None and d < TP.DAM["clear_wet"] - 4.0:
            continue
        z0 = -tl["sub"]
        if z0 > ZW - 4.0:
            continue
        r = random.Random(TP.SEEDS["fish"] * 1000003 + tl["i"] * 7919 + tl["j"])
        cand.append((r.random(), tl["i"], tl["j"], a, b, z0))
    cand.sort(key=lambda t: t[:3])                       # deterministic pick: the first street_max by the tile's seeded roll
    for (_, ti, tj, a, b, z0) in cand[:W["street_max"]]:
        r = random.Random(TP.SEEDS["fish"] * 1000003 + ti * 7919 + tj)
        kind = r.choices(kinds, weights=kw)[0]
        zlo = z0 + W["street_z"][0]
        zhi = min(ZW - W["street_top"], z0 + W["street_z"][1] + 4.0)
        if zhi - zlo < 1.5:
            continue
        zc = r.uniform(zlo + 0.5, zhi - 0.5)
        R = r.uniform(*W["street_big_R"])
        axis = math.atan2(b[1] - a[1], b[0] - a[0])
        c = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, zc)
        cnt["street_fish"] += build_shoal(ns, r, c, kind, R, (zlo, zhi), axis=axis, spin=r.choice((-1, 1)) * 0.15,
                                          n=r.randint(*W["street_big"]))
        cnt["street_shoals"] += 1
    print("TETHYS street shoals", cnt, flush=True)
    return cnt


def build_open_water_shoals(ns):
    """Loose, irregular shoals in the open sea beyond the breakwater (WILDLIFE.fish.open_n, seeded): drifting clouds and
    streams 38-50 BU from the HQ (the trench, over towers sunk 30+ BU), 5-11 BU under the surface; attached to nothing."""
    W = TP.WILDLIFE["fish"]
    O, ZW = ns["O"], ns["ZW"]
    hx, hy = ns["W"](O["hq"]["tethys"])
    r = random.Random(TP.SEEDS["fish"] + 11)
    kinds = [k for k, _ in W["kinds"]]
    kw = [w for _, w in W["kinds"]]
    cnt = dict(open_shoals=0, open_fish=0)
    for k in range(W["open_n"]):
        a = 2 * math.pi * (k + r.uniform(0.0, 0.8)) / W["open_n"]
        rr = r.uniform(*W["open_r"])
        zc = ZW - r.uniform(*W["open_z"])
        cnt["open_fish"] += build_shoal(ns, r, (hx + rr * math.cos(a), hy + rr * math.sin(a), zc), r.choices(kinds, weights=kw)[0],
                                        r.uniform(*W["street_big_R"]), (zc - 2.5, min(zc + 2.5, ZW - 2.5)), axis=r.uniform(0, 6.28),
                                        spin=r.choice((-1, 1)) * 0.15, n=r.randint(*W["street_big"]))
        cnt["open_shoals"] += 1
    print("TETHYS open-water shoals", cnt, flush=True)
    return cnt
