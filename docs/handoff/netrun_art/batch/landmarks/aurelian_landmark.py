# DRAFT for the art-pass session; unverified (no render).
# provenance: model claude-sonnet-5-5, batch msgbatch_01RaHqzf7jXZFejW88mMeGMY, custom_id lm__aurelian; status ok; tokens in 9569 cache-write 0 cache-read 132454 out 10237; cost $0.074; ast.parse: parses

"""DRAFT for the art-pass session; unverified (no render).
AURELIAN v3 LANDMARK: THE CIRCUS AURELIUS, an importable city-scale landmark module (spec 8.5, 8.6, 8.6b, 8.6c).

ENTRY POINTS
    import aurelian_landmark as AL
    info = AL.build(ctx)              # city hook (city_preset.LANDMARK_MODULES["aurelian"]):
                                      #   -> dict(label=(x, y, z), crown=(x, y, z) or None, hue=(r, g, b))
    AL.build(K, rooms=True, rail=False)   # HQ-netrun entry: dispatches to build_hq (currently a documented stub)
    AL.landmark_info()                # constants for the pipeline checks (12.2 landmark ratio, 8.6 k_fit)

    ctx   what landmarks.landmark_ctx("aurelian") provides. Used here: SURF, SMOOTH, NEON (accumulators with .face),
          GLASS (declared, unused: the built-in has none), prism, box, cyl, dome, bar, ring_line, annulus, circle,
          sc, spot_at, hq (world x, y of the HQ lot centre), district (the DIST["aurelian"] dict: "mat", "sec",
          "hue"), CP (city_preset module; CP.AURELIAN_LM holds recess, cols, col_r, steps), footprint.

WHAT IT BUILDS (all inside the lot footprint; one model for the city and, later, the HQ netrun, spec 8.6b)
  COLOSSEUM    an elliptical bowl (semi-major A 31 BU along x, minor/major ratio 0.8, 64 segments): three COLONNADE
               tiers (round columns on the outer ellipse, the wall set back by AURELIAN_LM["recess"], gilt-lit arches),
               a base band and an entablature band per tier, a solid attic band, a travertine cap ring and a verdigris
               neon ring
  CAVEA        four seating rings stair-stepped down to the arena (AURELIAN_LM["steps"] terraces per ring), each ring's
               inner edge a thin verdigris line
  ARENA        lit sand; THE ROSTRUM (the Central Server): a porphyry plinth, a ring of 12 columns, a core column with
               four lit rings, a laurel holo ring (16 leaves) and a gilt lamp
  CAMPANILI    four round bell towers on the diagonals, flat crowns with a verdigris ring and a gilt lantern
  LIGHTS       two arena searchlight floods (warm travertine key, verdigris fill)

UNITS / PLACING
    City world BU (x east, y north, z up; 1 floor = 1.9 BU, 1 lot = 6 BU). The geometry is built around ctx.hq. The
    built-in sizes are already city units, so there is no k_units here. Spec 8.6 k_fit (fill the HQ lot) is exposed as
    fit_scale(lot_w, lot_d) and is NOT applied by build(ctx): the city footprint is the fixed ellipse of
    LANDMARK_FP["aurelian"] (36 x 30), so k_fit is about 1.0 on the concept city.

SEEDS
    The built-in uses no randomness; nothing here draws random numbers. stream_rng(ctx, name) is provided for future
    detail and is keyed by (ctx.seed, "landmark.aurelian", name), never by draw order (spec 3.5 rule 3).
"""
import math
import random
from types import SimpleNamespace

# ------------------------------------------------------------------ constants (read by landmark_info)
CORP = "aurelian"
TITLE = "THE CIRCUS AURELIUS"
CENTRAL_SERVER = "THE ROSTRUM"          # Aurelian's own name (identity.md); not one of the GDD 11.7 working names
HUB = "THE GRAND STAND"
FOOTPRINT_SEMI_BU = (36.0, 30.0)        # ASSUMPTION: LANDMARK_FP ellipse "36 x 30" read as semi-axes (x, y)
BOWL_A = 31.0                           # semi-major of the bowl (x)
BOWL_K = 0.8                            # minor / major ratio
TIERS = 3
TIER_H = 5.0
ATTIC_H = 3.0
CAMPANILE_R = 2.3
CAMPANILE_OFFSET = 3.5
GOLD = (1.0, 0.72, 0.3)
HUE_FALLBACK = (0.161, 0.859, 0.651)    # VERDIGRIS #29DBA6, used only if ctx.district has no "sec"
_NSEG = 64


def _stream_seed(seed, stream):
    """FNV-1a 64 over the UTF-8 of a JSON-like key, then splitmix64 (spec 3.5)."""
    s = ("[%d,\"art/landmark.aurelian\",\"%s\"]" % (int(seed), stream)).encode("utf-8")
    h = 0xCBF29CE484222325
    for b in s:
        h = ((h ^ b) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    h = (h + 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    h = ((h ^ (h >> 30)) * 0xBF58476D1CE4E5B9) & 0xFFFFFFFFFFFFFFFF
    h = ((h ^ (h >> 27)) * 0x94D049BB133111EB) & 0xFFFFFFFFFFFFFFFF
    return h ^ (h >> 31)


def stream_rng(ctx, name):
    """A named per-purpose RNG (unused by the current geometry)."""
    return random.Random(_stream_seed(getattr(ctx, "seed", 0), name))


def fit_scale(lot_w, lot_d, margin=0.25 * 6.0):
    """Spec 8.6 k_fit for the colosseum's outer footprint (the 2x campanile-inclusive ellipse), lot inset by margin BU."""
    ex = BOWL_A + CAMPANILE_OFFSET + CAMPANILE_R * 1.2
    ey = BOWL_A * BOWL_K + CAMPANILE_OFFSET + CAMPANILE_R * 1.2
    return min((lot_w - 2 * margin) / (2 * ex), (lot_d - 2 * margin) / (2 * ey))


def _tier_heights():
    zt = TIERS * TIER_H
    return dict(tiers=[(k * TIER_H, (k + 1) * TIER_H) for k in range(TIERS)], attic=(zt, zt + ATTIC_H),
                colonnade_top=zt + ATTIC_H, rostrum_column_top=22.0, laurel_ring_z=25.0,
                campanile_top=3.0 + 8 * 3.45 + 1.1, label_z=40.0, crown_z=26.0)


def landmark_info():
    """Small dict for the pipeline checks (12.2 landmark ratio, 8.6 fill check)."""
    th = _tier_heights()
    return dict(corp=CORP, title=TITLE, central_server_name=CENTRAL_SERVER, hub_name=HUB,
                footprint_bu=dict(semi_axes=FOOTPRINT_SEMI_BU, bowl_semi=(BOWL_A, BOWL_A * BOWL_K)),
                tier_heights=th, hue=HUE_FALLBACK, landmark_pass_indices=(1, 5, 6))


# ------------------------------------------------------------------ the city build (port of landmarks.aurelian)
def _build_city(ctx):
    SURF, SMOOTH, NEON = ctx.SURF, ctx.SMOOTH, ctx.NEON
    prism, box, cyl, dome, bar = ctx.prism, ctx.box, ctx.cyl, ctx.dome, ctx.bar
    ring_line, annulus, circle, sc, spot_at = ctx.ring_line, ctx.annulus, ctx.circle, ctx.sc, ctx.spot_at
    hx, hy = ctx.hq
    D = ctx.district
    tr = D["mat"][0]
    sec = D["sec"] if "sec" in D else HUE_FALLBACK
    A, Bk = BOWL_A, BOWL_K
    n = _NSEG
    tiers = TIERS
    th = TIER_H
    attic = ATTIC_H
    AL = ctx.CP.AURELIAN_LM
    rec = AL["recess"]
    for k in range(tiers):
        z0, z1 = k * th, (k + 1) * th
        # the wall stands back behind the columns: lit gilt arches deep in the loggia
        prism(SURF, circle(hx, hy, A - rec, n, ry=(A - rec) * Bk), z0, z1, sc(tr, 0.86 - 0.03 * k), top=False,
              wc=(1.0, 0.76, 0.42), wl=0.8, wm=4, bid=0.1 * k, uvs=(1.6 / 3.4, 1.9 / th), vz0=0.0)
        # the colonnade: round columns on the outer ellipse
        for m in range(AL["cols"]):
            t = 2 * math.pi * m / AL["cols"]
            cx_, cy_ = hx + A * math.cos(t), hy + A * Bk * math.sin(t)
            cyl(SMOOTH, cx_, cy_, z0 + 0.25, z1 - 0.7, AL["col_r"], 10, sc(tr, 1.04 - 0.03 * k))
        prism(SURF, circle(hx, hy, A + AL["col_r"] + 0.25, n, ry=A * Bk + AL["col_r"] + 0.25), z0, z0 + 0.25,
              sc(tr, 0.95), top=False)
        prism(SURF, circle(hx, hy, A + AL["col_r"] + 0.35, n, ry=A * Bk + AL["col_r"] + 0.35), z1 - 0.7, z1,
              sc(tr, 1.05), top=False)
        k1_ = (A * Bk + AL["col_r"] + 0.35) / (A + AL["col_r"] + 0.35)
        annulus(SURF, hx, hy, z1, A - rec, A + AL["col_r"] + 0.35, sc(tr, 1.0), n=n, k0=Bk, k1=k1_)
        annulus(SURF, hx, hy, z1 - 0.7, A - rec, A + AL["col_r"] + 0.35, sc(tr, 0.7), n=n, k0=Bk, k1=k1_)
    zt_ = tiers * th
    prism(SURF, circle(hx, hy, A + 0.2, n, ry=A * Bk + 0.2), zt_, zt_ + attic, sc(tr, 0.97), top=False,
          wc=(1.0, 0.8, 0.5), wl=0.25, wm=0, bid=0.35)
    ring_line(SURF, hx, hy, zt_ + attic, A + 0.35, 0.5, sc(tr, 1.05), n=n, ry=A * Bk + 0.35)
    ring_line(NEON, hx, hy, zt_ + attic + 0.3, A + 0.4, 0.3, sec, n=n, ry=A * Bk + 0.4)
    # the cavea: four seating rings stair-stepped down to the arena (flat terraces + risers), each ring edge gilt
    rs = [A - 0.5, A * 0.86, A * 0.72, A * 0.6, A * 0.48]
    zs = [zt_ + attic, 15.0, 10.5, 6.5, 3.0]
    st_ = AL["steps"]
    terr_ = []                                   # (outer r, inner r, z, ring, step) top to bottom
    for k in range(4):
        z_top, z_bot = zs[k], zs[k + 1] + 1.2
        for m in range(st_):
            ro = rs[k] - (rs[k] - rs[k + 1]) * m / st_
            ri = rs[k] - (rs[k] - rs[k + 1]) * (m + 1) / st_
            terr_.append((ro, ri, z_top - (z_top - z_bot) * (m + 0.5) / st_, k, m))
    for i_, (ro, ri, zm, k, m) in enumerate(terr_):
        zn = terr_[i_ + 1][2] if i_ + 1 < len(terr_) else zs[4]     # the riser drops to the next terrace (arena last)
        annulus(SURF, hx, hy, zm, ri, ro, sc(tr, (0.84 if m % 2 == 0 else 0.76) - 0.04 * k), n=n, k0=Bk, k1=Bk)
        prism(SURF, circle(hx, hy, ri, n, ry=ri * Bk), zn, zm, sc(tr, 0.58), top=False)
        if m == st_ - 1:
            ring_line(NEON, hx, hy, zm + 0.05, ri, 0.32, sec, n=n, ry=ri * Bk)
    # the arena: lit sand, THE ROSTRUM, laurel holo
    prism(NEON, circle(hx, hy, rs[4], n, ry=rs[4] * Bk), 0.0, 3.0, sc((1.0, 0.72, 0.42), 0.35), top=True)
    cyl(SURF, hx, hy, 3.0, 4.2, 5.0, 20, (0.23, 0.08, 0.15))
    for kk in range(12):
        t = 2 * math.pi * kk / 12
        bar(SURF, (hx + 4.2 * math.cos(t), hy + 4.2 * math.sin(t), 4.2),
            (hx + 4.2 * math.cos(t), hy + 4.2 * math.sin(t), 7.5), 0.45, (0.95, 0.92, 0.85))
    cyl(SURF, hx, hy, 7.5, 8.0, 4.8, 20, (0.95, 0.92, 0.85))
    cyl(SMOOTH, hx, hy, 4.2, 22.0, 1.6, 14, (0.92, 0.88, 0.80))
    for zz in (10.0, 14.0, 18.0, 22.0):
        ring_line(NEON, hx, hy, zz, 1.75, 0.35, sec, n=14)
    ring_line(NEON, hx, hy, 25.0, 7.0, 0.42, sc(sec, 1.2), n=40)
    for kk in range(16):             # laurel leaves on the holo ring
        t = 2 * math.pi * kk / 16
        p0 = (hx + 7.0 * math.cos(t), hy + 7.0 * math.sin(t), 25.0)
        p1 = (hx + 8.6 * math.cos(t + 0.15), hy + 8.6 * math.sin(t + 0.15), 26.0)
        bar(NEON, p0, p1, 0.35, sc(sec, 1.2))
    box(NEON, hx - 0.6, hy - 0.6, 22.0, hx + 0.6, hy + 0.6, 23.4, (1.0, 0.85, 0.5))
    # four campanili on the colosseum's diagonals (flat crowns)
    for kk in range(4):
        t = math.radians(45 + 90 * kk)
        cx_, cy_ = hx + (A + CAMPANILE_OFFSET) * math.cos(t), hy + (A * Bk + CAMPANILE_OFFSET) * math.sin(t)
        rad = CAMPANILE_R
        cyl(SMOOTH, cx_, cy_, 0, 3, rad * 1.15, 14, tr)
        zz = 3.0
        for m in range(8):
            cyl(SMOOTH, cx_, cy_, zz, zz + 3.2, rad, 14, tr, wc=(1.0, 0.8, 0.5), wl=0.8, wm=4, bid=0.3 + kk * 0.1,
                uvs=(1.6 / 1.3, 1.9 / 3.2), vz0=0.0)
            cyl(SURF, cx_, cy_, zz + 3.2, zz + 3.45, rad * 1.1, 14, tr)
            zz += 3.45
        cyl(SURF, cx_, cy_, zz, zz + 0.5, rad * 1.18, 14, tr)
        cyl(SURF, cx_, cy_, zz + 0.5, zz + 1.1, rad * 1.05, 14, tr, top=False)
        ring_line(NEON, cx_, cy_, zz + 0.6, rad * 1.22, 0.28, sec, n=14)
        box(NEON, cx_ - 0.5, cy_ - 0.5, zz - 4.0, cx_ + 0.5, cy_ + 0.5, zz - 2.6, (1.0, 0.8, 0.4))
    # the arena searchlight floods
    spot_at((hx, hy, 6), (hx + 70, hy - 80, 55), (1.0, 0.86, 0.66), 2.4e6, 40)
    spot_at((hx, hy, 6), (hx - 75, hy - 50, 35), sec, 1.4e6, 38)
    return dict(label=(hx, hy, 40.0), crown=(hx, hy, 26.0), hue=tuple(sec))


# ------------------------------------------------------------------ the HQ-netrun entry (stub)
def build_hq(K, rooms=True, rail=False):
    """HQ-netrun builder (spec 8.5). NOT IMPLEMENTED: no Aurelian hq_build source was supplied (new_corps/roman has
    only a stub `build_hq`, and the HQ design is item 4 of the batch).
    TODO the HQ builder must provide, so the art-pass session can finish this:
      1. Room slots from the GAME graph (spec 8.4), never the mock `rooms` of roman_preset: slots on the four
         seating rings (frame, normal, size, ring index); the concept's 6/5/4/3 rooms and azimuths are fixtures only.
         The module must generate slots on demand for any graph (GDD 4.2, 7 layers of 2-4 nodes).
      2. `K.G` (room slots), `K.ROOM_EMIT`, `K.room_shell(id, rec)` cutaway for rooms=True.
      3. Hooks dict: {"accs": {...}, "beams": [(origin, dir, colour, power, cone)], "mover_lights": {},
         "post_build": fn(OBJ)}. Beam origin should be the laurel ring / rostrum crown (the city crown is (hx, hy, 26)).
      4. Mechanic visuals driven by game state (THE TURNING GATES): the gate rings as rotatable accumulators with the
         2 gates per ring, the yellow pencil telegraph positions, link de-powering where no gate stands.
      5. Light rig numbers (K.LH keys: neon, wash, server, uplight) and a K.CP "compound" block from the HQ preset.
      6. Scale: kit units to city units (k_units 0.2375 if the kit keeps 8 BU storeys) and k_fit to the HQ lot
         (spec 8.6); the silhouette must match the city build at IoU >= 0.85 at 320 px (spec 8.6b).
    """
    raise NotImplementedError("aurelian_landmark.build_hq: no hq_build source supplied; see the docstring TODO list")


def build(K, rooms=True, rail=False):
    """City (landmarks.landmark_ctx): build(ctx) -> dict(label, crown, hue). HQ kit: build(K, rooms, rail) -> hooks."""
    if hasattr(K, "SURF") and not hasattr(K, "A"):
        return _build_city(K)
    return build_hq(K, rooms, rail)
