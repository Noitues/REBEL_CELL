"""City-all-corps (exec'd by city_build.py): the seven landmarks at their HQ lots, sized to the landmark clearance
(landmark_r 5.6 lots = 33.6 BU). Each is the current HQ design, simplified to its silhouette at city scale:

  HALCYON     the stepped spiral pyramid (hq_halcyon): 6 tiers, the amber helix gallery climbing face by face, the
              PANOPTICON vault and the eye on the apex
  MERIDIAN    the container fortress (round 30 castle / hq_meridian): container curtain walls, corner towers, the keep,
              the gantry crane over the rail yard
  SOLACE      the tube helix v3 (hq_solace): two smooth swept tubes with porthole rows, a bow-tie bridge per floor
  ORBITAL     the launch ring (hq_orbital): the ring platform, the truss antenna tower, the rocket on its pad, two vaults
  REBEL_CELL  no landmark building (designer): the fist in red windows is its landmark (zoning crest rule)
  AURELIAN    THE CIRCUS AURELIUS (new_corps/roman): an elliptical colosseum, four arcade tiers outside, four seating
              rings inside with verdigris lines, the arena, THE ROSTRUM column and its laurel holo ring
  TETHYS      ATLANTIS STATION (new_corps/atlantis): the surface ring with five pressure-glass domes, the glass shaft
              down the trench, five pressure decks, the vent glow at the bottom
Returns, per corp, (label anchor xyz, crown xyz for its hero beam, landmark lights).
"""

LM = {}
GOLD = (1.0, 0.72, 0.3)


def hq_w(k):
    return W(O["hq"][k])


def spot_at(target, frm, col, power, cone=30.0):
    LIGHT_SPOTS.append(dict(loc=frm, tgt=target, col=col, power=power, cone=cone))


# ------------------------------------------------------------------ HALCYON
def halcyon():
    hx, hy = hq_w("halcyon")
    D = DIST["halcyon"]
    stone = (0.46, 0.43, 0.58)
    z = 0.0                                   # no podium: the city comes up to the bottom tier (designer)
    z = 0.0
    half = [29.0, 24.8, 20.6, 16.4, 12.2, 8.6]
    th = 5.6
    for k, s in enumerate(half):
        box(SURF, hx - s, hy - s, z, hx + s, hy + s, z + th, stone, wc=(1.0, 0.74, 0.38), wl=0.42, wm=0, bid=0.1 * k)
        cs = [(hx - s, hy - s), (hx + s, hy - s), (hx + s, hy + s), (hx - s, hy + s)]
        for i in range(4):
            bar(NEON, (*cs[i], z + th + 0.05), (*cs[(i + 1) % 4], z + th + 0.05), 0.32, D["hue"])
        # the helix gallery: one tier per face, counter-clockwise (S, E, N, W): an amber ribbon along that face
        f = k % 4
        a, c = [(cs[0], cs[1]), (cs[1], cs[2]), (cs[2], cs[3]), (cs[3], cs[0])][f]
        nxv = [(0, -1), (1, 0), (0, 1), (-1, 0)][f]
        o = 1.2
        bar(NEON, (a[0] + nxv[0] * o, a[1] + nxv[1] * o, z + th * 0.55), (c[0] + nxv[0] * o, c[1] + nxv[1] * o, z + th * 0.55 + th * 0.9),
            0.55, (1.0, 0.68, 0.25))
        z += th
    # THE PANOPTICON vault + the eye
    box(SURF, hx - 5.5, hy - 5.5, z, hx + 5.5, hy + 5.5, z + 4.0, sc(stone, 0.9), wc=(1.0, 0.8, 0.5), wl=0.7, wm=0, bid=0.9)
    z += 4.0
    cyl(SMOOTH, hx, hy, z, z + 2.0, 3.6, 16, (0.22, 0.2, 0.3))
    ez = z + 7.0
    # the eye faces the camera: an almond of light, the iris, the pupil
    tx, ty = CAMDIR.x, CAMDIR.y
    ox, oy = -ty, tx

    def P(u, v, d=0.0):
        return (hx + ox * u + tx * d, hy + oy * u + ty * d, ez + v)
    pts = []
    for kk in range(25):
        t = math.pi * kk / 24
        pts.append(P(-6.5 * math.cos(t), 3.4 * math.sin(t)))
    for kk in range(1, 24):
        t = math.pi * kk / 24
        pts.append(P(6.5 * math.cos(t), -3.4 * math.sin(t)))
    NEON.face(pts, (0.95, 0.88, 1.0))
    iris = [P(2.3 * math.cos(2 * math.pi * kk / 20), 2.3 * math.sin(2 * math.pi * kk / 20), 0.1) for kk in range(20)]
    NEON.face(iris, sc(D["hue"], 1.6))
    pup = [P(1.0 * math.cos(2 * math.pi * kk / 16), 1.0 * math.sin(2 * math.pi * kk / 16), 0.2) for kk in range(16)]
    SURF.face(pup, (0.01, 0.01, 0.02))
    bar(SURF, (hx, hy, z + 2.0), (hx, hy, ez - 3.4), 0.8, (0.22, 0.2, 0.3))
    for kk in range(5):            # the lashes (round 15 crest)
        t = math.radians(-90 + (kk - 2) * 26)
        a0 = P(6.0 * math.cos(t) * 0.95, -3.2 * math.sin(t))
        a1 = P(8.4 * math.cos(t) * 0.95, -4.9 * math.sin(t))
        bar(NEON, a0, a1, 0.5, GOLD)
    spot_at((hx, hy, 18), (hx + 90, hy - 90, 70), (0.85, 0.8, 1.0), 2.2e6, 34)
    spot_at((hx, hy, 18), (hx - 70, hy - 110, 30), D["hue"], 1.4e6, 34)
    return (hx, hy, ez + 14), (hx, hy, ez + 5), D["hue"]


# ------------------------------------------------------------------ MERIDIAN
def meridian():
    hx, hy = hq_w("meridian")
    D = DIST["meridian"]
    CC = [(0.72, 0.30, 0.08), (0.58, 0.22, 0.08), (0.14, 0.36, 0.38), (0.45, 0.42, 0.40), (0.80, 0.46, 0.10), (0.62, 0.12, 0.08)]
    r = random.Random(CP.SEEDS["landmark"] + 1)
    S = 28.0
    box(SURF, hx - S, hy - S, 0, hx + S, hy + S, 0.6, (0.26, 0.24, 0.24))
    # container curtain walls: 4 high, containers 6 x 2.4 x 2.6 along each side
    for side in range(4):
        for lv in range(4):
            u = -S
            while u < S - 0.5:
                L = min(6.0, S - u)
                c = CC[r.randrange(len(CC))]
                z0, z1 = 0.6 + lv * 2.6, 0.6 + (lv + 1) * 2.6
                if side == 0:
                    box(SURF, hx + u, hy - S, z0, hx + u + L - 0.15, hy - S + 2.4, z1, c)
                elif side == 1:
                    box(SURF, hx + S - 2.4, hy + u, z0, hx + S, hy + u + L - 0.15, z1, c)
                elif side == 2:
                    gx0, gx1 = CP.RAIL["gate_u"] - 3.0, CP.RAIL["gate_u"] + 3.0     # the NORTH rail-yard gate (2 levels)
                    if lv < 2 and u < gx1 and u + L > gx0:
                        if u < gx0:
                            box(SURF, hx + u, hy + S - 2.4, z0, hx + gx0, hy + S, z1, c)
                        if u + L > gx1:
                            box(SURF, hx + gx1, hy + S - 2.4, z0, hx + u + L - 0.15, hy + S, z1, c)
                    else:
                        box(SURF, hx + u, hy + S - 2.4, z0, hx + u + L - 0.15, hy + S, z1, c)
                else:
                    box(SURF, hx - S, hy + u, z0, hx - S + 2.4, hy + u + L - 0.15, z1, c)
                u += L
    # the gate: an orange-lit portal frame round the opening; the spur from the yard's middle track out through it
    gx = hx + CP.RAIL["gate_u"]
    for o in (-3.0, 3.0):
        bar(NEON, (gx + o, hy + S + 0.1, 0.6), (gx + o, hy + S + 0.1, 0.6 + 2 * 2.6), 0.25, (1.0, 0.55, 0.15))
    bar(NEON, (gx - 3.0, hy + S + 0.1, 0.6 + 2 * 2.6), (gx + 3.0, hy + S + 0.1, 0.6 + 2 * 2.6), 0.25, (1.0, 0.55, 0.15))
    for o in (-0.6, 0.6):
        bar(SURF, (gx + o, hy + 16.6, 0.7), (gx + o, hy + S + CP.RAIL["gate_out"], 0.7), 0.18, (0.5, 0.5, 0.55))
    wz = 0.6 + 4 * 2.6
    for (sx, sy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):       # corner towers, crenellated
        cx_, cy_ = hx + sx * S, hy + sy * S
        box(SURF, cx_ - 4, cy_ - 4, 0, cx_ + 4, cy_ + 4, 21, (0.34, 0.24, 0.18), wc=D["win"][0], wl=0.5, wm=0, bid=0.2)
        for kk in range(4):
            for m in range(3):
                t = -4 + 8 * (m + 0.5) / 3
                p = [(cx_ + t, cy_ - 4), (cx_ + 4, cy_ + t), (cx_ - t, cy_ + 4), (cx_ - 4, cy_ - t)][kk]
                box(SURF, p[0] - 0.7, p[1] - 0.7, 21, p[0] + 0.7, p[1] + 0.7, 22.4, (0.34, 0.24, 0.18))
        ring_line(NEON, cx_, cy_, 21.05, 5.6, 0.3, D["hue"], n=4)
    for i in range(4):
        cs = [(hx - S, hy - S), (hx + S, hy - S), (hx + S, hy + S), (hx - S, hy + S)]
        bar(NEON, (*cs[i], wz + 0.1), (*cs[(i + 1) % 4], wz + 0.1), 0.3, D["hue"])
    # the keep
    box(SURF, hx - 8, hy - 4, 0, hx + 6, hy + 10, 34, (0.32, 0.22, 0.16), wc=D["win"][0], wl=0.55, wm=0, bid=0.4)
    box(SURF, hx - 6, hy - 2, 34, hx + 4, hy + 8, 40, (0.30, 0.20, 0.15), wc=D["win"][1], wl=0.7, wm=0, bid=0.45)
    for i, (x0, y0, x1, y1) in enumerate(((-8, -4, 6, -4), (6, -4, 6, 10))):
        bar(NEON, (hx + x0, hy + y0, 34.1), (hx + x1, hy + y1, 34.1), 0.35, D["hue"])
    # the rail yard (north half, behind the keep): three tracks across the yard, sodium lamps
    for k in range(3):
        y = hy + 20 - k * 3.4
        for o in (-0.6, 0.6):
            bar(SURF, (hx - S + 2.5, y + o, 0.7), (hx + S - 2.5, y + o, 0.7), 0.18, (0.5, 0.5, 0.55))
        for m in range(4):
            x = hx - 20 + m * 13 + k * 3
            box(SURF, x, y - 1.1, 0.8, x + 6.0, y + 1.1, 3.2, CC[(k + m) % len(CC)])
    for m in range(6):
        x = hx - 22 + m * 9
        bar(SURF, (x, hy + 24, 0.6), (x, hy + 24, 8), 0.25, (0.3, 0.3, 0.32))
        box(NEON, x - 0.6, hy + 23.4, 8, x + 0.6, hy + 24.6, 8.5, (1.0, 0.6, 0.2))
    # the gantry crane straddling the yard
    CR = (0.95, 0.42, 0.08)
    for x in (hx - 22, hx + 22):
        for y in (hy + 24, hy + 12):
            bar(SURF, (x, y, 0.6), (x, y, 44), 1.4, CR)
        bar(SURF, (x, hy + 24, 44), (x, hy + 12, 44), 1.4, CR)
        for zz in (12, 24, 36):
            bar(SURF, (x, hy + 24, zz), (x, hy + 12, zz + 10), 0.5, CR)
    for y in (hy + 24, hy + 12):
        bar(SURF, (hx - 22, y, 44.5), (hx + 22, y, 44.5), 1.8, CR)
    box(SURF, hx - 3, hy + 11, 43, hx + 4, hy + 25, 47, (0.75, 0.32, 0.06))
    bar(SURF, (hx + 0.5, hy + 18, 43), (hx + 0.5, hy + 18, 22), 0.15, (0.2, 0.2, 0.22))
    box(SURF, hx - 1.4, hy + 16.8, 19.5, hx + 3.0, hy + 19.2, 22, CC[0])
    for x in (hx - 22, hx + 22):
        box(NEON, x - 0.5, hy + 17.5, 47.0, x + 0.5, hy + 18.5, 47.8, (1.0, 0.08, 0.06))
    bar(NEON, (hx - 22, hy + 24.9, 43.5), (hx + 22, hy + 24.9, 43.5), 0.3, D["hue"])
    spot_at((hx, hy, 14), (hx + 80, hy - 100, 60), (1.0, 0.75, 0.5), 2.4e6, 38)
    spot_at((hx, hy + 18, 30), (hx + 60, hy - 40, 40), D["hue"], 1.2e6, 30)
    return (hx, hy, 58), (hx - 1, hy + 3, 40.5), D["hue"]


# ------------------------------------------------------------------ SOLACE
def solace():
    hx, hy = hq_w("solace")
    D = DIST["solace"]
    cyl(SURF, hx, hy, 0, 2.5, 12.0, 24, (0.38, 0.44, 0.42), wc=D["win"][0], wl=0.4, wm=1, bid=0.2)
    ring_line(NEON, hx, hy, 2.55, 12.05, 0.35, D["hue"], n=24)
    R, rt, z0, z1 = 7.5, 3.4, 2.5, 86.0
    pitch = 62.0
    steps = 90
    nseg = 16
    tube_col = (0.82, 0.86, 0.84)

    def cpos(ph, z):
        t = 2 * math.pi * (z - z0) / pitch + ph
        return Vector((hx + R * math.cos(t), hy + R * math.sin(t), z))
    for ph in (0.0, math.pi):
        rings = []
        for k in range(steps + 1):
            z = z0 + (z1 - z0) * k / steps
            c = cpos(ph, z)
            tng = (cpos(ph, z + 0.2) - cpos(ph, z - 0.2)).normalized()
            nrm = Vector((c.x - hx, c.y - hy, 0)).normalized()
            bnm = tng.cross(nrm).normalized()
            nrm = bnm.cross(tng).normalized()
            rings.append([c + (nrm * math.cos(2 * math.pi * m / nseg) + bnm * math.sin(2 * math.pi * m / nseg)) * rt for m in range(nseg)])
        circ = 2 * math.pi * rt
        for k in range(steps):
            v0 = (z1 - z0) * k / steps
            v1 = (z1 - z0) * (k + 1) / steps
            for m in range(nseg):
                m1 = (m + 1) % nseg
                u0, u1 = circ * m / nseg, circ * (m + 1) / nseg
                SMOOTH.face([tuple(rings[k][m]), tuple(rings[k][m1]), tuple(rings[k + 1][m1]), tuple(rings[k + 1][m])], tube_col,
                            [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], (0.82, 1.0, 0.88), 0.62, 2, 0.3 + ph * 0.1, 0)
        # crown cap
        dome(SMOOTH, *tuple(cpos(ph, z1))[:2], z1, rt, sc(D["hue"], 0.5), n=nseg, rings=4)
    # bow-tie bridges, one per floor (every 4.2 BU): wide at the tubes, pinched at the axis, lime edges
    z = z0 + 3.0
    while z < z1 - 2:
        a, c = cpos(0.0, z), cpos(math.pi, z)
        d = (c - a).normalized()
        s = Vector((-d.y, d.x, 0))
        m = (a + c) / 2
        pts = [a + s * 2.6, m + s * 0.7, c + s * 2.6, c - s * 2.6, m - s * 0.7, a - s * 2.6]
        SURF.face([tuple(p) for p in pts], (0.7, 0.75, 0.72))
        for i in range(6):
            bar(NEON, tuple(pts[i] + Vector((0, 0, 0.05))), tuple(pts[(i + 1) % 6] + Vector((0, 0, 0.05))), 0.14, D["hue"])
        z += 4.2
    for ph in (0.0, math.pi):
        c = cpos(ph, z1 + rt)
        box(NEON, c.x - 0.5, c.y - 0.5, c.z, c.x + 0.5, c.y + 0.5, c.z + 1.2, (1.0, 0.25, 0.25))
    spot_at((hx, hy, 40), (hx + 70, hy - 70, 10), (0.85, 1.0, 0.9), 1.6e6, 40)
    spot_at((hx, hy, 50), (hx - 50, hy - 80, 5), D["hue"], 1.2e6, 36)
    return (hx, hy, z1 + 12), (hx, hy, z1 + 3), D["hue"]


# ------------------------------------------------------------------ ORBITAL
def orbital():
    """hq_orbital (current): the round launch podium, the SILO at its centre (caution ring, two door leaves open), the
    rocket risen out of it (white, two red bands), the red service gantry with LAUNCH CONTROL, the truss antenna with its
    elite vaults, dish stations on the rim. No floor glow (designer): the rocket is lit by a white key from the camera
    side and its own service light; the silo shaft only glows faintly inside."""
    hx, hy = hq_w("orbital")
    D = DIST["orbital"]
    steel = (0.48, 0.52, 0.60)
    R = 22.0
    cyl(SURF, hx, hy, 0, 3.4, R, 64, steel, wc=(0.8, 0.9, 1.0), wl=0.45, wm=1, bid=0.5, top=False)
    annulus(SURF, hx, hy, 3.4, 6.0, R, (0.30, 0.32, 0.38), n=64)
    ring_line(NEON, hx, hy, 3.45, R + 0.05, 0.3, D["sec"], n=64)
    # the silo: a dark shaft, the yellow-black caution ring (paint, not light), two door leaves swung open
    rs = 6.0
    cyl(SURF, hx, hy, -30.0, 3.45, rs, 32, (0.05, 0.05, 0.07), top=False)
    for k in range(24):
        t0, t1 = 2 * math.pi * k / 24, 2 * math.pi * (k + 1) / 24
        col = (0.85, 0.68, 0.10) if k % 2 == 0 else (0.06, 0.06, 0.06)
        SURF.face([(hx + rs * math.cos(t0), hy + rs * math.sin(t0), 3.46), (hx + (rs + 1.6) * math.cos(t0), hy + (rs + 1.6) * math.sin(t0), 3.46),
                   (hx + (rs + 1.6) * math.cos(t1), hy + (rs + 1.6) * math.sin(t1), 3.46), (hx + rs * math.cos(t1), hy + rs * math.sin(t1), 3.46)], col)
    for zz in (-6.0, -14.0):
        ring_line(NEON, hx, hy, zz, rs - 0.15, 0.3, sc((1.0, 0.4, 0.2), 0.35), n=24)
    for side in (-1, 1):                      # door leaves: half discs hinged on the rim, opened to 75 degrees
        hxv = hx + side * (rs + 0.2)
        pts = []
        for k in range(9):
            t = math.pi * k / 8
            u = rs * math.sin(t)
            v = rs * math.cos(t)
            a = math.radians(75)
            pts.append((hxv - side * u * math.cos(a), hy + v, 3.5 + u * math.sin(a)))
        SURF.face(pts, (0.62, 0.66, 0.72))
        for k in range(3):
            v = -3 + 3 * k
            bar(SURF, (hxv, hy + v, 3.5), (hxv - side * 4.5 * math.cos(math.radians(75)), hy + v, 3.5 + 4.5 * math.sin(math.radians(75))),
                0.25, (0.85, 0.68, 0.1))
    # the rocket, risen out of the silo
    rr_ = 2.4
    cyl(SMOOTH, hx, hy, -10.0, 30.0, rr_, 20, (0.93, 0.93, 0.96))
    for zz in (9.0, 21.0):
        cyl(SMOOTH, hx, hy, zz, zz + 1.6, rr_ + 0.05, 20, (0.85, 0.12, 0.10))
    cyl(SMOOTH, hx, hy, 30.0, 38.0, rr_, 20, (0.93, 0.93, 0.96), ts=0.04)
    for k in range(4):
        t = 2 * math.pi * k / 4 + 0.3
        p0 = (hx + rr_ * math.cos(t), hy + rr_ * math.sin(t))
        p1 = (hx + (rr_ + 2.2) * math.cos(t), hy + (rr_ + 2.2) * math.sin(t))
        SURF.face([(p0[0], p0[1], 3.6), (p1[0], p1[1], 3.6), (p1[0], p1[1], 6.5), (p0[0], p0[1], 11.0)], (0.85, 0.12, 0.10))
    # the red service gantry south of the silo, LAUNCH CONTROL deck near its top
    gx, gy = hx, hy - 10.5
    RED_G = (0.72, 0.14, 0.10)
    for (dx, dy) in ((-1.8, -1.8), (1.8, -1.8), (1.8, 1.8), (-1.8, 1.8)):
        bar(SURF, (gx + dx, gy + dy, 3.4), (gx + dx, gy + dy, 30.0), 0.45, RED_G)
    for zz in range(5, 30, 4):
        bar(SURF, (gx - 1.8, gy - 1.8, zz), (gx + 1.8, gy + 1.8, zz + 4), 0.22, RED_G)
        bar(SURF, (gx + 1.8, gy - 1.8, zz), (gx - 1.8, gy + 1.8, zz + 4), 0.22, RED_G)
    for zz in (12.0, 22.0):
        bar(SURF, (gx, gy + 1.8, zz), (hx, hy - rr_ - 0.2, zz), 0.5, RED_G)
    box(SURF, gx - 3.2, gy - 3.2, 24.0, gx + 3.2, gy + 3.2, 27.0, (0.20, 0.22, 0.26), wc=(0.85, 0.95, 1.0), wl=0.9, wm=1, bid=0.77)
    box(NEON, gx - 0.4, gy - 0.4, 30.0, gx + 0.4, gy + 0.4, 30.8, (1.0, 0.08, 0.06))
    # the truss antenna tower on the rim (two elite vaults at its feet)
    tx, ty = hx + 14.0, hy + 12.0
    H = 74.0
    legs = []
    for (dx, dy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        legs.append(((tx + dx * 3.6, ty + dy * 3.6, 3.4), (tx + dx * 0.7, ty + dy * 0.7, H)))
        bar(SURF, legs[-1][0], legs[-1][1], 0.5, (0.66, 0.70, 0.78))
    nb = 14
    for k in range(nb):
        t0, t1 = k / nb, (k + 1) / nb
        for i in range(4):
            j = (i + 1) % 4
            pa = Vector(legs[i][0]).lerp(Vector(legs[i][1]), t0)
            pb = Vector(legs[j][0]).lerp(Vector(legs[j][1]), t1)
            bar(SURF, tuple(pa), tuple(pb), 0.2, (0.62, 0.66, 0.74))
            pc = Vector(legs[j][0]).lerp(Vector(legs[j][1]), t0)
            bar(SURF, tuple(pa), tuple(pc), 0.2, (0.62, 0.66, 0.74))
    for zz in (H * 0.35, H * 0.65):
        box(SURF, tx - 3.0, ty - 3.0, zz, tx + 3.0, ty + 3.0, zz + 2.4, (0.22, 0.24, 0.30), wc=(0.8, 0.9, 1.0), wl=0.85, wm=1, bid=0.6)
    for zz in (H * 0.5, H + 0.2):
        box(NEON, tx - 0.5, ty - 0.5, zz, tx + 0.5, ty + 0.5, zz + 0.9, (1.0, 0.08, 0.06))
    bar(SURF, (tx, ty, H), (tx, ty, H + 9), 0.3, (0.7, 0.72, 0.8))
    ring_line(NEON, tx, ty, H - 5, 2.0, 0.3, D["hue"], n=12)
    for (vx, vy, vc) in ((tx - 7.5, ty + 1.0, (1.0, 0.35, 0.8)), (tx + 1.0, ty - 7.5, (0.35, 0.9, 1.0))):
        dome(GLASS, vx, vy, 3.4, 3.4, (0.8, 0.9, 1.0), n=16, rings=5)
        dome(NEON, vx, vy, 3.4, 2.4, sc(vc, 0.5), n=12, rings=4)
    # dish stations round the rim
    for k in range(3):
        t = math.radians(150 + 70 * k)
        dx_, dy_ = hx + (R - 4.5) * math.cos(t), hy + (R - 4.5) * math.sin(t)
        cyl(SURF, dx_, dy_, 3.4, 5.5, 1.4, 10, steel)
        annulus(SURF, dx_, dy_, 8.0, 0.01, 3.2, (0.85, 0.88, 0.92), n=14, z1=6.0)
    # the key: white on the rocket from the camera side, a cool rim from behind
    # the floodlit apron (art review): six flood masts on the rim light the podium disc, a light ring round its edge
    for k in range(6):
        t = 2 * math.pi * k / 6 + 0.25
        mx_, my_ = hx + (R - 1.2) * math.cos(t), hy + (R - 1.2) * math.sin(t)
        bar(SURF, (mx_, my_, 3.4), (mx_, my_, 15.0), 0.4, (0.5, 0.52, 0.58))
        box(NEON, mx_ - 0.7, my_ - 0.7, 15.0, mx_ + 0.7, my_ + 0.7, 15.6, (1.0, 0.97, 0.9))
        spot_at((hx + (mx_ - hx) * -0.3, hy + (my_ - hy) * -0.3, 3.4), (mx_, my_, 15.3), (1.0, 0.96, 0.9), 2.5e5, 70)
    ring_line(NEON, hx, hy, 3.5, R - 0.6, 0.55, (0.85, 0.93, 1.0), n=64)
    for k in range(32):                       # rim lamps
        t = 2 * math.pi * k / 32
        box(NEON, hx + (R + 0.4) * math.cos(t) - 0.2, hy + (R + 0.4) * math.sin(t) - 0.2, 1.6,
            hx + (R + 0.4) * math.cos(t) + 0.2, hy + (R + 0.4) * math.sin(t) + 0.2, 2.0, (0.75, 0.88, 1.0))
    spot_at((hx, hy, 18), (hx + 55, hy - 60, 45), (1.0, 0.98, 0.95), 1.6e6, 16)
    spot_at((hx, hy, 18), (hx - 40, hy + 40, 50), (0.7, 0.8, 1.0), 0.6e6, 16)
    return (hx, hy, 52), (tx, ty, H + 9), D["hue"]


# ------------------------------------------------------------------ AURELIAN: the Circus Aurelius
def aurelian():
    hx, hy = hq_w("aurelian")
    D = DIST["aurelian"]
    tr = D["mat"][0]
    A, Bk = 31.0, 0.8           # semi-major (x), minor/major ratio
    n = 64
    tiers = 4
    th = 5.0
    # outer wall: four arcade tiers (lit gilt arches), a cornice per tier
    for k in range(tiers):
        z0, z1 = k * th, (k + 1) * th
        pts = circle(hx, hy, A, n, ry=A * Bk)
        prism(SURF, pts, z0, z1, sc(tr, 1.0 - 0.04 * k), top=False, wc=(1.0, 0.76, 0.42), wl=0.8 if k < 3 else 0.0, wm=4 if k < 3 else 0,
              bid=0.1 * k, uvs=(1.6 / 3.4, 1.9 / th), vz0=0.0)
        ring_line(SURF, hx, hy, z1, A + 0.2, 0.5, sc(tr, 1.05), n=n, ry=A * Bk + 0.2)
    ring_line(NEON, hx, hy, tiers * th + 0.3, A + 0.25, 0.3, D["sec"], n=n, ry=A * Bk + 0.25)
    # the cavea: four seating rings stepping down to the arena, each ring edge in verdigris
    rs = [A - 0.5, A * 0.86, A * 0.72, A * 0.6, A * 0.48]
    zs = [tiers * th, 15.0, 10.5, 6.5, 3.0]
    for k in range(4):
        annulus(SURF, hx, hy, zs[k], rs[k + 1], rs[k], sc(tr, 0.82 - 0.05 * k), n=n, k0=Bk, k1=Bk, z1=zs[k + 1] + 1.2)
        prism(SURF, circle(hx, hy, rs[k + 1], n, ry=rs[k + 1] * Bk), zs[k + 1], zs[k + 1] + 1.2, sc(tr, 0.7), top=False)
        ring_line(NEON, hx, hy, zs[k + 1] + 1.25, rs[k + 1], 0.32, D["sec"], n=n, ry=rs[k + 1] * Bk)
    # the arena: lit sand, THE ROSTRUM (porphyry plinth, colonnade ring, the core column with lit rings), laurel holo
    prism(NEON, circle(hx, hy, rs[4], n, ry=rs[4] * Bk), 0.0, 3.0, sc((1.0, 0.72, 0.42), 0.35), top=True)
    cyl(SURF, hx, hy, 3.0, 4.2, 5.0, 20, (0.23, 0.08, 0.15))
    for kk in range(12):
        t = 2 * math.pi * kk / 12
        bar(SURF, (hx + 4.2 * math.cos(t), hy + 4.2 * math.sin(t), 4.2), (hx + 4.2 * math.cos(t), hy + 4.2 * math.sin(t), 7.5), 0.45, (0.95, 0.92, 0.85))
    cyl(SURF, hx, hy, 7.5, 8.0, 4.8, 20, (0.95, 0.92, 0.85))
    cyl(SMOOTH, hx, hy, 4.2, 22.0, 1.6, 14, (0.92, 0.88, 0.80))
    for zz in (10.0, 14.0, 18.0, 22.0):
        ring_line(NEON, hx, hy, zz, 1.75, 0.35, D["sec"], n=14)
    ring_line(NEON, hx, hy, 25.0, 7.0, 0.42, sc(D["sec"], 1.2), n=40)
    for kk in range(16):             # laurel leaves on the holo ring
        t = 2 * math.pi * kk / 16
        p0 = (hx + 7.0 * math.cos(t), hy + 7.0 * math.sin(t), 25.0)
        p1 = (hx + 8.6 * math.cos(t + 0.15), hy + 8.6 * math.sin(t + 0.15), 26.0)
        bar(NEON, p0, p1, 0.35, sc(D["sec"], 1.2))
    box(NEON, hx - 0.6, hy - 0.6, 22.0, hx + 0.6, hy + 0.6, 23.4, (1.0, 0.85, 0.5))
    # four campanili on the colosseum's diagonals (flat crowns), the district's signature
    for kk in range(4):
        t = math.radians(45 + 90 * kk)
        cx_, cy_ = hx + (A + 3.5) * math.cos(t), hy + (A * Bk + 3.5) * math.sin(t)
        rad = 2.3
        cyl(SMOOTH, cx_, cy_, 0, 3, rad * 1.15, 14, tr)
        zz = 3.0
        for m in range(8):
            cyl(SMOOTH, cx_, cy_, zz, zz + 3.2, rad, 14, tr, wc=(1.0, 0.8, 0.5), wl=0.8, wm=4, bid=0.3 + kk * 0.1, uvs=(1.6 / 1.3, 1.9 / 3.2), vz0=0.0)
            cyl(SURF, cx_, cy_, zz + 3.2, zz + 3.45, rad * 1.1, 14, tr)
            zz += 3.45
        cyl(SURF, cx_, cy_, zz, zz + 0.5, rad * 1.18, 14, tr)
        cyl(SURF, cx_, cy_, zz + 0.5, zz + 1.1, rad * 1.05, 14, tr, top=False)
        ring_line(NEON, cx_, cy_, zz + 0.6, rad * 1.22, 0.28, D["sec"], n=14)
        box(NEON, cx_ - 0.5, cy_ - 0.5, zz - 4.0, cx_ + 0.5, cy_ + 0.5, zz - 2.6, (1.0, 0.8, 0.4))
    # the arena searchlight floods
    spot_at((hx, hy, 6), (hx + 70, hy - 80, 55), (1.0, 0.86, 0.66), 2.4e6, 40)
    spot_at((hx, hy, 6), (hx - 75, hy - 50, 35), D["sec"], 1.4e6, 38)
    return (hx, hy, 40), (hx, hy, 26), D["sec"]


# ------------------------------------------------------------------ TETHYS: Atlantis Station
STATION = {}


def tethys():
    hx, hy = hq_w("tethys")
    D = DIST["tethys"]
    ti = (0.42, 0.46, 0.52)
    bed = -max(WET_CELLS.get((int(math.floor(O["hq"]["tethys"][0])), int(math.floor(O["hq"]["tethys"][1]))), 60.0), 60.0)
    # the surface ring (titanium deck at the waterline, portholes), the shaft cap
    annulus(SURF, hx, hy, ZW + 2.2, 9.0, 15.0, ti, n=40)
    cyl(SURF, hx, hy, ZW - 3.0, ZW + 2.2, 15.0, 40, ti, top=False, wc=(1.0, 0.91, 0.72), wl=0.7, wm=2, bid=0.2, wet=1)
    ring_line(NEON, hx, hy, ZW + 2.3, 15.1, 0.4, D["hue"], n=40)
    ring_line(NEON, hx, hy, ZW + 0.2, 15.2, 0.3, D["sec"], n=40)
    # the glass shaft from the trench floor to the cap
    cyl(GLASS, hx, hy, bed, ZW + 12.0, 5.0, 24, (0.6, 0.85, 1.0), wet=1)
    cyl(NEON, hx, hy, bed, ZW + 11.0, 1.2, 8, sc((1.0, 0.91, 0.72), 0.55), wet=1)   # the lift core light
    cyl(SURF, hx, hy, ZW + 12.0, ZW + 14.0, 6.2, 24, ti)
    ring_line(NEON, hx, hy, ZW + 14.05, 6.3, 0.35, D["hue"], n=24)
    box(NEON, hx - 0.5, hy - 0.5, ZW + 14.0, hx + 0.5, hy + 0.5, ZW + 15.2, (0.78, 0.15, 0.3))
    # five pressure-glass domes round the ring (the surface township): hemisphere above, the lower hull below
    for k in range(5):
        t = math.radians(-90 + 72 * k + 18)
        dx, dy = hx + 24.5 * math.cos(t), hy + 24.5 * math.sin(t)
        rd = 8.5
        cyl(SURF, dx, dy, ZW - 6.0, ZW + 1.0, rd + 0.6, 24, ti, wc=(1.0, 0.91, 0.72), wl=0.8, wm=2, bid=0.4 + k * 0.1, wet=1)
        dome(GLASS, dx, dy, ZW + 1.0, rd, (0.65, 0.88, 1.0), n=24, rings=7)
        for m in range(8):                       # ribs (meridians)
            a0 = 2 * math.pi * m / 8
            prev = None
            for kk in range(8):
                ph = math.pi / 2 * kk / 7
                p = (dx + rd * math.cos(ph) * math.cos(a0), dy + rd * math.cos(ph) * math.sin(a0), ZW + 1.0 + rd * math.sin(ph))
                if prev:
                    bar(SURF, prev, p, 0.18, (0.55, 0.6, 0.66))
                prev = p
        ring_line(NEON, dx, dy, ZW + 1.05, rd + 0.65, 0.35, D["hue"], n=24)
        rr = random.Random(7103 + k)
        for m in range(9):                       # the lit township inside
            px, py = dx + rr.uniform(-4, 4), dy + rr.uniform(-4, 4)
            if math.hypot(px - dx, py - dy) > 4.6:
                continue
            hh = rr.uniform(1.2, 4.5) * (1 - math.hypot(px - dx, py - dy) / 7.5)
            box(SURF, px - 0.8, py - 0.8, ZW + 1.0, px + 0.8, py + 0.8, ZW + 1.0 + hh, (0.4, 0.38, 0.36), wc=(1.0, 0.91, 0.72),
                wl=0.9, wm=0, bid=rr.random())
        box(NEON, dx - 3.5, dy - 3.5, ZW + 1.0, dx + 3.5, dy + 3.5, ZW + 1.05, sc((1.0, 0.91, 0.72), 0.5))
        # a glass tube from each dome to the ring, at the waterline
        bar(GLASS, (dx, dy, ZW + 0.5), (hx + 15 * math.cos(t), hy + 15 * math.sin(t), ZW + 0.5), 2.0, (0.6, 0.85, 1.0))
        STATION.setdefault("domes", []).append((dx, dy))
    # five pressure decks hung down the trench (lit porthole rims, abyss rings), drops between them
    decks = [ZW - 9.0, ZW - 25.0, ZW - 41.0, ZW - 57.0, ZW - 73.0]
    for k, zd in enumerate(decks):
        rdk = 16.0 - k * 0.8
        cyl(SURF, hx, hy, zd - 3.2, zd, rdk, 40, ti, wc=(1.0, 0.91, 0.72), wl=0.85, wm=2, bid=0.1 * k, wet=1, bottom=True)
        ring_line(NEON, hx, hy, zd + 0.05, rdk + 0.05, 0.45, D["hue"], n=40, wet=1)
        ring_line(NEON, hx, hy, zd - 3.25, rdk + 0.05, 0.3, D["sec"], n=40, wet=1)
        for m in range(6):                       # deck rooms on the rim (lit pods)
            t = 2 * math.pi * m / 6 + k * 0.3
            box(SURF, hx + (rdk - 2) * math.cos(t) - 1.5, hy + (rdk - 2) * math.sin(t) - 1.5, zd, hx + (rdk - 2) * math.cos(t) + 1.5,
                hy + (rdk - 2) * math.sin(t) + 1.5, zd + 2.2, ti, wc=(1.0, 0.91, 0.72), wl=0.9, wm=0, bid=0.3 + m * 0.1, wet=1)
        if k < 4:
            t = 2 * math.pi * (k * 0.37)
            bar(GLASS, (hx + 10 * math.cos(t), hy + 10 * math.sin(t), zd - 3.2), (hx + 10 * math.cos(t), hy + 10 * math.sin(t), decks[k + 1]),
                1.6, (0.6, 0.85, 1.0), wet=1)
    # ballast column (the tide gauge) and the vent at the trench floor: the black smoker's glow
    bx_, by_ = hx - 12.0, hy + 9.0
    cyl(GLASS, bx_, by_, bed + 4, ZW + 6.0, 1.6, 12, (0.6, 0.85, 1.0), wet=1)
    cyl(NEON, bx_, by_, bed + 4, ZW - 18.0, 1.3, 12, sc(D["hue"], 0.5), wet=1)
    ring_line(NEON, bx_, by_, ZW - 18.0, 1.7, 0.4, D["sec"], n=12, wet=1)
    cyl(SURF, hx + 8, hy - 6, bed, bed + 14, 3.0, 10, (0.08, 0.07, 0.07), ts=0.4, wet=1)
    cyl(NEON, hx + 8, hy - 6, bed + 13, bed + 15, 1.0, 8, (1.0, 0.35, 0.12), wet=1)
    STATION.update(centre=(hx, hy), bed=bed, decks=decks)
    spot_at((hx, hy, ZW + 4), (hx + 25, hy - 30, 70), (0.85, 0.95, 1.0), 0.5e6, 22)
    return (hx, hy, ZW + 26), (hx, hy, ZW + 15), D["hue"]


# ------------------------------------------------------------------ REBEL_CELL: no building; anchor on the fist
SIGNS = []        # (four corners, image path) textured emissive panels, built in city_render


def rebel_cell():
    """No landmark building (designer). The landmark is the district itself: the Tokyo street canyon (building language
    'tenement') with the fist subtle in red windows, and the red MAINFRAME blade sign (round 33 v4, locked) on a shop
    front. Rule: the REBEL_CELL building nearest the Cell's CORE node with a camera-facing street face >= 4 BU and at
    least 10 BU tall carries it at that face's corner, out over the street (3 x 12 BU, the sign's own 1:4 aspect)."""
    net = json.load(open(CP.NET36))
    core = next(nd for nd in net["nodes"] if nd["state"] == "core")
    best = None
    for b in O["buildings"]:
        if b["terr"] != "rebel_cell" or b["h"] * KH < 10 or b.get("wet"):
            continue
        q = [W(p) for p in b["q"]]
        n = len(q)
        cxq, cyq = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
        for i in range(n):
            vis, nrm, L = seen(q[i], q[(i + 1) % n], cxq, cyq)
            if vis and L >= 4.0:
                d = math.hypot(b["c"][0] - core["lot"][0], b["c"][1] - core["lot"][1])
                key = (round(d, 3), b["key"], i)
                if best is None or key < best[0]:
                    best = (key, q[i], q[(i + 1) % n], nrm, b)
                break
    _, a, c, (nx, ny), b = best
    L = math.hypot(c[0] - a[0], c[1] - a[1])
    ux_, uy_ = (c[0] - a[0]) / L, (c[1] - a[1]) / L
    px, py = a[0] + ux_ * 0.8, a[1] + uy_ * 0.8
    z0s, z1s, w_ = 2.4, 14.4, 3.0
    SIGNS.append(([(px + nx * 0.3, py + ny * 0.3, z0s), (px + nx * (0.3 + w_), py + ny * (0.3 + w_), z0s),
                   (px + nx * (0.3 + w_), py + ny * (0.3 + w_), z1s), (px + nx * 0.3, py + ny * 0.3, z1s)],
                  os.path.join(CP.SCR, "mainframe_blade.png")))
    # the red wash of the sign on its shop front (the round 33 spill), and the shop's own red front
    NEON.face([(a[0] + nx * 0.08, a[1] + ny * 0.08, 0.15), (c[0] + nx * 0.08, c[1] + ny * 0.08, 0.15),
               (c[0] + nx * 0.08, c[1] + ny * 0.08, 1.4), (a[0] + nx * 0.08, a[1] + ny * 0.08, 1.4)], (1.0, 0.16, 0.12))
    spot_at((px, py, 8.0), (px + nx * 6 + ux_ * 3, py + ny * 6 + uy_ * 3, 3.0), (1.0, 0.12, 0.08), 3.0e4, 70)
    STATION["mainframe"] = (px + nx * 1.8, py + ny * 1.8, 8.4)
    print("MAINFRAME on building", b["key"], "at", (round(px), round(py)), flush=True)
    pts = [p for seg in O["fist"] for p in seg]
    if pts:
        fx = sum(p[0] for p in pts) / len(pts)
        fy = sum(p[1] for p in pts) / len(pts)
    else:
        fx, fy = O["hq"]["rebel_cell"]
    x, y = W((fx, fy))
    return (x, y, 34), None, DIST["rebel_cell"]["hue"]


for _k, _fn in (("halcyon", halcyon), ("meridian", meridian), ("solace", solace), ("orbital", orbital),
                ("aurelian", aurelian), ("tethys", tethys), ("rebel_cell", rebel_cell)):
    LM[_k] = _fn()
    print("LANDMARK", _k, flush=True)
