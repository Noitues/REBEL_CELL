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
_ADD = "hq_kit" not in sys.modules and _KIT not in sys.path
if _ADD:
    sys.path.insert(0, _KIT)
from hq_kit import states as ST          # noqa: E402  the shared room-state language (no kit copies)
if _ADD:
    sys.path.remove(_KIT)

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
LANDMARK_SEMI = (36.0, 30.0)   # city_preset.LANDMARK_FP["aurelian"] ellipse semi-axes: the HQ lot
ROSTRUM = dict(plinth_r=5.0, plinth_z=(3.0, 4.2), tholos_r=4.2, tholos_z=(4.2, 7.5), core_r=1.6, core_top=22.0,
               rings_z=(10.0, 14.0, 18.0, 22.0), laurel_r=7.0, laurel_z=25.0)
TRAVERTINE_FALLBACK = (0.86, 0.78, 0.62)
GILT_FALLBACK = (0.788, 0.639, 0.353)          # DISTRICTS["aurelian"]["sec"]: the city's neon rings are gilt
VERDIGRIS = (0.161, 0.859, 0.651)              # the corp hue (#29DBA6)

# HQ room box in city units (the kit's 14 w x 8 h x 10 d cutaway x k_units)
ROOM = dict(w=3.3, h=1.9, d=2.4)
ROOM_BAY_H = 3.4          # a loggia room fills its arch bay (tier 5.0 minus the base and entablature bands)
LOGE_H = 3.5              # a cavea room is a LOGE in the ring edge: its floor on the next ring's top, its opening in the
                          # riser, cut back 2.4 BU into the seats (roof at most ~0.6 BU proud of the seats behind). 3.5 tall
ATTIC_ROOM_H = 2.9        # so every room clears the 46 px OVERVIEW target (hq_run.py px); the attic room fills its band


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
    ring_line(getattr(ctx, "LAUREL", NEON), hx, hy, R["laurel_z"], R["laurel_r"], 0.42, sc(sec, 1.2), n=40)
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
def st_mid(T, k):
    """The second step of ring k (the concept A / C thumbnails' room floor)."""
    return [t for t in T if t[3] == k][1][2]


def _levels(concept):
    T = terraces()
    rmid = [(RING_R[k] + RING_R[k + 1]) / 2 for k in range(4)]
    zring, rin = [], []
    for k in range(4):
        st = [t for t in T if t[3] == k]
        zring.append(RING_Z[k + 1] + 0.05)             # the loge floor: flush with the next ring's top (arena last)
        rin.append(st[-1][1] + 0.15)                   # its opening on the ring's lit edge
    cav = [dict(name="R%d" % (k + 1), kind="cavea", r=(rin[k] if concept == "B" else rmid[k]),
                z=(zring[k] if concept == "B" else st_mid(T, k)), arc=(160.0, 20.0), inward=True) for k in range(4)]
    rec = LM_DEFAULT["recess"]
    log = [dict(name="T%d" % (k + 1), kind="loggia", r=A - rec, z=k * TIER_H + 0.6, arc=(205.0, 335.0), inward=False,
                tier=k) for k in range(TIERS)]
    attic = dict(name="AT", kind="attic", r=A + 0.2, z=TIERS * TIER_H + 0.05, arc=(205.0, 335.0), inward=False)
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
                                normal=nrm, tier=L.get("tier"), li=li,
                                size=(ROOM["w"], {"loggia": ROOM_BAY_H, "cavea": LOGE_H, "attic": ATTIC_ROOM_H}.get(L["kind"], ROOM["h"]),
                                      ROOM["d"])))           # (w, h, d)
                u += 1
            u += 1
    vz = -11.0 if concept == "C" else ROSTRUM["plinth_z"][1]
    out.append(dict(layer=len(layers) - 1, node=0, level="VAULT", kind="vault", t=270.0, pos=(0.0, -0.0, vz),
                    normal=None, size=(2 * ROSTRUM["tholos_r"], 3.3, 2 * ROSTRUM["tholos_r"]), tier=None, li=None))
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


# ------------------------------------------------------------------ the city_build primitives, pure python
# (same signatures as city_all_corps/scripts/city_build.py, so canonical() runs unchanged on any accumulator with
# .face(pts, col, uv, wc, wl, wm, bid, wet))
def p_circle(cx, cy, r, n, a0=0.0, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def p_prism(acc, pts, z0, z1, col, ts=1.0, top=True, bottom=False, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0,
            top_col=None, uvs=(1.0, 1.0), vz0=None):
    n = len(pts)
    cx, cy = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    tp = [(cx + (x - cx) * ts, cy + (y - cy) * ts) for (x, y) in pts]
    for i in range(n):
        j = (i + 1) % n
        a, c = pts[i], pts[j]
        acc.face([(a[0], a[1], z0), (c[0], c[1], z0), (tp[j][0], tp[j][1], z1), (tp[i][0], tp[i][1], z1)], col, None,
                 wc, wl, wm, bid, wet)
    if top:
        acc.face([(x, y, z1) for (x, y) in tp], top_col or col)
    if bottom:
        acc.face([(x, y, z0) for (x, y) in reversed(pts)], col)


def p_box(acc, x0, y0, z0, x1, y1, z1, col, **kw):
    return p_prism(acc, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, col, **kw)


def p_cyl(acc, cx, cy, z0, z1, r, n, col, ts=1.0, **kw):
    return p_prism(acc, p_circle(cx, cy, r, n), z0, z1, col, ts=ts, **kw)


def _v_cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _v_unit(a):
    L = math.sqrt(sum(x * x for x in a)) or 1.0
    return tuple(x / L for x in a)


def p_bar(acc, p0, p1, w, col, **kw):
    d = tuple(b - a for a, b in zip(p0, p1))
    if math.sqrt(sum(x * x for x in d)) < 1e-6:
        return
    d = _v_unit(d)
    up = (0.0, 0.0, 1.0) if abs(d[2]) < 0.95 else (1.0, 0.0, 0.0)
    s = tuple(x * w / 2 for x in _v_unit(_v_cross(d, up)))
    t = tuple(x * w / 2 for x in _v_unit(_v_cross(d, s)))
    cs = [tuple(a + b for a, b in zip(s, t)), tuple(-a + b for a, b in zip(s, t)), tuple(-a - b for a, b in zip(s, t)),
          tuple(a - b for a, b in zip(s, t))]
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(p + c for p, c in zip(p0, cs[i])), tuple(p + c for p, c in zip(p0, cs[j])),
                  tuple(p + c for p, c in zip(p1, cs[j])), tuple(p + c for p, c in zip(p1, cs[i]))], col)


def p_ring_line(acc, cx, cy, z, r, w, col, n=48, ry=None, **kw):
    ry = r if ry is None else ry
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        p_bar(acc, (cx + r * math.cos(t0), cy + ry * math.sin(t0), z), (cx + r * math.cos(t1), cy + ry * math.sin(t1), z),
              w, col)


def p_annulus(acc, cx, cy, z, r0, r1, col, n=48, k0=1.0, k1=1.0, z1=None, **kw):
    z1 = z if z1 is None else z1
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        acc.face([(cx + r0 * math.cos(t0), cy + r0 * k0 * math.sin(t0), z1), (cx + r0 * math.cos(t1), cy + r0 * k0 * math.sin(t1), z1),
                  (cx + r1 * math.cos(t1), cy + r1 * k1 * math.sin(t1), z), (cx + r1 * math.cos(t0), cy + r1 * k1 * math.sin(t0), z)],
                 col)


def p_sc(c, k):
    return tuple(v * k for v in c)


def bays_for(slot_list):
    """The doorway bays (tier, t0, t1 radians) the loggia slots open in the colonnade (HQ only)."""
    out = []
    for s in slot_list:
        if s["kind"] != "loggia":
            continue
        t = math.radians(s["t"])
        rate = math.hypot(A * math.sin(t), A * BK * math.cos(t))
        dt = (s["size"][0] / 2 + 0.5) / rate
        out.append((s["tier"], (t - dt) % (2 * math.pi), (t + dt) % (2 * math.pi)))
    return out


# ------------------------------------------------------------------ the room cut (HQ): faces minus the room volumes
def _clip(poly, ax, v, keep_less):
    """Sutherland-Hodgman: the part of a convex polygon (local 3-tuples) on one side of the plane coord[ax] = v."""
    out = []
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        ia = (a[ax] <= v) if keep_less else (a[ax] >= v)
        ib = (b[ax] <= v) if keep_less else (b[ax] >= v)
        if ia:
            out.append(a)
        if ia != ib:
            t = (v - a[ax]) / ((b[ax] - a[ax]) or 1e-12)
            out.append(tuple(a[k] + (b[k] - a[k]) * t for k in range(3)))
    return out


class Cutter:
    """Subtracts oriented boxes (a room's opening frame + its volume, in the room's own u / dn / z frame) from faces."""

    def __init__(self, recs, pad=0.12, back=None):
        self.boxes = []
        for r in recs:
            n = r["n"]
            if n is None:
                continue
            t = (n[1], -n[0])
            ox, oy, z0 = r["o"]
            hw = r["w"] / 2 + pad
            d = r["d"] if back is None else back
            self.boxes.append(dict(o=(ox, oy), n=n, t=t, lim=((-hw, hw), (-d - pad, 0.06), (z0 - pad, z0 + r["h"] + pad)),
                                   rad=math.hypot(hw, d + pad) + 0.5))

    def pieces(self, pts):
        polys = [list(pts)]
        for B in self.boxes:
            cx, cy = B["o"]
            if all(math.hypot(p[0] - cx, p[1] - cy) > B["rad"] + 6.0 for p in pts):
                continue
            nxt = []
            for poly in polys:
                (u0, u1), (d0, d1), (z0, z1) = B["lim"]

                def loc(p):
                    dx, dy = p[0] - cx, p[1] - cy
                    return (dx * B["t"][0] + dy * B["t"][1], dx * B["n"][0] + dy * B["n"][1], p[2])

                def wor(q):
                    return (cx + B["t"][0] * q[0] + B["n"][0] * q[1], cy + B["t"][1] * q[0] + B["n"][1] * q[1], q[2])
                L = [loc(p) for p in poly]
                if (max(q[0] for q in L) <= u0 or min(q[0] for q in L) >= u1 or max(q[1] for q in L) <= d0 or
                        min(q[1] for q in L) >= d1 or max(q[2] for q in L) <= z0 or min(q[2] for q in L) >= z1):
                    nxt.append(poly)
                    continue
                rest = L
                for ax, v, less in ((0, u0, True), (0, u1, False), (1, d0, True), (1, d1, False), (2, z0, True),
                                    (2, z1, False)):
                    part = _clip(rest, ax, v, less)
                    if len(part) >= 3:
                        nxt.append([wor(q) for q in part])
                    rest = _clip(rest, ax, v, not less)
                    if len(rest) < 3:
                        break
            polys = nxt
        return polys


# ------------------------------------------------------------------ the HQ-kit build (spec 8.5)
GILT_DIM_DECISION = 0.45      # designer default 2026-10-18: the gilt lines dimmed next to the orange option links


class _KitAcc:
    """A city-signature accumulator (face(pts, col, uv, wc, wl, ...)) writing into an HQ-kit Acc in kit units, minus the
    room volumes; emission accumulators turn the colour's peak into the face strength k."""

    def __init__(self, acc, ks, cut, emit_k=None):
        self.acc, self.ks, self.cut, self.emit_k = acc, ks, cut, emit_k

    def face(self, pts, col, uv=None, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0):
        P = [(p[0] * self.ks, p[1] * self.ks, p[2] * self.ks) for p in pts]
        if self.emit_k is None:
            c, k = tuple(col), 0.0
        else:
            m = max(max(col), 1e-4)
            c, k = tuple(v / m for v in col), self.emit_k * m
        for poly in (self.cut.pieces(P) if self.cut else [P]):
            self.acc.face(poly, c, k)


def build_hq(K, rooms=True):
    """HQ-kit hook (hq_scene.py: build(K) -> hooks). The canonical colosseum in kit units (x 1 / k_units) with the
    route's doorway bays and room cuts, the lit loggia arches, the room cutaways, THE CONCORDAT VAULT in the tholos and
    the landmark light rig (DESIGN.md section 6). K.G must be this corp's hq_graph (G.SLOTS, G.ROOM, G.NODES)."""
    ks = 1.0 / K_UNITS
    G = K.G if rooms else None
    LH, A_ = K.LH, K.A
    hooks = {"accs": {}, "beams": [], "mover_lights": {}, "no_cut": ()}
    rooms_ = [i for i in G.NODES if i not in ("start", "srv")] if G else []
    cut = Cutter([G.ROOM[i] for i in rooms_], pad=0.5) if G else None
    gilt_acc = K.Acc("gilt", K.M["emit"], 1, K.COLL["compound"])
    loggia_acc = K.Acc("loggia", K.M["emit"], 1, K.COLL["compound"])
    laurel_acc = K.Acc("laurel", K.M["emit"], 1, K.COLL["compound"])     # the laurel ring is its own object (OVERVIEW dim)
    hooks["accs"].update(gilt=gilt_acc, loggia=loggia_acc, laurel=laurel_acc)
    lights = []

    def spot_at(target, frm, col, power, cone=30.0):
        lights.append((target, frm, col, power, cone))
    ctx = type("Ctx", (), {})()
    ctx.SURF = _KitAcc(A_["civic"], ks, cut)
    ctx.SMOOTH = _KitAcc(A_["civic"], ks, cut)
    ctx.NEON = _KitAcc(gilt_acc, ks, cut, LH["gilt_k"])
    ctx.LAUREL = _KitAcc(laurel_acc, ks, cut, LH["gilt_k"])
    ctx.prism, ctx.box, ctx.cyl, ctx.bar = p_prism, p_box, p_cyl, p_bar
    ctx.ring_line, ctx.annulus, ctx.circle, ctx.sc = p_ring_line, p_annulus, p_circle, p_sc
    ctx.spot_at = spot_at
    ctx.district = dict(mat=[K.pal("travertine")], sec=K.pal("gilt"))
    ctx.CP = None
    ctx.arena_open = False
    open_bays = bays_for(G.SLOTS) if G else []
    info = canonical(ctx, 0.0, 0.0, open_bays=open_bays)
    # the lit loggia: an arch panel in every bay of every tier on the recessed wall (the city shader's lit arches)
    LG = _KitAcc(loggia_acc, ks, cut, LH["loggia_k"])
    rw = A - LM_DEFAULT["recess"] + 0.04            # just proud of the recessed wall, behind the columns
    warm = K.pal("loggia")
    ncol = LM_DEFAULT["cols"]
    for k in range(TIERS):
        z0, z1 = k * TIER_H + 0.45, (k + 1) * TIER_H - 1.0
        for m in range(ncol):
            t0, t1 = 2 * math.pi * (m + 0.18) / ncol, 2 * math.pi * (m + 0.82) / ncol
            tm = (t0 + t1) / 2
            p0, p1 = ell(t0, rw), ell(t1, rw)
            half = 0.5 * math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            zs = z1 - half                                  # the springing line: a round arch head
            pts = [(p0[0], p0[1], z0), (p1[0], p1[1], z0), (p1[0], p1[1], zs)]
            for q in range(1, 6):
                a = math.pi * q / 6
                tt = tm + (t1 - tm) * math.cos(a)
                x, y = ell(tt, rw)
                pts.append((x, y, zs + half * math.sin(a)))
            pts.append((p0[0], p0[1], zs))
            LG.face(pts, sc_jit(warm, m, k))
    # warm cove strips under every entablature (the travertine's own light line)
    CV = _KitAcc(A_["trim"], ks, cut, LH["cove_k"])
    for k in range(TIERS):
        p_ring_line(CV, 0.0, 0.0, (k + 1) * TIER_H - 0.78, A - LM_DEFAULT["recess"] + 0.08, 0.12, K.pal("loggia"),
                    n=NSEG, ry=(A - LM_DEFAULT["recess"] + 0.08) * BK)
    # the route rooms (the kit cutaway) and THE CONCORDAT VAULT's server core inside the tholos
    if G:
        for i in rooms_:
            K.room_shell(i, G.ROOM[i])
        emv = K.ROOM_EMIT.setdefault("srv", K.Acc("room_srv", K.M["emit"], 5, K.COLL["rooms"]))
        SV = _KitAcc(emv, ks, None, LH["server_k"])
        R = ROSTRUM
        z0 = R["tholos_z"][0]
        p_cyl(SV, 0.0, 0.0, z0 + 0.2, z0 + 0.35, 2.6, 24, K.pal("server"))
        for q in range(5):
            zz = z0 + 0.6 + q * 0.55
            p_ring_line(SV, 0.0, 0.0, zz, R["core_r"] + 0.12, 0.16, K.pal("server"), n=20)
        for q in range(6):                                    # racks round the core
            t = 2 * math.pi * (q + 0.5) / 6
            cx, cy = 2.9 * math.cos(t), 2.9 * math.sin(t)
            p_box(_KitAcc(A_["metal"], ks, None), cx - 0.3, cy - 0.3, z0, cx + 0.3, cy + 0.3, z0 + 2.4, (0.05, 0.05, 0.06))
            for zz in (0.5, 1.1, 1.7):
                p_box(SV, cx - 0.32, cy - 0.32, z0 + zz, cx + 0.32, cy + 0.32, z0 + zz + 0.08, K.pal("server"))
        # the inscription band on the tholos entablature (CONCORDAT VAVLT; a lit gilt band at this scale)
        p_ring_line(_KitAcc(gilt_acc, ks, None, LH["gilt_k"] * 1.3), 0.0, 0.0, R["tholos_z"][1] + 0.25, 4.85, 0.18,
                    K.pal("gilt"), n=40)
    # ------------------------------------------------------------ the light rig (kit units; powers x ks^2)
    k2 = ks * ks
    for n_, (tgt, frm, col, power, cone) in enumerate(lights):        # the two canonical arena searchlights
        K.add_light("arena_%d" % n_, "SPOT", tuple(v * ks for v in frm), power * k2 * LH["flood_k"], col,
                    aim=tuple(v * ks for v in tgt), size=1.0, spot=cone, blend=0.85, group="corp", shadow=False)
    nup = LH["up_n"]
    for q in range(nup):                                      # base uplights grazing the colonnade
        t = 2 * math.pi * (q + 0.5) / nup
        x, y = ell(t, A + 2.4)
        ax, ay = ell(t, A - 0.6)
        K.add_light("up_%d" % q, "SPOT", (x * ks, y * ks, 0.3 * ks), LH["up_w"], K.pal("uplight"),
                    aim=(ax * ks, ay * ks, 13.0 * ks), size=0.6 * ks, spot=44, blend=0.7, group="corp", shadow=False)
    for sx in (-1, 1):                                        # the cavea fill over the near rim, down the far half
        K.add_light("cavea_%d" % (sx + 1), "AREA", (sx * 13.0 * ks, -16.0 * ks, 44.0 * ks), LH["cavea_w"],
                    K.pal("cavea_fill"), aim=(sx * 9.0 * ks, 14.0 * ks, 8.0 * ks), size=18.0 * ks, size_y=10.0 * ks,
                    group="corp", shadow=False)
    K.add_light("vault_key", "SPOT", (0.0, -14.0 * ks, 15.0 * ks), LH["vault_key_w"], K.pal("uplight"),
                aim=(0.0, 0.0, 5.5 * ks), size=0.5 * ks, spot=24, blend=0.6, group="corp", shadow=False)
    bo = tuple(v * ks for v in info["crown"])
    hooks["beams"].append((bo, (0.0, 0.0, 1.0), tuple(K.pal("gilt")), K.HZ["beams"]["power"], K.HZ["beams"]["cone"]))
    import bpy
    rimrx = bpy.data.collections.new("rim_rx")
    for q, (rx, ry, colk) in enumerate(((-46.0, 64.0, "rim_a"), (44.0, 70.0, "rim_b"))):
        K.add_light("rim_%d" % q, "AREA", (rx * ks, ry * ks, 26.0 * ks), LH["rim_w"], K.pal(colk),
                    aim=(0.0, 0.0, 10.0 * ks), size=40.0 * ks, size_y=12.0 * ks, group="corp", shadow=False,
                    receivers=rimrx)

    def post_build(OBJ):
        for ob in OBJ.values():
            if ob is not None and any(c.name == "compound" for c in ob.users_collection):
                rimrx.objects.link(ob)
    hooks["post_build"] = post_build

    # the city lift (round 2 test fixes): block uplights on the rectangle of the boulevard, aimed up at the first row of
    # blocks, light-linked to the city and the ground only (the landmark's own light is unchanged)
    dtc = K.HZ["downtown"]
    kx, ky = dtc["keep"][1] + dtc["street0"] * 0.5, dtc["keep"][2] + dtc["street0"] * 0.5
    nfill = int(LH.get("fill_n", 0))
    if nfill:
        import bpy
        fillrx = bpy.data.collections.new("cityfill_rx")
        per = 2.0 * (2.0 * kx + 2.0 * ky)
        for q in range(nfill):
            d = per * (q + 0.5) / nfill
            # walk the rectangle perimeter: (x, y, outward normal)
            segs = ((2 * kx, (-kx, -ky), (1, 0), (0, -1)), (2 * ky, (kx, -ky), (0, 1), (1, 0)),
                    (2 * kx, (kx, ky), (-1, 0), (0, 1)), (2 * ky, (-kx, ky), (0, -1), (-1, 0)))
            for (ln, o, dr, nr) in segs:
                if d < ln:
                    px, py = o[0] + dr[0] * d, o[1] + dr[1] * d
                    nx_, ny_ = nr
                    break
                d -= ln
            warm = (1.0, 0.62, 0.30) if q % 3 else (0.55, 0.80, 1.0)
            reach = 70.0
            K.add_light("cityfill_%d" % q, "SPOT", (px, py, 5.0), LH["fill_w"], warm,
                        aim=(px + nx_ * reach, py + ny_ * reach, 55.0), size=2.0, spot=LH.get("fill_cone", 95.0), blend=0.8,
                        group="corp", shadow=False, receivers=fillrx)

        # the camera-side city fill: one soft area light at the camera, aimed at the target, linked to the city and the
        # ground only (the facades that face the camera are the ones the view sees; per frame, scaled by distance^2)
        K.add_light("camfill", "AREA", (0.0, 0.0, 100.0), LH.get("camfill_w", 0.0), (0.62, 0.76, 1.0), aim=(0.0, 0.0, 0.0),
                    size=60.0, size_y=60.0, group="corp", shadow=False, receivers=fillrx)

        def fill_link(OBJ, _prev=post_build):
            _prev(OBJ)
            for k_ in ("city", "city_neon", "city_sign", "city_small", "city_metal", "ground", "sky"):
                if OBJ.get(k_) is not None:
                    fillrx.objects.link(OBJ[k_])
        hooks["post_build"] = fill_link

    def apply(fr, c):
        # a view ray crosses a column of cut blocks (2 transparent walls each): the engine's 16 transparent bounces end
        # it black (a dark "mast" in front of the colonnade). Aurelian only; the preset says how many.
        import bpy
        try:
            bpy.context.scene.cycles.transparent_max_bounces = int(LH.get("transparent_bounces", 16))
        except (AttributeError, TypeError):
            pass
        if K.JOB.get("hide_by_frame"):                         # debug: hide named objects per frame
            for ob_ in c["OBJ"].values():
                if ob_ is not None:
                    ob_.hide_render = ob_.name in K.JOB["hide_by_frame"].get(fr.get("name"), ())
        ob = c["OBJ"].get("gilt")
        ov = c["zoom"] < 0.5
        if ob is not None:
            c["set_pwo"](ob, (GILT_DIM_DECISION if c["zoom"] > 0.5 else 1.0) * c["cut"])
        for nm, kk in (("loggia", LH.get("ov_loggia", 1.0)), ("laurel", LH.get("ov_laurel", 1.0))):
            if c["OBJ"].get(nm) is not None:
                c["set_pwo"](c["OBJ"][nm], (kk if ov else 1.0) * c["cut"])
        fk = LH.get("fill_frame", {}).get(fr.get("name"), 1.0)
        for (lob, e0, grp) in c["LIGHTS"]:
            if lob.name.startswith("cityfill_"):
                lob.data.energy = e0 * fk * c["cut"]
            elif lob.name == "camfill":
                from mathutils import Vector
                loc, tgt = Vector(fr["pose"]["loc"]), Vector(fr["pose"]["tgt"])
                d_ = (loc - tgt).length
                lob.location = loc + Vector((0.0, 0.0, 0.12 * d_))
                lob.rotation_euler = (tgt - lob.location).to_track_quat("-Z", "Y").to_euler()
                lob.data.size = lob.data.size_y = 0.25 * d_
                lob.data.energy = e0 * (d_ / 265.0) ** 2 * LH.get("camfill_frame", {}).get(fr.get("name"), 1.0) * c["cut"]
            elif lob.name.startswith("up_"):                   # the colonnade uplights: per-frame trim (landmark / city ratio)
                lob.data.energy = e0 * LH.get("up_frame", {}).get(fr.get("name"), 1.0) * c["cut"]
    hooks["apply"] = apply
    K.log("aurelian landmark: rooms", len(rooms_), "open bays", len(open_bays), "lights", len(lights) + nup + 6)
    return hooks


def sc_jit(c, m, k):
    """Seeded-free tone jitter for the loggia arches (R-REP-1): a fixed per-bay pattern, deterministic by index."""
    j = 0.82 + 0.18 * (((m * 7 + k * 3) % 5) / 4.0)
    return tuple(v * j for v in c)
