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
    # v4: the skin's BACK side is the office wall (lit warm grey), the front the wet porcelain
    inn = nt2.nodes.new("ShaderNodeBsdfPrincipled")
    inn.inputs["Base Color"].default_value = (0.52, 0.50, 0.47, 1.0)
    inn.inputs["Emission Color"].default_value = (0.85, 0.82, 0.76, 1.0)
    inn.inputs["Emission Strength"].default_value = 0.22
    inn.inputs["Roughness"].default_value = 0.7
    geo2 = nt2.nodes.new("ShaderNodeNewGeometry")
    mix2 = nt2.nodes.new("ShaderNodeMixShader")
    nt2.links.remove(o2.inputs[0].links[0])
    nt2.links.new(geo2.outputs["Backfacing"], mix2.inputs[0])
    nt2.links.new(b2.outputs[0], mix2.inputs[1])
    nt2.links.new(inn.outputs[0], mix2.inputs[2])
    nt2.links.new(mix2.outputs[0], o2.inputs[0])
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

    # ------------------------------------------------------------ v4: REAL CUTAWAY windows + an office floor behind each
    # (designer v4): no surface textures. Each window is a modelled opening in the tube wall (the skin's vertices snapped
    # onto the oval, a thick jamb back from the skin edge, a metal frame ring); behind it is a thin clear glass patch that
    # follows the skin, and behind that the floor's own office (hq_office: slab, core, conference rooms, cubicle rows,
    # plants, ceiling panels, tiny people). The skin's back side is the office wall (backface shader). The 8 route
    # floors' inward windows are open (no glass): the node, with the skybridge running in through the cutaway.
    import hq_office as OFC
    OC = CP.get("office", {})
    PERSON_H = OC.get("person_h", 2.4)
    import os
    MODE = os.environ.get("HQ_INTERIOR", OC.get("mode", "hybrid"))        # hybrid (default) | built | map
    MV, MF, M_LOC, M_FRM, M_VST, M_TNT = [], [], [], [], [], []
    IM_NV = OC.get("imap_variants", 6)
    A_LO, A_HI = OC.get("a_floors", (5, 13))              # hybrid: built scenes on the route floors + these (the decision's frame)

    def built_floor(f_):
        return MODE == "built" or (MODE == "hybrid" and (f_ in RFS or A_LO <= f_ <= A_HI))
    WINS = [(t, f, side) for t in ("A", "B") for f in range(TOPF) for side in ("in", "out")]
    FR = {k: G.win_frame(*k) for k in WINS}
    WAX, NO = G.WAX, 96
    JAMB = 0.6

    mo, nto = K.new_mat("office")
    oo = nto.nodes.new("ShaderNodeOutputMaterial")
    bo = nto.nodes.new("ShaderNodeBsdfPrincipled")
    co_ = K.attr(nto, "col")
    nto.links.new(co_.outputs["Color"], bo.inputs["Base Color"])
    nto.links.new(co_.outputs["Color"], bo.inputs["Emission Color"])
    bo.inputs["Roughness"].default_value = 0.6
    ko_ = K.attr(nto, "k")
    po_ = K.attr(nto, "pwo", "OBJECT")
    nto.links.new(K.mth(nto, "MULTIPLY", ko_.outputs["Fac"], po_.outputs["Fac"]), bo.inputs["Emission Strength"])
    nto.links.new(bo.outputs[0], oo.inputs[0])
    mg, ntg = K.new_mat("win_glass")                    # clear glass: transparent, a faint fresnel reflection
    og = ntg.nodes.new("ShaderNodeOutputMaterial")
    trn = ntg.nodes.new("ShaderNodeBsdfTransparent")
    gls = ntg.nodes.new("ShaderNodeBsdfGlossy")
    gls.inputs["Roughness"].default_value = 0.12
    gls.inputs["Color"].default_value = (0.8, 0.92, 0.86, 1.0)
    fre = ntg.nodes.new("ShaderNodeFresnel")
    fre.inputs["IOR"].default_value = 1.45
    mxg = ntg.nodes.new("ShaderNodeMixShader")
    ntg.links.new(K.mth(ntg, "MULTIPLY", fre.outputs[0], 0.15), mxg.inputs[0])
    ntg.links.new(trn.outputs[0], mxg.inputs[1])
    ntg.links.new(gls.outputs[0], mxg.inputs[2])
    ntg.links.new(mxg.outputs[0], og.inputs[0])
    OFF = Acc("office", mo, 1, K.COLL["compound"])
    OG = Acc("win_glass", mg, 1, K.COLL["compound"])
    LAMP = Acc("office_lamp", K.M["emit"], 1, K.COLL["compound"])
    hooks["accs"].update({"office": OFF, "win_glass": OG, "office_lamp": LAMP})
    FLOOR_COL, FLOOR_K = (0.22, 0.21, 0.195), 0.20      # the office floor AND the skybridge deck top: one material
    OACC = {"off": OFF, "glass": OG, "lamp": LAMP}
    ostats = dict(boxes=0, people=0, cubicles=0, conf=0, plants=0)

    def kind_panels(i):
        em_ = K.ROOM_EMIT.setdefault(i, Acc("room_" + i, K.M["emit"], 5, K.COLL["rooms"]))
        tc_ = K.TYPE_COL.get(G.KIND[i], (1, 1, 1))
        kind_ = G.KIND[i]

        def f_(o, ex, ey, zf):
            def panel(u0, u1, z0, z1, kk):
                em_.face([(o[0] + ex[0] * u + ey[0] * 0.05, o[1] + ex[1] * u + ey[1] * 0.05, z) for (u, z) in
                          ((u0, z0), (u1, z0), (u1, z1), (u0, z1))], tc_, kk)
            h0 = zf + 0.6
            if kind_ == "router":
                for m_ in range(4):
                    a_ = -2.0 + m_ * 1.0
                    panel(a_ + 0.12, a_ + 0.88, h0, h0 + 2.0, 3.0)
            elif kind_ == "elite":
                for m_ in range(3):
                    a_ = -1.5 + m_ * 1.5
                    panel(a_ - 0.25, a_ + 0.25, h0, h0 + 2.6, 3.6)
            elif kind_ == "terminal":
                panel(-1.8, 1.8, h0 + 0.2, h0 + 2.2, 2.6)
            else:
                for sh in range(3):
                    panel(-2.0, 2.0, h0 + 0.2 + sh * 0.8, h0 + 0.45 + sh * 0.8, 3.0)
        return f_

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
        # outward normals (the skin's back side is the office wall): flip the winding if the first quad faces the axis
        q0 = faces[0]
        v0, v1, v3 = Vector(verts[q0[0]]), Vector(verts[q0[1]]), Vector(verts[q0[3]])
        nrm = (v1 - v0).cross(v3 - v0)
        cax = tube_pt(t, verts[q0[0]][2], 0.0, 0.0)
        if nrm.x * (v0.x - cax[0]) + nrm.y * (v0.y - cax[1]) < 0:
            faces = [tuple(reversed(f_)) for f_ in faces]
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
            # ---- the office floor behind this floor's two windows
            node_i = NODE_AT.get((t, f))
            if not built_floor(f):
                pass
            else:
                OFC.slab(G, t, f, OACC, FLOOR_COL, (0.12, 0.14, 0.14), FLOOR_K)
            orng = random.Random(6400 + 100 * f + (0 if t == "A" else 1))
            CH = OC.get("ceil_h", 4.0)
            zl = G.deck_z(f)
            zu = zl + CH + 0.4                                # the mezzanine storey: its own desks, core, people
            if built_floor(f):
                OFC.slab(G, t, f, OACC, FLOOR_COL, (0.12, 0.14, 0.14), FLOOR_K, z0=zl + CH, z1=zu)   # the mezzanine floor
                OFC.ceiling_disc(G, t, zu + CH, OACC)
                for (zs, npan) in ((zl, None), (zu, kind_panels(node_i) if node_i else None)):
                    st_ = OFC.floor_interior(G, t, f, OACC, orng, PERSON_H, npan, zf=zs, ceil_h=CH)
                    for k_, v_ in st_.items():
                        ostats[k_] += v_
            for side in ("in", "out"):
                fr = FR[(t, f, side)]
                node = node_i if side == "in" else None
                sk = G.win_skin_outline(fr, NO)
                for k_ in range(NO):                     # the jamb: the wall's thickness round the opening
                    k1 = (k_ + 1) % NO
                    ins = []
                    for kk_ in (k_, k1):
                        c_ = tube_pt(t, sk[kk_][2], 0.0, 0.0)
                        dx, dy = c_[0] - sk[kk_][0], c_[1] - sk[kk_][1]
                        L_ = math.hypot(dx, dy)
                        ins.append((sk[kk_][0] + dx / L_ * JAMB, sk[kk_][1] + dy / L_ * JAMB, sk[kk_][2]))
                    PORC.face([sk[k_], sk[k1], ins[1], ins[0]], (0.30, 0.32, 0.32))
                fl_ = G.win_skin_outline(fr, 64, 0.06)   # the frame ring on the skin
                for k_ in range(64):
                    tube(A["metal"], fl_[k_], fl_[(k_ + 1) % 64], WIN["frame_r"], (0.55, 0.58, 0.6), n=5)
                if not built_floor(f):
                    wr = orng
                    if node:
                        lit_, blind_, tnt_ = 1.0, 0.0, tuple(0.65 + 0.35 * c_ for c_ in K.TYPE_COL.get(G.KIND[node], (1, 1, 1)))
                    else:
                        lit_ = 1.0 if wr.random() < 0.84 else 0.0
                        blind_ = wr.uniform(0.3, 0.95) if wr.random() < 0.22 else 0.0
                        tnt_ = (wr.uniform(0.85, 1.0), wr.uniform(0.85, 1.0), wr.uniform(0.8, 1.0))
                    var_ = float(wr.randrange(IM_NV))
                    for a in range(48):
                        a0, a1 = 2 * math.pi * a / 48, 2 * math.pi * (a + 1) / 48
                        for g in range(4):
                            r0, r1 = g / 4, (g + 1) / 4
                            b0 = len(MV)
                            for (rho_, an) in ((r0, a0), (r1, a0), (r1, a1), (r0, a1)):
                                u_, dz_ = rho_ * WAX * math.cos(an), rho_ * WB * math.sin(an)
                                dd_ = G.skin_depth(fr, u_, dz_) - 0.2
                                MV.append(G.win_pt(fr, u_, dz_, dd_))
                                M_LOC.append((u_ + 32.0, dz_ + 32.0, dd_ + 64.0, 1.0))
                                M_FRM.append((fr["tw"][0] + 2.0, fr["tw"][1] + 2.0, fr["nw"][0] + 2.0, fr["nw"][1] + 2.0))
                                M_VST.append((var_, lit_, blind_, 1.0))
                                M_TNT.append(tuple(tnt_) + (1.0,))
                            MF.append((b0, b0 + 1, b0 + 2, b0 + 3))
                    continue
                if node:
                    continue
                for a in range(48):                      # the clear glass patch, 0.2 inside the skin
                    a0, a1 = 2 * math.pi * a / 48, 2 * math.pi * (a + 1) / 48
                    for g in range(4):
                        r0, r1 = g / 4, (g + 1) / 4
                        quad = []
                        for (rho_, an) in ((r0, a0), (r1, a0), (r1, a1), (r0, a1)):
                            u_, dz_ = rho_ * WAX * math.cos(an), rho_ * WB * math.sin(an)
                            quad.append(G.win_pt(fr, u_, dz_, G.skin_depth(fr, u_, dz_) - 0.2))
                        OG.face(quad, (0.8, 0.9, 0.85))
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
    MAPOB = None
    if MV:
        import hq_imap as IM
        atlas_p = OC.get("imap_atlas", "D:/rc_scratch/hq_rev/solace/v4/atlas/imap_atlas.png")
        mim = IM.material(K, atlas_p, IM_NV, LH.get("imap_k", 0.55))
        me_ = bpy.data.meshes.new("imap_glass")
        me_.from_pydata(MV, [], MF)
        me_.validate()
        for nm_, arr_ in (("loc", M_LOC), ("frm", M_FRM), ("vst", M_VST), ("tnt", M_TNT)):
            ca_ = me_.color_attributes.new(nm_, "FLOAT_COLOR", "CORNER")
            vals_ = []
            for poly in me_.polygons:
                for li_, vi_ in zip(poly.loop_indices, poly.vertices):
                    vals_.extend(arr_[vi_])
            ca_.data.foreach_set("color", vals_)
        MAPOB = bpy.data.objects.new("imap_glass", me_)
        K.COLL["compound"].objects.link(MAPOB)
        MAPOB.data.materials.append(mim)
        MAPOB.pass_index = 1
        MAPOB["pwo"] = 1.0
    log("strands + cutaway windows + office floors", MODE, ostats, "map faces", len(MF))

    # ------------------------------------------------------------ the node lights + the frosted unread cover
    LOCKS = {}
    no_light = []
    for i in G.NODES:
        if i not in G.TOWER:
            continue
        fr = FR[(G.TOWER[i], G.FLOOR[i], "in")]
        lp = G.win_pt(fr, 0.0, 1.0, G.skin_depth(fr, 0.0, 0.0) - 5.5)
        K.add_light("room_%s" % i, "POINT", lp, LH["room_w"] * LH.get("node_room_k", 0.6), (1, 1, 1), size=1.5,
                    group="room:" + i)
        no_light.append(i)
        # unread: a frosted patch over the opening (on the skin) + a frost ring
        fa = Acc("frost_%s" % i, K.M["lock"], 5, K.COLL["rooms"])
        fb = Acc("frostf_%s" % i, K.M["emit"], 5, K.COLL["rooms"])
        for a in range(48):
            a0, a1 = 2 * math.pi * a / 48, 2 * math.pi * (a + 1) / 48
            for g in range(4):
                r0, r1 = g / 4, (g + 1) / 4
                quad = []
                for (rho_, an) in ((r0, a0), (r1, a0), (r1, a1), (r0, a1)):
                    u_, dz_ = rho_ * WAX * math.cos(an), rho_ * WB * math.sin(an)
                    quad.append(G.win_pt(fr, u_, dz_, G.skin_depth(fr, u_, dz_) + 0.12))
                fa.face(quad, pal("frost"))
        ring = G.win_skin_outline(fr, 48, 0.2)
        for q in range(48):
            tube(fb, ring[q], ring[(q + 1) % 48], 0.16, pal("frost"), 6.0, n=4)
        LOCKS[i] = (fa, fb)
    hooks["no_room_light"] = tuple(no_light)
    log("node lights")

    # ------------------------------------------------------------ the skybridges (route floors): A mouth to B mouth,
    # flush into the cutaways: the deck runs on into each office at the SAME level and material as the floor
    wide, waist = CP["bridge_w"]
    brng = random.Random(6420)
    bstat = dict(people=0)

    for f in sorted(RFS):
        zb = G.deck_z(f)
        O_, e_, q_, half = G.bridge_frame(f)
        s_wall = half + (0.15 if MODE == "map" else 0.6)     # walls / roof end just inside the skin
        s_deck = half + (0.25 if MODE == "map" else 1.6)     # the deck runs on into the floor (map: to the patch)
        e3 = (e_[0], e_[1])

        def hw(s):
            return waist / 2 + (wide - waist) / 2 * (min(abs(s), half) / half) ** 1.6

        def P(s, side, z):
            return (O_[0] + e_[0] * s + q_[0] * side * hw(s), O_[1] + e_[1] * s + q_[1] * side * hw(s), z)
        NS = 16
        for k in range(NS):
            s0 = -s_deck + 2 * s_deck * k / NS
            s1 = -s_deck + 2 * s_deck * (k + 1) / NS
            OFF.face([P(s0, -1, zb - 0.01), P(s1, -1, zb - 0.01), P(s1, 1, zb - 0.01), P(s0, 1, zb - 0.01)][::-1], FLOOR_COL,
                     FLOOR_K)                                                                     # the deck top = the floor
            PORC.face([P(s0, 1, zb - 0.8), P(s1, 1, zb - 0.8), P(s1, -1, zb - 0.8), P(s0, -1, zb - 0.8)], POR)
            for side in (-1, 1):
                PORC.face([P(s0, side, zb - 0.8), P(s1, side, zb - 0.8), P(s1, side, zb - 0.01), P(s0, side, zb - 0.01)], POR)
            kb = LH["bridge_route_k"]
            A["trim"].face([P(s0, -0.25, zb + 0.02), P(s1, -0.25, zb + 0.02), P(s1, 0.25, zb + 0.02),
                            P(s0, 0.25, zb + 0.02)], CLIN, kb * 0.45)
        NW = 14
        for k in range(NW):
            s0 = -s_wall + 2 * s_wall * k / NW
            s1 = -s_wall + 2 * s_wall * (k + 1) / NW
            for side in (-1, 1):
                OG.face([P(s0, side, zb + 0.3), P(s1, side, zb + 0.3), P(s1, side, zb + 3.5), P(s0, side, zb + 3.5)], (0.8, 0.95, 0.9))
                A["trim"].face([P(s0, side, zb + 0.3), P(s1, side, zb + 0.3), P(s1, side, zb + 0.55), P(s0, side, zb + 0.55)],
                               (0.75, 1.0, 0.85), LH["bridge_wall_k"] * 8.0)          # the glowing kick strip
            PORC.face([P(s0, -1, zb + 3.5), P(s1, -1, zb + 3.5), P(s1, 1, zb + 3.7), P(s0, 1, zb + 3.7)], POR)
            LAMP.face([P(s0, 0.45, zb + 3.47), P(s1, 0.45, zb + 3.47), P(s1, -0.45, zb + 3.47), P(s0, -0.45, zb + 3.47)],
                      (1.0, 0.8, 0.58), 1.1)                                              # the ceiling light strip (warm)
        for k in range(0, NW + 1):                   # posts and the handrails (inside the glass), seen at decision zoom
            s_ = -s_wall + 2 * s_wall * k / NW
            for side in (-1, 1):
                tube(A["metal"], P(s_, side * 0.93, zb), P(s_, side * 0.93, zb + 1.15), 0.07, (0.55, 0.58, 0.6), n=5)
        for side in (-1, 1):
            for k in range(NW):
                s0 = -s_wall + 2 * s_wall * k / NW
                s1 = -s_wall + 2 * s_wall * (k + 1) / NW
                tube(A["metal"], P(s0, side * 0.93, zb + 1.15), P(s1, side * 0.93, zb + 1.15), 0.09, (0.62, 0.65, 0.67), n=5)
        for _ in range(5):                           # tiny people walking the bridge
            s_ = brng.uniform(-half + 4.0, half - 4.0)
            lat = brng.uniform(-0.55, 0.55) * hw(s_)
            d = (e_[0], e_[1]) if brng.random() < 0.5 else (-e_[0], -e_[1])
            px, py, _z = P(s_, 0.0, zb)
            px, py = px + q_[0] * lat, py + q_[1] * lat
            OFC.person(OFF, px, py, zb, (d[1], -d[0]), d, PERSON_H, brng, "walk" if brng.random() < 0.7 else "stand", 0.9, bright=True)
            bstat["people"] += 1
    log("bridges", bstat)

    # ------------------------------------------------------------ the UP stairs: a ribbon up each strand's front band
    for (a, b_) in G.PATH:
        et = G.edge_type(a, b_)
        if et == "bridge":
            continue
        pth = [p for p in G.edge_path(a, b_) if p[2] > G.PODIUM_H + 0.2]
        if et == "stair":                          # v4: the ribbon stays on the solid band: no tips into the windows
            pth = pth[1:-1]
        elif et == "ramp":
            pth = pth[:-1]
        else:
            pth = pth[1:]
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
        for k_ in ("office", "office_lamp"):
            ctx["set_pwo"](ctx["OBJ"].get(k_), ctx.get("cut", 1.0))
        ctx["set_pwo"](MAPOB, ctx.get("cut", 1.0))
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
