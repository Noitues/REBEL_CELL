"""Rationalist Rome look, Blender side. Called from rat_blender.py in front of the render section of hq_scene.py (globals g).
Cold dark city, cold light colours, verdigris fog tint, a low raking moon (shadows + god rays) linked to the landmark only,
a travertine piazza with a stepped stylobate, a ring of white marble athletes on the attic (Stadio dei Marmi), colossal
statues on tall plinths (Palazzo della Civilta Italiana's Dioscuri / de Chirico). Kit units: city units x KS."""
import math
import os
import random
import sys

import bpy
from mathutils import Vector

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "art_deco", "scripts")))
sys.dont_write_bytecode = True
import deco_restyle as D  # noqa: E402

KS = 1.0 / 0.2375


def marble(name, base, rough=0.38, coat=0.4, joints=None):
    m = D.principled(name, base, 0.0, rough, coat=coat, coat_rough=0.08)
    if joints:
        nt = m.node_tree
        b = [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"][0]
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sp = nt.nodes.new("ShaderNodeSeparateXYZ")
        nt.links.new(geo.outputs["Position"], sp.inputs[0])
        cx = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(sp.outputs["X"], cx.inputs[0])
        nt.links.new(sp.outputs["Y"], cx.inputs[1])
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.inputs["Scale"].default_value = 1.0
        br.inputs["Mortar Size"].default_value = 0.03
        br.inputs["Bias"].default_value = 0.0
        br.inputs["Brick Width"].default_value = joints
        br.inputs["Row Height"].default_value = joints
        br.offset = 0.0
        nt.links.new(cx.outputs[0], br.inputs["Vector"])
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        nt.links.new(br.outputs["Fac"], mx.inputs[0])
        mx.inputs[6].default_value = (0.01, 0.012, 0.014, 1.0)
        mx.inputs[7].default_value = tuple(base) + (1.0,)
        nt.links.new(mx.outputs[2], b.inputs["Base Color"])
    return m


def figure(acc, x, y, z0, H, rot=0.0, arm=True):
    """A blocky standing athlete / colossus facing +y (rotated by rot about z): legs, torso, shoulders, head, raised arm."""
    c, s = math.cos(rot), math.sin(rot)

    def B(x0, y0, z0_, x1, y1, z1_):
        pts = []
        for (px, py) in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            pts.append((x + px * c - py * s, y + px * s + py * c))
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        acc.box(min(xs), min(ys), z0 + z0_, max(xs), max(ys), z0 + z1_)
    u = H / 10.0
    B(-0.9 * u, -0.5 * u, 0, -0.1 * u, 0.5 * u, 4.6 * u)
    B(0.1 * u, -0.5 * u, 0, 0.9 * u, 0.5 * u, 4.6 * u)
    B(-1.0 * u, -0.6 * u, 4.6 * u, 1.0 * u, 0.6 * u, 6.0 * u)           # hips and robe
    B(-1.3 * u, -0.7 * u, 6.0 * u, 1.3 * u, 0.7 * u, 8.3 * u)           # torso and shoulders
    B(-0.5 * u, -0.5 * u, 8.3 * u, 0.5 * u, 0.5 * u, 9.6 * u)           # head
    if arm:
        B(1.3 * u, -0.3 * u, 7.0 * u, 1.9 * u, 0.3 * u, 10.0 * u)       # the raised arm


def apply(g, cfg):
    sc = bpy.context.scene
    coll = bpy.data.collections.new("rationalist")
    sc.collection.children.link(coll)
    OBJ, add = g["OBJ"], g["add_light"]
    # 1. the city: dark, cool, windows cold white
    ct = tuple(cfg.get("city_line", (0.20, 0.27, 0.32)))
    D.lacquer_facade(g["M_CITY"], gold=ct, dark=cfg.get("city_dark", 0.10), window_tint=tuple(cfg.get("win_tint", (0.55, 0.85, 1.0))),
                     win_boost=cfg.get("win_boost", 0.9), band_emit=0.05, mull_w=0.04)
    D.lacquer_panels(g["M_CIVIC"], gold=(0.7, 0.75, 0.78), dark=1.0, seam_gold=0.0) if cfg.get("civic_panels") else None
    for k in ("city_sign",):
        if OBJ.get(k) is not None:
            OBJ[k].hide_render = True
    cool = tuple(cfg.get("neon_cool", (0.25, 0.55, 1.0)))
    if OBJ.get("city_neon") is not None:
        D.recolor_attr(OBJ["city_neon"], lambda c: tuple(v * 0.8 for v in (cool if (c[0] > c[2]) else c)))
    # 2. fog: a cold tint with a little verdigris
    D.tune_fog(g, dict(fog_col=tuple(cfg.get("fog_col", (0.60, 0.72, 0.78))), fog_aniso=cfg.get("fog_aniso", 0.5)))
    # 3. every warm light goes cold (the base keeps the energies)
    for ob, e0, grp in g["LIGHTS"]:
        c = ob.data.color
        if c[0] > c[2] * 1.05:
            ob.data.color = (0.55, 0.78, 1.0) if grp != "corp" else (0.50, 0.85, 0.95)
        if ob.name.startswith(("cityglow_", "bankglow_")):
            ob.data.color = tuple(cfg.get("glow_col", (0.30, 0.55, 0.95)))
    # 4. materials and receivers
    stone = marble("rat_stone", cfg.get("stone", (0.62, 0.66, 0.68)), 0.42, 0.25)
    plaza_m = marble("rat_plaza", cfg.get("plaza", (0.20, 0.22, 0.25)), 0.16, 0.9, joints=cfg.get("joint", 9.0))
    porph = marble("rat_porphyry", (0.045, 0.011, 0.024), 0.18, 0.8)
    ST = D.DAcc("rat_stone", stone, coll, 1)
    PL = D.DAcc("rat_plaza", plaza_m, coll, 1)
    PO = D.DAcc("rat_porph", porph, coll, 1)
    VG = D.DAcc("rat_verd", D.emission("rat_verd", cfg.get("verd", (0.02, 0.85, 0.45)), cfg.get("verd_k", 3.0)), coll, 1)
    # the piazza: a pale slab with a stone joint grid, and a stepped stylobate under the colosseum (three wide steps)
    px, py = cfg.get("plaza_half", (146.0, 142.0))
    PL.box(-px, -py, 0.0, px, py, 0.18)
    sx, sy = cfg.get("sty_half", (31.0 * KS + 14.0, 25.0 * KS + 8.0))
    for i in range(3):
        d = i * 4.0
        ST.box(-(sx - d), -(sy - d), 0.18 + i * 0.45, sx - d, sy - d, 0.18 + (i + 1) * 0.45)
    # 5. statues: a ring of white athletes on the attic parapet (Stadio dei Marmi: 60, ~4 m), and four colossi on tall plinths
    n_ath = int(cfg.get("n_athletes", 60))
    a_r, zt = (31.0 + 0.45) * KS, (3 * 5.0 + 3.0) * KS
    for k in range(n_ath):
        t = 2 * math.pi * (k + 0.5) / n_ath
        ex, ey = a_r * math.cos(t), a_r * 0.8 * math.sin(t)
        nx, ny = math.cos(t) / 1.0, math.sin(t) / 0.8
        rot = math.atan2(ny, nx) - math.pi / 2
        ST.box(ex - 1.3, ey - 1.3, zt, ex + 1.3, ey + 1.3, zt + 1.6)
        figure(ST, ex, ey, zt + 1.6, cfg.get("ath_h", 9.0), rot, arm=False)
    col_h = cfg.get("colossus_h", 34.0)
    for (cx, cy, rot) in cfg.get("colossi", ((-14.0, -29.5, 0.0), (14.0, -29.5, 0.0), (-14.0, 29.5, math.pi), (14.0, 29.5, math.pi))):
        cx, cy = cx * KS, cy * KS
        hs = 5.0
        for i, (w, h) in enumerate(((hs * 1.5, 1.2), (hs * 1.25, 1.2), (hs, 10.0))):
            z_ = 0.18 + sum(q[1] for q in ((hs * 1.5, 1.2), (hs * 1.25, 1.2), (hs, 10.0))[:i])
            ST.box(cx - w, cy - w, z_, cx + w, cy + w, z_ + h)
        PO.box(cx - hs * 1.05, cy - hs * 1.05, 13.6, cx + hs * 1.05, cy + hs * 1.05, 14.4)
        figure(ST, cx, cy, 14.4, col_h, rot, arm=True)
        VG.box(cx - 0.2, cy - hs - 0.05, 3.0, cx + 0.2, cy - hs + 0.1, 12.0)
    # the EUR axes: two long parallel verdigris lines running out from the stylobate along the piazza (rigid symmetry)
    for sgn in (-1, 1):
        VG.box(sgn * 30.0 - 0.25, -py, 0.18, sgn * 30.0 + 0.25, -sy - 1.0, 0.30)
        VG.box(sgn * 30.0 - 0.25, sy + 1.0, 0.18, sgn * 30.0 + 0.25, py, 0.30)
    # colossi on the four campanile shafts (the shafts are their plinths; they read against the sky, de Chirico's silhouettes)
    for k_ in range(4):
        t_ = math.radians(45 + 90 * k_)
        cx, cy = (31.0 + 3.5) * math.cos(t_) * KS, (31.0 * 0.8 + 3.5) * math.sin(t_) * KS
        zc = 32.4 * KS
        ST.box(cx - 5.0, cy - 5.0, zc, cx + 5.0, cy + 5.0, zc + 3.0)
        figure(ST, cx, cy, zc + 3.0, cfg.get("top_h", 44.0), math.atan2(cy, cx) - math.pi / 2, arm=False)
    for a in (ST, PL, PO, VG):
        a.build()
    # 6. the low raking moon, linked to the landmark, the piazza and the statues only (the city stays dark)
    rx = bpy.data.collections.new("rat_rx")
    for ob in list(OBJ.values()):
        if ob is not None and any(c.name in ("compound", "rooms") for c in ob.users_collection):
            rx.objects.link(ob)
    for o in coll.objects:
        rx.objects.link(o)
    for k_ in ("city", "city_metal", "city_neon", "city_sign", "city_small"):      # the city does not shadow the moon (it lights the lot only)
        if OBJ.get(k_) is not None:
            OBJ[k_].visible_shadow = False
    sun = bpy.data.lights.new("rat_moon", "SUN")
    sun.energy = cfg.get("moon", 3.0)
    sun.color = tuple(cfg.get("moon_col", (0.70, 0.84, 1.0)))
    sun.angle = math.radians(cfg.get("moon_soft", 1.8))
    so = bpy.data.objects.new("rat_moon", sun)
    sc.collection.objects.link(so)
    el, az = math.radians(cfg.get("moon_el", 15.0)), math.radians(cfg.get("moon_az", 248.0))   # light comes FROM (az, el)
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    so.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    so.light_linking.receiver_collection = rx
    for ob_ in (so,):
        try:
            ob_.visible_camera = False
        except AttributeError:
            pass
    print("[rat] style applied; objects", len(coll.objects), flush=True)
