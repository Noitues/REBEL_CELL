# Round 27 street kit: the Tokyo canyon builders (from round 26 ideas26.py: sign_col, shophouse, tokyo_street, holo_fist),
# exec'd by hq27.py after kit26.py. Round 27 changes: no fist-road checks (the district is a normal grid now); the
# cross streets of the grid are kept open via GAPS (local y intervals); every roof is recorded in ROOFS_LOCAL so
# hq27.py can paint the ones inside the painted fist (same rule as the city roofs and the map).

GAPS = []
ROOFS_LOCAL = []
NEAR_Y = 34.0

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
SW = 3.2  # round 27: the canyon is a real grid street of the city (1 lot = 6 BU) + a narrow pavement


def shophouse(side, y0, y1, h, gr, depth=9.0, street=None):
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
        blade_sign((xf, yy), (nx, 0), hh, gr.uniform(1.5, 2.1), c, gr.randint(0, 9999), content=content, z0=z0, dark=dark)
        if not dark:  # wet street: the sign's reflection streak
            strip(NEON, (xf + nx * 2.4, yy - 0.2), (xf + nx * 2.4, yy - gr.uniform(6, 12)), 1.5, 0.05, tuple(v * 0.16 for v in c))
    ROOFS_LOCAL.append((x0, y0, x1, y1, h))
    cyl(gr.uniform(x0 + 2.5, x1 - 2.5), gr.uniform(y0 + 2.0, y1 - 2.0), h, h + 2.6, 1.3, (0.32, 0.30, 0.30), n=8)
    roof_trim(x0, y0, x1, y1, h + 0.1, (0.14, 0.12, 0.14), w=0.4)
    return x0, x1, col


def tokyo_street(y_lo, y_hi, seed=7, hmin=12, hfar=16, roof_screens=0.55):
    gr = random.Random(seed)
    for s in (-1, 1):  # pavements only: the street itself is the city's own tile with its lanes (as on the map)
        box(min(s * SW, s * (SW - 0.7)), y_lo, 0, max(s * SW, s * (SW - 0.7)), y_hi, 0.2, (0.30, 0.29, 0.31), facet=False)
    for side in (-1, 1):
        y = y_lo + gr.uniform(0, 3)
        while y < y_hi - 3:
            w = gr.uniform(5.0, 9.0)
            y1 = min(y + w, y_hi)
            gap = next(((a, b) for (a, b) in GAPS if not (y1 < a or y > b)), None)
            if gap:  # a cross street of the grid: leave it open
                y = gap[1] + 0.3
                continue
            if y1 - y < 3.5:
                y = y1 + 0.3
                continue
            far = (y1 - y_lo) / (y_hi - y_lo)  # buildings grow toward the palm (the base end)
            h = gr.uniform(hmin, hmin + 8) + hfar * far + (7 if gr.random() < 0.2 else 0)
            near = y1 < NEAR_Y  # round 27: the shophouses right in front of the camera stay low and bare
            if near:
                h = min(h, 10.0)
            x0, x1, col = shophouse(side, y, y1, h, gr)
            if gr.random() < roof_screens and not near:
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
            lantern_string((-SW + 0.1, y, zz), (SW - 0.1, y + gr.uniform(-1, 1), zz + gr.uniform(-1, 1)), 0.9, cols, n=5, size=0.45)
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
        vending(side * (SW - 0.5), yy, (-side, 0), vc)



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


