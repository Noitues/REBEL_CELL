r"""Storyboard v3: the mainline HQ City Grid (designer ruling: beats 1-2 and the start of the dive match the game as
built on main). The city is the round 40 unified kit (the source mainline was ported from, rebuilt here in m44/),
rendered by its own Blender scene (Eevee) and finished by post40 with the mainline values. This module holds the
mainline camera rule and the A <-> M world mapping used by the dive.

Mainline values (main @ D:\Godot\rebel_cell, read-only; scripts/city3d/city_config.gd, city_iso_camera.gd,
hq_scene.gd fit_hq_map, raid_zoom_fit.gd):
  orthographic, yaw 135, pitch 40, ortho = view width in BU, lot = 6 BU;
  HQ fit: the claimed + launchable Sites' iso box + 40 BU each side, fitted into the page's free rect x 0.65,
  anchored at (0.45, 0.42) of the frame, ortho clamped to 220..640 BU.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
M44 = os.path.join(HERE, "m44")
sys.path.insert(0, M44)
os.environ.setdefault("NET36", "net_scope.json")
import layout36 as L  # noqa: E402

YAW, PITCH = 135.0, 40.0
FIT_MARGIN, FIT_SHARE, ANCHOR, ORTHO_CLAMP = 40.0, 0.65, (0.45, 0.42), (220.0, 640.0)
GRID_ORTHO = 460.0     # the mainline grid view's scale (views.grid 440); the full fit (640, the clamp) shows our wider network too small
FREE = (230.0, 90.0, 1460.0, 800.0)          # the HQ page's free map area at 1080p (mainline layout)
SITE, RELAY = "m2_d", "m1_d"                 # Priority Lane Exchange, across the border link from Returns Processing


def net():
    return L.load_net()


def basis():
    return L.basis(dict(yaw=YAW, pitch=PITCH))


def hq_cam():
    """The mainline HQ camera: (target xyz, ortho)."""
    n = net()
    pts = [L.W(x["lot"]) for x in n["nodes"] if x["state"] in ("owned", "core", "available")]
    r, u, f = basis()
    xs = [p[0] * r[0] + p[1] * r[1] for p in pts]
    ys = [p[0] * u[0] + p[1] * u[1] for p in pts]
    bw = max(xs) - min(xs) + 2 * FIT_MARGIN
    bh = max(ys) - min(ys) + 2 * FIT_MARGIN
    fw, fh = (FREE[2] - FREE[0]) / 1920.0, (FREE[3] - FREE[1]) / 1080.0
    # px per BU = 1920 / ortho; the box spans FIT_SHARE of the free rect in the binding direction
    ortho = max(bw / (FIT_SHARE * fw), (bh * 1920.0 / 1080.0) / (FIT_SHARE * fh))
    ortho = min(ORTHO_CLAMP[1], max(ORTHO_CLAMP[0], ortho))
    ortho = min(ortho, GRID_ORTHO)
    cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    # place the box centre at the anchor: the frame centre is offset by (0.5 - a) of the view
    vw, vh = ortho, ortho * 1080.0 / 1920.0
    tx = cx + (0.5 - ANCHOR[0]) * vw
    ty = cy - (0.5 - ANCHOR[1]) * vh
    # back to world xy on the ground plane through (tx, ty) in the r/u frame (z = 0)
    # solve p.r = tx, p.u = ty with p.z = 0
    a11, a12, a21, a22 = r[0], r[1], u[0], u[1]
    det = a11 * a22 - a12 * a21
    px = (tx * a22 - a12 * ty) / det
    py = (a11 * ty - tx * a21) / det
    return (px, py, 0.0), ortho


# ---------------------------------------------------------------- the A (AAA street) <-> M (mainline city) mapping
def _nodes():
    return {x["id"]: x for x in net()["nodes"]}


def mapping():
    """M = s R(theta) (A - a0) + m0: the netrun street (relay -> Site) in A onto the border link (relay -> Site) in M."""
    import sgraph3 as G
    N = _nodes()
    a0 = ((G.col_x(G.LAST)[0] + G.col_x(G.LAST)[1]) / 2.0, G.DY[G.LAST] + 6.0)
    a1 = ((G.col_x(0)[0] + G.col_x(0)[1]) / 2.0, G.DY[0] + 6.0)
    m0, m1 = L.W(N[SITE]["lot"]), L.W(N[RELAY]["lot"])
    va = (a1[0] - a0[0], a1[1] - a0[1])
    vm = (m1[0] - m0[0], m1[1] - m0[1])
    s = math.hypot(*vm) / math.hypot(*va)
    th = math.atan2(vm[1], vm[0]) - math.atan2(va[1], va[0])
    return dict(a0=a0, m0=m0, s=s, th=th)


def a2m(p, mp=None):
    mp = mp or mapping()
    c, sn = math.cos(mp["th"]), math.sin(mp["th"])
    x, y, z = p[0] - mp["a0"][0], p[1] - mp["a0"][1], p[2]
    return (mp["m0"][0] + mp["s"] * (c * x - sn * y), mp["m0"][1] + mp["s"] * (sn * x + c * y), mp["s"] * z)


def m2a(p, mp=None):
    mp = mp or mapping()
    c, sn = math.cos(-mp["th"]), math.sin(-mp["th"])
    x, y, z = (p[0] - mp["m0"][0]) / mp["s"], (p[1] - mp["m0"][1]) / mp["s"], p[2] / mp["s"]
    return (mp["a0"][0] + c * x - sn * y, mp["a0"][1] + sn * x + c * y, z)


if __name__ == "__main__":
    t, o = hq_cam()
    print("HQ cam target", [round(v, 1) for v in t], "ortho %.1f" % o)
    mp = mapping()
    print("mapping s %.3f theta %.1f deg" % (mp["s"], math.degrees(mp["th"])))
