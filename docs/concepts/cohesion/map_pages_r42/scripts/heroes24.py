# Round 24 hero buildings + primitives. NOT a module: target_corps.py exec()s this file into its own
# namespace so it shares SOLID / NEON / WIN, box(), beam(), strip(), windows(), roof_trim(), text_obj(), rng.
# Every builder works around the origin with the round 11 scale (ziggurat: 64 wide, crane 80 high).

LIME = (0.50, 1.0, 0.16)
LIME_GLOW = (0.16, 0.46, 0.06)  # reactor fluid: kept low so bloom does not clip it to yellow
MINT = (0.35, 1.0, 0.62)
VIOLET = (0.62, 0.36, 1.0)
ICE = (0.80, 0.94, 1.0)
CRED = (1.0, 0.07, 0.09)
CPINK = (1.0, 0.30, 0.55)
HAL_STONE = (0.48, 0.42, 0.68)
ORB_WHITE = (0.82, 0.86, 0.92)
RC_BLACK = (0.11, 0.09, 0.11)

# corp knobs: street lane colours (centre, edge, cross, cross edge, avenue choices), district families,
# window colours, roof trims, sign colour
CORP_KNOBS = {
    "meridian": dict(lanes=(AMBER, CYAN, PINK, AMBER, (CYAN, AMBER, PINK)), fams=None, win=None, trims=None, sign=(1.0, 0.62, 0.22)),
    "solace": dict(lanes=(LIME, MINT, (0.45, 1.0, 0.30), (0.85, 1.0, 0.80), (LIME, MINT, CYAN)),
                   fams=[(0.40, 0.52, 0.46), (0.50, 0.58, 0.52), (0.36, 0.46, 0.44), (0.62, 0.66, 0.60), (0.44, 0.50, 0.40)],
                   win=[(0.8, 1.0, 0.6), (0.55, 1.0, 0.35), (0.9, 1.0, 0.9), (1.0, 0.85, 0.55), (0.45, 1.0, 0.8)],
                   trims=[LIME, LIME, MINT, CYAN], sign=(0.62, 1.0, 0.30)),
    "halcyon": dict(lanes=(AMBER, VIOLET, VIOLET, AMBER, (VIOLET, AMBER, PINK)),
                    fams=[(0.44, 0.40, 0.58), (0.50, 0.44, 0.62), (0.38, 0.36, 0.52), (0.56, 0.50, 0.66), (0.46, 0.42, 0.50)],
                    win=[(1.0, 0.70, 0.30), (1.0, 0.80, 0.45), (0.70, 0.50, 1.0), (0.95, 0.90, 1.0)],
                    trims=[VIOLET, VIOLET, AMBER, PINK], sign=(1.0, 0.72, 0.30)),
    "orbital": dict(lanes=(ICE, CYAN, CYAN, ICE, (CYAN, ICE, (0.5, 0.6, 1.0))),
                    fams=[(0.52, 0.56, 0.66), (0.60, 0.64, 0.72), (0.44, 0.48, 0.58), (0.70, 0.74, 0.80), (0.40, 0.44, 0.54)],
                    win=[(0.80, 0.95, 1.0), (0.40, 0.85, 1.0), (1.0, 1.0, 1.0), (0.6, 0.7, 1.0)],
                    trims=[ICE, CYAN, CYAN, (0.6, 0.7, 1.0)], sign=(0.75, 0.95, 1.0)),
    "rebel_cell": dict(lanes=(CRED, CPINK, CRED, (1.0, 0.40, 0.20), (CRED, CPINK, (1.0, 0.4, 0.2))),
                       fams=[(0.40, 0.30, 0.32), (0.34, 0.28, 0.30), (0.46, 0.36, 0.34), (0.30, 0.28, 0.34), (0.52, 0.34, 0.30)],
                       win=[(1.0, 0.25, 0.20), (1.0, 0.60, 0.30), (1.0, 0.45, 0.55), (0.9, 0.85, 0.8)],
                       trims=[CRED, CRED, CPINK, (1.0, 0.4, 0.2)], sign=(1.0, 0.18, 0.20)),
}


# ------------------------------------------------------------------ primitives
def _acc_face(acc, q, col, bid, facet):
    if facet and acc is SOLID:
        acc.facet_quad(*q, col, bid)
    else:
        acc.face(list(q), col, bid)


def cyl(cx, cy, z0, z1, r, col, n=12, r1=None, facet=True, cap=True, acc=None, bid=None, a_off=0.0):
    acc = acc or SOLID
    r1 = r if r1 is None else r1
    bid = bid or rid()
    for i in range(n):
        a0 = 2 * math.pi * i / n + a_off
        a1 = 2 * math.pi * (i + 1) / n + a_off
        q = ((cx + r * math.cos(a0), cy + r * math.sin(a0), z0), (cx + r * math.cos(a1), cy + r * math.sin(a1), z0),
             (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), z1), (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), z1))
        _acc_face(acc, q, col, bid, facet)
    if cap and r1 > 0.05:
        for i in range(n):
            a0 = 2 * math.pi * i / n + a_off
            a1 = 2 * math.pi * (i + 1) / n + a_off
            acc.face([(cx, cy, z1), (cx + r1 * math.cos(a0), cy + r1 * math.sin(a0), z1), (cx + r1 * math.cos(a1), cy + r1 * math.sin(a1), z1)], col, bid)
    return bid


def dome(cx, cy, z0, r, col, n=14, rings=4, acc=None, bid=None, hz=1.0):
    acc = acc or SOLID
    bid = bid or rid()
    for k in range(rings):
        t0, t1 = (math.pi / 2) * k / rings, (math.pi / 2) * (k + 1) / rings
        ra, rb = r * math.cos(t0), r * math.cos(t1)
        za, zb = z0 + r * hz * math.sin(t0), z0 + r * hz * math.sin(t1)
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            pts = [(cx + ra * math.cos(a0), cy + ra * math.sin(a0), za), (cx + ra * math.cos(a1), cy + ra * math.sin(a1), za),
                   (cx + rb * math.cos(a1), cy + rb * math.sin(a1), zb)]
            if rb > 0.01:
                pts.append((cx + rb * math.cos(a0), cy + rb * math.sin(a0), zb))
            acc.face(pts, col, bid)
    return bid


def ring_beams(center, u, v, R, w, col, n=36, acc=None, a0=0.0, a1=2 * math.pi):
    """Ring (or arc) of beams in the plane spanned by unit vectors u, v around center."""
    acc = acc or NEON
    c, u, v = Vector(center), Vector(u), Vector(v)
    pts = [c + (u * math.cos(a0 + (a1 - a0) * i / n) + v * math.sin(a0 + (a1 - a0) * i / n)) * R for i in range(n + 1)]
    bid = rid()
    for p, q in zip(pts, pts[1:]):
        beam(tuple(p), tuple(q), w, col, acc=acc, bid=bid)


def disc(center, u, v, R, col, acc=None, n=24):
    acc = acc or NEON
    c, u, v = Vector(center), Vector(u), Vector(v)
    bid = rid()
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        acc.face([tuple(c), tuple(c + (u * math.cos(a0) + v * math.sin(a0)) * R), tuple(c + (u * math.cos(a1) + v * math.sin(a1)) * R)], col, bid)


def dish(c, aim, R, depth, col, n=14, tip=None):
    """Shallow parabolic dish opening along `aim`, plus a feed arm and a glowing tip."""
    c = Vector(c)
    a = Vector(aim).normalized()
    u = a.cross(Vector((0, 0, 1)))
    if u.length < 1e-3:
        u = Vector((1, 0, 0))
    u.normalize()
    v = a.cross(u).normalized()
    bid = rid()
    rings = 3
    prev = [c] * (n + 1)
    for k in range(1, rings + 1):
        rr = R * k / rings
        off = depth * (k / rings) ** 2
        cur = [c + a * off + (u * math.cos(2 * math.pi * i / n) + v * math.sin(2 * math.pi * i / n)) * rr for i in range(n + 1)]
        for i in range(n):
            if k == 1:
                SOLID.face([tuple(c), tuple(cur[i]), tuple(cur[i + 1])], col, bid)
            else:
                SOLID.face([tuple(prev[i]), tuple(cur[i]), tuple(cur[i + 1]), tuple(prev[i + 1])], col, bid)
        prev = cur
    ring_beams(tuple(c + a * depth), u, v, R, 0.35, tuple(x * 0.8 for x in col), n=n, acc=SOLID)
    f = c + a * (R * 0.8)
    for i in range(3):
        p = c + a * (depth * 0.8) + (u * math.cos(2.1 * i) + v * math.sin(2.1 * i)) * R * 0.9
        beam(tuple(p), tuple(f), 0.25, (0.3, 0.3, 0.34))
    if tip:
        box(f.x - 0.5, f.y - 0.5, f.z - 0.5, f.x + 0.5, f.y + 0.5, f.z + 0.5, tip, facet=False)
        NEON.face([(f.x - 0.6, f.y - 0.62, f.z - 0.6), (f.x + 0.6, f.y - 0.62, f.z - 0.6), (f.x + 0.6, f.y - 0.62, f.z + 0.6), (f.x - 0.6, f.y - 0.62, f.z + 0.6)], tip, (0, 0, 0))


def plaza(R, ring_col, ground=(0.30, 0.28, 0.30), lamp=(1.0, 0.85, 0.55), ring2=None):
    n = 48
    bid = rid()
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        SOLID.face([(0, 0, 0.02), (R * math.cos(a0), R * math.sin(a0), 0.02), (R * math.cos(a1), R * math.sin(a1), 0.02)], ground, bid)
        for r, w, c in ((R - 1.2, 0.5, ring_col), (R - 3.0, 0.25, ring2 or ring_col)):
            strip(NEON, (r * math.cos(a0), r * math.sin(a0)), (r * math.cos(a1), r * math.sin(a1)), w, 0.05, c)
        if i % 4 == 0:
            x, y = (R - 2) * math.cos(a0), (R - 2) * math.sin(a0)
            if y < 0 and abs(x) < 13:
                continue
            beam((x, y, 0), (x, y, 5), 0.25, (0.2, 0.2, 0.22))
            NEON.face([(x - 0.55, y - 0.55, 5.62), (x + 0.55, y - 0.55, 5.62), (x + 0.55, y + 0.55, 5.62), (x - 0.55, y + 0.55, 5.62)], lamp, (0, 0, 0))


def vehicle(x, y, body, stripe=None, lights=None, rot90=True, L=6.0, Wd=2.6, Hh=2.2):
    if rot90:
        x0, y0, x1, y1 = x - Wd / 2, y - L / 2, x + Wd / 2, y + L / 2
    else:
        x0, y0, x1, y1 = x - L / 2, y - Wd / 2, x + L / 2, y + Wd / 2
    box(x0, y0, 0.4, x1, y1, Hh, body, facet=False)
    if stripe:
        NEON.face([(x0 - 0.05, y0, 1.0), (x0 - 0.05, y1, 1.0), (x0 - 0.05, y1, 1.4), (x0 - 0.05, y0, 1.4)], stripe, (0, 0, 0))
    if lights:  # roof light bar, two colours
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for k, c in enumerate(lights):
            o = (k - (len(lights) - 1) / 2) * 0.9
            box(cx - 0.4 + o, cy - 0.3, Hh, cx + 0.4 + o, cy + 0.3, Hh + 0.45, c, facet=False)
            NEON.face([(cx - 0.45 + o, cy - 0.35, Hh + 0.47), (cx + 0.45 + o, cy - 0.35, Hh + 0.47), (cx + 0.45 + o, cy + 0.35, Hh + 0.47), (cx - 0.45 + o, cy + 0.35, Hh + 0.47)], c, (0, 0, 0))


def fist(cx, y, z0, s, col, back=(0.06, 0.04, 0.05)):
    """REBEL_CELL raised-fist crest as glowing panels on a wall facing -Y (s = height)."""
    k = s / 14.0
    box(cx - 6.5 * k, y + 0.05, z0 - 0.8 * k, cx + 6.5 * k, y + 0.5, z0 + 14.8 * k, back, facet=False)
    yy = y - 0.05
    parts = []
    for i in range(4):  # fingers (curled, knuckle row)
        x0 = cx - 5.2 * k + i * 2.6 * k
        parts.append((x0, z0 + 8.4 * k, x0 + 2.3 * k, z0 + 13.2 * k + (0.6 * k if i in (1, 2) else 0)))
    parts.append((cx - 5.2 * k, z0 + 5.4 * k, cx + 5.2 * k, z0 + 8.0 * k))  # thumb across
    parts.append((cx - 3.6 * k, z0, cx + 3.6 * k, z0 + 5.0 * k))  # wrist
    for (x0, za, x1, zb) in parts:
        NEON.face([(x0, yy, za), (x1, yy, za), (x1, yy, zb), (x0, yy, zb)], col, (0, 0, 0))


# ================================================================== SOLACE
def renewal_engine():
    plaza(38, LIME, ground=(0.26, 0.30, 0.27), ring2=MINT)
    cyl(0, 0, 0, 6, 30, (0.70, 0.76, 0.72), n=8, a_off=math.pi / 8)
    cyl(0, 0, 6, 10, 23, (0.62, 0.68, 0.64), n=8, a_off=math.pi / 8)
    ring_beams((0, 0, 6.15), (1, 0, 0), (0, 1, 0), 29.5, 0.5, LIME, n=8)
    ring_beams((0, 0, 10.15), (1, 0, 0), (0, 1, 0), 22.6, 0.45, MINT, n=8)
    # the bioreactor capsule: glowing lime fluid in a steel-ribbed glass cage
    cyl(0, 0, 10, 56, 10, LIME_GLOW, n=16, acc=NEON, facet=False, cap=False)
    dome(0, 0, 56, 10, LIME_GLOW, n=16, acc=NEON)
    for z in range(14, 56, 6):  # cell stacks: dark bands across the fluid
        cyl(0, 0, z, z + 0.9, 10.25, (0.10, 0.18, 0.10), n=16, facet=False, cap=False)
    for i in range(10):
        a = 2 * math.pi * i / 10
        beam((12.5 * math.cos(a), 12.5 * math.sin(a), 10), (12.5 * math.cos(a), 12.5 * math.sin(a), 62), 0.8, (0.78, 0.84, 0.80))
    for z in (10.5, 22, 34, 46, 58):
        ring_beams((0, 0, z), (1, 0, 0), (0, 1, 0), 12.5, 0.75, (0.82, 0.88, 0.84), n=20, acc=SOLID)
    cyl(0, 0, 62, 64.5, 14, (0.72, 0.78, 0.74), n=16)
    beam((0, 0, 64.5), (0, 0, 80), 0.6, (0.7, 0.75, 0.72))
    box(-0.8, -0.8, 79, 0.8, 0.8, 80.6, LIME, facet=False)
    NEON.face([(-0.9, -0.85, 79), (0.9, -0.85, 79), (0.9, -0.85, 80.6), (-0.9, -0.85, 80.6)], LIME, (0, 0, 0))
    # double helix wound round the cage (Solace HQ echo): white strand + lime strand, mint rungs
    pts1, pts2 = [], []
    for i in range(73):
        t = i / 72
        a = t * 3 * 2 * math.pi
        z = 12 + t * 46
        pts1.append((16 * math.cos(a), 16 * math.sin(a), z))
        pts2.append((16 * math.cos(a + math.pi), 16 * math.sin(a + math.pi), z))
    for p, q in zip(pts1, pts1[1:]):
        beam(p, q, 1.1, (0.90, 0.95, 0.92))
    for p, q in zip(pts2, pts2[1:]):
        beam(p, q, 0.9, LIME, acc=NEON)
    for i in range(0, 73, 4):
        beam(pts1[i], pts2[i], 0.35, MINT, acc=NEON)
    # implant pods around the reactor, piped in
    for k in range(6):
        a = 2 * math.pi * k / 6 + math.pi / 6
        px, py = 20 * math.cos(a), 20 * math.sin(a)
        if py < -10 and abs(px) < 8:
            continue
        cyl(px, py, 10, 11.6, 3.7, (0.80, 0.86, 0.82), n=12)
        cyl(px, py, 11.6, 19, 3.1, (0.14, 0.40, 0.06), n=12, acc=NEON, facet=False, cap=False)
        dome(px, py, 19, 3.1, (0.18, 0.48, 0.08), n=12, acc=NEON)
        beam((px * 0.8, py * 0.8, 15), (12.5 * math.cos(a), 12.5 * math.sin(a), 15), 0.7, (0.85, 0.9, 0.86))
    # sign + flanking greenhouse cell domes
    box(-12, -31.6, 1.0, 12, -30.8, 5.2, (0.08, 0.10, 0.08), facet=False)
    text_obj("CONTINUUM", (0, -31.75, 3.1), (math.radians(90), 0, 0), 2.6, SIGNM)
    for sx in (-1, 1):
        for k in range(3):
            x = sx * (40 + k * 11)
            y = -48 - (k % 2) * 6
            cyl(x, y, 0, 1.2, 5.6, (0.55, 0.62, 0.56), n=12)
            dome(x, y, 1.2, 5.0, (0.62, 0.78, 0.66), n=12)
            ring_beams((x, y, 1.25), (1, 0, 0), (0, 1, 0), 5.1, 0.35, LIME, n=12)
    for (x, y) in ((-6.5, -78), (6.5, -104)):
        vehicle(x, y, (0.86, 0.90, 0.88), stripe=LIME, lights=(LIME, (0.9, 1, 0.9)), L=7, Wd=3, Hh=3.2)


def implant_hub():
    c = (0.78, 0.84, 0.80)
    box(-22, 4, 0, 22, 26, 10, c)
    windows(-22, 4, 0, 22, 26, 10, p=0.55, cols=[(0.8, 1.0, 0.6), (0.9, 1.0, 0.9)])
    roof_trim(-22, 4, 22, 26, 10.1, LIME, w=0.4)
    box(-6, 3.0, 0, 6, 4.0, 6, (0.10, 0.16, 0.10), facet=False)  # glass entrance
    NEON.face([(-5.6, 2.9, 0.4), (5.6, 2.9, 0.4), (5.6, 2.9, 5.6), (-5.6, 2.9, 5.6)], (0.30, 0.70, 0.18), (0, 0, 0))
    # cross sign pylon
    box(-0.6, 1.0, 0, 0.6, 2.2, 13, (0.25, 0.28, 0.26), facet=False)
    box(-4.2, 0.4, 13, 4.2, 1.2, 21, (0.06, 0.08, 0.06), facet=False)
    NEON.face([(-1.2, 0.3, 14), (1.2, 0.3, 14), (1.2, 0.3, 20), (-1.2, 0.3, 20)], LIME, (0, 0, 0))
    NEON.face([(-3.4, 0.3, 15.8), (3.4, 0.3, 15.8), (3.4, 0.3, 18.2), (-3.4, 0.3, 18.2)], LIME, (0, 0, 0))
    for k, x in enumerate((-12, 0, 12)):  # capsule tanks on the roof
        cyl(x, 17, 10, 11, 3.4, (0.72, 0.78, 0.74), n=12)
        cyl(x, 17, 11, 17, 2.8, (0.26, 0.62, 0.12), n=12, acc=NEON, facet=False, cap=False)
        dome(x, 17, 17, 2.8, (0.32, 0.72, 0.16), n=12, acc=NEON)
    for (x, y, r) in ((32, 8, 6), (40, 18, 4.6), (31, 24, 5.2)):  # cell domes
        cyl(x, y, 0, 1, r + 0.6, (0.55, 0.60, 0.56), n=12)
        dome(x, y, 1, r, (0.62, 0.78, 0.66), n=12)
        ring_beams((x, y, 1.05), (1, 0, 0), (0, 1, 0), r + 0.1, 0.3, LIME, n=12)
    box(-30, -2, 0, -24, 26, 1.4, (0.20, 0.34, 0.18))  # hedges
    for (x, y) in ((-5, -14), (5, -20), (-14, -10)):
        vehicle(x, y, (0.86, 0.90, 0.88), stripe=LIME, lights=(LIME, (0.9, 1, 0.9)), L=7, Wd=3, Hh=3.2)
    text_obj("IMPLANT PROVISIONING", (0, 3.8, 8.0), (math.radians(90), 0, 0), 1.5, SIGNM)


# ================================================================== HALCYON
def colonnade(x0, y0, x1, y1, z0, z1, col=(0.86, 0.84, 0.96), step=4.0, out=1.4, faces=(0, 1, 3)):
    walls = [((x0, y0 - out), (x1, y0 - out)), ((x1 + out, y0), (x1 + out, y1)), ((x1, y1 + out), (x0, y1 + out)), ((x0 - out, y1), (x0 - out, y0))]
    for fi in faces:
        (ax, ay), (bx, by) = walls[fi]
        L = math.hypot(bx - ax, by - ay)
        n = max(2, int(L / step))
        for i in range(n + 1):
            t = i / n
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            beam((x, y, z0), (x, y, z1), 1.0, col)
        beam((ax, ay, z1 + 0.4), (bx, by, z1 + 0.4), 1.2, col)


def eye(center, R, iris, lid=AMBER, pupil=(0.05, 0.03, 0.08), w=1.4):
    """Watching-eye crest in the xz-plane facing -Y: almond lids, amber iris, dark pupil, glint."""
    cx, cy, cz = center
    up = []
    lo = []
    for i in range(25):
        t = i / 24
        x = cx - R + 2 * R * t
        hgt = R * 0.48 * math.sin(math.pi * t)
        up.append((x, cy, cz + hgt))
        lo.append((x, cy, cz - hgt))
    for p, q in zip(up, up[1:]):
        beam(p, q, w, lid, acc=NEON)
    for p, q in zip(lo, lo[1:]):
        beam(p, q, w, lid, acc=NEON)
    disc((cx, cy + 0.2, cz), (1, 0, 0), (0, 0, 1), R * 0.62, (0.10, 0.06, 0.16), acc=SOLID)  # eye white = dark socket
    disc((cx, cy - 0.1, cz), (1, 0, 0), (0, 0, 1), iris, lid, acc=NEON)
    disc((cx, cy - 0.3, cz), (1, 0, 0), (0, 0, 1), iris * 0.46, pupil, acc=SOLID)
    disc((cx - iris * 0.3, cy - 0.45, cz + iris * 0.32), (1, 0, 0), (0, 0, 1), iris * 0.14, (1.0, 0.95, 0.85), acc=NEON)


def civic_core():
    plaza(38, VIOLET, ground=(0.28, 0.26, 0.34), ring2=AMBER)
    tiers = [(30, 0, 10), (24, 10, 20), (18, 20, 30), (12, 30, 38)]
    for i, (hs, z0, z1) in enumerate(tiers):
        c = tuple(v + i * 0.03 for v in HAL_STONE)
        box(-hs, -hs, z0, hs, hs, z1, c)
        zb = z0 + (z1 - z0) * 0.40
        for k in range(int(2 * hs / 3.0)):
            t0, t1 = -hs + k * 3.0 + 0.35, -hs + (k + 1) * 3.0 - 0.35
            WIN.face([(t0, -hs - 0.08, zb), (t1, -hs - 0.08, zb), (t1, -hs - 0.08, zb + 2.0), (t0, -hs - 0.08, zb + 2.0)], (1.0, 0.70, 0.30), (0, 0, 0))
            WIN.face([(-hs - 0.08, t1, zb), (-hs - 0.08, t0, zb), (-hs - 0.08, t0, zb + 2.0), (-hs - 0.08, t1, zb + 2.0)], (1.0, 0.70, 0.30), (0, 0, 0))
            WIN.face([(hs + 0.08, t0, zb), (hs + 0.08, t1, zb), (hs + 0.08, t1, zb + 2.0), (hs + 0.08, t0, zb + 2.0)], (1.0, 0.70, 0.30), (0, 0, 0))
        colonnade(-hs, -hs, hs, hs, z0, z1 - 0.6)
        roof_trim(-hs, -hs, hs, hs, z1 + 0.1, VIOLET, w=0.45)
    # apex pylon + the EYE crest (Halcyon's crest is now an eye, not a halo)
    box(-4, -4, 38, 4, 4, 46, (0.22, 0.18, 0.32))
    beam((0, -2, 46), (0, -2, 50), 1.6, (0.22, 0.18, 0.32))
    eye((0, -2.5, 58), 15, 5.4, lid=(0.62, 0.40, 0.10))  # dimmer than the slice values behind the wheels
    for k in range(7):  # short amber rays above the eye
        a = math.radians(30 + k * 20)
        beam((16.5 * math.cos(a), -2.5, 58 + 9.5 * math.sin(a)), (20.5 * math.cos(a), -2.5, 58 + 12.5 * math.sin(a)), 0.7, AMBER, acc=NEON)
    # radar dishes on tier 2 corners
    for sx in (-1, 1):
        beam((sx * 21, 8, 20), (sx * 21, 8, 24), 1.0, (0.3, 0.3, 0.36))
        dish((sx * 21, 8, 25), (sx * 0.5, -0.4, 0.8), 5.0, 1.5, (0.86, 0.84, 0.92), tip=AMBER)
    text_obj("HALCYON CIVIC", (0, -30.2, 6.6), (math.radians(90), 0, 0), 3.0, SIGNM)
    # police presence on the plaza
    for (x, y) in ((-20, -44), (-12, -48), (14, -46), (22, -42)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=False)




def precinct():
    c = HAL_STONE
    box(-24, 4, 0, 24, 24, 13, c)
    windows(-24, 4, 0, 24, 24, 13, p=0.45, cols=[(1.0, 0.70, 0.30), (0.7, 0.5, 1.0)], faces=(1, 2, 3))
    colonnade(-24, 4, 24, 24, 0, 11, faces=(0,), step=6.0, out=2.0)
    box(-25, 1.4, 11, 25, 4, 14, (0.56, 0.50, 0.72))  # lintel
    roof_trim(-24, 4, 24, 24, 14.1, VIOLET, w=0.4)
    box(-9, 1.0, 14, 9, 2.0, 22, (0.20, 0.16, 0.30), facet=False)
    eye((0, 0.85, 18), 7.5, 2.6, w=0.8)
    beam((14, 16, 13), (14, 16, 16), 0.8, (0.3, 0.3, 0.36))
    dish((14, 16, 17), (0.2, -0.5, 0.85), 4.5, 1.3, (0.86, 0.84, 0.92), tip=AMBER)
    beam((-16, 18, 13), (-16, 18, 30), 0.4, (0.3, 0.3, 0.36))
    NEON.face([(-16.5, 17.4, 29), (-15.5, 17.4, 29), (-15.5, 17.4, 30), (-16.5, 17.4, 30)], CRED, (0, 0, 0))
    for (x, y) in ((-14, -8), (-5, -12), (6, -9), (16, -14)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=False)
    for x in range(-30, 31, 5):  # amber barrier line
        box(x - 2, -26, 0, x + 2, -25.4, 1.1, AMBER if (x // 5) % 2 == 0 else (0.08, 0.06, 0.04), facet=False)
    text_obj("HALCYON ENFORCEMENT", (0, 1.25, 12.4), (math.radians(90), 0, 0), 1.5, SIGNM)


# ================================================================== ORBITAL
def commons_array():
    plaza(38, CYAN, ground=(0.10, 0.12, 0.18), ring2=ICE)
    srng = random.Random(77)
    stars = [(srng.uniform(-30, 30), srng.uniform(-30, 30)) for _ in range(16)]
    stars = [s for s in stars if math.hypot(*s) < 33]
    for (x, y) in stars:
        NEON.face([(x - 0.4, y - 0.4, 0.06), (x + 0.4, y - 0.4, 0.06), (x + 0.4, y + 0.4, 0.06), (x - 0.4, y + 0.4, 0.06)], ICE, (0, 0, 0))
    for p, q in zip(stars, stars[1:]):
        strip(NEON, p, q, 0.16, 0.05, (0.25, 0.6, 0.8))
    cyl(0, 0, 0, 4, 30, ORB_WHITE, n=24)
    ring_beams((0, 0, 4.1), (1, 0, 0), (0, 1, 0), 29.6, 0.45, CYAN, n=24)
    # lattice mast + beacon + uplink beam into the sky
    top = 92
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam((sx * 7, sy * 7, 4), (sx * 1.2, sy * 1.2, top), 1.0, (0.88, 0.92, 0.96))
    for z in range(10, top - 4, 9):
        k = 1 - (z - 4) / (top - 4)
        s = 1.2 + 5.8 * k
        for (a, b) in (((-s, -s), (s, -s)), ((s, -s), (s, s)), ((s, s), (-s, s)), ((-s, s), (-s, -s))):
            beam((a[0], a[1], z), (b[0], b[1], z), 0.4, (0.80, 0.85, 0.92))
        s2 = 1.2 + 5.8 * (1 - (z + 9 - 4) / (top - 4))
        beam((-s, -s, z), (s2, -s2, z + 9), 0.3, (0.75, 0.8, 0.88))
    box(-1.4, -1.4, top, 1.4, 1.4, top + 2.4, (0.9, 0.95, 1.0), facet=False)
    NEON.face([(-1.5, -1.5, top + 0.2), (1.5, -1.5, top + 0.2), (1.5, -1.5, top + 2.2), (-1.5, -1.5, top + 2.2)], CYAN, (0, 0, 0))
    box(-0.25, -0.25, top + 2.4, 0.25, 0.25, 420, (0.25, 0.65, 0.85), facet=False)  # uplink beam
    NEON.face([(-0.3, -0.3, top + 2.4), (0.3, -0.3, top + 2.4), (0.3, -0.3, 420), (-0.3, -0.3, 420)], (0.35, 0.80, 1.0), (0, 0, 0))
    # glowing rings up the mast (constellation status)
    for z in (24, 44, 64, 80):
        k = 1 - (z - 4) / (top - 4)
        s = 1.2 + 5.8 * k + 1.2
        ring_beams((0, 0, z), (1, 0, 0), (0, 1, 0), s * 1.25, 0.5, CYAN if z != 44 else ICE, n=16)
    # the dish array: three big dishes on pedestals + a ring of small ones
    for k, a in enumerate((math.radians(150), math.radians(30), math.radians(90))):
        px, py = 22 * math.cos(a), 22 * math.sin(a) + 4
        cyl(px, py, 4, 14, 2.4, (0.62, 0.66, 0.72), n=10)
        aim = Vector((math.cos(a) * 0.35, -0.45, 0.85))
        dish((px, py, 22), aim, 11.5, 3.6, (0.92, 0.95, 0.98), n=18, tip=CYAN)
        beam((px, py, 14), (px, py, 20), 1.6, (0.62, 0.66, 0.72))
    for k in range(5):
        a = math.radians(205 + k * 32.5)
        px, py = 26 * math.cos(a), 26 * math.sin(a)
        if abs(px) < 11:
            continue
        cyl(px, py, 4, 6, 1.2, (0.6, 0.64, 0.7), n=8)
        dish((px, py, 8), (math.cos(a) * 0.3, -0.5, 0.8), 3.6, 1.1, (0.9, 0.93, 0.97), tip=CYAN)
    text_obj("ORBITAL COMMONS", (0, -29.8, 2.1), (math.radians(90), 0, 0), 2.2, SIGNM)
    for (x, y) in ((-6.5, -80), (6.5, -110)):
        vehicle(x, y, (0.86, 0.9, 0.95), stripe=CYAN, L=7, Wd=3, Hh=3.0)


def ground_station():
    box(-28, 12, 0, -4, 30, 9, ORB_WHITE)
    windows(-28, 12, 0, -4, 30, 9, p=0.5, cols=[(0.8, 0.95, 1.0), (0.4, 0.85, 1.0)])
    roof_trim(-28, 12, -4, 30, 9.1, CYAN, w=0.4)
    for k, x in enumerate((-24, -16, -9)):
        beam((x, 22, 9), (x, 22, 11), 0.4, (0.4, 0.42, 0.48))
        dish((x, 22, 12), (0.1 * k - 0.1, -0.5, 0.8), 2.4, 0.8, (0.9, 0.93, 0.97), tip=CYAN)
    text_obj("GROUND STATION ALPHA", (-16, 11.8, 7.0), (math.radians(90), 0, 0), 1.4, SIGNM)
    # the big dish on its pedestal
    box(10, 6, 0, 18, 14, 10, (0.70, 0.74, 0.80))
    cyl(14, 10, 10, 13, 3.0, (0.6, 0.64, 0.7), n=10)
    dish((14, 10, 21), (-0.25, -0.55, 0.8), 12.5, 3.8, (0.92, 0.95, 0.98), n=18, tip=CYAN)
    beam((14, 10, 13), (14, 10, 19), 1.4, (0.6, 0.64, 0.7))
    # radome
    cyl(34, 26, 0, 4, 7.2, (0.7, 0.74, 0.8), n=14)
    dome(34, 26, 4, 7, (0.92, 0.95, 0.98), n=14, rings=5)
    for x in range(-44, 45, 4):  # perimeter fence
        beam((x, -24, 0), (x, -24, 2.5), 0.15, (0.4, 0.42, 0.46))
    strip(NEON, (-44, -24), (-10, -24), 0.25, 2.4, CYAN)
    strip(NEON, (10, -24), (44, -24), 0.25, 2.4, CYAN)
    vehicle(-4, -14, (0.86, 0.9, 0.95), stripe=CYAN, L=7, Wd=3, Hh=3.0)


# ================================================================== REBEL_CELL
def cable(p0, p1, sag, w=0.35, col=(0.05, 0.04, 0.05), acc=None, n=10):
    p0, p1 = Vector(p0), Vector(p1)
    pts = [p0.lerp(p1, i / n) - Vector((0, 0, sag * 4 * (i / n) * (1 - i / n))) for i in range(n + 1)]
    for a, b in zip(pts, pts[1:]):
        beam(tuple(a), tuple(b), w, col, acc=acc)


def dispatch():
    plaza(38, CRED, ground=(0.16, 0.08, 0.09), ring2=CPINK)
    grng = random.Random(55)
    for _ in range(60):  # corrupted plaza: offset slabs + red glitch tiles
        a, r = grng.uniform(0, 2 * math.pi), grng.uniform(16, 36)
        x, y = r * math.cos(a), r * math.sin(a)
        if y < -10 and abs(x) < 12:
            continue
        s = grng.uniform(1.5, 4.0)
        if grng.random() < 0.55:
            box(x - s, y - s, 0, x + s, y + s, grng.uniform(0.3, 1.6), (0.14, 0.07, 0.08), facet=False)
        else:
            NEON.face([(x - s, y - s, 0.07), (x + s, y - s, 0.07), (x + s, y + s, 0.07), (x - s, y + s, 0.07)],
                      CRED if grng.random() < 0.7 else CPINK, (0, 0, 0))
    # the DISPATCH stack: rack segments, some shoved sideways (corrupted), red vents, status LEDs
    z = 0
    for k in range(8):
        j = k * 0.8
        dx = grng.choice([0, 0, 0, 1.6, -1.8])
        x0, y0, x1, y1 = -15 + j + dx, -11 + j, 15 - j + dx, 11 - j
        h = 9.0
        box(x0, y0, z, x1, y1, z + h, RC_BLACK)
        for r in range(3):
            zz = z + 1.8 + r * 2.4
            NEON.face([(x0 + 1.2, y0 - 0.08, zz), (x1 - 1.2, y0 - 0.08, zz), (x1 - 1.2, y0 - 0.08, zz + 0.7), (x0 + 1.2, y0 - 0.08, zz + 0.7)],
                      CRED if (k + r) % 4 else CPINK, (0, 0, 0))
        for r in range(4):
            NEON.face([(x0 - 0.08, y0 + 2 + r * 2.5, z + 6), (x0 - 0.08, y0 + 2.6 + r * 2.5, z + 6), (x0 - 0.08, y0 + 2.6 + r * 2.5, z + 6.6), (x0 - 0.08, y0 + 2 + r * 2.5, z + 6.6)], CRED, (0, 0, 0))
        roof_trim(x0, y0, x1, y1, z + h + 0.05, (0.55, 0.04, 0.06), w=0.3)
        z += h
    top = z
    for sx in (-1, 1):  # antenna crown
        for sy in (-1, 1):
            beam((sx * 6, sy * 4, top), (sx * 1.0, sy * 0.8, top + 18), 0.7, (0.2, 0.18, 0.2))
    box(-1, -1, top + 17, 1, 1, top + 19, CRED, facet=False)
    NEON.face([(-1.1, -1.1, top + 17), (1.1, -1.1, top + 17), (1.1, -1.1, top + 19), (-1.1, -1.1, top + 19)], CRED, (0, 0, 0))
    dish((5, -3, top + 6), (0.6, -0.5, 0.4), 3.5, 1.0, (0.35, 0.3, 0.32))  # broken, tilted dish
    fist(0, -11.6 + 2 * 0.8, 20, 20, CRED)  # fist crest on the front of the stack
    # hijacked Cell relays round the plaza, cabled to the stack
    for k in range(6):
        a = math.radians(200 + k * 28)
        rx, ry = 31 * math.cos(a), 31 * math.sin(a) + 10
        if ry < -10 and abs(rx) < 14:
            continue
        box(rx - 2.6, ry - 2.6, 0, rx + 2.6, ry + 2.6, 4.2, (0.20, 0.16, 0.18))
        for s in (-1, 1):
            beam((rx + s * 1.5, ry, 4.2), (rx, ry, 13), 0.3, (0.25, 0.22, 0.24))
        NEON.face([(rx - 2.6, ry - 2.7, 2.6), (rx + 2.6, ry - 2.7, 2.6), (rx + 2.6, ry - 2.7, 3.2), (rx - 2.6, ry - 2.7, 3.2)], CPINK, (0, 0, 0))
        cable((rx, ry, 12), (0, 0, 30 + k * 4), 6, w=0.35)
        cable((rx, ry, 11), (0, 0, 24 + k * 3), 4, w=0.18, col=CRED, acc=NEON)
    text_obj("DISPATCH", (0, -11.75, 3.0), (math.radians(90), 0, 0), 2.8, SIGNM)


def relay_rooftop():
    c = (0.38, 0.30, 0.32)
    box(-20, 6, 0, 20, 26, 14, c)
    windows(-20, 6, 0, 20, 26, 14, p=0.5, cols=[(1.0, 0.45, 0.30), (1.0, 0.70, 0.40), (0.9, 0.85, 0.8)])
    box(-28, 10, 0, -20, 26, 9, (0.30, 0.26, 0.30))
    box(20, 8, 0, 30, 26, 11, (0.34, 0.28, 0.32))
    roof_trim(-20, 6, 20, 26, 14.1, (0.55, 0.05, 0.07), w=0.35)
    box(8, 16, 14, 16, 24, 18, (0.22, 0.18, 0.2))  # roof shack
    cyl(-12, 20, 14, 19, 2.6, (0.3, 0.26, 0.28), n=10)  # water tank
    # jury-rigged relay mast
    legs = [(-4, 12), (4, 12), (0, 19)]
    for (x, y) in legs:
        beam((x, y, 14), (0, 15, 44), 0.5, (0.24, 0.2, 0.22))
    for z in range(18, 42, 5):
        k = (z - 14) / 30
        pts = [(x * (1 - k), 15 + (y - 15) * (1 - k), z) for (x, y) in legs]
        for p, q in zip(pts, pts[1:] + pts[:1]):
            beam(p, q, 0.3, CRED if z % 10 == 8 else (0.28, 0.24, 0.26), acc=NEON if z % 10 == 8 else None)
    for k, (z, aim) in enumerate(((30, (-0.7, -0.5, 0.4)), (36, (0.7, -0.4, 0.5)), (24, (0.2, -0.8, 0.5)))):
        dish((0, 15, z), aim, 2.8, 0.9, (0.6, 0.55, 0.58))
    box(-0.6, 14.4, 44, 0.6, 15.6, 45.4, CRED, facet=False)
    NEON.face([(-0.7, 14.3, 44), (0.7, 14.3, 44), (0.7, 14.3, 45.4), (-0.7, 14.3, 45.4)], CRED, (0, 0, 0))
    for (p, q, s) in (((0, 15, 40), (-34, 2, 18), 5), ((0, 15, 38), (36, 30, 20), 6), ((0, 15, 34), (-30, 40, 24), 4)):
        cable(p, q, s, w=0.3, col=(0.30, 0.22, 0.26))
    cable((0, 15, 36), (34, 0, 16), 5, w=0.22, col=CRED, acc=NEON)
    cable((0, 15, 32), (-36, 6, 15), 6, w=0.22, col=CPINK, acc=NEON)
    fist(-10, 5.9, 4, 8, CRED)
    for k in range(4):  # spray-tag strips
        x = 2 + k * 4
        NEON.face([(x, 5.9, 2 + k % 2), (x + 3, 5.9, 2 + k % 2), (x + 3, 5.9, 2.4 + k % 2), (x, 5.9, 2.4 + k % 2)], CPINK, (0, 0, 0))
    for (x, y) in ((-6, -14), (8, -18)):
        vehicle(x, y, (0.22, 0.18, 0.2), lights=(CRED,), rot90=False)


HEROES = {("solace", "boss"): renewal_engine, ("solace", "regular"): implant_hub,
          ("halcyon", "boss"): civic_core, ("halcyon", "regular"): precinct,
          ("orbital", "boss"): commons_array, ("orbital", "regular"): ground_station,
          ("rebel_cell", "boss"): dispatch, ("rebel_cell", "regular"): relay_rooftop}


