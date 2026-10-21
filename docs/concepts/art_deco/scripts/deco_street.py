"""Art-deco restyle of the Netrun street panel (street_r2, decision camera). Imported inside Blender by deco_blender_street.py.

patch_cycles   inserts apply_street() in front of the frame loop of r2_cycles.py (and switches to CPU for previews)
apply_street   facade materials -> black lacquer + gold bands (the grid fades with distance), windows toward gold;
               every street frontage face gets gold piers that run past the roofline, parallel vertical neon, a gold
               cornice with a chevron band and triple-line neon, and 3 setback tiers with a spire / fan crown;
               floods on the frontage go gold; charcoal fog
"""
import json
import math
import os
import random

import bpy
from mathutils import Vector

import deco_restyle as D

CFG = json.loads(os.environ.get("DECO_CFG", "{}"))


def patch_cycles(src):
    key = "for fr in OCJ[\"frames\"]:\n"
    assert key in src
    src = src.replace(key, "import deco_street as _DSS\n_DSS.apply_street(globals())\n" + key, 1)
    if os.environ.get("DECO_CPU"):
        k2 = 'cy.device = "GPU"'
        assert k2 in src
        src = src.replace(k2, 'cy.device = "CPU"', 1)
    k3 = 'vs.inputs["Color"].default_value = tuple(LKA.get("scatter", (0.85, 0.80, 1.0))) + (1,)'
    if k3 in src and "fog_col" in CFG:
        src = src.replace(k3, 'vs.inputs["Color"].default_value = tuple(%r) + (1,)' % (tuple(CFG["fog_col"]),), 1)
    return src


def _norm(c, k=1.0):
    m = max(c) or 1.0
    return tuple(min(1.0, x / m) * k for x in c)


def face_deco(ctx, ff, rng, hue_mode="face"):
    """One street frontage face becomes a deco building front: an opaque black-lacquer skin over the old facade, fluted
    gold piers that run past the roofline, solid gold spandrel bands with a chevron row, lit windows, a stepped
    parapet, three setback tiers (80 %) with piers and thin parallel neon, and a fan crown or spire on top."""
    G, L, N, N2, W = ctx["gold"], ctx["lac"], ctx["neon"], ctx["neon2"], ctx["win"]
    u0, u1, face, out, top = ff["u0"], ff["u1"], ff["face"], ff["out"], ff["top"]
    w = u1 - u0
    fz0 = CFG.get("pier_z0", 2.4)
    sk = 0.10                                              # the skin stands this far off the old facade

    def yb(d0, d1):
        a, b = face + out * d0, face + out * d1
        return min(a, b), max(a, b)
    ya, yb_ = yb(0.04, 0.04 + sk)
    L.box(u0, ya, fz0, u1, yb_, top)                       # the lacquer skin (opaque)
    # fluted piers: three thin ribs per pier, gold, running past the roofline
    n = max(2, int(round(w / CFG.get("pier_pitch", 3.2))))
    over = CFG.get("pier_over", 3.2)
    for i in range(n + 1):
        u = u0 + w * i / n
        y0, y1 = yb(0.04, 0.04 + sk + 0.30)
        for du in (-0.18, 0.0, 0.18):
            G.box(u + du - 0.07, y0, fz0, u + du + 0.07, y1, top + over)
        if 0 < i < n:
            y0, y1 = yb(0.04 + sk, 0.04 + sk + 0.14)
            for du in (-0.36, -0.52):
                N.box(u + du - 0.035, y0, fz0 + 0.5, u + du + 0.035, y1, top - 0.5)
    # spandrels: a solid gold band every 4 floors (1.9 BU a floor), thin neon pair above it
    fl = 1.9
    z = fz0 + 4 * fl
    while z < top - 2.0:
        y0, y1 = yb(0.04 + sk, 0.04 + sk + 0.22)
        G.box(u0, y0, z, u1, y1, z + 0.30)
        for dz in (0.5, 0.72):
            y0, y1 = yb(0.04 + sk, 0.04 + sk + 0.12)
            N.box(u0 + 0.1, y0, z + dz, u1 - 0.1, y1, z + dz + 0.05)
        z += 4 * fl
    # chevrons only on a lacquer panel under the cornice (solid, on the skin)
    D.chevron_band(G, (u0, face + out * (0.04 + sk), 0.0), (1, 0, 0), (0, 0, 1), (0, out, 0), int(w / 2.0) + 1, top - 3.0, 1.3, 0.34, 0.2)
    # windows: dark glass in a gold frame with depth (the frame stands proud, so the glass reads inset); ~40 % lit in a
    # range of warm tones and brightnesses, some with blinds (dark slats across the lit pane)
    wz = fz0 + 0.9
    while wz < top - 3.4:
        bay = u0 + 0.9
        while bay < u1 - 0.9:
            ww, wh = 0.62, 1.05
            y0, y1 = yb(0.04 + sk, 0.04 + sk + 0.025)
            if rng.random() < CFG.get("win_p", 0.5):
                tone = rng.choice(ctx["wtones"])
                tone.box(bay - ww / 2, y0, wz, bay + ww / 2, y1, wz + wh)
                if rng.random() < 0.3:
                    for k in range(4):
                        ctx["glass"].box(bay - ww / 2, y0, wz + 0.1 + k * 0.25, bay + ww / 2, yb(0.04 + sk, 0.04 + sk + 0.04)[1], wz + 0.19 + k * 0.25)
            else:
                ctx["glass"].box(bay - ww / 2, y0, wz, bay + ww / 2, y1, wz + wh)
            f0, f1 = yb(0.04 + sk, 0.04 + sk + 0.15)
            ft = 0.05
            G.box(bay - ww / 2 - ft, f0, wz - ft, bay + ww / 2 + ft, f1, wz)
            G.box(bay - ww / 2 - ft, f0, wz + wh, bay + ww / 2 + ft, f1, wz + wh + ft)
            G.box(bay - ww / 2 - ft, f0, wz, bay - ww / 2, f1, wz + wh)
            G.box(bay + ww / 2, f0, wz, bay + ww / 2 + ft, f1, wz + wh)
            G.box(bay - 0.012, f0, wz, bay + 0.012, f1, wz + wh)
            bay += 1.5
        wz += fl
    # ground floor (v2): warm lit shop glass between the piers, gold sills, a marquee canopy with a bulb row
    for i in range(n):
        ua, ub = u0 + w * i / n + 0.35, u0 + w * (i + 1) / n - 0.35
        y0, y1 = yb(0.04 + sk, 0.04 + sk + 0.03)
        t = rng.choice(ctx["wtones"][:3])
        t.box(ua, y0, 0.45, ub, y1, fz0 - 0.55)
        f0, f1 = yb(0.04 + sk, 0.04 + sk + 0.14)
        G.box(ua - 0.06, f0, 0.35, ub + 0.06, f1, 0.45)
        G.box(ua - 0.06, f0, fz0 - 0.55, ub + 0.06, f1, fz0 - 0.45)
    cy0, cy1 = yb(0.04, 1.1)
    G.box(u0, cy0, fz0 - 0.45, u1, cy1, fz0 - 0.2)
    b0, b1 = yb(1.0, 1.14)
    nb = max(3, int(w / 0.55))
    for k in range(nb):
        bu = u0 + (k + 0.5) * w / nb
        ctx["bulb"].box(bu - 0.07, b0, fz0 - 0.62, bu + 0.07, b1, fz0 - 0.46)
    # cornice + stepped parapet
    y0, y1 = yb(0.04, 0.04 + sk + 0.7)
    G.box(u0 - 0.2, y0, top - 0.2, u1 + 0.2, y1, top + 0.25)
    for k in range(3):
        y0, y1 = yb(0.04 + sk + 0.5, 0.04 + sk + 0.64)
        N.box(u0, y0, top - 0.75 - k * 0.3, u1, y1, top - 0.68 - k * 0.3)
    nm = max(2, int(w / 1.6))
    for k in range(nm):
        uu = u0 + (k + 0.5) * w / nm
        hh = 0.5 + 0.35 * (k % 2)
        y0, y1 = yb(0.2, 0.7)
        G.box(uu - 0.3, y0, top + 0.25, uu + 0.3, y1, top + 0.25 + hh)
    # set-back tiers into the block
    dep = CFG.get("tier_depth", 6.0)
    cx, hw = (u0 + u1) / 2.0, w / 2.0 - 0.3
    cy = face - out * (dep / 2.0 - 0.3)
    hd = dep / 2.0
    z = top + 0.25
    th = max(2.8, min(7.5, top * 0.24))
    nt = 3
    for i in range(nt):
        hh = th * (1.0 if i < nt - 1 else 1.25)
        L.box(cx - hw, cy - hd, z, cx + hw, cy + hd, z + hh)
        for sx in (-1, 1):
            for sy in (-1, 1):
                for du in (-0.14, 0.0, 0.14):
                    G.box(cx + sx * hw + du * sx - 0.04, cy + sy * hd - 0.08, z, cx + sx * hw + du * sx + 0.04, cy + sy * hd + 0.08,
                          z + hh + (1.6 if i == nt - 1 else 0.5))
        G.box(cx - hw - 0.2, cy - hd - 0.2, z + hh - 0.2, cx + hw + 0.2, cy + hd + 0.2, z + hh + 0.08)
        D.neon_lines(N, cx, cy, hw, hd, z + hh * 0.5, n=3, gap=0.26, th=0.07, out=0.04)
        z += hh
        hw *= 0.8
        hd *= 0.8
    if rng.random() < CFG.get("fan_p", 0.5):
        D.fan_crown(G, L, N2, cx, cy, z, "x", max(hw * 1.7, 2.4), rng, nray=9, t=0.45, backing=True)
    else:
        D.spire(G, N2, cx, cy, z, th * 2.4, 0.3)


def frame_signs(ctx, g):
    """Signs become deco marquees: a gold frame (four bars + a stepped top) and a thin neon line round every board."""
    G, N = ctx["gold"], ctx["neon2"]
    moved = set()
    for so in g["SIGN_OBJS"]:
        if so["centre"][1] > 9.0:                      # on a street frontage: stand proud of the new skin
            for o in so["t1"] + so["t2"] + so["t3"]:
                if o.name not in moved:
                    o.location.y -= CFG.get("sign_push", 0.55)
                    moved.add(o.name)
    bpy.context.view_layer.update()
    for so in g["SIGN_OBJS"]:
        if so["centre"][1] <= 9.0:
            continue
        ob = so["t2"][0]
        bb = [ob.matrix_world @ Vector(v) for v in ob.bound_box]
        x0, x1 = min(p.x for p in bb), max(p.x for p in bb)
        y0, y1 = min(p.y for p in bb), max(p.y for p in bb)
        z0, z1 = min(p.z for p in bb), max(p.z for p in bb)
        if x1 - x0 < 0.3 or z1 - z0 < 0.3:
            continue
        t = 0.26
        e = 0.30
        G.box(x0 - t, y0 - e, z0 - t, x1 + t, y1 + e, z0)
        G.box(x0 - t, y0 - e, z1, x1 + t, y1 + e, z1 + t)
        G.box(x0 - t, y0 - e, z0, x0, y1 + e, z1)
        G.box(x1, y0 - e, z0, x1 + t, y1 + e, z1)
        cxm = (x0 + x1) / 2
        G.box(cxm - (x1 - x0) * 0.2, y0 - e, z1 + t, cxm + (x1 - x0) * 0.2, y1 + e, z1 + t + 0.3)
        G.box(cxm - (x1 - x0) * 0.08, y0 - e, z1 + t + 0.3, cxm + (x1 - x0) * 0.08, y1 + e, z1 + t + 0.6)


def lamp_globes(ctx, g):
    """One row of kerbside deco lamp posts: fluted gold post, stepped cap, a globe lantern and a warm 2700 K point light."""
    for o in g["scene"].objects:
        if o.name.startswith(("r2_lamp_post", "r2_lamp_head")):
            o.hide_render = True
    G, Wn = ctx["gold"], ctx["bulb"]
    import bmesh
    y = CFG.get("lamp_y", 6.8)
    for x in range(int(CFG.get("lamp_x0", 8)), int(CFG.get("lamp_x1", 190)), int(CFG.get("lamp_pitch", 13))):
        h = 4.6
        for du in (-0.07, 0.0, 0.07):
            G.box(x + du - 0.04, y - 0.04, 0.0, x + du + 0.04, y + 0.04, h)
        G.box(x - 0.2, y - 0.2, 0.0, x + 0.2, y + 0.2, 0.35)
        G.box(x - 0.14, y - 0.14, 0.35, x + 0.14, y + 0.14, 0.6)
        G.box(x - 0.22, y - 0.22, h, x + 0.22, y + 0.22, h + 0.12)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=2, radius=0.34)
        for f in bm.faces:
            Wn.face([(x + v.co.x, y + v.co.y, h + 0.48 + v.co.z) for v in f.verts])
        bm.free()
        G.box(x - 0.24, y - 0.24, h + 0.86, x + 0.24, y + 0.24, h + 0.94)
        G.box(x - 0.06, y - 0.06, h + 0.94, x + 0.06, y + 0.06, h + 1.25)
        g["_light"]("oc_deco_lamp_%d" % x, "POINT", (x, y, h + 0.5), (0, 0, 0), CFG.get("lamp_w", 260.0), (1.0, 0.72, 0.42))



def build_hero(ctx, g, coll, rng):
    """A Chrysler-style crown on the canyon axis: a slim tapering shaft, six stacked shrinking sunburst tiers (steel ribs and
    arcs, the triangular windows between them lit from inside), a needle spire. Champagne stainless, floodlit from below."""
    steel = D.principled("deco_steel", CFG.get("steel_col", (0.86, 0.70, 0.42)), 1.0, 0.16, coat=0.5, coat_rough=0.05,
                         emit=(0.9, 0.7, 0.4), emit_k=CFG.get("steel_emit", 0.35))
    inner = D.principled("deco_hero_inner", (0, 0, 0), 0.0, 0.5, emit=(1.0, 0.62, 0.25), emit_k=CFG.get("hero_inner", 2.4))
    shaft_m = D.principled("deco_hero_shaft", (0.02, 0.02, 0.03), 0.0, 0.2, coat=1.0, coat_rough=0.05, emit=(1.0, 0.55, 0.22), emit_k=0.5)
    ST, IN, SH = D.DAcc("deco_steelacc", steel, coll), D.DAcc("deco_innerlit", inner, coll), D.DAcc("deco_heroshaft", shaft_m, coll)
    NE = ctx["neon2"]
    fx, fy = CFG.get("crown_xy", (120.0, 19.0))
    z0 = CFG.get("crown_z", 6.0)
    hw = CFG.get("hero_hw", 2.3)
    # shaft: three tapering lacquer blocks with steel cornices and parallel neon
    z = 0.0
    for i, (f, h) in enumerate(((1.0, 3.5), (0.82, 3.0), (0.66, 2.5))):
        w = hw * f
        SH.box(fx - w, fy - w, z, fx + w, fy + w, z + h)
        ST.box(fx - w - 0.2, fy - w - 0.2, z + h - 0.3, fx + w + 0.2, fy + w + 0.2, z + h + 0.1)
        D.neon_lines(NE, fx, fy, w, w, z + h * 0.5, n=2, gap=0.4, th=0.1, out=0.08)
        for sx in (-1, 1):
            for sy in (-1, 1):
                ST.box(fx + sx * w - 0.12, fy + sy * w - 0.12, z, fx + sx * w + 0.12, fy + sy * w + 0.12, z + h)
        z += h
    # six sunburst tiers, each ~78 % of the one below, each facing the street (and the side), windows lit from inside
    r = CFG.get("crown_r", 3.8)
    th = CFG.get("tier_h", 1.9)
    for i in range(6):
        for ax in ("x", "y"):
            D.fan_crown(ST, IN, NE if i % 2 else ST, fx, fy - 0.0 if ax == "x" else fy, z, ax, r, rng, nray=9, t=0.5, backing=True)
        ST.box(fx - r * 0.55, fy - 0.4, z - 0.15, fx + r * 0.55, fy + 0.4, z + 0.12)
        z += th * (0.85 + 0.15 * (i < 3))
        r *= 0.78
    ST.box(fx - 0.35, fy - 0.35, z, fx + 0.35, fy + 0.35, z + 2.2)
    ST.box(fx - 0.12, fy - 0.12, z + 2.2, fx + 0.12, fy + 0.12, z + CFG.get("spire_h", 5.0))
    NE.box(fx - 0.04, fy - 0.2, z + 2.0, fx + 0.04, fy + 0.2, z + CFG.get("spire_h", 5.0) - 0.3)
    for k in range(3):
        a_ = k * 2.1 + 0.4
        loc = (fx + 6 * math.cos(a_), fy - 9 + 3 * math.sin(a_), 0.6)
        o = g["_light"]("oc_deco_crownup_%d" % k, "SPOT", loc, (Vector((fx, fy, z * 0.7)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(),
                        CFG.get("hero_flood", 40000.0), (1.0, 0.78, 0.5), spot=22.0, blend=0.4)
        o.visible_volume_scatter = False
    for a in (ST, IN, SH):
        a.build()


def b_paths(ctx, g, coll):
    """Gold and fog on separate light paths (no light linking): glossy-only emissive cards for the metal to reflect, extra warm
    lights with volume-scatter visibility off, and a cool fog-only light (diffuse / glossy off)."""
    sc = g["scene"]

    def card(name, loc, size, rot, col, k, glossy_only=True):
        me = bpy.data.meshes.new(name)
        w, h = size
        me.from_pydata([(-w / 2, -h / 2, 0), (w / 2, -h / 2, 0), (w / 2, h / 2, 0), (-w / 2, h / 2, 0)], [], [(0, 1, 2, 3)])
        m = D.emission(name + "_m", col, k)
        me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        sc.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = rot
        ob.visible_camera = False
        ob.visible_diffuse = False
        ob.visible_transmission = False
        ob.visible_volume_scatter = False
        ob.visible_shadow = False
        ob.visible_glossy = True
        return ob
    # facing +y (toward the facades), in front of the street, above camera height: warm champagne, plus a cool teal strip
    face = Vector((0, 1, 0)).to_track_quat("Z", "Y").to_euler()
    face = (math.pi / 2, 0, 0)          # plane normal +z -> rotate so it faces +y (normal = (0, -sin, cos)): x-rot 90 gives -y; flip below
    face = (-math.pi / 2, 0, 0)
    ck = CFG.get("card_k", 14.0)
    for i, (x, z, w, h, col, k) in enumerate(((100.0, 16.0, 70.0, 22.0, (1.0, 0.82, 0.5), ck), (150.0, 14.0, 60.0, 20.0, (1.0, 0.75, 0.42), ck),
                                                (118.0, 30.0, 90.0, 10.0, (0.55, 0.75, 1.0), ck * 0.5))):
        card("deco_card_%d" % i, (x, CFG.get("card_y", -18.0), z), (w, h), face, col, k)
    # warm accent lights for the gold: volume-scatter visibility off, so they light the metal and not the fog
    for k_, (px, pz) in enumerate(((95.0, 6.0), (125.0, 6.0), (150.0, 6.0))):
        loc = (px, -10.0, pz)
        o = g["_light"]("oc_deco_gold_%d" % k_, "AREA", loc, (Vector((px, 12.0, 8.0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(),
                        CFG.get("gold_light", 9000.0), (1.0, 0.8, 0.5), size=(12, 6))
        o.visible_volume_scatter = False
        o.visible_camera = False
    # the cool fog light: volume only
    loc = (118.0, 30.0, 55.0)
    o = g["_light"]("oc_deco_fogcool", "AREA", loc, (math.pi, 0, 0), CFG.get("fog_light", 40000.0), (0.5, 0.62, 0.95), size=(120, 80))
    o.visible_diffuse = False
    o.visible_glossy = False
    o.visible_transmission = False
    o.visible_camera = False
    o.visible_shadow = False
    D.fog_veil(dict(FOG_M=bpy.data.materials["oc_fog"]), dict(veil_k=CFG.get("veil_k_b", 0.16), veil_z=tuple(CFG.get("veil_z_b", (5.0, 30.0))), veil_scale=0.02))


def apply_street(g):
    sc = g["scene"]
    PLAN, LKA = g["PLAN"], g["LKA"]
    rng = random.Random(CFG.get("seed", 20261020))
    M = D.Mats()
    coll = bpy.data.collections.new("deco")
    sc.collection.children.link(coll)
    nk = CFG.get("neon_k", 3.0)
    hue = tuple(CFG.get("hue", (0.60, 0.25, 1.0)))
    hue2 = tuple(CFG.get("hue2", (0.15, 0.85, 1.0)))
    ctx = dict(mats=M, coll=coll)
    skin = D.principled("deco_skin", CFG.get("skin", (0.012, 0.012, 0.02)), 0.0, 0.16, coat=1.0, coat_rough=0.03)
    # floodlit from below, as a material: a warm glow that is strong at the base and dies up the facade (exp), with a
    # slow noise so it is not a flat gradient (the base pipeline's lights do not reach the new skin)
    nt = skin.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Position"], sp.inputs[0])
    fall = D._math(nt, "EXPONENT", D._math(nt, "MULTIPLY", D._math(nt, "MAXIMUM", D._math(nt, "SUBTRACT", sp.outputs["Z"], 2.0), 0.0), -1.0 / CFG.get("flood_h", 11.0)))
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 0.35
    nt.links.new(geo.outputs["Position"], nz.inputs["Vector"])
    f2 = D._math(nt, "MULTIPLY", fall, D._math(nt, "ADD", 0.55, nz.outputs["Fac"]))
    bsdf.inputs["Emission Color"].default_value = tuple(CFG.get("flood_col", (1.0, 0.62, 0.30))) + (1.0,)
    nt.links.new(D._math(nt, "MULTIPLY", f2, CFG.get("flood_k", 0.05)), bsdf.inputs["Emission Strength"])
    gold = D.principled("deco_gold_st", CFG.get("gold_col", (0.90, 0.68, 0.22)), 1.0, 0.22, coat=0.6, coat_rough=0.08, emit=(0.8, 0.5, 0.1), emit_k=CFG.get("gold_emit", 0.8))
    gn = gold.node_tree
    gb = next(n for n in gn.nodes if n.type == "BSDF_PRINCIPLED")
    gg = gn.nodes.new("ShaderNodeNewGeometry")
    gno = gn.nodes.new("ShaderNodeTexNoise")
    gno.inputs["Scale"].default_value = 3.0
    gno.inputs["Detail"].default_value = 4.0
    gn.links.new(gg.outputs["Position"], gno.inputs["Vector"])
    gn.links.new(D._math(gn, "ADD", 0.2, D._math(gn, "MULTIPLY", gno.outputs["Fac"], 0.22)), gb.inputs["Roughness"])
    glass = D.principled("deco_glass", (0.01, 0.012, 0.02), 0.0, 0.04, coat=1.0, coat_rough=0.02)
    tones = [D.principled("deco_wt%d" % i, (0, 0, 0), 0.0, 0.5, emit=c, emit_k=k * CFG.get("win_k", 1.0)) for i, (c, k) in enumerate(
        (((1.0, 0.45, 0.12), 1.3), ((1.0, 0.36, 0.08), 0.8), ((1.0, 0.55, 0.18), 1.8), ((0.9, 0.28, 0.06), 0.5), ((1.0, 0.5, 0.14), 1.0), ((0.8, 0.5, 0.25), 0.7)))]
    ctx["lac"] = D.DAcc("deco_lacquer", skin, coll)
    ctx["glass"] = D.DAcc("deco_glassacc", glass, coll)
    ctx["wtones"] = [D.DAcc("deco_wtacc%d" % i, t, coll) for i, t in enumerate(tones)]
    ctx["bulb"] = D.DAcc("deco_bulb", M.neon((1.0, 0.7, 0.35), 6.0), coll)
    ctx["gold"] = D.DAcc("deco_gold", gold, coll)
    ctx["neon"] = D.DAcc("deco_neon", M.neon(hue, nk), coll)
    ctx["neon2"] = D.DAcc("deco_neon2", M.neon(hue2, nk), coll)
    ctx["win"] = D.DAcc("deco_win", M.neon((1.0, 0.72, 0.36), CFG.get("win_k", 1.4)), coll)
    # materials: SURF (all facade colour), the kit panel and the plinth tops -> lacquer + gold grid near the camera
    for k in ("SURF", "PANELM", "LITA"):
        m = g.get(k)
        if m is not None:
            D.lacquer_facade(m, mull_u=1.6, mull_v=1.9, band_every=4, dark=CFG.get("dark", 0.55), window_tint=None,
                             fade0=CFG.get("fade0", 70.0), fade1=CFG.get("fade1", 170.0), mull_w=0.05, span_w=0.05, band_w=0.06)
    # windows pulled toward gold
    for nd in g["WINA"].node_tree.nodes:
        if nd.type == "EMISSION" and nd.inputs["Color"].is_linked:
            vm = g["WINA"].node_tree.nodes.new("ShaderNodeVectorMath")
            vm.operation = "MULTIPLY"
            src = nd.inputs["Color"].links[0].from_socket
            g["WINA"].node_tree.links.new(src, vm.inputs[0])
            vm.inputs[1].default_value = (1.0, 0.78, 0.45)
            g["WINA"].node_tree.links.new(vm.outputs[0], nd.inputs["Color"])
    faces = [dict(ff, kind="front") for ff in PLAN.get("front_faces", [])]
    seen = [(f["u0"], f["u1"]) for f in faces]
    for (c_, q_, zt_, terr_, ts_, key_) in g["BUILT"]:
        xs_ = [p[0] for p in q_]
        ys_ = [p[1] for p in q_]
        u0_, u1_, fy_ = min(xs_), max(xs_), min(ys_)
        if 10.5 < fy_ < 16.0 and zt_ > 8.0 and u1_ - u0_ > 2.5 and not any(abs(u0_ - a) < 1.5 and abs(u1_ - b) < 1.5 for a, b in seen):
            if CFG.get("x_lo", 100.0) < (u0_ + u1_) / 2 < CFG.get("x_hi", 230.0):
                faces.append(dict(uid="b%s" % key_, u0=u0_, u1=u1_, face=fy_, out=-1.0, top=zt_, col=[1, 1, 1], kind="extra"))
                seen.append((u0_, u1_))
    print("[deco] faces total", len(faces), flush=True)
    wm_ = bpy.data.materials.get("oc_wet")
    if wm_:
        for nd in wm_.node_tree.nodes:
            if nd.type == "MAP_RANGE" and abs(nd.inputs["To Min"].default_value - 0.3) < 1e-3:
                nd.inputs["To Min"].default_value = CFG.get("wet_rough", 0.14)
                nd.inputs["To Max"].default_value = 0.015
    for ff in faces:
        face_deco(ctx, ff, rng)
    # floods on the frontage: warm gold
    for o in sc.objects:
        if o.type == "LIGHT" and o.name.startswith(("oc_fwash", "oc_wash", "oc_spill")):
            c = tuple(o.data.color)
            o.data.color = tuple(0.35 * a + 0.65 * b for a, b in zip(c, CFG.get("flood_col", (1.0, 0.68, 0.32))))
            o.data.energy *= CFG.get("flood_k", 1.0)
    if CFG.get("hero", "v4") == "v4":
        build_hero(ctx, g, coll, rng)
    else:
        hskin = D.principled("deco_hero_skin", (0.02, 0.02, 0.03), 0.0, 0.2, coat=1.0, coat_rough=0.05)
        hb = next(n for n in hskin.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        hg = hskin.node_tree.nodes.new("ShaderNodeNewGeometry")
        hs_ = hskin.node_tree.nodes.new("ShaderNodeSeparateXYZ")
        hskin.node_tree.links.new(hg.outputs["Position"], hs_.inputs[0])
        hb.inputs["Emission Color"].default_value = (1.0, 0.55, 0.22, 1.0)
        hskin.node_tree.links.new(D._math(hskin.node_tree, "MULTIPLY", D._math(hskin.node_tree, "EXPONENT", D._math(hskin.node_tree, "MULTIPLY", hs_.outputs["Z"], -0.035)), 0.9), hb.inputs["Emission Strength"])
        hero_l = D.DAcc("deco_hero_lac", hskin, coll)
        fx, fy_ = CFG.get("crown_xy", (108.0, 40.0))
        zc = CFG.get("crown_z", 26.0)
        HW = CFG.get('hero_hw', 3.2)
        hero_l.box(fx - HW, fy_ - HW, 0, fx + HW, fy_ + HW, zc)
        ctx["gold"].box(fx - HW - 0.4, fy_ - HW - 0.4, zc - 0.6, fx + HW + 0.4, fy_ + HW + 0.4, zc + 0.2)
        D.neon_lines(ctx["neon"], fx, fy_, HW, HW, zc - 4, n=3, gap=0.5, th=0.14, out=0.2)
        sx_, z_ = HW * 0.75, zc + 0.2
        for i in range(3):
            hero_l.box(fx - sx_, fy_ - sx_, z_, fx + sx_, fy_ + sx_, z_ + 2.6)
            ctx["gold"].box(fx - sx_ - 0.2, fy_ - sx_ - 0.2, z_ + 2.4, fx + sx_ + 0.2, fy_ + sx_ + 0.2, z_ + 2.65)
            D.neon_lines(ctx["neon"], fx, fy_, sx_, sx_, z_ + 1.4, n=2, gap=0.4, th=0.1, out=0.1)
            z_ += 2.6
            sx_ *= 0.8
        for hz in range(3, int(zc), 5):
            D.neon_lines(ctx["neon2"], fx, fy_, HW, HW, hz, n=2, gap=0.5, th=0.22, out=0.25)
        for sx2 in (-1, 1):
            for sy2 in (-1, 1):
                ctx["neon"].box(fx + sx2 * (HW + 0.3) - 0.15, fy_ + sy2 * (HW + 0.3) - 0.15, 0, fx + sx2 * (HW + 0.3) + 0.15, fy_ + sy2 * (HW + 0.3) + 0.15, zc)
        D.fan_crown(ctx["gold"], hero_l, ctx["neon2"], fx, fy_ - 3.0, z_, "x", CFG.get("crown_r", 8.0), rng, nray=13, t=0.6, backing=True)
        D.spire(ctx["gold"], ctx["neon2"], fx, fy_, z_ + 2.0, CFG.get("spire_h", 12.0), 0.3)
        for k_ in range(3):
            a_ = k_ * 2.1
            loc = (fx + 9 * math.cos(a_), fy_ - 12 + 4 * math.sin(a_), 0.6)
            g["_light"]("oc_deco_crownup_%d" % k_, "SPOT", loc, (Vector((fx, fy_, zc + 6)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler(),
                        60000.0, (1.0, 0.72, 0.4), spot=34.0, blend=0.5)
    if CFG.get("bpath", True):
        b_paths(ctx, g, coll)
    frame_signs(ctx, g)
    lamp_globes(ctx, g)
    lg = g["_light"]
    for k_, ff in enumerate(faces):
        wmid = (ff["u0"] + ff["u1"]) / 2
        for j, f_ in enumerate((0.2, 0.5, 0.8)):
            uu = ff["u0"] + (ff["u1"] - ff["u0"]) * f_
            pos = (uu, ff["face"] + ff["out"] * 3.0, 1.8)
            tgt = Vector((uu, ff["face"], ff["top"] * 0.7))
            lg("oc_deco_up_%d_%d" % (k_, j), "SPOT", pos, (tgt - Vector(pos)).to_track_quat("-Z", "Y").to_euler(),
               CFG.get("up_w", 14000.0), CFG.get("flood_col", (1.0, 0.72, 0.38)), spot=48.0, blend=0.7)
    fog_g = dict(FOG_M=bpy.data.materials["oc_fog"])
    D.fog_veil(fog_g, dict(veil_k=CFG.get("veil_k", 0.10), veil_z=tuple(CFG.get("veil_z", (6.0, 40.0))), veil_scale=0.02))
    for k in ("lac", "gold", "neon", "neon2", "win", "glass", "bulb"):
        ctx[k].build()
    for t in ctx["wtones"]:
        t.build()
    if CFG.get('hero', 'v4') != 'v4':
        hero_l.build()
    ls = [o for o in sc.objects if o.name.startswith("oc_deco_up")]
    print("[deco] lights", len(ls), [(o.hide_render, o.get("oc_off"), o.data.energy, tuple(round(v, 1) for v in o.location), o.data.type) for o in ls[:3]], flush=True)
    print("[deco] street: faces", len(faces), {k: len(ctx[k].f) for k in ("lac", "gold", "neon", "neon2", "win")}, flush=True)
