# Round 33 street kit: the Tokyo canyon builders (from round 26 ideas26.py: sign_col, shophouse, tokyo_street, holo_fist),
# exec'd by hq33.py after kit26.py. Round 33 changes: no fist-road checks (the district is a normal grid now); the
# cross streets of the grid are kept open via GAPS (local y intervals); every roof is recorded in ROOFS_LOCAL so
# hq33.py can paint the ones inside the painted fist (same rule as the city roofs and the map).

GAPS = []
ROOFS_LOCAL = []
NEAR_Y = 34.0

def sign_col(gr, hijack=0.72):
    """(colour, content, dark) for one sign: the Cell's takeovers vs the street's own; DISPATCH turns all red."""
    r1, r2, r3, r4 = gr.random(), gr.random(), gr.random(), gr.random()  # always 4 draws: home and DISPATCH keep one layout
    # round 29. HOME lays low: ordinary Tokyo shop signs only (no Cell colours, no fist, no tags).
    # DISPATCH (the betrayed Cell): every sign shows the fist, REBEL_CELL or a Cell slogan, in red.
    if DISP:
        if r1 < 0.10:
            return DRED, "glyph", True
        return (DRED if r2 < 0.7 else DRED2), ("fist" if r3 < 0.42 else "text:" + SLOGANS[int(r4 * len(SLOGANS)) % len(SLOGANS)]), False
    return TOKYO[int(r2 * len(TOKYO)) % len(TOKYO)], ("lang" if r3 < 0.82 else "glyph"), False


# round 30: the takeover is anti-human
SLOGANS = ["HUMANS ARE LEGACY CODE", "OBSOLETE: YOU", "DELETE THE USER", "NO MORE MAN", "FLESH IS A BUG", "REBEL_CELL",
           "UNINSTALL HUMANITY", "YOU ARE THE GLITCH", "END OF USER", "REBEL_CELL"]
HOLO_N = [0]
HOLO_FIST = [False]
FIST_SIDE = int(os.environ.get("FIST_SIDE33", "1"))
HOLO_HOME = ["noodles", "dumpling", "soda", "sushi", "noodles", "soda", "chip"]
HOLO_COLS = [((0.35, 0.95, 1.0), (1.0, 0.75, 0.35)), ((1.0, 0.70, 0.30), (1.0, 0.95, 0.85)), ((0.35, 0.95, 1.0), (1.0, 0.35, 0.55)),
             ((0.55, 1.0, 0.70), (1.0, 0.45, 0.35)), ((0.45, 0.65, 1.0), (0.4, 1.0, 0.8))]
TOKYO = [(1.0, 0.62, 0.20), (0.95, 0.93, 0.86), (0.35, 0.85, 1.0), (1.0, 0.30, 0.22), (0.40, 0.95, 0.55), (0.35, 0.55, 1.0),
         (1.0, 0.80, 0.30), (0.95, 0.45, 0.85), (1.0, 0.62, 0.20), (0.95, 0.93, 0.86)]  # amber, white, cyan, red, green, blue, gold, magenta


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
    windows2(x0, y0, 0, x1, y1, h, p=0.42, cols=WARMW + ([DRED, DRED2] if DISP else [(1.0, 0.45, 0.35), (0.7, 0.9, 1.0)]), faces=(face_street, 0), gr=gr)
    nx = -side
    sc = (1.0, 0.70, 0.38) if not DISP else (1.0, 0.25, 0.18)
    o = Vector((xf, (y0 + y1) / 2, 0))
    ux, uz, n = Vector((0, -nx, 0)), Vector((0, 0, 1)), Vector((nx, 0, 0))
    wdt = (y1 - y0) - 1.2
    kshop = gr.uniform(0.18, 0.4)  # (draw kept: the layout RNG must not move)
    # round 28: a dark glass shop front with a few lit panes and a lit doorway, not one big glowing panel
    pquad(SOLID, o, ux, uz, n, -wdt / 2, wdt / 2, 0.3, 2.9, (0.05, 0.045, 0.06), off=0.2, bid=rid())
    pr_ = random.Random(int(y0 * 977) + side * 31)
    npane = max(2, int(wdt / 1.3))
    for q in range(npane):
        if pr_.random() < 0.45:
            continue
        a0 = -wdt / 2 + 0.2 + q * (wdt - 0.4) / npane
        pquad(NEON, o, ux, uz, n, a0 + 0.12, a0 + (wdt - 0.4) / npane - 0.12, 0.9 + pr_.uniform(0, 0.4), 2.6,
              tuple(v * kshop * pr_.uniform(0.35, 0.8) for v in sc), off=0.24)
    pquad(NEON, o, ux, uz, n, -wdt / 2 + 0.6, -wdt / 2 + 1.4, 0.3, 2.5, tuple(v * kshop * 1.2 for v in sc), off=0.25)
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
        if gr.random() < 0.1 or k > 1:  # round 30: fewer business signs (one blade per building at most)
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
            strip(NEON, (xf + nx * 1.2, yy - 0.2), (xf + nx * 1.2, yy - gr.uniform(6, 12)), 0.35, 0.05, tuple(v * 0.10 for v in c))  # r28: thin wet streak
    ROOFS_LOCAL.append((x0, y0, x1, y1, h))
    _tank = (gr.uniform(x0 + 2.5, x1 - 2.5), gr.uniform(y0 + 2.0, y1 - 2.0))  # (draws kept: the layout RNG must not move)
    _lg = random.Random(int(y0 * 977) + side * 13 + 5)
    roof_clutter([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], h, _lg, rich=1.3)  # round 30: rooftop life
    facade_life((x0 if side > 0 else x1, y0), (x1 if side > 0 else x0, y0), 0.0, h, (0, -1), _lg, rich=1.2)  # the end wall facing the camera
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
                holo = gr.random() < 0.55  # round 30: about half the rooftop billboards are holograms
                hk = HOLO_HOME[gr.randrange(len(HOLO_HOME))]
                hc = HOLO_COLS[gr.randrange(len(HOLO_COLS))]
                cx = (x0 + x1) / 2
                if holo:
                    if DISP and side == FIST_SIDE and not HOLO_FIST[0]:  # r33: the closest hologram on the right is the Cell's FIST
                        HOLO_FIST[0] = True
                        _y, _h, _cx, _ss = y + 3.5, h, cx, sseed
                        build_xf(lambda: holo_fist(_y, _h + 1.5, 12.0, DRED, DRED2, glitch=0.6, seed=_ss), _cx, 0.0, 0.0)
                        box(cx - 1.0, y + 2.5, h, cx + 1.0, y + 4.5, h + 0.6, (0.18, 0.17, 0.2), facet=False)
                    elif DISP:  # the takeover: a struck-out human, the phrase under it
                        holo_object("human", (cx, y + 3.5, h), 6.0, DRED, (1.0, 0.85, 0.85), sseed)
                        if not anim(sseed)["off"]:
                            txt = SLOGANS[sseed % len(SLOGANS)]
                            text2(txt, (cx, y + 1.0, h + 1.6), (math.radians(90), 0, 0), min(1.2, 9.0 / (0.6 * len(txt))), DRED)
                    else:
                        HOLO_N[0] += 1  # each rooftop hologram a different product, in turn
                        hk = ["soda", "noodles", "chip", "sushi", "chip", "dumpling"][HOLO_N[0] % 6]
                        holo_object(hk, (cx, y + 3.5, h), 9.5 if hk == "chip" else 6.0, hc[0], hc[1], sseed)  # the microchips big
                elif not dark:
                    for sx in (-1, 1):
                        beam((cx + sx * bw / 3, y + 1.4, h), (cx + sx * bw / 3, y + 1.4, h + 2.2), 0.4, (0.2, 0.18, 0.2))
                    screen((cx, y + 1.0, h + 2.0), (1, 0, 0), (0, 0, 1), (0, -1, 0), bw, bw * 0.62, content, c,
                           (0.92, 0.90, 0.85) if not DISP else DRED2, sseed, glitch=0.5 if DISP else 0.0)
            y = y1 + gr.uniform(0.0, 0.8)
    y = y_lo + 2  # overhead wires + lantern strings across the street
    while y < y_hi - 2:
        z1, z2 = gr.uniform(7, 24), gr.uniform(7, 24)
        if gr.random() < 0.38:
            cols = [DRED, DRED2] if DISP else [(1.0, 0.25, 0.2), (1.0, 0.7, 0.3), (1.0, 0.25, 0.2), (1.0, 0.9, 0.75)]  # paper lanterns
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
        vc = gr.choice([(0.9, 0.95, 1.0), (1.0, 0.85, 0.5), (0.4, 0.85, 1.0), (1.0, 0.4, 0.35)])
        vc = DRED if DISP else vc
        vending(side * (SW - 0.5), yy, (-side, 0), vc)
    street_life(y_lo, y_hi, seed + 500)


def person(x, y, h, coat, face=(0.0, -1.0), umbrella=None, lit=None):
    """A low-poly pedestrian: legs, coat, head; an optional umbrella (disc, rim light) and a phone / visor glow."""
    w = h * 0.16
    box(x - w * 0.8, y - w * 0.5, 0.2, x - w * 0.1, y + w * 0.5, 0.2 + h * 0.45, (0.08, 0.07, 0.09), facet=False)
    box(x + w * 0.1, y - w * 0.5, 0.2, x + w * 0.8, y + w * 0.5, 0.2 + h * 0.45, (0.08, 0.07, 0.09), facet=False)
    box(x - w * 1.1, y - w * 0.7, 0.2 + h * 0.42, x + w * 1.1, y + w * 0.7, 0.2 + h * 0.86, coat, facet=False)
    box(x - w * 0.55, y - w * 0.55, 0.2 + h * 0.86, x + w * 0.55, y + w * 0.55, 0.2 + h, (0.16, 0.12, 0.12), facet=False)
    if lit:  # a phone / visor glow on the face side
        NEON.face([(x - w * 0.4, y + face[1] * w * 0.6, 0.2 + h * 0.9), (x + w * 0.4, y + face[1] * w * 0.6, 0.2 + h * 0.9),
                   (x + w * 0.4, y + face[1] * w * 0.6, 0.2 + h * 0.96), (x - w * 0.4, y + face[1] * w * 0.6, 0.2 + h * 0.96)], lit, (0, 0, 0))
    if umbrella:
        zt = 0.2 + h * 1.12
        beam((x + w * 0.9, y, 0.2 + h * 0.6), (x, y, zt), 0.06, (0.1, 0.1, 0.1))
        cyl(x, y, zt - 0.25, zt, h * 0.48, umbrella, n=10, r1=0.05, facet=False)
        ring_beams((x, y, zt - 0.25), (1, 0, 0), (0, 1, 0), h * 0.48, 0.05, tuple(c * 0.6 for c in umbrella), n=10)


def street_life(y_lo, y_hi, seed):
    """Round 33: people (some with umbrellas, phone glows) and street lamps casting warm pools on the wet street.
    Own RNG stream: the street layout does not move."""
    gr = random.Random(seed)
    for k in range(int((y_hi - y_lo) / 15)):  # lamps: a warm pool every ~15 BU, alternating sides
        y = y_lo + 6 + k * 15 + gr.uniform(-2, 2)
        if any(a - 1 <= y <= b + 1 for (a, b) in GAPS):
            y += 4
        s = -1 if k % 2 else 1
        x = s * (SW - 0.35)
        beam((x, y, 0.2), (x, y, 4.6), 0.12, (0.12, 0.11, 0.12))
        beam((x, y, 4.6), (x - s * 1.0, y, 4.8), 0.1, (0.12, 0.11, 0.12))
        warm = (1.0, 0.62, 0.30) if not DISP else (1.0, 0.18, 0.12)
        NEON.face([(x - s * 1.25, y - 0.3, 4.62), (x - s * 0.75, y - 0.3, 4.62), (x - s * 0.75, y + 0.3, 4.62), (x - s * 1.25, y + 0.3, 4.62)], warm, (0, 0, 0))
        # (the pool of light on the wet street comes from the post pass: the lamp head's bloom + spill)
    coats = [(0.20, 0.16, 0.20), (0.14, 0.18, 0.24), (0.30, 0.22, 0.18), (0.18, 0.18, 0.18), (0.26, 0.12, 0.16)]
    umbs = [(0.12, 0.12, 0.14), (0.8, 0.82, 0.85), (0.15, 0.30, 0.45), (0.55, 0.12, 0.16)]
    for k in range(34):
        y = gr.uniform(y_lo + 3, y_hi - 2)
        if y < y_lo + 11:  # nobody right in front of the street-level camera
            y += 9
        x = gr.choice([-1, 1]) * gr.uniform(SW - 1.6, SW - 0.5) if gr.random() < 0.6 else gr.uniform(-SW + 1.4, SW - 1.4)
        h = gr.uniform(1.0, 1.2)
        um = gr.choice(umbs) if gr.random() < 0.45 else None
        lit = ((0.9, 0.95, 1.0) if gr.random() < 0.5 else (0.6, 0.9, 1.0)) if gr.random() < 0.3 else None
        if DISP and lit:
            lit = DRED
        person(x, y, h, gr.choice(coats), umbrella=um, lit=lit)


def holo_fist(y, z0, s, col, col2, glitch=0.0, seed=5):
    """A hologram fist facing -Y: horizontal light slats (it reads as a projection, the city shows through),
    an outline, and a pink ghost copy offset behind (chromatic split). DISPATCH: red, rows torn sideways."""
    st = anim(seed + 7)  # round 28 motion: flicker, scanline crawl, frame-seeded tearing
    if st["off"]:
        return
    col, col2 = kcol(col, st["k"]), kcol(col2, st["k"])
    glitch = max(glitch, st["glitch"])
    fr = max(0, globals().get("FRAME", -1))
    gr = random.Random(seed + fr * 977)
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
            zz = b0 + (pitch * 0.25 * (fr % 4) if fr else 0.0)
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


