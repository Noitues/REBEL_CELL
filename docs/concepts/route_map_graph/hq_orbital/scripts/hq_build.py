"""HQ Orbital: the Blender build of the launch complex (called by the kit's hq_scene.py: build(K) -> hooks).
Revised 2026-10-15 (designer review): the antenna is a truss TOWER with decks and two enclosed elite rooms; the ROCKET
is the hero (risen out of the open doors at a circuit's sabotage, hacked bands lit per retarget); LAUNCH CONTROL on the
service gantry; key + rim light on the active room and its options; pad floods, rocket service lights, fog lit from
below; the launch cutscene props (the city target facility, the rocket in flight, its trail, the strike).

Placed by rule from hq_preset "compound" + hq_graph; seeds: 7320 (dish tilts), 7340 (strike debris).
"""
import math
import random


def build(K):
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, Acc, obox, oquad, tube, box = K.A, K.Acc, K.obox, K.oquad, K.tube, K.box
    Vector = K.Vector
    import bpy
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ("mv_", "prep_", "trail", "boom")}
    ICE, STEEL, CAUT, LAUNCH, MARK = pal("ice"), pal("steel"), pal("caution"), pal("launch"), pal("marker")
    HACK = (0.66, 1.0, 0.0)                           # the Cell's lime: a hacked panel
    PR, PH, SR = CP["podium_r"], CP["podium_h"], CP["silo_r"]
    RR, RD, RW, RH = CP["ring_r"], CP["room_d"], CP["room_w"], CP["room_h"]
    AN, RK = CP["antenna"], CP["rocket"]
    log = K.log

    def ring(acc, r0, r1, z0, z1, col, k=0.0, n=72, a0=0.0, a1=360.0, top=True, inner=True, cx=0.0, cy=0.0):
        for i in range(n):
            b0 = math.radians(a0 + (a1 - a0) * i / n)
            b1 = math.radians(a0 + (a1 - a0) * (i + 1) / n)
            o0, o1 = (cx + math.sin(b0) * r1, cy + math.cos(b0) * r1), (cx + math.sin(b1) * r1, cy + math.cos(b1) * r1)
            i0, i1 = (cx + math.sin(b0) * r0, cy + math.cos(b0) * r0), (cx + math.sin(b1) * r0, cy + math.cos(b1) * r0)
            acc.face([(o0[0], o0[1], z0), (o1[0], o1[1], z0), (o1[0], o1[1], z1), (o0[0], o0[1], z1)], col, k)
            if inner and r0 > 0:
                acc.face([(i1[0], i1[1], z0), (i0[0], i0[1], z0), (i0[0], i0[1], z1), (i1[0], i1[1], z1)], col, k)
            if top:
                acc.face([(i0[0], i0[1], z1), (o0[0], o0[1], z1), (o1[0], o1[1], z1), (i1[0], i1[1], z1)], col, k)

    # ------------------------------------------------------------ the podium + the silo (v2: a DARK pad, painted marks)
    # v1's pale pad deck, the emissive caution ring and the glowing shaft rings read as one yellow blob from above;
    # v2: dark wet concrete, every marking PAINT (no glow), the shaft glow only while the doors are open
    PAINT = Acc("pad_paint", K.M["rough"], 1, K.COLL["compound"])
    hooks["accs"]["pad_paint"] = PAINT
    WP, YP = (0.62, 0.63, 0.62), (0.55, 0.36, 0.02)      # white / yellow paint albedo
    ring(A["civic"], SR, PR, 0.0, PH, STEEL)
    ring(A["ground"], SR + 3.0, PR - 1.5, PH, PH + 0.02, LH["pad_albedo"], k=1.0, inner=False)
    ring(A["trim"], PR + 0.02, PR + 0.1, PH - 0.7, PH - 0.4, ICE, LH["trim_k"])
    ring(A["trim"], PR + 0.02, PR + 0.1, 0.4, 0.6, ICE, LH["trim_k"] * 0.5)
    for k in range(36):                               # the caution ring: painted yellow / black
        ring(PAINT, SR, SR + 2.6, PH, PH + 0.05, YP if k % 2 == 0 else (0.015, 0.015, 0.015), 0.0, n=2, a0=k * 10.0,
             a1=(k + 1) * 10.0, inner=False)
    ring(PAINT, SR + 6.0, SR + 7.0, PH + 0.02, PH + 0.05, WP, inner=False)      # the blast circle
    ring(PAINT, PR - 7.0, PR - 6.2, PH + 0.02, PH + 0.05, WP, inner=False)      # the pad edge line
    for a in (0.0, 90.0, 180.0, 270.0):                                           # the cross-hair (gaps for the rails)
        v = G.az_vec(a)
        if abs(v[0]) > 0.5:
            continue                                  # E / W: the door rails run there
        r0, r1 = SR + 8.5, PR - 8.5
        box(PAINT, min(v[0] * r0, v[0] * r1) - 0.6, min(v[1] * r0, v[1] * r1) - 0.0, PH + 0.02,
            max(v[0] * r0, v[0] * r1) + 0.6, max(v[1] * r0, v[1] * r1), PH + 0.05, WP)
    for k in range(4):                                # quadrant chevrons (yellow paint) pointing at the silo
        a = 45.0 + 90.0 * k
        v = G.az_vec(a)
        for q in range(3):
            r_ = PR - 14.0 - q * 5.0
            c_ = (v[0] * r_, v[1] * r_)
            tvec = (-v[1], v[0])
            for sgn in (-1, 1):
                p0 = (c_[0] + tvec[0] * sgn * 3.0, c_[1] + tvec[1] * sgn * 3.0)
                p1 = (c_[0] - v[0] * 2.4, c_[1] - v[1] * 2.4)
                K.seg_box(PAINT, Vector((p0[0], p0[1], PH + 0.05)), Vector((p1[0], p1[1], PH + 0.05)), 0.9, 0.03, YP)
    # LC-1 stencilled on the deck (south side, facing the gantry)
    STEN = {"L": ["100", "100", "100", "100", "111"], "C": ["111", "100", "100", "100", "111"], "-": ["000", "000", "111", "000", "000"],
            "1": ["010", "110", "010", "010", "111"]}
    cell = 1.6
    xw = -((3 + 1) * 4 - 1) * cell / 2
    for ch in "LC-1":
        for row, bits in enumerate(STEN[ch]):
            for cix, bit in enumerate(bits):
                if bit == "1":
                    x0_ = xw + cix * cell
                    y0_ = -(SR + 13.0) - row * cell
                    box(PAINT, x0_, y0_ - cell * 0.9, PH + 0.02, x0_ + cell * 0.9, y0_, PH + 0.05, WP)
        xw += 4 * cell
    # the door rails: fixed tracks east and west of the silo the leaves slide onto (the open state reads)
    for sx_ in (-1, 1):
        for yy in (-(SR + 1.0), (SR + 1.0)):
            box(A["metal"], sx_ * (SR + 1.0) if sx_ > 0 else -(2 * SR + 4.0), yy - 0.5, PH, sx_ * (2 * SR + 4.0) if sx_ > 0 else -(SR + 1.0),
                yy + 0.5, PH + 0.6, (0.2, 0.21, 0.23))
        box(A["civic"], sx_ * (2 * SR + 4.0) - 1.2, -(SR + 2.5), PH, sx_ * (2 * SR + 4.0) + 1.2, SR + 2.5, PH + 2.4, STEEL)
    # the shaft: dark walls; the launch glow rings belong to an object whose weight follows the doors (prep_shaft)
    SHG = Acc("prep_shaft", K.M["emit"], 1, K.COLL["compound"])
    hooks["accs"]["prep_shaft"] = SHG
    for zz in (1.0, 3.5, 6.0, 8.5):
        ring(SHG, SR - 0.1, SR, zz, zz + 0.4, LAUNCH, 3.0, top=False, inner=True)
    ring(A["rough"], 0.0, SR, -0.5, 0.0, (0.05, 0.05, 0.05), inner=False)
    # the door status: red lock lamps on the rim (SHUT), white-green lamps (OPEN)
    LKR = Acc("prep_lock_red", K.M["emit"], 1, K.COLL["compound"])
    LKG = Acc("prep_lock_open", K.M["emit"], 1, K.COLL["compound"])
    hooks["accs"]["prep_lock_red"] = LKR
    hooks["accs"]["prep_lock_open"] = LKG
    for k in range(12):
        a = 15.0 + 30.0 * k
        v = G.az_vec(a)
        r_ = SR + 3.6
        box(LKR, v[0] * r_ - 0.5, v[1] * r_ - 0.5, PH + 0.05, v[0] * r_ + 0.5, v[1] * r_ + 0.5, PH + 0.9, MARK, LH["marker_k"])
        box(LKG, v[0] * r_ - 0.5, v[1] * r_ - 0.5, PH + 0.05, v[0] * r_ + 0.5, v[1] * r_ + 0.5, PH + 0.9, (0.6, 1.0, 0.7),
            LH["marker_k"] * 0.7)
    sh = K.add_light("shaft", "POINT", (0.0, 0.0, 1.5), LH["shaft_w"], LAUNCH, size=6.0, group="mech", shadow=False)
    K.add_light("shaft_beam", "SPOT", (0.0, 0.0, 0.5), LH["shaft_beam_w"], LAUNCH, aim=(0.0, 0.0, 300.0), size=0.0,
                spot=9.0, blend=0.4, group="mech", shadow=False, receivers=K.COLL["media"])
    log("podium")

    # ------------------------------------------------------------ the doors (movers)
    for name, s_ in (("door_e", 1), ("door_w", -1)):
        # v2: heavy dark blast-door leaves (they slide onto the rails), painted chevrons pointing at the seam (no glow),
        # a thin ice seam line; the leaf's outer edge carries a raised beam so the leaf reads as a slab
        mv = K.mover(name)
        x0, x1 = (0.0, SR + 1.5) if s_ > 0 else (-(SR + 1.5), 0.0)
        box(mv["accs"]["struct"], x0, -(SR + 1.5), PH - 0.6, x1, SR + 1.5, PH + 0.6, LH["door_albedo"])
        for q in range(-4, 5):
            box(mv["accs"]["metal"], x0 + 0.5 if s_ > 0 else x0, q * 3.6 - 0.2, PH + 0.6, x1 if s_ > 0 else x1 - 0.5,
                q * 3.6 + 0.2, PH + 0.8, (0.2, 0.21, 0.23))
        for q in range(-2, 3):                        # painted chevrons (yellow) pointing to the seam
            yc = q * 6.4
            for sgn in (-1, 1):
                pa = Vector((s_ * (SR - 1.0), yc + sgn * 2.4, PH + 0.82))
                pb = Vector((s_ * 3.0, yc, PH + 0.82))
                K.seg_box(mv["accs"]["rough"], pa, pb, 1.1, 0.02, (0.55, 0.36, 0.02))
        box(mv["accs"]["metal"], s_ * (SR + 0.3) - 0.8, -(SR + 1.5), PH + 0.6, s_ * (SR + 0.3) + 0.8, SR + 1.5, PH + 1.8,
            (0.18, 0.19, 0.21))
        xs = 0.15 if s_ > 0 else -0.15
        box(mv["accs"]["trim"], min(0.0, xs), -(SR + 1.0), PH + 0.81, max(0.0, xs), SR + 1.0, PH + 0.9, ICE, 1.5)

    # ------------------------------------------------------------ the rocket (mover): the hero
    ms = K.mover("rocket")
    rr_, rh = RK["r"], RK["h"]
    tube(ms["accs"]["struct"], (0, 0, 0.0), (0, 0, rh), rr_, (0.62, 0.64, 0.66), n=32)
    for zz in (rh * 0.12, rh * 0.62):
        tube(ms["accs"]["rough"], (0, 0, zz), (0, 0, zz + 2.4), rr_ + 0.05, (0.5, 0.04, 0.03), n=32)
    for k in range(12):
        r0, r1 = rr_ * (1 - k / 12) ** 0.7, rr_ * (1 - (k + 1) / 12) ** 0.7
        z0, z1 = rh + k * 1.6, rh + (k + 1) * 1.6
        for j in range(32):
            a0, a1 = 2 * math.pi * j / 32, 2 * math.pi * (j + 1) / 32
            ms["accs"]["struct"].face([(r0 * math.cos(a0), r0 * math.sin(a0), z0), (r0 * math.cos(a1), r0 * math.sin(a1), z0),
                                       (r1 * math.cos(a1), r1 * math.sin(a1), z1), (r1 * math.cos(a0), r1 * math.sin(a0), z1)],
                                      (0.62, 0.64, 0.66))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        box(ms["accs"]["rough"], math.cos(a) * rr_ - 0.4, math.sin(a) * rr_ - 0.4, 0.0, math.cos(a) * (rr_ + 4.0) + 0.4,
            math.sin(a) * (rr_ + 4.0) + 0.4, 9.0, (0.5, 0.04, 0.03))
    box(ms["accs"]["small"], -0.5, -0.5, rh + 19.2, 0.5, 0.5, rh + 20.2, MARK, 20.0)
    # the hack bands: 3 rings of access panels; a band lights lime when it is hacked (one per retarget)
    BANDS = []
    for b in range(3):
        acc = Acc("band_%d" % b, K.M["emit"], 6, K.COLL["movers"])
        zb = rh * (0.30 + 0.18 * b)
        for j in range(10):
            a0, a1 = 2 * math.pi * (j + 0.1) / 10, 2 * math.pi * (j + 0.8) / 10
            for (za, zz) in ((zb, zb + 2.2), (zb + 2.8, zb + 3.6)):
                acc.face([(math.cos(a0) * (rr_ + 0.06), math.sin(a0) * (rr_ + 0.06), za),
                          (math.cos(a1) * (rr_ + 0.06), math.sin(a1) * (rr_ + 0.06), za),
                          (math.cos(a1) * (rr_ + 0.06), math.sin(a1) * (rr_ + 0.06), zz),
                          (math.cos(a0) * (rr_ + 0.06), math.sin(a0) * (rr_ + 0.06), zz)],
                         HACK if (za == zb) else (1.0, 0.1, 0.06), 6.0)
        hooks["accs"]["band_%d" % b] = acc
        BANDS.append("band_%d" % b)
    # rocket service lights (on the rocket: ride with it) + strobes
    svc = K.add_light("rocket_svc", "SPOT", (rr_ + 14.0, -rr_ - 14.0, 10.0), LH["svc_w"], ICE, aim=(0.0, 0.0, 40.0),
                      size=1.5, spot=40, blend=0.6, group="mech")
    hooks["mover_lights"]["rocket"] = [(svc, (rr_ + 14.0, -rr_ - 14.0, 10.0))]
    log("doors, rocket")

    # ------------------------------------------------------------ the service gantry + LAUNCH CONTROL (the TARGET)
    gy = CP["control"]["y"]
    for (dx, dy) in ((-4, -4), (4, -4), (4, 4), (-4, 4)):
        tube(A["metal"], (dx, gy + dy, PH), (dx, gy + dy, PH + 70.0), 0.5, (0.5, 0.06, 0.04), n=5)
    z = PH
    while z < PH + 70:                                # v2: a real lattice (X braces) + lit ice corner edges
        box(A["metal"], -4.3, gy - 4.3, z, 4.3, gy + 4.3, z + 0.5, (0.5, 0.06, 0.04))
        for (a0, b0, a1, b1) in ((-4, -4, 4, -4), (4, -4, 4, 4), (4, 4, -4, 4), (-4, 4, -4, -4)):
            tube(A["metal"], (a0, gy + b0, z), (a1, gy + b1, z + 7.0), 0.16, (0.5, 0.06, 0.04), n=4)
            tube(A["metal"], (a1, gy + b1, z), (a0, gy + b0, z + 7.0), 0.16, (0.5, 0.06, 0.04), n=4)
        z += 7.0
    for (dx, dy) in ((-4.6, -4.6), (4.6, -4.6)):
        box(A["trim"], dx - 0.1, gy + dy - 0.1, PH, dx + 0.1, gy + dy + 0.1, PH + 70.0, ICE, LH["trim_k"] * 0.6)
    for zz in (PH + 22.0, PH + 44.0, PH + 64.0):      # service arms to the rocket
        box(A["metal"], -1.0, gy + 4.0, zz, 1.0, -RK["r"] - 1.5, zz + 1.2, (0.5, 0.06, 0.04))
        box(A["small"], -0.4, gy + 4.0, zz + 1.2, 0.4, -RK["r"] - 1.5, zz + 1.4, MARK, 3.0)
    so = G.ROOM["srv"]["o"]
    box(A["civic"], -9.0, gy - 7.0, so[2] - 1.0, 9.0, gy + 7.0, so[2], STEEL)
    box(A["glass"], -8.5, gy - 6.5, so[2], 8.5, gy + 6.5, so[2] + 8.0, (0.02, 0.04, 0.06))
    box(A["civic"], -9.0, gy - 7.0, so[2] + 8.0, 9.0, gy + 7.0, so[2] + 9.0, STEEL)
    emv = K.ROOM_EMIT.setdefault("srv", Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"]))
    for k in range(6):                                # the consoles inside (red: the TARGET)
        box(emv, -7.0 + k * 2.5, gy - 3.0, so[2] + 1.0, -5.6 + k * 2.5, gy - 2.0, so[2] + 3.4, (1.0, 0.22, 0.08), 5.0)
    box(A["trim"], -9.05, gy - 7.05, so[2] + 8.2, 9.05, gy - 6.95, so[2] + 8.8, ICE, 3.0)
    for k in range(8):
        box(A["small"], -0.4, gy - 0.4, PH + 70.0 + k * 0.01, 0.4, gy + 0.4, PH + 71.0, MARK, LH["marker_k"])
    log("gantry")

    # ------------------------------------------------------------ the stations (dish bunkers, the PAD)
    dr = random.Random(7320)
    for nid, a in sorted(G.STATION.items(), key=lambda kv: G.ORDER[kv[0]]):
        rec = G.ROOM[nid]
        v = G.az_vec(a)
        K.room_shell(nid, rec, kind="router" if nid == "start" else None)
        blk = dict(o=(v[0] * (RR + RD), v[1] * (RR + RD), 0.0), n=v)
        obox(A["civic"], blk, -RW / 2 - 6.0, -RW / 2 - 0.3, -RD - 4.0, 0.0, 0.0, RH + 3.0, STEEL)
        obox(A["civic"], blk, RW / 2 + 0.3, RW / 2 + 6.0, -RD - 4.0, 0.0, 0.0, RH + 3.0, STEEL)
        obox(A["civic"], blk, -RW / 2 - 6.0, RW / 2 + 6.0, -RD - 4.0, -RD - 0.3, 0.0, RH + 3.0, STEEL)
        obox(A["civic"], blk, -RW / 2 - 6.0, RW / 2 + 6.0, -RD - 4.0, 0.0, RH + 0.3, RH + 3.0, STEEL)
        oquad(A["trim"], blk, 0.05, -RW / 2 - 6.0, RH + 2.6, RW / 2 + 6.0, RH + 2.9, ICE, LH["trim_k"])
        K.add_light("work_%s" % nid, "SPOT", K.rf(blk, 22.0, 0.0, 2.0), LH["flood_w"] * 0.5, ICE,
                    aim=K.rf(blk, 0.0, 0.0, RH * 0.6), size=1.0, spot=70, blend=0.8, group="corp")
        top = RH + 3.0
        c = K.rf(blk, -RD / 2 - 2.0, 0.0, top)
        if nid == "start":                            # the crest on the PAD bunker
            cc = (c[0], c[1], top + 9.0)
            disc = [(cc[0] + v[1] * 5.0 * math.cos(2 * math.pi * k / 32), cc[1] - v[0] * 5.0 * math.cos(2 * math.pi * k / 32),
                     cc[2] + 5.0 * math.sin(2 * math.pi * k / 32)) for k in range(32)]
            A["trim"].face(disc, ICE, 2.0)
            for k in range(48):
                a0, a1 = 2 * math.pi * k / 48, 2 * math.pi * (k + 1) / 48
                p0 = (cc[0] + v[1] * 9.0 * math.cos(a0) + v[0] * 0.4, cc[1] - v[0] * 9.0 * math.cos(a0) + v[1] * 0.4,
                      cc[2] + 2.6 * math.sin(a0))
                p1 = (cc[0] + v[1] * 9.0 * math.cos(a1) + v[0] * 0.4, cc[1] - v[0] * 9.0 * math.cos(a1) + v[1] * 0.4,
                      cc[2] + 2.6 * math.sin(a1))
                tube(A["trim"], p0, p1, 0.35, ICE, 3.0, n=4)
            tube(A["metal"], (c[0], c[1], top), (cc[0], cc[1], cc[2] - 5.0), 0.5, (0.3, 0.3, 0.3), n=5)
        else:
            ped = top + 6.0
            tube(A["metal"], (c[0], c[1], top), (c[0], c[1], ped), 1.4, (0.32, 0.34, 0.37), n=8)
            tilt = math.radians(dr.uniform(35, 55))
            dvec = Vector((v[0] * math.cos(tilt), v[1] * math.cos(tilt), math.sin(tilt)))
            up = Vector((0, 0, 1)).cross(dvec)
            up = up.normalized() if up.length > 1e-4 else Vector((1, 0, 0))
            w2 = dvec.cross(up).normalized()
            centre = Vector((c[0], c[1], ped + 4.0))
            Rd, depth = 11.0, 3.0
            for i in range(6):
                for j in range(28):
                    pts = []
                    for (ii, jj) in ((i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)):
                        r = Rd * ii / 6
                        a_ = 2 * math.pi * jj / 28
                        pts.append(centre + up * (r * math.cos(a_)) + w2 * (r * math.sin(a_)) + dvec * (depth * (r / Rd) ** 2))
                    A["civic"].face(pts, (0.55, 0.58, 0.62))
            for j in range(48):
                a0, a1 = 2 * math.pi * j / 48, 2 * math.pi * (j + 1) / 48
                p0 = centre + up * (Rd * math.cos(a0)) + w2 * (Rd * math.sin(a0)) + dvec * depth
                p1 = centre + up * (Rd * math.cos(a1)) + w2 * (Rd * math.sin(a1)) + dvec * depth
                tube(A["trim"], p0, p1, 0.18, ICE, LH["dish_k"], n=4)
            tube(A["metal"], centre, centre + dvec * 9.0, 0.25, (0.4, 0.4, 0.42), n=4)
    log("stations")

    # ------------------------------------------------------------ THE ANTENNA TOWER: a truss with decks and rooms
    av = G.az_vec(AN["az"])
    tx, ty = av[0] * AN["r"], av[1] * AN["r"]
    hf, H = AN["half"], AN["h"]
    TR = (0.42, 0.44, 0.48)
    for (dx, dy) in ((-hf, -hf), (hf, -hf), (hf, hf), (-hf, hf)):
        tube(A["metal"], (tx + dx, ty + dy, 0.0), (tx + dx * 0.45, ty + dy * 0.45, H), 0.55, TR, n=6)
    z = 0.0
    while z < H - 8:                                  # the truss: X braces between the legs every 8 BU
        f0 = 1 - z / H * 0.55
        f1 = 1 - (z + 8) / H * 0.55
        for (a0, b0, a1, b1) in ((-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1)):
            tube(A["metal"], (tx + a0 * hf * f0, ty + b0 * hf * f0, z), (tx + a1 * hf * f1, ty + b1 * hf * f1, z + 8), 0.18, TR, n=4)
            tube(A["metal"], (tx + a1 * hf * f0, ty + b1 * hf * f0, z), (tx + a0 * hf * f1, ty + b0 * hf * f1, z + 8), 0.18, TR, n=4)
        z += 8.0
    for dz in AN["decks"]:                            # equipment decks: grating, railings, lit edge
        f = 1 - dz / H * 0.55
        ex = hf * f + 6.0
        box(A["metal"], tx - ex, ty - ex, dz - 0.6, tx + ex, ty + ex, dz, (0.3, 0.32, 0.35))
        for (x0, y0, x1, y1) in ((tx - ex, ty - ex, tx + ex, ty - ex + 0.2), (tx - ex, ty + ex - 0.2, tx + ex, ty + ex),
                                 (tx - ex, ty - ex, tx - ex + 0.2, ty + ex), (tx + ex - 0.2, ty - ex, tx + ex, ty + ex)):
            box(A["trim"], x0, y0, dz + 1.0, x1, y1, dz + 1.15, ICE, 2.0)
        if dz == AN["decks"][-1]:                     # the top deck: dishes + horn antennas, red markers
            for k in range(4):
                a = 45 + 90 * k
                v2 = G.az_vec(a)
                cpt = Vector((tx + v2[0] * (ex - 2), ty + v2[1] * (ex - 2), dz + 4.0))
                for j in range(24):
                    a0, a1 = 2 * math.pi * j / 24, 2 * math.pi * (j + 1) / 24
                    up_ = Vector((-v2[1], v2[0], 0.0))
                    p0 = cpt + up_ * (3.5 * math.cos(a0)) + Vector((0, 0, 3.5 * math.sin(a0)))
                    p1 = cpt + up_ * (3.5 * math.cos(a1)) + Vector((0, 0, 3.5 * math.sin(a1)))
                    tube(A["trim"], p0, p1, 0.12, ICE, LH["dish_k"], n=4)
    tube(A["metal"], (tx, ty, H), (tx, ty, H + 26.0), 0.3, TR, n=5)
    for zz in (30.0, 60.0, H, H + 26.0):
        box(A["small"], tx - 0.8, ty - 0.8, zz, tx + 0.8, ty + 0.8, zz + 1.2, MARK, LH["marker_k"] * 1.5)
    # the enclosed rooms (elite vaults) hang on the outer face at deck heights; a bunker at the foot
    for (nid, zr) in AN["rooms"]:
        rec = G.ROOM[nid]
        K.room_shell(nid, rec)
        obox(A["civic"], rec, -RW / 2 - 1.0, RW / 2 + 1.0, -RD - 1.0, 0.4, rec["o"][2] - 1.0, rec["o"][2] - 0.4, STEEL)
        obox(A["civic"], rec, -RW / 2 - 1.0, RW / 2 + 1.0, -RD - 1.0, 0.4, rec["o"][2] + RH + 0.3, rec["o"][2] + RH + 1.3, STEEL)
        for s_ in (-1, 1):
            obox(A["civic"], rec, s_ * (RW / 2 + 0.5) - 0.5, s_ * (RW / 2 + 0.5) + 0.5, -RD - 1.0, 0.4, rec["o"][2] - 0.4,
                 rec["o"][2] + RH + 0.3, STEEL)
        oquad(A["trim"], rec, 0.45, -RW / 2 - 1.0, rec["o"][2] + RH + 1.0, RW / 2 + 1.0, rec["o"][2] + RH + 1.3, MARK, 3.0)
        oquad(A["trim"], rec, 0.45, -RW / 2 - 1.0, rec["o"][2] - 1.0, RW / 2 + 1.0, rec["o"][2] - 0.7, MARK, 3.0)
    for (dz, side) in ((0.0, 1), (26.0, -1)):         # the stairs up the outer faces between the decks
        z0, z1 = dz, dz + 26.0
        x0 = tx + side * (hf + 2.0)
        for s in range(12):
            za = z0 + (z1 - z0) * s / 12
            box(A["metal"], x0 - 1.0, ty + hf + 1.0 - 2 * hf * s / 12, za, x0 + 1.0, ty + hf - 2 * hf * (s + 1) / 12 + 1.0,
                za + 0.3, (0.32, 0.34, 0.36))
    K.add_light("ant_key", "SPOT", (tx, ty + 60.0, 4.0), LH["key_w"], ICE, aim=(tx, ty, 50.0), size=1.5, spot=34,
                blend=0.5, group="corp")
    K.add_light("ant_red", "POINT", (tx, ty, H + 8.0), 6000.0, MARK, size=1.0, group="corp", shadow=False)
    log("antenna")

    # ------------------------------------------------------------ the causeway ring + spokes
    zc = G.GROUND_Z
    n = 120
    for k in range(n):
        a0, a1 = 360.0 * k / n, 360.0 * (k + 1) / n
        p0, p1 = G.az_vec(a0), G.az_vec(a1)
        K.seg_box(A["metal"], Vector((p0[0] * G.RL, p0[1] * G.RL, zc + 0.05)), Vector((p1[0] * G.RL, p1[1] * G.RL, zc + 0.05)),
                  3.0, 0.4, (0.3, 0.32, 0.35))
        for s2 in (-1.55, 1.55):
            K.seg_box(A["small"], Vector((p0[0] * (G.RL + s2), p0[1] * (G.RL + s2), zc + 0.1)),
                      Vector((p1[0] * (G.RL + s2), p1[1] * (G.RL + s2), zc + 0.1)), 0.12, 0.05, ICE, 0.7)
    for a in (150.0, 330.0, 210.0, 30.0, 90.0, 270.0):
        v = G.az_vec(a)
        K.seg_box(A["metal"], Vector((v[0] * PR, v[1] * PR, PH)), Vector((v[0] * (G.RL - 2), v[1] * (G.RL - 2), zc + 0.05)),
                  3.0, 0.4, (0.3, 0.32, 0.35))
    sxy = G.ROOM["start"]["o"]
    K.add_light("hack", "POINT", (sxy[0] - 4.0, sxy[1] - 4.0, 2.0), 120.0, (0.55, 1.0, 0.0), size=0.3, group="start")
    log("causeway")

    # ============================================================ THE LANDMARK RIG (+ the review: lift H_decision)
    RIMRX = bpy.data.collections.new("rim_rx")
    for k in range(4):
        a = 45.0 + 90.0 * k
        v = G.az_vec(a)
        K.add_light("rim_%d" % k, "AREA", (v[0] * 240.0, v[1] * 240.0, 50.0), LH["rim_w"],
                    pal("district_a" if k % 2 else "district_b"), aim=(0.0, 0.0, 30.0), size=120.0, size_y=80.0,
                    group="corp", shadow=False, receivers=RIMRX)
    for k in range(6):                                # launch-pad floodlight masts at the podium rim
        a = 30.0 + 60.0 * k
        v = G.az_vec(a)
        p = (v[0] * (PR + 6), v[1] * (PR + 6), 24.0)
        tube(A["metal"], (p[0], p[1], 0.0), p, 0.4, (0.2, 0.2, 0.22), n=5)
        box(A["trim"], p[0] - 1.5, p[1] - 1.5, p[2] - 0.6, p[0] + 1.5, p[1] + 1.5, p[2], ICE, 6.0)
        K.add_light("pad_flood_%d" % k, "SPOT", p, LH["pad_flood_w"], ICE, aim=(0.0, 0.0, PH + 10.0), size=1.5, spot=48,
                    blend=0.6, group="corp")
        if k % 2 == 0:
            hooks["beams"].append(((p[0], p[1], p[2] + 0.5), (v[0] * 0.25, v[1] * 0.25, 1.0), ICE, K.HZ["beams"]["power"],
                                   K.HZ["beams"]["cone"]))
    # KEYS on the active room and its options (moved per frame): a key from the camera side + a rim from behind
    KEYS = [K.add_light("key_room_%d" % k, "SPOT", (0, 0, -100), LH["room_key_w"], (1.0, 0.95, 0.88), aim=(0, 0, -200),
                        size=1.0, spot=40, blend=0.6, group="key", shadow=False) for k in range(3)]
    RIMS = [K.add_light("rim_room_%d" % k, "SPOT", (0, 0, -100), LH["room_key_w"] * 0.6, ICE, aim=(0, 0, -200), size=1.0,
                        spot=40, blend=0.6, group="key", shadow=False) for k in range(3)]
    # fog lit from below: a low bank round the podium (the general bank) + warm / ice fills under it
    for k in range(8):
        a = 22.5 + 45.0 * k
        v = G.az_vec(a)
        K.add_light("underfog_%d" % k, "AREA", (v[0] * 140.0, v[1] * 140.0, 0.4), LH["underfog_w"],
                    ICE if k % 2 else pal("sodium"), aim=(v[0] * 140.0, v[1] * 140.0, 30.0), size=40.0, size_y=30.0,
                    group="corp", shadow=False, receivers=K.COLL["media"])
    log("rig")

    # ============================================================ the launch cutscene props (hidden unless asked)
    LZ = LH["strike"]
    fx, fy = LZ["at"]
    fac = Acc("strike_site", K.M["metal"], 2, K.COLL["city"])
    box(fac, fx - 24, fy - 18, 0.0, fx + 24, fy + 18, 46.0, (0.08, 0.08, 0.1))
    for k in range(3):                                # the Orbital facility on the roof: dishes + a crest disc
        cx_ = fx - 14 + k * 14
        tube(fac, (cx_, fy, 46.0), (cx_, fy, 52.0), 0.8, (0.3, 0.3, 0.32), n=6)
    hooks["accs"]["strike_site"] = fac
    site_t = Acc("strike_trim", K.M["emit"], 2, K.COLL["city"])
    for k in range(3):
        cx_ = fx - 14 + k * 14
        for j in range(24):
            a0, a1 = 2 * math.pi * j / 24, 2 * math.pi * (j + 1) / 24
            tube(site_t, (cx_ + 5 * math.cos(a0), fy + 5 * math.sin(a0), 55.0), (cx_ + 5 * math.cos(a1), fy + 5 * math.sin(a1), 55.0),
                 0.2, ICE, 3.0, n=4)
    for q in range(10):
        box(site_t, fx - 24.05, fy - 16 + q * 3.4, 6.0, fx - 23.95, fy - 14.5 + q * 3.4, 42.0, ICE, 0.6)
    hooks["accs"]["strike_trim"] = site_t
    # the rocket in flight (a mover) + its trail (one object, revealed along its length) + the strike (a mover)
    fl = K.mover("flight")
    tube(fl["accs"]["struct"], (0, 0, -9.0), (0, 0, 9.0), 2.4, (0.62, 0.64, 0.66), n=16)
    tube(fl["accs"]["trim"], (0, 0, -12.0), (0, 0, -9.0), 2.0, (1.0, 0.75, 0.4), 30.0, n=12)
    fll = K.add_light("flight_glow", "POINT", (0, 0, -12.0), LZ["glow_w"], (1.0, 0.6, 0.3), size=2.0, group="mech",
                      shadow=False)
    hooks["mover_lights"]["flight"] = [(fll, (0.0, 0.0, -12.0))]
    tm, ntt = K.new_mat("trail")
    ot = ntt.nodes.new("ShaderNodeOutputMaterial")
    emt = ntt.nodes.new("ShaderNodeEmission")
    ca = K.attr(ntt, "col")
    ka = K.attr(ntt, "k")                             # the trail coordinate u (0 at the silo, 1 at the target)
    tv = ntt.nodes.new("ShaderNodeValue")
    tv.name = "TRAIL"
    tv.outputs[0].default_value = 0.0
    vis = K.mth(ntt, "LESS_THAN", ka.outputs["Fac"], tv.outputs[0])
    fade = K.mth(ntt, "ADD", 0.25, K.mth(ntt, "MULTIPLY", 0.75, K.smooth(ntt, K.mth(ntt, "SUBTRACT", ka.outputs["Fac"],
                                                                                      K.mth(ntt, "SUBTRACT", tv.outputs[0], 0.25)),
                                                                          0.0, 0.25)))
    ntt.links.new(ca.outputs["Color"], emt.inputs["Color"])
    ntt.links.new(K.mth(ntt, "MULTIPLY", K.mth(ntt, "MULTIPLY", vis, fade), LZ["trail_k"]), emt.inputs["Strength"])
    tr_ = ntt.nodes.new("ShaderNodeBsdfTransparent")
    mx = ntt.nodes.new("ShaderNodeMixShader")
    ntt.links.new(vis, mx.inputs[0])
    ntt.links.new(tr_.outputs[0], mx.inputs[1])
    ntt.links.new(emt.outputs[0], mx.inputs[2])
    ntt.links.new(mx.outputs[0], ot.inputs[0])
    TRAIL = Acc("trail", tm, 7, K.COLL["streaks"])
    arc = G.strike_arc(80)
    for k_, (p, q) in enumerate(zip(arc, arc[1:])):
        tube(TRAIL, p, q, 1.6 + 2.0 * (k_ / 80.0), (1.0, 0.92, 0.85), k_ / 80.0, n=6)
    hooks["accs"]["trail"] = TRAIL
    bm = K.mover("boom")
    for j in range(3):                                # the strike: nested emissive shells (scaled per frame)
        rr2 = [8.0, 14.0, 22.0][j]
        cols = [(1.0, 0.95, 0.8), (1.0, 0.5, 0.12), (0.9, 0.2, 0.05)][j]
        for i in range(10):
            for k in range(20):
                t0, t1 = math.pi * i / 10, math.pi * (i + 1) / 10
                a0, a1 = 2 * math.pi * k / 20, 2 * math.pi * (k + 1) / 20

                def sp(t, a):
                    return (rr2 * math.sin(t) * math.cos(a), rr2 * math.sin(t) * math.sin(a), rr2 * math.cos(t) * 0.8)
                bm["accs"]["trim"].face([sp(t0, a0), sp(t0, a1), sp(t1, a1), sp(t1, a0)], cols, [30.0, 8.0, 2.0][j])
    bl_ = K.add_light("boom_light", "POINT", (0, 0, 10.0), LZ["boom_w"], (1.0, 0.55, 0.2), size=8.0, group="mech",
                      shadow=False)
    hooks["mover_lights"]["boom"] = [(bl_, (0.0, 0.0, 10.0))]
    log("launch props")

    def post_build(OBJ):
        for name, ob in OBJ.items():
            if ob is not None and any(c.name in ("compound", "rooms", "movers") for c in ob.users_collection):
                RIMRX.objects.link(ob)
    hooks["post_build"] = post_build

    def apply(fr, ctx):
        me = fr.get("mech") or {}
        mv = fr.get("movers") or {}
        OBJ, LIGHTS = ctx["OBJ"], ctx["LIGHTS"]
        dk = (mv.get("door_e") or (0.0, 0, 0))[0] / (SR + 1.0)
        open_k = max(0.0, min(1.0, float(me.get("shaft", dk))))
        ctx["set_pwo"](OBJ.get("prep_shaft"), 0.35 * open_k)        # v2: the shaft glows only while open
        ctx["set_pwo"](OBJ.get("prep_lock_red"), 1.0 - open_k)      # SHUT: the red lock lamps
        ctx["set_pwo"](OBJ.get("prep_lock_open"), open_k)           # OPEN: the white-green lamps
        bands = int(me.get("bands", 0))
        for k, nm in enumerate(BANDS):
            ctx["set_pwo"](OBJ.get(nm), 1.0 if k < bands else 0.04)
        # the launch props: hidden unless the frame asks (launch board / strike still)
        show = bool(me.get("launch"))
        for nm in ("trail",):
            ob = OBJ.get(nm)
            if ob is not None:
                ob.hide_render = not show
        if show:
            tm.node_tree.nodes["TRAIL"].outputs[0].default_value = float(me.get("trail", 0.0))
        for name in ("flight", "boom"):
            for ob in K.MOVERS[name]["objs"]:
                ob.hide_render = not show or (name == "boom" and float(me.get("boom", 0.0)) <= 0.0) or \
                    (name == "flight" and not me.get("in_flight"))
        if me.get("heading"):
            rot = Vector(me["heading"]).to_track_quat("Z", "Y").to_euler()
            for ob in K.MOVERS["flight"]["objs"]:
                ob.rotation_euler = rot
        bk = float(me.get("boom", 0.0))
        for ob in K.MOVERS["boom"]["objs"]:
            s = 0.2 + 1.8 * bk
            ob.scale = (s, s, s)
        cam = fr["pose"]["loc"]
        room_ids = [i for i, s_ in (fr.get("room_state") or {}).items() if s_ in ("current", "option")]
        room_ids = sorted(room_ids, key=lambda i: (fr["room_state"][i] != "current", G.ORDER[i]))[:3]
        for (lob, e0, grp) in LIGHTS:
            if lob.name == "shaft":
                lob.data.energy = e0 * (0.05 + 0.95 * open_k)
            elif lob.name == "shaft_beam":
                lob.data.energy = e0 * open_k
            elif lob.name == "flight_glow":
                lob.data.energy = e0 if (show and me.get("in_flight")) else 0.0
            elif lob.name == "boom_light":
                lob.data.energy = e0 * bk if show else 0.0
        for k in range(3):
            if k < len(room_ids):
                c = Vector(G.room_center(room_ids[k]))
                cv = Vector(cam)
                d = (cv - c)
                d.z = 0
                d = d.normalized() if d.length > 1e-3 else Vector((0, -1, 0))
                kp = c + d * 26.0 + Vector((0, 0, 16.0))
                rp = c - d * 18.0 + Vector((0, 0, 14.0))
                KEYS[k].location = kp
                KEYS[k].rotation_euler = (c - kp).to_track_quat("-Z", "Y").to_euler()
                RIMS[k].location = rp
                RIMS[k].rotation_euler = (c - rp).to_track_quat("-Z", "Y").to_euler()
                KEYS[k].data.energy = LH["room_key_w"] * (1.3 if k == 0 else 1.0)
                RIMS[k].data.energy = LH["room_key_w"] * 0.6
            else:
                KEYS[k].data.energy = 0.0
                RIMS[k].data.energy = 0.0
    hooks["apply"] = apply
    return hooks
