"""REBEL_CELL / DISPATCH landmark: THE MAINFRAME BLADE SIGN on a Tokyo-canyon shop front (no landmark building). Reusable module.

ENTRY POINTS
    import rebel_cell_landmark as RL
    d = RL.build(ctx)                      # city hook: ctx = landmarks.landmark_ctx("rebel_cell")
                                           #   -> dict(label=(x, y, z), crown=None, hue=(r, g, b))
    hooks = RL.build(K, rooms=True, rail=False)    # HQ netrun (option A section); K as in meridian_landmark.py
    K2 = RL.place(K, origin=(hx, hy, 0.0), k=0.2375)   # wrap K to drop the kit build into the one city
    info = RL.landmark_info()              # constants for check 12.2 (landmark ratio) and 8.6b

What it builds (city hook, port of landmarks.rebel_cell, spec 8.5 / 8.6c)
  No building, no tower, no crown beam (designer). The landmark is the district (building language "tenement", the
  fist in red windows by the zoning crest rule) plus the red MAINFRAME blade sign (3 x 12 BU, z 2.4 .. 14.4, the sign's
  own 1:4 aspect, texture mainframe_blade.png). Rule: the REBEL_CELL building nearest the HQ lot (the Cell's anchor),
  at least 10 BU tall, not drowned, with a camera-facing street face >= 4 BU long, carries it at that face's corner,
  out over the street. Ties break by (distance, building key, face index). Also: a red wash strip on the shop front and
  one red spot (3.0e4, cone 70). The sign quad is appended to ctx.station["signs"] as (four corners, image path) for the
  city renderer (the built-in used the module global SIGNS); ctx.station["mainframe"] gets the sign's anchor point.

What it builds (HQ netrun, spec 8.4 / 8.5): option A, "three stacked lanes in one section" (hq_build_A.py, non-v3
  path): lane buildings (ground floor = street rooms, roof = rooftop rooms), detour huts on a steel frame, the earth
  cut open (service tunnel lane R, deeper detour level), the switch column and service shaft up to DISPATCH, the
  rooms through K.room_shell, start hut, walkways, tunnel / sodium / roof lights, a rim from the city. The district
  (rc_district), the alley (rc_alley) and the sewer v3 are NOT supplied; they come in through K hooks (see build_hq).
  Topology (G.ROOM, G.PATH ...) is MOCK route data per spec 8.4; the pipeline must feed slots from the game graph.

UNITS / PLACING
  City hook: world BU (x east, y north, z up; dry street z 0), no scaling. build_hq: HQ-kit units (1 storey = 8 BU);
  wrap with place(K, origin, k=0.2375) for the one city (spec 8.6). Rebel Cell has no lot-filling compound: the sign
  sits on a map building, so k_fit does not apply (ASSUMPTION; see landmark_info).

SEEDS
  Named streams via _rng(seed, name): random.Random(seed * 1000003 + sum(ord)) with seed = ctx.seed
  (CP.SEEDS["landmark"]). The city hook is fully rule-based and draws nothing; the stream helper serves build_hq.

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

# ------------------------------------------------------------------ constants (names per GDD 11.7 working names)
CORP = "rebel_cell"
CENTRAL_SERVER_NAME = "DISPATCH"
LANDMARK_NAME = "THE MAINFRAME BLADE SIGN"
K_UNITS = 0.2375
CITY_FOOTPRINT_BU = None          # ASSUMPTION: no lot footprint (ctx.footprint is None for rebel_cell); sign only
SIGN_W = 3.0                      # BU out over the street
SIGN_Z = (2.4, 14.4)              # BU, bottom / top of the blade
SIGN_TEX = "mainframe_blade.png"
SIGN_RED = (1.0, 0.16, 0.12)
SPOT_RED = (1.0, 0.12, 0.08)
SPOT_POWER = 3.0e4
SPOT_CONE = 70.0
MIN_BUILDING_H = 10.0             # BU
MIN_FACE_LEN = 4.0                # BU
LABEL_Z = 34.0
CROWN = None                      # no crown, no beam (designer; built-in note 8)


def _rng(seed, name):
    return random.Random(int(seed or 0) * 1000003 + sum(ord(c) for c in name))


def landmark_info():
    """Constants the pipeline checks (12.2 ratio, 8.6b silhouette) can read. All BU, city units."""
    return dict(corp=CORP, central_server_name=CENTRAL_SERVER_NAME, landmark=LANDMARK_NAME,
                footprint_bu=CITY_FOOTPRINT_BU,
                tier_heights=dict(sign_bottom=SIGN_Z[0], sign_top=SIGN_Z[1], sign_width=SIGN_W,
                                  label=LABEL_Z, min_building=MIN_BUILDING_H),
                crown=CROWN, pass_indices_note="sign = emissive quad; check 12.2 must use the sign box, not a compound")


# ------------------------------------------------------------------ the city hook
def _seen(a, b, cx, cy, cam):
    """Port stand-in for the city's seen(): (visible, outward unit normal, length) of edge a->b of a footprint
    whose centroid is (cx, cy); visible = the normal faces the camera (cam = ctx.camdir, xy used)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L < 1e-6:
        return False, (0.0, 0.0), 0.0
    nx, ny = dy / L, -dx / L
    mx, my = (a[0] + b[0]) / 2 - cx, (a[1] + b[1]) / 2 - cy
    if nx * mx + ny * my < 0:
        nx, ny = -nx, -ny
    cl = math.hypot(cam[0], cam[1]) or 1.0
    vis = (nx * cam[0] + ny * cam[1]) / cl > 0.05
    return vis, (nx, ny), L


BLOCK_HALF = (7.0, 6.0)           # standalone base block (the .glb / the HQ lot centre): half width x half depth, BU
BLOCK_H = 16.0
BLOCK_COL = (0.30, 0.11, 0.10)    # tenement brick


def _place_sign(ctx, a, c, nrm, building_key=None):
    """The MAINFRAME blade at the corner of the street face a->c (outward normal nrm), the red wash and the red spot."""
    NEON = ctx.NEON
    nx, ny = nrm
    L = math.hypot(c[0] - a[0], c[1] - a[1])
    ux, uy = (c[0] - a[0]) / L, (c[1] - a[1]) / L
    px, py = a[0] + ux * 0.8, a[1] + uy * 0.8
    z0s, z1s = SIGN_Z
    w_ = SIGN_W
    signs = ctx.station.setdefault("signs", [])
    cp_scr = getattr(ctx.CP, "SCR", "") if ctx.CP is not None else ""
    signs.append(([(px + nx * 0.3, py + ny * 0.3, z0s), (px + nx * (0.3 + w_), py + ny * (0.3 + w_), z0s),
                   (px + nx * (0.3 + w_), py + ny * (0.3 + w_), z1s), (px + nx * 0.3, py + ny * 0.3, z1s)],
                  str(cp_scr) + "/" + SIGN_TEX))
    # the red wash of the sign on its shop front
    NEON.face([(a[0] + nx * 0.08, a[1] + ny * 0.08, 0.15), (c[0] + nx * 0.08, c[1] + ny * 0.08, 0.15),
               (c[0] + nx * 0.08, c[1] + ny * 0.08, 1.4), (a[0] + nx * 0.08, a[1] + ny * 0.08, 1.4)], SIGN_RED)
    ctx.spot_at((px, py, 8.0), (px + nx * 6 + ux * 3, py + ny * 6 + uy * 3, 3.0), SPOT_RED, SPOT_POWER, SPOT_CONE)
    ctx.station["mainframe"] = (px + nx * 1.8, py + ny * 1.8, 8.4)
    if building_key is not None:
        ctx.station["mainframe_building"] = building_key


def build_standalone(ctx):
    """No map (ctx.O is None, the .glb export / a bare HQ lot): the base block at the HQ lot centre carries the blade at
    the west corner of its south (street) face, with the street door in the middle of that face. Not part of the city
    build (the city draws no block: the sign rides a map building)."""
    hx, hy = ctx.hq
    bx, by = BLOCK_HALF
    ctx.box(ctx.SURF, hx - bx, hy - by, 0.0, hx + bx, hy + by, BLOCK_H, BLOCK_COL, wc=(1.0, 0.35, 0.3), wl=0.4, wm=0, bid=0.5)
    # the street door: a lit recess in the south face (emissive, sodium white)
    ctx.box(ctx.NEON, hx - 1.1, hy - by - 0.05, 0.0, hx + 1.1, hy - by + 0.05, 2.6, (1.0, 0.85, 0.6))
    _place_sign(ctx, (hx - bx, hy - by), (hx + bx, hy - by), (0.0, -1.0), "block")
    return dict(label=(hx, hy, LABEL_Z), crown=CROWN, hue=tuple(ctx.district["hue"]))


def build_city(ctx):
    if ctx.O is None:
        return build_standalone(ctx)
    O, W, CP = ctx.O, ctx.W, ctx.CP
    core_lot = ctx.hq_lot
    best = None
    for b in O["buildings"]:
        if b["terr"] != CORP or b["h"] * CP.KH < MIN_BUILDING_H or b.get("wet"):
            continue
        q = [W(p) for p in b["q"]]
        n = len(q)
        cxq, cyq = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
        for i in range(n):
            vis, nrm, L = _seen(q[i], q[(i + 1) % n], cxq, cyq, ctx.camdir)
            if vis and L >= MIN_FACE_LEN:
                d = math.hypot(b["c"][0] - core_lot[0], b["c"][1] - core_lot[1])
                key = (round(d, 3), b["key"], i)
                if best is None or key < best[0]:
                    best = (key, q[i], q[(i + 1) % n], nrm, b)
                break
    hx, hy = ctx.hq
    hue = tuple(ctx.district["hue"])
    if best is None:                                  # no eligible building: no sign, label on the HQ lot
        return dict(label=(hx, hy, LABEL_Z), crown=CROWN, hue=hue)
    _, a, c, nrm, b = best
    _place_sign(ctx, a, c, nrm, b["key"])
    return dict(label=(hx, hy, LABEL_Z), crown=CROWN, hue=hue)


def build(K, rooms=True, rail=False):
    """City (landmarks.landmark_ctx): build(ctx) -> dict(label, crown, hue). HQ kit: build(K, rooms, rail) -> hooks."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return build_city(K)
    return build_hq(K, rooms, rail)


# the base block's street door: centre of its south (street) face
ENTRY = {"entry": [0.0, -BLOCK_HALF[1], 0.0], "entry_nrm": [0.0, -1.0]}


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
    return _hq_module("hq_build.py", "rebel_cell").build(K)
