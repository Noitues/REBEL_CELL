"""Build sd_kit.py (the district park kit as an importable module) from the district's sd_main.py (read only)."""
import os

SRC = r"D:\rc_art\art-pass\docs\concepts\solace_vertical\district\scripts\sd_main.py"
DST = r"D:\rc_art\art-pass\docs\concepts\solace_vertical\hq\scripts\sd_kit.py"
S = open(SRC, encoding="utf-8").read()


def seg(a, b):
    i = S.index(a)
    j = S.index(b, i + 1) if b else len(S)
    return S[i:j]


def sub(text, old, new, count=1):
    assert old in text, "missing: " + old[:70]
    return text.replace(old, new, count)


HEADER = '''"""Solace district kit for the HQ v5 plates (park, 3-tier plinth, A/B/C bundles, the C hospital), as a module.

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
RB0 = 195.0              # park boundary radius (district units; x SL = BU), +-25 / 15 wobble
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

'''

MATS = seg("NI = 2.0 if not CEL else 1.0", "# ------------------------------------------------------------------ the shared lot plan")
MATS = sub(MATS, "M = mats()\nBUILD = {}\n", "M = None\nBUILD = {}\nSCOPE = \"lawn\"\n")
MATS = sub(MATS, '''def mb(key, smooth=False):
    k = (key, smooth)
    if k not in BUILD:
        BUILD[k] = MB("%s_%s" % (key, "s" if smooth else "f"))
    return BUILD[k]


def build_all():
    for (key, smooth), b in BUILD.items():
        b.build(M[key], smooth, coll)
''', '''def mb(key, smooth=False):
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
''')

PLAN = '''# ------------------------------------------------------------------ the lot plan (lawn units)
def Rb(th):
    """The park's organic boundary radius at angle th."""
    return RB0 + 25.0 * math.sin(2 * th + 0.7) + 15.0 * math.sin(5 * th + 2.1)


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

'''

COLORS = seg("# ------------------------------------------------------------------ ground, streets, pads", "def ground():")
TREES = seg("# ------------------------------------------------------------------ trees and park", "# ------------------------------------------------------------------ the plaza and the helix landmark")
HOSP = seg("# ------------------------------------------------------------------ the hospital Site", "# ------------------------------------------------------------------ lights, world, camera")
HOSP = sub(HOSP, "hx, hy = 4.5 * PITCH, -2.5 * PITCH", "hx, hy = HX, HY")
HOSP = sub(HOSP, "math.radians(-45.0 if RAID else 45.0)", "math.radians(CROSS_ANG)")
R4 = seg("# ------------------------------------------------------------------ round 4: one continuous park", "# ------------------------------------------------------------------ assemble")
R4 = sub(R4, "HX, HY = 4.5 * PITCH, -2.5 * PITCH\n", "")
R4 = sub(R4, "math.hypot(x, y) - 38.0, math.hypot(x - HX, y - HY) - 36.0", "math.hypot(x, y) - (PL_R + 6.0), math.hypot(x - HX, y - HY) - 36.0")
R4 = sub(R4, "blocked = lambda x, y: 84 < x < 132 and -84 < y < -36", "blocked = lambda x, y: abs(x - HX) < 24 and abs(y - HY) < 24")
R4 = sub(R4, "(not out_goal) and rn < 46:", "(not out_goal) and rn < PL_R + 10.0:")
R4 = sub(R4, "if math.hypot(x, y) < 44.0 or math.hypot(x - HX, y - HY) < 42.0:", "if math.hypot(x, y) < PL_R + 8.0 or math.hypot(x - HX, y - HY) < 42.0:")
R4 = sub(R4, "SR = 36.0       # round 5: the stair feet sit on the old N-S / E-W corridors at 36 BU", "SR = PL_R       # the stair feet in lawn units (the plinth's own stair is PL_FOOT in plinth units)")
R4 = sub(R4, "r0, r1 = TIERS[-1][0] - 0.2, SR", "r0, r1 = TIERS[-1][0] - 0.2, PL_FOOT")
R4 = sub(R4, "    base = 0.2\n", "    base = 0.0\n")
R4 = sub(R4, "def plinth_build():", "def _plinth_build():")
R4 = sub(R4, "def park_world():", '''def plinth_build():
    global SCOPE
    SCOPE = "plinth"
    try:
        _plinth_build()
    finally:
        SCOPE = "lawn"


def park_world():''')
R4 = sub(R4, "((0.0, 0.0, 40.0, 0.4), (HX, HY, 38.0, 1.9))", "((0.0, 0.0, PL_R + 8.0, 0.4), (HX, HY, 38.0, 1.9))")
R4 = sub(R4, "x0, y0 = 46 * math.cos(th0), 46 * math.sin(th0)", "x0, y0 = (PL_R + 8.0) * math.cos(th0), (PL_R + 8.0) * math.sin(th0)")
R4 = sub(R4, "_nodes_route((132.0, -60.0), (1, 0), True,", "_nodes_route((HX + 24.0, HY), (1, 0), True,")
R4 = sub(R4, "_nodes_route((84.0, -60.0), (-1, 0), False,", "_nodes_route((HX - 24.0, HY), (-1, 0), False,")
R4 = sub(R4, "r = math.sqrt(rr.random()) * 205.0", "r = math.sqrt(rr.random()) * RB0")
R4 = sub(R4, "ntl = int(2 * math.pi * 205 / 4.5)", "ntl = int(2 * math.pi * RB0 / 4.5)")
R4 = sub(R4, "hr(k[0], k[1], 9) < 0.2", "hr(k[0], k[1], 9) < 0.45")
R4 = sub(R4, "GRAVEL = _pc(", "LAWN_A = tuple(c * 2.4 for c in LAWN_A); LAWN_B = tuple(c * 2.4 for c in LAWN_B)\nGRAVEL = _pc(")
R4 = sub(R4, "poly + [poly[0]], 0.42, 0.16,", "poly + [poly[0]], 0.9, 0.16,")
R4 = sub(R4, "_ribbon(mb(\"neon\"), pts, 0.2, 0.2, LIME,", "_ribbon(mb(\"neon\"), pts, 0.75, 0.2, LIME,")
R4 = sub(R4, "off[q:q + 3], 0.16, 0.2,", "off[q:q + 3], 0.5, 0.2,")
R4 = sub(R4, "TIERS = ((35.0, 1.1), (29.5, 2.2), (24.0, 3.3))", "TIERS = ((35.0, TIER_H / 3.0), (29.5, TIER_H * 2.0 / 3.0), (24.0, TIER_H))")

TAIL = '''

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
'''

out = HEADER + MATS + PLAN + COLORS + TREES + HOSP + R4 + TAIL
open(DST, "w", encoding="utf-8").write(out)
print("wrote", DST, len(out))
