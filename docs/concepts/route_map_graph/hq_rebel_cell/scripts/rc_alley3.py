"""Rebel Cell v3: the canyon after the designer's review of round 1 (2026-10-16). Blender side, through the kit's K
helpers; replaces rc_alley.build for the section (the red-sequence district build still uses rc_alley).
Seeds: 8440 (lots), 8441 (facades), 8442 (signs), 8443 (roofs), 8444 (district roofs).

  frontage   ONE continuous row: every lot touches its neighbours (no gaps, no back-alley slot); along the rooftop lane
             the lots' roofs are explicit (preset v3.lots) so the lane walks on them; procedural lots beyond
  roofs      NYC: parapets with copings, cornices, water towers on steel legs, satellite dishes, roof access bulkheads
             (door + lamp), AC units, antennas, vents, fire-escape tops (goosenecks over the parapet); on the frontage and
             on the district blocks behind
  rooftop    the top lane walks the roofs (duckboards), drops a level by LADDERS, climbs by STAIRS, and crosses between
  lane       roof heights on CATWALKS (posts down to the roof below); THE DROP's climb is a fire escape
  signage    the Tokyo canyon kept, the styles varied: blades, light BOXES (cubes on brackets), WRAPS round bays, cloth
             BANNERS and nobori flags, LED TICKERS, PAPER LANTERNS (rows and strings), boards; HOLOGRAMS at street level and
             on the roofs; rooftop BILLBOARDS on scaffolds and rooftop neon letters
  MAINFRAME  the locked v4 red sign on DISPATCH's building, centred over the CENTRAL SERVER room (the target)
  red        an accent only: the fist's windows (red_mix), a few takeover signs, one red billboard, the fist hologram
Never covers a room: over_room() for every sign, hologram and fitting in front of a room opening.
"""
import math
import os
import random

import rc_alley as R2
import rc_sewer


def lots_of(K):
    """The frontage lots (x0, x1, roof) from x_a to x_b: procedural west, explicit along the rooftop lane, procedural
    east. Every lot touches the next."""
    V3 = K.HZ["v3"]
    AL = dict(R2.AL, x_a=V3["front_x"][0], x_b=V3["front_x"][1])
    rr = random.Random(8440)
    ex = sorted(tuple(l_) for l_ in V3["lots"])

    def fill(a, b):
        out, x = [], a
        while x < b - 0.01:
            w = rr.uniform(*V3["lot_w"])
            if b - (x + w) < V3["lot_w"][0] * 0.7:
                w = b - x
            out.append((x, x + w, round(rr.uniform(*V3["lot_h"]), 1)))
            x += w
        return out
    return fill(AL["x_a"], ex[0][0]) + ex + fill(ex[-1][1], AL["x_b"])


def build(K, DIST, cat, hooks, tex_dir):
    import bpy
    G, CP, pal, LH, HZ = K.G, K.CP, K.pal, K.LH, K.HZ
    V3 = HZ["v3"]
    AL = dict(R2.AL, x_a=V3["front_x"][0], x_b=V3["front_x"][1])     # v3: the frontage runs past the frame
    AL["sign_k"] = V3.get("sign_k", AL["sign_k"])
    A, box, tube = K.A, K.box, K.tube
    Vector = K.Vector
    ST = CP["stack"]
    CUT = ST["cut"]
    RW, RH, RD = CP["room_w"], CP["room_h"], CP["room_d"]
    FY = CUT + 0.6
    Y1 = V3["front_y1"]
    AW = ST["alley_w"]
    ky = FY - AW
    rd = random.Random(8441)
    rs = random.Random(8442)
    rq = random.Random(8443)
    objs = []
    cols = sorted({round(r["o"][0], 1) for i, r in G.ROOM.items() if i not in ("start", "srv")})
    MX = ST["dispatch_x"]
    MW = V3["mf_w"]
    MZ0 = V3["mf_z0"]
    MZ1 = MZ0 + MW * 999 / 246
    YR = CUT + V3["roof_y"]

    # ---------------------------------------------------------------- textured quads (signs, holograms, cloth)
    MATS = {}

    def tex_mat(name, img_path, k, mode):
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
        mk = nt.nodes.new("ShaderNodeMath")
        mk.operation = "MULTIPLY"
        mk.inputs[1].default_value = k
        nt.links.new(pw.outputs["Fac"], mk.inputs[0])
        if mode == "cloth":
            # lit fabric: a diffuse cloth that also glows a little (backlit by the shop behind it)
            b = nt.nodes.new("ShaderNodeBsdfPrincipled")
            nt.links.new(ti.outputs["Color"], b.inputs["Base Color"])
            b.inputs["Roughness"].default_value = 0.85
            nt.links.new(ti.outputs["Color"], b.inputs["Emission Color"])
            nt.links.new(mk.outputs[0], b.inputs["Emission Strength"])
            nt.links.new(b.outputs[0], out.inputs[0])
            return m
        em = nt.nodes.new("ShaderNodeEmission")
        nt.links.new(ti.outputs["Color"], em.inputs["Color"])
        nt.links.new(mk.outputs[0], em.inputs["Strength"])
        if mode == "holo":
            sep = nt.nodes.new("ShaderNodeSeparateColor")
            nt.links.new(ti.outputs["Color"], sep.inputs[0])
            mx_ = K.mth(nt, "MAXIMUM", K.mth(nt, "MAXIMUM", sep.outputs[0], sep.outputs[1]), sep.outputs[2])
            al = nt.nodes.new("ShaderNodeMath")
            al.operation = "MULTIPLY"
            al.inputs[1].default_value = 0.9
            al.use_clamp = True
            nt.links.new(mx_, al.inputs[0])
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

    def tex_quads(fname, quads, k, holo=False, idx=1, mode=None, uvs=None):
        mode = mode or ("holo" if holo else "sign")
        key = (fname, mode, round(k, 2))
        if key not in MATS:
            MATS[key] = tex_mat("tex_%s_%d" % (os.path.splitext(fname)[0], len(MATS)), os.path.join(tex_dir, fname), k,
                                mode)
        me = bpy.data.meshes.new("tq_" + fname)
        vs, fs = [], []
        for q in quads:
            b = len(vs)
            vs.extend(q)
            fs.append((b, b + 1, b + 2, b + 3))
        me.from_pydata(vs, [], fs)
        uv = me.uv_layers.new(name="UVMap")
        for pi, poly in enumerate(me.polygons):
            u4 = (uvs[pi] if uvs else ((0, 0), (1, 0), (1, 1), (0, 1)))
            for li, (u, v) in zip(poly.loop_indices, u4):
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
        a = math.radians(ang)
        w = x1 - x0
        xr, yr = x0 + w * math.cos(a), y - w * math.sin(a)
        return [(x0, y, z0), (xr, yr, z0), (xr, yr, z1), (x0, y, z1)]

    def over_room(x, z0, z1, pad=1.5):
        for i, r in G.ROOM.items():
            ox, _, oz = r["o"]
            if abs(x - ox) < r["w"] / 2 + pad and z1 > oz - 1.0 and z0 < oz + r["h"] + 1.5:
                return True
        if abs(x - MX) < MW / 2 + pad and z1 > MZ0 - 1.0 and z0 < MZ1 + 1.0:      # the MAINFRAME sign
            return True
        return False

    K.log("alley v3: textures from", tex_dir)
    lots = lots_of(K)
    LOTS = lots

    def roof_at(x):
        hs = [h for (a, b, h) in LOTS if a - 0.01 <= x <= b + 0.01]
        return max(hs) if hs else 0.0
    L_REGION = (-190.0, -26.0)

    # ---------------------------------------------------------------- the frontage: one continuous row
    croom = {r["o"][0]: r for i, r in G.ROOM.items() if G.LANE.get(i) == "C"}
    srv = G.ROOM["srv"]
    WALLS = [(0.075, 0.07, 0.08), (0.09, 0.075, 0.07), (0.08, 0.08, 0.085), (0.07, 0.065, 0.06), (0.085, 0.07, 0.075)]
    lotinfo = []
    for li, (x0, x1, h) in enumerate(lots):
        c = float(cat((x0 + x1) / 2, FY + 6.0))
        colr = WALLS[rd.randrange(len(WALLS))]
        cr = next((r for xx, r in croom.items() if x0 < xx < x1), None)
        kind = "plain"
        if cr is not None:
            kind = "street_room"
            rx = cr["o"][0]
            a_, b_ = rx - RW / 2 - 0.4, rx + RW / 2 + 0.4
            if a_ > x0:
                box(DIST, x0, FY, 0.0, a_, Y1, 9.6, colr, k=c)
            if b_ < x1:
                box(DIST, b_, FY, 0.0, x1, Y1, 9.6, colr, k=c)
            box(DIST, a_, CUT + RD + 0.5, 0.0, b_, Y1, 9.6, colr, k=c)
            box(DIST, x0, FY, 9.6, x1, Y1, h, colr, k=c)
        elif x0 < srv["o"][0] < x1:
            kind = "dispatch"
            sx, sz, sw, sh, sd = srv["o"][0], srv["o"][2], srv["w"], srv["h"], srv["d"]
            a_, b_ = sx - sw / 2 - 0.4, sx + sw / 2 + 0.4
            box(DIST, x0, FY, 0.0, x1, Y1, sz - 0.4, colr, k=c)
            if a_ > x0:
                box(DIST, x0, FY, sz - 0.4, a_, Y1, sz + sh + 2.0, colr, k=c)
            if b_ < x1:
                box(DIST, b_, FY, sz - 0.4, x1, Y1, sz + sh + 2.0, colr, k=c)
            box(DIST, a_, CUT + sd + 0.5, sz - 0.4, b_, Y1, sz + sh + 2.0, colr, k=c)
            box(DIST, x0, FY, sz + sh + 2.0, x1, Y1, h, colr, k=c)
        else:
            box(DIST, x0, FY, 0.0, x1, Y1, h, colr, k=c)
        lotinfo.append(dict(x0=x0, x1=x1, h=h, kind=kind, lane=L_REGION[0] <= x0 and x1 <= L_REGION[1] + 0.01))
    K.log("alley v3: lots", len(lots))

    # parapets, copings, cornices (NYC)
    COP = (0.21, 0.2, 0.19)
    for li, L_ in enumerate(lotinfo):
        x0, x1, h = L_["x0"], L_["x1"], L_["h"]
        par = 0.7 if L_["lane"] else 1.2
        box(A["rough"], x0, FY, h, x1, FY + 0.45, h + par, (0.11, 0.1, 0.1))
        box(A["rough"], x0 - 0.02, FY - 0.12, h + par, x1 + 0.02, FY + 0.6, h + par + 0.16, COP)
        box(A["rough"], x0, Y1 - 0.45, h, x1, Y1, h + par, (0.11, 0.1, 0.1))
        for side, nb in ((0, li - 1), (1, li + 1)):
            if 0 <= nb < len(lotinfo) and lotinfo[nb]["h"] < h - 0.5:
                xs = x0 if side == 0 else x1 - 0.45
                box(A["rough"], xs, FY, h, xs + 0.45, Y1, h + par, (0.11, 0.1, 0.1))
        if not L_["lane"] and rd.random() < 0.6 and h > 20:                    # a cornice band (older buildings)
            box(A["rough"], x0, FY - 0.7, h - 1.6, x1, FY, h - 0.9, COP)
            box(A["rough"], x0, FY - 0.4, h - 2.2, x1, FY, h - 1.6, (0.15, 0.14, 0.13))
        if rd.random() < 0.5:                                                    # a floor-line string course
            zz = rd.choice((9.6, 13.5, 17.4))
            if zz < h - 3 and not over_room((x0 + x1) / 2, zz, zz + 0.3, pad=-RW / 2 + 0.1):
                box(A["rough"], x0, FY - 0.3, zz, x1, FY, zz + 0.3, (0.13, 0.12, 0.11))

    # ---------------------------------------------------------------- NYC rooftop kit
    def cone(acc, cx, cy, z, r, hh, col, n=12):
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            acc.face([(cx + r * math.cos(a0), cy + r * math.sin(a0), z), (cx + r * math.cos(a1), cy + r * math.sin(a1), z),
                      (cx, cy, z + hh)], col)

    S = V3.get("prop_s", 1.0)                            # t4: roof props scaled up for legibility at OVERVIEW

    def water_tower(cx, cy, z, r=None, k=1.0):
        r = (r or rq.uniform(1.6, 2.5)) * S * k
        legs = rq.uniform(3.0, 5.0) * S * k
        th = rq.uniform(3.8, 5.2) * S * k
        for (ex, ey) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            tube(A["metal"], (cx + ex * r * 0.7, cy + ey * r * 0.7, z), (cx + ex * r * 0.62, cy + ey * r * 0.62, z + legs), 0.12 * S,
                 (0.1, 0.1, 0.1), n=5)
        tube(A["metal"], (cx - r * 0.7, cy - r * 0.7, z + legs * 0.5), (cx + r * 0.7, cy + r * 0.7, z + legs * 0.5), 0.05,
             (0.1, 0.1, 0.1), n=4)
        tube(A["metal"], (cx + r * 0.7, cy - r * 0.7, z + legs * 0.5), (cx - r * 0.7, cy + r * 0.7, z + legs * 0.5), 0.05,
             (0.1, 0.1, 0.1), n=4)
        box(A["rough"], cx - r - 0.3, cy - r - 0.3, z + legs - 0.25, cx + r + 0.3, cy + r + 0.3, z + legs, (0.1, 0.09, 0.08))
        wood = rq.choice(((0.20, 0.12, 0.07), (0.16, 0.10, 0.06), (0.23, 0.15, 0.09)))
        tube(A["rough"], (cx, cy, z + legs), (cx, cy, z + legs + th), r, wood, n=14)
        for q in range(3):
            zz = z + legs + 0.6 + q * (th - 1.0) / 2
            tube(A["metal"], (cx, cy, zz), (cx, cy, zz + 0.12), r + 0.06, (0.06, 0.06, 0.06), n=14)
        cone(A["rough"], cx, cy, z + legs + th, r + 0.25, r * 0.65, (0.12, 0.1, 0.09), n=14)
        tube(A["metal"], (cx - r - 0.05, cy - 0.4, z), (cx - r - 0.05, cy - 0.4, z + legs + th), 0.05, (0.2, 0.2, 0.2), n=4)

    def bulkhead(cx, cy, z, lamp=True, k=1.0):
        w, d, hh = rq.uniform(2.8, 3.6) * S * k, rq.uniform(2.6, 3.4) * S * k, rq.uniform(2.8, 3.4) * S * k
        box(A["rough"], cx - w / 2, cy - d / 2, z, cx + w / 2, cy + d / 2, z + hh, (0.11, 0.09, 0.08))
        box(A["rough"], cx - w / 2 - 0.15, cy - d / 2 - 0.15, z + hh, cx + w / 2 + 0.15, cy + d / 2 + 0.15, z + hh + 0.2, COP)
        box(A["metal"], cx - 0.6 * S, cy - d / 2 - 0.05, z, cx + 0.6 * S, cy - d / 2, z + 2.2 * S, (0.06, 0.06, 0.07))
        if lamp:
            box(A["small"], cx - 0.25 * S, cy - d / 2 - 0.3, z + 2.3 * S + 0.15, cx + 0.25 * S, cy - d / 2 - 0.05,
                z + 2.3 * S + 0.45, (1.0, 0.78, 0.5), 7.0)

    def ac_unit(cx, cy, z):
        w, d = rq.uniform(1.8, 2.6) * S, rq.uniform(1.2, 1.7) * S
        box(A["metal"], cx - w / 2, cy - d / 2, z, cx + w / 2, cy + d / 2, z + 1.2 * S, (0.34, 0.35, 0.36))
        tube(A["metal"], (cx, cy, z + 1.2 * S), (cx, cy, z + 1.2 * S + 0.06), min(w, d) * 0.38, (0.05, 0.05, 0.05), n=10)

    def dish(cx, cy, z, r=None):
        r = (r or rq.uniform(0.7, 1.4)) * S
        tube(A["metal"], (cx, cy, z), (cx, cy, z + 1.4), 0.08 * S, (0.2, 0.2, 0.2), n=4)
        n_ = Vector((rq.uniform(-0.35, 0.35), -0.65, 0.7)).normalized()
        u = n_.cross(Vector((0, 0, 1))).normalized()
        v = n_.cross(u).normalized()
        c = Vector((cx, cy, z + 1.4 + r * 0.4))
        apex = c - n_ * (r * 0.32)
        rim = [c + (u * math.cos(2 * math.pi * i / 14) + v * math.sin(2 * math.pi * i / 14)) * r for i in range(14)]
        for i in range(14):
            A["rough"].face([rim[i], rim[(i + 1) % 14], apex], (0.5, 0.5, 0.52))
        tube(A["metal"], apex, c + n_ * (r * 0.75), 0.04, (0.2, 0.2, 0.2), n=4)

    def antenna(cx, cy, z):
        hh = rq.uniform(5.0, 11.0) * S
        tube(A["metal"], (cx, cy, z), (cx, cy, z + hh), 0.07 * S, (0.15, 0.15, 0.15), n=4)
        for q in range(rq.randint(2, 4)):
            zz = z + hh * (0.45 + 0.15 * q)
            ww = rq.uniform(0.8, 1.8) * (1.0 - 0.15 * q)
            tube(A["metal"], (cx - ww, cy, zz), (cx + ww, cy, zz), 0.035, (0.15, 0.15, 0.15), n=4)
        box(A["small"], cx - 0.12, cy - 0.12, z + hh, cx + 0.12, cy + 0.12, z + hh + 0.25, (1.0, 0.12, 0.08), 6.0)

    def vent(cx, cy, z):
        tube(A["metal"], (cx, cy, z), (cx, cy, z + rq.uniform(0.8, 1.6)), rq.uniform(0.18, 0.35), (0.22, 0.22, 0.23), n=8)

    def roof_kit(x0, y0, x1, y1, z, dense=1.0, lamps=None):
        """NYC roof clutter inside a footprint (x0..x1, y0..y1) at roof height z."""
        w, d = x1 - x0, y1 - y0
        if w < 3 or d < 3:
            return
        items = []
        if rq.random() < 0.42 * dense and w > 5 and d > 5:
            items.append("tower")
        if rq.random() < 0.65 * dense:
            items.append("bulk")
        items += ["ac"] * rq.randint(0, int(2 * dense) + 1)
        if rq.random() < 0.3 * dense:
            items.append("dish")
        if rq.random() < 0.35 * dense:
            items.append("ant")
        items += ["vent"] * rq.randint(0, 2)
        taken = []
        for it in items:
            for _ in range(6):
                rad = S * {"tower": 2.8, "bulk": 2.0, "ac": 1.4, "dish": 1.2, "ant": 0.6, "vent": 0.5}[it]
                if w < 2 * rad + 0.6 or d < 2 * rad + 0.6:
                    break
                cx = rq.uniform(x0 + rad + 0.3, x1 - rad - 0.3)
                cy = rq.uniform(y0 + rad + 0.3, y1 - rad - 0.3)
                if any(math.hypot(cx - a, cy - b) < rad + r_ + 0.3 for (a, b, r_) in taken):
                    continue
                taken.append((cx, cy, rad))
                if it == "tower":
                    water_tower(cx, cy, z)
                elif it == "bulk":
                    bulkhead(cx, cy, z)
                    if lamps is not None:
                        lamps.append((cx, cy - 2.0, z + 2.6))
                elif it == "ac":
                    ac_unit(cx, cy, z)
                elif it == "dish":
                    dish(cx, cy, z)
                elif it == "ant":
                    antenna(cx, cy, z)
                else:
                    vent(cx, cy, z)
                break

    roof_lamps = []
    for L_ in lotinfo:
        x0, x1, h = L_["x0"], L_["x1"], L_["h"]
        if L_["kind"] == "dispatch":
            continue                                    # its roof carries the MAINFRAME frame
        if L_["lane"]:
            # behind the lane's rooms and walk line only (the lane stays clear)
            roof_kit(x0 + 0.5, CUT + RD + 1.5, x1 - 0.5, Y1 - 0.6, h, dense=0.5, lamps=roof_lamps)
        else:
            roof_kit(x0 + 0.5, FY + 1.2, x1 - 0.5, Y1 - 0.6, h, dense=1.1, lamps=roof_lamps)
    # t4: the roof PLANES read as surfaces (a lighter tar-and-gravel membrane on every frontage roof, lit by the work
    # lights), and each top-lane node stands ON its roof next to a roof-access bulkhead, a water tower behind it and a
    # dish / AC on the shack: silhouettes against the city glow
    for L_ in lotinfo:
        x0, x1, h = L_["x0"], L_["x1"], L_["h"]
        box(A["rough"], x0 + 0.45, FY + 0.45, h, x1 - 0.45, Y1 - 0.45, h + 0.06,
            (0.17, 0.16, 0.15) if L_["lane"] else (0.13, 0.125, 0.12))
    for i, r in sorted(G.ROOM.items()):
        if G.LANE.get(i) != "L" or i in ("L2a", "L2b"):
            continue
        x, y, z = r["o"]
        side = 1.0 if i != "LK" else -1.0
        bx = x + side * (r["w"] / 2 + 3.4)
        nk = V3.get("node_prop_k", 1.0)                    # finals (AD): the node props another 1.3x
        bulkhead(bx, CUT + 7.4 + 0.6 * (nk - 1.0) * 3.0, z, k=nk)   # behind the walk line (y = cut + roof_y)
        roof_lamps.append((bx, CUT + 4.5, z + 3.8))
        water_tower(x + side * 2.0, CUT + RD + 6.5, z, r=2.3, k=nk)
        # a rim light from the city-glow side behind it: the tower's silhouette pops against the skyline
        tz = z + 2.3 * S * nk * 3.2
        K.add_light("tower_rim_%s" % i, "AREA", (x + side * 2.0 - side * 6.0, CUT + RD + 20.0, tz + 4.0),
                    V3.get("tower_rim_w", 900.0), (1.0, 0.45, 0.75) if side > 0 else (0.45, 0.8, 1.0),
                    aim=(x + side * 2.0, CUT + RD + 6.5, tz), size=4.0, size_y=6.0, group="corp", shadow=False)
        dish(x - side * 3.5, y + 5.0, z + RH + 0.6)
        ac_unit(x + side * 2.5, y + 6.5, z + RH + 0.6)
    rb_ = random.Random(8444)
    nblk = 0
    for (bx0, by0, bx1, by1, bh) in HZ.get("_blocks", []):
        if by0 > CUT + V3["roof_clutter_d"] or by0 < CUT:
            continue
        box(A["rough"], bx0, by0, bh, bx1, by0 + 0.4, bh + 1.0, (0.11, 0.1, 0.1))           # front parapet
        box(A["rough"], bx0 - 0.02, by0 - 0.1, bh + 1.0, bx1 + 0.02, by0 + 0.5, bh + 1.12, COP)
        roof_kit(bx0 + 0.4, by0 + 0.8, bx1 - 0.4, by1 - 0.4, bh, dense=0.8 + 0.4 * rb_.random())
        nblk += 1
    for k_, (lx, ly, lz) in enumerate(roof_lamps):
        K.add_light("roof_lamp_%d" % k_, "POINT", (lx, ly, lz), LH["roof_w"] * 0.3, (1.0, 0.75, 0.5), size=0.6,
                    group="corp", shadow=False)
    K.log("alley v3: roofs, district blocks dressed", nblk, "bulkhead lamps", len(roof_lamps))

    # ---------------------------------------------------------------- the rooftop lane: duckboards, ladders, stairs, catwalks
    GRATE, RAIL, PLANK = (0.2, 0.2, 0.21), (0.32, 0.3, 0.27), (0.15, 0.12, 0.09)

    def ladder(x, y, za, zb):
        za, zb = min(za, zb), max(za, zb)
        for s_ in (-0.45, 0.45):
            tube(A["metal"], (x + s_, y, za), (x + s_, y, zb + 1.1), 0.13, RAIL, n=5)
        z = za + 0.35
        while z < zb:
            tube(A["metal"], (x - 0.45, y, z), (x + 0.45, y, z), 0.08, RAIL, n=4)
            z += 0.45
        box(A["small"], x - 0.25, y - 0.3, zb + 1.2, x + 0.25, y + 0.2, zb + 1.5, (1.0, 0.72, 0.38), 8.0)   # a cage lamp
        box(A["small"], x - 0.6, y - 0.12, za + 0.05, x - 0.5, y - 0.02, zb + 1.0, (1.0, 0.6, 0.25), 1.6)   # hazard strip
        for s_ in (-0.45, 0.45):                                        # a gooseneck over the top
            tube(A["metal"], (x + s_, y, zb + 1.1), (x + s_, y + 0.6, zb + 1.3), 0.06, RAIL, n=4)

    def posts(p, q, step=3.0):
        L = (q - p).length
        n = max(1, int(L / step))
        for i in range(n + 1):
            c = p + (q - p) * (i / n)
            rz = roof_at(c.x)
            if c.z - 0.25 - rz > 0.6:
                tube(A["metal"], (c.x, c.y + 0.6, rz), (c.x, c.y + 0.6, c.z - 0.25), 0.17, (0.14, 0.14, 0.14), n=5)
                tube(A["metal"], (c.x, c.y - 0.6, rz), (c.x, c.y - 0.6, c.z - 0.25), 0.17, (0.14, 0.14, 0.14), n=5)
                tube(A["metal"], (c.x, c.y - 0.6, rz + 0.3), (c.x, c.y + 0.6, c.z - 0.6), 0.07, (0.14, 0.14, 0.14), n=4)

    def box_seg_light(p, q):
        # a thin amber edge strip along a catwalk / stair deck: the lane's structure reads as lines at OVERVIEW
        K.seg_box(A["small"], p + Vector((0, 0, 0.06)), q + Vector((0, 0, 0.06)), 0.1, 0.06, (1.0, 0.62, 0.28), k=2.2)

    def rails(p, q):
        for s_ in (-0.75, 0.75):
            o = Vector((0, s_, 1.05))
            tube(A["metal"], p + o, q + o, 0.09, RAIL, n=5)
            box_seg_light(p + Vector((0, s_, 0.02)), q + Vector((0, s_, 0.02)))
            o2 = Vector((0, s_, 0.5))
            tube(A["metal"], p + o2, q + o2, 0.03, RAIL, n=4)
            L = (q - p).length
            n = max(1, int(L / 1.6))
            for i in range(n + 1):
                c = p + (q - p) * (i / n)
                tube(A["metal"], c + Vector((0, s_, 0)), c + Vector((0, s_, 1.05)), 0.035, RAIL, n=4)

    def stair(p, q):
        d = q - p
        n = max(3, int(abs(d.z) / 0.55))
        for s_ in (-0.7, 0.7):
            K.seg_box(A["metal"], p + Vector((0, s_, 0)), q + Vector((0, s_, 0)), 0.12, 0.35, (0.16, 0.16, 0.17))
        for i in range(n):
            c = p + d * ((i + 0.5) / n)
            box(A["metal"], c.x - abs(d.x) / n / 2 - 0.05, c.y - 0.65, c.z - 0.06, c.x + abs(d.x) / n / 2 + 0.05, c.y + 0.65,
                c.z + 0.04, GRATE)
        rails(p, q)
        posts(p, q, step=2.5)

    nseg = {"walk": 0, "catwalk": 0, "ladder": 0, "stair": 0}
    for key, pts_ in V3["roof_paths"].items():
        pts = [Vector((x, YR, z)) for (x, z) in pts_]          # floor points
        for p, q in zip(pts, pts[1:]):
            d = q - p
            if abs(d.x) < 0.3 and abs(d.z) > 0.5:
                ladder(p.x, YR + 0.9, p.z, q.z)
                nseg["ladder"] += 1
            elif abs(d.z) < 0.3:
                under = max(roof_at(p.x + d.x * t) for t in (0.0, 0.25, 0.5, 0.75, 1.0))
                if p.z - under < 0.5:
                    K.seg_box(A["rough"], p + Vector((0, 0, 0.12)), q + Vector((0, 0, 0.12)), 1.3, 0.12, PLANK)
                    for t in range(int(abs(d.x) / 0.7)):
                        xx = min(p.x, q.x) + 0.35 + t * 0.7
                        box(A["rough"], xx - 0.05, p.y - 0.66, p.z + 0.12, xx + 0.05, p.y + 0.66, p.z + 0.15, (0.08, 0.07, 0.06))
                    nseg["walk"] += 1
                else:
                    K.seg_box(A["metal"], p, q, 1.5, 0.22, GRATE)
                    rails(p, q)
                    posts(p, q)
                    x = min(p.x, q.x) + 1.0
                    while x < max(p.x, q.x) - 0.5:
                        box(A["small"], x - 0.12, p.y + 0.75, p.z + 1.1, x + 0.12, p.y + 0.85, p.z + 1.3, (1.0, 0.7, 0.35), 6.0)
                        x += 4.0
                    nseg["catwalk"] += 1
            else:
                stair(p, q)
                nseg["stair"] += 1
    # work lights along the rooftop lane (warm pools on the roofs it walks; they make the roofs read from the street)
    seen = set()
    for key, pts_ in V3["roof_paths"].items():
        for (x, z) in pts_[1:-1]:
            kx = int(x // 9)
            if kx in seen:
                continue
            seen.add(kx)
            K.add_light("roofwork_%d" % len(seen), "POINT", (x, YR + 3.0, z + 4.0), LH["roof_w"] * 0.45, (1.0, 0.72, 0.45),
                        size=0.8, group="corp", shadow=False)
    K.log("alley v3: rooftop lane", nseg, "work lights", len(seen))

    # ---------------------------------------------------------------- fire escapes (THE DROP's climb + others)
    def fire_escape(x0, x1, h, ladder_x=None):
        z = 4.2
        k_ = 0
        lx0, lx1 = x0 + 0.6, x1 - 0.6
        while z < h - 3.0:
            box(A["metal"], lx0, FY - 2.0, z, lx1, FY, z + 0.18, (0.16, 0.16, 0.17))
            box(A["metal"], lx0, FY - 2.05, z + 0.18, lx1, FY - 1.95, z + 1.15, (0.22, 0.22, 0.23))
            for xx in (lx0, lx1):
                tube(A["metal"], (xx, FY - 2.0, z), (xx, FY - 2.0, z + 1.15), 0.04, (0.22, 0.22, 0.23), n=4)
            a_ = (lx0 + 0.4, FY - 1.0, z + 0.18) if k_ % 2 == 0 else (lx1 - 0.4, FY - 1.0, z + 0.18)
            b_ = (lx1 - 0.6, FY - 1.0, z + 3.9) if k_ % 2 == 0 else (lx0 + 0.6, FY - 1.0, z + 3.9)
            if z + 3.9 < h - 3.0:
                K.seg_box(A["metal"], Vector(a_), Vector(b_), 1.0, 0.25, (0.17, 0.17, 0.18))
            z += 3.9
            k_ += 1
        gx = (lx0 + lx1) / 2                                         # the top: a gooseneck ladder over the parapet
        for s_ in (-0.45, 0.45):
            tube(A["metal"], (gx + s_, FY - 1.6, z - 3.9), (gx + s_, FY - 1.6, h + 1.4), 0.06, RAIL, n=4)
            tube(A["metal"], (gx + s_, FY - 1.6, h + 1.4), (gx + s_, FY + 0.8, h + 1.6), 0.06, RAIL, n=4)
            tube(A["metal"], (gx + s_, FY + 0.8, h + 1.6), (gx + s_, FY + 1.4, h), 0.06, RAIL, n=4)
        if ladder_x is not None:
            ladder(ladder_x, FY - 1.3, 0.0, h - 12.0)

    fe_lots = set()
    for li, L_ in enumerate(lotinfo):
        x0, x1, h = L_["x0"], L_["x1"], L_["h"]
        if abs(x0 + 190.0) < 0.1:                                   # THE DROP's climb (start -> L1)
            fire_escape(x0, x1, h, ladder_x=None)
            fe_lots.add(li)
        elif L_["kind"] == "plain" and not L_["lane"] and x1 - x0 > 7.0 and h > 24 and rd.random() < 0.38:
            fire_escape(x0, x1, h)
            fe_lots.add(li)

    # ---------------------------------------------------------------- street level: shop fronts, awnings, boards, flags
    boards = sorted(f for f in os.listdir(tex_dir) if f.startswith("board_"))
    blades = sorted(f for f in os.listdir(tex_dir) if f.startswith("blade_") and not f.startswith("blade_red"))
    reds = sorted(f for f in os.listdir(tex_dir) if f.startswith("blade_red"))
    boxes_t = sorted(f for f in os.listdir(tex_dir) if f.startswith("box_"))
    wraps_t = sorted(f for f in os.listdir(tex_dir) if f.startswith("wrap_"))
    cloths = sorted(f for f in os.listdir(tex_dir) if f.startswith("cloth_"))
    tickers = sorted(f for f in os.listdir(tex_dir) if f.startswith("ticker_"))
    yf = FY - 0.05
    lantern_rows = []
    for li, L_ in enumerate(lotinfo):
        x0, x1, h = L_["x0"], L_["x1"], L_["h"]
        if L_["kind"] != "plain" or over_room((x0 + x1) / 2, 0.0, 4.0, pad=-1.0):
            continue
        sc = [(1.0, 0.55, 0.25), (0.45, 0.9, 1.0), (1.0, 0.35, 0.55), (0.9, 0.95, 1.0), (0.6, 1.0, 0.6)][rd.randrange(5)]
        box(A["sign"], x0 + 0.5, yf - 0.06, 0.3, x1 - 0.5, yf - 0.02, 3.6, sc, rd.uniform(1.4, 2.4))
        if rd.random() < 0.3:                                       # roll shutter half down
            box(A["metal"], x0 + 0.5, yf - 0.2, 2.2, x1 - 0.5, yf - 0.1, 3.7, (0.16, 0.16, 0.17))
        aw = [(0.45, 0.06, 0.05), (0.08, 0.1, 0.3), (0.4, 0.3, 0.05), (0.08, 0.25, 0.12)][rd.randrange(4)]
        box(A["rough"], x0 + 0.2, yf - 2.2, 3.9, x1 - 0.2, yf, 4.15, aw)                      # awning
        if boards and (x1 - x0) > 5.5:
            bw = min(x1 - x0 - 1.0, 7.5)
            bx = (x0 + x1) / 2 - bw / 2
            tex_quads(boards[rd.randrange(len(boards))], [facing_quad(bx, bx + bw, yf - 0.25, 4.4, 4.4 + bw / 4)],
                      AL["sign_k"] * 0.8)
        r_ = rd.random()
        if r_ < 0.35:                                               # a row of paper lanterns under the awning
            lantern_rows.append((x0 + 1.0, x1 - 1.0, yf - 1.6, 3.2))
        elif r_ < 0.6 and cloths:                                   # nobori flags at the shop
            for q in range(rd.randint(1, 2)):
                fx = rd.uniform(x0 + 0.8, x1 - 1.8)
                tube(A["metal"], (fx, yf - 2.6, 0.0), (fx, yf - 2.6, 5.6), 0.05, (0.3, 0.3, 0.3), n=4)
                tex_quads(cloths[rd.randrange(len(cloths))], [facing_quad(fx + 0.06, fx + 1.06, yf - 2.6, 1.4, 5.4)], 0.35,
                          mode="cloth")
        if rd.random() < 0.35:                                      # vending machines
            vx = rd.choice((x0 + 0.6, x1 - 2.2))
            box(A["metal"], vx, yf - 1.3, 0.0, vx + 1.6, yf, 3.2, (0.6, 0.6, 0.62))
            box(A["sign"], vx + 0.15, yf - 1.32, 0.9, vx + 1.45, yf - 1.3, 2.9, (0.85, 0.95, 1.0), 2.2)

    def lantern(x, y, z, col, r=0.42, hh=0.85):
        tube(A["small"], (x, y, z - hh / 2), (x, y, z + hh / 2), r, col, k=7.0, n=10)
        tube(A["metal"], (x, y, z + hh / 2), (x, y, z + hh / 2 + 0.1), r * 0.7, (0.05, 0.05, 0.05), n=10)
        tube(A["metal"], (x, y, z - hh / 2 - 0.1), (x, y, z - hh / 2), r * 0.7, (0.05, 0.05, 0.05), n=10)
    LCOL = [(1.0, 0.18, 0.08), (1.0, 0.8, 0.55), (1.0, 0.3, 0.1)]
    for (a_, b_, y_, z_) in lantern_rows:
        n = max(2, int((b_ - a_) / 1.3))
        for q in range(n):
            lantern(a_ + q * (b_ - a_) / max(1, n - 1), y_, z_, LCOL[q % 3])

    # ---------------------------------------------------------------- facade signage: varied kits per lot
    fac = []                                                        # (x0, x1, z0, z1) free facade bands
    for li, L_ in enumerate(lotinfo):
        x0, x1, h = L_["x0"], L_["x1"], L_["h"]
        z0 = 10.4
        if L_["kind"] == "dispatch" or x0 <= G.SHAFT_X <= x1:      # DISPATCH (MAINFRAME) and the shaft's face stay clear
            continue
        fac.append((li, x0, x1, z0, h - 1.2))
    nsig = {"blade": 0, "box": 0, "wrap": 0, "ticker": 0, "banner": 0, "board": 0}
    blade_groups = {}

    def add_blade(x, z0, bw, red=False):
        bh = bw * 4.0 * rs.uniform(0.85, 1.1)
        fn = (reds if red else blades)[rs.randrange(len(reds if red else blades))]
        ang = rs.choice((-25.0, 25.0, 18.0, -18.0))
        blade_groups.setdefault(fn, []).append(facing_quad(x, x + bw, FY - 1.2, z0, z0 + bh, ang))
        box(A["metal"], x - 0.05, FY - 1.25, z0 + 0.3, x + 0.1, FY, z0 + 0.6, (0.2, 0.2, 0.2))
        box(A["metal"], x - 0.05, FY - 1.25, z0 + bh - 0.6, x + 0.1, FY, z0 + bh - 0.3, (0.2, 0.2, 0.2))
        nsig["blade"] += 1
        return bh

    def add_box(x, z, s=2.2):
        fn = boxes_t[rs.randrange(len(boxes_t))]
        y0, y1 = FY - 1.6 - s, FY - 1.6
        q = [[(x, y0, z), (x + s, y0, z), (x + s, y0, z + s), (x, y0, z + s)],                  # front
             [(x, y1, z), (x, y0, z), (x, y0, z + s), (x, y1, z + s)],                          # left
             [(x + s, y0, z), (x + s, y1, z), (x + s, y1, z + s), (x + s, y0, z + s)]]          # right
        tex_quads(fn, q, AL["sign_k"] * 0.75)
        box(A["metal"], x - 0.05, y0 - 0.05, z + s, x + s + 0.05, y1 + 0.05, z + s + 0.12, (0.1, 0.1, 0.1))
        box(A["metal"], x + s / 2 - 0.08, y1, z + s * 0.4, x + s / 2 + 0.08, FY, z + s * 0.6, (0.2, 0.2, 0.2))
        nsig["box"] += 1

    def add_wrap(x0, x1, z):
        fn = wraps_t[rs.randrange(len(wraps_t))]
        dep = 1.4
        hh = 2.6
        box(A["rough"], x0, FY - dep, z - 0.4, x1, FY, z + hh + 0.4, (0.08, 0.07, 0.07))       # the bay
        y0 = FY - dep - 0.03
        q = [[(x0, FY, z), (x0, y0, z), (x0, y0, z + hh), (x0, FY, z + hh)],
             [(x0, y0, z), (x1, y0, z), (x1, y0, z + hh), (x0, y0, z + hh)],
             [(x1, y0, z), (x1, FY, z), (x1, FY, z + hh), (x1, y0, z + hh)]]
        tex_quads(fn, q, AL["sign_k"] * 0.7, uvs=[((0, 0), (1 / 3, 0), (1 / 3, 1), (0, 1)),
                                                   ((1 / 3, 0), (2 / 3, 0), (2 / 3, 1), (1 / 3, 1)),
                                                   ((2 / 3, 0), (1, 0), (1, 1), (2 / 3, 1))])
        nsig["wrap"] += 1

    def add_ticker(x0, x1, z):
        fn = tickers[rs.randrange(len(tickers) - 1)] if rs.random() > 0.12 else tickers[-1]   # the last one is red
        box(A["metal"], x0, FY - 0.5, z - 0.15, x1, FY, z + 1.05, (0.05, 0.05, 0.05))
        tex_quads(fn, [[(x0, FY - 0.52, z), (x1, FY - 0.52, z), (x1, FY - 0.52, z + 0.9), (x0, FY - 0.52, z + 0.9)]],
                  AL["sign_k"] * 0.8, uvs=[((0, 0), ((x1 - x0) / 32.0, 0), ((x1 - x0) / 32.0, 1), (0, 1))])
        nsig["ticker"] += 1

    def add_banner(x, h, w=2.4, hh=None):
        fn = cloths[rs.randrange(len(cloths))]
        hh = hh or w * 4.0
        y = FY - 0.35
        z1, z0 = h - 0.4, h - 0.4 - hh
        zm = (z0 + z1) / 2
        q = [[(x, y, zm), (x + w, y, zm), (x + w, y, z1), (x, y, z1)],
             [(x, y - 0.25, z0), (x + w, y - 0.25, z0), (x + w, y, zm), (x, y, zm)]]
        tex_quads(fn, q, 0.45, mode="cloth", uvs=[((0, 0.5), (1, 0.5), (1, 1), (0, 1)), ((0, 0), (1, 0), (1, 0.5), (0, 0.5))])
        tube(A["metal"], (x - 0.2, y, z1 + 0.1), (x + w + 0.2, y, z1 + 0.1), 0.06, (0.2, 0.2, 0.2), n=4)
        nsig["banner"] += 1

    for (li, x0, x1, z0, z1) in fac:
        if z1 - z0 < 4.0:
            continue
        lane = lotinfo[li]["lane"]
        w = x1 - x0
        CYC = ["box", "wrap", "ticker", "banner", "board", "box", "ticker", "wrap", "banner"]   # every style recurs
        kits = [CYC[li % len(CYC)]] + ([CYC[(li + 4) % len(CYC)]] if w > 9 else []) + ["blade"]
        if li in fe_lots:
            kits = ["banner"] if rs.random() < 0.5 else []
        used = []
        for kit in kits:
            if kit == "blade":
                for _ in range(rs.randint(3, 6 if w > 10 else 4)):
                    bw = rs.uniform(2.4, 3.2)
                    x = rs.uniform(x0 + 0.3, x1 - bw - 0.2)
                    zz = rs.uniform(z0, max(z0 + 0.1, min(z1 - 1.0, 64.0) - bw * 4.2))
                    if zz + bw * 4.4 > z1 or over_room(x + bw / 2, zz, zz + bw * 4.4, pad=2.0) or \
                            any(a < x + bw + 0.4 and x < b + 0.4 and c < zz + bw * 4.4 and zz < d for (a, b, c, d) in used):
                        continue
                    add_blade(x, zz, bw, red=rs.random() < V3["takeover_p"])
                    used.append((x, x + bw, zz, zz + bw * 4.4))
            elif kit == "box":
                x = rs.uniform(x0 + 0.4, x1 - 2.6)
                zz = rs.uniform(z0, max(z0 + 0.1, z1 - 7.5))
                n = rs.randint(1, 3)
                if over_room(x + 1.1, zz, zz + 2.4 * n, pad=2.0) or \
                        any(a < x + 2.6 and x < b and c < zz + 2.4 * n and zz < d for (a, b, c, d) in used):
                    continue
                for q in range(n):
                    if zz + 2.4 * q + 2.2 < z1:
                        add_box(x, zz + 2.4 * q)
                used.append((x, x + 2.6, zz, zz + 2.4 * n))
            elif kit == "wrap" and w > 6.0:
                zz = rs.uniform(z0 + 1.0, max(z0 + 1.1, min(z1 - 4.0, 24.0)))
                a_, b_ = x0 + 0.8, x1 - 0.8
                if zz + 3.4 > z1 or over_room((a_ + b_) / 2, zz, zz + 3.0, pad=(b_ - a_) / 2 + 0.5) or \
                        any(a < b_ and a_ < b and c < zz + 3.4 and zz - 0.4 < d for (a, b, c, d) in used):
                    continue
                add_wrap(a_, b_, zz)
                used.append((a_, b_, zz - 0.4, zz + 3.4))
            elif kit == "ticker":
                zz = rs.choice([v for v in (11.0, 14.9, 18.8, 22.7) if v < z1 - 1.5] or [z0])
                if over_room((x0 + x1) / 2, zz, zz + 1.0, pad=w / 2) or \
                        any(a < x1 and x0 < b and c < zz + 1.1 and zz - 0.2 < d for (a, b, c, d) in used):
                    continue
                add_ticker(x0 + 0.1, x1 - 0.1, zz)
                used.append((x0, x1, zz - 0.2, zz + 1.1))
            elif kit == "banner" and not lane and z1 > 20:
                bwid = min(2.6, w - 1.0)
                x = rs.uniform(x0 + 0.4, x1 - bwid - 0.4)
                hh = min(bwid * 4.0, z1 - z0 - 1.0)
                if over_room(x + bwid / 2, z1 - hh, z1, pad=1.0) or \
                        any(a < x + bwid and x < b and c < z1 and z1 - hh < d for (a, b, c, d) in used):
                    continue
                add_banner(x, z1 + 1.2, bwid, hh)
                used.append((x, x + bwid, z1 - hh, z1))
            elif kit == "board" and boards and w > 6.0:
                bw = min(w - 1.0, 9.0)
                bx = (x0 + x1) / 2 - bw / 2
                zz = rs.uniform(z0, max(z0 + 0.1, z1 - bw / 4 - 1.0))
                if over_room(bx + bw / 2, zz, zz + bw / 4, pad=bw / 2) or \
                        any(a < bx + bw and bx < b and c < zz + bw / 4 and zz < d for (a, b, c, d) in used):
                    continue
                tex_quads(boards[rs.randrange(len(boards))], [facing_quad(bx, bx + bw, FY - 0.3, zz, zz + bw / 4)],
                          AL["sign_k"] * 0.7)
                used.append((bx, bx + bw, zz, zz + bw / 4))
                nsig["board"] += 1
        # AC units and small fittings on every facade (never in front of a room or a sign)
        for _ in range(int(w * (z1 - z0) / 70)):
            ax = rd.uniform(x0 + 0.6, x1 - 1.8)
            az = rd.uniform(z0, z1 - 1.0)
            if over_room(ax + 0.6, az, az + 1.0) or any(a - 0.5 < ax + 1.3 and ax < b + 0.5 and c < az + 1 and az < d
                                                        for (a, b, c, d) in used):
                continue
            box(A["metal"], ax, yf - 1.0, az, ax + 1.3, yf, az + 0.9, (0.2, 0.2, 0.21))
            box(A["small"], ax + 0.15, yf - 1.02, az + 0.15, ax + 0.35, yf - 1.0, az + 0.3, (1.0, 0.4, 0.2), 4.0)
        if not lane and rd.random() < 0.35:                         # a neon ledge line
            zz = rd.uniform(z0, z1 - 1.0)
            if not over_room((x0 + x1) / 2, zz, zz + 0.3, pad=w / 2):
                c_ = [pal("neon_a"), pal("neon_b"), (1.0, 0.6, 0.2), (0.6, 1.0, 0.4)][rd.randrange(4)]
                box(A["trim"], x0 + 0.3, yf - 0.12, zz, x1 - 0.3, yf - 0.05, zz + 0.25, c_, 3.0)
    for fn, qs in blade_groups.items():
        tex_quads(fn, qs, AL["sign_k"])
    K.log("alley v3: facade signs", nsig)

    # ---------------------------------------------------------------- the MAINFRAME sign on the TARGET (DISPATCH)
    my = FY - V3["mf_off"]
    mh = MZ1 - MZ0
    tex_quads("mainframe.png", [facing_quad(MX - MW / 2, MX + MW / 2, my, MZ0, MZ1, 0.0)], V3["mf_k"], idx=3)
    box(A["metal"], MX - MW / 2 - 0.35, my + 0.05, MZ0 - 0.35, MX + MW / 2 + 0.35, my + 0.7, MZ1 + 0.35, (0.05, 0.03, 0.03))
    roof_d = next(L_["h"] for L_ in lotinfo if L_["kind"] == "dispatch")
    for zz in (MZ0 + 2.0, (MZ0 + roof_d) / 2, roof_d - 2.0):                      # brackets to the facade
        box(A["metal"], MX - 0.3, my + 0.7, zz, MX + 0.3, FY, zz + 0.5, (0.2, 0.2, 0.2))
    for s_ in (-1, 1):                                                            # its frame above the roof
        xx = MX + s_ * (MW / 2 - 0.6)
        tube(A["metal"], (xx, my + 0.9, roof_d), (xx, my + 0.9, MZ1 + 0.2), 0.2, (0.12, 0.12, 0.12), n=6)
        tube(A["metal"], (xx, FY + 5.0, roof_d), (xx, my + 0.9, MZ1 - 2.0), 0.14, (0.12, 0.12, 0.12), n=6)
    K.add_light("mainframe_spill", "AREA", (MX, my - 3.0, (MZ0 + MZ1) / 2), LH["mf_spill_w"], (1.0, 0.08, 0.08),
                aim=(MX, FY + 2.0, MZ0 - 6.0), size=MW + 3.0, size_y=mh, group="corp", shadow=False)
    # t4 (designer): the TARGET reads as the landmark through its BUILDING, not a hotter sign: a warm wash up DISPATCH's
    # facade, lit corner and cornice trims (red accent), a lit lobby band under the server room
    dl = next(L_ for L_ in lotinfo if L_["kind"] == "dispatch")
    for s_ in (-1, 1):
        wx = (dl["x0"] + dl["x1"]) / 2 + s_ * 7.0
        K.add_light("target_wash_%d" % (s_ + 1), "AREA", (wx, FY - 14.0, 3.0), V3.get("target_wash_w", 4000.0),
                    (1.0, 0.82, 0.7), aim=(wx, FY, 30.0), size=8.0, size_y=3.0, group="corp", shadow=False)
    for xx in (dl["x0"], dl["x1"]):
        box(A["trim"], xx - 0.2, FY - 0.25, 0.4, xx + 0.2, FY + 0.05, roof_d - 0.5, (1.0, 0.25, 0.22), 2.2)
    box(A["trim"], dl["x0"], FY - 0.3, roof_d - 0.9, dl["x1"], FY, roof_d - 0.5, (1.0, 0.3, 0.25), 2.4)
    box(A["sign"], dl["x0"] + 1.0, FY - 0.08, 1.0, dl["x1"] - 1.0, FY - 0.03, 4.2, (1.0, 0.85, 0.7), 1.8)   # the lobby
    K.add_light("target_room", "AREA", (MX, CUT - 4.0, srv["o"][2] + srv["h"] + 1.0), V3.get("target_wash_w", 4000.0) * 0.5,
                (1.0, 0.75, 0.65), aim=(MX, FY, srv["o"][2]), size=srv["w"], size_y=2.0, group="corp", shadow=False)
    K.add_light("mainframe_floor", "AREA", (MX, FY - 8.0, 3.0), LH["mf_spill_w"] * 0.35, (1.0, 0.1, 0.1),
                aim=(MX, FY - 8.0, 0.0), size=MW + 8.0, size_y=8.0, group="corp", shadow=False)

    # ---------------------------------------------------------------- the alley: slab, kerb, poles, cables, stalls
    box(A["ground"], AL["x_a"] - 40, ky, -0.7, AL["x_b"] + 40, FY, 0.0, (0.07, 0.07, 0.08), k=0.0)
    box(A["trim"], AL["x_a"] - 40, ky - 0.05, -0.25, AL["x_b"] + 40, ky + 0.05, -0.05, (0.9, 0.85, 0.8), 0.5)
    box(A["ground"], AL["x_a"] - 40, FY - 2.2, 0.0, AL["x_b"] + 40, FY, 0.18, (0.2, 0.2, 0.22), k=1.0)
    for x in range(int(AL["x_a"]) + 20, int(AL["x_b"]), 55):
        tube(A["metal"], (x, ky + 5.0, 0.0), (x, ky + 5.0, 0.03), 1.1, (0.12, 0.12, 0.12), n=14)
    poles = []
    for c in cols + [G.X0 - 22.0, MX + 26.0]:
        px = c + 22.0 if c in cols else c
        if over_room(px, 0, AL["pole_h"], pad=1.0) or any(abs(px - p) < 10 for p in poles):
            continue
        poles.append(px)
    poles.sort()
    ph = AL["pole_h"]

    def catenary(p, q, sag, r=0.07, col=(0.05, 0.05, 0.06), n=10):
        pts = []
        for i in range(n + 1):
            t = i / n
            pts.append(Vector((p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t,
                               p[2] + (q[2] - p[2]) * t - sag * 4 * t * (1 - t))))
        for a_, b_ in zip(pts, pts[1:]):
            tube(A["metal"], a_, b_, r, col, n=4)
        return pts
    for px in poles:
        py = ky + 0.9
        tube(A["metal"], (px, py, 0.0), (px, py, ph), 0.35, (0.16, 0.15, 0.14), n=8)
        for zz in (ph - 2.0, ph - 4.5):
            box(A["metal"], px - 2.4, py - 0.15, zz, px + 2.4, py + 0.15, zz + 0.3, (0.16, 0.15, 0.14))
        tube(A["metal"], (px + 0.8, py - 0.6, ph - 9.0), (px + 0.8, py - 0.6, ph - 6.5), 0.75, (0.25, 0.25, 0.27), n=10)
        box(A["metal"], px, py, ph - 10.0, px + 0.2, py + 3.0, ph - 9.8, (0.16, 0.15, 0.14))
        box(A["small"], px - 0.4, py + 2.6, ph - 10.3, px + 0.6, py + 3.4, ph - 10.0, (1.0, 0.75, 0.45), 14.0)
        K.add_light("alley_lamp_%d" % int(px), "SPOT", (px, py + 3.0, ph - 10.5), LH["alley_lamp_w"], (1.0, 0.72, 0.42),
                    aim=(px, py + 4.0, 0.0), size=0.6, spot=110, blend=0.9, group="corp", shadow=False)
        # wrap signs round the pole (a band of text round the post)
        if rs.random() < 0.6 and wraps_t:
            fn = wraps_t[rs.randrange(len(wraps_t))]
            rr_ = 0.5
            qs, us = [], []
            for i in range(8):
                a0, a1 = 2 * math.pi * i / 8, 2 * math.pi * (i + 1) / 8
                qs.append([(px + rr_ * math.cos(a0), py + rr_ * math.sin(a0), 5.0),
                           (px + rr_ * math.cos(a1), py + rr_ * math.sin(a1), 5.0),
                           (px + rr_ * math.cos(a1), py + rr_ * math.sin(a1), 6.6),
                           (px + rr_ * math.cos(a0), py + rr_ * math.sin(a0), 6.6)])
                us.append(((i / 8, 0), ((i + 1) / 8, 0), ((i + 1) / 8, 1), (i / 8, 1)))
            tex_quads(fn, qs, AL["sign_k"] * 0.6, uvs=us)
    for a_, b_ in zip(poles, poles[1:]):
        for k_, zz in enumerate((ph - 2.0, ph - 2.0, ph - 4.5, ph - 4.5, ph - 4.5)):
            off = (-2.0, 2.0, -1.8, 0.0, 1.8)[k_]
            catenary((a_ + off * 0.2, ky + 0.9 + off * 0.1, zz + 0.3), (b_ + off * 0.2, ky + 0.9 + off * 0.1, zz + 0.3),
                     rd.uniform(1.4, 2.6), r=0.06 + 0.03 * (k_ % 2))
    nl = 0
    for px in poles:                                                # cables + LANTERN STRINGS pole -> facade
        for k_ in range(3):
            tx = px + rd.uniform(-9, 9)
            tz = rd.uniform(11.0, 18.0)
            if over_room(tx, tz - 2, tz + 2, pad=0.0):
                continue
            pts = catenary((px, ky + 0.9, ph - 4.5 + 0.3), (tx, FY, tz), rd.uniform(0.8, 1.6), r=0.05)
            if k_ == 0:
                for p_ in pts[2:-1]:
                    if not over_room(p_.x, p_.z - 1.5, p_.z, pad=0.5):
                        lantern(p_.x, p_.y, p_.z - 0.75, LCOL[nl % 3], r=0.35, hh=0.7)
                        nl += 1
    for k_ in range(60):                                            # conduits end in the section face
        cx_ = rd.uniform(AL["x_a"] - 30, AL["x_b"] + 30)
        cz_ = rd.uniform(-9.0, -1.4)
        if any(abs(cx_ - r["o"][0]) < RW / 2 + 2 and cz_ < r["o"][2] + r["h"] + 5 for i, r in G.ROOM.items()
               if G.LANE.get(i) == "R"):
            continue
        r_ = rd.uniform(0.25, 0.8)
        c_ = [(0.2, 0.16, 0.12), (0.14, 0.2, 0.16), (0.25, 0.2, 0.1), (0.12, 0.12, 0.14), (0.3, 0.1, 0.08)][k_ % 5]
        tube(A["metal"], (cx_, ky - 0.25, cz_), (cx_, ky + 3.0, cz_), r_, c_, n=10)
    box(A["metal"], AL["x_a"] - 40, ky - 0.1, -0.95, AL["x_b"] + 40, ky + 0.02, -0.7, (0.14, 0.13, 0.12))
    for _ in range(40):                                             # crates / bins along the facade
        cx_ = rd.uniform(AL["x_a"], AL["x_b"])
        if over_room(cx_, 0, 3, pad=1.0):
            continue
        s_ = rd.uniform(0.7, 1.4)
        y_ = FY - 2.0 - rd.uniform(0, 1.5)
        box(A["rough"], cx_, y_, 0.18, cx_ + s_, y_ + s_, 0.18 + s_, (0.12, 0.1, 0.08))
    stall_x = [(cols[i] + cols[i + 1]) / 2 + rd.uniform(-4, 4) for i in range(len(cols) - 1)]
    stall_x += [G.X0 - 34.0, AL["x_a"] + 20.0, MX + 40.0]
    for k_, sx_ in enumerate(stall_x):
        if over_room(sx_, 0, 4.0, pad=4.5):
            continue
        sy_ = ky + rd.uniform(5.0, AW - 6.0)
        w_, d_ = rd.uniform(4.5, 6.0), 2.4
        box(A["rough"], sx_ - w_ / 2, sy_ - d_ / 2, 0.0, sx_ + w_ / 2, sy_ + d_ / 2, 1.9, (0.16, 0.09, 0.06))
        box(A["sign"], sx_ - w_ / 2 + 0.2, sy_ - d_ / 2 - 0.02, 1.2, sx_ + w_ / 2 - 0.2, sy_ - d_ / 2, 1.8, (1.0, 0.6, 0.3), 2.2)
        for (ex, ey) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            tube(A["metal"], (sx_ + ex * w_ / 2, sy_ + ey * d_ / 2, 1.9), (sx_ + ex * w_ / 2, sy_ + ey * d_ / 2, 3.8), 0.08,
                 (0.15, 0.15, 0.15), n=4)
        box(A["rough"], sx_ - w_ / 2 - 0.4, sy_ - d_ / 2 - 0.6, 3.8, sx_ + w_ / 2 + 0.4, sy_ + d_ / 2, 4.0,
            [(0.5, 0.06, 0.06), (0.1, 0.1, 0.35), (0.45, 0.32, 0.05)][k_ % 3])
        for q in range(3):
            lantern(sx_ - w_ / 2 + 0.8 + q * (w_ - 1.6) / 2, sy_ - d_ / 2 - 0.45, 3.2, LCOL[q % 3], r=0.32, hh=0.65)
        K.add_light("stall_%d" % k_, "POINT", (sx_, sy_ - d_ / 2 - 1.5, 3.2), LH["stall_w"], (1.0, 0.45, 0.2), size=1.0,
                    group="corp", shadow=False)
    for _ in range(14):                                             # scooters
        cx_ = rd.uniform(AL["x_a"], AL["x_b"])
        if over_room(cx_, 0, 2.0, pad=2.0):
            continue
        cy_ = FY - rd.uniform(2.6, 3.4)
        box(A["metal"], cx_, cy_ - 0.3, 0.4, cx_ + 2.0, cy_ + 0.3, 1.1, [(0.5, 0.1, 0.1), (0.1, 0.3, 0.5), (0.7, 0.7, 0.7)][_ % 3])
        box(A["small"], cx_ + 1.9, cy_ - 0.2, 0.9, cx_ + 2.05, cy_ + 0.2, 1.05, (1.0, 0.9, 0.7), 4.0)
    K.log("alley v3: poles", len(poles), "string lanterns", nl, "lantern rows", len(lantern_rows))

    # ---------------------------------------------------------------- the sewer (under the street)
    rc_sewer.build(K, AL, over_room, tex_quads, facing_quad, hooks, hooks["brick"])

    # ---------------------------------------------------------------- holograms: street level and rooftops
    mids = [(cols[i] + cols[i + 1]) / 2 for i in range(len(cols) - 1)]
    HS = [("holo_ramen.png", (0.4, 0.9, 1.0), 14.0), ("holo_can.png", (0.5, 0.8, 1.0), 12.0),
          ("holo_24.png", (0.4, 1.0, 0.6), 11.0), ("holo_chip.png", (1.0, 0.3, 0.8), 12.0)]
    holos = []
    for k_, hx in enumerate(mids + [G.X0 - 30.0]):
        fn, hc, hs = HS[k_ % len(HS)]
        hz = 10.5
        if over_room(hx, hz, hz + hs, pad=0.5):
            hs = 9.0
            if over_room(hx, hz, hz + hs, pad=0.5):
                continue
        holos.append((fn, hx, FY - 6.0, hz, hs, hc))
    # rooftop holograms (above the roofline, behind the lane): koi, maneki-neko, the red fist (an accent)
    for fn, hx, hy, hz, hs, hc in (("holo_koi.png", -59.0, CUT + 16.0, 41.0, 15.0, (1.0, 0.6, 0.3)),
                                   ("holo_neko.png", -232.0, CUT + 8.0, roof_at(-232.0) + 2.0, 13.0, (1.0, 0.9, 0.5)),
                                   ("holo_fist.png", 52.0, CUT + 8.0, roof_at(52.0) + 2.5, 13.0, (1.0, 0.06, 0.06))):
        if over_room(hx, hz, hz + hs, pad=0.5):
            continue
        holos.append((fn, hx, hy, hz, hs, hc))
        tube(A["metal"], (hx, hy, roof_at(hx)), (hx, hy, hz - 0.6), 0.3, (0.15, 0.15, 0.16), n=6)
        box(A["small"], hx - 1.0, hy - 1.0, hz - 1.0, hx + 1.0, hy + 1.0, hz - 0.5, hc, 6.0)
    for fn, hx, hy, hz, hs, hc in holos:
        tex_quads(fn, [facing_quad(hx - hs / 2, hx + hs / 2, hy, hz, hz + hs)], AL["holo_k"] * (0.8 if "fist" in fn else 1.0),
                  holo=True, idx=2)
        if hy < FY:
            tube(A["metal"], (hx, hy, hz - 1.2), (hx, hy, hz - 0.2), 0.25, (0.2, 0.2, 0.22), n=6)
        K.add_light("holo_spill_%d" % int(hx), "AREA", (hx, hy - 1.0, hz + hs / 2),
                    LH["holo_spill_w"] * (2.0 if "fist" in fn else 1.0), hc, aim=(hx, hy + 6.0, hz - 6.0), size=hs,
                    size_y=hs, group="corp", shadow=False)

    # ---------------------------------------------------------------- rooftop billboards + neon letters + a ticker crown
    bills = sorted(f for f in os.listdir(tex_dir) if f.startswith("bill_"))
    BL = [(-236.0, None, "bill_00.png", 15.0), (38.0, None, "bill_01.png", 14.0), (-104.0, 166.0, "bill_04.png", 22.0),
          (-206.0, 150.0, "bill_05.png", 18.0), (66.0, 150.0, "bill_06.png", 16.0), (-150.0, 190.0, "bill_03.png", 20.0)]
    blocks = HZ.get("_blocks", [])

    def block_at(x, y):
        for (bx0, by0, bx1, by1, bh) in blocks:
            if bx0 <= x <= bx1 and by0 <= y <= by1:
                return bh
        return None
    nbill = 0
    for (bx, by, fn, bw) in BL:
        if fn not in bills:
            continue
        if by is None:
            base, yb_ = roof_at(bx), FY + 6.0
        else:
            base, yb_ = block_at(bx, by), by
            if base is None:
                continue
        bh_ = bw / 2
        z0 = base + 4.0
        for s_ in (-1, 1):                                          # the scaffold
            for yy in (yb_, yb_ + 3.0):
                tube(A["metal"], (bx + s_ * bw * 0.35, yy, base), (bx + s_ * bw * 0.35, yy, z0 + bh_), 0.16, (0.13, 0.13, 0.13), n=5)
            tube(A["metal"], (bx + s_ * bw * 0.35, yb_, base), (bx + s_ * bw * 0.35, yb_ + 3.0, z0), 0.08, (0.13, 0.13, 0.13), n=4)
        box(A["metal"], bx - bw / 2 - 0.3, yb_ - 0.4, z0 - 0.3, bx + bw / 2 + 0.3, yb_ + 0.2, z0 + bh_ + 0.3, (0.06, 0.06, 0.06))
        box(A["metal"], bx - bw / 2, yb_ - 1.6, z0 - 0.5, bx + bw / 2, yb_ - 0.4, z0 - 0.3, (0.16, 0.16, 0.17))   # catwalk
        tex_quads(fn, [facing_quad(bx - bw / 2, bx + bw / 2, yb_ - 0.45, z0, z0 + bh_)], 1.3 if "06" not in fn else 1.0)
        for s_ in (-0.3, 0.3):                                      # up-lights on the catwalk
            box(A["small"], bx + s_ * bw - 0.3, yb_ - 1.5, z0 - 0.3, bx + s_ * bw + 0.3, yb_ - 1.0, z0, (1.0, 0.95, 0.85), 8.0)
        nbill += 1
    for (nx, fn, nw) in ((-252.0, "roofneon_00.png", 13.0), (60.0, "roofneon_02.png", 12.0)):
        base = roof_at(nx)
        for s_ in (-1, 1):
            tube(A["metal"], (nx + s_ * nw * 0.35, FY + 3.0, base), (nx + s_ * nw * 0.35, FY + 3.0, base + 3.0 + nw / 4), 0.1,
                 (0.13, 0.13, 0.13), n=4)
        box(A["metal"], nx - nw / 2, FY + 3.0, base + 2.6, nx + nw / 2, FY + 3.3, base + 2.8, (0.13, 0.13, 0.13))
        tex_quads(fn, [facing_quad(nx - nw / 2, nx + nw / 2, FY + 2.9, base + 2.8, base + 2.8 + nw / 4)], AL["holo_k"],
                  holo=True, idx=2)
    tall = sorted([b_ for b_ in blocks if CUT + 30 < b_[1] < CUT + 80 and -60 < b_[0] < -20], key=lambda b_: -b_[4])[:1]
    for (bx0, by0, bx1, by1, bh) in tall:                           # an LED ticker crown on a tall block behind
        tex_quads(tickers[2], [[(bx0, by0 - 0.3, bh - 2.4), (bx1, by0 - 0.3, bh - 2.4), (bx1, by0 - 0.3, bh - 1.2),
                                (bx0, by0 - 0.3, bh - 1.2)]], AL["sign_k"] * 0.9,
                  uvs=[((0, 0), ((bx1 - bx0) / 32.0, 0), ((bx1 - bx0) / 32.0, 1), (0, 1))])
    K.log("alley v3: holograms", len(holos), "billboards", nbill)

    # ---------------------------------------------------------------- t4: depth planes behind the district
    # a few dark towers in silhouette against the city glow, each with a LIT CROWN (bands, a setback box with lit edges,
    # a spire with aviation lights); their bodies keep only a corner light strip (PIPELINE_SPEC 13: atmosphere.layers)
    CROWN = [(0.75, 0.9, 1.0), (1.0, 0.7, 0.35), (0.4, 1.0, 0.85), (1.0, 0.45, 0.7)]
    for k_, (tx, ty, th, tw) in enumerate(V3.get("towers", [])):
        body = (0.03, 0.03, 0.035)
        box(A["rough"], tx - tw / 2, ty - tw / 2, 0.0, tx + tw / 2, ty + tw / 2, th, body)
        sw = tw * 0.72
        box(A["rough"], tx - sw / 2, ty - sw / 2, th, tx + sw / 2, ty + sw / 2, th + tw * 0.45, body)
        c_ = CROWN[k_ % len(CROWN)]
        for q in range(3):                                          # crown bands (front + sides)
            zz = th - 2.0 - q * 3.2
            box(A["trim"], tx - tw / 2 - 0.1, ty - tw / 2 - 0.1, zz, tx + tw / 2 + 0.1, ty + tw / 2 + 0.1, zz + 0.45,
                c_, 2.6 - 0.6 * q)
        for (ex, ey) in ((-1, -1), (1, -1)):                        # the setback's lit edges
            box(A["trim"], tx + ex * sw / 2 - 0.15, ty + ey * sw / 2 - 0.15, th, tx + ex * sw / 2 + 0.15,
                ty + ey * sw / 2 + 0.15, th + tw * 0.45, c_, 2.2)
        box(A["trim"], tx - sw / 2, ty - sw / 2 - 0.15, th + tw * 0.45 - 0.4, tx + sw / 2, ty - sw / 2, th + tw * 0.45,
            c_, 2.2)
        tube(A["metal"], (tx, ty, th + tw * 0.45), (tx, ty, th + tw * 0.45 + 14.0), 0.4, (0.05, 0.05, 0.05), n=6)
        for zz in (th + tw * 0.45 + 6.0, th + tw * 0.45 + 14.0):
            box(A["small"], tx - 0.5, ty - 0.5, zz, tx + 0.5, ty + 0.5, zz + 0.6, (1.0, 0.12, 0.08), 9.0)
        box(A["trim"], tx - tw / 2 - 0.1, ty - tw / 2 - 0.1, 0.0, tx - tw / 2 + 0.3, ty - tw / 2 + 0.3, th - 10.0,
            c_, 0.8)                                                # a corner light strip
    K.log("alley v3: background towers", len(V3.get("towers", [])))

    R2._rooms(K, G, A, box, tube, tex_quads, facing_quad, boards, blades, rd, LH, pal)
    hooks.update(R2._street_strips(K, CP, LH, pal, section=True))
    hooks.setdefault("tex_objs", []).extend(objs)
    hooks["lots"] = lots
    return objs
