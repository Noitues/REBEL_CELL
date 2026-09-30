"""R2A LOW-POLY 3D: the city diorama (one layout, three lighting modes).

build_city(mode) with mode in {"day", "night", "alert"}. The layout rng (seed LAYOUT_SEED) is consumed
identically in every mode, so the city is the same; each mode only swaps materials and adds extras
from its own seeded stream.
"""
import bpy
import math
import random
from mathutils import Vector
import lp_lib as L

LAYOUT_SEED = 1207
NX, NY = 8, 6
B, S = 4.0, 2.0
P = B + S
X0 = -NX * P / 2
Y0 = -NY * P / 2
WATER_ROW = 2
BRIDGES = (2, 5, 7)


def lx(i):
    return X0 + i * P


def ly(j):
    return Y0 + j * P


# ---- the node-and-path overlay (street intersections) --------------------------------
NODES = {
    "A": ((1, 1), "home"),
    "B": ((4, 1), "target"),
    "C": ((2, 3), "site"),
    "D": ((5, 4), "target"),
    "E": ((3, 5), "site"),
    "F": ((7, 5), "target"),
    "G": ((5, 5), "boss"),
}
PATHS = [
    [(1, 1), (4, 1)],
    [(1, 1), (1, 2), (2, 2), (2, 3)],
    [(4, 1), (5, 1), (5, 4)],
    [(2, 3), (2, 5), (3, 5)],
    [(3, 5), (5, 5)],
    [(5, 4), (5, 5)],
    [(5, 4), (7, 4), (7, 5)],
]
HERE = "A"
# blocks directly south of an east-west path segment stay low so the path reads from the camera
LOW_BLOCKS = {(1, 0), (2, 0), (3, 0), (1, 1), (3, 4), (4, 4), (5, 3), (6, 3)}
# landmark blocks (col, row)
MEGATOWER = (5, 5)
ARCOLOGY = (1, 4)
DISHHUB = (7, 3)
DOME = (3, 3)
PARK = (6, 1)
BILLBOARD = (2, 4)

MODE_PAL = {
    "day": dict(
        glass=("#6d7482", "#8d93a0", "#7f8fa3", "#998b9b"), glass_emit=(0, 0, 0, 0),
        signs=("#c7708c", "#5aa6a8", "#d49a58"), sign_emit=0.35,
        path="#2fb8c4", path_emit=0.7, node_top_emit=1.2, beacon_emit=1.5,
        water="#6f9aa0",
    ),
    "night": dict(
        glass=("#2a2c3e", "#ffc27a", "#7ee8ff", "#ff72bd"), glass_emit=(0, 3.2, 3.0, 3.0),
        signs=("#ff3fa4", "#35e6ff", "#ffb040"), sign_emit=7.0,
        path="#40f0ff", path_emit=5.0, node_top_emit=6.0, beacon_emit=7.0,
        water="#232f49",
    ),
    "alert": dict(
        glass=("#2a2030", "#ff9a66", "#6fdcff", "#ff4466"), glass_emit=(0, 3.0, 3.2, 2.6),
        signs=("#ff2a4a", "#ff5a3a", "#ffb040"), sign_emit=8.0,
        path="#40f0ff", path_emit=5.0, node_top_emit=6.0, beacon_emit=8.0,
        water="#2c1c30",
    ),
}

NODE_COL = {"home": "#ffc34d", "target": "#39e0ff", "site": "#b8ff6a", "boss": "#ff3f7a"}


def materials(mode):
    p = MODE_PAL[mode]
    M = []
    M.append(L.mat_flat("asphalt", "#5d5560"))            # 0
    M.append(L.mat_flat("pavement", "#b8a898"))           # 1
    M.append(L.mat_flat("body_a", "#d0b397"))             # 2 sand
    M.append(L.mat_flat("body_b", "#bc8d84"))             # 3 dusty rose
    M.append(L.mat_flat("body_c", "#9d93aa"))             # 4 lavender grey
    M.append(L.mat_flat("body_d", "#7d8797"))             # 5 slate
    M.append(L.mat_flat("body_e", "#e0cdb0"))             # 6 cream
    M.append(L.mat_flat("roof", "#a39287"))               # 7
    for k, (c, e) in enumerate(zip(p["glass"], p["glass_emit"])):   # 8..11
        if e > 0:
            M.append(L.mat_flat("glass%d" % k, c, emit=c, emit_str=e))
        else:
            M.append(L.mat_flat("glass%d" % k, c, rough=0.6, spec=0.3))
    for k, c in enumerate(p["signs"]):                                # 12..14
        M.append(L.mat_flat("sign%d" % k, c, emit=c, emit_str=p["sign_emit"]))
    M.append(L.mat_flat("water", p["water"], rough=0.35, spec=0.5))  # 15
    M.append(L.mat_flat("foliage", "#8fa36a"))            # 16
    M.append(L.mat_flat("trunk", "#7a5a4a"))              # 17
    M.append(L.mat_flat("rock", "#8c6d68"))               # 18
    red_e = 6.0 if mode != "day" else 0.8
    M.append(L.mat_flat("beacon_red", "#ff3a4a", emit="#ff3a4a", emit_str=red_e))  # 19
    M.append(L.mat_flat("metal", "#524a58"))              # 20
    M.append(L.mat_flat("rock_dark", "#6c5359"))          # 21
    return M


BODY = (2, 3, 4, 5, 6)


def _building(pb, rng, cx, cy, w, d, h, style_rng):
    """Generic faceted tower with ribbon or strip windows. Consumes rng identically in every mode."""
    body = rng.choice(BODY)
    fh = rng.choice((0.9, 1.0, 1.1))
    floors = max(1, int(h / fh))
    h = floors * fh
    sill = rng.uniform(0.35, 0.5)
    chamfer = rng.choice((0.0, 0.0, 0.25, 0.4)) if min(w, d) > 1.6 else 0.0
    per = L.perimeter(w, d, seg=rng.choice((0.7, 0.9, 1.1)), chamfer=chamfer)
    taper = rng.choice((0.0, 0.0, 0.05, 0.1))
    pattern = rng.choice(("ribbon", "strip", "ribbon", "grid"))
    zs = [0.0]
    kinds = []
    for k in range(floors):
        z = k * fh
        zs.append(z + fh * sill)
        kinds.append("slab")
        zs.append(z + fh)
        kinds.append("win")
    # parapet slab on top
    zs.append(h + 0.18)
    kinds.append("slab")
    win_pick = [rng.random() for _ in range(len(kinds) * len(per))]

    def mfn(k, i):
        if kinds[k] != "win":
            return body
        if pattern == "strip" and i % 2 == 1:
            return body
        if pattern == "grid" and (i + k // 2) % 3 == 2:
            return body
        r = win_pick[(k * len(per) + i) % len(win_pick)]
        if r < 0.45:
            return 8
        return 9 if r < 0.72 else (10 if r < 0.9 else 11)

    roof = rng.choice(("flat", "flat", "pyramid", "step"))
    cap_dz = rng.uniform(0.6, 1.6) if roof == "pyramid" else 0.0
    pb.rings(per, zs, mfn, jit=0.1, taper=taper, cx=cx, cy=cy, cap_dz=cap_dz, mi_cap=7)
    top = h + 0.18
    if roof == "step":
        s = 1 - taper
        pb.prism(L.rect(w * s * 0.55, d * s * 0.55), top, top + rng.uniform(0.6, 1.5), body, 7,
                 jit=0.04, cx=cx + rng.uniform(-0.2, 0.2), cy=cy + rng.uniform(-0.2, 0.2))
    if roof == "flat" and rng.random() < 0.6:
        s = 1 - taper
        bw = rng.uniform(0.4, 0.8)
        pb.prism(L.rect(bw, bw * rng.uniform(0.6, 1.2)), top, top + rng.uniform(0.3, 0.6), 20, 20,
                 jit=0.03, cx=cx + rng.uniform(-w * s / 4, w * s / 4), cy=cy + rng.uniform(-d * s / 4, d * s / 4))
    sign = rng.random() < 0.35 and h > 2.5
    sign_k = rng.randrange(3)
    sign_side = rng.choice((-1, 1))
    sign_z = rng.uniform(0.35, 0.7) * h
    if sign:
        # vertical neon blade on the front (-y) face corner
        sx = cx + sign_side * (w * (1 - taper * sign_z / h) / 2 - 0.05)
        sy = cy - d / 2 - 0.08
        pb.prism(L.rect(0.18, 0.5), sign_z - 0.9, sign_z + 0.9, 12 + sign_k, 12 + sign_k, jit=0.02,
                 cx=sx, cy=sy - 0.25)
    return top


def build_city(mode, coll=None):
    rng = random.Random(LAYOUT_SEED)
    mats = materials(mode)
    pb = L.PB()
    W = NX * P + S + 1.0
    D = NY * P + S + 1.0
    # --- island slab: faceted sides down to the floor
    outline = L.perimeter(W, D, seg=3.0, chamfer=2.0)
    jr = random.Random(LAYOUT_SEED + 1)
    zs = [0.0, -0.9, -2.4]
    rings = []
    for k, z in enumerate(zs):
        grow = (0.0, 0.35, -0.2)[k]
        ring = []
        for x, y in outline:
            v = Vector((x, y))
            v = v + v.normalized() * (grow + (jr.uniform(-0.3, 0.3) if k else 0))
            ring.append(pb.vert((v.x, v.y, z + (jr.uniform(-0.2, 0.2) if k else 0)), 0.0))
        rings.append(ring)
    n = len(outline)
    for k in range(2):
        for i in range(n):
            a, b = i, (i + 1) % n
            pb.face([rings[k + 1][a], rings[k + 1][b], rings[k][b], rings[k][a]], 18 if k == 0 else 21)
    c = pb.vert((0, 0, 0), 0.0)
    for i in range(n):
        pb.face([rings[0][i], rings[0][(i + 1) % n], c], 0)

    # --- water canal (block row WATER_ROW), with quays and bridges
    wy0 = ly(WATER_ROW) + S / 2 - 0.15
    wy1 = ly(WATER_ROW + 1) - S / 2 + 0.15
    pb.prism([(-W / 2 - 0.2, wy0), (W / 2 + 0.2, wy0), (W / 2 + 0.2, wy1), (-W / 2 - 0.2, wy1)],
             -0.3, 0.035, 15, 15, jit=0.0)
    for yy in (wy0 - 0.12, wy1 + 0.12):
        pb.prism(L.rect(W, 0.3), 0.0, 0.16, 1, 1, cy=yy)
    for i in BRIDGES:
        x = lx(i)
        pb.prism(L.rect(S * 0.95, wy1 - wy0 + 0.6), 0.0, 0.22, 20, 1, cx=x, cy=(wy0 + wy1) / 2)
        for side in (-1, 1):
            pb.prism(L.rect(0.14, wy1 - wy0 + 0.6), 0.22, 0.5, 20, 20, cx=x + side * S * 0.45, cy=(wy0 + wy1) / 2)

    # --- blocks
    for col in range(NX):
        for row in range(NY):
            cx = lx(col) + P / 2
            cy = ly(row) + P / 2
            if row == WATER_ROW:
                continue
            pb.prism(L.rect(B, B), 0.0, 0.12, 1, 1, cx=cx, cy=cy, jit=0.0)
            key = (col, row)
            if key == PARK:
                _park(pb, rng, cx, cy)
                continue
            if key == MEGATOWER:
                _megatower(pb, rng, cx, cy)
                continue
            if key == ARCOLOGY:
                _arcology(pb, rng, cx, cy)
                continue
            if key == DISHHUB:
                _dishhub(pb, rng, cx, cy)
                continue
            if key == DOME:
                _dome(pb, rng, cx, cy)
                continue
            hmin, hmax = ((1.0, 2.2), (1.4, 3.2), (0, 0), (2.0, 4.6), (2.6, 6.0), (3.4, 8.0))[row]
            if key in LOW_BLOCKS:
                hmax = min(hmax, 2.2)
                hmin = min(hmin, 1.2)
            split = rng.choice(("one", "two", "two", "four"))
            if split == "one":
                lots = [(0, 0, B - 0.6, B - 0.6)]
            elif split == "two":
                if rng.random() < 0.5:
                    lots = [(-B / 4, 0, B / 2 - 0.35, B - 0.6), (B / 4, 0, B / 2 - 0.35, B - 0.6)]
                else:
                    lots = [(0, -B / 4, B - 0.6, B / 2 - 0.35), (0, B / 4, B - 0.6, B / 2 - 0.35)]
            else:
                q = B / 4
                lots = [(-q, -q, B / 2 - 0.4, B / 2 - 0.4), (q, -q, B / 2 - 0.4, B / 2 - 0.4),
                        (-q, q, B / 2 - 0.4, B / 2 - 0.4), (q, q, B / 2 - 0.4, B / 2 - 0.4)]
            for (ox, oy, w, d) in lots:
                h = rng.uniform(hmin, hmax)
                if key in LOW_BLOCKS and oy > 0:
                    h = min(h * 1.3, 2.6)
                top = _building(pb, rng, cx + ox, cy + oy, w, d, h, rng)
                if key == BILLBOARD and ox <= 0 and oy <= 0:
                    _billboard(pb, rng, cx + ox, cy + oy, top)

    city = pb.build("city", mats, seed=LAYOUT_SEED, coll=coll)
    return city, mats


def _park(pb, rng, cx, cy):
    pb.prism(L.rect(B - 0.3, B - 0.3), 0.12, 0.2, 16, 16, cx=cx, cy=cy)
    for k in range(7):
        x = cx + rng.uniform(-1.4, 1.4)
        y = cy + rng.uniform(-1.4, 1.4)
        pb.prism(L.ngon(4, 0.09), 0.2, 0.6, 17, 17, cx=x, cy=y)
        r = rng.uniform(0.45, 0.7)
        pb.prism(L.ngon(5, r, rot=rng.uniform(0, 1)), 0.5, 0.5 + r * 0.8, 16, 16, top_scale=0.55, cx=x, cy=y,
                 top_center_dz=r * 0.9, jit=0.06)


def _megatower(pb, rng, cx, cy):
    """Corporate spire: hex prism in tapering segments with neon bands, crowned by a faceted spike."""
    z = 0.0
    r = 1.9
    segs = [(4.0, 1.0), (4.0, 0.86), (3.6, 0.72), (3.0, 0.6)]
    for k, (hh, s) in enumerate(segs):
        rr = r * s
        per = L.ngon(6, rr, rot=math.pi / 6)
        zs = [z, z + hh * 0.12, z + hh * 0.5, z + hh * 0.62, z + hh]
        band = [5, 13, 5, 8, 5]

        def mfn(kk, i, band=band):
            if kk == 1:
                return 12
            if kk == 3:
                return 10 if i % 2 == 0 else 8
            return 4 if i % 2 else 5
        pb.rings([(x, y) for x, y in per], zs, mfn, jit=0.06, taper=0.0, cx=cx, cy=cy, mi_cap=7)
        z += hh
    pb.prism(L.ngon(6, r * 0.45, rot=math.pi / 6), z, z + 3.6, 5, 4, top_scale=0.05, cx=cx, cy=cy, jit=0.04)
    pb.prism(L.ngon(4, 0.07), z + 3.4, z + 4.4, 19, 19, cx=cx, cy=cy)
    # crown fins
    for k in range(3):
        a = k * 2 * math.pi / 3
        fx, fy = cx + math.cos(a) * r * 0.5, cy + math.sin(a) * r * 0.5
        pb.prism([(0, -0.08), (0.5, -0.08), (0.5, 0.08), (0, 0.08)], z - 1.5, z + 1.2, 20, 12,
                 top_scale=0.3, cx=fx, cy=fy)


def _arcology(pb, rng, cx, cy):
    z = 0.12
    for k, (s, hh) in enumerate(((3.7, 1.4), (3.0, 1.4), (2.3, 1.4), (1.6, 1.3), (0.9, 1.0))):
        per = L.perimeter(s, s, seg=0.8, chamfer=0.25)
        zs = [z, z + hh * 0.45, z + hh]

        def mfn(kk, i):
            return 3 if kk == 0 else (9 if i % 3 else 8)
        pb.rings(per, zs, mfn, jit=0.05, taper=0.08, cx=cx, cy=cy, mi_cap=16 if k < 4 else 7,
                 cap_dz=0.0 if k < 4 else 0.8)
        z += hh


def _dishhub(pb, rng, cx, cy):
    per = L.ngon(7, 1.1)
    zs = [0.12, 2.0, 2.4, 4.4, 4.8, 6.2]

    def mfn(kk, i):
        return (8 if kk in (1, 3) else (5 if kk % 2 == 0 else 13))
    pb.rings(per, zs, mfn, jit=0.05, taper=0.2, cx=cx - 0.6, cy=cy + 0.4, mi_cap=20)
    # tilted faceted dish: shallow cone of 8 sides facing the camera-left
    dcx, dcy, dcz = cx - 0.6, cy + 0.2, 7.4
    ring = []
    rim = 2.0
    tilt = math.radians(50)
    for i in range(9):
        a = i * 2 * math.pi / 9
        x = math.cos(a) * rim
        y0 = math.sin(a) * rim
        # rotate around x axis by tilt so the dish faces -y and up
        y = y0 * math.cos(tilt)
        z = y0 * math.sin(tilt)
        ring.append(pb.vert((dcx + x, dcy + y, dcz + z), 0.03))
    back = pb.vert((dcx, dcy + 0.55 * math.sin(tilt) * 1.5, dcz - 0.55 * math.cos(tilt) * 1.5), 0.0)
    front = pb.vert((dcx, dcy + 0.2, dcz - 0.3), 0.0)
    for i in range(9):
        a, b = ring[i], ring[(i + 1) % 9]
        pb.face([a, b, front], 6)
        pb.face([b, a, back], 20)
    pb.prism(L.ngon(4, 0.12), 6.2, 7.3, 20, 20, cx=dcx, cy=dcy + 0.2)
    pb.prism(L.ngon(4, 0.06), 7.0, 8.6, 20, 19, cx=dcx, cy=dcy - 0.4, top_scale=0.4)
    # low annex
    _building(pb, rng, cx + 1.1, cy - 1.0, 1.4, 1.4, 1.8, rng)


def _dome(pb, rng, cx, cy):
    # faceted half-dome: rings of a 10-gon
    n = 10
    R = 1.85
    lat = [0, 22, 45, 68]
    ids = []
    for k, a in enumerate(lat):
        r = R * math.cos(math.radians(a))
        z = 0.5 + R * math.sin(math.radians(a))
        ids.append([pb.vert((cx + math.cos(i * 2 * math.pi / n + k * 0.3) * r,
                             cy + math.sin(i * 2 * math.pi / n + k * 0.3) * r, z), 0.04 if k else 0.0)
                    for i in range(n)])
    for k in range(len(lat) - 1):
        for i in range(n):
            a, b = i, (i + 1) % n
            mi = 6 if (i + k) % 3 else (10 if k == 1 else 6)
            pb.face([ids[k][a], ids[k][b], ids[k + 1][b], ids[k + 1][a]], mi)
    top = pb.vert((cx, cy, 0.5 + R), 0.0)
    for i in range(n):
        pb.face([ids[-1][i], ids[-1][(i + 1) % n], top], 6)
    pb.prism(L.ngon(n, R + 0.05), 0.12, 0.5, 1, 1, cx=cx, cy=cy)


def _billboard(pb, rng, x, y, top):
    for sx in (-0.7, 0.7):
        pb.prism(L.ngon(4, 0.07), top, top + 1.0, 20, 20, cx=x + sx, cy=y)
    pts = [(-1.4, -0.08), (1.4, -0.08), (1.4, 0.08), (-1.4, 0.08)]
    # the panel: a vertical slab facing -y; built as a thin prism rotated by hand
    z0, z1 = top + 0.9, top + 2.3
    a = pb.vert((x - 1.4, y - 0.1, z0), 0.02)
    b = pb.vert((x + 1.4, y - 0.1, z0), 0.02)
    c = pb.vert((x + 1.4, y - 0.1, z1), 0.02)
    d = pb.vert((x - 1.4, y - 0.1, z1), 0.02)
    m = pb.vert((x - 0.2, y - 0.12, (z0 + z1) / 2), 0.0)
    pb.face([a, b, m], 12)
    pb.face([b, c, m], 13)
    pb.face([c, d, m], 12)
    pb.face([d, a, m], 14)
    e = pb.vert((x - 1.4, y + 0.1, z0), 0.0)
    f = pb.vert((x + 1.4, y + 0.1, z0), 0.0)
    g = pb.vert((x + 1.4, y + 0.1, z1), 0.0)
    h = pb.vert((x - 1.4, y + 0.1, z1), 0.0)
    pb.face([f, e, h, g], 20)
    pb.face([a, d, h, e], 20)
    pb.face([b, f, g, c], 20)
    pb.face([d, c, g, h], 20)


# ---- overlay ---------------------------------------------------------------------------

def build_overlay(mode, coll=None):
    p = MODE_PAL[mode]
    path_mat = L.mat_flat("path", p["path"], emit=p["path"], emit_str=p["path_emit"])
    path_edge = L.mat_flat("path_edge", "#1c2230")
    puck_mat = L.mat_flat("puck", "#3a3346")
    puck_rim = L.mat_flat("puck_rim", "#e8dccb")
    tops = {k: L.mat_flat("ntop_" + k, c, emit=c, emit_str=p["node_top_emit"]) for k, c in NODE_COL.items()}
    icons = {k: L.mat_flat("nicon_" + k, c, emit=c, emit_str=p["beacon_emit"] * 0.5) for k, c in NODE_COL.items()}
    mats = [path_mat, path_edge, puck_mat, puck_rim] + [tops[k] for k in NODE_COL] + [icons[k] for k in NODE_COL]
    kidx = {k: 4 + i for i, k in enumerate(NODE_COL)}
    iidx = {k: 8 + i for i, k in enumerate(NODE_COL)}
    pb = L.PB()
    zp = 0.05
    # paths: flat faceted ribbons with a dark keyline, on the street plane
    for path in PATHS:
        pts = [Vector((lx(i), ly(j), 0)) for i, j in path]
        for a, b in zip(pts[:-1], pts[1:]):
            d = (b - a)
            L_ = d.length
            dn = d.normalized()
            nrm = Vector((-dn.y, dn.x, 0))
            for w, z, mi in ((0.62, zp, 1), (0.36, zp + 0.03, 0)):
                a2 = a - dn * (w / 2)
                b2 = b + dn * (w / 2)
                q = [a2 + nrm * w / 2, a2 - nrm * w / 2, b2 - nrm * w / 2, b2 + nrm * w / 2]
                # CCW from above
                qs = [(v.x, v.y) for v in q]
                if (qs[1][0] - qs[0][0]) * (qs[2][1] - qs[0][1]) - (qs[1][1] - qs[0][1]) * (qs[2][0] - qs[0][0]) < 0:
                    qs = qs[::-1]
                pb.prism(qs, z - 0.03, z, mi, mi)
            # chevrons along the segment
            steps = int(L_ / 1.6)
            for s in range(1, steps):
                c = a + dn * (s * L_ / steps)
                tip = c + dn * 0.28
                l = c - dn * 0.1 + nrm * 0.22
                r = c - dn * 0.1 - nrm * 0.22
                tri = [(r.x, r.y), (tip.x, tip.y), (l.x, l.y)]
                if (tri[1][0] - tri[0][0]) * (tri[2][1] - tri[0][1]) - (tri[1][1] - tri[0][1]) * (tri[2][0] - tri[0][0]) < 0:
                    tri = tri[::-1]
                pb.prism(tri, zp, zp + 0.06, 3, 3)
    # nodes: hex pucks with a glowing inset and a floating faceted icon
    for name, ((i, j), kind) in sorted(NODES.items()):
        x, y = lx(i), ly(j)
        big = name == HERE
        r = 1.35 if big else 1.1
        pb.prism(L.ngon(6, r, rot=math.pi / 6), 0.0, 0.3, 2, 3, cx=x, cy=y)
        pb.prism(L.ngon(6, r * 0.72, rot=math.pi / 6), 0.3, 0.38, kidx[kind], kidx[kind], cx=x, cy=y,
                 top_center_dz=0.08)
        hz = 3.0 if not big else 4.4
        if kind == "target":
            pb.prism(L.ngon(4, 0.62), hz - 0.75, hz, iidx[kind], iidx[kind], top_scale=1.0, cx=x, cy=y,
                     top_center_dz=0.7, bottom=True, mi_bot=iidx[kind])
        elif kind == "site":
            pb.prism(L.ngon(6, 0.58, rot=0.3), hz - 0.5, hz + 0.15, iidx[kind], iidx[kind], cx=x, cy=y,
                     top_center_dz=0.18, bottom=True)
        elif kind == "boss":
            pb.prism(L.ngon(3, 0.85, rot=0.5), hz - 0.4, hz + 0.15, iidx[kind], iidx[kind], cx=x, cy=y,
                     top_center_dz=0.9, bottom=True)
            pb.prism(L.ngon(3, 0.85, rot=0.5 + math.pi / 3), hz - 0.4, hz - 0.15, iidx[kind], iidx[kind],
                     cx=x, cy=y, top_center_dz=-1.3, bottom=False)
        # thin tether from puck to icon
        pb.prism(L.ngon(4, 0.05), 0.38, hz - 0.4, iidx[kind], iidx[kind], cx=x, cy=y)
        if big:
            # "you are here": a wide hex ring and a big downward pin
            for rr in ((2.0, 1.72),):
                outer = L.ngon(6, rr[0], rot=math.pi / 6)
                inner = L.ngon(6, rr[1], rot=math.pi / 6)
                for k in range(6):
                    a, b = k, (k + 1) % 6
                    q = [inner[a], outer[a], outer[b], inner[b]]
                    qq = [(x + u, y + v) for u, v in q]
                    ids_b = [pb.vert((u, v, 0.02)) for u, v in qq]
                    ids_t = [pb.vert((u, v, 0.14)) for u, v in qq]
                    pb.face([ids_t[0], ids_t[1], ids_t[2], ids_t[3]][::-1], kidx[kind])
                    pb.face([ids_b[1], ids_b[2], ids_t[2], ids_t[1]], kidx[kind])
            # inverted faceted pin
            pb.prism(L.ngon(6, 1.0, rot=0.2), hz, hz + 1.1, iidx[kind], iidx[kind], cx=x, cy=y,
                     top_center_dz=0.25, bottom=False)
            tip = pb.vert((x, y, hz - 1.8), 0.0)
            ring = L.ngon(6, 1.0, rot=0.2)
            bot = [pb.vert((x + u, y + v, hz), 0.0) for u, v in ring]
            for k in range(6):
                pb.face([bot[(k + 1) % 6], bot[k], tip], iidx[kind])
    return pb.build("overlay", mats, seed=5, coll=coll)


def node_world(name):
    (i, j), kind = NODES[name]
    return Vector((lx(i), ly(j), 0.0))


# ---- extras by mode ---------------------------------------------------------------------

def build_extras(mode, coll=None):
    """Cars, lamps, signage glows (night), searchlights/drones/heli (alert). Own rng stream."""
    rng = random.Random(9000)
    head = L.mat_flat("car_head", "#fff1d0", emit="#fff1d0", emit_str=6.0 if mode != "day" else 0.0)
    tail = L.mat_flat("car_tail", "#ff3050", emit="#ff3050", emit_str=6.0 if mode != "day" else 0.0)
    carcols = ["#c96f5a", "#6a8fa6", "#d8c9ae", "#8a7fa0", "#5f5a66"]
    cm = [L.mat_flat("car%d" % k, c) for k, c in enumerate(carcols)]
    lamp_head = L.mat_flat("lamp", "#ffd9a0", emit="#ffd9a0", emit_str=8.0 if mode != "day" else 0.0)
    mats = [head, tail, lamp_head, L.mat_flat("pole", "#3d3644")] + cm
    pb = L.PB()
    used = set()
    for path in PATHS:
        for (a, b) in zip(path[:-1], path[1:]):
            used.add((a, b)); used.add((b, a))
    # cars on lanes offset from the street centre
    for k in range(64):
        vertical = rng.random() < 0.5
        if vertical:
            i = rng.randrange(0, NX + 1)
            y = rng.uniform(ly(0), ly(NY))
            if ly(WATER_ROW) + S / 2 < y < ly(WATER_ROW + 1) - S / 2 and i not in BRIDGES:
                continue
            lane = rng.choice((-0.55, 0.55))
            x = lx(i) + lane
            ang = 0 if lane > 0 else math.pi
        else:
            j = rng.randrange(0, NY + 1)
            x = rng.uniform(lx(0), lx(NX))
            lane = rng.choice((-0.55, 0.55))
            y = ly(j) + lane
            ang = math.pi / 2 if lane < 0 else -math.pi / 2
        col = rng.randrange(len(cm))
        ca, sa = math.cos(ang), math.sin(ang)

        def rot(u, v):
            return (x + u * ca - v * sa, y + u * sa + v * ca)
        def lrot(u, v):
            return (u * ca - v * sa, u * sa + v * ca)
        body = [lrot(-0.24, -0.45), lrot(0.24, -0.45), lrot(0.24, 0.45), lrot(-0.24, 0.45)]
        # our local frame: +v forward
        pb.prism(body, 0.02, 0.26, 4 + col, 4 + col, top_scale=0.75, jit=0.02, cx=x, cy=y)
        f1, f2 = rot(-0.14, 0.41), rot(0.14, 0.41)
        pb.prism([rot(-0.2, 0.36), rot(0.2, 0.36), rot(0.2, 0.44), rot(-0.2, 0.44)], 0.08, 0.16, 0, 0)
        pb.prism([rot(-0.2, -0.44), rot(0.2, -0.44), rot(0.2, -0.36), rot(-0.2, -0.36)], 0.08, 0.16, 1, 1)
    # lamps on block corners
    for col in range(NX):
        for row in range(NY):
            if row == WATER_ROW or rng.random() < 0.4:
                continue
            cx = lx(col) + P / 2 + (B / 2 - 0.15) * rng.choice((-1, 1))
            cy = ly(row) + P / 2 - (B / 2 - 0.15)
            pb.prism(L.ngon(4, 0.04), 0.12, 0.9, 3, 3, cx=cx, cy=cy)
            pb.prism(L.ngon(4, 0.1, rot=0.78), 0.9, 1.0, 2, 2, cx=cx, cy=cy)
    ob = pb.build("extras", mats, seed=11, coll=coll)
    if mode == "alert":
        _alert(rng, coll)
    return ob


def _alert(rng, coll):
    beam_w = L.mat_beam("beam_w", "#ffe6d0", strength=1.6, a_near=0.16, a_far=0.0)
    beam_r = L.mat_beam("beam_r", "#ff3050", strength=2.2, a_near=0.18, a_far=0.0)
    body = L.mat_flat("drone_body", "#7a6a80")
    red = L.mat_flat("drone_red", "#ff2a44", emit="#ff2a44", emit_str=12.0)
    blue = L.mat_flat("drone_blue", "#3a7aff", emit="#3a7aff", emit_str=12.0)
    pool = L.mat_emit("pool", "#ffe8d0", strength=1.4, alpha=0.35)
    here = node_world(HERE)
    # searchlight beams: faceted cones from helicopters / drones down to ground pools
    sources = [
        (Vector((here.x + 8.0, here.y + 5.0, 11.0)), Vector((here.x + 0.6, here.y + 0.4, 0.05)), 2.2, beam_w),
        (Vector((lx(5) - 2.0, ly(3) - 3.0, 16.0)), Vector((lx(5), ly(1) + 1.0, 0.05)), 2.4, beam_w),
        (Vector((lx(7) + 1.0, ly(3) + 1.0, 12.0)), Vector((lx(6) + 0.5, ly(4) + 0.5, 0.05)), 2.2, beam_r),
        (Vector((lx(2) - 2.0, ly(5), 15.0)), Vector((lx(2), ly(3) + 1.5, 0.05)), 2.0, beam_w),
    ]
    for k, (src, dst, rad, m) in enumerate(sources):
        _cone(f"beam{k}", src, dst, rad, m, coll)
        # ground pool (flat faceted disc)
        pb = L.PB()
        pb.prism(L.ngon(9, rad * 1.05, rot=k), 0.0, 0.02, 0, 0, cx=dst.x, cy=dst.y)
        o = pb.build(f"pool{k}", [pool], seed=k, coll=coll, shadow=False)
        o.location.z = dst.z + 0.2
        L.point(f"poolL{k}", (dst.x, dst.y, 5.0), "#ffe6d0" if m is beam_w else "#ff3050", 900, radius=1.0)
        if k in (0, 2):
            _heli(f"heli{k}", src, body, red, blue, coll)
        else:
            _drone(f"sdrone{k}", src, body, red, blue, coll, scale=1.4)
    # small drone swarm around the player's node
    for k in range(7):
        a = k * 2 * math.pi / 7 + rng.uniform(-0.2, 0.2)
        r = rng.uniform(4.0, 8.0)
        pos = Vector((here.x + 2.0 + math.cos(a) * r, here.y + 2.0 + math.sin(a) * r, rng.uniform(3.0, 5.5)))
        _drone(f"drone{k}", pos, body, red if k % 2 == 0 else blue, red, coll, scale=1.8)
    # rooftop alarm beacons
    for k in range(10):
        x = rng.uniform(lx(0) + 2, lx(NX) - 2)
        y = rng.uniform(ly(3), ly(NY) - 1)
        L.point(f"alarm{k}", (x, y, 7.0), "#ff2040", 700, radius=0.5)


def _cone(name, src, dst, rad, mat, coll):
    d = dst - src
    L_ = d.length
    pb = L.PB()
    n = 7
    ring = L.ngon(n, rad)
    apex = pb.vert((0, 0, L_), 0.0)
    base = [pb.vert((x, y, 0), 0.0) for x, y in ring]
    for i in range(n):
        pb.face([base[i], base[(i + 1) % n], apex], 0)
    ob = pb.build(name, [mat], coll=coll, shadow=False, tri=False)
    ob.location = dst
    ob.rotation_euler = (-d).to_track_quat("Z", "Y").to_euler()
    return ob


def _drone(name, pos, body, l1, l2, coll, scale=1.0):
    pb = L.PB()
    s = scale
    pb.prism(L.ngon(4, 0.35 * s, rot=0.78), -0.1 * s, 0.1 * s, 0, 0, top_center_dz=0.12 * s, bottom=True)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        ax, ay = math.cos(a) * 0.55 * s, math.sin(a) * 0.55 * s
        pb.prism(L.ngon(6, 0.2 * s), 0.0, 0.05 * s, 0, 0, cx=ax, cy=ay)
    pb.prism(L.ngon(4, 0.1 * s), -0.2 * s, -0.08 * s, 1, 1, bottom=True)
    pb.prism(L.ngon(4, 0.06 * s), 0.1 * s, 0.2 * s, 2, 2, cx=0.2 * s)
    ob = pb.build(name, [body, l1, l2], coll=coll, shadow=True)
    ob.location = pos
    return ob


def _heli(name, pos, body, red, blue, coll):
    pb = L.PB()
    # faceted fuselage: an elongated octagon prism lying along x
    rng = random.Random(len(name))
    pb.prism(L.ngon(6, 0.9, sx=1.8, sy=0.8), -0.5, 0.5, 0, 0, top_scale=0.8, top_center_dz=0.25,
             bottom=True, jit=0.06)
    pb.prism([(-3.4, -0.12), (-1.2, -0.25), (-1.2, 0.25), (-3.4, 0.12)], -0.05, 0.2, 0, 0)
    pb.prism([(-3.6, -0.05), (-3.0, -0.05), (-3.0, 0.05), (-3.6, 0.05)], 0.1, 0.9, 0, 0)
    for k in range(2):
        a = k * math.pi / 2 + 0.3
        pts = [(math.cos(a) * 3.2 - math.sin(a) * 0.12, math.sin(a) * 3.2 + math.cos(a) * 0.12),
               (-math.cos(a) * 3.2 - math.sin(a) * 0.12, -math.sin(a) * 3.2 + math.cos(a) * 0.12),
               (-math.cos(a) * 3.2 + math.sin(a) * 0.12, -math.sin(a) * 3.2 - math.cos(a) * 0.12),
               (math.cos(a) * 3.2 + math.sin(a) * 0.12, math.sin(a) * 3.2 - math.cos(a) * 0.12)]
        pb.prism(pts, 0.7, 0.75, 0, 0)
    pb.prism(L.ngon(4, 0.15), -0.7, -0.5, 1, 1, cx=0.8, bottom=True)
    pb.prism(L.ngon(4, 0.1), 0.5, 0.65, 2, 2, cx=-0.4)
    pb.prism(L.ngon(4, 0.1), 0.2, 0.35, 1, 1, cx=-3.5)
    ob = pb.build(name, [body, red, blue], coll=coll, shadow=True)
    ob.location = pos
    ob.scale = (1.7, 1.7, 1.7)
    ob.rotation_euler = (0, math.radians(8), rng.uniform(0, 6.28))
    return ob
