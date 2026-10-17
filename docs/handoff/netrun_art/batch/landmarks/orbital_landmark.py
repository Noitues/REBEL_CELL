# DRAFT for the art-pass session; unverified (no render).
# provenance: model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id lm__orbital; status ok; tokens in 24036 cache-write 72279 cache-read 60175 out 21566; cost $0.228; ast.parse: parses

"""DRAFT for the art-pass session; unverified (no render).
ORBITAL COMMONS LANDMARK: THE LAUNCH COMPLEX (round podium, silo, rocket, service gantry, truss antenna, dish stations).

ENTRY POINTS
    import orbital_landmark as OL
    info = OL.build(ctx)                      # city hook: ctx from landmarks.landmark_ctx("orbital")
    hooks = OL.build(K, rooms=True, rail=False)   # HQ netrun: K = the kit namespace (see meridian_landmark.py)
    OL.build_hq(K2, rooms=False)              # same, after K2 = OL.place(K, origin=(hx, hy, 0), k=K_UNITS)
    OL.landmark_info()                        # dict(corp, central_server_name, footprint_bu, tier_heights)

    build(ctx) -> dict(label=(x, y, z), crown=(x, y, z) or None, hue=(r, g, b)); it only adds faces and lights.
    ctx attributes used: hq, footprint, district, seed, SURF, SMOOTH, NEON, GLASS, box, cyl, dome, bar, ring_line,
    annulus, sc, light_spots, CP (CP.ORBITAL_PAD).  The built-in landmarks.orbital() is the source of the rules.

WHAT IT BUILDS (spec 8.5, Orbital row; 8.6b: one model for the city and the HQ netrun)
    PODIUM   round launch platform (r 22 BU city scale), lit rim line, a stepped deck
    SILO     dark shaft in the centre, yellow-black caution ring (paint), two door leaves swung open
    ROCKET   white body, two red bands, nose, four fins; risen out of the silo (the hero)
    GANTRY   red service gantry south of the silo with the LAUNCH CONTROL deck and a red beacon
    ANTENNA  4-leg truss tower on the rim, two decks, red markers, two elite vaults at its feet
    DISHES   three dish stations on the rim
    LIGHT    no floodlit disc (designer round 3): short spot masts on the rim, each aimed at the rocket body

UNITS / PLACING
    build(ctx): world BU of the one city (1 floor = 1.9 BU), around ctx.hq.  The footprint radius (city) is
    FOOTPRINT_R_BU (22 BU podium + rim lamps, tower corner at about 23.5 BU).
    build_hq: geometry in HQ-kit units (1 storey = 8 BU) around (0, 0, 0), north = +y; use place(K, origin, k=0.2375)
    to drop it into the city (energies x k^2, sizes x k), same as the Meridian template.

SEEDS
    Streams come from ctx.seed (city) or the kit literals (HQ) via stream_seed(base, name): FNV-1a 64 over the
    UTF-8 of "base/name".  Legacy literal for golden parity: dish tilts 7320.  The city build draws no random numbers.
"""
import math
import random
from types import SimpleNamespace

# ----------------------------------------------------------------- constants (read by the pipeline checks)
CORP = "orbital"
CENTRAL_SERVER_NAME = "LAUNCH CONTROL"        # GDD 11.7 working name
K_UNITS = 0.2375
PODIUM_R_BU = 22.0
FOOTPRINT_R_BU = 24.0                          # podium r 22 + rim lamps; tower corner (17.6, 15.6) -> 23.5
ROCKET_TOP_BU = 38.0
TOWER_TOP_BU = 83.0                            # truss 74 + mast 9
GANTRY_TOP_BU = 30.8
HUE = (0.498, 0.659, 1.0)                      # fallback; the city passes its own district hue
LEGACY_SEEDS = {"dish": 7320, "strike": 7340}
_EMIT_K = 4.0


def stream_seed(base, name):
    """FNV-1a 64 of 'base/name' (documented hash, same in GDScript)."""
    h = 0xcbf29ce484222325
    for b in ("%s/%s" % (base, name)).encode("utf-8"):
        h ^= b
        h = (h * 0x100000001b3) & 0xFFFFFFFFFFFFFFFF
    return h


def landmark_info():
    return dict(corp=CORP, central_server_name=CENTRAL_SERVER_NAME, footprint_bu=FOOTPRINT_R_BU,
                tier_heights=dict(podium=6.0, gantry=GANTRY_TOP_BU, rocket=ROCKET_TOP_BU, antenna=TOWER_TOP_BU,
                                  dish_station=5.5))


# ----------------------------------------------------------------- tiny vector helpers (tuples)
def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _norm(a):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


# ================================================================== the city hook
def _build_city(ctx):
    hx, hy = ctx.hq
    D = ctx.district
    SURF, SMOOTH, NEON, GLASS = ctx.SURF, ctx.SMOOTH, ctx.NEON, ctx.GLASS
    box, cyl, dome, bar, ring_line, annulus, sc = ctx.box, ctx.cyl, ctx.dome, ctx.bar, ctx.ring_line, ctx.annulus, ctx.sc
    hue = tuple(D["hue"]) if "hue" in D else HUE
    steel = (0.48, 0.52, 0.60)
    R = PODIUM_R_BU
    cyl(SURF, hx, hy, 0, 3.4, R, 64, steel, wc=(0.8, 0.9, 1.0), wl=0.45, wm=1, bid=0.5, top=False)
    annulus(SURF, hx, hy, 3.4, 6.0, R, (0.30, 0.32, 0.38), n=64)
    ring_line(NEON, hx, hy, 3.45, R + 0.05, 0.3, D["sec"], n=64)
    # the silo: dark shaft, caution ring (paint), two open door leaves
    rs = 6.0
    cyl(SURF, hx, hy, -30.0, 3.45, rs, 32, (0.05, 0.05, 0.07), top=False)
    for k in range(24):
        t0, t1 = 2 * math.pi * k / 24, 2 * math.pi * (k + 1) / 24
        col = (0.85, 0.68, 0.10) if k % 2 == 0 else (0.06, 0.06, 0.06)
        SURF.face([(hx + rs * math.cos(t0), hy + rs * math.sin(t0), 3.46),
                   (hx + (rs + 1.6) * math.cos(t0), hy + (rs + 1.6) * math.sin(t0), 3.46),
                   (hx + (rs + 1.6) * math.cos(t1), hy + (rs + 1.6) * math.sin(t1), 3.46),
                   (hx + rs * math.cos(t1), hy + rs * math.sin(t1), 3.46)], col)
    for zz in (-6.0, -14.0):
        ring_line(NEON, hx, hy, zz, rs - 0.15, 0.3, sc((1.0, 0.4, 0.2), 0.35), n=24)
    a75 = math.radians(75)
    for side in (-1, 1):
        hxv = hx + side * (rs + 0.2)
        pts = []
        for k in range(9):
            t = math.pi * k / 8
            u = rs * math.sin(t)
            v = rs * math.cos(t)
            pts.append((hxv - side * u * math.cos(a75), hy + v, 3.5 + u * math.sin(a75)))
        SURF.face(pts, (0.62, 0.66, 0.72))
        for k in range(3):
            v = -3 + 3 * k
            bar(SURF, (hxv, hy + v, 3.5), (hxv - side * 4.5 * math.cos(a75), hy + v, 3.5 + 4.5 * math.sin(a75)),
                0.25, (0.85, 0.68, 0.1))
    # the rocket
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
    # the red service gantry south of the silo, LAUNCH CONTROL deck near the top
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
    # the truss antenna tower on the rim, two elite vaults at its feet
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
            pa = _lerp(legs[i][0], legs[i][1], t0)
            pb = _lerp(legs[j][0], legs[j][1], t1)
            pc = _lerp(legs[j][0], legs[j][1], t0)
            bar(SURF, pa, pb, 0.2, (0.62, 0.66, 0.74))
            bar(SURF, pa, pc, 0.2, (0.62, 0.66, 0.74))
    for zz in (H * 0.35, H * 0.65):
        box(SURF, tx - 3.0, ty - 3.0, zz, tx + 3.0, ty + 3.0, zz + 2.4, (0.22, 0.24, 0.30), wc=(0.8, 0.9, 1.0), wl=0.85, wm=1, bid=0.6)
    for zz in (H * 0.5, H + 0.2):
        box(NEON, tx - 0.5, ty - 0.5, zz, tx + 0.5, ty + 0.5, zz + 0.9, (1.0, 0.08, 0.06))
    bar(SURF, (tx, ty, H), (tx, ty, H + 9), 0.3, (0.7, 0.72, 0.8))
    ring_line(NEON, tx, ty, H - 5, 2.0, 0.3, D["hue"], n=12)
    for (vx, vy, vc) in ((tx - 7.5, ty + 1.0, (1.0, 0.35, 0.8)), (tx + 1.0, ty - 7.5, (0.35, 0.9, 1.0))):
        dome(GLASS, vx, vy, 3.4, 3.4, (0.8, 0.9, 1.0), n=16, rings=5)
        dome(NEON, vx, vy, 3.4, 2.4, sc(vc, 0.5), n=12, rings=4)
    # dish stations round the rim (verbatim call shapes of the built-in)
    for k in range(3):
        t = math.radians(150 + 70 * k)
        dx_, dy_ = hx + (R - 4.5) * math.cos(t), hy + (R - 4.5) * math.sin(t)
        cyl(SURF, dx_, dy_, 3.4, 5.5, 1.4, 10, steel)
        annulus(SURF, dx_, dy_, 8.0, 0.01, 3.2, (0.85, 0.88, 0.92), n=14, z1=6.0)
    # pad spot masts aimed at the rocket (no floodlit disc)
    OP = ctx.CP.ORBITAL_PAD
    for k in range(OP["n"]):
        t = 2 * math.pi * k / OP["n"] + 0.4
        mx_, my_ = hx + (R - 1.4) * math.cos(t), hy + (R - 1.4) * math.sin(t)
        mz_ = 3.4 + OP["mast_h"]
        bar(SURF, (mx_, my_, 3.4), (mx_, my_, mz_), 0.35, (0.5, 0.52, 0.58))
        aimz = OP["aim_z"][0] + (OP["aim_z"][1] - OP["aim_z"][0]) * ((k * 3) % OP["n"]) / max(1, OP["n"] - 1)
        tgt = (hx, hy, aimz)
        hd = _norm(_sub(tgt, (mx_, my_, mz_)))
        lp = _add((mx_, my_, mz_), _mul(hd, 0.7))
        box(SURF, mx_ - 0.6, my_ - 0.6, mz_ - 0.4, mx_ + 0.6, my_ + 0.6, mz_ + 0.5, (0.18, 0.19, 0.22))
        box(NEON, lp[0] - 0.35, lp[1] - 0.35, lp[2] - 0.3, lp[0] + 0.35, lp[1] + 0.35, lp[2] + 0.3, (1.0, 0.97, 0.9))
        ctx.light_spots.append(dict(loc=_add(lp, _mul(hd, 0.4)), tgt=tgt, col=(1.0, 0.97, 0.92), power=OP["power"],
                                    cone=OP["cone"], blend=OP["blend"], k=1.0))
    for k in range(32):
        t = 2 * math.pi * k / 32
        box(NEON, hx + (R + 0.4) * math.cos(t) - 0.2, hy + (R + 0.4) * math.sin(t) - 0.2, 1.6,
            hx + (R + 0.4) * math.cos(t) + 0.2, hy + (R + 0.4) * math.sin(t) + 0.2, 2.0, sc((0.75, 0.88, 1.0), OP["rim_lamp_k"]))
    return dict(label=(hx, hy, 52), crown=(tx, ty, H + 9), hue=hue)


# ================================================================== placing (for the city), as the Meridian template
class _AccProxy:
    def __init__(self, acc, f):
        self._acc, self._f = acc, f

    def face(self, pts, col, k=0.0):
        self._acc.face([self._f(p) for p in pts], col, k)

    def __getattr__(self, n):
        return getattr(self._acc, n)


def place(K, origin=(0.0, 0.0, 0.0), k=K_UNITS):
    """A copy of K whose accumulators, lights and movers are moved to origin and scaled by k.
    Helpers that take raw coordinates (box, tube, obox, oquad, seg_box) must write through the proxied accumulators;
    they do, because they call acc.face."""
    ox, oy, oz = origin

    def f(p):
        return (p[0] * k + ox, p[1] * k + oy, p[2] * k + oz)
    K2 = SimpleNamespace(**vars(K))
    K2.A = {n: _AccProxy(a, f) for n, a in K.A.items()}
    K2.Acc = lambda *a, **kw: _AccProxy(K.Acc(*a, **kw), f)

    def add_light(name, kind, loc, energy, col, aim=None, size=0.5, size_y=None, **kw):
        return K.add_light(name, kind, f(loc), energy * k * k, col, aim=None if aim is None else f(aim), size=size * k,
                           size_y=None if size_y is None else size_y * k, **kw)
    K2.add_light = add_light
    if hasattr(K, "mover"):
        def mover(name):
            mv = K.mover(name)
            return dict(mv, accs={n: _AccProxy(a, f) for n, a in mv["accs"].items()})
        K2.mover = mover
    K2.place_f = f
    return K2


# ================================================================== the HQ-netrun build (kit units)
def build_hq(K, rooms=True, rail=False):
    """Port of hq_orbital/scripts/hq_build.py (podium, silo, doors, rocket, gantry, stations, antenna, causeway, rig).
    Dropped: the launch cutscene props and hooks['apply'] (see NOTES)."""
    G, CP, pal, LH = getattr(K, "G", None), K.CP, K.pal, K.LH
    A, Acc, obox, oquad, tube, box = K.A, K.Acc, K.obox, K.oquad, K.tube, K.box
    Vector = K.Vector
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ("mv_", "prep_", "trail", "boom")}
    ICE, STEEL, CAUT, LAUNCH, MARK = pal("ice"), pal("steel"), pal("caution"), pal("launch"), pal("marker")
    HACK = (0.66, 1.0, 0.0)
    PR, PH, SR = CP["podium_r"], CP["podium_h"], CP["silo_r"]
    RR, RD, RW, RH = CP["ring_r"], CP["room_d"], CP["room_w"], CP["room_h"]
    AN, RK = CP["antenna"], CP["rocket"]
    log = K.log
    place_f = getattr(K, "place_f", None)

    def az_vec(a):
        if G is not None:
            return G.az_vec(a)
        r = math.radians(a)
        return (math.sin(r), math.cos(r))

    def ring(acc, r0, r1, z0, z1, col, k=0.0, n=72, a0=0.0, a1=360.0, top=True, inner=True, cx=0.0, cy=0.0):
        for i in range(n):
            b0 = math.radians(a0 + (a1 - a0) * i / n)
            b1 = math.radians(a0 + (a1 - a0) * (i + 1) / n)
            o0, o1 = (cx + math.sin(b0) * r1, cy + math.cos(b0) * r1), (cx + math.sin(b1) * r1, cy + math.cos(b1) * r1)
            i0, i1 = (cx + math.sin(b0) * r0, cy + math.cos(b0) * r0), (cx + math.sin(b1) * r0, cy + math.cos(b1) * r0)
            acc.face([(o0[0], o0[1], z0), (o1[0], o1[1], z0), (o1[0], o1[1], z1), (o0[0], o0[1], z1)], col, k)
            if inner and r0 > 0:
                acc.face([(i1[0], i1[1], z0), (i0[0], i0[1], z0), (i0[0], i0[1], z1), (i1[0], i1[1], z1)], col, k)
            if top:
                acc.face([(i0[0], i0[1], z1), (o0[0], o0[1], z1), (o1[0], o1[1], z1), (i1[0], i1[1], z1)], col, k)

    # ---- podium + silo (dark pad, painted marks)
    PAINT = Acc("pad_paint", K.M["rough"], 1, K.COLL["compound"])
    hooks["accs"]["pad_paint"] = PAINT
    WP, YP = (0.62, 0.63, 0.62), (0.55, 0.36, 0.02)
    ring(A["civic"], SR, PR, 0.0, PH, STEEL)
    ring(A["ground"], SR + 3.0, PR - 1.5, PH, PH + 0.02, LH["pad_albedo"], k=1.0, inner=False)
    ring(A["trim"], PR + 0.02, PR + 0.1, PH - 0.7, PH - 0.4, ICE, LH["trim_k"])
    ring(A["trim"], PR + 0.02, PR + 0.1, 0.4, 0.6, ICE, LH["trim_k"] * 0.5)
    for k in range(36):
        ring(PAINT, SR, SR + 2.6, PH, PH + 0.05, YP if k % 2 == 0 else (0.015, 0.015, 0.015), 0.0, n=2, a0=k * 10.0,
             a1=(k + 1) * 10.0, inner=False)
    ring(PAINT, SR + 6.0, SR + 7.0, PH + 0.02, PH + 0.05, WP, inner=False)
    ring(PAINT, PR - 7.0, PR - 6.2, PH + 0.02, PH + 0.05, WP, inner=False)
    for a in (0.0, 90.0, 180.0, 270.0):
        v = az_vec(a)
        if abs(v[0]) > 0.5:
            continue
        r0, r1 = SR + 8.5, PR - 8.5
        box(PAINT, min(v[0] * r0, v[0] * r1) - 0.6, min(v[1] * r0, v[1] * r1), PH + 0.02,
            max(v[0] * r0, v[0] * r1) + 0.6, max(v[1] * r0, v[1] * r1), PH + 0.05, WP)
    for k in range(4):
        v = az_vec(45.0 + 90.0 * k)
        for q in range(3):
            r_ = PR - 14.0 - q * 5.0
            c_ = (v[0] * r_, v[1] * r_)
            tv = (-v[1], v[0])
            for sgn in (-1, 1):
                p0 = (c_[0] + tv[0] * sgn * 3.0, c_[1] + tv[1] * sgn * 3.0)
                p1 = (c_[0] - v[0] * 2.4, c_[1] - v[1] * 2.4)
                K.seg_box(PAINT, Vector((p0[0], p0[1], PH + 0.05)), Vector((p1[0], p1[1], PH + 0.05)), 0.9, 0.03, YP)
    STEN = {"L": ["100", "100", "100", "100", "111"], "C": ["111", "100", "100", "100", "111"],
            "-": ["000", "000", "111", "000", "000"], "1": ["010", "110", "010", "010", "111"]}
    cell = 1.6
    xw = -((3 + 1) * 4 - 1) * cell / 2
    for ch in "LC-1":
        for row, bits in enumerate(STEN[ch]):
            for cix, bit in enumerate(bits):
                if bit == "1":
                    x0_ = xw + cix * cell
                    y0_ = -(SR + 13.0) - row * cell
                    box(PAINT, x0_, y0_ - cell * 0.9, PH + 0.02, x0_ + cell * 0.9, y0_, PH + 0.05, WP)
        xw += 4 * cell
    for sx_ in (-1, 1):
        for yy in (-(SR + 1.0), (SR + 1.0)):
            box(A["metal"], sx_ * (SR + 1.0) if sx_ > 0 else -(2 * SR + 4.0), yy - 0.5, PH,
                sx_ * (2 * SR + 4.0) if sx_ > 0 else -(SR + 1.0), yy + 0.5, PH + 0.6, (0.2, 0.21, 0.23))
        box(A["civic"], sx_ * (2 * SR + 4.0) - 1.2, -(SR + 2.5), PH, sx_ * (2 * SR + 4.0) + 1.2, SR + 2.5, PH + 2.4, STEEL)
    SHG = Acc("prep_shaft", K.M["emit"], 1, K.COLL["compound"])
    hooks["accs"]["prep_shaft"] = SHG
    for zz in (1.0, 3.5, 6.0, 8.5):
        ring(SHG, SR - 0.1, SR, zz, zz + 0.4, LAUNCH, 3.0, top=False, inner=True)
    ring(A["rough"], 0.0, SR, -0.5, 0.0, (0.05, 0.05, 0.05), inner=False)
    LKR = Acc("prep_lock_red", K.M["emit"], 1, K.COLL["compound"])
    LKG = Acc("prep_lock_open", K.M["emit"], 1, K.COLL["compound"])
    hooks["accs"]["prep_lock_red"] = LKR
    hooks["accs"]["prep_lock_open"] = LKG
    for k in range(12):
        v = az_vec(15.0 + 30.0 * k)
        r_ = SR + 3.6
        box(LKR, v[0] * r_ - 0.5, v[1] * r_ - 0.5, PH + 0.05, v[0] * r_ + 0.5, v[1] * r_ + 0.5, PH + 0.9, MARK, LH["marker_k"])
        box(LKG, v[0] * r_ - 0.5, v[1] * r_ - 0.5, PH + 0.05, v[0] * r_ + 0.5, v[1] * r_ + 0.5, PH + 0.9, (0.6, 1.0, 0.7),
            LH["marker_k"] * 0.7)
    K.add_light("shaft", "POINT", (0.0, 0.0, 1.5), LH["shaft_w"], LAUNCH, size=6.0, group="mech", shadow=False)
    K.add_light("shaft_beam", "SPOT", (0.0, 0.0, 0.5), LH["shaft_beam_w"], LAUNCH, aim=(0.0, 0.0, 300.0), size=0.0,
                spot=9.0, blend=0.4, group="mech", shadow=False, receivers=K.COLL["media"])
    log("orbital podium")

    # ---- doors (movers)
    for name, s_ in (("door_e", 1), ("door_w", -1)):
        mv = K.mover(name)
        x0, x1 = (0.0, SR + 1.5) if s_ > 0 else (-(SR + 1.5), 0.0)
        box(mv["accs"]["struct"], x0, -(SR + 1.5), PH - 0.6, x1, SR + 1.5, PH + 0.6, LH["door_albedo"])
        for q in range(-4, 5):
            box(mv["accs"]["metal"], x0 + 0.5 if s_ > 0 else x0, q * 3.6 - 0.2, PH + 0.6, x1 if s_ > 0 else x1 - 0.5,
                q * 3.6 + 0.2, PH + 0.8, (0.2, 0.21, 0.23))
        for q in range(-2, 3):
            yc = q * 6.4
            for sgn in (-1, 1):
                K.seg_box(mv["accs"]["rough"], Vector((s_ * (SR - 1.0), yc + sgn * 2.4, PH + 0.82)),
                          Vector((s_ * 3.0, yc, PH + 0.82)), 1.1, 0.02, (0.55, 0.36, 0.02))
        box(mv["accs"]["metal"], s_ * (SR + 0.3) - 0.8, -(SR + 1.5), PH + 0.6, s_ * (SR + 0.3) + 0.8, SR + 1.5, PH + 1.8,
            (0.18, 0.19, 0.21))
        xs = 0.15 if s_ > 0 else -0.15
        box(mv["accs"]["trim"], min(0.0, xs), -(SR + 1.0), PH + 0.81, max(0.0, xs), SR + 1.0, PH + 0.9, ICE, 1.5)

    # ---- the rocket (mover) with three hack bands
    ms = K.mover("rocket")
    rr_, rh = RK["r"], RK["h"]
    tube(ms["accs"]["struct"], (0, 0, 0.0), (0, 0, rh), rr_, (0.62, 0.64, 0.66), n=32)
    for zz in (rh * 0.12, rh * 0.62):
        tube(ms["accs"]["rough"], (0, 0, zz), (0, 0, zz + 2.4), rr_ + 0.05, (0.5, 0.04, 0.03), n=32)
    for k in range(12):
        r0, r1 = rr_ * (1 - k / 12) ** 0.7, rr_ * (1 - (k + 1) / 12) ** 0.7
        z0, z1 = rh + k * 1.6, rh + (k + 1) * 1.6
        for j in range(32):
            a0, a1 = 2 * math.pi * j / 32, 2 * math.pi * (j + 1) / 32
            ms["accs"]["struct"].face([(r0 * math.cos(a0), r0 * math.sin(a0), z0), (r0 * math.cos(a1), r0 * math.sin(a1), z0),
                                       (r1 * math.cos(a1), r1 * math.sin(a1), z1), (r1 * math.cos(a0), r1 * math.sin(a0), z1)],
                                      (0.62, 0.64, 0.66))
    for k in range(4):
        a = math.radians(45 + 90 * k)
        box(ms["accs"]["rough"], math.cos(a) * rr_ - 0.4, math.sin(a) * rr_ - 0.4, 0.0, math.cos(a) * (rr_ + 4.0) + 0.4,
            math.sin(a) * (rr_ + 4.0) + 0.4, 9.0, (0.5, 0.04, 0.03))
    box(ms["accs"]["small"], -0.5, -0.5, rh + 19.2, 0.5, 0.5, rh + 20.2, MARK, 20.0)
    for b in range(3):
        acc = Acc("band_%d" % b, K.M["emit"], 6, K.COLL["movers"])
        zb = rh * (0.30 + 0.18 * b)
        for j in range(10):
            a0, a1 = 2 * math.pi * (j + 0.1) / 10, 2 * math.pi * (j + 0.8) / 10
            for (za, zz) in ((zb, zb + 2.2), (zb + 2.8, zb + 3.6)):
                acc.face([(math.cos(a0) * (rr_ + 0.06), math.sin(a0) * (rr_ + 0.06), za),
                          (math.cos(a1) * (rr_ + 0.06), math.sin(a1) * (rr_ + 0.06), za),
                          (math.cos(a1) * (rr_ + 0.06), math.sin(a1) * (rr_ + 0.06), zz),
                          (math.cos(a0) * (rr_ + 0.06), math.sin(a0) * (rr_ + 0.06), zz)],
                         HACK if (za == zb) else (1.0, 0.1, 0.06), 6.0)
        hooks["accs"]["band_%d" % b] = acc
    svc = K.add_light("rocket_svc", "SPOT", (rr_ + 14.0, -rr_ - 14.0, 10.0), LH["svc_w"], ICE, aim=(0.0, 0.0, 40.0),
                      size=1.5, spot=40, blend=0.6, group="mech")
    hooks["mover_lights"]["rocket"] = [(svc, (rr_ + 14.0, -rr_ - 14.0, 10.0))]
    log("orbital doors, rocket")

    # ---- gantry + LAUNCH CONTROL (the TARGET; the slot "srv")
    gy = CP["control"]["y"]
    RG = (0.5, 0.06, 0.04)
    for (dx, dy) in ((-4, -4), (4, -4), (4, 4), (-4, 4)):
        tube(A["metal"], (dx, gy + dy, PH), (dx, gy + dy, PH + 70.0), 0.5, RG, n=5)
    z = PH
    while z < PH + 70:
        box(A["metal"], -4.3, gy - 4.3, z, 4.3, gy + 4.3, z + 0.5, RG)
        for (a0, b0, a1, b1) in ((-4, -4, 4, -4), (4, -4, 4, 4), (4, 4, -4, 4), (-4, 4, -4, -4)):
            tube(A["metal"], (a0, gy + b0, z), (a1, gy + b1, z + 7.0), 0.16, RG, n=4)
            tube(A["metal"], (a1, gy + b1, z), (a0, gy + b0, z + 7.0), 0.16, RG, n=4)
        z += 7.0
    for (dx, dy) in ((-4.6, -4.6), (4.6, -4.6)):
        box(A["trim"], dx - 0.1, gy + dy - 0.1, PH, dx + 0.1, gy + dy + 0.1, PH + 70.0, ICE, LH["trim_k"] * 0.6)
    for zz in (PH + 22.0, PH + 44.0, PH + 64.0):
        box(A["metal"], -1.0, gy + 4.0, zz, 1.0, -RK["r"] - 1.5, zz + 1.2, RG)
        box(A["small"], -0.4, gy + 4.0, zz + 1.2, 0.4, -RK["r"] - 1.5, zz + 1.4, MARK, 3.0)
    so_z = G.ROOM["srv"]["o"][2] if G is not None and "srv" in G.ROOM else PH + 55.0
    box(A["civic"], -9.0, gy - 7.0, so_z - 1.0, 9.0, gy + 7.0, so_z, STEEL)
    box(A["glass"], -8.5, gy - 6.5, so_z, 8.5, gy + 6.5, so_z + 8.0, (0.02, 0.04, 0.06))
    box(A["civic"], -9.0, gy - 7.0, so_z + 8.0, 9.0, gy + 7.0, so_z + 9.0, STEEL)
    emv = K.ROOM_EMIT.setdefault("srv", Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"])) if hasattr(K, "ROOM_EMIT") else A["small"]
    for k in range(6):
        box(emv, -7.0 + k * 2.5, gy - 3.0, so_z + 1.0, -5.6 + k * 2.5, gy - 2.0, so_z + 3.4, (1.0, 0.22, 0.08), 5.0)
    box(A["trim"], -9.05, gy - 7.05, so_z + 8.2, 9.05, gy - 6.95, so_z + 8.8, ICE, 3.0)
    for k in range(8):
        box(A["small"], -0.4, gy - 0.4, PH + 70.0 + k * 0.01, 0.4, gy + 0.4, PH + 71.0, MARK, LH["marker_k"])
    log("orbital gantry")

    # ---- stations (slots come from the game graph via G.STATION; none when rooms is False)
    dr = random.Random(stream_seed(LEGACY_SEEDS["dish"], "dish"))
    if rooms and G is not None:
        for nid, a in sorted(G.STATION.items(), key=lambda kv: G.ORDER[kv[0]]):
            rec = G.ROOM[nid]
            v = az_vec(a)
            K.room_shell(nid, rec, kind="router" if nid == "start" else None)
            blk = dict(o=(v[0] * (RR + RD), v[1] * (RR + RD), 0.0), n=v)
            obox(A["civic"], blk, -RW / 2 - 6.0, -RW / 2 - 0.3, -RD - 4.0, 0.0, 0.0, RH + 3.0, STEEL)
            obox(A["civic"], blk, RW / 2 + 0.3, RW / 2 + 6.0, -RD - 4.0, 0.0, 0.0, RH + 3.0, STEEL)
            obox(A["civic"], blk, -RW / 2 - 6.0, RW / 2 + 6.0, -RD - 4.0, -RD - 0.3, 0.0, RH + 3.0, STEEL)
            obox(A["civic"], blk, -RW / 2 - 6.0, RW / 2 + 6.0, -RD - 4.0, 0.0, RH + 0.3, RH + 3.0, STEEL)
            oquad(A["trim"], blk, 0.05, -RW / 2 - 6.0, RH + 2.6, RW / 2 + 6.0, RH + 2.9, ICE, LH["trim_k"])
            K.add_light("work_%s" % nid, "SPOT", K.rf(blk, 22.0, 0.0, 2.0), LH["flood_w"] * 0.5, ICE,
                        aim=K.rf(blk, 0.0, 0.0, RH * 0.6), size=1.0, spot=70, blend=0.8, group="corp")
            top = RH + 3.0
            c = K.rf(blk, -RD / 2 - 2.0, 0.0, top)
            if nid != "start":
                ped = top + 6.0
                tube(A["metal"], (c[0], c[1], top), (c[0], c[1], ped), 1.4, (0.32, 0.34, 0.37), n=8)
                tilt = math.radians(dr.uniform(35, 55))
                dvec = Vector((v[0] * math.cos(tilt), v[1] * math.cos(tilt), math.sin(tilt)))
                up = Vector((0, 0, 1)).cross(dvec)
                up = up.normalized() if up.length > 1e-4 else Vector((1, 0, 0))
                w2 = dvec.cross(up).normalized()
                centre = Vector((c[0], c[1], ped + 4.0))
                Rd, depth = 11.0, 3.0
                for j in range(48):
                    a0, a1 = 2 * math.pi * j / 48, 2 * math.pi * (j + 1) / 48
                    p0 = centre + up * (Rd * math.cos(a0)) + w2 * (Rd * math.sin(a0)) + dvec * depth
                    p1 = centre + up * (Rd * math.cos(a1)) + w2 * (Rd * math.sin(a1)) + dvec * depth
                    tube(A["trim"], p0, p1, 0.18, ICE, LH["dish_k"], n=4)
                tube(A["metal"], centre, centre + dvec * 9.0, 0.25, (0.4, 0.4, 0.42), n=4)
    log("orbital stations")

    # ---- the antenna tower (truss, decks, markers; rooms from the graph)
    av = az_vec(AN["az"])
    tx, ty = av[0] * AN["r"], av[1] * AN["r"]
    hf, H = AN["half"], AN["h"]
    TR = (0.42, 0.44, 0.48)
    for (dx, dy) in ((-hf, -hf), (hf, -hf), (hf, hf), (-hf, hf)):
        tube(A["metal"], (tx + dx, ty + dy, 0.0), (tx + dx * 0.45, ty + dy * 0.45, H), 0.55, TR, n=6)
    z = 0.0
    while z < H - 8:
        f0 = 1 - z / H * 0.55
        f1 = 1 - (z + 8) / H * 0.55
        for (a0, b0, a1, b1) in ((-1, -1, 1, -1), (1, -1, 1, 1), (1, 1, -1, 1), (-1, 1, -1, -1)):
            tube(A["metal"], (tx + a0 * hf * f0, ty + b0 * hf * f0, z), (tx + a1 * hf * f1, ty + b1 * hf * f1, z + 8), 0.18, TR, n=4)
            tube(A["metal"], (tx + a1 * hf * f0, ty + b1 * hf * f0, z), (tx + a0 * hf * f1, ty + b0 * hf * f1, z + 8), 0.18, TR, n=4)
        z += 8.0
    for dz in AN["decks"]:
        ex = hf * (1 - dz / H * 0.55) + 6.0
        box(A["metal"], tx - ex, ty - ex, dz - 0.6, tx + ex, ty + ex, dz, (0.3, 0.32, 0.35))
        for (x0, y0, x1, y1) in ((tx - ex, ty - ex, tx + ex, ty - ex + 0.2), (tx - ex, ty + ex - 0.2, tx + ex, ty + ex),
                                 (tx - ex, ty - ex, tx - ex + 0.2, ty + ex), (tx + ex - 0.2, ty - ex, tx + ex, ty + ex)):
            box(A["trim"], x0, y0, dz + 1.0, x1, y1, dz + 1.15, ICE, 2.0)
        if dz == AN["decks"][-1]:
            for k in range(4):
                v2 = az_vec(45 + 90 * k)
                cpt = Vector((tx + v2[0] * (ex - 2), ty + v2[1] * (ex - 2), dz + 4.0))
                up_ = Vector((-v2[1], v2[0], 0.0))
                for j in range(24):
                    a0, a1 = 2 * math.pi * j / 24, 2 * math.pi * (j + 1) / 24
                    p0 = cpt + up_ * (3.5 * math.cos(a0)) + Vector((0, 0, 3.5 * math.sin(a0)))
                    p1 = cpt + up_ * (3.5 * math.cos(a1)) + Vector((0, 0, 3.5 * math.sin(a1)))
                    tube(A["trim"], p0, p1, 0.12, ICE, LH["dish_k"], n=4)
    tube(A["metal"], (tx, ty, H), (tx, ty, H + 26.0), 0.3, TR, n=5)
    for zz in (30.0, 60.0, H, H + 26.0):
        box(A["small"], tx - 0.8, ty - 0.8, zz, tx + 0.8, ty + 0.8, zz + 1.2, MARK, LH["marker_k"] * 1.5)
    if rooms and G is not None:
        for (nid, zr) in AN["rooms"]:
            rec = G.ROOM[nid]
            K.room_shell(nid, rec)
            oz = rec["o"][2]
            obox(A["civic"], rec, -RW / 2 - 1.0, RW / 2 + 1.0, -RD - 1.0, 0.4, oz - 1.0, oz - 0.4, STEEL)
            obox(A["civic"], rec, -RW / 2 - 1.0, RW / 2 + 1.0, -RD - 1.0, 0.4, oz + RH + 0.3, oz + RH + 1.3, STEEL)
            for s_ in (-1, 1):
                obox(A["civic"], rec, s_ * (RW / 2 + 0.5) - 0.5, s_ * (RW / 2 + 0.5) + 0.5, -RD - 1.0, 0.4, oz - 0.4, oz + RH + 0.3, STEEL)
            oquad(A["trim"], rec, 0.45, -RW / 2 - 1.0, oz + RH + 1.0, RW / 2 + 1.0, oz + RH + 1.3, MARK, 3.0)
            oquad(A["trim"], rec, 0.45, -RW / 2 - 1.0, oz - 1.0, RW / 2 + 1.0, oz - 0.7, MARK, 3.0)
    for (dz, side) in ((0.0, 1), (26.0, -1)):
        x0 = tx + side * (hf + 2.0)
        for s in range(12):
            za = dz + 26.0 * s / 12
            box(A["metal"], x0 - 1.0, ty + hf + 1.0 - 2 * hf * s / 12, za, x0 + 1.0, ty + hf - 2 * hf * (s + 1) / 12 + 1.0,
                za + 0.3, (0.32, 0.34, 0.36))
    K.add_light("ant_key", "SPOT", (tx, ty + 60.0, 4.0), LH["key_w"], ICE, aim=(tx, ty, 50.0), size=1.5, spot=34,
                blend=0.5, group="corp")
    K.add_light("ant_red", "POINT", (tx, ty, H + 8.0), 6000.0, MARK, size=1.0, group="corp", shadow=False)
    log("orbital antenna")

    # ---- causeway ring (needs G.RL / G.GROUND_Z); skipped when the city places it (rooms False)
    if rooms and G is not None:
        zc = G.GROUND_Z
        n = 120
        for k in range(n):
            p0, p1 = az_vec(360.0 * k / n), az_vec(360.0 * (k + 1) / n)
            K.seg_box(A["metal"], Vector((p0[0] * G.RL, p0[1] * G.RL, zc + 0.05)), Vector((p1[0] * G.RL, p1[1] * G.RL, zc + 0.05)),
                      3.0, 0.4, (0.3, 0.32, 0.35))
        for a in (150.0, 330.0, 210.0, 30.0, 90.0, 270.0):
            v = az_vec(a)
            K.seg_box(A["metal"], Vector((v[0] * PR, v[1] * PR, PH)), Vector((v[0] * (G.RL - 2), v[1] * (G.RL - 2), zc + 0.05)),
                      3.0, 0.4, (0.3, 0.32, 0.35))
    # ---- the landmark rig: pad flood masts + the hero beams (rim lights omitted: they need a receivers collection)
    for k in range(6):
        v = az_vec(30.0 + 60.0 * k)
        p = (v[0] * (PR + 6), v[1] * (PR + 6), 24.0)
        tube(A["metal"], (p[0], p[1], 0.0), p, 0.4, (0.2, 0.2, 0.22), n=5)
        box(A["trim"], p[0] - 1.5, p[1] - 1.5, p[2] - 0.6, p[0] + 1.5, p[1] + 1.5, p[2], ICE, 6.0)
        K.add_light("pad_flood_%d" % k, "SPOT", p, LH["pad_flood_w"], ICE, aim=(0.0, 0.0, PH + 10.0), size=1.5, spot=48,
                    blend=0.6, group="corp")
        if k % 2 == 0:
            o_ = (p[0], p[1], p[2] + 0.5)
            hooks["beams"].append((place_f(o_) if place_f else o_, (v[0] * 0.25, v[1] * 0.25, 1.0), ICE,
                                   K.HZ["beams"]["power"], K.HZ["beams"]["cone"]))
    log("orbital rig")
    return hooks


def build(K, rooms=True, rail=False):
    """City: build(ctx) -> dict(label, crown, hue).  HQ kit: build(K, rooms, rail) -> hooks."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return _build_city(K)
    return build_hq(K, rooms, rail)
