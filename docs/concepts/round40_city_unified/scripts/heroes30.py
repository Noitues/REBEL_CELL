# Round 30: the LOCKED Meridian fortress (round 29 A) + rail yard, finer detailing, faceted moat water, and the
# moving parts (crane boom / trolley / container, passing freight train) built once PER ANIMATION FRAME into their
# own accumulators (MOVE_FRAMES), so hq_scene.py "anim" can toggle them like the Solace chaser.
# NOT a module: exec()'d after heroes29.py.

NFRAMES = 16
ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
MOVE_FRAMES = []          # per frame: dict(solid=Acc, lit=Acc, neon=Acc)
TRACK_Y = (34.0, 40.0)   # world y of the loading track (under the boom) and the through track
S30 = 18.0


def _swap(group):
    global SOLID, LIT, NEON
    old = (SOLID, LIT, NEON)
    SOLID, LIT, NEON = group["solid"], group["lit"], group["neon"]
    return old


def _restore(old):
    global SOLID, LIT, NEON
    SOLID, LIT, NEON = old


# ------------------------------------------------------------------ rail yard
def rails(y, x0=-90, x1=90):
    for dy in (-0.75, 0.75):
        beam((x0, y + dy, 0.35), (x1, y + dy, 0.35), 0.22, (0.62, 0.62, 0.66))
    for x in range(int(x0), int(x1), 2):
        box(x - 0.3, y - 1.3, 0.05, x + 0.3, y + 1.3, 0.25, (0.22, 0.17, 0.13), facet=False)
    strip(SOLID, (x0, y), (x1, y), 3.6, 0.03, (0.20, 0.18, 0.18))  # ballast bed


def rail_yard():
    for y in TRACK_Y:
        rails(y)
    for x in range(-60, 61, 24):  # catenary-free yard lights on masts between the tracks
        beam((x, 37, 0), (x, 37, 9), 0.3, (0.3, 0.3, 0.34))
        box(x - 0.8, 36.6, 9, x + 0.8, 37.4, 9.6, (0.9, 0.9, 0.85), facet=False)
        NEON.face([(x - 0.8, 36.5, 9.0), (x + 0.8, 36.5, 9.0), (x + 0.8, 37.5, 9.0), (x - 0.8, 37.5, 9.0)], (1.0, 0.85, 0.55), (0, 0, 0))
    for x in (-24, 24):  # signals
        beam((x, 31.8, 0), (x, 31.8, 5), 0.25, (0.2, 0.2, 0.22))
        NEON.face([(x - 0.4, 31.7, 4.4), (x + 0.4, 31.7, 4.4), (x + 0.4, 31.7, 5.2), (x - 0.4, 31.7, 5.2)], (0.3, 1.0, 0.4), (0, 0, 0))


def flatcar(x, y, conts, liv=None):
    box(x - 7, y - 1.4, 1.0, x + 7, y + 1.4, 1.6, (0.20, 0.18, 0.18), facet=False)
    for wx in (-5, -3.6, 3.6, 5):
        box(x + wx - 0.5, y - 1.5, 0.4, x + wx + 0.5, y + 1.5, 1.0, (0.10, 0.10, 0.10), facet=False)
    for i, c in enumerate(conts):
        if c:
            obox(x, y, 1.6, 12.0, 2.6 * 0 + 2.5, HC * 0.8, 0, c)


def locomotive(x, y, d=1):
    box(x - 8, y - 1.6, 1.0, x + 8, y + 1.6, 6.0, (1.0, 0.50, 0.10))
    box(x + d * 5.0 - 2.5, y - 1.7, 6.0, x + d * 5.0 + 2.5, y + 1.7, 8.0, (0.86, 0.84, 0.80))
    for wx in (-6, -4, 4, 6):
        box(x + wx - 0.6, y - 1.7, 0.4, x + wx + 0.6, y + 1.7, 1.2, (0.10, 0.10, 0.10), facet=False)
    WIN.face([(x + d * 7.5, y - 1.2, 6.3), (x + d * 7.5, y + 1.2, 6.3), (x + d * 7.5, y + 1.2, 7.6), (x + d * 7.5, y - 1.2, 7.6)], (1.0, 0.85, 0.5), (0, 0, 0))
    NEON.face([(x + d * 8.05, y - 0.9, 2.0), (x + d * 8.05, y + 0.9, 2.0), (x + d * 8.05, y + 0.9, 3.0), (x + d * 8.05, y - 0.9, 3.0)], (1.0, 0.95, 0.8), (0, 0, 0))
    for k in range(8):  # hazard chevrons on the nose
        z = 1.2 + k * 0.6
        (NEON if k % 2 else SOLID).face([(x + d * 8.03, y - 1.6, z), (x + d * 8.03, y + 1.6, z), (x + d * 8.03, y + 1.6, z + 0.3), (x + d * 8.03, y - 1.6, z + 0.3)],
                                        (1.0, 0.8, 0.1) if k % 2 else (0.05, 0.05, 0.05), (0, 0, 0))


CONT_LIV = [(0.86, 0.42, 0.10), (0.16, 0.36, 0.62), (0.15, 0.48, 0.46), (0.72, 0.20, 0.12), (0.80, 0.78, 0.72)]


def freight_train(x0, y, n=6, loaded=None, d=1):
    locomotive(x0, y, d)
    for i in range(n):
        x = x0 - d * (17 + i * 15)
        c = CONT_LIV[(i * 3) % 5] if (loaded is None or loaded[i]) else None
        flatcar(x, y, [c])


# ------------------------------------------------------------------ detailing on the fortress
def bolts_ladders_catwalks():
    S = S30
    ladder_x = S + 5.6
    for sy in (-1, 1):  # ladders up the two front corner towers and the gate towers
        for (x, y, top) in ((ladder_x, sy * (S - 2.5), 4 * HC), (S + 3.6, sy * 9.5, 3 * HC)):
            for dy in (-0.5, 0.5):
                beam((x, y + dy, 0.5), (x, y + dy, top), 0.14, (0.75, 0.72, 0.68))
            for z in range(1, int(top), 1):
                beam((x, y - 0.5, z), (x, y + 0.5, z), 0.1, (0.75, 0.72, 0.68))
    for sy in (-1, 1):  # catwalk along the front wall top with railing + lamps
        y0, y1 = sy * 5.5, sy * (S - 6)
        z = 2 * HC + 0.4
        box(S - 3.6, min(y0, y1), z - 0.2, S - 1.6, max(y0, y1), z, (0.30, 0.28, 0.28), facet=False)
        for zz in (z + 0.9, z + 0.5):
            beam((S - 1.6, y0, zz), (S - 1.6, y1, zz), 0.08, (0.8, 0.78, 0.74))
        for k in range(5):
            y = y0 + (y1 - y0) * k / 4
            beam((S - 1.6, y, z), (S - 1.6, y, z + 0.95), 0.1, (0.8, 0.78, 0.74))
            NEON.face([(S - 1.55, y - 0.25, z + 1.4), (S - 1.55, y + 0.25, z + 1.4), (S - 1.55, y + 0.25, z + 1.8), (S - 1.55, y - 0.25, z + 1.8)], (1.0, 0.85, 0.5), (0, 0, 0))
    rr = random.Random(30)
    for sx in (-1, 1):  # bolts on tower corners (small steel caps in rows)
        for sy in (-1, 1):
            cx, cy = sx * S, sy * S
            for z in range(1, 4 * int(HC), 3):
                for (dx, dy) in ((5.6, -5.6), (5.6, 5.6)):
                    x, y = cx + dx * (1 if sx > 0 else -1) * 0.98, cy + dy * 0.98
                    box(x - 0.18, y - 0.18, z, x + 0.18, y + 0.18, z + 0.36, (0.80, 0.78, 0.74), facet=False)
    for sy in (-1, 1):  # warning lamps at the gate
        NEON.face([(S + 3.55, sy * 3.4 - 0.3, 6.2), (S + 3.55, sy * 3.4 + 0.3, 6.2), (S + 3.55, sy * 3.4 + 0.3, 6.8), (S + 3.55, sy * 3.4 - 0.3, 6.8)], (1.0, 0.25, 0.15), (0, 0, 0))


def faceted_water(S_in, S_out, cell=1.6):
    """Low-poly moat surface: a triangulated grid with height jitter and tone variation; facets near the lit towers
    and gate catch the light (bright orange glints), others stay deep blue."""
    rr = random.Random(3030)
    lights = [(S30 + 5.5, -S30), (S30 + 5.5, S30), (S30 + 3.5, -6.6), (S30 + 3.5, 6.6), (S30 + 3.5, 0)]

    def zf(x, y):
        return 0.06 + 0.12 * math.sin(x * 0.9 + y * 0.4) * math.cos(y * 0.7 - x * 0.2)

    def tone(x, y):
        k = max(0.0, 1.0 - min(math.hypot(x - lx, y - ly) for lx, ly in lights) / 9.0)
        if rr.random() < 0.10 + 0.5 * k:
            return (1.0 * (0.25 + 0.6 * k), 0.50 * (0.25 + 0.6 * k), 0.12 * (0.3 + 0.5 * k))
        v = rr.uniform(0.7, 1.4)
        return (0.03 * v, 0.06 * v, 0.11 * v)
    n = int((2 * S_out) / cell)
    for i in range(n):
        for j in range(n):
            x0, y0 = -S_out + i * cell, -S_out + j * cell
            x1, y1 = x0 + cell, y0 + cell
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            if max(abs(cx), abs(cy)) < S_in or max(abs(cx), abs(cy)) > S_out:
                continue
            if cx > S30 + 3 and abs(cy) < 3.6:  # under the drawbridge
                continue
            p = [(x0, y0, zf(x0, y0)), (x1, y0, zf(x1, y0)), (x1, y1, zf(x1, y1)), (x0, y1, zf(x0, y1))]
            NEON.face([p[0], p[1], p[2]], tone(cx, cy), (0, 0, 0))
            NEON.face([p[0], p[2], p[3]], tone(cx, cy), (0, 0, 0))


# ------------------------------------------------------------------ the moving crane (one copy per frame)
def crane_dyn(boom_deg, t_local, cont_z, carry, cont_col=(0.15, 0.48, 0.46)):
    """heroes29.crane with the boom angle, trolley position (local x along the boom axis) and load as parameters."""
    LEG = (1.0, 0.52, 0.10)
    sx_, sy_ = 7.0, 9.0
    zp = 30.0
    for x in (-sx_, sx_):
        for y in (-sy_, sy_):
            beam((x, y, 0), (x, y, zp), 3.2, LEG, acc=LIT)
            box(x - 2.2, y - 2.6, 0, x + 2.2, y + 2.6, 1.6, (0.18, 0.16, 0.16), facet=False)
            for z in range(3, int(zp), 4):  # rivet/bolt rings on the legs
                box(x - 1.75, y - 1.75, z, x + 1.75, y + 1.75, z + 0.25, (0.80, 0.42, 0.10), facet=False)
        beam((x, -sy_, zp), (x, sy_, zp), 2.2, LEG, acc=LIT)
        beam((x, -sy_, 14), (x, sy_, 14), 1.4, LEG, acc=LIT)
        beam((x, -sy_, 14), (x, sy_ * 0.2, zp), 0.8, (0.70, 0.36, 0.08))
        beam((x, sy_, 14), (x, -sy_ * 0.2, zp), 0.8, (0.70, 0.36, 0.08))
        for z in range(2, int(zp), 2):  # ladder up one leg
            beam((x - 1.9, -sy_ - 0.6, z), (x - 1.9, -sy_ + 0.6, z), 0.1, (0.85, 0.82, 0.78))
    for y in (-sy_, sy_):
        beam((-sx_, y, zp), (sx_, y, zp), 2.2, LEG, acc=LIT)
    box(-sx_ - 1, -4, zp + 1.1, sx_ * 0.4, 4, zp + 7, (0.86, 0.84, 0.80))
    windows(-sx_ - 1, -4, zp + 1.1, sx_ * 0.4, 4, zp + 7, p=0.6, cols=[(1.0, 0.78, 0.45)])
    apex = (1.0, 0, zp + 18)
    for y in (-sy_, sy_):
        beam((-sx_, y, zp + 1), apex, 1.6, LEG, acc=LIT)
        beam((sx_, y, zp + 1), apex, 1.6, LEG, acc=LIT)
    NEON.face([(apex[0] - 0.8, -0.8, apex[2] + 1.45), (apex[0] + 0.8, -0.8, apex[2] + 1.45), (apex[0] + 0.8, 0.8, apex[2] + 1.45), (apex[0] - 0.8, 0.8, apex[2] + 1.45)], RED, (0, 0, 0))
    box(apex[0] - 0.7, -0.7, apex[2], apex[0] + 0.7, 0.7, apex[2] + 1.4, RED, facet=False)
    hinge = Vector((sx_, 0, zp + 3))
    back_tip = Vector((-sx_ - 14, 0, zp + 3))
    a = math.radians(boom_deg)
    dirv = Vector((math.cos(a), 0, math.sin(a)))
    tip = hinge + dirv * 36
    for y in (-2.2, 2.2):
        hazard_beam(tuple(hinge + Vector((0, y, 0))), tuple(tip + Vector((0, y * 0.7, 0))), 2.2, seg=2.6)
        hazard_beam(tuple(back_tip + Vector((0, y, 0))), tuple(hinge + Vector((-2 * sx_, y, 0))), 1.6, seg=2.6)
        beam(tuple(hinge + Vector((0, y, 0))), tuple(hinge + Vector((-2 * sx_, y, 0))), 1.6, LEG, acc=LIT)
    for k in range(13):
        p = hinge.lerp(tip, k / 12)
        beam(tuple(p + Vector((0, -2.2, 0))), tuple(p + Vector((0, 2.2, 0))), 0.35, (0.30, 0.28, 0.28))
        if k % 3 == 1:
            NEON.face([tuple(p + Vector((-0.3, -0.3, -1.3))), tuple(p + Vector((0.3, -0.3, -1.3))), tuple(p + Vector((0.3, 0.3, -1.3))), tuple(p + Vector((-0.3, 0.3, -1.3)))],
                      (1.0, 0.85, 0.5), (0, 0, 0))
    beam(tuple(hinge), tuple(tip), 0.25, BATTLE, acc=NEON)
    for e in (tip, back_tip):
        for y in (-2.0, 2.0):
            beam(apex, tuple(e + Vector((0, y, 0.6))), 0.35, (0.75, 0.72, 0.68))
        box(e.x - 0.6, -0.6, e.z + 0.8, e.x + 0.6, 0.6, e.z + 1.8, RED, facet=False)
    box(back_tip.x - 1, -3.2, back_tip.z - 4, back_tip.x + 4, 3.2, back_tip.z - 0.4, (0.24, 0.22, 0.22))
    if t_local >= sx_:
        tp = hinge + dirv * (t_local - sx_)
    else:
        tp = Vector((t_local, 0, zp + 3))
    box(tp.x - 2.2, -2.6, tp.z - 1.6, tp.x + 2.2, 2.6, tp.z + 0.4, (0.84, 0.82, 0.78))
    NEON.face([(tp.x - 2.25, -2.0, tp.z - 1.65), (tp.x + 2.25, -2.0, tp.z - 1.65), (tp.x + 2.25, 2.0, tp.z - 1.65), (tp.x - 2.25, 2.0, tp.z - 1.65)], (1.0, 0.92, 0.75), (0, 0, 0))
    sz = cont_z + HC * 0.8 + 0.4
    for (dx, dy) in ((-1.6, -1.6), (1.6, -1.6), (-1.6, 1.6), (1.6, 1.6)):
        beam((tp.x + dx * 0.6, dy * 0.6, tp.z - 1.6), (tp.x + dx, dy * 1.4, sz + 0.6), 0.14, (0.15, 0.15, 0.16))
    box(tp.x - 1.6, -6.2, sz, tp.x + 1.6, 6.2, sz + 0.8, (1.0, 0.82, 0.10))
    if carry:
        obox(tp.x, 0, cont_z, 12.0, 2.5, HC * 0.8, math.pi / 2, cont_col)  # along world x after the turn, like the flatcars


# A 16-frame loop (world y = crane-local x after the 90 degree turn): pick a container in the yard (y 6), carry it out
# over the wall and the moat, set it on the waiting flatcar at y 34, return empty while the boom lifts and settles;
# a through train passes on y 40 in the second half.
def crane_frame(f):
    if f < 6:                      # carry outward
        u = f / 5
        return dict(boom=0.0, t=6 + (34 - 6) * u, cz=14.0, carry=True)
    if f < 8:                      # lower onto the flatcar
        u = (f - 5) / 2
        return dict(boom=0.0, t=34, cz=14.0 - (14.0 - 2.2) * min(1, u), carry=True)
    if f < 12:                     # return, boom lifting
        u = (f - 7) / 4
        return dict(boom=24 * math.sin(math.pi * u), t=34 - (34 - 6) * u, cz=14.0, carry=False)
    u = (f - 11) / 4               # boom settles, pick the next container
    return dict(boom=0.0, t=6, cz=14.0 - 7 * math.sin(math.pi * u), carry=f >= 14)


def train_frame(f):
    """Through train x position on track 2 (None = not in view)."""
    if f < 6:
        return None
    return -150 + (f - 6) * 26


def fort_v30():
    fort_v29_static()
    bolts_ladders_catwalks()
    faceted_water(S30 + 6.2, S30 + 11.5)
    rail_yard()
    # the waiting loading train (static): flatcars under the boom, the next one loaded later in the loop
    loaded = [True, True, False, True, False, True]
    freight_train(47, TRACK_Y[0], n=6, loaded=loaded, d=1)
    for f in range(NFRAMES):
        g = MOVE_FRAMES[f]
        old = _swap(g)
        try:
            c = crane_frame(f)
            build_at(lambda: crane_dyn(c["boom"], c["t"], c["cz"], c["carry"]), rot=90.0)
            if f >= 8:  # the container just set down sits on the flatcar at x 0 (crane-local y = world x)
                obox(0.0, TRACK_Y[0], 1.6, 12.0, 2.5, HC * 0.8, 0, (0.15, 0.48, 0.46))
            tx = train_frame(f)
            if tx is not None:
                freight_train(tx, TRACK_Y[1], n=7, d=1)
        finally:
            _restore(old)


def fort_v29_static():
    """heroes29.fort_v29 without the crane (the crane is per frame now)."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    S = S30
    square_wall(S, 2, gate_w=6.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            sq_tower(sx * S, sy * S, 4, size=11.0, banner=sx > 0)
    sq_gatehouse(S, courses=3, w=6.6, size=7.0, moat=False)
    moat_edges(S + 6.2, S + 11.5)


def moat_edges(S_in, S_out):
    for r in (S_in - 0.3, S_out + 0.3):
        ring = [(-r, -r), (r, -r), (r, r), (-r, r)]
        for p, q in zip(ring, ring[1:] + ring[:1]):
            beam((p[0], p[1], 0.35), (q[0], q[1], 0.35), 0.6, (0.30, 0.26, 0.24))
            beam((p[0], p[1], 0.7), (q[0], q[1], 0.7), 0.15, BATTLE, acc=NEON)


MOVE_FRAMES[:] = [dict(solid=Acc("mv_s%02d" % f), lit=Acc("mv_l%02d" % f), neon=Acc("mv_n%02d" % f)) for f in range(NFRAMES)]
HEROES26["meridian"] = fort_v30
