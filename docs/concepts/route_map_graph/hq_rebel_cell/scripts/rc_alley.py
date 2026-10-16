"""Rebel Cell v2: the TOKYO ALLEY CANYON round option A's three lanes (designer review 2026-10-15, bible 3.14 / 4.4 /
4.10). Blender side, through the kit's K helpers. Seeds: 8410 (frontage), 8411 (dressing), 8412 (signs).

The section (option A) now cuts through a narrow wet ALLEY (alley_w BU) in front of a continuous frontage:
  frontage    the lane buildings (hq_build_A) + narrow attached INFILL buildings (6-11 BU wide, 16-46 tall) filling every
              gap along the facade line; all carry the district's window shader (so the red fist reads in them too)
  facades     AC units and balconies per floor, fire-escape STAIR-BACKS on infill faces, ledge neon, shop boards and lit
              shop fronts on the infill ground floors, roll shutters, vending machines
  blade signs multilingual blades (Japanese, Korean, Chinese, English) filled edge to edge between z_lo and the roofs,
              angled +-25 deg off the facade so they read as blades from the side camera; DISPATCH takeover blades
              (red, anti-human slogans) mixed in (takeover_p)
  the alley   a wet asphalt slab over the section void (its front edge = the kerb line), utility poles at the kerb
              between the lane columns with sagging cable bundles along and across, conduits hanging under the slab
              (the cut shows them), manholes, crates
  holograms   food (ramen) and chip holograms over the alley between the lanes; anti-human banners on the roofs; the
              RED FIST hologram (the nearest right hologram, DISPATCH version) beside DISPATCH
  MAINFRAME   the locked v4 sign (red variant: the Cell's district) on the shop just before the first lane column,
              with its cyan shop front and the red spill on the wet alley
  street light the district grid's streets lit by long sodium strips (also lifts the red-sequence frames: light, not
              exposure)
Never covers a room: nothing is placed in front of a room opening (x within room_w / 2 + 1.5 of a lane column at the
room's height band); signs and holograms sit between the street lane and the roof lane, or between columns.
"""
import math
import os
import random

AL = dict(x_a=-262.0, x_b=72.0, infill_w=(6.0, 11.0), infill_h=(26.0, 74.0), depth=9.0,
          blade_w=(2.6, 3.4), blade_z=(9.5, 66.0), takeover_p=0.28, pole_h=24.0, holo_k=3.2, sign_k=2.6, mf_k=4.2,
          mf_w=11.0, mf_z0=3.5, mf_off=3.2, holo_s=(15.0, 18.0), fist_s=20.0,
          uc_w=84.0, uc_fog_h=4.5, uc_fog_d=0.027)     # v2 r2: the undercroft (rc_undercroft): depth, low strata      # the alley width: stack.alley_w


def build(K, DIST, cat, hooks, tex_dir, only=False):
    import bpy
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, box, tube = K.A, K.box, K.tube
    Vector = K.Vector
    ST = CP["stack"]
    CUT = ST["cut"]
    RW = CP["room_w"]
    rr = random.Random(8410)
    rd = random.Random(8411)
    rs = random.Random(8412)
    cols = sorted({round(r["o"][0], 1) for i, r in G.ROOM.items() if i not in ("start", "srv")})
    lane_spans = [(c - 10.5, c + 10.5) for c in cols] + [(G.SHAFT_X - 4.0, G.SHAFT_X + 4.0),
                                                         (ST["dispatch_x"] - 12.5, ST["dispatch_x"] + 12.5)]
    MF = (G.SX + 12.0, G.X0 - 10.5)                         # the MAINFRAME shop's span (between the drop and lane 1)
    FY = CUT + 0.6                                          # the frontage facade line
    # the MAINFRAME hero sign (art director: large, the landmark): on the shop between the drop and lane 1
    MFS = ((MF[0] + MF[1]) / 2, AL["mf_z0"], AL["mf_z0"] + AL["mf_w"] * 999 / 246)      # x, z0, z1
    AW = ST["alley_w"]
    objs = []

    # ---------------------------------------------------------------- textured objects (signs, holograms)
    def tex_mat(name, img_path, k, holo=False):
        m = bpy.data.materials.new(name)
        try:
            m.use_nodes = True
        except Exception:  # noqa: BLE001
            pass
        nt = m.node_tree
        nt.nodes.clear()
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        ti = nt.nodes.new("ShaderNodeTexImage")
        ti.image = bpy.data.images.load(img_path, check_existing=True)
        ti.interpolation = "Cubic"
        pw = nt.nodes.new("ShaderNodeAttribute")
        pw.attribute_type = "OBJECT"
        pw.attribute_name = "pwo"
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(ti.outputs["Color"], em.inputs["Color"])
        mk = nt.nodes.new("ShaderNodeMath")
        mk.operation = "MULTIPLY"
        mk.inputs[1].default_value = k
        nt.links.new(pw.outputs["Fac"], mk.inputs[0])
        nt.links.new(mk.outputs[0], em.inputs["Strength"])
        if holo:
            # alpha from the line art's brightness; a faint flicker band (scan) in the projection
            sep = nt.nodes.new("ShaderNodeSeparateColor")
            nt.links.new(ti.outputs["Color"], sep.inputs[0])
            mx_ = nt.nodes.new("ShaderNodeMath")
            mx_.operation = "MAXIMUM"
            nt.links.new(sep.outputs[0], mx_.inputs[0])
            nt.links.new(sep.outputs[1], mx_.inputs[1])
            mx2 = nt.nodes.new("ShaderNodeMath")
            mx2.operation = "MAXIMUM"
            nt.links.new(mx_.outputs[0], mx2.inputs[0])
            nt.links.new(sep.outputs[2], mx2.inputs[1])
            al = nt.nodes.new("ShaderNodeMath")
            al.operation = "MULTIPLY"
            al.inputs[1].default_value = 0.9
            al.use_clamp = True
            nt.links.new(mx2.outputs[0], al.inputs[0])
            tr = nt.nodes.new("ShaderNodeBsdfTransparent")
            mix = nt.nodes.new("ShaderNodeMixShader")
            nt.links.new(al.outputs[0], mix.inputs[0])
            nt.links.new(tr.outputs[0], mix.inputs[1])
            nt.links.new(em.outputs[0], mix.inputs[2])
            nt.links.new(mix.outputs[0], out.inputs[0])
            try:
                m.surface_render_method = "DITHERED"
            except (AttributeError, TypeError):
                pass
        else:
            df = nt.nodes.new("ShaderNodeBsdfDiffuse")
            df.inputs["Color"].default_value = (0.02, 0.02, 0.025, 1.0)
            ad = nt.nodes.new("ShaderNodeAddShader")
            nt.links.new(df.outputs[0], ad.inputs[0])
            nt.links.new(em.outputs[0], ad.inputs[1])
            nt.links.new(ad.outputs[0], out.inputs[0])
        return m

    MATS = {}

    def tex_quads(fname, quads, k, holo=False, idx=1):
        key = (fname, holo, round(k, 2))
        if key not in MATS:
            MATS[key] = tex_mat("tex_%s_%d" % (os.path.splitext(fname)[0], len(MATS)), os.path.join(tex_dir, fname), k, holo)
        me = bpy.data.meshes.new("tq_" + fname)
        vs, fs = [], []
        for q in quads:
            b = len(vs)
            vs.extend(q)
            fs.append((b, b + 1, b + 2, b + 3))
        me.from_pydata(vs, [], fs)
        uv = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li, (u, v) in zip(poly.loop_indices, ((0, 0), (1, 0), (1, 1), (0, 1))):
                uv.data[li].uv = (u, v)
        ob = bpy.data.objects.new("tq_" + fname, me)
        K.COLL["compound"].objects.link(ob)
        ob.data.materials.append(MATS[key])
        ob.pass_index = idx
        ob["pwo"] = 1.0
        try:
            ob.visible_shadow = False
        except AttributeError:
            pass
        objs.append(ob)
        return ob

    def facing_quad(x0, x1, y, z0, z1, ang=0.0):
        """A quad facing the camera (-y), hinged at its left edge, swung by ang (deg, + = right edge toward camera)."""
        a = math.radians(ang)
        w = x1 - x0
        xr, yr = x0 + w * math.cos(a), y - w * math.sin(a)
        return [(x0, y, z0), (xr, yr, z0), (xr, yr, z1), (x0, y, z1)]

    def over_room(x, z0, z1, pad=1.5):
        """True if x (with the z band) falls in front of a room opening."""
        for i, r in G.ROOM.items():
            ox, _, oz = r["o"]
            if abs(x - ox) < r["w"] / 2 + pad and z1 > oz - 1.0 and z0 < oz + r["h"] + 1.5:
                return True
        return False

    def in_lane(x0, x1):
        return any(x1 > a and x0 < b for (a, b) in lane_spans)

    K.log("alley: textures from", tex_dir)
    if only:
        hooks.update(_street_strips(K, CP, LH, pal, section=False))
        return objs

    # ---------------------------------------------------------------- the frontage infill (attached narrow buildings)
    infill = []
    x = AL["x_a"]
    while x < AL["x_b"]:
        w = rr.uniform(*AL["infill_w"])
        x1 = min(x + w, AL["x_b"])
        if in_lane(x, x1):
            # skip to the end of the lane span
            ends = [b for (a, b) in lane_spans if x1 > a and x < b]
            x = max(ends) + 0.1
            continue
        if x1 > MF[0] and x < MF[1]:
            x = MF[1] + 0.1
            continue
        h = rr.uniform(*AL["infill_h"])
        infill.append((x, x1, h))
        x = x1 + rr.choice((0.0, 0.0, 0.0, 0.6))
    # the MAINFRAME shop building
    infill.append((MF[0], MF[1], MFS[2] + 8.0))
    for (x0, x1, h) in infill:
        c = cat((x0 + x1) / 2, FY + 4.5)
        colr = (0.075, 0.07, 0.08) if rr.random() < 0.6 else (0.09, 0.075, 0.075)
        box(DIST, x0, FY, 0.0, x1, FY + AL["depth"] + rr.uniform(0, 6), h, colr, k=float(c))
        # a stepped roof structure (water tank / stair hut) on some
        if rr.random() < 0.5:
            hx = (x0 + x1) / 2
            box(A["rough"], hx - 1.4, FY + 3, h, hx + 1.4, FY + 6, h + rr.uniform(2.5, 4.5), (0.08, 0.075, 0.08))
        if rr.random() < 0.35:
            hx = rr.uniform(x0 + 1.5, x1 - 1.5)
            tube(A["metal"], (hx, FY + 5, h + 1.2), (hx, FY + 5, h + 4.0), 1.3, (0.12, 0.10, 0.09), n=8)
            for (ex, ey) in ((-0.9, -0.9), (0.9, -0.9), (0.9, 0.9), (-0.9, 0.9)):
                tube(A["metal"], (hx + ex, FY + 5 + ey, h), (hx + ex, FY + 5 + ey, h + 1.2), 0.08, (0.1, 0.1, 0.1), n=4)
    K.log("alley: infill", len(infill))

    # ---------------------------------------------------------------- facade dressing (every frontage building)
    fronts = [(x0, x1, h) for (x0, x1, h) in infill]
    for c in cols:
        rf_ = max([r["o"][2] for i, r in G.ROOM.items() if abs(r["o"][0] - c) < 1 and G.LANE.get(i) == "L"] or [30.0])
        fronts.append((c - 10.0, c + 10.0, min(rf_, 36.0)))
    yf = FY - 0.05
    boards = sorted(f for f in os.listdir(tex_dir) if f.startswith("board_"))
    for (x0, x1, h) in fronts:
        is_lane = any(abs((x0 + x1) / 2 - c) < 1 for c in cols)
        # AC units / boxes on the facade (never in front of a room)
        for _ in range(int((x1 - x0) * h / 60)):
            ax = rd.uniform(x0 + 0.6, x1 - 1.8)
            az = rd.uniform(9.0, h - 2.0)
            if over_room(ax + 0.6, az, az + 1.0):
                continue
            box(A["metal"], ax, yf - 1.0, az, ax + 1.3, yf, az + 0.9, (0.2, 0.2, 0.21))
            box(A["small"], ax + 0.15, yf - 1.02, az + 0.15, ax + 0.35, yf - 1.0, az + 0.3, (1.0, 0.4, 0.2), 4.0)
        if is_lane:
            continue
        # ground floor: a lit shop front + an awning + a board (infill only: the lane buildings hold the street rooms)
        sc = [(1.0, 0.55, 0.25), (0.45, 0.9, 1.0), (1.0, 0.35, 0.55), (0.9, 0.95, 1.0)][rd.randrange(4)]
        if (x0, x1) == MF:
            sc = (0.35, 0.95, 1.0)                           # the MAINFRAME shop: cyan glass (the reference)
        box(A["sign"], x0 + 0.5, yf - 0.06, 0.3, x1 - 0.5, yf - 0.02, 3.6, sc, rd.uniform(1.6, 2.6))
        if rd.random() < 0.35:                               # roll shutter half down
            box(A["metal"], x0 + 0.5, yf - 0.2, 2.2, x1 - 0.5, yf - 0.1, 3.7, (0.16, 0.16, 0.17))
        box(A["metal"], x0 + 0.2, yf - 2.2, 3.9, x1 - 0.2, yf, 4.15, (0.14, 0.10, 0.10))
        if boards and (x1 - x0) > 5.5:
            bw = min(x1 - x0 - 1.0, 7.5)
            bx = (x0 + x1) / 2 - bw / 2
            tex_quads(boards[rd.randrange(len(boards))], [facing_quad(bx, bx + bw, yf - 0.25, 4.4, 4.4 + bw / 4)],
                      AL["sign_k"] * 0.8)
        # balconies with rails on some floors
        if rd.random() < 0.45:
            z = 8.0
            while z < h - 4:
                if rd.random() < 0.5:
                    box(A["metal"], x0 + 0.5, yf - 1.6, z, x1 - 0.5, yf, z + 0.25, (0.18, 0.18, 0.19))
                    box(A["metal"], x0 + 0.5, yf - 1.65, z + 0.25, x1 - 0.5, yf - 1.55, z + 1.3, (0.25, 0.25, 0.26))
                z += 3.9
        # fire-escape STAIR-BACK: a zigzag of flights + landings up the face
        if rd.random() < 0.3 and (x1 - x0) > 6.5:
            z = 4.2
            k_ = 0
            while z < h - 4:
                lx0, lx1 = (x0 + 0.6, x1 - 0.6)
                box(A["metal"], lx0, yf - 2.0, z, lx1, yf, z + 0.2, (0.17, 0.17, 0.18))
                box(A["metal"], lx0, yf - 2.05, z + 0.2, lx1, yf - 1.95, z + 1.2, (0.22, 0.22, 0.23))
                a_ = (lx0 + 0.4, yf - 1.0, z + 0.2) if k_ % 2 == 0 else (lx1 - 0.4, yf - 1.0, z + 0.2)
                b_ = (lx1 - 0.6, yf - 1.0, z + 3.9) if k_ % 2 == 0 else (lx0 + 0.6, yf - 1.0, z + 3.9)
                K.seg_box(A["metal"], Vector(a_), Vector(b_), 1.2, 0.3, (0.17, 0.17, 0.18))
                z += 3.9
                k_ += 1
        # a neon ledge line
        if rd.random() < 0.4:
            zz = rd.uniform(8, h - 3)
            c_ = [pal("neon_a"), pal("neon_b"), (1.0, 0.6, 0.2), (0.6, 1.0, 0.4)][rd.randrange(4)]
            box(A["trim"], x0 + 0.3, yf - 0.12, zz, x1 - 0.3, yf - 0.05, zz + 0.25, c_, 3.0)
        # vending machines at the shop door
        if rd.random() < 0.4:
            vx = rd.choice((x0 + 0.6, x1 - 2.2))
            box(A["metal"], vx, yf - 1.3, 0.0, vx + 1.6, yf, 3.2, (0.6, 0.6, 0.62))
            box(A["sign"], vx + 0.15, yf - 1.32, 0.9, vx + 1.45, yf - 1.3, 2.9, (0.85, 0.95, 1.0), 2.2)
    K.log("alley: facades")

    # ---------------------------------------------------------------- multilingual blade signs, edge to edge
    blades = sorted(f for f in os.listdir(tex_dir) if f.startswith("blade_") and not f.startswith("blade_red"))
    reds = sorted(f for f in os.listdir(tex_dir) if f.startswith("blade_red"))
    groups = {}
    x = AL["x_a"] + 1.0
    nb = 0
    while x < AL["x_b"] - 2:
        bw = rs.uniform(*AL["blade_w"])
        bh = bw * 4.0 * rs.uniform(0.85, 1.1)
        # the facade height there
        top = 0.0
        for (f0, f1, h) in fronts:
            if f0 <= x <= f1:
                top = h
        z0 = rs.uniform(AL["blade_z"][0], max(AL["blade_z"][0] + 0.1, min(AL["blade_z"][1], top - 1.5) - bh))
        if top > z0 + bh + 1.0 and not over_room(x + bw / 2, z0, z0 + bh, pad=2.0) and not (MF[0] - 2.0 < x + bw and x < MF[1] + 2.0):
            red = rs.random() < AL["takeover_p"]
            fn = (reds if red else blades)[rs.randrange(len(reds if red else blades))]
            ang = rs.choice((-25.0, 25.0, 18.0, -18.0))
            groups.setdefault(fn, []).append(facing_quad(x, x + bw, FY - 1.2, z0, z0 + bh, ang))
            box(A["metal"], x - 0.05, FY - 1.25, z0 + 0.3, x + 0.1, FY, z0 + 0.6, (0.2, 0.2, 0.2))
            box(A["metal"], x - 0.05, FY - 1.25, z0 + bh - 0.6, x + 0.1, FY, z0 + bh - 0.3, (0.2, 0.2, 0.2))
            nb += 1
            x += bw + rs.uniform(0.4, 1.4)
        else:
            x += 1.2
    for fn, qs in groups.items():
        tex_quads(fn, qs, AL["sign_k"])
    K.log("alley: blade signs", nb)

    # ---------------------------------------------------------------- the MAINFRAME sign (locked v4, red)
    # the hero: big, standing off the shop's facade on brackets (pass index 3: its own value check)
    mx, mz0, mz1 = MFS
    mh = mz1 - mz0
    mw = AL["mf_w"]
    my = FY - AL["mf_off"]
    tex_quads("mainframe.png", [facing_quad(mx - mw / 2, mx + mw / 2, my, mz0, mz1, 0.0)], AL["mf_k"], idx=3)
    box(A["metal"], mx - mw / 2 - 0.4, my + 0.05, mz0 - 0.4, mx + mw / 2 + 0.4, my + 0.8, mz1 + 0.4, (0.05, 0.03, 0.03))
    for zz in (mz0 + 3.0, (mz0 + mz1) / 2, mz1 - 3.0):
        box(A["metal"], mx - 0.3, my + 0.8, zz, mx + 0.3, FY, zz + 0.5, (0.2, 0.2, 0.2))
    K.add_light("mainframe_spill", "AREA", (mx, my - 3.0, (mz0 + mz1) / 2), LH["mf_spill_w"], (1.0, 0.08, 0.08),
                aim=(mx, FY + 2.0, 0.0), size=mw + 4.0, size_y=mh, group="corp", shadow=False)
    K.add_light("mainframe_floor", "AREA", (mx, my - 6.0, 2.0), LH["mf_spill_w"] * 0.6, (1.0, 0.1, 0.1),
                aim=(mx, my - 6.0, 0.0), size=mw + 10.0, size_y=10.0, group="corp", shadow=False)
    K.add_light("mainframe_shop", "AREA", ((MF[0] + MF[1]) / 2, FY - 3.0, 3.6), LH["mf_spill_w"] * 0.35, (0.4, 0.9, 1.0),
                aim=((MF[0] + MF[1]) / 2, FY - 10.0, 0.0), size=MF[1] - MF[0], size_y=2.0, group="corp", shadow=False)

    # ---------------------------------------------------------------- the alley: slab, kerb, poles, cables, conduits
    ky = FY - AW                                            # the kerb (the section's front edge at the street)
    box(A["ground"], AL["x_a"] - 40, ky, -0.7, AL["x_b"] + 40, FY, 0.0, (0.07, 0.07, 0.08), k=0.0)
    box(A["trim"], AL["x_a"] - 40, ky - 0.05, -0.25, AL["x_b"] + 40, ky + 0.05, -0.05, (0.9, 0.85, 0.8), 0.5)
    box(A["ground"], AL["x_a"] - 40, FY - 2.2, 0.0, AL["x_b"] + 40, FY, 0.18, (0.2, 0.2, 0.22), k=1.0)   # sidewalk
    for x in range(int(AL["x_a"]) + 20, int(AL["x_b"]), 55):           # manholes
        tube(A["metal"], (x, ky + 5.0, 0.0), (x, ky + 5.0, 0.03), 1.1, (0.12, 0.12, 0.12), n=14)
    poles = []
    for c in cols + [G.X0 - 22.0, ST["dispatch_x"] + 26.0]:
        px = c + 22.0 if c in cols else c
        if over_room(px, 0, AL["pole_h"], pad=1.0) or any(abs(px - p) < 10 for p in poles):
            continue
        poles.append(px)
    poles.sort()
    ph = AL["pole_h"]
    for px in poles:
        py = ky + 0.9
        tube(A["metal"], (px, py, 0.0), (px, py, ph), 0.35, (0.16, 0.15, 0.14), n=8)
        for zz in (ph - 2.0, ph - 4.5):
            box(A["metal"], px - 2.4, py - 0.15, zz, px + 2.4, py + 0.15, zz + 0.3, (0.16, 0.15, 0.14))
        tube(A["metal"], (px + 0.8, py - 0.6, ph - 9.0), (px + 0.8, py - 0.6, ph - 6.5), 0.75, (0.25, 0.25, 0.27), n=10)
        box(A["small"], px - 0.15, py - 0.45, ph - 7.0, px + 0.15, py - 0.35, ph - 6.7, (0.2, 1.0, 0.4), 6.0)
        # a lamp arm over the alley + its light
        box(A["metal"], px, py, ph - 10.0, px + 0.2, py + 3.0, ph - 9.8, (0.16, 0.15, 0.14))
        box(A["small"], px - 0.4, py + 2.6, ph - 10.3, px + 0.6, py + 3.4, ph - 10.0, (1.0, 0.75, 0.45), 14.0)
        K.add_light("alley_lamp_%d" % int(px), "SPOT", (px, py + 3.0, ph - 10.5), LH["alley_lamp_w"], (1.0, 0.72, 0.42),
                    aim=(px, py + 4.0, 0.0), size=0.6, spot=110, blend=0.9, group="corp", shadow=False)

    def catenary(p, q, sag, r=0.07, col=(0.05, 0.05, 0.06), n=10):
        pts = []
        for i in range(n + 1):
            t = i / n
            pts.append(Vector((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t,
                               p[2] + (q[2] - p[2]) * t - sag * 4 * t * (1 - t))))
        for a_, b_ in zip(pts, pts[1:]):
            tube(A["metal"], a_, b_, r, col, n=4)
    for a_, b_ in zip(poles, poles[1:]):
        for k_, zz in enumerate((ph - 2.0, ph - 2.0, ph - 4.5, ph - 4.5, ph - 4.5)):
            off = (-2.0, 2.0, -1.8, 0.0, 1.8)[k_]
            catenary((a_ + off * 0.2, ky + 0.9 + off * 0.1, zz + 0.3), (b_ + off * 0.2, ky + 0.9 + off * 0.1, zz + 0.3),
                     rd.uniform(1.4, 2.6), r=0.06 + 0.03 * (k_ % 2))
    for px in poles:                                            # drops from the poles to the facade (wall-to-wall)
        for k_ in range(3):
            tx = px + rd.uniform(-9, 9)
            tz = rd.uniform(11.0, 18.0)
            if over_room(tx, tz - 2, tz + 2, pad=0.0):
                continue
            catenary((px, ky + 0.9, ph - 4.5 + 0.3), (tx, FY, tz), rd.uniform(0.8, 1.6), r=0.05)
    # the cut through the street: utility conduits end in the section face (pipe ends), a cable tray under the crust
    for k_ in range(60):
        cx_ = rd.uniform(AL["x_a"] - 30, AL["x_b"] + 30)
        cz_ = rd.uniform(-9.0, -1.4)
        if any(abs(cx_ - r["o"][0]) < RW / 2 + 2 and cz_ < r["o"][2] + r["h"] + 5 for i, r in G.ROOM.items()
               if G.LANE.get(i) == "R"):
            continue
        r_ = rd.uniform(0.25, 0.8)
        c_ = [(0.2, 0.16, 0.12), (0.14, 0.2, 0.16), (0.25, 0.2, 0.1), (0.12, 0.12, 0.14), (0.3, 0.1, 0.08)][k_ % 5]
        tube(A["metal"], (cx_, ky - 0.25, cz_), (cx_, ky + 3.0, cz_), r_, c_, n=10)
    box(A["metal"], AL["x_a"] - 40, ky - 0.1, -0.95, AL["x_b"] + 40, ky + 0.02, -0.7, (0.14, 0.13, 0.12))
    box(A["trim"], AL["x_a"] - 40, ky - 0.12, -0.92, AL["x_b"] + 40, ky - 0.1, -0.86, (1.0, 0.45, 0.2), 0.8)
    # crates / bins along the facade (not in front of street rooms)
    for _ in range(40):
        cx_ = rd.uniform(AL["x_a"], AL["x_b"])
        if over_room(cx_, 0, 3, pad=1.0):
            continue
        s_ = rd.uniform(0.7, 1.4)
        box(A["rough"], cx_, FY - 2.0 - rd.uniform(0, 1.5), 0.18, cx_ + s_, FY - 2.0 - rd.uniform(0, 1.5) + s_, 0.18 + s_,
            (0.12, 0.1, 0.08))
    stall_x = []
    for i in range(len(cols) - 1):
        stall_x.append((cols[i] + cols[i + 1]) / 2 + rd.uniform(-4, 4))
    stall_x += [G.X0 - 34.0, AL["x_a"] + 20.0, ST["dispatch_x"] + 40.0]
    for k_, sx_ in enumerate(stall_x):
        if over_room(sx_, 0, 4.0, pad=4.5):
            continue
        sy_ = ky + rd.uniform(5.0, AW - 6.0)
        w_, d_ = rd.uniform(4.5, 6.0), 2.4
        box(A["rough"], sx_ - w_ / 2, sy_ - d_ / 2, 0.0, sx_ + w_ / 2, sy_ + d_ / 2, 1.9, (0.16, 0.09, 0.06))       # counter
        box(A["sign"], sx_ - w_ / 2 + 0.2, sy_ - d_ / 2 - 0.02, 1.2, sx_ + w_ / 2 - 0.2, sy_ - d_ / 2, 1.8,
            (1.0, 0.6, 0.3), 2.2)                                                                                     # lit front
        for (ex, ey) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            tube(A["metal"], (sx_ + ex * w_ / 2, sy_ + ey * d_ / 2, 1.9), (sx_ + ex * w_ / 2, sy_ + ey * d_ / 2, 3.8), 0.08,
                 (0.15, 0.15, 0.15), n=4)
        box(A["rough"], sx_ - w_ / 2 - 0.4, sy_ - d_ / 2 - 0.6, 3.8, sx_ + w_ / 2 + 0.4, sy_ + d_ / 2, 4.0,
            [(0.5, 0.06, 0.06), (0.1, 0.1, 0.35), (0.45, 0.32, 0.05)][k_ % 3])                                        # canopy
        for q in range(3):                                                                                            # lanterns
            lx_ = sx_ - w_ / 2 + 0.8 + q * (w_ - 1.6) / 2
            box(A["small"], lx_ - 0.35, sy_ - d_ / 2 - 0.75, 2.9, lx_ + 0.35, sy_ - d_ / 2 - 0.15, 3.6, (1.0, 0.25, 0.12), 9.0)
        K.add_light("stall_%d" % k_, "POINT", (sx_, sy_ - d_ / 2 - 1.5, 3.2), LH["stall_w"], (1.0, 0.45, 0.2), size=1.0,
                    group="corp", shadow=False)
    for _ in range(14):                                                                                               # scooters
        cx_ = rd.uniform(AL["x_a"], AL["x_b"])
        if over_room(cx_, 0, 2.0, pad=2.0):
            continue
        cy_ = FY - rd.uniform(2.6, 3.4)
        box(A["metal"], cx_, cy_ - 0.3, 0.4, cx_ + 2.0, cy_ + 0.3, 1.1, [(0.5, 0.1, 0.1), (0.1, 0.3, 0.5), (0.7, 0.7, 0.7)][_ % 3])
        box(A["small"], cx_ + 1.9, cy_ - 0.2, 0.9, cx_ + 2.05, cy_ + 0.2, 1.05, (1.0, 0.9, 0.7), 4.0)
    K.log("alley: slab, poles", len(poles))

    # ---------------------------------------------------------------- v2 r2: the undercroft (the lower street)
    import rc_undercroft
    rc_undercroft.build(K, AL, over_room, tex_quads, facing_quad, blades, boards, hooks)

    # ---------------------------------------------------------------- holograms
    # food + chip holograms over the alley between the lane columns (between the street and roof lanes)
    mids = [(cols[i] + cols[i + 1]) / 2 for i in range(len(cols) - 1)]
    hs0, hs1 = AL["holo_s"]
    hol = [("holo_ramen.png", mids[0] if mids else -150, 10.5, hs1), ("holo_chip.png", mids[1] if len(mids) > 1 else -100,
                                                                       11.0, hs0),
           ("holo_chip.png", mids[2] if len(mids) > 2 else -60, 11.0, hs0)]
    for fn, hx, hz, hs in hol:
        if over_room(hx, hz, hz + hs, pad=0.5):
            continue
        tex_quads(fn, [facing_quad(hx - hs / 2, hx + hs / 2, FY - 6.0, hz, hz + hs)], AL["holo_k"], holo=True, idx=2)
        tube(A["metal"], (hx, FY - 6.0, hz - 1.2), (hx, FY - 6.0, hz - 0.2), 0.25, (0.2, 0.2, 0.22), n=6)
    # anti-human banners on the roofs (DISPATCH takeover) + the red fist hologram (the nearest right hologram)
    banners = sorted(f for f in os.listdir(tex_dir) if f.startswith("banner_"))
    roof_spots = sorted([(x0, x1, h) for (x0, x1, h) in infill if x1 - x0 > 7.5], key=lambda t: -t[2])[:4]
    for k_, (x0, x1, h) in enumerate(roof_spots):
        if k_ >= len(banners):
            break
        bw = 16.0
        bx = (x0 + x1) / 2 - bw / 2
        tex_quads(banners[k_], [facing_quad(bx, bx + bw, FY + 3.0, h + 2.0, h + 2.0 + bw / 4)], AL["holo_k"] * 0.9,
                  holo=True, idx=2)
        for s_ in (bx + 1.5, bx + bw - 1.5):
            tube(A["metal"], (s_, FY + 3.2, h), (s_, FY + 3.2, h + 2.2), 0.15, (0.15, 0.15, 0.16), n=4)
    fx = ST["dispatch_x"] + 24.0
    fs = AL["fist_s"]                                       # secondary to the MAINFRAME hero (art director)
    fz = 42.0
    tex_quads("holo_fist.png", [facing_quad(fx - fs / 2, fx + fs / 2, FY - 7.0, fz, fz + fs)], AL["holo_k"] * 0.8,
              holo=True, idx=2)
    tube(A["metal"], (fx, FY - 7.0, 0.0), (fx, FY - 7.0, fz - 1.0), 0.4, (0.15, 0.1, 0.1), n=8)
    box(A["small"], fx - 1.2, FY - 8.2, fz - 1.6, fx + 1.2, FY - 5.8, fz - 1.0, (1.0, 0.1, 0.1), 10.0)
    K.add_light("fist_spill", "AREA", (fx, FY - 9.0, fz + fs / 2), LH["fist_spill_w"], (1.0, 0.06, 0.06), aim=(fx, FY + 10.0, 10.0),
                size=fs, size_y=fs, group="corp", shadow=False)
    for fn, hx, hz, hs in hol:
        K.add_light("holo_spill_%d" % int(hx), "AREA", (hx, FY - 7.0, hz + hs / 2), LH["holo_spill_w"],
                    (0.4, 0.9, 1.0) if "ramen" in fn else (1.0, 0.3, 0.8), aim=(hx, FY + 5.0, 0.0), size=hs, size_y=hs,
                    group="corp", shadow=False)
    K.log("alley: holograms")
    _rooms(K, G, A, box, tube, tex_quads, facing_quad, boards, blades, rd, LH, pal)
    hooks.update(_street_strips(K, CP, LH, pal, section=True))

    hooks.setdefault("tex_objs", []).extend(objs)
    return objs


def _rooms(K, G, A, box, tube, tex_quads, facing_quad, boards, blades, rd, LH, pal):
    """Every room a PLACE in the mainline Tokyo-alley look (art director: no pale grey blanks):
      street rooms   a half-rolled shutter with a tag, a lit back-wall shop board, paper lanterns at the jambs, a counter
      roof rooms     a corrugated rooftop shack: warm bulb string, a water tank, a lit blade on the back wall
      tunnel rooms   the service tunnel's rooms: pipe runs on the back wall, cage lamps, cable reels, a green status board
      kill switches  a red-lit breaker cabinet (kept)"""
    for i, r in sorted(G.ROOM.items()):
        if i in ("start", "srv"):
            continue
        x, y, z = r["o"]
        w, h, d = r["w"], r["h"], r["d"]
        lane = G.LANE.get(i)
        kind = G.KIND[i]
        if kind == "switch":
            continue
        yb = y + d - 0.2                                    # just in front of the back wall
        if lane == "C":
            fn = boards[rd.randrange(len(boards))]
            tex_quads(fn, [facing_quad(x - w / 2 + 1.6, x + w / 2 - 1.6, yb, z + 3.6, z + 3.6 + (w - 3.2) / 4)], 2.2)
            box(A["metal"], x - w / 2 + 0.2, y + 0.15, z + h - 2.0, x + w / 2 - 0.2, y + 0.45, z + h, (0.2, 0.19, 0.18))
            for q in range(5):                              # shutter slats
                box(A["metal"], x - w / 2 + 0.2, y + 0.1, z + h - 2.0 + q * 0.4, x + w / 2 - 0.2, y + 0.15,
                    z + h - 1.85 + q * 0.4, (0.27, 0.26, 0.25))
            box(A["sign"], x - 3.0, y + 0.08, z + h - 1.6, x + 1.5, y + 0.1, z + h - 0.6,
                [(1.0, 0.2, 0.6), (0.2, 0.9, 1.0), (1.0, 0.8, 0.2)][rd.randrange(3)], 1.6)      # the tag (spray, glows)
            for sx in (-1, 1):                              # paper lanterns at the jambs
                lx = x + sx * (w / 2 + 0.6)
                box(A["small"], lx - 0.45, y - 0.9, z + 4.6, lx + 0.45, y - 0.1, z + 5.8, (1.0, 0.22, 0.1), 7.0)
            box(A["rough"], x - w / 2 + 2.0, y + 3.0, z, x + w / 2 - 2.0, y + 4.4, z + 1.4, (0.22, 0.12, 0.07))   # counter
            K.add_light("room_warm_%s" % i, "POINT", (x, y + 5.0, z + h - 1.5), LH["room_warm_w"], (1.0, 0.55, 0.3),
                        size=1.5, group="corp", shadow=False)
        elif lane == "L":
            for sx in (-1, 1):                              # corrugated shack walls (dark tin) on the sides
                box(A["rough"], x + sx * (w / 2 + 0.3) - 0.2, y + 0.4, z, x + sx * (w / 2 + 0.3) + 0.2, y + d, z + h,
                    (0.16, 0.12, 0.1))
            for q in range(7):                              # a bulb string across the opening
                box(A["small"], x - w / 2 + 1.0 + q * (w - 2.0) / 6 - 0.2, y + 0.6, z + h - 0.9 - 0.25 * ((q % 2)),
                    x - w / 2 + 1.0 + q * (w - 2.0) / 6 + 0.2, y + 1.0, z + h - 0.5 - 0.25 * ((q % 2)), (1.0, 0.75, 0.4), 8.0)
            fn = blades[rd.randrange(len(blades))]
            tex_quads(fn, [facing_quad(x + w / 2 - 3.6, x + w / 2 - 1.4, yb, z + 0.8, z + 0.8 + 8.8 * 0.75)], 2.0)
            tube(A["metal"], (x - w / 2 + 2.5, y + d - 2.5, z), (x - w / 2 + 2.5, y + d - 2.5, z + 3.2), 1.4,
                 (0.12, 0.1, 0.09), n=10)
            K.add_light("room_warm_%s" % i, "POINT", (x, y + 4.0, z + h - 1.2), LH["room_warm_w"] * 0.8, (1.0, 0.65, 0.35),
                        size=1.5, group="corp", shadow=False)
        elif lane == "R":
            for q in range(4):                              # pipe runs along the back wall
                tube(A["metal"], (x - w / 2 + 0.3, yb - 0.4 - q * 0.1, z + 1.2 + q * 1.4),
                     (x + w / 2 - 0.3, yb - 0.4 - q * 0.1, z + 1.2 + q * 1.4), 0.35 - 0.05 * q,
                     [(0.3, 0.12, 0.08), (0.12, 0.25, 0.18), (0.25, 0.22, 0.1), (0.15, 0.15, 0.17)][q], n=8)
            for sx in (-1, 1):                              # cage lamps
                box(A["small"], x + sx * (w / 2 - 1.6) - 0.35, y + 1.0, z + h - 1.4, x + sx * (w / 2 - 1.6) + 0.35,
                    y + 1.7, z + h - 0.7, (0.6, 1.0, 0.75), 9.0)
            box(A["sign"], x - 2.4, yb - 0.05, z + 5.6, x + 2.4, yb, z + 7.0, (0.3, 1.0, 0.55), 1.8)    # status board
            tube(A["metal"], (x + 3.5, y + 4.0, z + 1.1), (x + 3.5, y + 5.2, z + 1.1), 1.1, (0.3, 0.2, 0.1), n=12)
            K.add_light("room_warm_%s" % i, "POINT", (x, y + 4.0, z + h - 1.0), LH["room_warm_w"] * 0.7, (0.6, 1.0, 0.8),
                        size=1.5, group="corp", shadow=False)


def _street_strips(K, CP, LH, pal, section=True):
    """The district grid's streets lit by sodium strip lights (low, pointing down, in 90 BU segments so every renderer
    keeps them): light, not exposure. Inside the blackout ring the arterials follow the sequence (art director: they
    must not split the fist): sodium before, DARK at the blackout, Cell RED as the red spreads / at full. In the section
    build only the streets behind the frontage are lit (no light falls in front of the cut). Also a low red glow under
    the fist, light-linked to the fog only, that rises with the sequence (the red bleeds into the air).
    Returns hooks: fist_strips [(light, e0)], fist_glow [(light, e0)]."""
    FI = CP["fist"]
    cell = FI["cell"]
    x0, x1 = FI["x"][0] - 90.0, FI["x"][1] + 90.0
    y0, y1 = FI["y"][0] - 90.0, FI["y"][1] + 90.0
    fcx, fcy = (FI["x"][0] + FI["x"][1]) / 2, (FI["y"][0] + FI["y"][1]) / 2
    ring = FI["ring"][1]
    cut = CP["stack"]["cut"]
    seg = LH.get("strip_seg", 90.0)
    cols = (pal("sodium"), (1.0, 0.62, 0.35))
    n = 0
    fist = []
    for axis in ("x", "y"):
        lo, hi = (x0, x1) if axis == "x" else (y0, y1)
        a0, a1 = (y0, y1) if axis == "x" else (x0, x1)
        v = lo
        k = 0
        while v <= hi:
            if k % LH["strip_every"] == 0:
                u = a0
                while u < a1:
                    u1 = min(u + seg, a1)
                    c = ((u + u1) / 2)
                    loc = (v, c, 5.0) if axis == "x" else (c, v, 5.0)
                    if section and loc[1] < cut + 10.0:
                        u = u1
                        continue
                    inside = ((loc[0] - fcx) ** 2 + (loc[1] - fcy) ** 2) ** 0.5 < ring
                    e0 = LH["strip_w"] * (u1 - u) / seg
                    ob = K.add_light("strip_%s_%d" % (axis, n), "AREA", loc, e0,
                                     cols[0 if axis == "x" else 1], aim=(loc[0], loc[1], 0.0),
                                     size=2.0 if axis == "x" else (u1 - u), size_y=(u1 - u) if axis == "x" else 2.0,
                                     group="fist_strip" if inside else "city", shadow=False)
                    if inside:
                        fist.append((ob, e0))
                    n += 1
                    u = u1
            v += cell
            k += 1
    glow = []
    if not section:
        for k_ in range(6):
            gx = fcx + (k_ % 3 - 1) * 110.0
            gy = fcy + (k_ // 3 - 0.5) * 150.0
            ob = K.add_light("fist_glow_%d" % k_, "AREA", (gx, gy, 3.0), LH["fist_glow_w"], pal("cell_red"),
                             aim=(gx, gy, 60.0), size=110.0, size_y=150.0, group="fist_glow", shadow=False,
                             receivers=K.COLL["media"])
            glow.append((ob, LH["fist_glow_w"]))
    K.log("street strips", n, "inside the ring", len(fist))
    return {"fist_strips": fist, "fist_glow": glow}


def seq_lights(hooks, seq, pal):
    """The arterials inside the ring + the red glow by the sequence value (0 before .. 1 blackout .. 3 full)."""
    import math
    blk = max(0.0, min(1.0, (seq - 0.55) / 0.45))           # 0 -> 1 over the blackout
    red = max(0.0, min(1.0, (seq - 1.0) / 1.0))             # 0 -> 1 as the red spreads
    sod, rc = pal("sodium"), pal("cell_red")
    for ob, e0 in hooks.get("fist_strips", []):
        if seq < 1.0:
            k, c = 1.0 - blk, sod
        else:
            k, c = 0.55 * red, rc
        ob.data.energy = e0 * k
        ob.data.color = c[:3]
    for ob, e0 in hooks.get("fist_glow", []):
        ob.data.energy = e0 * (0.15 + 0.85 * max(0.0, min(1.0, (seq - 1.2) / 1.6))) if seq >= 1.0 else e0 * 0.05
    return math.isfinite(seq)
# RC_R2B
# RC_FLOORLIGHT
