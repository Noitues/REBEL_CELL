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
    # lit windows: small warm panels on the skin, seeded
    wz = fz0 + 0.9
    while wz < top - 3.4:
        bay = u0 + 0.9
        while bay < u1 - 0.9:
            if rng.random() < CFG.get("win_p", 0.7):
                y0, y1 = yb(0.04 + sk, 0.04 + sk + 0.04)
                W.box(bay - 0.34, y0, wz, bay + 0.34, y1, wz + 1.0)
            bay += 1.5
        wz += fl
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
        t = 0.16
        e = 0.12
        G.box(x0 - t, y0 - e, z0 - t, x1 + t, y1 + e, z0)
        G.box(x0 - t, y0 - e, z1, x1 + t, y1 + e, z1 + t)
        G.box(x0 - t, y0 - e, z0, x0, y1 + e, z1)
        G.box(x1, y0 - e, z0, x1 + t, y1 + e, z1)
        cxm = (x0 + x1) / 2
        G.box(cxm - (x1 - x0) * 0.2, y0 - e, z1 + t, cxm + (x1 - x0) * 0.2, y1 + e, z1 + t + 0.3)
        G.box(cxm - (x1 - x0) * 0.08, y0 - e, z1 + t + 0.3, cxm + (x1 - x0) * 0.08, y1 + e, z1 + t + 0.6)


def lamp_globes(ctx, g):
    """Deco lamp posts: a gold collar, a stepped cap and an amber globe on every kerb lamp head."""
    import bmesh
    G, Wn = ctx["gold"], ctx["win"]
    for (pos, c) in g["LAMP_HEADS"]:
        x, y, z = pos
        G.box(x - 0.16, y - 0.16, z - 0.45, x + 0.16, y + 0.16, z - 0.2)
        G.box(x - 0.28, y - 0.28, z - 0.2, x + 0.28, y + 0.28, z - 0.1)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.32)
        vs = [v.co.copy() for v in bm.verts]
        for f in bm.faces:
            Wn.face([(x + vs_.x, y + vs_.y, z + 0.12 + vs_.z) for vs_ in [v.co for v in f.verts]])
        bm.free()
        G.box(x - 0.2, y - 0.2, z + 0.42, x + 0.2, y + 0.2, z + 0.5)
        G.box(x - 0.07, y - 0.07, z + 0.5, x + 0.07, y + 0.07, z + 0.9)


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
    skin = D.principled("deco_skin", CFG.get("skin", (0.03, 0.025, 0.04)), 0.0, 0.30, coat=1.0, coat_rough=0.05)
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
    nt.links.new(D._math(nt, "MULTIPLY", f2, CFG.get("flood_k", 0.22)), bsdf.inputs["Emission Strength"])
    gold = D.principled("deco_gold_st", D.GOLD_LIN, 1.0, 0.28, emit=D.GOLD_LIN, emit_k=CFG.get("gold_emit", 0.7))
    ctx["lac"] = D.DAcc("deco_lacquer", skin, coll)
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
    for ff in faces:
        face_deco(ctx, ff, rng)
    # floods on the frontage: warm gold
    for o in sc.objects:
        if o.type == "LIGHT" and o.name.startswith(("oc_fwash", "oc_wash", "oc_spill")):
            c = tuple(o.data.color)
            o.data.color = tuple(0.35 * a + 0.65 * b for a, b in zip(c, CFG.get("flood_col", (1.0, 0.68, 0.32))))
            o.data.energy *= CFG.get("flood_k", 1.0)
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
               CFG.get("up_w", 5000.0), CFG.get("flood_col", (1.0, 0.72, 0.38)), spot=48.0, blend=0.7)
    fog_g = dict(FOG_M=bpy.data.materials["oc_fog"])
    D.fog_veil(fog_g, dict(veil_k=CFG.get("veil_k", 0.06), veil_z=tuple(CFG.get("veil_z", (6.0, 40.0))), veil_scale=0.02))
    for k in ("lac", "gold", "neon", "neon2", "win"):
        ctx[k].build()
    ls = [o for o in sc.objects if o.name.startswith("oc_deco_up")]
    print("[deco] lights", len(ls), [(o.hide_render, o.get("oc_off"), o.data.energy, tuple(round(v, 1) for v in o.location), o.data.type) for o in ls[:3]], flush=True)
    print("[deco] street: faces", len(faces), {k: len(ctx[k].f) for k in ("lac", "gold", "neon", "neon2", "win")}, flush=True)
