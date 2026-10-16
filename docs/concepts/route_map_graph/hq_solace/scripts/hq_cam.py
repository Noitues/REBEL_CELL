"""HQ kit: the V3 camera rig with HQ camera beats (pure python), generalised from hq_halcyon/scripts/hq_cam.py.

The pose model, framing solver, hover ease and overview are r3 / V3 dynamic's cam_rig (same numbers); the corp's
beat lives in its preset ("cam") and, when a corp needs more than the generic rule, in hq_graph.CAM_RULE:
  decision yaw   the circular mean of the look vectors (-n) of the distinct room normals holding the current room
                 and the options (one face: straight at it; a choice round a corner: on the corner)
  pitch          pitch_lo .. pitch_hi by the current room's layer (higher rooms are seen from higher up)
  overview       a high 3/4 at the corp's yaw (preset cam.ov_yaw), framing hq_graph.OV_POINTS
  occlusion      a room is drawn only when its opening faces the camera (n . to-camera > margin)
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import hq_graph as G  # noqa: E402
import hq_preset as HP  # noqa: E402

CAMP = HP.PRESET["hq"]["cam"]
W, H = 1920, 1080
SENSOR = 36.0
USE = (300.0, 138.0, 1900.0, 1012.0)
UCX, UCY = (USE[0] + USE[2]) / 2, (USE[1] + USE[3]) / 2
UW, UH = USE[2] - USE[0], USE[3] - USE[1]
DMIN = CAMP["dmin"]
PITCH_LO, PITCH_HI = CAMP["pitch_lo"], CAMP["pitch_hi"]
LENS_D = CAMP["lens"]
FILL_W, FILL_H = CAMP["fill"]
HOVER_PULL, HOVER_YAW, HOVER_DOLLY = 0.22, 3.0, 0.96
PITCH_O, LENS_O = CAMP["pitch_o"], CAMP["lens_o"]
FILL_OW, FILL_OH = CAMP["fill_o"]
FPS = 24


def v_add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def v_sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def v_mul(a, k):
    return tuple(x * k for x in a)


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norm(a):
    L = math.sqrt(dot(a, a))
    return v_mul(a, 1.0 / L)


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = max(0.0, min(1.0, t))
    return t ** 3


def wrap(a):
    return (a + 180.0) % 360.0 - 180.0


class Pose:
    def __init__(self, F, yaw, pitch, dist, lens, sx=0.0, sy=0.0, roll=0.0):
        self.F, self.yaw, self.pitch, self.dist, self.lens, self.sx, self.sy = tuple(F), yaw, pitch, dist, lens, sx, sy
        self.roll = roll

    def dir(self):
        y, p = math.radians(self.yaw), math.radians(self.pitch)
        return (math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p))

    def loc(self):
        return v_sub(self.F, v_mul(self.dir(), self.dist))

    def proj(self, P, shift=True, w=W):
        f = self.dir()
        r = norm(cross(f, (0, 0, 1)))
        u = cross(r, f)
        d = v_sub(P, self.loc())
        z = dot(d, f)
        if z <= 0.1:
            return None
        k = self.lens / SENSOR
        nx, ny = k * dot(d, r) / z, k * dot(d, u) / z
        sx, sy = (self.sx, self.sy) if shift else (0.0, 0.0)
        h = w * 9 / 16
        return (w / 2 + (nx - sx) * w, h / 2 - (ny - sy) * w)

    def to_json(self):
        return dict(loc=self.loc(), tgt=self.F, lens=self.lens, shift_x=self.sx, shift_y=self.sy, yaw=self.yaw,
                    pitch=self.pitch, dist=self.dist)

    def mix(self, o, t, yaw_short=True):
        F = tuple(lerp(a, b, t) for a, b in zip(self.F, o.F))
        y1 = self.yaw + wrap(o.yaw - self.yaw) if yaw_short else o.yaw
        return Pose(F, lerp(self.yaw, y1, t), lerp(self.pitch, o.pitch, t),
                    math.exp(lerp(math.log(self.dist), math.log(o.dist), t)), lerp(self.lens, o.lens, t),
                    lerp(self.sx, o.sx, t), lerp(self.sy, o.sy, t))


def pose_of(js):
    loc, tgt = js["loc"], js["tgt"]
    d = [tgt[k] - loc[k] for k in range(3)]
    dist = math.sqrt(sum(v * v for v in d))
    yaw = math.degrees(math.atan2(d[0], d[1]))
    pitch = -math.degrees(math.asin(d[2] / dist))
    return Pose(tgt, yaw, pitch, dist, js["lens"], js.get("shift_x", 0.0), js.get("shift_y", 0.0))


def bbox_px(pose, pts):
    q = [pose.proj(p, shift=False) for p in pts]
    q = [p for p in q if p]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return min(xs), min(ys), max(xs), max(ys)


def frame_points(pts, yaw, pitch, lens, fw, fh, bias=0.0, centre=None, dmin=0.0):
    xs, ys, zs = zip(*pts)
    F = centre or ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
    lo, hi = 5.0, 3000.0
    for _ in range(60):
        d = math.sqrt(lo * hi)
        p = Pose(F, yaw, pitch, d, lens)
        try:
            x0, y0, x1, y1 = bbox_px(p, pts)
            k = max((x1 - x0) / (fw * UW), (y1 - y0) / (fh * UH))
        except ValueError:
            k = 9.0
        if k > 1.0:
            lo = d
        else:
            hi = d
    p = Pose(F, yaw, pitch, max(hi, dmin), lens)
    x0, y0, x1, y1 = bbox_px(p, pts)
    p.sx = ((x0 + x1) / 2 - (UCX + bias * UW)) / W
    p.sy = (UCY - (y0 + y1) / 2) / W
    return p


def yaw_of(v):
    return math.degrees(math.atan2(v[0], v[1]))


def look_yaw(ids, mt=None):
    seen = []
    for i in ids:
        n = G.room_normal(i, mt)
        if n is None:
            continue
        key = (round(n[0], 2), round(n[1], 2))
        if key not in seen:
            seen.append(key)
    sx = sum(-n[0] for n in seen)
    sy = sum(-n[1] for n in seen)
    if abs(sx) + abs(sy) < 1e-6:
        return CAMP.get("ov_yaw", 0.0)
    return yaw_of((sx, sy))


def beat(walked):
    lay = [G.LAYER.get(i, 0) for i in walked[-1:]]
    top = max(G.LAYER.values())
    return dict(pitch=lerp(PITCH_LO, PITCH_HI, (lay[0] / max(1, top))), lens=LENS_D)


def decision_ids(walked, mt=None):
    cur = walked[-1]
    st, opts = G.states(walked, mt)
    return ([cur] if cur != "start" else []) + opts


def centre_on(p, c):
    """Front and centre (designer review 2026-10-15): shift the lens so world point c sits in the middle of the
    usable frame (the framing solver has already pulled back far enough for the options)."""
    q = p.proj(c, shift=False)
    p.sx = (q[0] - UCX) / W
    p.sy = (UCY - q[1]) / W
    return p


def decision(walked, mt=None):
    if hasattr(G, "CAM_RULE"):
        return G.CAM_RULE(walked, mt, sys.modules[__name__])
    ids = decision_ids(walked, mt)
    pts = []
    for i in ids:
        pts += G.room_corners(i, mt)
    b = beat(walked)
    cur = walked[-1]
    if cur != "start" and CAMP.get("centre_current", True):
        c = G.room_center(cur, mt)
        p = frame_points(pts, look_yaw(ids, mt), b["pitch"], b["lens"], FILL_W, FILL_H, centre=c, dmin=DMIN)
        return centre_on(p, c)
    return frame_points(pts, look_yaw(ids, mt), b["pitch"], b["lens"], FILL_W, FILL_H, dmin=DMIN)


def hover(walked, node, k=1.0, mt=None):
    p = decision(walked, mt)
    c = G.room_center(node, mt)
    F = v_add(p.F, v_mul(v_sub(c, p.F), HOVER_PULL))
    d = p.dir()
    r = (d[1], -d[0])
    s = 1.0 if (c[0] - p.F[0]) * r[0] + (c[1] - p.F[1]) * r[1] > 0 else -1.0
    h = Pose(F, p.yaw + HOVER_YAW * s, p.pitch, p.dist * HOVER_DOLLY, p.lens, p.sx, p.sy)
    return p.mix(h, k)


def overview(walked=None, mt=None):
    return frame_points(G.OV_POINTS, CAMP["ov_yaw"], PITCH_O, LENS_O, FILL_OW, FILL_OH, centre=tuple(CAMP["ov_centre"]))


def zoom_of(pose, walked=None):
    w = walked or G.WALK_MID
    do, dd = overview(w).dist, decision(w).dist
    return max(0.0, min(1.0, math.log(do / pose.dist) / math.log(do / dd)))


def visible_n(n, o, pose, margin=0.12):
    if n is None:
        return True
    c = pose.loc()
    d = (c[0] - o[0], c[1] - o[1])
    L = math.hypot(*d)
    return (n[0] * d[0] + n[1] * d[1]) / max(L, 1e-6) > margin


def visible_room(i, pose, mt=None, margin=0.12):
    r = G.room_rec(i, mt)
    return visible_n(r["n"], r["o"], pose, margin)


def stills():
    return G.STILLS(sys.modules[__name__])


if __name__ == "__main__":
    for name, (p, s) in stills().items():
        print(name, [round(v, 1) for v in p.loc()], "yaw %.1f pitch %.1f dist %.1f sx %.3f sy %.3f zoom %.2f" % (
            p.yaw, p.pitch, p.dist, p.sx, p.sy, zoom_of(p)))
