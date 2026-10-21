"""Solace district kit for the HQ v5 plates (park, 3-tier plinth, A/B/C bundles, the C hospital), as a module.

Derived from solace_vertical/district/scripts/sd_main.py (round 5, --park 1 --plinth 1; that file is untouched) by
make_sd_kit.py: no scene / world / lights / camera / helix / render. Everything is built in the district's own units and
scaled when the meshes are made: the lawn, bundles, hospital, trees and paths by SL, the plinth by SPL (HQ BU).
build(coll) -> dict(objs, lights). Lights are returned as specs for hq_scene.add_light.
"""
import math
import os
import random
import sys
import time

import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import sd_lib as L  # noqa: E402
from sd_lib import MB, box, cyl, dome, lathe, sphere, torus, prism, rect, sweep, seg_tube, strip, disc, flat_poly, cross_shape  # noqa: E402

# ---- v5 layout numbers (the district's units unless noted)
SL = 1.5                 # lawn / kit / hospital / tree scale (district unit -> HQ BU)
SPL = 3.0                # plinth scale (district plinth r 35 / 29.5 / 24 -> 105 / 88.5 / 72 BU)
HK = 1.8                 # extra height on the bundle towers
RB_AMP = float(os.environ.get("HQ_RB_AMP", 1.0))  # HQ port: scales the boundary wobble
RB0 = float(os.environ.get("HQ_RB0", 195.0))              # park boundary radius (district units; x SL = BU), +-25 / 15 wobble
HOSP_CELL = (0, -7)      # the hospital's lower-left lot (i, j); its centre is (i + 1, j + 1) * PITCH
CROSS_ANG = -33.0        # degrees: the standing cross faces the overview camera (yaw 110 looks along +x, -y)
PL_FOOT = 36.0           # the plinth's stair feet in plinth units
TIER_H = 3.3             # top of the plinth in plinth units (x SPL = the helix' PODIUM_H)

DIR, MODE, SEED = "D", "night", 7
CEL, DAYV, RAID, PARK, PLINTH, N2 = False, False, False, True, True, True
A = {"bdk": "1.0"}
L.Z_FLAT = False
L.DAY = False
L.CEL_S = 1.0
L.EMIT_K = 0.35


def ekw(v):
    return {"ek": v} if N2 else {}


LIME = (0.588, 1.0, 0.275)
PINKC = (1.0, 0.275, 0.588)
GL1 = (0.55, 1.0, 0.45, 1)
TWC = "twC"
BEAM = False
D = True
GLASSC = (0.04, 0.20, 0.11)
PITCH = 24.0
LOT = 16.0
GRID = 9
PL_R = PL_FOOT * SPL / SL          # the plinth's foot in lawn units (72)
PARK_R = 118.0                     # the park ring (features, ponds) out to here; kits beyond
HX, HY = (HOSP_CELL[0] + 1) * PITCH, (HOSP_CELL[1] + 1) * PITCH

NI = 2.0 if not CEL else 1.0


def mats():
    M = {}
    bands = (0.30, 0.58, 0.95, 0.20, 0.50)
    if CEL and RAID and not DAYV:
        bands = (0.14, 0.30, 0.56, 0.20, 0.50)
    if CEL and DAYV:
        _k = float(A["bdk"])
        bands = (tuple(c * _k for c in (0.52, 0.58, 0.90)), tuple(c * _k for c in (0.88, 0.82, 0.70)), tuple(c * _k for c in (1.12, 1.05, 0.92)), 0.22, 0.55)
    s = 6.0 if not CEL else 1.0
    if DIR in ("A", "D"):
        M["tw"] = L.make_material("tw", "win", MODE, cw=7.0, ch=2.6, win=(0.0, 1.0, 0.30, 0.66), strength=2.4, rough=0.22, metal=0.25, bands=bands, coat=0.5)
        M["tw2"] = L.make_material("tw2", "win", MODE, cw=3.2, ch=3.2, win=(0.22, 0.78, 0.22, 0.78), strength=2.2, rough=0.3, bands=bands)
    elif DIR == "B":
        M["tw"] = L.make_material("tw", "win", MODE, cw=3.0, ch=3.0, win=(0.2, 0.8, 0.22, 0.78), strength=2.0, rough=0.3, bands=bands)
        M["tw2"] = M["tw"]
    else:
        M["tw"] = L.make_material("tw", "win", MODE, cw=100.0, ch=3.6, win=(0.0, 1.0, 0.18, 0.58), strength=1.4, rough=0.18, metal=0.0, bands=bands, coat=0.9)
        M["tw2"] = L.make_material("tw2", "win", MODE, cw=2.6, ch=3.6, win=(0.18, 0.82, 0.2, 0.8), strength=1.3, rough=0.3, bands=bands, coat=0.7)
    if DIR == "D":
        M["twC"] = L.make_material("twC", "win", MODE, cw=100.0, ch=3.6, win=(0.0, 1.0, 0.18, 0.58), strength=1.4, rough=0.18, metal=0.0, bands=bands, coat=0.9)
    M["plain"] = L.make_material("plain", "win", MODE, plain=True, rough=0.25, metal=0.0, bands=bands, coat=0.8 if DIR == "C" else (0.5 if DIR == "D" else 0.2))
    M["tube"] = L.make_material("tube", "win", MODE, plain=True, rough=0.2, coat=0.8, bands=bands, glow=((0.40, 0.95, 0.18), 0.55, 1.7), **ekw(0.6))
    M["ord"] = L.make_material("ord", "win", MODE, cw=3.4, ch=3.8, win=(0.2, 0.75, 0.25, 0.7), strength=1.5, rough=0.45, bands=bands, **ekw(0.55))
    M["ordr"] = L.make_material("ordr", "win", MODE, cw=2.6, ch=3.0, win=(0.22, 0.78, 0.2, 0.7), strength=1.5, rough=0.45, bands=bands, **ekw(0.55))
    M["glass"] = L.make_material("glass", "glass", MODE, strength=0.9, alpha=0.74, trans=0.92, bands=bands)
    M["glassB"] = L.make_material("glassB", "glass", MODE, strength=0.5, alpha=0.5, trans=0.97, bands=bands, cel_strength=0.3)
    M["glassb"] = L.make_material("glassb", "glass", MODE, strength=0.5, alpha=0.5, trans=0.97, bands=bands)
    M["neon"] = L.make_material("neon", "neon", MODE, strength=5.0 if not CEL else (0.45 if DAYV else 1.0))
    M["neon_p"] = L.make_material("neon_p", "neon", MODE, strength=34.0 if not CEL else 1.0, **ekw(0.07))
    M["neon_x"] = L.make_material("neon_x", "neon", MODE, strength=14.0 if not CEL else 1.0, **({"ek": 0.4} if (DAYV and MODE == "night") else ekw(0.3)))
    M["water"] = L.make_material("water", "water", MODE, bands=bands)
    M["stone"] = L.make_material("stone", "win", MODE, plain=True, rough=0.62, metal=0.0, bands=bands, coat=0.0)
    M["neon_l"] = L.make_material("neon_l", "neon", MODE, strength=5.0 if not CEL else 1.0, **ekw(0.16))
    M["neon_s"] = L.make_material("neon_s", "neon", MODE, strength=9.0 if not CEL else 1.0, **ekw(0.3))
    M["ground"] = L.make_material("ground", "ground", MODE, bands=bands)
    M["hwin"] = L.make_material("hwin", "hwin", MODE, strength=3.0, **ekw(0.55))
    M["hwin_n"] = L.make_material("hwin_n", "hwin", MODE, strength=11.0, **ekw(0.55))
    return M


M = None
BUILD = {}
SCOPE = "lawn"


def mb(key, smooth=False):
    k = (SCOPE, key, smooth)
    if k not in BUILD:
        BUILD[k] = MB("%s_%s_%s" % (SCOPE, key, "s" if smooth else "f"))
    return BUILD[k]


PASS_OF = {"ground": 4, "water": 4}


def build_all(coll):
    out = []
    for (scope, key, smooth), b in sorted(BUILD.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        ob = b.build(M[key], smooth, coll, SPL if scope == "plinth" else SL)
        if ob is not None:
            ob.pass_index = 3 if scope == "plinth" else PASS_OF.get(key, 2)
            ob["pwo"] = 1.0
            ob["park_scope"] = scope
            out.append(ob)
    return out


# ------------------------------------------------------------------ small helpers
def hr(i, j, k=0):
    return random.Random((i * 73856093) ^ (j * 19349663) ^ (k * 83492791) ^ (SEED * 2654435761) & 0xFFFFFFFF).random()


def rng_for(i, j, k=0):
    return random.Random(((i + 100) * 10007 + (j + 100)) * 97 + k * 13 + SEED * 100003)


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


def C(r, g, b):
    return (r, g, b)


def sd(n):
    return n if not CEL else max(6, int(n * 0.5))


# ------------------------------------------------------------------ the lot plan (lawn units)
def Rb(th):
    """The park's organic boundary radius at angle th."""
    return RB0 + RB_AMP * (25.0 * math.sin(2 * th + 0.7) + 15.0 * math.sin(5 * th + 2.1))


def inside_blob(x, y, margin=6.0):
    return math.hypot(x, y) < Rb(math.atan2(y, x)) - margin


def plan():
    """One seeded plan: plaza (the plinth), the park ring, the hospital + its park apron, then the Solace bundles."""
    P = {}
    for j in range(-GRID, GRID + 1):
        for i in range(-GRID, GRID + 1):
            cx, cy = i * PITCH, j * PITCH
            r = math.hypot(cx, cy)
            if r < PL_R + 4.0:
                kind = "plaza"
            elif abs(cx - HX) < PITCH * 1.1 and abs(cy - HY) < PITCH * 1.1:
                kind = "hosp"
            elif r <= PARK_R or (abs(cx - HX) <= 2.5 * PITCH and abs(cy - HY) <= 2.5 * PITCH):
                kind = "park"
            else:
                kind = "solace" if inside_blob(cx, cy, 8.0) else "ord"
            h = 0.0
            if kind == "solace":
                h = HK * (26.0 + 18.0 * smoothstep(100.0, 200.0, r) - 8.0 * smoothstep(200.0, 250.0, r)) * (0.62 + 0.62 * hr(i, j, 3))
            P[(i, j)] = dict(kind=kind, h=h, x=cx, y=cy, r=r)
    for (i, j), p in P.items():
        p["sub"] = hr(i, j, 4)
    return P


PLAN = plan()

# ------------------------------------------------------------------ ground, streets, pads
PAD_COL = {"A": (0.03, 0.075, 0.05), "B": (0.035, 0.07, 0.07), "C": (0.50, 0.54, 0.52), "D": (0.03, 0.075, 0.05)}[DIR]
PAD_C = (0.50, 0.54, 0.52) if not N2 else (0.16, 0.15, 0.14)
if CEL:
    PAD_COL = {"A": (0.09, 0.17, 0.14), "B": (0.10, 0.17, 0.17), "C": (0.60, 0.66, 0.64), "D": (0.09, 0.17, 0.14)}[DIR]
    PAD_C = (0.60, 0.66, 0.64)
ORD_PAD = (0.035, 0.035, 0.06) if not CEL else (0.12, 0.10, 0.22)
PARK_COL = (0.02, 0.09, 0.03) if not CEL else (0.07, 0.22, 0.10)
STREET_COL = (0.018, 0.018, 0.03) if not CEL else (0.06, 0.05, 0.13)
if DAYV and not CEL:
    STREET_COL, ORD_PAD, PARK_COL, PAD_COL, PAD_C = (0.07, 0.07, 0.08), (0.11, 0.11, 0.12), (0.05, 0.17, 0.05), (0.09, 0.16, 0.09), (0.50, 0.47, 0.42)
if DAYV and CEL:
    STREET_COL, ORD_PAD, PARK_COL, PAD_COL, PAD_C = (0.16, 0.15, 0.20), (0.22, 0.21, 0.27), (0.10, 0.32, 0.12), (0.16, 0.30, 0.22), (0.48, 0.46, 0.42)


# ------------------------------------------------------------------ trees and park
TREE_COL_N = [(0.02, 0.10, 0.03), (0.03, 0.14, 0.05), (0.015, 0.08, 0.05)] if not CEL else [(0.07, 0.26, 0.10), (0.10, 0.32, 0.12), (0.06, 0.22, 0.14)]
TREE_COL = TREE_COL_N if not (DAYV or (PARK and CEL)) else ([(0.05, 0.22, 0.06), (0.08, 0.28, 0.08), (0.04, 0.18, 0.07)] if not CEL else ([(0.12, 0.40, 0.14), (0.16, 0.46, 0.16), (0.10, 0.34, 0.18)] if DAYV else [(0.11, 0.38, 0.15), (0.15, 0.45, 0.17), (0.09, 0.32, 0.20)]))


def tree(x, y, rr, h=None, z=0.25, glow=False):
    t = mb("plain")
    h = h or (5.0 + 5.0 * rr.random())
    r = (1.6 + 1.2 * rr.random()) * (1.45 if PARK else 1.0)
    col = TREE_COL[int(rr.random() * 3)]
    n = 7 if CEL else 9
    lathe(t, x, y, [(0.0, z + h * 0.18), (r, z + h * 0.18), (r * 0.72, z + h * 0.55), (0.0, z + h)], n, col, (0, 0, 0, 0.3))
    lathe(t, x, y, [(0.0, z), (0.28, z), (0.28, z + h * 0.2)], 5, (0.05, 0.03, 0.02) if not CEL else (0.3, 0.2, 0.2), (0, 0, 0, 0.3))
    if glow:
        sphere(mb("neon"), x, y, z + h * 0.55, 0.45, 5, (LIME if rr.random() < 0.6 else PINKC), (0.8 if not CEL else 1, 0, 0, 1))


def park():
    rr = random.Random(SEED + 11)
    for (i, j), p in PLAN.items():
        if p["kind"] != "park":
            continue
        cx, cy = p["x"], p["y"]
        feat = hr(i, j, 5) < 0.2
        for k in range(0 if PARK else (10 if not feat else 5)):
            ang = rr.random() * 6.283
            d = math.sqrt(rr.random()) * (LOT / 2 - 1.8)
            x, y = cx + d * math.cos(ang), cy + d * math.sin(ang)
            if feat and math.hypot(x - cx, y - cy) < 5.5:
                continue
            tree(x, y, rr, glow=(kit_for(i, j) == "A" and rr.random() < 0.18))
        if feat:
            park_feature(cx, cy, i, j)
        # park lamp posts at the lot corners: tiny emissive beads
        if hr(i, j, 6) < 0.5:
            sphere(mb("neon"), cx + LOT / 2, cy + LOT / 2, 3.0, 0.4, 5, LIME if hr(i, j, 7) < 0.7 else PINKC, (0.9 if not CEL else 1, 0, 0, 1))
            cyl(mb("plain"), cx + LOT / 2, cy + LOT / 2, 0.25, 3.0, 0.1, 5, (0.3, 0.3, 0.3), (0, 0, 0, 0.5), cap=False)


def park_feature(cx, cy, i, j):
    n = sd(28)
    kf = kit_for(i, j)
    if kf == "A":      # a glass greenhouse dome with the grow lights on
        torus(mb("neon"), cx, cy, 0.45, 6.4, 0.22, n, 5, LIME, (0.9 if not CEL else 1, 0, 0, 1))
        dome(mb("glass", True), cx, cy, 0.3, 6.2, n, GL1, (1.0, 0, 0, 1), rings=5, squash=0.85)
        sphere(mb("neon"), cx, cy, 2.2, 1.7, 8, PINKC, (1.0 if not CEL else 1, 0, 0, 1))
        for k in range(5):
            tree(cx + 3.0 * math.cos(k * 1.26), cy + 3.0 * math.sin(k * 1.26), random.Random(k + i), h=4.0)
    elif kf == "B":    # a petri dish: glass rim, agar disc, colonies, ring lights
        torus(mb("glassb", True), cx, cy, 0.7, 6.6, 0.55, n, 6, GL1, (1.0, 0, 0, 1))
        disc(mb("neon"), cx, cy, 0.5, 6.3, n, (LIME[0] * 0.22, LIME[1] * 0.26, LIME[2] * 0.12), (0.5 if not CEL else 1, 0, 0, 1))
        torus(mb("neon"), cx, cy, 0.6, 4.4, 0.18, n, 5, LIME, (1.0 if not CEL else 1, 0, 0, 1))
        torus(mb("neon"), cx, cy, 0.6, 2.2, 0.16, n, 5, PINKC, (1.0 if not CEL else 1, 0, 0, 1))
        rr = random.Random(i * 31 + j)
        for k in range(6):
            a = rr.random() * 6.28
            d = rr.random() * 5.2
            sphere(mb("neon"), cx + d * math.cos(a), cy + d * math.sin(a), 0.7, 0.5 + 0.6 * rr.random(), 6, PINKC if rr.random() < 0.4 else LIME, (1.0 if not CEL else 1, 0, 0, 1))
    else:               # C: a still reflecting pool in a porcelain ring with a pink beacon
        torus(mb("plain", True), cx, cy, 0.4, 6.6, 0.7, n, 6, (0.85, 0.87, 0.85), (0, 0, 0, 0.5))
        disc(mb("glass"), cx, cy, 0.45, 6.2, n, (0.35, 0.8, 0.55, 1), (0.25, 0, 0, 1))
        sphere(mb("neon"), cx, cy, 1.4, 0.5, 6, PINKC, (1.0 if not CEL else 1, 0, 0, 1))


# ------------------------------------------------------------------ building kits
def pr(lit, lime, pink, seed):
    return (lit, lime, pink, seed)


def ord_building(i, j, p):
    rr = rng_for(i, j, 1)
    cx, cy, h = p["x"], p["y"], p["h"]
    w = 6.0 + 2.0 * rr.random()
    d = 6.0 + 2.0 * rr.random()
    base = [(0.06, 0.06, 0.12), (0.08, 0.07, 0.15), (0.05, 0.07, 0.11), (0.09, 0.06, 0.10)]
    if DAYV:
        base = [(0.20, 0.20, 0.26), (0.28, 0.24, 0.22), (0.18, 0.20, 0.26), (0.30, 0.26, 0.22)]
    if CEL:
        base = [(0.20, 0.16, 0.36), (0.24, 0.17, 0.38), (0.17, 0.17, 0.34), (0.27, 0.16, 0.32)]
        if DAYV:
            base = [(0.40, 0.36, 0.50), (0.44, 0.36, 0.42), (0.36, 0.38, 0.46), (0.46, 0.40, 0.36)]
    col = base[int(rr.random() * 4)]
    prm = pr(0.32 + 0.3 * rr.random(), 0.05, 0.12, rr.random())
    key = "ord" if rr.random() < 0.6 else "ordr"
    b = mb(key)
    box(b, cx - w, cy - d, 0.25, cx + w, cy + d, h, col, prm)
    if rr.random() < 0.55:
        w2, d2, h2 = w * 0.62, d * 0.62, h * (0.18 + 0.3 * rr.random())
        box(b, cx - w2, cy - d2, h, cx + w2, cy + d2, h + h2, tuple(c * 1.1 for c in col), prm)
    if rr.random() < 0.18:
        a = rr.choice([(w, 0), (-w, 0), (0, d), (0, -d)])
        col2 = rr.choice([(1.0, 0.25, 0.5), (0.2, 0.8, 1.0), (1.0, 0.7, 0.2)])
        seg = (a[0] + cx, a[1] + cy)
        n2 = mb("neon")
        prism(n2, rect(seg[0] + (a[0] * 0.03), seg[1] + (a[1] * 0.03), 0.18 if a[0] else 3.2, 3.2 if a[0] else 0.18), h * 0.45, h * 0.45 + 5.0, col2, (1, 0, 0, 1), top=False)


def a_tower(cx, cy, h, R, rr, i, j, stacked=False):
    seed = rr.random()
    glassc = GLASSC
    prm = pr(0.88, 0.62, 0.30, seed)
    n = sd(22)
    t = mb("tw", True)
    # podium ring + body + domed cap
    lathe(mb("plain", True), cx, cy, [(0, 0.25), (R + 1.4, 0.25), (R + 1.4, 2.4), (R + 0.2, 3.0)], n, (0.55, 0.62, 0.58) if not CEL else (0.7, 0.8, 0.76), (0, 0, 0, seed))
    prof = [(R, 2.8), (R, h)] + [(R * math.cos(math.pi / 2 * k / 4), h + R * 1.0 * math.sin(math.pi / 2 * k / 4)) for k in range(1, 5)]
    prof[-1] = (0.0, prof[-1][1])
    lathe(t, cx, cy, prof, n, glassc, prm)
    torus(mb("neon"), cx, cy, h + 0.1, R + 0.1, 0.22, n, 5, LIME, (1.0, 0, 0, 1))
    if stacked:
        R2 = R * 0.66
        h2 = h * 0.34
        prof2 = [(R2, h + R * 0.5), (R2, h + R * 0.5 + h2)] + [(R2 * math.cos(math.pi / 2 * k / 4), h + R * 0.5 + h2 + R2 * math.sin(math.pi / 2 * k / 4)) for k in range(1, 5)]
        prof2[-1] = (0.0, prof2[-1][1])
        lathe(t, cx, cy, prof2, n, glassc, pr(0.9, 0.7, 0.2, seed))
        torus(mb("neon"), cx, cy, h + R * 0.5 + h2, R2 + 0.1, 0.2, n, 5, PINKC, (1.0, 0, 0, 1))
        return h + R * 0.5 + h2 + R2
    # a little antenna mast with a pink beacon on some
    if rr.random() < 0.4:
        cyl(mb("plain"), cx, cy, h + R, h + R + 4.0, 0.15, 4, (0.6, 0.6, 0.6), (0, 0, 0, 0.5), cap=False)
        sphere(mb("neon"), cx, cy, h + R + 4.2, 0.4, 5, PINKC, (1.0 if not CEL else 1, 0, 0, 1))
    return h + R


def a_low_dome(cx, cy, h, R, rr, i, j):
    """Low-rise with a rooftop greenhouse dome (grow lights): a squat capsule drum + glass dome."""
    seed = rr.random()
    n = sd(22)
    glassc = GLASSC
    hh = max(10.0, h * 0.45)
    lathe(mb("tw", True), cx, cy, [(0, 0.25), (R, 0.25), (R, hh), (0, hh)], n, glassc, pr(0.85, 0.6, 0.3, seed))
    torus(mb("neon"), cx, cy, hh + 0.1, R + 0.05, 0.22, n, 5, LIME, (1.0, 0, 0, 1))
    dome(mb("glass", True), cx, cy, hh, R * 0.92, n, GL1, (1.0, 0, 0, 1), rings=5, squash=0.9)
    sphere(mb("neon"), cx, cy, hh + 1.6, R * 0.28, 8, PINKC, (1.0 if not CEL else 1, 0, 0, 1))
    for k in range(5):
        tree(cx + R * 0.5 * math.cos(k * 1.26), cy + R * 0.5 * math.sin(k * 1.26), random.Random(k * 7 + i), h=3.5, z=hh)
    return hh + R * 0.9


A_TOWERS = {}


def kit_A(i, j, p):
    rr = rng_for(i, j, 2)
    cx, cy, h = p["x"], p["y"], p["h"]
    R = 5.0 + 2.6 * rr.random()
    if p["sub"] < 0.2:
        A_TOWERS[(i, j)] = None
        a_low_dome(cx, cy, h, R + 0.8, rr, i, j)
        return
    top = a_tower(cx, cy, h, R, rr, i, j, stacked=p["sub"] > 0.84)
    A_TOWERS[(i, j)] = (h, R)


def a_bridges():
    """Bubble skybridges between neighbouring capsule towers: glass tubes with a lit floor."""
    for (i, j), v in A_TOWERS.items():
        if not v:
            continue
        for (di, dj) in ((1, 0), (0, 1)):
            w = A_TOWERS.get((i + di, j + dj))
            if not w or hr(i, j, 20 + di) > 0.5:
                continue
            h0, R0 = v
            h1, R1 = w
            z = 0.55 * min(h0, h1) + 3.0 * hr(i, j, 21)
            ax, ay = i * PITCH, j * PITCH
            bx, by = (i + di) * PITCH, (j + dj) * PITCH
            a = (ax + di * R0 * 0.9, ay + dj * R0 * 0.9, z)
            b = (bx - di * R1 * 0.9, by - dj * R1 * 0.9, z)
            seg_tube(mb("glass", True), a, b, 1.7, sd(10), GL1, (1.0, 0, 0, 1))
            sphere(mb("glass", True), a[0], a[1], a[2], 2.2, sd(10), GL1, (1.0, 0, 0, 1))
            sphere(mb("glass", True), b[0], b[1], b[2], 2.2, sd(10), GL1, (1.0, 0, 0, 1))
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, z - 0.8)
            seg_tube(mb("neon"), (a[0], a[1], z - 0.9), (b[0], b[1], z - 0.9), 0.25, 4, PINKC if hr(i, j, 22) < 0.35 else LIME, (1.0 if not CEL else 1, 0, 0, 1))


def kit_B(i, j, p):
    rr = rng_for(i, j, 3)
    cx, cy, h = p["x"], p["y"], p["h"]
    seed = rr.random()
    big = p["sub"] < 0.5
    ncell = 5 + int(rr.random() * 4) if big else 3 + int(rr.random() * 2)
    core_h = h * (0.95 if big else 0.6)
    coreR = 2.7 if big else 2.1
    dark = (0.04, 0.12, 0.10) if not CEL else (0.10, 0.26, 0.24)
    cyl(mb("tw2"), cx, cy, 0.25, core_h, coreR, sd(10), dark, pr(0.8, 0.5, 0.3, seed))
    torus(mb("neon"), cx, cy, 0.5, 6.6, 0.2, sd(24), 5, LIME, (0.8 if not CEL else 1, 0, 0, 1))
    glc = (0.10, 0.50, 0.28, 1) if CEL else (0.5, 1.0, 0.55, 1)
    if D:
        glc = (0.30, 0.74, 0.12, 1) if CEL else (0.62, 1.0, 0.32, 1)
    NU = "neon_p" if D else "neon_s"
    NR = 0.5 if D else 0.36
    n = sd(14)
    for k in range(ncell):
        f = (k + 0.5) / ncell
        z = 0.25 + core_h * (0.08 + 0.9 * f * f * 0.3 + 0.62 * f)
        rad = (5.4 - 2.2 * f) * (0.8 + 0.4 * rr.random()) * (1.0 if big else 0.8)
        ang = rr.random() * 6.283 + k * 2.2
        d = min(coreR + rad * 0.55, 5.6 - rad * 0.2 + 2.0)
        sx, sy = cx + d * math.cos(ang), cy + d * math.sin(ang)
        sz = max(z, rad + 0.25)
        sphere(mb("glassB", True), sx, sy, sz, rad, n, glc, (1.0, 0, 0, 1))
        if rr.random() < 0.45:
            sphere(mb(NU), sx, sy, sz, rad * NR, 7, PINKC, (1.0 if not CEL else 1, 0, 0, 1))
        elif rr.random() < 0.5:
            sphere(mb("neon_l" if D else "neon"), sx, sy, sz, rad * 0.30, 7, LIME, (0.9 if not CEL else 1, 0, 0, 1))
        if rr.random() < 0.5:        # a daughter cell budding off, half the radius, just touching
            a2 = ang + (rr.random() - 0.5) * 1.6
            r2 = rad * 0.55
            sx2, sy2 = sx + (rad + r2 * 0.55) * math.cos(a2), sy + (rad + r2 * 0.55) * math.sin(a2)
            if abs(sx2 - cx) < 9.5 and abs(sy2 - cy) < 9.5:
                sphere(mb("glassB", True), sx2, sy2, max(sz + (rr.random() - 0.5) * rad, r2 + 0.25), r2, n, glc, (1.0, 0, 0, 1))
    if big:
        top = sphere(mb("glassB", True), cx, cy, core_h + 2.3, 4.0, n, glc, (1.0, 0, 0, 1))
        sphere(mb(NU), cx, cy, core_h + 2.3, 1.55 * (1.3 if D else 1.0), 8, PINKC, (1.0 if not CEL else 1, 0, 0, 1))


def kit_C(i, j, p):
    rr = rng_for(i, j, 4)
    cx, cy, h = p["x"], p["y"], p["h"]
    seed = rr.random()
    porc = (0.80, 0.83, 0.80) if not CEL else (0.88, 0.92, 0.90)
    if N2:
        porc = (0.34, 0.32, 0.29)
    if RAID and CEL and not DAYV:
        porc = (0.52, 0.54, 0.62)
    if DAYV:
        porc = (0.66, 0.63, 0.56) if not CEL else (0.60, 0.58, 0.54)
    glassg = porc
    prmw = pr(0.86, 0.9, 0.04, seed)
    if p["sub"] < 0.22:            # low clinic wing: white block, one green band, roof garden
        w, d = 7.0, 5.5
        prism(mb(TWC), rect(cx, cy, w, d, 0.0), 0.25, max(11.0, h * 0.4), glassg, prmw)
        z = max(11.0, h * 0.4)
        box(mb("plain"), cx - w - 0.4, cy - d - 0.4, z, cx + w + 0.4, cy + d + 0.4, z + 0.5, porc, (0, 0, 0, seed))
        for k in range(6):
            tree(cx - w + 2 + k * 2.3, cy, rr, h=3.0, z=z + 0.5)
        sphere(mb("neon"), cx + w - 1.0, cy + d - 1.0, z + 1.2, 0.35, 5, PINKC, (1.0 if not CEL else 1, 0, 0, 1))
        return
    w = 6.0 + 2.0 * rr.random()
    tiers = [(w, h * 0.46), (w * 0.84, h * 0.26), (w * 0.66, h * 0.16)]
    z = 0.25
    for t, (tw, th) in enumerate(tiers):
        prism(mb(TWC), rect(cx, cy, tw, tw, 0.0), z, z + th, glassg, prmw)
        # porcelain corner piers (four slim white columns) + slab edge
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            box(mb("plain"), cx + sx * tw - 0.9 * (1 if sx > 0 else 0) - (0.0 if sx > 0 else 0), cy + sy * tw - 0.9 * (1 if sy > 0 else 0), z, cx + sx * tw + 0.9 * (0 if sx > 0 else 1), cy + sy * tw + 0.9 * (0 if sy > 0 else 1), z + th, porc, (0, 0, 0, seed))
        box(mb("plain"), cx - tw - 0.5, cy - tw - 0.5, z + th, cx + tw + 0.5, cy + tw + 0.5, z + th + 0.7, porc, (0, 0, 0, seed))
        # terrace on the setback: a green strip around the next tier
        if t < 2:
            nxt = tiers[t + 1][0]
            g = mb("ground")
            box(g, cx - tw - 0.5, cy - tw - 0.5, z + th + 0.7, cx + tw + 0.5, cy + tw + 0.5, z + th + 0.95, PARK_COL if not CEL else (0.18, 0.52, 0.24), (0.9, 0, 0, 1), top=True)
            for k in range(5):
                a = rr.random() * 6.283
                tx, ty = cx + (tw + nxt) / 2 * math.cos(a) * 0.7, cy + (tw + nxt) / 2 * math.sin(a) * 0.7
                if abs(tx - cx) > nxt + 0.5 or abs(ty - cy) > nxt + 0.5:
                    tree(tx, ty, rr, h=3.4, z=z + th + 0.95)
        z += th + 0.7
    # vertical greenhouse strip on one face (glass slab, lit)
    face = int(rr.random() * 4)
    fx, fy = [(1, 0), (0, 1), (-1, 0), (0, -1)][face]
    gh = tiers[0][1]
    seg_box = rect(cx + fx * (w + 0.5), cy + fy * (w + 0.5), 0.5 if fx else w * 0.5, w * 0.5 if fx else 0.5)
    prism(mb("glass"), seg_box, 0.25, gh, GL1, (1.0, 0, 0, 1))
    # the twisted crown: a stack of rotating slabs
    nsl = 7
    tw0 = tiers[2][0] * 0.82
    for s in range(nsl):
        ang = s * math.radians(11)
        ww = tw0 * (1.0 - 0.07 * s)
        prism(mb("plain"), rect(cx, cy, ww, ww, ang), z + s * 1.5, z + s * 1.5 + 1.25, porc, (0, 0, 0, seed))
        prism(mb("neon"), rect(cx, cy, ww + 0.05, ww + 0.05, ang), z + s * 1.5 + 1.25, z + s * 1.5 + 1.4, LIME if s % 2 == 0 else (0.7, 1.0, 0.8), (0.85 if not CEL else 1, 0, 0, 1), top=False)
    zt = z + nsl * 1.5
    sphere(mb("neon"), cx, cy, zt + 0.7, 0.55, 6, PINKC, (1.0 if not CEL else 1, 0, 0, 1))


KITS = {"A": kit_A, "B": kit_B, "C": kit_C}
KIT = KITS.get(DIR)


def make_bundles():
    """Direction D: seeded Voronoi bundles (about 3-8 neighbouring lots each), kits assigned so neighbours differ and no kit dominates."""
    sp = 2.6
    seeds = []
    for gj in range(-6, 7):
        for gi in range(-6, 7):
            x = gi * sp + (hr(gi, gj, 41) - 0.5) * 1.8
            y = gj * sp + (hr(gi, gj, 42) - 0.5) * 1.8
            if math.hypot(x, y) <= 11.5:
                seeds.append((gi, gj, x, y))
    kit_of, count = {}, {"A": 0, "B": 0, "C": 0}
    for (gi, gj, x, y) in seeds:
        near = [kit_of[(a, b)] for (a, b, xx, yy) in seeds if (a, b) in kit_of and math.hypot(xx - x, yy - y) < sp * 1.75]
        ok = [k for k in "ABC" if k not in near] or list("ABC")
        ok.sort(key=lambda k: (count[k] + hr(gi, gj, ord(k)) * 0.9, k))
        kit_of[(gi, gj)] = ok[0]
        count[ok[0]] += 1
    out, sizes = {}, {}
    for (i, j) in PLAN:
        best = min(seeds, key=lambda t: ((t[2] - i) ** 2 + (t[3] - j) ** 2, t[0], t[1]))
        out[(i, j)] = kit_of[(best[0], best[1])]
        sizes[(best[0], best[1])] = sizes.get((best[0], best[1]), 0) + (1 if PLAN[(i, j)]["kind"] in ("solace", "park") else 0)
    return out, kit_of, seeds, sizes


BUNDLE, BUNDLE_KIT, BUNDLE_SEEDS, BUNDLE_SIZES = make_bundles() if D else ({}, {}, [], {})


def kit_for(i, j):
    return BUNDLE[(i, j)] if D else DIR


# ------------------------------------------------------------------ the hospital Site (non-HQ landmark)
def hospital():
    hx, hy = HX, HY
    n = sd(28)
    porc = (0.80, 0.84, 0.81) if not CEL else (0.88, 0.92, 0.90)
    if N2:
        porc = (0.34, 0.32, 0.29)
    if RAID and CEL and not DAYV:
        porc = (0.52, 0.54, 0.62)
    if DAYV:
        porc = (0.66, 0.63, 0.56) if not CEL else (0.60, 0.58, 0.54)
    # helipad
    def helipad(x, y, z, r):
        torus(mb("neon"), x, y, z, r, 0.2, n, 4, LIME, (1.0 if not CEL else 1, 0, 0, 1))
        for sx in (-1, 1):
            box(mb("neon"), x + sx * r * 0.32 - 0.25, y - r * 0.4, z, x + sx * r * 0.32 + 0.25, y + r * 0.4, z + 0.1, LIME, (1.0 if not CEL else 1, 0, 0, 1))
        box(mb("neon"), x - r * 0.32, y - 0.25, z, x + r * 0.32, y + 0.25, z + 0.1, LIME, (1.0 if not CEL else 1, 0, 0, 1))
    # the pad ring + beacons
    if not PARK:
        torus(mb("neon"), hx, hy, 0.4, 35.0, 0.22, sd(48), 4, LIME, (0.8 if not CEL else 1, 0, 0, 1))
    glassc = GLASSC
    seed = 0.37
    HK = "C" if D else DIR
    if HK == "A":
        lathe(mb("tw", True), hx, hy, [(0, 0.3), (14.0, 0.3), (14.0, 18.0), (0, 18.0)], n, glassc, pr(0.9, 0.55, 0.3, seed))
        torus(mb("neon"), hx, hy, 18.1, 14.05, 0.3, n, 5, LIME, (1.0, 0, 0, 1))
        dome(mb("glass", True), hx, hy, 18.0, 13.5, n, (0.55, 1.0, 0.5, 1), (1.0, 0, 0, 1), rings=5, squash=0.7)
        for k, (ox, oy) in enumerate(((-24.0, 6.0), (24.0, 0.0), (0.0, 24.0))):
            Rw = 6.0
            lathe(mb("tw", True), hx + ox, hy + oy, [(0, 0.3), (Rw, 0.3), (Rw, 34.0)] + [(Rw * math.cos(math.pi / 2 * q / 4), 34.0 + Rw * math.sin(math.pi / 2 * q / 4)) for q in range(1, 5)], n, glassc, pr(0.9, 0.55, 0.3, seed + k))
            seg_tube(mb("glass", True), (hx + ox * 0.45, hy + oy * 0.45, 12.0), (hx + ox * 0.8, hy + oy * 0.8, 12.0), 1.6, 10, (0.55, 1.0, 0.5, 1), (1.0, 0, 0, 1))
        cz = 18.0 + 13.5 * 0.7 + 0.5
    elif HK == "B":
        sphere(mb("glassB", True), hx, hy, 12.0, 12.0, sd(20), GL1, (1.0, 0, 0, 1))
        sphere(mb("neon_s"), hx, hy, 12.0, 4.0, 10, PINKC, (1.2, 0, 0, 1))
        cyl(mb("tw2"), hx, hy, 0.3, 20.0, 3.0, sd(10), (0.04, 0.12, 0.10) if not CEL else (0.10, 0.26, 0.24), pr(0.8, 0.5, 0.3, seed))
        for k in range(6):
            a = k * math.pi / 3 + 0.3
            rad = 7.5 + (k % 2) * 2.0
            sphere(mb("glassB", True), hx + 17.0 * math.cos(a), hy + 17.0 * math.sin(a), rad, rad, sd(16), GL1, (1.0, 0, 0, 1))
            if k % 2 == 0:
                sphere(mb("neon"), hx + 17.0 * math.cos(a), hy + 17.0 * math.sin(a), rad, rad * 0.35, 8, PINKC, (1.0, 0, 0, 1))
            else:
                sphere(mb("neon"), hx + 17.0 * math.cos(a), hy + 17.0 * math.sin(a), rad, rad * 0.3, 8, LIME, (0.9, 0, 0, 1))
        cz = 25.0
    else:
        wing = [(30.0, 7.5, 0.0), (7.5, 30.0, 0.0)]
        for (ww, dd, _a) in wing:
            prism(mb(TWC), rect(hx, hy, ww, dd, 0.0), 0.3, 26.0, porc, pr(0.9, 0.9, 0.04, seed))
            box(mb("plain"), hx - ww - 0.6, hy - dd - 0.6, 26.0, hx + ww + 0.6, hy + dd + 0.6, 27.0, porc, (0, 0, 0, seed))
        for sx, sy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            box(mb("plain"), hx + sx * 30 - 1.2 + (1.2 if sx < 0 else 0) * 0, hy + sy * 30 - 1.2, 0.3, hx + sx * 30 + 1.2, hy + sy * 30 + 1.2, 26.0, porc, (0, 0, 0, seed)) if False else None
        box(mb("plain"), hx - 8.0, hy - 8.0, 27.0, hx + 8.0, hy + 8.0, 38.0, porc, (0, 0, 0, seed))
        prism(mb(TWC), rect(hx, hy, 8.0, 8.0, 0.0), 27.0, 38.0, porc, pr(0.9, 0.9, 0.04, seed))
        box(mb("plain"), hx - 8.8, hy - 8.8, 38.0, hx + 8.8, hy + 8.8, 39.0, porc, (0, 0, 0, seed))
        helipad(hx, hy, 39.1, 6.5)
        cz = 39.0
    # the standing green cross: a beacon over the roof, double-sided, facing the camera diagonal (the Site mark)
    cross_shape(mb("neon_x"), hx, hy, cz + 9.0, 11.0, 3.6, math.radians(CROSS_ANG), LIME, (1.0 if not CEL else 1, 0, 0, 1), depth=0.5)
    cyl(mb("plain"), hx, hy, cz, cz + 3.4, 0.35, 5, (0.6, 0.6, 0.6), (0, 0, 0, 0.5), cap=False)
    # a pink beacon on the mast
    sphere(mb("neon"), hx, hy, cz + 15.4, 0.7, 6, PINKC, (1.0, 0, 0, 1))
    # perimeter trees
    rr = random.Random(5)
    for k in range(0 if PARK else 18):
        a = 2 * math.pi * k / 18
        tree(hx + 30.0 * math.cos(a), hy + 30.0 * math.sin(a), rr, h=4.5, z=0.3)


# ------------------------------------------------------------------ round 4: one continuous park (direction D, --park 1)
def _pc(night, celnight, day, celday):
    if DAYV:
        return celday if CEL else day
    return celnight if CEL else night


LAWN_A = _pc((0.022, 0.075, 0.028), (0.07, 0.22, 0.10), (0.07, 0.20, 0.06), (0.12, 0.38, 0.14))
LAWN_B = _pc((0.04, 0.115, 0.04), (0.10, 0.30, 0.12), (0.11, 0.28, 0.08), (0.17, 0.48, 0.17))
LAWN_A = tuple(c * 2.4 for c in LAWN_A); LAWN_B = tuple(c * 2.4 for c in LAWN_B)
GRAVEL = _pc((0.09, 0.10, 0.08), (0.22, 0.25, 0.22), (0.50, 0.45, 0.36), (0.40, 0.37, 0.32))
LANE = _pc((0.03, 0.03, 0.04), (0.10, 0.09, 0.18), (0.09, 0.09, 0.10), (0.14, 0.14, 0.18))
CLEAR = _pc((0.10, 0.12, 0.11), (0.14, 0.22, 0.19), (0.46, 0.44, 0.38), (0.40, 0.40, 0.36))
WATERC = _pc((0.01, 0.05, 0.07), (0.06, 0.22, 0.30), (0.05, 0.20, 0.24), (0.20, 0.55, 0.60))
KITLOTS = {k for k, p in PLAN.items() if p["kind"] == "solace"}
FEATLOTS = {k for k, p in PLAN.items() if p["kind"] == "park" and hr(k[0], k[1], 5) < 0.2}
PONDLOTS = {k for k, p in PLAN.items() if p["kind"] == "park" and k not in FEATLOTS and hr(k[0], k[1], 9) < 0.45 and inside_blob(p["x"], p["y"], 20.0)}
FLATLOTS = KITLOTS | FEATLOTS | PONDLOTS


def _roll(x, y):
    return 0.8 * (1.1 + 0.9 * math.sin(x * 0.038 + 1.3) * math.cos(y * 0.031 + 0.4) + 0.7 * math.sin((x * 0.6 + y) * 0.062 + 0.5) + 0.35 * math.sin(x * 0.11) * math.sin(y * 0.09)) + 0.3


def _flat_mask(x, y):
    i, j = round(x / PITCH), round(y / PITCH)
    d = 1e9
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if (i + di, j + dj) in FLATLOTS:
                d = min(d, max(abs(x - (i + di) * PITCH), abs(y - (j + dj) * PITCH)))
    d = min(d, math.hypot(x, y) - (PL_R + 6.0), math.hypot(x - HX, y - HY) - 36.0)
    return smoothstep(10.0, 26.0, d)


def GZ(x, y):
    """Ground height of the lawn: rolling in the open, flat under buildings and clearings, tapering to the street level at the edge."""
    r = math.hypot(x, y)
    th = math.atan2(y, x)
    edge = smoothstep(Rb(th), Rb(th) - 24.0, r)
    return 0.24 + _roll(x, y) * _flat_mask(x, y) * edge


def _lawn_col(x, y):
    t = 0.5 + 0.5 * math.sin(x * 0.051 + math.sin(y * 0.043) * 2.2) * math.sin(y * 0.037 + 0.8 + math.sin(x * 0.029) * 1.7)
    t = max(0.0, min(1.0, t))
    return tuple(LAWN_A[k] + (LAWN_B[k] - LAWN_A[k]) * t for k in range(3))


def _chaikin(pts, it=2, q=0.2):
    for _ in range(it):
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            out.append((a[0] + (b[0] - a[0]) * q, a[1] + (b[1] - a[1]) * q))
            out.append((a[0] + (b[0] - a[0]) * (1 - q), a[1] + (b[1] - a[1]) * (1 - q)))
        out.append(pts[-1])
        pts = out
    return pts


def _resample(pts, step=3.0):
    out = [pts[0]]
    carry = 0.0
    for a, b in zip(pts, pts[1:]):
        L_ = math.hypot(b[0] - a[0], b[1] - a[1])
        if L_ < 1e-6:
            continue
        t = step - carry
        while t <= L_:
            out.append((a[0] + (b[0] - a[0]) * t / L_, a[1] + (b[1] - a[1]) * t / L_))
            t += step
        carry = L_ - (t - step)
    out.append(pts[-1])
    return out


def _wobble(pts, amp, wl, phase):
    out = []
    s_ = 0.0
    for i, p in enumerate(pts):
        if i > 0:
            s_ += math.hypot(p[0] - pts[i - 1][0], p[1] - pts[i - 1][1])
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1.0
        o = amp * math.sin(s_ / wl * 6.283 + phase)
        out.append((p[0] - ty / n * o, p[1] + tx / n * o))
    return out


def _ribbon(mbd, pts, w, zoff, col, prm):
    vs = []
    for i, p in enumerate(pts):
        a = pts[max(0, i - 1)]
        b = pts[min(len(pts) - 1, i + 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty) or 1.0
        nx, ny = -ty / n * w / 2, tx / n * w / 2
        z = GZ(p[0], p[1]) + zoff
        vs.append((mbd.v((p[0] - nx, p[1] - ny, z), col, prm), mbd.v((p[0] + nx, p[1] + ny, z), col, prm)))
    for (a0, a1), (b0, b1) in zip(vs, vs[1:]):
        mbd.f(a0, a1, b1, b0)


def _blob_poly(cx, cy, R, wob, ph, n=40, sx=1.0, sy=1.0, rot=0.0):
    pts = []
    for k in range(n):
        t = 2 * math.pi * k / n
        r = R * (1 + wob * math.sin(3 * t + ph) + wob * 0.6 * math.sin(5 * t + ph * 1.7) + wob * 0.4 * math.sin(2 * t + ph * 0.6))
        x, y = r * math.cos(t) * sx, r * math.sin(t) * sy
        pts.append((cx + x * math.cos(rot) - y * math.sin(rot), cy + x * math.sin(rot) + y * math.cos(rot)))
    return pts


def _nodes_route(start, head, out_goal, rr):
    blocked = lambda x, y: abs(x - HX) < 24 and abs(y - HY) < 24
    nodes = [start]
    h = head
    for _ in range(26):
        x, y = nodes[-1]
        r = math.hypot(x, y) or 1.0
        ox, oy = (x / r, y / r) if out_goal else (-x / r, -y / r)
        cands = [(h, 0.55), ((-h[1], h[0]), 0.225), ((h[1], -h[0]), 0.225)]
        sc = []
        for d_, w_ in cands:
            nx, ny = x + d_[0] * PITCH, y + d_[1] * PITCH
            if blocked(nx, ny):
                sc.append(0.0)
                continue
            sc.append(w_ * (0.35 + max(0.0, d_[0] * ox + d_[1] * oy)) * (0.6 + rr.random()))
        if sum(sc) <= 0:
            break
        k = max(range(3), key=lambda i: sc[i])
        h = cands[k][0]
        nodes.append((x + h[0] * PITCH, y + h[1] * PITCH))
        rn = math.hypot(*nodes[-1])
        if out_goal and rn > Rb(math.atan2(nodes[-1][1], nodes[-1][0])) + 55:
            break
        if (not out_goal) and rn < PL_R + 10.0:
            break
    return nodes


def _tree_ok(x, y, pathgrid, extra=0.0):
    if not inside_blob(x, y, 7.0):
        return False
    i, j = round(x / PITCH), round(y / PITCH)
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            if (i + di, j + dj) in FLATLOTS and max(abs(x - (i + di) * PITCH), abs(y - (j + dj) * PITCH)) < 11.0 + extra:
                return False
    if math.hypot(x, y) < PL_R + 8.0 or math.hypot(x - HX, y - HY) < 42.0:
        return False
    gx, gy = int(x // 5), int(y // 5)
    for a in (gx - 1, gx, gx + 1):
        for b in (gy - 1, gy, gy + 1):
            for (px, py, pw) in pathgrid.get((a, b), ()):
                if (px - x) ** 2 + (py - y) ** 2 < (pw / 2 + 2.4) ** 2:
                    return False
    return True


SR = PL_R       # the stair feet in lawn units (the plinth's own stair is PL_FOOT in plinth units)
TIERS = ((35.0, TIER_H / 3.0), (29.5, TIER_H * 2.0 / 3.0), (24.0, TIER_H))


def _plinth_build():
    """Round 5: the helix stands on a raised circular plinth of three low tiers, with four stair flights at N, E, S, W."""
    col = _pc((0.42, 0.46, 0.43), (0.66, 0.74, 0.70), (0.66, 0.65, 0.60), (0.62, 0.66, 0.64))
    scol = tuple(min(1.0, c * 1.25) for c in col)
    base = 0.0
    n = 72 if not CEL else 40
    for (r, h) in TIERS:
        cyl(mb("stone"), 0, 0, base, base + h, r, n, col, (0, 0, 0, 0.2))
        if not (CEL and DAYV):
            torus(mb("neon"), 0, 0, base + h + 0.02, r - 0.1, 0.22, n, 4, LIME, (1.0 if not CEL else 1, 0, 0, 1))
    top = base + TIERS[-1][1]
    torus(mb("neon"), 0, 0, top + 0.03, 17.0, 0.2, n, 4, PINKC, (0.9 if not CEL else 1, 0, 0, 1))
    torus(mb("neon"), 0, 0, top + 0.03, 12.05, 0.28, n, 4, LIME, (1.3 if not CEL else 1, 0, 0, 1))
    r0, r1 = TIERS[-1][0] - 0.2, PL_FOOT
    ns = 16
    run = (r1 - r0) / ns
    rise = (top - 0.24) / ns
    hw = 5.2
    for q in range(4):
        ang = q * math.pi / 2
        c_, s_ = round(math.cos(ang)), round(math.sin(ang))
        for k in range(ns):
            a, b = r0 + k * run, r0 + (k + 1) * run
            z1 = top - k * rise
            if c_ != 0:
                x0, x1 = sorted((a * c_, b * c_))
                box(mb("stone"), x0, -hw, base, x1, hw, z1, scol, (0, 0, 0, 0.2))
            else:
                y0, y1 = sorted((a * s_, b * s_))
                box(mb("stone"), -hw, y0, base, hw, y1, z1, scol, (0, 0, 0, 0.2))
        for sg in (-1, 1):
            pa = (r0 * c_ - s_ * hw * sg, r0 * s_ + c_ * hw * sg, top + 0.1)
            pb = (r1 * c_ - s_ * hw * sg, r1 * s_ + c_ * hw * sg, 0.45)
            seg_tube(mb("neon"), pa, pb, 0.13, 4, LIME, (0.9 if not CEL else 1, 0, 0, 1))


def plinth_build():
    global SCOPE
    SCOPE = "plinth"
    try:
        _plinth_build()
    finally:
        SCOPE = "lawn"


def park_world():
    """One continuous park: rolling lawn, organic clearings, curving footpaths and service lanes, ponds, tree clumps, a tree line."""
    g = mb("ground", True)
    rr = random.Random(SEED + 400)
    # ---- the lawn: a polar mesh out to the organic boundary
    NR, NA = 48, 220
    rings = []
    cvert = g.v((0, 0, GZ(0, 0) + 0.04), _lawn_col(0, 0), (0.9, 0.0, 0, 1))
    for k in range(1, NR + 1):
        u = k / NR
        row = []
        for a_ in range(NA + 1):
            th = 2 * math.pi * (a_ % NA) / NA
            R_ = Rb(th) * u
            x, y = R_ * math.cos(th), R_ * math.sin(th)
            row.append(g.v((x, y, GZ(x, y) + 0.04), _lawn_col(x, y), (0.9, 0.0, 0, 1)))
        rings.append(row)
    for a_ in range(NA):
        g.f(cvert, rings[0][a_ + 1], rings[0][a_])
    for k in range(NR - 1):
        for a_ in range(NA):
            g.f(rings[k][a_], rings[k][a_ + 1], rings[k + 1][a_ + 1], rings[k + 1][a_])
    # ---- clearings round the helix and the hospital
    for (cx, cy, R, ph) in ((0.0, 0.0, PL_R + 8.0, 0.4), (HX, HY, 38.0, 1.9)):
        poly = _blob_poly(cx, cy, R, 0.07, ph, 44)
        idx = [g.v((x, y, GZ(x, y) + 0.1), CLEAR, (0.55, 0.0, 0, 1)) for (x, y) in poly]
        c0 = g.v((cx, cy, GZ(cx, cy) + 0.1), CLEAR, (0.55, 0.0, 0, 1))
        for k in range(len(idx)):
            g.f(c0, idx[k], idx[(k + 1) % len(idx)])
    # lit loop paths in the clearings (wobbly rings)
    for (cx, cy, R, ph, col) in (((HX, HY, 31.0, 1.9, LIME),) if PLINTH else ((0.0, 0.0, 19.0, 0.4, PINKC), (0.0, 0.0, 27.5, 0.9, LIME), (0.0, 0.0, 35.0, 1.4, LIME), (HX, HY, 31.0, 1.9, LIME))):
        poly = _blob_poly(cx, cy, R, 0.045, ph, 64)
        _ribbon(mb("neon"), poly + [poly[0]], 0.9, 0.16, col, (0.8 if not CEL else 1, 0, 0, 1))
    # ---- footpaths and service lanes: curving routes along the old corridors, meandering, running out into the city streets
    routes = []
    n_out = 9
    for k in range(n_out):
        th0 = 2 * math.pi * k / n_out + (hr(k, 0, 51) - 0.5) * 0.5
        x0, y0 = (PL_R + 8.0) * math.cos(th0), (PL_R + 8.0) * math.sin(th0)
        a, b = round(x0 / PITCH - 0.5), round(y0 / PITCH - 0.5)
        start = ((a + 0.5) * PITCH, (b + 0.5) * PITCH)
        ox, oy = math.cos(th0), math.sin(th0)
        head = max(((1, 0), (0, 1), (-1, 0), (0, -1)), key=lambda d: d[0] * ox + d[1] * oy)
        routes.append((_nodes_route(start, head, True, random.Random(SEED + 500 + k)), "lane" if k in (1, 4, 7) else "foot"))
    if PLINTH:
        drop = (0, 2, 4, 7)
        routes = [r for k, r in enumerate(routes) if k not in drop]
        routes = [(n_, "lane" if (k_ in (1, 2)) else "foot") for k_, (n_, kd) in enumerate(routes)] if False else routes
        for q, (st_, hd_) in enumerate((((SR, 0.0), (0, 1)), ((0.0, SR), (1, 0)), ((-SR, 0.0), (0, -1)), ((0.0, -SR), (-1, 0)))):
            routes.append(([st_] + _nodes_route(st_, hd_, True, random.Random(SEED + 600 + q))[1:], "foot"))
    routes.append((_nodes_route((HX + 24.0, HY), (1, 0), True, random.Random(SEED + 530)), "foot"))
    routes.append((_nodes_route((HX - 24.0, HY), (-1, 0), False, random.Random(SEED + 531)), "foot"))
    if PLINTH:
        plinth_build()
    pathgrid = {}
    for ri, (nodes, kind) in enumerate(routes):
        if len(nodes) < 2:
            continue
        pts = _chaikin(nodes, 2, 0.2)
        pts = _resample(pts, 3.0)
        pts = _wobble(pts, 1.3 if kind == "foot" else 0.8, 46.0, ri * 1.7)
        w = 2.6 if kind == "foot" else 5.0
        _ribbon(g, pts, w, 0.12, GRAVEL if kind == "foot" else LANE, (0.8, 1.0 if kind == "lane" else 0.0, 0, 1))
        if kind == "foot":
            _ribbon(mb("neon"), pts, 0.75, 0.2, LIME, (0.55 if not CEL else 1, 0, 0, 1))
        else:
            for sgn in (-1, 1):
                off = []
                for i, p in enumerate(pts):
                    a_ = pts[max(0, i - 1)]
                    b_ = pts[min(len(pts) - 1, i + 1)]
                    tx, ty = b_[0] - a_[0], b_[1] - a_[1]
                    n_ = math.hypot(tx, ty) or 1.0
                    off.append((p[0] - ty / n_ * sgn * 2.2, p[1] + tx / n_ * sgn * 2.2))
                for q in range(0, len(off) - 3, 4):
                    _ribbon(mb("neon"), off[q:q + 3], 0.5, 0.2, LIME if sgn > 0 else (0.9, 0.7, 0.3), (0.7 if not CEL else 1, 0, 0, 1))
        for p in pts:
            pathgrid.setdefault((int(p[0] // 5), int(p[1] // 5)), []).append((p[0], p[1], w))
    # ---- ponds
    wm = mb("water")
    ponds = []
    for (i, j) in sorted(PONDLOTS):
        cx, cy = i * PITCH + (hr(i, j, 10) - 0.5) * 6, j * PITCH + (hr(i, j, 11) - 0.5) * 6
        poly = _blob_poly(cx, cy, 6.5 + 3.0 * hr(i, j, 12), 0.12, hr(i, j, 13) * 6, 28, 1.0, 0.65 + 0.3 * hr(i, j, 14), hr(i, j, 15) * 3.14)
        idx = [wm.v((x, y, GZ(x, y) + 0.1), WATERC, (0.1, 0, 0, 1)) for (x, y) in poly]
        c0 = wm.v((cx, cy, GZ(cx, cy) + 0.1), WATERC, (0.1, 0, 0, 1))
        for k in range(len(idx)):
            wm.f(c0, idx[k], idx[(k + 1) % len(idx)])
        ponds.append((cx, cy))
    # ---- tree clumps
    nt = 0
    for c in range(240):
        a = rr.random() * 6.283
        r = math.sqrt(rr.random()) * RB0
        cx, cy = r * math.cos(a), r * math.sin(a)
        if not inside_blob(cx, cy, 10.0):
            continue
        n = 4 + int(rr.random() * 8)
        rad = 4.0 + 6.0 * rr.random()
        for k in range(n):
            ang = rr.random() * 6.283
            d = abs(rr.gauss(0, rad * 0.55))
            x, y = cx + d * math.cos(ang), cy + d * math.sin(ang)
            if not _tree_ok(x, y, pathgrid):
                continue
            if any((x - px) ** 2 + (y - py) ** 2 < 100 for (px, py) in ponds):
                continue
            glow = (D and BUNDLE.get((round(x / PITCH), round(y / PITCH))) == "A" and rr.random() < 0.12)
            tree(x, y, rr, h=5.5 + 5.0 * rr.random(), z=GZ(x, y), glow=glow)
            nt += 1
    # ---- the tree line along the organic boundary (gaps where a path runs out)
    ntl = int(2 * math.pi * RB0 / 4.5)
    for k in range(ntl):
        th = 2 * math.pi * k / ntl + rr.random() * 0.02
        for row in (0, 1):
            r = Rb(th) - 3.0 - row * 4.5 + (rr.random() - 0.5) * 3.0
            x, y = r * math.cos(th), r * math.sin(th)
            gx, gy = int(x // 5), int(y // 5)
            near = any((px - x) ** 2 + (py - y) ** 2 < (pw / 2 + 2.8) ** 2 for a in (gx - 1, gx, gx + 1) for b in (gy - 1, gy, gy + 1) for (px, py, pw) in pathgrid.get((a, b), ()))
            if near:
                continue
            tree(x, y, rr, h=7.0 + 5.0 * rr.random(), z=GZ(x, y))
            nt += 1
    print("PARK trees", nt, "ponds", len(ponds), "routes", [len(r[0]) for r in routes], flush=True)
    if PLINTH:
        return
    # ---- the plinth drum at the helix (as the plaza, minus the geometric rings)
    cyl(mb("plain"), 0, 0, 0.3, 2.5, 12.0, sd(32), (0.38, 0.44, 0.42) if not CEL else (0.7, 0.78, 0.74), (0, 0, 0, 0.2))
    torus(mb("neon"), 0, 0, 2.55, 12.05, 0.28, sd(40), 5, LIME, (1.3 if not CEL else 1, 0, 0, 1))




# ------------------------------------------------------------------ assemble
def build(coll, emit_k=0.35, ek_scale=1.0):
    """Build the park kit into collection coll; returns dict(objs, lights, stats)."""
    global M
    L.EMIT_K = emit_k
    L.EK_SCALE = ek_scale
    M = mats()
    t0 = time.time()
    park()
    park_world()
    hospital()
    for (i, j), p in sorted(PLAN.items()):
        if p["kind"] == "solace":
            (KITS[kit_for(i, j)])(i, j, p)
    a_bridges()
    objs = build_all(coll)
    return dict(objs=objs, lights=light_specs(), seconds=time.time() - t0,
                bundles={k: sum(1 for (a, b), v in BUNDLE.items() if v == k and PLAN[(a, b)]["kind"] == "solace") for k in "ABC"})


def light_specs():
    """(name, kind, loc BU, colour, power, size, group) specs, in HQ BU: the C bundles' cool-white spots, the hospital's
    lime + white, the small lime / pink path lights. Powers are the district's N2 night numbers x SL^2 (the same
    illumination on the scaled geometry); hq_scene multiplies by its own exposure factor."""
    out = []
    k2 = SL * SL
    for (gi, gj, x, y) in BUNDLE_SEEDS:
        if BUNDLE_KIT[(gi, gj)] == "C" and inside_blob(x * PITCH, y * PITCH, 20.0) and math.hypot(x * PITCH, y * PITCH) > PARK_R:
            out.append(("kitC_%d_%d" % (gi, gj), "POINT", (x * PITCH * SL, y * PITCH * SL, 38.0 * SL), (0.85, 1.0, 0.95), 1.2e4 * k2, 4.0 * SL))
    out.append(("hosp_lime", "POINT", (HX * SL, HY * SL, 55.0 * SL), LIME, 4e4 * k2, 5.0 * SL))
    out.append(("hosp_white", "POINT", (HX * SL, HY * SL, 14.0 * SL), (0.9, 1.0, 0.95), 1.5e4 * k2, 5.0 * SL))
    rr = random.Random(3)
    for k in range(14):
        a = 2 * math.pi * k / 14 + 0.2
        r = (PL_R + 4.0) + 25 * rr.random()
        out.append(("path_%d" % k, "POINT", (r * math.cos(a) * SL, r * math.sin(a) * SL, 10.0 * SL), LIME if k % 3 else PINKC, 6e3 * k2, 2.0 * SL))
    return out
