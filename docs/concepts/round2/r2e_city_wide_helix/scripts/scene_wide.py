"""Wide gritty-E day city with a double-helix HQ, rendered in passes for the focus treatment.

The city fills the frame and runs past every edge. Only our district (3x3 blocks) is full colour
and full ink with the crystal node/path overlay; every other block is rendered in separate passes
(thin light ink) that post_wide.py fades (desaturated, lightened, translucent) over a pale smog
backdrop. Heights are random everywhere (seeded), capped where a building would hide a path.
The gritty E double helix (hx_e.py) stands at the route's end, east of the district, whole in frame.

usage: blender -b --factory-startup --python scene_wide.py -- <out_dir> [samples]
writes <out_dir>/pass_outb.png, pass_dist.png, pass_outf.png, pass_hud.png, meta.json
"""
import json
import math
import os
import random
import sys
import bmesh
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tt_lib as T
import tt_props as Pr
import tt_facet as Fc
from tt_props import PAL, sub, label, px
from hx_e import Helix

args = T.arg_list()
OUT_DIR = args[0]
SAMPLES = int(args[1]) if len(args) > 1 else 32
os.makedirs(OUT_DIR, exist_ok=True)
NIGHT = False

sc = T.reset()
T.MODE["name"] = "day"
T.MODE["grit"] = 0.8
T.setup_render(sc, samples=SAMPLES, bg="#8a8468", line=2.6, transparent=True)
T.compositor(sc)
wbg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
wbg.inputs[1].default_value = 1.3
T.sun(2.2, "#ffd9a0", rot=(58, 0, -24), angle=12)
R = random.Random(2049)
NL = T.noline_coll()

# ---------------------------------------------------------------- phases (objects are tagged per render pass)
PHASE = {}


def snapshot():
    return set(bpy.data.objects)


def tag(before, phase):
    for o in set(bpy.data.objects) - before:
        PHASE[o.name] = phase


def M(h, **kw):
    return T.paint(h, **kw)


def to_noline(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    NL.objects.link(o)
    return o


WALLS = ["#39414f", "#6e4632", "#4d5e5e", "#7d776a", "#5e4038", "#474a3e", "#5a5360", "#3f4a44"]
ROOFS = ["#2a2d33", "#4a3a30", "#3a4446", "#55504a"]
NEON = ["#ff2fb0", "#8cff2a", "#3ff0ff", "#ff9a2a"]
WIN_MATS = [M("#2c3a42", gloss=0.6, stroke=0.25), M("#3e4a4c", gloss=0.5, stroke=0.25), M("#1b2026"),
            T.glow("#ffb45a", 1.3)]
WIN_W = [0.46, 0.28, 0.18, 0.08]


def pick_win(rng):
    x = rng.random()
    acc = 0
    for i, w in enumerate(WIN_W):
        acc += w
        if x <= acc:
            return i
    return 0


def multi_box(parts, mats, name, parent=None, bev=0.025):
    bm = bmesh.new()
    for (c, s, mi) in parts:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((v.co.x * s[0] + c[0], v.co.y * s[1] + c[1], v.co.z * s[2] + c[2]))
        for f in {f for v in r["verts"] for f in v.link_faces}:
            f.material_index = mi
    o = bpy.data.objects.new(name, T.mesh_from_bm(bm, name))
    T.link_obj(o)
    for m in mats:
        o.data.materials.append(m)
    if bev:
        T.bevel(o, bev, 1)
    if parent:
        o.parent = parent
    return o


def cable(p0, p1, sag=0.6, col="#15161a", r=0.03):
    cu = bpy.data.curves.new("cable", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    sp = cu.splines.new("POLY")
    n = 14
    sp.points.add(n - 1)
    for i in range(n):
        t = i / (n - 1)
        p = Vector(p0).lerp(Vector(p1), t)
        p.z -= sag * 4 * t * (1 - t)
        sp.points[i].co = (p.x, p.y, p.z, 1)
    o = bpy.data.objects.new("cable", cu)
    T.link_obj(o)
    cu.materials.append(M(col))
    return o


TAGS = ["Zkr", "vX0", "KRSH", "n0Mad", "RxT", "SL1M", "0bey?", "Kx", "wYrm", "LLx"]


def neon_mat(c, s=3.5, broken=False):
    if broken:
        return M("#2a2630")
    return T.glow(c, 1.7)


def graffiti(body, w, d, side, rng):
    word = rng.choice(TAGS)
    col = rng.choice(("#8cff2a", "#ff2fb0", "#e8e4dc", "#ffcf3a", "#3ff0ff"))
    t = T.text(word, rng.uniform(0.35, 0.5), (rng.uniform(-w / 3, w / 3), -d / 2 - 0.035, rng.uniform(0.35, 0.9)),
               rot=(90, 0, rng.uniform(-6, 6)), mat=T.flat_col(col), fnt="tag", extrude=0.0, bev=0, coll=NL)
    t.parent = body


def stacked_signs(body, w, d, h, side, rng):
    n = rng.randint(1, 3)
    z = min(h - 0.4, 4.8)
    sx = side * (w / 2 + 0.3)
    for k in range(n):
        word = rng.choice(("BAR", "RAM", "EAT", "24H", "CHIP", "OPEN", "VAPE", "HOTEL", "BIO", "LOAN"))
        sz = 0.34
        bh = len(word) * sz * 1.05 + 0.22
        z0 = z - bh
        if z0 < 0.4:
            break
        yy = -d / 2 + 0.35 + (k % 2) * 0.25
        b = T.box((0.12, 0.55, bh), (sx, yy, z0), M(rng.choice(("#23222a", "#3a2a2a", "#26303a"))), bev=0.04,
                  wonk=0.03, rng=rng, rot=(0, 0, rng.uniform(-4, 4)))
        b.parent = body
        t = T.text("\n".join(word), sz, (sx + side * 0.08, yy, z0 + bh / 2), rot=(90, 0, 90 * side),
                   mat=neon_mat(rng.choice(NEON), 3.5, rng.random() < 0.25), fnt="title", extrude=0.03, bev=0,
                   coll=T.thin_coll())
        t.parent = body
        z = z0 - 0.15


def _roof_junk(cx, cy, w, d, zt, rng, full=True):
    for i in range(rng.randint(1, 4 if full else 2)):
        kind = rng.choice(("ac", "ac", "tank", "ant", "dish", "vent") if full else ("ac", "ant"))
        x = cx + rng.uniform(-w / 2 + 0.45, w / 2 - 0.45)
        y = cy + rng.uniform(-d / 2 + 0.45, d / 2 - 0.45)
        if kind == "ac":
            T.box((0.7, 0.55, 0.45), (x, y, zt), M("#8a8e88", gloss=0.2), bev=0.05, wonk=0.05, rng=rng)
        elif kind == "tank":
            for lx in (-0.25, 0.25):
                for ly in (-0.25, 0.25):
                    T.cyl(0.04, 0.5, (x + lx, y + ly, zt), M("#3a3530"), verts=6, bev=0)
            T.cyl(0.42, 0.7, (x, y, zt + 0.5), M("#5a4030", streak_axis=2, streak=18), verts=12, bev=0.05, wonk=0.05, rng=rng)
            T.cyl(0.5, 0.3, (x, y, zt + 1.2), M("#3a3a3a"), r2=0.05, verts=12, bev=0.03)
        elif kind == "ant":
            h_ = rng.uniform(1.0, 2.0)
            T.cyl(0.04, h_, (x, y, zt), M("#5a5a5a"), verts=6, bev=0)
            T.cyl(0.09, 0.1, (x, y, zt + h_), M("#a03a30"), verts=8, bev=0.02)
        elif kind == "dish":
            T.cyl(0.08, 0.35, (x, y, zt), M("#5a5a5a"), verts=6, bev=0)
            T.cyl(0.55, 0.22, (x, y, zt + 0.55), M("#b8b4a8", gloss=0.3), r2=0.12, verts=16, bev=0.03,
                  rot=(rng.uniform(-50, -30), 0, rng.uniform(-40, 40)), origin_bottom=False)
        else:
            T.cyl(0.16, 0.6, (x, y, zt), M("#6a6660", gloss=0.3), verts=10, bev=0.03)


def box_building(cx, cy, w, d, h, wall, rng, side, z0=0.18, name="bld", full=True):
    body = T.box((w, d, h), (cx, cy, z0), M(wall, seed=rng.randint(0, 99), streak_axis=rng.choice((0, 2)),
                                           pattern=rng.choice(("brick", "plank", "tiles", None))),
                 bev=0.12, wonk=0.025, rng=rng, taper=rng.uniform(-0.05, 0.06), name=name)
    body.rotation_euler = (math.radians(rng.uniform(-2, 2)), math.radians(rng.uniform(-2, 2)),
                           math.radians(rng.uniform(-3, 3)))
    fl_h = 1.05
    nfl = int((h - 0.3) / fl_h)
    parts = []
    for k in range(1, nfl + 1):
        zz = k * fl_h - 0.1
        if zz > h - 0.35:
            break
        if rng.random() < 0.6:
            parts.append(((0, 0, zz), (w + 0.1, d + 0.1, 0.1), 0))
    parts.append(((0, 0, h + 0.06), (w + 0.22, d + 0.22, 0.2), 1))
    multi_box(parts, [M("#5a574f", streak_axis=0), M(rng.choice(ROOFS), stroke=0.3)], name + "_trim", parent=body, bev=0.03)
    wparts = []
    cols = max(1, int(w / 0.62))
    scol = max(1, int(d / 0.62))
    for k in range(nfl):
        z = 0.3 + k * fl_h + 0.3
        if z + 0.3 > h - 0.2:
            break
        for c in range(cols):
            if rng.random() < 0.12:
                continue
            x = -w / 2 + (c + 0.5) * w / cols
            wparts.append(((x, -d / 2 - 0.02, z), (0.3, 0.1, 0.42), pick_win(rng)))
            if full and rng.random() < 0.18:
                wparts.append(((x, -d / 2 - 0.2, z - 0.35), (0.34, 0.3, 0.22), 0))
        for c in range(scol):
            if rng.random() < 0.12:
                continue
            y = -d / 2 + (c + 0.5) * d / scol
            wparts.append(((side * (w / 2 + 0.02), y, z), (0.1, 0.3, 0.42), pick_win(rng)))
    if wparts:
        multi_box(wparts, WIN_MATS, name + "_win", parent=body, bev=0.015 if full else 0.0)
    return body


def building(cx, cy, w, d, h, wall, side, rng, full=True, stack=None, name="bld"):
    body = box_building(cx, cy, w, d, h, wall, rng, side, name=name, full=full)
    top = h + 0.18
    if stack:
        sw, sd, sh = stack
        ox = rng.uniform(-(w - sw) / 2, (w - sw) / 2) * 0.8
        oy = rng.uniform(-(d - sd) / 2, (d - sd) / 2) * 0.8
        box_building(cx + ox, cy + oy, sw, sd, sh, rng.choice(WALLS), rng, side, z0=top + 0.1, name=name + "_st", full=full)
        _roof_junk(cx + ox, cy + oy, sw, sd, top + 0.1 + sh + 0.2, rng, full)
    else:
        _roof_junk(cx, cy, w, d, top + 0.2, rng, full)
    if full:
        if rng.random() < 0.5:
            s_ = T.box((rng.uniform(0.7, 1.1), 0.9, 0.75), (cx + rng.uniform(-w / 3, w / 3), cy + d / 2 - 0.6, top + 0.2),
                       M(rng.choice(("#6e5a44", "#4d5e5e", "#7a4a32")), pattern="plank"), bev=0.05, wonk=0.06, rng=rng)
        px_ = -side * (w / 2 + 0.08)
        T.cyl(0.08, h - 0.1, (px_, -d / 2 + 0.1, 0.0), M("#6a6258", gloss=0.3), verts=8, bev=0).parent = body
        T.cyl(0.06, h - 0.1, (px_ + side * 0.2, -d / 2 + 0.1, 0.0), M("#7a4a32"), verts=8, bev=0).parent = body
        if h > 2.8 and rng.random() < 0.7:
            stacked_signs(body, w, d, h, side, rng)
        if rng.random() < 0.6:
            graffiti(body, w, d, side, rng)
    return body


# ---------------------------------------------------------------- grid
BW, ST = 7.0, 1.6
DIST_X = [(-12.3, -5.4), (-3.8, 3.2), (4.8, 12.3)]
DIST_Y = [(-7.8, -2.0), (-0.2, 3.6), (5.0, 7.8)]
DX0, DX1, DY0, DY1 = -13.1, 13.1, -8.6, 8.6          # district boundary (half streets included)
HQ = (17.6, -1.1)                                     # helix axis: the avenue runs east out of the district into it
HQ_R = 5.0


def outer_lots():
    xs, ys = [], []
    x = 12.3 + ST
    while x < 44:
        xs.append((x, x + BW)); x += BW + ST
    x = -12.3 - ST
    while x > -44:
        xs.append((x - BW, x)); x -= BW + ST
    xs += DIST_X
    depths = [5.8, 3.8, 4.6]
    y = 7.8 + ST
    k = 0
    while y < 60:
        d = depths[k % 3]; ys.append((y, y + d)); y += d + ST; k += 1
    y = -7.8 - ST
    k = 0
    while y > -24:
        d = depths[(k + 1) % 3]; ys.append((y - d, y)); y -= d + ST; k += 1
    ys += DIST_Y
    lots = []
    for x0, x1 in sorted(xs):
        for y0, y1 in sorted(ys):
            if x0 >= DX0 and x1 <= DX1 and y0 >= DY0 and y1 <= DY1:
                continue
            lots.append((x0, y0, x1, y1))
    return lots


def hf():
    rng = random.Random(4099)
    cl = [(rng.uniform(-40, 45), rng.uniform(-20, 60), rng.uniform(3, 8), rng.uniform(5, 11)) for _ in range(24)]
    return lambda x, y: 1.6 + sum(a * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (r * r)) for cx, cy, a, r in cl)


HF = hf()

# ---------------------------------------------------------------- camera (orthographic, E frontal feel)
EL = math.radians(44)
OS = 56.0
r_ = Vector((1, 0, 0))
u_ = Vector((0, math.sin(EL), math.cos(EL)))
w_ = Vector((0, -math.cos(EL), math.sin(EL)))
hq_base = Vector((HQ[0], HQ[1], 0))
C = r_ * 6.2 + u_ * (hq_base.dot(u_) + 9.6) + w_ * 120.0
cam_d = bpy.data.cameras.new("ortho")
cam_d.type = "ORTHO"
cam_d.ortho_scale = OS
cam_d.clip_start = 0.1
cam_d.clip_end = 400
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
from mathutils import Matrix
cam.matrix_world = Matrix((r_, u_, w_)).transposed().to_4x4()
cam.location = C
sc.camera = cam
bpy.context.view_layer.update()

# ---------------------------------------------------------------- OUTER city (faded later)
b0 = snapshot()
T.prism(Pr.rrect_poly(200, 200, 1.0), 0.06, (0, 20, -0.08), M("#2a2e35", stroke=0.25, blotch=0.3), bev=0, name="ground")
for (x0, y0, x1, y1) in outer_lots():
    if math.hypot((x0 + x1) / 2 - HQ[0], (y0 + y1) / 2 - HQ[1]) < HQ_R + 2.5:
        continue
    T.prism(Pr.rrect_poly(x1 - x0 - 0.3, y1 - y0 - 0.3, 0.3), 0.18, ((x0 + x1) / 2, (y0 + y1) / 2, 0.0),
            M("#6e695e", stroke=0.28, blotch=0.3), bev=0.04, name="oblock")
    lrng = random.Random("L%.1f,%.1f" % (x0, y0))
    n = lrng.choice((2, 3, 3))
    ws = [lrng.uniform(0.8, 1.2) for _ in range(n)]
    tot = sum(ws)
    xa = x0 + 0.3
    front = y1 < DY0                       # rows in front of the district: keep low so they never bury it
    for k in range(n):
        w = (x1 - x0 - 0.6) * ws[k] / tot
        d = (y1 - y0) - 0.8
        h = HF((x0 + x1) / 2, (y0 + y1) / 2) * lrng.uniform(0.5, 1.5)
        if lrng.random() < 0.12:
            h *= 1.8
        h = max(1.2, min(13.0, h))
        if front:
            h = min(h, lrng.uniform(1.2, 3.0))
        stack = None
        if h > 6 and lrng.random() < 0.4:
            stack = (w * 0.6, d * 0.6, lrng.uniform(2, 4))
        building(xa + w / 2, (y0 + y1) / 2, w - 0.25, d, h, lrng.choice(WALLS), 1 if xa < 0 else -1, lrng,
                 full=False, stack=stack, name="ob")
        xa += w
tag(b0, "outer")
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if PHASE.get(o.name) == "outer":
        # front rows go in their own pass (drawn translucent over the district)
        wp = o.matrix_world.translation
        PHASE[o.name] = "outf" if (wp.y < DY0 - 0.5 and o.name not in ("ground",)) else "outb"

# ---------------------------------------------------------------- DISTRICT (full colour, full ink)
b0 = snapshot()
T.prism(Pr.rrect_poly(DX1 - DX0, DY1 - DY0, 0.4), 0.1, (0, 0, -0.07), M("#262a31", stroke=0.25, blotch=0.3, gloss=0.3),
        bev=0.02, name="dground")
# crisp boundary: a heavy ink kerb around the district
for (cx, cy, sx, sy) in ((0, DY0, DX1 - DX0, 0.22), (0, DY1, DX1 - DX0, 0.22), (DX0, 0, 0.22, DY1 - DY0),
                         (DX1, 0, 0.22, DY1 - DY0)):
    T.box((sx, sy, 0.2), (cx, cy, 0.0), M("#1e1c1e"), bev=0)
# lane dashes
dash = []
for x in [i * 1.1 - 12 for i in range(26)]:
    dash.append(((x, -1.1, 0.035), (0.55, 0.1, 0.02), 0))
    if x < 12:
        dash.append(((x, 4.3, 0.035), (0.55, 0.1, 0.02), 0))
to_noline(multi_box(dash, [M("#a08a4a", flat=True)], "lane", bev=0))
# the avenue continues out of the district to the HQ plaza
T.prism(Pr.rrect_poly(HQ[0] - DX1 + 0.4, 1.8, 0.1), 0.08, ((DX1 + HQ[0]) / 2, -1.1, -0.06), M("#262a31", stroke=0.25),
        bev=0, name="hq_road")
# path-safe random heights: parcels whose back edge fronts a path street stay low
PATH_STREETS_Y = [(-1.1, -13.1, 13.1), (4.3, -4.6, 4.0)]


# route geometry (must match the overlay below) - used to keep every path and pin visible
ROUTE_PTS = {"home": (-9.0, -1.1), "n2": (-4.6, -1.1), "n3": (-4.6, 4.3), "n4": (4.0, -1.1), "n5": (4.0, 4.3),
             "shop": (-0.3, -4.9), "n8": (9.0, -1.1), "boss": (12.9, -1.1), "via": (-4.6, -4.9)}
ROUTE_SEGS = [("home", "n2"), ("n2", "n4"), ("n2", "n3"), ("n3", "n5"), ("n4", "n5"), ("n4", "n8"), ("n8", "boss"),
              ("n2", "via"), ("via", "shop")]
TAN_EL = math.tan(math.radians(44))


def cap_for(x0, x1, y1):
    """Max height for a building spanning x0..x1 whose back face is at y1: in this orthographic view a
    building of height h hides ground up to h / tan(el) behind it, and a pin (about 2.4 tall) a bit more."""
    cap = 99.0
    for a, b in ROUTE_SEGS:
        (ax, ay), (bx, by) = ROUTE_PTS[a], ROUTE_PTS[b]
        lo_x, hi_x = min(ax, bx) - 0.45, max(ax, bx) + 0.45
        if hi_x < x0 or lo_x > x1:
            continue
        y_seg = max(ay, by) if abs(ax - bx) < 1e-6 else ay
        y_near = min(ay, by)
        if y_seg <= y1 - 0.2:
            continue
        dist = max(0.0, y_near - y1)
        cap = min(cap, max(1.2, dist * TAN_EL * 0.9 + 0.2))
    for k, (nx, ny) in ROUTE_PTS.items():
        mg = 3.2 if k == "home" else 0.8
        if x0 - mg < nx < x1 + mg and ny > y1:
            cap = min(cap, max(1.2, (ny - y1) * TAN_EL * 0.9 + 0.2))
    return cap


drng = random.Random(77)
for bi, (x0, x1) in enumerate(DIST_X):
    for bj, (y0, y1) in enumerate(DIST_Y):
        T.prism(Pr.rrect_poly(x1 - x0 - 0.3, y1 - y0 - 0.3, 0.3), 0.18, ((x0 + x1) / 2, (y0 + y1) / 2, 0.0),
                M("#6e695e", stroke=0.28, blotch=0.3, pattern="tiles"), bev=0.05, name="block")
        if (bi, bj) == (1, 0):
            continue                      # market plaza (shop node)
        rows = [(y0 + 0.2, y1 - 0.2)] if (y1 - y0) < 4.5 else [(y0 + 0.2, (y0 + y1) / 2), ((y0 + y1) / 2, y1 - 0.2)]
        for (ry0, ry1) in rows:
            n = drng.choice((2, 3))
            xa = x0 + 0.25
            ws = [drng.uniform(0.8, 1.2) for _ in range(n)]
            tot = sum(ws)
            for k in range(n):
                w = (x1 - x0 - 0.5) * ws[k] / tot
                h = drng.uniform(2.2, 8.5) if drng.random() > 0.15 else drng.uniform(9.0, 11.5)
                h = min(h, cap_for(xa, xa + w, ry1 - 0.1) * drng.uniform(0.9, 1.0))
                if h < 1.3:
                    h = 1.3
                stack = None
                if h > 5.5 and drng.random() < 0.45:
                    stack = (w * 0.65, (ry1 - ry0) * 0.6, drng.uniform(1.8, 3.2))
                side = 1 if (xa + w / 2) < 0 else -1
                building(xa + w / 2, (ry0 + ry1) / 2, w - 0.3, ry1 - ry0 - 0.2, h, drng.choice(WALLS), side,
                         random.Random(drng.random()), full=True, stack=stack, name="db")
                xa += w
# market plaza: tarps, crates, dumpster
mx, my = -0.3, -4.9
for (tx, ty, c) in ((mx - 2.0, my + 1.3, "#3a4a5a"), (mx + 2.0, my + 1.2, "#5a3a3a")):
    for lx in (-0.7, 0.7):
        for ly in (-0.55, 0.55):
            T.cyl(0.05, 1.3, (tx + lx, ty + ly, 0.18), M("#4a4640"), verts=6, bev=0)
    T.box((1.8, 1.5, 0.08), (tx, ty, 1.5), M(c, stroke=0.35), bev=0.03, rot=(-7, 3, 0), wonk=0.08, rng=R)
    T.box((1.3, 0.8, 0.6), (tx, ty, 0.18), M("#6a5038", pattern="plank"), bev=0.05, wonk=0.05, rng=R)
T.box((1.4, 0.8, 0.8), (mx + 3.0, my - 1.6, 0.18), M("#2f4a3a", gloss=0.3), bev=0.06, wonk=0.04, rng=R, rot=(0, 0, 8))
for (x, y) in ((mx + 2.2, my - 2.0), (mx - 3.0, my - 1.9), (-8.0, -2.4), (8.5, -2.4), (-5.7, 4.0), (5.0, 3.1)):
    for k in range(4):
        T.rock(R.uniform(0.18, 0.3), (x + R.uniform(-0.4, 0.4), y + R.uniform(-0.3, 0.3), 0.18),
               M(R.choice(("#1e1e22", "#2a2a30")), gloss=0.5), R, flat=0.85)
# eye billboard on stilts (back centre)
bbx, bby, bbz = 0.2, 7.2, 9.0
for lx in (-2.0, 0.0, 2.0):
    T.box((0.18, 0.18, bbz), (bbx + lx, bby + 0.1, 0.18), M("#3a3a3a"), bev=0.02)
T.box((5.2, 0.3, 2.6), (bbx, bby, bbz), M("#2a2a2e"), bev=0.08, wonk=0.01, rng=R)


def eye_img(u, v):
    du, dv = (u - 0.3) / 0.24, (v - 0.5) / 0.36
    r2 = du * du + dv * dv
    if r2 < 0.12:
        return 0
    if r2 < 0.35:
        return 1
    if abs(dv) < 1.0 - abs(du) ** 1.6 * 0.95 and abs(du) < 1.0:
        return 2
    return 3


Fc.tri_panel(4.8, 2.2, 15, 7, ["#120a20", "#ff2fb0", "#e8e4dc", "#2a1850"], loc=(bbx, bby - 0.17, bbz + 1.3),
             rot=(90, 0, 0), glow=1.1, seed=21, image=eye_img)
T.text("OBEY\nCOMPLY", 0.42, (bbx + 1.25, bby - 0.26, bbz + 1.6), mat=T.glow("#e8e4dc", 1.6), fnt="stencil", extrude=0.03,
       bev=0, coll=T.thin_coll())
# street furniture: lamps, cameras, a few cars, cable bundles
for x in (-10.5, -7.0, -2.2, 1.6, 6.5, 10.5):
    T.cyl(0.06, 1.8, (x, -2.25, 0.18), M("#3a3a3a"), verts=6, bev=0)
    T.box((0.28, 0.2, 0.12), (x, -1.83, 1.85), M("#c8b890"), bev=0.02)
for (x, y, hd, col) in ((-7.5, -1.55, 0, "#6a5a3a"), (1.0, -0.6, 180, "#3a4a4a"), (-4.15, 2.2, 90, "#4a4058")):
    g = T.empty("car", (x, y, 0.0), (0, 0, hd))
    T.box((1.3, 0.62, 0.36), (0, 0, 0.16), M(col, gloss=0.4), bev=0.08, wonk=0.03, rng=R).parent = g
    T.box((0.7, 0.54, 0.3), (-0.08, 0, 0.5), M("#2c3a42", gloss=0.8), bev=0.08, taper=0.2).parent = g
for (p0, p1) in (((-6.0, 1.3, 4.0), (-3.3, 1.3, 3.4)), ((2.6, 1.5, 4.6), (5.5, 1.5, 3.2)), ((-9.0, 6.0, 6.5), (-5.5, 6.2, 5.8))):
    for j in range(3):
        cable(Vector(p0) + Vector((0, j * 0.1, 0)), Vector(p1) + Vector((0, j * 0.1, 0)), 0.5 + j * 0.1)
# the HQ double helix at the route's end
hx = Helix(HQ[0], HQ[1], math.pi)
hx.build()
tag(b0, "dist")

# ---------------------------------------------------------------- overlay (crystal pins + paths): district pass
b0 = snapshot()
cam_m = cam.matrix_world.to_3x3()
T.MODE["fake"] = tuple(cam_m @ Vector((-0.5, 0.6, 1.0)))
T.MODE["name"] = "day_ui"
T.MODE["grit"] = 0.25
F = "ui"
NODES = {"home": (-9.0, -1.1), "n2": (-4.6, -1.1), "n3": (-4.6, 4.3), "n4": (4.0, -1.1), "n5": (4.0, 4.3),
         "shop": (-0.3, -4.9), "n8": (9.0, -1.1), "boss": (12.9, -1.1)}
KIND = {"home": ("home", "#ffc830"), "n2": ("fight", "#ff4a5a"), "n3": ("event", "#3ff0ff"),
        "n4": ("event", "#3ff0ff"), "n5": ("fight", "#ff4a5a"), "shop": ("shop", "#8cff2a"),
        "boss": ("boss", "#b02040"), "n8": ("fight", "#ff4a5a")}
EDGES = [("home", "n2", None), ("n2", "n4", None), ("n2", "n3", None), ("n3", "n5", None), ("n4", "n5", None),
         ("n4", "n8", None), ("n8", "boss", None), ("n2", "shop", [(-4.6, -4.9)])]
PATH_Z = 0.07


def path_band(a, b, via, hot, seed):
    pts = [Vector(a)] + [Vector(v) for v in (via or [])] + [Vector(b)]
    band = [tuple(p) for p in pts]
    a0 = Vector(band[0]); a1 = Vector(band[1]); band[0] = tuple(a0 + (a1 - a0).normalized() * 0.55)
    b0_ = Vector(band[-1]); b1 = Vector(band[-2]); band[-1] = tuple(b0_ + (b1 - b0_).normalized() * 0.55)
    dense = []
    for i in range(len(band) - 1):
        p, q = Vector(band[i]), Vector(band[i + 1])
        n = max(2, int((q - p).length / 0.3))
        for k in range(n):
            dense.append(tuple(p.lerp(q, k / n)))
    dense.append(band[-1])
    Fc.facet_ribbon(dense, 0.78 if hot else 0.62, PATH_Z, "#3ff0ff" if hot else "#e8b030", glow=1.05, seed=seed, thick=0.1)


for ei, (a, b, via) in enumerate(EDGES):
    path_band(NODES[a], NODES[b], via, hot=(a == "home"), seed=ei + 10)


def node_marker(key):
    x, y = NODES[key]
    kind, col = KIND[key]
    home = kind == "home"
    s = 1.55 if home or kind == "boss" else 1.3
    Fc.cut_gem(0.66 * s, 0.14, 0.05, n=6, loc=(x, y, 0.06), col="#c8d0d8", glow=0.9, seed=len(key), table=0.72)
    Fc.cut_gem(0.46 * s, 0.2, 0.05, n=6, loc=(x, y, 0.1), col=col, glow=1.05, seed=len(key) + 1, table=0.6)
    g = T.empty("pin", (x, y, 1.45 * s))
    g.rotation_euler = cam.matrix_world.to_euler()
    g.scale = (s, s, s)
    Fc.crystal(0.42, 0.55, 1.0, n=6, loc=(0, 0.1, 0), col=col, glow=1.05, rot=(-90, 0, 0), parent=g, seed=len(key) + 7,
               mid=0.25)
    glyph = {"home": "H", "fight": "!", "event": "?", "shop": "$", "boss": "X"}[kind]
    t = T.text(glyph, 0.62, (0, 0.24, 0.5), rot=(0, 0, 0), mat=T.flat_col("#fff8e8"), fnt="sign", extrude=0.02, bev=0,
               coll=T.thin_coll())
    t.parent = g


for k in NODES:
    node_marker(k)
tag(b0, "dist")

# ---------------------------------------------------------------- HUD (camera UI)
b0 = snapshot()
ui = Pr.ui_root(cam, depth=6.0)
T.MODE["fake"] = tuple(cam_m @ Vector((-0.45, 0.55, 1.0)))
rng = random.Random(77)
p = Pr.plaque(ui, 4.4, 0.9, (*px(270, 62), 0), col="#2e3238", trim="#8a6a3a", rng=rng, name="hud_district")
label(p, "SECTOR 9 : THE SUMP", 0.36, (0, 0.1, 0.18), "#e8e0cc", fnt="title")
label(p, "DAY 3  -  SMOG ADVISORY", 0.22, (0, -0.24, 0.18), "#8cff2a", fnt="title", lined=False)
Pr.meter(ui, 4.0, 0.3, (*px(1600, 78), 0), fill="#8cff2a", segs=10, label_txt="SUSPICION", frame="#2e3238", name="susp",
         gems=True)
eye_g = sub(ui, (*px(1340, 78), 0.3), name="eye")
Fc.cut_gem(0.4, 0.2, 0.12, n=8, loc=(0, 0, 0.1), col="#8cff2a", glow=1.1, parent=eye_g, seed=5)
lg = sub(ui, (*px(190, 985), 0), name="legend")
Pr.plaque(lg, 3.1, 1.3, (0, 0, 0), col="#2a2c30", trim="#6a6258", rng=rng, bolts=False)
for i, (col, name) in enumerate((("#ff4a5a", "FIGHT"), ("#3ff0ff", "EVENT"), ("#8cff2a", "MARKET"), ("#b02040", "CORP HQ"))):
    gx, gy = -0.95 + (i % 2) * 1.5, 0.25 - (i // 2) * 0.52
    Fc.crystal(0.16, 0.2, 0.24, n=6, loc=(gx, gy + 0.02, 0.2), col=col, glow=1.1, rot=(-90, 0, 0), parent=lg)
    label(lg, name, 0.2, (gx + 0.28, gy - 0.01, 0.14), "#e8e0cc", fnt="title", align="LEFT", lined=False)
# HQ label beside the helix top
bpy.context.view_layer.update()
top = Vector((HQ[0], HQ[1], hx.top_z()))
tp = world_to_camera_view(sc, cam, top)
hx_px, hy_px = tp.x * 1920, (1 - tp.y) * 1080
g = sub(ui, (*px(hx_px - 250, hy_px + 190), 0.3), rot=(0, 0, -3), name="hq_lbl")
Pr.plaque(g, 1.9, 0.72, (0, 0, 0), col="#a0201e", trim="#e8c030", rng=rng, bolts=False)
label(g, "CORP HQ", 0.32, (0, -0.02, 0.18), PAL["cream"], fnt="title", thin=True)
Fc.crystal(0.14, 0.2, 0.3, n=4, loc=(1.15, 0, 0.2), col="#ff4a5a", glow=1.2, rot=(0, 0, 90), parent=g)
# YOU ARE HERE banner: screen-space plaque over the home pin (never hidden by buildings)
hp = world_to_camera_view(sc, cam, Vector((NODES["home"][0], NODES["home"][1], 3.4)))
bn = sub(ui, (*px(hp.x * 1920, (1 - hp.y) * 1080 - 70), 0.4), scale=0.8, name="banner")
Pr.plaque(bn, 3.2, 0.66, (0, 0, 0), col="#2e3238", trim="#6a6258", rng=random.Random(8), bolts=False)
label(bn, "YOU ARE HERE", 0.34, (0, -0.02, 0.16), "#3ff0ff", fnt="title", lined=False)
for k in (-1, 1):
    Fc.crystal(0.1, 0.14, 0.14, n=4, loc=(k * 1.78, 0, 0.2), col="#3ff0ff", glow=1.1, rot=(0, 90, 0), parent=bn)
Fc.crystal(0.14, 0.05, 0.26, n=4, loc=(0, -0.5, 0.2), col="#3ff0ff", glow=1.1, rot=(-90, 0, 0), parent=bn)
tag(b0, "hud")
T.MODE["name"], T.MODE["grit"] = "day", 0.8

# ---------------------------------------------------------------- meta: HQ screen bbox (for the close-up)
bpy.context.view_layer.update()
pts = []
for z in (0.0, hx.top_z()):
    for a in range(12):
        ang = a / 12 * math.tau
        v = world_to_camera_view(sc, cam, Vector((HQ[0] + 4.2 * math.cos(ang), HQ[1] + 4.2 * math.sin(ang), z)))
        pts.append((v.x * 1920, (1 - v.y) * 1080))
meta = dict(hq_bbox=[min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)],
            hq_top_px=[hx_px, hy_px])
json.dump(meta, open(os.path.join(OUT_DIR, "meta.json"), "w"), indent=2)
print("META", meta)

# ---------------------------------------------------------------- passes
ls_main = sc.view_layers[0].freestyle_settings.linesets[0].linestyle


def set_pass(name):
    for o in bpy.data.objects:
        ph = PHASE.get(o.name)
        if ph is None:
            continue
        o.hide_render = (ph != name)


for name in ("outb", "outf", "dist", "hud"):
    set_pass(name)
    if name in ("outb", "outf"):
        ls_main.thickness = 1.3
        ls_main.color = T.lin("#6a6458")[:3]
    else:
        ls_main.thickness = 2.6
        ls_main.color = T.lin(T.INK)[:3]
    T.render(sc, os.path.join(OUT_DIR, "pass_%s.png" % name))
