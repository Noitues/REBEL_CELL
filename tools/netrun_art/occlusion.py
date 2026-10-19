"""occlusion: the camera-rig occlusion rule, a pure twin of the shader (spec 7.1-7.4).

Ports `HK/downtown.py` 46d161ce lines 319-439. Constants follow spec 7.2 (BU, already one-city): `stub` 3.8, front fade
`kit(6.0)`, `CLUTTER` 5.94 (one constant). The kit `corridor_low` tuple is retired (O-H): the rail comes from the
`zoned.json` `rail` object (`rail_segments`, `rail_cap`). The 28 flat `occ_*` keys are the shader's `KEYS`
(`HK/section.py:31-32`); `occ_on` is a bool in JSON. Heights are above local ground. Standard library only.
"""
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

from .units import kit, smoothstep01

NK = 5                                  # depth knots of the cone
OCC: Dict[str, float] = dict(cone_margin=0.10, stub=3.8, ghost=0.18, edge=0.6, tsoft=0.035, vsoft=0.025)
FRONT_FADE = kit(6.0)                   # 1.425 BU: soft fade past the farthest target
CLUTTER = kit(25.0)                     # 5.9375 BU (spec: 5.94): roof clutter above a building's top
BAND: Dict[str, float] = dict(hq_step_deg=3.0, street_step_bu=1.0)   # face band spacing (spec 7.1 rule 1, AD 2026-10-18)
EASE_S = 0.35                          # per-instance ease, seconds (spec 7.1 rule 6)
MIN_SPAN = 0.02                         # smallest tangent span used for the margin
KEYS: Tuple[str, ...] = ("occ_on", "occ_cx", "occ_cy", "occ_cz", "occ_ux", "occ_uy", "occ_tsoft", "occ_a0", "occ_amax",
                         "occ_vsoft", "occ_stub", "occ_ghost", "occ_edge") + tuple(
    "occ_%s%d" % (c, k) for c in "tTv" for k in range(NK))

Pt3 = Sequence[float]


def rooms_in_frame(rooms: Dict[str, Dict[str, Any]], pose: Any, ref_w: float, ref_h: float,
                   visible: Optional[Any] = None) -> List[str]:
    """Ids (sorted) of the route rooms the DECISION cone must cover: every room whose front quad projects fully in
    front of the camera, with its centre inside the frame, and (when `visible(room, pose)` is given) facing the camera.
    Twin of art-pass `occ_check.in_frame_rooms` (6d214ce9, `hq_aurelian/scripts/occ_check.py`)."""
    out: List[str] = []
    for rid in sorted(rooms):
        r = rooms[rid]
        gz = r.get("ground_z", 0.0)
        q = [pose.proj([c[0], c[1], c[2] + gz]) for c in r["front"]]
        if any(v is None for v in q):
            continue
        cx = sum(v[0] for v in q) / len(q)
        cy = sum(v[1] for v in q) / len(q)
        if not (0.0 <= cx <= ref_w and 0.0 <= cy <= ref_h):
            continue
        if visible is not None and not visible(r, pose):
            continue
        out.append(rid)
    return out


def room_normal_xy(room: Dict[str, Any]) -> List[float]:
    """Outward plan normal of a room (back centre -> front centre, unit)."""
    f = room["front"]
    b = room["back"]
    nx = sum(q[0] for q in f) / len(f) - sum(q[0] for q in b) / len(b)
    ny = sum(q[1] for q in f) / len(f) - sum(q[1] for q in b) / len(b)
    ln = math.hypot(nx, ny) or 1.0
    return [nx / ln, ny / ln]


def room_faces_camera(room: Dict[str, Any], pose: Any) -> bool:
    """True when the room's outward normal points toward the camera (street netruns; an HQ uses `visible_room`)."""
    loc = pose.loc()
    n = room_normal_xy(room)
    f = room["front"]
    cx = sum(q[0] for q in f) / len(f)
    cy = sum(q[1] for q in f) / len(f)
    return n[0] * (loc[0] - cx) + n[1] * (loc[1] - cy) > 0.0


def _band_point_ok(p: Sequence[float], nrm: Sequence[float], pose: Any, ref_w: float, ref_h: float) -> bool:
    loc = pose.loc()
    if nrm[0] * (loc[0] - p[0]) + nrm[1] * (loc[1] - p[1]) <= 0.0:
        return False
    q = pose.proj(list(p))
    return q is not None and 0.0 <= q[0] <= ref_w and 0.0 <= q[1] <= ref_h


def _band_levels(rooms: Dict[str, Dict[str, Any]], ids: Sequence[str], key: Any) -> List[Dict[str, Any]]:
    """One representative room (lowest id) per distinct `key(room)`, sorted by key."""
    seen: Dict[Any, str] = {}
    for i in sorted(ids):
        seen.setdefault(key(rooms[i]), i)
    return [rooms[seen[k]] for k in sorted(seen)]


def hq_band_points(rooms: Dict[str, Dict[str, Any]], ids: Sequence[str], centre: Sequence[float], pose: Any,
                   ref_w: float, ref_h: float, step_deg: Optional[float] = None) -> List[List[float]]:
    """Face band of the HQ's current level (spec 7.1 rule 1): for each tier (layer) of the rooms `ids`, points on the
    tier's square face every `step_deg` (default `BAND["hq_step_deg"]`) around the compound centre, at floor and room-top
    height, that face the camera and project inside the frame."""
    st = BAND["hq_step_deg"] if step_deg is None else step_deg
    out: List[List[float]] = []
    for r in _band_levels(rooms, ids, lambda q: q["layer"]):
        n = room_normal_xy(r)
        f = r["front"]
        hs = (sum(q[0] for q in f) / len(f) - centre[0]) * n[0] + (sum(q[1] for q in f) / len(f) - centre[1]) * n[1]
        gz = r.get("ground_z", 0.0)
        z0 = min(q[2] for q in f) + gz
        z1 = max(q[2] for q in f) + gz
        for k in range(int(360.0 / st)):
            a = math.radians(k * st)
            ca, sa = math.cos(a), math.sin(a)
            s = hs / max(abs(ca), abs(sa))
            if abs(ca) >= abs(sa):
                nrm = [1.0 if ca > 0 else -1.0, 0.0]
            else:
                nrm = [0.0, 1.0 if sa > 0 else -1.0]
            for z in (z0, z1):
                p = [centre[0] + s * ca, centre[1] + s * sa, z]
                if _band_point_ok(p, nrm, pose, ref_w, ref_h):
                    out.append(p)
    return out


def street_band_points(rooms: Dict[str, Dict[str, Any]], ids: Sequence[str], extents: Dict[str, Sequence[float]],
                       pose: Any, ref_w: float, ref_h: float, step_bu: Optional[float] = None) -> List[List[float]]:
    """Face band of the route building(s) holding the rooms `ids` (spec 7.1 rule 1): points along the building's face
    every `step_bu` (default `BAND["street_step_bu"]`), at the floor and room-top height of each distinct (building,
    floor, span) level, that face the camera and project inside the frame. `extents[bid] = (x0, x1, y0, y1)`."""
    st = BAND["street_step_bu"] if step_bu is None else step_bu
    out: List[List[float]] = []
    for r in _band_levels(rooms, ids, lambda q: (q["bld"], q["floor"], q["span"])):
        n = room_normal_xy(r)
        f = r["front"]
        gz = r.get("ground_z", 0.0)
        z0 = min(q[2] for q in f) + gz
        z1 = max(q[2] for q in f) + gz
        x0, x1, y0, y1 = extents[r["bld"]]
        along_x = abs(f[0][1] - f[1][1]) < 1e-9          # the face runs along x (constant y)
        lo, hi = (x0, x1) if along_x else (y0, y1)
        for k in range(int((hi - lo) / st) + 1):
            u = lo + k * st
            for z in (z0, z1):
                p = [u, f[0][1], z] if along_x else [f[0][0], u, z]
                if _band_point_ok(p, n, pose, ref_w, ref_h):
                    out.append(p)
    return out


def building_extent(city: Dict[str, Any], bid: str) -> List[float]:
    """`[x0, x1, y0, y1]` bounding box over all parts of the city building `bid`."""
    b = next(q for q in city["buildings"] if q["bid"] == bid)
    xs = [p[0] for pt in b["parts"] for p in pt["poly"]]
    ys = [p[1] for pt in b["parts"] for p in pt["poly"]]
    return [min(xs), max(xs), min(ys), max(ys)]


def occlusion_params(cam: Pt3, pts: Sequence[Pt3], cfg: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """The per-frame cone of the target volume as the 28 flat `occ_*` keys (spec 7.3).

    `cam` camera position, `pts` the front points of the active room plus the visible route nodes. `cfg["occ"]` may
    override the `OCC` numbers.
    """
    o = dict(OCC, **((cfg or {}).get("occ") or {}))
    cx, cy, cz = cam
    ox = sum(p[0] for p in pts) / len(pts)
    oy = sum(p[1] for p in pts) / len(pts)
    L = math.hypot(ox - cx, oy - cy) or 1.0
    ux, uy = (ox - cx) / L, (oy - cy) / L
    T, V, AL = [], [], []
    for p in pts:
        al = max((p[0] - cx) * ux + (p[1] - cy) * uy, 1.0)
        la = (p[1] - cy) * ux - (p[0] - cx) * uy
        T.append(la / al)
        V.append((p[2] - cz) / al)
        AL.append(al)
    msp_t = o["cone_margin"] * max(max(T) - min(T), MIN_SPAN)
    msp_v = o["cone_margin"] * max(max(V) - min(V), MIN_SPAN)
    a0, a1 = min(AL), max(AL)
    out: Dict[str, Any] = dict(occ_on=True, occ_cx=cx, occ_cy=cy, occ_cz=cz, occ_ux=ux, occ_uy=uy, occ_tsoft=o["tsoft"],
                               occ_a0=a0, occ_amax=a1, occ_vsoft=o["vsoft"], occ_stub=o["stub"], occ_ghost=o["ghost"],
                               occ_edge=o["edge"])
    for k in range(NK):
        ak = a0 + (a1 - a0) * k / (NK - 1)
        sub = [j for j in range(len(AL)) if AL[j] >= ak - 1e-6] or [AL.index(a1)]
        out["occ_t%d" % k] = min(T[j] for j in sub) - msp_t
        out["occ_T%d" % k] = max(T[j] for j in sub) + msp_t
        out["occ_v%d" % k] = min(V[j] for j in sub) - msp_v
    return out


def _knot(p: Dict[str, Any], key: str, a: float) -> float:
    f = (a - p["occ_a0"]) / max(p["occ_amax"] - p["occ_a0"], 1.0) * (NK - 1)
    f = max(0.0, min(NK - 1.0, f))
    v = p["occ_%s0" % key]
    for k in range(1, NK):
        v += max(0.0, min(1.0, f - (k - 1))) * (p["occ_%s%d" % (key, k)] - p["occ_%s%d" % (key, k - 1)])
    return v


def _sstep(x: float, w: float) -> float:
    return smoothstep01(x / max(w, 1e-4))


def occlusion_state(p: Dict[str, Any], b: Pt3) -> Tuple[float, float]:
    """`(cut_height, opacity)` of one building `b = (x, y, top, hx, hy)` under the frame params `p` (spec 7.3)."""
    x, y, top, hx, hy = b
    r = max(math.hypot(hx, hy), 0.5)
    dx, dy = x - p["occ_cx"], y - p["occ_cy"]
    al = dx * p["occ_ux"] + dy * p["occ_uy"]
    la = dy * p["occ_ux"] - dx * p["occ_uy"]
    alc = max(al, 1.0)
    tmin, tmax, vmin = _knot(p, "t", al - r), _knot(p, "T", al - r), _knot(p, "v", al - r)
    lat = _sstep((la + r) / alc - tmin, p["occ_tsoft"]) * _sstep(tmax - (la - r) / alc, p["occ_tsoft"])
    front = (1.0 if al > 0 else 0.0) * _sstep(p["occ_amax"] - (al - r), FRONT_FADE)

    def blocks(z: float) -> float:
        return _sstep((z - p["occ_cz"]) / max(al + r, 1.0) - vmin, p["occ_vsoft"])
    fc = (1.0 if p["occ_on"] else 0.0) * lat * front * blocks(top)
    stub = min(p["occ_stub"], top)
    zc = stub + (1.0 - fc) * (top + CLUTTER - stub)
    g = fc * blocks(stub)
    return min(zc, top), 1.0 - g * (1.0 - p["occ_ghost"])


def building_boxes(city: Dict[str, Any], skip: Optional[set] = None) -> List[Dict[str, Any]]:
    """`[{bid, box: (x, y, top, hx, hy)}]` of the city buildings (whole-building box over all parts), sorted by bid."""
    out = []
    for b in sorted(city["buildings"], key=lambda q: q["bid"]):
        if skip and b["bid"] in skip:
            continue
        xs = [p[0] for pt in b["parts"] for p in pt["poly"]]
        ys = [p[1] for pt in b["parts"] for p in pt["poly"]]
        top = max(pt["z0"] + pt["h"] for pt in b["parts"])
        out.append(dict(bid=b["bid"], box=((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, top,
                                           (max(xs) - min(xs)) / 2, (max(ys) - min(ys)) / 2)))
    return out


def occlusion_block(params: Dict[str, Any], boxes: Sequence[Dict[str, Any]], eps: float = 1e-4) -> Dict[str, Any]:
    """`{params, buildings[], unaffected}` for the parity files: only buildings with a cut or a ghost are listed."""
    rows = []
    for bx in boxes:
        cut, op = occlusion_state(params, bx["box"])
        if cut < bx["box"][2] - eps or op < 1.0 - eps:
            rows.append(dict(bid=bx["bid"], cut_height=cut, opacity=op))
    return dict(params=params, buildings=rows, unaffected=len(boxes) - len(rows))


# ---------------------------------------------------------------- rail corridor (zoned.json `rail`, O-C / O-H)
def rail_segments(rail: Dict[str, Any]) -> List[Tuple[float, float, float, float, float]]:
    """Corridor segments `(ax, ay, bx, by, half)` from consecutive `rail.pts` with `half = rail.half_clear`."""
    pts = rail["pts"]
    return [(a[0], a[1], b[0], b[1], rail["half_clear"]) for a, b in zip(pts, pts[1:])]


def _seg_point_dist(ax: float, ay: float, bx: float, by: float, x: float, y: float) -> float:
    vx, vy = bx - ax, by - ay
    L2 = vx * vx + vy * vy or 1.0
    t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / L2))
    return math.hypot(x - ax - vx * t, y - ay - vy * t)


def corridor_dist(segs: Sequence[Sequence[float]], x: float, y: float) -> float:
    """Distance from `(x, y)` to the nearest corridor axis (inf without corridors)."""
    return min((_seg_point_dist(s[0], s[1], s[2], s[3], x, y) for s in segs), default=math.inf)


def in_corridor(segs: Sequence[Sequence[float]], x0: float, y0: float, x1: float, y1: float) -> bool:
    """True when the box meets a corridor segment (exact distance from the segment to the box, not sampled)."""
    for ax, ay, bx, by, hw in segs:
        n = max(1, int(math.hypot(bx - ax, by - ay) / 0.5) + 1)   # 0.5 BU samples, finer than the 3 BU polyline step
        for k in range(n + 1):
            px, py = ax + (bx - ax) * k / n, ay + (by - ay) * k / n
            dx = max(x0 - px, 0.0, px - x1)
            dy = max(y0 - py, 0.0, py - y1)
            if math.hypot(dx, dy) < hw:
                return True
    return False


def rail_cap(rail: Dict[str, Any], x: float, y: float, h: float) -> Tuple[float, bool]:
    """Height cap beside the rail: within `side_d` of the polyline a top is limited to `side_cap` -> `(h, capped)`."""
    if corridor_dist(rail_segments(rail), x, y) > rail["side_d"] or h <= rail["side_cap"]:
        return h, False
    return rail["side_cap"], True
