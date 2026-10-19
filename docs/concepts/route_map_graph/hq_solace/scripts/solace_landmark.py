"""SOLACE LANDMARK: THE TWIN HELIX (tube helix v3), an importable landmark module. Pure Python (no bpy, no numpy).

ENTRY POINTS
    import solace_landmark as SL
    info = SL.build(ctx)                       # THE CITY HOOK (spec 8.6c): ctx = landmarks.landmark_ctx("solace")
                                               #   -> dict(label=(x, y, z), crown=(x, y, z), hue=(r, g, b))
    hooks = SL.build(K, rooms=True, rail=False)    # HQ netrun kit (spec 8.5): K as in meridian_landmark.py
    K2 = SL.place(K, origin=(hx, hy, 0.0), k=SL.K_UNITS * k_fit)    # drop the HQ build into a one-city lot
    SL.landmark_info()                         # constants for the checks (spec 12.2)
    build() dispatches: a ctx with SURF and no A is the city; anything with A is the HQ kit.

WHAT IT BUILDS
  City scale (a port of landmarks.solace(); same rules, same lights):
    plinth       drum r 12.0, z 0..2.5, with a lit hue ring at z 2.55
    helix        two smooth swept tubes (tube r 3.4, centreline radius 7.5, 16 sides, 90 steps), z 2.5..86, one full
                 turn per 62 BU of height (phase 0 and pi), porcelain tint, porthole texture through the SMOOTH
                 accumulator's uv / window arguments, a dome crown cap in the hue on each tube
    bridges      one bow-tie skybridge per 4.2 BU of height between the tubes (wide 2.6 each side at the tubes,
                 0.7 at the waist), hue edges
    beacons      one red beacon per tube top
    lights       a cool-white key from the camera side and a hue fill (both scaled by CP.SOLACE_LIFT)
  HQ scale (reduced port of hq_solace/scripts/hq_build.py, see NOTES in the hand-off): the two strand tubes, the
    downlight rings, the mint seam, route-floor bow-tie bridges, the crown with THE GENOME CORE and the pink halo
    ring, the dark plaza podium with the lit entry and the SOLACE name, the ground spots and the rim. The node
    cutaway windows, office floors and interior-mapping atlas are NOT ported (Blender material graphs / hq_office).
    Route rooms are cut by K.room_shell when the corp graph module G is given (slots come from G, spec 8.4).

UNITS / PLACING IN THE CITY
    City build: world BU (1 lot = 6 BU), x east, y north, z up, geometry around ctx.hq. It stays inside a drum of
    radius 12.0 BU (the helix reaches 7.5 + 3.4 = 10.9; the plinth 12.0), far inside the landmark clearance
    (landmark_r 5.6 lots = 33.6 BU).
    HQ build: HQ-kit units (1 storey = 8 BU) around (0, 0, 0). place() maps it to one-city units
    (k_units 0.2375, spec 8.6) and `k_fit` for the lot (spec 8.6); lights x k^2.

SEEDS
    The city build has no random draws (as the built-in). The HQ build uses art streams named "landmark.solace.<use>"
    derived from ctx.seed / K seed by fnv1a64 + splitmix64 (spec 3.5); the legacy literal 6330 / 6331 is kept as
    LEGACY_SEEDS for golden-image parity only.

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

# ---------------------------------------------------------------- constants (spec 8.5, GDD 11.7 working names)
CORP = "solace"
CENTRAL_SERVER_NAME = "THE GENOME CORE"
K_UNITS = 0.2375                       # HQ kit storey 8 BU -> one floor 1.9 BU (spec 8.6)
LEAF = (0.588, 1.0, 0.275)             # Solace leaf #96FF46 (HQ preset), linear-ish as the HQ palette uses it
PINK = (1.0, 0.275, 0.588)
LEGACY_SEEDS = {"windows": 6330, "podium": 6331, "bridge": 6420}

# city-scale numbers (landmarks.solace)
C_PLINTH_R = 12.0
C_PLINTH_Z = (0.0, 2.5)
C_R, C_RT = 7.5, 3.4                    # helix centreline radius, tube radius
C_Z0, C_Z1 = 2.5, 86.0
C_PITCH = 62.0
C_STEPS, C_NSEG = 90, 16
C_BRIDGE_STEP = 4.2
C_CROWN_LABEL_DZ = 12.0
TUBE_COL = (0.82, 0.86, 0.84)
WIN_TINT = (0.82, 1.0, 0.88)


# ---------------------------------------------------------------- seeds
def _fnv1a64(data):
    h = 0xCBF29CE484222325
    for b in data.encode("utf-8"):
        h ^= b
        h = (h * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def _splitmix64(x):
    x = (x + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    z = x
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return z ^ (z >> 31)


def art_rng(seed, stream, *keys):
    """Named per-object stream (spec 3.5 rule 3): keyed by content ids, never by draw order."""
    txt = "[" + ",".join(repr(x) for x in (seed, "art/landmark." + CORP + "." + stream) + tuple(keys)) + "]"
    return random.Random(_splitmix64(_fnv1a64(txt)))


# ---------------------------------------------------------------- small vector helpers (tuples)
def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _mul(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / n, a[1] / n, a[2] / n)


def _lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t)


# ================================================================== placing (HQ kit -> city units)
def _footprint_radius(ctx):
    fp = getattr(ctx, "footprint", None)
    if isinstance(fp, (int, float)):
        return float(fp)
    if isinstance(fp, (tuple, list)) and fp:
        try:
            return float(max(fp))
        except (TypeError, ValueError):
            return None
    return None


def _build_city(ctx):
    SURF, SMOOTH, NEON = ctx.SURF, ctx.SMOOTH, ctx.NEON
    box, cyl, dome, bar, ring_line, sc, spot_at = ctx.box, ctx.cyl, ctx.dome, ctx.bar, ctx.ring_line, ctx.sc, ctx.spot_at
    hx, hy = ctx.hq
    D = ctx.district
    lift = getattr(ctx.CP, "SOLACE_LIFT", 1.0)
    R, rt, z0, z1 = C_R, C_RT, C_Z0, C_Z1
    pitch, steps, nseg = C_PITCH, C_STEPS, C_NSEG

    # the plinth drum and its lit ring
    cyl(SURF, hx, hy, C_PLINTH_Z[0], C_PLINTH_Z[1], C_PLINTH_R, 24, (0.38, 0.44, 0.42),
        wc=D["win"][0], wl=0.4, wm=1, bid=0.2)
    ring_line(NEON, hx, hy, 2.55, C_PLINTH_R + 0.05, 0.35, D["hue"], n=24)

    def cpos(ph, z):
        t = 2 * math.pi * (z - z0) / pitch + ph
        return (hx + R * math.cos(t), hy + R * math.sin(t), z)

    for ph in (0.0, math.pi):
        rings = []
        for k in range(steps + 1):
            z = z0 + (z1 - z0) * k / steps
            c = cpos(ph, z)
            tng = _unit(_sub(cpos(ph, z + 0.2), cpos(ph, z - 0.2)))
            nrm = _unit((c[0] - hx, c[1] - hy, 0.0))
            bnm = _unit(_cross(tng, nrm))
            nrm = _unit(_cross(bnm, tng))
            rings.append([tuple(c[i] + (nrm[i] * math.cos(2 * math.pi * m / nseg)
                                        + bnm[i] * math.sin(2 * math.pi * m / nseg)) * rt for i in range(3))
                          for m in range(nseg)])
        circ = 2 * math.pi * rt
        for k in range(steps):
            v0 = (z1 - z0) * k / steps
            v1 = (z1 - z0) * (k + 1) / steps
            for m in range(nseg):
                m1 = (m + 1) % nseg
                u0, u1 = circ * m / nseg, circ * (m + 1) / nseg
                SMOOTH.face([rings[k][m], rings[k][m1], rings[k + 1][m1], rings[k + 1][m]], TUBE_COL,
                            [(u0, v0), (u1, v0), (u1, v1), (u0, v1)], WIN_TINT, 0.62, 2, 0.3 + ph * 0.1, 0)
        top = cpos(ph, z1)
        dome(SMOOTH, top[0], top[1], z1, rt, sc(D["hue"], 0.5), n=nseg, rings=4)      # crown cap

    # bow-tie bridges, one per floor (every 4.2 BU): wide at the tubes, pinched at the axis, hue edges
    z = z0 + 3.0
    while z < z1 - 2:
        a, c = cpos(0.0, z), cpos(math.pi, z)
        d = _unit(_sub(c, a))
        s = (-d[1], d[0], 0.0)
        m = _mul(_add(a, c), 0.5)
        pts = [_add(a, _mul(s, 2.6)), _add(m, _mul(s, 0.7)), _add(c, _mul(s, 2.6)),
               _sub(c, _mul(s, 2.6)), _sub(m, _mul(s, 0.7)), _sub(a, _mul(s, 2.6))]
        SURF.face(pts, (0.7, 0.75, 0.72))
        for i in range(6):
            bar(NEON, _add(pts[i], (0, 0, 0.05)), _add(pts[(i + 1) % 6], (0, 0, 0.05)), 0.14, D["hue"])
        z += C_BRIDGE_STEP

    # red beacons on the two tube tops
    for ph in (0.0, math.pi):
        c = cpos(ph, z1 + rt)
        box(NEON, c[0] - 0.5, c[1] - 0.5, c[2], c[0] + 0.5, c[1] + 0.5, c[2] + 1.2, (1.0, 0.25, 0.25))

    # lights: a cool-white key from the camera side, a hue fill (designer r3b: a little brighter via SOLACE_LIFT)
    spot_at((hx, hy, 40), (hx + 70, hy - 70, 10), (0.85, 1.0, 0.9), 1.6e6 * lift, 40)
    spot_at((hx, hy, 50), (hx - 50, hy - 80, 5), D["hue"], 1.2e6 * lift, 36)

    r = _footprint_radius(ctx)
    if r is not None and r < C_PLINTH_R:
        print("SOLACE warning: footprint radius", r, "< plinth radius", C_PLINTH_R, flush=True)
    return dict(label=(hx, hy, z1 + C_CROWN_LABEL_DZ), crown=(hx, hy, z1 + 3), hue=D["hue"])


# ================================================================== HQ KIT BUILD (reduced port of hq_build.py)
def build(K, rooms=True, rail=False):
    """City hook: build(ctx) -> dict(label, crown, hue). HQ kit: build(K, rooms, rail) -> hooks."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return _build_city(K)
    return build_hq(K, rooms, rail)


def landmark_info():
    """Constants for the pipeline checks (spec 12.2 / 8.6b). Lengths in city BU unless noted."""
    return dict(
        corp=CORP,
        central_server_name=CENTRAL_SERVER_NAME,
        footprint_bu=2.0 * C_PLINTH_R,                      # drum diameter (plinth); the helix spans 2 * (7.5 + 3.4)
        footprint_radius_bu=C_PLINTH_R,
        tier_heights=dict(plinth_top=C_PLINTH_Z[1], helix_base=C_Z0, helix_top=C_Z1,
                          crown_label=C_Z1 + C_CROWN_LABEL_DZ, bridge_step=C_BRIDGE_STEP),
        pass_indices=dict(compound=1, rooms=5, movers=6),   # HQ kit object pass indices (spec 8.1)
        hue=None,                                           # the district hue comes from ctx.district at build time
    )


# the ground lobby: south face of the plinth drum (the face the overview camera sees)
ENTRY = {"entry": [0.0, -C_PLINTH_R, 0.0], "entry_nrm": [0.0, -1.0]}

# FACE_OUTLINE (BU, CCW): plinth drum C_PLINTH_R = 12.0 - sampled every 10 deg.
FACE_OUTLINE = [
    [12.0, 0.0], [11.82, 2.08], [11.28, 4.1], [10.39, 6.0],
    [9.19, 7.71], [7.71, 9.19], [6.0, 10.39], [4.1, 11.28],
    [2.08, 11.82], [0.0, 12.0], [-2.08, 11.82], [-4.1, 11.28],
    [-6.0, 10.39], [-7.71, 9.19], [-9.19, 7.71], [-10.39, 6.0],
    [-11.28, 4.1], [-11.82, 2.08], [-12.0, 0.0], [-11.82, -2.08],
    [-11.28, -4.1], [-10.39, -6.0], [-9.19, -7.71], [-7.71, -9.19],
    [-6.0, -10.39], [-4.1, -11.28], [-2.08, -11.82], [0.0, -12.0],
    [2.08, -11.82], [4.1, -11.28], [6.0, -10.39], [7.71, -9.19],
    [9.19, -7.71], [10.39, -6.0], [11.28, -4.1], [11.82, -2.08]
]


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
    return _hq_module("hq_build.py", "solace").build(K)
