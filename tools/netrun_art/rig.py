"""rig: the camera pose model, the framing solver, the street rig and the dive path (spec 6.1-6.3, 5.1).

Ports `V3D/cam_rig.py` 47850a23 (`Pose`, `frame_points`), `SB/sb_onecity.py` c83e3b00 (`cam`, `frame`, the OVERVIEW /
DECISION poses of `derive`) and `SB/sb_ocjobs.py` c83e3b00 (`pose_at`, `zoom_of`, `hover_pose`, `smoother`) to the rig
yaw convention (DERIVE_V2_REVIEW Q1.7, AD resolution 4): `yaw` 0 looks along +y (north), positive turns clockwise seen from
above (toward +x); `dir = (sin yaw cos pitch, cos yaw cos pitch, -sin pitch)`; the camera is at `tgt - dist * dir`;
pitch is positive looking down. The layout36 concept yaw is `90 - yaw_rig`. `shift_x` / `shift_y` are fractions of the
frame width (36 mm sensor, 1920 x 1080 reference). Standard library only.
"""
import math
from typing import Any, Dict, List, Optional, Sequence, Tuple

Pt3 = Sequence[float]

SENSOR = 36.0                       # mm, horizontal fit
REF_W, REF_H = 1920.0, 1080.0       # reference frame, px
USE = (300.0, 138.0, 1900.0, 1012.0)      # usable street area, px at 1080p
UCX, UCY = (USE[0] + USE[2]) / 2, (USE[1] + USE[3]) / 2
UW, UH = USE[2] - USE[0], USE[3] - USE[1]
SOLVER_ITERS = 60                   # bisection iterations on dist
SOLVER_BRACKET = (5.0, 3000.0)      # dist bracket, BU
NEAR_Z = 0.1                        # points nearer than this along the view axis are not projected

# Street rig constants (DERIVE_V2_REVIEW Q2.3; stored in poses_<run>.json `rig` so every consumer reads one source)
RIG: Dict[str, Any] = dict(
    yaw_max=24.0, pitch_d=9.0, lens_d=30.0, fill_w=0.66, fill_h=0.70, look_bias=0.10,
    hover_pull=0.22, hover_yaw=3.0, hover_dolly=0.96,
    ov_yaw_k=0.3, pitch_o=2.0, lens_o=40.0, fill_ow=0.95, fill_oh=0.90, ov_base_frac=0.815,
    t_step=0.9, t_hover_in=0.30, t_hover_out=0.35, t_zoom=1.0,
    sensor_mm=SENSOR, ref_w=REF_W, ref_h=REF_H, use=list(USE),
    solver_iters=SOLVER_ITERS, solver_bracket=list(SOLVER_BRACKET))
# The DECISION look-bias sign: +1 moves the framed set toward the look direction (the one-city derive), confirmed by
# art-pass 2026-10-18 (golden_plates/look_bias_check.jpg: 173 px from the usable-area center vs 493 px with -1; spec 6.2).
LOOK_BIAS_SIGN = 1.0

# Dive path (spec 6.3; SB/sb_ocjobs.py:70-91)
DIVE: Dict[str, Any] = dict(duration_s=3.0, hq_lens=300.0, hq_yaw_l36=135.0, hq_pitch=40.0, lag_k=1.08, lag_pow=1.6)
# Mainline HQ page camera fit (SB/sb_mainline.py hq_cam; main scripts/city3d): box + margin fitted into the free rect
HQ_PAGE: Dict[str, Any] = dict(fit_margin=40.0, fit_share=0.65, anchor=[0.45, 0.42], ortho_clamp=[220.0, 640.0],
                               grid_ortho=460.0, free=[230.0, 90.0, 1460.0, 800.0])


def clamp01(x: float) -> float:
    """Clamp to 0..1."""
    return max(0.0, min(1.0, x))


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def ease(t: float) -> float:
    """Smoothstep easing."""
    t = clamp01(t)
    return t * t * (3.0 - 2.0 * t)


def ease_out(t: float) -> float:
    """Cubic ease-out."""
    t = clamp01(t)
    return 1.0 - (1.0 - t) ** 3


def smootherstep(t: float) -> float:
    """`SB/sb_ocjobs.py` smoother."""
    t = clamp01(t)
    return t * t * t * (t * (6.0 * t - 15.0) + 10.0)


def _cross(a: Pt3, b: Pt3) -> List[float]:
    return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]


def _dot(a: Pt3, b: Pt3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(a: Pt3) -> List[float]:
    n = math.sqrt(_dot(a, a))
    return [a[0] / n, a[1] / n, a[2] / n]


def yaw_to_rig(yaw_l36: float) -> float:
    """layout36 concept yaw (0 = +x, counter-clockwise) -> rig yaw (0 = +y, clockwise)."""
    return 90.0 - yaw_l36


def yaw_of_nrm(nrm: Sequence[float]) -> float:
    """Rig yaw looking along a plan vector: `atan2(x, y)` in degrees (review Q1.7)."""
    return math.degrees(math.atan2(nrm[0], nrm[1]))


def unwrap_yaw(y: float, ref: float) -> float:
    """`y` shifted by multiples of 360 to lie within 180 of `ref` (the dive takes the shortest arc)."""
    while y - ref > 180.0:
        y -= 360.0
    while y - ref < -180.0:
        y += 360.0
    return y


class Pose:
    """A camera pose `(F, yaw, pitch, dist, lens, sx, sy)` in the rig convention (see the module docstring)."""

    def __init__(self, F: Pt3, yaw: float, pitch: float, dist: float, lens: float, sx: float = 0.0, sy: float = 0.0):
        self.F = tuple(F)
        self.yaw, self.pitch, self.dist, self.lens, self.sx, self.sy = yaw, pitch, dist, lens, sx, sy

    def dir(self) -> List[float]:
        """Unit view direction."""
        y, p = math.radians(self.yaw), math.radians(self.pitch)
        return [math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p)]

    def loc(self) -> List[float]:
        """Camera position."""
        d = self.dir()
        return [self.F[i] - d[i] * self.dist for i in range(3)]

    def proj(self, P: Pt3, shift: bool = True) -> Optional[Tuple[float, float]]:
        """Pixel of world point `P` in the 1920 x 1080 reference frame, or None behind the camera."""
        f = self.dir()
        r = _norm(_cross(f, (0.0, 0.0, 1.0)))
        u = _cross(r, f)
        loc = self.loc()
        d = [P[i] - loc[i] for i in range(3)]
        z = _dot(d, f)
        if z <= NEAR_Z:
            return None
        k = self.lens / SENSOR
        nx, ny = k * _dot(d, r) / z, k * _dot(d, u) / z
        sx, sy = (self.sx, self.sy) if shift else (0.0, 0.0)
        return (REF_W / 2 + (nx - sx) * REF_W, REF_H / 2 - (ny - sy) * REF_W)

    def to_json(self) -> Dict[str, Any]:
        """`{loc, tgt, lens, shift_x, shift_y, yaw, pitch, dist}` (the v2 pose shape; no `persp`)."""
        return dict(loc=self.loc(), tgt=list(self.F), lens=self.lens, shift_x=self.sx, shift_y=self.sy, yaw=self.yaw,
                    pitch=self.pitch, dist=self.dist)

    @staticmethod
    def from_json(js: Dict[str, Any]) -> "Pose":
        """Pose from the v2 shape."""
        return Pose(js["tgt"], js["yaw"], js["pitch"], js["dist"], js["lens"], js["shift_x"], js["shift_y"])

    def mix(self, o: "Pose", t: float) -> "Pose":
        """Interpolate: F, yaw, pitch, lens, shift linear, dist in log space."""
        return Pose([lerp(a, b, t) for a, b in zip(self.F, o.F)], lerp(self.yaw, o.yaw, t), lerp(self.pitch, o.pitch, t),
                    math.exp(lerp(math.log(self.dist), math.log(o.dist), t)), lerp(self.lens, o.lens, t),
                    lerp(self.sx, o.sx, t), lerp(self.sy, o.sy, t))


def bbox_px(pose: Pose, pts: Sequence[Pt3]) -> Tuple[float, float, float, float]:
    """Pixel box of the unshifted projections; raises ValueError when no point is in front of the camera."""
    q = [pose.proj(p, shift=False) for p in pts]
    q = [p for p in q if p]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return min(xs), min(ys), max(xs), max(ys)


def frame_points(pts: Sequence[Pt3], yaw: float, pitch: float, lens: float, fw: float, fh: float, bias: float = 0.0,
                 centre: Optional[Pt3] = None, dmin: float = 0.0) -> Pose:
    """Solve `dist` and the lens shift so `pts` fill `fw` of the usable width or `fh` of its height, centred in it.

    Bisection on dist (geometric mean, 60 iterations, bracket 5..3000 BU). `bias` offsets the centre by that share of the
    usable width. `centre` fixes the focus; `dmin` is a lower bound for dist.
    """
    xs, ys, zs = zip(*pts)
    F = centre or ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
    lo, hi = SOLVER_BRACKET
    for _ in range(SOLVER_ITERS):
        d = math.sqrt(lo * hi)
        try:
            x0, y0, x1, y1 = bbox_px(Pose(F, yaw, pitch, d, lens), pts)
            k = max((x1 - x0) / (fw * UW), (y1 - y0) / (fh * UH))
        except ValueError:
            k = 9.0
        if k > 1.0:
            lo = d
        else:
            hi = d
    p = Pose(F, yaw, pitch, max(hi, dmin), lens)
    x0, y0, x1, y1 = bbox_px(p, pts)
    p.sx = ((x0 + x1) / 2 - (UCX + bias * UW)) / REF_W
    p.sy = (UCY - (y0 + y1) / 2) / REF_W
    return p


def room_corners(room: Dict[str, Any]) -> List[List[float]]:
    """The 8 world corners of a derive room (front then back quad). Room z values are above `ground_z` (spec 2.3)."""
    gz = room.get("ground_z", 0.0)
    return [[p[0], p[1], p[2] + gz] for p in list(room["front"]) + list(room["back"])]


def room_center(room: Dict[str, Any]) -> List[float]:
    """Centroid of the 8 corners."""
    c = room_corners(room)
    return [sum(p[k] for p in c) / len(c) for k in range(3)]


def street_yaw0(nrm: Sequence[float]) -> float:
    """`yaw0` of the street rig: the camera looks along the street face normal."""
    return yaw_of_nrm(nrm)


def street_overview(rooms: Dict[str, Dict[str, Any]], nrm: Sequence[float], start_left: bool,
                    rig: Optional[Dict[str, Any]] = None) -> Pose:
    """The street OVERVIEW pose (spec 6.2 one-city overrides, rig convention).

    Yaw `yaw0 + sgn * ov_yaw_k * yaw_max`, framed on every room corner, then shifted so the lowest room fronts sit at
    `ov_base_frac` of the frame height. `sgn` is +1 when the start is on the screen's left.
    """
    g = dict(RIG, **(rig or {}))
    sgn = 1.0 if start_left else -1.0
    pts = [p for r in rooms.values() for p in room_corners(r)]
    ov = frame_points(pts, street_yaw0(nrm) + sgn * g["ov_yaw_k"] * g["yaw_max"], g["pitch_o"], g["lens_o"], g["fill_ow"],
                      g["fill_oh"])
    low = [ov.proj([p[0], p[1], p[2] + r.get("ground_z", 0.0)]) for r in rooms.values() for p in r["front"] if p[2] < 0.5]
    low = [q[1] for q in low if q]
    if low:
        ov.sy += (g["ov_base_frac"] * REF_H - max(low)) / REF_W
    return ov


def street_u(layers: int, current_layer: int) -> float:
    """`u = layer / (layers - 1)` clamped 0..1; layer 0 is 'no current' (before the first layer)."""
    return clamp01(current_layer / max(1, layers - 1))


def street_decision(rooms: Dict[str, Dict[str, Any]], current: Optional[str], options: Sequence[str], u: float,
                    nrm: Sequence[float], start_left: bool, rig: Optional[Dict[str, Any]] = None,
                    entry: Optional[Pt3] = None) -> Pose:
    """The street DECISION pose on `current` (or none) plus `options`.

    With no `current` the first decision has no highlighted room (AD 2026-10-18 Q2): the `entry` anchor (the street leg's
    start end, or the HQ entrance slot) is the virtual current and is framed with the options.

    Yaw `yaw0 + sgn * yaw_max * (1 - 2u)`, framed on the 8 corners of each room, bias
    `LOOK_BIAS_SIGN * look_bias * (yaw offset / yaw_max)` (+sgn * 0.10 at u = 0, as the one-city derive).
    """
    g = dict(RIG, **(rig or {}))
    sgn = 1.0 if start_left else -1.0
    ids = ([current] if current else []) + [o for o in options if o != current]
    pts = [p for i in ids for p in room_corners(rooms[i])]
    if not current and entry is not None:
        pts.append(list(entry))
    off = sgn * g["yaw_max"] * (1.0 - 2.0 * clamp01(u))
    return frame_points(pts, street_yaw0(nrm) + off, g["pitch_d"], g["lens_d"], g["fill_w"], g["fill_h"],
                        bias=LOOK_BIAS_SIGN * g["look_bias"] * off / g["yaw_max"])


def street_hover(decision: Pose, target_room: Dict[str, Any], nrm: Sequence[float], k: float = 1.0,
                 rig: Optional[Dict[str, Any]] = None) -> Pose:
    """The street HOVER pose at ease `k` (1 = fully hovered): F pulls `hover_pull` toward the room, yaw turns
    `hover_yaw` toward it (screen-right test, review Q2.1.3), dist x `hover_dolly`."""
    g = dict(RIG, **(rig or {}))
    c = room_center(target_room)
    p = decision
    F = [p.F[i] + (c[i] - p.F[i]) * g["hover_pull"] for i in range(3)]
    right = (nrm[1], -nrm[0])
    s = 1.0 if (c[0] - p.F[0]) * right[0] + (c[1] - p.F[1]) * right[1] > 0 else -1.0
    h = Pose(F, p.yaw + g["hover_yaw"] * s, p.pitch, p.dist * g["hover_dolly"], p.lens, p.sx, p.sy)
    return p.mix(h, k)


# ---------------------------------------------------------------- the dive path (6.3)
def hq_page_camera(net: Dict[str, Any]) -> Tuple[List[float], float]:
    """The mainline HQ page camera `(target xyz, frame width BU)` fitted to the claimed and launchable Sites.

    Node plan points (net.json `lot`, BU plan per NA02 O3) of states core / owned / corporate (the launchable Sites) fitted in the layout36 iso frame
    (yaw 135, pitch 40). Port of `SB/sb_mainline.py` hq_cam.
    """
    c = HQ_PAGE
    yw, pt = math.radians(DIVE["hq_yaw_l36"]), math.radians(DIVE["hq_pitch"])
    fwd = (math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt))
    right = (math.sin(yw), -math.cos(yw), 0.0)
    up = (right[1] * fwd[2] - right[2] * fwd[1], right[2] * fwd[0] - right[0] * fwd[2], right[0] * fwd[1] - right[1] * fwd[0])
    pts = [n["lot"] for n in net["nodes"] if n["state"] in ("core", "owned", "corporate")] or [n["lot"] for n in net["nodes"]]
    xs = [p[0] * right[0] + p[1] * right[1] for p in pts]
    ys = [p[0] * up[0] + p[1] * up[1] for p in pts]
    bw = max(xs) - min(xs) + 2 * c["fit_margin"]
    bh = max(ys) - min(ys) + 2 * c["fit_margin"]
    fr = c["free"]
    fw, fh = (fr[2] - fr[0]) / REF_W, (fr[3] - fr[1]) / REF_H
    ortho = max(bw / (c["fit_share"] * fw), (bh * REF_W / REF_H) / (c["fit_share"] * fh))
    ortho = min(c["ortho_clamp"][1], max(c["ortho_clamp"][0], ortho))
    ortho = min(ortho, c["grid_ortho"])
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    vw, vh = ortho, ortho * REF_H / REF_W
    tx = cx + (0.5 - c["anchor"][0]) * vw
    ty = cy - (0.5 - c["anchor"][1]) * vh
    a11, a12, a21, a22 = right[0], right[1], up[0], up[1]
    det = a11 * a22 - a12 * a21
    return [(tx * a22 - a12 * ty) / det, (a11 * ty - tx * a21) / det, 0.0], ortho


def hq_page_pose(target: Pt3, width: float) -> Pose:
    """The HQ page camera as a perspective pose: orthographic emulated by a 300 mm lens (`dist = width * lens / 36`)."""
    return Pose(target, yaw_to_rig(DIVE["hq_yaw_l36"]), DIVE["hq_pitch"], width * DIVE["hq_lens"] / SENSOR,
                DIVE["hq_lens"])


def dive_pose(u: float, hq: Pose, ov: Pose) -> Pose:
    """The dive camera at `u` (0 = HQ page, 1 = street OVERVIEW; `SB/sb_ocjobs.py` pose_at).

    Target, yaw (shortest arc) and shift on smootherstep, frame width and lens in log space, pitch lagging
    (`min(1, lag_k * u) ** lag_pow`).
    """
    s = smootherstep(u)
    sp = smootherstep(min(1.0, u * DIVE["lag_k"]) ** DIVE["lag_pow"])
    w0 = hq.dist * SENSOR / hq.lens
    w1 = ov.dist * SENSOR / ov.lens
    tg = [lerp(a, b, s) for a, b in zip(hq.F, ov.F)]
    yaw = lerp(hq.yaw, unwrap_yaw(ov.yaw, hq.yaw), s)
    pit = lerp(hq.pitch, ov.pitch, sp)
    w = math.exp(lerp(math.log(w0), math.log(w1), s))
    lens = math.exp(lerp(math.log(hq.lens), math.log(ov.lens), s))
    return Pose(tg, yaw, pit, w * lens / SENSOR, lens, lerp(0.0, ov.sx, s), lerp(0.0, ov.sy, s))


def dive_distance(p: Pose, ov: Pose) -> float:
    """Distance from the camera to the OVERVIEW target (the `zoom_dive` distance, review Q2.4)."""
    loc = p.loc()
    return math.sqrt(sum((loc[i] - ov.F[i]) ** 2 for i in range(3)))
