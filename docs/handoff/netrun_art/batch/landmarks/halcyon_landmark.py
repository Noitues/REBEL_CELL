# DRAFT for the art-pass session; unverified (no render).
# provenance: model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id lm__halcyon; status ok; tokens in 18211 cache-write 132454 cache-read 0 out 7403; cost $0.221; ast.parse: parses

"""DRAFT for the art-pass session; unverified (no render).
HALCYON LANDMARK: the stepped spiral pyramid with THE PANOPTICON vault and the eye, a standalone landmark module.

ENTRY POINTS
    import halcyon_landmark as HL
    info = HL.build(ctx)              # THE CITY HOOK: ctx = landmarks.landmark_ctx("halcyon")
                                      #   -> dict(label=(x, y, z), crown=(x, y, z), hue=(r, g, b))
    HL.build_hq(K, rooms=True, rail=False)   # HQ-netrun scale: documented STUB, raises NotImplementedError (see its docstring)
    HL.build(K_or_ctx)                # dispatcher like meridian_landmark.build: a ctx (has SURF, no A) goes to the city
    HL.landmark_info()                # small dict for the pipeline check 12.2 (landmark ratio) and the lot-fit check 8.6

WHAT IT BUILDS (a port of landmarks.halcyon(), spec 8.6b: one model serves the city and the HQ netrun)
  SIX TIERS     squares of half-size 29.0, 24.8, 20.6, 16.4, 12.2, 8.6 BU, each 5.6 BU high, stacked from z 0 (no podium:
                the city blocks come up to the bottom tier). Lit edge line (district hue) round every tier top.
  GALLERY       one amber ribbon per tier on one face, face = tier mod 4 (S, E, N, W, S, E), climbing 0.9 tier heights:
                the helix gallery counter-clockwise from above.
  VAULT         THE PANOPTICON: a 11 x 11 x 4 BU box on tier 6 with a windowed face.
  EYE           a drum (r 3.6, 2 BU) on the vault, a spindle, and the eye turned to the map camera: an almond of white light
                (the lid), the iris in the district hue (x1.6), a dark pupil, five gold lashes below.
  LIGHTS        two spots (cold white key from the camera side, district-hue fill).
  RETURN        label 14 BU above the eye centre, crown (hero-beam origin) 5 BU above it, hue = the district hue.

UNITS / PLACING
    World BU of the one city (x east, y north, z up; dry street z 0). Everything is placed relative to ctx.hq (the HQ
    centre in world BU); all geometry stays inside |dx|, |dy| <= HALF[0] (+ the 0.32 BU edge-line width) = 29.3 BU,
    inside the landmark clearance of landmark_r 5.6 lots = 33.6 BU. No scaling by k_units is needed (city units already).
    For a different lot size pass fit=k_fit (spec 8.6): every length and the light positions scale about the HQ centre.

SEEDS
    The built-in is fully rule-based: no random draw is made. The stream name `landmark.halcyon` (spec 3.5) is reserved
    and `rng()` returns random.Random(derived from ctx.seed) for future detail (none is used today), never a global.
"""
import math
import random
from types import SimpleNamespace

CORP = "halcyon"
CENTRAL_SERVER_NAME = "THE PANOPTICON"          # GDD 11.7 working name (not "Civic Core")
STREAM = "landmark.halcyon"

# the numbers of landmarks.halcyon() (city BU)
HALF = (29.0, 24.8, 20.6, 16.4, 12.2, 8.6)      # tier half-sizes, bottom to top
TIER_H = 5.6
STONE = (0.46, 0.43, 0.58)
GOLD = (1.0, 0.72, 0.3)
AMBER = (1.0, 0.68, 0.25)
VAULT_HALF = 5.5
VAULT_H = 4.0
DRUM_R, DRUM_H = 3.6, 2.0
EYE_RISE = 7.0                                   # eye centre above the vault top
LABEL_UP, CROWN_UP = 14.0, 5.0
KEY_SPOT = dict(frm=(90.0, -90.0, 70.0), col=(0.85, 0.8, 1.0), power=2.2e6, cone=34)
FILL_SPOT = dict(frm=(-70.0, -110.0, 30.0), power=1.4e6, cone=34)
# face order of the gallery ribbon: (corner index a, corner index c, outward normal) for faces S, E, N, W
FACES = ((0, 1, (0, -1)), (1, 2, (1, 0)), (2, 3, (0, 1)), (3, 0, (-1, 0)))


def _fnv1a64(text):
    h = 0xCBF29CE484222325
    for b in text.encode("utf-8"):
        h = ((h ^ b) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def rng(seed, name=STREAM):
    """A named, seed-derived stream (spec 3.5). Unused by the current geometry; kept for the plugin contract."""
    return random.Random(_fnv1a64("[%r,%r]" % (seed, "art/" + name)))


def landmark_info():
    """For the pipeline checks: 12.2 (landmark ratio) and 8.6 (lot fit). Values in city BU."""
    z = 0.0
    tops = []
    for _ in HALF:
        z += TIER_H
        tops.append(z)
    vault_top = z + VAULT_H
    return dict(corp=CORP, central_server_name=CENTRAL_SERVER_NAME,
                footprint_bu=2.0 * HALF[0],
                tier_heights=[TIER_H] * len(HALF),
                tier_tops=tops,
                tier_half_sizes=list(HALF),
                vault_top=vault_top,
                eye_centre_z=vault_top + EYE_RISE,
                total_height_bu=vault_top + EYE_RISE + TIER_H * 0.0 + 3.4)


# ================================================================== the city hook
def _build_city(ctx):
    hx, hy = ctx.hq[0], ctx.hq[1]
    D = ctx.district
    hue = tuple(D["hue"])
    SURF, SMOOTH, NEON = ctx.SURF, ctx.SMOOTH, ctx.NEON
    box, cyl, bar, sc, spot_at = ctx.box, ctx.cyl, ctx.bar, ctx.sc, ctx.spot_at
    camx, camy = ctx.camdir[0], ctx.camdir[1]
    z = 0.0
    # ---- the six tiers, the edge lines and the helix gallery
    for k, s in enumerate(HALF):
        box(SURF, hx - s, hy - s, z, hx + s, hy + s, z + TIER_H, STONE, wc=(1.0, 0.74, 0.38), wl=0.42, wm=0, bid=0.1 * k)
        cs = [(hx - s, hy - s), (hx + s, hy - s), (hx + s, hy + s), (hx - s, hy + s)]
        for i in range(4):
            bar(NEON, (cs[i][0], cs[i][1], z + TIER_H + 0.05), (cs[(i + 1) % 4][0], cs[(i + 1) % 4][1], z + TIER_H + 0.05), 0.32, hue)
        ia, ic, nv = FACES[k % 4]
        a, c = cs[ia], cs[ic]
        o = 1.2
        bar(NEON, (a[0] + nv[0] * o, a[1] + nv[1] * o, z + TIER_H * 0.55),
            (c[0] + nv[0] * o, c[1] + nv[1] * o, z + TIER_H * 0.55 + TIER_H * 0.9), 0.55, AMBER)
        z += TIER_H
    # ---- THE PANOPTICON vault and the eye
    box(SURF, hx - VAULT_HALF, hy - VAULT_HALF, z, hx + VAULT_HALF, hy + VAULT_HALF, z + VAULT_H, sc(STONE, 0.9),
        wc=(1.0, 0.8, 0.5), wl=0.7, wm=0, bid=0.9)
    z += VAULT_H
    cyl(SMOOTH, hx, hy, z, z + DRUM_H, DRUM_R, 16, (0.22, 0.2, 0.3))
    ez = z + EYE_RISE
    ox, oy = -camy, camx                         # the eye's screen-right axis; (camx, camy) points at the camera

    def P(u, v, d=0.0):
        return (hx + ox * u + camx * d, hy + oy * u + camy * d, ez + v)
    pts = []
    for kk in range(25):                         # the almond: upper lid then lower lid
        t = math.pi * kk / 24
        pts.append(P(-6.5 * math.cos(t), 3.4 * math.sin(t)))
    for kk in range(1, 24):
        t = math.pi * kk / 24
        pts.append(P(6.5 * math.cos(t), -3.4 * math.sin(t)))
    NEON.face(pts, (0.95, 0.88, 1.0))
    iris = [P(2.3 * math.cos(2 * math.pi * kk / 20), 2.3 * math.sin(2 * math.pi * kk / 20), 0.1) for kk in range(20)]
    NEON.face(iris, sc(hue, 1.6))
    pup = [P(1.0 * math.cos(2 * math.pi * kk / 16), 1.0 * math.sin(2 * math.pi * kk / 16), 0.2) for kk in range(16)]
    SURF.face(pup, (0.01, 0.01, 0.02))
    bar(SURF, (hx, hy, z + DRUM_H), (hx, hy, ez - 3.4), 0.8, (0.22, 0.2, 0.3))
    for kk in range(5):                          # the lashes (round 15 crest)
        t = math.radians(-90 + (kk - 2) * 26)
        a0 = P(6.0 * math.cos(t) * 0.95, -3.2 * math.sin(t))
        a1 = P(8.4 * math.cos(t) * 0.95, -4.9 * math.sin(t))
        bar(NEON, a0, a1, 0.5, GOLD)
    # ---- the landmark lights (render turns them into spots)
    spot_at((hx, hy, 18), (hx + KEY_SPOT["frm"][0], hy + KEY_SPOT["frm"][1], KEY_SPOT["frm"][2]), KEY_SPOT["col"],
            KEY_SPOT["power"], KEY_SPOT["cone"])
    spot_at((hx, hy, 18), (hx + FILL_SPOT["frm"][0], hy + FILL_SPOT["frm"][1], FILL_SPOT["frm"][2]), hue,
            FILL_SPOT["power"], FILL_SPOT["cone"])
    return dict(label=(hx, hy, ez + LABEL_UP), crown=(hx, hy, ez + CROWN_UP), hue=hue)


# ================================================================== the HQ-netrun entry (stub)
def build_hq(K, rooms=True, rail=False):
    """HQ-netrun-scale Halcyon (spec 8.5): NOT IMPLEMENTED. No hq_build source for Halcyon was supplied (the netrun
    builder is the reference `hq_scene.py` civic architecture plus `hq_graph.py`, not seen here).

    TODO, what the HQ builder must expose for the art-pass session to finish this (hooks contract of
    meridian_landmark.build_hq: hooks = {"accs", "beams", "mover_lights", "post_build"}):
      1. Room slots from the corp graph (spec 8.4, topology ALWAYS from the game graph, GDD 4.2): ordered slots with
         frame, normal, size, tier and face on the six tiers (face = tier mod 4); cutaway room 14 x 8 x 10 kit BU
         (x k_units 0.2375) in the face; slot generation on demand for any 7-layer / 2-4 node graph. The Compound
         chains rows 6-5-4-3-2-1, the helix links (gallery, corner stair, stair, climb) are MOCK data.
      2. Link geometry per step class (gallery same level, corner stair, stair up, climb up a face at the same u),
         on the facade, as slots-to-slots polylines.
      3. The eye: turret pose and azimuth from game state (`mt`, `room_state`, `affected`); the gobo gaze spot
         (90 deg sector, compound-linked), blade scan line, lighthouse beam (2.2 + 6 deg cones, -9 deg), lockdown
         red x2.2 + scan-line plane: lights through K.add_light, beams through hooks["beams"].
      4. The same silhouette as build() (8.6b, IoU >= 0.85 at 320 px): tiers, gallery, vault, eye drum; the vault open
         on four faces with the server core column (red iris rings) for the TARGET read.
      5. k_fit per lot (8.6) and the K.place wrapper (K.place_f) for kit -> city units.
      6. Accumulators (A["civic"], "glass", "trim", "small", ...) and K.room_shell(id, rec) as in meridian_landmark.
    """
    raise NotImplementedError("halcyon build_hq: see the TODO list in the docstring (room slots from the game graph, "
                              "eye lights, beams, hooks dict)")


def build(K, rooms=True, rail=False):
    """City: build(ctx) -> dict(label, crown, hue). HQ kit: build(K, rooms, rail) -> hooks (stub)."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return _build_city(K)
    return build_hq(K, rooms, rail)
