"""HQ Meridian v2: the Blender build of the container fortress (called by the kit's hq_scene.py: build(K) -> hooks).
v2 (designer review 2026-10-15): the route rings all four walls; a BREACH per wall whose SHUTTLE container the keep
crane moves between the wall and the train; the LOOP TRACK, the freight PLATFORMS and the moat run all round; the
slewing KEEP CRANE in the yard; MANIFEST CONTROL moved to the yard's south-west. v1's build: git history.

Everything is placed by rule from hq_preset "compound" + hq_graph; seeds: 5320 (container colours / IDs), 5321 (yard
stacks), 5322 (signals), 5323 (platform stacks), 5330 (the landmark rig).
  walls      container courses between the corner towers in runs between the route rooms (a room = a container slot
             cut open on its outer face); the breach slot in the top course stays EMPTY (the shuttle mover fills it);
             the sally port room under it in course 0; merlons on top
  towers     5 courses of crossed containers; the route's tower room on the face the run arrives at (course 3)
  the loop   the track (rails, sleepers, a sodium glint) round the fortress, a ring of flatcars with closed containers
             (the freight train standing on the loop), empty flatcars opposite every breach (where a shuttle lands)
  platforms  the outer deck round the track: container offices (the Q rooms), stacks, lamp posts, gangways
  moat       round all four sides beyond the platforms; the gate's drawbridge on the west
  crane      the slewing keep crane (mast, cab, jib, counter-jib, trolley, spreader, cables): the jib turns to the lift
  control    MANIFEST CONTROL with m1 on its south face, THE MASTER MANIFEST vault on the roof, the crown sign
"""
import math
import random


def build(K):
    G, CP, pal, LH = K.G, K.CP, K.pal, K.LH
    A, Acc, obox, oquad, rf, tube, box = K.A, K.Acc, K.obox, K.oquad, K.rf, K.tube, K.box
    Vector = K.Vector
    import bpy
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ("mv_", "cable", "crane_")}
    rr = random.Random(5320)
    CRS, RW, RH, RD = CP["course"], CP["room_w"], CP["room_h"], CP["room_d"]
    WX, WY = CP["wall"]["x"], CP["wall"]["y"]
    NC = CP["wall"]["courses"]
    TC, TH_ = CP["tower"]["c"], CP["tower"]["half"]
    TCO = CP["tower"]["courses"]
    CTL = CP["control"]
    TRK, PD0, PD1 = CP["track_off"], CP["platform_deck"][0], CP["platform_deck"][1]
    MO0, MO1 = CP["moat_off"]
    STEEL = pal("steel_alt")
    ORANGE, RED, YW, YC, HAZ = pal("corp_orange"), pal("corp_red"), pal("yard_white"), pal("yard_cool"), pal("hazard")
    SOD, WORK = pal("sodium"), pal("work")
    log = K.log

    # ------------------------------------------------------------ the container material (corrugated, wet, rust)
    m, nt = K.new_mat("container")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    col = K.attr(nt, "col")
    g, ps, ns = K.pos_sep(nt)
    u_ = K.mth(nt, "ADD", ps.outputs["X"], ps.outputs["Y"])
    rib = K.mth(nt, "SINE", K.mth(nt, "MULTIPLY", u_, 4.2))
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

    def container(rec, u0, u1, dn0, dn1, z0, z1, colr=None, doors=True, acc=None):
        c = colr or STEEL[rr.randrange(len(STEEL))]
        obox(acc or C, rec, u0, u1, dn0, dn1, z0 + 0.15, z1, c)
        for uu in (u0, u1 - 0.35):
            obox(A["metal"], rec, uu, uu + 0.35, dn1 - 0.02, dn1 + 0.06, z0 + 0.15, z1, (0.05, 0.05, 0.055))
        if doors and rr.random() < 0.35:
            zz = z0 + (z1 - z0) * 0.72
            uu = rr.uniform(u0 + 1.0, max(u0 + 1.2, u1 - 5.0))
            for q in range(10):
                if rr.random() < 0.6:
                    oquad(A["sign"], rec, dn1 + 0.04, uu + q * 0.36, zz, uu + q * 0.36 + 0.2, zz + 0.9, (0.9, 0.9, 0.85), 0.35)

    # a wall's frame: o on the outer face's centre line, n outward, the tangent = the run direction (hq_graph)
    def wall_frame(side):
        return dict(o=(G.wall_pt(side, 0.0)[0], G.wall_pt(side, 0.0)[1], 0.0), n=G.NRM[side])

    def wall_len(side):
        return (TC[1] - TH_) if side in ("W", "E") else (TC[0] - TH_)

    # the frame's tangent (kit rf: t = (n.y, -n.x)) equals the run direction, so u in the frame = u along the run
    rooms_on = {}
    for (nid, wall, uu, c) in CP["rooms"]:
        rooms_on.setdefault((wall, c), []).append(uu)
    for w in G.WALLS:
        bu = CP["breach"][w]["u"]
        rooms_on.setdefault((w, NC - 1), []).append(bu)       # the breach slot (top course): the shuttle's place
        rooms_on.setdefault((w, 0), []).append(bu)            # the sally port under it
    gate_u = CP["gate_u"]

    # ------------------------------------------------------------ the walls: container courses in runs
    for side in G.WALLS:
        rec = wall_frame(side)
        L = wall_len(side)
        for c in range(NC + 1):
            z0, z1 = c * CRS, c * CRS + CRS - 1.0
            gaps = [(uu - RW / 2 - 0.2, uu + RW / 2 + 0.2) for uu in sorted(rooms_on.get((side, c), []))]
            if side == "W" and c == 0:
                gaps.append((gate_u - 5.0, gate_u + 5.0))
            gaps.sort()
            if c == NC:                              # merlons: half containers every other slot (not over a breach)
                bu = CP["breach"][side]["u"]
                uu = -L
                k = 0
                while uu < L - 1:
                    if k % 2 == 0 and not (bu - RW / 2 - 4 < uu + 3.5 < bu + RW / 2 + 4):
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
        # the breach: an empty slot frame (hazard-striped jambs) + a slot floor; lit red when the shuttle is away
        bu = CP["breach"][side]["u"]
        zb = (NC - 1) * CRS
        for s_ in (-1, 1):
            obox(STRIPE, rec, bu + s_ * (RW / 2 + 0.2) - 0.25, bu + s_ * (RW / 2 + 0.2) + 0.25, -RD, 0.25, zb, zb + CRS,
                 (0.9, 0.55, 0.02))
        obox(A["metal"], rec, bu - RW / 2, bu + RW / 2, -RD, 0.2, zb - 0.1, zb + 0.15, (0.1, 0.1, 0.1))
        for s_ in (-1, 1):
            oquad(A["small"], rec, 0.3, bu + s_ * (RW / 2 + 0.2) - 0.25, zb + CRS - 1.2, bu + s_ * (RW / 2 + 0.2) + 0.25,
                  zb + CRS - 0.6, HAZ, 10.0)
        # the battlement walk: lit warm strip under the merlons (big layer) on both faces
        for dn in (0.08, -RD - 0.08):
            oquad(A["trim"], rec, dn, -L, NC * CRS - 0.6, L, NC * CRS - 0.35, YW, LH["trim_k"])
    log("walls")

    # ------------------------------------------------------------ corner towers: crossed courses, masts, beacons
    troom = {}
    for t, (w, (cx, cy)) in G.TOWER.items():
        troom[(round(cx), round(cy))] = (t, w)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * TC[0], sy * TC[1]
            t, wf = troom[(round(cx), round(cy))]
            n_ = G.NRM[wf]
            for c in range(TCO):
                z0, z1 = c * CRS, c * CRS + CRS - 1.0
                along_x = c % 2 == 0
                if c == 3:
                    continue                          # the tower room's course: built below
                for k in range(2):
                    off = -TH_ + k * TH_
                    if along_x:
                        r_ = dict(o=(cx, cy + off + TH_, 0.0), n=(0.0, 1.0))
                        container(r_, -TH_, TH_, -TH_ + 0.2, 0.0, z0, z1)
                    else:
                        r_ = dict(o=(cx + off + TH_, cy, 0.0), n=(1.0, 0.0))
                        container(r_, -TH_, TH_, -TH_ + 0.2, 0.0, z0, z1)
            # the tower room course: walls round the room slot on the run's face
            r_ = dict(o=(cx + n_[0] * TH_, cy + n_[1] * TH_, 0.0), n=n_)
            z0 = 3 * CRS
            obox(C, r_, -TH_, -RW / 2 - 0.4, -2 * TH_, 0.0, z0 + 0.15, z0 + CRS - 1.0, STEEL[1])
            obox(C, r_, RW / 2 + 0.4, TH_, -2 * TH_, 0.0, z0 + 0.15, z0 + CRS - 1.0, STEEL[1])
            obox(C, r_, -TH_, TH_, -2 * TH_, -RD - 0.4, z0 + 0.15, z0 + CRS - 1.0, STEEL[2])
            top = TCO * CRS
            tube(A["metal"], (cx, cy, top), (cx, cy, top + 16.0), 0.45, (0.12, 0.12, 0.13), n=6)
            box(A["small"], cx - 0.6, cy - 0.6, top + 16.0, cx + 0.6, cy + 0.6, top + 17.0, RED, 12.0)
            for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                K.add_light("tflood_%d_%d_%d_%d" % (sx, sy, dx, dy), "SPOT", (cx + dx * (TH_ + 9), cy + dy * (TH_ + 9), 2.0),
                            LH["flood_w"] * 0.5, YW, aim=(cx + dx * TH_, cy + dy * TH_, top * 0.7), size=1.0, spot=55,
                            blend=0.5, group="corp")
            hooks["beams"].append(((cx + sx * 2, cy + sy * 2, top + 15.0), (sx * 0.30, sy * 0.30, 1.0), YC,
                                   K.HZ["beams"]["power"], K.HZ["beams"]["cone"]))
            for (fx, fy) in ((sx, 0), (0, sy)):
                bx, by = cx + fx * (TH_ + 0.25), cy + fy * (TH_ + 0.25)
                rb = dict(o=(bx, by, 0.0), n=(float(fx), float(fy)))
                obox(A["rough"], rb, -2.2, 2.2, 0.0, 0.15, top - 20.0, top - 2.0, (0.55, 0.12, 0.012))
                obox(A["rough"], rb, -0.5, 0.5, 0.15, 0.2, top - 20.0, top - 2.0, (0.7, 0.7, 0.68))
    log("towers")

    # ------------------------------------------------------------ the yard floor, the loop track, the train ring
    box(A["ground"], -WX, -WY, 0.0, WX, WY, 0.02, (0.25, 0.26, 0.27), k=1.0)

    def ring_box(acc, d0, d1, z0, z1, col, k=0.0, corner=True, north=True):
        """A band round the fortress between offsets d0..d1 outside the wall faces (four sides + corner squares);
        north=False: the W, S, E sides only (the moat: the north side is the rail yard)."""
        X0, X1, Y0, Y1 = WX + d0, WX + d1, WY + d0, WY + d1
        if north:
            box(acc, -X1, Y0, z0, X1, Y1, z1, col, k)              # north band (incl. corners)
        box(acc, -X1, -Y1, z0, X1, -Y0, z1, col, k)                # south
        box(acc, X0, -Y0, z0, X1, Y0 if north else Y1, z1, col, k)                  # east
        box(acc, -X1, -Y0, z0, -X0, Y0 if north else Y1, z1, col, k)                # west
    ring_box(A["ground"], 0.0, PD0, -0.02, 0.0, (0.10, 0.10, 0.11), k=0.0)          # the track bed (dark, wet)
    ring_box(A["ground"], PD0, PD1, 0.0, 1.2, (0.24, 0.24, 0.26), k=1.0)            # the platform deck
    # the moat: a dark water channel all round; the gate's drawbridge crosses it on the west
    # spec: the moat on the W, S and E sides only; the north side is the RAIL YARD (a paved apron with sidings)
    ring_box(A["ground"], MO0, MO1, -2.5, -2.4, (0.02, 0.025, 0.03), k=1.0, north=False)
    ring_box(A["rough"], PD1, MO0, -2.5, 0.3, (0.12, 0.12, 0.12), north=False)
    ring_box(A["rough"], MO1, MO1 + 0.8, -2.5, 0.3, (0.12, 0.12, 0.12), north=False)
    box(A["ground"], -WX - PD1, WY + PD1, -0.02, WX + PD1, WY + MO1 + 0.8, 0.0, (0.09, 0.09, 0.1), k=1.0)
    for yy_ in (WY + PD1 + 3.0, WY + PD1 + 8.0, WY + PD1 + 13.0):          # the yard's sidings (east-west)
        for s_ in (-0.9, 0.9):
            K.seg_box(A["metal"], Vector((-WX - 20.0, yy_ + s_, 0.3)), Vector((WX + 20.0, yy_ + s_, 0.3)), 0.24, 0.3,
                      (0.33, 0.31, 0.3))
            K.seg_box(A["trim"], Vector((-WX - 20.0, yy_ + s_, 0.32)), Vector((WX + 20.0, yy_ + s_, 0.32)), 0.1, 0.02,
                      SOD, LH["rail_k"] * 0.6)
    # rails: two rails round the loop at TRK +- 0.9 (a rectangle with 45-degree chamfered corners)
    def loop_pts(d):
        X, Y = WX + d, WY + d
        ch = 14.0
        return [(-X + ch, Y), (X - ch, Y), (X, Y - ch), (X, -Y + ch), (X - ch, -Y), (-X + ch, -Y), (-X, -Y + ch), (-X, Y - ch)]
    for s_ in (-0.9, 0.9):
        pts = loop_pts(TRK + s_)
        for a_, b_ in zip(pts, pts[1:] + pts[:1]):
            K.seg_box(A["metal"], Vector((a_[0], a_[1], 0.45)), Vector((b_[0], b_[1], 0.45)), 0.24, 0.45, (0.35, 0.33, 0.32))
            K.seg_box(A["trim"], Vector((a_[0], a_[1], 0.47)), Vector((b_[0], b_[1], 0.47)), 0.1, 0.02, SOD, LH["rail_k"])
    pts = loop_pts(TRK)
    for a_, b_ in zip(pts, pts[1:] + pts[:1]):                       # sleepers every 1.6 BU
        L_ = math.hypot(b_[0] - a_[0], b_[1] - a_[1])
        nseg = int(L_ / 1.6)
        for q in range(nseg):
            p = Vector((a_[0] + (b_[0] - a_[0]) * q / nseg, a_[1] + (b_[1] - a_[1]) * q / nseg, 0.18))
            d = Vector((b_[0] - a_[0], b_[1] - a_[1], 0.0)).normalized()
            sd = Vector((-d.y, d.x, 0.0)) * 1.6
            K.seg_box(A["rough"], p - sd, p + sd, 0.5, 0.2, (0.09, 0.08, 0.075))
    # the train: a ring of flatcars on the loop (closed containers), empty cars opposite each breach (the landing)
    def flatcar(rec, x0):
        obox(A["metal"], rec, x0 - 8.2, x0 + 8.2, -RD - 0.2, 0.2, 0.8, CP["car_deck"] - 0.05, (0.07, 0.07, 0.075))
        for wx in (-6.0, -4.0, 4.0, 6.0):
            obox(A["metal"], rec, x0 + wx - 0.6, x0 + wx + 0.6, -RD + 0.3, -RD + 0.9, 0.0, 1.4, (0.04, 0.04, 0.04))
            obox(A["metal"], rec, x0 + wx - 0.6, x0 + wx + 0.6, -0.9, -0.3, 0.0, 1.4, (0.04, 0.04, 0.04))
        for q in range(7):
            oquad(A["trim"], rec, 0.25, x0 - 7.0 + q * 2.3, 1.6, x0 - 6.4 + q * 2.3, 2.0, (1.0, 0.55, 0.1), LH["train_run_k"])
    for side in G.WALLS:
        n_ = G.NRM[side]
        L = (WY + TRK - 16.0) if side in ("W", "E") else (WX + TRK - 16.0)
        rec = dict(o=(G.wall_pt(side, 0.0, TRK + RD / 2)[0], G.wall_pt(side, 0.0, TRK + RD / 2)[1], 0.0), n=n_)
        bu = CP["breach"][side]["u"]
        x0 = -L + 8.4
        k = 0
        while x0 < L - 8.4:
            flatcar(rec, x0)
            if abs(x0 - bu) > 9.0:
                if rr.random() < 0.85:
                    container(rec, x0 - 7.5, x0 + 7.5, -RD + 0.2, -0.2, CP["car_deck"], CP["car_deck"] + 8.4)
            else:
                # the landing car: hazard deck markings + guide posts (where the shuttle lands)
                for s_ in (-1, 1):
                    obox(STRIPE, rec, x0 + s_ * 7.6 - 0.3, x0 + s_ * 7.6 + 0.3, -RD, 0.0, CP["car_deck"], CP["car_deck"] + 3.0,
                         (0.9, 0.55, 0.02))
                oquad(A["small"], rec, 0.3, x0 - 7.8, CP["car_deck"] + 3.0, x0 - 7.4, CP["car_deck"] + 3.6, HAZ, 10.0)
                oquad(A["small"], rec, 0.3, x0 + 7.4, CP["car_deck"] + 3.0, x0 + 7.8, CP["car_deck"] + 3.6, HAZ, 10.0)
            x0 += 17.0
            k += 1
    # ------------------------------------------------------------ THE FREIGHT LINE OUT (designer: "a train track leading
    # away"): a junction on the loop's north side, the line north through a portal on the platform, a truss bridge over
    # the moat, a ramp up onto an elevated viaduct on piers, threading a cleared corridor (over a downtown street) out
    # of frame toward the port; rail glow in Meridian orange, catenary masts, signal lamps, a train running out on it
    VD = CP["viaduct"]
    vx, vy0, dz = VD["x"], VD["y0"], VD["deck_z"]
    ra, rb = VD["ramp"]
    yend, vw = VD["end_y"], VD["w"]

    def zat(y):
        """The deck height: a constant freight grade (VD grade, about 3 %) from the yard (y = ramp[0]), capped at
        deck_z; a short ease where the climb starts (the vertical curve)."""
        g = VD.get("grade", 0.03)
        u = y - ra
        if u <= 0.0:
            return 0.0
        e = 40.0                                           # the vertical curve (BU)
        z = g * u * u / (2 * e) if u < e else g * (u - e / 2)
        return min(dz, z)
    # the switch off the loop + the line north (rails, sleepers on the ground part)
    path = [(vx - 26.0, vy0), (vx - 12.0, vy0 + 1.5), (vx - 3.0, vy0 + 6.0), (vx, vy0 + 14.0)]
    yy = vy0 + 14.0
    while yy < yend:
        path.append((vx, min(yy + 12.0, yend)))
        yy += 12.0
    for s_ in (-0.9, 0.9):
        for (a_, b_) in zip(path, path[1:]):
            d_ = Vector((b_[0] - a_[0], b_[1] - a_[1], 0.0)).normalized()
            nrm = Vector((-d_.y, d_.x, 0.0)) * s_
            pa = Vector((a_[0], a_[1], zat(a_[1]) + 0.45)) + nrm
            pb = Vector((b_[0], b_[1], zat(b_[1]) + 0.45)) + nrm
            K.seg_box(A["metal"], pa, pb, 0.24, 0.45, (0.35, 0.33, 0.32))
            K.seg_box(A["trim"], pa + Vector((0, 0, 0.02)), pb + Vector((0, 0, 0.02)), 0.1, 0.02, WORK, LH["rail_k"] * 1.3)
    yy = vy0 + 14.0
    while yy < ra:
        K.seg_box(A["rough"], Vector((vx - 1.6, yy, 0.18)), Vector((vx + 1.6, yy, 0.18)), 0.5, 0.2, (0.09, 0.08, 0.075))
        yy += 1.6
    # the portal on the platform: container columns + a lintel container, the MERIDIAN FREIGHT stripe, signals
    py0, py1 = WY + PD0, WY + PD1
    pm = (py0 + py1) / 2
    for sx in (-1, 1):
        box(C, vx + sx * 7.0 - 1.6, pm - 3.0, 0.0, vx + sx * 7.0 + 1.6, pm + 3.0, 14.0, STEEL[3])
    box(C, vx - 9.0, pm - 3.2, 14.0, vx + 9.0, pm + 3.2, 18.5, STEEL[0])
    box(A["trim"], vx - 8.6, pm + 3.25, 15.2, vx + 8.6, pm + 3.3, 16.0, ORANGE, LH["logo_k"])
    box(A["trim"], vx - 8.6, pm - 3.3, 15.2, vx + 8.6, pm - 3.25, 16.0, ORANGE, LH["logo_k"])
    for (sx, col_) in ((-1, (0.1, 1.0, 0.35)), (1, RED)):
        box(A["small"], vx + sx * 4.0 - 0.4, pm + 3.3, 12.0, vx + sx * 4.0 + 0.4, pm + 3.5, 12.8, col_, 14.0)
    K.add_light("portal_wash", "SPOT", (vx, pm + 16.0, 22.0), LH["work_w"] * 1.2, WORK, aim=(vx, pm, 6.0), size=1.0,
                spot=60, blend=0.7, group="corp")
    # (spec: no moat on the north side: the line runs out across the rail yard, no bridge)
    m0, m1 = WY + MO0 - 1.0, WY + MO1 + 1.0
    for sx in ():
        xx = vx + sx * vw / 2
        box(STRIPE, xx - 0.3, m0, 4.0, xx + 0.3, m1, 4.6, (0.34, 0.10, 0.045))
        k_ = 0
        y_ = m0
        while y_ < m1 - 0.5:
            tube(A["metal"], (xx, y_, 0.0), (xx, min(y_ + 3.0, m1), 4.3), 0.15, (0.34, 0.10, 0.045), n=4)
            y_ += 3.0
    # the ramp + the viaduct deck, parapets with the orange rail glow, piers, catenary masts, signals
    y_ = WY + MO1 + 1.0
    step = 6.0
    while y_ < yend:
        y1_ = min(y_ + step, yend)
        za, zb = zat(y_), zat(y1_)
        K.seg_box(A["civic"], Vector((vx, y_, za)), Vector((vx, y1_, zb)), vw, 1.4, (0.13, 0.13, 0.14))
        for sx in (-1, 1):
            K.seg_box(A["rough"], Vector((vx + sx * (vw / 2 - 0.2), y_, za + 1.0)), Vector((vx + sx * (vw / 2 - 0.2), y1_, zb + 1.0)),
                      0.4, 1.0, (0.16, 0.15, 0.15))
            K.seg_box(A["trim"], Vector((vx + sx * (vw / 2 - 0.2), y_, za + 1.05)), Vector((vx + sx * (vw / 2 - 0.2), y1_, zb + 1.05)),
                      0.42, 0.04, WORK, LH["rail_k"] * 0.9)
        y_ = y1_
    y_ = ra + 10.0
    while y_ < yend:
        zz = zat(y_)
        if zz > 3.0:
            box(A["civic"], vx - 1.6, y_ - 1.2, 0.0, vx + 1.6, y_ + 1.2, zz - 1.4, (0.11, 0.11, 0.12))
            box(A["civic"], vx - vw / 2, y_ - 1.4, zz - 2.6, vx + vw / 2, y_ + 1.4, zz - 1.4, (0.12, 0.12, 0.13))
        y_ += VD["pier_step"]
    k_ = 0
    y_ = WY + MO1 + 8.0
    while y_ < yend:
        zz = zat(y_)
        for sx in (-1, 1):
            tube(A["metal"], (vx + sx * (vw / 2 + 0.4), y_, zz), (vx + sx * (vw / 2 + 0.4), y_, zz + 8.0), 0.18,
                 (0.18, 0.18, 0.19), n=5)
        box(A["metal"], vx - vw / 2 - 0.6, y_ - 0.15, zz + 7.6, vx + vw / 2 + 0.6, y_ + 0.15, zz + 7.9, (0.18, 0.18, 0.19))
        if k_ % 3 == 0:                                       # signal lamps (green ahead, red behind)
            box(A["small"], vx + vw / 2 + 0.6, y_ - 0.3, zz + 5.0, vx + vw / 2 + 1.2, y_ + 0.3, zz + 5.6,
                (0.1, 1.0, 0.35) if k_ % 2 == 0 else RED, 16.0)
        k_ += 1
        y_ += VD["mast_step"]
    tube(A["metal"], (vx, WY + MO1 + 8.0, zat(WY + MO1 + 8.0) + 7.0), (vx, yend, dz + 7.0), 0.06, (0.08, 0.08, 0.09), n=4)
    for y_ in (300.0, 520.0, 760.0):                          # lamps washing the deck (the corridor reads in the city)
        K.add_light("via_lamp_%d" % y_, "SPOT", (vx, y_, zat(y_) + 9.0), LH["work_w"] * 0.8, WORK, aim=(vx, y_, 0.0),
                    size=0.8, spot=95, blend=0.9, group="corp")
    # a train running OUT on the viaduct: light streaks (white heads ahead, red tails behind) on both rails
    for (ya, yb_, col_, kk) in ((560.0, 640.0, (1.0, 0.92, 0.8), 6.0), (640.0, 700.0, (1.0, 0.5, 0.15), 3.0),
                                (380.0, 420.0, (1.0, 0.08, 0.05), 4.0)):
        for s_ in (-1.4, 1.4):
            box(A["streaks"], vx + s_ - 0.12, ya, zat(ya) + 1.2, vx + s_ + 0.12, yb_, zat(yb_) + 1.5, col_, kk)
    # the freight train standing at the junction: the loco on the line out, two cars behind it (the way in / out)
    lo_ = dict(o=(vx, vy0 + 26.0, 0.0), n=(1.0, 0.0))
    obox(STRIPE, lo_, -8.0, 8.0, -2.4, 2.4, 0.8, 7.4, (0.5, 0.16, 0.02))
    obox(A["small"], lo_, 7.9, 8.05, -1.2, 1.2, 4.6, 5.6, (1.0, 0.92, 0.75), 10.0)
    for q in range(5):
        obox(A["trim"], lo_, -7.0 + q * 3.0, -6.0 + q * 3.0, 2.42, 2.5, 1.0, 2.0, (1.0, 0.75, 0.05), 0.8)
    K.add_light("loco_beam", "SPOT", (vx, vy0 + 34.5, 5.0), LH["head_w"], (1.0, 0.9, 0.75), aim=(vx, vy0 + 160.0, 8.0),
                size=0.0, spot=9, blend=0.4, group="beam", shadow=False, receivers=K.COLL["media"])
    log("loop track, train ring, the freight line out")

    # ------------------------------------------------------------ the freight platforms: offices (Q), stacks, lamps
    pr = random.Random(5323)
    for side in G.WALLS:
        n_ = G.NRM[side]
        rec = dict(o=(G.wall_pt(side, 0.0, PD1)[0], G.wall_pt(side, 0.0, PD1)[1], 0.0), n=n_)
        L = (WY + PD1) if side in ("W", "E") else (WX + PD1)
        bu = CP["breach"][side]["u"]
        uu = -L + 4.0
        while uu < L - 12.0:
            if abs(uu + 7.0 - bu) > 16.0 and not (side == "W" and abs(uu + 7.0 - gate_u) < 14.0) and pr.random() < 0.55:
                hgt = pr.randint(1, 2)
                for c in range(hgt):
                    container(rec, uu, uu + 14.0, -(PD1 - PD0) + 1.0, -2.0, 1.2 + c * 8.6, 1.2 + c * 8.6 + 8.4)
            uu += 15.0
        # lamp posts along the platform edge (sodium), every 24 BU
        uu = -L + 6.0
        while uu < L:
            p = K.rf(dict(o=rec["o"], n=n_), -(PD1 - PD0) + 0.6, uu, 0.0)
            tube(A["metal"], (p[0], p[1], 1.2), (p[0], p[1], 12.0), 0.15, (0.1, 0.1, 0.1), n=5)
            box(A["small"], p[0] - 0.6, p[1] - 0.6, 11.6, p[0] + 0.6, p[1] + 0.6, 12.0, SOD, 12.0)
            uu += 24.0
    # the platform offices = the Q rooms (a container office on the deck, open outward) + a lit sign over each
    for w in G.WALLS:
        q = "q" + w.lower()
        r = G.ROOM[q]
        K.room_shell(q, r)
        obox(C, r, -RW / 2 - 0.6, RW / 2 + 0.6, -RD - 0.6, 0.0, r["o"][2] + RH, r["o"][2] + RH + 0.8, STEEL[2])
        obox(A["trim"], r, -RW / 2, RW / 2, 0.1, 0.2, r["o"][2] + RH + 0.9, r["o"][2] + RH + 1.6, ORANGE, LH["logo_k"])
        K.add_light("plat_%s" % w, "SPOT", rf(r, 10.0, 0.0, 14.0), LH["work_w"] * 0.6, SOD, aim=rf(r, 0.0, 0.0, 2.0),
                    size=0.8, spot=70, blend=0.8, group="corp")
    log("platforms")

    # ------------------------------------------------------------ the gate (west): portcullis, drawbridge
    gr = dict(o=(-WX, gate_u, 0.0), n=(-1.0, 0.0))
    container(gr, -6.0, 6.0, -RD, 0.6, CRS - 1.0, CRS + 2.0, STEEL[3])
    oquad(A["trim"], gr, -RD * 0.5, -4.5, 0.0, 4.5, CRS - 1.2, (1.0, 0.45, 0.12), 2.4)
    for q in range(7):
        obox(A["metal"], gr, -4.2 + q * 1.4, -4.0 + q * 1.4, -1.2, -0.9, 0.0, CRS - 1.2, (0.08, 0.08, 0.09))
    for s_ in (-1, 1):
        oquad(A["small"], gr, 0.65, s_ * 5.2 - 0.4, CRS - 0.4, s_ * 5.2 + 0.4, CRS + 0.4, RED, 14.0)
    obox(C, gr, -4.5, 4.5, PD1, MO1 + 2.0, 0.0, 0.6, STEEL[0])                   # the drawbridge over the moat
    obox(A["metal"], gr, -4.5, 4.5, 0.6, PD0, 0.0, 0.35, (0.2, 0.2, 0.21))       # the crossing over the track
    for s_ in (-1, 1):
        tube(A["metal"], rf(gr, PD1, s_ * 4.5, 9.0), rf(gr, MO1 + 1.5, s_ * 4.5, 0.6), 0.12, (0.2, 0.2, 0.2), n=4)
        tube(A["metal"], rf(gr, PD1, s_ * 4.5, 0.0), rf(gr, PD1, s_ * 4.5, 10.0), 0.4, (0.15, 0.15, 0.16), n=5)
    K.add_light("gate", "POINT", rf(gr, 4.0, 0.0, 4.0), 900.0, (1.0, 0.5, 0.2), size=1.0, group="corp")
    sx_, sy_ = CP["start"]
    box(A["rough"], sx_ - 3, sy_ - 4, 0, sx_ + 3, sy_ + 4, 4.4, (0.2, 0.2, 0.21))
    box(A["trim"], sx_ + 3.0, sy_ + 2.8, 1.4, sx_ + 3.2, sy_ + 3.6, 2.8, (0.55, 1.0, 0.0), 6.0)
    K.add_light("hack", "POINT", (sx_ + 4.0, sy_ + 3.0, 2.0), 120.0, (0.55, 1.0, 0.0), size=0.3, group="start")
    # yard container stacks (dressing, seeded, clear of the crane mast, MANIFEST CONTROL and the skyway)
    yr = random.Random(5321)
    for (gx, gy) in ((40, 40), (40, 20), (58, -30), (58, -10), (20, -40), (-40, 38), (-60, 38), (50, 44)):
        n_ = yr.randint(1, 3)
        r_ = dict(o=(gx, gy, 0.0), n=(0.0, 1.0))
        for c in range(n_):
            container(r_, -7.0, 7.0, -5.0, 5.0, c * CRS * 0.95, c * CRS * 0.95 + 8.4)
    log("gate, yard")

    # ------------------------------------------------------------ MANIFEST CONTROL (the server tower)
    cx, cy, hf, H = CTL["c"][0], CTL["c"][1], CTL["half"], CTL["h"]
    vz0 = H - CP["target_h"]
    m1 = G.ROOM["m1"]
    for (fx, fy) in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        fr_ = dict(o=(cx + fx * hf, cy + fy * hf, 0.0), n=(float(fx), float(fy)))
        z = 0.0
        while z < vz0 - 0.5:
            z1 = min(z + 7.0, vz0)
            segs = [(-hf, hf)]
            if (fx, fy) == (0, -1) and z < m1["o"][2] + RH + 0.5 and z1 > m1["o"][2] - 0.5:
                ru = (m1["o"][0] - cx) * -1.0           # the S face's tangent is -x
                segs = [s for s0 in segs for s in ((s0[0], min(s0[1], ru - RW / 2 - 0.3)), (max(s0[0], ru + RW / 2 + 0.3), s0[1]))
                        if s[1] - s[0] > 0.3]
            for (s0, s1) in segs:
                obox(A["glass"], fr_, s0, s1, -RD, -0.2, z + 0.6, z1, (0.012, 0.022, 0.03))
                obox(A["metal"], fr_, s0, s1, -RD, 0.25, z, z + 0.6, (0.14, 0.14, 0.15))
                uu = s0
                while uu < s1 - 0.4:
                    obox(A["metal"], fr_, uu, uu + 0.22, -0.2, 0.22, z + 0.6, z1, (0.16, 0.16, 0.17))
                    uu += 2.4
                if rr.random() < 0.7:
                    oquad(A["trim"], fr_, -0.6, s0 + 0.3, z + 4.6, s1 - 0.3, z + 5.2, YC if rr.random() < 0.6 else YW,
                          LH["slit_k"] * rr.uniform(0.6, 1.4))
            z = z1
    box(A["civic"], cx - hf + RD, cy - hf + RD, 0.0, cx + hf - RD, cy + hf - RD, vz0, (0.10, 0.11, 0.12))
    K.room_shell("m1", m1)
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
    for (fx, fy) in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        fr_ = dict(o=(cx + fx * hf, cy + fy * hf, 0.0), n=(float(fx), float(fy)))
        oquad(A["trim"], fr_, 0.06, -hf, H + 0.6, hf, H + 0.9, YW, LH["trim_k"])
    STEN = {"M": ["10001", "11011", "10101", "10001", "10001"], "E": ["1111", "1000", "1110", "1000", "1111"],
            "R": ["1110", "1001", "1110", "1010", "1001"], "I": ["111", "010", "010", "010", "111"],
            "D": ["1110", "1001", "1001", "1001", "1110"], "A": ["0110", "1001", "1111", "1001", "1001"],
            "N": ["1001", "1101", "1011", "1001", "1001"]}
    for (fx, fy) in ((0, -1), (-1, 0), (0, 1), (1, 0)):
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
                        oquad(A["trim"], fr_, 0.05, -(uu + (cix + 1) * cell - cell * 0.15), z0 + (4 - row) * cell,
                              -(uu + cix * cell), z0 + (5 - row) * cell - cell * 0.15, ORANGE, 6.0 * LH["sign_k"] * 4)
            uu += (len(gph[0]) + 1) * cell
    for (fx, fy) in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        o_ = (cx + fx * (hf + 26.0), cy + fy * (hf + 26.0), 1.0)
        K.add_light("keep_wash_%d_%d" % (fx, fy), "SPOT", o_, LH["keep_w"], SOD if (fx + fy) % 2 else WORK,
                    aim=(cx + fx * hf, cy + fy * hf, H * 0.55), size=2.0, spot=42, blend=0.5, group="corp")
    hooks["beams"].append(((cx, cy, H + 2.5), (0.0, 0.0, 1.0), YC, K.HZ["beams"]["power"] * 1.4, K.HZ["beams"]["cone"] * 1.4))
    log("control tower")

    # ------------------------------------------------------------ static rooms (walls, sally ports, towers)
    for i in G.NODES:
        if i in ("start", "srv", "m1") or (len(i) == 2 and i[0] in "qs" and i[1].upper() in G.WALLS):
            continue
        K.room_shell(i, G.ROOM[i])

    # ------------------------------------------------------------ links: catwalks, ladders, stairs, the skyway
    def walk(path, w=2.2, col=(0.32, 0.33, 0.35), led=True):
        for p, q in zip(path, path[1:]):
            p, q = Vector(p), Vector(q)
            d = q - p
            hz = math.hypot(d.x, d.y)
            if hz < 0.3 and abs(d.z) > 0.5:          # ladder
                side = Vector((1.0, 0.0, 0.0)) if abs(p.y) > abs(p.x) * (WY / WX) else Vector((0, 1, 0))
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
            nrm = Vector((-d.y, d.x, 0.0)).normalized() * (w / 2) if hz > 0.01 else Vector((0, 0, 0))
            tube(A["metal"], p + nrm + Vector((0, 0, -0.5)), q + nrm + Vector((0, 0, -0.5)), 0.06, (0.5, 0.5, 0.52), n=4)
            if abs(d.z) > 2.0 and hz > 2.0:            # stair / gangway posts down to the ground
                for f_ in (0.25, 0.75):
                    c_ = p.lerp(q, f_)
                    if c_.z > 3.0:
                        tube(A["metal"], (c_.x, c_.y, 0.0), (c_.x, c_.y, c_.z - 1.6), 0.25, (0.12, 0.12, 0.13), n=5)

    done = set()
    for e in G.base_edges(["start"], 0) + sum((G.base_edges(["start"], t) for t in range(1, G.CYCLE)), []):
        if e in done:
            continue
        done.add(e)
        a, b_ = e
        if a == "start" or G.edge_type(a, b_) in ("ride", "shuttle"):
            continue
        pth = G.edge_path(a, b_)
        if G.edge_type(a, b_) == "skyway":
            for p, q in zip(pth[1:], pth[2:]):
                K.seg_box(A["metal"], Vector(p) + Vector((0, 0, -1.55)), Vector(q) + Vector((0, 0, -1.55)), 3.2, 0.4,
                          (0.2, 0.2, 0.21))
                K.seg_box(A["glass"], Vector(p) + Vector((0, 0, 2.2)), Vector(q) + Vector((0, 0, 2.2)), 3.2, 0.1,
                          (0.02, 0.03, 0.035))
                K.seg_box(A["trim"], Vector(p) + Vector((0, 0, 2.15)), Vector(q) + Vector((0, 0, 2.15)), 0.3, 0.05, YC,
                          LH["trim_k"])
            walk(pth[:2])
            for p in pth[2:-1]:
                tube(A["metal"], (p[0], p[1], 0.0), (p[0], p[1], p[2] - 1.6), 0.6, (0.12, 0.12, 0.13), n=6)
            continue
        walk(pth)
    # the shuttle links: the catwalk ends at a breach (landings on both sides of the slot) + the ladders
    for w in G.WALLS:
        bk = CP["breach"][w]
        s_ = "s" + w.lower()
        pa = G.edge_path(bk["prev"], s_, _wall_turn(G, w))
        pb = G.edge_path(s_, bk["next"], _wall_turn(G, w))
        walk(pa[:-1])
        walk(pb[1:])
    log("links")

    # ------------------------------------------------------------ the shuttle containers (movers carrying rooms)
    for w in G.WALLS:
        s_ = "s" + w.lower()
        mv = K.mover(s_)
        rec0 = dict(o=(0.0, 0.0, 0.0), n=G.NRM[w], w=RW, h=RH, d=RD)
        K.mover_room(s_, s_, rec0)
        # the container shell round the room: roof, sides (hazard yellow-black: a shuttle reads at a glance)
        obox(mv["accs"]["struct"], rec0, -RW / 2 - 0.5, RW / 2 + 0.5, -RD - 0.4, 0.4, RH + 0.3, RH + 1.0, (0.45, 0.28, 0.02))
        for s2 in (-1, 1):
            obox(mv["accs"]["rough"], rec0, s2 * (RW / 2 + 0.25) - 0.25, s2 * (RW / 2 + 0.25) + 0.25, -RD - 0.4, 0.4, -0.4,
                 RH + 0.3, (0.45, 0.28, 0.02))
        for uu in range(-7, 7, 2):
            oquad(mv["accs"]["trim"], rec0, 0.42, uu, RH + 0.35, uu + 1.0, RH + 0.95, (1.0, 0.55, 0.02), 1.4)
        obox(mv["accs"]["small"], rec0, -0.5, 0.5, -RD / 2 - 0.5, -RD / 2 + 0.5, RH + 1.0, RH + 1.8, HAZ, 14.0)
        # the spreader's twist-lock frame on the roof (for the crane's hook)
        obox(mv["accs"]["metal"], rec0, -RW / 2, RW / 2, -RD / 2 - 0.6, -RD / 2 + 0.6, RH + 1.0, RH + 1.5, (0.2, 0.2, 0.22))
        bl = K.add_light("beacon_" + s_, "POINT", (0.0, 0.0, RH + 2.4), LH["beacon_w"], HAZ, size=0.4, group="corp",
                         shadow=False)
        nn_ = G.NRM[w]
        bl.location = (-nn_[0] * RD / 2, -nn_[1] * RD / 2, RH + 2.4)
        hooks["mover_lights"][s_] = [(bl, tuple(bl.location))]
    hooks["local_rec"] = lambda i: dict(o=(0.0, 0.0, 0.0), n=G.NRM[i[1].upper()], w=RW, h=RH, d=RD)
    log("shuttles")

    # ------------------------------------------------------------ the KEEP CRANE (slewing): the landmark silhouette
    cr = CP["crane"]
    mx, my, mz = cr["x"], cr["y"], cr["z"]
    ms = cr["mast"] / 2
    CRANE = (0.34, 0.10, 0.045)
    # the mast: 4 legs + X braces every 8 BU, hazard bands at the foot, a lit edge line
    for (dx, dy) in ((-ms, -ms), (ms, -ms), (ms, ms), (-ms, ms)):
        box(STRIPE, mx + dx - 0.5, my + dy - 0.5, 0.0, mx + dx + 0.5, my + dy + 0.5, mz - 4.0, CRANE)
    z = 2.0
    while z < mz - 6.0:
        for (a_, b_) in (((-ms, -ms), (ms, -ms)), ((ms, -ms), (ms, ms)), ((ms, ms), (-ms, ms)), ((-ms, ms), (-ms, -ms))):
            tube(A["metal"], (mx + a_[0], my + a_[1], z), (mx + b_[0], my + b_[1], z + 8.0), 0.18, CRANE, n=4)
            tube(A["metal"], (mx + b_[0], my + b_[1], z), (mx + a_[0], my + a_[1], z + 8.0), 0.18, CRANE, n=4)
        z += 8.0
    for q in range(6):
        box(STRIPE, mx - ms - 0.6, my - ms - 0.6, q * 1.2, mx + ms + 0.6, my + ms + 0.6, q * 1.2 + 0.6,
            (0.9, 0.55, 0.02) if q % 2 == 0 else (0.02, 0.02, 0.02))
    for (dx, dy) in ((-ms, -ms), (ms, ms)):
        tube(A["trim"], (mx + dx * 1.15, my + dy * 1.15, 4.0), (mx + dx * 1.15, my + dy * 1.15, mz - 4.0), 0.1, WORK,
             LH["boom_k"] * 0.7, n=4)
    for (dx, dy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        K.add_light("crane_up_%d_%d" % (dx, dy), "SPOT", (mx + dx * 14.0, my + dy * 14.0, 0.5), LH["flood_w"] * 0.45, YW,
                    aim=(mx, my, mz * 0.6), size=0.8, spot=24, blend=0.5, group="corp")
    # the slewing head (jib + counter-jib + cab + apex) built in LOCAL coordinates (x = along the jib), rotated per
    # frame about the mast axis
    JIB = {k: Acc("crane_jib_" + k, mt_, 1, K.COLL["compound"]) for k, mt_ in
           (("st", K.M["rough"]), ("metal", K.M["metal"]), ("trim", K.M["emit"]), ("small", K.M["emit"]))}
    L, Lc = cr["jib"], cr["counter"]
    for s_ in (-1, 1):                               # two bottom chords + the top chord (a triangular lattice)
        box(JIB["st"], -Lc, s_ * 2.2 - 0.4, -0.4, L, s_ * 2.2 + 0.4, 0.4, CRANE)
        box(JIB["trim"], -Lc, s_ * 2.62 - 0.05, -0.2, L, s_ * 2.62 + 0.05, 0.2, WORK, LH["boom_k"])
    box(JIB["st"], -Lc * 0.5, -0.4, 3.6, L * 0.92, 0.4, 4.4, CRANE)
    x = -Lc
    while x < L - 4.0:
        for s_ in (-1, 1):
            tube(JIB["metal"], (x, s_ * 2.2, 0.0), (x + 4.0, 0.0, 4.0), 0.14, CRANE, n=4)
            tube(JIB["metal"], (x + 4.0, 0.0, 4.0), (x + 8.0, s_ * 2.2, 0.0), 0.14, CRANE, n=4)
        x += 8.0
    box(JIB["st"], -ms - 1.0, -ms - 1.0, -4.0, ms + 1.0, ms + 1.0, 0.0, (0.2, 0.2, 0.22))            # the slewing ring
    box(JIB["st"], -ms - 0.5, ms + 1.0, -6.0, ms + 3.0, ms + 6.0, -0.5, (0.25, 0.25, 0.27))         # the cab
    box(JIB["trim"], ms + 3.05, ms + 1.5, -5.2, ms + 3.1, ms + 5.5, -1.5, YW, 3.0)
    # the apex (cat head) + pendant ties to the jib and the counter-jib
    box(JIB["st"], -1.0, -1.0, 0.0, 1.0, 1.0, 22.0, CRANE)
    for xe in (L * 0.55, L * 0.95):
        tube(JIB["metal"], (0.0, 0.0, 22.0), (xe, 0.0, 4.4), 0.2, (0.35, 0.35, 0.35), n=4)
    tube(JIB["metal"], (0.0, 0.0, 22.0), (-Lc, 0.0, 0.4), 0.2, (0.35, 0.35, 0.35), n=4)
    for q in range(4):                               # counterweights
        box(JIB["st"], -Lc + 1.0 + q * 2.4, -2.6, -6.0, -Lc + 3.2 + q * 2.4, 2.6, -0.5, (0.18, 0.18, 0.2))
    x = 0.0
    while x <= L:                                    # red lamps along the jib, white strobes at the tip and the apex
        box(JIB["small"], x - 0.3, -0.3, 4.4, x + 0.3, 0.3, 5.0, RED, 8.0)
        x += 16.0
    box(JIB["small"], L - 0.8, -0.8, 0.4, L + 0.8, 0.8, 1.6, (1.0, 1.0, 1.0), 25.0)
    box(JIB["small"], -0.7, -0.7, 22.0, 0.7, 0.7, 23.4, RED, 14.0)
    # MERIDIAN on the counter-jib's ballast (both sides, orange)
    for s_ in (-1, 1):
        box(JIB["trim"], -Lc + 1.0, s_ * 2.65 - 0.03, -5.0, -Lc + 10.6, s_ * 2.65 + 0.03, -1.5, ORANGE, LH["logo_k"])
    for k_, acc in JIB.items():
        hooks["accs"]["crane_jib_" + k_] = acc
    # the trolley + the spreader (the hook) + the cables: positioned per frame
    TROL = Acc("crane_trolley", K.M["rough"], 1, K.COLL["compound"])
    box(TROL, -2.5, -2.6, -2.0, 2.5, 2.6, -0.2, (0.18, 0.18, 0.2))
    hooks["accs"]["crane_trolley"] = TROL
    hk = K.mover("hook")
    obox(hk["accs"]["struct"], dict(o=(0, 0, 0), n=(0.0, 1.0)), -RW / 2 - 0.6, RW / 2 + 0.6, -RD / 2 - 1.0, RD / 2 + 1.0,
         0.0, 1.0, (0.45, 0.28, 0.02))
    obox(hk["accs"]["small"], dict(o=(0, 0, 0), n=(0.0, 1.0)), -0.5, 0.5, -0.5, 0.5, 1.0, 1.8, HAZ, 12.0)
    hs_ = K.add_light("hook_spot", "SPOT", (0.0, 0.0, -0.5), LH["hook_spot_w"], (1.0, 0.92, 0.8), aim=(0.0, 0.0, -50.0),
                      size=0.5, spot=26, blend=0.4, group="corp")
    hooks["mover_lights"]["hook"] = [(hs_, (0.0, 0.0, -0.5))]
    cab = Acc("cable", K.M["metal"], 6, K.COLL["movers"])
    for (dx, dy) in ((-1.6, -1.6), (1.6, -1.6), (-1.6, 1.6), (1.6, 1.6)):
        tube(cab, (dx, dy, 0.0), (dx, dy, 1.0), 0.1, (0.2, 0.2, 0.2), n=4)
    hooks["accs"]["cable"] = cab
    hl_ = K.add_light("crane_tip_flood", "SPOT", (0, 0, 0), LH["flood_w"] * 0.6, YC, aim=(0, 0, -1), size=1.0, spot=60,
                      blend=0.6, group="corp")
    log("keep crane")

    # ============================================================ THE LANDMARK RIG (review: Meridian under target)
    # 1. lit seams under every container course, all four walls (the run uses them all now) + the towers
    for side in G.WALLS:
        rec = wall_frame(side)
        L_ = wall_len(side)
        for c in range(1, NC + 1):
            oquad(A["trim"], rec, 0.06, -L_, c * CRS - 1.0, L_, c * CRS - 0.82, WORK, LH["seam_k"])
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx_, cy_ = sx * TC[0], sy * TC[1]
            for (fx, fy) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                rb = dict(o=(cx_ + fx * (TH_ + 0.05), cy_ + fy * (TH_ + 0.05), 0.0), n=(float(fx), float(fy)))
                for c in range(1, TCO + 1):
                    oquad(A["trim"], rb, 0.0, -TH_, c * CRS - 1.0, TH_, c * CRS - 0.8, WORK, LH["seam_k"] * 0.8)
            for (fx, fy) in ((sx, 0), (0, sy)):
                rb = dict(o=(cx_ + fx * (TH_ + 0.3), cy_ + fy * (TH_ + 0.3), 0.0), n=(float(fx), float(fy)))
                z_ = 2 * CRS + 1.0
                oquad(A["trim"], rb, 0.0, -6.0, z_, 6.0, z_ + 6.0, ORANGE, LH["logo_k"])
                oquad(A["trim"], rb, 0.02, -6.0, z_ + 2.6, 6.0, z_ + 3.4, (1.0, 0.95, 0.9), LH["logo_k"] * 1.2)
    # 2. orange work lights along every wall, from the platform edge, washing the containers
    for side in G.WALLS:
        rec = wall_frame(side)
        L_ = wall_len(side)
        uu = -L_ + 8.0
        while uu < L_ - 4:
            K.add_light("work_%s_%d" % (side, uu), "SPOT", rf(rec, PD0 - 2.0, uu, 3.0), LH["work_w"], WORK,
                        aim=rf(rec, 0.0, uu, 16.0), size=0.8, spot=60, blend=0.8, group="corp")
            uu += 16.0
    # 3. flood towers on the corner towers aimed into the yard (sodium)
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = TCO * CRS + 16.0
            o_ = (sx * TC[0], sy * TC[1], top)
            K.add_light("ftower_%d_%d" % (sx, sy), "SPOT", o_, LH["tower_flood_w"], SOD,
                        aim=(sx * TC[0] * 0.2, sy * TC[1] * 0.2, 0.0), size=1.5, spot=75, blend=0.6, group="corp")
            box(A["trim"], o_[0] - 1.6, o_[1] - 1.6, top - 1.2, o_[0] + 1.6, o_[1] + 1.6, top - 0.2, SOD, 8.0)
    # 4. the track: a sodium glow strip along the loop (low area lights per side)
    for side in G.WALLS:
        p = G.wall_pt(side, 0.0, TRK)
        horiz = side in ("N", "S")
        K.add_light("rail_glow_" + side, "AREA", (p[0], p[1], 9.0), LH["sodium_w"] * 6, SOD, aim=(p[0], p[1], 0.0),
                    size=(2 * WX + 30) if horiz else 8.0, size_y=8.0 if horiz else (2 * WY + 30), group="corp")
    # 5. rim: the city glow behind grazes the landmark only (light-linked), from two diagonals
    RIMRX = bpy.data.collections.new("rim_rx")
    for k, (rx, ry, col_) in enumerate(((-150.0, -200.0, "district_a"), (180.0, 150.0, "district_b"))):
        K.add_light("rim_%d" % k, "AREA", (rx, ry, 40.0), LH["rim_w"], pal(col_), aim=(0.0, 0.0, 25.0),
                    size=120.0, size_y=50.0, group="corp", shadow=False, receivers=RIMRX)

    def post_build(OBJ):
        for name, ob in OBJ.items():
            if ob is not None and any(c.name in ("compound", "movers") for c in ob.users_collection):
                RIMRX.objects.link(ob)
        for k_ in JIB:
            ob = OBJ.get("crane_jib_" + k_)
            if ob is not None:
                ob.location = (mx, my, mz)
    hooks["post_build"] = post_build
    log("rig")

    def apply(fr, ctx):
        mt = fr.get("mt") or 0.0
        hp, carrying = G.crane_target(mt)
        mv = fr.get("movers") or {}
        hp = mv.get("hook", hp)
        yaw = math.atan2(hp[1] - my, hp[0] - mx)
        rad = math.hypot(hp[0] - mx, hp[1] - my)
        OBJ = ctx["OBJ"]
        for k_ in JIB:
            ob = OBJ.get("crane_jib_" + k_)
            if ob is not None:
                ob.location = (mx, my, mz)
                ob.rotation_euler = (0.0, 0.0, yaw)
        tz = mz - 0.4
        tr_ = OBJ.get("crane_trolley")
        if tr_ is not None:
            tr_.location = (mx + math.cos(yaw) * rad, my + math.sin(yaw) * rad, tz)
            tr_.rotation_euler = (0.0, 0.0, yaw)
        # the spreader sits at hp (the hook mover is placed by the kit); the cables from the trolley down to it
        cb = OBJ.get("cable")
        if cb is not None:
            cb.location = (hp[0], hp[1], hp[2] + 1.0)
            cb.scale = (1.0, 1.0, max(0.5, tz - 2.0 - hp[2] - 1.0))
            cb.rotation_euler = (0.0, 0.0, yaw)
        for (lob, e0, grp) in ctx["LIGHTS"]:
            if lob.name == "crane_tip_flood":
                lob.location = (mx + math.cos(yaw) * (rad + 6.0), my + math.sin(yaw) * (rad + 6.0), mz - 1.0)
                lob.rotation_euler = (Vector((hp[0], hp[1], 0.0)) - Vector(lob.location)).to_track_quat("-Z", "Y").to_euler()
            elif lob.name.startswith("beacon_s"):
                lob.data.energy = e0 * (1.6 if carrying and ("s" + carrying.lower()) in lob.name else 1.0)
    hooks["apply"] = apply
    return hooks


def _wall_turn(G, w):
    """A turn at which breach w's shuttle sits in the wall (for the static catwalk landings)."""
    for t in range(G.CYCLE):
        if G.shuttle_at(w, t) == "wall":
            return t
    return 0
# MER_SPEC
# MER_GRADE
