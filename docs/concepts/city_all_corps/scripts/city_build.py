"""City-all-corps: the ONE city with all seven corp districts (Blender 5.2 headless).

blender -b --factory-startup --python city_build.py -- <mode> <cam> <outdir> [res_scale] [spp]
  mode  aaa   Cycles, the AAA-2 look (HIP GPU): Combined (with media) + Emission + Depth -> npy; anchors json
        main  Eevee, the MAINLINE City Grid look (toon ramp + window emission) + normal / id / depth passes for the ink
  cam   a key of city_preset.CAMS (hero, close)

Geometry is built from zoned.json (zoning.py) by rule:
  * every layout building, extruded as the kit does (footprint quad, base, height x KH, taper), then dressed by its
    district's building language (city_preset.DISTRICTS[..]["lang"]; generators below), seeded by the building key;
  * windows are a procedural facade shader (UV = metres along the facade, height), lit share / colour by district;
  * the seven landmarks at their HQ lots (landmarks below), the Aurelian aqueduct on its rule line;
  * Tethys: the sea past the coast, the seawall with pump towers, the drowned quarter (subsided ground, sea level water,
    levee), the Atlantis station in its trench; the clear-water recipe is a material rule (water_fade);
  * the city ring past the map edge (hq_kit.city_ring rules: one seeded tower per grid cell, 12 % empty);
  * arterial light-streaks, the fog field, beams (r3 rule + one hero beam per landmark), district city-glow.
"""
import json
import math
import os
import random
import sys
import time

import bpy
import bmesh
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import city_preset as CP  # noqa: E402
import city_rules as RU  # noqa: E402

T0 = time.time()
_argv = sys.argv[sys.argv.index("--") + 1:]
MODE, CAMK, OUTDIR = _argv[0], _argv[1], _argv[2]
CYC = MODE in ("aaa", "day")          # Cycles looks: aaa = the AAA-2 night, day = the round-3 daytime look
DAYM = MODE == "day"
RES_K = float(_argv[3]) if len(_argv) > 3 else 1.0
SPP = int(_argv[4]) if len(_argv) > 4 else 64
os.makedirs(OUTDIR, exist_ok=True)
O = json.load(open(CP.ZONED))
U, KH = CP.U, CP.KH
CX, CY = O["centre"]
WAT = CP.WATER
ZW = WAT["z"]
DIST = CP.DISTRICTS
R2 = math.sqrt(2)


def W(p):
    return ((p[0] - CX) * U, -(p[1] - CY) * U)


def ab_w(x, y):
    """world -> (a, b) in lots."""
    lx, ly = x / U + CX, -y / U + CY
    dx, dy = lx - CX, ly - CY
    return (dx - dy) / R2, -(dx + dy) / R2


def w_ab(a, b):
    lx, ly = CX + (a - b) / R2, CY + (-a - b) / R2
    return W((lx, ly))


B_COAST = O["b_coast"]
BAYP = O["bay"]


def bwall(a):
    """the seawall line (zoning Z6): b in lots at screen-across position a (the bay bows out round the drowned quarter)."""
    v = B_COAST + BAYP["depth"] * math.exp(-((a - BAYP["ac"]) / BAYP["width"]) ** 2)
    if abs(a - BAYP["ac"]) > BAYP["head_start"]:
        v += BAYP["head_k"] * (abs(a - BAYP["ac"]) - BAYP["head_start"]) ** 2
    return v


# the coast in world: the line b = B_COAST; its seaward normal (world) and along direction
_p0, _p1 = Vector((*w_ab(0, B_COAST), 0)), Vector((*w_ab(0, B_COAST + 1), 0))
SEA_N = (_p1 - _p0).normalized()
COAST_T = Vector((*w_ab(1, B_COAST), 0)) - _p0
COAST_T.normalize()


# ------------------------------------------------------------------ geometry accumulator
class Acc:
    """Per-face attributes: col (albedo or emission colour), wc (window colour), wl (lit share), wm (window mode:
    0 grid, 1 ribbon, 2 porthole, 3 none, 4 arch), bid (0..1 per building), wet (in the water)."""

    def __init__(self, name, smooth=False):
        self.name, self.smooth = name, smooth
        self.V, self.F, self.UV = [], [], []
        self.col, self.wc, self.wl, self.wm, self.bid, self.wet = [], [], [], [], [], []

    def face(self, pts, col, uv=None, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0):
        # horizontal faces always face up (the lot -> world map flips y, so layout winding comes in either way; a
        # down-facing water plane would make its Fresnel total-internal-reflect past 49 degrees)
        if len(pts) >= 3 and max(p[2] for p in pts) - min(p[2] for p in pts) < 1e-6:
            ar = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
            if ar < 0:
                pts = list(reversed(pts))
                if uv is not None:
                    uv = list(reversed(uv))
        n0 = len(self.V)
        self.V.extend(pts)
        self.F.append(tuple(range(n0, n0 + len(pts))))
        self.UV.extend(uv if uv is not None else [(0.0, 0.0)] * len(pts))
        self.col.append(col)
        self.wc.append(wc)
        self.wl.append(wl)
        self.wm.append(wm)
        self.bid.append(bid)
        self.wet.append(wet)

    def obj(self, mat):
        me = bpy.data.meshes.new(self.name)
        me.from_pydata(self.V, [], self.F)
        nf = len(self.F)
        for nm, data in (("col", self.col), ("wc", self.wc)):
            a = me.attributes.new(nm, "FLOAT_COLOR", "FACE")
            flat = []
            for c in data:
                flat.extend((c[0], c[1], c[2], 1.0))
            a.data.foreach_set("color", flat)
        for nm, data in (("wl", self.wl), ("wm", self.wm), ("bid", self.bid), ("wet", self.wet)):
            a = me.attributes.new(nm, "FLOAT", "FACE")
            a.data.foreach_set("value", [float(v) for v in data])
        uvl = me.uv_layers.new(name="UVMap")
        flat = []
        for f in self.F:
            for vi in f:
                flat.extend(self.UV[vi])
        uvl.data.foreach_set("uv", flat)
        if self.smooth:
            bm = bmesh.new()
            bm.from_mesh(me)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.002)
            bm.to_mesh(me)
            bm.free()
            for p in me.polygons:
                p.use_smooth = True
        me.materials.append(mat)
        ob = bpy.data.objects.new(self.name, me)
        bpy.context.scene.collection.objects.link(ob)
        print("MESH %s faces %d" % (self.name, nf), flush=True)
        return ob


SURF = Acc("surf")          # opaque architecture (facade shader with windows)
SMOOTH = Acc("smooth", smooth=True)   # tubes, domes, drums (same shader, smooth shaded)
NEON = Acc("neon")          # emitters (col = emission colour, relative)
GLASS = Acc("glass", smooth=True)
GROUND = Acc("ground")
SEABED = Acc("seabed")
WATER = Acc("water")
STREAK = Acc("streak")      # traffic light-streaks (their own emitter strength)
BILL = Acc("bill")          # the larger billboards (blade signs, rooftop holo panels): their own day strength (AD r3)


# ------------------------------------------------------------------ primitives
def quad_uv(p0, p1, z0, z1, u0=0.0, sx=1.0, sy=1.0):
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    return [(u0 * sx, z0 * sy), ((u0 + L) * sx, z0 * sy), ((u0 + L) * sx, z1 * sy), (u0 * sx, z1 * sy)], L


def prism(acc, pts, z0, z1, col, ts=1.0, top=True, bottom=False, wc=(0, 0, 0), wl=0.0, wm=3, bid=0.0, wet=0, top_col=None,
          uvs=(1.0, 1.0), vz0=None):
    """Vertical prism on a polygon (world xy), taper ts at the top (kit rule), UV = metres along the facade, height."""
    n = len(pts)
    cx, cy = sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n
    tp = [(cx + (x - cx) * ts, cy + (y - cy) * ts) for (x, y) in pts]
    u = 0.0
    vb = z0 if vz0 is None else vz0
    for i in range(n):
        j = (i + 1) % n
        a, c = pts[i], pts[j]
        uv, L = quad_uv(a, c, vb, vb + (z1 - z0), u, *uvs)
        acc.face([(a[0], a[1], z0), (c[0], c[1], z0), (tp[j][0], tp[j][1], z1), (tp[i][0], tp[i][1], z1)], col, uv,
                 wc, wl, wm if L > 0.9 else 3, bid, wet)
        u += L
    if top:
        acc.face([(x, y, z1) for (x, y) in tp], top_col or col, None, wc, 0, 3, bid, wet)
    if bottom:
        acc.face([(x, y, z0) for (x, y) in reversed(pts)], col, None, wc, 0, 3, bid, wet)
    return tp


def box(acc, x0, y0, z0, x1, y1, z1, col, **kw):
    return prism(acc, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], z0, z1, col, **kw)


def circle(cx, cy, r, n, a0=0.0, ry=None):
    ry = r if ry is None else ry
    return [(cx + r * math.cos(a0 + 2 * math.pi * k / n), cy + ry * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


def cyl(acc, cx, cy, z0, z1, r, n, col, ts=1.0, **kw):
    return prism(acc, circle(cx, cy, r, n), z0, z1, col, ts=ts, **kw)


def dome(acc, cx, cy, z, r, col, n=16, rings=6, hemi=True, wet=0, bid=0.0, zscale=1.0, emit=None):
    lo = 0 if hemi else -rings
    for k in range(lo, rings):
        a0, a1 = math.pi / 2 * k / rings, math.pi / 2 * (k + 1) / rings
        r0, r1 = r * math.cos(a0), r * math.cos(a1)
        z0, z1 = z + r * math.sin(a0) * zscale, z + r * math.sin(a1) * zscale
        for i in range(n):
            t0, t1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            pts = [(cx + r0 * math.cos(t0), cy + r0 * math.sin(t0), z0), (cx + r0 * math.cos(t1), cy + r0 * math.sin(t1), z0),
                   (cx + r1 * math.cos(t1), cy + r1 * math.sin(t1), z1), (cx + r1 * math.cos(t0), cy + r1 * math.sin(t0), z1)]
            if r1 < 1e-4:
                pts = pts[:3]
            acc.face(pts, col, None, (0, 0, 0), 0, 3, bid, wet)


def bar(acc, p0, p1, w, col, **kw):
    """A square beam between two 3D points (width w)."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    if d.length < 1e-6:
        return
    d.normalize()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    s = d.cross(up).normalized() * (w / 2)
    t = d.cross(s).normalized() * (w / 2)
    cs = [s + t, -s + t, -s - t, s - t]
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(p0 + cs[i]), tuple(p0 + cs[j]), tuple(p1 + cs[j]), tuple(p1 + cs[i])], col, None, **kw)


def strip(acc, p0, p1, w, z, col, **kw):
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy / L * w / 2, dx / L * w / 2
    acc.face([(p0[0] - nx, p0[1] - ny, z), (p1[0] - nx, p1[1] - ny, z), (p1[0] + nx, p1[1] + ny, z), (p0[0] + nx, p0[1] + ny, z)],
             col, None, **kw)


def ring_line(acc, cx, cy, z, r, w, col, n=48, ry=None, **kw):
    ry = r if ry is None else ry
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        a = (cx + r * math.cos(t0), cy + ry * math.sin(t0), z)
        b = (cx + r * math.cos(t1), cy + ry * math.sin(t1), z)
        bar(acc, a, b, w, col, **kw)


def annulus(acc, cx, cy, z, r0, r1, col, n=48, k0=1.0, k1=1.0, z1=None, **kw):
    """flat (or sloped, z1) elliptic annulus; k0/k1 = ry/rx for the inner / outer ellipse."""
    z1 = z if z1 is None else z1
    for k in range(n):
        t0, t1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
        acc.face([(cx + r0 * math.cos(t0), cy + r0 * k0 * math.sin(t0), z1), (cx + r0 * math.cos(t1), cy + r0 * k0 * math.sin(t1), z1),
                  (cx + r1 * math.cos(t1), cy + r1 * k1 * math.sin(t1), z), (cx + r1 * math.cos(t0), cy + r1 * k1 * math.sin(t0), z)],
                 col, None, **kw)


def mixc(a, b, k):
    return tuple(a[i] * (1 - k) + b[i] * k for i in range(3))


def sc(c, k):
    return tuple(v * k for v in c)


CAMDIR = Vector((0.7071, -0.7071, 0.0))      # from the scene toward the camera (yaw 135)


# ------------------------------------------------------------------ the city buildings by district language
RS = random.Random(CP.SEEDS["build"])
ROOFS = []           # (x, y, top z, key, district, wet) for the beam rule
LIGHT_SPOTS = []


def seen(a, c, cxq, cyq):
    L = math.hypot(c[0] - a[0], c[1] - a[1]) or 1
    nx, ny = (c[1] - a[1]) / L, -(c[0] - a[0]) / L
    if nx * (a[0] - cxq) + ny * (a[1] - cyq) < 0:
        nx, ny = -nx, -ny
    return nx * CAMDIR.x + ny * CAMDIR.y > 0.05, (nx, ny), L


def lerp(a, b, t):
    return a + (b - a) * t


PK = CP.PARKS


def tree_clumps(x0, y0, x1, y1, rr):
    """AD r3: tree clumps inside a rectangle (world BU): a few clumps of round crowns on short trunks."""
    for _ in range(rr.randint(*PK["clumps"])):
        cx_, cy_ = rr.uniform(min(x0, x1) + 1.0, max(x0, x1) - 1.0), rr.uniform(min(y0, y1) + 1.0, max(y0, y1) - 1.0)
        for _ in range(rr.randint(*PK["trees"])):
            r_ = rr.uniform(*PK["r"])
            tx, ty = cx_ + rr.uniform(-2.2, 2.2), cy_ + rr.uniform(-2.2, 2.2)
            if not (min(x0, x1) + r_ < tx < max(x0, x1) - r_ and min(y0, y1) + r_ < ty < max(y0, y1) - r_):
                continue
            bar(SURF, (tx, ty, 0.0), (tx, ty, r_ * 1.1), 0.22, (0.16, 0.12, 0.09))
            dome(SMOOTH, tx, ty, r_ * 1.6, r_, sc(rr.choice(PK["tree_cols"]), rr.uniform(0.8, 1.15)), n=7, rings=2, hemi=False)


def park(p0, p1, rr):
    """a park: lawn, a cross of paths, tree clumps (world BU corners p0, p1)."""
    (x0, y0), (x1, y1) = p0, p1
    GROUND.face([(x0, y0, 0.02), (x1, y0, 0.02), (x1, y1, 0.02), (x0, y1, 0.02)], PK["lawn"])
    mx_, my_ = (x0 + x1) / 2, (y0 + y1) / 2
    strip(GROUND, (x0, my_), (x1, my_), 0.9, 0.03, PK["path"])
    strip(GROUND, (mx_, y0), (mx_, y1), 0.9, 0.03, PK["path"])
    tree_clumps(x0, y0, x1, y1, rr)


def building(b):
    d = b["terr"]
    D = RU.palette(d)                  # round 3: REBEL_CELL wears the sprawl palette (note 8); the language stays its own
    lang = DIST[d]["lang"]
    r = random.Random(b["key"] * 7 + 13)
    q = [W(p) for p in b["q"]]
    n = len(q)
    sub = b.get("sub", 0.0)
    wet = b.get("wet", 0)
    uu = 1.0 if wet else b.get("u", 1.0)          # the urban core factor (note 6): low and dim past the organic edge
    RSIDE = b.get("rail_side", 0)      # beside the Meridian viaduct: a plain roof under the side cap (art director ruling)
    z0 = b["z0"] * KH - sub
    h = b["h"] * KH * (CP.REBEL_H if d == "rebel_cell" else 1.0) * lerp(CP.URBAN["h_k"][0], CP.URBAN["h_k"][1], uu)
    z1 = z0 + h
    ts = b["ts"]
    cxq, cyq = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
    col = sc(D["mat"][abs(b["key"]) % len(D["mat"])], r.uniform(0.85, 1.12))
    roof_day = None
    if DAYM:
        # AD r3 (day test 2): a material family per building (concrete, glass curtain, brick, rust, stone; the sprawl
        # rustier), a roof finish (tar, gravel, green, solar, terracotta), then the corp tint, stronger near its HQ
        DM = CP.DAY_MATS
        fam = RU.pick(DM["sprawl" if d in ("", "rebel_cell") else "city"], RU._hash01(7720, b["key"]))
        col = DM["glass"] if fam == "glass" else mixc(col, fam, DM["k"])
        roof_day = RU.pick(CP.DAY_ROOFS, RU._hash01(7721, b["key"]))
        if d not in ("", "rebel_cell"):
            hq_ = O["hq"][d]
            dh = math.hypot(b["c"][0] - hq_[0], b["c"][1] - hq_[1]) if "c" in b else 99.0
            col = mixc(col, sc(D["hue"], 0.55), min(0.75, CP.DAY["tint"] + CP.DAY["tint_near"] * math.exp(-dh / CP.DAY["tint_r"])))
    wc = D["win"][r.randrange(len(D["win"]))]
    wl = D["lit"] * r.uniform(0.55, 1.35) * lerp(CP.URBAN["lit_k"][0], CP.URBAN["lit_k"][1], uu)
    bid = r.random()
    wm = 0
    if b.get("crest"):            # round 34: the fist in red windows (subtle: SEQ 2 "lit", not the full blaze)
        wc, wl = (0.95, 0.15, 0.12), 0.30          # subtle (designer): fewer, dimmer red windows
    if wet:                       # the drowned quarter: the tenements are still lit (people live behind the pumps)
        wl = max(wl, 0.45)        # brighter (art review): the drowned windows read through the clear water
    hue = D["hue"]
    xs, ys = [p[0] for p in q], [p[1] for p in q]
    wx, wy = max(xs) - min(xs), max(ys) - min(ys)
    small = min(wx, wy)
    top = z1
    if lang == "capsule" and small > 2.2 and r.random() < 0.55 and ts > 0.99 and not RSIDE:
        # SOLACE: round capsule towers with ribbon windows and a domed cap
        rad = small * 0.48
        cyl(SMOOTH, cxq, cyq, z0, z1, rad, 14, col, wc=wc, wl=wl, wm=1, bid=bid, wet=wet)
        dome(SMOOTH, cxq, cyq, z1, rad, mixc(col, (0.8, 0.9, 0.85), 0.3), n=14, rings=4, zscale=0.45, wet=wet, bid=bid)
        if r.random() < 0.5:
            ring_line(NEON, cxq, cyq, z1 + 0.1, rad + 0.05, 0.22, hue, n=14, wet=wet)
        top = z1 + rad * 0.45
    elif lang == "civic" and h > 7 and small > 2.4:
        # HALCYON: stepped setbacks (ziggurat tiers), violet tier trims
        tiers = 2 + (h > 16) + (h > 30)
        zz = z0
        fr = [0.55, 0.27, 0.12, 0.06][:tiers]
        s = sum(fr)
        cur = q
        for k in range(tiers):
            zt = zz + h * fr[k] / s
            prism(SURF, cur, zz, zt, col, wc=wc, wl=wl, wm=wm, bid=bid, wet=wet, vz0=zz - z0)
            if r.random() < 0.6:
                for i in range(len(cur)):
                    j = (i + 1) % len(cur)
                    bar(NEON, (cur[i][0], cur[i][1], zt + 0.05), (cur[j][0], cur[j][1], zt + 0.05), 0.2,
                        hue if k % 2 == 0 else D["sec"], wet=wet)
            cur = [(cxq + (x - cxq) * 0.78, cyq + (y - cyq) * 0.78) for (x, y) in cur]
            zz = zt
        top = zz
    elif lang == "roman" and h > 10 and small < 6.0 and small > 2.0 and r.random() < 0.3 and not RSIDE:
        # AURELIAN: campanile (round, arcaded galleries, flat crown: cornice, roof, parapet, verdigris ring)
        rad = min(small * 0.5, 2.6)
        hz = max(h * 1.25, 14.0)
        cyl(SMOOTH, cxq, cyq, z0, z0 + 3.0, rad * 1.15, 14, col, wet=wet, bid=bid)
        lv = int((hz - 4.5) / 3.2)
        zz = z0 + 3.0
        for k in range(lv):
            cyl(SMOOTH, cxq, cyq, zz, zz + 3.2, rad, 14, col, wc=(1.0, 0.8, 0.5), wl=0.75, wm=4, bid=bid, wet=wet,
                uvs=(1.6 / 1.3, 1.9 / 3.2), vz0=0.0)
            cyl(SURF, cxq, cyq, zz + 3.2, zz + 3.45, rad * 1.1, 14, mixc(col, (1, 1, 1), 0.15), wet=wet, bid=bid)
            zz += 3.45
        cyl(SURF, cxq, cyq, zz, zz + 0.5, rad * 1.18, 14, col, wet=wet, bid=bid)          # cornice + flat roof
        cyl(SURF, cxq, cyq, zz + 0.5, zz + 1.1, rad * 1.05, 14, col, wet=wet, bid=bid, top=False)   # parapet
        ring_line(NEON, cxq, cyq, zz + 0.55, rad * 1.2, 0.2, D["sec"], n=14, wet=wet)
        top = zz + 1.1
    elif lang == "roman" and small > 9.0 and r.random() < 0.5 and not RSIDE:
        # AURELIAN: basilica (podium + drum + verdigris copper dome)
        prism(SURF, q, z0, z0 + min(h, 7.0), col, wc=D["win"][0], wl=0.5, wm=4, bid=bid, wet=wet, uvs=(1.6 / 2.4, 1.9 / 3.5))
        zt = z0 + min(h, 7.0)
        rad = small * 0.36
        cyl(SMOOTH, cxq, cyq, zt, zt + rad * 0.5, rad, 18, col, wc=(1.0, 0.8, 0.5), wl=0.8, wm=4, bid=bid, wet=wet,
            uvs=(1.6 / 1.6, 1.9 / 2.0))
        dome(SMOOTH, cxq, cyq, zt + rad * 0.5, rad, (0.16, 0.42, 0.34), n=18, rings=6, wet=wet, bid=bid)
        ring_line(NEON, cxq, cyq, zt + rad * 0.5 + 0.05, rad + 0.05, 0.22, hue, n=18, wet=wet)
        cyl(NEON, cxq, cyq, zt + rad * 1.5 - 0.1, zt + rad * 1.5 + 0.9, 0.35, 6, (1.0, 0.85, 0.5), wet=wet)
        top = zt + rad * 1.5
    else:
        prism(SURF, q, z0, z1, col, ts=ts, wc=wc, wl=wl, wm=(2 if lang == "hull" else wm), bid=bid, wet=wet,
              top_col=roof_day or sc(col, 1.05))
        top = z1
        if lang == "roman" and ts > 0.99:
            # colonnade on the street faces (the ground floor arcade), cornices every 4 floors, pediment / parapet
            for i in range(n):
                j = (i + 1) % n
                a, c = q[i], q[j]
                vis, (nx, ny), L = seen(a, c, cxq, cyq)
                if L < 3.0 or not vis:
                    continue
                k = int(L / 1.6)
                for m in range(k + 1):
                    t = 0.2 + (L - 0.4) * m / max(1, k)
                    px, py = a[0] + (c[0] - a[0]) / L * t + nx * 0.9, a[1] + (c[1] - a[1]) / L * t + ny * 0.9
                    bar(SURF, (px, py, z0), (px, py, z0 + 3.0), 0.32, mixc(col, (1, 1, 1), 0.2), wet=wet, bid=bid)
                e0 = (a[0] + nx * 1.1, a[1] + ny * 1.1)
                e1 = (c[0] + nx * 1.1, c[1] + ny * 1.1)
                prism(SURF, [a, c, e1, e0], z0 + 3.0, z0 + 3.45, mixc(col, (1, 1, 1), 0.15), wet=wet, bid=bid)
                strip(NEON, (a[0] + nx * 0.4, a[1] + ny * 0.4), (c[0] + nx * 0.4, c[1] + ny * 0.4), 0.9, z0 + 0.05,
                      sc((1.0, 0.75, 0.42), 0.7), wet=wet)
                zc = z0 + 4 * CP.FLOOR + 3.0
                while zc < z1 - 1.5:
                    bar(SURF, (a[0] + nx * 0.15, a[1] + ny * 0.15, zc), (c[0] + nx * 0.15, c[1] + ny * 0.15, zc), 0.35,
                        mixc(col, (1, 1, 1), 0.15), wet=wet, bid=bid)
                    zc += 4 * CP.FLOOR
            if r.random() < 0.3 and n == 4:
                ln = sorted(range(4), key=lambda i: -math.hypot(q[(i + 1) % 4][0] - q[i][0], q[(i + 1) % 4][1] - q[i][1]))[0]
                a, c = q[ln], q[(ln + 1) % 4]
                d_, e = q[(ln + 2) % 4], q[(ln + 3) % 4]
                ma = ((a[0] + e[0]) / 2, (a[1] + e[1]) / 2)
                mc = ((c[0] + d_[0]) / 2, (c[1] + d_[1]) / 2)
                hp = min(2.6, small * 0.3)
                SURF.face([(a[0], a[1], z1), (c[0], c[1], z1), (mc[0], mc[1], z1 + hp), (ma[0], ma[1], z1 + hp)], sc(col, 0.9), None, (0, 0, 0), 0, 3, bid, wet)
                SURF.face([(d_[0], d_[1], z1), (e[0], e[1], z1), (ma[0], ma[1], z1 + hp), (mc[0], mc[1], z1 + hp)], sc(col, 0.9), None, (0, 0, 0), 0, 3, bid, wet)
                SURF.face([(a[0], a[1], z1), (ma[0], ma[1], z1 + hp), (e[0], e[1], z1)], col, None, (0, 0, 0), 0, 3, bid, wet)
                SURF.face([(c[0], c[1], z1), (d_[0], d_[1], z1), (mc[0], mc[1], z1 + hp)], col, None, (0, 0, 0), 0, 3, bid, wet)
                bar(NEON, (ma[0], ma[1], z1 + hp + 0.1), (mc[0], mc[1], z1 + hp + 0.1), 0.18, D["sec"], wet=wet)
                top = z1 + hp
            elif r.random() < 0.5:
                for i in range(n):
                    j = (i + 1) % n
                    bar(SURF, (q[i][0], q[i][1], z1 + 0.3), (q[j][0], q[j][1], z1 + 0.3), 0.45, sc(col, 1.05), wet=wet, bid=bid)
                if r.random() < 0.35:
                    bar(NEON, (q[0][0], q[0][1], z1 + 0.62), (q[1][0], q[1][1], z1 + 0.62), 0.18, D["sec"], wet=wet)
                if r.random() < 0.25:    # rooftop statue (billboard mount)
                    bar(SURF, (cxq, cyq, z1), (cxq, cyq, z1 + 2.2), 0.6, (0.9, 0.86, 0.78), wet=wet, bid=bid)
        if lang == "freight" and ts > 0.99 and small > 1.8 and r.random() < 0.95:
            # MERIDIAN: stacked shipping containers on the roofs, sodium roof lamps
            CC = [(0.62, 0.24, 0.08), (0.12, 0.34, 0.36), (0.42, 0.40, 0.38), (0.55, 0.12, 0.08), (0.75, 0.42, 0.10)]
            for k in range(r.randint(2, 6)):
                lx, ly = r.uniform(min(xs) + 0.9, max(xs) - 0.9), r.uniform(min(ys) + 0.6, max(ys) - 0.6)
                lv = 0 if RSIDE else r.randint(0, 3)
                if r.random() < 0.5:
                    box(SURF, lx - 1.2, ly - 0.45, z1 + lv * 0.95, lx + 1.2, ly + 0.45, z1 + (lv + 1) * 0.95, CC[r.randrange(5)], wet=wet, bid=bid)
                else:
                    box(SURF, lx - 0.45, ly - 1.2, z1 + lv * 0.95, lx + 0.45, ly + 1.2, z1 + (lv + 1) * 0.95, CC[r.randrange(5)], wet=wet, bid=bid)
                top = max(top, z1 + (lv + 1) * 0.95)
            if r.random() < 0.5:
                box(NEON, cxq - 0.25, cyq - 0.25, z1 + 0.05, cxq + 0.25, cyq + 0.25, z1 + 0.4, (1.0, 0.55, 0.15), wet=wet)
        if lang == "spire" and ts > 0.99:
            # ORBITAL: masts with red beacons on the tall roofs, dishes, an ice crown trim
            if h > 18 and r.random() < 0.55:
                mh = r.uniform(5, 14)
                bar(SURF, (cxq, cyq, z1), (cxq, cyq, z1 + mh), 0.3, (0.5, 0.55, 0.62), wet=wet, bid=bid)
                box(NEON, cxq - 0.3, cyq - 0.3, z1 + mh, cxq + 0.3, cyq + 0.3, z1 + mh + 0.5, (1.0, 0.08, 0.06), wet=wet)
                top = z1 + mh
            if small > 3 and r.random() < 0.3:
                dx, dy = r.uniform(-0.25, 0.25) * wx, r.uniform(-0.25, 0.25) * wy
                annulus(SURF, cxq + dx, cyq + dy, z1 + 1.2, 0.01, min(1.4, small * 0.25), (0.8, 0.82, 0.86), n=10, z1=z1 + 0.6, wet=wet)
        if lang == "tenement" and ts > 0.99:
            # REBEL_CELL, the mainline identity: a Tokyo alley / street canyon. Every street face carries stacked blade
            # signs (vertical neon, out over the narrow street), stacked box signs between the floors, a lit shop
            # front with an awning; tall roofs carry a holo panel. Palette: TOKYO (pink, cyan, amber, white, violet, red)
            TOKYO = [(1.0, 0.2, 0.45), (0.2, 0.9, 1.0), (1.0, 0.65, 0.2), (1.0, 0.95, 0.85), (0.85, 0.3, 1.0), (1.0, 0.12, 0.1)]
            TOKYO_R = TOKYO[:5]          # round 3 (note 8): no red weighting, no red; the canyon wears the mixed sign palette
            for i in range(n):
                j = (i + 1) % n
                a, c = q[i], q[j]
                vis, (nx, ny), L = seen(a, c, cxq, cyq)
                if L < 2.0 or h < 3.0:
                    continue
                ux_, uy_ = (c[0] - a[0]) / L, (c[1] - a[1]) / L
                for kk in range(r.randint(1, 3 if vis else 1)):          # blade signs, out from the facade
                    t0 = r.uniform(0.4, L - 0.4)
                    zb = z0 + r.uniform(1.4, max(1.6, min(h * 0.5, 6.0)))
                    zt = min(z1 - 0.3, zb + r.uniform(2.5, 7.5))
                    if zt <= zb + 1.0:
                        continue
                    out = r.uniform(0.5, 1.3)
                    px, py = a[0] + ux_ * t0, a[1] + uy_ * t0
                    sc_ = r.choice(TOKYO_R)
                    BILL.face([(px + nx * 0.1, py + ny * 0.1, zb), (px + nx * out, py + ny * out, zb), (px + nx * out, py + ny * out, zt),
                               (px + nx * 0.1, py + ny * 0.1, zt)], sc(sc_, 0.85))
                if vis:
                    for kk in range(r.randint(1, 4)):                     # stacked box signs between the floors
                        w_ = r.uniform(0.8, min(3.2, L - 0.4))
                        t0 = r.uniform(0.2, max(0.25, L - w_ - 0.2))
                        zb = z0 + 1.3 + r.randint(0, max(0, int(min(h, 10.0) / 1.9) - 1)) * 1.9
                        hb = r.uniform(0.5, 0.95)
                        p0 = (a[0] + ux_ * t0 + nx * 0.12, a[1] + uy_ * t0 + ny * 0.12)
                        p1 = (p0[0] + ux_ * w_, p0[1] + uy_ * w_)
                        NEON.face([(p0[0], p0[1], zb), (p1[0], p1[1], zb), (p1[0], p1[1], zb + hb), (p0[0], p0[1], zb + hb)],
                                  sc(r.choice(TOKYO_R), r.uniform(0.5, 0.9)))
                    if z0 > -0.5:                                          # the shop front + awning, always
                        p0 = (a[0] + nx * 0.07, a[1] + ny * 0.07)
                        p1 = (c[0] + nx * 0.07, c[1] + ny * 0.07)
                        NEON.face([(p0[0], p0[1], 0.15), (p1[0], p1[1], 0.15), (p1[0], p1[1], 1.15), (p0[0], p0[1], 1.15)],
                                  sc(r.choice([(1.0, 0.78, 0.5), (1.0, 0.5, 0.75), (0.55, 0.9, 1.0)]), 0.7))
                        e0, e1 = (p0[0] + nx * 0.9, p0[1] + ny * 0.9), (p1[0] + nx * 0.9, p1[1] + ny * 0.9)
                        SURF.face([(p0[0], p0[1], 1.5), (p1[0], p1[1], 1.5), (e1[0], e1[1], 1.25), (e0[0], e0[1], 1.25)],
                                  r.choice([(0.55, 0.12, 0.14), (0.2, 0.2, 0.26), (0.5, 0.36, 0.14)]), None, wet=wet)
                        # a lantern string sagging along the street face, out over the alley (red / amber paper lanterns)
                        ns = max(4, int(L / 0.9))
                        for m in range(ns + 1):
                            t = m / ns
                            sag = 0.7 * 4 * t * (1 - t)
                            lx_ = a[0] + (c[0] - a[0]) * t + nx * 1.4
                            ly_ = a[1] + (c[1] - a[1]) * t + ny * 1.4
                            lz = 3.4 - sag
                            lc = (1.0, 0.62, 0.26) if (m + kk) % 3 else (1.0, 0.86, 0.6)     # amber / warm white (no red yet)
                            box(NEON, lx_ - 0.13, ly_ - 0.13, lz - 0.18, lx_ + 0.13, ly_ + 0.13, lz + 0.12, lc)
            if h > 12 and r.random() < 0.3 and not RSIDE:                                # rooftop holo panel, facing the camera
                hc = r.choice(TOKYO[:3] + TOKYO[4:])
                wv = r.uniform(3.0, 6.0)
                BILL.face([(cxq + 0.7 * wv / 2, cyq + 0.7 * wv / 2, z1 + 1), (cxq - 0.7 * wv / 2, cyq - 0.7 * wv / 2, z1 + 1),
                           (cxq - 0.7 * wv / 2, cyq - 0.7 * wv / 2, z1 + 1 + wv * 0.6), (cxq + 0.7 * wv / 2, cyq + 0.7 * wv / 2, z1 + 1 + wv * 0.6)],
                          sc(hc, 0.6))
        if lang == "tenement" and ts > 0.99 and small > 2 and r.random() < 0.3:
            tx, ty = r.uniform(min(xs) + 1.0, max(xs) - 1.0), r.uniform(min(ys) + 1.0, max(ys) - 1.0)
            for dx, dy in ((-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5)):
                bar(SURF, (tx + dx, ty + dy, z1), (tx + dx, ty + dy, z1 + 0.9), 0.12, (0.2, 0.2, 0.24), wet=wet)
            cyl(SURF, tx, ty, z1 + 0.9, z1 + 2.1, 0.8, 8, (0.42, 0.34, 0.30), wet=wet)
        if lang == "hull" and ts > 0.99:
            # TETHYS: photophore strips up the corners, pressure-glass roof domes, a red beacon
            if r.random() < 0.45:
                k = r.randrange(n)
                bar(NEON, (q[k][0], q[k][1], z0 + 0.5), (q[k][0], q[k][1], z1), 0.18, D["sec"], wet=wet)
            if small > 3.0 and r.random() < 0.22 and not RSIDE:
                rad = small * 0.35
                dome(GLASS, cxq, cyq, z1, rad, (0.55, 0.8, 1.0), n=14, rings=5, wet=wet)
                box(NEON, cxq - rad * 0.4, cyq - rad * 0.3, z1, cxq + rad * 0.3, cyq + rad * 0.4, z1 + rad * 0.35, (1.0, 0.85, 0.6), wet=wet)
                ring_line(NEON, cxq, cyq, z1 + 0.1, rad + 0.05, 0.2, D["hue"], n=14, wet=wet)
                top = z1 + rad
            if h > 14 and r.random() < 0.3:
                box(NEON, cxq - 0.3, cyq - 0.3, z1, cxq + 0.3, cyq + 0.3, z1 + 0.5, (0.78, 0.15, 0.3), wet=wet)
        if lang == "sprawl" and ts > 0.99 and h > 14 and r.random() < 0.16 and not RSIDE:
            hc = r.choice([(1.0, 0.3, 0.7), (0.3, 0.9, 1.0), (0.7, 0.45, 1.0), (1.0, 0.65, 0.2)])
            wv = r.uniform(3.0, 6.0)
            BILL.face([(cxq + 0.7 * wv / 2, cyq + 0.7 * wv / 2, z1 + 1), (cxq - 0.7 * wv / 2, cyq - 0.7 * wv / 2, z1 + 1),
                       (cxq - 0.7 * wv / 2, cyq - 0.7 * wv / 2, z1 + 1 + wv * 0.6), (cxq + 0.7 * wv / 2, cyq + 0.7 * wv / 2, z1 + 1 + wv * 0.6)],
                      sc(hc, 0.75), None, wet=wet)
        # the district neon crown trim (the district reads by its hue from above)
        trim_p = {"freight": 0.16, "capsule": 0.20, "civic": 0.20, "spire": 0.25, "tenement": 0.14, "roman": 0.15,
                  "hull": 0.22, "sprawl": 0.20}[lang]
        if not (b.get("art") or b.get("border")):
            trim_p *= CP.OUTLINE["trim_off_k"]          # art review: no wireframe grid (full trims on arterials / borders)
        trim_p *= 0.25 + 0.75 * uu                      # round 3: fewer past the organic edge
        if lang == "roman":
            hue = D["sec"]                              # Aurelian: gilt trims (verdigris only on domes)
        if r.random() >= trim_p and ts > 0.99 and small > 1.6:
            # rooftop clutter + a warm lamp instead of an outline
            for k in range(r.randint(1, 3)):
                vx, vy = r.uniform(min(xs) + 0.4, max(xs) - 0.9), r.uniform(min(ys) + 0.4, max(ys) - 0.8)
                box(SURF, vx, vy, top, vx + r.uniform(0.5, 1.0), vy + r.uniform(0.4, 0.8), top + r.uniform(0.3, 0.7),
                    r.choice([(0.30, 0.30, 0.34), (0.36, 0.34, 0.32), (0.24, 0.25, 0.30)]), wet=wet, bid=bid)
            if r.random() < CP.OUTLINE["lamp_p"]:
                vx, vy = r.uniform(min(xs) + 0.3, max(xs) - 0.3), r.uniform(min(ys) + 0.3, max(ys) - 0.3)
                box(NEON, vx - 0.18, vy - 0.18, top + 0.05, vx + 0.18, vy + 0.18, top + 0.35, (1.0, 0.68, 0.32), wet=wet)
        if r.random() < trim_p and ts > 0.05:
            tp = [(cxq + (x - cxq) * ts, cyq + (y - cyq) * ts) for (x, y) in q]
            c2 = hue if r.random() < 0.75 else D["sec"]
            if b.get("crest"):
                c2 = DIST[d]["sec"]
            if d == "":
                c2 = sc(c2, CP.OUTLINE["out_k"])          # outside the seven districts (revision 2)
            for i in range(n):
                j = (i + 1) % n
                bar(NEON, (tp[i][0], tp[i][1], z1 + 0.08), (tp[j][0], tp[j][1], z1 + 0.08), 0.2, c2, wet=wet)
        # street-level shopfronts on the camera faces (the AAA street glow seen from above)
        if z0 > -0.5 and not wet and h > 2 and lang != "tenement":
            for i in range(n):
                j = (i + 1) % n
                vis, (nx, ny), L = seen(q[i], q[j], cxq, cyq)
                if vis and L > 2.5 and r.random() < 0.4:
                    s_c = r.choice([(1.0, 0.75, 0.45), (1.0, 0.5, 0.8), (0.5, 0.9, 1.0), hue])
                    a, c = q[i], q[j]
                    NEON.face([(a[0] + nx * 0.06, a[1] + ny * 0.06, 0.2), (c[0] + nx * 0.06, c[1] + ny * 0.06, 0.2),
                               (c[0] + nx * 0.06, c[1] + ny * 0.06, 1.1), (a[0] + nx * 0.06, a[1] + ny * 0.06, 1.1)], sc(s_c, 0.55), None)
    ROOFS.append((cxq, cyq, top, b["key"], d, wet))


for b in O["buildings"]:
    building(b)
print("BUILDINGS", len(O["buildings"]), "%.1fs" % (time.time() - T0), flush=True)

# ------------------------------------------------------------------ ground: asphalt, streets, lanes, plazas
WET_CELLS = {(c[0], c[1]): c[2] for c in O["lagoon_cells"]}
# the base ground: lot-cell runs on the land side of the coast, with the drowned quarter cut out (its seabed is below)
for _ly in range(-300, 312):
    _run = None
    for _lx in range(-300, 313):
        _ok = _lx < 312 and (_lx, _ly) not in WET_CELLS and \
            -((_lx + 0.5 - CX) + (_ly + 0.5 - CY)) / R2 < bwall(((_lx + 0.5 - CX) - (_ly + 0.5 - CY)) / R2) + 0.6 and abs(_lx + 0.5 - CX) + abs(_ly + 0.5 - CY) < 300
        if _ok and _run is None:
            _run = _lx
        elif not _ok and _run is not None:
            _q = [W((_run, _ly)), W((_lx, _ly)), W((_lx, _ly + 1)), W((_run, _ly + 1))]
            GROUND.face([(x, y, -0.03) for (x, y) in _q], (0.075, 0.075, 0.08) if DAYM else (0.12, 0.12, 0.15))   # day: asphalt (the ring streets too)
            _run = None
for pz in O["plazas"]:
    if pz.get("wet"):
        continue
    q = [W(p) for p in pz["q"]]
    tc = DIST[pz["terr"]]["hue"] if pz["terr"] in DIST else (0.8, 0.8, 0.8)
    rp_ = random.Random(7722 * 100003 + int(sum(p[0] * 1000 + p[1] for p in pz["q"])))
    is_park = rp_.random() < PK["plaza_p"]            # AD r3: plazas are parks (lawn + tree clumps) or paved squares
    if DAYM:
        GROUND.face([(x, y, 0.005) for (x, y) in q], PK["lawn"] if is_park else PK["paved"])
    else:
        GROUND.face([(x, y, 0.005) for (x, y) in q], mixc((0.13, 0.125, 0.15), tc, 0.12))
    if is_park:
        xs_, ys_ = [p[0] for p in q], [p[1] for p in q]
        if max(xs_) - min(xs_) > 4.0 and max(ys_) - min(ys_) > 4.0:
            tree_clumps(min(xs_), min(ys_), max(xs_), max(ys_), rp_)
for t in O["tiles"]:
    if t["wet"]:
        continue
    q = [W(p) for p in t["q"]]
    GROUND.face([(x, y, 0.01) for (x, y) in q], (0.05, 0.05, 0.055) if DAYM else (0.085, 0.085, 0.11))   # day: dark asphalt
    if not t["ab"] or not t["col"] or t.get("lm"):        # round 3: nothing under a landmark
        continue
    a, b = W(t["ab"][0]), W(t["ab"][1])
    col, tr = tuple(t["col"]), t["tr"]
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -dy, dx
    strokes = 7 + int(tr * 23)
    half = (1.5 + strokes * 0.42) / 38.0 * U
    nl = min(strokes, 3 + int(tr * 9))
    hr = random.Random(t["i"] * 7919 + t["j"])
    for k in range(min(nl, 4)):
        u = (k + 0.5) / min(nl, 4) * 2 - 1
        lane = u * half * 0.8 + (hr.random() - 0.5) * 0.25
        al = (0.35 + 0.3 * hr.random() + tr * 0.15) * 0.5 * (1.0 if t.get("art") else CP.OUTLINE["lane_off_k"])
        al *= CP.OUTLINE["out_k"] if t.get("terr", "") == "" else 1.0     # outside the seven districts (revision 2)
        al *= 0.3 + 0.7 * t.get("u", 1.0)                                 # round 3: dimmer past the organic edge
        strip(NEON, (a[0] + nx * lane - dx * 0.35, a[1] + ny * lane - dy * 0.35), (b[0] + nx * lane + dx * 0.35, b[1] + ny * lane + dy * 0.35),
              0.14, 0.04, sc(col, al))
    if hr.random() < 0.5:                         # a warm street lamp at the kerb (the street glow off the arterials)
        sd = 1 if hr.random() < 0.5 else -1
        lx_, ly_ = (a[0] + b[0]) / 2 + nx * sd * (half + 0.4), (a[1] + b[1]) / 2 + ny * sd * (half + 0.4)
        box(NEON, lx_ - 0.16, ly_ - 0.16, 1.5, lx_ + 0.16, ly_ + 0.16, 1.8, (1.0, 0.7, 0.38))

# ------------------------------------------------------------------ arterial light-streaks (r3 street-lane rule, city scale)
RT = random.Random(CP.SEEDS["streaks"])
LMK_W = {k: W(O["hq"][k]) for k in O.get("landmarks", [])}
RC = random.Random(CP.SEEDS["streaks"] + 11)       # day: car colours / spacing (its own stream, the night draws stay put)


def under_landmark(x, y, m=2.0):
    return any(RU.in_footprint(k, x - v[0], y - v[1], m) for k, v in LMK_W.items())


def traffic(p0, p1, z, col, k, w=0.16):
    """one traffic draw: at night a light streak (long exposure), by day a row of cars along the same stretch."""
    if not DAYM:
        strip(STREAK, p0, p1, w, z, sc(col, k))
        return
    L = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if L < 1.0:
        return
    ux_, uy_ = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
    s = RC.uniform(0.0, 1.2)
    while s < L - 1.0:
        c0 = (p0[0] + ux_ * s, p0[1] + uy_ * s)
        c1 = (c0[0] + ux_ * 1.05, c0[1] + uy_ * 1.05)
        nx_, ny_ = -uy_ * 0.24, ux_ * 0.24
        q_ = [(c0[0] - nx_, c0[1] - ny_), (c1[0] - nx_, c1[1] - ny_), (c1[0] + nx_, c1[1] + ny_), (c0[0] + nx_, c0[1] + ny_)]
        prism(SURF, q_, z - 0.1, z + 0.32, RC.choice(CP.DAY["car_cols"]), top_col=None)
        s += RC.uniform(1.9, 4.2)


# arterial light-streaks (r3 street-lane rule, city scale); round 3 (note 6): they run on along their own line into the
# sprawl (zoning H6 ext) and thin out there, density and brightness x exp(-d / TRAILS.thin) lots past the map
for art in O["arterials"]:
    k_ax = 0 if art["axis"] == "x" else 1
    s_lo, s_hi = art["a"][k_ax], art["b"][k_ax]
    e_lo, e_hi = art.get("ext", [s_lo, s_hi])

    def lp(s_lot):
        p_ = list(art["a"])
        p_[k_ax] = s_lot
        return W(p_)
    a = lp(e_lo)
    b = lp(e_hi)
    L = math.hypot(b[0] - a[0], b[1] - a[1]) or 1
    dx, dy = (b[0] - a[0]) / L, (b[1] - a[1]) / L
    nx, ny = -dy, dx
    for off, dirn, col in ((0.55, 1, (1.0, 0.93, 0.82)), (1.25, 1, (1.0, 0.85, 0.6)), (-0.55, -1, (1.0, 0.1, 0.06)),
                           (-1.25, -1, (1.0, 0.18, 0.08))):
        s = -RT.uniform(0, 20)
        while s < L:
            ln = RT.uniform(4.0, 26.0)
            k = RT.uniform(0.45, 1.2) * (0.7 + 0.5 * art["tr"])
            gap = RT.uniform(3.0, 30.0)
            keep_r = RT.random()
            s0, s1 = max(0.0, s), min(L, s + ln)
            sl = e_lo + (s0 + s1) / 2 / U * (1 if e_hi >= e_lo else -1)
            dd = max(0.0, s_lo - sl, sl - s_hi)                 # lots past the map run
            fall = math.exp(-dd / CP.TRAILS["thin"])
            pa = (a[0] + dx * s0 + nx * off, a[1] + dy * s0 + ny * off)
            pb = (a[0] + dx * s1 + nx * off, a[1] + dy * s1 + ny * off)
            if s1 > s0 + 0.5 and keep_r < fall and not under_landmark((pa[0] + pb[0]) / 2, (pa[1] + pb[1]) / 2):
                traffic(pa, pb, 0.12, col, k * (0.45 + 0.55 * fall))
            s += ln + gap


for _f in ("city_world.py", "city_transit.py", "landmarks.py", "city_render.py"):
    exec(open(os.path.join(HERE, _f), encoding="utf-8").read())
