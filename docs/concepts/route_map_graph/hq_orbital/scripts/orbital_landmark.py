"""ORBITAL COMMONS LANDMARK: THE LAUNCH COMPLEX (round podium, silo, rocket, service gantry, truss antenna, dish stations).

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

STATUS (queue item 4, art-pass): the city build is verified face-for-face against landmarks.py (city_all_corps) through
the CITY_LM_OVERRIDE / CITY_LM_DUMP hooks; module_check.jpg shows built-in vs module. place() and the primitives come
from route_map_graph/lm_common.py. ENTRY (below) is the HQ entry anchor, BU relative to the HQ lot CENTRE, x east,
y north, z above ground: {"entry": [x, y, z], "entry_nrm": [nx, ny]} (the outward normal of the door face).
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..")))
from lm_common import K_UNITS, kit_ctx, place  # noqa: E402,F401  the shared helpers (one copy: lm_common.py)

import math
import random

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
def build(K, rooms=True, rail=False):
    """City: build(ctx) -> dict(label, crown, hue).  HQ kit: build(K, rooms, rail) -> hooks."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return _build_city(K)
    return build_hq(K, rooms, rail)


# the ground lobby: the LAUNCH CONTROL gantry foot (gantry centre y -10.5, half 3.2) on the podium deck, south face
ENTRY = {"entry": [0.0, -13.7, 3.4], "entry_nrm": [0.0, -1.0]}


def _hq_module(fname, tag):
    """The HQ-kit builder next to this file (hq_build.py), loaded by path under a unique name (the HQ dirs each have an
    hq_build.py). It is the shared kit source: nothing is copied here."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("%s_%s" % (tag, fname[:-3]), os.path.join(_HERE, fname))
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, _HERE)
    try:
        spec.loader.exec_module(mod)
    finally:
        sys.path.remove(_HERE)
    return mod


def build_hq(K, rooms=True, rail=False):
    """HQ scale (spec 8.5): the HQ-kit build in kit units (1 storey = 8 BU) around (0, 0, 0): hq_build.build(K) -> hooks.
    K is the HQ scene's helper namespace (hq_scene); wrap it with place(K, origin, K_UNITS) to drop it into the city."""
    return _hq_module("hq_build.py", "orbital").build(K)
