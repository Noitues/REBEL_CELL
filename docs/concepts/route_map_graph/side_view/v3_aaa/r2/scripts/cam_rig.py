"""V3 dynamic: the camera rig (pure python, no Blender). The spec in NOTES.md is this file.

A pose is (F, yaw, pitch, dist, lens, shift_x, shift_y): the camera sits at F - dist * dir and looks at F, with
dir = (sin yaw cos pitch, cos yaw cos pitch, -sin pitch). yaw > 0 looks right (down the street, +x).

  DECISION  yaw(u) = YAW_MAX * (1 - 2u), u = current layer / (TARGET layer - 1): left looking right at the start,
            centred mid-run, right looking back left at the last room. The framed set is the current room plus the
            available rooms (8 corners each); the distance is solved so that set fills FILL_W of the usable width or
            FILL_H of the usable height (whichever binds), then the lens shift centres it in the usable area (the
            street area right of the sidebar, under the top strip, over the legend).
  HOVER     F eases HOVER_PULL of the way to the hovered room, yaw turns HOVER_YAW toward it, dist x HOVER_DOLLY.
  OVERVIEW  the whole run (every room + the TARGET crown), yaw = OV_YAW_K * yaw(u), flatter pitch, longer lens.
  Moves interpolate F (linear), yaw, pitch, lens, shift (linear) and dist (log) with smoothstep easing.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import sgraph3 as G  # noqa: E402

W, H = 1920, 1080
SENSOR = 36.0
USE = (300.0, 138.0, 1900.0, 1012.0)          # usable street area (px at 1080p)
UCX, UCY = (USE[0] + USE[2]) / 2, (USE[1] + USE[3]) / 2
UW, UH = USE[2] - USE[0], USE[3] - USE[1]

YAW_MAX = 24.0          # deg
PITCH_D = 9.0
LENS_D = 30.0
FILL_W, FILL_H = 0.66, 0.70
LOOK_BIAS = 0.10          # the decision set sits this much (x usable width) off-centre, away from where the camera looks
HOVER_PULL, HOVER_YAW, HOVER_DOLLY = 0.22, 3.0, 0.96
OV_YAW_K, PITCH_O, LENS_O, FILL_OW, FILL_OH = 0.3, 6.0, 40.0, 0.95, 0.90
T_STEP, T_HOVER_IN, T_HOVER_OUT, T_ZOOM = 0.9, 0.30, 0.35, 0.70     # seconds (the video uses these)
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


class Pose:
    def __init__(self, F, yaw, pitch, dist, lens, sx=0.0, sy=0.0):
        self.F, self.yaw, self.pitch, self.dist, self.lens, self.sx, self.sy = tuple(F), yaw, pitch, dist, lens, sx, sy

    def dir(self):
        y, p = math.radians(self.yaw), math.radians(self.pitch)
        return (math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), -math.sin(p))

    def loc(self):
        return v_sub(self.F, v_mul(self.dir(), self.dist))

    def proj(self, P, shift=True):
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
        return (W / 2 + (nx - sx) * W, H / 2 - (ny - sy) * W)

    def to_json(self):
        return dict(loc=self.loc(), tgt=self.F, lens=self.lens, shift_x=self.sx, shift_y=self.sy, yaw=self.yaw,
                    pitch=self.pitch, dist=self.dist)

    def mix(self, o, t):
        F = tuple(lerp(a, b, t) for a, b in zip(self.F, o.F))
        return Pose(F, lerp(self.yaw, o.yaw, t), lerp(self.pitch, o.pitch, t),
                    math.exp(lerp(math.log(self.dist), math.log(o.dist), t)), lerp(self.lens, o.lens, t),
                    lerp(self.sx, o.sx, t), lerp(self.sy, o.sy, t))


def bbox_px(pose, pts):
    q = [pose.proj(p, shift=False) for p in pts]
    q = [p for p in q if p]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    return min(xs), min(ys), max(xs), max(ys)


def frame_points(pts, yaw, pitch, lens, fw, fh, bias=0.0):
    """Solve dist and shift so pts fill fw of the usable width or fh of the usable height, centred in it."""
    xs, ys, zs = zip(*pts)
    F = ((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, (min(zs) + max(zs)) / 2)
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
    p = Pose(F, yaw, pitch, hi, lens)
    x0, y0, x1, y1 = bbox_px(p, pts)
    p.sx = ((x0 + x1) / 2 - (UCX + bias * UW)) / W
    p.sy = (UCY - (y0 + y1) / 2) / W
    return p


def yaw_u(u):
    return YAW_MAX * (1 - 2 * max(0.0, min(1.0, u)))


def decision(walked):
    cur = walked[-1]
    st, opts = G.states(walked)
    pts = []
    for i in [cur] + opts:
        pts += G.room_corners(i)
    u = G.LAYER[cur] / (G.LAST - 1)
    y = yaw_u(u)
    return frame_points(pts, y, PITCH_D, LENS_D, FILL_W, FILL_H, bias=-LOOK_BIAS * y / YAW_MAX)


def hover(walked, node, k=1.0):
    p = decision(walked)
    c = G.room_center(node)
    F = v_add(p.F, v_mul(v_sub(c, p.F), HOVER_PULL))
    s = 1.0 if c[0] > p.F[0] else -1.0
    h = Pose(F, p.yaw + HOVER_YAW * s, p.pitch, p.dist * HOVER_DOLLY, p.lens, p.sx, p.sy)
    return p.mix(h, k)


def overview(walked):
    pts = []
    for i in G.NODES:
        pts += G.room_corners(i)
    x0, x1 = G.col_x(G.LAST)
    pts += [(x0, G.DY[G.LAST], G.roof_z(G.LAST) + 6.0), (x1, G.DY[G.LAST], G.roof_z(G.LAST) + 6.0), (G.col_x(0)[0], 0, -2)]
    u = G.LAYER[walked[-1]] / (G.LAST - 1)
    return frame_points(pts, OV_YAW_K * yaw_u(u), PITCH_O, LENS_O, FILL_OW, FILL_OH)


# ---------------------------------------------------------------- shots
def stills():
    """name -> (pose, overlay state). Overlay state: walked, hover, hover_k, zoom (0 decision .. 1 overview)."""
    return {
        "D_start": (decision(G.WALK_START), dict(walked=G.WALK_START)),
        "D_mid": (decision(G.WALK_MID), dict(walked=G.WALK_MID)),
        "D_mid_hover": (hover(G.WALK_MID, G.HOVER_MID), dict(walked=G.WALK_MID, hover=G.HOVER_MID, hover_k=1.0)),
        "D_end": (decision(G.WALK_END), dict(walked=G.WALK_END)),
        "O_overview": (overview(G.WALK_MID), dict(walked=G.WALK_MID, zoom=1.0)),
    }


def timeline():
    """The video: a list of (pose, overlay state) per frame at FPS. States carry 'step' = (a, b, t) while moving."""
    fr = []

    def hold(walked, sec, pose_fn=None, **kw):
        n = int(round(sec * FPS))
        for _ in range(n):
            fr.append(((pose_fn or (lambda: decision(walked)))(), dict(walked=walked, **kw)))

    walk = G.VIDEO_WALK
    hold(walk[:1], 0.5)
    for s in range(1, len(walk)):
        before, after = walk[:s], walk[:s + 1]
        p0, p1 = decision(before), decision(after)
        n = int(round(T_STEP * FPS))
        for k in range(n):
            t = (k + 1) / n
            fr.append((p0.mix(p1, ease(t)), dict(walked=before, step=(before[-1], after[-1], ease(min(1.0, t * 1.12))))))
        hold(after, 0.25 if s < len(walk) - 1 else 0.3)
    mid = walk
    n = int(round(T_HOVER_IN * FPS))
    for k in range(n):
        t = ease_out((k + 1) / n)
        fr.append((hover(mid, G.HOVER_MID, t), dict(walked=mid, hover=G.HOVER_MID, hover_k=t)))
    hold(mid, 0.5, lambda: hover(mid, G.HOVER_MID, 1.0), hover=G.HOVER_MID, hover_k=1.0)
    n = int(round(T_HOVER_OUT * FPS))
    for k in range(n):
        t = 1 - ease((k + 1) / n)
        fr.append((hover(mid, G.HOVER_MID, t), dict(walked=mid, hover=G.HOVER_MID if t > 0.02 else None, hover_k=t)))
    zs = len(fr)
    hold(mid, 0.25)
    d, o = decision(mid), overview(mid)
    n = int(round(T_ZOOM * FPS))
    for k in range(n):
        t = ease((k + 1) / n)
        fr.append((d.mix(o, t), dict(walked=mid, zoom=t)))
    hold(mid, 0.5, lambda: o, zoom=1.0)
    ze = len(fr)
    for k in range(n):
        t = ease((k + 1) / n)
        fr.append((o.mix(d, t), dict(walked=mid, zoom=1 - t)))
    hold(mid, 0.35)
    return fr, (zs, ze)


if __name__ == "__main__":
    for name, (p, s) in stills().items():
        print(name, [round(v, 2) for v in p.loc()], "yaw %.1f dist %.1f sx %.3f sy %.3f" % (p.yaw, p.dist, p.sx, p.sy))
    fr, z = timeline()
    print("video frames", len(fr), "%.2fs" % (len(fr) / FPS), "zoom range", z)
