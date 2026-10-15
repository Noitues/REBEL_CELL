"""Storyboard: the camera poses and the animatic timeline (pure python, no Blender).

Every 3D camera in the animatic is a cam_rig Pose (the v3_dynamic rig), so the same solver drives the HQ aerial, the dive,
the OVERVIEW, the zoom and the DECISION / hover framings. Times are seconds at FPS = 24.

Beats (see NOTES.md for the table):
  1 HQ      the City Grid / HQ page idle over the AERIAL pose (static camera, 2D UI life)
  2 SELECT  cursor to the Site, holo Site file decrypts, click, orange pencil plan draws, JACK IN gloss, press
  3 JACK IN terminal types, binary rain on the link, CRT collapse, wheel slaps and spins, then the DIVE (3D)
  4 OVERVIEW the full run at the run start (static camera, city alive)
  5 ZOOM    OVERVIEW -> DECISION on the start room (the rig's zoom move, eased)
  6 CHOOSE  cursor hovers option 1 (hover ease + power cut), then option 2 (held hover, no blink), held decision
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import cam_rig as R  # noqa: E402
import sgraph3 as G  # noqa: E402

FPS = 24
WALK = G.WALK_START
OPT1, OPT2 = "L1_0", "L1_1"

# ---------------------------------------------------------------- poses
# the HQ aerial: the City Grid azimuth seen from the south-west, high, framing the Cell's network and the netrun street
OVERVIEW = R.overview(WALK)
DECISION = R.decision(WALK)
HOVER1 = R.hover(WALK, OPT1, 1.0)
HOVER2 = R.hover(WALK, OPT2, 1.0)
CORE_AT = (-420.0, 200.0)     # the Cell's territory anchor, relative to the relay (cityfill.CFG core_at)
# the MAINLINE City Grid camera (main @ 8727fd3c, PLAN1 W3_HQ / W3_GRID, ART-5 GRID_PER_CORP): the iso azimuth
# (streets on the diagonals), a high pitch, a long lens (near-orthographic)
AERIAL_YAW, AERIAL_PITCH, AERIAL_LENS, AERIAL_FILL = 45.0, 50.0, 50.0, 0.9
HQ_USE = (240.0, 110.0, 1440.0, 800.0)     # the HQ page's free map area: right of the tabs, under the bar, left of
                                          # the Site card, above the crew polaroids (mainline layout)


def _aerial():
    """The HQ framing (the rig's frame_points): the netrun street (relay to the Site, plus the block behind it) and the
    Cell's territory blocks (cityfill.net_blocks) fill AERIAL_FILL of the usable area at the City Grid azimuth."""
    import cityfill as CF
    d = CF.build(aerial=False)
    x0, _ = G.col_x(0)
    _, x1 = G.col_x(G.LAST)
    pts = [(x0, 0.0, 0.0), (x0, 12.0, 20.0), (x1, 0.0, 0.0), (x1, 12.0, 80.0), (x0, 120.0, 0.0), (x1, 120.0, 0.0)]
    for bk in d["net_blocks"]:
        bx0, by0, bx1, by1 = bk["rect"]
        pts += [((bx0 + bx1) / 2, (by0 + by1) / 2, 0.0)]
    keep = (R.USE, R.UCX, R.UCY, R.UW, R.UH)
    R.USE = HQ_USE
    R.UCX, R.UCY = (HQ_USE[0] + HQ_USE[2]) / 2, (HQ_USE[1] + HQ_USE[3]) / 2
    R.UW, R.UH = HQ_USE[2] - HQ_USE[0], HQ_USE[3] - HQ_USE[1]
    try:
        return R.frame_points(pts, AERIAL_YAW, AERIAL_PITCH, AERIAL_LENS, AERIAL_FILL, AERIAL_FILL)
    finally:
        R.USE, R.UCX, R.UCY, R.UW, R.UH = keep


AERIAL = _aerial()


def smoother(t):
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (6 * t - 15) + 10)


def dive_pose(t):
    """The jack-in dive, t 0..1: AERIAL -> OVERVIEW. F, lens and shift ease with smootherstep, distance in log space;
    the pitch lags (the camera keeps looking down while it drops, then levels out onto the street: pitch uses the
    curve u^1.6 eased), yaw eases with the position."""
    a, b = AERIAL, OVERVIEW
    u = smoother(t)
    up = smoother(min(1.0, t * 1.08) ** 1.6)
    F = tuple(R.lerp(x, y, u) for x, y in zip(a.F, b.F))
    dist = math.exp(R.lerp(math.log(a.dist), math.log(b.dist), u))
    return R.Pose(F, R.lerp(a.yaw, b.yaw, u), R.lerp(a.pitch, b.pitch, up), dist, R.lerp(a.lens, b.lens, u),
                  R.lerp(a.sx, b.sx, u), R.lerp(a.sy, b.sy, u))


# ---------------------------------------------------------------- the timeline (seconds)
T = dict(
    b1=0.0,            # HQ idle
    b2=3.0,            # SELECT: cursor sets off
    hover_site=3.7,    # cursor reaches the Site: holo decrypts (0.5 s)
    click=4.9,         # click: the Site is selected, the pencil plan draws (0.8 s)
    gloss=5.9,         # JACK IN gloss sweep (0.8 s)
    to_jack=6.5,       # cursor travels to JACK IN (0.5 s)
    press=7.1,         # press (0.25 s squash)
    b3=7.35,           # JACK IN: terminal opens and types
    rain=8.75,         # binary rain along the link (1.25 s; the designer dropped the wheel lens, the rain fills the gap)
    crt=10.0,          # terminal CRT collapse (line then dot, 0.45 s), straight into the dive
    dive=10.45,        # the dive (3.0 s), the route walls closed all the way down
    b4=13.45,          # street level (OVERVIEW): the REVEAL (walls into bits left to right, links write on), 3.64 s
    mark=17.09,        # MARK: stickers slap, rings draw, numbers, the TARGET writes on (1.0 s), the route UI arrives
    b5=18.89,          # ZOOM to the start room (1.0 s) + 0.5 s settle (after a 0.8 s hold on the marked route)
    b6=20.39,          # CHOOSE: cursor in
    hover1=20.79,      # hover option 1: ease in 0.30 s (ease-out cubic)
    hover2=22.59,      # hover option 2: the held hover moves 0.30 s (smoothstep)
    end=25.6,
)
DIVE_S = 3.0
ZOOM_S = 1.0
HOVER_IN = R.T_HOVER_IN
HOVER_MOVE = 0.30


def fr(sec):
    return int(round(sec * FPS))


NF = fr(T["end"])


def cam_at(f):
    """(segment, pose, extra) for video frame f. Segments: hq (static aerial), dive (moving), ov (static), zoom (moving),
    dec (static), hin (moving: hover ease into option 1), h1 (static), hmove (moving), h2 (static)."""
    t = f / FPS
    if t < T["dive"]:
        return "hq", AERIAL, {}
    if t < T["b4"]:
        u = (t - T["dive"]) / DIVE_S
        return "dive", dive_pose(u), dict(u=u)
    if t < T["b5"]:
        return "ov", OVERVIEW, {}
    if t < T["b5"] + ZOOM_S:
        u = R.ease((t - T["b5"]) / ZOOM_S)
        return "zoom", OVERVIEW.mix(DECISION, u), dict(u=u)
    if t < T["hover1"]:
        return "dec", DECISION, {}
    if t < T["hover1"] + HOVER_IN:
        k = R.ease_out((t - T["hover1"]) / HOVER_IN)
        return "hin", DECISION.mix(HOVER1, k), dict(k=k)
    if t < T["hover2"]:
        return "h1", HOVER1, {}
    if t < T["hover2"] + HOVER_MOVE:
        k = R.ease((t - T["hover2"]) / HOVER_MOVE)
        return "hmove", HOVER1.mix(HOVER2, k), dict(k=k)
    return "h2", HOVER2, {}


FILL_FK0 = 0.15      # the fill fog's strength over the aerial (x the stage's own field)


def fill_fk(seg, extra):
    """The fill fog fades out during the dive (it only exists for the aerial; the route views keep the r3 media)."""
    if seg == "hq":
        return FILL_FK0
    if seg == "dive":
        u = extra["u"]
        return FILL_FK0 * (1.0 - R.ease(min(1.0, max(0.0, (u - 0.30) / 0.50))))
    return 0.0


def zoom_at(seg, pose):
    """0 = the HQ city aerial .. 1 = the street (OVERVIEW): log of the camera's distance to the street centre."""
    if seg == "hq":
        return 0.0
    if seg != "dive":
        return 1.0
    c = pose.loc()
    s = OVERVIEW.F

    def dist(p):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, s)))
    d0, d1 = dist(AERIAL.loc()), dist(OVERVIEW.loc())
    return max(0.0, min(1.0, math.log(d0 / max(dist(c), 1e-3)) / math.log(d0 / d1)))


WALL_START, WALL_STAGGER, WALL_DUR = 0.50, 0.045, 0.40    # dive fraction, s per room, s per wall


def wall_order():
    """The dissolve order: the route's rooms from the start room toward the TARGET (layer, then slot)."""
    return sorted(G.NODES, key=lambda i: (G.LAYER[i], G.K[i]))


def wall_dis(f):
    """v2: the walls stay closed through the whole dive (the street-level reveal is composited, sb_reveal.py)."""
    return {i: 0.0 for i in G.NODES}


def wall_dis_v1(f):
    """{room: dissolve 0..1} at video frame f (v1: in the dive's last second)."""
    t = f / FPS
    t0 = T["dive"] + WALL_START * DIVE_S
    out = {}
    for k, i in enumerate(wall_order()):
        u = (t - (t0 + k * WALL_STAGGER)) / WALL_DUR
        out[i] = max(0.0, min(1.0, u))
    return out


CITY_HAZE = 0.20     # the aerial's haze, as a share of the stage's back haze (the whole city reads alike)


def _dive_fade(u):
    return 1.0 - R.ease(min(1.0, max(0.0, (u - 0.30) / 0.50)))


def haze_at(seg, extra):
    """(stage back-haze share, fill haze body share): city level in the aerial, r3 at the street."""
    if seg == "hq":
        return CITY_HAZE, CITY_HAZE
    if seg == "dive":
        f = _dive_fade(extra["u"])
        return 1.0 - (1.0 - CITY_HAZE) * f, CITY_HAZE * f
    return 1.0, 0.0


MOVING = ("dive", "zoom", "hin", "hmove")


def segments():
    """Ordered list of (segment, first frame, last frame)."""
    out = []
    for f in range(NF):
        s = cam_at(f)[0]
        if out and out[-1][0] == s:
            out[-1][2] = f
        else:
            out.append([s, f, f])
    return out


if __name__ == "__main__":
    for nm, p in (("AERIAL", AERIAL), ("OVERVIEW", OVERVIEW), ("DECISION", DECISION), ("HOVER1", HOVER1), ("HOVER2", HOVER2)):
        print(nm, [round(v, 1) for v in p.loc()], "F", [round(v, 1) for v in p.F], "yaw %.1f pitch %.1f dist %.1f lens %.0f"
              % (p.yaw, p.pitch, p.dist, p.lens))
    print("frames", NF, "%.2f s" % (NF / FPS))
    for s in segments():
        print(s, "%d frames" % (s[2] - s[1] + 1))
    for u in (0.0, 0.25, 0.5, 0.75, 0.9, 1.0):
        p = dive_pose(u)
        print("dive %.2f" % u, [round(v, 1) for v in p.loc()], "pitch %.1f dist %.0f" % (p.pitch, p.dist))


# ---------------------------------------------------------------- v3: the dive starts in the mainline city (designer)
# One camera path, defined in the mainline (M) world: from the mainline HQ camera (orthographic, emulated by a long lens
# so the start does not jump) down to the street OVERVIEW mapped into M (the netrun street = the border link from
# Returns Processing to the Site the player picked in beat 2: sb_mainline.mapping). The AAA-2 (A) camera of any frame is
# the same pose mapped back. The two worlds cross in the look_blend_by_zoom band behind a cloud veil.
HQ_LENS = 300.0
LOOK_M_MAX, LOOK_A_MIN = 0.60, 0.16     # the band (0.20-0.55) plus a margin each side


def _ml():
    import sb_mainline as ML
    return ML


def _m_ends():
    ML = _ml()
    mp = ML.mapping()
    t0, o0 = ML.hq_cam()
    y0, p0 = 135.0, 40.0
    locA, FA = OVERVIEW.loc(), OVERVIEW.F
    locM, FM = ML.a2m(locA, mp), ML.a2m(FA, mp)
    fv = [b - a for a, b in zip(locM, FM)]
    D1 = math.sqrt(sum(v * v for v in fv))
    fv = [v / D1 for v in fv]
    y1 = math.degrees(math.atan2(fv[1], fv[0]))
    while y1 - y0 > 180:
        y1 -= 360
    while y1 - y0 < -180:
        y1 += 360
    p1 = math.degrees(math.asin(-fv[2]))
    return dict(t0=t0, w0=o0, y0=y0, p0=p0, t1=FM, w1=D1 * 36.0 / OVERVIEW.lens, y1=y1, p1=p1, l1=OVERVIEW.lens,
                sx1=OVERVIEW.sx, sy1=OVERVIEW.sy, mp=mp)


_ME = {}


def dive_pose_m(t):
    """The dive camera in the mainline world: dict(loc, tgt, lens, sx, sy)."""
    if "e" not in _ME:
        _ME["e"] = _m_ends()
    e = _ME["e"]
    u = smoother(t)
    up = smoother(min(1.0, t * 1.08) ** 1.6)
    tg = [R.lerp(a, b, u) for a, b in zip(e["t0"], e["t1"])]
    yaw = R.lerp(e["y0"], e["y1"], u)
    pit = R.lerp(e["p0"], e["p1"], up)
    w = math.exp(R.lerp(math.log(e["w0"]), math.log(e["w1"]), u))
    lens = math.exp(R.lerp(math.log(HQ_LENS), math.log(e["l1"]), u))
    D = w * lens / 36.0
    yr, pr = math.radians(yaw), math.radians(pit)
    fv = (math.cos(yr) * math.cos(pr), math.sin(yr) * math.cos(pr), -math.sin(pr))
    loc = [tg[i] - fv[i] * D for i in range(3)]
    return dict(loc=loc, tgt=tg, lens=lens, sx=R.lerp(0.0, e["sx1"], u), sy=R.lerp(0.0, e["sy1"], u))


def dive_pose(t):  # noqa: F811
    """v3: the dive camera in the AAA-2 world (the mainline pose mapped back)."""
    ML = _ml()
    pm = dive_pose_m(t)
    if "e" not in _ME:
        _ME["e"] = _m_ends()
    mp = _ME["e"]["mp"]
    la, fa = ML.m2a(pm["loc"], mp), ML.m2a(pm["tgt"], mp)
    d = [b - a for a, b in zip(la, fa)]
    D = math.sqrt(sum(v * v for v in d))
    d = [v / D for v in d]
    return R.Pose(tuple(fa), math.degrees(math.atan2(d[0], d[1])), math.degrees(math.asin(-d[2])), D, pm["lens"],
                  pm["sx"], pm["sy"])


def zoom_at(seg, pose):  # noqa: F811
    """0 = the HQ (mainline aerial) .. 1 = the street OVERVIEW: log of the A-world camera distance to the street centre."""
    if seg == "hq":
        return 0.0
    if seg != "dive":
        return 1.0
    s = OVERVIEW.F

    def dist(p):
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p, s)))
    if "d0" not in _ME:
        _ME["d0"] = dist(dive_pose(0.0).loc())
    d0, d1 = _ME["d0"], dist(OVERVIEW.loc())
    return max(0.0, min(1.0, math.log(d0 / max(dist(pose.loc()), 1e-3)) / math.log(d0 / d1)))


def look_blend(zoom):
    """0 = the mainline look and world, 1 = AAA-2 (look_preset lod_bands look_blend_by_zoom)."""
    import look_preset as LP
    a, b = LP.PRESET["lod_bands"]["look_blend_by_zoom"]
    u = max(0.0, min(1.0, (zoom - a) / (b - a)))
    return u * u * (3 - 2 * u)


def mainline_dive(f):
    s, pose, ex = cam_at(f)
    return s == "dive" and zoom_at(s, pose) <= LOOK_M_MAX


def aaa_dive(f):
    s, pose, ex = cam_at(f)
    return s == "dive" and zoom_at(s, pose) >= LOOK_A_MIN
