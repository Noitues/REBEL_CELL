"""Graffiti layer for the original F1b scene (round33/scripts/scene.py, Eevee toon): built at run time inside its main().

Everything added keeps F1b's own look: decals reuse F1b's toon material (same banded light, same lights, same post: ink, haze,
bloom, rain, wet-floor reflections). Decals take the pass index of the wall under them, so the ink pass draws no outline round them.
Emissive additions (blades, holo, fascia) are registered as kind 'sign' so post.py reflects them in the wet street like the sign.
"""
import math
import random

import bpy
from mathutils import Vector

T1 = "D:/rc_scratch/hq_styles/rebel_cell_graffiti/tex"
T2 = "D:/rc_scratch/hq_styles/rebel_cell_graffiti/tex2"


class NT:
    def __init__(self, mat):
        mat.use_nodes = True
        self.t = mat.node_tree
        self.n, self.l = self.t.nodes, self.t.links
        for x in list(self.n):
            self.n.remove(x)
        self.out = self.n.new("ShaderNodeOutputMaterial")

    def node(self, t, **kw):
        nd = self.n.new(t)
        for k, v in kw.items():
            setattr(nd, k, v)
        return nd

    def link(self, a, b):
        self.l.new(a, b)

    def math(self, op, a, b=None, clamp=False):
        nd = self.node("ShaderNodeMath", operation=op, use_clamp=clamp)
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                nd.inputs[i].default_value = x
            else:
                self.link(x, nd.inputs[i])
        return nd.outputs[0]

    def maprange(self, v, a0, a1, b0, b1):
        nd = self.node("ShaderNodeMapRange")
        self.link(v, nd.inputs[0])
        nd.inputs[1].default_value, nd.inputs[2].default_value = a0, a1
        nd.inputs[3].default_value, nd.inputs[4].default_value = b0, b1
        return nd.outputs[0]


_IM = {}


def img(path, nc=False):
    if (path, nc) not in _IM:
        im = bpy.data.images.load(path)
        im.colorspace_settings.name = "Non-Color" if nc else "sRGB"
        im.alpha_mode = "STRAIGHT"
        _IM[(path, nc)] = im
    return _IM[(path, nc)]


def extras(ns):
    F = ns["F"]
    Mesh, hexl, scl = ns["Mesh"], ns["hexl"], ns["scl"]
    YS, YF, YFB, XA0, XA1, XFR = ns["YS"], ns["YF"], ns["YFB"], ns["XA0"], ns["XA1"], ns["XFR"]
    SX0, SX1, SZ1, D_SIGN, RX0, RX1, RZ, RD = ns["SX0"], ns["SX1"], ns["SZ1"], ns["D_SIGN"], ns["RX0"], ns["RX1"], ns["RZ"], ns["RD"]
    Y_ST0, Y_ST1, Z_LAND, YW, HF, Y_KERB = ns["Y_ST0"], ns["Y_ST1"], ns["Z_LAND"], ns["YW"], ns["HF"], ns["Y_KERB"]
    pal = ns["PAL"][ns["OPT"]]
    sc = bpy.context.scene
    TOON = F.TOON["m"]
    rng = random.Random(404)

    def pid(name):
        for k, (n, kind) in F.OBJ["kinds"].items():
            if n == name:
                return k
        raise KeyError(name)

    def register(ob, name, kind="sign"):
        F.OBJ["n"] += 1
        ob.pass_index = F.OBJ["n"]
        F.OBJ["kinds"][F.OBJ["n"]] = (name, kind)

    # ---- F1b's toon material with the albedo (and glow) swapped for an image: same banded light, same wet gloss layer
    def toon_variant(name, color_path, glow_path=None, alpha=True, glow_k=0.35, base_emit=0.0):
        m = TOON.copy()
        m.name = name
        nt = m.node_tree
        acol = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeAttribute" and n.attribute_name == "col")
        aemi = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeAttribute" and n.attribute_name == "emit")
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = img(color_path)
        tex.interpolation = "Linear"
        for l in list(acol.outputs[0].links):
            nt.links.new(tex.outputs["Color"], l.to_socket)
        tg = [l.to_socket for l in aemi.outputs[0].links]
        if glow_path:
            gt = nt.nodes.new("ShaderNodeTexImage")
            gt.image = img(glow_path, True)
            sc_ = nt.nodes.new("ShaderNodeVectorMath")
            sc_.operation = "SCALE"
            nt.links.new(tex.outputs["Color"], sc_.inputs[0])
            ad = nt.nodes.new("ShaderNodeMath")
            ad.operation = "ADD"
            ad.inputs[1].default_value = base_emit
            nt.links.new(gt.outputs["Color"], ad.inputs[0])
            nt.links.new(ad.outputs[0], sc_.inputs["Scale"])
            for s in tg:
                nt.links.new(sc_.outputs[0], s)
            for node in (gt,):
                pass
        if alpha:
            out = next(n for n in nt.nodes if n.bl_idname == "ShaderNodeOutputMaterial")
            src = out.inputs["Surface"].links[0].from_socket
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mx = nt.nodes.new("ShaderNodeMixShader")
            gtn = nt.nodes.new("ShaderNodeMath")
            gtn.operation = "GREATER_THAN"
            gtn.inputs[1].default_value = 0.4
            nt.links.new(tex.outputs["Alpha"], gtn.inputs[0])
            nt.links.new(gtn.outputs[0], mx.inputs[0])
            nt.links.new(tr.outputs[0], mx.inputs[1])
            nt.links.new(src, mx.inputs[2])
            nt.links.new(mx.outputs[0], out.inputs["Surface"])
        return m

    def quad(name, o, u, v, uv0, uv1, mat, pass_id, shadow=False):
        o, u, v = Vector(o), Vector(u), Vector(v)
        me = bpy.data.meshes.new(name)
        me.from_pydata([tuple(o), tuple(o + u), tuple(o + u + v), tuple(o + v)], [], [(0, 1, 2, 3)])
        ul = me.uv_layers.new(name="UVMap")
        for i, c in enumerate([(uv0[0], uv0[1]), (uv1[0], uv0[1]), (uv1[0], uv1[1]), (uv0[0], uv1[1])]):
            ul.data[i].uv = c
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        sc.collection.objects.link(ob)
        ob.pass_index = pass_id
        ob.visible_shadow = shadow
        return ob

    # ---- 1. roll shutters: bombed panels over F1b's own shutters (the second is half open)
    shut = pid("fb_shutters")
    for i, x0 in enumerate((XA1 + 0.8, XA1 + 5.9)):
        z0 = 0.18 + (1.0 if i == 1 else 0.0)
        m = toon_variant("gz_shutter%d" % i, f"{T2}/gz_shutter{i}_albedo.png", f"{T2}/gz_shutter{i}_glow.png", alpha=False, glow_k=0.4, base_emit=0.3)
        h = 2.9 - (1.0 if i == 1 else 0.0)
        quad("gz_shutter%d" % i, (x0, YF - 0.075, z0), (4.6, 0, 0), (0, 0, h), (0, 0 if i == 0 else 0.0), (1, 1), m, shut)

    # ---- 2. wall pieces (patch-masked atlas), in zones; none beside the stair, none on the sign or fire escape
    wm = toon_variant("gz_wall", f"{T2}/gz_wall_albedo.png", f"{T2}/gz_wall_glow.png", alpha=True, base_emit=0.10)

    def wall_decal(name, host, o, u, v):
        lu, lv = Vector(u).length, Vector(v).length
        u0, v0 = rng.random() * 0.45, rng.random() * 0.45
        quad(name, o, u, v, (u0, v0), (u0 + lu / 40.96, v0 + lv / 20.48), wm, pid(host))

    wall_decal("gz_alley_r", "front", (XA1 - 0.03, YF + 0.4, 0.2), (0, 5.2, 0), (0, 0, 3.7))
    wall_decal("gz_alley_l", "shop_tower", (XA0 + 0.03, YS + 0.3, 0.2), (0, 3.0, 0), (0, 0, 4.0))
    wall_decal("gz_tower_edge", "shop_tower", (-14.5, YS - 0.03, 0.2), (4.7, 0, 0), (0, 0, 9.0))
    wall_decal("gz_side_row", "side_row", (XFR + 1.6, 30.97, 0.2), (23.0, 0, 0), (0, 0, 4.4))

    # ---- 3. the sign-side utility pole: square, stickers on the two faces the camera sees, each sticker wholly inside its face
    px, py, pw = -6.0, Y_KERB + 0.6, 0.38
    pm = Mesh("gz_pole", "solid")
    pm.box(px - pw / 2, px + pw / 2, py - pw / 2, py + pw / 2, 0.18, 9.0, cell=3, col=hexl("#2c3038"), var=0.06, faces="fblrt")
    pm.build()
    ph_ = bpy.data.objects.get("fb_posters")
    if ph_:
        ph_.hide_render = True      # the dark F1b posters on the shutters read as holes under the paint
    pole_id = pid("gz_pole")
    for nm, o, u, tex in (("f", (px - pw / 2, py - pw / 2 - 0.012, 0.2), (pw, 0, 0), "pole_f"), ("r", (px + pw / 2 + 0.012, py - pw / 2, 0.2), (0, pw, 0), "pole_r")):
        mpm = toon_variant("gz_pole_" + nm, f"{T2}/{tex}.png", None, alpha=False)
        quad("gz_pole_" + nm, o, u, (0, 0, 3.2), (0, 0), (1, 1), mpm, pole_id)
    pc = Mesh("gz_pole_arm", "solid")
    pc.box(px - 1.0, px + 1.0, py - 0.1, py + 0.1, 8.2, 8.35, cell=3, col=hexl("#2a2c30"), faces="fblrt")
    pc.build()

    # ---- 4. the sidewalk RECYCLE BIN, tagged; cylinder UV with the seam at the back (+y)
    bx, by = -1.7, 19.9
    seg = 36
    prof = [(0.50, 0.18), (0.68, 1.75)]
    vs, fs, uvs = [], [], []
    for i in range(seg + 1):
        a = 2 * math.pi * i / seg
        for (r, z) in prof:
            vs.append((bx + r * math.sin(a), by + r * math.cos(a), z))
    for i in range(seg):
        a0 = i * 2
        fs.append((a0, a0 + 2, a0 + 3, a0 + 1))
    me = bpy.data.meshes.new("gz_bin")
    me.from_pydata(vs, [], fs)
    ul = me.uv_layers.new(name="UVMap")
    for pi, poly in enumerate(me.polygons):
        t0, t1 = pi / seg, (pi + 1) / seg
        for k, li in enumerate(poly.loop_indices):
            ul.data[li].uv = [(t0, 0), (t1, 0), (t1, 1), (t0, 1)][k]
    me.update()
    me.materials.append(toon_variant("gz_bin", f"{T2}/bin2.png", None, alpha=False))
    ob = bpy.data.objects.new("gz_bin", me)
    sc.collection.objects.link(ob)
    register(ob, "gz_bin", "solid")
    bl = Mesh("gz_binlid", "solid")
    bl.box(bx - 0.7, bx + 0.7, by - 0.7, by + 0.7, 1.75, 1.82, cell=3, col=hexl("#1d2026"), faces="fblrt")
    bl.build()
    br = Mesh("gz_binring", "window")
    br.box(bx - 0.5, bx + 0.5, by - 0.5, by + 0.5, 1.82, 1.84, cell=3, col=scl(hexl("#a8ff30"), 0.3), emi=scl(hexl("#a8ff30"), 1.1), faces="t")
    br.build()
    F.light("POINT", (bx, by - 0.5, 2.1), hexl("#a8ff30"), 90, size=0.2, name="bin_lime")

    # ---- 5. alley stair: lit riser strips, a cyan wash on the treads; no paint beside it
    n = int((Z_LAND - 0.18) / 0.28)
    sg = Mesh("gz_stair_glow", "window")
    cc = hexl(pal["alley"])
    for i in range(n):
        y = Y_ST0 + (Y_ST1 - Y_ST0) * i / n
        z = 0.18 + (Z_LAND - 0.18) * (i + 1) / n
        sg.grid((XA0 + 0.35, y - 0.012, z - 0.085), (XA1 - XA0 - 0.7, 0, 0), (0, 0, 0.06), cell=3, col=scl(cc, 0.3), emi=scl(cc, 1.0))
    sg.build()
    for (y, z, k) in ((Y_ST0 + 1.5, 2.0, 520), (Y_ST0 + 5.0, 3.6, 520), (Y_ST0 + 8.5, 5.2, 420)):
        F.light("POINT", (0.0, y, z + 0.9), cc, k, size=0.25, name="stair_lamp")

    # ---- 6. MAINFRAME shopfront: warmer glow in the foyer, fascia board
    F.light("AREA", ((RX0 + RX1) / 2, YS + RD - 0.4, 1.8), hexl("#ffd9b0"), 380, size=RX1 - RX0, size_y=1.2, rot=(-math.pi / 2, 0, 0), name="foyer_warm")

    def emit_mat(name, path, cell, grid, k):
        m = bpy.data.materials.new(name)
        nt = NT(m)
        tc = nt.node("ShaderNodeTexCoord")
        mp = nt.node("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = (1 / grid[0], 1 / grid[1], 1)
        mp.inputs["Location"].default_value = (cell[0] / grid[0], 1 - (cell[1] + 1) / grid[1], 0)
        nt.link(tc.outputs["UV"], mp.inputs[0])
        a = nt.node("ShaderNodeTexImage")
        a.image = img(path)
        nt.link(mp.outputs[0], a.inputs[0])
        em = nt.node("ShaderNodeEmission")
        nt.link(a.outputs["Color"], em.inputs[0])
        em.inputs[1].default_value = k
        nt.link(em.outputs[0], nt.out.inputs["Surface"])
        return m

    fm = emit_mat("gz_fascia", f"{T1}/mainframe_h.png", (0, 0), (1, 1), 1.3)
    f = quad("gz_fascia", (-7.0, YS - 0.215, 3.15), (3.9, 0, 0), (0, 0, 0.975), (0, 0), (1, 1), fm, 0)
    register(f, "gz_fascia")
    fr = Mesh("gz_fascia_frame", "solid")
    fr.box(-7.08, -3.02, YS - 0.2, YS - 0.08, 3.08, 4.2, cell=2, col=hexl("#1a1a1e"), faces="fltrd")
    fr.build()

    # ---- 7. blade signs (multilingual, lit), on the F1b buildings; none on the hero sign
    gfr = Mesh("gz_blade_frames", "solid")

    def blade(x, y, z, w, h, cell, rotz, kind="v", k=0.85):
        grid = (8, 3) if kind == "v" else (2, 8)
        path = f"{T1}/signs_v.png" if kind == "v" else f"{T1}/signs_h.png"
        c = cell % (24 if kind == "v" else 16)
        cr = (c % 8, c // 8) if kind == "v" else (c % 2, c // 2)
        m = emit_mat("gz_bl%s%d" % (kind, c), path, cr, grid, k)
        d = 0.26
        for side in (1, -1):
            me = bpy.data.meshes.new("gz_blade")
            if kind == "v":
                pts = [(side * d / 2, -w / 2 * side, 0), (side * d / 2, w / 2 * side, 0), (side * d / 2, w / 2 * side, h), (side * d / 2, -w / 2 * side, h)]
            else:
                pts = [(-w / 2 * side, -side * d / 2, 0), (w / 2 * side, -side * d / 2, 0), (w / 2 * side, -side * d / 2, h), (-w / 2 * side, -side * d / 2, h)]
            me.from_pydata(pts, [], [(0, 1, 2, 3)])
            ul = me.uv_layers.new(name="UVMap")
            for i, cc_ in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
                ul.data[i].uv = cc_
            me.materials.append(m)
            ob = bpy.data.objects.new("gz_blade", me)
            sc.collection.objects.link(ob)
            ob.location = (x, y, z)
            ob.rotation_euler = (0, 0, rotz if kind == "v" else 0)
            register(ob, "gz_blade")
        if kind == "v":
            ax = Vector((math.cos(rotz), math.sin(rotz), 0)) * (d / 2 - 0.02)
            ay = Vector((-math.sin(rotz), math.cos(rotz), 0)) * (w / 2 + 0.05)
            gfr.obox((x, y, z + h / 2), tuple(ax), tuple(ay), (0, 0, h / 2 + 0.05), col=hexl("#16171b"), var=0.05, cell=2)
        else:
            gfr.obox((x, y, z + h / 2), (w / 2 + 0.05, 0, 0), (0, d / 2 - 0.02, 0), (0, 0, h / 2 + 0.05), col=hexl("#16171b"), var=0.05, cell=2)

    blade(XA0 - 0.2, YS - 0.9, 6.3, 0.9, 3.4, 14, -0.45)                    # tower corner
    blade(XA1 + 0.2, YF - 0.9, 3.7, 0.9, 3.0, 1, 0.45)                       # front building, alley side
    blade(XFR - 0.3, YF - 0.9, 3.0, 0.9, 3.9, 17, 0.45, k=1.1)             # RAMEN
    for x, z, h, c in ((16.5, 3.3, 4.2, 3), (20.5, 4.4, 3.6, 9), (25.0, 3.0, 4.6, 22), (29.5, 5.0, 3.4, 6), (34.0, 3.4, 4.2, 0)):
        blade(x, 30.3, z, 1.0, h, c, 0.35)
    for x, z, c in ((6.0, 8.8, 4), (11.5, 9.2, 19), (17.0, 8.5, 10), (23.0, 9.0, 12), (29.0, 8.7, 2)):
        blade(x, YW - 0.9, z, 1.0, 3.0, c, 0.3)
    blade(XA0 + 0.5, YS + 6.5, 6.6, 0.7, 2.4, 21, 1.35)
    blade(XA1 - 0.5, YF + 5.5, 7.4, 0.7, 2.4, 8, -1.35)
    blade(7.4, YF - 0.3, 3.55, 5.0, 0.8, 7, 0, "h", k=0.7)                   # a dim horizontal over the shutters
    gfr.build()

    # ---- 8. the ramen hologram: recognisable bowl, noodles, egg, chopsticks, steam; translucent emissive with scanlines and a cone
    def holo_mat(name, c0, c1, alpha=0.5, k=9.0, fres=0.8):
        m = bpy.data.materials.new(name)
        nt = NT(m)
        tc = nt.node("ShaderNodeTexCoord")
        sep = nt.node("ShaderNodeSeparateXYZ")
        nt.link(tc.outputs["Object"], sep.inputs[0])
        zz = sep.outputs[2]
        ramp = nt.node("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].color = (*c0, 1)
        ramp.color_ramp.elements[1].color = (*c1, 1)
        nt.link(nt.maprange(zz, 0.0, 1.0, 0.0, 1.0), ramp.inputs[0])
        scan = nt.maprange(nt.math("SINE", nt.math("MULTIPLY", zz, 220.0)), -1.0, 1.0, 0.4, 1.2)
        lw = nt.node("ShaderNodeLayerWeight")
        lw.inputs["Blend"].default_value = 0.3
        em = nt.node("ShaderNodeEmission")
        nt.link(ramp.outputs[0], em.inputs[0])
        nt.link(nt.math("MULTIPLY", scan, k), em.inputs[1])
        tr = nt.node("ShaderNodeBsdfTransparent")
        mx = nt.node("ShaderNodeMixShader")
        nt.link(nt.math("ADD", alpha, nt.math("MULTIPLY", lw.outputs["Fresnel"], fres), clamp=True), mx.inputs[0])
        nt.link(tr.outputs[0], mx.inputs[1])
        nt.link(em.outputs[0], mx.inputs[2])
        nt.link(mx.outputs[0], nt.out.inputs["Surface"])
        return m

    def lathe(name, prof, mat, cx, cy, cz, seg=32, scale=1.0):
        me = bpy.data.meshes.new(name)
        vs, fs = [], []
        for i in range(seg):
            a = 2 * math.pi * i / seg
            for (r, z) in prof:
                vs.append((cx + r * scale * math.cos(a), cy + r * scale * math.sin(a), cz + z * scale))
        m_ = len(prof)
        for i in range(seg):
            j = (i + 1) % seg
            for k in range(m_ - 1):
                fs.append((i * m_ + k, j * m_ + k, j * m_ + k + 1, i * m_ + k + 1))
        me.from_pydata(vs, [], fs)
        me.update()
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me)
        sc.collection.objects.link(ob)
        ob.visible_shadow = False
        register(ob, name)
        return ob

    def tube(name, pts, r, mat):
        cd = bpy.data.curves.new(name, "CURVE")
        cd.dimensions = "3D"
        cd.bevel_depth = r
        cd.bevel_resolution = 1
        sp = cd.splines.new("POLY")
        sp.points.add(len(pts) - 1)
        for i, p in enumerate(pts):
            sp.points[i].co = (*p, 1.0)
        ob = bpy.data.objects.new(name, cd)
        sc.collection.objects.link(ob)
        ob.data.materials.append(mat)
        ob.visible_shadow = False
        register(ob, name)
        return ob

    cx, cy, cz, S = XFR - 0.3, YF - 0.9, 8.4, 1.9
    mh = holo_mat("gz_holo_bowl", (0.2, 0.95, 1.0), (1.0, 0.35, 0.95), 0.4, 1.3)
    mn = holo_mat("gz_holo_noodle", (1.0, 0.8, 0.25), (1.0, 0.45, 0.6), 0.8, 1.6)
    mg = holo_mat("gz_holo_egg", (1.0, 0.95, 0.7), (1.0, 0.6, 0.3), 0.7, 1.4)
    bowl = [(0.0, 0.0), (0.18, 0.0), (0.30, 0.04), (0.42, 0.14), (0.50, 0.26), (0.52, 0.30), (0.48, 0.30), (0.46, 0.26), (0.38, 0.14), (0.26, 0.07), (0.0, 0.05)]
    objs = [lathe("gz_bowl", bowl, mh, 0, 0, 0.0, 36), lathe("gz_broth", [(0.0, 0.26), (0.44, 0.26)], mh, 0, 0, 0.0, 36)]
    for k in range(10):
        pts = []
        ph = k * 0.65
        for i in range(46):
            t = i / 45
            ang = ph + t * 6.0
            rr = 0.38 * (1 - 0.5 * t) * (0.6 + 0.4 * math.sin(t * 9 + k))
            pts.append((rr * math.cos(ang), rr * math.sin(ang), 0.30 + 0.12 * math.sin(t * 14 + k) + 0.16 * t))
        objs.append(tube("gz_noodle", pts, 0.014, mn))
    for (ex, ey) in ((0.2, -0.15), (-0.18, 0.1)):
        objs.append(lathe("gz_egg", [(0.0, 0.0), (0.08, 0.01), (0.14, 0.05), (0.15, 0.09), (0.08, 0.13), (0.0, 0.14)], mg, ex, ey, 0.30, 16))
    for sgn in (1, -1):
        objs.append(tube("gz_stick", [(0.1 + sgn * 0.025, 0.18, 1.05), (0.36 + sgn * 0.025, -0.1, 0.55)], 0.014, mh))
    for k in range(3):
        pts = [(0.30 * math.sin(i * 0.55 + k * 2.1) * (0.4 + i * 0.05), 0.12 * math.cos(i * 0.4 + k) + 0.1 * k - 0.1, 0.5 + i * 0.045) for i in range(14)]
        objs.append(tube("gz_steam", pts, 0.006, mh))
    for ob in objs:
        ob.scale = (S, S, S)
        ob.location = (cx, cy, cz + ob.location.z)
    ez = 6.95
    em_box = Mesh("gz_emitter", "solid")
    em_box.box(cx - 0.16, cx + 0.16, cy - 0.16, cy + 0.16, ez - 0.12, ez + 0.02, cell=3, col=hexl("#16171b"), faces="fblrt")
    em_box.build()
    eled = Mesh("gz_emitter_led", "window")
    eled.box(cx - 0.07, cx + 0.07, cy - 0.17, cy - 0.15, ez - 0.08, ez - 0.02, cell=3, col=scl(hexl("#56f2ff"), 0.3), emi=scl(hexl("#56f2ff"), 1.4), faces="f")
    eled.build()
    F.light("POINT", (cx - 0.4, cy - 1.2, cz + 0.6), hexl("#56f2ff"), 160, size=0.4, name="holo_c")
    F.light("POINT", (cx + 0.5, cy - 1.2, cz + 0.4), hexl("#ff4fd0"), 90, size=0.4, name="holo_m")
