"""Render one still's 3D base.  Usage:
blender -b --factory-startup --python render_shot.py -- <shot> <out_png> [samples]
shot: city_day | city_night | city_suspicion | combat | shop
Writes <out_png> and <out_png>.json (projected anchors for the Pillow pass)."""
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from bpy_extras.object_utils import world_to_camera_view  # noqa: E402
from mathutils import Vector  # noqa: E402

import layout as L  # noqa: E402
from bl_kit import (m_emit, m_pbr, m_screen, m_veil, MeshBuf, rrect, curve_obj, arc, swirl,  # noqa: E402
                    point_light, spot_light, sun, camera, setup_render, link)
import bl_city as C  # noqa: E402

FONT_DIR = "C:/Windows/Fonts/"


def clear():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)


def project(cam, p):
    v = world_to_camera_view(bpy.context.scene, cam, Vector(p))
    return (v.x * L.W, (1.0 - v.y) * L.H)


def ui_root(cam):
    e = bpy.data.objects.new("ui_root", None)
    link(e, cam)
    e.location = (0, 0, -L.UI_DIST)
    return e


def P(px, py, z=0.0):
    u, v = L.px_to_ui(px, py)
    return (u, v, z)


# ---------------------------------------------------------------- UI pieces
def card3d(root, rng, cx, cy, ang_deg, kind, z=0.3):
    col = L.SLICE_COLORS[kind]
    w, h = L.CARD_W / L.PPU, L.CARD_H / L.PPU
    e = bpy.data.objects.new("card", None)
    link(e, root)
    e.location = P(cx, cy, z)
    e.rotation_euler = (0, 0, math.radians(ang_deg))
    b = MeshBuf()
    b.prism(rrect(w, h, 0.09), -0.02, 0.0)
    b.build("card_body", [m_pbr((0.05, 0.025, 0.09), rough=0.22, metal=0.35, emit=col, es=0.08, film=460)], parent=e)
    outline = [(x, y, 0.004) for x, y in rrect(w, h, 0.09)]
    curve_obj("card_edge", outline, 0.009, m_emit(col, 2.4), parent=e, cyclic=True)
    inner = [(x * 0.94, y * 0.96, 0.004) for x, y in rrect(w, h, 0.09)]
    curve_obj("card_edge2", inner, 0.003, m_emit((1, 1, 1), 1.2, alpha=0.6), parent=e, cyclic=True)
    # art window: painted neon gradient + a mini light-swirl
    aw, ah = w * 0.86, h * 0.42
    ay = h * 0.12
    stops = {"atk": [(0, (0.5, 0.0, 0.25)), (0.45, (1.0, 0.15, 0.4)), (0.7, (1.0, 0.6, 0.2)), (1, (1.0, 0.9, 0.6))],
             "blk": [(0, (0.0, 0.1, 0.35)), (0.45, (0.1, 0.6, 1.0)), (0.7, (0.5, 0.9, 1.0)), (1, (0.9, 0.5, 1.0))],
             "hack": [(0, (0.35, 0.05, 0.0)), (0.45, (1.0, 0.45, 0.05)), (0.7, (1.0, 0.85, 0.3)), (1, (1.0, 0.3, 0.6))]}[kind]
    b = MeshBuf()
    b.prism([(x, y + ay) for x, y in rrect(aw, ah, 0.05)], 0.0, 0.006)
    b.build("card_art", [m_screen(stops, 0.9, scale=1.6)], parent=e)
    art = bpy.data.objects.new("art", None)
    link(art, e)
    art.location = (0, ay, 0.03)
    swirl(rng, "cs", (0, 0, 0), (0, 0, 0), ah * 0.12, ah * 0.46, 12,
          [(1, 1, 1), col, (1.0, 0.6, 0.2)], 2.2, thick=(0.003, 0.009), parent=art, tilt=0.4)
    # cost orb
    b = MeshBuf()
    b.prism([(0.1 * math.cos(math.tau * k / 24) - w / 2 + 0.08, 0.1 * math.sin(math.tau * k / 24) + h / 2 - 0.08) for k in range(24)], 0.0, 0.03)
    b.build("cost", [m_pbr((0.05, 0.02, 0.08), rough=0.2, emit=(1.0, 0.55, 0.15), es=0.6)], parent=e)
    arc("cost_ring", 0.1, 0, 360, 0.008, m_emit((1.0, 0.7, 0.3), 3.0), loc=(-w / 2 + 0.08, h / 2 - 0.08, 0.035), parent=e, taper=False)
    return e


def spinner3d(root, rng, sp, mood_col, z=0.0):
    R = L.SPINNER_R_PX / L.PPU
    cx, cy = sp["center"]
    e = bpy.data.objects.new("spinner", None)
    link(e, root)
    e.location = P(cx, cy, z)
    b = MeshBuf()
    b.prism([(R * 1.1 * math.cos(math.tau * k / 96), R * 1.1 * math.sin(math.tau * k / 96)) for k in range(96)], -0.04, -0.01)
    b.build("spin_back", [m_pbr((0.02, 0.01, 0.04), rough=0.15, metal=0.6, emit=sp["color"], es=0.05, film=420)], parent=e)
    for a0, a1, kind, val in L.slice_geometry(sp):
        col = L.SLICE_COLORS[kind]
        g = 1.3
        pts = []
        n = max(4, int((a1 - a0) / 3))
        for k in range(n + 1):
            a = math.radians(a0 + g + (a1 - a0 - 2 * g) * k / n)
            pts.append((R * 0.95 * math.cos(a), R * 0.95 * math.sin(a)))
        for k in range(n, -1, -1):
            a = math.radians(a0 + g * 2 + (a1 - a0 - 4 * g) * k / n)
            pts.append((R * 0.33 * math.cos(a), R * 0.33 * math.sin(a)))
        b = MeshBuf()
        b.prism(pts, 0.0, 0.02)
        es = 0.35 if kind == "empty" else 0.95
        if kind == "empty":
            smat = m_pbr(tuple(c * 0.4 for c in col), rough=0.2, metal=0.2, emit=col, es=es, film=300)
        else:
            smat = m_screen([(0.0, tuple(c * 0.5 for c in col)), (0.45, col), (0.75, tuple(0.35 + 0.65 * c for c in col)), (1.0, col)], 0.95, scale=2.2)
        b.build("slice", [smat], parent=e)
        curve_obj("slice_edge", [(x, y, 0.025) for x, y in pts], 0.006,
                  m_emit(tuple(0.5 + 0.5 * c for c in col), 2.6 if kind != "empty" else 1.0), parent=e, cyclic=True)
    ticks = MeshBuf()
    for t in range(30):
        a = math.radians(90 - t * 12 - sp["rot_ticks"] * 12)
        ln = 0.09 if t % 5 == 0 else 0.045
        r = R * 1.0 + ln / 2
        ticks.box(r * math.cos(a), r * math.sin(a), 0.0, ln, 0.012, 0.02, rot=a)
    ticks.build("ticks", [m_emit((0.9, 0.9, 1.0), 2.5)], parent=e)
    arc("rim", R * 1.07, 0, 360, 0.014, m_emit(sp["color"], 3.2), parent=e, taper=False, loc=(0, 0, 0.01))
    # swirling rings of light around the wheel
    pal = [sp["color"], (1.0, 0.55, 0.15), (1.0, 0.25, 0.65), (0.6, 0.3, 1.0), sp["color"]]
    swirl(rng, "sw", (0, 0, -0.05), (0, 0, 0), R * 1.12, R * 1.5, 40, pal, 1.35 * mood_col,
          thick=(0.004, 0.022), parent=e, tilt=0.18, spiral=(-0.06, 0.1))
    # hub
    b = MeshBuf()
    b.prism([(R * 0.27 * math.cos(math.tau * k / 48), R * 0.27 * math.sin(math.tau * k / 48)) for k in range(48)], 0.0, 0.04)
    b.build("hub", [m_pbr((0.03, 0.02, 0.06), rough=0.1, metal=0.8, emit=sp["color"], es=0.3, film=500)], parent=e)
    arc("hub_ring", R * 0.2, 0, 360, 0.01, m_emit(sp["color"], 3.0), parent=e, taper=False, loc=(0, 0, 0.05))
    arc("hub_ring2", R * 0.12, 30, 300, 0.008, m_emit((1, 1, 1), 3.0), parent=e, loc=(0, 0, 0.05))
    # pointer: glowing shard at the top pointing into the wheel
    b = MeshBuf()
    ptr = [(0, R * 0.74), (R * 0.17, R * 1.24), (0, R * 1.13), (-R * 0.17, R * 1.24)]
    b.prism(ptr, 0.05, 0.1)
    b.build("pointer", [m_screen([(0, (1.0, 0.35, 0.05)), (0.5, (1.0, 0.7, 0.2)), (1, (1.0, 0.45, 0.1))], 1.0, scale=4.0)], parent=e)
    curve_obj("pointer_edge", [(x, y, 0.11) for x, y in ptr], 0.008, m_emit((1.0, 0.95, 0.85), 3.0), parent=e, cyclic=True)
    # health bar
    hw, hh = L.HPBAR["w"] / L.PPU, L.HPBAR["h"] / L.PPU
    hy = -L.HPBAR["dy"] / L.PPU
    b = MeshBuf()
    b.prism([(x, y + hy) for x, y in rrect(hw, hh, hh / 2)], -0.01, 0.0)
    b.build("hp_back", [m_pbr((0.02, 0.01, 0.04), rough=0.2, metal=0.5)], parent=e)
    frac = sp["hp"][0] / sp["hp"][1]
    fw = (hw - 0.04) * frac
    b = MeshBuf()
    b.prism([(x - (hw - 0.04) / 2 + fw / 2, y + hy) for x, y in rrect(fw, hh - 0.04, (hh - 0.04) / 2)], 0.0, 0.01)
    b.build("hp_fill", [m_screen([(0, tuple(0.6 * c for c in sp["color"])), (0.5, sp["color"]), (1, tuple(0.8 * c for c in sp["color"]))], 0.9, scale=3.0)], parent=e)
    curve_obj("hp_edge", [(x, y + hy, 0.012) for x, y in rrect(hw, hh, hh / 2)], 0.006, m_emit(sp["color"], 2.6), parent=e, cyclic=True)
    return e


def button3d(root, rng, cx, cy, w, h, col, col2, z=0.3):
    e = bpy.data.objects.new("btn", None)
    link(e, root)
    e.location = P(cx, cy, z)
    W, Hh = w / L.PPU, h / L.PPU
    b = MeshBuf()
    b.prism(rrect(W, Hh, Hh * 0.3), -0.02, 0.0)
    b.build("btn_body", [m_screen([(0, tuple(0.5 * c for c in col)), (0.5, col), (0.8, col2), (1, col)], 0.9, scale=1.2)], parent=e)
    curve_obj("btn_edge", [(x, y, 0.005) for x, y in rrect(W, Hh, Hh * 0.3)], 0.012, m_emit((1, 0.9, 0.8), 3.0), parent=e, cyclic=True)
    el = bpy.data.objects.new("bsw_el", None)
    link(el, e)
    el.scale = (1.0, 0.42, 1.0)
    swirl(rng, "bsw", (0, 0, -0.03), (0, 0, 0), W * 0.56, W * 0.68, 14, [col, (1, 0.8, 0.6), col2], 1.6,
          thick=(0.004, 0.01), parent=el, tilt=0.05)
    return e


# ---------------------------------------------------------------- shots
def shot_city(mood_key):
    M = C.MOODS[mood_key]
    cam = camera(L.CITY_CAM_LOC, L.CITY_CAM_TARGET, L.CITY_CAM_LENS)
    C.build_city(M)
    if mood_key == "day":
        sun((56, 0, 140), (1.0, 0.74, 0.55), 6.5, angle=3)
    else:
        sun((40, 0, 200), (0.5, 0.45, 1.0), 0.12 if mood_key == "night" else 0.08)
    if mood_key == "alarm":
        build_alarm(M)
    bpy.context.view_layer.update()
    anchors = {"nodes": {}}
    for n in L.NODES:
        x, y = L.node_world(n)
        anchors["nodes"][n[0]] = {"base": project(cam, (x, y, 0.2)), "top": project(cam, (x, y, 5.0 if n[0] != L.YOU_ARE_HERE else 13.0)),
                                  "label": n[2], "kind": n[3]}
    return anchors


def build_alarm(M):
    rng = random.Random(L.SEED + 7)
    targets = [(-22, 11), (0, 22), (-33, 44), (22, 44), (0, 55), (-11, 77), (30, 70), (-45, 30)]
    drone_mat = m_pbr((0.03, 0.03, 0.05), rough=0.3, metal=0.8)
    red, blue = m_emit((1.0, 0.05, 0.05), 8.0), m_emit((0.2, 0.4, 1.0), 8.0)
    for k, (tx, ty) in enumerate(targets):
        hx = tx + rng.uniform(-12, 12)
        hy = ty + rng.uniform(-2, 8)
        hz = rng.uniform(30, 44)
        spot_light((hx, hy, hz), (tx + rng.uniform(-3, 3), ty + rng.uniform(-3, 3), 0), (0.9, 0.95, 1.0),
                   rng.uniform(1200000, 1800000), rng.uniform(8, 11), blend=0.1, shadow=(k < 5))
        b = MeshBuf()
        if k % 3 == 1:   # helicopter: body, tail, rotor disc
            b.box(hx, hy, hz + 0.3, 1.6, 4.0, 1.4, bottom=True)
            b.box(hx, hy + 3.6, hz + 0.9, 0.3, 4.0, 0.4, bottom=True)
            b.build("heli", [drone_mat])
            rot = MeshBuf()
            rot.prism([(3.6 * math.cos(math.tau * i / 24), 3.6 * math.sin(math.tau * i / 24)) for i in range(24)], hz + 1.9, hz + 1.95,
                      xf=lambda p, hx=hx, hy=hy: (p[0] + hx, p[1] + hy, p[2]))
            rot.build("rotor", [m_emit((0.6, 0.6, 0.7), 0.25, additive=True)])
        else:            # quad drone
            b.box(hx, hy, hz + 0.3, 1.2, 1.2, 0.4, bottom=True)
            for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
                b.box(hx + dx * 0.9, hy + dy * 0.9, hz + 0.5, 0.8, 0.8, 0.05, bottom=True)
            b.build("drone", [drone_mat])
        lb = MeshBuf()
        lb.box(hx - 0.9, hy, hz + 0.5, 0.6, 0.6, 0.6, bottom=True)
        lb.build("blink", [red])
        lb = MeshBuf()
        lb.box(hx + 0.9, hy, hz + 0.5, 0.6, 0.6, 0.6, bottom=True)
        lb.build("blink", [blue])
        lamp = MeshBuf()
        lamp.box(hx, hy, hz - 0.1, 0.9, 0.9, 0.3, bottom=True)
        lamp.build("lamp", [m_emit((1.0, 1.0, 1.0), 12.0)])
        point_light((hx, hy, hz - 1), (1.0, 0.1, 0.1), 1500, radius=0.5)
    # red rotating beacons on roofs + alarm spill
    for k in range(18):
        x, y = rng.uniform(-60, 60), rng.uniform(0, 110)
        point_light((x, y, rng.uniform(6, 16)), (1.0, 0.06, 0.04), rng.uniform(900, 2200), radius=1.5)
    # warning rings around the boss HQ
    hq = next(n for n in L.NODES if n[3] == "boss")
    x, y = L.node_world(hq)
    for k in range(4):
        arc("warn", 5 + k * 2.2, 0, 360, 0.2, m_emit((1.0, 0.1, 0.08), 3.0), loc=(x, y, 3 + k * 3.0), taper=False)
    swirl(rng, "alarm_sw", (x, y, 8), (0, 0, 0), 5, 14, 24, [(1.0, 0.2, 0.1), (1.0, 0.6, 0.1)], 2.5, thick=(0.05, 0.2), tilt=0.15)


def shot_combat():
    M = C.MOODS["night"]
    cam = camera(L.CITY_CAM_LOC, L.CITY_CAM_TARGET, L.UI_LENS)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = L.UI_DIST
    cam.data.dof.aperture_fstop = 0.32
    rng = C.build_city(M, nav=False)
    sun((40, 0, 200), (0.5, 0.45, 1.0), 0.12)
    bpy.context.view_layer.update()
    root = ui_root(cam)
    veil = MeshBuf()
    veil.poly([(-12, -8, -4), (12, -8, -4), (12, 8, -4), (-12, 8, -4)])
    veil.build("veil", [m_veil((0.03, 0.005, 0.06), 0.5)], parent=root)
    urng = random.Random(L.SEED + 11)
    for key in ("player", "enemy"):
        spinner3d(root, urng, L.SPINNERS[key], 1.0, z=0.0)
    # centre clash swirl between the wheels
    swirl(urng, "clash", P(960, 430, -0.3), (0, 0, 0), 0.4, 1.1, 30,
          [(1, 1, 1), (1.0, 0.3, 0.7), (1.0, 0.6, 0.2), (0.3, 0.8, 1.0)], 2.0, thick=(0.004, 0.02), parent=root, tilt=0.5)
    for k, (name, cost, kind, text) in enumerate(L.HAND):
        (cx, cy), ang = L.hand_card(k)
        card3d(root, urng, cx, cy, ang, kind, z=0.03 + 0.004 * k)
    g = L.GO_BTN
    button3d(root, urng, g["center"][0], g["center"][1], g["w"], g["h"], (1.0, 0.32, 0.03), (1.0, 0.6, 0.1), z=0.03)
    # floating shards/fragments around the UI plane (some in front, blurred by DOF)
    sh = bpy.data.objects.new("uish", None)
    link(sh, root)
    C.build_shards(M, urng, region=((-6, 6), (-3.2, 3.2), (-3.0, -0.6)), n=26, nfrag=70, parent=sh, size=(0.06, 0.3))
    for (x, y, z) in ((-5.2, 2.4, 3.0), (5.0, 2.6, 2.5), (-5.5, -1.0, 2.2), (5.4, -0.2, 3.5)):
        C.build_shards(M, urng, region=((x - 0.4, x + 0.4), (y - 0.4, y + 0.4), (z, z + 0.3)), n=2, nfrag=3, parent=sh, size=(0.3, 0.6))
    point_light((0, 0, 3), (1.0, 0.4, 0.8), 60, radius=3, parent=root)
    return {}


def shot_shop():
    M = dict(C.MOODS["night"])
    M["win_str"] = 2.6
    M["neon"] = 1.3
    cam = camera((0.0, -30.0, 6.0), (0.0, 70.0, 16.0), L.UI_LENS)
    cam.data.dof.use_dof = True
    cam.data.dof.focus_distance = L.UI_DIST
    cam.data.dof.aperture_fstop = 0.3
    rng = C.build_city(M, caps_on=False, nav=False, tall_bias=1.6, j_range=range(0, 20))
    bpy.context.view_layer.update()
    root = ui_root(cam)
    veil = MeshBuf()
    veil.poly([(-12, -8, -3), (12, -8, -3), (12, 8, -3), (-12, 8, -3)])
    veil.build("veil", [m_veil((0.02, 0.0, 0.04), 0.38)], parent=root)
    urng = random.Random(L.SEED + 23)
    # sign with a swirling halo
    font = bpy.data.fonts.load(FONT_DIR + "AGENCYB.TTF")
    for dz, col, s, off in ((-0.02, (1.0, 0.2, 0.6), 1.2, (0, 0)),):
        cu = bpy.data.curves.new("sign", "FONT")
        cu.body = "BLACK MARKET"
        cu.font = font
        cu.size = 0.95
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.extrude = 0.02
        ob = bpy.data.objects.new("sign", cu)
        link(ob, root)
        ob.location = P(960 + off[0] * L.PPU, 128 - off[1] * L.PPU, 0.2 + dz)
        cu.materials.append(m_emit(col, s))
    swirl(urng, "signsw", P(960, 128, -0.2), (math.radians(80), 0, 0), 2.6, 3.6, 36,
          [(1.0, 0.3, 0.7), (1.0, 0.6, 0.2), (0.3, 0.8, 1.0)], 2.0, thick=(0.005, 0.02), parent=root, tilt=0.08)
    # glass counter along the bottom
    b = MeshBuf()
    x0, _ = L.px_to_ui(-100, 0)
    x1, _ = L.px_to_ui(2020, 0)
    _, ytop = L.px_to_ui(0, 800)
    _, ybot = L.px_to_ui(0, 1200)
    b.poly([(x0, ybot, -0.05), (x1, ybot, -0.05), (x1, ytop, -0.05), (x0, ytop, -0.05)])
    b.build("counter", [m_screen([(0, (0.01, 0.002, 0.02)), (0.5, (0.03, 0.005, 0.04)), (0.8, (0.012, 0.008, 0.035)), (1, (0.05, 0.01, 0.03))], 1.0, scale=0.9)], parent=root)
    for yy, cc in ((870, (1.0, 0.3, 0.7)), (960, (0.2, 0.7, 1.0))):
        _, yv = L.px_to_ui(0, yy)
        curve_obj("counter_strip", [(x0, yv, -0.04), (x1, yv, -0.04)], 0.004, m_emit(cc, 1.5), parent=root)
    curve_obj("counter_edge", [(x0, ytop, -0.04), (x1, ytop, -0.04)], 0.012, m_emit((1.0, 0.3, 0.7), 3.0), parent=root)
    for k, (name, kind, price, text) in enumerate(L.SHOP_CARDS):
        card3d(root, urng, L.SHOP_CARD_XS[k], L.SHOP_ROW_Y, (k - 1) * -2.0, kind, z=0.03)
    for k, (name, kind, price, text) in enumerate(L.SHOP_PARTS):
        part3d(root, urng, L.SHOP_PART_XS[k], L.SHOP_ROW_Y - 20, kind)
    for x in L.SHOP_CARD_XS + L.SHOP_PART_XS:   # display pedestals of light
        arc("ped", 0.55, 0, 360, 0.012, m_emit((1.0, 0.5, 0.2), 2.5), loc=P(x, 745, 0.0), rot=(math.radians(80), 0, 0), parent=root, taper=False)
        arc("ped2", 0.75, 200, 340, 0.008, m_emit((1.0, 0.3, 0.7), 2.0), loc=P(x, 752, 0.0), rot=(math.radians(80), 0, 0), parent=root)
    lb = L.LEAVE_BTN
    button3d(root, urng, lb["center"][0], lb["center"][1], lb["w"], lb["h"], (0.1, 0.5, 1.0), (0.6, 0.2, 1.0), z=0.03)
    sh = bpy.data.objects.new("uish", None)
    link(sh, root)
    C.build_shards(M, urng, region=((-6, 6), (-3.2, 3.2), (-3.0, -0.8)), n=24, nfrag=80, parent=sh, size=(0.06, 0.3))
    for (x, y, z) in ((-5.3, 2.2, 3.0), (5.2, 2.5, 2.5), (5.4, -1.8, 3.0)):
        C.build_shards(M, urng, region=((x - 0.4, x + 0.4), (y - 0.4, y + 0.4), (z, z + 0.3)), n=2, nfrag=3, parent=sh, size=(0.3, 0.6))
    point_light((0, 0, 3), (1.0, 0.4, 0.8), 80, radius=3, parent=root)
    return {}


def part3d(root, rng, cx, cy, kind):
    e = bpy.data.objects.new("part", None)
    link(e, root)
    e.location = P(cx, cy, 0.0)
    glass = lambda col, es: m_pbr(tuple(c * 0.4 for c in col), rough=0.1, metal=0.4, emit=col, es=es, film=480)
    if kind == "slice":
        col = L.SLICE_COLORS["atk"]
        R = 1.05
        pts = []
        for k in range(13):
            a = math.radians(60 + 60 * k / 12)
            pts.append((R * math.cos(a), R * math.sin(a) - 0.62))
        for k in range(12, -1, -1):
            a = math.radians(64 + 52 * k / 12)
            pts.append((0.3 * math.cos(a), 0.3 * math.sin(a) - 0.62))
        b = MeshBuf()
        b.prism(pts, -0.06, 0.06)
        ob = b.build("p_slice", [glass(col, 1.0)], parent=e)
        ob.rotation_euler = (math.radians(-18), math.radians(22), math.radians(-8))
        curve_obj("p_edge", [(x, y, 0.065) for x, y in pts], 0.008, m_emit((1, 0.6, 0.8), 3.0), parent=ob, cyclic=True)
        swirl(rng, "psw", (0, -0.1, 0), (0.3, 0.2, 0), 0.7, 1.0, 16, [(1, 1, 1), col, (1.0, 0.6, 0.2)], 2.2, thick=(0.003, 0.01), parent=e, tilt=0.4)
    elif kind == "rim":
        ob = bpy.data.objects.new("rimgrp", None)
        link(ob, e)
        ob.rotation_euler = (math.radians(58), math.radians(-12), 0)
        arc("rim_main", 0.62, 0, 360, 0.05, m_pbr((0.5, 0.5, 0.6), rough=0.08, metal=1.0, film=520), parent=ob, taper=False)
        arc("rim_glow", 0.69, 0, 360, 0.01, m_emit((0.2, 0.85, 1.0), 3.0), parent=ob, taper=False)
        t = MeshBuf()
        for k in range(30):
            a = math.tau * k / 30
            ln = 0.09 if k % 5 == 0 else 0.05
            t.box(0.54 * math.cos(a), 0.54 * math.sin(a), -0.01, ln, 0.012, 0.02, rot=a)
        t.build("rim_ticks", [m_emit((0.8, 0.95, 1.0), 2.5)], parent=ob)
        swirl(rng, "rsw", (0, 0, 0), (0, 0, 0), 0.75, 1.0, 16, [(1, 1, 1), (0.2, 0.85, 1.0), (0.6, 0.3, 1.0)], 2.2, thick=(0.003, 0.01), parent=ob, tilt=0.2)
    else:
        col = (0.15, 0.75, 1.0)
        b = MeshBuf()
        pts = [(0, -0.75), (0.32, 0.55), (0, 0.38), (-0.32, 0.55)]
        b.prism(pts, -0.07, 0.07)
        ob = b.build("p_ptr", [glass(col, 0.9)], parent=e)
        ob.rotation_euler = (math.radians(15), math.radians(-30), math.radians(10))
        curve_obj("ptr_edge", [(x, y, 0.075) for x, y in pts], 0.008, m_emit((1.0, 1.0, 1.0), 3.0), parent=ob, cyclic=True)
        swirl(rng, "gsw", (0, 0, 0), (0.2, -0.3, 0), 0.6, 0.95, 18, [(1, 1, 1), col, (0.8, 0.4, 1.0)], 2.2, thick=(0.003, 0.01), parent=e, tilt=0.4)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    shot, out = argv[0], argv[1]
    samples = int(argv[2]) if len(argv) > 2 else 64
    clear()
    setup_render(samples=samples, bloom=(0.95, 0.55, 0.7))
    if shot == "city_day":
        anchors = shot_city("day")
    elif shot == "city_night":
        anchors = shot_city("night")
    elif shot == "city_suspicion":
        anchors = shot_city("alarm")
    elif shot == "combat":
        anchors = shot_combat()
    elif shot == "shop":
        anchors = shot_shop()
    else:
        raise SystemExit("unknown shot " + shot)
    bpy.context.scene.render.filepath = out
    bpy.ops.render.render(write_still=True)
    with open(out + ".json", "w") as f:
        json.dump(anchors, f, indent=1)
    print("DONE", out)


main()
