"""HQ Meridian: the Blender build of the container fortress (called by the kit's hq_scene.py: build(K) -> hooks).

Everything is placed by rule from hq_preset "compound" + hq_graph; seeds: 5320 (container colours / IDs), 5321 (yard
stacks), 5322 (sleepers / signals), 5323 (banners).
  walls      container courses between the corner towers, in runs between the route rooms (a room = a container slot
             cut open on its outer face); the top course alternates full and half containers (merlons)
  towers     5 courses of crossed containers (the course orientation alternates), flood masts, red beacons
  moat       west, south, east; the rail yard on the north (the through track + a siding, a parked train)
  gate       the gatehouse on the west wall, a lit portcullis, the container drawbridge on chains
  crane      the gantry crane straddling the north wall and the track, the boom over the yard (static frame), the
             trolley + hook container + cables (movers)
  train      loco + flatcars on the through track, one carrying the CAR room (mover)
  control    MANIFEST CONTROL: glass + steel tower, m1 / m2 cut into its north face, THE MASTER MANIFEST vault on the
             roof (open all round), the MERIDIAN FREIGHT crown sign
  links      facade catwalks at sill height, ladders where a course changes, the corner stairs, the skyway, gangways
"""
import math
import random


def build(K):
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, Acc, obox, oquad, rf, tube, box = K.A, K.Acc, K.obox, K.oquad, K.rf, K.tube, K.box
    Vector = K.Vector
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ("mv_", "cable")}
    rr = random.Random(5320)
    CRS, RW, RH, RD = CP["course"], CP["room_w"], CP["room_h"], CP["room_d"]
    WX, WY = CP["wall"]["x"], CP["wall"]["y"]
    NC = CP["wall"]["courses"]
    TC, TH_ = CP["tower"]["c"], CP["tower"]["half"]
    TCO = CP["tower"]["courses"]
    CTL = CP["control"]
    STEEL = pal("steel_alt")
    ORANGE, RED, YW, YC, HAZ = pal("corp_orange"), pal("corp_red"), pal("yard_white"), pal("yard_cool"), pal("hazard")

    # ------------------------------------------------------------ the container material (corrugated, wet, rust)
    m, nt = K.new_mat("container")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = K.attr(nt, "col")
    g, ps, ns = K.pos_sep(nt)
    u = K.mth(nt, "ADD", ps.outputs["X"], ps.outputs["Y"])
    rib = K.mth(nt, "SINE", K.mth(nt, "MULTIPLY", u, 4.2))
    n1 = K.nn(nt, "ShaderNodeTexNoise", Scale=0.18, Detail=6.0, Roughness=0.62)
    nt.links.new(g.outputs["Position"], n1.inputs["Vector"])
    rust = K.smooth(nt, n1.outputs["Fac"], 0.48, 0.70)
    n2 = K.nn(nt, "ShaderNodeTexNoise", Scale=1.1, Detail=3.0)
    nt.links.new(K.vmul(nt, g.outputs["Position"], (1.0, 1.0, 0.07)), n2.inputs["Vector"])
    streak = K.smooth(nt, n2.outputs["Fac"], 0.5, 0.78)
    base = K.vsc(nt, col.outputs["Color"], K.mth(nt, "MULTIPLY", K.mth(nt, "ADD", 0.85, K.mth(nt, "MULTIPLY", rib, 0.08)),
                                                  K.mth(nt, "SUBTRACT", 1.0, K.mth(nt, "MULTIPLY", streak, 0.25))))
    base = K.mixc(nt, K.mth(nt, "MULTIPLY", rust, 0.55), base, (0.16, 0.05, 0.018))
    nt.links.new(base, b.inputs["Base Color"])
    nt.links.new(K.mth(nt, "ADD", 0.22, K.mth(nt, "MULTIPLY", rust, 0.45)), b.inputs["Roughness"])
    b.inputs["Metallic"].default_value = 0.35
    b.inputs["Coat Weight"].default_value = 0.3
    b.inputs["Coat Roughness"].default_value = 0.1
    bump = K.nn(nt, "ShaderNodeBump", Strength=0.35, Distance=0.08)
    nt.links.new(rib, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
    nt.links.new(b.outputs[0], out.inputs[0])
    M_CONT = m
    C = Acc("containers", M_CONT, 1, K.COLL["compound"])
    hooks["accs"]["containers"] = C
    STRIPE = Acc("hazard_paint", K.M["rough"], 1, K.COLL["compound"])
    hooks["accs"]["hazard_paint"] = STRIPE

    def container(rec, u0, u1, dn0, dn1, z0, z1, colr=None, doors=True):
        c = colr or STEEL[rr.randrange(len(STEEL))]
        obox(C, rec, u0, u1, dn0, dn1, z0 + 0.15, z1, c)
        # corner castings + door-end bars (read the courses at distance)
        for uu in (u0, u1 - 0.35):
            obox(A["metal"], rec, uu, uu + 0.35, dn1 - 0.02, dn1 + 0.06, z0 + 0.15, z1, (0.05, 0.05, 0.055))
        if doors and rr.random() < 0.35:            # an ID band (barcode stripe) on the outer face, signage LOD
            zz = z0 + (z1 - z0) * 0.72
            uu = rr.uniform(u0 + 1.0, max(u0 + 1.2, u1 - 5.0))
            for q in range(10):
                if rr.random() < 0.6:
                    oquad(A["sign"], rec, dn1 + 0.04, uu + q * 0.36, zz, uu + q * 0.36 + 0.2, zz + 0.9, (0.9, 0.9, 0.85), 0.35)

    def wall_frame(side):
        return {"W": dict(o=(-WX, 0.0, 0.0), n=(-1.0, 0.0)), "N": dict(o=(0.0, WY, 0.0), n=(0.0, 1.0)),
                "E": dict(o=(WX, 0.0, 0.0), n=(1.0, 0.0)), "S": dict(o=(0.0, -WY, 0.0), n=(0.0, -1.0))}[side]

    rooms_on = {}
    for (nid, wall, uu, c) in CP["rooms"]:
        if wall in ("W", "N"):
            rooms_on.setdefault((wall, c), []).append(uu)
    gate_u = CP["gate_u"]

    # ------------------------------------------------------------ the walls: container courses in runs
    for side in ("W", "N", "E", "S"):
        rec = wall_frame(side)
        L = (TC[1] - TH_) if side in ("W", "E") else (TC[0] - TH_)
        for c in range(NC + 1):
            z0, z1 = c * CRS, c * CRS + CRS - 1.0
            cuts = sorted(rooms_on.get((side, c), []))
            gaps = [(uu - RW / 2, uu + RW / 2) for uu in cuts]
            if side == "W" and c == 0:
                gaps.append((gate_u - 5.0, gate_u + 5.0))
            gaps.sort()
            if c == NC:                              # merlons: half containers every other slot
                uu = -L
                k = 0
                while uu < L - 1:
                    if k % 2 == 0:
                        container(rec, uu, min(uu + 7.0, L), -RD, 0.0, z0, z0 + 4.6, doors=False)
                    uu += 7.4
                    k += 1
                continue
            runs, a = [], -L
            for (g0, g1) in gaps:
                runs.append((a, g0))
                a = g1
            runs.append((a, L))
            for (r0, r1) in runs:
                uu = r0
                while uu < r1 - 0.8:
                    v = min(uu + 14.0, r1)
                    container(rec, uu + 0.1, v - 0.1, -RD, 0.0, z0, z1)
                    uu = v + 0.3
            if side == "W" and c == 0:               # the gate: lintel container over the opening
                pass
        # the battlement walk: lit warm strip under the merlons (big layer) on both faces
        for dn in (0.08, -RD - 0.08):
            oquad(A["trim"], rec, dn, -L, NC * CRS - 0.6, L, NC * CRS - 0.35, YW, LH["trim_k"])
    log = K.log
    log("walls")

    # ------------------------------------------------------------ corner towers: crossed courses, masts, beacons
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * TC[0], sy * TC[1]
            for c in range(TCO):
                z0, z1 = c * CRS, c * CRS + CRS - 1.0
                along_x = c % 2 == 0
                if sy == 1 and c == 3:
                    continue                          # the tower room's course (t1 / t2): built below
                for k in range(2):
                    off = -TH_ + k * TH_
                    if along_x:
                        r_ = dict(o=(cx, cy + off + TH_, 0.0), n=(0.0, 1.0))
                        container(r_, -TH_, TH_, -TH_ + 0.2, 0.0, z0, z1)
                    else:
                        r_ = dict(o=(cx + off + TH_, cy, 0.0), n=(1.0, 0.0))
                        container(r_, -TH_, TH_, -TH_ + 0.2, 0.0, z0, z1)
            # the tower room course on the north towers: walls round the room slot
            if sy == 1:
                r_ = dict(o=(cx, cy + TH_, 0.0), n=(0.0, 1.0))
                z0 = 3 * CRS
                obox(C, r_, -TH_, -RW / 2 - 0.4, -2 * TH_, 0.0, z0 + 0.15, z0 + CRS - 1.0, STEEL[1])
                obox(C, r_, RW / 2 + 0.4, TH_, -2 * TH_, 0.0, z0 + 0.15, z0 + CRS - 1.0, STEEL[1])
                obox(C, r_, -TH_, TH_, -2 * TH_, -RD - 0.4, z0 + 0.15, z0 + CRS - 1.0, STEEL[2])
            top = TCO * CRS
            # flood mast + beacon on every tower; floods wash the tower faces (lit toon: floodlit towers)
            tube(A["metal"], (cx, cy, top), (cx, cy, top + 16.0), 0.45, (0.12, 0.12, 0.13), n=6)
            box(A["small"], cx - 0.6, cy - 0.6, top + 16.0, cx + 0.6, cy + 0.6, top + 17.0, RED, 12.0)
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                K.add_light("tflood_%d_%d_%d_%d" % (sx, sy, dx, dy), "SPOT", (cx + dx * (TH_ + 9), cy + dy * (TH_ + 9), 2.0),
                            LH["flood_w"] * 0.5, YW, aim=(cx + dx * TH_, cy + dy * TH_, top * 0.7), size=1.0, spot=55,
                            blend=0.5, group="corp")
            # searchlight beams leaning out on the diagonal (Meridian's mast lights: cold)
            hooks["beams"].append(((cx + sx * 2, cy + sy * 2, top + 15.0), (sx * 0.30, sy * 0.30, 1.0), YC,
                                   HP_beam(K)["power"], HP_beam(K)["cone"]))
            # orange banners with a white stripe on the outward faces (round 27 readability kit)
            for (fx, fy) in ((sx, 0), (0, sy)):
                bx, by = cx + fx * (TH_ + 0.25), cy + fy * (TH_ + 0.25)
                rb = dict(o=(bx, by, 0.0), n=(float(fx), float(fy)))
                obox(A["rough"], rb, -2.2, 2.2, 0.0, 0.15, top - 20.0, top - 2.0, (0.55, 0.12, 0.012))
                obox(A["rough"], rb, -0.5, 0.5, 0.15, 0.2, top - 20.0, top - 2.0, (0.7, 0.7, 0.68))
    log("towers")

    # ------------------------------------------------------------ the moat (W, S, E), the yard floor, the gate
    mw, mg = CP["moat"]["w"], CP["moat"]["gap"]
    for side in ("W", "S", "E"):
        rec = wall_frame(side)
        L = (TC[1] + TH_ + mg + mw) if side in ("W", "E") else (TC[0] + TH_ + mg + mw)
        d0 = (TH_ - (WX - TC[0]) if side in ("W", "E") else TH_ - (WY - TC[1])) + mg
        obox(A["ground"], rec, -L, L, d0, d0 + mw, -2.5, -2.4, (0.02, 0.025, 0.03), k=1.0)
        obox(A["rough"], rec, -L, L, d0 - 0.6, d0, -2.5, 0.3, (0.12, 0.12, 0.12))
        obox(A["rough"], rec, -L, L, d0 + mw, d0 + mw + 0.6, -2.5, 0.3, (0.12, 0.12, 0.12))
        uu = -L
        while uu < L:                                 # the moat's lit edge (small lights, warm)
            oquad(A["small"], rec, d0 + mw + 0.62, uu, 0.05, uu + 0.6, 0.25, HAZ, 3.0)
            uu += 9.0
    box(A["ground"], -WX, -WY, 0.0, WX, WY, 0.02, (0.25, 0.26, 0.27), k=1.0)
    # the gatehouse: portcullis glow, red gate lamps, the container drawbridge on chains
    gr = dict(o=(-WX, gate_u, 0.0), n=(-1.0, 0.0))
    obox(C, gr, -6.0, 6.0, -RD, 0.6, CRS - 1.0, CRS + 2.0, STEEL[3])
    oquad(A["trim"], gr, -RD * 0.5, -4.5, 0.0, 4.5, CRS - 1.2, (1.0, 0.45, 0.12), 2.4)
    for q in range(7):
        obox(A["metal"], gr, -4.2 + q * 1.4, -4.0 + q * 1.4, -1.2, -0.9, 0.0, CRS - 1.2, (0.08, 0.08, 0.09))
    for s_ in (-1, 1):
        oquad(A["small"], gr, 0.65, s_ * 5.2 - 0.4, CRS - 0.4, s_ * 5.2 + 0.4, CRS + 0.4, RED, 14.0)
        tube(A["metal"], rf(gr, 0.6, s_ * 4.5, CRS + 1.5), rf(gr, mw + mg + 8.0, s_ * 4.5, 0.6), 0.12, (0.2, 0.2, 0.2), n=4)
    obox(C, gr, -4.5, 4.5, 0.6, mw + mg + 9.0, 0.0, 0.6, STEEL[0])
    K.add_light("gate", "POINT", rf(gr, 4.0, 0.0, 4.0), 900.0, (1.0, 0.5, 0.2), size=1.0, group="corp")
    sx_, sy_ = CP["start"]
    box(A["rough"], sx_ - 4, sy_ - 3, 0, sx_ + 4, sy_ + 3, 4.4, (0.2, 0.2, 0.21))
    box(A["trim"], sx_ - 4.4, sy_ - 3.2, 1.4, sx_ - 3.4, sy_ - 2.8, 2.8, (0.55, 1.0, 0.0), 6.0)
    K.add_light("hack", "POINT", (sx_ - 4.6, sy_ - 3.6, 2.0), 120.0, (0.55, 1.0, 0.0), size=0.3, group="start")
    log("moat, gate")

    # ------------------------------------------------------------ the rail yard (north): tracks, sleepers, signals
    sr = random.Random(5322)
    for ty in CP["track_y"]:
        for s_ in (-0.9, 0.9):
            box(A["metal"], -420, ty + s_ - 0.12, 0.0, 420, ty + s_ + 0.12, 0.45, (0.35, 0.33, 0.32))
        x = -420.0
        while x < 420:
            box(A["rough"], x, ty - 1.6, -0.02, x + 0.5, ty + 1.6, 0.18, (0.09, 0.08, 0.075))
            x += 1.6
        box(A["ground"], -420, ty - 2.4, -0.03, 420, ty + 2.4, 0.0, (0.10, 0.10, 0.10), k=0.0)
    for x in (-200.0, -110.0, 110.0, 200.0):
        tube(A["metal"], (x, CP["track_y"][0] - 3.5, 0), (x, CP["track_y"][0] - 3.5, 7.0), 0.18, (0.1, 0.1, 0.1), n=5)
        box(A["small"], x - 0.35, CP["track_y"][0] - 3.85, 6.2, x + 0.35, CP["track_y"][0] - 3.5, 6.9,
            (0.1, 1.0, 0.35) if sr.random() < 0.6 else RED, 10.0)
    # the parked train on the siding (dressing): a loco + 6 closed container cars
    ty = CP["track_y"][1]
    x = 150.0
    for k in range(7):
        r_ = dict(o=(x, ty + 1.6, 0.0), n=(0.0, 1.0))
        obox(A["metal"], r_, -8.0, 8.0, -3.2, 0.0, 0.8, 2.2, (0.08, 0.08, 0.085))
        if k == 0:
            obox(STRIPE, r_, -7.5, 7.5, -3.2, 0.0, 2.2, 7.5, (0.55, 0.14, 0.02))
            oquad(A["small"], r_, 0.05, 6.0, 4.5, 7.4, 5.4, (1.0, 0.9, 0.7), 8.0)
        else:
            container(r_, -7.5, 7.5, -3.2, 0.0, 2.2, 8.6)
        x += 17.0
    # yard container stacks (dressing, seeded, clear of the control tower, the crane path and the route links)
    yr = random.Random(5321)
    for (gx, gy) in ((-50, -30), (-50, -8), (-28, -30), (-28, 20), (-50, 20), (60, -30), (60, -8)):
        n_ = yr.randint(1, 3)
        r_ = dict(o=(gx, gy, 0.0), n=(0.0, 1.0))
        for c in range(n_):
            container(r_, -7.0, 7.0, -5.0, 5.0, c * CRS * 0.95, c * CRS * 0.95 + 8.4)
    log("rail yard")

    # ------------------------------------------------------------ MANIFEST CONTROL (the server tower)
    cx, cy, hf, H = CTL["c"][0], CTL["c"][1], CTL["half"], CTL["h"]
    vz0 = H - CP["target_h"]
    face = dict(o=(cx, cy + hf, 0.0), n=(0.0, 1.0))
    room_us = [(G.ROOM[i]["o"][0] - cx, G.ROOM[i]["o"][2]) for i in ("m1", "m2")]
    core = hf - RD
    obox(A["civic"], face, -core, core, -2 * hf + RD, -RD, 0.0, vz0, (0.10, 0.11, 0.12))     # the core block
    for (fx, fy) in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        fr_ = dict(o=(cx + fx * hf, cy + fy * hf, 0.0), n=(float(fx), float(fy)))
        z = 0.0
        fl = 0
        while z < vz0 - 0.5:
            z1 = min(z + 7.0, vz0)
            cutset = [ru for ru in room_us if (fx, fy) == (0, 1) and z < ru[1] + RH + 0.5 and z1 > ru[1] - 0.5]
            # glass curtain with mullions + floor slab (steel); north face: room openings cut through the floors
            segs = [(-hf, hf)]
            for (ru, rz) in cutset:
                segs = [s for s0 in segs for s in ((s0[0], min(s0[1], ru - RW / 2 - 0.3)), (max(s0[0], ru + RW / 2 + 0.3), s0[1]))
                        if s[1] - s[0] > 0.3]
            for (s0, s1) in segs:
                obox(A["glass"], fr_, s0, s1, -RD, -0.2, z + 0.6, z1, (0.012, 0.022, 0.03))
                obox(A["metal"], fr_, s0, s1, -RD, 0.25, z, z + 0.6, (0.14, 0.14, 0.15))
                uu = s0
                while uu < s1 - 0.4:
                    obox(A["metal"], fr_, uu, uu + 0.22, -0.2, 0.22, z + 0.6, z1, (0.16, 0.16, 0.17))
                    uu += 2.4
                # office light bands behind the glass (big layer: building light), seeded per floor
                if rr.random() < 0.7:
                    oquad(A["trim"], fr_, -0.6, s0 + 0.3, z + 4.6, s1 - 0.3, z + 5.2, YC if rr.random() < 0.6 else YW,
                          LH["slit_k"] * rr.uniform(0.6, 1.4))
            z = z1
            fl += 1
    # the vault on the roof: open all round, the server core (red rings), the crown + the MERIDIAN FREIGHT sign
    box(A["civic"], cx - hf, cy - hf, vz0 - 0.4, cx + hf, cy + hf, vz0, (0.12, 0.12, 0.13))
    for (sx, sy) in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        box(A["metal"], cx + sx * hf - (2 if sx > 0 else 0), cy + sy * hf - (2 if sy > 0 else 0), vz0,
            cx + sx * hf + (0 if sx > 0 else 2), cy + sy * hf + (0 if sy > 0 else 2), H, (0.1, 0.1, 0.11))
    box(A["civic"], cx - hf, cy - hf, H, cx + hf, cy + hf, H + 2.0, (0.12, 0.12, 0.13))
    emv = K.ROOM_EMIT.setdefault("srv", Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"]))
    tube(A["metal"], (cx, cy, vz0), (cx, cy, H), 3.2, (0.08, 0.08, 0.1), n=16)
    for k_ in range(7):
        zz = vz0 + 1.0 + k_ * 1.25
        tube(emv, (cx, cy, zz), (cx, cy, zz + 0.25), 3.3, (1.0, 0.22, 0.08), 6.0, n=24)
    sr2 = random.Random(77)
    for (fx, fy) in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        fr_ = dict(o=(cx + fx * hf, cy + fy * hf, 0.0), n=(float(fx), float(fy)))
        for s_ in (-1, 1):
            obox(A["metal"], fr_, s_ * 8.0 - 0.8, s_ * 8.0 + 0.8, -9.0, -5.0, vz0, vz0 + 7.5, (0.1, 0.1, 0.12))
            for led in range(9):
                lz = vz0 + 0.8 + led * 0.72
                oquad(emv, fr_, -4.98, s_ * 8.0 - 0.6, lz, s_ * 8.0 - 0.6 + 0.35 + sr2.random() * 0.8, lz + 0.12,
                      (1.0, 0.18 + 0.4 * sr2.random(), 0.05), 5.0)
        oquad(A["trim"], fr_, 0.06, -hf, H + 0.6, hf, H + 0.9, YW, LH["trim_k"])
    # the crown sign: MERIDIAN on the north and west faces (orange, the corp's one big orange mark)
    STEN = {"M": ["10001", "11011", "10101", "10001", "10001"], "E": ["1111", "1000", "1110", "1000", "1111"],
            "R": ["1110", "1001", "1110", "1010", "1001"], "I": ["111", "010", "010", "010", "111"],
            "D": ["1110", "1001", "1001", "1001", "1110"], "A": ["0110", "1001", "1111", "1001", "1001"],
            "N": ["1001", "1101", "1011", "1001", "1001"]}
    for (fx, fy) in ((0, 1), (-1, 0)):
        fr_ = dict(o=(cx + fx * (hf + 0.3), cy + fy * (hf + 0.3), 0.0), n=(float(fx), float(fy)))
        cell = 0.66
        word = "MERIDIAN"
        wl = sum((len(STEN[ch][0]) + 1) * cell for ch in word)
        uu = -wl / 2
        z0 = H + 3.0
        obox(A["metal"], fr_, -wl / 2 - 1, wl / 2 + 1, -0.3, 0.0, H + 2.0, z0 + 5 * cell + 1.0, (0.05, 0.05, 0.05))
        for ch in word:
            gph = STEN[ch]
            for row, bits in enumerate(gph):
                for cix, bit in enumerate(bits):
                    if bit == "1":
                        # the frame tangent points screen-LEFT (seen from outside): letters run along -u
                        oquad(A["trim"], fr_, 0.05, -(uu + (cix + 1) * cell - cell * 0.15), z0 + (4 - row) * cell,
                              -(uu + cix * cell), z0 + (5 - row) * cell - cell * 0.15, ORANGE, 6.0 * LH["sign_k"] * 4)
            uu += (len(gph[0]) + 1) * cell
    K.add_light("ctl_wash", "SPOT", (cx, cy + hf + 40, 2.0), LH["flood_w"], YW, aim=(cx, cy + hf, H * 0.6), size=1.5,
                spot=50, blend=0.6, group="corp")
    hooks["beams"].append(((cx, cy, H + 2.5), (0.0, 0.0, 1.0), YC, HP_beam(K)["power"] * 1.4, HP_beam(K)["cone"] * 1.4))
    log("control tower")

    # ------------------------------------------------------------ static rooms
    for i in G.NODES:
        if i in ("start", "srv", "car", "hook"):
            continue
        K.room_shell(i, G.ROOM[i])

    # ------------------------------------------------------------ links: catwalks, ladders, stairs, the skyway, gangways
    def walk(path, w=2.2, col=(0.32, 0.33, 0.35), led=True):
        for p, q in zip(path, path[1:]):
            p, q = Vector(p), Vector(q)
            d = q - p
            hz = math.hypot(d.x, d.y)
            if hz < 0.3 and abs(d.z) > 0.5:          # ladder (twin rails + rungs) with a hazard cage
                side = Vector((1.0, 0.0, 0.0)) if abs(p.x - q.x) < 0.01 and abs(p.y) > abs(p.x) * 0 else Vector((0, 1, 0))
                for s_ in (-0.5, 0.5):
                    tube(A["metal"], p + side * s_ + Vector((0, 0, -1.6)), q + side * s_ + Vector((0, 0, -0.6)), 0.08,
                         (0.6, 0.5, 0.15), n=4)
                nr = int(abs(d.z) / 0.8)
                for k in range(nr + 1):
                    c_ = p.lerp(q, k / max(1, nr)) + Vector((0, 0, -1.6))
                    tube(A["metal"], c_ - side * 0.5, c_ + side * 0.5, 0.05, (0.6, 0.5, 0.15), n=4)
                continue
            K.seg_box(A["metal"], p + Vector((0, 0, -1.55)), q + Vector((0, 0, -1.55)), w, 0.2, col)
            if led and hz > 0.5:
                K.seg_box(A["small"], p + Vector((0, 0, -1.5)), q + Vector((0, 0, -1.5)), 0.12, 0.05, HAZ, 2.5)
            # handrail on the outside
            nrm = Vector((-d.y, d.x, 0.0)).normalized() * (w / 2) if hz > 0.01 else Vector((0, 0, 0))
            for s_ in (1,):
                tube(A["metal"], p + nrm * s_ + Vector((0, 0, -0.5)), q + nrm * s_ + Vector((0, 0, -0.5)), 0.06,
                     (0.5, 0.5, 0.52), n=4)

    W = G.WALK_MID
    for (a, b_) in G.PATH:
        pth = G.edge_path(a, b_)
        if G.edge_type(a, b_) == "skyway":
            for p, q in zip(pth, pth[1:]):
                K.seg_box(A["metal"], Vector(p) + Vector((0, 0, -1.55)), Vector(q) + Vector((0, 0, -1.55)), 3.2, 0.4,
                          (0.2, 0.2, 0.21))
                K.seg_box(A["glass"], Vector(p) + Vector((0, 0, 2.2)), Vector(q) + Vector((0, 0, 2.2)), 3.2, 0.1,
                          (0.02, 0.03, 0.035))
                K.seg_box(A["trim"], Vector(p) + Vector((0, 0, 2.15)), Vector(q) + Vector((0, 0, 2.15)), 0.3, 0.05, YC,
                          LH["trim_k"])
            # skyway pylons
            for p in pth[1:-1]:
                tube(A["metal"], (p[0], p[1], 0.0), (p[0], p[1], p[2] - 1.6), 0.6, (0.12, 0.12, 0.13), n=6)
            continue
        if a == "start":
            continue
        walk(pth)
    # boarding gear (static): a ladder down the wall by n1, the tower ladder by t2, the gangway by n3, the landing at m2
    walk(G.edge_path("n1", "car", 6.0)[:3])
    walk(G.edge_path("car", "t2", 7.0)[-3:])
    p = G.edge_path("n3", "hook", 7.0)
    walk(p[:3])
    p2 = G.edge_path("hook", "m2", 9.0)
    walk(p2[-2:], w=3.0)
    log("links")

    # ------------------------------------------------------------ the ship-to-shore crane (static frame) + movers
    # portal legs inside the yard behind the north wall, a tall A-frame, the boom out over the track (forestays) and
    # the backreach over the yard (backstays): the landmark silhouette (iconic at OVERVIEW)
    cr = CP["crane"]
    xc, lx, (ly0, ly1), cz, (by0, by1) = cr["x"], cr["legs_x"], cr["legs_y"], cr["z"], cr["boom_y"]
    apex = cr.get("apex", 96.0)
    CRANE = (0.34, 0.10, 0.045)
    for ly in (ly0, ly1):
        for s_ in (-1, 1):
            x = xc + s_ * lx
            box(STRIPE, x - 1.1, ly - 1.1, 0.0, x + 1.1, ly + 1.1, cz - 3.0, CRANE)
            for q in range(6):                          # hazard bands at the foot
                box(STRIPE, x - 1.15, ly - 1.15, q * 1.2, x + 1.15, ly + 1.15, q * 1.2 + 0.6,
                    (0.9, 0.55, 0.02) if q % 2 == 0 else (0.02, 0.02, 0.02))
        box(STRIPE, xc - lx - 1.1, ly - 1.1, cz - 6.0, xc + lx + 1.1, ly + 1.1, cz - 3.0, CRANE)
        box(STRIPE, xc - lx - 1.1, ly - 1.1, 22.0, xc + lx + 1.1, ly + 1.1, 24.0, CRANE)
    for s_ in (-1, 1):
        x = xc + s_ * lx
        box(STRIPE, x - 0.8, ly0, cz - 6.0, x + 0.8, ly1, cz - 4.0, CRANE)
        tube(A["metal"], (x, ly0, 24.0), (x, ly1, cz - 6.0), 0.4, CRANE, n=5)
    for s_ in (-1, 1):                                  # the two boom girders (backreach .. boom tip)
        x = xc + s_ * (lx - 4.0)
        box(STRIPE, x - 1.0, by0, cz - 3.0, x + 1.0, by1, cz, CRANE)
        box(A["trim"], x - 1.05, by0, cz - 0.55, x + 1.05, by1, cz - 0.25, pal("work"), LH["boom_k"])
        box(A["trim"], x - 1.05, by0, cz - 3.25, x + 1.05, by1, cz - 2.95, YC, LH["trim_k"] * 0.6)
        # the A-frame: from the portal top up to the apex, stays to the boom tip and the backreach
        ym = (ly0 + ly1) / 2
        tube(A["metal"], (xc + s_ * lx, ly0, cz), (xc + s_ * (lx - 4.0), ym, apex), 0.7, CRANE, n=6)
        tube(A["metal"], (xc + s_ * lx, ly1, cz), (xc + s_ * (lx - 4.0), ym, apex), 0.7, CRANE, n=6)
        tube(A["metal"], (x, ym, apex), (x, by1, cz), 0.22, (0.35, 0.35, 0.35), n=4)
        tube(A["metal"], (x, ym, apex), (x, by1 - (by1 - ym) * 0.45, cz), 0.22, (0.35, 0.35, 0.35), n=4)
        tube(A["metal"], (x, ym, apex), (x, by0, cz), 0.22, (0.35, 0.35, 0.35), n=4)
        y = by0
        while y <= by1:
            box(A["small"], x - 0.3, y - 0.3, cz, x + 0.3, y + 0.3, cz + 0.6, RED, 8.0)
            y += 16.0
    box(STRIPE, xc - lx + 2.0, (ly0 + ly1) / 2 - 1.0, apex, xc + lx - 2.0, (ly0 + ly1) / 2 + 1.0, apex + 1.6, CRANE)
    for s_ in (-1, 1):                                  # lit truss edges up the A-frame (orange neon)
        for ly in (ly0, ly1):
            tube(A["trim"], (xc + s_ * (lx + 0.8), ly, cz), (xc + s_ * (lx - 3.2), (ly0 + ly1) / 2, apex), 0.12,
                 pal("work"), LH["boom_k"], n=4)
        for ly in (ly0, ly1):                           # leg edge lines
            tube(A["trim"], (xc + s_ * (lx + 1.2), ly + 1.2, 6.0), (xc + s_ * (lx + 1.2), ly + 1.2, cz - 3.0), 0.1,
                 pal("work"), LH["boom_k"] * 0.7, n=4)
    for (yy, zz) in ((by1, cz + 0.6), (by0, cz + 0.6), ((ly0 + ly1) / 2, apex + 2.6)):   # white warning strobes
        box(A["small"], xc - 0.7, yy - 0.7, zz, xc + 0.7, yy + 0.7, zz + 0.8, (1.0, 1.0, 1.0), 25.0)
    box(A["small"], xc - 0.6, (ly0 + ly1) / 2 - 0.6, apex + 1.6, xc + 0.6, (ly0 + ly1) / 2 + 0.6, apex + 2.6, RED, 14.0)
    box(STRIPE, xc - lx - 3, ly1 + 2, cz - 7.0, xc - lx + 3, ly1 + 8, cz - 3.0, (0.25, 0.25, 0.27))   # the cab
    box(A["trim"], xc - lx - 3.05, ly1 + 7.95, cz - 6.5, xc - lx + 3.05, ly1 + 8.05, cz - 4.0, YW, 3.0)
    # uplights at the leg feet wash the portal + A-frame (the landmark reads at OVERVIEW)
    for ly in (ly0, ly1):
        for s_ in (-1, 1):
            K.add_light("crane_up_%d_%d" % (ly, s_), "SPOT", (xc + s_ * (lx + 5.0), ly + 4.0, 0.5), LH["flood_w"] * 0.35,
                        YW, aim=(xc + s_ * lx, ly, cz), size=0.8, spot=28, blend=0.5, group="corp")
    K.add_light("crane_apex", "SPOT", (xc, (ly0 + ly1) / 2 + 40.0, cz + 4.0), LH["flood_w"] * 0.5, YC,
                aim=(xc, (ly0 + ly1) / 2, apex - 6.0), size=1.0, spot=30, blend=0.6, group="corp")
    # floods under the boom, aimed down at the wall / the track / the yard (cold)
    for (yy, aim_y) in ((by1 - 6.0, WY + 14.0), (WY + 6.0, WY), (ly0, cy + hf + 4)):
        K.add_light("crane_flood_%d" % yy, "SPOT", (xc, yy, cz - 4.0), LH["flood_w"] * 0.8, YC, aim=(xc, aim_y, 8.0),
                    size=1.0, spot=58, blend=0.6, group="corp")
    # the trolley (mover): rides the girders over the hook
    tr = K.mover("trolley")
    box(tr["accs"]["rough"], -lx + 2.0, -3.0, -1.0, lx - 2.0, 3.0, 2.5, (0.18, 0.18, 0.2))
    box(tr["accs"]["small"], -1.0, -3.05, 0.2, 1.0, -2.95, 1.0, HAZ, 10.0)
    box(tr["accs"]["trim"], -lx + 2.0, -3.05, 1.2, lx - 2.0, -2.95, 1.6, (1.0, 0.9, 0.7), 3.0)
    hs_ = K.add_light("hook_spot", "SPOT", (0.0, 0.0, -1.5), LH["hook_spot_w"], (1.0, 0.92, 0.8), aim=(0.0, 0.0, -50.0),
                      size=0.5, spot=24, blend=0.4, group="corp")
    hooks["mover_lights"]["trolley"] = [(hs_, (0.0, 0.0, -1.5))]
    # the hook container (mover) = the HOOK room + spreader bar + hazard rim + a rotating amber beacon
    hk = K.mover("hook")
    rec0 = dict(o=(0.0, 0.0, 0.0), n=(0.0, 1.0), w=RW, h=RH, d=RD)
    K.mover_room("hook", "hook", rec0)
    obox(hk["accs"]["rough"], rec0, -RW / 2 - 0.5, RW / 2 + 0.5, -RD - 0.4, 0.4, RH + 0.3, RH + 1.0, (0.12, 0.12, 0.12))
    obox(hk["accs"]["struct"], rec0, -RW / 2 - 0.6, RW / 2 + 0.6, -RD - 0.6, 0.6, RH + 1.0, RH + 1.9, (0.45, 0.28, 0.02))
    for uu in range(-7, 7, 2):
        oquad(hk["accs"]["trim"], rec0, 0.62, uu, RH + 1.05, uu + 1.0, RH + 1.85, (1.0, 0.55, 0.02), 1.2)
    obox(hk["accs"]["small"], rec0, -0.5, 0.5, -RD / 2 - 0.5, -RD / 2 + 0.5, RH + 1.9, RH + 2.7, HAZ, 14.0)
    hb = K.add_light("hook_beacon", "POINT", (0.0, -RD / 2, RH + 3.2), LH["beacon_w"], HAZ, size=0.4, group="corp",
                     shadow=False)
    hooks["mover_lights"]["hook"] = [(hb, (0.0, -RD / 2, RH + 3.2))]
    # the cables (scaled per frame from the trolley to the spreader)
    cab = Acc("cable", K.M["metal"], 6, K.COLL["movers"])
    for (dx, dy) in ((-4.0, -2.0), (4.0, -2.0), (-4.0, -8.0), (4.0, -8.0)):
        tube(cab, (dx, dy, 0.0), (dx, dy, 1.0), 0.12, (0.2, 0.2, 0.2), n=4)
    hooks["accs"]["cable"] = cab
    # the train (mover): CAR room on its flatcar, the loco (east end, headlight), 3 more cars with closed containers
    trn = K.mover("train")
    recc = dict(o=(0.0, 0.0, 0.0), n=(0.0, 1.0), w=RW, h=RH, d=RD)
    deck = -CP["track_y"][0] * 0 + 2.6

    def flatcar(x0):
        obox(trn["accs"]["metal"], dict(o=(x0, 0.0, 0.0), n=(0.0, 1.0)), -8.2, 8.2, -RD - 0.2, 0.2, -2.6 + 0.8, -0.05,
             (0.07, 0.07, 0.075))
        for wx in (-6.0, -4.0, 4.0, 6.0):
            for wy in (-RD + 0.6, -0.6):
                tube(trn["accs"]["metal"], (x0 + wx, wy, -2.0), (x0 + wx, wy + (0.3 if wy > -5 else -0.3), -2.0), 0.7,
                     (0.04, 0.04, 0.04), n=8)
        for q in range(7):                              # running lights along the car (both sides)
            for wy in (0.25, -RD - 0.25):
                box(trn["accs"]["trim"], x0 - 7.0 + q * 2.3, wy - 0.1, -1.0, x0 - 6.4 + q * 2.3, wy + 0.1, -0.6,
                    (1.0, 0.55, 0.1), LH["train_run_k"])
        for wx in (-6.0, 6.0):                          # wheel sparks (hot points at the rails)
            box(trn["accs"]["small"], x0 + wx - 0.25, -0.35, -2.55, x0 + wx + 0.25, 0.1, -2.35, (1.0, 0.6, 0.15), 30.0)
    rec_room = dict(o=(0.0, 0.0, 0.0), n=(0.0, 1.0), w=RW, h=RH, d=RD)
    K.mover_room("car", "train", rec_room)
    flatcar(0.0)
    obox(trn["accs"]["struct"], recc, -RW / 2 - 0.4, RW / 2 + 0.4, -RD - 0.3, 0.3, RH, RH + 0.5, (0.45, 0.28, 0.02))
    for uu in range(-7, 7, 2):
        oquad(trn["accs"]["trim"], recc, 0.32, uu, RH + 0.02, uu + 1.0, RH + 0.48, (1.0, 0.55, 0.02), 1.2)
    obox(trn["accs"]["small"], recc, -0.5, 0.5, -RD / 2 - 0.5, -RD / 2 + 0.5, RH + 0.5, RH + 1.3, HAZ, 14.0)
    tb = K.add_light("car_beacon", "POINT", (0.0, -RD / 2, RH + 1.8), LH["beacon_w"], HAZ, size=0.4, group="corp", shadow=False)
    hooks["mover_lights"]["train"] = [(tb, (0.0, -RD / 2, RH + 1.8))]
    for k in (1, 2):
        flatcar(-17.0 * k)
        r_ = dict(o=(-17.0 * k, 0.0, 0.0), n=(0.0, 1.0))
        obox(trn["accs"]["rough"], r_, -7.5, 7.5, -RD + 0.2, -0.2, 0.0, 8.4, STEEL[k + 1])
    # the loco (east end)
    lr_ = dict(o=(19.0, 0.0, 0.0), n=(0.0, 1.0))
    flatcar(19.0)
    obox(trn["accs"]["struct"], lr_, -7.6, 7.6, -RD + 0.5, -0.5, 0.0, 7.2, (0.5, 0.16, 0.02))
    for q in range(5):
        oquad(trn["accs"]["trim"], lr_, -0.48, -7.0 + q * 3.0, 1.0, -6.0 + q * 3.0, 2.0, (1.0, 0.75, 0.05), 0.8)
    oquad(trn["accs"]["small"], dict(o=(26.7, -RD / 2, 0.0), n=(1.0, 0.0)), 0.02, -2.0, 4.6, 2.0, 5.6, (1.0, 0.92, 0.75), 10.0)
    hl = K.add_light("loco_head", "SPOT", (27.0, -RD / 2, 5.0), 4000.0, (1.0, 0.9, 0.75), aim=(80.0, -RD / 2, 1.0),
                     size=0.5, spot=40, blend=0.5, group="corp", shadow=False)
    hooks["mover_lights"]["train"].append((hl, (27.0, -RD / 2, 5.0)))
    hb_ = K.add_light("loco_beam", "SPOT", (27.2, -RD / 2, 5.0), LH["head_w"], (1.0, 0.9, 0.75), aim=(140.0, -RD / 2, 2.0),
                      size=0.0, spot=9, blend=0.4, group="beam", shadow=False, receivers=K.COLL["media"])
    hooks["mover_lights"]["train"].append((hb_, (27.2, -RD / 2, 5.0)))
    K.add_light("rail_glow", "AREA", (-30.0, CP["track_y"][0], 9.0), LH["sodium_w"] * 6, pal("sodium"),
                aim=(-30.0, CP["track_y"][0], 0.0), size=180.0, size_y=6.0, group="corp")
    # ============================================================ THE LANDMARK RIG (designer audit 2026-10-15):
    # the compound is the hero: keyed, rimmed and separated from the city by lighting (not exposure)
    SOD, WORK = pal("sodium"), pal("work")
    rg = random.Random(5330)
    # 1. lit seams: a warm line under every container course on the route walls' outer faces + the towers (big layer)
    for side in ("W", "N", "E", "S"):
        rec = wall_frame(side)
        L = (TC[1] - TH_) if side in ("W", "E") else (TC[0] - TH_)
        kk = LH["seam_k"] * (1.0 if side in ("W", "N") else 0.55)
        for c in range(1, NC + 1):
            oquad(A["trim"], rec, 0.06, -L, c * CRS - 1.0, L, c * CRS - 0.82, WORK, kk)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx_, cy_ = sx * TC[0], sy * TC[1]
            for (fx, fy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rb = dict(o=(cx_ + fx * (TH_ + 0.05), cy_ + fy * (TH_ + 0.05), 0.0), n=(float(fx), float(fy)))
                for c in range(1, TCO + 1):
                    oquad(A["trim"], rb, 0.0, -TH_, c * CRS - 1.0, TH_, c * CRS - 0.8, WORK, LH["seam_k"] * 0.8)
    # 2. container logos: the MERIDIAN mark (orange panel + white stripe) on the outer face of every tower (big layer)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx_, cy_ = sx * TC[0], sy * TC[1]
            for (fx, fy) in ((sx, 0), (0, sy)):
                rb = dict(o=(cx_ + fx * (TH_ + 0.3), cy_ + fy * (TH_ + 0.3), 0.0), n=(float(fx), float(fy)))
                z_ = 2 * CRS + 1.0
                oquad(A["trim"], rb, 0.0, -6.0, z_, 6.0, z_ + 6.0, ORANGE, LH["logo_k"])
                oquad(A["trim"], rb, 0.02, -6.0, z_ + 2.6, 6.0, z_ + 3.4, (1.0, 0.95, 0.9), LH["logo_k"] * 1.2)
    # 3. orange work lights along the walls (from the moat edge / the rail side) washing the containers
    for side in ("W", "N", "S", "E"):
        rec = wall_frame(side)
        L = (TC[1] - TH_) if side in ("W", "E") else (TC[0] - TH_)
        uu = -L + 8.0
        pw = LH["work_w"] * (1.0 if side in ("W", "N") else 0.5)
        while uu < L - 4:
            K.add_light("work_%s_%d" % (side, uu), "SPOT", rf(rec, 14.0, uu, 1.2), pw, WORK,
                        aim=rf(rec, 0.0, uu, 16.0), size=0.8, spot=70, blend=0.8, group="corp")
            uu += 18.0
    # 4. flood towers at the corners pointing inward (sodium), the keep gets the brightest wash
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = TCO * CRS + 16.0
            o_ = (sx * TC[0], sy * TC[1], top)
            K.add_light("ftower_%d_%d" % (sx, sy), "SPOT", o_, LH["tower_flood_w"], SOD,
                        aim=(sx * TC[0] * 0.2, sy * TC[1] * 0.2, 0.0), size=1.5, spot=75, blend=0.6, group="corp")
            box(A["trim"], o_[0] - 1.6, o_[1] - 1.6, top - 1.2, o_[0] + 1.6, o_[1] + 1.6, top - 0.2, SOD, 8.0)
    cx_, cy_, hf_ = CTL["c"][0], CTL["c"][1], CTL["half"]
    for (fx, fy) in ((0, 1), (-1, 0), (1, 0), (0, -1)):
        o_ = (cx_ + fx * (hf_ + 30.0), cy_ + fy * (hf_ + 30.0), 1.0)
        K.add_light("keep_wash_%d_%d" % (fx, fy), "SPOT", o_, LH["keep_w"], SOD if (fx + fy) % 2 else WORK,
                    aim=(cx_ + fx * hf_, cy_ + fy * hf_, CTL["h"] * 0.55), size=2.0, spot=42, blend=0.5, group="corp")
    # 5. sodium yard lights on poles (yard + rail yard), their pools on the wet ground
    for (px_, py_) in ((-40, 0), (40, -30), (-40, -38), (60, 20), (-60, CP["track_y"][0] - 6), (-20, CP["track_y"][0] - 6),
                       (40, CP["track_y"][0] - 6), (100, CP["track_y"][0] - 6), (-120, CP["track_y"][0] - 6)):
        tube(A["metal"], (px_, py_, 0.0), (px_, py_, 14.0), 0.2, (0.1, 0.1, 0.1), n=5)
        box(A["small"], px_ - 0.8, py_ - 0.4, 13.6, px_ + 0.8, py_ + 0.4, 14.0, SOD, 12.0)
        K.add_light("sod_%d_%d" % (px_, py_), "SPOT", (px_, py_, 13.5), LH["sodium_w"], SOD, aim=(px_, py_, 0.0),
                    size=0.6, spot=95, blend=0.9, group="corp")
    # 6. the rails: a sodium glint along both rails of the through track near the fortress
    for s_ in (-0.9, 0.9):
        box(A["trim"], -150, CP["track_y"][0] + s_ - 0.06, 0.45, 150, CP["track_y"][0] + s_ + 0.06, 0.5, SOD, LH["rail_k"])
    # 7. the moat and the drawbridge: lit water edge + gate lamps already; an orange glow under the drawbridge
    K.add_light("bridge_glow", "AREA", (-WX - 12.0, CP["gate_u"], -1.5), LH["work_w"] * 0.4, WORK,
                aim=(-WX - 12.0, CP["gate_u"], 10.0), size=10.0, size_y=6.0, group="corp")
    # 8. rim: the city glow behind the compound (south of it, low) grazes its back edges; the fog bank behind it,
    #    lit from below, makes the silhouette
    import bpy
    RIMRX = bpy.data.collections.new("rim_rx")             # the rim grazes the landmark only (not the ground)
    for k, (rx, col_) in enumerate(((-90.0, "district_a"), (90.0, "district_b"))):
        K.add_light("rim_%d" % k, "AREA", (rx, -230.0, 30.0), LH["rim_w"], pal(col_), aim=(rx * 0.3, 0.0, 30.0),
                    size=120.0, size_y=40.0, group="corp", shadow=False, receivers=RIMRX)

    def post_build(OBJ):
        for name, ob in OBJ.items():
            if ob is not None and any(c.name in ("compound", "movers") for c in ob.users_collection):
                RIMRX.objects.link(ob)
    hooks["post_build"] = post_build
    # the bank behind the compound is the main fog lit from below by these fills (a second volume box doubled the
    # render time; removed after the first Cycles test)
    x0, y0, z0_, x1, y1, z1_ = LH["bank_box"]
    for k in range(5):
        gx = x0 + (x1 - x0) * (k + 0.5) / 5
        K.add_light("bankfill_%d" % k, "AREA", (gx, (y0 + y1) / 2, 0.5), LH["bank_fill_w"], YC if k % 2 else SOD,
                    aim=(gx, (y0 + y1) / 2, 40.0), size=50.0, size_y=40.0, group="corp", shadow=False,
                    receivers=K.COLL["media"])
    log("crane, train")

    hooks["local_rec"] = lambda i: rec_room if i == "car" else rec0

    def apply(fr, ctx):
        mv = fr.get("movers") or {}
        hkp = mv.get("hook")
        if hkp:
            ob = ctx["OBJ"].get("cable")
            top = hkp[2] + RH + 1.9
            if ob is not None:
                ob.location = (hkp[0], hkp[1], top)
                ob.scale = (1.0, 1.0, max(0.5, cz - 3.0 - top))
        # mover beacons pulse (the hazard of a moving ride): energy by the mech phase
        k = fr.get("mech", {}).get("beacon", 1.0)
        for (lob, e0, grp) in ctx["LIGHTS"]:
            if lob.name in ("hook_beacon", "car_beacon"):
                lob.data.energy = e0 * k
    hooks["apply"] = apply
    return hooks


def HP_beam(K):
    return K.HZ["beams"]
