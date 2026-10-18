"""hq.orbit: the HQ orbit camera on generic slots (spec 6.4; ports the rules of `HK/orbit.py` c47c67a9 / `HM/hq_cam.py`).

DECISION azimuth is the mean look vector of the distinct faces holding the current room and the options, pitch rises over
the climb, framing never closer than `dmin`; HOVER pulls 22 % toward the room; OVERVIEW is a high 3/4 view on the corner
whose two faces hold the most live rooms. Kit lengths are converted with `K_UNITS`. Rooms come from `hq.slots`
(`front` outward, `back` inside). Standard library only.
"""
import math
from typing import Any, Dict, List, Optional, Sequence

from ..rig import Pose, clamp01, frame_points, lerp, room_center, room_corners
from ..units import kit
from .slots import FACES

HQ_RIG: Dict[str, Any] = dict(            # ORBIT_DEFAULTS (HK/orbit.py:30); dmin 135 kit units -> BU
    dmin=kit(135.0), look_ahead=0.0, pitch_lo=13.0, pitch_hi=24.0, lens_d=30.0, fill_w=0.66, fill_h=0.70,
    hover_pull=0.22, hover_yaw=3.0, hover_dolly=0.96, pitch_o=26.0, lens_o=40.0, fill_ow=0.95, fill_oh=0.90,
    vis_margin=0.12)


def room_normal(room: Dict[str, Any]) -> List[float]:
    """Outward plan normal of a room (back centre -> front centre, unit)."""
    f = [sum(q[k] for q in room["front"]) / 4 for k in range(2)]
    b = [sum(q[k] for q in room["back"]) / 4 for k in range(2)]
    n = [f[0] - b[0], f[1] - b[1]]
    L = math.hypot(n[0], n[1]) or 1.0
    return [n[0] / L, n[1] / L]


def face_index(room: Dict[str, Any]) -> int:
    """Index into `FACES` of the face a room stands on."""
    n = room_normal(room)
    return max(range(4), key=lambda i: (FACES[i][0] * n[0] + FACES[i][1] * n[1], -i))


def _yaw(v: Sequence[float]) -> float:
    return math.degrees(math.atan2(v[0], v[1]))


def decision_yaw(rooms: Dict[str, Dict[str, Any]], ids: Sequence[str], look_ahead: float = 0.0) -> float:
    """Mean look vector (minus the outward normal) of the distinct faces of `ids`, as a rig yaw."""
    faces = sorted({face_index(rooms[i]) for i in ids})
    v = (sum(-FACES[f][0] for f in faces), sum(-FACES[f][1] for f in faces))
    return _yaw(v) + look_ahead


def hq_decision(rooms: Dict[str, Dict[str, Any]], current: Optional[str], options: Sequence[str], layer_idx: int,
                n_layers: int, rig: Optional[Dict[str, Any]] = None, entry: Optional[Sequence[float]] = None) -> Pose:
    """DECISION pose on `current` (or none) plus `options`; `layer_idx` is the 0-based climb row. With no `current`
    the `entry` anchor (the HQ entrance slot) is the virtual current and is framed with the options; no room is highlighted."""
    g = dict(HQ_RIG, **(rig or {}))
    ids = ([current] if current else []) + [o for o in options if o != current]
    pts = [p for i in ids for p in room_corners(rooms[i])]
    if not current and entry is not None:
        pts.append(list(entry))
    pitch = lerp(g["pitch_lo"], g["pitch_hi"], clamp01(layer_idx / max(1, n_layers - 1)))
    return frame_points(pts, decision_yaw(rooms, ids, g["look_ahead"]), pitch, g["lens_d"], g["fill_w"], g["fill_h"],
                        dmin=g["dmin"])


def hq_hover(decision: Pose, room: Dict[str, Any], k: float = 1.0, rig: Optional[Dict[str, Any]] = None) -> Pose:
    """HOVER pose at ease `k`: pull toward the room, turn toward it (side by camera right), dolly."""
    g = dict(HQ_RIG, **(rig or {}))
    c = room_center(room)
    F = [decision.F[i] + (c[i] - decision.F[i]) * g["hover_pull"] for i in range(3)]
    d = decision.dir()
    right = (d[1], -d[0])
    s = 1.0 if (c[0] - decision.F[0]) * right[0] + (c[1] - decision.F[1]) * right[1] > 0 else -1.0
    h = Pose(F, decision.yaw + g["hover_yaw"] * s, decision.pitch, decision.dist * g["hover_dolly"], decision.lens,
             decision.sx, decision.sy)
    return decision.mix(h, k)


def overview_yaw(rooms: Dict[str, Dict[str, Any]], live: Sequence[str], current: Optional[str]) -> float:
    """Yaw on the corner whose two faces hold the most live rooms; tie to the current face, then the lower face."""
    fc = face_index(rooms[current]) if current else -1
    best = None
    for f in range(4):
        g = (f + 1) % 4
        n = sum(1 for i in live if face_index(rooms[i]) in (f, g))
        key = (n, 1 if f == fc else 0, -f)
        if best is None or key > best[0]:
            best = (key, f, g)
    _, f, g = best
    return _yaw((-FACES[f][0] - FACES[g][0], -FACES[f][1] - FACES[g][1]))


def overview_points(comp: Dict[str, Any]) -> List[List[float]]:
    """Corner points of every tier base, the crown, and the lot rectangle on the ground."""
    cx, cy = comp["centre"]
    pts = []
    for hs, z0 in zip(comp["half"], comp["z0"]):
        for sx in (-1, 1):
            for sy in (-1, 1):
                pts.append([cx + sx * hs, cy + sy * hs, z0])
    top = comp["z0"][-1] + comp["tier_h"]
    pts.append([cx, cy, top])
    r = comp["rect"]
    pts += [[r[0], r[2], 0.0], [r[1], r[2], 0.0], [r[1], r[3], 0.0], [r[0], r[3], 0.0]]
    return pts


def hq_overview(rooms: Dict[str, Dict[str, Any]], comp: Dict[str, Any], live: Sequence[str], current: Optional[str],
                rig: Optional[Dict[str, Any]] = None) -> Pose:
    """OVERVIEW pose framed on the whole landmark, centred on its mid height."""
    g = dict(HQ_RIG, **(rig or {}))
    mid = (comp["z0"][-1] + comp["tier_h"]) / 2.0
    return frame_points(overview_points(comp), overview_yaw(rooms, live, current), g["pitch_o"], g["lens_o"], g["fill_ow"],
                        g["fill_oh"], centre=(comp["centre"][0], comp["centre"][1], mid))


def visible_room(room: Dict[str, Any], pose: Pose, margin: Optional[float] = None) -> bool:
    """A room is drawn when `dot(face normal, direction to the camera) > vis_margin`."""
    m = HQ_RIG["vis_margin"] if margin is None else margin
    loc = pose.loc()
    c = room_center(room)
    dx, dy = loc[0] - c[0], loc[1] - c[1]
    L = math.hypot(dx, dy) or 1.0
    n = room_normal(room)
    return (n[0] * dx + n[1] * dy) / L > m
