# Round 29: the Meridian fortress on texture A (round 28 t1), lower and wider, a moat, and a ship-to-shore gantry
# crane as the keep. NOT a module: hq_scene.py exec()s this after heroes28.py (shares every primitive).
# STATE: "raised" (boom up, the keep stands tall) | "lowered" (boom down across the front wall, container over the moat)

TEX.clear()
TEX.update(TEX_VARIANTS["t1"])          # locked texture: raw corrugated steel, unified Meridian orange
WALL_C[:] = TEX["wall"]
TOWER_C[:] = TEX["tower"]
CRANE_STATE = globals().get("STATE", "") or "lowered"
WATER = (0.03, 0.05, 0.09)


def moat(S_in, S_out, gate_w, S=18.0):
    """Square moat ring between S_in and S_out: dark water, ripple lines, and vertical reflection streaks of the lit
    towers / battlements / gate (emissive, so they glow like reflections at night)."""
    for (x0, y0, x1, y1) in ((-S_out, -S_out, S_out, -S_in), (-S_out, S_in, S_out, S_out), (-S_out, -S_in, -S_in, S_in), (S_in, -S_in, S_out, S_in)):
        NEON.face([(x0, y0, 0.06), (x1, y0, 0.06), (x1, y1, 0.06), (x0, y1, 0.06)], WATER, (0, 0, 0))
    for r in (S_in - 0.3, S_out + 0.3):  # stone kerbs with a lit edge
        ring = [(-r, -r), (r, -r), (r, r), (-r, r)]
        for p, q in zip(ring, ring[1:] + ring[:1]):
            beam((p[0], p[1], 0.35), (q[0], q[1], 0.35), 0.6, (0.30, 0.26, 0.24))
        for p, q in zip(ring, ring[1:] + ring[:1]):
            beam((p[0], p[1], 0.7), (q[0], q[1], 0.7), 0.15, BATTLE, acc=NEON)
    rr = random.Random(29)
    for k in range(40):  # ripples
        side = k % 4
        t = rr.uniform(-S_out + 2, S_out - 2)
        d = rr.uniform(S_in + 0.8, S_out - 0.8)
        L = rr.uniform(1.5, 4.0)
        col = (0.10, 0.16, 0.24)
        if side == 0:
            strip(NEON, (t, -d), (t + L, -d), 0.12, 0.08, col)
        elif side == 1:
            strip(NEON, (t, d), (t + L, d), 0.12, 0.08, col)
        elif side == 2:
            strip(NEON, (-d, t), (-d, t + L), 0.12, 0.08, col)
        else:
            strip(NEON, (d, t), (d, t + L), 0.12, 0.08, col)
    # reflections on the front (+X) moat: broken streaks under every lit vertical, toward the camera
    W0, W1 = S_in + 0.4, S_out - 0.4
    for (y, col, w) in ((-S, BATTLE, 3.0), (S, BATTLE, 3.0), (-7.6, BATTLE, 2.2), (7.6, BATTLE, 2.2), (0.0, (1.0, 0.55, 0.12), 3.4),
                        (-12, (0.9, 0.45, 0.12), 1.2), (12, (0.9, 0.45, 0.12), 1.2)):
        if abs(y) < gate_w:
            continue
        x = W0
        seg = 0
        while x < W1:
            L = rr.uniform(0.5, 1.4)
            k = max(0.0, 1.0 - (x - W0) / (W1 - W0)) * 0.75 + 0.15
            ww = w * rr.uniform(0.5, 1.0)
            strip(NEON, (x, y - ww / 2), (min(W1, x + L), y + ww / 2 - ww), ww, 0.09, tuple(c * k for c in col))
            x += L + rr.uniform(0.25, 0.7)
            seg += 1


def crane(state):
    """Ship-to-shore gantry crane, the keep: four heavy legs on a portal, machinery house, A-frame, boom along +X,
    backreach along -X, trolley, spreader and a hanging container. Lit legs (lit toon), hazard-striped boom."""
    LEG = (1.0, 0.52, 0.10)
    sx_, sy_ = 7.0, 9.0
    zp = 30.0
    for x in (-sx_, sx_):
        for y in (-sy_, sy_):
            beam((x, y, 0), (x, y, zp), 3.2, LEG, acc=LIT)
            box(x - 2.2, y - 2.6, 0, x + 2.2, y + 2.6, 1.6, (0.18, 0.16, 0.16), facet=False)  # bogie
        beam((x, -sy_, zp), (x, sy_, zp), 2.2, LEG, acc=LIT)                # portal beams along y
        beam((x, -sy_, 14), (x, sy_, 14), 1.4, LEG, acc=LIT)                # sill beam
        beam((x, -sy_, 14), (x, sy_ * 0.2, zp), 0.8, (0.70, 0.36, 0.08))   # bracing
        beam((x, sy_, 14), (x, -sy_ * 0.2, zp), 0.8, (0.70, 0.36, 0.08))
    for y in (-sy_, sy_):
        beam((-sx_, y, zp), (sx_, y, zp), 2.2, LEG, acc=LIT)
    box(-sx_ - 1, -4, zp + 1.1, sx_ * 0.4, 4, zp + 7, (0.86, 0.84, 0.80))   # machinery house
    windows(-sx_ - 1, -4, zp + 1.1, sx_ * 0.4, 4, zp + 7, p=0.6, cols=[(1.0, 0.78, 0.45)])
    text_obj("MERIDIAN", (sx_ * 0.4 + 0.1, 0, zp + 4.2), (math.radians(90), 0, math.radians(90)), 1.8, SIGNM)
    # A-frame
    apex = (1.0, 0, zp + 18)
    for y in (-sy_, sy_):
        beam((-sx_, y, zp + 1), apex, 1.6, LEG, acc=LIT)
        beam((sx_, y, zp + 1), apex, 1.6, LEG, acc=LIT)
    box(apex[0] - 0.7, -0.7, apex[2], apex[0] + 0.7, 0.7, apex[2] + 1.4, RED, facet=False)
    NEON.face([(apex[0] - 0.8, -0.8, apex[2] + 1.45), (apex[0] + 0.8, -0.8, apex[2] + 1.45), (apex[0] + 0.8, 0.8, apex[2] + 1.45), (apex[0] - 0.8, 0.8, apex[2] + 1.45)], RED, (0, 0, 0))
    hinge = Vector((sx_, 0, zp + 3))
    back_tip = Vector((-sx_ - 14, 0, zp + 3))
    if state == "raised":
        a = math.radians(72)
        tip = hinge + Vector((math.cos(a), 0, math.sin(a))) * 32
    else:
        tip = hinge + Vector((36, 0, 0))
    for y in (-2.2, 2.2):  # twin boom girders, hazard-striped
        hazard_beam(tuple(hinge + Vector((0, y, 0))), tuple(tip + Vector((0, y * 0.7, 0))), 2.2, seg=2.6)
        hazard_beam(tuple(back_tip + Vector((0, y, 0))), tuple(hinge + Vector((-2 * sx_, y, 0))), 1.6, seg=2.6)
        beam(tuple(hinge + Vector((0, y, 0))), tuple(hinge + Vector((-2 * sx_, y, 0))), 1.6, LEG, acc=LIT)
    n = 12  # lattice between the girders
    for k in range(n + 1):
        p = hinge.lerp(tip, k / n)
        beam(tuple(p + Vector((0, -2.2, 0))), tuple(p + Vector((0, 2.2, 0))), 0.35, (0.30, 0.28, 0.28))
    beam(tuple(hinge), tuple(tip), 0.25, BATTLE, acc=NEON)  # lit strip along the boom underside
    for e in (tip, back_tip):  # tie rods to the apex
        for y in (-2.0, 2.0):
            beam(apex, tuple(e + Vector((0, y, 0.6))), 0.35, (0.75, 0.72, 0.68))
    for e in (tip, back_tip):
        box(e.x - 0.6, -0.6, e.z + 0.8, e.x + 0.6, 0.6, e.z + 1.8, RED, facet=False)
        NEON.face([(e.x - 0.7, -0.7, e.z + 1.85), (e.x + 0.7, -0.7, e.z + 1.85), (e.x + 0.7, 0.7, e.z + 1.85), (e.x - 0.7, 0.7, e.z + 1.85)], RED, (0, 0, 0))
    box(back_tip.x - 1, -3.2, back_tip.z - 4, back_tip.x + 4, 3.2, back_tip.z - 0.4, (0.24, 0.22, 0.22))  # counterweight
    # trolley + spreader + container
    if state == "raised":
        tp = Vector((-sx_ - 7, 0, zp + 3))
        cz = 12.0
        cc = (0.16, 0.36, 0.62)
    else:
        tp = hinge + Vector((22, 0, 0))
        cz = 12.0
        cc = (0.15, 0.48, 0.46)
    box(tp.x - 2.2, -2.6, tp.z - 1.6, tp.x + 2.2, 2.6, tp.z + 0.4, (0.84, 0.82, 0.78))
    NEON.face([(tp.x - 2.25, -2.0, tp.z - 1.65), (tp.x + 2.25, -2.0, tp.z - 1.65), (tp.x + 2.25, 2.0, tp.z - 1.65), (tp.x - 2.25, 2.0, tp.z - 1.65)], (1.0, 0.92, 0.75), (0, 0, 0))
    sz = cz + HC + 1.2
    for (dx, dy) in ((-1.6, -1.6), (1.6, -1.6), (-1.6, 1.6), (1.6, 1.6)):
        beam((tp.x + dx * 0.6, dy * 0.6, tp.z - 1.6), (tp.x + dx, dy * 1.4, sz + 0.6), 0.14, (0.15, 0.15, 0.16))
    box(tp.x - 6.2, -1.6, sz, tp.x + 6.2, 1.6, sz + 0.8, (1.0, 0.82, 0.10))  # spreader
    obox(tp.x, 0, cz, 12.0, 4.8, HC, 0, cc)
    cone(Vector((tp.x, 0, tp.z - 1.7)), Vector((tp.x, 0, cz + HC + 0.9)), 0.8, 3.2, (0.55, 0.48, 0.32), n=10)


def fort_v29():
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    S = 18.0
    square_wall(S, 2, gate_w=6.0)                       # lower curtain: 2 courses
    for sx in (-1, 1):
        for sy in (-1, 1):
            sq_tower(sx * S, sy * S, 4, size=11.0, banner=sx > 0)   # squat corner towers: 4 courses, wider
    sq_gatehouse(S, courses=3, w=6.6, size=7.0, moat=False)
    moat(S + 6.2, S + 11.5, 4.0)
    build_at(lambda: crane(CRANE_STATE), rot=90.0)  # boom across the view (+Y): the crane reads side-on from the gate camera


HEROES26["meridian"] = fort_v29
