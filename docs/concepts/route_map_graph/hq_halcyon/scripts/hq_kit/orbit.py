"""hq_kit.orbit: the orbit camera for an HQ compound (pure python). The pose model, the framing solver and the hover
ease are V3 dynamic's cam_rig (same numbers); the HQ replaces psi(u) with an ORBIT:

    from hq_kit.orbit import Orbit, Pose
    O = Orbit(compound, cfg=None)        # cfg overrides ORBIT_DEFAULTS
    O.decision(walked) / O.hover(walked, node, k) / O.overview(walked) -> Pose
    O.zoom_of(pose, walked) -> 0 (overview) .. 1 (decision)       (the lod_bands parameter)
    O.visible_face(f, pose) -> bool                                (rooms on far faces are hidden by the landmark)
    Pose.proj(world_point, w=1920) -> pixel (16:9), Pose.mix(other, t), Pose.to_json()

Rules:
  DECISION azimuth = the mean of the look vectors (-outward normal) of the DISTINCT faces holding the current room and
           the options (one face: straight at it; a choice round a corner: the camera sits on the corner).
  DECISION pitch   = lerp(pitch_lo, pitch_hi) over the climb (segment / (segments - 1)); lens 30.
  framing          = the rig's solver: the set fills fill_w of the usable width or fill_h of its height, never closer
                     than dmin (a one-option decision would fill the frame with one room).
  hover            = 22 % toward the room, 3 deg toward it, distance x0.96.
  OVERVIEW         = high 3/4 (pitch_o, lens_o) on the CORNER whose two faces hold the most route rooms that still
                     matter (walked, current, options, ahead), tie to the current face; framed on the whole landmark.
  occlusion        = a room is drawn when dot(face normal, direction to the camera) > 0.12.
"""
import math

W, H = 1920, 1080
SENSOR = 36.0
USE = (300.0, 138.0, 1900.0, 1012.0)          # usable area (px at 1080p): right of the sidebar, under the top strip
UCX, UCY = (USE[0] + USE[2]) / 2, (USE[1] + USE[3]) / 2
UW, UH = USE[2] - USE[0], USE[3] - USE[1]
ORBIT_DEFAULTS = dict(dmin=135.0, look_ahead=0.0, pitch_lo=13.0, pitch_hi=24.0, lens_d=30.0, fill_w=0.66, fill_h=0.70,
                      hover_pull=0.22, hover_yaw=3.0, hover_dolly=0.96, pitch_o=26.0, lens_o=40.0, fill_ow=0.95,
                      fill_oh=0.90, vis_margin=0.12)


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

    def mix(self, o, t):
        F = tuple(lerp(a, b, t) for a, b in zip(self.F, o.F))
        return Pose(F, lerp(self.yaw, o.yaw, t), lerp(self.pitch, o.pitch, t),
                    math.exp(lerp(math.log(self.dist), math.log(o.dist), t)), lerp(self.lens, o.lens, t),
                    lerp(self.sx, o.sx, t), lerp(self.sy, o.sy, t))

    @staticmethod
    def from_json(js):
        loc, tgt = js["loc"], js["tgt"]
        d = [tgt[k] - loc[k] for k in range(3)]
        dist = math.sqrt(sum(v * v for v in d))
        return Pose(tgt, math.degrees(math.atan2(d[0], d[1])), -math.degrees(math.asin(d[2] / dist)), dist, js["lens"],
                    js.get("shift_x", 0.0), js.get("shift_y", 0.0))


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


class Orbit:
    def __init__(self, compound, cfg=None):
        self.C = compound
        self.cfg = dict(ORBIT_DEFAULTS)
        self.cfg.update(cfg or {})

    @staticmethod
    def look_of_face(f):
        from .layout import N
        return (-N[f][0], -N[f][1])

    @staticmethod
    def yaw_of(v):
        return math.degrees(math.atan2(v[0], v[1]))

    def beat(self, row):
        r = max(0, min(self.C.R - 1, row))
        return dict(pitch=lerp(self.cfg["pitch_lo"], self.cfg["pitch_hi"], r / max(1, self.C.R - 1)),
                    lens=self.cfg["lens_d"])

    def decision_yaw(self, walked):
        cur = walked[-1]
        st, opts = self.C.states(walked)
        ids = [cur if cur != "start" else self.C.NODES[1]] + opts
        faces = sorted({self.C.FACE[i] for i in ids if self.C.FACE[i] >= 0})
        v = (sum(self.look_of_face(f)[0] for f in faces), sum(self.look_of_face(f)[1] for f in faces))
        return self.yaw_of(v) + self.cfg["look_ahead"]

    def decision(self, walked):
        cur = walked[-1]
        st, opts = self.C.states(walked)
        pts = []
        for i in [cur] + opts:
            pts += self.C.room_corners(i)
        b = self.beat(self.C.ROW[cur] if self.C.ROW[cur] >= 0 else 0)
        return frame_points(pts, self.decision_yaw(walked), b["pitch"], b["lens"], self.cfg["fill_w"],
                            self.cfg["fill_h"], dmin=self.cfg["dmin"])

    def hover(self, walked, node, k=1.0):
        p = self.decision(walked)
        c = self.C.room_center(node)
        F = v_add(p.F, v_mul(v_sub(c, p.F), self.cfg["hover_pull"]))
        d = p.dir()
        r = (d[1], -d[0])
        s = 1.0 if (c[0] - p.F[0]) * r[0] + (c[1] - p.F[1]) * r[1] > 0 else -1.0
        h = Pose(F, p.yaw + self.cfg["hover_yaw"] * s, p.pitch, p.dist * self.cfg["hover_dolly"], p.lens, p.sx, p.sy)
        return p.mix(h, k)

    def overview_yaw(self, walked):
        C = self.C
        st, _ = C.states(walked)
        live = [i for i in C.NODES if i not in ("start", "srv") and st[i] != "grey"]
        cur = walked[-1] if walked[-1] != "start" else C.NODES[1]
        fc = C.FACE[cur]
        best = None
        for f in range(4):
            g = (f + 1) % 4
            n = sum(1 for i in live if C.FACE[i] in (f, g))
            key = (n, 1 if f == fc else 0, -f)
            if best is None or key > best[0]:
                best = (key, f, g)
        _, f, g = best
        lf, lg = self.look_of_face(f), self.look_of_face(g)
        return self.yaw_of((lf[0] + lg[0], lf[1] + lg[1]))

    def overview_points(self):
        C = self.C
        pts = []
        for t in C.tiers():
            for sx_ in (-1, 1):
                for sy_ in (-1, 1):
                    pts.append((sx_ * t["hs"], sy_ * t["hs"], t["z0"]))
        e = C.eye_pos()
        pts += [(e[0], e[1], e[2] + C.cfg["eye"].get("h", 20.0) / 2 + 6.0)]
        sx, sy, _ = C.start_pos()
        pts += [(sx - 6, sy - 4, -1.0)]
        pc = C.cfg["podium_x"]
        pts += [(-pc, -pc, 0.0), (pc, -pc, 0.0), (pc, pc, 0.0), (-pc, pc, 0.0)]
        return pts

    def overview(self, walked):
        mid = (self.C.tier_floor(self.C.R) + self.C.TH) / 2.0
        return frame_points(self.overview_points(), self.overview_yaw(walked), self.cfg["pitch_o"], self.cfg["lens_o"],
                            self.cfg["fill_ow"], self.cfg["fill_oh"], centre=(0.0, 0.0, mid))

    def zoom_of(self, pose, walked):
        do, dd = self.overview(walked).dist, self.decision(walked).dist
        return max(0.0, min(1.0, math.log(do / pose.dist) / math.log(do / dd)))

    def visible_face(self, f, pose, margin=None):
        from .layout import N
        m = self.cfg["vis_margin"] if margin is None else margin
        c = pose.loc()
        L = math.hypot(c[0], c[1])
        return (N[f][0] * c[0] + N[f][1] * c[1]) / max(L, 1e-6) > m
