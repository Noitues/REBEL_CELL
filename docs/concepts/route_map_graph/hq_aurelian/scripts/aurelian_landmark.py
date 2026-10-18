"""AURELIAN CONCORD HQ: THE CIRCUS AURELIUS, the one landmark model for the full city and the HQ netrun (spec 8.6b).

Status: design pass, step 2 (massing thumbnails). The city build is the canonical full-city colosseum, ported 1:1 from
city_all_corps/scripts/landmarks.py aurelian() (the same numbers, the same order of faces). build_hq (the HQ-kit scene
hook, spec 8.5) is written after the coordinator picks a concept; until then it raises.

ENTRY POINTS
    import aurelian_landmark as AL
    info = AL.build(ctx)                 # city hook (city_preset.LANDMARK_MODULES["aurelian"]; city_all_corps/NOTES.md
                                         #   "Landmark modules"): -> dict(label=xyz, crown=xyz, hue=rgb)
    S = AL.slots(layers, concept="B")    # pure python: room slots on demand for ANY game graph (spec 8.4 rule 5)
    AL.canonical(ctx, hx, hy, open_bays=())   # the canonical geometry with the ctx primitives (used by both)

    ctx   the city ctx (SimpleNamespace): SURF, SMOOTH, NEON accumulators; prism, box, cyl, bar, ring_line, annulus,
          circle, sc; spot_at; hq (world xy); district (DISTRICTS["aurelian"]: "mat", "sec", "hue"); CP (city_preset:
          CP.AURELIAN_LM). Any caller can build its own ctx (thumbs.py does).

UNITS
    City world BU (1 floor = 1.9 BU), x east, y north, z up, the street at z 0. The canonical model is authored in city
    units, so the city build needs no k_units. The HQ kit scenes run in kit units (1 storey = 8 BU): build_hq will wrap K
    with a place() proxy at k = 1 / 0.2375 (the Meridian v3 pattern, inverted). The HQ lot is the LANDMARK_FP ellipse
    (semi-axes 36 x 30 BU); the colosseum + campanili fill it (k_fit 1.0 on the concept city).

SEEDS
    The landmark draws no random numbers. The slot generator is pure and order-stable (layer, node, then azimuth).
"""
import math
import os
import sys

sys.dont_write_bytecode = True
_HERE = os.path.dirname(os.path.abspath(__file__))
_KIT = os.path.normpath(os.path.join(_HERE, "..", "..", "hq_meridian", "scripts"))
if _KIT not in sys.path:
    sys.path.insert(0, _KIT)
from hq_kit import states as ST          # the shared room-state language (no kit copies)

CORP = "aurelian"
TITLE = "THE CIRCUS AURELIUS"
CENTRAL_SERVER = "THE CONCORDAT VAULT"   # designer A3, 2026-10-18
K_UNITS = 0.2375

# ------------------------------------------------------------------ canonical numbers (landmarks.py aurelian())
A = 31.0                 # bowl semi-major (x, east-west)
BK = 0.8                 # minor / major
NSEG = 64
TIERS = 3                # colonnade tiers
TIER_H = 5.0
ATTIC_H = 3.0
LM_DEFAULT = dict(cols=60, col_r=0.62, recess=1.7, steps=4)     # city_preset.AURELIAN_LM
RING_R = [A - 0.5, A * 0.86, A * 0.72, A * 0.6, A * 0.48]        # cavea ring edges, outer -> arena
RING_Z = [TIERS * TIER_H + ATTIC_H, 15.0, 10.5, 6.5, 3.0]
CAMP_OFF, CAMP_R = 3.5, 2.3
ROSTRUM = dict(plinth_r=5.0, plinth_z=(3.0, 4.2), tholos_r=4.2, tholos_z=(4.2, 7.5), core_r=1.6, core_top=22.0,
               rings_z=(10.0, 14.0, 18.0, 22.0), laurel_r=7.0, laurel_z=25.0)
TRAVERTINE_FALLBACK = (0.86, 0.78, 0.62)
GILT_FALLBACK = (0.788, 0.639, 0.353)          # DISTRICTS["aurelian"]["sec"]: the city's neon rings are gilt
VERDIGRIS = (0.161, 0.859, 0.651)              # the corp hue (#29DBA6)

# HQ room box in city units (the kit's 14 x 8 x 10 cutaway x k_units)
ROOM = dict(w=3.3, d=1.9, h=2.4)
ROOM_BAY_H = 3.4          # a loggia room fills its arch bay (tier 5.0 minus the base and entablature bands)


def _lm(ctx):
    cp = getattr(ctx, "CP", None)
    return dict(getattr(cp, "AURELIAN_LM", LM_DEFAULT)) if cp is not None else dict(LM_DEFAULT)


def terraces(steps=LM_DEFAULT["steps"]):
    """The cavea terraces, top to bottom: list of (outer r, inner r, z, ring index, step index)."""
    out = []
    for k in range(4):
        z_top, z_bot = RING_Z[k], RING_Z[k + 1] + 1.2
        for m in range(steps):
            ro = RING_R[k] - (RING_R[k] - RING_R[k + 1]) * m / steps
            ri = RING_R[k] - (RING_R[k] - RING_R[k + 1]) * (m + 1) / steps
            out.append((ro, ri, z_top - (z_top - z_bot) * (m + 0.5) / steps, k, m))
    return out


def ell(t, r):
    """A point on the bowl ellipse of semi-major r (the minor is r * BK) at parameter t (radians), centre (0, 0)."""
    return (r * math.cos(t), r * BK * math.sin(t))


def ell_normal(t, r, inward):
    x, y = ell(t, r)
    nx, ny = x / (r * r), y / ((r * BK) ** 2)
    L = math.hypot(nx, ny) or 1.0
    s = -1.0 if inward else 1.0
    return (s * nx / L, s * ny / L, 0.0)


# ------------------------------------------------------------------ the canonical geometry
def canonical(ctx, hx, hy, open_bays=()):
    """The full-city Circus Aurelius at (hx, hy) with the ctx primitives. open_bays: (tier, t0, t1) arcs (radians) where
    the outer colonnade drops its columns for an HQ room's doorway bay (HQ only; the city passes none)."""
    SURF, SMOOTH, NEON = ctx.SURF, ctx.SMOOTH, ctx.NEON
    prism, box, cyl, bar = ctx.prism, ctx.box, ctx.cyl, ctx.bar
    ring_line, annulus, circle, sc = ctx.ring_line, ctx.annulus, ctx.circle, ctx.sc
    D = getattr(ctx, "district", None) or {}
    tr = D["mat"][0] if "mat" in D else TRAVERTINE_FALLBACK
    sec = D["sec"] if "sec" in D else GILT_FALLBACK
    LM = _lm(ctx)
    rec, n, th, attic = LM["recess"], NSEG, TIER_H, ATTIC_H

    def bay_open(k, t):
        tt = t % (2 * math.pi)
        return any(k == kb and t0 <= tt <= t1 for (kb, t0, t1) in open_bays)

    for k in range(TIERS):
        z0, z1 = k * th, (k + 1) * th
        prism(SURF, circle(hx, hy, A - rec, n, ry=(A - rec) * BK), z0, z1, sc(tr, 0.86 - 0.03 * k), top=False,
              wc=(1.0, 0.76, 0.42), wl=0.8, wm=4, bid=0.1 * k, uvs=(1.6 / 3.4, 1.9 / th), vz0=0.0)
        for m in range(LM["cols"]):
            t = 2 * math.pi * m / LM["cols"]
            if bay_open(k, t):
                continue
            cyl(SMOOTH, hx + A * math.cos(t), hy + A * BK * math.sin(t), z0 + 0.25, z1 - 0.7, LM["col_r"], 10,
                sc(tr, 1.04 - 0.03 * k))
        prism(SURF, circle(hx, hy, A + LM["col_r"] + 0.25, n, ry=A * BK + LM["col_r"] + 0.25), z0, z0 + 0.25,
              sc(tr, 0.95), top=False)
        prism(SURF, circle(hx, hy, A + LM["col_r"] + 0.35, n, ry=A * BK + LM["col_r"] + 0.35), z1 - 0.7, z1,
              sc(tr, 1.05), top=False)
        k1 = (A * BK + LM["col_r"] + 0.35) / (A + LM["col_r"] + 0.35)
        annulus(SURF, hx, hy, z1, A - rec, A + LM["col_r"] + 0.35, sc(tr, 1.0), n=n, k0=BK, k1=k1)
        annulus(SURF, hx, hy, z1 - 0.7, A - rec, A + LM["col_r"] + 0.35, sc(tr, 0.7), n=n, k0=BK, k1=k1)
    zt = TIERS * th
    prism(SURF, circle(hx, hy, A + 0.2, n, ry=A * BK + 0.2), zt, zt + attic, sc(tr, 0.97), top=False,
          wc=(1.0, 0.8, 0.5), wl=0.25, wm=0, bid=0.35)
    ring_line(SURF, hx, hy, zt + attic, A + 0.35, 0.5, sc(tr, 1.05), n=n, ry=A * BK + 0.35)
    ring_line(NEON, hx, hy, zt + attic + 0.3, A + 0.4, 0.3, sec, n=n, ry=A * BK + 0.4)
    T = terraces(LM["steps"])
    for i, (ro, ri, zm, k, m) in enumerate(T):
        zn = T[i + 1][2] if i + 1 < len(T) else RING_Z[4]
        annulus(SURF, hx, hy, zm, ri, ro, sc(tr, (0.84 if m % 2 == 0 else 0.76) - 0.04 * k), n=n, k0=BK, k1=BK)
        prism(SURF, circle(hx, hy, ri, n, ry=ri * BK), zn, zm, sc(tr, 0.58), top=False)
        if m == LM["steps"] - 1:
            ring_line(NEON, hx, hy, zm + 0.05, ri, 0.32, sec, n=n, ry=ri * BK)
    if not getattr(ctx, "arena_open", False):          # concept C cuts the arena floor (the hypogeum below)
        prism(NEON, circle(hx, hy, RING_R[4], n, ry=RING_R[4] * BK), 0.0, 3.0, sc((1.0, 0.72, 0.42), 0.35), top=True)
    R = ROSTRUM
    cyl(SURF, hx, hy, R["plinth_z"][0], R["plinth_z"][1], R["plinth_r"], 20, (0.23, 0.08, 0.15))
    for kk in range(12):
        t = 2 * math.pi * kk / 12
        x, y = hx + R["tholos_r"] * math.cos(t), hy + R["tholos_r"] * math.sin(t)
        bar(SURF, (x, y, R["tholos_z"][0]), (x, y, R["tholos_z"][1]), 0.45, (0.95, 0.92, 0.85))
    cyl(SURF, hx, hy, R["tholos_z"][1], R["tholos_z"][1] + 0.5, 4.8, 20, (0.95, 0.92, 0.85))
    cyl(SMOOTH, hx, hy, R["tholos_z"][0], R["core_top"], R["core_r"], 14, (0.92, 0.88, 0.80))
    for zz in R["rings_z"]:
        ring_line(NEON, hx, hy, zz, 1.75, 0.35, sec, n=14)
    ring_line(NEON, hx, hy, R["laurel_z"], R["laurel_r"], 0.42, sc(sec, 1.2), n=40)
    for kk in range(16):
        t = 2 * math.pi * kk / 16
        p0 = (hx + 7.0 * math.cos(t), hy + 7.0 * math.sin(t), 25.0)
        p1 = (hx + 8.6 * math.cos(t + 0.15), hy + 8.6 * math.sin(t + 0.15), 26.0)
        bar(NEON, p0, p1, 0.35, sc(sec, 1.2))
    box(NEON, hx - 0.6, hy - 0.6, 22.0, hx + 0.6, hy + 0.6, 23.4, (1.0, 0.85, 0.5))
    for kk in range(4):
        t = math.radians(45 + 90 * kk)
        cx, cy = hx + (A + CAMP_OFF) * math.cos(t), hy + (A * BK + CAMP_OFF) * math.sin(t)
        rad = CAMP_R
        cyl(SMOOTH, cx, cy, 0, 3, rad * 1.15, 14, tr)
        zz = 3.0
        for m in range(8):
            cyl(SMOOTH, cx, cy, zz, zz + 3.2, rad, 14, tr, wc=(1.0, 0.8, 0.5), wl=0.8, wm=4, bid=0.3 + kk * 0.1,
                uvs=(1.6 / 1.3, 1.9 / 3.2), vz0=0.0)
            cyl(SURF, cx, cy, zz + 3.2, zz + 3.45, rad * 1.1, 14, tr)
            zz += 3.45
        cyl(SURF, cx, cy, zz, zz + 0.5, rad * 1.18, 14, tr)
        cyl(SURF, cx, cy, zz + 0.5, zz + 1.1, rad * 1.05, 14, tr, top=False)
        ring_line(NEON, cx, cy, zz + 0.6, rad * 1.22, 0.28, sec, n=14)
        box(NEON, cx - 0.5, cy - 0.5, zz - 4.0, cx + 0.5, cy + 0.5, zz - 2.6, (1.0, 0.8, 0.4))
    ctx.spot_at((hx, hy, 6), (hx + 70, hy - 80, 55), (1.0, 0.86, 0.66), 2.4e6, 40)
    ctx.spot_at((hx, hy, 6), (hx - 75, hy - 50, 35), sec, 1.4e6, 38)
    return dict(label=(hx, hy, 40.0), crown=(hx, hy, 26.0), hue=tuple(sec))


# ------------------------------------------------------------------ slots on demand (spec 8.4)
# A level is an arc of slots on one part of the landmark. t runs left -> right as seen from the OVERVIEW (camera south
# of the bowl, looking north): the south arc goes west -> east (t 200 -> 340 deg), the north arc west -> east through
# north (t 160 -> 20 deg). "dir" alternates the walk per level (boustrophedon), so a level change happens at an end.
def _levels(concept):
    T = terraces()
    rmid = [(RING_R[k] + RING_R[k + 1]) / 2 for k in range(4)]
    zring = []
    for k in range(4):
        st = [t for t in T if t[3] == k]
        zring.append(st[1][2])                         # the second step of the ring: the room stands on it
    cav = [dict(name="R%d" % (k + 1), kind="cavea", r=rmid[k], z=zring[k], arc=(160.0, 20.0), inward=True)
           for k in range(4)]
    rec = LM_DEFAULT["recess"]
    log = [dict(name="T%d" % (k + 1), kind="loggia", r=A - rec, z=k * TIER_H + 0.6, arc=(205.0, 335.0), inward=False,
                tier=k) for k in range(TIERS)]
    attic = dict(name="AT", kind="attic", r=A + 0.2, z=TIERS * TIER_H + 0.3, arc=(205.0, 335.0), inward=False)
    if concept == "A":
        lv = cav + [dict(name="AR", kind="arena", r=RING_R[4] - 2.6, z=3.0, arc=(150.0, 30.0), inward=True)]
    elif concept == "B":
        lv = log + [attic] + cav
    elif concept == "C":
        lv = cav[:2] + [dict(name="H%d" % (k + 1), kind="hypogeum", r=RING_R[4] * (0.82 - 0.22 * k), z=-2.2 - 2.8 * k,
                             arc=(170.0, 10.0), inward=True) for k in range(3)]
    else:
        raise ValueError(concept)
    for i, L in enumerate(lv):
        L["dir"] = 1 if i % 2 == 0 else -1
    return lv


def level_of(i, n_route, n_levels):
    """Layer i (0-based, route layers only) -> level index. More layers than levels: consecutive layers share a level
    (they walk along it). Fewer: the layers spread evenly from the first level to the last."""
    if n_route >= n_levels:
        return min(n_levels - 1, (i * n_levels) // n_route)
    return int(round(i * (n_levels - 1) / max(n_route - 1, 1)))


def slots(layers, concept="B"):
    """Room slots for a game graph. layers: node counts per layer, the LAST layer is THE CONCORDAT VAULT (1 node).
    Any layer count (D10: more than 7 is allowed). Returns a list of dicts (layer, node, level, kind, pos (x, y, z) of
    the room's front-centre at floor level, normal, t (deg), size) in layer, node order; plus the vault."""
    lv = _levels(concept)
    route = layers[:-1]
    nl = len(lv)
    groups = {}
    for i, cnt in enumerate(route):
        groups.setdefault(level_of(i, len(route), nl), []).append((i, cnt))
    out = []
    for li, members in sorted(groups.items()):
        L = lv[li]
        a0, a1 = L["arc"]
        if L["dir"] < 0:
            a0, a1 = a1, a0
        total = sum(c for _, c in members) + (len(members) - 1)            # one empty slot between layer groups
        u = 0
        for (i, cnt) in members:
            for j in range(cnt):
                f = (u + 0.5) / total
                td = a0 + (a1 - a0) * f
                t = math.radians(td)
                x, y = ell(t, L["r"])
                nrm = ell_normal(t, L["r"], L["inward"])
                out.append(dict(layer=i, node=j, level=L["name"], kind=L["kind"], t=td, pos=(x, y, L["z"]),
                                normal=nrm, size=(ROOM["w"], ROOM["d"], ROOM_BAY_H if L["kind"] == "loggia" else ROOM["h"]), tier=L.get("tier")))
                u += 1
            u += 1
    vz = -11.0 if concept == "C" else ROSTRUM["plinth_z"][1]
    out.append(dict(layer=len(layers) - 1, node=0, level="VAULT", kind="vault", t=270.0, pos=(0.0, -0.0, vz),
                    normal=(0.0, -1.0, 0.0), size=(2 * ROSTRUM["tholos_r"],) * 2 + (3.3,), tier=None))
    return out


def fixture_edges(layers):
    """MOCK edges for concept renders only (spec 8.4: topology comes from the game). Node j of layer i links to the
    proportional node of layer i + 1 and, on even j, its right neighbour."""
    E = []
    for i in range(len(layers) - 1):
        a, b = layers[i], layers[i + 1]
        for j in range(a):
            q = int(round(j * (b - 1) / max(a - 1, 1)))
            E.append(((i, j), (i + 1, q)))
            if j % 2 == 0 and q + 1 < b:
                E.append(((i, j), (i + 1, q + 1)))
    for i in range(len(layers) - 1):                   # every node of layer i + 1 must be reachable
        for q in range(layers[i + 1]):
            if not any(e[1] == (i + 1, q) for e in E):
                E.append(((i, min(layers[i] - 1, q)), (i + 1, q)))
    return sorted(set(E))


def state_colour(state):
    """The shared state language (hq_kit.states), 0-1 floats."""
    return tuple(c / 255.0 for c in ST.STATE_COL.get(state, ST.WHITE))


# ------------------------------------------------------------------ hooks
def build(ctx, rooms=True, rail=False):
    """City (landmarks.landmark_ctx): build(ctx) -> dict(label, crown, hue). HQ kit (K has .A): build_hq."""
    if hasattr(ctx, "A") and isinstance(getattr(ctx, "A"), dict):
        return build_hq(ctx, rooms=rooms)
    return canonical(ctx, ctx.hq[0], ctx.hq[1])


def build_hq(K, rooms=True):
    """HQ-kit scene hook (spec 8.5). Written after the concept is approved (design pass step 3)."""
    raise NotImplementedError("aurelian_landmark.build_hq: pending the concept pick (hq_aurelian/DESIGN.md section 9)")
