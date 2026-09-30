"""01-03 city (GRITTY): a torn-out chunk of dystopian megacity - stacked patched mega-blocks,
walkways, pipes, cable bundles, stacked signs, graffiti, trash, steam, surveillance - with the
node-and-path overlay lying on the wet street plane.

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

BG = {"day": "#8a8468", "night": "#10141f", "alarm": "#240c18"}[MODE]
sc = T.reset()
T.MODE["name"] = MODE
T.MODE["grit"] = 0.8
T.setup_render(sc, samples=SAMPLES, bg=BG, line=2.6, transparent=True)
T.compositor(sc, bloom=(0.9, 1.5, 8) if NIGHT else None)
world_bg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
world_bg.inputs[1].default_value = {"day": 1.3, "night": 0.3, "alarm": 0.3}[MODE]

CAM_LOC, CAM_TGT, LENS = (0.0, -29.5, 23.5), (0.0, 1.8, 3.0), 25.5
if not HUD:   # background plate for combat / shop: down in the alley between the blocks
    CAM_LOC, CAM_TGT, LENS = (-1.5, -15.0, 5.5), (0.2, 3.0, 4.5), 24
cam = T.camera(CAM_LOC, CAM_TGT, lens=LENS)
bpy.context.view_layer.update()

if MODE == "day":
    T.sun(1.9, "#e0d4a8", rot=(58, 0, -24), angle=12)
elif MODE == "night":
    T.sun(1.2, "#7f95d8", rot=(55, 0, 40), angle=6)
else:
    T.sun(1.0, "#b070e0", rot=(55, 0, 40), angle=6)

R = random.Random(2049)
NL = T.noline_coll()


def M(h, **kw):
    return T.paint(h, **kw)


def to_noline(o):
    for c in list(o.users_collection):
        c.objects.unlink(o)
    NL.objects.link(o)
    return o


# palette: soot navy, rust, oily teal-grey, stained concrete, dirty brick
WALLS = ["#39414f", "#6e4632", "#4d5e5e", "#7d776a", "#5e4038", "#474a3e", "#5a5360", "#3f4a44"]
ROOFS = ["#2a2d33", "#4a3a30", "#3a4446", "#55504a"]
NEON = ["#ff2fb0", "#8cff2a", "#3ff0ff", "#ff9a2a"]   # sickly magenta, acid green, cold cyan, sodium orange

# ---------------------------------------------------------------- window glass
if NIGHT:
    WIN_MATS = [M("#161b24"), T.glow("#ffb85a", 1.9), T.glow("#6fe6ff", 1.6), T.glow("#ff5ac0", 1.6),
                T.glow("#c8ff7a", 1.4)]
    WIN_W = [0.45, 0.3, 0.12, 0.07, 0.06]
    if ALARM:
        WIN_MATS = [M("#171220"), T.glow("#ffb36b", 1.3), T.glow("#ff3b4e", 2.0), T.glow("#ff5ac0", 1.3), T.glow("#fff0c8", 1.0)]
        WIN_W = [0.62, 0.12, 0.18, 0.04, 0.04]
else:
    WIN_MATS = [M("#2c3a42", gloss=0.6, stroke=0.25), M("#3e4a4c", gloss=0.5, stroke=0.25), M("#1b2026")]
    WIN_W = [0.5, 0.3, 0.2]


def pick_win(rng):
    x = rng.random()
    acc = 0
    for i, w in enumerate(WIN_W):
        acc += w
        if x <= acc:
            return i
    return 0


def multi_box(parts, mats, name, parent=None, bev=0.025):
    """One object made of many boxes (center, size, mat_idx)."""
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


def cable(p0, p1, sag=0.6, col="#15161a", flags=None, r=0.03):
    cu = bpy.data.curves.new("cable", "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 1
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


def cable_bundle(p0, p1, sag=0.7, n=4, spread=0.12):
    for k in range(n):
        o = Vector((R.uniform(-spread, spread), R.uniform(-spread, spread), R.uniform(-spread, spread)))
        cable(Vector(p0) + o, Vector(p1) + o, sag * R.uniform(0.8, 1.3), R.choice(("#15161a", "#2a2020", "#1a2226")),
              r=R.uniform(0.02, 0.04))


# ---------------------------------------------------------------- the torn-out chunk of city
def blob(rx, ry, n, amp, rng, cy=0.0):
    pts = []
    for i in range(n):
        a = i / n * math.tau
        k = 1 + rng.uniform(-amp, amp) + 0.05 * math.sin(a * 7 + 0.4)
        pts.append((math.cos(a) * rx * k, cy + math.sin(a) * ry * k))
    return pts


rng_i = random.Random(5)
isl = blob(14.6, 9.9, 60, 0.05, rng_i, cy=0.2)
T.prism(isl, 1.2, (0, 0, -1.3), M("#6d685e", streak_axis=2, streak=6, stroke=0.3, pattern="plank", pat_scale=0.8),
        bev=0.1, name="slab")
T.prism([(x * 0.94 + rng_i.uniform(-0.3, 0.3), y * 0.92 + rng_i.uniform(-0.3, 0.3)) for x, y in isl], 1.0, (0, 0, -2.2),
        M("#4a4640", stroke=0.3), bev=0.1, name="slab2")
T.prism([(x * 0.72, y * 0.68) for x, y in isl], 1.1, (0, 0, -3.2), M("#3a3632"), bev=0.1, name="slab3")
# jagged broken chunks hanging under the slab
for i in range(22):
    a = R.uniform(0, math.tau)
    rr = R.uniform(0.35, 0.85)
    x, y = math.cos(a) * 14.0 * rr, math.sin(a) * 9.4 * rr + 0.2
    h = R.uniform(0.8, 2.2)
    o = T.cyl(R.uniform(0.6, 1.3), h, (x, y, -2.2 - h), M("#4f4a44", stroke=0.3), r2=R.uniform(0.9, 1.6), verts=5,
              bev=0.05, wonk=0.2, rng=R, smooth=False)
    o.rotation_euler = (R.uniform(-0.2, 0.2), R.uniform(-0.2, 0.2), R.uniform(0, 6))
# rebar sticking out of the broken edge, hanging cables, broken pipes
for i in range(40):
    a = R.uniform(0, math.tau)
    x, y = math.cos(a) * 14.6, math.sin(a) * 9.9 + 0.2
    z = R.uniform(-1.8, -0.2)
    ln = R.uniform(0.6, 1.5)
    o = T.cyl(0.035, ln, (x, y, z), M("#8a4a2a", gloss=0.2), verts=5, bev=0, smooth=False)
    o.rotation_euler = (math.radians(R.uniform(60, 110)), 0, a + math.pi / 2 + R.uniform(-0.5, 0.5))
    o.rotation_euler = (Vector((math.cos(a), math.sin(a), R.uniform(-0.6, 0.5)))).to_track_quat("Z", "Y").to_euler()
for i in range(12):
    a = R.uniform(0, math.tau)
    x, y = math.cos(a) * 14.4, math.sin(a) * 9.8 + 0.2
    cable((x, y, -0.3), (x + math.cos(a) * 0.9, y + math.sin(a) * 0.9, -0.3 - R.uniform(2.0, 4.0)), 0.3,
          R.choice(("#15161a", "#2a2020")), r=0.035)
for a in (-2.1, -1.2, 3.6, -0.4):
    x, y = math.cos(a) * 14.5, math.sin(a) * 9.8 + 0.2
    rz = math.degrees(a) + 90
    T.cyl(0.35, 1.4, (x, y, -0.8), M("#5a5550", gloss=0.3), verts=12, bev=0.04, rot=(90, 0, rz), origin_bottom=False,
          wonk=0.1, rng=R)
    if NIGHT:
        T.cyl(0.26, 0.04, (x + math.cos(a) * 0.72, y + math.sin(a) * 0.72, -0.8), T.glow("#8cff2a", 2.5), verts=12,
              bev=0, rot=(90, 0, rz), origin_bottom=False)
# broken concrete rubble along the top rim (no grass)
for i in range(110):
    a = R.uniform(0, math.tau)
    k = R.uniform(0.9, 0.99)
    x, y = math.cos(a) * 14.4 * k, math.sin(a) * 9.8 * k + 0.2
    if abs(x) < 12.9 and abs(y) < 8.4:
        continue
    T.rock(R.uniform(0.15, 0.5), (x, y, -0.05), M(R.choice(("#7d776a", "#5f5a52", "#8a8478"))), R, flat=0.55)
for i in range(18):
    a = R.uniform(0, math.tau)
    x, y = math.cos(a) * 13.9, math.sin(a) * 9.4 + 0.2
    if abs(x) < 12.9 and abs(y) < 8.4:
        continue
    T.box((R.uniform(0.6, 1.3), R.uniform(0.3, 0.7), 0.25), (x, y, -0.05), M("#6d685e", pattern="tiles"), bev=0.04,
          rot=(R.uniform(-15, 15), R.uniform(-15, 15), R.uniform(0, 180)))

# asphalt + stained pavement blocks
XS = [(-12.3, -5.4), (-3.8, 3.2), (4.8, 12.3)]
YS = [(-7.8, -2.0), (-0.2, 3.6), (5.0, 7.8)]
T.prism(Pr.rrect_poly(25.6, 16.6, 1.2), 0.08, (0, 0.0, -0.06), M("#262a31", stroke=0.25, blotch=0.3, gloss=0.35),
        bev=0.03, name="asphalt")
BLOCKS = {}
for i, (x0, x1) in enumerate(XS):
    for j, (y0, y1) in enumerate(YS):
        w, d = x1 - x0 - 0.3, y1 - y0 - 0.3
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        BLOCKS[(i, j)] = (cx, cy, w, d)
        T.prism(Pr.rrect_poly(w, d, 0.3), 0.18, (cx, cy, 0.0), M("#6e695e", stroke=0.28, blotch=0.3, pattern="tiles"),
                bev=0.05, name="block")
# faded lane dashes
dash = []
for x in [i * 1.1 - 12 for i in range(23)]:
    if not any(a - 0.2 < x < b + 0.2 for a, b in ((-5.4, -3.8), (3.2, 4.8))) and R.random() < 0.8:
        dash.append(((x, -1.1, 0.035), (0.55, 0.1, 0.02), 0))
        dash.append(((x, 4.3, 0.035), (0.55, 0.1, 0.02), 0))
for y in [i * 1.1 - 7.6 for i in range(15)]:
    if not any(a - 0.2 < y < b + 0.2 for a, b in ((-2.0, -0.2), (3.6, 5.0))) and R.random() < 0.8:
        dash.append(((-4.6, y, 0.035), (0.1, 0.55, 0.02), 0))
        dash.append(((4.0, y, 0.035), (0.1, 0.55, 0.02), 0))
to_noline(multi_box(dash, [M("#a08a4a", flat=True)], "lane", bev=0))

# wet street: puddles with painted neon reflections
def puddle(x, y, rx, ry, col):
    pts = blob(rx, ry, 18, 0.18, R)
    pts = [(px_ + x, py_ + y) for px_, py_ in pts]
    if NIGHT:
        m = T.glow(col, 0.55)
    else:
        m = M("#59626b", gloss=0.9, stroke=0.1, flat=True)
    o = T.prism(pts, 0.012, (0, 0, 0.022), m, bev=0, name="puddle")
    return to_noline(o)


for (x, y, rx, ry) in ((-7.2, -1.3, 1.1, 0.35), (-1.8, -0.7, 1.4, 0.4), (2.3, -1.5, 0.9, 0.3), (8.1, -0.8, 1.2, 0.35),
                       (-4.4, -4.0, 0.3, 0.9), (4.2, 1.8, 0.35, 0.9), (-4.5, 6.4, 0.3, 0.7), (0.6, 4.5, 1.0, 0.3),
                       (6.6, 4.1, 0.9, 0.3), (4.1, -5.3, 0.3, 1.0)):
    puddle(x, y, rx, ry, R.choice(NEON) if not ALARM else R.choice(("#ff2a3a", "#3a5bff")))
# neon reflection streaks on the wet asphalt (night)
if NIGHT:
    for i in range(26):
        x = R.uniform(-12, 12)
        y = R.choice((-1.1, 4.3)) + R.uniform(-0.6, 0.6)
        c = R.choice(NEON) if not ALARM else R.choice(("#ff2a3a", "#ff2a3a", "#3a5bff"))
        to_noline(T.box((0.08, R.uniform(0.5, 1.2), 0.01), (x, y, 0.03), T.glow(c, 0.9, alpha=0.6), bev=0))


# ---------------------------------------------------------------- buildings
LIGHTS_BUDGET = [0]
TAGS = ["Zkr", "vX0", "KRSH", "n0Mad", "RxT", "SL1M", "0bey?", "Kx", "wYrm", "LLx"]


def neon_mat(c, s=3.5, broken=False):
    if broken:
        return M("#2a2630")
    if NIGHT:
        if ALARM and R.random() < 0.5:
            c = "#ff3b4e"
        return T.glow(c, s)
    return T.glow(c, 1.15)   # day: neon still burns faintly through the smog


def graffiti(body, w, d, side, rng, face="front"):
    word = rng.choice(TAGS)
    col = rng.choice(("#8cff2a", "#ff2fb0", "#e8e4dc", "#ffcf3a", "#3ff0ff"))
    z = rng.uniform(0.35, 0.9)
    if face == "front":
        t = T.text(word, rng.uniform(0.35, 0.5), (rng.uniform(-w / 3, w / 3), -d / 2 - 0.035, z), rot=(90, 0, rng.uniform(-6, 6)),
                   mat=T.flat_col(col) if not NIGHT else T.glow(col, 0.5), fnt="tag", extrude=0.0, bev=0, coll=NL)
    else:
        t = T.text(word, rng.uniform(0.35, 0.5), (side * (w / 2 + 0.035), rng.uniform(-d / 3, d / 3), z),
                   rot=(90, rng.uniform(-6, 6), 90 * side), mat=T.flat_col(col) if not NIGHT else T.glow(col, 0.5),
                   fnt="tag", extrude=0.0, bev=0, coll=NL)
    t.parent = body


def stacked_signs(body, w, d, h, side, rng, cx, cy):
    """A column of vertical signs down the corner, one of them broken/flickering."""
    n = rng.randint(2, 3)
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
        broken = rng.random() < 0.25
        col = rng.choice(NEON)
        t = T.text("\n".join(word), sz, (sx + side * 0.08, yy, z0 + bh / 2), rot=(90, 0, 90 * side),
                   mat=neon_mat(col, 3.5, broken), fnt="title", extrude=0.03, bev=0, coll=T.thin_coll())
        t.parent = body
        if NIGHT and not broken and LIGHTS_BUDGET[0] < 16:
            LIGHTS_BUDGET[0] += 1
            T.point((cx + sx + side * 0.9, cy + yy, z0 + bh / 2), "#ff3b4e" if ALARM else col, 130, 0.4)
        z = z0 - 0.15


def box_building(cx, cy, w, d, h, wall, rng, side, z0=0.18, name="bld", roof=None, windows=True):
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
    multi_box(parts, [M("#5a574f", streak_axis=0), M(roof or rng.choice(ROOFS), stroke=0.3)], name + "_trim",
              parent=body, bev=0.03)
    if windows:
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
                if rng.random() < 0.18:   # AC box under a window
                    wparts.append(((x, -d / 2 - 0.2, z - 0.35), (0.34, 0.3, 0.22), 0))
            for c in range(scol):
                if rng.random() < 0.12:
                    continue
                y = -d / 2 + (c + 0.5) * d / scol
                wparts.append(((side * (w / 2 + 0.02), y, z), (0.1, 0.3, 0.42), pick_win(rng)))
        if wparts:
            multi_box(wparts, WIN_MATS, name + "_win", parent=body, bev=0.015)
    return body


def building(cx, cy, w, d, h, wall, side=None, sign=True, stack=None, shacks=True, scaffold=False, name="bld"):
    """Patched-together mega-block: base box, an older/newer tower stacked on top, rooftop shacks,
    pipes, stacked signs, graffiti, AC units, dishes, antennas."""
    rng = random.Random(int(cx * 100 + cy * 37 + h * 11))
    side = side if side is not None else (1 if cx < 0 else -1)
    body = box_building(cx, cy, w, d, h, wall, rng, side, name=name)
    top = h + 0.18
    if stack:
        sw, sd, sh = stack
        ox = rng.uniform(-(w - sw) / 2, (w - sw) / 2) * 0.8
        oy = rng.uniform(-(d - sd) / 2, (d - sd) / 2) * 0.8
        box_building(cx + ox, cy + oy, sw, sd, sh, rng.choice(WALLS), rng, side, z0=top + 0.1, name=name + "_stack")
        # the stack gets its own roof junk
        _roof_junk(cx + ox, cy + oy, sw, sd, top + 0.1 + sh + 0.2, rng)
    if shacks:
        for k in range(rng.randint(1, 2)):
            sw = rng.uniform(0.7, 1.2)
            x = cx + rng.uniform(-w / 2 + sw / 2, w / 2 - sw / 2)
            y = cy + rng.uniform(-d / 2 + 0.5, d / 2 - 0.5)
            if stack:
                y = cy - d / 2 + 0.55
            s_ = T.box((sw, 0.9, 0.75), (x, y, top + 0.2), M(rng.choice(("#6e5a44", "#4d5e5e", "#7a4a32")), pattern="plank"),
                       bev=0.05, wonk=0.06, rng=rng, rot=(0, 0, rng.uniform(-8, 8)))
            T.box((sw + 0.25, 1.1, 0.08), (x, y, top + 0.95), M("#5a5a52", gloss=0.3), bev=0.02,
                  rot=(rng.uniform(-6, 6), 0, rng.uniform(-8, 8)))
    if not stack:
        _roof_junk(cx, cy, w, d, top + 0.2, rng)
    # exposed pipes: one vertical run + one horizontal run on the front
    px_ = -side * (w / 2 + 0.08)
    T.cyl(0.08, h - 0.1, (px_, -d / 2 + 0.1, 0.0), M("#6a6258", gloss=0.3), verts=8, bev=0).parent = body
    T.cyl(0.06, h - 0.1, (px_ + side * 0.2, -d / 2 + 0.1, 0.0), M("#7a4a32"), verts=8, bev=0).parent = body
    zz = rng.uniform(1.4, max(1.5, h - 1.0))
    T.cyl(0.07, w * 0.9, (0, -d / 2 - 0.1, zz), M("#6a6258", gloss=0.3), verts=8, bev=0, rot=(0, 90, 0),
          origin_bottom=False).parent = body
    if sign:
        stacked_signs(body, w, d, h, side, rng, cx, cy)
    graffiti(body, w, d, side, rng, "front")
    if rng.random() < 0.6:
        graffiti(body, w, d, side, rng, "side")
    if scaffold:
        sp = []
        for k in range(int(w / 0.8) + 1):
            x = -w / 2 + k * w / int(w / 0.8)
            sp.append(((x, -d / 2 - 0.45, h * 0.35), (0.06, 0.06, h * 0.7), 0))
        for zk in range(1, int(h * 0.7 / 1.0) + 1):
            sp.append(((0, -d / 2 - 0.45, zk * 1.0), (w, 0.06, 0.06), 0))
            sp.append(((0, -d / 2 - 0.35, zk * 1.0 - 0.05), (w, 0.45, 0.05), 1))
        multi_box(sp, [M("#8a7a3a"), M("#6e5a44", pattern="plank")], "scaffold", parent=body, bev=0.0)
    return body


def _roof_junk(cx, cy, w, d, zt, rng):
    for i in range(rng.randint(2, 4)):
        kind = rng.choice(("ac", "ac", "tank", "ant", "dish", "vent"))
        x = cx + rng.uniform(-w / 2 + 0.45, w / 2 - 0.45)
        y = cy + rng.uniform(-d / 2 + 0.45, d / 2 - 0.45)
        if kind == "ac":
            T.box((0.7, 0.55, 0.45), (x, y, zt), M("#8a8e88", gloss=0.2), bev=0.05, wonk=0.05, rng=rng)
            T.cyl(0.18, 0.05, (x, y, zt + 0.45), M(PAL["iron"]), verts=10, bev=0.01)
        elif kind == "tank":
            for lx in (-0.25, 0.25):
                for ly in (-0.25, 0.25):
                    T.cyl(0.04, 0.5, (x + lx, y + ly, zt), M("#3a3530"), verts=6, bev=0)
            T.cyl(0.42, 0.7, (x, y, zt + 0.5), M("#5a4030", streak_axis=2, streak=18), verts=12, bev=0.05, wonk=0.05, rng=rng)
            T.cyl(0.5, 0.3, (x, y, zt + 1.2), M("#3a3a3a"), r2=0.05, verts=12, bev=0.03)
        elif kind == "ant":
            h_ = rng.uniform(1.0, 2.0)
            T.cyl(0.04, h_, (x, y, zt), M("#5a5a5a"), verts=6, bev=0)
            T.box((0.5, 0.04, 0.04), (x, y, zt + h_ * 0.7), M("#5a5a5a"), bev=0)
            T.cyl(0.09, 0.1, (x, y, zt + h_), T.glow("#ff3b4e", 5) if NIGHT else M("#a03a30"), verts=8, bev=0.02)
        elif kind == "dish":
            T.cyl(0.08, 0.35, (x, y, zt), M("#5a5a5a"), verts=6, bev=0)
            T.cyl(0.55, 0.22, (x, y, zt + 0.55), M("#b8b4a8", gloss=0.3), r2=0.12, verts=16, bev=0.03,
                  rot=(rng.uniform(-50, -30), 0, rng.uniform(-40, 40)), origin_bottom=False)
        else:
            T.cyl(0.16, 0.6, (x, y, zt), M("#6a6660", gloss=0.3), verts=10, bev=0.03)
            T.cyl(0.24, 0.12, (x, y, zt + 0.6), M(PAL["iron"]), verts=10, bev=0.02)


def fill_block(key, specs):
    cx, cy, w, d = BLOCKS[key]
    for sp in specs:
        fx, fy, fw, fd, h, wall = sp[:6]
        kw = sp[6] if len(sp) > 6 else {}
        building(cx + fx * w / 2, cy + fy * d / 2, fw, fd, h, wall, **kw)


# back row: tall mega-blocks, towers on towers
fill_block((0, 2), [(-0.62, 0.1, 2.2, 2.0, 7.8, WALLS[0], {"stack": (1.6, 1.4, 3.2)}),
                    (0.05, 0.0, 1.6, 1.8, 5.8, WALLS[2], {"sign": False}),
                    (0.62, 0.05, 2.0, 2.0, 6.6, WALLS[1], {"stack": (1.4, 1.3, 2.4)})])
fill_block((1, 2), [(-0.62, 0.05, 2.1, 2.0, 6.2, WALLS[5], {"stack": (1.5, 1.4, 2.6)}),
                    (0.1, 0.1, 1.5, 1.8, 8.6, WALLS[6], {"sign": False})])
# middle row: dense
fill_block((0, 1), [(-0.62, 0.0, 2.2, 2.6, 4.6, WALLS[4], {"scaffold": True}),
                    (0.05, 0.15, 1.5, 2.2, 5.6, WALLS[3], {"sign": False}),
                    (0.62, 0.1, 2.1, 2.4, 4.2, WALLS[0], {"side": 1, "stack": (1.3, 1.2, 1.8)})])
fill_block((1, 1), [(-0.55, 0.1, 2.6, 2.4, 4.6, WALLS[1], {"side": -1}),
                    (0.5, 0.0, 2.4, 2.8, 6.0, WALLS[7], {"side": 1, "stack": (1.5, 1.6, 2.2)})])
fill_block((2, 1), [(-0.5, 0.05, 2.6, 2.6, 4.2, WALLS[2], {"side": -1}),
                    (0.4, 0.25, 1.9, 1.8, 3.0, WALLS[6], {"side": -1, "sign": False})])
# front row: low slum blocks so the avenue stays visible
fill_block((0, 0), [(0.45, 0.0, 2.8, 2.6, 2.6, WALLS[3], {"side": 1}),
                    (-0.55, 0.3, 2.2, 2.2, 3.4, WALLS[5], {"side": 1})])
fill_block((2, 0), [(-0.45, 0.2, 3.0, 2.6, 2.8, WALLS[4], {"side": -1}),
                    (0.55, 0.0, 2.2, 2.2, 3.6, WALLS[2], {"side": -1})])

# ---------------------------------------------------------------- landmarks
# 1. corp tower looming over the slums (back right): dark glass, cold cyan strips, halo ring
cx, cy, w, d = BLOCKS[(2, 2)]
hx, hy = cx + 0.5, cy + 0.2
tiers = [(3.8, 2.4, 3.2, "#20263a"), (3.0, 2.0, 3.1, "#262d44"), (2.2, 1.6, 2.7, "#2c3450"), (1.4, 1.1, 1.6, "#343c5a")]
z = 0.18
for i, (tw, td, th, c) in enumerate(tiers):
    b = T.box((tw, td, th), (hx, hy, z), M(c, seed=i, gloss=0.4), bev=0.1, taper=0.07, wonk=0.008, rng=R)
    T.box((tw * 0.96 + 0.24, td * 0.96 + 0.24, 0.22), (hx, hy, z + th - 0.05), M("#6a6e78", gloss=0.6), bev=0.05)
    strips = []
    n = int(tw / 0.5)
    for k in range(n):
        x = -tw / 2 + (k + 0.5) * tw / n
        strips.append(((x, -td / 2 - 0.01, th * 0.5), (0.14, 0.1, th * 0.82), 1 if NIGHT and R.random() < 0.8 else 0))
    multi_box(strips, [M("#3a4a5a", gloss=0.8), T.glow("#6ff0ff" if not ALARM else "#ff4f63", 1.8)], "hq_glass", parent=b)
    z += th + 0.15
T.cyl(0.7, 1.6, (hx, hy, z), M("#4a5068", gloss=0.6), r2=0.08, verts=6, bev=0.05)
T.cyl(0.05, 1.2, (hx, hy, z + 1.5), M(PAL["steel"]), verts=6, bev=0)
T.cyl(0.16, 0.2, (hx, hy, z + 2.7), T.glow("#ff3b4e", 6) if NIGHT else M("#a03a30"), verts=10, bev=0.03)
halo_z = z - 1.4
for o in Pr.ring(1.9, 2.2, 0.2, (hx, hy, halo_z), T.glow("#3ff0ff", 3.0) if (NIGHT and not ALARM) else
                 (T.glow("#ff3b4e", 3.5) if ALARM else M("#8a8e98", gloss=0.8)), None, bev=0.05, segs=28):
    o.rotation_euler = (math.radians(8), 0, 0)
# searchlights sweeping from the corp tower (night)
if NIGHT and not ALARM:
    for tgt in ((-6.0, 7.0, 8.0), (1.0, 9.0, 10.5)):
        src = Vector((hx, hy, z + 0.3))
        tv = Vector(tgt)
        cone = T.cyl(0.9, (tv - src).length, (0, 0, 0), T.beam("#bfe8ff", 1.0, 0.0, 0.3, "sweep"), r2=0.12, verts=16,
                     bev=0, name="sweep", coll=NL)
        cone.location = tv
        cone.rotation_euler = (src - tv).to_track_quat("Z", "Y").to_euler()
# corp logo: an eye on the tower face
logo = sub(None, (hx, hy - 1.28, 4.7), rot=(90, 0, 0), name="logo")
T.cyl(0.7, 0.12, (0, 0, 0), M("#101320"), verts=24, bev=0.03).parent = logo
e_ = T.cyl(0.55, 0.06, (0, 0, 0.12), neon_mat("#3ff0ff", 4) if NIGHT else M("#c8ccd4", gloss=0.5), verts=24, bev=0)
e_.parent = logo
e_.scale = (1.0, 0.55, 1.0)
T.cyl(0.2, 0.08, (0, 0, 0.16), T.glow("#ff3b4e", 5) if NIGHT else M("#a03a30"), verts=16, bev=0).parent = logo
T.text("ORBYT", 0.44, (hx, hy - 1.34, 1.2), mat=neon_mat("#3ff0ff", 3.5), fnt="title", extrude=0.04, bev=0,
       coll=T.thin_coll())
if NIGHT:
    T.point((hx, hy - 3, 3.0), "#ff3b4e" if ALARM else "#3ff0ff", 500, 1.0)
    T.point((hx, hy - 2.0, halo_z), "#ff3b4e" if ALARM else "#3ff0ff", 300, 1.0)

# 2. huge corp billboard with the eye over the slums (back centre, on stilts above the roofs)
cx, cy, w, d = BLOCKS[(1, 2)]
bbx, bby, bbz = cx + 0.5, cy + 0.8, 9.6
for lx in (-2.2, 0.0, 2.2):
    T.box((0.18, 0.18, 1.2), (bbx + lx, bby + 0.1, bbz - 1.2), M("#3a3a3a"), bev=0.02)
T.box((5.6, 0.3, 2.8), (bbx, bby, bbz), M("#2a2a2e"), bev=0.08, wonk=0.01, rng=R)
T.box((5.2, 0.12, 2.4), (bbx, bby - 0.16, bbz + 0.2), T.glow("#1a1030", 1.0) if NIGHT else M("#3a3048"), bev=0.02)
ey = sub(None, (bbx - 1.2, bby - 0.26, bbz + 1.4), rot=(90, 0, 0), name="bb_eye")
T.cyl(1.0, 0.05, (0, 0, 0), neon_mat("#ff2fb0", 3.0) if NIGHT else M("#d8d0c4"), verts=24, bev=0).parent = ey
ey.children[0].scale = (1.0, 0.5, 1.0)
T.cyl(0.36, 0.07, (0, 0, 0.04), M("#101010"), verts=16, bev=0).parent = ey
T.text("OBEY\nCOMPLY", 0.46, (bbx + 1.2, bby - 0.26, bbz + 1.72), mat=neon_mat("#e8e4dc", 3.0), fnt="stencil", extrude=0.03,
       bev=0, coll=T.thin_coll())
# torn poster strips hanging off the billboard
for k in range(4):
    T.box((0.35, 0.03, R.uniform(0.4, 0.9)), (bbx - 2.3 + k * 1.4, bby - 0.2, bbz - 0.3), M("#b8a88a"), bev=0,
          rot=(0, R.uniform(-10, 10), 0))
if NIGHT:
    T.point((bbx, bby - 2.5, bbz + 1.0), "#ff3b4e" if ALARM else "#ff2fb0", 500, 1.0)

# 3. overhanging walkways between blocks + pipe bridge
def walkway(p0, p1, z, w_=0.8):
    a, b = Vector(p0), Vector(p1)
    mid = (a + b) / 2
    L_ = (b - a).length
    ang = math.degrees(math.atan2(b.y - a.y, b.x - a.x))
    g = T.empty("walk", (mid.x, mid.y, z), (0, 0, ang))
    T.box((L_, w_, 0.14), (0, 0, 0), M("#4a4a46", pattern="plank"), bev=0.03, wonk=0.01, rng=R).parent = g
    for sy in (-1, 1):
        T.box((L_, 0.05, 0.05), (0, sy * w_ / 2, 0.55), M("#6a5a3a"), bev=0).parent = g
        for k in range(int(L_ / 0.6) + 1):
            T.box((0.05, 0.05, 0.55), (-L_ / 2 + k * L_ / int(L_ / 0.6), sy * w_ / 2, 0.0), M("#6a5a3a"), bev=0).parent = g
    T.box((L_, 0.12, 0.12), (0, 0, -0.18), M("#7a4a32"), bev=0.01).parent = g
    if NIGHT:
        T.box((0.3, 0.2, 0.08), (0, 0, -0.1), T.glow("#ff9a2a", 3), bev=0).parent = g
    return g


walkway((-7.4, 1.4), (-3.0, 1.2), 3.6)
walkway((1.5, 6.0), (6.1, 6.2), 5.2)
walkway((-9.5, 3.1), (-9.4, 5.1), 4.4, 0.7)
T.cyl(0.14, 4.6, (-3.0, 5.6, 6.0), M("#6a6258", gloss=0.3), verts=10, bev=0, rot=(0, 90, 0), origin_bottom=False)
T.cyl(0.1, 4.6, (-3.0, 5.35, 5.8), M("#7a4a32"), verts=10, bev=0, rot=(0, 90, 0), origin_bottom=False)

# 4. market alley (front centre): tarps, crates, stalls, dumpster, trash
cx, cy, w, d = BLOCKS[(1, 0)]
for k, (tx, ty, c) in enumerate(((cx - 1.8, cy + 1.2, "#3a4a5a"), (cx + 1.8, cy + 1.1, "#5a3a3a"), (cx + 0.0, cy + 1.6, "#4a5a3a"))):
    for lx in (-0.7, 0.7):
        for ly in (-0.55, 0.55):
            T.cyl(0.05, 1.3, (tx + lx, ty + ly, 0.18), M("#4a4640"), verts=6, bev=0)
    T.box((1.8, 1.5, 0.08), (tx, ty, 1.5), M(c, stroke=0.35), bev=0.03, rot=(R.uniform(-10, -4), R.uniform(-6, 6), 0),
          wonk=0.08, rng=R)
    T.box((1.3, 0.8, 0.6), (tx, ty, 0.18), M("#6a5038", pattern="plank"), bev=0.05, wonk=0.05, rng=R)
    if NIGHT:
        T.cyl(0.12, 0.2, (tx, ty - 0.6, 1.25), T.glow(R.choice(("#ff9a2a", "#8cff2a")), 4), verts=8, bev=0.02)
T.box((1.4, 0.8, 0.8), (cx + 3.1, cy - 1.8, 0.18), M("#2f4a3a", gloss=0.3), bev=0.06, wonk=0.04, rng=R, rot=(0, 0, 8))
T.box((1.5, 0.9, 0.1), (cx + 3.1, cy - 1.8, 0.98), M("#26342c"), bev=0.03, rot=(-12, 0, 8))


def trash(x, y, n=4):
    for k in range(n):
        T.rock(R.uniform(0.18, 0.3), (x + R.uniform(-0.4, 0.4), y + R.uniform(-0.3, 0.3), 0.18),
               M(R.choice(("#1e1e22", "#2a2a30", "#3a3a2a")), gloss=0.5), R, flat=0.85)


for (x, y) in ((cx + 2.2, cy - 2.0), (cx - 3.0, cy - 1.9), (-8.0, -2.4), (8.5, -2.4), (-5.7, 4.0), (5.0, 3.1),
               (-10.8, 0.1), (10.5, 0.2), (1.0, 3.9)):
    trash(x, y, R.randint(3, 5))
for i in range(14):
    T.box((R.uniform(0.2, 0.45), R.uniform(0.2, 0.4), R.uniform(0.15, 0.35)),
          (R.uniform(-11, 11), R.choice((-2.2, 0.0, 3.8, 4.8)) + R.uniform(-0.1, 0.1), 0.02),
          M(R.choice(("#6a5038", "#5a5a52", "#7a6a4a"))), bev=0.03, rot=(0, 0, R.uniform(0, 90)))

# steam venting from street grates (painted puffs)
for (x, y) in ((-10.5, -2.5), (1.8, -2.5), (6.8, 3.75), (-7.0, 3.75)):
    T.box((0.7, 0.5, 0.03), (x, y, 0.2), M("#1a1a1a"), bev=0)
    for k in range(4):
        T.rock(0.2 + k * 0.1, (x + k * 0.12, y + k * 0.05, 0.3 + k * 0.5),
               M("#b8b8b0" if not NIGHT else "#6a6a78", toplight=0.1, stroke=0.1), R, flat=0.8)

# ---------------------------------------------------------------- street furniture: lamps, cameras, cars
lamp_head = T.glow("#ff9a2a", 4.0) if NIGHT else M("#c8b890")
for x in (-10.5, -7.0, -2.2, 1.6, 6.5, 10.5):
    for y, fl_ in ((-2.25, 1), (0.05, -1)):
        if (x, y) in ((-7.0, 0.05), (6.5, -2.25), (1.6, 0.05)):
            continue
        T.cyl(0.06, 1.8, (x, y, 0.18), M("#3a3a3a"), verts=6, bev=0)
        T.box((0.5, 0.12, 0.1), (x, y + 0.2 * fl_, 1.95), M("#3a3a3a"), bev=0.02)
        T.box((0.28, 0.2, 0.12), (x, y + 0.42 * fl_, 1.85), lamp_head, bev=0.02)
        if NIGHT and LIGHTS_BUDGET[0] < 24 and R.random() < 0.6:
            LIGHTS_BUDGET[0] += 1
            T.point((x, y + 0.42 * fl_, 1.4), "#ff9a2a" if not ALARM else "#ff6a5a", 45, 0.3)


def cam_pole(x, y, yaw):
    g = T.empty("campole", (x, y, 0.18), (0, 0, yaw))
    T.cyl(0.06, 2.4, (0, 0, 0), M("#4a4a4a"), verts=6, bev=0).parent = g
    T.box((0.5, 0.06, 0.06), (0.2, 0, 2.35), M("#4a4a4a"), bev=0).parent = g
    T.box((0.42, 0.22, 0.22), (0.45, 0, 2.2), M("#d8d4c8", gloss=0.3), bev=0.04, rot=(0, 18, 0)).parent = g
    T.cyl(0.07, 0.06, (0.68, 0, 2.14), T.glow("#ff2a3a", 6) if NIGHT else M("#a02a2a"), verts=8, bev=0,
          rot=(0, 90, 0), origin_bottom=False).parent = g


for (x, y, yaw) in ((-5.6, -2.3, 200), (3.1, -2.3, -30), (-3.7, 3.7, 150), (4.9, 5.1, -20), (-11.6, 0.2, 10),
                    (11.6, 3.6, 170)):
    cam_pole(x, y, yaw)


def car(x, y, heading, col, armored=False):
    g = T.empty("car", (x, y, 0.0), (0, 0, heading))
    if armored:
        T.box((1.9, 0.95, 0.7), (0, 0, 0.2), M(col, gloss=0.3), bev=0.1, wonk=0.02, rng=R, taper=0.12).parent = g
        T.box((0.5, 0.9, 0.3), (0.95, 0, 0.3), M(col), bev=0.08, rot=(0, -30, 0)).parent = g
        for k in range(4):   # hazard stripes on the flank
            T.box((0.14, 0.02, 0.3), (-0.6 + k * 0.35, -0.49, 0.45), M("#e8c030" if k % 2 else "#1a1a1a", flat=True),
                  bev=0, rot=(0, 30, 0)).parent = g
        for wx_ in (-0.6, 0.0, 0.6):
            for wy_ in (-0.48, 0.48):
                T.cyl(0.22, 0.14, (wx_, wy_, 0.22), M("#1e1e22"), verts=10, bev=0.02, rot=(90, 0, 0), origin_bottom=False).parent = g
        T.box((0.3, 0.8, 0.1), (0.1, 0.0, 0.95), T.glow("#ff2a3a", 8), bev=0).parent = g
        T.box((0.3, 0.4, 0.1), (0.1, 0.2, 0.96), T.glow("#3a6bff", 8), bev=0).parent = g
        T.point((x, y, 1.6), "#ff2a3a", 250, 0.5)
        T.point((x + 0.3, y + 0.3, 1.6), "#3a6bff", 200, 0.5)
        return g
    T.box((1.3, 0.62, 0.36), (0, 0, 0.16), M(col, gloss=0.4), bev=0.08, wonk=0.03, rng=R).parent = g
    T.box((0.7, 0.54, 0.3), (-0.08, 0, 0.5), M("#2c3a42", gloss=0.8), bev=0.08, taper=0.2).parent = g
    for wx_ in (-0.4, 0.4):
        for wy_ in (-0.32, 0.32):
            T.cyl(0.16, 0.1, (wx_, wy_, 0.17), M("#1e1e22"), verts=10, bev=0.02, rot=(90, 0, 0), origin_bottom=False).parent = g
    if NIGHT:
        for wy_ in (-0.2, 0.2):
            T.box((0.06, 0.14, 0.08), (0.66, wy_, 0.36), T.glow("#fff0c0", 6), bev=0).parent = g
            T.box((0.06, 0.14, 0.08), (-0.66, wy_, 0.36), T.glow("#ff2a3a", 5), bev=0).parent = g
    return g


car(-7.5, -1.55, 0, "#6a5a3a")
car(1.0, -0.6, 180, "#3a4a4a")
car(7.6, -1.55, 0, "#5a3030")
car(-4.15, 2.2, 90, "#4a4058")
car(-1.5, 4.7, 180, "#5a5448")

# neon spill (night)
if NIGHT:
    for (x, y, c) in ((-4.6, 1.5, NEON[0]), (4.0, 1.5, NEON[2]), (-8.0, -1.1, NEON[3]), (0.0, -1.1, NEON[1]),
                      (8.0, -1.1, NEON[2]), (0.0, 4.3, NEON[0]), (-0.3, -4.5, NEON[3])):
        T.point((x, y, 2.6), "#ff3b4e" if (ALARM and R.random() < 0.6) else c, 420, 1.5)

# ---------------------------------------------------------------- surveillance: drones (night) / crackdown (alarm)
beam_w = T.beam("#e8f4ff", 1.4, 0.4, 0.02, "beam")
beam_r = T.beam("#ff5a6a", 1.5, 0.35, 0.02, "beam_r")


def drone(x, y, z, target=None, bm=beam_w):
    g = T.empty("drone", (x, y, z))
    T.cyl(0.35, 0.22, (0, 0, 0), M("#2a2e36", gloss=0.5), verts=10, bev=0.06).parent = g
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        T.box((0.7, 0.08, 0.06), (math.cos(ang) * 0.35, math.sin(ang) * 0.35, 0.12), M(PAL["iron"]), bev=0.01,
              rot=(0, 0, math.degrees(ang))).parent = g
        T.cyl(0.22, 0.04, (math.cos(ang) * 0.7, math.sin(ang) * 0.7, 0.18), M("#6a7078"), verts=10, bev=0).parent = g
    T.cyl(0.12, 0.1, (0, 0, -0.08), T.glow("#ff2a3a", 8), verts=10, bev=0).parent = g
    T.point((x, y, z - 0.5), "#ff2a3a", 90, 0.3)
    if target:
        src = Vector((x, y, z - 0.1)); tgt = Vector(target)
        cone = T.cyl(0.8, (src - tgt).length, (0, 0, 0), bm, r2=0.05, verts=16, bev=0, name="dbeam", coll=NL)
        cone.location = tgt
        cone.rotation_euler = (src - tgt).to_track_quat("Z", "Y").to_euler()
        T.cyl(0.8, 0.02, (tgt.x, tgt.y, 0.22), T.glow("#e8f4ff" if bm is beam_w else "#ff5a6a", 1.0, alpha=0.45),
              verts=20, bev=0, coll=NL)
    return g


if NIGHT and not ALARM:
    drone(-9.0, 3.0, 7.0, (-8.6, 0.8, 0.2))
    drone(6.5, -3.8, 6.0, (7.2, -1.9, 0.2))
    drone(-1.5, 8.0, 10.5)

if ALARM:
    def heli(x, y, z, yaw, target, bm):
        g = T.empty("heli", (x, y, z), (0, 6, yaw))
        T.box((1.9, 0.95, 0.85), (0, 0, 0), M("#262a32", gloss=0.5), bev=0.25, segs=3).parent = g
        T.box((0.8, 0.8, 0.5), (0.72, 0, 0.1), M("#3a4a52", gloss=0.8), bev=0.2, taper=0.3).parent = g
        T.box((1.9, 0.22, 0.22), (-1.7, 0, 0.35), M("#262a32"), bev=0.06, taper=0.3).parent = g
        T.box((0.1, 0.5, 0.6), (-2.5, 0, 0.45), M("#e8c030"), bev=0.04).parent = g
        T.cyl(0.06, 0.25, (0, 0, 0.82), M(PAL["iron"]), verts=6, bev=0).parent = g
        T.box((3.8, 0.2, 0.05), (0, 0, 1.07), M("#1a1a1e"), bev=0.02, rot=(0, 0, 25)).parent = g
        T.box((3.8, 0.2, 0.05), (0, 0, 1.07), M("#1a1a1e"), bev=0.02, rot=(0, 0, -65)).parent = g
        T.cyl(0.12, 0.12, (0.2, 0, 0.9), T.glow("#ff2a3a", 8), verts=8, bev=0).parent = g
        src = Vector((x, y, z - 0.4))
        tgt = Vector(target)
        cone = T.cyl(1.6, (src - tgt).length, (0, 0, 0), bm, r2=0.12, verts=24, bev=0, name="beam", coll=NL)
        cone.location = tgt
        cone.rotation_euler = (src - tgt).to_track_quat("Z", "Y").to_euler()
        T.spot(tuple(src), tuple(tgt), "#fff0d0" if bm is beam_w else "#ff5a6a", 9000, 18, 0.5)
        T.cyl(1.5, 0.02, (tgt.x, tgt.y, 0.22), T.glow("#fff4d8" if bm is beam_w else "#ff5a6a", 1.2, alpha=0.55),
              verts=28, bev=0, coll=NL)
        return g

    heli(-7.5, -3.0, 10.0, 20, (-4.6, 1.9, 0.05), beam_w)
    heli(5.4, 0.6, 11.5, 160, (7.0, 4.3, 0.05), beam_r)
    drone(-9.5, 2.5, 6.5, (-9.0, 0.6, 0.2), beam_r)
    drone(1.5, -3.0, 6.0, (0.5, -4.2, 0.2), beam_w)
    drone(9.8, -3.5, 5.5)
    drone(-1.5, 8.0, 10.5)
    for (x, y, z) in ((-10.0, 6.3, 11.6), (-2.6, 6.2, 9.2), (8.0, 1.8, 4.6), (-8.2, 1.7, 5.0), (1.6, 1.8, 6.4)):
        T.cyl(0.18, 0.3, (x, y, z), T.glow("#ff2a3a", 8), verts=10, bev=0.03)
        T.point((x, y, z + 0.6), "#ff2a3a", 300, 0.5)
    T.point((0, -6, 8), "#ff2a5a", 1500, 3.0)
    T.point((3, -4, 4), "#3a5bff", 900, 2.0)
    # armoured vehicles + police strobes blocking the avenue, concrete barriers with hazard paint
    car(-2.6, -1.1, 90, "#2a3040", armored=True)
    car(2.3, -1.1, 90, "#2a3040", armored=True)
    car(4.0, 6.2, 0, "#2a3040", armored=True)
    for k in range(5):
        x = -1.6 + k * 0.8
        T.box((0.7, 0.35, 0.5), (x, -1.9 + (k % 2) * 0.2, 0.02), M("#8a8578"), bev=0.05, taper=0.35,
              rot=(0, 0, R.uniform(-12, 12)), wonk=0.04, rng=R)
        T.box((0.72, 0.37, 0.1), (x, -1.9 + (k % 2) * 0.2, 0.3), M("#e8c030" if k % 2 else "#1a1a1a", flat=True), bev=0,
              rot=(0, 0, 0))

# ---------------------------------------------------------------- node + path overlay (UI palette, readable)
cam_m = cam.matrix_world.to_3x3()
T.MODE["fake"] = tuple(cam_m @ Vector((-0.5, 0.6, 1.0)))
saved_mode, saved_grit = T.MODE["name"], T.MODE["grit"]
T.MODE["name"] = "day_ui"
T.MODE["grit"] = 0.25
F = "ui"
NODES = {
    "home": (-9.0, -1.1), "n2": (-4.6, -1.1), "n3": (-4.6, 4.3), "n4": (4.0, -1.1), "n5": (4.0, 4.3),
    "shop": (-0.3, -4.9), "boss": (9.6, 4.3), "n8": (9.6, -1.1),
}
KIND = {"home": ("home", "#f2c230"), "n2": ("fight", "#e8483c"), "n3": ("event", "#27b5ad"),
        "n4": ("event", "#27b5ad"), "n5": ("fight", "#e8483c"), "shop": ("shop", "#b05ee0"),
        "boss": ("boss", "#2a2230"), "n8": ("fight", "#e8483c")}
EDGES = [("home", "n2", None), ("n2", "n4", None), ("n2", "n3", None), ("n3", "n5", None), ("n4", "n5", None),
         ("n5", "boss", None), ("n4", "n8", None), ("n2", "shop", [(-4.6, -4.9)])]
PATH_Z = 0.07


def path_band(a, b, via, hot):
    pts = [Vector(a)] + [Vector(v) for v in (via or [])] + [Vector(b)]
    band = [tuple(p) for p in pts]
    a0 = Vector(band[0]); a1 = Vector(band[1]); band[0] = tuple(a0 + (a1 - a0).normalized() * 0.5)
    b0 = Vector(band[-1]); b1 = Vector(band[-2]); band[-1] = tuple(b0 + (b1 - b0).normalized() * 0.5)
    dense = []
    for i in range(len(band) - 1):
        p, q = Vector(band[i]), Vector(band[i + 1])
        n = max(2, int((q - p).length / 0.4))
        for k in range(n):
            dense.append(tuple(p.lerp(q, k / n)))
    dense.append(band[-1])
    rib_col = "#ffc93a" if hot else "#f0e6cc"
    T.ribbon(dense, 0.62 if hot else 0.52, PATH_Z, T.paint(rib_col, fake=F, stroke=0.15,
             emit=rib_col if NIGHT else None, emit_str=0.35 if hot else 0.12), name="path_band", thick=0.06)


for a, b, via in (EDGES if OVERLAY else []):
    path_band(NODES[a], NODES[b], via, hot=(a == "home"))


def badge_icon(g, kind):
    if kind == "home":
        T.prism([(-0.26, -0.22), (0.26, -0.22), (0.26, 0.08), (0.0, 0.32), (-0.26, 0.08)], 0.12, (0, 0, 0.12),
                T.paint(PAL["ink"], fake=F), bev=0.02).parent = g
        T.box((0.12, 0.05, 0.16), (0.0, -0.14, 0.24), T.paint("#f2c230", fake=F), bev=0.0).parent = g
    elif kind == "boss":
        Pr.icon_skull(sub(g, (0, 0, 0.12), scale=0.62), F)
    else:
        glyph = {"fight": "!", "event": "?", "shop": "$"}[kind]
        label(g, glyph, 0.55, (0, -0.03, 0.12), PAL["cream"], fnt="sign", fake=F, thin=False)


def node_marker(key):
    x, y = NODES[key]
    kind, col = KIND[key]
    home = kind == "home"
    s = 1.25 if home or kind == "boss" else 1.0
    T.cyl(0.66 * s, 0.14, (x, y, 0.0), T.paint("#f0e6cc", fake=F, stroke=0.1), verts=28, bev=0.05)
    T.cyl(0.5 * s, 0.1, (x, y, 0.12), T.paint(col, fake=F, gloss=0.4), verts=28, bev=0.04)
    if NIGHT:
        T.cyl(0.8 * s, 0.02, (x, y, 0.02), T.glow("#ffd84a" if home else (col if kind != "boss" else "#ff3b4e"), 1.5,
                                                    alpha=0.6), verts=28, bev=0, coll=NL)
    g = T.empty("pin", (x, y, 1.55 * s))
    g.rotation_euler = cam.matrix_world.to_euler()
    g.scale = (s, s, s)
    T.cyl(0.5, 0.2, (0, 0, -0.1), T.paint(col, fake=F, gloss=0.5, stroke=0.14), verts=24, bev=0.06).parent = g
    T.cyl(0.58, 0.14, (0, 0, -0.14), T.paint("#f0e6cc", fake=F), verts=24, bev=0.04).parent = g
    T.prism([(-0.28, -0.35), (0.28, -0.35), (0.0, -0.95)], 0.16, (0, 0, -0.12), T.paint("#f0e6cc", fake=F), bev=0.04).parent = g
    badge_icon(g, kind)
    if home:
        bn = sub(g, (0, 1.15, 0.0), scale=1.35, name="banner")
        Pr.plaque(bn, 2.9, 0.62, (0, 0, 0), col="#2e3238", trim="#f2c230", rng=random.Random(8), bolts=False)
        label(bn, "YOU ARE HERE", 0.3, (0, -0.02, 0.16), "#f2c230", fnt="title", thin=True)
        Pr.ring(0.95, 1.12, 0.08, (x, y, 0.02), T.paint("#ffd84a", fake=F, emit="#ffd84a" if NIGHT else None,
                                                         emit_str=0.8), None, bev=0.02, segs=24)
        Pr.ring(1.35, 1.46, 0.05, (x, y, 0.02), T.paint("#ffd84a", fake=F), None, bev=0.01, segs=24)


for k in (NODES if OVERLAY else []):
    node_marker(k)

# ---------------------------------------------------------------- HUD
if HUD:
    ui = Pr.ui_root(cam, depth=6.0)
    T.MODE["fake"] = tuple(cam_m @ Vector((-0.45, 0.55, 1.0)))
    rng = random.Random(77)
    p = Pr.plaque(ui, 4.4, 0.9, (*px(270, 62), 0), col="#2e3238", trim="#8a6a3a", rng=rng, name="hud_district")
    label(p, "SECTOR 9 : THE SUMP", 0.36, (0, 0.1, 0.18), "#e8e0cc", fnt="title")
    label(p, {"day": "DAY 3  -  SMOG ADVISORY", "night": "DAY 3  -  CURFEW 02:00", "alarm": "DAY 3  -  LOCKDOWN"}[MODE],
          0.22, (0, -0.24, 0.18), "#8cff2a" if not ALARM else "#ff5a5a", fnt="title", lined=False)
    frac = {"day": 0.3, "night": 0.5, "alarm": 0.9}[MODE]
    fill = {"day": "#8cff2a", "night": "#ff9a2a", "alarm": "#ff2a3a"}[MODE]
    Pr.meter(ui, 4.0, frac, (*px(1600, 78), 0), fill=fill, segs=10, label_txt="SUSPICION", frame="#2e3238", name="susp")
    eye_g = sub(ui, (*px(1340, 78), 0.3), name="eye")
    T.cyl(0.36, 0.2, (0, 0, 0), T.paint(fill, fake=F, gloss=0.5), verts=16, bev=0.05).parent = eye_g
    T.cyl(0.16, 0.1, (0, 0, 0.2), T.paint(PAL["ink"], fake=F), verts=12, bev=0.02).parent = eye_g
    if ALARM:
        w_ = sub(ui, (*px(960, 62), 0.2), rot=(0, 0, -2), name="warn")
        Pr.plaque(w_, 3.6, 0.66, (0, 0, 0), col="#a0201e", trim="#e8c030", rng=rng, bolts=False)
        label(w_, "!! SECTOR LOCKDOWN !!", 0.28, (0, -0.02, 0.16), PAL["cream"], fnt="title", thin=True)
    lg = sub(ui, (*px(190, 985), 0), name="legend")
    Pr.plaque(lg, 3.1, 1.3, (0, 0, 0), col="#2a2c30", trim="#6a6258", rng=rng, bolts=False)
    for i, (glyph, col, name) in enumerate((("!", "#e8483c", "FIGHT"), ("?", "#27b5ad", "EVENT"),
                                            ("$", "#b05ee0", "MARKET"), ("X", "#2a2230", "CORP HQ"))):
        gx, gy = -0.95 + (i % 2) * 1.5, 0.25 - (i // 2) * 0.52
        T.cyl(0.18, 0.1, (gx, gy, 0.14), T.paint(col, fake=F), verts=16, bev=0.02).parent = lg
        label(lg, glyph, 0.22, (gx, gy - 0.01, 0.24), PAL["cream"], fnt="sign", thin=True)
        label(lg, name, 0.2, (gx + 0.28, gy - 0.01, 0.14), "#e8e0cc", fnt="title", align="LEFT", lined=False)
T.MODE["name"], T.MODE["grit"] = saved_mode, saved_grit

T.render(sc, OUT)
