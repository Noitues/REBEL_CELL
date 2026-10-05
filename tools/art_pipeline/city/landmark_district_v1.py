# ART-5 5b: the REBEL_CELL district builder (v1). NOT a module: landmark_build_v1.py exec()s it into its namespace
# (Acc, beam, strip, SOLID, NEON, WIN, KN, CORP_KNOBS, WIN_COLS from the concept target_corps / heroes24).
#
# Bible 4.4 (LOCKED, round 34): no tower, a normal street grid, no fist roads, no painted roofs, no holograms. The fist
# is drawn in red WINDOWS of ordinary buildings (landmark_crest_v1: the round 34 tucked-thumb crest on the iso screen
# plane); its detail lines are buildings with no windows; the blackout ring around it goes dark in the reveal.
# Buildings follow the round 36 unified-city recipe (unified40.city_building: window grid 1.6 x 1.9 BU on the walls
# the camera sees, neon roof trims in the building's ink, round 6 families, no district tint), with 4 jittered
# triangles a wall (the 1.7 BU facet grid is the CityModel shader's job; it kept this glb game-sized).
#
# Window meshes (each window's face attribute fj carries its own seeded value 0-1, exported as COLOR_0 alpha):
#   win_city        : outside the ring, the city's own share (0.3), always lit
#   win_ring        : inside the blackout ring; lit before the reveal (density 0.9 = the washed-out start), off once the
#                     blackout front passes (visible while alpha > q, a flicker band at the front)
#   win_lines       : on the fist's detail lines; lit before the reveal (visible while alpha < (1 - q) * 0.85)
#   win_fist_home   : the red fist, home look (alpha < 0.70 = bible's 70 % density)
#   win_fist_dispatch : the red fist, DISPATCH look (glitch bands shift rows sideways; 0.90 density, a few white)
# Building solids on a detail line go to the "lines" mesh (map34: darkened toward (8, 6, 12) by 0.55 * q).
import landmark_crest_v1 as CR

DLINES = Acc("lines")
WRING = Acc("win_ring")
WLINES = Acc("win_lines")
WFIST_H = Acc("win_fist_home")
WFIST_D = Acc("win_fist_dispatch")
DIST_ACCS = {"lines": DLINES, "win_ring": WRING, "win_lines": WLINES, "win_fist_home": WFIST_H, "win_fist_dispatch": WFIST_D}
FAMS_D = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36), (0.40, 0.38, 0.46)]
FIST_GROW = 0.25   # the red panes are 1.3 x 1.2 BU (0.8 x 0.7 elsewhere)
FIST_RED = {"home": (0.95, 0.24, 0.22), "dispatch": (1.0, 0.09, 0.14)}   # unified40.CREST_RED; dispatch harsher (map34.RED)
CITY_WIN = [(1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)]
CAMDIR = (0.7071067811865476, -0.7071067811865476)   # from the scene toward the iso camera (yaw 135)


def _window(acc, p0, p1, z, col, fj, grow=0.0):
    """A window pane 0.8 x 0.7 BU on the wall (grow: extra BU on every side; the red fist panes are bigger, as
    map34 lights the crest's windows denser and brighter so the fist reads at the City Grid zoom)."""
    ux, uy = (p1[0] - p0[0]) / 0.8, (p1[1] - p0[1]) / 0.8
    a = (p0[0] - ux * grow, p0[1] - uy * grow)
    b = (p1[0] + ux * grow, p1[1] + uy * grow)
    z0, z1 = z - grow, z + 0.7 + grow
    acc.face([(a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1)], col, (0, 0, 0), fj=fj)


def _district_building(q, h, r, trims):
    n = len(q)
    cx = sum(p[0] for p in q) / n
    cy = sum(p[1] for p in q) / n
    X, Y = CR.screen((cx, cy, h * 0.5))
    on_line = CR.zone(X, Y) == 2
    acc = DLINES if on_line else SOLID
    col = FAMS_D[r.randrange(len(FAMS_D))]
    bid = (r.random(), r.random(), r.random())
    for i in range(n):
        j = (i + 1) % n
        a, c = q[i], q[j]
        quad = [(a[0], a[1], 0.0), (c[0], c[1], 0.0), (c[0], c[1], h), (a[0], a[1], h)]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        ux, uy = (c[0] - a[0]) / (L or 1), (c[1] - a[1]) / (L or 1)
        nx, ny = uy, -ux
        if nx * (a[0] - cx) + ny * (a[1] - cy) < 0:
            nx, ny = -nx, -ny
        seen = nx * CAMDIR[0] + ny * CAMDIR[1] > 0.1
        acc.facet_quad(*quad, col, bid)  # 4 jittered triangles a wall (the city's own walls get the 1.7 BU grid in 5a's shader)
        if not seen or L < 1.2 or h < 2.4:
            continue
        nxw, nzw = int((L - 0.6) / 1.6), int((h - 1.6) / 1.9)
        for u in range(nxw):
            for v in range(nzw):
                roll = r.random()
                t = r.random()
                wc = CITY_WIN[r.randrange(len(CITY_WIN))]
                s = 0.5 + 0.5 * r.random()
                t0 = 0.3 + u * 1.6 + 0.4
                z = 1.6 + v * 1.9
                p0 = (a[0] + ux * t0 + nx * 0.05, a[1] + uy * t0 + ny * 0.05)
                p1 = (p0[0] + ux * 0.8, p0[1] + uy * 0.8)
                mid = ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, z + 0.35)
                X, Y = CR.screen(mid)
                zh, zd = CR.zone(X, Y), CR.zone(X, Y, dispatch=True)
                if zd == 1 and roll < SPEC.WIN_DENSITY["dispatch"]:  # DISPATCH fist (its own glitched rows)
                    dc = (1.0, 0.96, 0.96) if t < 0.06 else FIST_RED["dispatch"]
                    _window(WFIST_D, p0, p1, z, tuple(x * (0.75 + 0.25 * s) for x in dc), roll, grow=FIST_GROW)
                if zh == 1:
                    if roll < SPEC.WIN_DENSITY["home"]:
                        _window(WFIST_H, p0, p1, z, tuple(x * (0.75 + 0.25 * s) for x in FIST_RED["home"]), roll, grow=FIST_GROW)
                    continue
                if zh == 2:
                    if roll < 0.85:
                        _window(WLINES, p0, p1, z, tuple(x * s for x in wc), roll)
                    continue
                w = CR.ring_weight(X, Y)
                if w > 0.5:
                    if roll < 0.9:
                        _window(WRING, p0, p1, z, tuple(x * s for x in wc), t)
                elif roll < 0.3:
                    _window(WIN, p0, p1, z, tuple(x * s for x in wc), t)
    top = [(x, y, h) for (x, y) in q]
    acc.face(top, tuple(min(1, v * 1.08) for v in col), bid)
    if r.random() < 0.42:  # neon roof trim in the building's ink
        ink = trims[r.randrange(len(trims))]
        for i in range(n):
            j = (i + 1) % n
            beam((q[i][0], q[i][1], h + 0.08), (q[j][0], q[j][1], h + 0.08), 0.22, ink, acc=NEON)
    return on_line


def build_district():
    """The Cell's district patch around the palm (origin): DISTRICT_LOTS x DISTRICT_LOTS lots, streets every 4th lot."""
    r = random.Random(3434)
    N = SPEC.DISTRICT_LOTS
    half = N * U / 2
    lanes = KN["lanes"]
    trims = KN["trims"] or [CRED, CPINK]
    # ground: asphalt under everything, sidewalks on the blocks
    gb = rid()
    SOLID.face([(-half, -half, 0.0), (half, -half, 0.0), (half, half, 0.0), (-half, half, 0.0)], (0.13, 0.13, 0.16), gb)
    n_bld = n_line = 0
    for i in range(N):
        for j in range(N):
            if i % 4 == 0 or j % 4 == 0:
                continue
            x0, y0 = -half + i * U, -half + j * U
            SOLID.face([(x0, y0, 0.01), (x0 + U, y0, 0.01), (x0 + U, y0 + U, 0.01), (x0, y0 + U, 0.01)], (0.26, 0.25, 0.30), gb)
            k = r.random()
            if k < 0.06:
                continue  # an empty lot / court
            ins = r.uniform(0.5, 1.1)
            cxl, cyl = x0 + U / 2, y0 + U / 2
            hr = r.random()
            h = 7.0 + 20.0 * hr * hr + (r.uniform(10, 24) if r.random() < 0.04 else 0.0)  # mid-rise, as the round 34 district
            shape = r.random()
            if shape < 0.22:  # hexagonal / octagonal prisms, as in the city
                sides = 6 if shape < 0.12 else 8
                rad = U / 2 - ins
                a0 = r.uniform(0, math.pi)
                q = [(cxl + rad * math.cos(a0 + 2 * math.pi * s / sides), cyl + rad * math.sin(a0 + 2 * math.pi * s / sides)) for s in range(sides)]
            else:
                q = [(x0 + ins, y0 + ins), (x0 + U - ins, y0 + ins), (x0 + U - ins, y0 + U - ins), (x0 + ins, y0 + U - ins)]
            n_bld += 1
            n_line += _district_building(q, h, r, trims)
    # street lanes: the district's lane colours (red family), a dim bed and three strokes per street
    for i in range(0, N + 1, 4):
        if i == N:
            continue
        c = -half + i * U + U / 2
        col = lanes[(i // 4) % 2]
        for (a, b) in (((c, -half), (c, half)), ((-half, c), (half, c))):
            strip(NEON, a, b, U * 0.9, 0.02, tuple(v * 0.12 for v in col))
            for k in (-1, 0, 1):
                off = k * U * 0.25
                if a[0] == b[0]:
                    strip(NEON, (a[0] + off, a[1]), (b[0] + off, b[1]), 0.18, 0.04, tuple(v * 0.8 for v in col))
                else:
                    strip(NEON, (a[0], a[1] + off), (b[0], b[1] + off), 0.18, 0.04, tuple(v * 0.8 for v in col))
    print("DISTRICT buildings", n_bld, "on detail lines", n_line, flush=True)
