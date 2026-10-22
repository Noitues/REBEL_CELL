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
import rat_statue as RS  # noqa: E402

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
        mx.inputs[7].default_value = (0.02, 0.022, 0.025, 1.0)
        mx.inputs[6].default_value = tuple(base) + (1.0,)
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


def refine_stone(mat, lift=0.0):
    """v2: per-block tone variation, pitting and clearer joints on the engine's civic material (the landmark stone)."""
    nt = mat.node_tree
    bsdf = [n for n in nt.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"][0]
    br = [n for n in nt.nodes if n.bl_idname == "ShaderNodeTexBrick"][0]
    br.inputs["Color1"].default_value = (0.74 + lift, 0.74 + lift, 0.72 + lift, 1.0)
    br.inputs["Color2"].default_value = (1.0, 1.0, 1.0, 1.0)
    br.inputs["Mortar"].default_value = (0.40, 0.40, 0.40, 1.0)
    br.inputs["Mortar Size"].default_value = 0.05
    br.inputs["Brick Width"].default_value = 4.8
    br.inputs["Row Height"].default_value = 1.9
    src = bsdf.inputs["Base Color"].links[0].from_socket
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "MULTIPLY"
    nt.links.new(src, mul.inputs[0])
    nt.links.new(br.outputs["Color"], mul.inputs[1])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 2.6
    nz.inputs["Detail"].default_value = 9.0
    nz.inputs["Roughness"].default_value = 0.7
    nt.links.new(geo.outputs["Position"], nz.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeMapRange")
    ramp.inputs["From Min"].default_value, ramp.inputs["From Max"].default_value = 0.35, 0.62
    ramp.inputs["To Min"].default_value, ramp.inputs["To Max"].default_value = 0.70 + lift, 1.0           # pits are darker
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Value"])
    sc2 = nt.nodes.new("ShaderNodeVectorMath")
    sc2.operation = "SCALE"
    nt.links.new(mul.outputs[0], sc2.inputs[0])
    nt.links.new(ramp.outputs[0], sc2.inputs["Scale"])
    nt.links.new(sc2.outputs[0], bsdf.inputs["Base Color"])
    bump = [n for n in nt.nodes if n.bl_idname == "ShaderNodeBump"]
    if bump:
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        old = bump[0].inputs["Height"].links[0].from_socket if bump[0].inputs["Height"].is_linked else None
        if old is not None:
            nt.links.new(old, add.inputs[0])
        nz2 = nt.nodes.new("ShaderNodeTexNoise")
        nz2.inputs["Scale"].default_value = 7.0
        nz2.inputs["Detail"].default_value = 6.0
        nt.links.new(geo.outputs["Position"], nz2.inputs["Vector"])
        nt.links.new(nz2.outputs["Fac"], add.inputs[1])
        nt.links.new(add.outputs[0], bump[0].inputs["Height"])
        bump[0].inputs["Strength"].default_value = 0.55


def v2_scene(g, cfg, ST, PL, PO, VG, coll, px, py, sx, sy):
    """v2: 12 slender classical figures (4 on the tower tops, 4 on the attic front/back, 4 on plinths in the piazza), stone paving in
    the arena, axis lines that reach into frame, a key light for the white drum."""
    import bpy
    refine_stone(g["M_CIVIC"], float(cfg.get("stone_lift", 0.0)))
    if cfg.get("matte"):            # v3: less coat, so the stone reads white instead of reflecting the dark sky
        for b_ in [n for n in g["M_CIVIC"].node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"]:
            b_.inputs["Coat Weight"].default_value = float(cfg["matte"][0])
            b_.inputs["Specular IOR Level"].default_value = float(cfg["matte"][1])
    zt = (3 * 5.0 + 3.0) * KS
    ar, br_ = (31.0 + 0.75) * KS, (31.0 * 0.8 + 0.75) * KS
    kinds = ["athlete", "draped", "athlete", "draped"]
    # 4 on the towers: tall, facing outward
    for k_ in range(4):
        t_ = math.radians(45 + 90 * k_)
        cx, cy = (31.0 + 3.5) * math.cos(t_) * KS, (31.0 * 0.8 + 3.5) * math.sin(t_) * KS
        zc = 32.4 * KS
        ST.box(cx - 5.2, cy - 5.2, zc, cx + 5.2, cy + 5.2, zc + 1.2)
        ST.box(cx - 4.0, cy - 4.0, zc + 1.2, cx + 4.0, cy + 4.0, zc + 4.2)
        RS.statue(ST, (cx, cy, zc + 4.2), cfg.get("top_h", 46.0), math.atan2(cy, cx), kinds[k_], pose=k_)
    # 8 figures on the attic parapet (4 front, 4 back), facing outward
    for k_, deg in enumerate((212, 250, 290, 328, 32, 70, 110, 148)):
        t_ = math.radians(deg)
        ex, ey = ar * math.cos(t_), br_ * math.sin(t_)
        nx, ny = math.cos(t_), math.sin(t_) / 0.8
        f = math.atan2(ny, nx)
        ST.box(ex - 2.6, ey - 2.6, zt, ex + 2.6, ey + 2.6, zt + 0.8)
        ST.box(ex - 1.9, ey - 1.9, zt + 0.8, ex + 1.9, ey + 1.9, zt + 3.0)
        RS.statue(ST, (ex, ey, zt + 3.0), cfg.get("attic_h", 22.0), f, kinds[k_ % 4], pose=k_ + 1)
    # 2 pairs on plinths in the piazza, flanking the entry axis (the Dioscuri idea)
    ppos = cfg.get("plaza_pos", ((-16.0, -26.5, -math.pi / 2), (16.0, -26.5, -math.pi / 2), (-16.0, 27.0, math.pi / 2), (16.0, 27.0, math.pi / 2)))
    if cfg.get("flank"):                         # v4: the front pair flanks the entry portal and faces outward
        import aurelian_landmark as _AL
        te = math.radians(_AL.ENTRY_T)
        ppos = []
        for dt in (-cfg.get("flank_dt", 0.21), cfg.get("flank_dt", 0.21)):
            t_ = te + dt
            r_ = 31.0 + 3.8
            nrm = math.atan2(math.sin(t_) / 0.8, math.cos(t_))
            ppos.append((r_ * math.cos(t_), 0.8 * r_ * math.sin(t_), nrm - math.pi))
        ppos += [(-16.0, 27.0, math.pi / 2), (16.0, 27.0, math.pi / 2)]
    for k_, (cx, cy, f) in enumerate(ppos):
        cx, cy = cx * KS, cy * KS
        ST.box(cx - 7.5, cy - 7.5, 0.18, cx + 7.5, cy + 7.5, 1.8)
        ST.box(cx - 6.0, cy - 6.0, 1.8, cx + 6.0, cy + 6.0, 3.4)
        ST.box(cx - 4.6, cy - 4.6, 3.4, cx + 4.6, cy + 4.6, 17.0)
        ST.box(cx - 5.4, cy - 5.4, 17.0, cx + 5.4, cy + 5.4, 18.0)
        PO.box(cx - 4.7, cy - 4.7, 17.0, cx + 4.7, cy + 4.7, 17.3)
        RS.statue(ST, (cx, cy, 18.0), cfg.get("plaza_h", 36.0), -f if False else f + math.pi, kinds[(k_ + 1) % 4], pose=k_ + 2)
    # axes: two wide paired verdigris lines running from the stylobate toward the camera and away
    for sgn in (-1, 1):
        for off in (0.0, 1.4):
            VG.box(sgn * 62.0 + off - 0.12, -py, 0.18, sgn * 62.0 + off + 0.12, -sy + 4.0, 0.26)
            VG.box(sgn * 62.0 + off - 0.12, sy - 4.0, 0.18, sgn * 62.0 + off + 0.12, py, 0.26)
    # stone paving for the arena (joint grid, matt), a ring of border stones
    paving = marble("rat_paving", cfg.get("paving", (0.60, 0.63, 0.64)), 0.55, 0.10, joints=3.0)
    PV = D.DAcc("rat_paving", paving, coll, 1)
    rr = 14.9 * KS
    n = 72
    zf = 2.9 * KS
    ring = [(rr * math.cos(2 * math.pi * j / n), rr * 0.8 * math.sin(2 * math.pi * j / n), zf) for j in range(n)]
    PV.face(list(reversed(ring)))
    pvo = PV.build()
    print('[rat] paving', len(pvo.data.polygons), [round(v.co.z, 2) for v in pvo.data.vertices][:3], pvo.hide_render, pvo.data.materials[0].name, flush=True)
    # a cold key on the white drum, from the camera side, light-linked with the rest
    add = g["add_light"]
    lo = add("rat_drum", "SPOT", (0.0, -70.0, 120.0), cfg.get("drum_w", 40000.0), (0.78, 0.9, 1.0), aim=(0.0, 0.0, 26.0), size=4.0, spot=22.0,
             blend=0.6, group="corp", shadow=False)
    la = add("rat_arena", "SPOT", (0.0, -60.0, 300.0), cfg.get("arena_w", 160000.0), (0.78, 0.9, 1.0), aim=(0.0, 0.0, 10.0), size=8.0, spot=cfg.get("arena_cone", 52.0),
             blend=0.7, group="corp", shadow=False)
    lights = [lo, la]
    if cfg.get("fill_w"):                       # v3: a big soft cold area fill from the camera side so the white risers read white
        lf = add("rat_fill", "AREA", (0.0, -200.0, 230.0), cfg["fill_w"], (0.80, 0.90, 1.0), aim=(0.0, 20.0, 10.0), size=160.0, size_y=100.0,
                 group="corp", shadow=False)
        lights.append(lf)
    cfg["_drum"] = tuple(lights)


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
    SY = ST
    if cfg.get("sty_dark"):                     # v3: a darker stylobate so the landmark keeps the top of the value hierarchy
        SY = D.DAcc("rat_sty", marble("rat_sty", tuple(cfg["sty_dark"]), 0.35, 0.3, joints=6.0), coll, 1)
    for i in range(3):
        d = i * 4.0
        SY.box(-(sx - d), -(sy - d), 0.18 + i * 0.45, sx - d, sy - d, 0.18 + (i + 1) * 0.45)
    if SY is not ST:
        cfg["_sy"] = SY
    if cfg.get("v2"):
        v2_scene(g, cfg, ST, PL, PO, VG, coll, px, py, sx, sy)
    else:
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
    for a in (ST, PL, PO, VG) + ((cfg["_sy"],) if cfg.get("_sy") is not None else ()):
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
    el, az = math.radians(cfg.get("moon_el", 15.0)), math.radians(cfg.get("moon_az", 248.0))   # light comes FROM (az, el)
    d = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    if cfg.get("nolink"):
        # no light linking (it hung the GPU once): a far SPOT with a narrow cone stands in for the sun, so only the lot is lit
        dist = 900.0
        sun = bpy.data.lights.new("rat_moon", "SPOT")
        sun.energy = cfg.get("moon", 3.0) * 4.0 * math.pi * math.pi * dist * dist * cfg.get("spot_k", 1.0)
        sun.color = tuple(cfg.get("moon_col", (0.70, 0.84, 1.0)))
        sun.shadow_soft_size = dist * math.tan(math.radians(cfg.get("moon_soft", 1.8)))
        sun.spot_size = math.radians(cfg.get("moon_cone", 24.0))
        sun.spot_blend = 0.08
        so = bpy.data.objects.new("rat_moon", sun)
        sc.collection.objects.link(so)
        so.location = tuple(Vector((0.0, 0.0, 40.0)) + d * dist)
        so.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    else:
        sun = bpy.data.lights.new("rat_moon", "SUN")
        sun.energy = cfg.get("moon", 3.0)
        sun.color = tuple(cfg.get("moon_col", (0.70, 0.84, 1.0)))
        sun.angle = math.radians(cfg.get("moon_soft", 1.8))
        so = bpy.data.objects.new("rat_moon", sun)
        sc.collection.objects.link(so)
        so.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        so.light_linking.receiver_collection = rx
    for ob_ in (so,):
        try:
            ob_.visible_camera = False
        except AttributeError:
            pass
    if cfg.get("_drum") is not None:
        for lo_ in ([] if cfg.get("nolink") else cfg["_drum"]):
            try:
                lo_.light_linking.receiver_collection = rx
            except AttributeError:
                pass
    if cfg.get("no_vol"):                    # v3: the landmark lights do not scatter in the fog (they would lift the whole frame's median)
        for o_ in [so] + list(cfg.get("_drum") or ()):
            try:
                o_.visible_volume_scatter = False
            except AttributeError:
                pass
    print("[rat] style applied; objects", len(coll.objects), flush=True)
