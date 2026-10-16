"""Rebel Cell v2 round 2: THE UNDERCROFT (art director 20:55: the bottom of the frame was a flat blown fog plane;
"replace it with the alley floor: wet dark street, stalls, cables, sign reflections, thin dark low fog strata").
Blender side, through the kit's K helpers and rc_alley's sign helpers. Seed 8413.

The service tunnel (the third lane, under the alley) opens on its camera side onto a SUNKEN SERVICE STREET one level
down (the tunnel's own floor level, a Tokyo two-level street): the section face at the kerb becomes a retaining wall
with the alley above it, and the lower street fills the bottom of the frame:
  floor        wet asphalt (the kit's ground material: puddles, sign reflections) from the retaining wall `uc_w` BU toward
               the camera; in front of the detour rooms (the deeper level) a sunken PIT one more level down, with side
               walls and a stair, so the deeper rooms stay open to the camera
  wall         the retaining wall's face: a lit fascia band over the tunnel's arcade, multilingual blade signs between
               the rooms, roll shutters + lit shop fronts on the wall beyond the tunnel, pipes, a kerb railing on top
  street life  yatai stalls with lanterns (never in front of a room), scooters, crates, utility poles with sagging
               cable bundles strung up to the kerb, lantern strings
  air          thin dark LOW FOG STRATA over the lower floor (a volume a few BU deep, layered noise, low density)
Nothing is placed in front of a room opening (rc_alley.over_room with the lower level's band)."""
import math
import random


def build(K, AL, over_room, tex_quads, facing_quad, blades, boards, hooks=None):
    import bpy
    G, CP, LH = K.G, K.CP, K.LH
    A, box, tube = K.A, K.box, K.tube
    Vector = K.Vector
    rd = random.Random(8413)
    RH = CP["room_h"]
    TY = G.TY
    ZL = G.ZL["R"] - 3.0                                    # the lower street = the tunnel's floor
    ZT = G.ZL["R"] + RH + 4.0                               # the tunnel's top (the arcade's lintel)
    ZD = G.ZL["R"] - 15.0                                   # the pit floor (the deeper detour level)
    dxa, dxb = G.XS["2a"] - 12.0, G.XS["2b"] + 12.0
    xa, xb = G.X0 - 45.0, G.SHAFT_X + 4.0                   # the tunnel's span
    LW = AL["uc_w"]
    ya = TY - LW
    XA, XB = AL["x_a"] - 70.0, AL["x_b"] + 70.0
    ASP = (0.09, 0.088, 0.095)

    # ---------------------------------------------------------------- the floor + the pit
    # its own wet asphalt (art director, full render: no defocus smear). The smear was the post's zoom LOD, which
    # blurs every ground-index pixel (index 4) when zoomed out; this floor is its own object (index 1), so it stays
    # sharp. Wet asphalt with a slight sheen (rough 0.14) and SHARP puddles (rough 0.03) that mirror the stalls,
    # lanterns and signs.
    fm, fnt = K.new_mat("uc_floor")
    fo = fnt.nodes.new("ShaderNodeOutputMaterial")
    fb = fnt.nodes.new("ShaderNodeBsdfPrincipled")
    fg, fps, _ = K.pos_sep(fnt)
    fn1 = K.nn(fnt, "ShaderNodeTexNoise", Scale=0.11, Detail=4.0, Roughness=0.55)
    fnt.links.new(fg.outputs["Position"], fn1.inputs["Vector"])
    pud = K.smooth(fnt, fn1.outputs["Fac"], 0.45, 0.48)
    fn2 = K.nn(fnt, "ShaderNodeTexNoise", Scale=1.3, Detail=6.0, Roughness=0.6)
    fnt.links.new(fg.outputs["Position"], fn2.inputs["Vector"])
    alb = K.mth(fnt, "MULTIPLY", K.mth(fnt, "ADD", 0.75, K.mth(fnt, "MULTIPLY", fn2.outputs["Fac"], 0.5)),
                K.mth(fnt, "SUBTRACT", 1.0, K.mth(fnt, "MULTIPLY", pud, 0.6)))
    fca = K.attr(fnt, "col")
    fnt.links.new(K.vsc(fnt, fca.outputs["Color"], alb), fb.inputs["Base Color"])
    fnt.links.new(K.mth(fnt, "ADD", 0.03, K.mth(fnt, "MULTIPLY", K.mth(fnt, "SUBTRACT", 1.0, pud), 0.11)), fb.inputs["Roughness"])
    fb.inputs["Specular IOR Level"].default_value = 0.6
    FL = K.Acc("uc_floor", fm, 1, K.COLL["compound"])
    if hooks is not None:
        hooks.setdefault("accs", {})["uc_floor"] = FL
    else:
        FL = A["ground"]
    for (x0_, x1_) in ((XA, dxa), (dxb, XB)):
        box(FL, x0_, ya, ZL - 1.2, x1_, TY, ZL, ASP, k=0.0)
        box(A["trim"], x0_, ya - 0.05, ZL - 0.5, x1_, ya, ZL - 0.3, (1.0, 0.5, 0.25), 0.4)      # the slab's cut edge
    box(FL, dxa, ya, ZD - 1.2, dxb, TY, ZD, ASP, k=0.0)
    for xx in (dxa, dxb):
        box(A["rough"], xx - 0.7, ya, ZD, xx + 0.7, TY, ZL, (0.05, 0.045, 0.045))
        box(A["trim"], xx - 0.75, ya, ZL - 0.25, xx + 0.75, TY, ZL - 0.1, (1.0, 0.75, 0.3), 1.6)    # the pit's lit lip
        for k_ in range(4):
            box(A["metal"], xx - 0.9, ya + 4.0 + k_ * (LW - 8.0) / 3, ZL, xx + 0.9, ya + 4.3 + k_ * (LW - 8.0) / 3, ZL + 1.1,
                (0.25, 0.22, 0.18))
    ns = 10                                                 # the pit's stair (down along its left wall)
    for s in range(ns):
        z1 = ZL - (ZL - ZD) * (s + 1) / ns
        y0 = TY - 18.0 - s * 2.2
        box(A["rough"], dxa + 0.7, y0 - 2.2, ZD, dxa + 6.0, y0, z1 + (ZL - ZD) / ns, (0.08, 0.075, 0.075))
    # puddle glints: thin emissive sheets under the signs (the reflection reads even at low samples)
    # ---------------------------------------------------------------- the retaining wall's face
    WY = TY - 0.05
    box(A["trim"], XA, WY - 0.12, ZT - 0.2, XB, WY, ZT + 0.5, (1.0, 0.62, 0.3), 1.4)             # the fascia band
    box(A["metal"], XA, WY - 1.6, ZT + 0.5, XB, WY, ZT + 0.8, (0.12, 0.11, 0.1))                 # its canopy lip
    box(A["metal"], XA, TY - 0.6, -0.1, XB, TY - 0.45, 1.2, (0.22, 0.2, 0.18))                   # the kerb railing
    x = XA + 2.0
    while x < XB:
        tube(A["metal"], (x, TY - 0.5, -0.1), (x, TY - 0.5, 1.2), 0.07, (0.22, 0.2, 0.18), n=4)
        x += 2.5
    for q in range(3):                                                                            # pipes on the wall
        zz = ZT + 2.0 + q * 1.3
        tube(A["metal"], (XA, WY - 0.5 - q * 0.3, zz), (XB, WY - 0.5 - q * 0.3, zz), 0.3 - 0.06 * q,
             [(0.2, 0.15, 0.1), (0.12, 0.16, 0.14), (0.3, 0.1, 0.07)][q], n=6)
    # blades between the rooms on the wall above the arcade
    nb = 0
    x = XA + 4.0
    while x < XB - 4.0:
        bw = rd.uniform(2.2, 3.2)
        z0 = ZT + rd.uniform(1.6, 4.5)
        z1 = min(-1.0, z0 + bw * rd.uniform(1.6, 3.4))
        if rd.random() < 0.45:                              # gaps: clusters, never a ticker row
            x += rd.uniform(6.0, 16.0)
            continue
        if not over_room(x + bw / 2, z0, z1, pad=0.5) and blades and z1 > z0 + 3.0:
            tex_quads(blades[rd.randrange(len(blades))], [facing_quad(x, x + bw, WY - 1.0, z0, z1, rd.uniform(-22, 22))],
                      AL["sign_k"] * 0.9)
            K.add_light("uc_sign_%d" % nb, "AREA", (x + bw / 2, WY - 2.5, (z0 + z1) / 2), LH["uc_sign_w"],
                        [(1.0, 0.2, 0.6), (0.3, 0.8, 1.0), (1.0, 0.55, 0.2), (0.75, 0.3, 1.0)][nb % 4], aim=(x + bw / 2, WY - 14.0, ZL), size=bw + 1.0, size_y=z1 - z0,
                        group="corp", shadow=False)
            nb += 1
        x += bw + rd.uniform(1.5, 7.0)
    # beyond the tunnel: the wall comes down to the lower street: undercroft shops (roll shutters + lit fronts + boards)
    for (s0, s1) in ((XA, xa), (xb, XB)):
        x = s0 + 2.0
        while x < s1 - 8.0:
            w_ = rd.uniform(7.0, 11.0)
            x1_ = min(x + w_, s1 - 1.0)
            if rd.random() < 0.6:
                fc_ = [(1.0, 0.62, 0.32), (1.0, 0.78, 0.5), (0.7, 0.85, 1.0), (1.0, 0.4, 0.62)][rd.randrange(4)]
                box(A["sign"], x + 0.4, WY - 0.08, ZL, x1_ - 0.4, WY - 0.02, ZL + 4.2, fc_, rd.uniform(1.4, 2.4))
                K.add_light("uc_shop_%d" % int(x), "AREA", ((x + x1_) / 2, WY - 1.2, ZL + 3.8), LH["uc_shop_w"], fc_,
                            aim=((x + x1_) / 2, WY - 10.0, ZL), size=x1_ - x, size_y=3.0, group="corp", shadow=False)
                box(A["metal"], x + 0.2, WY - 2.2, ZL + 4.3, x1_ - 0.2, WY, ZL + 4.55, (0.14, 0.1, 0.1))
                if boards:
                    tex_quads(boards[rd.randrange(len(boards))],
                              [facing_quad(x + 0.6, x1_ - 0.6, WY - 0.15, ZL + 4.8, ZL + 4.8 + (x1_ - x - 1.2) / 4)], 2.0)
            else:
                for q in range(9):
                    box(A["metal"], x + 0.3, WY - 0.12, ZL + q * 0.5, x1_ - 0.3, WY - 0.05, ZL + q * 0.5 + 0.42,
                        (0.24, 0.23, 0.22))
                box(A["sign"], x + 1.0, WY - 0.14, ZL + 1.4, x + 3.6, WY - 0.13, ZL + 2.6,
                    [(1.0, 0.2, 0.6), (0.2, 0.9, 1.0), (1.0, 0.8, 0.2)][rd.randrange(3)], 1.4)
            x = x1_ + rd.uniform(0.5, 2.0)
    # ---------------------------------------------------------------- street life: stalls, scooters, crates
    nst = 0
    x = XA + 10.0
    while x < XB - 10.0:
        sy_ = TY - rd.uniform(9.0, 26.0)
        w_, d_ = rd.uniform(4.5, 6.5), 2.6
        in_pit = dxa - 4.0 < x < dxb + 4.0
        if not in_pit and not over_room(x, ZL, ZL + 6.0, pad=6.0):
            z0 = ZL
            box(A["rough"], x - w_ / 2, sy_ - d_ / 2, z0, x + w_ / 2, sy_ + d_ / 2, z0 + 1.9, (0.16, 0.09, 0.06))
            box(A["sign"], x - w_ / 2 + 0.2, sy_ - d_ / 2 - 0.02, z0 + 1.2, x + w_ / 2 - 0.2, sy_ - d_ / 2, z0 + 1.8,
                (1.0, 0.6, 0.3), 2.2)
            for (ex, ey) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
                tube(A["metal"], (x + ex * w_ / 2, sy_ + ey * d_ / 2, z0 + 1.9), (x + ex * w_ / 2, sy_ + ey * d_ / 2, z0 + 3.8),
                     0.08, (0.15, 0.15, 0.15), n=4)
            box(A["rough"], x - w_ / 2 - 0.4, sy_ - d_ / 2 - 0.6, z0 + 3.8, x + w_ / 2 + 0.4, sy_ + d_ / 2, z0 + 4.0,
                [(0.5, 0.06, 0.06), (0.1, 0.1, 0.35), (0.45, 0.32, 0.05)][nst % 3])
            for q in range(3):
                lx_ = x - w_ / 2 + 0.8 + q * (w_ - 1.6) / 2
                box(A["small"], lx_ - 0.35, sy_ - d_ / 2 - 0.75, z0 + 2.9, lx_ + 0.35, sy_ - d_ / 2 - 0.15, z0 + 3.6,
                    (1.0, 0.25, 0.12), 9.0)
            K.add_light("uc_stall_%d" % nst, "POINT", (x, sy_ - d_ / 2 - 1.5, z0 + 3.2), LH["stall_w"] * 4.0,
                        (1.0, 0.45, 0.2), size=1.0, group="corp", shadow=False)
            nst += 1
        x += rd.uniform(13.0, 21.0)
    for _ in range(26):
        cx_ = rd.uniform(XA, XB)
        if dxa - 2 < cx_ < dxb + 2:
            continue
        cy_ = TY - rd.uniform(3.0, LW - 6.0)
        if rd.random() < 0.5:
            box(A["metal"], cx_, cy_ - 0.3, ZL + 0.4, cx_ + 2.0, cy_ + 0.3, ZL + 1.1,
                [(0.5, 0.1, 0.1), (0.1, 0.3, 0.5), (0.7, 0.7, 0.7)][_ % 3])
            box(A["small"], cx_ + 1.9, cy_ - 0.2, ZL + 0.9, cx_ + 2.05, cy_ + 0.2, ZL + 1.05, (1.0, 0.9, 0.7), 4.0)
        else:
            s_ = rd.uniform(0.7, 1.5)
            box(A["rough"], cx_, cy_, ZL, cx_ + s_, cy_ + s_, ZL + s_, (0.12, 0.1, 0.08))
    # ---------------------------------------------------------------- poles, cables, lantern strings, lamps
    def catenary(p, q, sag, r=0.06, col=(0.05, 0.05, 0.06), n=10):
        pts = []
        for i in range(n + 1):
            t = i / n
            pts.append(Vector((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t,
                               p[2] + (q[2] - p[2]) * t - sag * 4 * t * (1 - t))))
        for a_, b_ in zip(pts, pts[1:]):
            tube(A["metal"], a_, b_, r, col, n=4)
        return pts
    PY = ya + 14.0
    PH = 15.0
    poles = []
    x = XA + 18.0
    while x < XB:
        if not (dxa - 3 < x < dxb + 3):
            poles.append(x)
        x += rd.uniform(34.0, 44.0)
    for px in poles:
        tube(A["metal"], (px, PY, ZL), (px, PY, ZL + PH), 0.32, (0.16, 0.15, 0.14), n=8)
        box(A["metal"], px - 2.2, PY - 0.15, ZL + PH - 2.0, px + 2.2, PY + 0.15, ZL + PH - 1.7, (0.16, 0.15, 0.14))
        box(A["metal"], px, PY, ZL + PH - 4.0, px + 0.2, PY + 3.0, ZL + PH - 3.8, (0.16, 0.15, 0.14))
        box(A["small"], px - 0.4, PY + 2.6, ZL + PH - 4.3, px + 0.6, PY + 3.4, ZL + PH - 4.0, (1.0, 0.75, 0.45), 14.0)
        K.add_light("uc_lamp_%d" % int(px), "SPOT", (px, PY + 3.0, ZL + PH - 4.5), LH["alley_lamp_w"], (1.0, 0.72, 0.42),
                    aim=(px, PY + 6.0, ZL), size=0.6, spot=110, blend=0.9, group="corp", shadow=False)
        for k_ in range(3):                                   # bundles up to the kerb
            tx = px + rd.uniform(-12, 12)
            catenary((px, PY, ZL + PH - 1.8), (tx, TY - 0.6, 0.6), rd.uniform(1.5, 3.0), r=0.05)
    for a_, b_ in zip(poles, poles[1:]):
        for zz in (ZL + PH - 1.8, ZL + PH - 2.4):
            catenary((a_, PY, zz), (b_, PY, zz), rd.uniform(1.6, 2.8), r=0.06)
        q_ = catenary((a_, PY, ZL + PH - 3.2), ((a_ + b_) / 2, TY - 0.6, 0.4), rd.uniform(1.5, 2.5), r=0.03, n=14)
        for p_ in q_[1:-1]:                                   # a lantern string across the street (pole -> kerb)
            box(A["small"], p_.x - 0.3, p_.y - 0.3, p_.z - 0.9, p_.x + 0.3, p_.y + 0.3, p_.z - 0.3,
                [(1.0, 0.25, 0.12), (1.0, 0.7, 0.3), (1.0, 0.2, 0.5)][rd.randrange(3)], 8.0)
        pts = catenary((a_, PY + 0.2, ZL + PH - 3.0), (b_, PY + 0.2, ZL + PH - 3.0), rd.uniform(2.0, 3.0), r=0.03)
        K.add_light("uc_lantern_%d" % int(a_), "AREA", ((a_ + b_) / 2, PY + 0.2, ZL + PH - 5.5), LH["uc_lantern_w"],
                    (1.0, 0.45, 0.25), aim=((a_ + b_) / 2, PY + 0.2, ZL), size=b_ - a_, size_y=3.0, group="corp",
                    shadow=False)
        for p_ in pts[1:-1]:                                   # a lantern string
            box(A["small"], p_.x - 0.3, p_.y - 0.3, p_.z - 0.9, p_.x + 0.3, p_.y + 0.3, p_.z - 0.3,
                [(1.0, 0.25, 0.12), (1.0, 0.7, 0.3), (1.0, 0.2, 0.5)][rd.randrange(3)], 8.0)
    # the arcade's own spill + the sign wash on the wet floor (light, not exposure)
    for x in range(int(XA) + 20, int(XB), 48):
        K.add_light("uc_wash_%d" % x, "AREA", (x, TY - 3.0, ZT - 1.0), LH["uc_wash_w"], (1.0, 0.55, 0.3),
                    aim=(x, TY - 14.0, ZL), size=30.0, size_y=4.0, group="corp", shadow=False)
    # ---------------------------------------------------------------- the low fog strata (thin, dark)
    m = bpy.data.materials.new("uc_strata")
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
    nz.inputs["Roughness"].default_value = 0.6
    nt.links.new(mp.outputs[0], nz.inputs["Vector"])
    hgt = AL["uc_fog_h"]
    fall = K.mth(nt, "SUBTRACT", 1.0, K.smooth(nt, sp.outputs["Z"], ZL + 0.3, ZL + hgt))
    dens = K.mth(nt, "MULTIPLY", K.mth(nt, "MULTIPLY", K.smooth(nt, nz.outputs["Fac"], 0.42, 0.66), fall), AL["uc_fog_d"])
    pv = nt.nodes.new("ShaderNodeVolumePrincipled")
    pv.inputs["Color"].default_value = (0.72, 0.38, 0.66, 1.0)              # red-violet (lit by the signs)
    pv.inputs["Absorption Color"].default_value = (0.8, 0.7, 0.8, 1.0)
    pv.inputs["Anisotropy"].default_value = 0.35
    nt.links.new(dens, pv.inputs["Density"])
    nt.links.new(pv.outputs[0], out.inputs["Volume"])
    zb = ZL - 1.0                                           # (the pit stays clear: the deeper rooms read)
    me = bpy.data.meshes.new("uc_strata")
    x0, y0, z0, x1, y1, z1 = XA, ya, zb, XB, TY - 0.2, ZL + hgt + 1.0
    me.from_pydata([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1),
                    (x0, y1, z1)], [], [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    ob = bpy.data.objects.new("uc_strata", me)
    K.COLL["media"].objects.link(ob)
    ob.data.materials.append(m)
    K.log("undercroft: stalls", nst, "poles", len(poles), "blades", nb)
# RC_FLOORLIGHT
