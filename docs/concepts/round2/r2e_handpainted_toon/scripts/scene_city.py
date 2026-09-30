"""01-03 city: a chunky hand-painted cyberpunk block on a floating diorama island, with the
node-and-path overlay lying on the street plane.

usage: blender -b --factory-startup --python scene_city.py -- <out.png> <day|night|alarm> [samples] [hud 0/1]
"""
import os
import sys
import math
import random
import bmesh
import bpy
from mathutils import Vector
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tt_lib as T
import tt_props as Pr
from tt_props import PAL, sub, label, px

args = T.arg_list()
OUT = args[0] if args else os.path.join(T.OUT_ROOT, "stills", "01_city_day.png")
MODE = args[1] if len(args) > 1 else "day"
SAMPLES = int(args[2]) if len(args) > 2 else 32
HUD = (args[3] != "0") if len(args) > 3 else True
OVERLAY = HUD   # a background plate (combat / shop) drops the HUD and the node overlay
NIGHT = MODE in ("night", "alarm")
ALARM = MODE == "alarm"

BG = {"day": "#3f5566", "night": "#141a2e", "alarm": "#2b0f24"}[MODE]
sc = T.reset()
T.MODE["name"] = MODE
T.setup_render(sc, samples=SAMPLES, bg=BG, line=2.6, transparent=True)
T.compositor(sc, bloom=(0.9, 1.4, 8) if NIGHT else None, kuwahara=int(os.environ.get("R2E_KUW", "0")))
world_bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
world_bg.inputs[1].default_value = {"day": 1.0, "night": 0.35, "alarm": 0.35}[MODE]

CAM_LOC, CAM_TGT = (0.0, -28.5, 23.0), (0.0, 1.6, 1.6)
LENS = 28.5
if not HUD:   # background plate for combat / shop: a closer, lower look into the streets
    CAM_LOC, CAM_TGT, LENS = (-1.0, -17.0, 8.5), (0.5, 3.0, 3.2), 26
cam = T.camera(CAM_LOC, CAM_TGT, lens=LENS)
bpy.context.view_layer.update()

if MODE == "day":
    T.sun(2.7, "#fff0d2", rot=(50, 0, -30), angle=4)
elif MODE == "night":
    T.sun(1.5, "#8aa2ff", rot=(55, 0, 40), angle=4)
else:
    T.sun(1.2, "#c07aff", rot=(55, 0, 40), angle=4)

R = random.Random(2077)


def M(h, **kw):
    return T.paint(h, **kw)


# ---------------------------------------------------------------- window glass
if NIGHT:
    WIN_MATS = [M("#1c2336"), T.glow("#ffc56b", 2.2), T.glow("#6fe6ff", 2.0), T.glow("#ff7ac0", 2.0), T.glow("#fff0c8", 1.8)]
    WIN_W = [0.22, 0.36, 0.18, 0.12, 0.12]
    if ALARM:
        WIN_MATS = [M("#1c1626"), T.glow("#ffb36b", 1.6), T.glow("#ff3b4e", 2.2), T.glow("#ff7ac0", 1.6), T.glow("#fff0c8", 1.2)]
        WIN_W = [0.55, 0.15, 0.2, 0.05, 0.05]
else:
    WIN_MATS = [M("#2e6f86", gloss=0.7, stroke=0.25), M("#3d8aa0", gloss=0.7, stroke=0.25)]
    WIN_W = [0.6, 0.4]


def pick_win():
    x = R.random()
    acc = 0
    for i, w in enumerate(WIN_W):
        acc += w
        if x <= acc:
            return i
    return 0


def multi_box(parts, mats, name, parent=None, bev=0.025):
    """One object made of many boxes (center, size, mat_idx) -> cheap windows / dashes."""
    bm = bmesh.new()
    for (c, s, mi) in parts:
        r = bmesh.ops.create_cube(bm, size=1.0)
        for v in r["verts"]:
            v.co = Vector((v.co.x * s[0] + c[0], v.co.y * s[1] + c[1], v.co.z * s[2] + c[2]))
        faces = {f for v in r["verts"] for f in v.link_faces}
        for f in faces:
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


# ---------------------------------------------------------------- island + streets
def blob(rx, ry, n, amp, rng, cx=0.0, cy=0.0):
    pts = []
    for i in range(n):
        a = i / n * math.tau
        k = 1 + rng.uniform(-amp, amp) + 0.04 * math.sin(a * 5 + 1.3)
        pts.append((cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    return pts


rng_i = random.Random(5)
isl = blob(15.2, 10.4, 72, 0.035, rng_i, cy=0.2)
T.prism(isl, 1.3, (0, 0, -1.55), M("#7a4e33", streak_axis=2, streak=5, stroke=0.25), bev=0.12, name="earth")
T.prism([(x * 0.93, y * 0.9) for x, y in isl], 0.9, (0, 0, -2.35), M("#5e3b2a", stroke=0.25), bev=0.12, name="earth2")
T.prism([(x * 0.7, y * 0.66) for x, y in isl], 0.8, (0, 0, -3.0), M("#4b2f24"), bev=0.12, name="earth3")
T.prism([(x * 1.012 + rng_i.uniform(-0.1, 0.1), y * 1.012 + rng_i.uniform(-0.1, 0.1)) for x, y in isl], 0.3,
        (0, 0, -0.3), M("#65a53b", stroke=0.28, blotch=0.28, streak_axis=0), bev=0.08, name="grass")
# strata rocks on the island side
for i in range(26):
    a = R.uniform(0, math.tau)
    T.rock(R.uniform(0.35, 0.7), (math.cos(a) * 15.2 * 0.99, math.sin(a) * 10.4 * 0.99 + 0.2, R.uniform(-1.6, -0.7)),
           M("#8e8a86"), R, flat=0.7)
# asphalt slab and raised pavement blocks
XS = [(-12.3, -5.4), (-3.8, 3.2), (4.8, 12.3)]
YS = [(-7.8, -2.0), (-0.2, 3.6), (5.0, 7.8)]
T.prism(Pr.rrect_poly(25.6, 16.6, 1.2), 0.08, (0, 0.0, -0.06), M("#3b3f4d", stroke=0.2, blotch=0.22), bev=0.03, name="asphalt")
BLOCKS = {}
for i, (x0, x1) in enumerate(XS):
    for j, (y0, y1) in enumerate(YS):
        w, d = x1 - x0 - 0.3, y1 - y0 - 0.3
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        BLOCKS[(i, j)] = (cx, cy, w, d)
        T.prism(Pr.rrect_poly(w, d, 0.45), 0.18, (cx, cy, 0.0), M("#b9ad9a", stroke=0.22, blotch=0.2, pattern="tiles"), bev=0.05, name="block")
# lane dashes (flat painted, no ink)
dash = []
for x in [i * 1.1 - 12 for i in range(23)]:
    if not any(a - 0.2 < x < b + 0.2 for a, b in ((-5.4, -3.8), (3.2, 4.8))):
        dash.append(((x, -1.1, 0.035), (0.55, 0.1, 0.02), 0))
        dash.append(((x, 4.3, 0.035), (0.55, 0.1, 0.02), 0))
for y in [i * 1.1 - 7.6 for i in range(15)]:
    if not any(a - 0.2 < y < b + 0.2 for a, b in ((-2.0, -0.2), (3.6, 5.0))):
        dash.append(((-4.6, y, 0.035), (0.1, 0.55, 0.02), 0))
        dash.append(((4.0, y, 0.035), (0.1, 0.55, 0.02), 0))
o = multi_box(dash, [M("#e8c060", flat=True)], "lane", bev=0)
noline = T.noline_coll()
sc.collection.objects.unlink(o); noline.objects.link(o)

# grass tufts, flowers and rocks on the rim
ga, gb = M("#86c94a"), M("#4d8c2c")
bush_m = [M("#5aa43a", stroke=0.3), M("#6fbd46", stroke=0.3), M("#4a8f35", stroke=0.3)]
for i in range(70):
    a = R.uniform(0, math.tau)
    k = R.uniform(0.9, 0.985)
    x, y = math.cos(a) * 15.0 * k, math.sin(a) * 10.2 * k + 0.2
    if abs(x) < 13.0 and abs(y) < 8.5:
        continue
    T.rock(R.uniform(0.3, 0.55), (x, y, 0.05), R.choice(bush_m), R, flat=0.75)
for i in range(120):
    a = R.uniform(0, math.tau)
    k = R.uniform(0.9, 0.99)
    x, y = math.cos(a) * 15.0 * k, math.sin(a) * 10.2 * k + 0.2
    if abs(x) < 12.9 and abs(y - 0) < 8.4:
        continue
    T.tuft((x, y, 0.0), R, ga, gb, s=R.uniform(1.2, 2.0), blades=6)
for i in range(20):
    a = R.uniform(0, math.tau)
    x, y = math.cos(a) * 14.4, math.sin(a) * 9.8 + 0.2
    if abs(x) < 12.9 and abs(y) < 8.4:
        continue
    T.rock(R.uniform(0.2, 0.42), (x, y, 0.0), M("#a9aeb3"), R)
fl = M("#d65ad6", flat=True)
for i in range(30):
    a = R.uniform(0, math.tau)
    x, y = math.cos(a) * 14.6, math.sin(a) * 9.9 + 0.2
    if abs(x) < 12.9 and abs(y) < 8.4:
        continue
    T.cyl(0.12, 0.06, (x, y, 0.02), fl, verts=5, bev=0)
# drain pipes sticking out of the island side
for a in (-2.1, -1.2, 3.6):
    x, y = math.cos(a) * 14.9, math.sin(a) * 10.1 + 0.2
    rot_z = math.degrees(a) + 90
    T.cyl(0.35, 1.2, (x, y, -0.7), M(PAL["steel"], gloss=0.5), verts=14, bev=0.04, rot=(90, 0, rot_z), origin_bottom=False)
    T.cyl(0.45, 0.2, (x + math.cos(a) * 0.6, y + math.sin(a) * 0.6, -0.7), M(PAL["iron"]), verts=14, bev=0.04,
          rot=(90, 0, rot_z), origin_bottom=False)
    if NIGHT:
        T.cyl(0.27, 0.04, (x + math.cos(a) * 0.7, y + math.sin(a) * 0.7, -0.7), T.glow("#6bff8a", 2.5), verts=12, bev=0,
              rot=(90, 0, rot_z), origin_bottom=False)


# ---------------------------------------------------------------- buildings
SIGN_WORDS = ["BAR", "24H", "EAT", "RAM", "ZAP", "HOT", "NET", "OPEN"]
NEON = ["#ff4fb8", "#4ff0ff", "#ffd24f", "#9dff4f", "#b98cff"]
LIGHTS_BUDGET = [0]


def neon_mat(c, s=4.0):
    if NIGHT:
        if ALARM and R.random() < 0.5:
            c = "#ff3b4e"
        return T.glow(c, s)
    return M(c, gloss=0.4, stroke=0.1)


ROOFS = ["#6d4a3a", "#3f6f7a", "#9a3f3a", "#4a4060", "#7a6a50", "#2f5a4a"]


def building(cx, cy, w, d, h, wall, trim="#e6c28f", roof=None, floors=None, sign=None, side=None,
             roof_props=True, tilt=True, awning=None, win_cols=None, name="bld"):
    rng = random.Random(int(cx * 100 + cy * 37 + h * 11))
    roof = roof or rng.choice(ROOFS)
    body = T.box((w, d, h), (cx, cy, 0.18), M(wall, seed=rng.randint(0, 99), streak_axis=rng.choice((0, 2)),
                                              pattern=rng.choice(("brick", "brick", "plank", None))),
                 bev=0.12, wonk=0.02, rng=rng, taper=rng.uniform(-0.04, 0.08), name=name)
    if tilt:
        body.rotation_euler = (math.radians(rng.uniform(-1.8, 1.8)), math.radians(rng.uniform(-1.8, 1.8)),
                               math.radians(rng.uniform(-2.5, 2.5)))
    kids = []
    fl_h = 1.15
    nfl = int((h - 0.4) / fl_h)
    # trim band per floor
    parts = []
    for k in range(1, nfl + 1):
        z = k * fl_h - 0.1
        if z > h - 0.4:
            break
        parts.append(((0, 0, z), (w + 0.1, d + 0.1, 0.12), 0))
    parts.append(((0, 0, h + 0.08), (w + 0.25, d + 0.25, 0.26), 1))
    multi_box(parts, [M(trim, streak_axis=0), M(roof, stroke=0.2)], name + "_trim", parent=body, bev=0.03)
    # windows on front face and on the side facing the centre line
    side = side if side is not None else (1 if cx < 0 else -1)
    wparts = []
    cols = win_cols or max(1, int(w / 0.75))
    scol = max(1, int(d / 0.75))
    for k in range(nfl):
        z = 0.35 + k * fl_h + 0.35
        if z + 0.3 > h - 0.2:
            break
        if awning and k == 0:
            continue
        for c in range(cols):
            x = -w / 2 + (c + 0.5) * w / cols
            wparts.append(((x, -d / 2 - 0.02, z), (0.34, 0.12, 0.46), pick_win()))
        for c in range(scol):
            y = -d / 2 + (c + 0.5) * d / scol
            wparts.append(((side * (w / 2 + 0.02), y, z), (0.12, 0.34, 0.46), pick_win()))
    if wparts:
        multi_box(wparts, WIN_MATS, name + "_win", parent=body, bev=0.02)
    if awning:
        a = T.box((w * 0.85, 0.7, 0.14), (0, -d / 2 - 0.3, 1.25), M(awning, streak_axis=0), bev=0.04, rot=(-16, 0, 0),
                  wonk=0.03, rng=rng)
        a.parent = body
        door = T.box((0.7, 0.1, 1.0), (w * 0.2, -d / 2 - 0.02, 0.0), M("#3d2a26"), bev=0.03)
        door.parent = body
        glow_front = T.box((w * 0.45, 0.08, 0.6), (-w * 0.18, -d / 2 - 0.03, 0.3),
                           T.glow("#ffcf7a", 1.6) if NIGHT else M("#3d8aa0", gloss=0.6), bev=0.02)
        glow_front.parent = body
    if sign:
        word, col = sign
        sz = 0.42
        board_h = len(word) * sz * 1.05 + 0.3
        z0 = min(h - board_h - 0.1, 1.6)
        sx = side * (w / 2 + 0.28)
        b = T.box((0.12, 0.6, board_h), (sx, -d / 2 + 0.5, z0), M("#2c2433"), bev=0.04)
        b.parent = body
        t = T.text("\n".join(word), sz, (sx, -d / 2 + 0.5 - 0.0, z0 + board_h / 2),
                   rot=(90, 0, 90 * side if side > 0 else -90), mat=neon_mat(col), fnt="title", extrude=0.04, bev=0,
                   coll=T.thin_coll())
        t.rotation_euler = (math.radians(90), 0, math.radians(90 * side))
        t.location.x = sx + side * 0.09
        t.parent = body
        if NIGHT and LIGHTS_BUDGET[0] < 14:
            LIGHTS_BUDGET[0] += 1
            T.point((cx + sx + side * 0.8, cy - d / 2 + 0.5, z0 + board_h / 2 + 0.18), "#ff3b4e" if ALARM else col, 160, 0.4)
    if roof_props:
        n = rng.randint(1, 3)
        for i in range(n):
            kind = rng.choice(("ac", "ac", "tank", "ant", "vent"))
            x = rng.uniform(-w / 2 + 0.5, w / 2 - 0.5)
            y = rng.uniform(-d / 2 + 0.5, d / 2 - 0.5)
            zt = h + 0.2
            if kind == "ac":
                o = T.box((0.7, 0.55, 0.45), (x, y, zt), M("#b7c1c8", gloss=0.3), bev=0.05, wonk=0.04, rng=rng)
                o.parent = body
                f = T.cyl(0.18, 0.05, (x, y, zt + 0.45), M(PAL["iron"]), verts=10, bev=0.01)
                f.parent = body
            elif kind == "tank":
                for lx in (-0.25, 0.25):
                    for ly in (-0.25, 0.25):
                        T.cyl(0.04, 0.5, (x + lx, y + ly, zt), M(PAL["wood_d"]), verts=6, bev=0).parent = body
                T.cyl(0.42, 0.7, (x, y, zt + 0.5), M("#8a5a36", streak_axis=2, streak=18), verts=14, bev=0.05).parent = body
                T.cyl(0.5, 0.3, (x, y, zt + 1.2), M("#b8413a"), r2=0.05, verts=14, bev=0.03).parent = body
            elif kind == "ant":
                T.cyl(0.04, 1.4, (x, y, zt), M(PAL["steel"]), verts=6, bev=0).parent = body
                T.cyl(0.1, 0.12, (x, y, zt + 1.4), T.glow("#ff3b4e", 5) if NIGHT else M("#e8483c"), verts=8, bev=0.02).parent = body
            else:
                T.cyl(0.16, 0.6, (x, y, zt), M("#8c969e", gloss=0.4), verts=10, bev=0.03).parent = body
                T.cyl(0.24, 0.12, (x, y, zt + 0.6), M(PAL["iron"]), verts=10, bev=0.02).parent = body
    # corner drain pipe
    px_ = -side * (w / 2 + 0.06)
    T.cyl(0.07, h - 0.1, (px_, -d / 2 + 0.06, 0.0), M(PAL["steel"], gloss=0.4), verts=8, bev=0).parent = body
    for zz in (0.8, h * 0.5, h - 0.6):
        T.box((0.18, 0.18, 0.08), (px_, -d / 2 + 0.06, zz), M(PAL["iron"]), bev=0.01).parent = body
    # balconies on taller buildings
    if h > 3.9 and rng.random() < 0.7:
        for k in range(1, nfl - 1, 2):
            z = k * fl_h + 0.05
            bx_ = rng.choice((-1, 1)) * w * 0.22
            T.box((w * 0.42, 0.45, 0.1), (bx_, -d / 2 - 0.22, z), M(trim), bev=0.02).parent = body
            T.box((w * 0.42, 0.06, 0.32), (bx_, -d / 2 - 0.43, z + 0.1), M(PAL["iron"]), bev=0.01).parent = body
            if rng.random() < 0.6:
                T.cyl(0.13, 0.22, (bx_ + w * 0.12, -d / 2 - 0.25, z + 0.1), M("#c0623a"), verts=8, bev=0.02).parent = body
                T.rock(0.16, (bx_ + w * 0.12, -d / 2 - 0.25, z + 0.38), M("#5aa43a"), rng, flat=0.9).parent = body
    return body


def cable(p0, p1, sag=0.6, col="#2a2630", flags=None):
    """Sagging cable between two points (curve -> mesh), optional pennant flags."""
    import bpy as _b
    cu = _b.data.curves.new("cable", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = 0.03
    cu.bevel_resolution = 1
    sp = cu.splines.new("POLY")
    n = 14
    sp.points.add(n - 1)
    pts = []
    for i in range(n):
        t = i / (n - 1)
        p = Vector(p0).lerp(Vector(p1), t)
        p.z -= sag * 4 * t * (1 - t)
        sp.points[i].co = (p.x, p.y, p.z, 1)
        pts.append(p)
    o = _b.data.objects.new("cable", cu)
    T.link_obj(o)
    cu.materials.append(M(col))
    if flags:
        for i in range(1, n - 1):
            p = pts[i]
            c = flags[i % len(flags)]
            tri = T.prism([(-0.14, 0), (0.14, 0), (0, -0.32)], 0.02, (p.x, p.y, p.z), M(c, toplight=0.0), bev=0,
                          rot=(90, 0, 0))
    return o


def fill_block(key, specs):
    cx, cy, w, d = BLOCKS[key]
    for sp in specs:
        fx, fy, fw, fd, h, wall = sp[:6]
        kw = sp[6] if len(sp) > 6 else {}
        building(cx + fx * w / 2, cy + fy * d / 2, fw, fd, h, wall, **kw)


# back row (tallest)
fill_block((0, 2), [(-0.55, 0.1, 2.2, 1.9, 7.2, "#c9744a", {"sign": ("HOT", NEON[0]), "trim": "#f0cf98"}),
                    (0.35, 0.05, 2.6, 2.0, 5.2, "#4f8a8f", {"sign": ("NET", NEON[1]), "roof": "#3a3048"}),
                    ])
fill_block((1, 2), [(-0.6, 0.05, 2.0, 2.0, 4.6, "#8c5aa8", {"sign": ("ZAP", NEON[2])}),
                    (0.45, 0.05, 2.6, 2.0, 6.0, "#d2a65a", {"roof": "#5a3a4a"})])
# middle row
fill_block((0, 1), [(-0.55, 0.0, 2.4, 2.6, 3.0, "#5d7fa6", {"awning": "#e0493f", "roof_props": False}),
                    (0.45, 0.2, 2.6, 2.2, 4.2, "#d88b4f", {"sign": ("BAR", NEON[0]), "side": 1})])
fill_block((1, 1), [(-0.5, 0.1, 2.6, 2.4, 3.6, "#e2b56a", {"awning": "#2fb3b0", "sign": ("EAT", NEON[3]), "side": -1}),
                    (0.5, 0.0, 2.4, 2.8, 5.0, "#7b5ea8", {"sign": ("RAM", NEON[1]), "side": 1})])
fill_block((2, 1), [(-0.45, 0.05, 2.8, 2.6, 3.4, "#b8534a", {"awning": "#f2b534", "side": -1}),
                    (0.5, 0.25, 2.2, 1.8, 2.4, "#6f9a5a", {"roof_props": False, "side": -1})])
# front row (low, so the avenue stays visible)
fill_block((0, 0), [(0.45, 0.0, 2.8, 2.6, 2.2, "#e5c27a", {"awning": "#e0493f", "roof_props": False, "side": 1}),
                    (-0.55, 0.3, 2.2, 2.2, 3.0, "#5d8fa6", {"sign": ("24H", NEON[1]), "side": 1})])
fill_block((2, 0), [(-0.45, 0.2, 3.0, 2.6, 2.4, "#8a6fb3", {"awning": "#9ee03a", "side": -1, "sign": ("OPEN", NEON[3])}),
                    (0.55, 0.0, 2.2, 2.2, 3.2, "#cf7d52", {"side": -1})])

# ---------------------------------------------------------------- landmarks
# 1. the corp spire (back right)
cx, cy, w, d = BLOCKS[(2, 2)]
hx, hy = cx + 0.6, cy + 0.2
tiers = [(3.6, 2.3, 2.8, "#5b3f8f"), (2.8, 1.9, 2.5, "#6a4ba3"), (2.0, 1.5, 2.1, "#7a58b8")]
z = 0.18
for i, (tw, td, th, c) in enumerate(tiers):
    b = T.box((tw, td, th), (hx, hy, z), M(c, seed=i, gloss=0.2), bev=0.12, taper=0.06, wonk=0.01, rng=R)
    band = T.box((tw * 0.96 + 0.28, td * 0.96 + 0.28, 0.28), (hx, hy, z + th - 0.05), M("#e2b24a", gloss=0.6), bev=0.06)
    # vertical glass strips
    strips = []
    for k in range(int(tw / 0.55)):
        x = -tw / 2 + (k + 0.5) * tw / int(tw / 0.55)
        strips.append(((x, -td / 2 - 0.01, th * 0.5), (0.22, 0.1, th * 0.78), 1 if NIGHT and R.random() < 0.7 else 0))
    multi_box(strips, [M("#2d5e7a", gloss=0.8), T.glow("#8ff0ff" if not ALARM else "#ff5f73", 1.8)], "hq_glass", parent=b)
    b.location = (hx, hy, z)
    z += th + 0.2
crown = T.cyl(0.9, 1.4, (hx, hy, z), M("#e2b24a", gloss=0.8), r2=0.12, verts=8, bev=0.06)
T.cyl(0.06, 0.9, (hx, hy, z + 1.3), M(PAL["steel"]), verts=6, bev=0)
T.cyl(0.18, 0.2, (hx, hy, z + 2.2), T.glow("#ff3b4e", 6) if NIGHT else M("#e8483c"), verts=10, bev=0.03)
# floating halo ring + logo
halo_z = z - 1.0
for o in Pr.ring(1.9, 2.25, 0.24, (hx, hy, halo_z), T.glow("#ff5fd0", 3.2) if (NIGHT and not ALARM) else
                 (T.glow("#ff3b4e", 3.5) if ALARM else M("#e2b24a", gloss=0.8)), None, bev=0.05, segs=28):
    o.rotation_euler = (math.radians(8), 0, 0)
logo = sub(None, (hx, hy - 1.38, 4.4), rot=(90, 0, 0), name="logo")
T.cyl(0.62, 0.14, (0, 0, 0), M("#1f1a2e"), verts=24, bev=0.03).parent = logo
lt = T.text("O", 0.8, (0, 0.0, 0.14), rot=(0, 0, 0), mat=neon_mat("#ff5fd0", 4) if NIGHT else M("#e2b24a", gloss=0.6),
            fnt="title", extrude=0.05, bev=0)
lt.parent = logo
plq = T.box((2.4, 0.2, 0.6), (hx, hy - 1.32, 0.9), M("#1f1a2e"), bev=0.05)
T.text("ORBYT", 0.44, (hx, hy - 1.44, 1.2), mat=neon_mat("#ff5fd0", 3.5) if NIGHT else M("#e2b24a", gloss=0.6),
       fnt="title", extrude=0.04, bev=0, coll=T.thin_coll())
if NIGHT:
    T.point((hx, hy - 3, 3.0), "#ff3b4e" if ALARM else "#ff5fd0", 400, 1.0)
    T.point((hx, hy - 2.0, halo_z), "#ff3b4e" if ALARM else "#ff5fd0", 250, 1.0)

# 2. noodle bar with a giant bowl on the roof (front left)
cx, cy, w, d = BLOCKS[(0, 0)]
nb = building(cx - 2.2, cy - 0.9, 2.6, 2.0, 1.9, "#d8544a", trim="#f2d49a", roof="#7a3a2e", roof_props=False,
              awning="#f2b534", side=1, tilt=False, name="noodle")
bx, by, bz = cx - 2.2, cy - 0.9, 2.35
T.cyl(1.05, 0.8, (bx, by, bz), M("#fff0d6"), r2=1.45, verts=28, bev=0.06)
T.cyl(1.46, 0.16, (bx, by, bz + 0.62), M("#e0493f"), verts=28, bev=0.05)
T.cyl(1.3, 0.1, (bx, by, bz + 0.72), M("#f2c14a", stroke=0.3), verts=28, bev=0.03)
for k, (dx, a) in enumerate(((-0.25, 18), (0.25, 26))):
    T.box((0.12, 0.12, 2.6), (bx + dx, by + 0.2, bz + 0.4), M("#a86a3a", streak_axis=2, streak=20), bev=0.03,
          rot=(-10, a, 0))
if not ALARM:
    for k in range(3):
        s = T.cyl(0.28 - k * 0.05, 0.25, (bx - 0.4 + k * 0.35, by, bz + 1.2 + k * 0.45), M("#f4f1ea", toplight=0.1),
                  verts=10, bev=0.08)
T.box((2.1, 0.14, 0.55), (bx, by - 1.42, bz + 0.12), M("#2c2433"), bev=0.04, rot=(-8, 0, 0))
T.text("NOODLE", 0.42, (bx, by - 1.52, bz + 0.4), mat=neon_mat("#ffd24f", 3.5), fnt="title", extrude=0.04, bev=0,
       coll=T.thin_coll(), rot=(82, 0, 0))

# 3. satellite dish (middle left roof)
cx, cy, w, d = BLOCKS[(0, 1)]
dx, dy, dz = cx - 1.7, cy + 0.2, 3.35
T.cyl(0.18, 0.8, (dx, dy, dz), M(PAL["steel"]), verts=8, bev=0.03)
dish = T.cyl(1.3, 0.45, (dx, dy - 0.2, dz + 1.1), M("#e9e4d8", gloss=0.4), r2=0.35, verts=24, bev=0.05,
             rot=(-40, 0, 20), origin_bottom=False)
T.cyl(0.05, 1.0, (dx, dy - 0.2, dz + 1.1), M(PAL["iron"]), verts=6, bev=0, rot=(-40, 0, 20))

# 4. billboard (back centre)
cx, cy, w, d = BLOCKS[(1, 2)]
bbx, bby = cx + 1.3, cy + 0.2
for lx in (-1.2, 1.2):
    T.box((0.14, 0.14, 1.4), (bbx + lx, bby, 6.2), M(PAL["iron"]), bev=0.02)
T.box((3.4, 0.25, 1.9), (bbx, bby, 7.4), M(PAL["iron"]), bev=0.06)
scr = T.box((3.1, 0.12, 1.6), (bbx, bby - 0.14, 7.55), T.glow("#2a1a4a", 1.0) if NIGHT else M("#2a1a4a"), bev=0.02)
T.text("DREAM\nNET", 0.52, (bbx - 0.35, bby - 0.22, 8.35), mat=neon_mat("#4ff0ff", 4.0), fnt="title", extrude=0.03,
       bev=0, coll=T.thin_coll())
eye = T.cyl(0.42, 0.06, (bbx + 1.0, bby - 0.22, 8.35), neon_mat("#ff4fb8", 4.0), verts=16, bev=0, rot=(90, 0, 0),
            origin_bottom=False)
eye.scale = (1.0, 0.6, 1.0)
T.cyl(0.16, 0.08, (bbx + 1.0, bby - 0.26, 8.35), M("#1a1020"), verts=12, bev=0, rot=(90, 0, 0), origin_bottom=False)
if NIGHT:
    T.point((bbx, bby - 2.5, 8.0), "#ff3b4e" if ALARM else "#4ff0ff", 250, 1.0)

# 5. water tower (middle right)
cx, cy, w, d = BLOCKS[(2, 1)]
wx, wy = cx + 2.1, cy + 0.9
for lx in (-0.45, 0.45):
    for ly in (-0.45, 0.45):
        T.cyl(0.07, 2.0, (wx + lx, wy + ly, 2.6), M(PAL["wood_d"]), verts=6, bev=0)
T.cyl(0.8, 1.2, (wx, wy, 4.5), M("#8a5a36", streak_axis=2, streak=24, stroke=0.3), verts=18, bev=0.06)
T.cyl(0.95, 0.6, (wx, wy, 5.7), M("#2fb3b0"), r2=0.1, verts=18, bev=0.04)
for zz in (4.7, 5.4):
    T.cyl(0.83, 0.08, (wx, wy, zz), M(PAL["iron"]), verts=18, bev=0.01)

# 6. black-market plaza (front centre): tents, crates, lanterns, tree
cx, cy, w, d = BLOCKS[(1, 0)]
for k, (tx, ty, c) in enumerate(((cx - 1.7, cy + 1.1, "#9a5ee0"), (cx + 1.8, cy + 1.0, "#e0493f"))):
    for lx in (-0.7, 0.7):
        for ly in (-0.55, 0.55):
            T.cyl(0.05, 1.3, (tx + lx, ty + ly, 0.18), M(PAL["wood_d"]), verts=6, bev=0)
    roof = T.cyl(1.25, 0.7, (tx, ty, 1.45), M(c, stroke=0.3), r2=0.08, verts=4, bev=0.05, rot=(0, 0, 45))
    roof.scale = (1.0, 0.8, 1.0)
    T.box((1.4, 0.8, 0.6), (tx, ty, 0.18), M("#a86a3a", streak_axis=0, streak=18), bev=0.05, wonk=0.04, rng=R)
    if NIGHT:
        T.cyl(0.13, 0.22, (tx, ty - 0.6, 1.25), T.glow("#ffb54f", 4), verts=8, bev=0.02)
for k in range(5):
    T.box((0.5, 0.5, 0.45), (cx + 3.2 + R.uniform(-0.3, 0.3), cy - 1.6 + k * 0.1, 0.18 + (0.45 if k == 4 else 0)),
          M("#b07a44", streak_axis=0, streak=16), bev=0.04, wonk=0.05, rng=R, rot=(0, 0, R.uniform(-20, 20)))


def tree(x, y, s=1.0):
    T.cyl(0.14 * s, 1.1 * s, (x, y, 0.18), M("#7a4e2e", streak_axis=2, streak=14), verts=8, bev=0.03, wonk=0.1, rng=R)
    for k in range(3):
        T.rock(0.65 * s - k * 0.12, (x + R.uniform(-0.2, 0.2), y + R.uniform(-0.2, 0.2), 1.25 * s + k * 0.45 * s),
               M("#5aa43a" if k != 1 else "#6fbd46", stroke=0.3), R, flat=0.85)


tree(cx - 3.2, cy - 1.8, 1.0)
tree(cx + 3.3, cy + 1.3, 0.9)
cx2, cy2, w2, d2 = BLOCKS[(1, 1)]
tree(cx2 + 0.1, cy2 - 1.2, 0.8)

# ---------------------------------------------------------------- cables and bunting
cx, cy, w, d = BLOCKS[(1, 0)]
cable((cx - 1.7, cy + 1.1, 2.05), (cx + 1.8, cy + 1.0, 2.05), 0.35, flags=["#f2b534", "#e8483c", "#27b5ad", "#fff0cf"])
cable((-6.06, 1.3, 4.0), (-3.28, 1.3, 3.4), 0.5)
cable((-6.06, 1.0, 3.6), (-3.28, 1.0, 3.0), 0.4, flags=["#ff4fb8", "#4ff0ff", "#ffd24f"])
cable((2.57, 1.5, 4.6), (5.53, 1.5, 3.2), 0.5)
if NIGHT:
    for (x, y, z) in ((-4.7, 1.0, 3.05), (-0.1, -3.8, 1.8)):
        T.cyl(0.14, 0.26, (x, y, z - 0.3), T.glow("#ffb54f", 4), verts=8, bev=0.03)

# neon spill over the streets
if NIGHT:
    for (x, y, c) in ((-4.6, 1.5, "#ff4fb8"), (4.0, 1.5, "#4ff0ff"), (-8.0, -1.1, "#ffb54f"), (0.0, -1.1, "#b98cff"),
                      (8.0, -1.1, "#4ff0ff"), (0.0, 4.3, "#ff4fb8"), (-0.3, -4.5, "#ffb54f")):
        T.point((x, y, 2.6), "#ff3b4e" if (ALARM and R.random() < 0.6) else c, 450, 1.5)

# ---------------------------------------------------------------- street lamps + cars
lamp_head = T.glow("#ffd98a", 4.0) if NIGHT else M("#fff2c4")
for x in (-10.5, -7.0, -2.2, 1.6, 6.5, 10.5):
    for y, fl_ in ((-2.25, 1), (0.05, -1)):
        if (x, y) in ((-7.0, 0.05), (6.5, -2.25), (1.6, 0.05)):
            continue
        T.cyl(0.06, 1.8, (x, y, 0.18), M(PAL["iron"]), verts=6, bev=0)
        T.box((0.5, 0.12, 0.1), (x, y + 0.2 * fl_, 1.95), M(PAL["iron"]), bev=0.02)
        T.box((0.28, 0.2, 0.12), (x, y + 0.42 * fl_, 1.85), lamp_head, bev=0.02)
        if NIGHT and LIGHTS_BUDGET[0] < 22 and R.random() < 0.6:
            LIGHTS_BUDGET[0] += 1
            T.point((x, y + 0.42 * fl_, 1.4), "#ffcf7a" if not ALARM else "#ff9a6a", 80, 0.3)


def car(x, y, heading, col):
    g = T.empty("car", (x, y, 0.0), (0, 0, heading))
    b = T.box((1.3, 0.62, 0.36), (0, 0, 0.16), M(col, gloss=0.5), bev=0.08, wonk=0.02, rng=R)
    b.parent = g
    T.box((0.7, 0.54, 0.3), (-0.08, 0, 0.5), M("#2e6f86", gloss=0.8), bev=0.08, taper=0.2).parent = g
    for wx_ in (-0.4, 0.4):
        for wy_ in (-0.32, 0.32):
            T.cyl(0.16, 0.1, (wx_, wy_, 0.17), M("#2a2630"), verts=10, bev=0.02, rot=(90, 0, 0), origin_bottom=False).parent = g
    if NIGHT:
        for wy_ in (-0.2, 0.2):
            T.box((0.06, 0.14, 0.08), (0.66, wy_, 0.36), T.glow("#fff6d0", 6), bev=0).parent = g
            T.box((0.06, 0.14, 0.08), (-0.66, wy_, 0.36), T.glow("#ff2a3a", 5), bev=0).parent = g
    return g


car(-7.5, -1.55, 0, "#f2b534")
car(1.0, -0.6, 180, "#27b5ad")
car(7.6, -1.55, 0, "#e8483c")
car(-4.15, 2.2, 90, "#9a5ee0")
car(4.45, -5.2, 270, "#f4efe4")
car(-1.5, 4.7, 180, "#e27b3a")

# ---------------------------------------------------------------- suspicion props
if ALARM:
    beam_m = T.beam("#fff4d8", 1.6, 0.42, 0.02, "beam")
    beam_r = T.beam("#ff5a6a", 1.6, 0.35, 0.02, "beam_r")

    def heli(x, y, z, yaw, target, bm):
        g = T.empty("heli", (x, y, z), (0, 6, yaw))
        T.box((1.8, 0.9, 0.8), (0, 0, 0), M("#3c4452", gloss=0.5), bev=0.25, segs=3).parent = g
        T.box((0.8, 0.8, 0.5), (0.7, 0, 0.1), M("#6fe6ff", gloss=0.8), bev=0.2, taper=0.3).parent = g
        T.box((1.8, 0.22, 0.22), (-1.6, 0, 0.35), M("#3c4452"), bev=0.06, taper=0.3).parent = g
        T.box((0.1, 0.5, 0.6), (-2.4, 0, 0.45), M("#e8483c"), bev=0.04).parent = g
        T.cyl(0.06, 0.25, (0, 0, 0.8), M(PAL["iron"]), verts=6, bev=0).parent = g
        T.box((3.6, 0.2, 0.05), (0, 0, 1.05), M("#2a2630"), bev=0.02, rot=(0, 0, 25)).parent = g
        T.box((3.6, 0.2, 0.05), (0, 0, 1.05), M("#2a2630"), bev=0.02, rot=(0, 0, -65)).parent = g
        T.cyl(0.12, 0.12, (0.2, 0, 0.9), T.glow("#ff2a3a", 8), verts=8, bev=0).parent = g
        # beam: cone from the belly to the ground target
        src = Vector((x, y, z - 0.4))
        tgt = Vector(target)
        L = (src - tgt).length
        cone = T.cyl(1.5, L, (0, 0, 0), bm, r2=0.12, verts=24, bev=0, name="beam", coll=T.noline_coll(),
                     smooth=True, origin_bottom=True)
        cone.location = tgt
        T.look_at(cone, src)
        # cone points along -Z after look_at; flip so +Z goes to source
        cone.rotation_euler = (src - tgt).to_track_quat("Z", "Y").to_euler()
        T.spot(tuple(src), tuple(tgt), "#fff0d0" if bm is beam_m else "#ff5a6a", 9000, 18, 0.5)
        ring_ = T.cyl(1.45, 0.02, (tgt.x, tgt.y, 0.22), T.glow("#fff4d8" if bm is beam_m else "#ff5a6a", 1.2, alpha=0.55),
                      verts=28, bev=0, coll=T.noline_coll())
        return g

    heli(-7.5, -3.0, 9.5, 20, (-4.6, 1.9, 0.05), beam_m)
    heli(5.2, 1.0, 10.5, 160, (7.0, 4.3, 0.05), beam_r)

    def drone(x, y, z, target=None):
        g = T.empty("drone", (x, y, z))
        T.cyl(0.35, 0.22, (0, 0, 0), M("#2e3440", gloss=0.5), verts=12, bev=0.06).parent = g
        for a in range(4):
            ang = a * math.pi / 2 + math.pi / 4
            T.box((0.7, 0.08, 0.06), (math.cos(ang) * 0.35, math.sin(ang) * 0.35, 0.12), M(PAL["iron"]), bev=0.01,
                  rot=(0, 0, math.degrees(ang))).parent = g
            T.cyl(0.22, 0.04, (math.cos(ang) * 0.7, math.sin(ang) * 0.7, 0.18), M("#8d9ba8"), verts=10, bev=0).parent = g
        T.cyl(0.12, 0.1, (0, 0, -0.08), T.glow("#ff2a3a", 8), verts=10, bev=0).parent = g
        T.point((x, y, z - 0.5), "#ff2a3a", 90, 0.3)
        if target:
            src = Vector((x, y, z - 0.1)); tgt = Vector(target)
            cone = T.cyl(0.7, (src - tgt).length, (0, 0, 0), beam_r, r2=0.05, verts=18, bev=0, name="dbeam",
                         coll=T.noline_coll())
            cone.location = tgt
            cone.rotation_euler = (src - tgt).to_track_quat("Z", "Y").to_euler()
        return g

    drone(-9.5, 2.5, 6.0, (-9.0, 0.6, 0.2))
    drone(1.5, -3.0, 5.5, (0.5, -4.2, 0.2))
    drone(9.8, -3.5, 5.0)
    drone(-1.5, 7.5, 9.5)
    # rooftop alarm beacons + red wash
    for (x, y, z) in ((-10.0, 6.3, 7.5), (-2.3, 6.2, 4.9), (8.0, 1.8, 3.7), (-8.2, 1.7, 3.3), (1.6, 1.8, 5.2)):
        T.cyl(0.18, 0.3, (x, y, z), T.glow("#ff2a3a", 8), verts=10, bev=0.03)
        T.point((x, y, z + 0.6), "#ff2a3a", 300, 0.5)
    T.point((0, -6, 8), "#ff2a5a", 1500, 3.0)
    # police hover-cars blocking the avenue
    for (x, y, hd) in ((-2.8, -1.1, 90), (2.4, -1.1, 90)):
        g = car(x, y, hd, "#2d3a5a")
        T.box((0.2, 0.5, 0.1), (0.0, 0.0, 0.7), T.glow("#ff2a3a", 8), bev=0).parent = g
        T.box((0.2, 0.25, 0.1), (0.0, 0.25, 0.7), T.glow("#3a7bff", 8), bev=0).parent = g
    # barricade
    for k in range(4):
        T.box((0.9, 0.2, 0.5), (-0.4 + k * 1.0 - 1.5, -1.1 + (k % 2) * 0.3, 0.02), M("#f2b534"), bev=0.05,
              rot=(0, 0, R.uniform(-15, 15)), wonk=0.04, rng=R)


# ---------------------------------------------------------------- node + path overlay
cam_m = cam.matrix_world.to_3x3()
T.MODE["fake"] = tuple(cam_m @ Vector((-0.5, 0.6, 1.0)))
saved_mode = T.MODE["name"]
T.MODE["name"] = "day"   # the overlay is UI: one palette in every lighting state
F = "ui"
NODES = {
    "home": (-9.0, -1.1), "n2": (-4.6, -1.1), "n3": (-4.6, 4.3), "n4": (4.0, -1.1), "n5": (4.0, 4.3),
    "shop": (-0.3, -4.9), "boss": (9.6, 4.3), "n8": (9.6, -1.1),
}
KIND = {"home": ("home", "#f2c230"), "n2": ("fight", "#e8483c"), "n3": ("event", "#27b5ad"),
        "n4": ("event", "#27b5ad"), "n5": ("fight", "#e8483c"), "shop": ("shop", "#9a5ee0"),
        "boss": ("boss", "#2a2230"), "n8": ("fight", "#e8483c")}
EDGES = [("home", "n2", None), ("n2", "n4", None), ("n2", "n3", None), ("n3", "n5", None), ("n4", "n5", None),
         ("n5", "boss", None), ("n4", "n8", None), ("n2", "shop", [(-4.6, -4.9)])]
PATH_Z = 0.07


def path_dashes(a, b, via, hot):
    pts = [Vector(a)] + [Vector(v) for v in (via or [])] + [Vector(b)]
    parts = []
    seg_len = 0.5
    for i in range(len(pts) - 1):
        p, q = pts[i], pts[i + 1]
        L = (q - p).length
        d = (q - p).normalized()
        n = int(L / seg_len)
        for k in range(n):
            t0 = k * seg_len + 0.1
            if t0 < 0.75 or t0 > L - 0.75:
                continue
            c = p + d * (t0 + 0.15)
            sx = 0.32 if abs(d.x) > 0.5 else 0.24
            sy = 0.24 if abs(d.x) > 0.5 else 0.32
            if hot:
                sx *= 1.3 if abs(d.x) > 0.5 else 1.3
                sy *= 1.3
            parts.append(((c.x, c.y, PATH_Z + 0.05), (sx, sy, 0.1), 0))
    band = [tuple(p) for p in pts]
    # trim the band so it starts/ends under the node discs
    a0 = Vector(band[0]); a1 = Vector(band[1]); band[0] = tuple(a0 + (a1 - a0).normalized() * 0.5)
    b0 = Vector(band[-1]); b1 = Vector(band[-2]); band[-1] = tuple(b0 + (b1 - b0).normalized() * 0.5)
    dense = []
    for i in range(len(band) - 1):
        p, q = Vector(band[i]), Vector(band[i + 1])
        n = max(2, int((q - p).length / 0.4))
        for k in range(n):
            dense.append(tuple(p.lerp(q, k / n)))
    dense.append(band[-1])
    rib_col = "#ffc93a" if hot else "#fff6dc"
    T.ribbon(dense, 0.62 if hot else 0.52, PATH_Z, T.paint(rib_col, fake=F, stroke=0.12,
             emit=rib_col if (NIGHT and hot) else None, emit_str=0.25 if NIGHT else 0.0), name="path_band", thick=0.06)
    mat = T.paint("#c0392b" if hot else "#7a5a3a", fake=F, stroke=0.1)
    parts = [((c[0], c[1], PATH_Z + 0.07), (sz[0] * 0.55, sz[1] * 0.55, 0.05), 0) for (c, sz, _) in parts[::2]]
    if not parts:
        return None
    o = multi_box(parts, [mat], "path_dots", bev=0.0)
    sc.collection.objects.unlink(o); T.noline_coll().objects.link(o)
    return o


for a, b, via in (EDGES if OVERLAY else []):
    path_dashes(NODES[a], NODES[b], via, hot=(a == "home"))


def badge_icon(g, kind):
    if kind == "home":
        T.prism([(-0.26, -0.22), (0.26, -0.22), (0.26, 0.08), (0.0, 0.32), (-0.26, 0.08)], 0.12, (0, 0, 0.12),
                T.paint(PAL["ink"], fake=F), bev=0.02).parent = g
        T.box((0.12, 0.05, 0.16), (0.0, -0.14, 0.24), T.paint("#f2c230", fake=F), bev=0.0).parent = g
    elif kind == "boss":
        s = sub(g, (0, 0, 0.12), scale=0.62)
        Pr.icon_skull(s, F)
    else:
        glyph = {"fight": "!", "event": "?", "shop": "$"}[kind]
        label(g, glyph, 0.55, (0, -0.03, 0.12), PAL["cream"], fnt="sign", fake=F, thin=False)


def node_marker(key):
    x, y = NODES[key]
    kind, col = KIND[key]
    home = kind == "home"
    s = 1.25 if home or kind == "boss" else 1.0
    base = T.cyl(0.66 * s, 0.14, (x, y, 0.0), T.paint("#fff0cf", fake=F, stroke=0.1), verts=28, bev=0.05)
    T.cyl(0.5 * s, 0.1, (x, y, 0.12), T.paint(col, fake=F, gloss=0.4), verts=28, bev=0.04)
    if NIGHT:
        T.cyl(0.8 * s, 0.02, (x, y, 0.02), T.glow("#ffd84a" if home else col if kind != "boss" else "#ff3b4e", 1.5,
                                                    alpha=0.6), verts=28, bev=0, coll=T.noline_coll())
    # pin: faces the camera, stands above the disc
    hz = 1.55 * s
    pos = Vector((x, y, hz))
    q = (Vector(CAM_LOC) - pos).to_track_quat("Z", "Y")
    g = T.empty("pin", tuple(pos))
    g.rotation_euler = cam.matrix_world.to_euler()
    g.scale = (s, s, s)
    T.cyl(0.5, 0.2, (0, 0, -0.1), T.paint(col, fake=F, gloss=0.5, stroke=0.14), verts=24, bev=0.06).parent = g
    T.cyl(0.58, 0.14, (0, 0, -0.14), T.paint("#fff0cf", fake=F), verts=24, bev=0.04).parent = g
    T.prism([(-0.28, -0.35), (0.28, -0.35), (0.0, -0.95)], 0.16, (0, 0, -0.12), T.paint("#fff0cf", fake=F), bev=0.04).parent = g
    badge_icon(g, kind)
    if home:
        # YOU ARE HERE banner + ring pulse
        bn = sub(g, (0, 1.15, 0.0), scale=1.35, name="banner")
        Pr.plaque(bn, 2.9, 0.62, (0, 0, 0), col=PAL["wood"], trim="#f2c230", rng=random.Random(8), bolts=False)
        label(bn, "YOU ARE HERE", 0.3, (0, -0.02, 0.16), PAL["cream"], fnt="title", thin=True)
        for o in Pr.ring(0.95, 1.12, 0.08, (x, y, 0.02), T.paint("#ffd84a", fake=F, emit="#ffd84a" if NIGHT else None,
                                                                   emit_str=0.8), None, bev=0.02, segs=24):
            pass
        for o in Pr.ring(1.35, 1.46, 0.05, (x, y, 0.02), T.paint("#ffd84a", fake=F), None, bev=0.01, segs=24):
            pass


for k in (NODES if OVERLAY else []):
    node_marker(k)

# ---------------------------------------------------------------- HUD
if HUD:
    ui = Pr.ui_root(cam, depth=6.0)
    T.MODE["fake"] = tuple(cam_m @ Vector((-0.45, 0.55, 1.0)))
    rng = random.Random(77)
    p = Pr.plaque(ui, 4.4, 0.9, (*px(270, 62), 0), col=PAL["wood"], rng=rng, name="hud_district")
    label(p, "SECTOR 9 : NEON WARD", 0.34, (0, 0.1, 0.18), PAL["cream"], fnt="title")
    label(p, {"day": "DAY 3  -  MORNING", "night": "DAY 3  -  NIGHT", "alarm": "DAY 3  -  LOCKDOWN"}[MODE], 0.24,
          (0, -0.22, 0.18), "#f2c230" if not ALARM else "#ff6a6a", fnt="title", lined=False)
    frac = {"day": 0.3, "night": 0.5, "alarm": 0.9}[MODE]
    fill = {"day": "#9ee03a", "night": "#f2b534", "alarm": "#ff3b3b"}[MODE]
    m = Pr.meter(ui, 4.0, frac, (*px(1600, 78), 0), fill=fill, segs=10, label_txt="SUSPICION", name="susp")
    eye_g = sub(ui, (*px(1340, 78), 0.3), name="eye")
    T.cyl(0.36, 0.2, (0, 0, 0), T.paint(fill, fake=F, gloss=0.5), verts=16, bev=0.05).parent = eye_g
    T.cyl(0.16, 0.1, (0, 0, 0.2), T.paint(PAL["ink"], fake=F), verts=12, bev=0.02).parent = eye_g
    if ALARM:
        w_ = sub(ui, (*px(960, 62), 0.2), rot=(0, 0, -2), name="warn")
        Pr.plaque(w_, 3.2, 0.62, (0, 0, 0), col="#c8302e", trim="#f2b534", rng=rng, bolts=False)
        label(w_, "!! CITY ON ALERT !!", 0.28, (0, -0.02, 0.16), PAL["cream"], fnt="title", thin=True)
    # legend for the node icons (bottom left)
    lg = sub(ui, (*px(190, 985), 0), name="legend")
    Pr.plaque(lg, 3.1, 1.3, (0, 0, 0), col=PAL["wood_d"], trim=PAL["brass"], rng=rng, bolts=False)
    for i, (glyph, col, name) in enumerate((("!", "#e8483c", "FIGHT"), ("?", "#27b5ad", "EVENT"),
                                            ("$", "#9a5ee0", "MARKET"), ("X", "#2a2230", "CORP HQ"))):
        gx, gy = -0.95 + (i % 2) * 1.5, 0.25 - (i // 2) * 0.52
        T.cyl(0.18, 0.1, (gx, gy, 0.14), T.paint(col, fake=F), verts=16, bev=0.02).parent = lg
        label(lg, glyph, 0.22, (gx, gy - 0.01, 0.24), PAL["cream"], fnt="sign", thin=True)
        label(lg, name, 0.2, (gx + 0.28, gy - 0.01, 0.14), PAL["cream"], fnt="title", align="LEFT", thin=True)
T.MODE["name"] = saved_mode

T.render(sc, OUT)
