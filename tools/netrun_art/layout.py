"""layout: city.json / net.json helpers and the mainline layout rules (spec 3.1, 3.2; 2.2 `layout.*`).

Ports `SB/sb_onecity.py` c83e3b00 (`apply_layout_rules`, `merged_buildings`, `bld_info`) and `M44/layout36.py` 96c1af6f
(`W`, `lots`, the street BFS) to the NA-02 shapes. Everything is BU plan coordinates; `bid` replaces the legacy `key`
(the legacy `key` only feeds the `abs(key) % 3` height jitter). A border link is defined by O-D (NA03_NA04_ANSWERS).
Standard library only.
"""
import copy
import math
from collections import deque
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .units import FLOOR_BU

Pt = Sequence[float]

LAYOUT_RULES: Dict[str, Any] = dict(
    frontage_min_floors=6, border_street_width=8.0, base_street_width=6.0,
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


def street_cells(city: Dict[str, Any]) -> set:
    """Set of `(i, j)` street lot cells."""
    return {(int(s["lot"][0]), int(s["lot"][1])) for s in city["streets"]}


def _bfs(a: Tuple[int, int], b: Tuple[int, int], cells: set) -> Optional[List[Tuple[int, int]]]:
    prev = {a: None}
    q = deque([a])
    while q:
        c = q.popleft()
        if c == b:
            break
        for di, dj in BFS_STEPS:
            n = (c[0] + di, c[1] + dj)
            if n in cells and n not in prev:
                prev[n] = c
                q.append(n)
    if b not in prev:
        return None
    out = []
    c = b
    while c is not None:
        out.append(c)
        c = prev[c]
    return out[::-1]


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
                       stats: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
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
    for link in border_links(net):
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
                    if abs(p[k] - ref) < FACE_TOL:
                        p[k] += sgn * step
                        moved += 1
                want = (r["frontage_min_floors"] + abs(bi["key"]) % 3) * FLOOR_BU + 0.1
                if bi["h"] < want:
                    base["h"] = want - base["z0"]
                    raised += 1
    if stats is not None:
        stats.update(frontage=len(done), raised=raised, moved=moved)
    return out
