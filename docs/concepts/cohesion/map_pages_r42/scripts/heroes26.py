# Round 26 HQ / Site builders. NOT a module: hq_scene.py exec()s this file after heroes24.py and heroes25.py,
# sharing SOLID / NEON / WIN, box(), beam(), strip(), cyl(), dome(), dish(), eye(), plaza(), vehicle(), ...
# New this round: BEAM (translucent light cones), ANIM_ACCS (one light set per animation frame: Solace chaser),
# EYE_ACC (Halcyon's eye as its own objects so it can turn and scan).

BEAM = Acc("beam")
LIT = Acc("lit")  # floodlit surfaces: toon shading + a warm self-light
ANIM_ACCS = []
EYE_ACC = {}
EYE_STATIC = []
EYE_ANGLES = []      # per animation frame (degrees, about the pylon axis)
EYE_STILL = 0.0
NFRAMES = 12
HC = 5.2             # container course height
MERIDIAN_CHOICE = "motte"

# ================================================================== helpers
def obox(cx, cy, z0, L, Wd, H, ang, col, ribs=True, acc=None, bid=None):
    """Oriented container: L along `ang`, corrugation ribs on the long faces."""
    acc = acc or SOLID
    ca, sa = math.cos(ang), math.sin(ang)

    def P(u, v, z):
        return (cx + u * ca - v * sa, cy + u * sa + v * ca, z)
    hl, hw = L / 2, Wd / 2
    b = [P(-hl, -hw, z0), P(hl, -hw, z0), P(hl, hw, z0), P(-hl, hw, z0)]
    t = [P(-hl, -hw, z0 + H), P(hl, -hw, z0 + H), P(hl, hw, z0 + H), P(-hl, hw, z0 + H)]
    bid = bid or rid()
    for i in range(4):
        j = (i + 1) % 4
        acc.facet_quad(b[i], b[j], t[j], t[i], col, bid)
    acc.facet_quad(t[0], t[1], t[2], t[3], col, bid, jit=0.01)
    if ribs and L > 3:
        dark = tuple(c * 0.66 for c in col)
        n = max(2, int(L / 1.7))
        for v in (-hw - 0.05, hw + 0.05):
            for k in range(1, n):
                u = -hl + L * k / n
                acc.face([P(u - 0.16, v, z0 + 0.35), P(u + 0.16, v, z0 + 0.35), P(u + 0.16, v, z0 + H - 0.35), P(u - 0.16, v, z0 + H - 0.35)], dark, bid)


WALL_C = [(0.26, 0.11, 0.07), (0.21, 0.09, 0.06), (0.30, 0.12, 0.07), (0.18, 0.08, 0.06)]   # dark rust walls
TOWER_C = [(1.0, 0.56, 0.12), (1.0, 0.50, 0.10), (1.0, 0.64, 0.20)]                       # bright orange towers
WHITE_C = (0.88, 0.86, 0.80)
BATTLE = (1.0, 0.62, 0.15)


def wcol(k):
    return WALL_C[k % len(WALL_C)]


def tcol(k):
    return TOWER_C[k % len(TOWER_C)] if k % 7 else WHITE_C


def drum(cx, cy, r, courses, z0=0.0, cols=tcol, merlons=True, roof=(0.18, 0.10, 0.06), banner=None):
    """Round tower: rings of containers set tangentially, course by course; lit battlement ring on top."""
    n = max(6, int(2 * math.pi * r / 4.6))
    L = 2 * r * math.sin(math.pi / n) * 1.12
    for k in range(courses):
        off = (k % 2) * math.pi / n
        for i in range(n):
            a = 2 * math.pi * i / n + off
            obox(cx + r * math.cos(a), cy + r * math.sin(a), z0 + k * HC, L, 2.4, HC, a + math.pi / 2, cols(i + 3 * k),
                 acc=LIT if cols is tcol else None)  # towers: floodlit (lit toon), walls: plain toon
    top = z0 + courses * HC
    disc((cx, cy, top - 0.3), (1, 0, 0), (0, 1, 0), r + 0.6, roof, acc=SOLID, n=n)
    if merlons:
        for i in range(0, n, 2):
            a = 2 * math.pi * (i + 0.5) / n
            obox(cx + r * math.cos(a), cy + r * math.sin(a), top, L * 0.55, 2.4, 2.2, a + math.pi / 2, cols(i + 1), ribs=False)
    ring_beams((cx, cy, top + 0.15), (1, 0, 0), (0, 1, 0), r + 1.35, 0.45, BATTLE, n=max(12, n))
    for j in range(4):  # floodlights wash the tower from its foot: towers read lit against dark walls
        a = 2 * math.pi * (j + 0.5) / 4
        ca, sa = math.cos(a), math.sin(a)
        NEON.face([(cx + (r + 2.2) * ca - 0.6, cy + (r + 2.2) * sa - 0.6, z0 + 0.6), (cx + (r + 2.2) * ca + 0.6, cy + (r + 2.2) * sa - 0.6, z0 + 0.6),
                   (cx + (r + 2.2) * ca + 0.6, cy + (r + 2.2) * sa + 0.6, z0 + 0.6), (cx + (r + 2.2) * ca - 0.6, cy + (r + 2.2) * sa + 0.6, z0 + 0.6)], (1.0, 0.85, 0.55), (0, 0, 0))

    if banner is not None:  # a long orange banner hanging on the side that faces `banner` (radians)
        a = banner
        bx, by = cx + (r + 1.4) * math.cos(a), cy + (r + 1.4) * math.sin(a)
        tx, ty = -math.sin(a) * 1.6, math.cos(a) * 1.6
        zt = top - 1.0
        SOLID.face([(bx - tx, by - ty, zt), (bx + tx, by + ty, zt), (bx + tx, by + ty, zt - 13), (bx, by, zt - 15.5), (bx - tx, by - ty, zt - 13)],
                   (1.0, 0.48, 0.06), rid())
        NEON.face([(bx - tx * 0.3 + math.cos(a) * 0.05, by - ty * 0.3 + math.sin(a) * 0.05, zt - 3), (bx + tx * 0.3 + math.cos(a) * 0.05, by + ty * 0.3 + math.sin(a) * 0.05, zt - 3),
                   (bx + tx * 0.3 + math.cos(a) * 0.05, by + ty * 0.3 + math.sin(a) * 0.05, zt - 10), (bx - tx * 0.3 + math.cos(a) * 0.05, by - ty * 0.3 + math.sin(a) * 0.05, zt - 10)],
                  (1.0, 0.92, 0.80), (0, 0, 0))
        beam((bx, by, zt), (bx, by, zt + 7), 0.3, (0.2, 0.2, 0.22))
        flag(bx, by, zt + 6.5, 1.2, (1.0, 0.5, 0.08))
    return top


def cwall(p0, p1, courses, z0=0.0, cols=wcol, merlons=True, skip=None):
    """Straight curtain wall of containers from p0 to p1 (2D), lit battlement line along its top."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy)
    ang = math.atan2(dy, dx)
    n = max(1, int(round(L / 12.0)))
    l = L / n
    for k in range(courses):
        for i in range(n):
            u = (i + 0.5) / n
            x, y = p0[0] + dx * u, p0[1] + dy * u
            if skip and skip(x, y):
                continue
            obox(x, y, z0 + k * HC, l * 1.02, 4.8, HC, ang, cols(i + 2 * k))
    top = z0 + courses * HC
    if merlons:
        m = max(1, int(L / 4.0))
        for i in range(0, m, 2):
            u = (i + 0.5) / m
            x, y = p0[0] + dx * u, p0[1] + dy * u
            if skip and skip(x, y):
                continue
            obox(x, y, top, L / m * 0.9, 4.8, 2.0, ang, cols(i + 1), ribs=False)
    nx, ny = -dy / L, dx / L
    for s in (-1, 1):
        a = (p0[0] + nx * 2.5 * s, p0[1] + ny * 2.5 * s, top + 0.12)
        b = (p1[0] + nx * 2.5 * s, p1[1] + ny * 2.5 * s, top + 0.12)
        beam(a, b, 0.35, BATTLE, acc=NEON)
    return top


def gatehouse(gx, courses=6, w=7.5, moat=True):
    """Twin drum towers facing +X, portcullis, glowing gate, drawbridge (a container) over a lit moat."""
    for sy in (-1, 1):
        drum(gx, sy * w, 4.4, courses, banner=0.0)
    gh = (courses - 2) * HC
    obox(gx, 0, gh, 2 * w, 6.0, 2 * HC, math.pi / 2, TOWER_C[0])  # gate passage block over the arch
    for u in (-3.6, -1.8, 0, 1.8, 3.6):
        beam((gx + 3.2, u, 0.2), (gx + 3.2, u, gh), 0.45, (0.10, 0.09, 0.10))
    for z in range(3, int(gh), 4):
        beam((gx + 3.2, -4.4, z), (gx + 3.2, 4.4, z), 0.45, (0.10, 0.09, 0.10))
    NEON.face([(gx + 2.6, -4.4, 0.2), (gx + 2.6, 4.4, 0.2), (gx + 2.6, 4.4, gh), (gx + 2.6, -4.4, gh)], (0.85, 0.42, 0.08), (0, 0, 0))
    text_obj("MERIDIAN", (gx + 3.3, 0, gh + HC), (math.radians(90), 0, math.radians(90)), 2.2, SIGNM)
    x0 = gx + 3.4
    SOLID.face([(x0, -4.6, 1.6), (x0 + 10, -4.6, 0.4), (x0 + 10, 4.6, 0.4), (x0, 4.6, 1.6)], (0.80, 0.36, 0.08), rid())
    for u in range(-4, 5, 2):
        beam((x0 + 0.2, u, 1.7), (x0 + 9.8, u, 0.5), 0.3, (0.40, 0.18, 0.06))
    for sy in (-1, 1):
        beam((x0, sy * 5.0, gh), (x0 + 9.6, sy * 4.6, 0.6), 0.25, (0.7, 0.7, 0.72))
    if moat:
        for (a0, a1) in ((-27, -5.2), (5.2, 27)):
            strip(NEON, (x0 + 5, a0), (x0 + 5, a1), 6.0, 0.03, (0.32, 0.13, 0.02))
            strip(NEON, (x0 + 2.2, a0), (x0 + 2.2, a1), 0.35, 0.05, BATTLE)
            strip(NEON, (x0 + 7.8, a0), (x0 + 7.8, a1), 0.35, 0.05, BATTLE)
        strip(NEON, (x0 + 5, -5.2), (x0 + 5, 5.2), 6.0, 0.03, (0.32, 0.13, 0.02))


# ================================================================== MERIDIAN: four castle silhouettes
def castle_concentric():
    """Beaumaris / Harlech: a low outer ring with small drums, a high inner square with big drum corners, a central keep."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    Ro = 23.0
    pts = [(Ro * math.cos(math.radians(22.5 + 45 * i)), Ro * math.sin(math.radians(22.5 + 45 * i))) for i in range(8)]
    for i in range(8):
        p, q = pts[i], pts[(i + 1) % 8]
        cwall(p, q, 2, skip=lambda x, y: x > 15 and abs(y) < 6)
    for i, p in enumerate(pts):
        drum(p[0], p[1], 3.0, 3)
    S = 13.0
    for (p, q) in (((-S, -S), (S, -S)), ((S, S), (-S, S)), ((-S, S), (-S, -S)), ((S, -S), (S, S))):
        cwall(p, q, 4, skip=lambda x, y: x > 10 and abs(y) < 5)
    for sx in (-1, 1):
        for sy in (-1, 1):
            drum(sx * S, sy * S, 4.8, 6, banner=math.atan2(-sy * 0.0 - 0.7, 0.7) if sx > 0 else None)
    for sy in (-1, 1):
        drum(0, sy * S, 3.8, 5)
    drum(-2, 0, 6.0, 9, banner=0.0)  # the keep
    flag(-2, 0, 9 * HC + 2, 12, (1.0, 0.5, 0.08))
    gatehouse(S, courses=6, w=6.6, moat=False)
    gatehouse(Ro, courses=3, w=7.0, moat=True)


def castle_motte():
    """Motte-and-bailey: a keep on a mound at the back, a container palisade round the bailey, gate to the front."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    mx = -11.0
    cyl(mx, 0, 0, 12, 14, (0.28, 0.24, 0.15), n=20, r1=8.0)  # the motte (faceted earth)
    for k in range(5):  # spiral path up the mound
        a0, a1 = math.radians(-60 + k * 70), math.radians(-60 + (k + 1) * 70)
        r0, r1 = 13.5 - k * 1.1, 13.5 - (k + 1) * 1.1
        beam((mx + r0 * math.cos(a0), r0 * math.sin(a0), k * 2.4), (mx + r1 * math.cos(a1), r1 * math.sin(a1), (k + 1) * 2.4), 0.6, BATTLE, acc=NEON)
    drum(mx, 0, 7.4, 1, z0=12, cols=wcol)
    drum(mx, 0, 4.6, 6, z0=12, banner=0.0)
    flag(mx, 0, 12 + 6 * HC + 2, 12, (1.0, 0.5, 0.08))
    n = 9
    pts = [(4 + 20 * math.cos(math.radians(-150 + 300 * i / (n - 1))), 22 * math.sin(math.radians(-150 + 300 * i / (n - 1)))) for i in range(n)]
    for p, q in zip(pts, pts[1:]):
        cwall(p, q, 2, skip=lambda x, y: x > 19 and abs(y) < 6)
    for p in pts[::2]:
        drum(p[0], p[1], 2.8, 3)
    for i, (x, y) in enumerate(((2, -9), (6, 8), (12, -2))):  # sheds in the bailey
        obox(x, y, 0, 12, 4.8, HC, 0.3 * i, tcol(i))
    beam((-3, 0, 12), (8, 0, 0.5), 2.4, (0.40, 0.20, 0.08))  # bridge from the bailey up the motte
    gatehouse(23.0, courses=3, w=6.6, moat=True)


def castle_star():
    """Star fort: five pointed bastions, low thick walls, watch drums on the points, a tall central keep."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    pts = []
    for i in range(10):
        a = math.radians(36 * i + 36)
        r = 26.0 if i % 2 == 0 else 15.5
        pts.append((r * math.cos(a), r * math.sin(a)))
    for i in range(10):
        p, q = pts[i], pts[(i + 1) % 10]
        cwall(p, q, 2, skip=lambda x, y: x > 12 and abs(y) < 5)
    for i in range(0, 10, 2):
        drum(pts[i][0], pts[i][1], 2.8, 4)
    drum(0, 0, 6.5, 8, banner=0.0)
    drum(0, 0, 4.0, 2, z0=8 * HC, cols=lambda k: WHITE_C)
    flag(0, 0, 10 * HC + 2, 12, (1.0, 0.5, 0.08))
    gatehouse(15.5, courses=4, w=6.0, moat=True)


def castle_japan():
    """Himeji-like: battered stone base, shrinking tiers of containers under flared roofs, a fenced outer court."""
    plaza(27.5, BATTLE, ground=(0.22, 0.18, 0.16), ring2=(1.0, 0.45, 0.10))
    box(-17, -17, 0, 17, 17, 9, (0.32, 0.31, 0.34), taper=3.0)  # battered stone base
    z = 9.0
    for i, h in enumerate((13.0, 11.0, 9.0, 7.0, 5.2)):
        for (p, q) in (((-h, -h), (h, -h)), ((h, -h), (h, h)), ((h, h), (-h, h)), ((-h, h), (-h, -h))):
            cwall(p, q, 1, z0=z, cols=(tcol if i % 2 == 0 else (lambda k: WHITE_C)), merlons=False)
        z += HC
        rh = h + 3.4
        box(-rh, -rh, z, rh, rh, z + 0.9, (0.20, 0.24, 0.28), facet=False)  # flared roof slab
        box(-h + 0.6, -h + 0.6, z + 0.9, h - 0.6, h - 0.6, z + 2.4, (0.20, 0.24, 0.28), taper=1.2)
        for sx in (-1, 1):
            for sy in (-1, 1):  # upturned corners
                beam((sx * rh, sy * rh, z + 0.9), (sx * (rh + 1.4), sy * (rh + 1.4), z + 2.6), 0.6, (0.20, 0.24, 0.28))
        ring = [(-rh, -rh), (rh, -rh), (rh, rh), (-rh, rh)]
        for p, q in zip(ring, ring[1:] + ring[:1]):
            beam((p[0], p[1], z + 0.95), (q[0], q[1], z + 0.95), 0.3, BATTLE, acc=NEON)
        z += 2.4
    for sx in (-1, 1):  # golden roof fins
        beam((sx * 3.4, 0, z), (sx * 4.2, 0, z + 3.2), 0.8, (1.0, 0.70, 0.20), acc=NEON)
    for (p, q) in (((-25, -25), (25, -25)), ((25, 25), (-25, 25)), ((-25, 25), (-25, -25)), ((25, -25), (25, 25))):
        cwall(p, q, 1, skip=lambda x, y: x > 20 and abs(y) < 6)
    for k in range(6):  # nobori banners along the outer court
        y = -20 + k * 8
        if abs(y) < 7:
            continue
        flag(26, y, 5.2, 9, (1.0, 0.5, 0.08), side=1)
    gatehouse(25.0, courses=2, w=6.0, moat=True)


CASTLES = {"concentric": castle_concentric, "motte": castle_motte, "star": castle_star, "japan": castle_japan}


def meridian26():
    CASTLES.get(globals().get("STATE", "") or MERIDIAN_CHOICE, CASTLES[MERIDIAN_CHOICE])()


# ================================================================== SOLACE: the helix (locked form) + light show
def double_helix26():
    double_helix()
    R, z0, z1, turns, N = 13.5, 6.5, 108.0, 2.6, 160
    A, B = [], []
    for i in range(N + 1):
        t = i / N
        a = t * turns * 2 * math.pi + math.radians(-45)
        z = z0 + t * (z1 - z0)
        A.append((R * math.cos(a), R * math.sin(a), z))
        B.append((R * math.cos(a + math.pi), R * math.sin(a + math.pi), z))
    # down-lighting: a bright strip under each strand + light cones falling from its underside
    for S_, col in ((A, (0.40, 1.0, 0.75)), (B, (0.62, 1.0, 0.25))):
        under = [(x, y, z - 2.7) for (x, y, z) in S_]
        tube(under, 0.42, col, acc=NEON, n=6)
        for i in range(10, N, 26):
            x, y, z = S_[i]
            cone(Vector((x, y, z - 3.0)), Vector((x * 1.1, y * 1.1, max(0.5, z - 16))), 0.5, 3.0, tuple(c * 0.45 for c in col))
    # the spotlight at the bottom centre, pointing straight up through the helix
    cyl(0, 0, 6.5, 8.2, 2.6, (0.25, 0.30, 0.28), n=12)
    disc((0, 0, 8.25), (1, 0, 0), (0, 1, 0), 2.1, (0.85, 1.0, 0.75), acc=NEON, n=12)
    cone(Vector((0, 0, 8.3)), Vector((0, 0, 140)), 1.4, 4.5, (0.20, 0.42, 0.16))
    # chaser lights: bulbs along both strands' outer side, a band of lit bulbs climbing frame by frame
    for S_ in (A, B):
        for i in range(2, N, 2):
            x, y, z = S_[i]
            k = 1.24
            p = (x * k, y * k, z)
            box(p[0] - 0.45, p[1] - 0.45, z - 0.45, p[0] + 0.45, p[1] + 0.45, z + 0.45, (0.18, 0.30, 0.16), facet=False)
            for f in range(NFRAMES):
                if (i // 2 - f) % 12 < 3:
                    a = ANIM_ACCS[f]
                    a.face([(p[0] - 0.62, p[1] - 0.62, z + 0.5), (p[0] + 0.62, p[1] - 0.62, z + 0.5), (p[0] + 0.62, p[1] + 0.62, z + 0.5), (p[0] - 0.62, p[1] + 0.62, z + 0.5)],
                           (0.85, 1.0, 0.55), (0, 0, 0))
                    for (dx, dy) in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                        a.face([(p[0] + dx * 0.62 - dy * 0.62, p[1] + dy * 0.62 + dx * 0.62, z - 0.62), (p[0] + dx * 0.62 + dy * 0.62, p[1] + dy * 0.62 - dx * 0.62, z - 0.62),
                                (p[0] + dx * 0.62 + dy * 0.62, p[1] + dy * 0.62 - dx * 0.62, z + 0.62), (p[0] + dx * 0.62 - dy * 0.62, p[1] + dy * 0.62 + dx * 0.62, z + 0.62)],
                               (0.85, 1.0, 0.55), (0, 0, 0))


def cone(apex, base_c, r0, r1, col, n=14):
    """Translucent light cone (BEAM material) from apex (radius r0) to base_c (radius r1)."""
    d = (base_c - apex).normalized()
    u = d.cross(Vector((0, 0, 1)))
    if u.length < 1e-3:
        u = Vector((1, 0, 0))
    u.normalize()
    v = d.cross(u).normalized()
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        p0 = apex + (u * math.cos(a0) + v * math.sin(a0)) * r0
        p1 = apex + (u * math.cos(a1) + v * math.sin(a1)) * r0
        q0 = base_c + (u * math.cos(a0) + v * math.sin(a0)) * r1
        q1 = base_c + (u * math.cos(a1) + v * math.sin(a1)) * r1
        BEAM.face([tuple(p0), tuple(p1), tuple(q1), tuple(q0)], col, (0, 0, 0))


# ================================================================== HALCYON: more levels, stairs, no dish, the scanning eye
def civic_core26():
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
    for sx, sy in ((1, 0), (0, -1)):  # grand stair ramps (locked)
        for s in range(14):
            z = s * 1.3
            if sx:
                box(27 + 6 - s * 0.45, -4, 0, 27 + 6.5 - s * 0.45, 4, z + 1.3, (0.62, 0.58, 0.78), facet=False)
            else:
                box(-4, -27 - 6.5 + s * 0.45, 0, 4, -27 - 6 + s * 0.45, z + 1.3, (0.62, 0.58, 0.78), facet=False)
    box(-3.5, -3.5, 62, 3.5, 3.5, 70, (0.22, 0.18, 0.32))
    cyl(0, 0, 70, 74, 1.6, (0.22, 0.18, 0.32), n=10)
    text_obj("HALCYON CIVIC", (0, -27.2, 5.4), (math.radians(90), 0, 0), 2.6, SIGNM)
    for (x, y) in ((-24, -32), (-14, -34), (31, 14), (33, -12)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=False)
    # the eye on its own objects (it turns about the pylon axis): lids, iris, rays and its searchlight
    es, en, eb = Acc("eye_s"), Acc("eye_n"), Acc("eye_b")
    EYE_ACC.update(solid=es, neon=en, beam=eb)
    global SOLID, NEON, BEAM
    s0, n0, b0 = SOLID, NEON, BEAM
    SOLID, NEON, BEAM = es, en, eb
    try:
        box(-1.2, -1.2, 74, 1.2, 1.2, 78, (0.22, 0.18, 0.32), facet=False)
        eye((0, -2.5, 82), 14, 5.0, lid=(0.62, 0.40, 0.10))
        for k in range(7):
            a = math.radians(30 + k * 20)
            beam((15.5 * math.cos(a), -2.5, 82 + 9 * math.sin(a)), (19.5 * math.cos(a), -2.5, 82 + 12 * math.sin(a)), 0.7, (0.62, 0.40, 0.10), acc=NEON)
        cone(Vector((0, -3.2, 82)), Vector((0, -125, 0)), 3.0, 13.0, (0.42, 0.26, 0.08))
        ell = [(math.cos(2 * math.pi * j / 20) * 14, -125 + math.sin(2 * math.pi * j / 20) * 20, 0.12) for j in range(20)]
        for j in range(20):
            NEON.face([(0, -125, 0.12), ell[j], ell[(j + 1) % 20]], (0.55, 0.36, 0.10), (0, 0, 0))
    finally:
        SOLID, NEON, BEAM = s0, n0, b0
    EYE_ANGLES[:] = [-55 + 110 * (0.5 - 0.5 * math.cos(2 * math.pi * f / NFRAMES)) for f in range(NFRAMES)]


# ================================================================== ORBITAL: crescent + a silo IN the ground, sliding doors
def orbital_silo26():
    open_ = globals().get("STATE", "") == "open"
    PZ = 6.0
    plaza(27.5, CYAN, ground=(0.10, 0.12, 0.18), ring2=ICE)
    n = 48
    Ri, Ro = 12.5, 28.0
    bid = rid()
    for i in range(n):  # the launch podium: an annulus at PZ, outer wall, inner shaft wall
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        c0, s0, c1, s1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
        SOLID.face([(Ri * c0, Ri * s0, PZ), (Ro * c0, Ro * s0, PZ), (Ro * c1, Ro * s1, PZ), (Ri * c1, Ri * s1, PZ)], (0.42, 0.46, 0.52), bid)
        SOLID.face([(Ro * c0, Ro * s0, 0), (Ro * c1, Ro * s1, 0), (Ro * c1, Ro * s1, PZ), (Ro * c0, Ro * s0, PZ)], (0.36, 0.40, 0.46), bid)
        SOLID.face([(Ri * c0, Ri * s0, 0.5), (Ri * c1, Ri * s1, 0.5), (Ri * c1, Ri * s1, PZ), (Ri * c0, Ri * s0, PZ)], (0.12, 0.13, 0.16), bid)
        col = (1.0, 0.82, 0.10) if i % 2 == 0 else (0.05, 0.05, 0.05)  # yellow/black caution ring on the rim
        acc = NEON if i % 2 == 0 else SOLID
        acc.face([(Ri * c0, Ri * s0, PZ + 0.05), (14.4 * c0, 14.4 * s0, PZ + 0.05), (14.4 * c1, 14.4 * s1, PZ + 0.05), (Ri * c1, Ri * s1, PZ + 0.05)], col, (0, 0, 0))
    ring_beams((0, 0, PZ + 0.08), (1, 0, 0), (0, 1, 0), Ro - 0.6, 0.4, CYAN, n=48)
    for k in range(3):  # steps up the podium on the side facing the camera
        a = math.radians(-45)
        r = Ro + 1.5 + k * 1.6
        box(r * math.cos(a) - 4, r * math.sin(a) - 4, 0, r * math.cos(a) + 4, r * math.sin(a) + 4, PZ - (k + 1) * 1.6, (0.40, 0.44, 0.50), facet=False)
    disc((0, 0, 0.6), (1, 0, 0), (0, 1, 0), Ri, (0.02, 0.03, 0.05), acc=SOLID, n=32)  # shaft floor
    ring_beams((0, 0, 0.7), (1, 0, 0), (0, 1, 0), Ri - 0.4, 0.3, CYAN, n=32)
    # sliding doors 1.6 below the rim: two half discs; open = slid sideways into the podium (out of sight)
    zd = PZ - 1.6
    slide = 13.6 if open_ else 0.0
    for sx in (-1, 1):
        pts = [(sx * slide + sx * 0.08, -Ri + 0.15, zd)]
        for j in range(17):
            a = math.radians(-90 + 180 * j / 16) if sx > 0 else math.radians(90 + 180 * j / 16)
            pts.append((sx * slide + (Ri - 0.15) * math.cos(a), (Ri - 0.15) * math.sin(a), zd))
        pts.append((sx * slide + sx * 0.08, Ri - 0.15, zd))
        SOLID.face(pts, (0.60, 0.64, 0.70), rid())
        for u in range(-9, 10, 3):
            beam((sx * slide + sx * 0.6, u, zd + 0.1), (sx * slide + sx * (Ri - 1.0) * math.cos(math.asin(min(1, abs(u) / Ri))), u, zd + 0.1), 0.22, (0.40, 0.42, 0.48))
        if not open_:
            for y in (-8, 8):
                NEON.face([(sx * 6.5 - 0.6, y - 0.6, zd + 0.12), (sx * 6.5 + 0.6, y - 0.6, zd + 0.12), (sx * 6.5 + 0.6, y + 0.6, zd + 0.12), (sx * 6.5 - 0.6, y + 0.6, zd + 0.12)],
                          (1.0, 0.25, 0.2), (0, 0, 0))
    if not open_:
        strip(NEON, (0, -Ri + 0.2), (0, Ri - 0.2), 0.35, zd + 0.13, CYAN)
    else:
        cyl(0, 0, 0.6, 0.65, Ri - 0.5, (0.18, 0.40, 0.52), n=32, acc=NEON, facet=False)
        RZ = PZ + 8
        cyl(0, 0, 0.6, RZ, 4.4, (0.90, 0.93, 0.97), n=16)
        cyl(0, 0, RZ, RZ + 13, 4.4, (0.92, 0.95, 0.98), n=16, r1=0.3)
        for zr, cr in ((PZ + 1.5, CYAN), (PZ + 5, (1.0, 0.25, 0.2)), (RZ + 2, CYAN)):
            ring_beams((0, 0, zr), (1, 0, 0), (0, 1, 0), 4.5, 0.6, cr, n=16)
        box(-0.4, -0.4, RZ + 12.8, 0.4, 0.4, RZ + 13.8, (1.0, 0.25, 0.2), facet=False)
        NEON.face([(-0.5, -0.5, RZ + 13.9), (0.5, -0.5, RZ + 13.9), (0.5, 0.5, RZ + 13.9), (-0.5, 0.5, RZ + 13.9)], (1.0, 0.25, 0.2), (0, 0, 0))
    # the crescent (locked from round 25): mast at the back, dishes, ops wall - all on the podium
    back = math.radians(135)
    mx, my = 20 * math.cos(back), 20 * math.sin(back)
    top = 82 + PZ
    cyl(mx, my, PZ, PZ + 3, 7, ORB_WHITE, n=12)
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam((mx + sx * 5, my + sy * 5, PZ + 3), (mx + sx * 1.0, my + sy * 1.0, top), 0.9, (0.88, 0.92, 0.96))
    for z in range(int(PZ + 9), int(top - 4), 8):
        k = 1 - (z - PZ - 3) / (top - PZ - 3)
        s = 1.0 + 4.0 * k
        for (a, b) in (((-s, -s), (s, -s)), ((s, -s), (s, s)), ((s, s), (-s, s)), ((-s, s), (-s, -s))):
            beam((mx + a[0], my + a[1], z), (mx + b[0], my + b[1], z), 0.35, (0.80, 0.85, 0.92))
    for z in (PZ + 24, PZ + 44, PZ + 64):
        k = 1 - (z - PZ - 3) / (top - PZ - 3)
        ring_beams((mx, my, z), (1, 0, 0), (0, 1, 0), (1.0 + 4.0 * k) * 1.6, 0.45, CYAN, n=16)
    box(mx - 1.2, my - 1.2, top, mx + 1.2, my + 1.2, top + 2.2, (0.9, 0.95, 1.0), facet=False)
    NEON.face([(mx - 1.3, my - 1.3, top + 0.2), (mx + 1.3, my - 1.3, top + 0.2), (mx + 1.3, my - 1.3, top + 2.0), (mx - 1.3, my - 1.3, top + 2.0)], CYAN, (0, 0, 0))
    for k, (deg, big) in enumerate(((90, True), (180, True), (60, False), (210, False))):
        a = math.radians(deg)
        r = 20.5 if big else 23.5
        px, py = r * math.cos(a), r * math.sin(a)
        if big:
            cyl(px, py, PZ, PZ + 8, 2.2, (0.62, 0.66, 0.72), n=10)
            aim = Vector((-math.cos(a) * 0.35 + 0.25, -math.sin(a) * 0.35 - 0.25, 0.85))
            dish((px, py, PZ + 15), aim, 8.0, 2.6, (0.92, 0.95, 0.98), n=18, tip=CYAN)
            beam((px, py, PZ + 8), (px, py, PZ + 13), 1.4, (0.62, 0.66, 0.72))
        else:
            cyl(px, py, PZ, PZ + 3, 1.2, (0.6, 0.64, 0.7), n=8)
            dish((px, py, PZ + 5.5), (-math.cos(a) * 0.3 + 0.2, -math.sin(a) * 0.3 - 0.2, 0.85), 3.2, 1.0, (0.9, 0.93, 0.97), tip=CYAN)
    for k in range(12):
        a0 = math.radians(45 + k * 15)
        cx_, cy_ = 26 * math.cos(a0), 26 * math.sin(a0)
        box(cx_ - 2.2, cy_ - 2.2, PZ, cx_ + 2.2, cy_ + 2.2, PZ + 3.0, ORB_WHITE, facet=False)
    text_obj("ORBITAL COMMONS", (19.8, -19.8, 3.0), (math.radians(90), 0, math.radians(45)), 2.0, SIGNM)


# ================================================================== regular Sites
def hospital():
    """Solace: SOLACE GENERAL - a clinic block with wings, a lime cross, an ambulance bay and a rooftop helipad."""
    pale, wing = (0.80, 0.86, 0.84), (0.72, 0.80, 0.78)
    box(-16, 0, 0, 16, 20, 18, pale)
    windows(-16, 0, 0, 16, 20, 18, p=0.6, cols=[(0.85, 1.0, 0.85), (0.95, 1.0, 0.95), (0.6, 1.0, 0.5)])
    for sx in (-1, 1):
        box(sx * 16, -8, 0, sx * 27, 20, 11, wing)
        windows(min(sx * 16, sx * 27), -8, 0, max(sx * 16, sx * 27), 20, 11, p=0.55, cols=[(0.85, 1.0, 0.85), (0.95, 1.0, 0.95)])
        roof_trim(min(sx * 16, sx * 27), -8, max(sx * 16, sx * 27), 20, 11.1, (0.45, 1.0, 0.35), w=0.3)
    roof_trim(-16, 0, 16, 20, 18.1, (0.45, 1.0, 0.35), w=0.35)
    box(-9, -6, 4.5, 9, 0, 5.3, (0.6, 0.66, 0.64), facet=False)  # ambulance bay canopy
    strip(NEON, (-9, -6.1), (9, -6.1), 0.35, 4.6, (0.55, 1.0, 0.35))
    box(-6, -0.4, 0, 6, 0, 4.4, (0.10, 0.16, 0.12), facet=False)
    NEON.face([(-5.6, -0.5, 0.3), (5.6, -0.5, 0.3), (5.6, -0.5, 4.0), (-5.6, -0.5, 4.0)], (0.30, 0.55, 0.30), (0, 0, 0))
    box(-4, -0.9, 10, 4, -0.2, 17.6, (0.06, 0.08, 0.06), facet=False)  # the cross on the facade
    NEON.face([(-1.0, -1.0, 11), (1.0, -1.0, 11), (1.0, -1.0, 17), (-1.0, -1.0, 17)], (0.62, 1.0, 0.30), (0, 0, 0))
    NEON.face([(-3.0, -1.0, 13), (3.0, -1.0, 13), (3.0, -1.0, 15), (-3.0, -1.0, 15)], (0.62, 1.0, 0.30), (0, 0, 0))
    text_obj("SOLACE GENERAL", (0, -0.15, 7.0), (math.radians(90), 0, 0), 1.6, SIGNM)
    disc((4, 10, 18.1), (1, 0, 0), (0, 1, 0), 6.5, (0.16, 0.20, 0.18), acc=SOLID, n=20)  # helipad
    ring_beams((4, 10, 18.2), (1, 0, 0), (0, 1, 0), 6.0, 0.25, (0.55, 1.0, 0.35), n=20)
    for (x0, y0, x1, y1) in ((1.6, 7.5, 2.4, 12.5), (5.6, 7.5, 6.4, 12.5), (2.4, 9.6, 5.6, 10.4)):
        NEON.face([(x0, y0, 18.25), (x1, y0, 18.25), (x1, y1, 18.25), (x0, y1, 18.25)], (0.95, 1.0, 0.95), (0, 0, 0))
    for (x, y) in ((-5, -12), (2, -14), (9, -11)):
        vehicle(x, y, (0.86, 0.90, 0.88), stripe=(0.55, 1.0, 0.35), lights=((0.55, 1.0, 0.35), (0.9, 1, 0.9)), L=7, Wd=3, Hh=3.2)


def tv_station():
    """Orbital: OC-TV - a broadcast studio with dishes on the roof, a lattice mast, a big screen and an uplink truck."""
    box(-20, 0, 0, 12, 20, 15, ORB_WHITE)
    windows(-20, 0, 0, 12, 20, 15, p=0.5, cols=[(0.8, 0.95, 1.0), (0.4, 0.85, 1.0)])
    roof_trim(-20, 0, 12, 20, 15.1, CYAN, w=0.35)
    box(12, 4, 0, 24, 20, 9, (0.70, 0.74, 0.80))
    roof_trim(12, 4, 24, 20, 9.1, CYAN, w=0.3)
    box(-14, -0.6, 4, 6, 0, 13, (0.05, 0.06, 0.08), facet=False)  # the big screen
    NEON.face([(-13.4, -0.7, 4.5), (5.4, -0.7, 4.5), (5.4, -0.7, 12.5), (-13.4, -0.7, 12.5)], (0.20, 0.45, 0.70), (0, 0, 0))
    for k in range(5):
        NEON.face([(-12 + k * 3.4, -0.75, 6 + (k % 2) * 2.5), (-9.8 + k * 3.4, -0.75, 6 + (k % 2) * 2.5), (-9.8 + k * 3.4, -0.75, 9.5 + (k % 2) * 2.5),
                   (-12 + k * 3.4, -0.75, 9.5 + (k % 2) * 2.5)], (0.75, 0.95, 1.0), (0, 0, 0))
    text_obj("OC-TV", (-4, -0.8, 14.0), (math.radians(90), 0, 0), 1.8, SIGNM)
    for k, (x, y) in enumerate(((-15, 8), (-8, 14), (-1, 7))):  # radar dishes on the roof
        cyl(x, y, 15, 17, 1.0, (0.6, 0.64, 0.7), n=8)
        dish((x, y, 20), (0.25 - 0.2 * k, -0.5, 0.8), 3.4, 1.0, (0.92, 0.95, 0.98), tip=CYAN)
    mx, my = 7, 14
    for (dx, dy) in ((-1.6, -1.6), (1.6, -1.6), (0, 1.8)):
        beam((mx + dx, my + dy, 15), (mx, my, 52), 0.35, (0.85, 0.9, 0.95))
    for z in range(19, 50, 5):
        k = 1 - (z - 15) / 37
        pts = [(mx + dx * k, my + dy * k, z) for (dx, dy) in ((-1.6, -1.6), (1.6, -1.6), (0, 1.8))]
        for p, q in zip(pts, pts[1:] + pts[:1]):
            beam(p, q, 0.2, (0.8, 0.85, 0.92))
    for z in (30, 41, 52):
        box(mx - 0.4, my - 0.4, z, mx + 0.4, my + 0.4, z + 0.8, (1.0, 0.2, 0.15), facet=False)
        NEON.face([(mx - 0.5, my - 0.5, z + 0.85), (mx + 0.5, my - 0.5, z + 0.85), (mx + 0.5, my + 0.5, z + 0.85), (mx - 0.5, my + 0.5, z + 0.85)], (1.0, 0.2, 0.15), (0, 0, 0))
    vehicle(16, -8, (0.86, 0.9, 0.95), stripe=CYAN, L=8, Wd=3, Hh=3.2, rot90=False)
    dish((16, -8, 5.5), (0.2, -0.4, 0.9), 2.2, 0.7, (0.92, 0.95, 0.98), tip=CYAN)


def sphinx():
    """Halcyon: a civic sphinx on a plinth, the amber eye on its headdress, obelisks with amber tips."""
    st, lt = HAL_STONE, tuple(min(1, v * 1.25) for v in HAL_STONE)
    box(-16, -26, 0, 16, 20, 3, lt)  # plinth
    roof_trim(-16, -26, 16, 20, 3.05, AMBER, w=0.35)
    box(-7, -4, 3, 7, 18, 12, st)        # body
    box(-7.5, 8, 3, 7.5, 18, 14, st)    # haunches
    box(-6, -12, 3, 6, -2, 16, st)      # chest
    for sx in (-1, 1):                   # forepaws
        box(sx * 5 - 2.2, -24, 3, sx * 5 + 2.2, -9, 6, lt)
    box(-4.2, -15, 15, 4.2, -8, 24.5, lt, taper=0.4)   # head
    box(-6.2, -13, 13, 6.2, -7, 24, st, taper=1.4)    # nemes headdress
    for k in range(5):  # amber headdress stripes
        z = 14.5 + k * 1.9
        beam((-6.25, -13.05, z), (6.25, -13.05, z), 0.25, AMBER, acc=NEON)
    eye((0, -15.2, 21.2), 2.8, 1.0, w=0.4)
    beam((0, -15.25, 17), (0, -15.25, 18.2), 0.5, (0.12, 0.10, 0.16))
    for sx in (-1, 1):  # obelisks
        box(sx * 13 - 1.4, 14, 3, sx * 13 + 1.4, 17, 26, st, taper=0.9)
        box(sx * 13 - 0.6, 14.9, 26, sx * 13 + 0.6, 16.1, 28, AMBER, taper=0.6)
        NEON.face([(sx * 13 - 0.5, 14.8, 26.1), (sx * 13 + 0.5, 14.8, 26.1), (sx * 13 + 0.5, 14.8, 27.6), (sx * 13 - 0.5, 14.8, 27.6)], AMBER, (0, 0, 0))
    for (x, y) in ((-22, -18), (22, -10)):
        vehicle(x, y, (0.16, 0.13, 0.24), lights=(CRED, (0.2, 0.4, 1.0)), rot90=True)


def police_station():
    """Halcyon: the precinct (round 24) as a POLICE station - no dish, a lit POLICE sign, a red/blue roof bar."""
    global dish
    d0 = dish
    dish = lambda *a, **k: None
    try:
        precinct()
    finally:
        dish = d0
    box(-8, 0.6, 22.2, 8, 1.4, 26.2, (0.06, 0.06, 0.12), facet=False)
    text_obj("POLICE", (0, 0.5, 24.2), (math.radians(90), 0, 0), 2.6, SIGNM)
    for k in range(10):
        x = -9 + k * 2
        NEON.face([(x, 0.45, 26.4), (x + 1.6, 0.45, 26.4), (x + 1.6, 0.45, 27.2), (x, 0.45, 27.2)], CRED if k % 2 else (0.2, 0.4, 1.0), (0, 0, 0))


HEROES26 = {"meridian": meridian26, "solace": double_helix26, "halcyon": civic_core26, "orbital": orbital_silo26}
SITES26 = {("solace", ""): hospital, ("orbital", ""): tv_station, ("halcyon", ""): police_station, ("halcyon", "police"): police_station,
           ("halcyon", "sphinx"): sphinx}
ANIM_ACCS[:] = [Acc("chase%02d" % f) for f in range(NFRAMES)]
