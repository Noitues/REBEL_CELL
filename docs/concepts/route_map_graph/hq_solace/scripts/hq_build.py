"""HQ Solace: the Blender build of the double-helix strands (called by the kit's hq_scene.py: build(K) -> hooks).
v3 (designer review of round 1, 2026-10-16): the strands make one FULL turn (27 floors, the city landmark's twist
rate); ONLY 2 windows a floor per strand, one INWARD (the walkway) and one OUTWARD, each a landscape oval spanning
140 degrees of its tube half; the inward windows of the route floors ARE the route nodes (an opening into a lit,
kind-dressed room; the bow-tie bridge enters it); the plinth crisp (its own non-ground pass: no LOD blur).

Placed by rule from hq_preset "compound" + hq_graph; seed 6330 (window tints).
  strands   two smooth swept tubes (a shared-vertex mesh, smooth shaded, wet porcelain + the leaf-green fresnel rim);
            the node windows are real holes (outline vertices snapped onto the oval), a downlight ring under every
            floor, a mint light seam up the BACK band, the UP stair up the FRONT band
  windows   every floor, per strand: the inward + the outward oval; non-node windows are lit glass (seeded tints, a
            few dark) with mullions; every window a frame ring
  rooms     node windows: a curved room behind the opening (floor = the bridge deck, sill, back wall, ceiling strips,
            kind-coloured panels), its own state-driven light; unread: a frosted oval over the opening
  bridges   route floors only: a bow-tie walkway from inward window to inward window (the A <-> B cross-links)
  crown     the top floor joins the strands; THE GENOME CORE sits open in its middle (red rings: the TARGET), pink halo
  podium    a rectangular plaza podium (dark, dressed, a lit entry), the clinic gate (start)
  rig       ground spots aimed up the strands, downlights, rim from the city behind, the halo fog ring
"""
import math
import random


def build(K):
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, Acc, obox, oquad, tube, box = K.A, K.Acc, K.obox, K.oquad, K.tube, K.box
    Vector = K.Vector
    import bpy
    hooks = {"accs": {}, "beams": [], "mover_lights": {}}
    PLX = bpy.data.collections.new("plinth_rx")   # v3: the plinth lights light surfaces only, never the haze (crisp)
    LEAF, PINK, CLIN, POR = pal("leaf"), pal("pink"), pal("clinic"), pal("porcelain")
    R, FH, TW, TD = CP["radius"], CP["floor_h"], CP["tower_w"], CP["tower_d"]
    TOPF = CP["floors"]
    RFS = set(CP["route_floors"])
    WIN = CP["win"]
    rr = random.Random(6330)
    log = K.log
    WB = G.WB

    m2, nt2 = K.new_mat("porcelain")
    o2 = nt2.nodes.new("ShaderNodeOutputMaterial")
    b2 = nt2.nodes.new("ShaderNodeBsdfPrincipled")
    c2 = K.attr(nt2, "col")
    nt2.links.new(c2.outputs["Color"], b2.inputs["Base Color"])
    b2.inputs["Roughness"].default_value = 0.2
    b2.inputs["Coat Weight"].default_value = 0.6
    b2.inputs["Coat Roughness"].default_value = 0.05
    # v2 r2: the bioluminescent RIM: leaf-green emission on the grazing faces (fresnel), the strands read as lit forms
    lw2 = nt2.nodes.new("ShaderNodeLayerWeight")
    lw2.inputs["Blend"].default_value = 0.5
    rim2 = K.mth(nt2, "MULTIPLY", K.mth(nt2, "POWER", lw2.outputs["Facing"], LH["rim_pow"]), LH["rim_k"])
    b2.inputs["Emission Color"].default_value = tuple(LEAF) + (1.0,)
    nt2.links.new(rim2, b2.inputs["Emission Strength"])
    nt2.links.new(b2.outputs[0], o2.inputs[0])
    m2p = m2.copy()                          # the bridges / podium / crown porcelain WITHOUT the rim
    m2p.name = "porcelain_flat"
    _bp = next(n for n in m2p.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    for l_ in list(_bp.inputs["Emission Strength"].links):
        m2p.node_tree.links.remove(l_)
    _bp.inputs["Emission Strength"].default_value = 0.0
    PORC = Acc("porc", m2p, 1, K.COLL["compound"])
    hooks["accs"]["porc"] = PORC
    DECK = Acc("plinth_deck", K.M["ground"], 1, K.COLL["compound"])   # v3: the plinth deck is NOT the LOD-blurred
    hooks["accs"]["plinth_deck"] = DECK                                 # ground pass (index 4): crisp at any zoom
    APRON = Acc("plaza_apron", K.M["ground"], 3, K.COLL["compound"])   # v3: the street ring round the plinth too
    hooks["accs"]["plaza_apron"] = APRON                                # (index 3: neither landmark nor background)
    _dk = K.HZ["downtown"]
    _kx, _ky = _dk["keep"][1] + _dk["street0"], _dk["keep"][2] + _dk["street0"]
    box(APRON, -_kx, -_ky, 0.0, _kx, _ky, 0.03, (0.11, 0.12, 0.12), k=1.0)

    rt = CP["tube_r"]
    ztop = G.floor_z(TOPF)
    NSEG, DZ = 96, 0.6
    tube_pt = G.tube_pt
    NODE_AT = {(G.TOWER[i], G.FLOOR[i]): i for i in G.NODES if i in G.TOWER}

    # ------------------------------------------------------------ v3 final: FLAT level / plumb oval windows
    # (designer after t3: no bending along the helix). Each window: the oval prism along its normal cuts the skin (head
    # on a true oval), a jamb (the prism's wall) runs back to the window plane, and in that plane sit the flat frame and
    # either frosted glass (non-node: the interiors atlas, translucent look) or, for a node, the open recess room.
    WINS = [(t, f, side) for t in ("A", "B") for f in range(TOPF) for side in ("in", "out")]
    FR = {k: G.win_frame(*k) for k in WINS}
    WAX, NO = G.WAX, 96
    GV, GF, GUV, GK, GC = [], [], [], [], []           # the frosted glass: one UV-mapped mesh (the atlas)
    import os
    atlas_path = K.HZ.get("glass_atlas", r"D:\rc_scratch\hq_rev\solace\v3\glass_atlas.png")

    for t in ("A", "B"):
        near = [k for k in WINS if k[0] == t]
        nz = int((ztop - G.PODIUM_H) / DZ) + 1
        verts = []
        for iz in range(nz):
            z = G.PODIUM_H + iz * DZ
            fl = [k for k in near if abs(z - FR[k]["zc"]) < WB + 1.5]
            for j in range(NSEG):
                p = tube_pt(t, z, 2 * math.pi * j / NSEG)
                for k in fl:                              # snap the ring of vertices nearest the oval onto it
                    fr = FR[k]
                    u, dz, dep = G.win_local(fr, p)
                    if dep <= 0:
                        continue
                    rho = math.hypot(u / WAX, dz / WB)
                    if abs(rho - 1.0) < 0.12:
                        u, dz = u / rho, dz / rho
                        p = G.win_pt(fr, u, dz, G.skin_depth(fr, u, dz))
                        break
                verts.append(p)
        faces = []
        for iz in range(nz - 1):
            z = G.PODIUM_H + (iz + 0.5) * DZ
            fl = [k for k in near if abs(z - FR[k]["zc"]) < WB + 1.5]
            for j in range(NSEG):
                a0, a1 = iz * NSEG + j, iz * NSEG + (j + 1) % NSEG
                q = (a0, a1, a1 + NSEG, a0 + NSEG)
                if fl:
                    cpt = tuple(sum(verts[v][c] for v in q) / 4 for c in range(3))
                    hole = False
                    for k in fl:
                        u, dz, dep = G.win_local(FR[k], cpt)
                        if dep > 0 and math.hypot(u / WAX, dz / WB) < 1.0:
                            hole = True
                            break
                    if hole:
                        continue
                faces.append(q)
        me = bpy.data.meshes.new("strand_" + t)
        me.from_pydata(verts, [], faces)
        me.validate()
        for poly in me.polygons:
            poly.use_smooth = True
        ca = me.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
        ca.data.foreach_set("color", [v for _ in range(len(me.loops)) for v in tuple(POR) + (1.0,)])
        ob = bpy.data.objects.new("strand_" + t, me)
        K.COLL["compound"].objects.link(ob)
        ob.data.materials.append(m2)
        ob.pass_index = 1
        ob["pwo"] = 1.0

        for f in range(TOPF):
            for side in ("in", "out"):
                fr = FR[(t, f, side)]
                node = NODE_AT.get((t, f)) if side == "in" else None
                sk = G.win_skin_outline(fr, NO)
                pl = [G.win_pt(fr, *G.win_uv(k_, NO), fr["dp"]) for k_ in range(NO)]
                for k_ in range(NO):                     # the jamb: the prism's wall from the skin back to the plane
                    k1 = (k_ + 1) % NO
                    PORC.face([sk[k_], sk[k1], pl[k1], pl[k_]], (0.30, 0.32, 0.32))
                fl_ = G.win_plane_outline(fr, 64, 0.12)  # the flat frame ring
                for k_ in range(64):
                    tube(A["metal"], fl_[k_], fl_[(k_ + 1) % 64], WIN["frame_r"], (0.55, 0.58, 0.6), n=5)
                if node:
                    continue
                # frosted glass: a flat polar grid in the plane, UV-mapped to one atlas tile, tinted per window
                tile = rr.randrange(16)
                tu, tv = tile % 4, 3 - tile // 4
                lit = rr.random() < 0.9
                tint = (rr.uniform(0.85, 1.0), 1.0, rr.uniform(0.85, 1.0))
                kg = LH["porthole_k"] * LH.get("glass_k", 1.0)
                kk = kg * rr.uniform(0.8, 1.15) if lit else kg * 0.15
                NA, NRg = 48, 4
                for a in range(NA):
                    a0, a1 = 2 * math.pi * a / NA, 2 * math.pi * (a + 1) / NA
                    for g in range(NRg):
                        r0, r1 = g / NRg, (g + 1) / NRg
                        quad = [(rho_ * math.cos(an), rho_ * math.sin(an)) for (rho_, an) in
                                ((r0, a0), (r1, a0), (r1, a1), (r0, a1))]
                        b_ = len(GV)
                        for (cu, cv) in quad:
                            GV.append(G.win_pt(fr, cu * WAX, cv * WB, fr["dp"] + 0.03))
                            GUV.append(((tu + 0.03 + 0.94 * (cu + 1) / 2) / 4, (tv + 0.03 + 0.94 * (cv + 1) / 2) / 4))
                        GF.append((b_, b_ + 1, b_ + 2, b_ + 3))
                        GK.append(kk)
                        GC.append(tint)
        # the light rising inside: a continuous mint seam up the back band (between the windows, away from the stair)
        prev = None
        z = G.PODIUM_H
        while z <= ztop:
            p = tube_pt(t, z, G.stair_phi(t) + math.pi, rt + 0.1)
            if prev is not None:
                tube(A["trim"], prev, p, 0.45, (0.55, 1.0, 0.72), LH["atrium_k"], n=6)   # pale mint: never the route lime
            prev = p
            z += 2.0
        for f in range(TOPF):                            # the downlight ring under every floor
            zd = G.floor_z(f) + 0.3
            for q in range(NSEG):
                p0 = tube_pt(t, zd, 2 * math.pi * q / NSEG, rt + 0.08)
                p1 = tube_pt(t, zd, 2 * math.pi * (q + 1) / NSEG, rt + 0.08)
                A["trim"].face([p0, p1, (p1[0], p1[1], p1[2] + 0.25), (p0[0], p0[1], p0[2] + 0.25)], (1.0, 0.95, 0.85),
                               LH["down_k"])
            if f % 2 == 1:
                c, rv, n = G.tower_frame(t, f)
                for nn_ in (n, rv):
                    p = (c[0] + nn_[0] * (rt + 1.5), c[1] + nn_[1] * (rt + 1.5), G.floor_z(f) - 0.2)
                    K.add_light("down_%s_%d_%.1f" % (t, f, nn_[0]), "SPOT", p, LH["down_w"], (1.0, 0.95, 0.85),
                                aim=(p[0], p[1], p[2] - 30.0), size=0.6, spot=80, blend=0.9, group="corp", shadow=False)

    # the frosted glass object (emission = the atlas x the window's tint x k; a glossy coat over it)
    mg, ntg = K.new_mat("frost_glass")
    og = ntg.nodes.new("ShaderNodeOutputMaterial")
    bg_ = ntg.nodes.new("ShaderNodeBsdfPrincipled")
    bg_.inputs["Base Color"].default_value = (0.02, 0.03, 0.03, 1.0)
    bg_.inputs["Roughness"].default_value = 0.35
    bg_.inputs["Coat Weight"].default_value = 0.5
    bg_.inputs["Coat Roughness"].default_value = 0.08
    img = bpy.data.images.load(atlas_path) if os.path.exists(atlas_path) else None
    tex = ntg.nodes.new("ShaderNodeTexImage")
    if img is not None:
        tex.image = img
    tex.interpolation = "Cubic"
    gc_ = K.attr(ntg, "col")
    mul = ntg.nodes.new("ShaderNodeMix")
    mul.data_type = "RGBA"
    mul.blend_type = "MULTIPLY"
    mul.inputs["Factor"].default_value = 1.0
    ntg.links.new(tex.outputs["Color"], mul.inputs[6])
    ntg.links.new(gc_.outputs["Color"], mul.inputs[7])
    ntg.links.new(mul.outputs[2], bg_.inputs["Emission Color"])
    gk_ = K.attr(ntg, "k")
    gp_ = K.attr(ntg, "pwo", "OBJECT")
    ntg.links.new(K.mth(ntg, "MULTIPLY", gk_.outputs["Fac"], gp_.outputs["Fac"]), bg_.inputs["Emission Strength"])
    ntg.links.new(bg_.outputs[0], og.inputs[0])
    gme = bpy.data.meshes.new("frost_glass")
    gme.from_pydata(GV, [], GF)
    gme.validate()
    uvl = gme.uv_layers.new(name="UVMap")
    for poly in gme.polygons:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            uvl.data[li].uv = GUV[vi]
    gka = gme.attributes.new("k", "FLOAT", "FACE")
    gka.data.foreach_set("value", GK[:len(gme.polygons)])
    gca = gme.color_attributes.new("col", "FLOAT_COLOR", "CORNER")
    gca.data.foreach_set("color", [c for poly in gme.polygons for _ in poly.loop_indices
                                   for c in tuple(GC[poly.index]) + (1.0,)])
    GLASS_OB = bpy.data.objects.new("frost_glass", gme)
    K.COLL["compound"].objects.link(GLASS_OB)
    GLASS_OB.data.materials.append(mg)
    GLASS_OB.pass_index = 1
    GLASS_OB["pwo"] = 1.0
    log("strands + flat windows", len(GF), "glass faces", "atlas" if img else "NO ATLAS")

    # ------------------------------------------------------------ the node rooms: the open recess behind the oval
    LOCKS = {}
    no_light = []
    for i in G.NODES:
        if i not in G.TOWER:
            continue
        fr = FR[(G.TOWER[i], G.FLOOR[i], "in")]
        dp = fr["dp"]
        em = K.ROOM_EMIT.setdefault(i, Acc("room_" + i, K.M["emit"], 5, K.COLL["rooms"]))
        dzf = G.deck_z(G.FLOOR[i]) - fr["zc"] - 0.02
        um = WAX * math.sqrt(max(0.0, 1.0 - (dzf / WB) ** 2))
        for s_ in range(24):                             # the recess floor (level with the bridge deck)
            u0, u1 = -um + 2 * um * s_ / 24, -um + 2 * um * (s_ + 1) / 24
            A["int"].face([G.win_pt(fr, u0, dzf, dp), G.win_pt(fr, u1, dzf, dp),
                           G.win_pt(fr, u1, dzf, G.skin_depth(fr, u1, dzf) - 0.05),
                           G.win_pt(fr, u0, dzf, G.skin_depth(fr, u0, dzf) - 0.05)], (0.32, 0.33, 0.35))
        for a in range(48):                              # the back wall (the window plane)
            a0, a1 = 2 * math.pi * a / 48, 2 * math.pi * (a + 1) / 48
            A["int"].face([G.win_pt(fr, 0.0, 0.0, dp), G.win_pt(fr, WAX * math.cos(a1), WB * math.sin(a1), dp),
                           G.win_pt(fr, WAX * math.cos(a0), WB * math.sin(a0), dp)], (0.62, 0.65, 0.68))
        tc = K.TYPE_COL.get(G.KIND[i], (1, 1, 1))
        kind = G.KIND[i]

        def panel(u0, u1, z0, z1, kk, col=tc):
            em.face([G.win_pt(fr, u0, z0, dp + 0.05), G.win_pt(fr, u1, z0, dp + 0.05), G.win_pt(fr, u1, z1, dp + 0.05),
                     G.win_pt(fr, u0, z1, dp + 0.05)], col, kk)
        h0 = dzf + 0.6
        if kind == "router":
            for m_ in range(4):
                a_ = -0.62 * WAX + m_ * 0.31 * WAX
                panel(a_ + 0.15, a_ + 0.31 * WAX - 0.15, h0 + 1.2, h0 + 3.4, 3.2)
        elif kind == "elite":
            for m_ in range(3):
                a_ = -0.45 * WAX + m_ * 0.45 * WAX
                panel(a_ - 0.18, a_ + 0.18, h0, h0 + 4.6, 4.0)
        elif kind == "terminal":
            panel(-0.5 * WAX, 0.5 * WAX, h0 + 0.8, h0 + 4.0, 2.6)
        else:
            for sh in range(3):
                panel(-0.6 * WAX, 0.6 * WAX, h0 + 0.4 + sh * 1.5, h0 + 0.7 + sh * 1.5, 3.0)
        panel(-0.45 * WAX, 0.45 * WAX, 0.72 * WB, 0.80 * WB, 4.0, (0.85, 0.95, 1.0))      # the ceiling light bar
        lp = G.win_pt(fr, 0.0, 1.2, (dp + G.skin_depth(fr, 0.0, 0.0)) * 0.5)
        K.add_light("room_%s" % i, "POINT", lp, LH["room_w"] * LH.get("node_room_k", 0.6), (1, 1, 1), size=1.5,
                    group="room:" + i)
        no_light.append(i)
        # unread: a frosted flat oval over the opening + a frost ring
        fa = Acc("frost_%s" % i, K.M["lock"], 5, K.COLL["rooms"])
        fb = Acc("frostf_%s" % i, K.M["emit"], 5, K.COLL["rooms"])
        for a in range(64):
            a0, a1 = 2 * math.pi * a / 64, 2 * math.pi * (a + 1) / 64
            fa.face([G.win_pt(fr, 0.0, 0.0, dp + 0.3), G.win_pt(fr, WAX * math.cos(a1), WB * math.sin(a1), dp + 0.3),
                     G.win_pt(fr, WAX * math.cos(a0), WB * math.sin(a0), dp + 0.3)], pal("frost"))
        ring = G.win_plane_outline(fr, 48, 0.35)
        for q in range(48):
            tube(fb, ring[q], ring[(q + 1) % 48], 0.16, pal("frost"), 6.0, n=4)
        LOCKS[i] = (fa, fb)
    hooks["no_room_light"] = tuple(no_light)
    log("rooms")

    # ------------------------------------------------------------ the bow-tie skybridges (route floors: inward to inward)
    wide, waist = CP["bridge_w"]
    s_end = R - rt * 0.97                         # v3 final: the deck ends at the skin, in the node's recess

    def hw(s):
        return waist / 2 + (wide - waist) / 2 * (abs(s) / s_end) ** 1.6

    for f in sorted(RFS):
        zb = G.deck_z(f)
        c, rv, n = G.tower_frame("A", (zb - G.PODIUM_H) / FH)
        NS = 14

        def P(s, side, z):
            return (rv[0] * s + n[0] * side * hw(s), rv[1] * s + n[1] * side * hw(s), z)
        for k in range(NS):
            s0 = -s_end + 2 * s_end * k / NS
            s1 = -s_end + 2 * s_end * (k + 1) / NS
            PORC.face([P(s0, -1, zb), P(s1, -1, zb), P(s1, 1, zb), P(s0, 1, zb)], POR)
            PORC.face([P(s0, 1, zb - 0.8), P(s1, 1, zb - 0.8), P(s1, -1, zb - 0.8), P(s0, -1, zb - 0.8)], POR)
            for side in (-1, 1):
                A["trim"].face([P(s0, side, zb + 0.4), P(s1, side, zb + 0.4), P(s1, side, zb + 3.6), P(s0, side, zb + 3.6)],
                               (0.75, 1.0, 0.85), LH["bridge_wall_k"] * 1.6)
                PORC.face([P(s0, side, zb - 0.8), P(s1, side, zb - 0.8), P(s1, side, zb), P(s0, side, zb)], POR)
            PORC.face([P(s0, -1, zb + 3.8), P(s1, -1, zb + 3.8), P(s1, 1, zb + 4.0), P(s0, 1, zb + 4.0)], POR)
            kb = LH["bridge_route_k"]
            A["trim"].face([P(s0, -0.35, zb + 0.03), P(s1, -0.35, zb + 0.03), P(s1, 0.35, zb + 0.03), P(s0, 0.35, zb + 0.03)],
                           CLIN, kb)
            A["trim"].face([P(s0, 0.5, zb + 3.75), P(s1, 0.5, zb + 3.75), P(s1, -0.5, zb + 3.75), P(s0, -0.5, zb + 3.75)],
                           (0.7, 1.0, 0.75), kb * 0.5)
    log("bridges")

    # ------------------------------------------------------------ the UP stairs: a ribbon up each strand's front band
    for (a, b_) in G.PATH:
        et = G.edge_type(a, b_)
        if et == "bridge":
            continue
        pth = [p for p in G.edge_path(a, b_) if p[2] > G.PODIUM_H + 0.2]
        for p, q in zip(pth, pth[1:]):
            K.seg_box(A["metal"], Vector(p) + Vector((0, 0, -1.55)), Vector(q) + Vector((0, 0, -1.55)), 1.8, 0.25,
                      (0.42, 0.45, 0.45))
    log("stairs")
    # ------------------------------------------------------------ the crown + THE GENOME CORE
    c, rv, n = G.tower_frame("A", TOPF)
    zc = G.floor_z(TOPF)
    ch = CP["crown_h"]
    crown = dict(o=(n[0] * TW / 2, n[1] * TW / 2, 0.0), n=n)
    for (s0, s1) in ((-R - TD / 2, -11.0), (11.0, R + TD / 2)):
        obox(PORC, crown, s0, s1, -TW, 0.0, zc, zc + 1.5, POR)
        obox(A["glass"], crown, s0, s1, -TW, 0.0, zc + 1.5, zc + ch, (0.015, 0.04, 0.03))
        obox(PORC, crown, s0, s1, -TW, 0.0, zc + ch, zc + ch + 1.5, POR)
        oquad(A["trim"], crown, 0.05, s0 + 1.0, zc + 4.0, s1 - 1.0, zc + ch - 3.0, CLIN, LH["band_k"])
    obox(PORC, crown, -11.0, 11.0, -TW, 0.0, zc, zc + 1.5, POR)
    obox(PORC, crown, -11.0, 11.0, -TW, 0.0, zc + ch, zc + ch + 1.5, POR)
    emv = K.ROOM_EMIT.setdefault("srv", Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"]))
    so = G.ROOM["srv"]["o"]
    tube(A["metal"], (so[0], so[1], zc + 1.5), (so[0], so[1], zc + ch), 3.4, (0.08, 0.08, 0.1), n=16)
    for k_ in range(8):
        zz = zc + 2.5 + k_ * 1.4
        tube(emv, (so[0], so[1], zz), (so[0], so[1], zz + 0.3), 3.5, (1.0, 0.22, 0.08), 6.0, n=24)
    for k in range(48):
        a0, a1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
        tube(A["trim"], (math.sin(a0) * 20, math.cos(a0) * 20, zc + ch + 8.0),
             (math.sin(a1) * 20, math.cos(a1) * 20, zc + ch + 8.0), 0.5, PINK, 3.0, n=4)
    K.add_light("crown_glow", "POINT", (0, 0, zc + ch + 6.0), 2.0e4, PINK, size=3.0, group="corp", shadow=False)
    log("crown")

    # ------------------------------------------------------------ the podium + the clinic gate + the name
    px, py, ph = CP["podium"]
    PL = (0.09, 0.10, 0.10)                  # v2 r2: the plinth dark (was pale 0.45), dressed, a lit entry
    box(PORC, -px, -py, 0.0, px, py, ph, PL)
    box(DECK, -px + 1, -py + 1, ph, px - 1, py - 1, ph + 0.02, (0.11, 0.12, 0.12), k=1.0)   # v3: crisp
    # dressing: planter beds with leaf-green edge light, bollards, a slatted base course
    prr = random.Random(6331)
    for (qx, qy) in ((-46.0, -34.0), (46.0, -34.0), (-46.0, 34.0), (46.0, 34.0), (-52.0, 0.0), (52.0, 0.0)):
        box(A["rough"], qx - 6.0, qy - 3.0, ph, qx + 6.0, qy + 3.0, ph + 1.0, (0.06, 0.07, 0.06))
        box(A["trim"], qx - 6.05, qy - 3.05, ph + 0.95, qx + 6.05, qy + 3.05, ph + 1.05, LEAF, LH["trim_k"] * 0.5)
        for _ in range(5):
            tx_, ty_ = qx + prr.uniform(-5, 5), qy + prr.uniform(-2.4, 2.4)
            tube(A["rough"], (tx_, ty_, ph + 1.0), (tx_, ty_, ph + prr.uniform(2.0, 3.6)), prr.uniform(0.5, 0.9),
                 (0.03, 0.08, 0.04), n=6)
    for k_ in range(int(2 * px / 4)):
        xx = -px + 2.0 + k_ * 4.0
        box(A["metal"], xx - 0.2, -py - 0.25, 0.4, xx + 0.2, -py, ph - 0.8, (0.16, 0.17, 0.17))
    # THE LIT ENTRY: a glazed clinic lobby at the top of the stair (warm-white light inside, a leaf-green lintel)
    box(A["glass"], -12.0, -py + 0.5, ph, 12.0, -py + 6.0, ph + 7.0, (0.02, 0.05, 0.04))
    box(A["trim"], -11.0, -py + 0.45, ph + 0.4, 11.0, -py + 0.5, ph + 6.2, (1.0, 0.92, 0.78), 2.6)
    box(PORC, -13.0, -py - 1.5, ph + 7.0, 13.0, -py + 6.5, ph + 8.0, PL)
    box(A["trim"], -13.0, -py - 1.55, ph + 7.2, 13.0, -py - 1.5, ph + 7.8, LEAF, LH["trim_k"])
    K.add_light("entry_glow", "AREA", (0.0, -py - 3.0, ph + 6.5), LH["entry_w"], (1.0, 0.88, 0.7),
                aim=(0.0, -py - 6.0, ph * 0.5), size=22.0, size_y=4.0, group="corp", shadow=False, receivers=PLX)
    for (x0, y0, x1, y1) in ((-px, -py - 0.06, px, -py), (-px, py, px, py + 0.06), (-px - 0.06, -py, -px, py),
                             (px, -py, px + 0.06, py)):
        box(A["trim"], x0, y0, ph - 0.6, x1, y1, ph - 0.35, LEAF, LH["trim_k"] * 0.6)
    for s in range(6):
        box(PORC, -18.0, -py - (6 - s) * 1.4, 0.0, 18.0, -py, ph * (s + 1) / 6, PL)
        box(A["trim"], -18.0, -py - (6 - s) * 1.4 - 0.03, ph * (s + 1) / 6 - 0.12, 18.0, -py - (6 - s) * 1.4,
            ph * (s + 1) / 6 - 0.04, (1.0, 0.9, 0.75), 1.2)                      # lit stair nosings
    sx_, sy_ = CP["start"]
    box(PORC, sx_ - 5, sy_ - 3, 0, sx_ + 5, sy_ + 3, 4.6, PL)
    box(A["trim"], sx_ - 0.4, sy_ - 3.1, 6.0, sx_ + 0.4, sy_ - 3.0, 8.4, LEAF, 4.0)
    box(A["trim"], sx_ - 1.2, sy_ - 3.1, 6.8, sx_ + 1.2, sy_ - 3.0, 7.6, LEAF, 4.0)
    box(A["trim"], sx_ - 4.4, sy_ - 3.2, 1.4, sx_ - 3.4, sy_ - 2.8, 2.8, (0.55, 1.0, 0.0), 6.0)
    K.add_light("hack", "POINT", (sx_ - 4.6, sy_ - 3.6, 2.0), 120.0, (0.55, 1.0, 0.0), size=0.3, group="start")
    STEN = {"S": ["0111", "1000", "0110", "0001", "1110"], "O": ["0110", "1001", "1001", "1001", "0110"],
            "L": ["1000", "1000", "1000", "1000", "1111"], "A": ["0110", "1001", "1111", "1001", "1001"],
            "C": ["0111", "1000", "1000", "1000", "0111"], "E": ["1111", "1000", "1110", "1000", "1111"]}
    rec = dict(o=(30.0, -py - 0.1, 0.0), n=(0.0, -1.0))
    cell = 0.62
    word = "SOLACE"
    wl = sum((len(STEN[ch_][0]) + 1) * cell for ch_ in word)
    uu = -wl / 2
    for ch_ in word:
        gph = STEN[ch_]
        for row, bits in enumerate(gph):
            for cix, bit in enumerate(bits):
                if bit == "1":
                    oquad(A["sign"], rec, 0.05, -(uu + (cix + 1) * cell - cell * 0.15), 0.9 + (4 - row) * cell * 0.8,
                          -(uu + cix * cell), 0.9 + (5 - row) * cell * 0.8 - cell * 0.12, LEAF, 6.0 * LH["sign_k"] * 4)
        uu += (len(gph[0]) + 1) * cell
    # v2 (review: Solace too dark overall): the plaza's own WARM WASH (low area lights over the deck, clinic-warm)
    for k, (wx, wy) in enumerate(((-34.0, -26.0), (34.0, -26.0), (-34.0, 26.0), (34.0, 26.0))):
        K.add_light("plaza_wash_%d" % k, "AREA", (wx, wy, ph + 16.0), LH["plaza_wash_w"], (1.0, 0.78, 0.55),
                    aim=(wx, wy, ph), size=40.0, size_y=30.0, group="corp", shadow=False, receivers=PLX)
    log("podium")

    # ============================================================ THE LANDMARK RIG (designer audit + redesign)
    RIMRX = bpy.data.collections.new("rim_rx")
    for k in range(8):                                # big ground spots at the base, aimed up the towers
        a = 22.5 + 45.0 * k
        v = G.az_vec(a)
        p = (v[0] * 58.0, v[1] * 46.0, ph + 0.4)
        K.add_light("ground_spot_%d" % k, "SPOT", p, LH["ground_spot_w"], CLIN if k % 2 else (0.75, 1.0, 0.7),
                    aim=(v[0] * 6.0, v[1] * 6.0, 110.0), size=1.5, spot=26, blend=0.5, group="corp", receivers=RIMRX)
        box(A["small"], p[0] - 1.2, p[1] - 1.2, p[2], p[0] + 1.2, p[1] + 1.2, p[2] + 0.6, CLIN, 8.0)
        if k % 4 == 0 and LH.get("plinth_beams", False):     # v3: off (their lit haze blurred the plinth)
            hooks["beams"].append((p, (v[0] * 0.10, v[1] * 0.10, 1.0), CLIN, K.HZ["beams"]["power"], K.HZ["beams"]["cone"]))
    for k in range(4):
        a = 45.0 + 90.0 * k
        v = G.az_vec(a)
        K.add_light("rim_%d" % k, "AREA", (v[0] * 230.0, v[1] * 230.0, 70.0), LH["rim_w"],
                    pal("district_a" if k % 2 else "district_b"), aim=(0.0, 0.0, 90.0), size=90.0, size_y=140.0,
                    group="corp", shadow=False, receivers=RIMRX)
    mb, ntb = K.new_mat("halo")
    ob_ = ntb.nodes.new("ShaderNodeOutputMaterial")
    gb, psb, nsb = K.pos_sep(ntb)
    rr_ = K.mth(ntb, "SQRT", K.mth(ntb, "ADD", K.mth(ntb, "POWER", psb.outputs["X"], 2.0),
                                   K.mth(ntb, "POWER", psb.outputs["Y"], 2.0)))
    band = K.mth(ntb, "MULTIPLY", K.smooth(ntb, rr_, LH["halo_r"][0], LH["halo_r"][0] + 30.0),
                 K.mth(ntb, "SUBTRACT", 1.0, K.smooth(ntb, rr_, LH["halo_r"][1] - 30.0, LH["halo_r"][1])))
    nzb = K.nn(ntb, "ShaderNodeTexNoise", Scale=0.03, Detail=3.0, Roughness=0.55)
    ntb.links.new(gb.outputs["Position"], nzb.inputs["Vector"])
    hfb = K.mth(ntb, "SUBTRACT", 1.0, K.smooth(ntb, psb.outputs["Z"], 8.0, LH["halo_h"]))
    db = K.mth(ntb, "MULTIPLY", K.mth(ntb, "MULTIPLY", K.mth(ntb, "MULTIPLY", K.smooth(ntb, nzb.outputs["Fac"], 0.35, 0.65),
                                                              hfb), band), LH["halo_peak"])
    vsb = ntb.nodes.new("ShaderNodeVolumeScatter")
    vsb.inputs["Color"].default_value = (0.85, 0.92, 0.9, 1.0)
    vsb.inputs["Anisotropy"].default_value = 0.3
    ntb.links.new(db, vsb.inputs["Density"])
    ntb.links.new(vsb.outputs[0], ob_.inputs["Volume"])
    r1 = LH["halo_r"][1]
    mesh = bpy.data.meshes.new("halo")
    mesh.from_pydata([(-r1, -r1, 0), (r1, -r1, 0), (r1, r1, 0), (-r1, r1, 0), (-r1, -r1, LH["halo_h"] + 10),
                      (r1, -r1, LH["halo_h"] + 10), (r1, r1, LH["halo_h"] + 10), (-r1, r1, LH["halo_h"] + 10)], [],
                     [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    obh = bpy.data.objects.new("halo", mesh)
    K.COLL["media"].objects.link(obh)
    obh.data.materials.append(mb)
    for k in range(10):
        a = 36.0 * k
        v = G.az_vec(a)
        rm = (LH["halo_r"][0] + LH["halo_r"][1]) / 2
        K.add_light("halofill_%d" % k, "AREA", (v[0] * rm, v[1] * rm, 0.5), LH["halo_fill_w"],
                    CLIN, aim=(v[0] * rm, v[1] * rm, 40.0), size=60.0, size_y=40.0,
                    group="corp", shadow=False, receivers=K.COLL["media"])
    log("rig")

    def post_build(OBJ):
        for i, (a, b_) in list(LOCKS.items()):
            LOCKS[i] = (a.build(), b_.build())
        for name, ob in OBJ.items():
            if ob is not None and any(c_.name in ("compound", "rooms") for c_ in ob.users_collection):
                RIMRX.objects.link(ob)
            if ob is not None and any(c_.name in ("compound", "rooms", "ground") for c_ in ob.users_collection):
                PLX.objects.link(ob)
    hooks["post_build"] = post_build

    def apply(fr, ctx):
        ctx["set_pwo"](GLASS_OB, ctx.get("cut", 1.0))
        un = set(fr.get("affected") or [])
        for i, (a, b_) in LOCKS.items():
            for o in (a, b_):
                if o is None:
                    continue
                o.hide_render = i not in un
                ctx["set_pwo"](o, 0.35)
        for (lob, e0, grp) in ctx["LIGHTS"]:
            if grp.startswith("room:") and grp[5:] in un:
                lob.data.energy *= 0.25
                lob.data.color = pal("frost")
    hooks["apply"] = apply
    return hooks
# SOL_R2
