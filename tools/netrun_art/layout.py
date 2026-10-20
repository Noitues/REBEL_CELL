"""layout: city.json / net.json helpers and the mainline layout rules (spec 3.1, 3.2; 2.2 `layout.*`).

Ports `SB/sb_onecity.py` c83e3b00 (`apply_layout_rules`, `merged_buildings`, `bld_info`) and `M44/layout36.py` 96c1af6f
(`W`, `lots`, the street BFS) to the NA-02 shapes. Everything is BU plan coordinates; `bid` replaces the legacy `key`
(the legacy `key` only feeds the `abs(key) % 3` height jitter). A border link is defined by O-D (NA03_NA04_ANSWERS).
Standard library only.
"""
import copy
import math
from collections import deque
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple

from .units import FLOOR_BU

Pt = Sequence[float]

LAYOUT_RULES: Dict[str, Any] = dict(
    frontage_min_floors=6, border_street_width=8.0, base_street_width=6.0, face_tol=0.05,
    hero_sign_rule=dict(blade=True, band=True, palette=["district_a", "district_b"]))
# Street frontage numbers shared with derive.street (spec 3.3 table; SB/sb_onecity.py RULES)
FRONT_BAND = (0.8, 6.5)     # near-edge distance band from the leg centre line, BU
EXTEND = (12.0, 60.0)       # a leg extends this far before its start / past its end, BU
BASE_TOL = 0.05             # a part with z0 <= this stands on the street level
AXIS_TOL = 1e-6
FACE_TOL = 0.05             # vertices this close to the street face move with it
OPEN_STATES = ("open", "opened")
OWN_STATES = ("core", "owned")
CORP_STATES = ("corporate", "taken")
BFS_STEPS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def lot_to_plan(lot: Pt, origin_lot: Pt, lot_bu: float) -> List[float]:
    """Plan BU `[x, y]` of a lot point (`M44/layout36.py` `W`)."""
    return [(lot[0] - origin_lot[0]) * lot_bu, -(lot[1] - origin_lot[1]) * lot_bu]


def plan_to_lot(p: Pt, origin_lot: Pt, lot_bu: float) -> List[float]:
    """Lot point of a plan BU point (`layout36.lots`)."""
    return [p[0] / lot_bu + origin_lot[0], origin_lot[1] - p[1] / lot_bu]


def poly_bbox(poly: Sequence[Pt]) -> Tuple[float, float, float, float]:
    """`(x0, x1, y0, y1)` of a polygon."""
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), max(xs), min(ys), max(ys)


def base_part_index(b: Dict[str, Any]) -> Optional[int]:
    """Index of the street-level base part of a building (z0 <= 0.05, largest footprint box, lowest index), or None."""
    best = None
    for i, p in enumerate(b["parts"]):
        if p["z0"] > BASE_TOL:
            continue
        x0, x1, y0, y1 = poly_bbox(p["poly"])
        key = (-(x1 - x0) * (y1 - y0), i)
        if best is None or key < best[0]:
            best = (key, i)
    return best[1] if best else None


def building_info(b: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """The building as the game reads it (spec 3.1): base box, top of the highest part, tier indices.

    `parts` lists the base index and every stacked part (z0 > 0.05) whose footprint centre lies inside the base box,
    sorted ascending. None when no part stands on the street level.
    """
    bi = base_part_index(b)
    if bi is None:
        return None
    base = b["parts"][bi]
    x0, x1, y0, y1 = poly_bbox(base["poly"])
    members = [bi]
    for j, p in enumerate(b["parts"]):
        if j == bi or p["z0"] <= BASE_TOL:
            continue
        px0, px1, py0, py1 = poly_bbox(p["poly"])
        cx, cy = (px0 + px1) / 2, (py0 + py1) / 2
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            members.append(j)
    top = max(b["parts"][j]["z0"] + b["parts"][j]["h"] for j in members)
    return dict(bid=b["bid"], key=b["key"], hq=bool(b["hq"]), base=bi, x0=x0, x1=x1, y0=y0, y1=y1, z0=base["z0"],
                h=top, ts=base["taper"], parts=sorted(members))


def merged_buildings(city: Dict[str, Any], include_hq: bool = False) -> List[Dict[str, Any]]:
    """`building_info` of every street-level building, sorted by `bid`; HQ stand-ins only when `include_hq`."""
    out = []
    for b in sorted(city["buildings"], key=lambda q: q["bid"]):
        if b["hq"] and not include_hq:
            continue
        bi = building_info(b)
        if bi:
            out.append(bi)
    return out


def border_links(net: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Border links (O-D): open or opened, one end core/owned, the other corporate/taken. Sorted by `(a, b)`."""
    st = {n["id"]: n["state"] for n in net["nodes"]}
    out = []
    for l in sorted(net["links"], key=lambda q: (q["a"], q["b"])):
        if l["state"] not in OPEN_STATES:
            continue
        sa, sb = st.get(l["a"]), st.get(l["b"])
        if (sa in OWN_STATES and sb in CORP_STATES) or (sb in OWN_STATES and sa in CORP_STATES):
            out.append(l)
    return out


def coast_of(city: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """NA-12 r2: a generated city's optional `coast` section as {"sea_side", "shoreline" set, "sea_cells" set} of `(i, j)`
    lots, or None (the fixed city has no sea)."""
    c = city.get("coast")
    if c is None:
        return None
    return {"sea_side": c["sea_side"], "shoreline": {(int(p[0]), int(p[1])) for p in c["shoreline"]},
            "sea_cells": {(int(p[0]), int(p[1])) for p in c["sea_cells"]}}


def hills_of(city: Dict[str, Any]) -> List[Dict[str, Any]]:
    """NA-12 r2: the optional `terrain.hills` (plan BU, city_A2.json's Gaussian form), [] when absent."""
    return list(city.get("terrain", {}).get("hills", []))


def hill_height(hills: Sequence[Dict[str, Any]], x: float, y: float) -> float:
    """Ground height (BU) at plan point (x, y): the sum of the rotated Gaussians (data only until NA-12c renders it)."""
    z = 0.0
    for h in hills:
        dx, dy = x - float(h["centre"][0]), y - float(h["centre"][1])
        r = float(h["rotation"])
        u = dx * math.cos(r) + dy * math.sin(r)
        v = -dx * math.sin(r) + dy * math.cos(r)
        z += float(h["height"]) * math.exp(-0.5 * ((u / float(h["sigma_x"])) ** 2 + (v / float(h["sigma_y"])) ** 2))
    return z


def street_cells(city: Dict[str, Any]) -> set:
    """Set of `(i, j)` street lot cells."""
    return {(int(s["lot"][0]), int(s["lot"][1])) for s in city["streets"]}


def _bfs(a: Tuple[int, int], b: Tuple[int, int], cells: set) -> Optional[List[Tuple[int, int]]]:
    """A shortest 4-connected cell path `a -> b`; ties: fewest turns, then the lowest tile `(i, j)` at each step.

    Link routing over street tiles is intended (AD 2026-10-18 Q3). Distances come from a BFS out of `b`; the walk from
    `a` then keeps only steps that lower the distance, scored by `(turns to go, next tile)` with a memoised DP.
    """
    dist = {b: 0}
    q = deque([b])
    while q:
        c = q.popleft()
        for di, dj in BFS_STEPS:
            n = (c[0] + di, c[1] + dj)
            if n in cells and n not in dist:
                dist[n] = dist[c] + 1
                q.append(n)
    if a not in dist:
        return None
    memo: Dict[Tuple[Tuple[int, int], Optional[Tuple[int, int]]], Tuple[int, Tuple[int, int]]] = {}

    def best(c: Tuple[int, int], d: Optional[Tuple[int, int]]) -> Tuple[int, Optional[Tuple[int, int]]]:
        """`(turns still to make, next tile)` from tile `c` having arrived with step `d`."""
        if c == b:
            return 0, None
        key = (c, d)
        if key not in memo:
            opts = []
            for di, dj in BFS_STEPS:
                n = (c[0] + di, c[1] + dj)
                if n in dist and dist[n] == dist[c] - 1:
                    opts.append((best(n, (di, dj))[0] + (1 if d is not None and d != (di, dj) else 0), n))
            memo[key] = min(opts)
        return memo[key]

    out = [a]
    d: Optional[Tuple[int, int]] = None
    while out[-1] != b:
        c = out[-1]
        n = best(c, d)[1]
        d = (n[0] - c[0], n[1] - c[1])
        out.append(n)
    return out


def _simplify(path: Sequence[Tuple[int, int]]) -> List[List[float]]:
    """Cell path -> polyline of the corner cell centres (lots)."""
    pts = [[c[0] + 0.5, c[1] + 0.5] for c in path]
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, b, c = out[-1], pts[i], pts[i + 1]
        if (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0]) != 0:
            out.append(b)
    out.append(pts[-1])
    return out


def _nearest_cell(p: Pt, cells: Sequence[Tuple[int, int]]) -> Tuple[int, int]:
    best = None
    for c in cells:
        key = (math.hypot(c[0] + 0.5 - p[0], c[1] + 0.5 - p[1]), c)
        if best is None or key < best:
            best = key
    return best[1]


def route_on_streets(city: Dict[str, Any], a: Pt, b: Pt) -> List[List[float]]:
    """Axis-aligned plan polyline (BU) from `a` to `b` along street tiles (`layout36` BFS + simplify).

    Falls back to an L-shaped route when the two points share a cell or no street path exists.
    """
    ol, lb = city["origin_lot"], city["lot_bu"]
    cells = sorted(street_cells(city))
    la, lb_pt = plan_to_lot(a, ol, lb), plan_to_lot(b, ol, lb)
    if cells:
        ca, cb = _nearest_cell(la, cells), _nearest_cell(lb_pt, cells)
        path = _bfs(ca, cb, set(cells)) if ca != cb else None
        if path and len(path) >= 2:
            return [lot_to_plan(p, ol, lb) for p in _simplify(path)]
    return [list(a), [b[0], a[1]], list(b)]


def link_legs(city: Dict[str, Any], pts: Sequence[Pt]) -> List[List[float]]:
    """The link polyline made of axis-aligned legs: a diagonal segment is replaced by a street route (NA02 O3)."""
    out: List[List[float]] = [list(pts[0])]
    for p, q in zip(pts, pts[1:]):
        if abs(p[0] - q[0]) < AXIS_TOL or abs(p[1] - q[1]) < AXIS_TOL:
            out.append(list(q))
        else:
            out += route_on_streets(city, p, q)[1:]
    return out


def leg_axis(a: Pt, c: Pt) -> int:
    """0 when the leg runs along x, else 1 (`sb_onecity` convention)."""
    return 0 if abs(a[1] - c[1]) < AXIS_TOL else 1


def apply_layout_rules(city: Dict[str, Any], net: Dict[str, Any], rules: Optional[Dict[str, Any]] = None,
                       stats: Optional[Dict[str, int]] = None, border_mode: str = "state") -> Dict[str, Any]:
    """`layout.rules`: a new city.json with the street-front band raised and border streets widened (spec 3.2).

    Every street-level non-HQ building whose near edge lies within `FRONT_BAND` of a leg of a border link (extended
    by `max(EXTEND)` each way) is processed once (first link, then first leg): its street face steps back by
    `(border_street_width - base_street_width) / 2` and its height rises to
    `(frontage_min_floors + abs(key) % 3) * FLOOR_BU + 0.1`. With no border link the city is returned unchanged.
    `stats` (optional dict) receives `frontage`, `raised`, `moved` counts.
    """
    r = dict(LAYOUT_RULES, **(rules or {}))
    out = copy.deepcopy(city)
    step = (r["border_street_width"] - r["base_street_width"]) / 2.0
    bases = merged_buildings(city)
    byid = {b["bid"]: b for b in out["buildings"]}
    done: set = set()
    raised = moved = 0
    reach = max(EXTEND)
    for link in links_of(net, border_mode):
        legs = link_legs(city, link["pts"])
        for a, c in zip(legs, legs[1:]):
            ax = leg_axis(a, c)
            lo, hi = sorted((a[ax], c[ax]))
            lo, hi = lo - reach, hi + reach
            for bi in bases:
                if bi["bid"] in done:
                    continue
                if ax == 0:
                    a0, a1, d0, d1 = bi["x0"], bi["x1"], bi["y0"] - a[1], a[1] - bi["y1"]
                else:
                    a0, a1, d0, d1 = bi["y0"], bi["y1"], bi["x0"] - a[0], a[0] - bi["x1"]
                near = d0 if d0 > 0 else d1
                if not (a1 > lo and a0 < hi and FRONT_BAND[0] < near < FRONT_BAND[1]):
                    continue
                done.add(bi["bid"])
                base = byid[bi["bid"]]["parts"][bi["base"]]
                sgn = 1.0 if d0 > 0 else -1.0
                ref = (bi["y0"] if sgn > 0 else bi["y1"]) if ax == 0 else (bi["x0"] if sgn > 0 else bi["x1"])
                k = 1 if ax == 0 else 0
                for p in base["poly"]:
                    if abs(p[k] - ref) < r["face_tol"]:
                        p[k] += sgn * step
                        moved += 1
                want = (r["frontage_min_floors"] + abs(bi["key"]) % 3) * FLOOR_BU + 0.1
                if bi["h"] < want:
                    base["h"] = want - base["z0"]
                    raised += 1
    if stats is not None:
        stats.update(frontage=len(done), raised=raised, moved=moved)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# NA-11: the street r2 height passes (frontage.silhouette, horizon.break) and the full rule pipeline.
# Ports `street_r2/scripts/r2_rules.py` `layout_pass` (art-pass ded90765, the revision in this repo's history; ed8675a8
# was not reachable): see docs/handoff/plan2/drafts/NA11_RULES.md. Changes from the original: draws are splitmix64 art
# streams (not Python's `random`), the sightline term and the screen-projected spike heights are dropped (no camera at
# layout time), and the passes are keyed on `bid`.
# ---------------------------------------------------------------------------------------------------------------------
R2_RULES: Dict[str, Any] = dict(
    # r2_config.py RULES_R2["frontage.silhouette"]
    # CITY-A2 step 2 (A-039): the floors of art-pass r2_config.py RULES_R2 as the street r2 renders them (ded90765 had 6-7 / 8-9 / 9-10)
    silhouette=dict(floors_low=[6, 8], floors_mid=[9, 13], floors_tall=[14, 21], rhythm_p=[0.34, 0.33, 0.33],
                    height_step_min=2, triple_span_min=6, route_sign_floors=3, rotate_run=2, base_h_eps=0.05),
    # RULES_R2["horizon.break"]; spike_spacing_bu replaces the 1/6-frame spacing (no camera at layout time)
    horizon=dict(spikes_min=3, spikes_max=5, spike_k=1.6, backdrop_band=[24.0, 170.0], spike_min_w=4.0,
                 spike_spacing_bu=30.0, pick_jitter=25.0, default_median=15.0),
    # NA-11c (art-pass W1_NA11 fix 2): within `zone_lots` lots of an HQ lot no building is taller than `cap_k` x the HQ
    # stand-in top (the landmark top; landmarks lead), and those buildings are exempt from spikes. Route columns keep their height.
    hq=dict(zone_lots=2.0, cap_k=0.6, clamp_eps=0.1),
)
RHYTHM = ("low", "mid", "tall")


def links_of(net: Dict[str, Any], border_mode: str = "state") -> List[Dict[str, Any]]:
    """The links the rules treat as border streets, sorted by `(a, b)`.

    "state": `border_links` (O-D, by Grid state). "all": every link, state ignored (the fixed city, NA-11 ruling).
    """
    if border_mode == "all":
        return sorted(net["links"], key=lambda q: (q["a"], q["b"]))
    return border_links(net)


def _draws(layout_seed: Any, stream: str, *keys: Any) -> Iterator[float]:
    """Uniform draws in `[0, 1)` of the art stream (`seeds.art_seed`, then splitmix64)."""
    from . import seeds
    for x in seeds.splitmix64(seeds.art_seed(layout_seed, stream, *keys)):
        yield seeds.uniform(x)


def _randint(u: float, lo: int, hi: int) -> int:
    """Integer in `[lo, hi]` from one uniform draw."""
    return lo + min(int(math.floor(u * (hi - lo + 1))), hi - lo)


def frontage_rows(bases: List[Dict[str, Any]], a: Pt, c: Pt) -> Dict[int, List[Dict[str, Any]]]:
    """The frontage rows of a leg per side (`+1` / `-1`), in order along the leg (ties by `bid`): the 3.2 band and extension."""
    ax = leg_axis(a, c)
    lo, hi = sorted((a[ax], c[ax]))
    reach = max(EXTEND)
    lo, hi = lo - reach, hi + reach
    rows: Dict[int, list] = {1: [], -1: []}
    for bi in bases:
        if ax == 0:
            a0, a1, d0, d1 = bi["x0"], bi["x1"], bi["y0"] - a[1], a[1] - bi["y1"]
        else:
            a0, a1, d0, d1 = bi["y0"], bi["y1"], bi["x0"] - a[0], a[0] - bi["x1"]
        near = d0 if d0 > 0 else d1
        if a1 > lo and a0 < hi and FRONT_BAND[0] < near < FRONT_BAND[1]:
            rows[1 if d0 > 0 else -1].append(((a0 + a1) / 2.0, bi["bid"], bi))
    return {s: [r[2] for r in sorted(v, key=lambda r: (r[0], r[1]))] for s, v in rows.items()}


def is_stacked(b: Dict[str, Any], bi: Dict[str, Any]) -> bool:
    """True when a part above the base reaches higher than the base (the building's top is not its base)."""
    base = b["parts"][bi["base"]]
    return bi["h"] > base["z0"] + base["h"] + 1e-6


def frontage_silhouette(city: Dict[str, Any], net: Dict[str, Any], rules: Optional[Dict[str, Any]] = None,
                        route_tops: Optional[Dict[str, int]] = None, border_mode: str = "state",
                        stats: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """`frontage.silhouette` (r2_rules.py:115-215): the street front is a rhythm of heights, not a flat band.

    Per side of every border leg (links by `(a, b)`, legs in order), buildings along the leg take a class
    (low / mid / tall, never 3 in a row) and a floor count in its range. A floor count never drops under
    `frontage_min_floors`; any 3 neighbours span at least `triple_span_min` floors; neighbours differ by at least
    `height_step_min`. `route_tops` (bid -> top room floor) lifts a route column to that plus `route_sign_floors` (the
    hero sign zone, r2 `route_sign_floors`). A building with stacked parts is never changed. Each building is set once
    (first leg that reaches it). Draws: stream `frontage`, key `bid`: class, rotate, floors.
    """
    r = dict(LAYOUT_RULES, **(rules or {}))
    P = R2_RULES["silhouette"]
    min_f = int(r["frontage_min_floors"])
    out = copy.deepcopy(city)
    byid = {b["bid"]: b for b in out["buildings"]}
    bases = merged_buildings(city)
    route_tops = route_tops or {}
    seed = city["layout_seed"]
    done: set = set()
    assigned: Dict[str, int] = {}
    n_set = 0
    for link in links_of(net, border_mode):
        legs = link_legs(city, link["pts"])
        for a, c in zip(legs, legs[1:]):
            rows = frontage_rows(bases, a, c)
            for side in (1, -1):
                prev_cls: Optional[str] = None
                run = 0
                prev_f: Optional[int] = None
                hist: List[int] = []
                for bi in rows[side]:
                    bid = bi["bid"]
                    if bid in done:
                        prev_f = assigned[bid]
                        hist.append(prev_f)
                        continue
                    done.add(bid)
                    b = byid[bid]
                    d = _draws(seed, "frontage", bid)
                    u_cls, u_rot, u_fl = next(d), next(d), next(d)
                    top0 = bi["h"]
                    f0 = int(top0 / FLOOR_BU)
                    acc, cls = 0.0, RHYTHM[-1]
                    for name, p in zip(RHYTHM, P["rhythm_p"]):
                        acc += p
                        if u_cls * sum(P["rhythm_p"]) < acc:
                            cls = name
                            break
                    if cls == prev_cls and run >= P["rotate_run"]:
                        cls = RHYTHM[(RHYTHM.index(cls) + 1 + int(u_rot * 2)) % 3]
                    lo, hi = P["floors_" + cls]
                    f = max(_randint(u_fl, lo, hi), min_f)
                    if bid in route_tops:
                        f = max(f, route_tops[bid] + P["route_sign_floors"])
                    stacked = is_stacked(b, bi)
                    floor_min = max(min_f, f0 if stacked else 0)
                    f = max(f, floor_min)
                    span = P["triple_span_min"]
                    if len(hist) >= 2:
                        lo3, hi3 = min(hist[-2:] + [f]), max(hist[-2:] + [f])
                        if hi3 - lo3 < span:
                            mean2 = sum(hist[-2:]) / 2.0
                            lift, drop = min(hist[-2:]) + span, max(hist[-2:]) - span
                            ceil_f = P["floors_tall"][1]
                            if f >= mean2 and lift <= ceil_f:
                                f = lift
                            elif drop >= floor_min:
                                f = drop
                            elif lift <= ceil_f:
                                f = lift
                    step = P["height_step_min"]
                    if prev_f is not None and abs(f - prev_f) < step:
                        down = prev_f - step
                        go_down = down >= floor_min and (f < prev_f or prev_f + step > P["floors_tall"][1])
                        f = down if go_down else prev_f + step
                    want = f * FLOOR_BU + 0.1
                    got = f0 if stacked else f
                    if not stacked and abs(top0 - want) > P["base_h_eps"]:
                        base = b["parts"][bi["base"]]
                        base["h"] = want - base["z0"]
                        n_set += 1
                    assigned[bid] = got
                    prev_f = got
                    hist.append(got)
                    run = run + 1 if cls == prev_cls else 1
                    prev_cls = cls
    if stats is not None:
        stats.update(silhouette_buildings=len(done), silhouette_set=n_set)
    return out


def hq_rects(city: Dict[str, Any]) -> List[Tuple[float, float, float, float, float]]:
    """`(x0, x1, y0, y1, top)` of every HQ stand-in (plan bbox of all its parts, top of the highest part), by `bid`."""
    out = []
    for b in sorted(city["buildings"], key=lambda q: q["bid"]):
        if not b["hq"] or not b["parts"]:
            continue
        bb = [poly_bbox(p["poly"]) for p in b["parts"]]
        out.append((min(q[0] for q in bb), max(q[1] for q in bb), min(q[2] for q in bb), max(q[3] for q in bb),
                    max(p["z0"] + p["h"] for p in b["parts"])))
    return out


def hq_zone_top(city: Dict[str, Any], bi: Dict[str, Any]) -> Optional[float]:
    """The HQ top (BU) of the tallest HQ lot within `zone_lots` lots of building `bi` (plan gap, both axes), else None."""
    reach = R2_RULES["hq"]["zone_lots"] * city["lot_bu"]
    best = None
    for x0, x1, y0, y1, top in hq_rects(city):
        gap = max(x0 - bi["x1"], bi["x0"] - x1, y0 - bi["y1"], bi["y0"] - y1, 0.0)
        if gap <= reach and (best is None or top > best):
            best = top
    return best


def hq_cap(city: Dict[str, Any], route_bids: Sequence[str] = (), stats: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """Within `zone_lots` lots of an HQ lot no building is taller than `cap_k` x the HQ stand-in top (route columns exempt).

    Every part of a too-tall building is clamped: `h <= cap - z0`; a stacked part that would start at or above the cap
    drops to `cap - clamp_eps`, so the building top is the cap.
    """
    P = R2_RULES["hq"]
    out = copy.deepcopy(city)
    byid = {b["bid"]: b for b in out["buildings"]}
    route = set(route_bids)
    n = 0
    for bi in merged_buildings(city):
        top = hq_zone_top(city, bi)
        if top is None or bi["bid"] in route:
            continue
        cap = P["cap_k"] * top
        if bi["h"] <= cap + 1e-9:
            continue
        n += 1
        for j in bi["parts"]:
            part = byid[bi["bid"]]["parts"][j]
            part["z0"] = min(part["z0"], cap - P["clamp_eps"])
            part["h"] = min(part["h"], cap - part["z0"])
    if stats is not None:
        stats.update(hq_capped=n)
    return out


def horizon_break(city: Dict[str, Any], net: Dict[str, Any], route_bids: Sequence[str] = (), border_mode: str = "state",
                  stats: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """`horizon.break` (r2_rules.py:216-251): `spikes_min..spikes_max` backdrop towers reach `spike_k` x the median roof (the cap; NA-11c 1.6).

    The reference street is the first leg of the first border link. Candidates: street-level, unstacked, non-route
    buildings centred `backdrop_band` BU behind the street line (either side) along the extended leg, with a footprint
    of at least `spike_min_w`. Picks by `(-(top + jitter), bid)`, jitter a `spike_pick` draw x `pick_jitter`, at least
    `spike_spacing_bu` apart along the street. Raised to `max(spike_k * median, top)`, never lowered. No border link: unchanged.
    """
    H = R2_RULES["horizon"]
    out = copy.deepcopy(city)
    links = links_of(net, border_mode)
    if not links:
        return out
    legs = link_legs(city, links[0]["pts"])
    if len(legs) < 2:
        return out
    a, c = legs[0], legs[1]
    ax = leg_axis(a, c)
    lo, hi = sorted((a[ax], c[ax]))
    lo, hi = lo - max(EXTEND), hi + max(EXTEND)
    byid = {b["bid"]: b for b in out["buildings"]}
    route = set(route_bids)
    cand = []
    for bi in merged_buildings(city):
        if bi["bid"] in route or is_stacked(byid[bi["bid"]], bi) or hq_zone_top(city, bi) is not None:
            continue
        if ax == 0:
            along, far = (bi["x0"] + bi["x1"]) / 2.0, abs((bi["y0"] + bi["y1"]) / 2.0 - a[1])
        else:
            along, far = (bi["y0"] + bi["y1"]) / 2.0, abs((bi["x0"] + bi["x1"]) / 2.0 - a[0])
        if not (lo <= along <= hi and H["backdrop_band"][0] < far < H["backdrop_band"][1]):
            continue
        if min(bi["x1"] - bi["x0"], bi["y1"] - bi["y0"]) < H["spike_min_w"]:
            continue
        cand.append((bi["h"], along, bi))
    med = sorted(x[0] for x in cand)[len(cand) // 2] if cand else H["default_median"]
    seed = city["layout_seed"]
    n_sp = _randint(next(_draws(seed, "spikes", links[0]["a"], links[0]["b"])), H["spikes_min"], H["spikes_max"])
    scored = sorted(((-(t + next(_draws(seed, "spike_pick", bi["bid"])) * H["pick_jitter"]), bi["bid"], t, al, bi)
                     for t, al, bi in cand), key=lambda s: (s[0], s[1]))
    picked: List[float] = []
    for _, bid, t, al, bi in scored:
        if len(picked) >= n_sp:
            break
        if all(abs(al - p) >= H["spike_spacing_bu"] for p in picked):
            picked.append(al)
            base = byid[bid]["parts"][bi["base"]]
            base["h"] = max(H["spike_k"] * med - base["z0"], base["h"])  # never lower (B-060): a spike keeps its own top
    if stats is not None:
        stats.update(spikes=len(picked))
    return out


def apply_rules(city: Dict[str, Any], net: Dict[str, Any], rules: Optional[Dict[str, Any]] = None,
                route_tops: Optional[Dict[str, int]] = None, border_mode: str = "state",
                stats: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
    """The whole layout rule pipeline in spec order (3.2): frontage minimum + border width, silhouette, horizon.

    `border_mode` "state" (border links by Grid state) or "all" (every link: the fixed city the game builds).
    """
    st = stats if stats is not None else {}
    c1 = apply_layout_rules(city, net, rules, st, border_mode)
    c2 = frontage_silhouette(c1, net, rules, route_tops, border_mode, st)
    routes = list((route_tops or {}).keys())
    return horizon_break(hq_cap(c2, routes, st), net, routes, border_mode, st)
