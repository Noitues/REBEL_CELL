# Round 25 HQ builders. NOT a module: hq_scene.py exec()s this file (after heroes24.py) into its own namespace,
# sharing SOLID / NEON / WIN, box(), beam(), strip(), container(), cyl(), dome(), dish(), eye(), plaza(), ...
# Each HQ is built ONCE around the origin on its 10 x 10 lot HQ plot (1 lot = 6 BU, so +-30 BU) and the same
# builder feeds both the city-map sprite (ortho iso camera) and the combat close-up (perspective camera).
# World axes: lot (x, y) -> world (x * 6, -y * 6); the map camera looks in from world (+1, -1).




def tube(pts, r, col, acc=None, n=10, bid=None):
    """Round tube along a polyline (thick strands)."""
    acc = acc or SOLID
    bid = bid or rid()
    P = [Vector(p) for p in pts]
    rings = []
    for k, p in enumerate(P):
        t = (P[min(k + 1, len(P) - 1)] - P[max(k - 1, 0)]).normalized()
        a = t.cross(Vector((0, 0, 1)))
        if a.length < 1e-3:
            a = Vector((1, 0, 0))
        a.normalize()
        b = t.cross(a).normalized()
        rings.append([p + (a * math.cos(2 * math.pi * i / n) + b * math.sin(2 * math.pi * i / n)) * r for i in range(n)])
    for r0, r1 in zip(rings, rings[1:]):
        for i in range(n):
            j = (i + 1) % n
            acc.face([tuple(r0[i]), tuple(r0[j]), tuple(r1[j]), tuple(r1[i])], col, bid)
    for ring in (rings[0], rings[-1][::-1]):
        acc.face([tuple(v) for v in ring], col, bid)


def flag(x, y, z, h, col, side=1):
    beam((x, y, z), (x, y, z + h), 0.35, (0.2, 0.2, 0.22))
    SOLID.face([(x, y, z + h), (x + side * 4.0, y - side * 0.6, z + h - 0.8), (x + side * 3.6, y - side * 0.5, z + h - 2.6),
                (x, y, z + h - 2.4)], col, rid())


# ================================================================== MERIDIAN: the container castle
CONT = [(0.86, 0.42, 0.10), (0.80, 0.36, 0.08), (0.72, 0.30, 0.10), (0.62, 0.22, 0.10), (0.90, 0.52, 0.16),
        (0.16, 0.36, 0.62), (0.15, 0.48, 0.46), (0.72, 0.70, 0.64)]


def ccol(k):
    return CONT[k % 5] if (k * 7) % 11 else CONT[5 + k % 3]


def container_castle():
    plaza(27.5, AMBER, ground=(0.24, 0.20, 0.18), ring2=(1.0, 0.45, 0.10))
    S = 21.0
    Hc = 5.2
    k = 0
    # curtain walls: containers laid lengthwise, 3 courses in running bond; a gate gap in the +X wall
    for course in range(3):
        z = course * Hc
        off = 6.0 if course % 2 else 0.0
        for side in range(4):
            for n in range(-2, 2):
                u = n * 12.0 + 6.0 + off
                if abs(u) > S - 3:
                    continue
                k += 1
                if side == 0:
                    container(u, -S, z, c=ccol(k))
                elif side == 1:
                    container(u, S, z, c=ccol(k))
                elif side == 2:
                    container(-S, u, z, rot90=True, c=ccol(k))
                else:
                    if abs(u) < 7:  # gate
                        continue
                    container(S, u, z, rot90=True, c=ccol(k))
    wall_top = 3 * Hc
    # crenellations: short containers as merlons along every wall top
    for side in range(4):
        for n in range(-4, 5):
            u = n * 4.8
            if n % 2:
                continue
            if side == 3 and abs(u) < 8:
                continue
            if side == 0:
                container(u, -S, wall_top, L=3.2, W=4.8, Hh=2.6, c=ccol(n + 3))
            elif side == 1:
                container(u, S, wall_top, L=3.2, W=4.8, Hh=2.6, c=ccol(n + 4))
            elif side == 2:
                container(-S, u, wall_top, rot90=True, L=3.2, W=4.8, Hh=2.6, c=ccol(n + 5))
            else:
                container(S, u, wall_top, rot90=True, L=3.2, W=4.8, Hh=2.6, c=ccol(n + 6))
    roof_trim(-S - 2.4, -S - 2.4, S + 2.4, S + 2.4, wall_top + 0.1, (1.0, 0.55, 0.12), w=0.45)
    # corner towers: crossed container courses, 7 high, merlons and a flag
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * S, sy * S
            for course in range(7):
                z = course * Hc
                if course % 2:
                    container(x - 2.5, y, z, rot90=True, L=10, c=ccol(course + 2))
                    container(x + 2.5, y, z, rot90=True, L=10, c=ccol(course + 5))
                else:
                    container(x, y - 2.5, z, L=10, c=ccol(course + 1))
                    container(x, y + 2.5, z, L=10, c=ccol(course + 3))
            top = 7 * Hc
            for (dx, dy) in ((-4, -4), (4, -4), (-4, 4), (4, 4)):
                box(x + dx - 1.1, y + dy - 1.1, top, x + dx + 1.1, y + dy + 1.1, top + 2.6, (0.80, 0.38, 0.10))
            roof_trim(x - 5, y - 5, x + 5, y + 5, top + 0.1, (1.0, 0.55, 0.12), w=0.4)
            flag(x, y, top, 8, (1.0, 0.50, 0.08), side=1)
            for z in (12, 22):  # arrow-slit lights
                WIN.face([(x + sx * 5.05, y - 0.5, z), (x + sx * 5.05, y + 0.5, z), (x + sx * 5.05, y + 0.5, z + 2.2), (x + sx * 5.05, y - 0.5, z + 2.2)], (1.0, 0.66, 0.26), (0, 0, 0))
                WIN.face([(x - 0.5, y + sy * 5.05, z), (x + 0.5, y + sy * 5.05, z), (x + 0.5, y + sy * 5.05, z + 2.2), (x - 0.5, y + sy * 5.05, z + 2.2)], (1.0, 0.66, 0.26), (0, 0, 0))
    # the keep: 2 x 3 containers per course, 9 courses, crossing every course
    for course in range(9):
        z = course * Hc
        if course % 2:
            for i in (-1, 0, 1):
                container(i * 4.8, 0, z, rot90=True, L=12, c=ccol(course * 3 + i))
        else:
            for j in (-1, 0, 1):
                container(0, j * 4.8, z, L=12, c=ccol(course * 3 + j + 1))
    ktop = 9 * Hc
    for (dx, dy) in ((-5, -6), (0, -6), (5, -6), (-5, 6), (0, 6), (5, 6), (-6, 0), (6, 0)):
        box(dx - 1.0, dy - 1.0, ktop, dx + 1.0, dy + 1.0, ktop + 2.4, (0.84, 0.40, 0.10))
    roof_trim(-6, -7.2, 6, 7.2, ktop + 0.1, (1.0, 0.55, 0.12), w=0.45)
    for z in range(6, int(ktop) - 2, 7):  # keep window band
        for u in (-3.6, 0, 3.6):
            WIN.face([(u - 0.8, -7.25, z), (u + 0.8, -7.25, z), (u + 0.8, -7.25, z + 1.6), (u - 0.8, -7.25, z + 1.6)], (1.0, 0.70, 0.30), (0, 0, 0))
            WIN.face([(6.05, u - 0.8, z), (6.05, u + 0.8, z), (6.05, u + 0.8, z + 1.6), (6.05, u - 0.8, z + 1.6)], (1.0, 0.70, 0.30), (0, 0, 0))
    flag(0, 0, ktop, 14, (1.0, 0.50, 0.08), side=1)
    # gatehouse on the +X wall: two gate towers, portcullis, container drawbridge over a lit moat
    for sy in (-1, 1):
        for course in range(5):
            container(S, sy * 9.0, course * Hc, rot90=(course % 2 == 0), L=7, W=6, Hh=Hc, c=ccol(course + (2 if sy > 0 else 4)))
        box(S - 3.5, sy * 9 - 3.5, 5 * Hc, S + 3.5, sy * 9 + 3.5, 5 * Hc + 2.4, (0.80, 0.38, 0.10))
    beam((S, -6, 4 * Hc + 1.2), (S, 6, 4 * Hc + 1.2), 2.4, (0.30, 0.18, 0.10))  # lintel
    for u in (-4.5, -2.25, 0, 2.25, 4.5):  # portcullis bars
        beam((S + 0.4, u, 0.2), (S + 0.4, u, 4 * Hc), 0.45, (0.10, 0.09, 0.10))
    for z in (3, 7, 11, 15, 19):
        beam((S + 0.4, -6, z), (S + 0.4, 6, z), 0.45, (0.10, 0.09, 0.10))
    NEON.face([(S - 1.0, -6, 0.2), (S - 1.0, 6, 0.2), (S - 1.0, 6, 4 * Hc), (S - 1.0, -6, 4 * Hc)], (0.55, 0.26, 0.05), (0, 0, 0))  # gate glow
    strip(NEON, (S + 4.0, -26), (S + 4.0, 26), 5.0, 0.03, (0.30, 0.12, 0.02))  # moat
    strip(NEON, (S + 1.6, -26), (S + 1.6, 26), 0.35, 0.05, AMBER)
    strip(NEON, (S + 6.4, -26), (S + 6.4, 26), 0.35, 0.05, AMBER)
    # drawbridge: a container lowered on chains across the moat
    db0, db1 = Vector((S + 0.5, -5.2, 0.3)), Vector((S + 9.5, -5.2, 0.3))
    SOLID.face([(S + 0.5, -5.2, 1.6), (S + 10.0, -5.2, 0.4), (S + 10.0, 5.2, 0.4), (S + 0.5, 5.2, 1.6)], CONT[1], rid())
    for u in range(-4, 5, 2):
        beam((S + 0.6, u, 1.7), (S + 9.8, u, 0.5), 0.3, (0.40, 0.18, 0.06))
    for sy in (-1, 1):
        beam((S + 1.0, sy * 6.5, 4 * Hc), (S + 9.8, sy * 5.0, 0.6), 0.25, (0.6, 0.6, 0.62))
    text_obj("MERIDIAN", (S + 1.25, 0, 4 * Hc + 1.2), (math.radians(90), 0, math.radians(90)), 2.0, SIGNM)
    # gantry cranes as siege towers at the two back corners, booms swung over the walls
    for (x, y, rot) in ((-S - 7, S - 2, 0), (-S + 2, S + 7, 1)):
        hz = 46
        leg = (0.20, 0.18, 0.18)
        d1 = (0, 1) if rot == 0 else (1, 0)
        d2 = (1, 0) if rot == 0 else (0, 1)
        for a in (-1, 1):
            for b in (-1, 1):
                px, py = x + d1[0] * a * 5 + d2[0] * b * 3, y + d1[1] * a * 5 + d2[1] * b * 3
                beam((px, py, 0), (px, py, hz), 1.2, leg)
        for b in (-1, 1):
            p0 = (x + d2[0] * b * 3 - d1[0] * 6, y + d2[1] * b * 3 - d1[1] * 6, hz)
            p1 = (x + d2[0] * b * 3 + d2[0] * 26, y + d2[1] * b * 3 + d2[1] * 26, hz)
            hazard_beam((x + d2[0] * b * 3 - d2[0] * 4, y + d2[1] * b * 3 - d2[1] * 4, hz), (x + d2[0] * 30, y + d2[1] * 30, hz), 1.5, seg=2.2)
        tx, ty = x + d2[0] * 22, y + d2[1] * 22
        beam((tx, ty, hz), (tx, ty, 26), 0.2, (0.1, 0.1, 0.1))
        container(tx, ty, 21, rot90=(rot == 1), c=CONT[5 + rot], L=10, W=4.4, Hh=4.6)
        box(x - 0.6, y - 0.6, hz + 1.0, x + 0.6, y + 0.6, hz + 2.2, RED, facet=False)


# ================================================================== SOLACE: the double helix (no tower)
STRAND_A = (0.74, 0.88, 0.82)  # calm teal-white
STRAND_B = (0.58, 0.80, 0.46)  # calm lime
RUNG = (0.55, 1.0, 0.30)       # the bright accent lives only on rungs and lights


def double_helix():
    plaza(27.5, (0.30, 0.78, 0.50), ground=(0.24, 0.30, 0.28), ring2=(0.45, 0.85, 0.35))
    cyl(0, 0, 0, 3.5, 23, (0.66, 0.72, 0.70), n=8, a_off=math.pi / 8)
    cyl(0, 0, 3.5, 6.5, 18, (0.58, 0.66, 0.62), n=8, a_off=math.pi / 8)
    ring_beams((0, 0, 3.6), (1, 0, 0), (0, 1, 0), 22.6, 0.4, (0.35, 0.80, 0.45), n=8)
    ring_beams((0, 0, 6.6), (1, 0, 0), (0, 1, 0), 17.6, 0.4, (0.35, 0.80, 0.45), n=8)
    R, z0, z1, turns = 13.5, 6.5, 108.0, 2.6
    N = 160
    A, B = [], []
    for i in range(N + 1):
        t = i / N
        a = t * turns * 2 * math.pi + math.radians(-45)
        z = z0 + t * (z1 - z0)
        A.append((R * math.cos(a), R * math.sin(a), z))
        B.append((R * math.cos(a + math.pi), R * math.sin(a + math.pi), z))
    tube(A, 2.9, STRAND_A, n=12)
    tube(B, 2.9, STRAND_B, n=12)
    # a calm, dim glow seam along each strand (teal / lime) so they keep their colour at night
    for S_, gc in ((A, (0.16, 0.40, 0.32)), (B, (0.24, 0.44, 0.10))):
        seam = [(x * 1.21, y * 1.21, z) for (x, y, z) in S_]
        tube(seam, 0.45, gc, acc=NEON, n=6)
    # base-pair walkways: thin planks with railings and a bright lit strip, all the way up
    for i in range(4, N - 2, 4):
        p, q = Vector(A[i]), Vector(B[i])
        d = (q - p).normalized()
        p2, q2 = p + d * 2.6, q - d * 2.6
        beam(tuple(p2), tuple(q2), 0.9, (0.70, 0.76, 0.74))
        side = d.cross(Vector((0, 0, 1))).normalized() * 0.55
        beam(tuple(p2 + side + Vector((0, 0, 0.9))), tuple(q2 + side + Vector((0, 0, 0.9))), 0.18, (0.82, 0.88, 0.86))
        beam(tuple(p2 - side + Vector((0, 0, 0.9))), tuple(q2 - side + Vector((0, 0, 0.9))), 0.18, (0.82, 0.88, 0.86))
        beam(tuple(p2 + Vector((0, 0, 0.5))), tuple(q2 + Vector((0, 0, 0.5))), 0.25, RUNG, acc=NEON)
    for i in range(2, N, 6):  # small node lights along the strands
        for S_ in (A, B):
            x, y, z = S_[i]
            k = 1.06
            box(x * k - 0.45, y * k - 0.45, z - 0.45, x * k + 0.45, y * k + 0.45, z + 0.45, (0.40, 0.80, 0.30), facet=False)
            NEON.face([(x * k - 0.5, y * k - 0.5, z + 0.47), (x * k + 0.5, y * k - 0.5, z + 0.47), (x * k + 0.5, y * k + 0.5, z + 0.47), (x * k - 0.5, y * k + 0.5, z + 0.47)], RUNG, (0, 0, 0))
    for S_ in (A, B):  # cap beacons
        x, y, z = S_[-1]
        dome(x, y, z, 3.0, (0.62, 0.72, 0.68), n=12)
        beam((x, y, z + 2.8), (x, y, z + 9), 0.4, (0.6, 0.66, 0.64))
        NEON.face([(x - 0.6, y - 0.6, z + 9), (x + 0.6, y - 0.6, z + 9), (x + 0.6, y - 0.6, z + 10.2), (x - 0.6, y - 0.6, z + 10.2)], RUNG, (0, 0, 0))
    # implant pods round the podium (muted glass, lime only as a thin ring light)
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        px, py = 20 * math.cos(a), 20 * math.sin(a)
        if (px - py) > 22:  # keep the side facing the camera open
            continue
        cyl(px, py, 3.5, 5, 3.2, (0.72, 0.78, 0.74), n=12)
        cyl(px, py, 5, 10.5, 2.7, (0.30, 0.46, 0.36), n=12)
        dome(px, py, 10.5, 2.7, (0.40, 0.56, 0.46), n=12)
        ring_beams((px, py, 8), (1, 0, 0), (0, 1, 0), 2.78, 0.22, RUNG, n=12)
    box(-10, -23.6, 0.6, 10, -22.9, 3.4, (0.08, 0.10, 0.08), facet=False)
    text_obj("SOLACE", (0, -23.7, 2.0), (math.radians(90), 0, 0), 2.0, SIGNM)


# ================================================================== HALCYON: taller civic ziggurat + eye
def civic_core_tall():
    plaza(27.5, VIOLET, ground=(0.28, 0.26, 0.34), ring2=AMBER)
    tiers = [(27, 0, 9), (23.5, 9, 18), (20, 18, 27), (16.5, 27, 36), (13.5, 36, 45), (10.5, 45, 54), (7.5, 54, 62)]
    for i, (hs, z0, z1) in enumerate(tiers):
        c = tuple(v + i * 0.025 for v in HAL_STONE)
        box(-hs, -hs, z0, hs, hs, z1, c)
        zb = z0 + (z1 - z0) * 0.40
        n = int(2 * hs / 3.0)
        for k in range(n):
            t0, t1 = -hs + k * 3.0 + 0.35, -hs + (k + 1) * 3.0 - 0.35
            for q in ([(t0, -hs - 0.08, zb), (t1, -hs - 0.08, zb), (t1, -hs - 0.08, zb + 2.0), (t0, -hs - 0.08, zb + 2.0)],
                      [(hs + 0.08, t0, zb), (hs + 0.08, t1, zb), (hs + 0.08, t1, zb + 2.0), (hs + 0.08, t0, zb + 2.0)],
                      [(-hs - 0.08, t1, zb), (-hs - 0.08, t0, zb), (-hs - 0.08, t0, zb + 2.0), (-hs - 0.08, t1, zb + 2.0)]):
                WIN.face(q, (1.0, 0.70, 0.30), (0, 0, 0))
        if hs > 9:
            colonnade(-hs, -hs, hs, hs, z0, z1 - 0.6, step=3.6, out=1.2, faces=(0, 1, 3))
        roof_trim(-hs, -hs, hs, hs, z1 + 0.1, VIOLET, w=0.42)
    for sx, sy in ((1, 0), (0, -1)):  # grand stairs up the two faces the camera sees
        for s in range(14):
            z = s * 1.3
            if sx:
                box(27 + 6 - s * 0.45, -4, 0, 27 + 6.5 - s * 0.45, 4, z + 1.3, (0.62, 0.58, 0.78), facet=False)
            else:
                box(-4, -27 - 6.5 + s * 0.45, 0, 4, -27 - 6 + s * 0.45, z + 1.3, (0.62, 0.58, 0.78), facet=False)
    box(-3.5, -3.5, 62, 3.5, 3.5, 70, (0.22, 0.18, 0.32))
    beam((0, -2, 70), (0, -2, 74), 1.4, (0.22, 0.18, 0.32))
    eye((0, -2.5, 82), 14, 5.0, lid=(0.62, 0.40, 0.10))
    for k in range(7):
        a = math.radians(30 + k * 20)
        beam((15.5 * math.cos(a), -2.5, 82 + 9 * math.sin(a)), (19.5 * math.cos(a), -2.5, 82 + 12 * math.sin(a)), 0.7, (0.62, 0.40, 0.10), acc=NEON)
    for sx in (-1, 1):
        beam((sx * 19, 6, 27), (sx * 19, 6, 30), 1.0, (0.3, 0.3, 0.36))
        dish((sx * 19, 6, 31), (sx * 0.5, -0.4, 0.8), 4.6, 1.4, (0.86, 0.84, 0.92), tip=AMBER)
    text_obj("HALCYON CIVIC", (0, -27.2, 5.4), (math.radians(90), 0, 0), 2.6, SIGNM)
    for (x, y) in ((-24, -32), (-14, -34), (31, 14), (33, -12)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=False)


# ================================================================== ORBITAL: crescent round the missile silo
def orbital_silo():
    plaza(27.5, CYAN, ground=(0.10, 0.12, 0.18), ring2=ICE)
    back = math.radians(135)  # away from the camera (camera sits toward world +x -y)
    # mast (kept from round 24) at the back of the crescent
    mx, my = 19 * math.cos(back), 19 * math.sin(back)
    top = 82
    cyl(mx, my, 0, 3, 8, ORB_WHITE, n=12)
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam((mx + sx * 5, my + sy * 5, 3), (mx + sx * 1.0, my + sy * 1.0, top), 0.9, (0.88, 0.92, 0.96))
    for z in range(9, top - 4, 8):
        k = 1 - (z - 3) / (top - 3)
        s = 1.0 + 4.0 * k
        for (a, b) in (((-s, -s), (s, -s)), ((s, -s), (s, s)), ((s, s), (-s, s)), ((-s, s), (-s, -s))):
            beam((mx + a[0], my + a[1], z), (mx + b[0], my + b[1], z), 0.35, (0.80, 0.85, 0.92))
    for z in (24, 44, 64):
        k = 1 - (z - 3) / (top - 3)
        ring_beams((mx, my, z), (1, 0, 0), (0, 1, 0), (1.0 + 4.0 * k) * 1.6, 0.45, CYAN, n=16)
    box(mx - 1.2, my - 1.2, top, mx + 1.2, my + 1.2, top + 2.2, (0.9, 0.95, 1.0), facet=False)
    NEON.face([(mx - 1.3, my - 1.3, top + 0.2), (mx + 1.3, my - 1.3, top + 0.2), (mx + 1.3, my - 1.3, top + 2.0), (mx - 1.3, my - 1.3, top + 2.0)], CYAN, (0, 0, 0))
    # dishes along the crescent
    for k, (deg, big) in enumerate(((90, True), (180, True), (45, False), (225, False), (65, False), (205, False))):
        a = math.radians(deg)
        r = 20 if big else 23
        px, py = r * math.cos(a), r * math.sin(a)
        if big:
            cyl(px, py, 0, 8, 2.2, (0.62, 0.66, 0.72), n=10)
            aim = Vector((-math.cos(a) * 0.35 + 0.25, -math.sin(a) * 0.35 - 0.25, 0.85))
            dish((px, py, 15), aim, 9.0, 2.8, (0.92, 0.95, 0.98), n=18, tip=CYAN)
            beam((px, py, 8), (px, py, 13), 1.4, (0.62, 0.66, 0.72))
        else:
            cyl(px, py, 0, 3, 1.2, (0.6, 0.64, 0.7), n=8)
            dish((px, py, 5.5), (-math.cos(a) * 0.3 + 0.2, -math.sin(a) * 0.3 - 0.2, 0.85), 3.4, 1.0, (0.9, 0.93, 0.97), tip=CYAN)
    # low ops wall along the crescent
    for k in range(14):
        a0 = math.radians(40 + k * 14)
        a1 = a0 + math.radians(12)
        p0 = (26 * math.cos(a0), 26 * math.sin(a0))
        p1 = (26 * math.cos(a1), 26 * math.sin(a1))
        cx_, cy_ = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
        box(cx_ - 2.4, cy_ - 2.4, 0, cx_ + 2.4, cy_ + 2.4, 3.2, ORB_WHITE, facet=False)
    # the silo: concrete ring, hazard rim, two flat doors (closed) or swung up with the missile nose out (open)
    cyl(0, 0, 0, 0.8, 12.5, (0.46, 0.50, 0.56), n=24)
    for i in range(24):
        a0, a1 = 2 * math.pi * i / 24, 2 * math.pi * (i + 0.5) / 24
        strip(NEON, (11.6 * math.cos(a0), 11.6 * math.sin(a0)), (11.6 * math.cos(a1), 11.6 * math.sin(a1)), 0.8, 0.85, (1.0, 0.80, 0.10))
    if globals().get("STATE", "") != "open":
        for sx in (-1, 1):
            box(min(0, sx * 10.4) + (0.15 if sx > 0 else 0), -10.4, 0.8, max(0, sx * 10.4) - (0.15 if sx < 0 else 0), 10.4, 1.4, (0.62, 0.66, 0.72), facet=False)
            for u in range(-8, 9, 4):
                beam((sx * 0.6, u, 1.45), (sx * 10.0, u, 1.45), 0.25, (0.40, 0.42, 0.48))
        strip(NEON, (0, -10.4), (0, 10.4), 0.35, 1.5, CYAN)
        for (x, y) in ((-7, -7), (7, -7), (-7, 7), (7, 7)):
            NEON.face([(x - 0.6, y - 0.6, 1.5), (x + 0.6, y - 0.6, 1.5), (x + 0.6, y + 0.6, 1.5), (x - 0.6, y + 0.6, 1.5)], (1.0, 0.25, 0.2), (0, 0, 0))
    else:
        cyl(0, 0, 0.82, 0.86, 10.4, (0.02, 0.03, 0.05), n=24, facet=False)
        for z in (0.9,):
            ring_beams((0, 0, z), (1, 0, 0), (0, 1, 0), 10.2, 0.35, CYAN, n=24)
        for sx in (-1, 1):  # doors hinged on their outer edge, swung up ~75 degrees
            hx = sx * 10.6
            tip = Vector((hx - sx * 10.4 * math.cos(math.radians(75)), 0, 0.8 + 10.4 * math.sin(math.radians(75))))
            q = [(hx, -10.4, 0.8), (hx, 10.4, 0.8), (tip.x, 10.4, tip.z), (tip.x, -10.4, tip.z)]
            SOLID.face(q, (0.62, 0.66, 0.72), rid())
            SOLID.face(q[::-1], (0.50, 0.54, 0.60), rid())
            beam((hx, -10.4, 0.8), (tip.x, -10.4, tip.z), 0.4, (1.0, 0.80, 0.10), acc=NEON)
            beam((hx, 10.4, 0.8), (tip.x, 10.4, tip.z), 0.4, (1.0, 0.80, 0.10), acc=NEON)
        cyl(0, 0, -6, 20, 4.4, (0.90, 0.93, 0.97), n=16)
        cyl(0, 0, 20, 34, 4.4, (0.92, 0.95, 0.98), n=16, r1=0.3)
        for zr, cr in ((8, CYAN), (14, CYAN), (19, (1.0, 0.25, 0.2))):
            ring_beams((0, 0, zr), (1, 0, 0), (0, 1, 0), 4.5, 0.6, cr, n=16)
        box(-0.4, -0.4, 33.8, 0.4, 0.4, 34.8, (1.0, 0.25, 0.2), facet=False)
        NEON.face([(-0.5, -0.5, 34.9), (0.5, -0.5, 34.9), (0.5, 0.5, 34.9), (-0.5, 0.5, 34.9)], (1.0, 0.25, 0.2), (0, 0, 0))
        cyl(0, 0, 0.9, 1.0, 9.6, (0.20, 0.42, 0.55), n=24, acc=NEON, facet=False)  # silo glow
    text_obj("ORBITAL COMMONS", (0, -27.6, 1.8), (math.radians(90), 0, 0), 2.0, SIGNM)


# ================================================================== REBEL_CELL: the Cell's hidden base / DISPATCH
def rebel_base():
    disp = globals().get("STATE", "") == "dispatch"
    L1 = (1.0, 0.10, 0.10) if disp else (0.60, 1.0, 0.30)   # lime (home) / red
    L2 = (0.80, 0.05, 0.12) if disp else (1.0, 0.35, 0.65)  # pink (home) / dark red
    WARM = (1.0, 0.30, 0.22) if disp else (1.0, 0.72, 0.40)
    grng = random.Random(25)
    # an enclosed courtyard of old tenements and a converted parking deck (hidden in plain sight)
    blocks = [(-24, -24, -8, -12, 14), (-24, -12, -14, 12, 18), (-24, 12, 0, 24, 12), (0, 14, 24, 24, 16), (12, -6, 24, 14, 10),
              (6, -24, 24, -12, 9)]
    for (x0, y0, x1, y1, h) in blocks:
        c = (0.36, 0.30, 0.32) if not disp else (0.24, 0.12, 0.14)
        box(x0, y0, 0, x1, y1, h, c)
        windows(x0, y0, 0, x1, y1, h, p=0.45, cols=[WARM, WARM, L1, L2])
        roof_trim(x0, y0, x1, y1, h + 0.1, L2 if not disp else (0.55, 0.04, 0.06), w=0.3)
        for k in range(3):  # roof junk: tanks, tarps, solar
            px, py = grng.uniform(x0 + 2, x1 - 2), grng.uniform(y0 + 2, y1 - 2)
            if k == 0:
                cyl(px, py, h, h + 3, 1.6, (0.30, 0.26, 0.28), n=8)
            elif k == 1:
                SOLID.face([(px - 3, py - 2, h + 0.3), (px + 3, py - 2, h + 0.3), (px + 3, py + 2, h + 1.6), (px - 3, py + 2, h + 1.6)],
                           (0.20, 0.36, 0.52) if not disp else (0.30, 0.10, 0.12), rid())
            else:
                SOLID.face([(px - 2.5, py - 1.5, h + 0.4), (px + 2.5, py - 1.5, h + 0.4), (px + 2.5, py + 1.5, h + 1.4), (px - 2.5, py + 1.5, h + 1.4)],
                           (0.10, 0.14, 0.26), rid())
    # the big fist painted on the deck roof (readable from above, same crest as the fist roads)
    zf = 18.15
    parts = [(-23.0, 6.6, -15.2, 8.8), (-23.0, 4.0, -15.2, 6.2), (-23.0, 1.4, -15.2, 3.6), (-23.0, -1.2, -15.2, 1.0),  # fingers
             (-23.4, -4.4, -17.0, -1.8),  # thumb
             (-21.6, -11.0, -16.6, -4.8)]  # wrist / forearm
    for (x0, y0, x1, y1) in parts:
        NEON.face([(x0, y0, zf), (x1, y0, zf), (x1, y1, zf), (x0, y1, zf)], L2, (0, 0, 0))
    # courtyard: container shacks, string lights, the sunken entrance ramp, the Cell relay mast
    for i, (x, y, rot) in enumerate(((-6, -6, False), (-6, 4, True), (4, -10, False))):
        container(x, y, 0, rot90=rot, L=8, W=4, Hh=3.6, c=(0.30, 0.42, 0.40) if not disp else (0.28, 0.10, 0.12))
    disc((0, 0, 0.04), (1, 0, 0), (0, 1, 0), 13.0, tuple(v * 0.22 for v in L2), acc=NEON, n=24)  # the lit courtyard: the base glows from inside
    SOLID.face([(2, 2, 0.05), (10, 2, 0.05), (10, 10, -0.05), (2, 10, -0.05)], (0.06, 0.05, 0.06), rid())  # ramp down
    for z in (0.4,):
        strip(NEON, (2.4, 2.4), (9.6, 2.4), 0.3, z, L1)
        strip(NEON, (2.4, 9.6), (9.6, 9.6), 0.3, z, L1)
    for (p, q) in (((-14, -10, 12), (12, 14, 10)), ((-14, 6, 14), (12, -4, 9)), ((-8, -12, 12), (6, 14, 12)), ((-14, -2, 13), (12, 4, 9))):
        cable(p, q, 2.5, w=0.12, col=(0.12, 0.10, 0.12))
        P0, P1 = Vector(p), Vector(q)
        for t in range(1, 12):
            u = t / 12
            v = P0.lerp(P1, u) - Vector((0, 0, 2.5 * 4 * u * (1 - u)))
            col = L1 if t % 2 else L2
            box(v.x - 0.55, v.y - 0.55, v.z - 0.9, v.x + 0.55, v.y + 0.55, v.z + 0.1, col, facet=False)
            NEON.face([(v.x - 0.6, v.y - 0.6, v.z - 0.95), (v.x + 0.6, v.y - 0.6, v.z - 0.95), (v.x + 0.6, v.y + 0.6, v.z - 0.95), (v.x - 0.6, v.y + 0.6, v.z - 0.95)], col, (0, 0, 0))
            NEON.face([(v.x - 0.6, v.y - 0.6, v.z + 0.12), (v.x + 0.6, v.y - 0.6, v.z + 0.12), (v.x + 0.6, v.y + 0.6, v.z + 0.12), (v.x - 0.6, v.y + 0.6, v.z + 0.12)], col, (0, 0, 0))
    legs = [(-2, -2), (2, -2), (0, 2)]
    for (x, y) in legs:
        beam((x, y, 0), (0, 0, 34), 0.45, (0.24, 0.2, 0.22))
    for z in range(5, 32, 5):
        kk = z / 34
        pts = [(x * (1 - kk), y * (1 - kk), z) for (x, y) in legs]
        for p, q in zip(pts, pts[1:] + pts[:1]):
            beam(p, q, 0.25, (0.28, 0.24, 0.26))
    for (z, aim) in ((22, (-0.7, -0.5, 0.4)), (27, (0.7, -0.4, 0.5)), (17, (0.2, -0.8, 0.5))):
        dish((0, 0, z), aim, 2.4, 0.8, (0.6, 0.55, 0.58))
    box(-0.6, -0.6, 34, 0.6, 0.6, 35.4, L1, facet=False)
    NEON.face([(-0.7, -0.7, 34), (0.7, -0.7, 34), (0.7, -0.7, 35.4), (-0.7, -0.7, 35.4)], L1, (0, 0, 0))
    if disp:  # post-betrayal: DISPATCH has taken the base - corrupted slabs, red vents, cables into every roof
        for _ in range(40):
            x, y = grng.uniform(-24, 24), grng.uniform(-24, 24)
            s = grng.uniform(0.8, 2.4)
            NEON.face([(x - s, y - s, 0.07), (x + s, y - s, 0.07), (x + s, y + s, 0.07), (x - s, y + s, 0.07)],
                      (1.0, 0.07, 0.09) if grng.random() < 0.7 else (1.0, 0.3, 0.55), (0, 0, 0))
        for (x0, y0, x1, y1, h) in blocks:
            for r in range(2):
                zz = 3 + r * 4
                NEON.face([(x0 + 1, y0 - 0.08, zz), (x1 - 1, y0 - 0.08, zz), (x1 - 1, y0 - 0.08, zz + 0.5), (x0 + 1, y0 - 0.08, zz + 0.5)], (1.0, 0.07, 0.09), (0, 0, 0))
            cable((0, 0, 30), ((x0 + x1) / 2, (y0 + y1) / 2, h), 5, w=0.18, col=(1.0, 0.07, 0.09), acc=NEON)
        text_obj("DISPATCH", (12.3, -16, 6.5), (math.radians(90), 0, math.radians(90)), 1.6, SIGNM)


HEROES25 = {"meridian": container_castle, "solace": double_helix, "halcyon": civic_core_tall, "orbital": orbital_silo,
            "rebel_cell": rebel_base}
