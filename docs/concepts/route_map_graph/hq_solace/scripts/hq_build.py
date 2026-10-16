"""HQ Solace: the Blender build of the twin double-helix towers (called by the kit's hq_scene.py: build(K) -> hooks).
Redesign 2026-10-15 (designer): solid towers of stacked, turning floors; a glazed bow-tie skybridge on every floor;
an atrium shaft glowing up each tower; slab downlights; big ground spots; the route rooms cut into the floors' fronts.

Placed by rule from hq_preset "compound" + hq_graph; seed 6330 (window panes and their tints).
  floors    every floor of each tower: a porcelain slab (protruding, its edge lit underneath = the downlights), a dark
            glass body, a band of office windows with mullions on all four faces (seeded panes, some dark), the
            atrium: a leaf-green glazed slot up the outer face (continuous: it draws each tower's helix line)
  bridges   every floor: a bow-tie plan walkway (wide at the towers, narrow at the waist), glass walls, a lit floor;
            the route floors' bridges are brighter
  crown     the top floor joins the towers; THE GENOME CORE sits open in its middle (red rings: the TARGET), pink halo
  podium    a rectangular plaza podium (no ring platform), the clinic gate (start)
  rig       ground spots aimed up the towers, slab downlights (spots every other floor), rim from the city behind
            (landmark only), the halo fog ring lit from below; unread rooms: a frosted pane, dimmed
"""
import math
import random


def build(K):
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, Acc, obox, oquad, tube, box = K.A, K.Acc, K.obox, K.oquad, K.tube, K.box
    Vector = K.Vector
    import bpy
    hooks = {"accs": {}, "beams": [], "mover_lights": {}}
    LEAF, PINK, CLIN, POR = pal("leaf"), pal("pink"), pal("clinic"), pal("porcelain")
    R, FH, TW, TD = CP["radius"], CP["floor_h"], CP["tower_w"], CP["tower_d"]
    RWc, RDc = CP["room_w"], CP["room_d"]
    TOPF = CP["floors"]
    RFS = set(CP["route_floors"])
    rr = random.Random(6330)
    log = K.log
    GL = (0.012, 0.03, 0.02)

    m2, nt2 = K.new_mat("porcelain")
    o2 = nt2.nodes.new("ShaderNodeOutputMaterial")
    b2 = nt2.nodes.new("ShaderNodeBsdfPrincipled")
    c2 = K.attr(nt2, "col")
    nt2.links.new(c2.outputs["Color"], b2.inputs["Base Color"])
    b2.inputs["Roughness"].default_value = 0.2
    b2.inputs["Coat Weight"].default_value = 0.6
    b2.inputs["Coat Roughness"].default_value = 0.05
    nt2.links.new(b2.outputs[0], o2.inputs[0])
    PORC = Acc("porc", m2, 1, K.COLL["compound"])
    hooks["accs"]["porc"] = PORC

    # ------------------------------------------------------------ the strands: two smooth swept TUBES (designer, v3)
    # each strand is one continuous tube following the helix (shared-vertex mesh, smooth shaded, soft porcelain
    # specular); the "floors" read as rows of OVAL portholes (aircraft fuselage) lit from inside, a thin frame ring
    # round each; a leaf-green light seam rises up the outer side (the light inside the tower); a downlight ring
    # under every row. Route rooms are cut into the tube's front at their floor.
    rt = CP["tube_r"]
    ztop = G.floor_z(TOPF)
    NSEG, DZ = 40, 1.25
    room_zs = {t: [(G.floor_z(f) + 1.0, G.floor_z(f) + 1.0 + CP["room_h"]) for f in RFS] for t in ("A", "B")}

    def tube_pt(t, z, phi, r=None):
        f = (z - G.PODIUM_H) / FH
        c, rv, n = G.tower_frame(t, f)
        rr2 = rt if r is None else r
        # phi measured from the front normal, counter-clockwise seen from above (front = phi 0)
        tx_ = (n[1], -n[0])
        return (c[0] + (n[0] * math.cos(phi) + tx_[0] * math.sin(phi)) * rr2,
                c[1] + (n[1] * math.cos(phi) + tx_[1] * math.sin(phi)) * rr2, z)

    for t in ("A", "B"):
        verts, faces = [], []
        nz = int((ztop - G.PODIUM_H) / DZ) + 1
        for iz in range(nz):
            z = G.PODIUM_H + iz * DZ
            for j in range(NSEG):
                verts.append(tube_pt(t, z, 2 * math.pi * j / NSEG))
        for iz in range(nz - 1):
            z = G.PODIUM_H + (iz + 0.5) * DZ
            cut = any(z0 - 0.4 < z < z1 + 0.4 for (z0, z1) in room_zs[t])
            for j in range(NSEG):
                ang = 2 * math.pi * (j + 0.5) / NSEG
                if cut and (ang < 0.95 or ang > 2 * math.pi - 0.95):      # the room's opening on the front
                    continue
                a0, a1 = iz * NSEG + j, iz * NSEG + (j + 1) % NSEG
                faces.append((a0, a1, a1 + NSEG, a0 + NSEG))
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
        # the portholes: rows of ovals round the tube, one row per floor; lit from inside; thin frame rings
        for f in range(TOPF):
            zr = G.floor_z(f) + FH * 0.5
            route = f in RFS
            nwin = 12
            for j in range(nwin):
                phi = 2 * math.pi * (j + 0.5) / nwin
                if route and (phi < 1.2 or phi > 2 * math.pi - 1.2):
                    continue
                ew, eh = 1.7, 2.9                     # half axes of the oval (along the tube, up)
                ring = []
                for q in range(16):
                    a = 2 * math.pi * q / 16
                    dphi = ew * math.cos(a) / rt
                    ring.append(tube_pt(t, zr + eh * math.sin(a), phi + dphi, rt + 0.06))
                col = CLIN if rr.random() < 0.75 else (0.6, 1.0, 0.55)
                A["trim"].face(ring, col, LH["band_k"] * rr.uniform(0.7, 1.3) if rr.random() < 0.85 else 0.05)
                for q in range(16):                   # the frame ring
                    tube(A["metal"], ring[q], ring[(q + 1) % 16], 0.12, (0.55, 0.58, 0.6), n=4)
            # the downlight ring under the row (the stack's lit layering)
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
        # the light rising inside: a continuous leaf-green seam up the tube's outer side
        prev = None
        z = G.PODIUM_H
        while z <= ztop:
            f = (z - G.PODIUM_H) / FH
            c, rv, n = G.tower_frame(t, f)
            tx_ = (n[1], -n[0])
            side = 1.0 if (tx_[0] * rv[0] + tx_[1] * rv[1]) > 0 else -1.0
            p = tube_pt(t, z, side * math.pi / 2, rt + 0.1)
            if prev is not None:
                tube(A["trim"], prev, p, 0.45, (0.55, 1.0, 0.72), LH["atrium_k"], n=6)   # pale mint: never the route lime
            prev = p
            z += 2.0
    log("towers")
    # ------------------------------------------------------------ the bow-tie skybridges (every floor)
    wide, waist = CP["bridge_w"]
    s_end = R - TD / 2

    def hw(s):
        return waist / 2 + (wide - waist) / 2 * (abs(s) / s_end) ** 1.6

    for f in range(TOPF):
        c, rv, n = G.tower_frame("A", f)
        zb = G.floor_z(f) + 1.2
        route = f in RFS
        NS = 14

        def P(s, side, z):
            return (rv[0] * s + n[0] * side * hw(s), rv[1] * s + n[1] * side * hw(s), z)
        for k in range(NS):
            s0 = -s_end + 2 * s_end * k / NS
            s1 = -s_end + 2 * s_end * (k + 1) / NS
            PORC.face([P(s0, -1, zb), P(s1, -1, zb), P(s1, 1, zb), P(s0, 1, zb)], POR)
            PORC.face([P(s0, 1, zb - 0.8), P(s1, 1, zb - 0.8), P(s1, -1, zb - 0.8), P(s0, -1, zb - 0.8)], POR)
            for side in (-1, 1):
                # glazed walls lit from inside (the rungs read as lit bands from any distance)
                A["trim"].face([P(s0, side, zb + 0.4), P(s1, side, zb + 0.4), P(s1, side, zb + 3.9), P(s0, side, zb + 3.9)],
                               (0.75, 1.0, 0.85), LH["bridge_wall_k"] * (1.6 if route else 1.0))
                PORC.face([P(s0, side, zb - 0.8), P(s1, side, zb - 0.8), P(s1, side, zb), P(s0, side, zb)], POR)
            PORC.face([P(s0, -1, zb + 4.2), P(s1, -1, zb + 4.2), P(s1, 1, zb + 4.4), P(s0, 1, zb + 4.4)], POR)
            kb = LH["bridge_route_k"] if route else LH["bridge_k"]
            A["trim"].face([P(s0, -0.35, zb + 0.03), P(s1, -0.35, zb + 0.03), P(s1, 0.35, zb + 0.03), P(s0, 0.35, zb + 0.03)],
                           CLIN, kb)
            A["trim"].face([P(s0, 0.5, zb + 4.15), P(s1, 0.5, zb + 4.15), P(s1, -0.5, zb + 4.15), P(s0, -0.5, zb + 4.15)],
                           (0.7, 1.0, 0.75), kb * 0.5)
    log("bridges")

    # ------------------------------------------------------------ rooms (+ the unread frosted panes), facade stairs
    LOCKS = {}
    for i in G.NODES:
        if i in ("start", "srv"):
            continue
        rec = G.ROOM[i]
        K.room_shell(i, rec)
        LOCKS[i] = K.lock_plane(i, rec, pal("frost"), name="frost")
    for (a, b_) in G.PATH:
        if G.edge_type(a, b_) != "stair":
            continue
        pth = G.edge_path(a, b_)
        for p, q in zip(pth, pth[1:]):
            K.seg_box(A["metal"], Vector(p) + Vector((0, 0, -1.55)), Vector(q) + Vector((0, 0, -1.55)), 1.8, 0.25,
                      (0.42, 0.45, 0.45))
    log("rooms")

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
    box(PORC, -px, -py, 0.0, px, py, ph, (0.45, 0.48, 0.48))
    box(A["ground"], -px + 1, -py + 1, ph, px - 1, py - 1, ph + 0.02, (0.34, 0.36, 0.36), k=1.0)
    for (x0, y0, x1, y1) in ((-px, -py - 0.06, px, -py), (-px, py, px, py + 0.06), (-px - 0.06, -py, -px, py),
                             (px, -py, px + 0.06, py)):
        box(A["trim"], x0, y0, ph - 0.6, x1, y1, ph - 0.35, LEAF, LH["trim_k"] * 0.6)
    for s in range(6):
        box(PORC, -18.0, -py - (6 - s) * 1.4, 0.0, 18.0, -py, ph * (s + 1) / 6, (0.45, 0.48, 0.48))
    sx_, sy_ = CP["start"]
    box(PORC, sx_ - 5, sy_ - 3, 0, sx_ + 5, sy_ + 3, 4.6, (0.45, 0.48, 0.48))
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
        if k % 4 == 0:
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
    hooks["post_build"] = post_build

    def apply(fr, ctx):
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
