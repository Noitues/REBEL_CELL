"""derive.street: the netrun street derived from the city map (spec 3.3, 2.3).

Ports `SB/sb_onecity.py` c83e3b00 (`floors`, `frontage`, `assign`, `choose_street`, `room_boxes`, `link_paths`, `derive`)
to the NA-02 shapes and the derive v2 rulings (DERIVE_V2_REVIEW, AD resolutions): `bid` for `key`; `u` is the signed
distance in BU from `street.a` along `c - a`; both quads are normalised to BL, BR, TR, TL as seen from the street;
`parts` are sorted indices into `buildings[bld].parts`; poses are in the rig yaw convention and carry no `persp`.
Room z values are above the room's `ground_z`. Standard library only.
"""
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .. import layout as LY
from .. import rig as RG
from ..units import FLOOR_BU
from . import VERSION, game_partial

RULES: Dict[str, Any] = dict(
    front_band=LY.FRONT_BAND, floor_bu=FLOOR_BU, base_floor=0, room_inset=0.45, room_depth=2.6, room_px_target=46.0,
    min_width=2.5, max_setback=0.6, extend=LY.EXTEND,
    room_z_inset=0.12,       # room box inset above and below its floors (SB/sb_onecity.py:266-267)
    link_offset=0.5,         # facade link plane in front of the faces
    link_stub=0.3,           # link leaves / enters a room this far along the facade
    span_max=4)              # NA-23b: the street span (floors per room) is searched in 1..span_max
ROOM_KINDS = ("router", "terminal", "mainframe", "server_rack", "rest", "workshop", "cache")
LINK_TYPES = ("facade",)     # "hq" is reserved for HQ landmark links (AD 2026-10-18)
GROUND_Z_DEFAULT = 0.0       # city.json v1 has no terrain; the local ground height under a room


class DeriveError(Exception):
    """The street derivation cannot be done on this city (message says why)."""


def floors(b: Dict[str, Any], rules: Optional[Dict[str, Any]] = None) -> int:
    """Usable floors of a frontage building (real floors; on a tapered one only while the setback stays small)."""
    r = rules or RULES
    n = int(b["h"] / r["floor_bu"])
    if b["ts"] >= 0.99:
        return n
    depth = (b["y1"] - b["y0"]) if b.get("axis", 0) == 0 else (b["x1"] - b["x0"])
    k = 0
    while k < n:
        z = (k + 1) * r["floor_bu"]
        if (1 - b["ts"]) * depth / 2 * z / b["h"] > r["max_setback"]:
            break
        k += 1
    return k


def frontage(B: Sequence[Dict[str, Any]], a: Sequence[float], c: Sequence[float], side: int,
             rules: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Buildings fronting the leg a -> c on `side` (+1 = left of the walking direction), ordered by `(along, bid)`."""
    r = rules or RULES
    ax = LY.leg_axis(a, c)
    d = 1 if c[ax] > a[ax] else -1
    lo, hi = sorted((a[ax], c[ax]))
    nrm = (0.0, float(side * d)) if ax == 0 else (float(-side * d), 0.0)
    out = []
    for b in B:
        if ax == 0:
            a0, a1 = b["x0"], b["x1"]
            near = b["y0"] if nrm[1] > 0 else b["y1"]
            dist = (near - a[1]) * nrm[1]
        else:
            a0, a1 = b["y0"], b["y1"]
            near = b["x0"] if nrm[0] > 0 else b["x1"]
            dist = (near - a[0]) * nrm[0]
        if a1 > lo and a0 < hi and r["front_band"][0] < dist < r["front_band"][1] and a1 - a0 >= r["min_width"]:
            out.append(dict(b, along=((a0 + a1) / 2 - a[ax]) * d, face=near, nrm=nrm, axis=ax, dirn=d))
    out.sort(key=lambda q: (q["along"], q["bid"]))
    return out


def layer_nodes(run_graph: Dict[str, Any]) -> List[Tuple[int, List[Dict[str, Any]]]]:
    """`[(layer, nodes sorted by index)]` in layer order."""
    by: Dict[int, List[Dict[str, Any]]] = {}
    for n in run_graph["nodes"]:
        by.setdefault(n["layer"], []).append(n)
    return [(l, sorted(by[l], key=lambda n: (n["index"], n["id"]))) for l in sorted(by)]


def assign(front: Sequence[Dict[str, Any]], layers: Sequence[Tuple[int, List[Dict[str, Any]]]], span: int = 1,
           rules: Optional[Dict[str, Any]] = None) -> Tuple[List[Tuple[int, Dict[str, Any]]], bool]:
    """Layer -> frontage building in link order, skipping a building without the floors for that layer."""
    r = rules or RULES
    out, k = [], 0
    for l, rooms in layers:
        need = r["base_floor"] + len(rooms) * span
        while k < len(front) and floors(front[k], r) < need:
            k += 1
        if k >= len(front):
            return out, False
        out.append((l, front[k]))
        k += 1
    return out, True


def choose_street(B: Sequence[Dict[str, Any]], legs: Sequence[Sequence[float]],
                  layers: Sequence[Tuple[int, List[Dict[str, Any]]]], rules: Optional[Dict[str, Any]] = None):
    """The leg + side whose frontage fits the run best: max `(layers assigned, total floors, start-left)`.

    Ties go to the lower leg index, then side +1 before -1. A leg extends along its own line by `extend` BU.
    Returns `(score, leg, side, a, c, frontage, assignment, ok, start_left)` or None.
    """
    r = rules or RULES
    best = None
    e = r["extend"]
    for li, (a0, c0) in enumerate(zip(legs, legs[1:])):
        L = math.hypot(c0[0] - a0[0], c0[1] - a0[1])
        if L < 1e-9:
            continue
        ux, uy = (c0[0] - a0[0]) / L, (c0[1] - a0[1]) / L
        a, c = (a0[0] - ux * e[0], a0[1] - uy * e[0]), (c0[0] + ux * e[1], c0[1] + uy * e[1])
        for side in (1, -1):
            fr = frontage(B, a, c, side, r)
            asg, ok = assign(fr, layers, 1, r)
            nfl = sum(floors(b, r) for _, b in asg)
            nrm = fr[0]["nrm"] if fr else (0.0, 1.0)
            right = (nrm[1], -nrm[0])
            start_left = ((c[0] - a[0]) * right[0] + (c[1] - a[1]) * right[1]) > 0
            score = (len(asg), nfl, 1 if start_left else 0)
            if best is None or score > best[0]:
                best = (score, li, side, a, c, fr, asg, ok, start_left)
    return best


def square_legs(legs: Sequence[Sequence[float]]) -> List[List[float]]:
    """`legs` with every slanted leg replaced by an L (dominant axis first); axis-aligned legs are kept as they are.

    A routed link whose end points are off the street tile centres leaves a leg a few BU off the axis; `leg_axis` then
    reads it as a y leg and the frontage is looked up on the wrong axis (NA-23b).
    """
    out = [list(legs[0])]
    for p, q in zip(legs, legs[1:]):
        dx, dy = abs(q[0] - p[0]), abs(q[1] - p[1])
        if dx >= LY.AXIS_TOL and dy >= LY.AXIS_TOL:
            out.append([q[0], p[1]] if dx >= dy else [p[0], q[1]])
        out.append(list(q))
    return out


def choose_street_fitting(B: Sequence[Dict[str, Any]], legs: Sequence[Sequence[float]],
                          layers: Sequence[Tuple[int, List[Dict[str, Any]]]], rules: Optional[Dict[str, Any]] = None):
    """`(best, step)`: `choose_street`, then, only when it does not fit every layer, the same on the squared legs.

    Step 0 is the legs as given; step 1 the legs squared (`square_legs`). A street that fits at step 0 is never changed
    (bids and derive output stay as they were). When neither fits the step 0 result is returned with step 0.
    """
    r = rules or RULES
    first = choose_street(B, legs, layers, r)
    if first is not None and first[5] and first[7]:
        return first, 0
    sq = square_legs(legs)
    if sq != [list(p) for p in legs]:
        best = choose_street(B, sq, layers, r)
        if best is not None and best[5] and best[7]:
            return best, 1
    return first, 0


def select_link(net: Dict[str, Any], site: str) -> Tuple[Dict[str, Any], List[List[float]]]:
    """The selected Site's border link (or, with none, any link at the Site) and its points from the relay end.

    Links at the Site are taken in `(a, b)` order; the first border link wins. Raises `DeriveError` without a link.
    """
    mine = [l for l in sorted(net["links"], key=lambda q: (q["a"], q["b"])) if site in (l["a"], l["b"])]
    if not mine:
        raise DeriveError(f"site {site} has no link")
    border = {(l["a"], l["b"]) for l in LY.border_links(net)}
    link = next((l for l in mine if (l["a"], l["b"]) in border), mine[0])
    pts = [list(p) for p in link["pts"]]
    if link["a"] == site:
        pts.reverse()
    return link, pts


def room_boxes(asg: Sequence[Tuple[int, Dict[str, Any]]], layers: Sequence[Tuple[int, List[Dict[str, Any]]]], span: int,
               rules: Optional[Dict[str, Any]] = None, ground_z: float = GROUND_Z_DEFAULT) -> Dict[str, Dict[str, Any]]:
    """`{node id: room}` in the concept corner order (u0 < u1 on the world axis); heights above `ground_z`."""
    r = rules or RULES
    nodes = dict(layers)
    rooms: Dict[str, Dict[str, Any]] = {}
    for l, b in asg:
        ax, nrm = b["axis"], b["nrm"]
        span_l = span if floors(b, r) >= r["base_floor"] + len(nodes[l]) * span else 1
        lo, hi = (b["x0"], b["x1"]) if ax == 0 else (b["y0"], b["y1"])
        u0, u1 = lo + r["room_inset"], hi - r["room_inset"]
        for k, n in enumerate(nodes[l]):
            f = r["base_floor"] + k * span_l
            z0 = f * r["floor_bu"] + r["room_z_inset"]
            z1 = (f + span_l) * r["floor_bu"] - r["room_z_inset"]
            face = b["face"]
            back = face + r["room_depth"] * (nrm[1] if ax == 0 else nrm[0])
            if ax == 0:
                fr = [[u0, face, z0], [u1, face, z0], [u1, face, z1], [u0, face, z1]]
                bk = [[u0, back, z0], [u1, back, z0], [u1, back, z1], [u0, back, z1]]
            else:
                fr = [[face, u0, z0], [face, u1, z0], [face, u1, z1], [face, u0, z1]]
                bk = [[back, u0, z0], [back, u1, z0], [back, u1, z1], [back, u0, z1]]
            rooms[n["id"]] = dict(front=fr, back=bk, floor=f, span=span_l, ground_z=ground_z, bld=b["bid"],
                                  parts=list(b["parts"]), layer=l, kind=n["type"])
    return rooms


def link_paths(rooms: Dict[str, Dict[str, Any]], edges: Sequence[Dict[str, Any]],
               rules: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Facade links: out of room a 0.3 BU, across at the mid point, into room b; Manhattan on a plane 0.5 BU in front."""
    r = rules or RULES
    out = []
    for e in sorted(edges, key=lambda q: (q["a"], q["b"])):
        ra, rb = rooms[e["a"]], rooms[e["b"]]
        fa, fb = ra["front"], rb["front"]
        ax = 0 if abs(fa[0][1] - fa[1][1]) < 1e-6 else 1
        nrm_s = 1.0 if ra["back"][0][1 - ax] > fa[0][1 - ax] else -1.0
        face = min(fa[0][1 - ax], fb[0][1 - ax]) if nrm_s > 0 else max(fa[0][1 - ax], fb[0][1 - ax])
        face = face - r["link_offset"] * nrm_s
        ua, ub = [p[ax] for p in fa], [p[ax] for p in fb]
        dirn = 1.0 if sum(ub) > sum(ua) else -1.0
        xa = max(ua) if dirn > 0 else min(ua)
        xb = min(ub) if dirn > 0 else max(ub)
        za, zb = (fa[0][2] + fa[2][2]) / 2, (fb[0][2] + fb[2][2]) / 2
        xm = (xa + xb) / 2

        def P(u: float, z: float) -> List[float]:
            return [u, face, z] if ax == 0 else [face, u, z]
        out.append(dict(a=e["a"], b=e["b"], type="facade",
                        path=[P(xa - dirn * r["link_stub"], za), P(xm, za), P(xm, zb), P(xb + dirn * r["link_stub"], zb)]))
    return out


def normalise_quad(q: Sequence[Sequence[float]], nrm: Sequence[float]) -> List[List[float]]:
    """Reorder a quad to BL, BR, TR, TL seen from the street (camera looks along `nrm`; review Q1.1, AD 1)."""
    right = (nrm[1], -nrm[0])
    du = (q[1][0] - q[0][0]) * right[0] + (q[1][1] - q[0][1]) * right[1]
    if du >= 0:
        return [list(p) for p in q]
    return [list(q[1]), list(q[0]), list(q[3]), list(q[2])]


def _span_poses(rooms: Dict[str, Dict[str, Any]], layers, nrm, start_left: bool, rig: Optional[Dict[str, Any]],
                entry: Optional[Sequence[float]] = None):
    ov = RG.street_overview(rooms, nrm, start_left, rig)
    first = [n["id"] for n in layers[0][1]]
    dec = RG.street_decision(rooms, None, first, 0.0, nrm, start_left, rig, entry)
    return ov, dec


def room_px(ov: Any, room: Dict[str, Any]) -> Optional[float]:
    """Projected height in px (1920 x 1080 frame) of a room's front edge in the pose `ov`; None when the edge is not visible."""
    c = RG.room_corners(room)
    p0, p3 = ov.proj(c[0]), ov.proj(c[3])
    if not p0 or not p3:
        return None
    for p in (p0, p3):
        if not (0.0 <= p[0] <= RG.REF_W and 0.0 <= p[1] <= RG.REF_H):
            return None
    return abs(p0[1] - p3[1])


def span_scan(asg: Sequence[Tuple[int, Dict[str, Any]]], layers, nrm, start_left: bool, rules: Dict[str, Any],
              rig: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """One row per candidate span 1..span_max: `{span, min_px, fallback}`.

    `min_px` is the smallest visible route-room height in the OVERVIEW pose over the rooms that hold the span (0.0 with none);
    `fallback` lists the layers whose building cannot fit the span (its rooms keep span 1, `room_boxes` span_l).
    """
    rows = []
    for span in range(1, int(rules["span_max"]) + 1):
        rooms = room_boxes(asg, layers, span, rules)
        ov = RG.street_overview(rooms, nrm, start_left, rig)
        px = [q for rm in rooms.values() if rm["span"] == span for q in [room_px(ov, rm)] if q is not None]
        fb = sorted({rm["layer"] for rm in rooms.values() if rm["span"] != span})
        rows.append(dict(span=span, min_px=min(px) if px else 0.0, fallback=fb))
    return rows


def choose_span(asg, layers, nrm, start_left: bool, rules: Optional[Dict[str, Any]] = None,
                rig: Optional[Dict[str, Any]] = None) -> int:
    """The smallest span whose smallest visible route room in the OVERVIEW pose reaches `room_px_target` (NA-23b, spec 12.6).

    When no span up to `span_max` reaches it, the span with the largest smallest room (the lower span on a tie).
    Buildings that cannot fit the chosen span keep the per-building fallback of `room_boxes`; `span_scan` reports them.
    """
    r = rules or RULES
    rows = span_scan(asg, layers, nrm, start_left, r, rig)
    for row in rows:
        if row["min_px"] >= r["room_px_target"]:
            return row["span"]
    return max(rows, key=lambda q: (q["min_px"], -q["span"]))["span"]


def derive_street(city: Dict[str, Any], net: Dict[str, Any], run_graph: Dict[str, Any], site: str,
                  partial: Optional[Dict[str, Any]] = None, rules: Optional[Dict[str, Any]] = None,
                  rig: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The whole street derivation: a derive v2 dict (`kind: "street"`).

    `partial` is the game's partial file (`game_partial`); without it one is built from the city header. Raises
    `DeriveError` when the frontage runs out. `city` is the city.json after `layout.apply_layout_rules`.
    """
    r = dict(RULES, **(rules or {}))
    layers = layer_nodes(run_graph)
    _, pts = select_link(net, site)
    legs = LY.link_legs(city, pts)
    B = LY.merged_buildings(city)
    best, _ = choose_street_fitting(B, legs, layers, r)
    if best is None or not best[5]:
        raise DeriveError("no frontage along the link of " + site)
    score, li, side, a, c, fr, asg, ok, start_left = best
    if not ok:
        raise DeriveError(f"frontage runs out: {len(asg)} of {len(layers)} layers assigned on leg {li} side {side}")
    nrm = fr[0]["nrm"]
    span = choose_span(asg, layers, nrm, start_left, r, rig)
    rooms = room_boxes(asg, layers, span, r)
    ov, dec = _span_poses(rooms, layers, nrm, start_left, rig, [a[0], a[1], 0.0])
    edges = link_paths(rooms, run_graph["edges"], r)
    ax = LY.leg_axis(a, c)
    sgn = 1.0 if c[ax] > a[ax] else -1.0
    col_info = []
    for l, b in asg:
        lo, hi = (b["x0"], b["x1"]) if b["axis"] == 0 else (b["y0"], b["y1"])
        u0, u1 = sorted(((lo - a[ax]) * sgn, (hi - a[ax]) * sgn))
        col_info.append(dict(layer=l, bid=b["bid"], top=b["h"], u0=u0, u1=u1, face=b["face"]))
    out_rooms = {}
    for rid in sorted(rooms):
        rm = dict(rooms[rid])
        rm["front"] = normalise_quad(rm["front"], nrm)
        rm["back"] = normalise_quad(rm["back"], nrm)
        out_rooms[rid] = rm
    for e in edges:
        e["path"] = [list(p) for p in e["path"]]
    base = dict(partial) if partial else game_partial(city["layout_seed"], run_graph.get("run", "run"), "street")
    base.update(version=VERSION, kind="street")
    base.update(
        street=dict(a=list(a), c=list(c)), nrm=list(nrm), start_left=start_left, span=span,
        columns=[[l, b["bid"]] for l, b in asg], route_keys=[b["bid"] for _, b in asg], col_info=col_info,
        rooms=out_rooms, edges=edges, overview=ov.to_json(), decision=dec.to_json(),
        frontage=[[b["bid"], round(b["h"], 1), floors(b, r), round(b["ts"], 2)] for b in fr])
    return base
