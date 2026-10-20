"""Street r2 layout passes (frontage.silhouette, horizon.break): the part of the art-pass `r2_rules.py` that changes heights."""
import copy

from . import onecity as OC
from .config import R
from .streams import rng


# ---------------------------------------------------------------- the one-city helpers
def _proj(OC, c, p):
    return OC.proj(c, p)


def _border_legs(OC, links):
    legs = []
    for l in sorted(links, key=lambda l: (l["a"], l["b"])):
        if l["state"] != "border":
            continue
        pts = [OC.W(p) for p in l["pts"]]
        for k, (a, c) in enumerate(zip(pts, pts[1:])):
            legs.append(("%s|%s|%d" % (l["a"], l["b"], k), a, c))
    return legs


def _frontage_rows(OC, bases, a, c):
    """The frontage rows of a leg, per side, in order along the leg (the v3 layout rule's band and extension)."""
    ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
    lo, hi = sorted((a[ax], c[ax]))
    lo, hi = lo - max(OC.EXTEND), hi + max(OC.EXTEND)
    fb = (0.8, 6.5)
    rows = {1: [], -1: []}
    for bi in bases:
        if bi["z0"] > 0.05:
            continue
        if ax == 0:
            a0, a1, d0, d1 = bi["x0"], bi["x1"], bi["y0"] - a[1], a[1] - bi["y1"]
        else:
            a0, a1, d0, d1 = bi["y0"], bi["y1"], bi["x0"] - a[0], a[0] - bi["x1"]
        near = d0 if d0 > 0 else d1
        if a1 > lo and a0 < hi and fb[0] < near < fb[1] and a1 - a0 >= OC.MIN_WIDTH:   # the derivation's frontage
            rows[1 if d0 > 0 else -1].append(((a0 + a1) / 2, bi["uid"], bi))
    return {s: [r[2] for r in sorted(v, key=lambda r: (r[0], r[1]))] for s, v in rows.items()}


def _tops(bases):
    tops = {}
    for bi in bases:
        if bi["z0"] > 0.05:
            cx, cy = (bi["x0"] + bi["x1"]) / 2, (bi["y0"] + bi["y1"]) / 2
            for bb in bases:
                if bb["z0"] <= 0.05 and bb["x0"] <= cx <= bb["x1"] and bb["y0"] <= cy <= bb["y1"]:
                    tops[bb["uid"]] = max(tops.get(bb["uid"], 0.0), bi["z0"] + bi["h"])
                    break
    return tops


def horizon_pick(seed, bs, D, route):
    """horizon.break selection: the backdrop towers that become spikes. `bs` = BU building records (`bld_info`), `route` = the route
    column uids. Candidates stand 24..170 BU behind the street, are not route columns, are at least `spike_min_w` wide and project
    inside the OVERVIEW frame; `n_sp` of them are picked by (height + a `spike_pick` jitter), at least `spike_spacing` frame widths
    apart. Returns `(pick, median)`, pick = [(top, sx, far, record)]."""
    H = R["horizon.break"]
    ov, nrm, sa = D["overview"], D["nrm"], D["a"]
    st_axis = 0 if abs(D["a"][1] - D["c"][1]) < 1e-6 else 1
    cand = []
    tops2 = _tops(bs)
    for bi in bs:
        if bi["z0"] > 0.05 or bi["uid"] in route:
            continue
        cx, cy = (bi["x0"] + bi["x1"]) / 2, (bi["y0"] + bi["y1"]) / 2
        far = (cy - sa[1]) * nrm[1] if st_axis == 0 else (cx - sa[0]) * nrm[0]
        if not (H["backdrop_band"][0] < far < H["backdrop_band"][1]):
            continue
        if min(bi["x1"] - bi["x0"], bi["y1"] - bi["y0"]) < H["spike_min_w"]:
            continue
        sx = _proj(OC, ov, (cx, cy, 0.0))[0] / OC.W_
        if not (0.04 < sx < 0.96):
            continue
        cand.append((max(bi["h"], tops2.get(bi["uid"], 0.0)), sx, far, bi))
    med = sorted(c_[0] for c_ in cand)[len(cand) // 2] if cand else 15.0
    r_ = rng(seed, "spikes", D["route_uids"][0])
    n_sp = r_.randint(H["spikes_min"], H["spikes_max"])
    scored = sorted(cand, key=lambda c_: (-(c_[0] + rng(seed, "spike_pick", c_[3]["uid"]).uniform(0, 25.0)), c_[3]["uid"]))
    pick = []
    for top, sx, far, bi in scored:
        if all(abs(sx - p[1]) >= H["spike_spacing"] for p in pick):
            pick.append((top, sx, far, bi))
        if len(pick) >= n_sp:
            break
    return pick, med


# ---------------------------------------------------------------- LAYOUT: frontage.silhouette + horizon.break
def layout_pass(seed, city, links, D):
    """The layout passes on the v3 city `city` (raw lot records: `buildings`, `hqs`), the scope network's `links` and the street
    derivation `D`. Returns `(city', log)`: a copy of the city with the new heights, and the pass log (rhythm, sightline, spikes)."""
    ov = D["overview"]
    LAY = copy.deepcopy(city)
    bymap = {"%d_%d" % (b["ci"], b["key"]): b for b in LAY["buildings"]}
    bases = [dict(OC.bld_info(b)) for b in LAY["buildings"]]
    tops = _tops(bases)
    fl = OC.FLOOR_BU
    KH = OC.KH
    P = R["frontage.silhouette"]
    route = set(D["column_uids"])
    room_top = {}
    for r in D["rooms"].values():
        room_top[r["bld_uid"]] = max(room_top.get(r["bld_uid"], 0), r["floor"] + r["span"])
    # the corp landmark's screen x (Meridian HQ crane) for the sightline term
    hq = OC.W(LAY["hqs"]["meridian"])
    lx = _proj(OC, ov, (hq[0], hq[1], 20.0))[0] / OC.W_
    st_axis = 0 if abs(D["a"][1] - D["c"][1]) < 1e-6 else 1
    st_line = D["a"][1 - st_axis]
    log = dict(raised=0, rows=0, sightline=[], spikes=[], crowns=[])
    done, assigned = set(), {}

    def on_netrun(leg):                      # the netrun street's own legs go first: its row is the one the camera sees
        _, a, c = leg
        ax = 0 if abs(a[1] - c[1]) < 1e-6 else 1
        return 0 if ax == st_axis and abs(a[1 - ax] - st_line) < 1e-3 else 1
    for lid, a, c in sorted(_border_legs(OC, links), key=lambda lg: (on_netrun(lg), lg[0])):
        rows = _frontage_rows(OC, bases, a, c)
        for side in (1, -1):
            row = rows[side]
            if not row or all(b["uid"] in done for b in row):
                continue
            log["rows"] += 1
            prev_cls, run, prev_f = None, 0, None
            hist = []
            for b in row:
                if b["uid"] in done:            # a corner building set by a crossing row: fixed, but still a neighbour
                    prev_f = assigned[b["uid"]]
                    hist.append(prev_f)
                    continue
                done.add(b["uid"])
                r_ = rng(seed, "frontage", b["uid"])
                top0 = max(b["h"], tops.get(b["uid"], 0.0))
                f0 = int(top0 / fl)
                # rhythm class: never the same class 3 times running
                cls = r_.choices(("low", "mid", "tall"), weights=[P["rhythm_p"][k] for k in ("low", "mid", "tall")])[0]
                if cls == prev_cls and run >= 2:
                    cls = ("low", "mid", "tall")[(("low", "mid", "tall").index(cls) + 1 + r_.randrange(2)) % 3]
                lo, hi = P["floors_" + cls]
                f = r_.randint(lo, hi)
                f = max(f, P["frontage_min_floors"])
                if b["uid"] in route:
                    f = max(f, room_top.get(b["uid"], 6) + P["route_sign_floors"])
                # the netrun street's sightline to the landmark
                on_street = abs(((b["y0"] + b["y1"]) / 2 if st_axis == 0 else (b["x0"] + b["x1"]) / 2) - st_line) < 20
                if on_street and b["uid"] not in route:
                    xs = [_proj(OC, ov, (x, y, 0.0))[0] / OC.W_ for x in (b["x0"], b["x1"]) for y in (b["y0"], b["y1"])]
                    if min(xs) - P["sightline_pad"] < lx < max(xs) + P["sightline_pad"]:
                        f = min(f, P["sightline_floors"])
                        log["sightline"].append(b["uid"])
                stacked = tops.get(b["uid"], 0.0) > b["h"] + 1e-6
                floor_min = max(P["frontage_min_floors"], f0 if stacked else 0)   # stacked parts are never cut
                f = max(f, floor_min)
                # no flat stretch: any 3 neighbours span at least triple_span_min floors
                if len(hist) >= 2:
                    lo3, hi3 = min(hist[-2:] + [f]), max(hist[-2:] + [f])
                    if hi3 - lo3 < P["triple_span_min"]:
                        mean2 = sum(hist[-2:]) / 2.0
                        if f >= mean2 or min(hist[-2:]) + P["triple_span_min"] <= P["floors_tall"][1]:
                            f = max(f, min(hist[-2:]) + P["triple_span_min"])
                        if f < mean2 and max(hist[-2:]) - P["triple_span_min"] >= floor_min:
                            f = max(hist[-2:]) - P["triple_span_min"]
                st_ = P["height_step_min"]
                if prev_f is not None and abs(f - prev_f) < st_:
                    down = prev_f - st_
                    f = down if (f < prev_f and down >= floor_min) else prev_f + st_
                want = f * fl + 0.1
                if abs(top0 - want) > 0.05 and not (stacked and top0 > want):
                    bymap[b["uid"]]["h"] = want / KH
                    log["raised" if want > top0 else "lowered"] = log.get("raised" if want > top0 else "lowered", 0) + 1
                prev_f = f if not (stacked and top0 > want) else f0
                assigned[b["uid"]] = prev_f
                log.setdefault("rhythm", {})[b["uid"]] = [lid, side, f, round(top0, 1), stacked]
                hist.append(prev_f)
                run = run + 1 if cls == prev_cls else 1
                prev_cls = cls
    # horizon.break: spikes in the backdrop of the netrun street
    H = R["horizon.break"]
    bs2 = [dict(OC.bld_info(b)) for b in LAY["buildings"]]
    pick, med = horizon_pick(seed, bs2, D, route)
    for top, sx, far, bi in pick:
        cx, cy = (bi["x0"] + bi["x1"]) / 2, (bi["y0"] + bi["y1"]) / 2
        ty = rng(seed, "spike_top", bi["uid"]).uniform(*H["spike_top"]) * OC.H_
        lo_, hi_ = 1.0, 400.0
        for _ in range(40):
            mid = (lo_ + hi_) / 2
            if _proj(OC, ov, (cx, cy, mid))[1] > ty:
                lo_ = mid
            else:
                hi_ = mid
        z = max(hi_, H["spike_k"] * med, top)
        bymap[bi["uid"]]["h"] = z / KH
        log["spikes"].append(dict(key=bi["uid"], z=round(z, 1), sx=round(sx, 3), far=round(far, 1)))
    log["backdrop_median"] = round(med, 1)
    return LAY, log
