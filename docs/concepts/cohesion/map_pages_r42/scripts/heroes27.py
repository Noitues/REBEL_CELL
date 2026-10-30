# Round 27 builders. NOT a module: hq_scene.py exec()s this after heroes26.py (shares every primitive).
# MERIDIAN: angular container FORTRESS takes (no round shapes). HALCYON: three regular-Site landmark options.

FORTRESS_CHOICE = "wall"


# ------------------------------------------------------------------ angular helpers
def sq_tower(x, y, courses, size=10.0, z0=0.0, lit=True, banner=True, flag_=True):
    """Square tower of stacked containers, crossing every course; corner merlons, lit battlement square."""
    acc = LIT if lit else None
    h = size / 2
    for k in range(courses):
        z = z0 + k * HC
        if k % 2:
            for s in (-1, 1):
                obox(x + s * (h - 1.2), y, z, size, 2.4, HC, math.pi / 2, tcol(k + s + 3) if lit else wcol(k), acc=acc)
                obox(x, y + s * (h - 3.6), z, size - 4.8, 2.4, HC, 0, tcol(k + 2) if lit else wcol(k + 1), acc=acc)
        else:
            for s in (-1, 1):
                obox(x, y + s * (h - 1.2), z, size, 2.4, HC, 0, tcol(k + s + 1) if lit else wcol(k), acc=acc)
                obox(x + s * (h - 3.6), y, z, size - 4.8, 2.4, HC, math.pi / 2, tcol(k + 4) if lit else wcol(k + 2), acc=acc)
    top = z0 + courses * HC
    box(x - h + 0.6, y - h + 0.6, top - 0.4, x + h - 0.6, y + h - 0.6, top - 0.1, (0.16, 0.09, 0.06), facet=False)
    for (dx, dy) in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -1), (0, 1), (-1, 0), (1, 0)):
        obox(x + dx * (h - 1.2), y + dy * (h - 1.2), top, 2.4, 2.4, 2.4, 0, tcol(dx + dy + 5), ribs=False, acc=acc)
    roof_trim(x - h - 0.2, y - h - 0.2, x + h + 0.2, y + h + 0.2, top + 0.12, BATTLE, w=0.45)
    if banner:  # long banner down the +X face
        bx = x + h + 0.15
        SOLID.face([(bx, y - 1.8, top - 1), (bx, y + 1.8, top - 1), (bx, y + 1.8, top - 13), (bx, y, top - 15.5), (bx, y - 1.8, top - 13)], (1.0, 0.48, 0.06), rid())
        NEON.face([(bx + 0.05, y - 0.5, top - 3), (bx + 0.05, y + 0.5, top - 3), (bx + 0.05, y + 0.5, top - 10), (bx + 0.05, y - 0.5, top - 10)], (1.0, 0.92, 0.80), (0, 0, 0))
    if flag_:
        flag(x, y, top + 2.4, 8, (1.0, 0.5, 0.08))
    return top


def bastion(x, y, ang, courses, L=12.0):
    """Angular (diamond) bastion: two container stacks meeting at a point that faces outward."""
    for k in range(courses):
        for s in (-1, 1):
            a = ang + s * math.radians(45)
            cx_, cy_ = x + math.cos(a) * L / 2 * 0.72, y + math.sin(a) * L / 2 * 0.72
            obox(cx_, cy_, k * HC, L, 4.8, HC, a + math.pi / 2, tcol(k + s), acc=LIT)
    top = courses * HC
    for s in (-1, 1):
        a = ang + s * math.radians(45)
        beam((x, y, top + 0.15), (x + math.cos(a) * L * 0.9, y + math.sin(a) * L * 0.9, top + 0.15), 0.4, BATTLE, acc=NEON)
    return top


def sq_gatehouse(gx, courses=6, w=7.0, size=8.0, moat=True):
    """Two square gate towers facing +X, a lintel block, portcullis, glowing gate, container drawbridge, lit moat."""
    for sy in (-1, 1):
        sq_tower(gx, sy * w, courses, size=size)
    gh = (courses - 2) * HC
    obox(gx, 0, gh, 2 * w - size + 2.4, 6.0, 2 * HC, math.pi / 2, TOWER_C[0], acc=LIT)
    box(gx + 2.0, -w + size / 2, gh + 2 * HC, gx + 3.4, w - size / 2, gh + 2 * HC + 2.4, TOWER_C[1])
    for u in (-2.6, -1.3, 0, 1.3, 2.6):
        beam((gx + 3.2, u, 0.2), (gx + 3.2, u, gh), 0.45, (0.10, 0.09, 0.10))
    for z in range(3, int(gh), 4):
        beam((gx + 3.2, -3.0, z), (gx + 3.2, 3.0, z), 0.45, (0.10, 0.09, 0.10))
    NEON.face([(gx + 2.6, -3.0, 0.2), (gx + 2.6, 3.0, 0.2), (gx + 2.6, 3.0, gh), (gx + 2.6, -3.0, gh)], (0.85, 0.42, 0.08), (0, 0, 0))
    text_obj("MERIDIAN", (gx + 3.3, 0, gh + HC), (math.radians(90), 0, math.radians(90)), 2.0, SIGNM)
    x0 = gx + 3.4
    SOLID.face([(x0, -3.4, 1.6), (x0 + 10, -3.4, 0.4), (x0 + 10, 3.4, 0.4), (x0, 3.4, 1.6)], (0.80, 0.36, 0.08), rid())
    for u in range(-3, 4, 2):
        beam((x0 + 0.2, u, 1.7), (x0 + 9.8, u, 0.5), 0.3, (0.40, 0.18, 0.06))
    for sy in (-1, 1):
        beam((x0, sy * 3.6, gh), (x0 + 9.6, sy * 3.4, 0.6), 0.25, (0.7, 0.7, 0.72))
    if moat:
        for (a0, a1) in ((-27, -3.6), (3.6, 27)):
            strip(NEON, (x0 + 5, a0), (x0 + 5, a1), 6.0, 0.03, (0.32, 0.13, 0.02))
            strip(NEON, (x0 + 2.2, a0), (x0 + 2.2, a1), 0.35, 0.05, BATTLE)
            strip(NEON, (x0 + 7.8, a0), (x0 + 7.8, a1), 0.35, 0.05, BATTLE)


def corp_block(x0, y0, x1, y1, h, setback=True):
    """A regular corporate / logistics office: glass and steel, amber window grid, orange roof trims, MERIDIAN sign."""
    glass = (0.30, 0.33, 0.42)
    box(x0, y0, 0, x1, y1, h, glass)
    windows(x0, y0, 0, x1, y1, h, p=0.6, cols=[(1.0, 0.75, 0.40), (1.0, 0.85, 0.6), (0.9, 0.9, 1.0)])
    roof_trim(x0, y0, x1, y1, h + 0.1, BATTLE, w=0.4)
    top = h
    if setback:
        i = 3.0
        box(x0 + i, y0 + i, h, x1 - i, y1 - i, h + 14, glass)
        windows(x0 + i, y0 + i, h, x1 - i, y1 - i, h + 14, p=0.6, cols=[(1.0, 0.75, 0.40), (0.9, 0.9, 1.0)])
        roof_trim(x0 + i, y0 + i, x1 - i, y1 - i, h + 14.1, BATTLE, w=0.4)
        top = h + 14
    box(x1 + 0.05, (y0 + y1) / 2 - 6, top - 6, x1 + 0.6, (y0 + y1) / 2 + 6, top - 1.5, (0.06, 0.05, 0.05), facet=False)
    text_obj("MERIDIAN FREIGHT", (x1 + 0.7, (y0 + y1) / 2, top - 3.8), (math.radians(90), 0, math.radians(90)), 1.6, SIGNM)
    beam(((x0 + x1) / 2, (y0 + y1) / 2, top), ((x0 + x1) / 2, (y0 + y1) / 2, top + 9), 0.3, (0.3, 0.3, 0.34))
    NEON.face([((x0 + x1) / 2 - 0.5, (y0 + y1) / 2, top + 8), ((x0 + x1) / 2 + 0.5, (y0 + y1) / 2, top + 8),
               ((x0 + x1) / 2 + 0.5, (y0 + y1) / 2, top + 9), ((x0 + x1) / 2 - 0.5, (y0 + y1) / 2, top + 9)], RED, (0, 0, 0))
    return top


def square_wall(S, courses, gate_w=5.0, skip_gate=True):
    for (p, q) in (((-S, -S), (S, -S)), ((S, S), (-S, S)), ((-S, S), (-S, -S)), ((S, -S), (S, S))):
        cwall(p, q, courses, skip=(lambda x, y: x > S - 3 and abs(y) < gate_w) if skip_gate else None)


# ------------------------------------------------------------------ MERIDIAN fortress options
def fort_wall():
    """A: the container WALL. Straight crenellated curtain, square stacked corner towers, a square gatehouse,
    and a regular corporate tower standing inside."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    S = 21.0
    square_wall(S, 4, gate_w=7.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            sq_tower(sx * S, sy * S, 7, size=10.0, banner=sx > 0)
    sq_gatehouse(S, courses=6, w=7.6, size=7.0)
    corp_block(-11, -9, 5, 9, 30)


def fort_bunker():
    """B: stepped container BUNKER: four receding terraces of containers, angular, slit windows, a deep gate."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    z = 0.0
    for i, (S, c) in enumerate(((24.0, 2), (19.0, 2), (14.0, 2), (9.0, 2))):
        for (p, q) in (((-S, -S), (S, -S)), ((S, S), (-S, S)), ((-S, S), (-S, -S)), ((S, -S), (S, S))):
            cwall(p, q, c, z0=z, cols=(wcol if i % 2 == 0 else tcol), merlons=(i == 3),
                  skip=(lambda x, y, S=S: x > S - 3 and abs(y) < 4.0) if i == 0 else None)
        box(-S + 2.4, -S + 2.4, z + c * HC - 0.4, S - 2.4, S - 2.4, z + c * HC, (0.18, 0.10, 0.06), facet=False)
        for sx in (-1, 1):
            for sy in (-1, 1):  # angular corner prows on every terrace
                bastion(sx * S, sy * S, math.atan2(sy, sx), 1) if i == 0 else None
        for k in range(int(2 * S / 4)):  # slit windows along the +X face
            yy = -S + 2 + k * 4
            WIN.face([(S + 2.45, yy, z + 3), (S + 2.45, yy + 1.4, z + 3), (S + 2.45, yy + 1.4, z + 3.8), (S + 2.45, yy, z + 3.8)], (1.0, 0.7, 0.3), (0, 0, 0))
        z += c * HC
    sq_tower(0, 0, 3, size=8.0, z0=z)
    sq_gatehouse(24.0, courses=3, w=6.0, size=6.0)


def fort_yard():
    """C: walled FREIGHT YARD: a straight container wall, four tall watchtowers (lattice legs + container cab),
    container stacks and a gantry crane inside, the gate on the front."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    S = 23.0
    square_wall(S, 3, gate_w=6.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * S, sy * S
            for (dx, dy) in ((-2.5, -2.5), (2.5, -2.5), (-2.5, 2.5), (2.5, 2.5)):
                beam((x + dx, y + dy, 0), (x + dx * 0.6, y + dy * 0.6, 34), 0.8, (0.20, 0.18, 0.18))
            for zz in (8, 16, 24):
                for (a, b) in (((-2.4, -2.4), (2.4, -2.4)), ((2.4, -2.4), (2.4, 2.4)), ((2.4, 2.4), (-2.4, 2.4)), ((-2.4, 2.4), (-2.4, -2.4))):
                    beam((x + a[0], y + a[1], zz), (x + b[0], y + b[1], zz), 0.35, (0.24, 0.22, 0.22))
            obox(x, y, 34, 8.0, 7.0, HC, 0, tcol(sx + sy + 3), acc=LIT)
            box(x - 4.6, y - 4.2, 34 + HC, x + 4.6, y + 4.2, 34 + HC + 0.8, (0.18, 0.10, 0.06), facet=False)
            roof_trim(x - 4.6, y - 4.2, x + 4.6, y + 4.2, 34 + HC + 0.85, BATTLE, w=0.4)
            WIN.face([(x + 4.05, y - 2.5, 36), (x + 4.05, y + 2.5, 36), (x + 4.05, y + 2.5, 38), (x + 4.05, y - 2.5, 38)], (1.0, 0.75, 0.4), (0, 0, 0))
            flag(x, y, 34 + HC + 0.8, 7, (1.0, 0.5, 0.08))
    for row in range(3):
        for k in range(-1, 2):
            z = 0
            for lvl in range(2 + (row + k) % 3):
                z = container(-10 + row * 7.0, k * 13.0, z, rot90=True, L=12, W=4.8, Hh=HC)
    hz = 30
    for sy in (-1, 1):
        for sx in (-1, 1):
            beam((-14 + sx * 6, sy * 15, 0), (-14 + sx * 6, sy * 15, hz), 1.2, (0.2, 0.18, 0.18))
        hazard_beam((-22, sy * 15, hz), (8, sy * 15, hz), 1.6, seg=2.2)
    sq_gatehouse(S, courses=4, w=6.6, size=6.0)


def fort_citadel():
    """D: container CITADEL with a gatehouse face: a towering front block of containers (two square towers + a
    stepped face) dominates the view, high walls behind, a tall square keep."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    S = 20.0
    square_wall(S, 5, gate_w=10.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            if sx > 0:
                continue
            sq_tower(sx * S, sy * S, 6, size=8.0, banner=False)
    for sy in (-1, 1):  # angular bastions on the two front corners
        bastion(S, sy * S, math.atan2(sy, 1), 5)
    for k in range(3):  # stepped face rising over the gate
        obox(S - 2 - k * 2.4, 0, (5 + k) * HC, 2.4, 16 - k * 4, HC, 0, tcol(k), acc=LIT)
    sq_gatehouse(S, courses=8, w=9.0, size=8.0)
    sq_tower(-6, 0, 10, size=12.0)


FORTS = {"wall": fort_wall, "bunker": fort_bunker, "yard": fort_yard, "citadel": fort_citadel}


def meridian27():
    FORTS.get(globals().get("STATE", "") or FORTRESS_CHOICE, FORTS[FORTRESS_CHOICE])()


# ------------------------------------------------------------------ HALCYON regular-Site options
def tube_var(pts, radii, col, acc=None, n=16):
    """Tube with a radius per point (smooth sculpted forms)."""
    acc = acc or SOLID
    bid = rid()
    P = [Vector(p) for p in pts]
    rings = []
    for k, p in enumerate(P):
        t = (P[min(k + 1, len(P) - 1)] - P[max(k - 1, 0)]).normalized()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 1e-3:
            a = Vector((1, 0, 0))
        a.normalize()
        b = t.cross(a).normalized()
        r = radii[k]
        rings.append([p + (a * math.cos(2 * math.pi * i / n) + b * math.sin(2 * math.pi * i / n)) * r for i in range(n)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            acc.face([tuple(r0[i]), tuple(r0[j]), tuple(r1[j]), tuple(r1[i])], col, bid)
    for ring in (rings[0], rings[-1][::-1]):
        acc.face([tuple(v) for v in ring], col, bid)


def sphinx_smooth():
    """A sculpted sphinx: a smooth lion body (tapered tube with a rounded chest and haunch), long rounded paws,
    a smooth head under a flared nemes, the amber eye on the brow."""
    st, lt = HAL_STONE, tuple(min(1, v * 1.25) for v in HAL_STONE)
    box(-15, -27, 0, 15, 21, 3, lt, facet=False)
    roof_trim(-15, -27, 15, 21, 3.05, AMBER, w=0.35)
    body = [(0, 17, 6.5), (0, 13, 8.0), (0, 6, 8.6), (0, -1, 9.0), (0, -6, 9.6)]
    tube_var(body, [3.6, 5.6, 5.4, 5.8, 6.0], st, n=18)
    tube_var([(0, 17, 6), (0, 21, 4), (2, 23, 3.4), (5, 22, 3.4)], [1.0, 0.9, 0.8, 0.7], st, n=10)  # tail
    for sx in (-1, 1):
        tube_var([(sx * 4.5, 15, 4.0), (sx * 5.5, 12, 4.6), (sx * 5.2, 9, 4.0)], [2.4, 3.2, 2.0], st, n=14)  # haunch
        tube_var([(sx * 3.4, -6, 5.5), (sx * 3.6, -14, 4.0), (sx * 3.6, -23, 4.0), (sx * 3.6, -25.5, 4.0)], [2.2, 1.9, 1.8, 1.4], lt, n=14)  # forelegs
    dome(0, -8, 9.0, 5.8, st, n=18, rings=5)                                     # chest
    tube_var([(0, -9, 11), (0, -11.5, 15), (0, -12.5, 18)], [3.6, 3.2, 2.9], st, n=16)  # neck
    dome(0, -12.8, 18.5, 3.4, lt, n=18, rings=6, hz=1.25)                        # head
    cyl(0, -12.8, 15.6, 18.6, 3.0, lt, n=18)                                      # face / jaw
    cyl(0, -12.3, 19.0, 23.2, 4.8, st, n=18, r1=3.0)                              # nemes crown
    for sx in (-1, 1):                                                            # nemes lappets
        tube_var([(sx * 4.0, -12.6, 20.5), (sx * 4.6, -13.2, 16.5), (sx * 4.2, -13.6, 12.5)], [1.4, 1.6, 1.2], st, n=10)
    for k in range(5):
        ring_beams((0, -12.3, 19.3 + k * 0.85), (1, 0, 0), (0, 1, 0), 4.7 - k * 0.36, 0.2, AMBER, n=18, acc=NEON)
    eye((0, -16.0, 20.4), 2.0, 0.75, w=0.35)
    for sx in (-1, 1):
        box(sx * 12 - 1.4, 15, 3, sx * 12 + 1.4, 18, 25, st, taper=0.9)
        box(sx * 12 - 0.6, 15.9, 25, sx * 12 + 0.6, 17.1, 27, AMBER, taper=0.6)
    for (x, y) in ((-21, -18), (21, -10)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=True)


def courthouse():
    """Halcyon Court: a colonnaded temple front with a pediment, broad steps, and a giant statue of Justice holding
    lit scales (the eye crest on the pediment, the blindfold replaced by Halcyon's eye)."""
    st, lt = HAL_STONE, tuple(min(1, v * 1.25) for v in HAL_STONE)
    box(-18, -4, 0, 18, 22, 14, st)
    windows(-18, -4, 0, 18, 22, 14, p=0.4, cols=[(1.0, 0.72, 0.35)], faces=(1, 2, 3))
    for s in range(5):  # steps
        box(-19 + s * 0.4, -10 + s * 1.2, 0, 19 - s * 0.4, -4, (s + 1) * 0.6, lt, facet=False)
    for k in range(8):  # columns
        x = -15.5 + k * (31 / 7)
        cyl(x, -6.0, 3, 14, 1.0, (0.86, 0.84, 0.96), n=10)
    box(-18.5, -7.5, 14, 18.5, 22, 16, lt, facet=False)  # entablature
    SOLID.face([(-18.5, -7.5, 16), (18.5, -7.5, 16), (0, -7.5, 22)], lt, rid())  # pediment front
    SOLID.face([(-18.5, 22, 16), (0, 22, 22), (18.5, 22, 16)], lt, rid())
    SOLID.face([(-18.5, -7.5, 16), (0, -7.5, 22), (0, 22, 22), (-18.5, 22, 16)], (0.34, 0.30, 0.48), rid())
    SOLID.face([(18.5, -7.5, 16), (18.5, 22, 16), (0, 22, 22), (0, -7.5, 22)], (0.38, 0.34, 0.52), rid())
    eye((0, -7.6, 18.3), 3.0, 1.1, w=0.4)
    text_obj("HALCYON COURT", (0, -7.6, 15.0), (math.radians(90), 0, 0), 1.6, SIGNM)
    # the statue of Justice on a plinth in front of the steps
    bx, by = 0, -19
    box(bx - 3, by - 3, 0, bx + 3, by + 3, 6, lt)
    roof_trim(bx - 3, by - 3, bx + 3, by + 3, 6.05, AMBER, w=0.3)
    cyl(bx, by, 6, 22, 3.4, st, n=16, r1=1.6)          # robed body
    cyl(bx, by, 22, 25, 1.6, st, n=12, r1=1.9)         # shoulders
    dome(bx, by, 25, 1.9, lt, n=14, rings=5, hz=1.3)   # head
    eye((bx, by - 1.95, 26.4), 1.1, 0.42, w=0.25)      # the eye where the blindfold would be
    beam((bx + 1.4, by, 23.5), (bx + 4.5, by, 29), 0.7, st)        # raised arm
    beam((bx - 6.5, by, 29.2), (bx + 6.5, by, 29.2), 0.45, AMBER, acc=NEON)  # the balance beam
    for sx in (-1, 1):
        px = bx + sx * 6.0
        for d in (-0.8, 0.8):
            beam((px, by, 29.2), (px + d, by, 25.0), 0.12, (0.85, 0.75, 0.5))
        disc((px, by, 24.9), (1, 0, 0), (0, 1, 0), 1.6, AMBER, acc=NEON, n=12)
    beam((bx - 1.4, by, 23.5), (bx - 2.6, by - 1.0, 13), 0.7, st)  # lowered arm
    beam((bx - 2.6, by - 1.0, 13), (bx - 2.6, by - 1.0, 4.0), 0.35, (0.86, 0.84, 0.96))  # sword
    for (x, y) in ((-14, -26), (14, -26)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=False)


def surveillance_obelisk():
    """The Watchtower: a faceted obelisk with camera rings and the eye at its tip, sweeping amber floods, bollards."""
    st, lt = HAL_STONE, tuple(min(1, v * 1.25) for v in HAL_STONE)
    box(-14, -14, 0, 14, 14, 2.4, lt, facet=False)
    roof_trim(-14, -14, 14, 14, 2.45, AMBER, w=0.35)
    box(-5, -5, 2.4, 5, 5, 8, st)
    box(-3.6, -3.6, 8, 3.6, 3.6, 50, st, taper=1.6)
    box(-2.0, -2.0, 50, 2.0, 2.0, 55, lt, taper=1.9)
    for z in (16, 26, 36, 46):  # camera rings
        k = (z - 8) / 42
        s = 3.6 - 1.6 * k + 0.5
        roof_trim(-s, -s, s, s, z, AMBER, w=0.35)
        for (dx, dy) in ((-s, -s), (s, -s), (s, s), (-s, s)):
            box(dx - 0.5, dy - 0.5, z - 1.2, dx + 0.5, dy + 0.5, z - 0.2, (0.15, 0.12, 0.2), facet=False)
            NEON.face([(dx - 0.25, dy - 0.55, z - 0.9), (dx + 0.25, dy - 0.55, z - 0.9), (dx + 0.25, dy - 0.55, z - 0.5), (dx - 0.25, dy - 0.55, z - 0.5)], CRED, (0, 0, 0))
    eye((0, -2.6, 44), 1.8, 0.7, w=0.3)
    for k in range(12):  # bollards with lights
        a = 2 * math.pi * k / 12
        x, y = 12 * math.cos(a), 12 * math.sin(a)
        box(x - 0.4, y - 0.4, 2.4, x + 0.4, y + 0.4, 4.2, (0.2, 0.18, 0.26), facet=False)
        NEON.face([(x - 0.45, y - 0.45, 4.25), (x + 0.45, y - 0.45, 4.25), (x + 0.45, y + 0.45, 4.25), (x - 0.45, y + 0.45, 4.25)], AMBER, (0, 0, 0))
    for (x, y) in ((-20, -16), (19, -14)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=True)


HEROES26["meridian"] = meridian27
SITES26[("halcyon", "sphinx2")] = sphinx_smooth
SITES26[("halcyon", "court")] = courthouse
SITES26[("halcyon", "obelisk")] = surveillance_obelisk

SITES26[("halcyon", "")] = courthouse  # recommended
