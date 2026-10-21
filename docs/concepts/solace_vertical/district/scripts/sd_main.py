"""Solace district concept scene + renders.   blender -b --python sd_main.py -- --dir A --mode map --size 1920x1080 --out X.png
dir  A capsule grove | B culture cells | C clean ward      mode  map (Eevee cel, ortho) | night (Cycles AAA-2 hero)
Same layout for all three directions: one seeded lot plan, one helix, one hospital Site; only the building kit changes.
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

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
A = {"dir": "A", "mode": "night", "size": "1920x1080", "spp": "64", "out": "out/test.png", "cam": "", "scale": "300", "post": "1", "seed": "7", "device": "GPU"}
for i in range(0, len(argv), 2):
    A[argv[i].lstrip("-")] = argv[i + 1]
DIR, MODE = A["dir"], A["mode"]
W, H = [int(x) for x in A["size"].split("x")]
CEL = MODE in ("map", "ink")
L.Z_FLAT = CEL
SEED = int(A["seed"])
N2 = (DIR == "D" and MODE == "night" and A.get("n2", "1") == "1")      # round-2 night fix: darker, shaded, readable forms
L.EMIT_K = 0.35 if N2 else 1.0


def ekw(v):
    return {"ek": v} if N2 else {}


MOON = float(A.get("moon", "1.6"))
SKY = float(A.get("sky", "1.0"))
EXPO = float(A.get("expo", "0.0"))

LIME = (0.588, 1.0, 0.275)
PINKC = (1.0, 0.275, 0.588)
GL1 = (0.55, 1.0, 0.45, 1) if not CEL else (0.16, 0.66, 0.22, 1)
TWC = "twC" if DIR == "D" else "tw"       # the clinic band material key
BEAM = False                          # round 2: no beam / dark column over the helix (no centre tower)
D = DIR == "D"
PITCH = 24.0          # one lot (16 BU) + one street (8 BU)
LOT = 16.0
GRID = 20             # +- cells built (ordinary city beyond the 500 BU district shows at the hero horizon)
DISTRICT_R = 250.0

# ------------------------------------------------------------------ scene setup
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
coll = scene.collection
scene.render.resolution_x, scene.render.resolution_y = W, H
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_depth = "8"

# ------------------------------------------------------------------ materials per direction
NI = 2.0 if not CEL else 1.0


def mats():
    M = {}
    bands = (0.30, 0.58, 0.95, 0.20, 0.50)
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
    M["neon"] = L.make_material("neon", "neon", MODE, strength=5.0 if not CEL else 1.0)
    M["neon_p"] = L.make_material("neon_p", "neon", MODE, strength=34.0 if not CEL else 1.0, **ekw(0.07))
    M["neon_l"] = L.make_material("neon_l", "neon", MODE, strength=5.0 if not CEL else 1.0, **ekw(0.16))
    M["neon_s"] = L.make_material("neon_s", "neon", MODE, strength=9.0 if not CEL else 1.0, **ekw(0.3))
    M["ground"] = L.make_material("ground", "ground", MODE, bands=bands)
    M["hwin"] = L.make_material("hwin", "hwin", MODE, strength=3.0, **ekw(0.55))
    M["hwin_n"] = L.make_material("hwin_n", "hwin", MODE, strength=11.0, **ekw(0.55))
    return M


M = mats()
BUILD = {}


def mb(key, smooth=False):
    k = (key, smooth)
    if k not in BUILD:
        BUILD[k] = MB("%s_%s" % (key, "s" if smooth else "f"))
    return BUILD[k]


def build_all():
    for (key, smooth), b in BUILD.items():
        b.build(M[key], smooth, coll)


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


# ------------------------------------------------------------------ the shared lot plan
def plan():
    """One seeded plan for every direction: kind per lot, height per lot, the hospital cells, the park ring."""
    P = {}
    for j in range(-GRID, GRID + 1):
        for i in range(-GRID, GRID + 1):
            cx, cy = i * PITCH, j * PITCH
            r = math.hypot(cx, cy)
            r_ = hr(i, j, 1)
            if r < 36.0:
                kind = "plaza"
            elif 4 <= i <= 5 and -3 <= j <= -2:
                kind = "hosp"
            elif 40.0 < r <= 92.0 or (2 <= i <= 7 and -5 <= j <= 0):
                kind = "park"
            elif r <= DISTRICT_R:
                ordp = smoothstep(150.0, 245.0, r + (r_ - 0.5) * 40.0)
                kind = "ord" if hr(i, j, 2) < ordp else "solace"
            else:
                kind = "ord"
            h = 0.0
            if kind == "solace":
                h = (26.0 + 18.0 * smoothstep(100.0, 200.0, r) - 8.0 * smoothstep(200.0, 250.0, r)) * (0.62 + 0.62 * hr(i, j, 3))
            elif kind == "ord":
                far = smoothstep(180.0, 400.0, r)
                h = (24.0 + 44.0 * hr(i, j, 3) ** 1.5) * (1.0 - 0.3 * far)
            P[(i, j)] = dict(kind=kind, h=h, x=cx, y=cy, r=r)
    # secondary type for solace lots (direction picks the model)
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


def ground():
    g = mb("ground")
    ext = (GRID + 1) * PITCH + 800
    flat_poly(g, [(-ext, -ext, -0.05), (ext, -ext, -0.05), (ext, ext, -0.05), (-ext, ext, -0.05)], STREET_COL, (0.5, 1.0, 0, 1))
    for (i, j), p in PLAN.items():
        k = p["kind"]
        cx, cy = p["x"], p["y"]
        if k == "hosp":
            continue
        col = {"plaza": PAD_COL, "park": PARK_COL, "solace": PAD_COL, "ord": ORD_PAD}[k]
        if D and k == "solace" and BUNDLE.get((i, j)) == "C":
            col = PAD_C
        rough = 0.9 if k == "park" else 0.55
        z = 0.25
        box(g, cx - LOT / 2, cy - LOT / 2, 0.0, cx + LOT / 2, cy + LOT / 2, z, col, (rough, 0.0, 0, 1))
    # hospital pad (2x2 cells + the street between)
    hx, hy = 4.5 * PITCH, -2.5 * PITCH
    box(g, hx - 1.5 * PITCH + 4 - 0.0, hy - 1.5 * PITCH + 4, 0.0, hx + 1.5 * PITCH - 4, hy + 1.5 * PITCH - 4, 0.3,
        (0.62, 0.66, 0.64) if not CEL else (0.34, 0.42, 0.40), (0.5, 0.0, 0, 1))
    # plaza disc over the central 3x3 cells
    disc(g, 0, 0, 0.32, 40.0, 48, (0.10, 0.12, 0.11) if not CEL else (0.14, 0.22, 0.19), (0.5, 0.0, 0, 1))


def street_lines():
    n = mb("neon")
    for j in range(-GRID, GRID + 1):
        for i in range(-GRID, GRID + 1):
            p = PLAN[(i, j)]
            cx, cy = p["x"], p["y"]
            r = p["r"]
            if r > 330:
                continue
            solace = p["kind"] in ("plaza", "park", "solace", "hosp")
            col = (LIME[0] * 0.5, LIME[1] * 0.5, LIME[2] * 0.5) if solace else (0.9, 0.55, 0.25)
            if CEL:
                col = LIME if solace else (0.95, 0.7, 0.35)
            dim = 0.07 if not CEL else 1.0
            # dashed centre line of the street to the east and north of this lot
            for (dx, dy) in ((1, 0), (0, 1)):
                if p["kind"] == "hosp":
                    continue
                x0, y0 = cx + dx * PITCH / 2 + (dy * 0), cy + dy * PITCH / 2
                for s in range(-1, 2):
                    a = (x0 - (dy) * (s * 6.0 + 1.5), y0 + dx * (s * 6.0 - 1.5)) if False else None
                # dashes along the street running perpendicular to the step
                for s in range(4):
                    t = -LOT / 2 + 2 + s * 4.0
                    ax, ay = (x0, cy + t) if dx else (cx + t, y0)
                    bx, by = (x0, cy + t + 2.0) if dx else (cx + t + 2.0, y0)
                    strip(n, (ax, ay), (bx, by), 0.16, 0.06, col, (dim, 0, 0, 1))


# ------------------------------------------------------------------ trees and park
TREE_COL = [(0.02, 0.10, 0.03), (0.03, 0.14, 0.05), (0.015, 0.08, 0.05)] if not CEL else [(0.07, 0.26, 0.10), (0.10, 0.32, 0.12), (0.06, 0.22, 0.14)]


def tree(x, y, rr, h=None, z=0.25, glow=False):
    t = mb("plain")
    h = h or (5.0 + 5.0 * rr.random())
    r = 1.6 + 1.2 * rr.random()
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
        for k in range(10 if not feat else 5):
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
    if CEL:
        base = [(0.20, 0.16, 0.36), (0.24, 0.17, 0.38), (0.17, 0.17, 0.34), (0.27, 0.16, 0.32)]
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
    glassc = (0.04, 0.20, 0.11) if not CEL else (0.10, 0.34, 0.22)
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
    glassc = (0.04, 0.20, 0.11) if not CEL else (0.10, 0.34, 0.22)
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


# ------------------------------------------------------------------ the plaza and the helix landmark (identical in all directions)
def plaza():
    n = sd(48)
    cyl(mb("plain"), 0, 0, 0.3, 2.5, 12.0, sd(32), (0.38, 0.44, 0.42) if not CEL else (0.7, 0.78, 0.74), (0, 0, 0, 0.2))
    torus(mb("neon"), 0, 0, 2.55, 12.05, 0.28, sd(40), 5, LIME, (1.3 if not CEL else 1, 0, 0, 1))
    for R_, col, s in ((18.0, PINKC, 0.9), (24.0, LIME, 0.7), (31.0, LIME, 0.5), (37.0, LIME, 0.35)):
        torus(mb("neon"), 0, 0, 0.45, R_, 0.2, n, 4, col, (s if not CEL else 1, 0, 0, 1))
    for k in range(16):      # radial dashes: the plaza reads as a petri-dish / compass rose
        a = 2 * math.pi * k / 16
        strip(mb("neon"), (14.0 * math.cos(a), 14.0 * math.sin(a)), (17.0 * math.cos(a), 17.0 * math.sin(a)), 0.2, 0.5, LIME, (0.7 if not CEL else 1, 0, 0, 1))


def helix():
    """THE helix (2026-10-16 rulings): two strands, each a full 360 deg turn; per floor two sideways-oval windows (one inward
    to the walkway, one outward) whose outlines are truly horizontal / vertical; non-node windows translucent (faux interior);
    bow-tie walkways flush with the floors; no centre tower; lit lime/pink and the brightest thing in the district."""
    R, rt, z0, z1 = 7.5, 3.4, 2.5, 86.0
    pitch = z1 - z0                                   # one full turn per strand over the height
    steps = 140 if not CEL else 56
    nseg = 18 if not CEL else 10
    tube = (0.84, 0.88, 0.85) if not CEL else (0.88, 0.92, 0.90)

    def cpos(ph, z):
        t = 2 * math.pi * (z - z0) / pitch + ph
        return (R * math.cos(t), R * math.sin(t), z)

    for ph in (0.0, math.pi):
        pts, nr = [], []
        for k in range(steps + 1):
            z = z0 + (z1 - z0) * k / steps
            c = cpos(ph, z)
            pts.append(c)
            nr.append(L._unit((c[0], c[1], 0.0)))
        sweep(mb("tube", True), pts, nr, rt, nseg, tube, (0, 0, 0, 0.3))
        top = cpos(ph, z1)
        dome(mb("glass", True), top[0], top[1], z1, rt, nseg, GL1, (1.0, 0, 0, 1), rings=3)
        torus(mb("neon_s"), top[0], top[1], z1, rt + 0.05, 0.22, nseg, 5, LIME if ph == 0 else PINKC, (1.0, 0, 0, 1))
    # the crown halo: a floating pink ring over the two strand tops (as the HQ crown)
    torus(mb("neon_s"), 0, 0, z1 + 4.0, 11.5, 0.42, 40, 5, PINKC, (1.0, 0, 0, 1))
    torus(mb("neon"), 0, 0, z1 + 4.0, 9.2, 0.2, 40, 4, LIME, (1.0, 0, 0, 1))
    # floors: bridge deck + rungs + windows
    floor_h = 4.2
    nfl = int((z1 - z0 - 3.0) / floor_h)
    rr = random.Random(SEED + 99)
    for f in range(nfl):
        zf = z0 + 3.0 + f * floor_h
        a, c = cpos(0.0, zf), cpos(math.pi, zf)
        d = L._unit(L._sub(c, a))
        s = (-d[1], d[0], 0.0)
        m = L._mul(L._add(a, c), 0.5)
        pts6 = [L._add(a, L._mul(s, 2.6)), L._add(m, L._mul(s, 0.7)), L._add(c, L._mul(s, 2.6)), L._sub(c, L._mul(s, 2.6)), L._sub(m, L._mul(s, 0.7)), L._sub(a, L._mul(s, 2.6))]
        deck_t = 0.5
        # a flush bow-tie deck: slab (extruded polygon, the walkway melds into the floor level)
        poly = [(p[0], p[1]) for p in pts6]
        # make CCW
        area = sum(poly[i][0] * poly[(i + 1) % 6][1] - poly[(i + 1) % 6][0] * poly[i][1] for i in range(6))
        if area < 0:
            poly = poly[::-1]
        prism(mb("plain"), poly, zf - deck_t, zf, (0.8, 0.84, 0.82), (0, 0, 0, 0.4))
        col = LIME if f % 2 == 0 else PINKC                 # base-pair rungs: lime / pink alternate
        for q in range(6):
            p0, p1 = poly[q], poly[(q + 1) % 6]
            strip(mb("neon_s"), p0, p1, 0.13, zf + 0.04, col, (1.0 if not CEL else 1, 0, 0, 1))
        # floor ring on each tube (a lit line at the slab)
        # the two oval windows per floor per strand: inward (to the walkway) and outward
        for ph in (0.0, math.pi):
            zw = zf + 1.95
            ctr = cpos(ph, zw)
            tz = L._unit(L._sub(cpos(ph, zw + 0.2), cpos(ph, zw - 0.2)))
            rad = L._unit((ctr[0], ctr[1], 0.0))
            for side in (-1, 1):                              # -1 inward, +1 outward
                nrm = L._mul(rad, side)
                oval_window(mb("hwin"), mb("hwin_n"), mb("neon"), ctr, tz, nrm, rt, rr, f, ph, side)


def oval_window(mw, mn, mf, ctr, T, n, rt, rr, f, ph, side):
    """A horizontal-axis oval on the tube surface: outline exactly horizontal / vertical in the world (rays along -n)."""
    ca, cb = 1.85, 1.15                                       # half width, half height (wider than tall: a sideways oval)
    th = (-n[1], n[0], 0.0)

    def hit(dx, dz):
        q0 = (ctr[0] + n[0] * (rt + 3.0) + th[0] * dx, ctr[1] + n[1] * (rt + 3.0) + th[1] * dx, ctr[2] + dz)
        w = L._sub(q0, ctr)
        wp = L._sub(w, L._mul(T, L._dot(w, T)))
        d = (-n[0], -n[1], 0.0)
        dp = L._sub(d, L._mul(T, L._dot(d, T)))
        Aq = L._dot(dp, dp)
        Bq = 2 * L._dot(wp, dp)
        Cq = L._dot(wp, wp) - rt * rt
        disc_ = Bq * Bq - 4 * Aq * Cq
        if disc_ < 0:
            return None
        s = (-Bq - math.sqrt(disc_)) / (2 * Aq)
        P = L._add(q0, L._mul(d, s))
        r_ = L._sub(P, ctr)
        N = L._unit(L._sub(r_, L._mul(T, L._dot(r_, T))))
        return P, N
    node = (f % 5 == 2 and side > 0)                          # a few lit-lime "node" windows
    seed = rr.random()
    prm = (0.0, 0.0, 0.0, seed)
    if node:
        prm = (1.4, 1.0, 0.0, seed)
    else:
        v = rr.random()
        prm = (0.7 + 0.5 * rr.random(), 0.0 if v < 0.45 else 0.9, 0.7 if (0.45 <= v < 0.55) else 0.0, seed)
    ring = []
    N_ = 22 if not CEL else 14
    for k in range(N_):
        ang = 2 * math.pi * k / N_
        h = hit(ca * math.cos(ang), cb * math.sin(ang))
        h2 = hit(ca * 1.1 * math.cos(ang), cb * 1.17 * math.sin(ang))
        ring.append((h, h2, ang))
    if any(r[0] is None or r[1] is None for r in ring):
        return
    ch = hit(0.0, 0.0)
    mw_ = mn if node else mw
    lift = 0.05
    ci = mw_.v(L._add(ch[0], L._mul(ch[1], lift)), (1, 1, 1, 1), prm, (0.5, 0.5))
    ids = []
    for (h, h2, ang) in ring:
        ids.append(mw_.v(L._add(h[0], L._mul(h[1], lift)), (1, 1, 1, 1), prm, (0.5 + 0.5 * math.cos(ang), 0.5 + 0.5 * math.sin(ang))))
    for k in range(N_):
        mw_.f(ci, ids[k], ids[(k + 1) % N_]) if True else None
    # frame ring: a thin lit outline
    fcol = LIME if (node or f % 2 == 0) else (0.8, 1.0, 0.85)
    inner = [mf.v(L._add(r[0][0], L._mul(r[0][1], 0.06)), fcol, (0.9 if not CEL else 1, 0, 0, 1)) for r in ring]
    outer = [mf.v(L._add(r[1][0], L._mul(r[1][1], 0.06)), fcol, (0.9 if not CEL else 1, 0, 0, 1)) for r in ring]
    for k in range(N_):
        mf.f(inner[k], outer[k], outer[(k + 1) % N_], inner[(k + 1) % N_])


def helix_beam():
    """The soft lime beam up from the crown (as on the plate), a cone of emission fading to nothing."""
    b = mb("neon")
    n = 12
    z0, z1 = 88.0, 150.0
    rings = []
    for k, (z, r, a) in enumerate(((z0, 2.6, 0.30), (z0 + 20, 4.0, 0.10), (z0 + 45, 5.5, 0.03), (z1, 7.0, 0.0))):
        rings.append([b.v((r * math.cos(2 * math.pi * q / n), r * math.sin(2 * math.pi * q / n), z), LIME, (a if not CEL else a * 1.6, 0, 0, 1)) for q in range(n + 1)])
    for k in range(3):
        for q in range(n):
            b.f(rings[k][q], rings[k][q + 1], rings[k + 1][q + 1], rings[k + 1][q])


# ------------------------------------------------------------------ the hospital Site (non-HQ landmark)
def hospital():
    hx, hy = 4.5 * PITCH, -2.5 * PITCH
    n = sd(28)
    porc = (0.80, 0.84, 0.81) if not CEL else (0.88, 0.92, 0.90)
    if N2:
        porc = (0.34, 0.32, 0.29)
    # helipad
    def helipad(x, y, z, r):
        torus(mb("neon"), x, y, z, r, 0.2, n, 4, LIME, (1.0 if not CEL else 1, 0, 0, 1))
        for sx in (-1, 1):
            box(mb("neon"), x + sx * r * 0.32 - 0.25, y - r * 0.4, z, x + sx * r * 0.32 + 0.25, y + r * 0.4, z + 0.1, LIME, (1.0 if not CEL else 1, 0, 0, 1))
        box(mb("neon"), x - r * 0.32, y - 0.25, z, x + r * 0.32, y + 0.25, z + 0.1, LIME, (1.0 if not CEL else 1, 0, 0, 1))
    # the pad ring + beacons
    torus(mb("neon"), hx, hy, 0.4, 35.0, 0.22, sd(48), 4, LIME, (0.8 if not CEL else 1, 0, 0, 1))
    glassc = (0.04, 0.20, 0.11) if not CEL else (0.10, 0.34, 0.22)
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
    cross_shape(mb("neon_s"), hx, hy, cz + 9.0, 11.0, 3.6, math.radians(45.0), LIME, (1.0 if not CEL else 1, 0, 0, 1), depth=0.5)
    cyl(mb("plain"), hx, hy, cz, cz + 3.4, 0.35, 5, (0.6, 0.6, 0.6), (0, 0, 0, 0.5), cap=False)
    # a pink beacon on the mast
    sphere(mb("neon"), hx, hy, cz + 15.4, 0.7, 6, PINKC, (1.0, 0, 0, 1))
    # perimeter trees
    rr = random.Random(5)
    for k in range(18):
        a = 2 * math.pi * k / 18
        tree(hx + 30.0 * math.cos(a), hy + 30.0 * math.sin(a), rr, h=4.5, z=0.3)


# ------------------------------------------------------------------ lights, world, camera
def add_light(kind, loc, col, power, size=1.0, rot=None, **kw):
    ld = bpy.data.lights.new(kind, kind)
    ld.color = col
    ld.energy = power
    if kind == "SUN":
        ld.angle = kw.get("angle", 0.05)
    elif kind == "AREA":
        ld.size = size
    else:
        ld.shadow_soft_size = size
    ob = bpy.data.objects.new(kind, ld)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    coll.objects.link(ob)
    return ob


def world():
    w = bpy.data.worlds.new("w")
    scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    nt.links.new(tc.outputs["Generated"], sep.inputs[0]) if False else None
    nt.links.new(tc.outputs["Window"], sep.inputs[0]) if False else None
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    nt.links.new(geo.outputs["Incoming"], sep.inputs[0])
    mp = nt.nodes.new("ShaderNodeMath")
    mp.operation = "ABSOLUTE"
    nt.links.new(sep.outputs[2], mp.inputs[0])
    nt.links.new(mp.outputs[0], ramp.inputs[0])
    if CEL:
        ramp.color_ramp.elements[0].color = (0.05, 0.03, 0.10, 1)
        ramp.color_ramp.elements[1].color = (0.02, 0.015, 0.05, 1)
        bg.inputs[1].default_value = 1.0
    else:
        ramp.color_ramp.elements[0].color = ((0.035, 0.022, 0.07, 1) if not N2 else (0.07 * SKY, 0.07 * SKY, 0.16 * SKY, 1))
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[1].color = ((0.002, 0.003, 0.010, 1) if not N2 else (0.018 * SKY, 0.026 * SKY, 0.06 * SKY, 1))
        ramp.color_ramp.elements[1].position = 0.5
        bg.inputs[1].default_value = 1.0
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    nt.links.new(bg.outputs[0], out.inputs[0])
    if not CEL:
        vol = nt.nodes.new("ShaderNodeVolumePrincipled")
        vol.inputs["Color"].default_value = (0.55, 0.45, 0.8, 1)
        vol.inputs["Density"].default_value = 0.00038 if not N2 else 0.00018
        vol.inputs["Anisotropy"].default_value = 0.35
        nt.links.new(vol.outputs[0], out.inputs[1])


def lights():
    if CEL:
        add_light("SUN", (0, 0, 300), (0.78, 0.80, 1.0), 2.6, rot=(math.radians(52), 0, math.radians(-125)), angle=0.02)
        add_light("SUN", (0, 0, 300), (0.9, 0.4, 0.8), 0.5, rot=(math.radians(60), 0, math.radians(60)), angle=0.02)
        return
    add_light("SUN", (0, 0, 300), (0.55, 0.6, 1.0), 0.28 if not N2 else MOON, rot=(math.radians(58), 0, math.radians(-125)), angle=0.04)
    if N2:
        add_light("SUN", (0, 0, 300), (0.75, 0.55, 0.95), 0.35 * MOON / 1.6, rot=(math.radians(55), 0, math.radians(55)), angle=0.1)
    add_light("POINT", (0, 0, 40), LIME, 6e4 if not N2 else 3.5e4, size=6)
    add_light("POINT", (0, 0, 70), (1.0, 0.3, 0.6), 3e4, size=6)
    add_light("POINT", (0, 0, 8), (0.9, 1.0, 0.9), 1.2e4, size=4)
    hx, hy = 4.5 * PITCH, -2.5 * PITCH
    add_light("POINT", (hx, hy, 55), LIME, 4e4, size=5)
    add_light("POINT", (hx, hy, 14), (0.9, 1.0, 0.95), 1.5e4, size=5)
    if DIR == "C":
        rc = random.Random(9)
        for k in range(16):
            a = 2 * math.pi * k / 16 + 0.1
            r = 70 + 90 * rc.random()
            add_light("POINT", (r * math.cos(a), r * math.sin(a), 38), (0.85, 1.0, 0.95), 5e4, size=4)
    if D:
        for (gi, gj, x, y) in BUNDLE_SEEDS:
            if BUNDLE_KIT[(gi, gj)] == "C":
                add_light("POINT", (x * PITCH, y * PITCH, 38), (0.85, 1.0, 0.95), 5e4 if not N2 else 1.2e4, size=4)
    rr = random.Random(3)
    for k in range(14):
        a = 2 * math.pi * k / 14 + 0.2
        r = 60 + 25 * rr.random()
        add_light("POINT", (r * math.cos(a), r * math.sin(a), 10), LIME if k % 3 else PINKC, 6e3, size=2)


def camera():
    cam = bpy.data.cameras.new("cam")
    ob = bpy.data.objects.new("cam", cam)
    coll.objects.link(ob)
    scene.camera = ob
    if CEL:
        tgt = Vector((52.0, -26.0, 22.0))
        el = math.radians(38.0)
        az = math.radians(-135.0)
        dist = 900.0
        ob.location = tgt + Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))) * dist
        cam.type = "ORTHO"
        cam.ortho_scale = float(A["scale"])
        cam.clip_start, cam.clip_end = 10, 3000
    else:
        tgt = Vector((14.0, -4.0, 36.0))
        el = math.radians(37.0)
        az = math.radians(-128.0)
        dist = 235.0
        ob.location = tgt + Vector((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))) * dist
        cam.lens = 27.0
        cam.sensor_width = 36.0
        cam.clip_start, cam.clip_end = 1, 4000
    if A["cam"]:
        v = [float(x) for x in A["cam"].split(",")]
        ob.location = (v[0], v[1], v[2])
        tgt = Vector((v[3], v[4], v[5]))
    d = tgt - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# ------------------------------------------------------------------ assemble
t_start = time.time()
ground()
street_lines()
park()
plaza()
helix()
if BEAM:
    helix_beam()
hospital()
for (i, j), p in sorted(PLAN.items()):
    if p["kind"] == "ord":
        ord_building(i, j, p)
    elif p["kind"] == "solace":
        (KITS[kit_for(i, j)])(i, j, p)
if DIR in ("A", "D"):
    a_bridges()
build_all()
world()
lights()
camera()
print("BUILD %.1f s, %d builders" % (time.time() - t_start, len(BUILD)), flush=True)

# ------------------------------------------------------------------ render settings
out_path = os.path.abspath(A["out"])
os.makedirs(os.path.dirname(out_path), exist_ok=True)
scene.render.filepath = out_path
try:
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = (-0.6 if not N2 else EXPO) if not CEL else 0.0
except Exception as e:
    print("view transform", e)

if CEL:
    scene.render.engine = "BLENDER_EEVEE"
    if MODE == "ink":
        scene.render.image_settings.color_depth = "16"
        scene.render.filter_size = 0.0
        scene.display_settings.display_device = "sRGB"
    ee = scene.eevee
    ee.taa_render_samples = 24
    if MODE == "ink":
        ee.taa_render_samples = 1
    for a_, v_ in (("use_raytracing", False), ("use_shadows", True), ("use_volumetric_shadows", False)):
        try:
            setattr(ee, a_, v_)
        except Exception:
            pass
    scene.render.use_freestyle = (MODE == "map" and A.get("freestyle", "0") == "1")
    vl = bpy.context.view_layer
    vl.use_freestyle = scene.render.use_freestyle
    fs = vl.freestyle_settings
    fs.crease_angle = math.radians(70)
    for old in list(fs.linesets):
        fs.linesets.remove(old)
    ls = fs.linesets.new("ink")
    ls.select_by_visibility = True
    ls.select_by_edge_types = True
    ls.visibility = "VISIBLE"
    ls.select_silhouette = True
    ls.select_border = True
    ls.select_crease = True
    ls.select_edge_mark = False
    st = ls.linestyle
    st.color = (0.03, 0.015, 0.08) if not A.get("inkdbg") else (1, 0, 0)
    st.thickness = 4.4 * (W / 1920.0)
    st.thickness_position = "CENTER"
    scene.render.line_thickness_mode = "ABSOLUTE"
    scene.render.line_thickness = 1.0
    try:
        m = st.geometry_modifiers.new("wob", "SINUS_DISPLACEMENT")
        m.wavelength = 34.0 * (W / 1920.0)
        m.amplitude = 1.8 * (W / 1920.0)
        m.phase = 0.0
    except Exception as e:
        print("wobble", e)
    try:
        pass
    except Exception:
        pass
else:
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.samples = int(A["spp"])
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.02
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    try:
        cy.denoising_use_gpu = True
    except Exception:
        pass
    cy.max_bounces = 7
    cy.diffuse_bounces = 3
    cy.glossy_bounces = 4
    cy.transmission_bounces = 6
    cy.volume_bounces = 1
    cy.volume_step_rate = 1.5
    cy.volume_preview_step_rate = 1.5
    cy.sample_clamp_indirect = 8.0
    cy.sample_clamp_direct = 0
    cy.device = "GPU" if A.get("device", "GPU") == "GPU" else "CPU"
    pref = bpy.context.preferences.addons["cycles"].preferences
    pref.compute_device_type = "HIP"
    pref.get_devices()
    for d in pref.devices:
        d.use = d.type == "HIP"
    print("DEVICES", [(d.name, d.type, d.use) for d in pref.devices], flush=True)

t0 = time.time()
bpy.ops.render.render(write_still=True)
print("RENDER_SECONDS %.1f" % (time.time() - t0), flush=True)
if D:
    import collections
    cnt = collections.Counter(v for (k, v) in BUNDLE.items() if PLAN[k]["kind"] in ("solace", "park") and math.hypot(*[PLAN[k]["x"] - 52, PLAN[k]["y"] + 26]) < 170)
    print("BUNDLES", len(BUNDLE_SEEDS), "sizes", sorted(BUNDLE_SIZES.values()), "kits in view", dict(cnt), flush=True)
