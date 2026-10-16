"""City-all-corps: the district zoning and landmark placement rules (pure Python + numpy; no Blender).

    python zoning.py            -> D:/rc_scratch/city_all_corps/zoned.json  (+ zoning_map.png, a top view check)

Source of truth: the one-city layout (`unified_v3.json`, written by the storyboard's sb_onecity.apply_layout_rules from
the game's city layout: streets, 14 000 buildings, plazas, the five existing territories and HQ lots). Read-only.

Rules (numbers in city_preset.ZONING / WATER):
  Z1  The five existing territories (Meridian, Solace, Halcyon, Orbital, REBEL_CELL) keep their buildings: they are
      the game's own claims (rounds 24-40, locked).
  Z2  The unclaimed buildings ('' territory) split into k = 3 clusters (k-means on lot centroids, farthest-point init
      from the lowest building key: deterministic).
  Z3  The coastal cluster (mean depth b within coast_band of the coast) becomes TETHYS DEEP: the water corp takes the
      sea front. The cluster nearest the city centre becomes AURELIAN CONCORD (the old stone core; its aqueduct is
      the city's backbone). Any other cluster stays THE SPRAWL.
  Z4  The coast is the city's far edge from the map camera (yaw 135): b_coast = the deepest building + 0.8 lot.
      The seawall runs along it, past the city on both sides.
  Z5  Tethys' seaward share (lagoon_frac by depth) is the DROWNED QUARTER: a lapsed ward with the pumps off. Its
      ground has subsided (subside, deeper toward the sea, plus the trench under the station) and the sea stands in
      it at the sea level. A levee runs round its landward edge.
  L1  Existing HQ lots are the layout's own (layout36: hqs + cell_base). A NEW corp's HQ lot is the pole of
      inaccessibility of its district (the grid point farthest from any building of another district), Tethys' over
      its drowned quarter (the station stands in the lagoon). Ties: lower lot x, then y.
  L2  Every landmark clears landmark_r lots round its lot (layout36's plaza rule). REBEL_CELL has no landmark
      building (designer): its cleared base lot is refilled with tenements on the lot grid, heights from its
      neighbours, and the fist is drawn in red windows (round 34: within crest_d of a fist stroke).
  L3  The aqueduct follows the Aurelian street line (row or column) carrying the most Aurelian frontage that passes
      the HQ outside its clearance, from the district's first to last tile on that line, +- aqueduct_ext.
  T1  Arterials (traffic light-streaks): street-tile runs of >= arterial_len tiles with mean lane traffic >=
      arterial_tr, on both axes.
"""
import json
import math
import os
import random
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import city_preset as CP  # noqa: E402
import city_rules as RU  # noqa: E402

R2 = math.sqrt(2.0)
CX, CY = 6.0, 6.0


def ab(x, y):
    """lots -> screen-aligned (a right, b away from the map camera), in lots."""
    dx, dy = x - CX, y - CY
    return (dx - dy) / R2, -(dx + dy) / R2


def from_ab(a, b):
    return CX + (a - b) / R2, CY + (-a - b) / R2


def centroid(q):
    return sum(p[0] for p in q) / len(q), sum(p[1] for p in q) / len(q)


def kmeans(X, k, iters=60):
    C = [X[0]]
    while len(C) < k:
        d = np.min([np.hypot(*(X - c).T) for c in C], axis=0)
        C.append(X[int(np.argmax(d))])
    C = np.array(C, float)
    for _ in range(iters):
        lab = np.argmin([np.hypot(*(X - c).T) for c in C], axis=0)
        C2 = np.array([X[lab == i].mean(0) for i in range(k)])
        if np.allclose(C2, C):
            break
        C = C2
    return lab, C


def smooth(x, a, b):
    t = min(1.0, max(0.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def main():
    L = json.load(open(CP.LAYOUT))
    net = json.load(open(CP.NET36))
    Z, W = CP.ZONING, CP.WATER
    B = L["buildings"]
    cen = [centroid(b["q"]) for b in B]
    abs_ = [ab(*c) for c in cen]
    # ---- Z1-Z3
    dist = [b["terr"] for b in B]
    neutral = sorted([i for i, b in enumerate(B) if not b["terr"]], key=lambda i: B[i]["key"])
    X = np.array([cen[i] for i in neutral])
    lab, C = kmeans(X, Z["k_neutral"])
    b_coast = max(v[1] for v in abs_) + 0.8
    stats = []
    for c in range(Z["k_neutral"]):
        idx = [neutral[j] for j in range(len(neutral)) if lab[j] == c]
        mb = float(np.mean([abs_[i][1] for i in idx]))
        stats.append(dict(c=c, n=len(idx), mean_b=mb, centre=C[c].tolist(), r_centre=float(math.hypot(*(C[c] - (CX, CY)))), idx=idx))
    coastal = [s for s in stats if b_coast - s["mean_b"] <= Z["coast_band"]]
    teth = max(coastal, key=lambda s: (s["mean_b"], -s["c"]))
    rest = [s for s in stats if s is not teth]
    aur = min(rest, key=lambda s: (s["r_centre"], s["c"]))
    for i in teth["idx"]:
        dist[i] = "tethys"
    for i in aur["idx"]:
        dist[i] = "aurelian"
    # ---- Z5 the drowned quarter
    tb = sorted(abs_[i][1] for i in teth["idx"])
    b_split = tb[int(len(tb) * (1 - W.get("lagoon_frac", Z["lagoon_frac"])))] if "lagoon_frac" in W else tb[int(len(tb) * (1 - Z["lagoon_frac"]))]
    drowned = {i for i in teth["idx"] if abs_[i][1] >= b_split}
    ta = [abs_[i][0] for i in drowned]
    a_lo, a_hi = min(ta), max(ta)
    # ---- L1 HQ lots. Round 3 (H1, designer notes 7 + 8): REBEL_CELL at the city centre; the six corps on their
    # bearings at radius r round it (city_preset.HQ_LAYOUT); Tethys keeps its pole over the drowned quarter.
    hq_old = {k: list(v) for k, v in L["hqs"].items()}
    hq_old["rebel_cell"] = list(L["cell_base"])
    hq = {}
    for k in sorted(CP.HQ_LAYOUT):
        spec = CP.HQ_LAYOUT[k]
        if spec.get("centre"):
            hq[k] = [float(round(CX)), float(round(CY))]
        elif "bearing" in spec:
            t = math.radians(spec["bearing"])
            x_, y_ = from_ab(spec["r"] * math.cos(t), spec["r"] * math.sin(t))
            hq[k] = [float(round(x_)), float(round(y_))]

    def pole(members, others, extra_edges=None, bbox=None):
        xs = [cen[i][0] for i in members]
        ys = [cen[i][1] for i in members]
        x0, x1, y0, y1 = bbox or (min(xs), max(xs), min(ys), max(ys))
        O = np.array([cen[i] for i in others])
        M = np.array([cen[i] for i in members])
        best = None
        st = Z["pole_step"]
        for gx in np.arange(math.floor(x0), math.ceil(x1) + st, st):
            for gy in np.arange(math.floor(y0), math.ceil(y1) + st, st):
                # inside the district: its own buildings are nearer than any other's
                dm = np.min(np.hypot(M[:, 0] - gx, M[:, 1] - gy))
                do = np.min(np.hypot(O[:, 0] - gx, O[:, 1] - gy))
                if dm > 2.5:
                    continue
                d = do
                if extra_edges:
                    d = min(d, extra_edges(gx, gy))
                for kk, v in hq.items():
                    if kk != "rebel_cell":
                        d = min(d, math.hypot(gx - v[0], gy - v[1]) - 2 * Z["landmark_r"])
                key = (-round(d, 3), gx, gy)
                if best is None or key < best[0]:
                    best = (key, (float(gx), float(gy)), d)
        return best[1], best[2]

    d_aur = 0.0
    dr = sorted(drowned)
    hq["tethys"], d_teth = pole(dr, [i for i in range(len(B)) if i not in drowned and dist[i] != "tethys"] +
                                [i for i in teth["idx"] if i not in drowned],
                                extra_edges=lambda gx, gy: (b_coast - ab(gx, gy)[1]) * 1.4)
    LMK = [k for k in sorted(hq) if CP.LANDMARK_FP.get(k)]          # the corps with a landmark building
    # ---- L2 clearances: every landmark clears landmark_r round its (new) lot
    keep = []
    for i, b in enumerate(B):
        c = cen[i]
        if any(math.hypot(c[0] - hq[k][0], c[1] - hq[k][1]) < Z["landmark_r"] for k in LMK):
            continue
        keep.append(i)
    # L2 (designer 2026-10-15: no open space round the HQs): every empty lot cell inside an HQ's clearance and outside
    # its landmark's footprint (city_preset.LANDMARK_FP + fp_margin) is built up with blocks of the district, heights
    # drawn from the district's buildings within 14 lots; street tiles stay streets; plazas there are built over
    street_cells = {(t["i"], t["j"]) for t in L["tiles"]}
    occ = set()
    for i in keep:
        for p in B[i]["q"]:
            occ.add((int(math.floor(p[0])), int(math.floor(p[1]))))

    def in_fp(k, x, y, m_lots=None):
        dx, dy = (x - hq[k][0]) * CP.U, -(y - hq[k][1]) * CP.U      # world BU (x east, y north)
        return RU.in_footprint(k, dx, dy, (Z["fp_margin"] if m_lots is None else m_lots) * CP.U)

    def in_any_fp(x, y, m_lots=None):
        return any(in_fp(k, x, y, m_lots) for k in LMK)

    rr = random.Random(CP.SEEDS["zoning"])
    fill = []
    fill_cells = {}
    # refill sites: every new landmark's clearance (outside its footprint) and every OLD HQ lot of the layout that no
    # longer holds a landmark (round 3 moved them; the old plazas are built over: dense city, no empty plazas)
    sites = [(k, hq[k]) for k in LMK if k not in CP.LANDMARK_NO_REFILL] + \
            [("old_" + k, v) for k, v in sorted(hq_old.items())]
    for k, (cx0, cy0) in sites:
        near_h = sorted(B[i]["h"] for i in keep if math.hypot(cen[i][0] - cx0, cen[i][1] - cy0) < 14)
        n0 = len(fill)
        for gi in range(int(cx0 - 8), int(cx0 + 9)):
            for gj in range(int(cy0 - 8), int(cy0 + 9)):
                x, y = gi + 0.5, gj + 0.5
                if math.hypot(x - cx0, y - cy0) > Z["landmark_r"] + 0.6:
                    continue
                if (gi, gj) in street_cells or (gi, gj) in occ or (gi, gj) in fill_cells or in_any_fp(x, y):
                    continue
                if any(math.hypot(x - hq[kk][0], y - hq[kk][1]) < Z["landmark_r"] + 0.6 and kk != k for kk in LMK if kk in CP.LANDMARK_NO_REFILL):
                    continue
                parts = [(0.0, 1.0)] if rr.random() < 0.6 else [(0.0, 0.5), (0.5, 1.0)]
                for (u0, u1) in parts:
                    ins = rr.uniform(0.05, 0.12)
                    nh = max(1, len(near_h) // 2) if not k.startswith("old_") else max(1, len(near_h))
                    h = near_h[rr.randrange(nh)] if near_h else 40.0   # by a landmark: the lower half (it stays legible)
                    x0_, x1_ = gi + ins, gi + 1 - ins
                    y0_, y1_ = gj + u0 + ins, gj + u1 - ins
                    fill.append(dict(q=[[x0_, y0_], [x1_, y0_], [x1_, y1_], [x0_, y1_]], z0=0.0, h=h, ts=1.0,
                                     ink=list(CP.DISTRICTS[""]["hue"]), terr="", ci=-1,
                                     key=900000 + (gi + 300) * 1000 + (gj + 300) + int(u0 * 2) * 1000000))
                fill_cells[(gi, gj)] = k
        print("REFILL", k, len(fill) - n0)
    # ---- fist (round 34 locked outline, lots)
    fist = net.get("fist", [])

    def seg_d(p, a, b):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L2 = dx * dx + dy * dy or 1e-9
        t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
        return math.hypot(p[0] - (a[0] + dx * t), p[1] - (a[1] + dy * t))

    def subside(a_, b_):
        s0, s1 = W["subside"]
        s = s0 + (s1 - s0) * smooth(b_, b_split, b_coast)
        hx, hy = hq["tethys"]
        ha, hb = ab(hx, hy)
        r = math.hypot(a_ - ha, b_ - hb)
        s += W["trench"][0] * math.exp(-(r / W["trench"][1]) ** 2)
        return s

    out_b = []
    for i in keep:
        b = dict(B[i])
        b["terr"] = dist[i]
        c = cen[i]
        b["c"] = [c[0], c[1]]
        if i in drowned:
            b["sub"] = subside(*abs_[i])
            b["wet"] = 1
        else:
            b["sub"] = 0.0
            b["wet"] = 0
        b["crest"] = 0            # round 3 (note 8): the red is not shown yet (no fist windows in this key art)
        out_b.append(b)
    for b in fill:
        c = centroid(b["q"])
        b["c"] = list(c)
        b["sub"], b["wet"] = 0.0, 0
        b["crest"] = 0
        out_b.append(b)
    # ---- H2 / H3 (notes 5, 6): the district of every building by HQ influence (seeded per key), scaled by the organic
    # urban-core factor u; drowned buildings stay Tethys. u is exported for the build (heights, lit share, trims).
    hq_ab = {k: ab(*hq[k]) for k in hq}
    for b in out_b:
        a_, b_ = ab(*b["c"])
        u = RU.urban_u(a_, b_)
        b["u"] = round(u, 4)
        if b["wet"]:
            b["terr"] = "tethys"
            continue
        w, w0 = RU.district_weights(a_, b_, hq_ab, u)
        b["terr"] = RU.draw_district(b["key"], w, w0)
    # ---- tiles: district by the nearest building (within 2.5 lots), lanes recoloured to the district hue for the new
    # corps; tiles in the drowned quarter are submerged
    from collections import defaultdict
    grid = defaultdict(list)
    for b in out_b:
        grid[(int(b["c"][0] // 4), int(b["c"][1] // 4))].append(b)

    def nearest(x, y, r=2.5):
        best = None
        for gx in range(int(x // 4) - 1, int(x // 4) + 2):
            for gy in range(int(y // 4) - 1, int(y // 4) + 2):
                for b in grid.get((gx, gy), ()):
                    d = math.hypot(b["c"][0] - x, b["c"][1] - y)
                    if d < r and (best is None or (d, b["key"]) < best[0]):
                        best = ((d, b["key"]), b)
        return best[1] if best else None

    tiles = []
    for t in L["tiles"]:
        t = dict(t)
        cx_, cy_ = centroid(t["q"])
        nb = nearest(cx_, cy_)
        t["terr"] = nb["terr"] if nb else ""
        a_, b_ = ab(cx_, cy_)
        t["wet"] = 1 if (nb is not None and nb["wet"]) or (b_ >= b_split and a_lo - 1 <= a_ <= a_hi + 1 and t["terr"] == "tethys") else 0
        t["sub"] = subside(a_, b_) if t["wet"] else 0.0
        if t["col"]:          # round 3: the lane hue is the tile's district (the influence draw); sprawl / REBEL_CELL warm
            pal = RU.palette(t["terr"])
            t["col"] = list(pal["sec"] if t["terr"] == "aurelian" else (pal["hue"] if t["terr"] not in ("", "rebel_cell") else (1.0, 0.72, 0.45)))
        t["u"] = round(RU.urban_u(a_, b_), 4)
        t["lm"] = 1 if in_any_fp(cx_, cy_, 0.4) else 0          # under a landmark: no lanes / lamps / streaks
        tiles.append(t)
    plazas = []
    for pz in L["plazas"]:
        pz = dict(pz)
        cx_, cy_ = centroid(pz["q"])
        nb = nearest(cx_, cy_, 3.0)
        pz["terr"] = nb["terr"] if nb else pz["terr"]
        a_, b_ = ab(cx_, cy_)
        pz["wet"] = 1 if nb is not None and nb["wet"] else 0
        pz["sub"] = subside(a_, b_) if pz["wet"] else 0.0
        if any(math.hypot(cx_ - hq[k][0], cy_ - hq[k][1]) < Z["landmark_r"] + 0.6 for k in LMK):
            continue
        if any(math.hypot(cx_ - v[0], cy_ - v[1]) < Z["landmark_r"] + 0.6 for v in hq_old.values()):
            continue
        plazas.append(pz)
    # ---- the lagoon cells (seabed mesh + levee) : lot cells whose nearest building / tile is drowned
    wet_cells = set()
    for t in tiles:
        if t["wet"]:
            wet_cells.add((t["i"], t["j"]))
    for b in out_b:
        if b["wet"]:
            for p in b["q"]:
                wet_cells.add((int(math.floor(p[0])), int(math.floor(p[1]))))
    # close small holes: a cell surrounded on >= 3 sides by wet cells is wet; the HQ clearance is wet
    hx, hy = hq["tethys"]
    for gi in range(int(hx - 7), int(hx + 8)):
        for gj in range(int(hy - 7), int(hy + 8)):
            if math.hypot(gi + 0.5 - hx, gj + 0.5 - hy) < Z["landmark_r"] + 0.8:
                wet_cells.add((gi, gj))
    for _ in range(3):
        add = set()
        cand = {(i + di, j + dj) for (i, j) in wet_cells for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1))} - wet_cells
        for (i, j) in cand:
            n = sum((i + di, j + dj) in wet_cells for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)))
            if n >= 3 and ab(i + 0.5, j + 0.5)[1] >= b_split - 1.5:
                add.add((i, j))
        wet_cells |= add
    # Z6 (art review: no ruler-straight coast) the seawall curves into a BAY: it bows out to sea round the drowned
    # quarter (depth / width in city_preset.BAY), so the drowned blocks and the bay water sit inside the wall; past the
    # bay the land curves seaward into headlands. bc(a) = the wall line (lots of depth b).
    BAY = CP.BAY
    bay_ac = (a_lo + a_hi) / 2.0

    def bc(a_):
        v = b_coast + BAY["depth"] * math.exp(-((a_ - bay_ac) / BAY["width"]) ** 2)
        if abs(a_ - bay_ac) > BAY["head_start"]:
            v += BAY["head_k"] * (abs(a_ - bay_ac) - BAY["head_start"]) ** 2
        return v
    # the drowned quarter runs to the wall: every cell from the coast band out to the wall, where the bay is open water
    for gi in range(-160, 160):
        for gj in range(-160, 160):
            a_, b_ = ab(gi + 0.5, gj + 0.5)
            if b_ < b_coast - 3.0 or b_ > bc(a_) + 1.5:
                continue
            if (a_lo - 2 <= a_ <= a_hi + 2) or (bc(a_) - b_coast > BAY["min_water"] and b_ > b_coast + 0.5):
                wet_cells.add((gi, gj))
    cells = [[i, j, subside(*ab(i + 0.5, j + 0.5))] for (i, j) in sorted(wet_cells)]
    # ---- T1 arterials
    rows, cols = defaultdict(list), defaultdict(list)
    for t in tiles:
        if not t["ab"] or t["wet"]:
            continue
        (x0, y0), (x1, y1) = t["ab"]
        if abs(y1 - y0) < 1e-6:
            rows[t["j"]].append(t)
        else:
            cols[t["i"]].append(t)
    arterials = []
    for axis, lines in (("x", rows), ("y", cols)):
        for key in sorted(lines):
            ts_ = sorted(lines[key], key=lambda t: t["i"] if axis == "x" else t["j"])
            run = [ts_[0]]
            for t in ts_[1:] + [None]:
                if t is not None and 1 <= ((t["i"] - run[-1]["i"]) if axis == "x" else (t["j"] - run[-1]["j"])) <= 3:
                    run.append(t)
                    continue
                if len(run) >= Z["arterial_len"] and np.mean([r["tr"] for r in run]) >= Z["arterial_tr"]:
                    a0 = run[0]["ab"][0]
                    a1 = run[-1]["ab"][1]
                    arterials.append(dict(axis=axis, line=key, a=a0, b=a1, tr=float(np.mean([r["tr"] for r in run])),
                                          col=run[len(run) // 2]["col"] or [1, 1, 1], n=len(run)))
                if t is not None:
                    run = [t]
    # ---- L4 (round 3b, designer): the Meridian FREIGHT RAIL runs from the fortress's north gate to the PORT on a coast
    # stretch far from the drowned quarter (PORT a0..a1: not Tethys' water), along one smooth curve (no 90-degree
    # turns): straight out of the gate, a gentle bend, into the port yard. Its corridor is cleared of buildings (T1).
    mx, my = hq["meridian"]
    RA_ = CP.RAIL      # the north gate: world (gate_u, wall_s + gate_out) from the HQ -> lots (world y flips)
    gate_lot = (mx + RA_["gate_u"] / CP.U, my - (RA_["wall_s"] + RA_["gate_out"]) / CP.U)
    streets = {(t["i"], t["j"]) for t in tiles if not t["wet"]}
    PT = CP.PORT
    port_entry = from_ab(PT["entry_a"], bc(PT["entry_a"]) - PT["depth"] + 1.5)
    port_inner = from_ab(PT["entry_a"] + 12.0, bc(PT["entry_a"] + 12.0) - PT["depth"] * 0.55)
    RW_ = CP.RAIL_WEST          # round 3c: the line runs past the fort's north side (west approach -> the gate -> east, then north-east)
    g_w = [(gate_lot[0] + dx_, gate_lot[1] + dy_) for dx_, dy_ in RW_["west"]]
    g_e = [(gate_lot[0] + dx_, gate_lot[1] + dy_) for dx_, dy_ in RW_["east"]]
    g2 = g_e[-1]
    ga, gb = ab(*g2)
    ea, eb = ab(*port_entry)
    da, db = ea - ga, eb - gb
    dl = math.hypot(da, db)
    mid = from_ab(ga + da * 0.5 - db / dl * 5.0, gb + db * 0.5 + da / dl * 5.0)   # a gentle S: 5 lots off the chord
    simp = [list(p) for p in RU.catmull_rom(g_w + [gate_lot] + g_e + [mid, port_entry, port_inner], CP.CURVES["step"])]
    path = []
    print("RAIL samples", len(simp), "to the port at a", PT["entry_a"])
    # ---- L3 aqueduct
    ax, ay = hq["aurelian"]
    best = None
    for axis, lines in (("x", rows), ("y", cols)):
        for key in sorted(lines):
            off = (key + 0.5 - ay) if axis == "x" else (key + 0.5 - ax)
            if abs(off) < Z["landmark_r"] + 1.0 or abs(off) > Z["landmark_r"] + 9:
                continue
            ts_ = [t for t in lines[key] if t["terr"] == "aurelian" and math.hypot(centroid(t["q"])[0] - ax, centroid(t["q"])[1] - ay) < 22.0]
            if len(ts_) < 8:
                continue
            score = (len(ts_), -abs(off), axis, key)
            if best is None or score > best[0]:
                best = (score, axis, key, ts_)
    _, axis, key, ts_ = best
    if axis == "x":
        u = sorted(t["i"] for t in ts_)
        aq = [[u[0] - Z["aqueduct_ext"], key + 0.5], [u[-1] + 1 + Z["aqueduct_ext"], key + 0.5]]
    else:
        u = sorted(t["j"] for t in ts_)
        aq = [[key + 0.5, u[0] - Z["aqueduct_ext"]], [key + 0.5, u[-1] + 1 + Z["aqueduct_ext"]]]
    # ---- T (round 3b, designer): the Meridian transport HUB (a truck ring road round the HQ lot), highway SPOKES that
    # leave it tangentially along smooth curves (no 90-degree turns), the metro as a smooth closed loop, the port; every
    # corridor is cleared of map buildings and kept off by the ring (CP.CURVES / HUB / SPOKES / PORT / METRO)
    HW = CP.HIGHWAY
    CV = CP.CURVES

    def land_ok(x, y, ext):
        a_, b_ = ab(x, y)
        if b_ > bc(a_) - HW["coast_stop"] or abs(a_) > 200 or b_ < -200:
            return False
        if a_lo - 3 <= a_ <= a_hi + 3 and b_ > b_split - HW["coast_stop"]:
            return False
        if (int(math.floor(x)), int(math.floor(y))) in wet_cells:
            return False
        return abs(x - CX) + abs(y - CY) - 92.0 <= ext

    def line_pt(axis, key, s):
        return (s, key + 0.5) if axis == "x" else (key + 0.5, s)

    def span(axis, key, ext, s_mid):
        ok = [s for s in [k * 0.5 for k in range(-560, 561)] if land_ok(*line_pt(axis, key, s), ext)]
        runs, run = [], []
        for s in ok:
            if run and s - run[-1] > 0.51:
                runs.append(run)
                run = []
            run.append(s)
        if run:
            runs.append(run)
        runs = [r_ for r_ in runs if r_[0] <= s_mid <= r_[-1]] or runs
        r_ = max(runs, key=lambda r_: (r_[-1] - r_[0], -r_[0]))
        return r_[0], r_[-1]

    def in_port(x, y, pad=0.0):
        a_, b_ = ab(x, y)
        return PT["a0"] - pad <= a_ <= PT["a1"] + pad and bc(a_) - PT["depth"] - pad <= b_ <= bc(a_) + PT["quay"] + pad
    paths = [dict(kind="rail", pts=simp, w=2.8 + 2.0)]
    # the hub ring (world BU rounded square outside the footprint, -> lots)
    HB = CP.HUB
    mxw, myw = (mx - CX) * CP.U, -(my - CY) * CP.U
    hh_ = CP.LANDMARK_FP["meridian"][1] + HB["gap"] + HB["w"] / 2.0
    ring_l = [(x / CP.U + CX, -y / CP.U + CY) for (x, y) in RU.rounded_rect(mxw, myw, hh_, hh_, HB["r"], CV["step"] * CP.U)]
    paths.append(dict(kind="hub", pts=ring_l, w=HB["w"], closed=True))
    highways = []
    RG, RM = CP.RING, CP.RAMPS
    stp = CV["step"]

    def clip_end(pp):
        pp = list(pp)
        while len(pp) > 40 and not land_ok(pp[-1][0], pp[-1][1], HW["ext"]):
            pp.pop()
        return pp
    for name in sorted(CP.THROUGH):
        sp_ = CP.THROUGH[name]
        ctrl = [from_ab(*p_) for p_ in sp_["wp"]]
        if sp_.get("to_port"):
            ctrl.append(from_ab(PT["entry_a"] - 6.0, bc(PT["entry_a"] - 6.0) - PT["depth"] + 3.0))
        pts = RU.catmull_rom(ctrl, stp)
        if not sp_.get("to_port"):
            pts = clip_end(pts)
        pts = clip_end(pts[::-1])[::-1]
        highways.append(dict(name=name, pts=[list(p_) for p_ in pts], z=sp_["z"], to_port=bool(sp_.get("to_port"))))
        paths.append(dict(kind="hw", pts=pts, w=HW["width"]))
    # ---- R1 the PERIMETER RING highway round the city core (replaces the metro circle): the urban edge, dilated, smoothed,
    # pushed out, held off the coast / drowned quarter / port
    def ring_ok(a_, b_):
        x_, y_ = from_ab(a_, b_)
        if b_ > bc(a_) - RG["hold"]:
            return False
        if a_lo - 7 <= a_ <= a_hi + 7 and b_ > b_split - RG["hold"] - 2:
            return False
        if PT["a0"] - RG["port_hold"] <= a_ <= PT["a1"] + RG["port_hold"] and b_ > bc(a_) - PT["depth"] - RG["port_hold"]:
            return False
        return (int(math.floor(x_)), int(math.floor(y_))) not in wet_cells

    def rmax_(th):
        r_ = 5.0
        while r_ < 160.0 and ring_ok(r_ * math.cos(th), r_ * math.sin(th)):
            r_ += 0.5
        return r_ - 0.5

    def urban_r_(th):
        r_ = 1.0
        while r_ < 160.0 and RU.urban_u(r_ * math.cos(th), r_ * math.sin(th)) > 0.5:
            r_ += 0.5
        return r_
    nr_ = 180
    prof = RU.ring_profile(urban_r_, rmax_, RG["margin"], RG["dil"], RG["sig1"], RG["sig2"], nr_)
    stride = max(1, int(round(RG["ctrl_deg"] / (360.0 / nr_))))
    rctrl = [from_ab(prof[k] * math.cos(2 * math.pi * k / nr_), prof[k] * math.sin(2 * math.pi * k / nr_)) for k in range(0, nr_, stride)]
    ring_pts = RU.catmull_rom(rctrl, stp, closed=True)
    ring = dict(pts=[list(p_) for p_ in ring_pts], z=RG["z"], w=RG["width"])
    paths.append(dict(kind="hw", pts=ring_pts, w=RG["width"], closed=True))
    # ---- R2 ramps and interchanges
    ROADS = {h_["name"]: RU.LotPath(h_["pts"]) for h_ in highways}
    ROADS["ring"] = RU.LotPath(ring_pts, closed=True)
    ROADS["hub"] = RU.LotPath(ring_l, closed=True)
    ramps = []

    def add_ramp(pts, e0, e1):
        ramps.append(dict(pts=[list(p_) for p_ in pts], ends=[e0, e1], w=RM["w"]))
        paths.append(dict(kind="ramp", pts=pts, w=RM["w"]))
    # hub exits (the kit's S / W / E exits, on the hub's outer kerb): an on-ramp and an off-ramp to the nearest through highway
    for nm_ in sorted(RM["hub_exit"]):
        ex_, ey_ = RM["hub_exit"][nm_]
        E_ = (mx + ex_ / CP.U, my - ey_ / CP.U)
        dl_ = math.hypot(ex_, ey_)
        if abs(ex_) < 1e-6:
            dvec = (0.0, 1.0 if ey_ < 0 else -1.0)
        else:
            dvec = (1.0 if ex_ > 0 else -1.0, 0.0)
        pv = (-dvec[1], dvec[0])
        best = min(("ew", "ns"), key=lambda k: (round(ROADS[k].nearest(E_)[1], 4), k))
        R_ = ROADS[best]
        sn_, _ = R_.nearest(E_)
        s_on = min(R_.L - 4.0, sn_ + RM["hub_d"])
        s_off = max(4.0, sn_ - RM["hub_d"])
        pe, te = R_.at(s_on)
        add_ramp(RU.hermite((E_[0] + pv[0] * 0.5, E_[1] + pv[1] * 0.5), dvec, pe, te, stp, 1.1), "hub", best)
        pf, tf = R_.at(s_off)
        add_ramp(RU.hermite(pf, tf, (E_[0] - pv[0] * 0.5, E_[1] - pv[1] * 0.5), (-dvec[0], -dvec[1]), stp, 1.1), best, "hub")
    # the ring x the through highways: slip ramps (four per crossing), a cloverleaf at the south crossing of the ring and RM clover_at
    mer_c = (mx, my)
    cross = []
    for nm_ in sorted(ROADS):
        if nm_ in ("ring", "hub"):
            continue
        for (sa_, sb_, X_) in RU.intersections(ROADS[nm_], ROADS["ring"]):
            a_, b_ = ab(*X_)
            if b_ > bc(a_) - PT["depth"] - 14.0:
                continue                                        # the port end: no interchange
            cross.append((nm_, sa_, sb_, X_, b_))
    clover = min([c_ for c_ in cross if c_[0] == RM["clover_at"]], key=lambda c_: c_[4], default=None)
    stack_x = RU.intersections(ROADS["ew"], ROADS["ns"])      # the two through highways cross: a stack (cloverleaf loops)
    for (sa_, sb_, X_) in stack_x:
        for pts_, e_ in RU.cloverleaf(ROADS["ew"], sa_, ROADS["ns"], sb_, RM["stack_d"], stp):
            add_ramp(pts_, "ew", "ns")
    print("STACK ew x ns at", [[round(v, 1) for v in X_] for (_, _, X_) in stack_x])
    for (nm_, sa_, sb_, X_, b_) in cross:
        if clover is not None and (nm_, sa_) == (clover[0], clover[1]):
            for pts_, e_ in RU.cloverleaf(ROADS[nm_], sa_, ROADS["ring"], sb_, RM["clover_d"], stp):
                add_ramp(pts_, nm_, "ring")
            continue
        for qa in (1, -1):
            for qb in (1, -1):
                add_ramp(RU.slip(ROADS[nm_], sa_ + qa * RM["slip_d"], -qa, ROADS["ring"], sb_ + qb * RM["slip_d"], qb, stp), nm_, "ring")
    # arterial on / off ramps (core crossings, spaced)
    art_log = []
    for nm_ in ("ew", "ns"):
        R_ = ROADS[nm_]
        cands = []
        for A_ in arterials:
            for (sa_, sb_, X_) in RU.intersections(R_, RU.LotPath([A_["a"], A_["b"]])):
                a_, b_ = ab(*X_)
                if RU.urban_u(a_, b_) < RM["art_u"] or b_ > bc(a_) - PT["depth"] - 16.0:
                    continue
                if math.hypot(X_[0] - mer_c[0], X_[1] - mer_c[1]) < 18.0:
                    continue
                if any(abs(sa_ - c_[1]) < RM["slip_d"] + RM["art_d"] for c_ in cross if c_[0] == nm_):
                    continue
                cands.append((sa_, X_, A_))
        cands.sort(key=lambda c_: c_[0])
        chosen = []
        for c_ in cands:
            if len(chosen) < RM["art_n"] and all(abs(c_[0] - q_[0]) >= RM["art_gap"] for q_ in chosen):
                chosen.append(c_)
        for (sa_, X_, A_) in chosen:
            p0_, t_ = R_.at(sa_)
            rt = (-t_[1], t_[0])
            tb_ = (A_["b"][0] - A_["a"][0], A_["b"][1] - A_["a"][1])
            tl_ = math.hypot(*tb_)
            tb_ = (tb_[0] / tl_, tb_[1] / tl_)
            if tb_[0] * rt[0] + tb_[1] * rt[1] < 0:
                tb_ = (-tb_[0], -tb_[1])
            Pa_ = (X_[0] + tb_[0] * 9.0, X_[1] + tb_[1] * 9.0)
            pf, tf = R_.at(sa_ - RM["art_d"])
            add_ramp(RU.hermite(pf, tf, Pa_, tb_, stp, 1.1), nm_, "ground")
            pe, te = R_.at(sa_ + RM["art_d"])
            add_ramp(RU.hermite(Pa_, (-tb_[0], -tb_[1]), pe, te, stp, 1.1), "ground", nm_)
            art_log.append((nm_, [round(v, 1) for v in X_]))
    print("RAMPS", len(ramps), "ring samples", len(ring_pts), "clover", None if clover is None else [round(v, 1) for v in clover[3]], "arterial junctions", art_log)
    metro = None
    # landmark clearance check (the curves must pass round the landmarks; Meridian's hub and rail start at its lot)
    for P_ in paths:
        for k in LMK:
            if k == "meridian" and P_["kind"] in ("hub", "hw", "rail", "ramp"):
                lim = CP.LANDMARK_FP["meridian"][1] / CP.U + 0.3
            else:
                lim = Z["landmark_r"] + 0.3
            dmin = min(math.hypot(p_[0] - hq[k][0], p_[1] - hq[k][1]) for p_ in P_["pts"])
            if dmin < lim:
                print("WARNING path", P_["kind"], P_["pts"][0], "passes", k, "at %.1f lots (< %.1f)" % (dmin, lim))
    # corridor clearing (T1): map buildings within the half width + margin of any path, and in the port, are removed;
    # the lot cells near the paths and the port are exported for the ring
    from collections import defaultdict as _dd
    bgrid = _dd(list)
    for idx, b in enumerate(out_b):
        bgrid[(int(b["c"][0] // 2), int(b["c"][1] // 2))].append(idx)

    def poly_d(p_, q):
        n_ = len(q)
        ins = False
        for i in range(n_):
            (x0, y0), (x1, y1) = q[i], q[(i + 1) % n_]
            if (y0 > p_[1]) != (y1 > p_[1]) and p_[0] < (x1 - x0) * (p_[1] - y0) / ((y1 - y0) or 1e-12) + x0:
                ins = not ins
        if ins:
            return 0.0
        return min(seg_d(p_, q[i], q[(i + 1) % n_]) for i in range(n_))
    kill = set()
    corr_cells = set()
    for P_ in paths:
        r_ = P_["w"] / 2.0 / CP.U + CV["clear_margin"]
        for (x, y) in P_["pts"]:
            for gx in range(int(x // 2) - 2, int(x // 2) + 3):
                for gy in range(int(y // 2) - 2, int(y // 2) + 3):
                    for idx in bgrid.get((gx, gy), ()):
                        if idx not in kill and not out_b[idx]["wet"] and poly_d((x, y), out_b[idx]["q"]) < r_:
                            kill.add(idx)
            rc = r_ + 0.6
            for ci in range(int(math.floor(x - rc)), int(math.floor(x + rc)) + 1):
                for cj in range(int(math.floor(y - rc)), int(math.floor(y + rc)) + 1):
                    if math.hypot(ci + 0.5 - x, cj + 0.5 - y) < rc:
                        corr_cells.add((ci, cj))
    for idx, b in enumerate(out_b):
        if in_port(b["c"][0], b["c"][1], 0.6):
            kill.add(idx)
    for ci in range(-160, 200):
        for cj in range(-200, 160):
            if in_port(ci + 0.5, cj + 0.5, 1.0):
                corr_cells.add((ci, cj))
    n_cut = len(kill)
    out_b = [b for idx, b in enumerate(out_b) if idx not in kill]
    port = dict(a0=PT["a0"], a1=PT["a1"], depth=PT["depth"], quay=PT["quay"], z=PT["z"],
                wall=[[a_, bc(a_)] for a_ in [PT["a0"] + (PT["a1"] - PT["a0"]) * k / 40 for k in range(41)]])
    print("TRANSIT spokes", [(h_["name"], len(h_["pts"])) for h_ in highways], "hub samples", len(ring_l),
          "corridor buildings removed", n_cut, "corridor cells", len(corr_cells))
    # H6 the arterial trails continue into the sprawl: an end at the map edge extends along its own line (land only,
    # TRAILS.ext lots past the map); the ring keeps its blocks off the extension
    for a in arterials:
        k_ = 0 if a["axis"] == "x" else 1
        s_lo, s_hi = a["a"][k_], a["b"][k_]
        e_lo, e_hi = s_lo, s_hi
        S0, S1 = span(a["axis"], a["line"], CP.TRAILS["ext"], (s_lo + s_hi) / 2)
        if abs(a["a"][0] - CX) + abs(a["a"][1] - CY) > 92.0 - 6.0:
            e_lo = min(s_lo, S0)
        if abs(a["b"][0] - CX) + abs(a["b"][1] - CY) > 92.0 - 6.0:
            e_hi = max(s_hi, S1)
        a["ext"] = [e_lo, e_hi]
    # ---- O1 (art review: no wireframe grid) flags for the outline rules: buildings / tiles on an arterial (within
    # 1.3 lots of its line) and buildings on a district border (another district's building within 2 lots) keep the
    # full crown trim and lane glow; everything else is dimmed in city_build
    def seg_dist(p, a, b):
        return seg_d(p, a, b)
    for b in out_b:
        c = b["c"]
        b["art"] = 1 if any(seg_dist(c, a["a"], a["b"]) < 1.3 for a in arterials) else 0
        nb_ = [o for gx in range(int(c[0] // 4) - 1, int(c[0] // 4) + 2) for gy in range(int(c[1] // 4) - 1, int(c[1] // 4) + 2)
               for o in grid.get((gx, gy), ()) if math.hypot(o["c"][0] - c[0], o["c"][1] - c[1]) < 2.0]
        b["border"] = 1 if any(o["terr"] != b["terr"] for o in nb_) else 0
    # L4b (art director ruling): every building within side_d lots of the rail line is capped so its roof stays
    # under side_cap BU (the deck at deck_z clears it); flagged rail_side so city_build keeps its roof plain
    n_cap = 0
    for b in out_b:
        if b["wet"]:
            continue
        dmin = min(seg_dist(p, simp[k], simp[k + 1]) for p in list(b["q"]) + [b["c"]] for k in range(len(simp) - 1))
        b["rail_side"] = 1 if dmin < RA_["side_d"] else 0
        if b["rail_side"]:
            cap_h = (RA_["side_cap"] - b["z0"] * CP.KH) / CP.KH
            if b["h"] > cap_h:
                b["h"] = cap_h
                n_cap += 1
    print("RAIL side buildings", sum(b.get("rail_side", 0) for b in out_b), "capped", n_cap)
    for t in tiles:
        cx_, cy_ = centroid(t["q"])
        t["art"] = 1 if any(seg_dist((cx_, cy_), a["a"], a["b"]) < 0.8 for a in arterials) else 0
    # ---- export
    O = dict(
        centre=[CX, CY], U=CP.U, KH=CP.KH, b_coast=b_coast, b_split=b_split, lagoon_a=[a_lo, a_hi],
        bay=dict(ac=bay_ac, **BAY),
        hq=hq, hq_clear={"aurelian": d_aur, "tethys": d_teth},
        clusters=[dict(c=s["c"], n=s["n"], mean_b=s["mean_b"], centre=s["centre"], to=("tethys" if s is teth else "aurelian" if s is aur else "sprawl")) for s in stats],
        buildings=out_b, tiles=tiles, plazas=plazas, trails=L["trails"], fist=fist, lagoon_cells=cells,
        arterials=arterials, aqueduct=aq, rail=simp, terr_count={k: sum(1 for b in out_b if b["terr"] == k) for k in CP.DISTRICTS},
        n_fill=len(fill), n_crest=sum(b["crest"] for b in out_b), n_drowned=sum(b["wet"] for b in out_b),
        n_art=sum(b["art"] for b in out_b), n_border=sum(b["border"] for b in out_b),
        hq_old=hq_old, landmarks=LMK, highways=highways, metro=metro, ring=ring, ramps=ramps, hub=dict(pts=[list(p_) for p_ in ring_l], w=CP.HUB["w"]),
        port=port, corr_cells=sorted([list(c) for c in corr_cells]),
    )
    os.makedirs(CP.SCR, exist_ok=True)
    json.dump(O, open(CP.ZONED, "w"))
    print("clusters", [(c["n"], round(c["mean_b"]), c["to"]) for c in O["clusters"]])
    print("hq", {k: [round(v[0], 1), round(v[1], 1)] for k, v in hq.items()}, "clear", O["hq_clear"])
    print("terr", O["terr_count"], "fill", len(fill), "crest", O["n_crest"], "drowned", O["n_drowned"],
          "lagoon cells", len(cells), "b_coast %.1f b_split %.1f" % (b_coast, b_split), "art", O["n_art"], "border", O["n_border"])
    print("arterials", len(arterials), "aqueduct", aq)
    return O


def draw_map(O, path):
    from PIL import Image, ImageDraw
    S = 4
    im = Image.new("RGB", (260 * S, 260 * S), (8, 8, 12))
    d = ImageDraw.Draw(im)
    f = lambda p: ((p[0] + 125) * S, (p[1] + 125) * S)  # noqa: E731
    for c in O["lagoon_cells"]:
        d.rectangle([f((c[0], c[1])), f((c[0] + 1, c[1] + 1))], fill=(10, 30, int(60 + min(150, c[2] * 1.5))))
    for t in O["tiles"]:
        if not t["wet"]:
            d.polygon([f(p) for p in t["q"]], fill=(36, 36, 44))
    for a in O["arterials"]:
        d.line([f(a["a"]), f(a["b"])], fill=(255, 240, 200), width=2)
    for b in O["buildings"]:
        c = RU.palette(b["terr"])["hue"]
        k = (0.4 + min(0.6, b["h"] / 120.0)) * (0.35 + 0.65 * b.get("u", 1.0))
        if b["wet"]:
            k *= 0.45
        if b["terr"] == "rebel_cell":
            k *= 0.6                    # the canyon language, sprawl palette (drawn darker to tell it apart)
        col = tuple(int(v * 255 * k) for v in c)
        d.polygon([f(p) for p in b["q"]], fill=col)
    d.line([f(O["aqueduct"][0]), f(O["aqueduct"][1])], fill=(41, 219, 166), width=5)
    d.line([f(p) for p in O["rail"]], fill=(255, 140, 26), width=3)
    for h_ in O["highways"]:
        d.line([f(p) for p in h_["pts"]], fill=(255, 255, 255), width=6)
    hp_ = O["hub"]["pts"]
    d.line([f(p) for p in hp_ + [hp_[0]]], fill=(255, 200, 120), width=6)
    for a_ in range(int(O["port"]["a0"]), int(O["port"]["a1"]) + 1, 2):
        b0_ = O["b_coast"]
        for (aa, bb) in O["port"]["wall"]:
            if abs(aa - a_) < 1.1:
                b0_ = bb
        d.line([f(from_ab(a_, b0_ - O["port"]["depth"])), f(from_ab(a_, b0_ + O["port"]["quay"]))], fill=(255, 150, 40), width=4)
    rp_ = O["ring"]["pts"]
    d.line([f(p) for p in rp_ + [rp_[0]]], fill=(255, 255, 255), width=6)
    for r_ in O["ramps"]:
        d.line([f(p) for p in r_["pts"]], fill=(120, 240, 255), width=3)
    # the urban core edge (u = 0.5)
    ring = []
    for k in range(360):
        th = 2 * math.pi * k / 360
        r = 1.0
        while r < 140 and RU.urban_u(r * math.cos(th), r * math.sin(th)) > 0.5:
            r += 0.5
        ring.append(f(from_ab(r * math.cos(th), r * math.sin(th))))
    d.line(ring + [ring[0]], fill=(255, 220, 120), width=2)
    for k, v in O["hq"].items():
        x, y = f(v)
        r = CP.ZONING["landmark_r"] * S
        d.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255), width=3)
        d.text((x + r + 4, y - 6), CP.DISTRICTS[k]["name"], fill=(255, 255, 255))
    a0, a1 = -110, 110
    p0, p1 = from_ab(a0, O["b_coast"]), from_ab(a1, O["b_coast"])
    d.line([f(p0), f(p1)], fill=(80, 140, 255), width=4)
    # legend (top view, lots; the map camera looks from the bottom-right toward the coast at the top-left)
    y = 12
    for k in CP.CORPS + [""]:
        c = tuple(int(v * 255 * (0.6 if k == "rebel_cell" else 1.0)) for v in RU.palette(k)["hue"])
        d.rectangle([12, y, 30, y + 14], fill=c)
        d.text((38, y + 1), "%s  %d bldg" % (CP.DISTRICTS[k]["name"], O["terr_count"][k]), fill=(235, 235, 240))
        y += 20
    for txt, c in (("dark blue cells: drowned quarter (seabed)", (60, 110, 220)), ("blue line: coast / seawall", (80, 140, 255)),
                   ("thin cream lines: arterials (light-streaks)", (255, 240, 200)), ("verdigris line: aqueduct", (41, 219, 166)),
                   ("thick white: highways + perimeter ring; cyan: ramps; orange: freight rail", (255, 255, 255)),
                   ("gold contour: the urban core edge (u = 0.5)", (255, 220, 120)),
                   ("circles: landmark clearance (5.6 lots)", (255, 255, 255))):
        d.text((12, y + 4), txt, fill=c)
        y += 18
    im.save(path)


if __name__ == "__main__":
    O = main()
    draw_map(O, os.path.join(CP.SCR, "zoning_map.png"))
