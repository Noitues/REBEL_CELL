"""hq.slots: the generic HQ slot generator for any GDD 4.2 run graph (spec 8.4 rule 5; build ruling O-E).

No concept source maps a graph to slots (the `HK/layout.py` `Compound` chains are mock data, spec 8.4). This module is
new: a stepped square landmark inside the HQ lot, one tier per graph layer (bottom = layer 1, narrowing upward); a
layer's nodes (in index order, ties by node id) take the four faces round-robin from a face that turns by one per
tier (a spiral), and share each face evenly. A room is a quad on its tier's face (`front`, BL BR TR TL seen from
outside) with its `back` inside. Placement is deterministic, uses no RNG and reads only the graph and the lot. Art-pass
reviews the look later. Link geometry is the reserved `"hq"` type. Standard library only.
"""
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .. import layout as LY
from ..derive import VERSION, game_partial
from ..derive.street import RULES, layer_nodes
from ..units import FLOOR_BU

# placeholder tuning numbers (art-pass reviews the look)
SLOT_PARAMS: Dict[str, float] = dict(
    lot_margin=0.5,         # BU between the base tier and the lot edge
    top_share=0.45,         # top tier half size / base tier half size
    min_half=3.0,           # smallest tier half size, BU
    corner_pad=1.8,         # BU kept free at each end of a face (more than room_depth, so corner rooms never touch)
    room_w_max=3.2,         # widest room, BU
    room_fill=0.8,          # share of a face segment a room fills
    room_depth=1.6,         # room depth behind the face, BU
    tier_floors=2,          # floors per tier
    link_out=0.5)           # link leaves the face this far
FACES: Tuple[Tuple[int, int], ...] = ((0, 1), (1, 0), (0, -1), (-1, 0))   # outward normals N, E, S, W


class SlotError(Exception):
    """The graph cannot be placed in this lot."""


def hq_lot_rect(city: Dict[str, Any], corp: str) -> Tuple[float, float, float, float]:
    """`(x0, x1, y0, y1)` plan BU of `city.hqs[corp]` (`[i, j, w, h]` in lots)."""
    i, j, w, h = city["hqs"][corp]
    ol, lb = city["origin_lot"], city["lot_bu"]
    return ((i - ol[0]) * lb, (i + w - ol[0]) * lb, -(j + h - ol[1]) * lb, -(j - ol[1]) * lb)


def plan_compound(rect: Sequence[float], n_tiers: int, params: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """The stepped landmark: centre, tier half sizes and base heights. Raises `SlotError` when the lot is too small."""
    p = dict(SLOT_PARAMS, **(params or {}))
    cx, cy = (rect[0] + rect[1]) / 2, (rect[2] + rect[3]) / 2
    base = min(rect[1] - rect[0], rect[3] - rect[2]) / 2 - p["lot_margin"]
    top = max(p["min_half"], base * p["top_share"])
    if base < top:
        raise SlotError("lot too small for the landmark")
    hs = [base - (base - top) * t / max(1, n_tiers - 1) for t in range(n_tiers)]
    tier_h = p["tier_floors"] * FLOOR_BU
    entrance = [cx, cy - hs[0], 0.0]   # ground centre of the base tier's south face (FACES[2]): the HQ entrance slot (AD 2026-10-18 Q2)
    return dict(entrance=entrance, centre=[cx, cy], half=hs, tier_h=tier_h, z0=[t * tier_h for t in range(n_tiers)], rect=list(rect))


def _quad(c: Tuple[float, float], n: Tuple[int, int], s0: float, s1: float, z0: float, z1: float, off: float):
    """Quad on the plane `off` along the outward normal `n` from the compound centre `c`; BL BR TR TL seen from outside."""
    t = (-n[1], n[0])      # screen right when looking along -n
    px, py = c[0] + n[0] * off, c[1] + n[1] * off
    return [[px + t[0] * s0, py + t[1] * s0, z0], [px + t[0] * s1, py + t[1] * s1, z0],
            [px + t[0] * s1, py + t[1] * s1, z1], [px + t[0] * s0, py + t[1] * s0, z1]]


def place_slots(run_graph: Dict[str, Any], rect: Sequence[float], hq_bid: str, n_parts: int = 1,
                params: Optional[Dict[str, float]] = None) -> Dict[str, Dict[str, Any]]:
    """`{node id: room}` for every node of the graph (rooms in the derive v2 shape, `bld` = the HQ bid)."""
    p = dict(SLOT_PARAMS, **(params or {}))
    layers = layer_nodes(run_graph)
    comp = plan_compound(rect, len(layers), p)
    cx, cy = comp["centre"]
    rooms: Dict[str, Dict[str, Any]] = {}
    for t, (layer, nodes) in enumerate(layers):
        hs = comp["half"][t]
        length = 2 * hs - 2 * p["corner_pad"]
        if length <= 0:
            raise SlotError("tier too small")
        face_of = [(t + k) % 4 for k in range(len(nodes))]
        count = {f: face_of.count(f) for f in range(4)}
        seen = {f: 0 for f in range(4)}
        floor = t * int(p["tier_floors"])
        z0 = floor * FLOOR_BU + RULES["room_z_inset"]
        z1 = (floor + 1) * FLOOR_BU - RULES["room_z_inset"]
        for k, nd in enumerate(nodes):
            f = face_of[k]
            c = count[f]
            seg = length / c
            w = min(p["room_w_max"], p["room_fill"] * seg)
            mid = -length / 2 + (seen[f] + 0.5) * seg
            seen[f] += 1
            n = FACES[f]
            rooms[nd["id"]] = dict(
                front=_quad((cx, cy), n, mid - w / 2, mid + w / 2, z0, z1, hs),
                back=_quad((cx, cy), n, mid - w / 2, mid + w / 2, z0, z1, hs - p["room_depth"]),
                floor=floor, span=1, ground_z=0.0, bld=hq_bid, parts=[min(t, max(0, n_parts - 1))], layer=layer,
                kind=nd["type"])
    return rooms


def room_slot_box(room: Dict[str, Any]) -> Tuple[float, float, float, float, float, float]:
    """Axis-aligned box `(x0, x1, y0, y1, z0, z1)` of a room (front and back corners)."""
    pts = list(room["front"]) + list(room["back"])
    return (min(q[0] for q in pts), max(q[0] for q in pts), min(q[1] for q in pts), max(q[1] for q in pts),
            min(q[2] for q in pts), max(q[2] for q in pts))


def overlaps(rooms: Dict[str, Dict[str, Any]]) -> List[Tuple[str, str]]:
    """Pairs of rooms whose boxes intersect (open interiors), sorted by id."""
    ids = sorted(rooms)
    boxes = {i: room_slot_box(rooms[i]) for i in ids}
    bad = []
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            a, b = boxes[ids[x]], boxes[ids[y]]
            if all(a[2 * k] < b[2 * k + 1] - 1e-9 and b[2 * k] < a[2 * k + 1] - 1e-9 for k in range(3)):
                bad.append((ids[x], ids[y]))
    return bad


def inside_rect(room: Dict[str, Any], rect: Sequence[float]) -> bool:
    """True when every room corner lies inside the lot rectangle."""
    return all(rect[0] <= q[0] <= rect[1] and rect[2] <= q[1] <= rect[3] for q in list(room["front"]) + list(room["back"]))


def link_paths(rooms: Dict[str, Dict[str, Any]], edges: Sequence[Dict[str, Any]],
               params: Optional[Dict[str, float]] = None) -> List[Dict[str, Any]]:
    """`"hq"` links: from the front centre of room a out `link_out` along its face normal, across, into room b."""
    p = dict(SLOT_PARAMS, **(params or {}))

    def out(r: Dict[str, Any]) -> Tuple[List[float], List[float], List[float]]:
        f = r["front"]
        c = [sum(q[k] for q in f) / 4 for k in range(3)]
        b = [sum(q[k] for q in r["back"]) / 4 for k in range(3)]
        n = [c[0] - b[0], c[1] - b[1]]
        L = math.hypot(n[0], n[1]) or 1.0
        n = [n[0] / L, n[1] / L]
        return c, [c[0] + n[0] * p["link_out"], c[1] + n[1] * p["link_out"], c[2]], n
    res = []
    for e in sorted(edges, key=lambda q: (q["a"], q["b"])):
        ca, oa, _ = out(rooms[e["a"]])
        cb, ob, _ = out(rooms[e["b"]])
        res.append(dict(a=e["a"], b=e["b"], type="hq", path=[ca, oa, ob, cb]))
    return res


def derive_hq(city: Dict[str, Any], run_graph: Dict[str, Any], corp: str, partial: Optional[Dict[str, Any]] = None,
              params: Optional[Dict[str, float]] = None, rig: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """A derive v2 dict with `kind: "hq"` (no `street`, `nrm`, `start_left`; spec D10) for the corp's HQ lot."""
    from . import orbit
    rect = hq_lot_rect(city, corp)
    bid = "hq:" + corp
    hb = next((b for b in city["buildings"] if b["bid"] == bid), None)
    rooms = place_slots(run_graph, rect, bid, len(hb["parts"]) if hb else 1, params)
    comp = plan_compound(rect, len(layer_nodes(run_graph)), params)
    first = [n["id"] for n in layer_nodes(run_graph)[0][1]]
    ov = orbit.hq_overview(rooms, comp, first, None, rig)
    dec = orbit.hq_decision(rooms, None, first, 0, len(layer_nodes(run_graph)), rig, comp["entrance"])
    base = dict(partial) if partial else game_partial(city["layout_seed"], run_graph.get("run", "run"), "hq", [corp])
    base.update(version=VERSION, kind="hq")
    for k in ("street", "nrm", "start_left"):
        base.pop(k, None)
    base.update(span=1, route_keys=[bid], rooms={i: rooms[i] for i in sorted(rooms)},
                edges=link_paths(rooms, run_graph["edges"], params), overview=ov.to_json(), decision=dec.to_json())
    return base
