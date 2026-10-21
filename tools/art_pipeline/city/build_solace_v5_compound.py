"""HQ v5: the Solace compound as glTF 2.0 (Blender 5.2 headless), from the approved v5 golden plates' scene.

  blender -b --factory-startup --python build_solace_v5_compound.py -- solace <outdir>
    -> <outdir>/solace_compound.glb + <outdir>/build_info.json (same contract as build_hq_compound.py)

The geometry is the art-pass plate scene's (docs/concepts/solace_vertical/hq/scripts @ v5, vendored in vendor_solace_v5/: hq_graph,
hq_preset, hqk_graph, look_preset, sd_kit, sd_lib): the lime double helix (two strands of one 360 degree turn, 27 floors, two
sideways-oval cutaway windows per floor and strand), the lit window frame rings, the bow-tie skybridges on the route floors, the
crown (pink halo + lime inner ring, the Genome Core), the 3-tier plinth with cardinal stairs and the park (lawn, paths, ponds,
trees) of the district kit. HYBRID interiors (NOTES, hq_rev v4): built floors (route floors and floors 5..13: slab, mezzanine,
ceiling disc, core, desks) as real geometry behind the cutaway; every other window one flat oval patch for the interior-mapping
shader (per-vertex frame data: normal = window normal, UV0 = (u, dz) in the window frame, UV1 = (variant, blind), COLOR = tint, lit).

Materials carry the role in their name (hq_sx_*); the vertex colour is the base colour; for the lit roles the alpha is the emission
gain. Normals and UVs ARE exported (PBR look; the other corporations' compounds are the toon pipeline).
Frame: Blender (x east, y north, z up); the plinth centre is the origin, the ground is z 0 (glTF: (x, z, -y)).
"""
import json
import math
import os
import random
import sys

import bpy
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
VEND = os.path.join(HERE, "vendor_solace_v5")
sys.path.insert(0, HERE)
sys.path.insert(0, VEND)
import hq_compound_spec as SPEC  # noqa: E402

_args = sys.argv[sys.argv.index("--") + 1:]
CORP_ARG, OUT_ARG = _args[0], os.path.abspath(_args[1])
os.makedirs(OUT_ARG, exist_ok=True)
os.environ.setdefault("HQ_RB0", "120")  # the immediate park ring (the plates' park is 195: out to ~290 BU)
import hq_graph as G  # noqa: E402
import sd_kit as SD  # noqa: E402

CP, LH = G.CP, __import__("hq_preset").PRESET["hq"]["light"]
PAL = __import__("hq_preset").PRESET["hq"]["palette"]
LEAF, PINK, CLIN, POR = PAL["leaf"], PAL["pink"], PAL["clinic"], PAL["porcelain"]
SKIN = LH["skin"]
R, FH, RT, TW, TD = CP["radius"], CP["floor_h"], CP["tube_r"], CP["tower_w"], CP["tower_d"]
TOPF = CP["floors"]
RFS = set(CP["route_floors"])
WIN = CP["win"]
WB, WAX = G.WB, G.WAX
A_LO, A_HI = CP["office"]["a_floors"]
NSEG, DZ, NO, JAMB = 56, 0.9, 64, 0.6
IM_NV = 6
FLOOR_COL = (0.22, 0.21, 0.195)

# ------------------------------------------------------------------ mesh accumulators (one per role)
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)


class Role:
    def __init__(self, name, smooth=False, uv=False):
        self.name, self.smooth, self.uv = name, smooth, uv
        self.V, self.C, self.N, self.U0, self.U1, self.F = [], [], [], [], [], []

    def v(self, p, c, u0=(0.0, 0.0), u1=(0.0, 0.0)):
        self.V.append((float(p[0]), float(p[1]), float(p[2])))
        self.C.append((float(c[0]), float(c[1]), float(c[2]), float(c[3]) if len(c) > 3 else 1.0))
        self.U0.append(u0)
        self.U1.append(u1)
        return len(self.V) - 1

    def f(self, *idx):
        self.F.append(tuple(idx))

    def quad(self, pts, c):
        """A flat polygon of world points with one colour."""
        self.f(*[self.v(p, c) for p in pts])

    def tri_count(self):
        return sum(len(f) - 2 for f in self.F)


ROLES = {}


def role(name, **kw):
    if name not in ROLES:
        ROLES[name] = Role(name, **kw)
    return ROLES[name]


def box(r, x0, y0, z0, x1, y1, z1, c, top=True, bottom=False):
    x0, x1, y0, y1, z0, z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
    r.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], c)
    r.quad([(x1, y1, z0), (x0, y1, z0), (x0, y1, z1), (x1, y1, z1)], c)
    r.quad([(x0, y1, z0), (x0, y0, z0), (x0, y0, z1), (x0, y1, z1)], c)
    r.quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], c)
    if top:
        r.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], c)
    if bottom:
        r.quad([(x0, y1, z0), (x1, y1, z0), (x1, y0, z0), (x0, y0, z0)], c)


def tube(r, p0, p1, rad, c, n=6):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    if d.length < 1e-4:
        return
    d.normalize()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    u = d.cross(up).normalized()
    w = d.cross(u).normalized()
    ring = [u * math.cos(2 * math.pi * i / n) * rad + w * math.sin(2 * math.pi * i / n) * rad for i in range(n)]
    for i in range(n):
        j = (i + 1) % n
        r.quad([a + ring[i], a + ring[j], b + ring[j], b + ring[i]], c)


def disc(r, cx, cy, z, rad, c, n=24, up=True):
    pts = [(cx + rad * math.cos(2 * math.pi * k / n), cy + rad * math.sin(2 * math.pi * k / n), z) for k in range(n)]
    r.quad(pts if up else pts[::-1], c)


def slab(r, cx, cy, z0, z1, rad, c, n=24):
    disc(r, cx, cy, z1, rad, c, n, True)
    disc(r, cx, cy, z0, rad, c, n, False)
    for k in range(n):
        a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        r.quad([(cx + rad * math.cos(a0), cy + rad * math.sin(a0), z0), (cx + rad * math.cos(a1), cy + rad * math.sin(a1), z0),
                (cx + rad * math.cos(a1), cy + rad * math.sin(a1), z1), (cx + rad * math.cos(a0), cy + rad * math.sin(a0), z1)], c)


def rf(rec, dn, du, z):
    n = rec["n"]
    t = (n[1], -n[0])
    o = rec["o"]
    return (o[0] + n[0] * dn + t[0] * du, o[1] + n[1] * dn + t[1] * du, z)


def obox(r, rec, u0, u1, dn0, dn1, z0, z1, c, top=True, bottom=False):
    cc = [[rf(rec, dn, u, z) for (u, dn) in ((u0, dn0), (u1, dn0), (u1, dn1), (u0, dn1))] for z in (z0, z1)]
    b, t_ = cc
    for i in range(4):
        j = (i + 1) % 4
        r.quad([b[i], b[j], t_[j], t_[i]], c)
    if top:
        r.quad(t_, c)
    if bottom:
        r.quad(list(reversed(b)), c)


def neon(c, k):
    return (c[0], c[1], c[2], k)


SKINR = role("skin", smooth=True)           # the strand skin (lime glossy body; back side = office wall)
PORC = role("porc")                          # jambs, deck undersides, crown porcelain
NEO = role("neon")                           # lit frame rings, rungs, rings, crown halo: colour + alpha = emission gain
FLR = role("office")                         # built floors: slabs, ceilings, core, desks (colour + alpha = emission gain)
GLS = role("glass")                          # glass patches, bridge walls, crown glass
MET = role("metal")                          # posts, rails, stair ribbon, core
WINR = role("win", uv=True)                  # interior-mapped window patches
STONE = role("stone")                        # plinth
GROUND = role("ground", smooth=True)         # lawn, paths
PLAIN = role("plain")                        # trees, trunks, lamp posts
WATER = role("water")                        # ponds

# ------------------------------------------------------------------ the strands (skin with cutaway windows)
WINS = [(t, f, side) for t in ("A", "B") for f in range(TOPF) for side in ("in", "out")]
FR = {k: G.win_frame(*k) for k in WINS}
ztop = G.floor_z(TOPF)
NODE_AT = {(G.TOWER[i], G.FLOOR[i]): i for i in G.NODES if i in G.TOWER}


def built_floor(f):
    return f in RFS or A_LO <= f <= A_HI


def skin(t):
    near = [k for k in WINS if k[0] == t]
    nz = int((ztop - G.PODIUM_H) / DZ) + 1
    verts = []
    for iz in range(nz):
        z = G.PODIUM_H + iz * DZ
        fl = [k for k in near if abs(z - FR[k]["zc"]) < WB + 1.5]
        for j in range(NSEG):
            p = G.tube_pt(t, z, 2 * math.pi * j / NSEG)
            for k in fl:
                fr = FR[k]
                u, dz, dep = G.win_local(fr, p)
                if dep <= 0:
                    continue
                rho = math.hypot(u / WAX, dz / WB)
                if abs(rho - 1.0) < 0.12:
                    u, dz = u / rho, dz / rho
                    p = G.win_pt(fr, u, dz, G.skin_depth(fr, u, dz))
                    break
            verts.append(p)
    faces = []
    for iz in range(nz - 1):
        z = G.PODIUM_H + (iz + 0.5) * DZ
        fl = [k for k in near if abs(z - FR[k]["zc"]) < WB + 1.5]
        for j in range(NSEG):
            a0, a1 = iz * NSEG + j, iz * NSEG + (j + 1) % NSEG
            q = (a0, a1, a1 + NSEG, a0 + NSEG)
            if fl:
                cpt = tuple(sum(verts[v][c] for v in q) / 4 for c in range(3))
                if any(G.win_local(FR[k], cpt)[2] > 0 and math.hypot(G.win_local(FR[k], cpt)[0] / WAX, G.win_local(FR[k], cpt)[1] / WB) < 1.0
                       for k in fl):
                    continue
            faces.append(q)
    q0 = faces[0]
    v0, v1, v3 = Vector(verts[q0[0]]), Vector(verts[q0[1]]), Vector(verts[q0[3]])
    nrm = (v1 - v0).cross(v3 - v0)
    cax = G.tube_pt(t, verts[q0[0]][2], 0.0, 0.0)
    if nrm.x * (v0.x - cax[0]) + nrm.y * (v0.y - cax[1]) < 0:
        faces = [tuple(reversed(f_)) for f_ in faces]
    base = len(SKINR.V)
    for p in verts:
        SKINR.v(p, SKIN)
    for q in faces:
        SKINR.f(*[base + i for i in q])


def ring_ribbon(fr, f, lift, w, col):
    """The lit frame ring: a flat ribbon of width 2 w round the skin-edge oval (offsets along the oval's own normal)."""
    pts_in, pts_out = [], []
    for k in range(NO):
        u, dz = G.win_uv(k, NO)
        nx, nz_ = u / WAX ** 2, dz / WB ** 2
        L_ = math.hypot(nx, nz_) or 1.0
        nx, nz_ = nx / L_, nz_ / L_
        for sgn, dst in ((-1, pts_in), (1, pts_out)):
            uu, zz = u + nx * w * sgn, dz + nz_ * w * sgn
            dst.append(G.win_pt(fr, uu, zz, G.skin_depth(fr, uu, zz) + 0.06))
    for k in range(NO):
        k1 = (k + 1) % NO
        NEO.f(NEO.v(pts_in[k], col), NEO.v(pts_in[k1], col), NEO.v(pts_out[k1], col), NEO.v(pts_out[k], col))


def office_floor(t, f, rng):
    """One built floor behind the cutaway: slab, mezzanine, ceiling disc, core, desks (two storeys, as the plates' kit)."""
    zl = G.deck_z(f)
    CH = 4.0
    zu = zl + CH + 0.4
    for (z0, z1, cap) in ((zl - 0.4, zl, False), (zl + CH, zu, False)):
        c, _rv, _n = G.tower_frame(t, (z1 - G.PODIUM_H) / FH)
        slab(FLR, c[0], c[1], z0, z1, RT - 0.3, neon(FLOOR_COL, 0.20))
    c, _rv, _n = G.tower_frame(t, (zu + CH - G.PODIUM_H) / FH)
    disc(FLR, c[0], c[1], zu + CH, RT - 0.3, neon((0.55, 0.52, 0.46), 0.6), 24, False)       # the dropped lit ceiling
    for zs in (zl, zu):
        c, rv, n = G.tower_frame(t, (zs - G.PODIUM_H) / FH)
        tube(FLR, (c[0], c[1], zs), (c[0], c[1], zs + CH), 2.6, neon((0.12, 0.13, 0.14), 0.0), 10)   # the core
        for k in range(9):
            a = rng.uniform(0, 2 * math.pi)
            d = rng.uniform(4.5, RT - 1.8)
            x, y = c[0] + d * math.cos(a), c[1] + d * math.sin(a)
            hx, hy = rng.uniform(0.7, 1.3), rng.uniform(0.4, 0.7)
            box(FLR, x - hx, y - hy, zs, x + hx, y + hy, zs + 0.8, neon((0.09, 0.1, 0.11), 0.0))
            if rng.random() < 0.6:
                box(FLR, x - 0.3, y - 0.05, zs + 0.8, x + 0.3, y + 0.05, zs + 1.4, neon((0.5, 0.8, 1.0), 1.4))   # a lit monitor
        for k in range(3):
            a = rng.uniform(0, 2 * math.pi)
            d = rng.uniform(5.0, RT - 1.6)
            x, y = c[0] + d * math.cos(a), c[1] + d * math.sin(a)
            box(FLR, x - 0.4, y - 0.4, zs, x + 0.4, y + 0.4, zs + 1.5, neon((0.05, 0.28, 0.08), 0.0))      # a plant


def windows_and_floors(t):
    for f in range(TOPF):
        node_i = NODE_AT.get((t, f))
        orng = random.Random(6400 + 100 * f + (0 if t == "A" else 1))
        if built_floor(f):
            office_floor(t, f, orng)
        for side in ("in", "out"):
            fr = FR[(t, f, side)]
            node = node_i if side == "in" else None
            sk = G.win_skin_outline(fr, NO)
            for k in range(NO):                                    # the jamb: the wall's thickness round the opening
                k1 = (k + 1) % NO
                ins = []
                for kk in (k, k1):
                    c_ = G.tube_pt(t, sk[kk][2], 0.0, 0.0)
                    dx, dy = c_[0] - sk[kk][0], c_[1] - sk[kk][1]
                    L_ = math.hypot(dx, dy)
                    ins.append((sk[kk][0] + dx / L_ * JAMB, sk[kk][1] + dy / L_ * JAMB, sk[kk][2]))
                PORC.quad([sk[k], sk[k1], ins[1], ins[0]], (0.30, 0.32, 0.32))
            fc = LEAF if (node or f % 2 == 0) else (0.62, 1.0, 0.7)
            ring_ribbon(fr, f, 0.06, WIN["frame_r"] * 1.15, neon(fc, LH["frame_k"]))
            if node and built_floor(f):
                continue                                             # an open node window: the room, the bridge deck runs in
            if built_floor(f):                                       # glass patch, 0.2 inside the skin
                for a in range(0, 48, 3):
                    a0, a1 = 2 * math.pi * a / 48, 2 * math.pi * (a + 3) / 48
                    quad = []
                    for (rho_, an) in ((0.0, a0), (1.0, a0), (1.0, a1)):
                        u_, dz_ = rho_ * WAX * math.cos(an), rho_ * WB * math.sin(an)
                        quad.append(G.win_pt(fr, u_, dz_, G.skin_depth(fr, u_, dz_) - 0.2))
                    GLS.quad(quad, (0.8, 0.9, 0.85, 1.0))
                continue
            lit_ = 1.0 if orng.random() < 0.84 else 0.0                # interior-mapped patch (one flat oval, plane depth dp)
            blind_ = orng.uniform(0.3, 0.95) if orng.random() < 0.22 else 0.0
            tnt = (orng.uniform(0.85, 1.0), orng.uniform(0.85, 1.0), orng.uniform(0.8, 1.0), lit_)
            var_ = float(orng.randrange(IM_NV))
            NS = 40
            nw3 = Vector((fr["nw"][0], fr["nw"][1], 0.0))
            ring = []
            for a in range(NS):
                an = 2 * math.pi * a / NS
                u_, dz_ = WAX * math.cos(an), WB * math.sin(an)
                ring.append((G.win_pt(fr, u_, dz_, fr["dp"]), (u_, dz_)))
            idx = [WINR.v(p, tnt, uv, (var_, blind_)) for (p, uv) in ring]
            ctr = WINR.v(G.win_pt(fr, 0.0, 0.0, fr["dp"]), tnt, (0.0, 0.0), (var_, blind_))
            for a in range(NS):                                        # outward-facing winding (+nw)
                WINR.f(ctr, idx[(a + 1) % NS], idx[a])


def mint_seam_and_rings(t):
    prev = None
    z = G.PODIUM_H
    while z <= ztop:
        p = G.tube_pt(t, z, G.stair_phi(t) + math.pi, RT + 0.1)
        if prev is not None:
            tube(NEO, prev, p, 0.45, neon((0.55, 1.0, 0.72), LH["atrium_k"]), 4)
        prev = p
        z += 2.0
    for f in range(TOPF):
        zd = G.floor_z(f) + 0.3
        col = neon(LEAF if f % 2 == 0 else PINK, LH["ring_k"])
        for q in range(NSEG):
            p0 = G.tube_pt(t, zd, 2 * math.pi * q / NSEG, RT + 0.08)
            p1 = G.tube_pt(t, zd, 2 * math.pi * (q + 1) / NSEG, RT + 0.08)
            NEO.quad([p0, p1, (p1[0], p1[1], p1[2] + 0.25), (p0[0], p0[1], p0[2] + 0.25)], col)


# ------------------------------------------------------------------ skybridges (route floors)
def bridges():
    wide, waist = CP["bridge_w"]
    for f in sorted(RFS):
        zb = G.deck_z(f)
        O_, e_, q_, half = G.bridge_frame(f)
        s_wall, s_deck = half + 0.6, half + 1.6
        rung = LEAF if (f // 3) % 2 == 0 else PINK

        def hw(s):
            return waist / 2 + (wide - waist) / 2 * (min(abs(s), half) / half) ** 1.6

        def P(s, side, z):
            return (O_[0] + e_[0] * s + q_[0] * side * hw(s), O_[1] + e_[1] * s + q_[1] * side * hw(s), z)
        NS = 16
        for k in range(NS):
            s0 = -s_deck + 2 * s_deck * k / NS
            s1 = -s_deck + 2 * s_deck * (k + 1) / NS
            FLR.quad([P(s0, -1, zb - 0.01), P(s1, -1, zb - 0.01), P(s1, 1, zb - 0.01), P(s0, 1, zb - 0.01)][::-1], neon(FLOOR_COL, 0.20))
            PORC.quad([P(s0, 1, zb - 0.8), P(s1, 1, zb - 0.8), P(s1, -1, zb - 0.8), P(s0, -1, zb - 0.8)], POR)
            for side in (-1, 1):
                PORC.quad([P(s0, side, zb - 0.8), P(s1, side, zb - 0.8), P(s1, side, zb - 0.01), P(s0, side, zb - 0.01)], POR)
            NEO.quad([P(s0, -0.12, zb + 0.02), P(s1, -0.12, zb + 0.02), P(s1, 0.12, zb + 0.02), P(s0, 0.12, zb + 0.02)],
                     neon(CLIN, LH["bridge_route_k"] * 0.25))
            for side in (-1, 1):                                     # v5: the rungs = the deck's lit edges
                NEO.quad([P(s0, side * 0.80, zb + 0.03), P(s1, side * 0.80, zb + 0.03), P(s1, side * 0.97, zb + 0.03),
                          P(s0, side * 0.97, zb + 0.03)], neon(rung, LH["rung_k"]))
        NW = 14
        for k in range(NW):
            s0 = -s_wall + 2 * s_wall * k / NW
            s1 = -s_wall + 2 * s_wall * (k + 1) / NW
            for side in (-1, 1):
                GLS.quad([P(s0, side, zb + 0.3), P(s1, side, zb + 0.3), P(s1, side, zb + 3.5), P(s0, side, zb + 3.5)], (0.8, 0.95, 0.9, 1.0))
                NEO.quad([P(s0, side, zb + 0.3), P(s1, side, zb + 0.3), P(s1, side, zb + 0.55), P(s0, side, zb + 0.55)],
                         neon(rung, LH["bridge_wall_k"] * 8.0))
            PORC.quad([P(s0, -1, zb + 3.5), P(s1, -1, zb + 3.5), P(s1, 1, zb + 3.7), P(s0, 1, zb + 3.7)], POR)
            FLR.quad([P(s0, 0.45, zb + 3.47), P(s1, 0.45, zb + 3.47), P(s1, -0.45, zb + 3.47), P(s0, -0.45, zb + 3.47)],
                     (1.0, 0.8, 0.58, 1.1))
        for k in range(0, NW + 1, 2):
            s_ = -s_wall + 2 * s_wall * k / NW
            for side in (-1, 1):
                tube(MET, P(s_, side * 0.93, zb), P(s_, side * 0.93, zb + 1.15), 0.07, (0.55, 0.58, 0.6, 1.0), 4)
        for side in (-1, 1):
            for k in range(NW):
                s0 = -s_wall + 2 * s_wall * k / NW
                s1 = -s_wall + 2 * s_wall * (k + 1) / NW
                tube(MET, P(s0, side * 0.93, zb + 1.15), P(s1, side * 0.93, zb + 1.15), 0.09, (0.62, 0.65, 0.67, 1.0), 4)


def stair_ribbon():
    for (a, b_) in G.PATH:
        et = G.edge_type(a, b_)
        if et == "bridge":
            continue
        pth = [p for p in G.edge_path(a, b_) if p[2] > G.PODIUM_H + 0.2]
        if et == "stair":
            pth = pth[1:-1]
        elif et == "ramp":
            pth = pth[:-1]
        else:
            pth = pth[1:]
        for p, q in zip(pth, pth[1:]):
            p, q = Vector(p) + Vector((0, 0, -1.55)), Vector(q) + Vector((0, 0, -1.55))
            d = q - p
            if d.length < 1e-4:
                continue
            side = Vector((-d.y, d.x, 0.0))
            side = side.normalized() * 0.9 if side.length > 1e-6 else Vector((0.9, 0, 0))
            dz = Vector((0, 0, -0.25))
            a_ = [p - side, q - side, q + side, p + side]
            b2 = [v + dz for v in a_]
            MET.quad(a_, (0.42, 0.45, 0.45, 1.0))
            MET.quad(list(reversed(b2)), (0.42, 0.45, 0.45, 1.0))
            for i in range(4):
                j = (i + 1) % 4
                MET.quad([b2[i], b2[j], a_[j], a_[i]], (0.42, 0.45, 0.45, 1.0))


def crown():
    c, rv, n = G.tower_frame("A", TOPF)
    zc = G.floor_z(TOPF)
    ch = CP["crown_h"]
    crown_f = dict(o=(n[0] * TW / 2, n[1] * TW / 2, 0.0), n=n)
    pc = (POR[0], POR[1], POR[2], 1.0)
    for (s0, s1) in ((-R - TD / 2, -11.0), (11.0, R + TD / 2)):
        obox(PORC, crown_f, s0, s1, -TW, 0.0, zc, zc + 1.5, POR)
        obox(GLS, crown_f, s0, s1, -TW, 0.0, zc + 1.5, zc + ch, (0.015, 0.04, 0.03, 1.0))
        obox(PORC, crown_f, s0, s1, -TW, 0.0, zc + ch, zc + ch + 1.5, POR)
    obox(PORC, crown_f, -11.0, 11.0, -TW, 0.0, zc, zc + 1.5, POR)
    obox(PORC, crown_f, -11.0, 11.0, -TW, 0.0, zc + ch, zc + ch + 1.5, POR)
    tube(MET, (0, 0, zc + 1.5), (0, 0, zc + ch), 3.4, (0.08, 0.08, 0.1, 1.0), 16)
    for k_ in range(8):
        zz = zc + 2.5 + k_ * 1.4
        tube(NEO, (0, 0, zz), (0, 0, zz + 0.3), 3.5, neon((1.0, 0.22, 0.08), 6.0), 24)
    RPK, RLM = R + RT * 1.07, R * 0.84 + RT * 0.5
    zr = zc + ch + 10.0
    for k in range(96):
        a0, a1 = 2 * math.pi * k / 96, 2 * math.pi * (k + 1) / 96
        tube(NEO, (math.sin(a0) * RPK, math.cos(a0) * RPK, zr), (math.sin(a1) * RPK, math.cos(a1) * RPK, zr), 1.25, neon(PINK, LH["crown_k"]), 6)
        tube(NEO, (math.sin(a0) * RLM, math.cos(a0) * RLM, zr), (math.sin(a1) * RLM, math.cos(a1) * RLM, zr), 0.6, neon(LEAF, LH["crown_k"] * 0.5), 5)


# ------------------------------------------------------------------ the park setting (the district kit, vendored)
def park():
    SD.park_world()
    sc_of = {"plinth": SD.SPL, "lawn": SD.SL}
    tgt = {"ground": GROUND, "neon": NEO, "plain": PLAIN, "water": WATER, "stone": STONE}
    stats = {}
    for (scope, key, smooth), b in sorted(SD.BUILD.items(), key=lambda kv: (kv[0][0], kv[0][1], kv[0][2])):
        r = tgt[key]
        s = sc_of[scope]
        base = len(r.V)
        for p, c, prm in zip(b.V, b.C, b.P):
            col = (c[0], c[1], c[2], (prm[0] if key == "neon" else 1.0))
            r.v((p[0] * s, p[1] * s, p[2] * s), col)
        for fc in b.F:
            r.f(*[base + i for i in fc])
        stats["%s_%s" % (scope, key)] = len(b.F)
    return stats


def clinic_gate():
    sx_, sy_ = CP["start"]
    box(PORC, sx_ - 5, sy_ - 3, 0, sx_ + 5, sy_ + 3, 4.6, POR)
    box(NEO, sx_ - 0.4, sy_ - 3.1, 6.0, sx_ + 0.4, sy_ - 3.0, 8.4, neon(LEAF, 4.0))
    box(NEO, sx_ - 1.2, sy_ - 3.1, 6.8, sx_ + 1.2, sy_ - 3.0, 7.6, neon(LEAF, 4.0))


for t in ("A", "B"):
    skin(t)
    windows_and_floors(t)
    mint_seam_and_rings(t)
bridges()
stair_ribbon()
crown()
clinic_gate()
pstats = park()


# ------------------------------------------------------------------ objects, materials
def role_mat(name):
    m = bpy.data.materials.new("hq_sx_" + name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bs = nt.nodes.new("ShaderNodeBsdfPrincipled")
    ca = nt.nodes.new("ShaderNodeVertexColor")
    ca.layer_name = "Col"
    nt.links.new(ca.outputs["Color"], bs.inputs["Base Color"])
    nt.links.new(bs.outputs[0], out.inputs[0])
    m["hq_role"] = "sx_" + name
    return m


objs = []
for name, r in ROLES.items():
    if not r.F:
        continue
    me = bpy.data.meshes.new("hq_solace_" + name)
    me.from_pydata(r.V, [], r.F)
    me.validate()
    n_loops = len(me.loops)
    cols = np.array(r.C, np.float32)
    vi = np.zeros(n_loops, np.int32)
    me.loops.foreach_get("vertex_index", vi)
    ca = me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    ca.data.foreach_set("color", cols[vi].ravel())
    me.color_attributes.active_color = ca
    me.color_attributes.render_color_index = 0
    if r.uv:
        for nm, arr in (("UV0", r.U0), ("UV1", r.U1)):
            uvl = me.uv_layers.new(name=nm)
            u = np.array(arr, np.float32)[vi]
            uvl.data.foreach_set("uv", u.ravel())
    me.polygons.foreach_set("use_smooth", [bool(r.smooth)] * len(me.polygons))
    me.update()
    ob = bpy.data.objects.new("hq_solace_" + name, me)
    scene.collection.objects.link(ob)
    me.materials.append(role_mat(name))
    objs.append(ob)
bpy.context.view_layer.update()

# ------------------------------------------------------------------ anchors: every slot must sit on a surface
L = SPEC.layout(CORP_ARG)
dg = bpy.context.evaluated_depsgraph_get()


def surface(p):
    hit, loc, _n, _i, _o, _m = scene.ray_cast(dg, Vector((p[0], p[1], p[2] + 3.0)), Vector((0, 0, -1)), distance=60.0)
    return round(loc.z, 3) if hit else None


LIFT = 0.3


def snap(p):
    s = surface(p)
    return None if s is None else [round(p[0], 3), round(p[1], 3), round(s + LIFT, 3)]


checks, anchors = [], []
for li, row in enumerate(L["rows"]):
    out_row = []
    for si, p in enumerate(row):
        a = snap(p)
        checks.append(dict(layer=li + 1, slot=si, z=p[2], surface=None if a is None else round(a[2] - LIFT, 3)))
        out_row.append(a)
    anchors.append(out_row)
srv_anchor = snap(L["server"])
entry_anchor = [round(c, 3) for c in L["entry"]]
srv_surface = None if srv_anchor is None else round(srv_anchor[2] - LIFT, 3)

# ------------------------------------------------------------------ bounds, triangles, export
mins, maxs = [1e9] * 3, [-1e9] * 3
tris = {}
for o in bpy.data.objects:
    me = o.data
    me.calc_loop_triangles()
    tris[o.data.materials[0]["hq_role"]] = len(me.loop_triangles)
    for v in me.vertices:
        for k in range(3):
            mins[k] = min(mins[k], v.co[k])
            maxs[k] = max(maxs[k], v.co[k])
glb = os.path.join(OUT_ARG, "%s_compound.glb" % CORP_ARG)
bpy.ops.export_scene.gltf(filepath=glb, export_format="GLB", export_yup=True, use_selection=False, export_apply=True,
                          export_texcoords=True, export_normals=True, export_vertex_color="ACTIVE",
                          export_all_vertex_colors=False, export_materials="EXPORT", export_extras=True,
                          export_cameras=False, export_lights=False, export_animations=False)
info = dict(corp=CORP_ARG, glb=os.path.basename(glb),
            bounds_blender=dict(min=[round(x, 3) for x in mins], max=[round(x, 3) for x in maxs]),
            triangles=tris, slot_surfaces=checks, server_surface=srv_surface, state="static", park=pstats,
            anchors_blender=dict(rows=anchors, server=srv_anchor, entry=entry_anchor, lift=LIFT), blender=bpy.app.version_string)
json.dump(info, open(os.path.join(OUT_ARG, "build_info.json"), "w"), indent=1)
print("DONE", CORP_ARG, json.dumps(tris), flush=True)
