# Round 26 base ideas. NOT a module: hq26.py exec()s it (after kit26.py). Every builder works in the LOCAL frame of
# idea_cfg.py: origin = the palm of the fist roads, local -Y = toward the camera (map and close-up), 1 lot = 6 BU.
# hq26.py rotates the result +45 deg into the world. DISP (bool) = the DISPATCH state.

S2 = math.sqrt(2.0)


def lot_of(lx, ly):
    u, v = lx / 6.0, -ly / 6.0
    return (CFG.P[0] + (u + v) / S2, CFG.P[1] + (v - u) / S2)


def local_of(x, y):
    u, v = CFG.uv(x, y)
    return (6.0 * u, -6.0 * v)


# the current sub-frame of a builder (e.g. the canyon) -> hero local, for the fist-road checks
SUBXF = [lambda x, y: (x, y)]


def _seg_d(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - dx * t, p[1] - a[1] - dy * t)


def on_fist(x, y, r=0.95, ignore_canyon=False):
    lx, ly = SUBXF[-1](x, y)
    p = lot_of(lx, ly)
    for a, b in CFG.fist:
        if ignore_canyon and CFG.canyon_td(*a)[1] < 1.4 and CFG.canyon_td(*b)[1] < 1.4:
            continue
        if _seg_d(p, a, b) < r:
            return True
    return False


def sign_col(gr, hijack=0.72):
    """(colour, content, dark) for one sign: the Cell's takeovers vs the street's own; DISPATCH turns all red."""
    r1, r2, r3, r4 = gr.random(), gr.random(), gr.random(), gr.random()  # always 4 draws: home and DISPATCH keep one layout
    if DISP:
        if r1 < 0.22:
            return DRED, "glyph", True
        return (DRED if r2 < 0.7 else DRED2), ("fist" if r3 < 0.45 else "glyph"), False
    if r1 < hijack:
        c = LIME26 if r2 < 0.5 else PINK26
        return c, ("fist" if r3 < 0.4 else ("tag" if r4 < 0.4 else "glyph")), False
    return ORIG[int(r2 * len(ORIG)) % len(ORIG)], "glyph", False


TEN_COLS = [(0.42, 0.36, 0.36), (0.36, 0.38, 0.44), (0.46, 0.40, 0.34), (0.30, 0.32, 0.38), (0.50, 0.44, 0.42), (0.40, 0.34, 0.40)]


def ten_col(gr):
    c = gr.choice(TEN_COLS)
    if DISP:
        c = (c[0] * 0.75 + 0.06, c[1] * 0.55, c[2] * 0.6)
    return c


WARMW = [(1.0, 0.72, 0.40), (1.0, 0.8, 0.55), (0.6, 0.9, 1.0)]
SW = 7.0  # Tokyo street half width (14 BU, Kabukicho-style: wide enough to read in the close-up)


def shophouse(side, y0, y1, h, gr, depth=12.0, street=None):
    """A narrow Tokyo-style building on one side of a street running along Y (side -1 = left, +1 = right)."""
    street = SW if street is None else street
    xf = side * street
    xb = side * (street + depth)
    x0, x1 = min(xf, xb), max(xf, xb)
    col = ten_col(gr)
    wall_box(x0, y0, 0, x1, y1, h, col)
    face_street = 1 if side < 0 else 3
    windows2(x0, y0, 0, x1, y1, h, p=0.42, cols=WARMW + ([DRED, DRED2] if DISP else [LIME26, PINK26]), faces=(face_street, 0), gr=gr)
    nx = -side
    sc = (1.0, 0.70, 0.38) if not DISP else (1.0, 0.25, 0.18)
    o = Vector((xf, (y0 + y1) / 2, 0))
    ux, uz, n = Vector((0, -nx, 0)), Vector((0, 0, 1)), Vector((nx, 0, 0))
    wdt = (y1 - y0) - 1.2
    pquad(NEON, o, ux, uz, n, -wdt / 2, wdt / 2, 0.3, 2.9, tuple(v * gr.uniform(0.35, 0.7) for v in sc), off=0.22)
    pquad(SOLID, o, ux, uz, n, -wdt / 2, -wdt / 2 + 0.5, 0.3, 2.9, (0.1, 0.09, 0.1), off=0.26, bid=rid())
    ac = gr.choice([(0.7, 0.18, 0.2), (0.2, 0.35, 0.5), (0.85, 0.82, 0.75), (0.25, 0.25, 0.28)])
    SOLID.face([tuple(o + ux * (-wdt / 2) + uz * 3.4 + n * 0.25), tuple(o + ux * (wdt / 2) + uz * 3.4 + n * 0.25),
                tuple(o + ux * (wdt / 2) + uz * 2.8 + n * 2.0), tuple(o + ux * (-wdt / 2) + uz * 2.8 + n * 2.0)], ac, rid())
    c, content, dark = sign_col(gr)
    gseed = gr.randint(0, 9999)
    pquad(SOLID, o, ux, uz, n, -wdt / 2, wdt / 2, 3.6, 5.4, (0.08, 0.07, 0.09), off=0.28, bid=rid())
    if not dark:
        pquad(NEON, o, ux, uz, n, -wdt / 2 + 0.2, wdt / 2 - 0.2, 3.75, 5.25, tuple(v * 0.25 for v in c), off=0.32)
        glyphs(o + uz * 3.8, ux, uz, n, wdt * 0.85, 1.4, c, gseed, cols=max(2, int(wdt / 1.5)), off=0.36)
    for z in range(8, int(h) - 3, 4):  # balconies + AC units
        if gr.random() < 0.35:
            yb = gr.uniform(y0 + 1, y1 - 3.5)
            box(min(xf, xf + nx * 1.3), yb, z - 0.3, max(xf, xf + nx * 1.3), yb + 2.6, z, (0.22, 0.2, 0.22), facet=False)
            beam((xf + nx * 1.3, yb, z + 1.0), (xf + nx * 1.3, yb + 2.6, z + 1.0), 0.12, (0.22, 0.2, 0.22))
        if gr.random() < 0.4:
            ya = gr.uniform(y0 + 0.8, y1 - 1.8)
            box(min(xf, xf + nx * 0.9), ya, z + 1.4, max(xf, xf + nx * 0.9), ya + 1.2, z + 2.2, (0.62, 0.62, 0.6), facet=False)
    nb = 2 if (y1 - y0) < 9 else 3  # blade signs, stacked up the facade: they face the camera down the street
    for k in range(nb):
        if gr.random() < 0.1:
            continue
        yy = y0 + (y1 - y0) * (0.2 + 0.6 * (k % 2)) + gr.uniform(-0.6, 0.6)
        c, content, dark = sign_col(gr)
        top = h - 1.5
        hh = gr.uniform(6, min(16, max(6.5, h - 8)))
        z0 = 6.0 if k < 2 else min(top - hh, 6.0 + 16.5)
        if k == 1 and nb == 3:
            z0 = gr.uniform(6.0, 9.0)
        blade_sign((xf, yy), (nx, 0), hh, gr.uniform(2.2, 3.2), c, gr.randint(0, 9999), content=content, z0=z0, dark=dark)
        if not dark:  # wet street: the sign's reflection streak
            strip(NEON, (xf + nx * 2.4, yy - 0.2), (xf + nx * 2.4, yy - gr.uniform(6, 12)), 1.5, 0.05, tuple(v * 0.16 for v in c))
    cyl(gr.uniform(x0 + 2.5, x1 - 2.5), gr.uniform(y0 + 2.0, y1 - 2.0), h, h + 2.6, 1.3, (0.32, 0.30, 0.30), n=8)
    roof_trim(x0, y0, x1, y1, h + 0.1, (0.14, 0.12, 0.14), w=0.4)
    return x0, x1, col


def tokyo_street(y_lo, y_hi, seed=7, hmin=12, hfar=16, roof_screens=0.55):
    gr = random.Random(seed)
    SOLID.face([(-SW, y_lo, 0.03), (SW, y_lo, 0.03), (SW, y_hi, 0.03), (-SW, y_hi, 0.03)], (0.10, 0.10, 0.12), rid())
    for s in (-1, 1):
        box(min(s * SW, s * (SW - 1.6)), y_lo, 0, max(s * SW, s * (SW - 1.6)), y_hi, 0.25, (0.30, 0.29, 0.31), facet=False)
    for side in (-1, 1):
        y = y_lo + gr.uniform(0, 3)
        while y < y_hi - 3:
            w = gr.uniform(6.5, 12.5)
            y1 = min(y + w, y_hi)
            if any(on_fist(side * xx, yy, ignore_canyon=True) for xx in (SW + 1, SW + 6, SW + 11) for yy in (y + 1, (y + y1) / 2, y1 - 1)):
                y = y1 + 0.6
                continue
            far = (y1 - y_lo) / (y_hi - y_lo)  # buildings grow toward the palm (the base end)
            h = gr.uniform(hmin, hmin + 10) + hfar * far + (10 if gr.random() < 0.2 else 0)
            x0, x1, col = shophouse(side, y, y1, h, gr)
            if gr.random() < roof_screens:
                c, content, dark = sign_col(gr, hijack=0.85)
                bw = gr.uniform(7, 11)
                sseed = gr.randint(0, 9999)
                if not dark:
                    cx = (x0 + x1) / 2
                    for sx in (-1, 1):
                        beam((cx + sx * bw / 3, y + 1.4, h), (cx + sx * bw / 3, y + 1.4, h + 2.2), 0.4, (0.2, 0.18, 0.2))
                    screen((cx, y + 1.0, h + 2.0), (1, 0, 0), (0, 0, 1), (0, -1, 0), bw, bw * 0.62, content, c,
                           PINK26 if c == LIME26 else (LIME26 if not DISP else DRED2), sseed, glitch=0.5 if DISP else 0.0)
            y = y1 + gr.uniform(0.0, 0.8)
    y = y_lo + 2  # overhead wires + lantern strings across the street
    while y < y_hi - 2:
        z1, z2 = gr.uniform(7, 24), gr.uniform(7, 24)
        if gr.random() < 0.38:
            cols = [DRED, DRED2] if DISP else [PINK26, (1.0, 0.25, 0.2), LIME26, (1.0, 0.7, 0.3)]
            zz = gr.uniform(7, 11)
            lantern_string((-SW + 0.1, y, zz), (SW - 0.1, y + gr.uniform(-2, 2), zz + gr.uniform(-1, 1)), 1.4, cols, n=9)
        else:
            cable((-SW + 0.1, y, z1), (SW - 0.1, y + gr.uniform(-3, 3), z2), gr.uniform(0.6, 2.4), w=0.09, col=(0.05, 0.04, 0.05))
            rr = gr.random()
            if DISP and rr < 0.4:
                cable((-SW + 0.1, y + 0.5, z1 - 1), (SW - 0.1, y + 0.5, z2 - 1), 1.5, w=0.12, col=DRED, acc=NEON)
        y += gr.uniform(2.5, 5.5)
    for k in range(4):
        s = -1 if k % 2 else 1
        cable((s * (SW - 0.3), y_lo, 10 + k * 3), (s * (SW - 0.7), y_hi, 12 + k * 4), 3, w=0.08, col=(0.05, 0.04, 0.05))
    for k in range(12):
        side = -1 if k % 2 else 1
        yy = gr.uniform(y_lo + 4, y_hi - 6)
        vc = gr.choice([(0.9, 0.95, 1.0), LIME26, (0.4, 0.85, 1.0), PINK26])
        vc = DRED if DISP else vc
        vending(side * (SW - 2.1), yy, (-side, 0), vc)


def cell_tower(y0, y1, w=15.0, h=62.0, seed=3):
    """The canyon's head: the Cell's tower facing down the street, its big hijacked screen showing the fist."""
    gr = random.Random(seed)
    col = (0.30, 0.27, 0.32) if not DISP else (0.26, 0.12, 0.14)
    wall_box(-w, y0, 0, w, y1, h, col)
    wall_box(-w + 3, y0 + 2, h, w - 3, y1 - 2, h + 6, col)
    windows2(-w, y0, 0, w, y1, h, p=0.45, cols=[(1.0, 0.72, 0.40)] + ([DRED, DRED2] if DISP else [LIME26, PINK26]), faces=(0, 1, 3), gr=gr)
    sc = DRED if DISP else LIME26
    sc2 = DRED2 if DISP else PINK26
    screen((0, y0 - 0.4, 30), (1, 0, 0), (0, 0, 1), (0, -1, 0), 22, 17, "fist", sc, sc2, 11, glitch=0.6 if DISP else 0.0, depth=1.2)
    for s in (-1, 1):
        beam((s * 11.6, y0 - 0.9, 29.4), (s * 11.6, y0 - 0.9, 47.6), 0.45, sc2, acc=NEON)
    beam((-11.6, y0 - 0.9, 47.6), (11.6, y0 - 0.9, 47.6), 0.45, sc2, acc=NEON)
    beam((-11.6, y0 - 0.9, 29.4), (11.6, y0 - 0.9, 29.4), 0.45, sc2, acc=NEON)
    text_obj("DISPATCH" if DISP else "REBEL_CELL", (0, y0 - 0.6, 25.0), (math.radians(90), 0, 0), 3.2, SIGNM)
    for s in (-1, 1):  # corner blade signs, stacked
        for k in range(2):
            c, content, dark = sign_col(gr, hijack=1.0)
            blade_sign((s * (w - 1.2), y0), (0, -1), 14, 2.6, c, gr.randint(0, 999), content="fist" if k == 0 else "glyph", z0=8 + k * 18, dark=dark)
    pquad(NEON, (0, y0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0), -4, 4, 0.2, 5.0, tuple(v * 0.7 for v in sc), off=0.3)
    for s in (-1, 1):
        pquad(SOLID, (s * 9, y0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0), -4, 4, 0.2, 5.5, (0.32, 0.32, 0.34), off=0.25, bid=rid())
        tag_scrawl((s * 9, y0, 0.5), (1, 0, 0), (0, 0, 1), (0, -1, 0), 7, 4.5, sc2, gr.randint(0, 999), off=0.32)
    ym = (y0 + y1) / 2  # the relay mast on the roof
    zt = h + 6
    legs = [(-3, ym - 2), (3, ym - 2), (0, ym + 4)]
    for (x, y) in legs:
        beam((x, y, zt), (0, ym, zt + 30), 0.45, (0.24, 0.2, 0.22))
    for z in range(int(zt) + 5, int(zt) + 28, 5):
        kk = (z - zt) / 30
        pts = [(x * (1 - kk), ym + (y - ym) * (1 - kk), z) for (x, y) in legs]
        for p, q in zip(pts, pts[1:] + pts[:1]):
            beam(p, q, 0.25, (0.28, 0.24, 0.26))
    for (z, aim) in ((zt + 18, (-0.7, -0.5, 0.4)), (zt + 24, (0.7, -0.4, 0.5)), (zt + 12, (0.2, -0.8, 0.5))):
        dish((0, ym, z), aim, 2.6, 0.8, (0.6, 0.55, 0.58))
    box(-0.6, ym - 0.6, zt + 30, 0.6, ym + 0.6, zt + 31.4, sc, facet=False)
    NEON.face([(-0.7, ym - 0.7, zt + 30), (0.7, ym - 0.7, zt + 30), (0.7, ym - 0.7, zt + 31.4), (-0.7, ym - 0.7, zt + 31.4)], sc, (0, 0, 0))
    if DISP:
        for xx in (-w + 3, w - 3):
            cable((0, ym, zt + 26), (xx, y0 + 1, h), 6, w=0.2, col=DRED, acc=NEON)


# ---- the canyon frame: Y runs along the fist road under the thumb, from the wrist (y = -LC) to the palm (y = 0)
_A = local_of(*CFG.canyon[0])
_B = local_of(*CFG.canyon[1])
LC = math.hypot(_A[0] - _B[0], _A[1] - _B[1])
_dir = ((_A[0] - _B[0]) / LC, (_A[1] - _B[1]) / LC)
CROT = math.degrees(math.atan2(-_dir[0], _dir[1]))


def canyon_to_local(x, y):
    c, s = math.cos(math.radians(CROT)), math.sin(math.radians(CROT))
    return (_A[0] + x * c - y * s, _A[1] + x * s + y * c)


def in_canyon_frame(fn):
    def run():
        SUBXF.append(canyon_to_local)
        build_xf(fn, _A[0], _A[1], CROT)
        SUBXF.pop()
    return run


def tokyo_canyon():
    tokyo_street(-LC - 4, 1.0)
    cell_tower(2.0, 20.0)


def idea_tokyo():
    in_canyon_frame(tokyo_canyon)()


def idea_stub():
    cell_tower(10, 28)


def _cam_canyon(cam, tgt, lens):
    c = canyon_to_local(cam[0], cam[1])
    t = canyon_to_local(tgt[0], tgt[1])
    return ((c[0], c[1], cam[2]), (t[0], t[1], tgt[2]), lens)


IDEAS26 = {"tokyo": idea_tokyo, "roofs": idea_stub, "skyline": idea_stub, "deck": idea_stub, "rec": idea_stub}
# close-up cameras in the local frame: (camera xyz, target xyz, lens)
CAMS26 = {"tokyo": _cam_canyon((0, -LC + 6, 10), (0, 10, 24), 24), "roofs": ((0, -230, 210), (0, 0, 0), 30),
          "skyline": ((0, -190, 110), (0, 0, 50), 30), "deck": ((0, -190, 130), (0, 0, 14), 30), "rec": ((0, -190, 120), (0, 0, 18), 30)}


# ================================================================== 2  PAINTED ROOFS (the city roofs are painted in hq26.py)
def paint_works():
    """The crew's base in the palm: an old paint warehouse, roof fully painted, scaffold, drums, work lights."""
    gr = random.Random(21)
    col = (0.40, 0.34, 0.32) if not DISP else (0.24, 0.12, 0.13)
    wall_box(-13, -11, 0, 13, 12, 10, col)
    windows2(-13, -11, 0, 13, 12, 10, p=0.4, cols=[(1.0, 0.72, 0.40), LIME26 if not DISP else DRED], faces=(0, 1, 3), gr=gr)
    paint = (2.3, 0.16, 0.17)
    rag = [(-12.4 + gr.uniform(0, 0.6), -10.4, 10.06), (12.4, -10.4 + gr.uniform(0, 0.6), 10.06), (12.4 - gr.uniform(0, 0.6), 11.4, 10.06), (-12.4, 11.4, 10.06)]
    (NEON if DISP else SOLID).face(rag, (0.85, 0.03, 0.05) if DISP else paint, rid())
    for k in range(9):  # drips over the front edges
        x = gr.uniform(-12, 12)
        ln = gr.uniform(1.0, 5.0)
        (NEON if DISP else SOLID).face([(x - 0.35, -11.25, 10.05), (x + 0.35, -11.25, 10.05), (x + 0.15, -11.25, 10 - ln), (x - 0.15, -11.25, 10 - ln)],
                                       (0.7, 0.02, 0.04) if DISP else paint, rid())
    # roller door, glowing
    pquad(NEON, (0, -11, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0), -5, 5, 0.2, 6.0, (1.0, 0.55, 0.25) if not DISP else (1.0, 0.1, 0.08), off=0.3)
    for z in (1.2, 2.4, 3.6, 4.8):
        pquad(SOLID, (0, -11, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0), -5, 5, z, z + 0.15, (0.1, 0.08, 0.08), off=0.34, bid=rid())
    text_obj("DISPATCH" if DISP else "PAINT WORKS", (0, -11.5, 7.6), (math.radians(90), 0, 0), 1.8, SIGNM)
    # scaffold tower + roller arm on the roof, drums, work lights
    for (x, y) in ((-8, 4), (-4, 4), (-8, 8), (-4, 8)):
        beam((x, y, 10), (x, y, 22), 0.3, (0.5, 0.48, 0.45))
    for z in (14, 18, 22):
        for (a, b) in (((-8, 4), (-4, 4)), ((-4, 4), (-4, 8)), ((-4, 8), (-8, 8)), ((-8, 8), (-8, 4))):
            beam((a[0], a[1], z), (b[0], b[1], z), 0.25, (0.5, 0.48, 0.45))
    beam((-6, 6, 22), (8, -6, 14), 0.4, (0.6, 0.55, 0.2))
    cyl(8, -6, 12.8, 13.4, 1.4, (1.0, 0.15, 0.15) if not DISP else (0.3, 0.05, 0.06), n=10)
    for k in range(7):
        cyl(gr.uniform(2, 11), gr.uniform(-9, 10), 10, 11.6, 0.7, (0.75, 0.12, 0.12) if gr.random() < 0.6 else (0.3, 0.3, 0.32), n=8)
    for (x, y, aim) in ((-11, -9, (0.6, 0.6)), (11, 10, (-0.6, -0.6)), (-6, 6, (0.3, -0.9))):
        beam((x, y, 10), (x, y, 15), 0.25, (0.2, 0.2, 0.22))
        box(x - 0.8, y - 0.5, 15, x + 0.8, y + 0.5, 16.2, (0.2, 0.2, 0.22), facet=False)
        NEON.face([(x - 0.75, y - 0.55, 15.1), (x + 0.75, y - 0.55, 15.1), (x + 0.75, y - 0.55, 16.1), (x - 0.75, y - 0.55, 16.1)], LIME26 if not DISP else DRED, (0, 0, 0))
        disc((x + aim[0] * 4, y + aim[1] * 4, 10.12), (1, 0, 0), (0, 1, 0), 2.6, tuple(v * 0.08 for v in (LIME26 if not DISP else DRED)), acc=NEON, n=16)
    # the relay mast
    for (x, y) in ((6, 4), (10, 4), (8, 8)):
        beam((x, y, 10), (8, 6, 34), 0.35, (0.24, 0.2, 0.22))
    dish((8, 6, 26), (0.5, -0.7, 0.4), 2.2, 0.7, (0.6, 0.55, 0.58))
    box(7.5, 5.5, 34, 8.5, 6.5, 35.2, LIME26 if not DISP else DRED, facet=False)
    if DISP:  # DISPATCH floodlights sweep the painted fist
        for (x, y) in ((-12, -10), (12, 11)):
            beam((x, y, 10), (x, y, 26), 0.6, (0.15, 0.1, 0.12))
            beam((x, y, 26), (x * 3.5, y * 3.0, 0), 0.9, (0.45, 0.02, 0.04), acc=NEON)


ROOF_CREW = []  # filled by hq26.py: painted roofs (world xy top polygon, z) to dress with crew lights


def roof_crew_world():
    """Crew gear on a few painted roofs (world coords): a lime work light and drums, a spray rig. Called by hq26."""
    gr = random.Random(77)
    for (top, z) in ROOF_CREW:
        if gr.random() > 0.08:
            continue
        cx = sum(p[0] for p in top) / len(top)
        cy = sum(p[1] for p in top) / len(top)
        lc = LIME26 if not DISP else DRED
        beam((cx, cy, z), (cx, cy, z + 3.5), 0.2, (0.2, 0.2, 0.22))
        box(cx - 0.6, cy - 0.4, z + 3.5, cx + 0.6, cy + 0.4, z + 4.3, (0.2, 0.2, 0.22), facet=False)
        NEON.face([(cx - 0.55, cy - 0.45, z + 3.55), (cx + 0.55, cy - 0.45, z + 3.55), (cx + 0.55, cy - 0.45, z + 4.25), (cx - 0.55, cy - 0.45, z + 4.25)], lc, (0, 0, 0))
        disc((cx + 1.0, cy - 1.0, z + 0.12), (1, 0, 0), (0, 1, 0), 1.6, tuple(v * 0.10 for v in lc), acc=NEON, n=12)
        for k in range(gr.randint(1, 3)):
            cyl(cx + gr.uniform(-2, 2), cy + gr.uniform(-2, 2), z, z + 1.2, 0.5, (0.8, 0.1, 0.1), n=8)


def idea_roofs():
    paint_works()


# ================================================================== 3  HIJACKED SKYLINE (screens everywhere + the giant hologram fist)
def holo_fist(y, z0, s, col, col2, glitch=0.0, seed=5):
    """A hologram fist facing -Y: horizontal light slats (it reads as a projection, the city shows through),
    an outline, and a pink ghost copy offset behind (chromatic split). DISPATCH: red, rows torn sideways."""
    gr = random.Random(seed)
    k = s / 14.0
    parts = []
    for i in range(4):  # bolder gaps than the wall crest so the fingers read at distance
        x0 = -5.2 * k + i * 2.65 * k
        parts.append((x0, x0 + 2.05 * k, 8.6 * k, 13.2 * k + (0.7 * k if i in (1, 2) else 0)))
    parts.append((-5.2 * k, 5.4 * k, 5.4 * k, 7.9 * k))
    parts.append((-3.4 * k, 3.4 * k, 0.0, 4.8 * k))
    pitch = 1.15
    for (layer, c, dy, dx) in ((0, col, 0.0, 0.0), (1, col2, 3.0, 0.0)):
        for (a0, a1, b0, b1) in parts:
            zz = b0
            while zz < b1 - 0.2:
                sh = 0.0
                if glitch and gr.random() < glitch * 0.25:
                    sh = gr.uniform(-1, 1) * 3.0 * k
                zt = min(zz + pitch * 0.62, b1)
                fl = gr.random()
                if fl < 0.06:  # a dropped scanline
                    zz += pitch
                    continue
                c2 = tuple(v * (0.65 + 0.35 * gr.random()) for v in c) if layer == 0 else tuple(v * 0.55 for v in c)
                for yy in ((y + dy - 0.02), (y + dy + 0.02)):
                    NEON.face([(a0 + sh + dx, yy, z0 + zz), (a1 + sh + dx, yy, z0 + zz), (a1 + sh + dx, yy, z0 + zt), (a0 + sh + dx, yy, z0 + zt)], c2, (0, 0, 0))
                zz += pitch
            if layer == 0:
                for (p, q) in (((a0, b0), (a1, b0)), ((a1, b0), (a1, b1)), ((a1, b1), (a0, b1)), ((a0, b1), (a0, b0))):
                    beam((p[0], y - 0.3, z0 + p[1]), (q[0], y - 0.3, z0 + q[1]), 0.35, c, acc=NEON)


def tower_screens(x0, y0, x1, y1, h, gr, faces=(0, 1, 3), dens=0.7):
    """Hijacked screens / ads on a tower's walls (0: -Y, 1: +X, 3: -X)."""
    for f in faces:
        if f == 0:
            o, ux, n, L = Vector(((x0 + x1) / 2, y0 - 0.25, 0)), Vector((1, 0, 0)), Vector((0, -1, 0)), x1 - x0
        elif f == 1:
            o, ux, n, L = Vector((x1 + 0.25, (y0 + y1) / 2, 0)), Vector((0, 1, 0)), Vector((1, 0, 0)), y1 - y0
        else:
            o, ux, n, L = Vector((x0 - 0.25, (y0 + y1) / 2, 0)), Vector((0, -1, 0)), Vector((-1, 0, 0)), y1 - y0
        z = gr.uniform(6, 12)
        while z < h - 8:
            if gr.random() < dens:
                w = min(L - 3, gr.uniform(0.55, 0.9) * L)
                hh = min(h - z - 3, gr.uniform(5, 12))
                if hh < 4:
                    break
                c, content, dark = sign_col(gr, hijack=0.9)
                sh_, sseed = gr.uniform(-0.1, 0.1), gr.randint(0, 9999)
                if not dark:
                    c2 = PINK26 if c == LIME26 else (LIME26 if not DISP else DRED2)
                    screen(o + Vector((0, 0, z)) + ux * sh_ * L, ux, Vector((0, 0, 1)), n, w, hh, content, c, c2,
                           sseed, glitch=0.5 if DISP else 0.0, depth=0.5)
                z += hh + gr.uniform(3, 7)
            else:
                z += gr.uniform(5, 9)


def skyline_block():
    gr = random.Random(33)
    towers = [(-26, -26, -8, -8, 34), (-6, -27, 10, -12, 26), (12, -26, 27, -6, 42), (-27, -4, -10, 14, 50), (-6, -8, 8, 10, 64),
              (12, -2, 27, 12, 46), (-25, 16, -6, 27, 36), (-2, 14, 14, 27, 54), (16, 15, 27, 27, 38)]
    for (x0, y0, x1, y1, h) in towers:
        col = ten_col(gr)
        wall_box(x0, y0, 0, x1, y1, h, col)
        windows2(x0, y0, 0, x1, y1, h, p=0.32, cols=WARMW, faces=(0, 1, 3), gr=gr)
        tower_screens(x0, y0, x1, y1, h, gr)
        roof_trim(x0, y0, x1, y1, h + 0.1, (LIME26 if gr.random() < 0.5 else PINK26) if not DISP else DRED2, w=0.35)
    # projector crown on the central tower: emitters aimed at the hologram, light rays up to its base
    hz = 74
    pc = LIME26 if not DISP else DRED
    for (x, y) in ((-5, -7), (7, -7), (-5, 9), (7, 9)):
        box(x - 1.2, y - 1.2, 64, x + 1.2, y + 1.2, 67, (0.22, 0.2, 0.22), facet=False)
        NEON.face([(x - 0.9, y - 0.9, 67.05), (x + 0.9, y - 0.9, 67.05), (x + 0.9, y + 0.9, 67.05), (x - 0.9, y + 0.9, 67.05)], pc, (0, 0, 0))
        for tx in (-18, -6, 6, 18):
            beam((x, y, 67), (tx, 0, hz), 0.12, tuple(v * 0.5 for v in pc), acc=NEON)
    for (x0, y0, x1, y1, h) in towers:  # roof projectors on the other towers too, beams converging
        if h > 60:
            continue
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        box(cx - 1, cy - 1, h, cx + 1, cy + 1, h + 2.4, (0.22, 0.2, 0.22), facet=False)
        beam((cx, cy, h + 2.4), (cx * 0.4, 0, hz), 0.1, tuple(v * 0.35 for v in (PINK26 if not DISP else DRED2)), acc=NEON)
    holo_fist(0.0, hz, 62, LIME26 if not DISP else DRED, PINK26 if not DISP else DRED2, glitch=0.8 if DISP else 0.0)
    if DISP:
        text_obj("DISPATCH", (0, -0.6, hz - 6), (math.radians(90), 0, 0), 7.0, SIGNM)


def idea_skyline():
    skyline_block()


# ================================================================== 4  KNUCKLE DECK (a converted parking structure whose plan is the fist)
DECK_FLOOR = 4.2
ALT2 = []  # second light colour for alternate deck levels (set by knuckle_deck)


def deck_block(x0, y0, x1, y1, levels, gr, col, light, tip=False, ramp_face=None):
    """Open parking levels: slabs, columns, low parapets with light strips, parked cars; a roof deck."""
    bid = rid()
    for L in range(levels + 1):
        z = L * DECK_FLOOR
        box(x0, y0, z, x1, y1, z + 0.7, col, facet=False, bid=bid)
        if L == 0:
            continue
        # parapet (low wall) + its light strip under the slab edge
        for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
            beam((a[0], a[1], z + 1.3), (b[0], b[1], z + 1.3), 0.4, tuple(c * 0.9 for c in col))
            beam((a[0], a[1], z - 0.15), (b[0], b[1], z - 0.15), 0.22, light if (L % 2 or not ALT2) else ALT2[0], acc=NEON)
    xs = [x0 + 0.6 + i * (x1 - x0 - 1.2) / max(1, int((x1 - x0) / 7)) for i in range(int((x1 - x0) / 7) + 1)]
    ys = [y0 + 0.6 + i * (y1 - y0 - 1.2) / max(1, int((y1 - y0) / 7)) for i in range(int((y1 - y0) / 7) + 1)]
    for x in xs:
        for y in ys:
            if x in (xs[0], xs[-1]) or y in (ys[0], ys[-1]):
                box(x - 0.45, y - 0.45, 0, x + 0.45, y + 0.45, levels * DECK_FLOOR, tuple(c * 0.85 for c in col), facet=False)
    # the dark interior of each level (so the open floors read as voids with lit ceilings)
    for L in range(levels):
        z = L * DECK_FLOOR
        for (a, b, nrm) in (((x0 + 0.4, y0 + 0.4), (x1 - 0.4, y0 + 0.4), (0, -1)), ((x1 - 0.4, y0 + 0.4), (x1 - 0.4, y1 - 0.4), (1, 0)),
                            ((x0 + 0.4, y1 - 0.4), (x0 + 0.4, y0 + 0.4), (-1, 0))):
            SOLID.face([(a[0], a[1], z + 0.7), (b[0], b[1], z + 0.7), (b[0], b[1], z + DECK_FLOOR), (a[0], a[1], z + DECK_FLOOR)], (0.05, 0.045, 0.06), rid())
        # ceiling strip lights (the deck glows from inside)
        for x in xs[1:-1]:
            strip(NEON, (x, y0 + 1.5), (x, y1 - 1.5), 0.35, z + DECK_FLOOR - 0.05, (0.75, 0.62, 0.45) if not DISP else (0.7, 0.08, 0.08))
        for k in range(int((x1 - x0) / 6)):  # cars
            if gr.random() < 0.45:
                cx = x0 + 3 + k * 6
                cy = y0 + 3.2 if gr.random() < 0.5 else y1 - 3.2
                vc = gr.choice([(0.6, 0.6, 0.62), (0.25, 0.3, 0.4), (0.55, 0.15, 0.15), (0.2, 0.2, 0.22)])
                box(cx - 1.1, cy - 2.2, z + 0.75, cx + 1.1, cy + 2.2, z + 2.0, vc, facet=False)
                if gr.random() < 0.5:
                    NEON.face([(cx - 0.9, cy - 2.25, z + 1.3), (cx - 0.4, cy - 2.25, z + 1.3), (cx - 0.4, cy - 2.25, z + 1.6), (cx - 0.9, cy - 2.25, z + 1.6)],
                              (1.0, 0.9, 0.7), (0, 0, 0))
    top = levels * DECK_FLOOR + 0.7
    if ramp_face == "front":  # zigzag ramps across the front (they read as the 'wrist' strapping)
        for L in range(levels):
            z = L * DECK_FLOOR
            a, b = (x0 + 1, y0 - 1.2, z + 0.7), (x1 - 1, y0 - 1.2, z + DECK_FLOOR + 0.7)
            if L % 2:
                a, b = (x1 - 1, y0 - 1.2, z + 0.7), (x0 + 1, y0 - 1.2, z + DECK_FLOOR + 0.7)
            beam(a, b, 2.2, col)
            beam((a[0], a[1] - 1.2, a[2] + 1.2), (b[0], b[1] - 1.2, b[2] + 1.2), 0.25, light, acc=NEON)
    return top


def knuckle_deck(dy=0.0, finger_lv=(6, 7, 7, 6), thumb_lv=3, wrist_lv=2):
    """Plan = the Cell's crest seen from above (fingers away from the camera, the wrist toward it), 6 BU per lot.
    The levels step up wrist -> thumb -> knuckles, so from the street the four finger decks rise like a fist."""
    gr = random.Random(41)
    col = (0.50, 0.48, 0.50) if not DISP else (0.30, 0.16, 0.17)
    li = LIME26 if not DISP else DRED
    li2 = PINK26 if not DISP else DRED2
    ALT2[:] = [li2]
    k = 5.4  # crest unit -> BU
    tops = []
    marks = [(acc, len(acc.bm.verts)) for acc in (SOLID, NEON, WIN)]
    for i in range(4):  # fingers (curled, knuckle row), stepping up toward the middle; clear gaps between them
        fw = 2.05 * k
        x0 = -5.25 * k + i * 2.7 * k
        y0, y1 = 8.4 * k - 40, 13.0 * k - 40 + (0.8 * k if i in (1, 2) else 0)
        lv = finger_lv[i]
        t = deck_block(x0, y0 - 6, x0 + fw, y1 - fw / 2, lv, gr, col, li)
        tops.append((x0, y0 - 6, x0 + fw, y1 - fw / 2, t))
        # the rounded fingertip: a half-drum (the helical down-ramp of each finger), lit rim
        cxk, cyk, r = x0 + fw / 2, y1 - fw / 2, fw / 2
        n = 12
        for j in range(n):
            a0, a1 = math.pi * j / n, math.pi * (j + 1) / n
            p0 = (cxk + r * math.cos(a0), cyk + r * math.sin(a0))
            p1 = (cxk + r * math.cos(a1), cyk + r * math.sin(a1))
            SOLID.facet_quad((p0[0], p0[1], 0), (p1[0], p1[1], 0), (p1[0], p1[1], t - 0.7), (p0[0], p0[1], t - 0.7), col, rid(), jit=0.004)
            SOLID.face([(cxk, cyk, t - 0.7), (p0[0], p0[1], t - 0.7), (p1[0], p1[1], t - 0.7)], col, rid())
            for L in range(1, lv + 1):
                beam((p0[0], p0[1], L * DECK_FLOOR - 0.15), (p1[0], p1[1], L * DECK_FLOOR - 0.15), 0.22, li, acc=NEON)
    t = deck_block(-5.6 * k, 5.4 * k - 40, 5.6 * k, 8.4 * k - 40, thumb_lv, gr, col, li2)  # thumb, across
    tops.append((-5.6 * k, 5.4 * k - 40, 5.6 * k, 8.4 * k - 40, t))
    t = deck_block(-3.6 * k, -1.0 * k - 40, 3.6 * k, 5.4 * k - 40, wrist_lv, gr, col, li, ramp_face="front")  # wrist: the ramp block
    tops.append((-3.6 * k, -1.0 * k - 40, 3.6 * k, 5.4 * k - 40, t))
    if dy:
        for acc, m in marks:
            acc.bm.verts.ensure_lookup_table()
            for v in acc.bm.verts[m:]:
                v.co.y += dy
        tops = [(a, b + dy, c, d + dy, t) for (a, b, c, d, t) in tops]
    return tops, col, li, li2, gr


def deck_dressing(tops, col, li, li2, gr, screens=True):
    """The Cell living on its deck: container shacks, tarps, string lights, the relay mast, hijacked screens on the front."""
    for (x0, y0, x1, y1, t) in tops:
        for k in range(2):
            if gr.random() < 0.55:
                cx, cy = gr.uniform(x0 + 4, x1 - 4), gr.uniform(y0 + 4, y1 - 4)
                rot, cc = gr.random() < 0.5, gr.choice([(0.30, 0.42, 0.40), (0.55, 0.30, 0.18), (0.25, 0.30, 0.45)])
                container(cx, cy, t, rot90=rot, L=6, W=2.6, Hh=2.6, c=cc if not DISP else (0.28, 0.10, 0.12))
        if gr.random() < 0.6:
            tx, ty = gr.uniform(x0 + 3, x1 - 6), gr.uniform(y0 + 3, y1 - 6)
            SOLID.face([(tx, ty, t + 0.3), (tx + 5, ty, t + 0.3), (tx + 5, ty + 4, t + 1.8), (tx, ty + 4, t + 1.8)],
                       (0.20, 0.36, 0.52) if not DISP else (0.30, 0.10, 0.12), rid())
    # string lights between the knuckles
    for a, b in zip(tops[:3], tops[1:4]):
        p = ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2, a[4] + 3)
        q = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2, b[4] + 3)
        lantern_string(p, q, 1.5, [li, li2] if not DISP else [DRED, DRED2], n=8, size=0.4)
    # relay mast on the tallest knuckle
    x0, y0, x1, y1, t = tops[1]
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    for (dx, dy) in ((-2.5, -2), (2.5, -2), (0, 2.5)):
        beam((mx + dx, my + dy, t), (mx, my, t + 30), 0.4, (0.24, 0.2, 0.22))
    for z in range(int(t) + 5, int(t) + 28, 5):
        kk = (z - t) / 30
        pts = [(mx + dx * (1 - kk), my + dy * (1 - kk), z) for (dx, dy) in ((-2.5, -2), (2.5, -2), (0, 2.5))]
        for p, q in zip(pts, pts[1:] + pts[:1]):
            beam(p, q, 0.22, (0.28, 0.24, 0.26))
    for (z, aim) in ((t + 18, (-0.7, -0.5, 0.4)), (t + 24, (0.7, -0.4, 0.5)), (t + 12, (0.2, -0.8, 0.5))):
        dish((mx, my, z), aim, 2.4, 0.8, (0.6, 0.55, 0.58))
    box(mx - 0.6, my - 0.6, t + 30, mx + 0.6, my + 0.6, t + 31.4, li, facet=False)
    # hanging fist banners on the thumb front and hijacked screens on the wrist front
    x0, y0, x1, y1, t = tops[4]
    for s in (-1, 1):
        fist_icon((s * 15, y0 - 1.6, 4.6), (1, 0, 0), (0, 0, 1), (0, -1, 0), 9.0, li2, back=(0.08, 0.06, 0.08), off=0.12)
    x0, y0, x1, y1, t = tops[5]
    if screens:
        screen((0, y0 - 2.6, t + 0.6), (1, 0, 0), (0, 0, 1), (0, -1, 0), 20, 9.5, "fist", li, li2, 9, glitch=0.6 if DISP else 0.0)
        for s in (-1, 1):
            beam((s * 6, y0 - 2.0, t - 1), (s * 6, y0 - 2.0, t + 0.8), 0.5, (0.2, 0.18, 0.2))
    text_obj("DISPATCH" if DISP else "LEVEL 0 // THE CELL", (0, y0 - 2.7, 1.9), (math.radians(90), 0, 0), 1.7, SIGNM)
    # the Cell's marks on every front that faces the street: tags on the parapets, blade signs, a screen per knuckle
    for idx, (x0, y0, x1, y1, t) in enumerate(tops):
        for L in range(1, int(t / DECK_FLOOR) + 1):
            if gr.random() < 0.5:
                w = gr.uniform(4, 8)
                xc = gr.uniform(x0 + w / 2 + 1, x1 - w / 2 - 1) if x1 - x0 > w + 2 else (x0 + x1) / 2
                tc = gr.choice([li, li2, (0.95, 0.95, 0.9)])
                tag_scrawl((xc, y0 - 0.25, L * DECK_FLOOR + 0.75), (1, 0, 0), (0, 0, 1), (0, -1, 0), w, 1.0, tc if not DISP else DRED,
                           gr.randint(0, 9999), off=0.05)
        if idx < 4 and screens:  # each knuckle wears a hijacked screen on its street face
            c, content, dark = sign_col(gr, hijack=1.0)
            sseed = gr.randint(0, 9999)
            if not dark:
                screen(((x0 + x1) / 2, y0 - 0.5, t - 9.5), (1, 0, 0), (0, 0, 1), (0, -1, 0), (x1 - x0) * 0.72, 7.5, "fist" if idx in (1, 2) else content,
                       c, li2 if c == li else li, sseed, glitch=0.6 if DISP else 0.0, depth=0.4)
    for (x0, y0, x1, y1, t) in tops[4:5]:  # blade signs off the thumb deck corners
        for s in (-1, 1):
            c, content, dark = sign_col(gr, hijack=0.9)
            blade_sign((x0 if s < 0 else x1, y0 + 2.0), (s, 0), 10, 2.6, c, gr.randint(0, 999), content=content, z0=1.5, dark=dark)
    pquad(NEON, (0, y0, 0), (1, 0, 0), (0, 0, 1), (0, -1, 0), -6, 6, 0.1, 3.2, tuple(v * 0.6 for v in li), off=1.5)
    if DISP:
        for (a, b) in zip(tops, tops[1:]):
            cable(((a[0] + a[2]) / 2, (a[1] + a[3]) / 2, a[4] + 1), ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2, b[4] + 1), 3, w=0.25, col=DRED, acc=NEON)


def idea_deck():
    tops, col, li, li2, gr = knuckle_deck(finger_lv=(6, 7, 7, 6), thumb_lv=3, wrist_lv=2)
    deck_dressing(tops, col, li, li2, gr)


IDEAS26.update({"roofs": idea_roofs, "skyline": idea_skyline, "deck": idea_deck})
CAMS26.update({"roofs": ((0, -150, 125), (0, -12, 0), 30), "skyline": ((0, -172, 56), (0, 0, 80), 26),
               "deck": ((0, -140, 62), (0, -4, 16), 30)})


# ================================================================== RECOMMENDED: the Knuckle Deck at the head of a hijacked canyon
def rec_build():
    import idea_cfg as _IC
    global SW
    SW = 9.0  # a wider street in front of the deck: the view opens onto the HQ
    y0 = _IC.REC_DECK_Y0
    tokyo_street(-LC - 4, y0 - 1.0, seed=17, hmin=8, hfar=5, roof_screens=0.25)
    tops, col, li, li2, gr = knuckle_deck(dy=y0 + 45.36, finger_lv=(6, 7, 7, 6), thumb_lv=3, wrist_lv=2)
    deck_dressing(tops, col, li, li2, gr)
    # the canyon's lantern strings run into the deck's wrist (the street is the Cell's front door)
    cols = [DRED, DRED2] if DISP else [PINK26, LIME26, (1.0, 0.7, 0.3)]
    for k in range(4):
        yy = y0 - 4 - k * 5
        lantern_string((-SW + 0.1, yy, 8.5 + k * 0.4), (SW - 0.1, yy + 1.0, 8.0 + k * 0.5), 1.2, cols, n=8, size=0.45)


def idea_rec():
    in_canyon_frame(rec_build)()


IDEAS26["rec"] = idea_rec
CAMS26["rec"] = _cam_canyon((0, -64, 30), (0, -8, 22), 24)
