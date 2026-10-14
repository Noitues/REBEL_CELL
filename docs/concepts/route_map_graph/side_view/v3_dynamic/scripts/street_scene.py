"""Side view: the netrun street in side elevation, cut open on the route floors (Blender 5.2 headless, Eevee).

blender -b --factory-startup --python street_scene.py -- <layout.json> <outdir> <side|tq> [preview]

Built on the round 30-35 city kit (target_corps.py primitives: faceted Cv2 boxes with tone jitter, 3-band toon ramp,
neon / window glow materials, the id / normal / depth data passes for the ink post) and the round 35 hq_climb rooms
(every room dressed; the 8 round-35 set dressings come back as each room's second prop).
  side : orthographic side elevation (camera on -y looking +y), 10 px per BU at 1080p (matches sgraph.to_px)
  tq   : a 3/4 perspective dolly camera: the street recedes to the left, the TARGET tower stands near on the right
Writes <tag>_beauty_night.png, _glow_night.png, _normal.png, _id.png, _depth.png, _sem.png, anchors_<tag>.json.
sem pass (Raw): R = class (0.1 facade, 0.3 cut, 0.5 room, 0.7 link structure, 0.85 far city, 0.2 ground), G = room
index / 32 for room faces, B = column / 10. All randomness is seeded.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
LAYOUT, OUTDIR, CAM = argv[0], argv[1], argv[2]
PREVIEW = len(argv) > 3 and argv[3] == "preview"
TAG = CAM
os.makedirs(OUTDIR, exist_ok=True)
LY = json.load(open(LAYOUT))
C = LY["const"]
FH, SLAB, DEPTH = C["FLOOR_H"], C["SLAB"], C["DEPTH"]
rng = random.Random(4207)

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE"
except TypeError:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
RES = (1440, 810) if PREVIEW else (2880, 1620)
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 6 if PREVIEW else 24
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_depth = "16"
scene.render.film_transparent = False

AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
LIME = (0.83, 1.0, 0.0)
MERIDIAN = (0.86, 0.42, 0.10)
# the node-type light colours (the stickers' own ring colours; parent round "bloom" colours)
TYPE_LIGHT = {"router": (0.36, 0.88, 1.0), "elite": (1.0, 0.38, 0.16), "terminal": (0.24, 1.0, 0.55),
              "modem": (0.35, 0.59, 1.0), "rack": (1.0, 0.77, 0.24), "target": (1.0, 0.17, 0.24), "start": LIME}


# ------------------------------------------------------------------ geometry accumulator (round 30 kit + sem layer)
class Acc:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.col = self.bm.faces.layers.float_color.new("col")
        self.fj = self.bm.faces.layers.float.new("fj")
        self.bid = self.bm.faces.layers.float_color.new("bid")
        self.sem = self.bm.faces.layers.float_color.new("sem")

    def face(self, pts, col, bid, fj=None, sem=None):
        vs = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(vs)
        f[self.col] = (col[0], col[1], col[2], 1.0)
        f[self.fj] = rng.random() if fj is None else fj
        f[self.bid] = (bid[0], bid[1], bid[2], 1.0)
        s = sem or SEM
        f[self.sem] = (s[0], s[1], s[2], 1.0)
        return f

    def facet_quad(self, a, b, c, d, col, bid, jit=0.035):
        A, B, Cc, D = map(Vector, (a, b, c, d))
        n = (B - A).cross(D - A)
        size = max((B - A).length, (D - A).length)
        if n.length < 1e-6 or size < 2.5:
            self.face([a, b, c, d], col, bid)
            return
        n.normalize()
        u, v = rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7)
        P = A.lerp(B, u).lerp(D.lerp(Cc, u), v) + n * rng.uniform(-jit, jit) * size
        for p, q in ((A, B), (B, Cc), (Cc, D), (D, A)):
            self.face([tuple(p), tuple(q), tuple(P)], col, bid)

    def obj(self, mat):
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(mat)
        for p in me.polygons:
            p.use_smooth = False
        return ob


SEM = (0.1, 0.0, 0.0)


def set_sem(cls, room=0, col=0):
    global SEM
    SEM = (cls, room / 32.0, col / 10.0)


SOLID = Acc("solid")
NEON = Acc("neon")
WIN = Acc("win")


def rid():
    return (rng.random(), rng.random(), rng.random())


def box(x0, y0, z0, x1, y1, z1, col, facet=True, bid=None, top=True, bottom=False, acc=None):
    acc = acc or SOLID
    bid = bid or rid()
    b = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    u = [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    sides = [(b[0], b[1], u[1], u[0]), (b[1], b[2], u[2], u[1]), (b[2], b[3], u[3], u[2]), (b[3], b[0], u[0], u[3])]
    for q in sides:
        if facet and acc is SOLID:
            acc.facet_quad(*q, col, bid)
        else:
            acc.face(list(q), col, bid)
    if top:
        acc.face(u, col, bid)
    if bottom:
        acc.face(list(reversed(b)), col, bid)
    return bid


def beam(p0, p1, w, col, acc=None, bid=None):
    acc = acc or SOLID
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    a = d.cross(up).normalized() * (w / 2)
    b = d.cross(a).normalized() * (w / 2)
    c0 = [p0 + a + b, p0 - a + b, p0 - a - b, p0 + a - b]
    c1 = [p1 + a + b, p1 - a + b, p1 - a - b, p1 + a - b]
    bid = bid or rid()
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(c0[i]), tuple(c0[j]), tuple(c1[j]), tuple(c1[i])], col, bid)
    acc.face([tuple(v) for v in c1], col, bid)
    acc.face([tuple(v) for v in reversed(c0)], col, bid)


def quad_y(acc, x0, z0, x1, z1, y, col, bid=(0, 0, 0)):
    """A quad facing -y (towards the side camera) at depth y."""
    acc.face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], col, bid)


def hazard(x0, x1, z, y, h=0.35, seg=0.9):
    n = max(1, int((x1 - x0) / seg))
    for i in range(n):
        a, b = x0 + (x1 - x0) * i / n, x0 + (x1 - x0) * (i + 1) / n
        quad_y(SOLID, a, z, b, z + h, y, MERIDIAN if i % 2 == 0 else (0.06, 0.05, 0.05))


WIN_COLS = [(1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)]


def windows(x0, y0, z0, x1, y1, z1, p=0.35, sx=2.2, sz=2.6, ww=1.1, wh=1.0, cols=None, faces=(0, 1, 2, 3), zoff=1.0, k=1.0):
    cols = cols or WIN_COLS
    o = 0.06
    walls = [((x0, y0 - o), (x1, y0 - o)), ((x1 + o, y0), (x1 + o, y1)), ((x1, y1 + o), (x0, y1 + o)), ((x0 - o, y1), (x0 - o, y0))]
    for fi in faces:
        (ax, ay), (bx, by) = walls[fi]
        L = math.hypot(bx - ax, by - ay)
        nx = int((L - 1.0) / sx)
        nz = int((z1 - z0 - zoff - wh) / sz) + 1
        if nx < 1 or nz < 1:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        off = (L - nx * sx) / 2
        for i in range(nx):
            for k in range(nz):
                if rng.random() > p:
                    continue
                c = rng.choice(cols)
                s = (0.5 + 0.5 * rng.random()) * k
                c = (c[0] * s, c[1] * s, c[2] * s)
                t0 = off + i * sx + (sx - ww) / 2
                z = z0 + zoff + k * sz
                pa = (ax + ux * t0, ay + uy * t0)
                pb = (ax + ux * (t0 + ww), ay + uy * (t0 + ww))
                WIN.face([(pa[0], pa[1], z), (pb[0], pb[1], z), (pb[0], pb[1], z + wh), (pa[0], pa[1], z + wh)], c, (0, 0, 0))


def roof_trim(x0, y0, x1, y1, z, col, w=0.3):
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        beam((a[0], a[1], z), (b[0], b[1], z), w, col, acc=NEON)


# ------------------------------------------------------------------ materials (round 30 toon + glow)
def attr(nt, name):
    n = nt.nodes.new("ShaderNodeAttribute")
    n.attribute_type = "GEOMETRY"
    n.attribute_name = name
    return n


def mat_toon():
    m = bpy.data.materials.new("toon")
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[1].position = 0.12
    el.new(0.32)
    col = attr(nt, "col")
    fj = attr(nt, "fj")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.86
    mr.inputs["To Max"].default_value = 1.12
    m1 = nt.nodes.new("ShaderNodeMix")
    m1.data_type = "RGBA"
    m1.blend_type = "MULTIPLY"
    m1.inputs["Factor"].default_value = 1.0
    m2 = nt.nodes.new("ShaderNodeVectorMath")
    m2.operation = "SCALE"
    em = nt.nodes.new("ShaderNodeEmission")
    L = nt.links.new
    L(dif.outputs[0], s2r.inputs[0])
    L(s2r.outputs["Color"], bw.inputs[0])
    L(bw.outputs[0], ramp.inputs[0])
    L(col.outputs["Color"], m1.inputs[6])
    L(ramp.outputs["Color"], m1.inputs[7])
    L(fj.outputs["Fac"], mr.inputs["Value"])
    L(m1.outputs[2], m2.inputs[0])
    L(mr.outputs[0], m2.inputs["Scale"])
    L(m2.outputs[0], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m, ramp


def mat_glow(name, k=1.0):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    col = attr(nt, "col")
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    sc.inputs["Scale"].default_value = k
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(col.outputs["Color"], sc.inputs[0])
    nt.links.new(sc.outputs[0], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mat_flat(name, rgb):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = tuple(rgb) + (1,)
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


TOON, RAMP = mat_toon()
NEONM = mat_glow("neon", 1.0)
WINM = mat_glow("win", 1.0)
for e, c in zip(RAMP.color_ramp.elements, [(0.09, 0.08, 0.21), (0.20, 0.17, 0.36), (0.36, 0.30, 0.54)]):
    e.color = c + (1,)

world = bpy.data.worlds.new("w")
scene.world = world
wnt = world.node_tree
bg = next(n for n in wnt.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.03, 0.025, 0.06, 1)

# key light: from the upper left front (lit band on the -y faces and the tops)
sun = bpy.data.lights.new("sun", "SUN")
sun.energy = 1.7
so = bpy.data.objects.new("sun", sun)
so.rotation_euler = (math.radians(52), math.radians(-28), math.radians(-24))
scene.collection.objects.link(so)

# ------------------------------------------------------------------ palette
FAMS = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36), (0.40, 0.38, 0.46)]
CUT = (0.15, 0.13, 0.19)       # the cut concrete (slab and wall sections): lighter, so the cutaway reads as a cut
TRIMS = [AMBER, CYAN, PINK, (0.6, 0.4, 1.0), (0.4, 1.0, 0.6)]
ROOM_IDX = {}
for _n, _i in enumerate(sorted(LY["nodes"], key=lambda i: (LY["nodes"][i]["layer"], LY["nodes"][i]["k"]))):
    ROOM_IDX[_i] = _n + 1


# ------------------------------------------------------------------ rooms (round 35 hq_climb lineage)
def light_strip(x0, x1, z, y0, y1, col):
    NEON.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], col, (0, 0, 0))


def panel(x0, z0, x1, z1, y, col):
    quad_y(NEON, x0, z0, x1, z1, y, col)


def room(i, n):
    x0, z0, x1, z1 = n["room"]
    kind = n["kind"]
    lc = TYPE_LIGHT[kind]
    set_sem(0.5, ROOM_IDX[i], n["layer"])
    yb = DEPTH - 0.6
    inner = (0.22, 0.2, 0.26)
    # back wall + a dim type-colour wash on it (the room's colour reads from afar)
    quad_y(SOLID, x0, z0, x1, z1, yb, inner)
    quad_y(NEON, x0 + 0.3, z0 + 0.3, x1 - 0.3, z1 - 0.3, yb - 0.02, tuple(v * 0.16 for v in lc))
    # side walls inside (seen in 3/4)
    box(x0 - 0.02, 0.6, z0, x0, yb, z1, inner, facet=False, top=False)
    box(x1, 0.6, z0, x1 + 0.02, yb, z1, inner, facet=False, top=False)
    # floor: plates + a light pool; ceiling light strip in the type colour
    box(x0, 0.0, z0 - 0.02, x1, yb, z0, (0.3, 0.28, 0.32), facet=False)
    NEON.face([(x0 + 1.0, 0.4, z0 + 0.02), (x1 - 1.0, 0.4, z0 + 0.02), (x1 - 1.0, yb - 1.0, z0 + 0.02), (x0 + 1.0, yb - 1.0, z0 + 0.02)],
              tuple(v * 0.22 for v in lc), (0, 0, 0))
    light_strip(x0 + 1.2, x1 - 1.2, z1 - 0.05, 2.0, 3.0, tuple(min(1, v * 1.2) for v in lc))
    cx = (x0 + x1) / 2
    zf = z0
    yk = yb - 0.4                       # props stand against the back wall
    W = x1 - x0
    if kind == "start":
        # the Cell's relay: a jury-rigged desk with a CRT stack, a couch, a fist poster, cables on the floor
        box(x0 + 1.0, yk - 3.0, zf, x0 + 5.2, yk - 1.2, zf + 1.4, (0.36, 0.28, 0.22), facet=False)
        for q, (dx, dz) in enumerate(((0.0, 1.4), (1.6, 1.4), (0.8, 2.9))):
            box(x0 + 1.4 + dx, yk - 2.4, zf + dz, x0 + 2.9 + dx, yk - 1.3, zf + dz + 1.4, (0.16, 0.16, 0.18), facet=False)
            panel(x0 + 1.55 + dx, zf + dz + 0.2, x0 + 2.75 + dx, zf + dz + 1.2, yk - 2.45, LIME if q != 1 else CYAN)
        box(cx + 0.6, yk - 2.0, zf, x1 - 1.0, yk - 0.6, zf + 1.2, (0.5, 0.18, 0.3), facet=False)
        box(cx + 0.6, yk - 0.9, zf + 1.2, x1 - 1.0, yk - 0.6, zf + 2.4, (0.5, 0.18, 0.3), facet=False)
        panel(cx + 1.2, zf + 3.2, cx + 3.4, zf + 5.6, yk + 0.25, PINK)
    elif kind == "router":
        # the security room: a monitor wall (3 x 2 cyan feeds), a guard desk, a gun locker with a cyan eye, a ceiling turret
        for r in range(2):
            for c in range(3):
                bx = cx - 3.3 + c * 2.2
                bz = zf + 2.8 + r * 1.6
                box(bx, yk - 0.3, bz, bx + 2.0, yk, bz + 1.4, (0.1, 0.1, 0.12), facet=False)
                panel(bx + 0.15, bz + 0.15, bx + 1.85, bz + 1.25, yk - 0.32, tuple(v * (0.6 + 0.4 * ((r + c) % 2)) for v in lc))
        box(cx - 3.6, yk - 2.6, zf, cx + 2.0, yk - 1.4, zf + 1.3, (0.3, 0.3, 0.34), facet=False)
        box(x1 - 2.3, yk - 1.6, zf, x1 - 0.6, yk - 0.2, zf + 4.6, (0.2, 0.2, 0.24))
        panel(x1 - 2.0, zf + 3.4, x1 - 0.9, zf + 3.9, yk - 1.65, lc)
        box(x0 + 0.8, yk - 2.4, zf, x0 + 2.2, yk - 1.0, zf + 1.6, (0.45, 0.32, 0.2))
        beam((cx + 3.2, 3.0, z1), (cx + 3.2, 3.0, z1 - 1.0), 0.25, (0.25, 0.25, 0.28))
        box(cx + 2.6, 2.4, z1 - 1.8, cx + 3.8, 3.6, z1 - 1.0, (0.3, 0.3, 0.34), facet=False)
        panel(cx + 2.8, z1 - 1.6, cx + 3.6, z1 - 1.2, 2.38, RED)
    elif kind == "elite":
        # the armoured vault: heavy plates with a hazard frame, the hulking armoured drone frame with a red eye
        for c in range(4):
            box(x0 + 0.6 + c * (W - 1.2) / 4, yk - 0.4, zf + 0.4, x0 + 0.5 + (c + 1) * (W - 1.2) / 4, yk, z1 - 0.6, (0.32, 0.3, 0.3))
        hazard(x0 + 0.4, x1 - 0.4, z1 - 0.9, yk - 0.45, 0.4)
        hazard(x0 + 0.4, x1 - 0.4, zf + 0.05, 0.3, 0.35)
        box(cx - 2.2, yk - 3.6, zf, cx + 2.2, yk - 1.0, zf + 1.0, (0.18, 0.17, 0.2))
        box(cx - 1.8, yk - 3.2, zf + 1.0, cx + 1.8, yk - 1.2, zf + 4.2, MERIDIAN)
        box(cx - 1.1, yk - 3.0, zf + 4.2, cx + 1.1, yk - 1.4, zf + 5.2, (0.2, 0.2, 0.22))
        panel(cx - 0.7, zf + 4.4, cx + 0.7, zf + 4.9, yk - 3.05, RED)
        for s in (-1, 1):
            beam((cx + s * 1.8, yk - 2.2, zf + 3.6), (cx + s * 3.4, yk - 2.6, zf + 2.0), 0.6, (0.25, 0.24, 0.26))
        panel(x0 + 0.8, zf + 4.6, x0 + 1.5, zf + 5.3, yk - 0.45, RED)
        panel(x1 - 1.5, zf + 4.6, x1 - 0.8, zf + 5.3, yk - 0.45, RED)
    elif kind == "terminal":
        # the odd room: one CRT on a plinth under a hanging cable nest, an aquarium glowing, an empty chair
        box(cx - 1.2, yk - 3.0, zf, cx + 1.2, yk - 1.6, zf + 1.6, (0.25, 0.24, 0.28))
        box(cx - 1.0, yk - 2.8, zf + 1.6, cx + 1.0, yk - 1.7, zf + 3.2, (0.12, 0.12, 0.14), facet=False)
        panel(cx - 0.8, zf + 1.8, cx + 0.8, zf + 3.0, yk - 2.85, lc)
        for k in range(5):
            xx = cx - 2.0 + k
            beam((xx, yk - 2.2, z1), (xx + 0.3 * ((k % 2) * 2 - 1), yk - 2.2, z1 - 1.0 - (k % 3) * 0.7), 0.12, (0.1, 0.1, 0.1))
        box(x0 + 0.8, yk - 1.4, zf, x0 + 3.6, yk - 0.2, zf + 2.6, (0.1, 0.12, 0.14), facet=False)
        panel(x0 + 0.95, zf + 0.25, x0 + 3.45, zf + 2.3, yk - 1.45, (0.1, 0.55, 0.65))
        for k in range(3):
            panel(x0 + 1.3 + k * 0.7, zf + 0.9 + (k % 2) * 0.6, x0 + 1.6 + k * 0.7, zf + 1.1 + (k % 2) * 0.6, yk - 1.48, AMBER)
        box(x1 - 2.6, yk - 2.6, zf, x1 - 1.4, yk - 1.4, zf + 1.1, (0.4, 0.2, 0.3), facet=False)
        box(x1 - 2.6, yk - 1.6, zf + 1.1, x1 - 1.4, yk - 1.4, zf + 2.6, (0.4, 0.2, 0.3), facet=False)
    elif kind == "modem":
        # the shop: three vending machines (lit fronts), a market counter with a striped awning, the MAINFRAME sign
        for c, vc in enumerate((PINK, CYAN, AMBER)):
            bx = x0 + 0.8 + c * 2.0
            box(bx, yk - 1.4, zf, bx + 1.7, yk - 0.2, zf + 4.2, (0.2, 0.22, 0.32), facet=False)
            panel(bx + 0.15, zf + 1.5, bx + 1.55, zf + 3.9, yk - 1.45, vc)
            panel(bx + 0.3, zf + 0.6, bx + 1.4, zf + 1.0, yk - 1.45, (0.15, 0.15, 0.18))
        box(cx + 1.0, yk - 3.4, zf, x1 - 0.6, yk - 2.4, zf + 1.6, (0.4, 0.3, 0.22), facet=False)
        for c in range(4):
            a = cx + 1.0 + c * (x1 - 0.6 - cx - 1.0) / 4
            b = cx + 1.0 + (c + 1) * (x1 - 0.6 - cx - 1.0) / 4
            quad_y(SOLID, a, zf + 3.4, b, zf + 4.0, yk - 3.6, (0.85, 0.85, 0.9) if c % 2 else (0.25, 0.4, 0.9))
        for c in range(3):
            box(cx + 1.4 + c * 1.2, yk - 3.2, zf + 1.6, cx + 2.2 + c * 1.2, yk - 2.6, zf + 2.2, rng.choice([(0.8, 0.3, 0.5), (0.3, 0.7, 0.8), (0.9, 0.7, 0.2)]), facet=False)
        panel(cx + 1.2, z1 - 1.4, x1 - 0.8, z1 - 0.6, yk + 0.25, (0.3, 0.55, 1.0))
    elif kind in ("rack", "target"):
        # the Rack: server cabinets with amber / green LEDs; the TARGET vault adds a red core and cable bundles
        n_ = 4 if kind == "rack" else 5
        span = (W - 1.6) if kind == "rack" else (W - 1.6)
        for c in range(n_):
            bx = x0 + 0.8 + c * span / n_
            if kind == "target" and c == n_ // 2:
                box(bx + 0.2, yk - 3.0, zf, bx + span / n_ - 0.2, yk - 1.0, zf + 5.6, (0.16, 0.12, 0.14))
                panel(bx + 0.5, zf + 1.0, bx + span / n_ - 0.5, zf + 5.0, yk - 3.05, RED)
                continue
            box(bx, yk - 2.6, zf, bx + span / n_ - 0.4, yk - 0.8, zf + 5.2, (0.14, 0.13, 0.15))
            for q in range(7):
                for p in range(2):
                    panel(bx + 0.3 + p * 0.7, zf + 0.6 + q * 0.62, bx + 0.6 + p * 0.7, zf + 0.85 + q * 0.62, yk - 2.65,
                          AMBER if (q + p + c) % 3 else (0.4, 1.0, 0.5))
        for k in range(3):
            beam((x0 + 0.6, yk - 0.4 - k * 0.3, z1 - 0.6 - k * 0.35), (x1 - 0.6, yk - 0.4 - k * 0.3, z1 - 0.6 - k * 0.35), 0.25, (0.3, 0.3, 0.34))
    if kind not in ("start", "target"):
        detail(n["layer"], n["k"], x0, zf, x1, z1, yk)


def detail(t, i, x0, zf, x1, z1, yb):
    """The 8 round 35 set dressings, one per room as its second prop (variant by column and slot)."""
    v = (t * 5 + i * 3) % 8
    cx = (x0 + x1) / 2
    if v == 0:      # pipes along the back wall + a red valve
        for k in range(2):
            beam((x0 + 0.6, yb - 0.3, z1 - 0.8 - k * 0.5), (x1 - 0.6, yb - 0.3, z1 - 0.8 - k * 0.5), 0.26, (0.5, 0.45, 0.4))
        panel(x1 - 1.4, z1 - 1.5, x1 - 0.9, z1 - 1.0, yb - 0.5, RED)
    elif v == 1:    # a hanging bulb
        beam((x0 + 1.4, 1.5, z1), (x0 + 1.4, 1.5, z1 - 1.2), 0.06, (0.1, 0.1, 0.1))
        panel(x0 + 1.15, z1 - 1.6, x0 + 1.65, z1 - 1.2, 1.45, (1.0, 0.85, 0.5))
    elif v == 2:    # a pallet jack
        box(x1 - 2.4, 1.2, zf, x1 - 0.8, 2.4, zf + 0.5, (0.86, 0.62, 0.10), facet=False)
        beam((x1 - 0.9, 1.8, zf + 0.5), (x1 - 0.6, 1.8, zf + 2.0), 0.15, (0.2, 0.2, 0.22))
    elif v == 3:    # oil barrels
        for k in range(2):
            box(x1 - 2.4 + k * 0.9, 1.0, zf, x1 - 1.6 + k * 0.9, 1.8, zf + 1.3, (0.16, 0.36, 0.62) if k % 2 else RED, facet=False)
    elif v == 4:    # a desk lamp
        panel(x0 + 0.8, zf + 1.6, x0 + 1.4, zf + 2.0, 1.2, (1.0, 0.85, 0.5))
    elif v == 5:    # a cargo net with sacks under the ceiling
        for k in range(3):
            box(x0 + 1.0 + k * 1.3, yb - 2.2, z1 - 1.4, x0 + 2.0 + k * 1.3, yb - 1.3, z1 - 0.6, (0.6, 0.5, 0.34))
    elif v == 6:    # a cooling fan + a cable tray
        panel(x0 + 0.8, z1 - 2.6, x0 + 2.0, z1 - 1.4, yb - 0.45, (0.3, 0.6, 1.0))
        beam((x0 + 0.6, yb - 0.4, z1 - 0.5), (x1 - 0.6, yb - 0.4, z1 - 0.5), 0.3, (0.3, 0.3, 0.32))
    else:           # a mop bucket
        box(x1 - 1.6, 1.4, zf, x1 - 0.9, 2.1, zf + 0.7, (0.86, 0.62, 0.10), facet=False)


# ------------------------------------------------------------------ buildings
ROUTE_FLOORS = {}
for i, n in LY["nodes"].items():
    ROUTE_FLOORS.setdefault(int(n["layer"]), {})[n["floor"]] = i


def building(l):
    x0, x1 = LY["cols"][str(l)]
    st = LY["storeys"][str(l)]
    top = st * FH
    c = FAMS[(l * 3 + 1) % len(FAMS)] if l != 7 else (0.34, 0.3, 0.36)
    fb = rid()
    rf = ROUTE_FLOORS.get(l, {})
    for f in range(st):
        za, zb = f * FH, (f + 1) * FH
        if f in rf:
            # the cut: slab below / above in the CUT tone, side walls cut, the back of the floor behind
            set_sem(0.3, 0, l)
            box(x0, 0, za - SLAB / 2 if f else 0, x1, DEPTH, za + SLAB / 2, CUT, facet=False, bid=fb)
            box(x0, 0, zb - SLAB / 2, x1, DEPTH, zb + SLAB / 2 if f < st - 1 else zb, CUT, facet=False, bid=fb)
            box(x0, 0, za, x0 + 0.7, DEPTH, zb, CUT, facet=False, bid=fb)
            box(x1 - 0.7, 0, za, x1, DEPTH, zb, CUT, facet=False, bid=fb)
            # a thin dark reveal line just inside the cut (ink helps it, this makes it read in V1 too)
            set_sem(0.3, 0, l)
            room(rf[f], LY["nodes"][rf[f]])
        else:
            set_sem(0.1, 0, l)
            box(x0, 0, za, x1, DEPTH, zb, c, bid=fb, top=(f == st - 1))
            p = 0.55 if l != 7 else 0.65
            cols = None if l != 7 else [(1.0, 0.2, 0.12), (1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (0.9, 0.9, 1.0)]
            windows(x0, 0, za, x1, DEPTH, zb, p=p * 0.8, sx=2.15, sz=FH, ww=1.1, wh=3.0, cols=cols, zoff=2.6, k=0.95)
            if f == 0:
                # street-level shopfront glow + an awning
                set_sem(0.1, 0, l)
                quad_y(NEON, x0 + 1.0, 0.4, x1 - 1.0, 3.6, -0.08, tuple(v * 0.55 for v in rng.choice(TRIMS)))
                box(x0 + 0.6, -1.6, 3.8, x1 - 0.6, 0, 4.2, rng.choice([(0.6, 0.15, 0.3), (0.15, 0.4, 0.5), (0.5, 0.35, 0.1)]), facet=False)
    # roof: parapet, tank, antenna, AC, neon trim
    set_sem(0.1, 0, l)
    box(x0, 0, top, x1, DEPTH, top + 0.8, tuple(v * 0.9 for v in c), facet=False)
    roof_trim(x0 + 0.1, 0.1, x1 - 0.1, DEPTH - 0.1, top + 0.85, TRIMS[l % len(TRIMS)] if l != 7 else MERIDIAN, w=0.28)
    if l != 7:
        if l % 2 == 0:
            box(x0 + 2, 3, top + 0.8, x0 + 5, 6, top + 4.0, (0.35, 0.3, 0.28), facet=False)
            for q in (2.3, 4.7):
                beam((x0 + q, 4.5, top + 0.8), (x0 + q, 4.5, top - 0.0), 0.2, (0.2, 0.2, 0.2))
        else:
            beam((x1 - 2.5, 4, top + 0.8), (x1 - 2.5, 4, top + 9.0), 0.25, (0.3, 0.3, 0.32))
            panel(x1 - 2.75, top + 8.8, x1 - 2.25, top + 9.3, -0.2 + 3.6, RED)
            box(x0 + 1.5, 2, top + 0.8, x0 + 4.5, 5, top + 2.4, (0.3, 0.3, 0.34), facet=False)
    else:
        # the TARGET tower: Meridian crown + mast with a red beacon, red crest windows on its ground floors
        box(x0 + 2, 1.5, top + 0.8, x1 - 2, DEPTH - 1.5, top + 5.0, (0.3, 0.26, 0.3))
        hazard(x0 + 2, x1 - 2, top + 4.0, 1.45, 0.6, seg=1.2)
        beam(((x0 + x1) / 2, 6, top + 5.0), ((x0 + x1) / 2, 6, top + 15.0), 0.35, (0.3, 0.3, 0.32))
        panel((x0 + x1) / 2 - 0.4, top + 14.6, (x0 + x1) / 2 + 0.4, top + 15.4, 5.6, RED)
    # a blade sign on some facades (vertical neon plate on the alley-side edge)
    if l in (2, 5):
        set_sem(0.1, 0, l)
        sx = x1 + 0.1
        box(sx, -1.4, top - 14, sx + 0.6, 1.0, top - 4, (0.12, 0.1, 0.14), facet=False)
        quad_y(NEON, sx + 0.05, top - 13.6, sx + 0.55, top - 4.4, -1.45, PINK if l == 2 else CYAN)
    # side walls of the building (alley faces) get windows for the 3/4 camera
    if CAM == "tq":
        for f in range(st):
            if f in rf:
                continue
            windows(x0, 0, f * FH, x1, DEPTH, (f + 1) * FH, p=0.35, sx=2.4, sz=FH, ww=1.0, wh=4.2, faces=(1, 3), zoff=1.8)


for l in range(8):
    building(l)

# ------------------------------------------------------------------ the links' physical structure (catwalks, risers)
set_sem(0.7, 0, 0)
STEEL = (0.22, 0.21, 0.26)
YF = -0.7          # links run just in front of the facade line
seen_h = set()
for e in LY["edges"]:
    pts = e["path"]
    for (xa, za), (xb, zb) in zip(pts, pts[1:]):
        key = (round(xa, 2), round(za, 2), round(xb, 2), round(zb, 2))
        if key in seen_h:
            continue
        seen_h.add(key)
        if abs(za - zb) < 1e-6:
            # catwalk / skybridge deck under the cable + a hand rail
            beam((xa, YF, za - 0.55), (xb, YF, za - 0.55), 0.5, STEEL)
            beam((xa, YF - 0.6, za + 0.9), (xb, YF - 0.6, za + 0.9), 0.12, (0.3, 0.3, 0.34))
            n = max(1, int(abs(xb - xa) / 1.4))
            for q in range(n + 1):
                xx = xa + (xb - xa) * q / n
                beam((xx, YF - 0.6, za - 0.3), (xx, YF - 0.6, za + 0.9), 0.1, (0.3, 0.3, 0.34))
        elif abs(xa - xb) < 1e-6:
            # a lift riser: two rails + rungs
            lo, hi = min(za, zb), max(za, zb)
            for s in (-0.45, 0.45):
                beam((xa + s, YF + 0.2, lo - 0.6), (xa + s, YF + 0.2, hi + 0.6), 0.16, STEEL)
            k = 0.0
            while lo + k < hi:
                beam((xa - 0.45, YF + 0.2, lo + k), (xa + 0.45, YF + 0.2, lo + k), 0.08, (0.3, 0.3, 0.34))
                k += 0.9
        else:
            beam((xa, YF, za - 0.4), (xb, YF, zb - 0.4), 0.35, STEEL)

# ------------------------------------------------------------------ the street, the cut below it, the far city
set_sem(0.2, 0, 0)
box(-20, -30, -9, 230, 60, 0, (0.16, 0.14, 0.2), facet=False)              # the ground block (cut face = y -30)
box(-20, -30, -0.6, 230, -18, 0.15, (0.2, 0.19, 0.24), facet=False)      # the far kerb strip seen edge-on
quad_y(NEON, -20, -0.35, 230, -0.2, -30.05, (0.55, 0.3, 0.9))              # lane glow on the road edge
# under the street: a utility conduit (cut) with a cable trough (the net literally runs under the street)
quad_y(SOLID, -20, -7.6, 230, -3.2, -30.04, (0.1, 0.09, 0.13))
for k in range(3):
    beam((-20, -30.3, -4.2 - k * 1.1), (230, -30.3, -4.2 - k * 1.1), 0.5, (0.32, 0.28, 0.3) if k != 1 else (0.24, 0.3, 0.34))
quad_y(NEON, -20, -6.9, 230, -6.75, -30.4, (0.2, 0.55, 0.65))
# foreground street furniture between the camera and the street (y < -20): lamp posts, a parked van, a fence
set_sem(0.2, 0, 0)
for lx in (52.0, 94.5, 136.0):
    beam((lx, -24, 0), (lx, -24, 10.5), 0.35, (0.08, 0.07, 0.1))
    beam((lx, -24, 10.5), (lx + 2.4, -24, 10.8), 0.25, (0.08, 0.07, 0.1))
    panel(lx + 1.6, 10.1, lx + 2.9, 10.4, -24.3, (1.0, 0.82, 0.55))
box(107.0, -27, 0.2, 116.0, -23, 3.6, (0.08, 0.07, 0.1), facet=False)        # van
box(108.0, -27, 3.6, 113.4, -23, 5.0, (0.08, 0.07, 0.1), facet=False)
panel(115.6, 1.6, 116.05, 2.3, -27.05, (1.0, 0.9, 0.7))
panel(106.95, 1.6, 107.4, 2.3, -27.05, RED)
for k in range(60):                                                           # a low fence
    xx = -10 + k * 4.0
    beam((xx, -21, 0), (xx, -21, 1.6), 0.12, (0.07, 0.06, 0.09))
beam((-10, -21, 1.5), (230, -21, 1.5), 0.12, (0.07, 0.06, 0.09))
# cars on the road (side silhouettes with head / tail lights)
for (cx, dirn, cc) in ((70.0, 1, PINK), (124.0, -1, CYAN), (160.0, 1, AMBER), (24.0, -1, (0.6, 0.4, 1.0))):
    box(cx - 2.6, -14, 0.4, cx + 2.6, -11, 1.5, (0.12, 0.1, 0.14), facet=False)
    box(cx - 1.4, -13.6, 1.5, cx + 1.4, -11.4, 2.3, (0.06, 0.06, 0.08), facet=False)
    panel(cx + dirn * 2.55 - 0.25, 0.8, cx + dirn * 2.55 + 0.25, 1.2, -14.05, WHITE)
    panel(cx - dirn * 2.55 - 0.25, 0.8, cx - dirn * 2.55 + 0.25, 1.2, -14.05, RED)
    quad_y(NEON, cx - 2.2, 0.25, cx + 2.2, 0.4, -14.05, cc)

# far city: two layers of skyline behind the street (haze makes the depth)
set_sem(0.85, 0, 0)
for layer, (y0, hmin, hmax, p) in enumerate(((24, 22, 62, 0.22), (70, 36, 96, 0.12))):
    x = -20.0
    while x < 225:
        w = rng.uniform(8, 18)
        h = rng.uniform(hmin, hmax)
        c = tuple(v * (0.42 if layer else 0.6) for v in rng.choice(FAMS))
        box(x, y0, 0, x + w, y0 + w, h, c, facet=layer == 0)
        windows(x, y0, 0, x + w, y0 + w, h, p=p, sx=2.2, sz=3.0, ww=1.0, wh=1.4, faces=(0,))
        if rng.random() < 0.35:
            roof_trim(x + 0.2, y0 + 0.2, x + w - 0.2, y0 + w - 0.2, h + 0.1, rng.choice(TRIMS), w=0.3)
        if rng.random() < 0.3:
            beam((x + w / 2, y0 + w / 2, h), (x + w / 2, y0 + w / 2, h + rng.uniform(4, 10)), 0.25, (0.2, 0.2, 0.22))
        x += w + rng.uniform(0.5, 4)
# a sky lane far behind: streaks of fast cars
for k in range(26):
    y = 50 + rng.uniform(-4, 4)
    z = rng.choice([58, 64, 86]) + rng.uniform(-1, 1)
    x = rng.uniform(-10, 220)
    ln = rng.uniform(3, 9)
    quad_y(NEON, x, z, x + ln, z + 0.25, y, rng.choice([PINK, CYAN, AMBER, (0.6, 0.4, 1.0), (0.4, 1.0, 0.7)]))

solid = SOLID.obj(TOON)
neon = NEON.obj(NEONM)
win = WIN.obj(WINM)

# ------------------------------------------------------------------ camera
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_end = 2000
if CAM == "side":
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 192.0
    cam.location = (96.0, -400.0, (930.0 - 540.0) / 10.0)
    cam.rotation_euler = (math.radians(90), 0, 0)
else:
    cfg = json.load(open(os.path.join(os.path.dirname(LAYOUT), "tq_cam.json"))) if os.path.exists(
        os.path.join(os.path.dirname(LAYOUT), "tq_cam.json")) else {}
    cam_data.type = "PERSP"
    cam_data.lens = cfg.get("lens", 32)
    cam.location = tuple(cfg.get("loc", (205.0, -95.0, 40.0)))
    tgt = Vector(cfg.get("tgt", (110.0, 6.0, 34.0)))
    cam.rotation_euler = (tgt - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
    cam_data.shift_x = cfg.get("shift_x", 0.0)
    cam_data.shift_y = cfg.get("shift_y", 0.0)
bpy.context.view_layer.update()


def proj(p):
    v = world_to_camera_view(scene, cam, Vector(p))
    return (round(v.x * 1920, 2), round((1 - v.y) * 1080, 2))


anchors = dict(rooms={}, edges=[])
for i, n in LY["nodes"].items():
    x0, z0, x1, z1 = n["room"]
    anchors["rooms"][i] = dict(front=[proj((x0, 0, z0)), proj((x1, 0, z0)), proj((x1, 0, z1)), proj((x0, 0, z1))],
                               back=[proj((x0, DEPTH - 0.6, z0)), proj((x1, DEPTH - 0.6, z0)),
                                     proj((x1, DEPTH - 0.6, z1)), proj((x0, DEPTH - 0.6, z1))])
for e in LY["edges"]:
    anchors["edges"].append(dict(a=e["a"], b=e["b"], pts=[proj((x, YF, z)) for x, z in e["path"]]))
anchors["ground"] = [proj((0, 0, 0)), proj((200, 0, 0))]
with open(os.path.join(OUTDIR, "anchors_%s.json" % TAG), "w") as f:
    json.dump(anchors, f, indent=1)


def render(path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path, flush=True)


render(os.path.join(OUTDIR, "%s_beauty_night.png" % TAG))
if PREVIEW:
    print("DONE", flush=True)
    sys.exit(0)
blackm = mat_flat("black", (0.0, 0.0, 0.0))
solid.data.materials[0] = blackm
bg.inputs["Color"].default_value = (0, 0, 0, 1)
render(os.path.join(OUTDIR, "%s_glow_night.png" % TAG))
solid.data.materials[0] = TOON


def override_mat(kind):
    m = bpy.data.materials.new("ov_" + kind)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    L = nt.links.new
    if kind == "normal":
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        vm = nt.nodes.new("ShaderNodeVectorMath")
        vm.operation = "MULTIPLY_ADD"
        vm.inputs[1].default_value = (0.5, 0.5, 0.5)
        vm.inputs[2].default_value = (0.5, 0.5, 0.5)
        L(geo.outputs["Normal"], vm.inputs[0])
        L(vm.outputs[0], em.inputs["Color"])
    elif kind == "id":
        a = attr(nt, "bid")
        oi = nt.nodes.new("ShaderNodeObjectInfo")
        mx = nt.nodes.new("ShaderNodeMix")
        mx.data_type = "RGBA"
        mx.blend_type = "ADD"
        mx.inputs["Factor"].default_value = 1.0
        L(a.outputs["Color"], mx.inputs[6])
        cc = nt.nodes.new("ShaderNodeCombineColor")
        L(oi.outputs["Random"], cc.inputs[0])
        L(oi.outputs["Random"], cc.inputs[2])
        L(cc.outputs[0], mx.inputs[7])
        L(mx.outputs[2], em.inputs["Color"])
    elif kind == "depth":
        cd = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = 600.0
        L(cd.outputs["View Distance"], mr.inputs["Value"])
        L(mr.outputs[0], em.inputs["Color"])
    elif kind == "sem":
        a = attr(nt, "sem")
        L(a.outputs["Color"], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m


scene.eevee.taa_render_samples = 1
for kind in ("normal", "id", "depth", "sem"):
    bpy.context.view_layer.material_override = override_mat(kind)
    bg.inputs["Color"].default_value = (1, 1, 1, 1) if kind == "depth" else (0, 0, 0, 1)
    if kind == "sem":
        try:
            scene.view_settings.view_transform = "Raw"
        except TypeError:
            pass
    render(os.path.join(OUTDIR, "%s_%s.png" % (TAG, kind)))
bpy.context.view_layer.material_override = None
print("DONE", flush=True)
