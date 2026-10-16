"""Rebel Cell v3: THE SEWER under the street (designer review of round 1, note 3: "the underground gets character:
sewers with a slight green light, running water, and pipe tunnels leading to and away from the route"). Replaces the v2
undercroft street (rc_undercroft). Blender side, through the kit's K helpers. Seed 8433.

The third lane (RIGGER, the service tunnel cut open in the kerb's section face) now opens onto a SEWER GALLERY one level
down (the tunnel's floor level):
  pipe tunnels   two big brick PIPE TUNNELS continue the lane's tunnel to the west (toward THE DROP's manhole) and to the
                 east (away, past the shaft), cut open by the section like the tunnel; round culvert mouths in the
                 tunnel's back wall lead off into the earth (green glow, trickles)
  channel        a brick flood channel along the gallery with RUNNING WATER (a flowing, streaked, glossy surface); it
                 falls into the sump in front of the deeper detour rooms (a cascade) and restarts from an outfall
  outfalls       round pipe mouths in the channel's far wall pour sheets of water into it (foam where they land)
  ledges         a walkway between the arcade and the channel; a wide front ledge of wet brick pavers with the trunk
                 PIPES on saddles (flanges, valve wheels), gratings, work lamps, stencil plates
  light          slight GREEN: mercury cage lamps on the walls, low green area lights over the water (the water carries a
                 faint green emission too), a few warm work lamps; no fog plane (thin dark strata only)
  brick          one brick material (wet, mortar, grime) for the retaining wall, the channel, the pipe tunnels, the floor
Nothing is placed in front of a room opening (rc_alley.over_room)."""
import math
import random


def brick_acc(K, name="brick"):
    """The wet sewer brick: running bond on (x + y, z) for walls and (x, y) for floors; dark mortar, grime, wet sheen."""
    nt_m, nt = K.new_mat(name)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = K.attr(nt, "col")
    g, ps, ns = K.pos_sep(nt)
    M = K.mth
    flat = K.smooth(nt, M(nt, "ABSOLUTE", ns.outputs["Z"]), 0.6, 0.8)
    wall = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(M(nt, "ADD", ps.outputs["X"], ps.outputs["Y"]), wall.inputs[0])
    nt.links.new(ps.outputs["Z"], wall.inputs[1])
    flo = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(ps.outputs["X"], flo.inputs[0])
    nt.links.new(ps.outputs["Y"], flo.inputs[1])
    mv = nt.nodes.new("ShaderNodeMix")
    mv.data_type = "VECTOR"
    nt.links.new(flat, mv.inputs[0])
    nt.links.new(wall.outputs[0], mv.inputs[4])
    nt.links.new(flo.outputs[0], mv.inputs[5])
    br = K.nn(nt, "ShaderNodeTexBrick", Scale=1.0, Mortar_Size=0.06, Bias=0.0, Brick_Width=1.1, Row_Height=0.42)
    br.offset = 0.5
    nt.links.new(mv.outputs[1], br.inputs["Vector"])
    br.inputs["Color1"].default_value = (1.0, 1.0, 1.0, 1.0)
    br.inputs["Color2"].default_value = (0.78, 0.74, 0.72, 1.0)
    br.inputs["Mortar"].default_value = (0.35, 0.36, 0.34, 1.0)
    n1 = K.nn(nt, "ShaderNodeTexNoise", Scale=0.12, Detail=5.0, Roughness=0.6)
    nt.links.new(g.outputs["Position"], n1.inputs["Vector"])
    gm = K.smooth(nt, n1.outputs["Fac"], 0.35, 0.7)
    base = K.vsc(nt, col.outputs["Color"], M(nt, "ADD", 0.65, M(nt, "MULTIPLY", gm, 0.45)))
    vm = nt.nodes.new("ShaderNodeVectorMath")
    vm.operation = "MULTIPLY"
    nt.links.new(base, vm.inputs[0])
    nt.links.new(br.outputs["Color"], vm.inputs[1])
    nt.links.new(vm.outputs[0], b.inputs["Base Color"])
    wet = K.smooth(nt, n1.outputs["Fac"], 0.48, 0.56)
    nt.links.new(M(nt, "SUBTRACT", 0.34, M(nt, "MULTIPLY", wet, 0.26)), b.inputs["Roughness"])   # t4: wet brick
    b.inputs["Specular IOR Level"].default_value = 0.7
    b.inputs["Coat Weight"].default_value = 0.25
    b.inputs["Coat Roughness"].default_value = 0.06
    bump = K.nn(nt, "ShaderNodeBump", Strength=0.35, Distance=0.05)
    nt.links.new(br.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return K.Acc(name, nt_m, 1, K.COLL["compound"])


def water_mat(K, green, k):
    """Running water: dark, glossy, streaked along the flow (x); foam streaks; a faint green emission."""
    m, nt = K.new_mat("sewer_water")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    g, ps, ns = K.pos_sep(nt)
    M = K.mth
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.05, 0.9, 0.9)
    nt.links.new(g.outputs["Position"], mp.inputs["Vector"])
    n1 = K.nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=8.0, Roughness=0.62)
    nt.links.new(mp.outputs[0], n1.inputs["Vector"])
    mp2 = nt.nodes.new("ShaderNodeMapping")
    mp2.inputs["Scale"].default_value = (0.12, 1.8, 1.8)
    nt.links.new(g.outputs["Position"], mp2.inputs["Vector"])
    n2 = K.nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=4.0, Roughness=0.5)
    nt.links.new(mp2.outputs[0], n2.inputs["Vector"])
    mp3 = nt.nodes.new("ShaderNodeMapping")                 # t4: thin bright FLOW STREAKS along the current
    mp3.inputs["Scale"].default_value = (0.025, 3.2, 3.2)
    nt.links.new(g.outputs["Position"], mp3.inputs["Vector"])
    n3 = K.nn(nt, "ShaderNodeTexNoise", Scale=1.0, Detail=3.0, Roughness=0.5)
    nt.links.new(mp3.outputs[0], n3.inputs["Vector"])
    streak = K.smooth(nt, n3.outputs["Fac"], 0.64, 0.70)
    foam = M(nt, "MAXIMUM", K.smooth(nt, n2.outputs["Fac"], 0.70, 0.76), M(nt, "MULTIPLY", streak, 0.8))
    b.inputs["Base Color"].default_value = (0.003, 0.009, 0.006, 1.0)
    nt.links.new(M(nt, "ADD", 0.015, M(nt, "MULTIPLY", foam, 0.5)), b.inputs["Roughness"])
    b.inputs["Specular IOR Level"].default_value = 0.8
    bump = K.nn(nt, "ShaderNodeBump", Strength=0.35, Distance=0.1)
    nt.links.new(n1.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    b.inputs["Emission Color"].default_value = (0.72, 1.0, 0.82, 1.0)
    nt.links.new(M(nt, "ADD", k, M(nt, "MULTIPLY", foam, 0.55)), b.inputs["Emission Strength"])
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def falls_mat(K):
    """A falling sheet of water: streaks along z, partly transparent, a cold green-white glint."""
    import bpy
    m = bpy.data.materials.new("sewer_falls")
    try:
        m.use_nodes = True
    except Exception:  # noqa: BLE001
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    g = nt.nodes.new("ShaderNodeNewGeometry")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (2.2, 2.2, 0.12)
    nt.links.new(g.outputs["Position"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 6.0
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    a = K.smooth(nt, nz.outputs["Fac"], 0.42, 0.62)
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (0.7, 1.0, 0.85, 1.0)
    nt.links.new(K.mth(nt, "MULTIPLY", a, 0.9), em.inputs["Strength"])
    gl = nt.nodes.new("ShaderNodeBsdfGlossy")
    gl.inputs["Roughness"].default_value = 0.1
    ad = nt.nodes.new("ShaderNodeAddShader")
    nt.links.new(em.outputs[0], ad.inputs[0])
    nt.links.new(gl.outputs[0], ad.inputs[1])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(K.mth(nt, "MULTIPLY", a, 0.85), mx.inputs[0])
    nt.links.new(tr.outputs[0], mx.inputs[1])
    nt.links.new(ad.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs[0])
    try:
        m.surface_render_method = "DITHERED"
    except (AttributeError, TypeError):
        pass
    return m


def half_pipe(acc, x0, x1, yc, zc, r, col, n=14, k=0.0):
    """The BACK half of a horizontal pipe (axis along x) seen from -y: inner faces, cut open at the plane y = yc."""
    for i in range(n):
        a0 = math.pi * i / n
        a1 = math.pi * (i + 1) / n
        p0 = (yc + r * math.sin(a0), zc - r * math.cos(a0))
        p1 = (yc + r * math.sin(a1), zc - r * math.cos(a1))
        acc.face([(x0, p0[0], p0[1]), (x0, p1[0], p1[1]), (x1, p1[0], p1[1]), (x1, p0[0], p0[1])], col, k)


def mouth(K, acc_ring, acc_dark, x, y, z, r, ring_col, glow=None):
    """A round pipe mouth in a wall facing -y: a brick ring (an annulus of quads) and a dark recessed disc, a faint glow."""
    n = 20
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        acc_ring.face([(x + r * c0, y - 0.6, z + r * s0), (x + r * c1, y - 0.6, z + r * s1),
                       (x + (r + 1.0) * c1, y - 0.6, z + (r + 1.0) * s1), (x + (r + 1.0) * c0, y - 0.6, z + (r + 1.0) * s0)],
                      ring_col)
        acc_ring.face([(x + r * c1, y - 0.6, z + r * s1), (x + r * c0, y - 0.6, z + r * s0),
                       (x + r * c0, y + 3.0, z + r * s0), (x + r * c1, y + 3.0, z + r * s1)], (0.05, 0.05, 0.045))
    acc_dark.face([(x + r * math.cos(2 * math.pi * i / n), y + 3.0, z + r * math.sin(2 * math.pi * i / n))
                   for i in range(n)], glow or (0.01, 0.015, 0.012), 0.6 if glow else 0.0)


def build(K, AL, over_room, tex_quads, facing_quad, hooks, BR):
    import bpy
    G, CP, LH, HZ = K.G, K.CP, K.LH, K.HZ
    SW = HZ["v3"]["sewer"]
    A, box, tube = K.A, K.box, K.tube
    Vector = K.Vector
    rd = random.Random(8433)
    RH = CP["room_h"]
    TY = G.TY
    ZL = G.ZL["R"] - 3.0                                    # the gallery floor = the tunnel's floor
    ZT = G.ZL["R"] + RH + 4.0                               # the tunnel's top
    ZD = G.ZL["R"] - 15.0                                   # the sump floor (in front of the deeper detour rooms)
    dxa, dxb = G.XS["2a"] - 12.0, G.XS["2b"] + 12.0
    xa, xb = G.X0 - 45.0, G.SHAFT_X + 4.0                   # the tunnel's span
    LW = HZ["v3"].get("gallery_d", AL["uc_w"])            # t4: shallower: the front cut (vault profiles) is in frame
    ya = TY - LW
    XA, XB = AL["x_a"] - 70.0, AL["x_b"] + 70.0
    GREEN = tuple(SW["green"])
    c0, c1 = TY + SW["chan"][0], TY + SW["chan"][1]          # the channel's y span (front, back)
    zw = ZL + SW["water_dz"]                                 # the water surface
    zc = ZL + SW["chan_dz"]                                  # the channel's bed
    BRICK = (0.15, 0.13, 0.10)                               # wet, algae-dulled brick (not red: red is the accent)
    BRICK_D = (0.11, 0.10, 0.08)
    WM = water_mat(K, GREEN, SW["water_k"])
    FM = falls_mat(K)
    WAT = K.Acc("sewer_water", WM, 1, K.COLL["compound"])
    FAL = K.Acc("sewer_falls", FM, 1, K.COLL["compound"])
    hooks.setdefault("accs", {}).update({"sewer_water": WAT, "sewer_falls": FAL})
    DARK = K.A["small"]

    # ---------------------------------------------------------------- the floor: ledges, the channel, the sump
    def floor_span(x0_, x1_):
        box(BR, x0_, c1, ZL - 1.2, x1_, TY, ZL, BRICK_D)                         # the back ledge (arcade walkway)
        box(BR, x0_, ya, ZL - 1.2, x1_, c0, ZL, BRICK_D)                         # the front ledge
        box(BR, x0_, c0, zc - 1.0, x1_, c1, zc, (0.08, 0.07, 0.06))              # the channel bed
        box(WAT, x0_, c0 + 0.1, zw - 0.2, x1_, c1 - 0.1, zw, (0, 0, 0))          # the running water
        box(BR, x0_, c1 - 0.05, zc, x1_, c1 + 0.6, ZL, BRICK)                    # the far wall (faces the camera)
        box(BR, x0_, c0 - 0.6, zc, x1_, c0 + 0.05, ZL, BRICK)                    # the near wall
        box(A["trim"], x0_, c1 - 0.12, ZL - 0.25, x1_, c1 - 0.05, ZL - 0.1, (1.0, 0.75, 0.25), 0.5)   # the kerb edge
    floor_span(XA, dxa)
    floor_span(dxb, XB)
    # the sump: one level down in front of the deeper rooms; the channel falls into it (a cascade)
    box(BR, dxa, ya, ZD - 1.2, dxb, TY, ZD, BRICK_D)
    box(BR, dxa, TY - 9.0, ZD, dxb, TY, ZD + 2.6, BRICK_D)                       # a ledge to the deeper rooms
    box(WAT, dxa, ya, ZD + 0.4, dxb, TY - 9.0, ZD + 0.6, (0, 0, 0))              # the sump's water
    for xx in (dxa, dxb):
        box(BR, xx - 0.7, ya, ZD, xx + 0.7, TY, ZL, BRICK)
        box(A["trim"], xx - 0.75, ya, ZL - 0.25, xx + 0.75, TY, ZL - 0.1, (1.0, 0.75, 0.3), 1.2)
    for k_ in range(10):                                                          # the stair down
        z1 = ZL - (ZL - ZD) * (k_ + 1) / 10
        y0 = TY - 20.0 - k_ * 2.2
        box(BR, dxa + 0.7, y0 - 2.2, ZD, dxa + 6.0, y0, z1 + (ZL - ZD) / 10, BRICK_D)
    # the cascade: the channel pours over the lip into the sump (west), an outfall restarts it (east)
    box(FAL, dxa + 0.7, c0 + 0.4, ZD + 0.5, dxa + 1.0, c1 - 0.4, zw, (0, 0, 0))
    box(FAL, dxa + 1.0, c0 + 0.2, ZD + 0.5, dxa + 3.5, c1 - 0.2, ZD + 1.6, (0, 0, 0))     # spray
    if SW["green_w"] > 0:
        K.add_light("sewer_cascade", "AREA", (dxa + 3.0, (c0 + c1) / 2, zw + 2.0), SW["green_w"] * 0.8, GREEN,
                    aim=(dxa + 3.0, (c0 + c1) / 2, ZD), size=6.0, size_y=c1 - c0, group="corp", shadow=False)
    K.add_light("cascade_pool", "SPOT", (dxa + 4.0, c0 - 2.0, ZL + 5.0), SW["lamp_w"] * 0.8, GREEN,
                aim=(dxa + 2.0, (c0 + c1) / 2, ZD), size=0.4, spot=45, blend=0.7, group="corp", shadow=False)
    # ---------------------------------------------------------------- the pipe tunnels: west + east of the lane's tunnel
    PR = SW["portal_r"]
    zcp = ZL + PR                                                                 # the pipe's axis height
    for (p0, p1) in ((XA, xa), (xb, XB)):
        half_pipe(BR, p0, p1, TY, zcp, PR, BRICK)
        box(WAT, p0, TY + 0.1, ZL + 0.3, p1, TY + 3.2, ZL + 0.5, (0, 0, 0))     # its water (bottom of the pipe)
        x = p0 + 8.0
        while x < p1 - 4.0:                                                       # green cage lamps on the crown
            box(A["small"], x - 0.5, TY + PR - 1.4, zcp + PR - 1.6, x + 0.5, TY + PR - 0.6, zcp + PR - 0.9,
                (0.7, 1.0, 0.75), 7.0)
            for i in range(8):                                                    # a steel rib round the pipe
                a0, a1 = math.pi * i / 8, math.pi * (i + 1) / 8
                tube(A["metal"], (x + 6.0, TY + (PR - 0.25) * math.sin(a0), zcp - (PR - 0.25) * math.cos(a0)),
                     (x + 6.0, TY + (PR - 0.25) * math.sin(a1), zcp - (PR - 0.25) * math.cos(a1)), 0.18,
                     (0.12, 0.12, 0.11), n=4)
            if abs(x - (xa if p1 == xa else xb)) < 30.0:
                K.add_light("pipe_%d" % int(x), "POINT", (x, TY + 2.0, zcp + 2.0), SW["lamp_w"] * 0.25, GREEN, size=1.0,
                            group="corp", shadow=False)
            x += 26.0
    # the tunnel's back wall: culvert mouths lead off into the earth (between the rooms)
    yb = TY + 16.0
    rooms_x = sorted(r["o"][0] for i, r in G.ROOM.items() if G.LANE.get(i) == "R" and abs(r["o"][2] - G.ZL["R"]) < 1)
    gaps = [(a + b) / 2 for a, b in zip(rooms_x, rooms_x[1:]) if b - a > 20.0]
    for gx in gaps + [xa + 14.0]:
        if over_room(gx, ZL, ZL + 8.0, pad=0.5):
            continue
        mouth(K, BR, DARK, gx, yb - 0.4, ZL + 4.2, 3.0, BRICK, glow=(0.02, 0.05, 0.03))
        box(FAL, gx - 1.2, yb - 0.9, ZL, gx + 1.2, yb - 0.7, ZL + 1.4, (0, 0, 0))   # a trickle out of it
        K.add_light("culvert_%d" % int(gx), "SPOT", (gx, yb - 5.0, ZL + 9.0), SW["lamp_w"] * 0.5, GREEN,
                    aim=(gx, yb - 1.0, ZL + 2.0), size=0.4, spot=40, blend=0.6, group="corp", shadow=False)
    # ---------------------------------------------------------------- outfalls: pipe mouths in the channel's far wall
    nof = 0
    x = XA + 18.0
    while x < XB - 10.0:
        if not (dxa - 6 < x < dxb + 6) and not over_room(x, zc, ZL, pad=0.0):
            r_ = rd.uniform(0.8, 1.4)
            mouth(K, A["metal"], DARK, x, c1 + 0.6, zw + r_ + 0.5, r_, (0.16, 0.14, 0.12))
            box(FAL, x - r_ * 0.7, c1 - 0.5, zw, x + r_ * 0.7, c1 - 0.2, zw + r_ + 0.3, (0, 0, 0))   # the pour
            box(FAL, x - r_ * 1.2, c1 - 2.2, zw, x + r_ * 1.2, c1 - 0.4, zw + 0.25, (0, 0, 0))     # foam
            nof += 1
            if nof % 2 == 0:
                K.add_light("outfall_%d" % nof, "SPOT", (x, c1 - 3.0, zw + 6.0), SW["outfall_w"] * 2.0, GREEN,
                            aim=(x, c1 - 1.0, zw), size=0.3, spot=40, blend=0.6, group="corp", shadow=False)
        x += rd.uniform(22.0, 34.0)
    # ---------------------------------------------------------------- the retaining wall's face (above the arcade)
    WY = TY - 0.05
    box(BR, XA, WY - 0.3, ZT, XB, WY, -0.7, BRICK)                                # brick veneer up to the kerb
    box(A["metal"], XA, WY - 1.2, ZT - 0.2, XB, WY, ZT + 0.3, (0.12, 0.11, 0.1))  # the arcade's lintel
    for k_ in range(0, int(XB - XA), 6):                                          # a hazard stripe on the lintel
        xx = XA + k_
        box(A["trim"], xx, WY - 1.25, ZT - 0.1, xx + 3.0, WY - 1.2, ZT + 0.2, (1.0, 0.72, 0.1), 0.6)
    for q in range(3):                                                            # pipes along the wall
        zz = ZT + 2.2 + q * 1.4
        tube(A["metal"], (XA, WY - 0.6 - q * 0.3, zz), (XB, WY - 0.6 - q * 0.3, zz), 0.34 - 0.06 * q,
             [(0.2, 0.15, 0.1), (0.1, 0.18, 0.13), (0.26, 0.12, 0.07)][q], n=6)
    box(A["metal"], XA, TY - 0.6, -0.1, XB, TY - 0.45, 1.2, (0.22, 0.2, 0.18))  # the kerb railing
    x = XA + 2.0
    while x < XB:
        tube(A["metal"], (x, TY - 0.5, -0.1), (x, TY - 0.5, 1.2), 0.07, (0.22, 0.2, 0.18), n=4)
        x += 2.5
    # mercury cage lamps on the wall, stencil plates, a ladder down from the street now and then
    x = XA + 10.0
    k_ = 0
    while x < XB - 6.0:
        if not over_room(x, ZT - 1, ZT + 3, pad=0.5):
            box(A["small"], x - 0.45, WY - 0.9, ZT + 1.0, x + 0.45, WY - 0.3, ZT + 1.7, (0.75, 1.0, 0.8), 8.0)
            K.add_light("wall_lamp_%d" % k_, "SPOT", (x, WY - 1.4, ZT + 1.0), SW["lamp_w"], GREEN,
                        aim=(x, WY - 11.0, ZL), size=0.4, spot=46, blend=0.55, group="corp", shadow=False)
            k_ += 1
        x += 32.0
    plates = ["sewer_00.png", "sewer_01.png", "sewer_02.png"]
    for k_, px in enumerate((xa - 30.0, G.X0 - 22.0, xb + 18.0, xb + 70.0)):
        if over_room(px, ZT, ZT + 3.0, pad=0.5):
            continue
        tex_quads(plates[k_ % 3], [facing_quad(px - 3.2, px + 3.2, WY - 0.4, ZT + 4.6, ZT + 7.0)], 0.9)
    for lx in (xa - 44.0, xb + 40.0, XA + 30.0):                                  # ladders (street -> gallery)
        for s_ in (-0.45, 0.45):
            tube(A["metal"], (lx + s_, WY - 0.7, ZL), (lx + s_, WY - 0.7, 1.5), 0.07, (0.3, 0.3, 0.28), n=4)
        z = ZL + 0.5
        while z < 0.0:
            tube(A["metal"], (lx - 0.45, WY - 0.7, z), (lx + 0.45, WY - 0.7, z), 0.05, (0.3, 0.3, 0.28), n=4)
            z += 0.6
    # ---------------------------------------------------------------- the front ledge: trunk pipes, gratings, lamps
    yp = (ya + c0) / 2
    for (yy, r_, cc, zz) in ((c0 - 4.0, 2.0, (0.20, 0.12, 0.07), ZL + 2.6), (c0 - 8.5, 1.3, (0.08, 0.16, 0.12), ZL + 1.8),
                             (c0 - 11.5, 0.8, (0.22, 0.2, 0.18), ZL + 1.2)):
        if yy - r_ < ya + 0.4:
            continue                                        # (the ledge is shallower than the pipe rack)
        for (p0, p1) in ((XA, dxa - 1.0), (dxb + 1.0, XB)):
            tube(A["metal"], (p0, yy, zz), (p1, yy, zz), r_, cc, n=12)
            x = p0 + 6.0
            while x < p1 - 2:
                tube(A["metal"], (x - 0.3, yy, zz), (x + 0.3, yy, zz), r_ + 0.25, (0.1, 0.1, 0.1), n=12)   # flange
                box(A["rough"], x - 0.6, yy - r_ * 0.8, ZL, x + 0.6, yy + r_ * 0.8, zz - r_ * 0.6, (0.1, 0.09, 0.08))
                x += 12.0
        # the trunk pipes dive into the sump's walls (leading on under the deeper level)
        tube(A["metal"], (dxa - 1.0, yy, zz), (dxa - 1.0, yy, ZD + 1.0), r_, cc, n=12)
        tube(A["metal"], (dxb + 1.0, yy, zz), (dxb + 1.0, yy, ZD + 1.0), r_, cc, n=12)
    for _ in range(14):                                                           # valve wheels on the big pipe
        x = rd.uniform(XA + 10, XB - 10)
        if dxa - 3 < x < dxb + 3:
            continue
        yy, zz = c0 - 4.0, ZL + 2.6 + 2.0
        tube(A["metal"], (x, yy, ZL + 4.4), (x, yy, zz + 0.6), 0.12, (0.15, 0.15, 0.15), n=4)
        for i in range(10):
            a0, a1 = 2 * math.pi * i / 10, 2 * math.pi * (i + 1) / 10
            tube(A["metal"], (x + 0.8 * math.cos(a0), yy + 0.8 * math.sin(a0), zz + 0.6),
                 (x + 0.8 * math.cos(a1), yy + 0.8 * math.sin(a1), zz + 0.6), 0.09, (0.55, 0.12, 0.08), n=4)
    for _ in range(18):                                                           # floor gratings (glow from below)
        x = rd.uniform(XA + 6, XB - 6)
        if dxa - 3 < x < dxb + 3:
            continue
        y = rd.uniform(ya + 0.6, ya + 1.6)
        box(A["metal"], x, y, ZL, x + 2.6, y + 2.6, ZL + 0.06, (0.05, 0.05, 0.05))
        for s in range(5):
            box(A["small"], x + 0.3 + s * 0.45, y + 0.3, ZL + 0.01, x + 0.5 + s * 0.45, y + 2.3, ZL + 0.07,
                (0.45, 1.0, 0.6), 1.2)
    for _ in range(22):                                                           # crates, drums, debris
        x = rd.uniform(XA, XB)
        if dxa - 2 < x < dxb + 2:
            continue
        y = rd.uniform(ya + 0.8, ya + 2.4)
        if rd.random() < 0.5:
            tube(A["metal"], (x, y, ZL), (x, y, ZL + 1.6), 0.6, [(0.2, 0.25, 0.1), (0.3, 0.1, 0.06), (0.1, 0.15, 0.25)][_ % 3],
                 n=10)
        else:
            s_ = rd.uniform(0.8, 1.6)
            box(A["rough"], x, y, ZL, x + s_, y + s_, ZL + s_, (0.12, 0.1, 0.08))
    # work lamps on stands (warm: the gallery is not all green) + green area lights over the water
    nl = 0
    x = XA + 30.0
    while x < XB - 20.0:
        if not (dxa - 4 < x < dxb + 4):
            y = ya + 0.9
            tube(A["metal"], (x, y, ZL), (x, y, ZL + 5.5), 0.1, (0.2, 0.2, 0.2), n=4)
            box(A["small"], x - 0.5, y - 0.4, ZL + 5.5, x + 0.5, y + 0.4, ZL + 6.2, (1.0, 0.8, 0.5), 10.0)
            K.add_light("work_%d" % nl, "SPOT", (x, y - 0.6, ZL + 5.6), SW["lamp_w"] * 0.9, (1.0, 0.78, 0.5),
                        aim=(x + 2.0, y + 9.0, ZL), size=0.4, spot=55, blend=0.6, group="corp", shadow=False)
            nl += 1
        x += 38.0
    x = XA + 20.0
    while x < XB - 10.0:
        if not (dxa < x < dxb) and SW["green_w"] > 0:
            K.add_light("chan_%d" % int(x), "AREA", (x, (c0 + c1) / 2, ZL + 6.0), SW["green_w"], GREEN,
                        aim=(x, (c0 + c1) / 2, zw), size=24.0, size_y=c1 - c0 + 4.0, group="corp", shadow=False)
        x += 40.0
    for sx_ in (dxa + 12.0, dxb - 12.0):                    # the sump: two lamp pools, not a fill
        K.add_light("sump_pool_%d" % int(sx_), "SPOT", (sx_, TY - 4.0, ZL + 2.0), SW["lamp_w"], GREEN,
                    aim=(sx_, TY - 16.0, ZD), size=0.4, spot=50, blend=0.6, group="corp", shadow=False)
    # ---------------------------------------------------------------- t4: the front cut: brick barrel-vault profiles
    # The gallery's front edge is the section cut through the earth (y = ya). Brick BARREL-VAULT sewers run off under
    # the front ledge toward the camera; the cut shows each one's profile: a voussoir ring, a dark mouth, black water
    # with a glint, a cage lamp over it. Elsewhere the cut is solid earth (brick poche).
    EB = ZL - 48.0                                     # (deep enough for the trunk sewer's section)
    VAULTS = [v for v in HZ["v3"].get("vaults", []) if not (dxa - 10 < v[0] < dxb + 10)]
    yv1 = c0 - 0.6
    spans = []
    for (vx, vr) in VAULTS:
        spans.append((vx - vr - 1.3, vx + vr + 1.3))
    x = XA
    cuts = sorted([(a_, b_) for a_, b_ in spans] + [(dxa, dxb)])
    for (a_, b_) in cuts:                                   # solid earth between the vaults (not under the sump)
        if a_ > x:
            box(BR, x, ya, EB, a_, yv1, ZL - 1.2, BRICK_D)
        x = max(x, b_)
    if x < XB:
        box(BR, x, ya, EB, XB, yv1, ZL - 1.2, BRICK_D)
    box(BR, dxa, ya, EB, dxb, TY, ZD - 1.2, BRICK_D)
    RING = (0.24, 0.19, 0.15)
    for k_, (vx, vr) in enumerate(VAULTS):
        zs = ZL - 1.2 - 1.3 - vr                            # springline (crown under the ledge slab + the ring)
        zf = zs - vr * 0.45                                 # the floor (straight walls below the springline)
        n = 16
        for i in range(n):                                  # earth over the arch, slice by slice
            x0_ = vx - vr - 1.3 + (2 * vr + 2.6) * i / n
            x1_ = vx - vr - 1.3 + (2 * vr + 2.6) * (i + 1) / n
            xm = (x0_ + x1_) / 2 - vx
            top = zs + math.sqrt(max(0.0, (vr + 1.3) ** 2 - xm * xm))
            box(BR, x0_, ya, top, x1_, yv1, ZL - 1.2, BRICK_D)
        box(BR, vx - vr - 1.3, ya, EB, vx + vr + 1.3, yv1, zf, BRICK_D)                  # under the floor
        for sx in (-1, 1):                                                                # the side walls
            box(BR, vx + sx * vr, ya, zf, vx + sx * (vr + 1.3), yv1, zs, BRICK)
        for i in range(n):                                  # the voussoir ring on the cut face + the vault's soffit
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            c0_, s0_, c1_, s1_ = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
            BR.face([(vx + vr * c0_, ya - 0.08, zs + vr * s0_), (vx + vr * c1_, ya - 0.08, zs + vr * s1_),
                     (vx + (vr + 1.3) * c1_, ya - 0.08, zs + (vr + 1.3) * s1_),
                     (vx + (vr + 1.3) * c0_, ya - 0.08, zs + (vr + 1.3) * s0_)], RING)
            BR.face([(vx + vr * c1_, ya, zs + vr * s1_), (vx + vr * c0_, ya, zs + vr * s0_),
                     (vx + vr * c0_, yv1, zs + vr * s0_), (vx + vr * c1_, yv1, zs + vr * s1_)], BRICK)
        box(BR, vx - vr - 1.4, ya - 0.1, zs - 0.4, vx - vr + 0.1, ya, zs, RING)                     # imposts
        box(BR, vx + vr - 0.1, ya - 0.1, zs - 0.4, vx + vr + 1.4, ya, zs, RING)
        box(BR, vx - 0.7, ya - 0.14, zs + vr - 0.2, vx + 0.7, ya - 0.06, zs + vr + 1.5, (0.28, 0.22, 0.17))   # keystone
        box(BR, vx - vr, ya, zf - 0.6, vx + vr, yv1, zf, (0.06, 0.06, 0.05))                           # its floor
        box(WAT, vx - vr + 0.6, ya - 3.0, zf, vx + vr - 0.6, yv1 - 0.4, zf + 0.5, (0, 0, 0))           # black water
        box(A["metal"], vx - vr, yv1 - 0.5, zf, vx + vr, yv1 - 0.3, zs + vr, (0.04, 0.04, 0.04))       # a grate, deep
        box(A["small"], vx - 0.4, ya - 0.9, zs + vr + 1.9, vx + 0.4, ya - 0.3, zs + vr + 2.5, (0.75, 1.0, 0.8), 8.0)
        K.add_light("vault_lamp_%d" % k_, "SPOT", (vx, ya - 1.6, zs + vr + 1.8), SW["lamp_w"] * 0.7, GREEN,
                    aim=(vx, ya + 4.0, zf), size=0.4, spot=55, blend=0.6, group="corp", shadow=False)
        K.add_light("vault_deep_%d" % k_, "POINT", (vx, yv1 - 4.0, zs), SW["lamp_w"] * 0.12, GREEN, size=0.6,
                    group="corp", shadow=False)
        box(FAL, vx - 1.6, c0 - 0.7, zf + 0.5, vx + 1.6, c0 - 0.5, zw, (0, 0, 0))   # the channel drains into it
    # finals (AD): the cut face below the vaults is a drawn SECTION, not an empty field: strata courses, cut pipe ends
    # with rims, and one deep trunk sewer's round mouth under the sump (dark, rimmed, a green glint at its invert)
    def flat_mouth(x, z, r, rim, glint=False):
        n = 20
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            c0_, s0_, c1_, s1_ = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
            BR.face([(x + r * c0_, ya - 0.1, z + r * s0_), (x + r * c1_, ya - 0.1, z + r * s1_),
                     (x + (r + 0.18 * r + 0.25) * c1_, ya - 0.1, z + (r + 0.18 * r + 0.25) * s1_),
                     (x + (r + 0.18 * r + 0.25) * c0_, ya - 0.1, z + (r + 0.18 * r + 0.25) * s0_)], rim)
        DARK.face([(x + r * math.cos(2 * math.pi * i / n), ya - 0.06, z + r * math.sin(2 * math.pi * i / n))
                   for i in range(n)], (0.0, 0.0, 0.0), 0.0)
        if glint:
            box(WAT, x - r * 0.7, ya - 0.2, z - r * 0.92, x + r * 0.7, ya - 0.07, z - r * 0.72, (0, 0, 0))
    vsp = [(vx - vr - 1.5, vx + vr + 1.5) for (vx, vr) in VAULTS] + [(dxa - 1.0, dxb + 1.0)]
    for zz, col in ((ZL - 15.0, (0.16, 0.13, 0.10)), (ZL - 21.5, (0.09, 0.08, 0.07)), (ZL - 29.0, (0.14, 0.12, 0.09))):
        box(BR, XA, ya - 0.12, zz, XB, ya, zz + 0.9, col)                        # strata courses
    for _ in range(26):                                                           # cut pipe ends
        x = rd.uniform(XA + 10, XB - 10)
        r_ = rd.uniform(0.5, 1.5)
        z = rd.uniform(ZL - 36.0, ZL - 10.0)
        if any(a_ - r_ < x < b_ + r_ for (a_, b_) in vsp[:-1]) and z > ZL - 22.0:
            continue
        if dxa - 2 < x < dxb + 2 and z > ZD - 3.0:
            continue
        flat_mouth(x, z, r_, [(0.22, 0.2, 0.18), (0.25, 0.14, 0.08), (0.12, 0.2, 0.15)][_ % 3])
    tx, trr = (dxa + dxb) / 2, 7.5                                                # the deep trunk under the sump
    flat_mouth(tx, ZD - 4.5 - trr, trr, (0.24, 0.19, 0.15), glint=True)
    K.add_light("trunk_glint", "SPOT", (tx, ya - 6.0, ZD - 2.0), SW["lamp_w"] * 0.6, GREEN,
                aim=(tx, ya, ZD - 4.5 - 2 * trr), size=0.4, spot=40, blend=0.6, group="corp", shadow=False)
    box(A["small"], tx - 0.4, ya - 0.7, ZD - 3.4, tx + 0.4, ya - 0.2, ZD - 2.8, (0.75, 1.0, 0.8), 7.0)
    for k_, lx in enumerate((-150.0 if not (dxa < -150 < dxb) else -180.0, -10.0, 80.0, -280.0)):   # grazing lamps
        box(A["small"], lx - 0.4, ya - 0.8, ZL - 8.6, lx + 0.4, ya - 0.2, ZL - 8.0, (0.75, 1.0, 0.8), 7.0)
        K.add_light("cut_lamp_%d" % k_, "SPOT", (lx, ya - 1.2, ZL - 8.8), SW["lamp_w"] * 0.7, GREEN,
                    aim=(lx, ya - 0.3, ZL - 34.0), size=0.3, spot=60, blend=0.7, group="corp", shadow=False)
    K.log("sewer: vault profiles", len(VAULTS))
    # ---------------------------------------------------------------- thin dark strata over the water (no fog plane)
    m = bpy.data.materials.new("sewer_strata")
    try:
        m.use_nodes = True
    except Exception:  # noqa: BLE001
        pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    g = nt.nodes.new("ShaderNodeNewGeometry")
    sp = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(g.outputs["Position"], sp.inputs[0])
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.03, 0.09, 0.9)
    nt.links.new(g.outputs["Position"], mp.inputs["Vector"])
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 1.0
    nz.inputs["Detail"].default_value = 4.0
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    hgt = 3.5
    fall = K.mth(nt, "SUBTRACT", 1.0, K.smooth(nt, sp.outputs["Z"], zw, ZL + hgt))
    dens = K.mth(nt, "MULTIPLY", K.mth(nt, "MULTIPLY", K.smooth(nt, nz.outputs["Fac"], 0.42, 0.66), fall), 0.03)
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.55, 0.85, 0.65, 1.0)                    # a green mist (lit by the lamps)
    pv.inputs["Absorption Color"].default_value = (0.75, 0.85, 0.78, 1.0)
    nt.links.new(dens, pv.inputs["Density"])
    nt.links.new(pv.outputs[0], out.inputs["Volume"])
    me = bpy.data.meshes.new("sewer_strata")
    x0, y0, z0, x1, y1, z1 = XA, ya, zw - 0.5, XB, TY - 0.2, ZL + hgt + 1.0
    me.from_pydata([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
                    (x0, y1, z1)], [], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    ob = bpy.data.objects.new("sewer_strata", me)
    K.COLL["media"].objects.link(ob)
    ob.data.materials.append(m)
    # the big green fills light the brick and the ledges but never mirror in the water as glowing slabs (the water
    # reflects the lamps, the signs and the city instead)
    for ob in bpy.data.objects:
        if ob.type == "LIGHT" and ob.name.startswith(("chan_", "sump_green", "sewer_cascade")):
            try:
                ob.visible_glossy = False
            except AttributeError:
                pass
    K.log("sewer: outfalls", nof, "culverts", len(gaps), "work lamps", nl)
    return Vector
