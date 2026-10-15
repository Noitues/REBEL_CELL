"""V3 AAA: the V3 dynamic street (same layout, same seeded build stream) re-lit for path tracing (Blender 5.2, Cycles CPU).

blender -b --factory-startup --python scene_aaa.py -- <job.json>

job adds: "look": "cel" | "real" | "hybrid", "vol_res": [w, h], "data_res": [w, h], "room_k": {node: light multiplier},
"power": {"keep": [node ids], "k": 0.25} (the hover power cut, done in 3D: emitters outside the branch drop to k).
Per shot it writes (in "out"):
  <shot>_main.exr   Cycles surfaces, denoised (OIDN): Combined, Emit, Denoising Albedo, Depth (no volume objects)
  <shot>_vol.exr    Cycles volumes only, half res: every surface is a holdout for camera rays (it still blocks light
                    and still emits), so Combined = in-scattered light up to the first surface (real god rays)
  <shot>_normal / _id / _depth / _sem / _wz.png (Eevee data passes for ink, masks and fog, as in V3 dynamic)
  anchors_<shot>.json (rooms, links, camera; projected at 1920 x 1080 like V3 dynamic so the overlay code is reused)
The extra dressing (dress_aaa.py) and the lights and volumes (light_aaa.py) are exec'd into this namespace AFTER the
V3 dynamic build, each with its own seeded stream, so the shared rng stream (4207) and the layout stay identical.

The V3 dynamic notes follow.
blender -b --factory-startup --python scene3.py -- <job.json>

Builds once, then renders every shot of the job (camera pose + animation time t) with the round 30-35 passes:
  <shot>_beauty.png  (toon city + neon + additive atmosphere: shafts, searchlights, sky traffic trails, steam)
  <shot>_glow.png    (emissive only, atmosphere hidden)
  <shot>_normal / _id / _depth / _sem / _wz.png (data passes for ink, haze, fog and the post masks)
  anchors_<shot>.json (rooms, links, hidden foreground occluders, all projected by Blender)
job: {"layout": path, "out": dir, "res": [w, h], "samples": n, "passes": [...], "mode": "shots"|"sheet",
      "shots": [{"name", "pose": {loc, tgt, lens, shift_x, shift_y}, "t", "protect": [node ids]}]}
sem (Raw): R = class (0.1 route facade, 0.2 ground, 0.3 cut, 0.5 room, 0.6 mid-row building, 0.7 link structure,
0.85 far city, 0.95 foreground occluder), G = room index / 32, B = column / 10. All randomness is seeded.
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
JOB = json.load(open(argv[0]))
LY = json.load(open(JOB["layout"]))
OUTDIR = JOB["out"]
MODE = JOB.get("mode", "shots")
os.makedirs(OUTDIR, exist_ok=True)
C = LY["const"]
FH, SLAB, DEPTH, YF = C["FLOOR_H"], C["SLAB"], C["DEPTH"], C["YF"]
rng = random.Random(int(JOB.get("build_seed", 4207)))     # r3: the proof plate builds another street

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
LOOK = JOB.get("look", "cel")
HERE = os.path.dirname(os.path.abspath(__file__))
JIT_K = 0.0 if LOOK == "real" else 1.0      # facet jitter (the rng calls still happen, so the stream is unchanged)
EEVEE = "BLENDER_EEVEE"
try:
    scene.render.engine = EEVEE
except TypeError:
    EEVEE = "BLENDER_EEVEE_NEXT"
    scene.render.engine = EEVEE
scene.render.resolution_x, scene.render.resolution_y = JOB["res"]
scene.render.resolution_percentage = 100
SAMPLES = JOB.get("samples", 16)
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_depth = "16"
scene.render.film_transparent = False
W_OUT, H_OUT = 1920.0, 1080.0

AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)
VIOLET = (0.6, 0.4, 1.0)
LIME = (0.83, 1.0, 0.0)
MERIDIAN = (0.86, 0.42, 0.10)
TYPE_LIGHT = {"router": (0.36, 0.88, 1.0), "elite": (1.0, 0.38, 0.16), "terminal": (0.24, 1.0, 0.55),
              "modem": (0.35, 0.59, 1.0), "rack": (1.0, 0.77, 0.24), "target": (1.0, 0.17, 0.24), "start": LIME}
OFF = [0.0, 0.0, 0.0]          # translation applied to every face built (route columns sit at their own depth)


# ------------------------------------------------------------------ geometry accumulator (round 30 kit + sem layer)
class Acc:
    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.col = self.bm.faces.layers.float_color.new("col")
        self.fj = self.bm.faces.layers.float.new("fj")
        self.bid = self.bm.faces.layers.float_color.new("bid")
        self.sem = self.bm.faces.layers.float_color.new("sem")
        self.n = 0

    def face(self, pts, col, bid, fj=None, sem=None):
        vs = [self.bm.verts.new((p[0] + OFF[0], p[1] + OFF[1], p[2] + OFF[2])) for p in pts]
        try:
            f = self.bm.faces.new(vs)
        except ValueError:
            return None
        f[self.col] = (col[0], col[1], col[2], 1.0)
        f[self.fj] = rng.random() if fj is None else fj
        f[self.bid] = (bid[0], bid[1], bid[2], 1.0)
        s = sem or SEM
        f[self.sem] = (s[0], s[1], s[2], 1.0)
        self.n += 1
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
        P = A.lerp(B, u).lerp(D.lerp(Cc, u), v) + n * rng.uniform(-jit, jit) * size * JIT_K
        for p, q in ((A, B), (B, Cc), (Cc, D), (D, A)):
            self.face([tuple(p), tuple(q), tuple(P)], col, bid)

    def obj(self, mat, name=None):
        me = bpy.data.meshes.new(name or self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(name or self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(mat)
        for p in me.polygons:
            p.use_smooth = False
        return ob


class AtmosAcc:
    """Additive atmosphere meshes: per-corner colour (premultiplied fade) so beams and plumes fade along their length."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.col = self.bm.loops.layers.float_color.new("acol")

    def quad(self, pts, cols):
        vs = [self.bm.verts.new(p) for p in pts]
        try:
            f = self.bm.faces.new(vs)
        except ValueError:
            return
        for lp, c in zip(f.loops, cols):
            lp[self.col] = (c[0], c[1], c[2], 1.0)

    def obj(self, mat, name=None):
        me = bpy.data.meshes.new(name or self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(name or self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(mat)
        return ob


SEM = (0.1, 0.0, 0.0)


def set_sem(cls, room=0, col=0):
    global SEM
    SEM = (cls, room / 32.0, col / 10.0)


SOLID = Acc("solid")
NEON = Acc("neon")
WIN = Acc("win")
SOLID_OBJS, NEON_OBJS, ATMOS_OBJS, FG_OBJS = [], [], [], {}


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


def beam(p0, p1, w, col, acc=None, bid=None, h=None):
    acc = acc or SOLID
    p0, p1 = Vector(p0), Vector(p1)
    if (p1 - p0).length < 1e-4:
        return
    d = (p1 - p0).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    a = d.cross(up).normalized() * (w / 2)
    b = d.cross(a).normalized() * ((h if h is not None else w) / 2)
    c0 = [p0 + a + b, p0 - a + b, p0 - a - b, p0 + a - b]
    c1 = [p1 + a + b, p1 - a + b, p1 - a - b, p1 + a - b]
    bid = bid or rid()
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(c0[i]), tuple(c0[j]), tuple(c1[j]), tuple(c1[i])], col, bid)
    acc.face([tuple(v) for v in c1], col, bid)
    acc.face([tuple(v) for v in reversed(c0)], col, bid)


def tube(p0, p1, r, col, acc=None, n=8, bid=None, open_top=False):
    """An n-gon tube (faceted) from p0 to p1. open_top drops the upper faces (a cut half-tube)."""
    acc = acc or SOLID
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0).normalized()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    a = d.cross(up).normalized()
    b = d.cross(a).normalized()
    bid = bid or rid()
    ring = []
    for k in range(n):
        t = 2 * math.pi * (k + 0.5) / n
        ring.append(a * math.cos(t) * r + b * math.sin(t) * r)
    for k in range(n):
        j = (k + 1) % n
        mid = (ring[k] + ring[j]) / 2
        if open_top and mid.dot(Vector((0, 0, 1))) > 0.2 * r:
            continue
        acc.face([tuple(p0 + ring[k]), tuple(p0 + ring[j]), tuple(p1 + ring[j]), tuple(p1 + ring[k])], col, bid)


def quad_y(acc, x0, z0, x1, z1, y, col, bid=(0, 0, 0)):
    acc.face([(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)], col, bid)


def quad_x(acc, x, y0, z0, y1, z1, col, bid=(0, 0, 0)):
    acc.face([(x, y1, z0), (x, y0, z0), (x, y0, z1), (x, y1, z1)], col, bid)


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
            for kk in range(nz):
                if rng.random() > p:
                    continue
                c = rng.choice(cols)
                s = (0.5 + 0.5 * rng.random()) * k
                c = (c[0] * s, c[1] * s, c[2] * s)
                t0 = off + i * sx + (sx - ww) / 2
                z = z0 + zoff + kk * sz
                pa = (ax + ux * t0, ay + uy * t0)
                pb = (ax + ux * (t0 + ww), ay + uy * (t0 + ww))
                WIN.face([(pa[0], pa[1], z), (pb[0], pb[1], z), (pb[0], pb[1], z + wh), (pa[0], pa[1], z + wh)], c, (0, 0, 0))


def roof_trim(x0, y0, x1, y1, z, col, w=0.3):
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        beam((a[0], a[1], z), (b[0], b[1], z), w, col, acc=NEON)


# r2: alternate building shapes + the Sink / OwnRng helpers that keep the shared stream 4207 unchanged
exec(compile(open(os.path.join(HERE, "shapes_lib_r2.py")).read(), "shapes_lib_r2.py", "exec"), globals())


# ------------------------------------------------------------------ materials (round 30 toon + glow + additive air)
def attr(nt, name, kind="GEOMETRY"):
    n = nt.nodes.new("ShaderNodeAttribute")
    n.attribute_type = kind
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


def mat_air(name, noise=False):
    """Additive: transparent + emission(corner colour [x noise]). Beams, shafts, trails, steam."""
    m = bpy.data.materials.new(name)
    for prop, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
        try:
            setattr(m, prop, val)
        except (AttributeError, TypeError):
            pass
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    em = nt.nodes.new("ShaderNodeEmission")
    add = nt.nodes.new("ShaderNodeAddShader")
    col = attr(nt, "acol")
    src = col.outputs["Color"]
    if noise:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 0.22
        nz.inputs["Detail"].default_value = 4.0
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.42
        mr.inputs["From Max"].default_value = 0.75
        mul = nt.nodes.new("ShaderNodeVectorMath")
        mul.operation = "SCALE"
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        nt.links.new(nz.outputs["Fac"], mr.inputs["Value"])
        nt.links.new(src, mul.inputs[0])
        nt.links.new(mr.outputs[0], mul.inputs["Scale"])
        src = mul.outputs[0]
    nt.links.new(src, em.inputs["Color"])
    nt.links.new(tr.outputs[0], add.inputs[0])
    nt.links.new(em.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], out.inputs[0])
    return m


exec(compile(open(os.path.join(HERE, "mats_aaa.py")).read(), "mats_aaa.py", "exec"), globals())

FAMS = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36), (0.40, 0.38, 0.46)]
CUT = (0.15, 0.13, 0.19)
# AAA palette lock (CRITIQUE §3 #3c): magenta / cyan district pair + violet, pink, red; no lime, orange, yellow or
# white trims (those are the route's state colours). Same list length, so the seeded choices are unchanged.
TRIMS = [(1.0, 0.16, 0.54), (0.16, 0.83, 1.0), (0.54, 0.24, 1.0), (1.0, 0.3, 0.65), (1.0, 0.16, 0.16)]
ROOM_IDX = {}
for _n, _i in enumerate(sorted(LY["nodes"], key=lambda i: (LY["nodes"][i]["layer"], LY["nodes"][i]["k"]))):
    ROOM_IDX[_i] = _n + 1


# ------------------------------------------------------------------ rooms (round 35 hq_climb lineage, parent V3)
def light_strip(x0, x1, z, y0, y1, col):
    NEON.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], col, (0, 0, 0))


def panel(x0, z0, x1, z1, y, col):
    quad_y(NEON, x0, z0, x1, z1, y, col)


WARM_ROOMS = {"L4_0": (0.0, 0.7, 1.0)}


def room(i, n):
    x0, z0, x1, z1 = n["room"]
    kind = n["kind"]
    lc = TYPE_LIGHT[kind]
    # r2: option 1 (a cyan fight room) read like the cool ahead rooms: a deeper, saturated cyan monitor wall over a
    # warm floor and a warm ceiling strip, so it reads as a lit, warm-keyed option (colours only: no rng change)
    warm = i in WARM_ROOMS
    if warm:
        lc = WARM_ROOMS[i]
    set_sem(0.5, ROOM_IDX[i], n["layer"])
    yb = DEPTH - 0.6
    inner = (0.22, 0.2, 0.26)
    quad_y(SOLID, x0, z0, x1, z1, yb, inner)
    quad_y(NEON, x0 + 0.3, z0 + 0.3, x1 - 0.3, z1 - 0.3, yb - 0.02, tuple(v * 0.16 for v in lc))
    box(x0 - 0.02, 0.6, z0, x0, yb, z1, inner, facet=False, top=False)
    box(x1, 0.6, z0, x1 + 0.02, yb, z1, inner, facet=False, top=False)
    box(x0, 0.0, z0 - 0.02, x1, yb, z0, (0.3, 0.28, 0.32), facet=False)
    NEON.face([(x0 + 1.0, 0.4, z0 + 0.02), (x1 - 1.0, 0.4, z0 + 0.02), (x1 - 1.0, yb - 1.0, z0 + 0.02), (x0 + 1.0, yb - 1.0, z0 + 0.02)],
              tuple(v * 0.22 for v in lc) if not warm else (0.42, 0.2, 0.06), (0, 0, 0))
    light_strip(x0 + 1.2, x1 - 1.2, z1 - 0.05, 2.0, 3.0, tuple(min(1, v * 1.2) for v in lc) if not warm else (1.0, 0.72, 0.42))
    cx = (x0 + x1) / 2
    zf = z0
    yk = yb - 0.4
    W = x1 - x0
    if kind == "start":
        box(x0 + 1.0, yk - 3.0, zf, x0 + 5.2, yk - 1.2, zf + 1.4, (0.36, 0.28, 0.22), facet=False)
        for q, (dx, dz) in enumerate(((0.0, 1.4), (1.6, 1.4), (0.8, 2.9))):
            box(x0 + 1.4 + dx, yk - 2.4, zf + dz, x0 + 2.9 + dx, yk - 1.3, zf + dz + 1.4, (0.16, 0.16, 0.18), facet=False)
            panel(x0 + 1.55 + dx, zf + dz + 0.2, x0 + 2.75 + dx, zf + dz + 1.2, yk - 2.45, LIME if q != 1 else CYAN)
        box(cx + 0.6, yk - 2.0, zf, x1 - 1.0, yk - 0.6, zf + 1.2, (0.5, 0.18, 0.3), facet=False)
        box(cx + 0.6, yk - 0.9, zf + 1.2, x1 - 1.0, yk - 0.6, zf + 2.4, (0.5, 0.18, 0.3), facet=False)
        panel(cx + 1.2, zf + 3.2, cx + 3.4, zf + 5.6, yk + 0.25, PINK)
    elif kind == "router":
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
            box(cx + 1.4 + c * 1.2, yk - 3.2, zf + 1.6, cx + 2.2 + c * 1.2, yk - 2.6, zf + 2.2,
                rng.choice([(0.8, 0.3, 0.5), (0.3, 0.7, 0.8), (0.9, 0.7, 0.2)]), facet=False)
        panel(cx + 1.2, z1 - 1.4, x1 - 0.8, z1 - 0.6, yk + 0.25, (0.3, 0.55, 1.0))
    elif kind in ("rack", "target"):
        n_ = 4 if kind == "rack" else 5
        span = W - 1.6
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
    v = (t * 5 + i * 3) % 8
    if v == 0:
        for k in range(2):
            beam((x0 + 0.6, yb - 0.3, z1 - 0.8 - k * 0.5), (x1 - 0.6, yb - 0.3, z1 - 0.8 - k * 0.5), 0.26, (0.5, 0.45, 0.4))
        panel(x1 - 1.4, z1 - 1.5, x1 - 0.9, z1 - 1.0, yb - 0.5, RED)
    elif v == 1:
        beam((x0 + 1.4, 1.5, z1), (x0 + 1.4, 1.5, z1 - 1.2), 0.06, (0.1, 0.1, 0.1))
        panel(x0 + 1.15, z1 - 1.6, x0 + 1.65, z1 - 1.2, 1.45, (1.0, 0.85, 0.5))
    elif v == 2:
        box(x1 - 2.4, 1.2, zf, x1 - 0.8, 2.4, zf + 0.5, (0.86, 0.62, 0.10), facet=False)
        beam((x1 - 0.9, 1.8, zf + 0.5), (x1 - 0.6, 1.8, zf + 2.0), 0.15, (0.2, 0.2, 0.22))
    elif v == 3:
        for k in range(2):
            box(x1 - 2.4 + k * 0.9, 1.0, zf, x1 - 1.6 + k * 0.9, 1.8, zf + 1.3, (0.16, 0.36, 0.62) if k % 2 else RED, facet=False)
    elif v == 4:
        panel(x0 + 0.8, zf + 1.6, x0 + 1.4, zf + 2.0, 1.2, (1.0, 0.85, 0.5))
    elif v == 5:
        for k in range(3):
            box(x0 + 1.0 + k * 1.3, yb - 2.2, z1 - 1.4, x0 + 2.0 + k * 1.3, yb - 1.3, z1 - 0.6, (0.6, 0.5, 0.34))
    elif v == 6:
        panel(x0 + 0.8, z1 - 2.6, x0 + 2.0, z1 - 1.4, yb - 0.45, (0.3, 0.6, 1.0))
        beam((x0 + 0.6, yb - 0.4, z1 - 0.5), (x1 - 0.6, yb - 0.4, z1 - 0.5), 0.3, (0.3, 0.3, 0.32))
    else:
        box(x1 - 1.6, 1.4, zf, x1 - 0.9, 2.1, zf + 0.7, (0.86, 0.62, 0.10), facet=False)


# ------------------------------------------------------------------ silhouettes (shared by the route row, mid row, sheet)
def blade_sign(x, y, z0, z1, col, side=1):
    """A vertical neon blade sign sticking out of a facade edge toward the street."""
    box(x - 0.3, y - 2.6, z0, x + 0.3, y, z1, (0.12, 0.1, 0.14), facet=False)
    quad_x(NEON, x - 0.32, y - 2.4, z0 + 0.4, y - 0.2, z1 - 0.4, col)
    quad_x(NEON, x + 0.32, y - 2.4, z0 + 0.4, y - 0.2, z1 - 0.4, col)
    quad_y(NEON, x - 0.25, z0 + 0.4, x + 0.25, z1 - 0.4, y - 2.62, tuple(v * 0.8 for v in col))


def billboard_panel(x0, x1, z0, z1, y, palette, seed):
    """An emissive billboard face: two-tone stripes, a disc logo, a scan bar."""
    r = random.Random(seed)
    c1, c2 = palette
    quad_y(SOLID, x0 - 0.4, z0 - 0.4, x1 + 0.4, z1 + 0.4, y + 0.05, (0.08, 0.07, 0.1))
    quad_y(NEON, x0, z0, x1, z1, y - 0.02, tuple(v * 0.22 for v in c1))
    n = 5
    for k in range(n):
        if r.random() < 0.6:
            za = z0 + (z1 - z0) * k / n + 0.25
            quad_y(NEON, x0 + 0.6, za, x0 + (x1 - x0) * r.uniform(0.35, 0.6), za + (z1 - z0) / n * 0.5, y - 0.05, c2)
    cx, cz = x0 + (x1 - x0) * 0.76, (z0 + z1) / 2
    rr = min(x1 - x0, z1 - z0) * 0.3
    for k in range(8):
        a0, a1 = 2 * math.pi * k / 8, 2 * math.pi * (k + 1) / 8
        NEON.face([(cx, y - 0.06, cz), (cx + rr * math.cos(a0), y - 0.06, cz + rr * math.sin(a0)),
                   (cx + rr * math.cos(a1), y - 0.06, cz + rr * math.sin(a1))], c1, (0, 0, 0))


def lattice(x0, x1, y0, y1, z0, z1, col=(0.18, 0.17, 0.22), step=4.0):
    for x in (x0, x1):
        for y in (y0, y1):
            beam((x, y, z0), (x, y, z1), 0.45, col)
    z = z0
    while z < z1 - 0.1:
        za = min(z1, z + step)
        for (ax, ay), (bx, by) in (((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x0, y0), (x0, y1)), ((x1, y0), (x1, y1))):
            beam((ax, ay, za), (bx, by, za), 0.25, col)
        beam((x0, y0, z), (x1, y0, za), 0.18, col)
        beam((x1, y0, z), (x0, y0, za), 0.18, col)
        z = za


def setback_tiers(x0, x1, y0, y1, z, tiers, col, win_p=0.35):
    for t in range(tiers):
        inset = 1.6 * (t + 1)
        h = FH * (2 if t < tiers - 1 else 1.5)
        a0, a1, b0, b1 = x0 + inset, x1 - inset, y0 + inset * 0.8, y1 - inset * 0.5
        if a1 - a0 < 3:
            break
        box(a0, b0, z, a1, b1, z + h, tuple(v * (0.96 - 0.04 * t) for v in col))
        windows(a0, b0, z, a1, b1, z + h, p=win_p, sx=2.2, sz=FH, ww=1.0, wh=2.6, zoff=2.4, k=0.8, faces=(0, 1, 3))
        roof_trim(a0 + 0.1, b0 + 0.1, a1 - 0.1, b1 - 0.1, z + h + 0.05, TRIMS[(t + int(x0)) % len(TRIMS)], w=0.22)
        z += h
    return z


def spire(x, y, z, h, beacon=RED):
    beam((x, y, z), (x, y, z + h), 0.35, (0.28, 0.28, 0.32))
    beam((x - 1.2, y, z + h * 0.35), (x + 1.2, y, z + h * 0.35), 0.18, (0.28, 0.28, 0.32))
    panel(x - 0.45, z + h - 0.4, x + 0.45, z + h + 0.5, y - 0.3, beacon)


def parking(x0, x1, y0, y1, decks, col=(0.30, 0.29, 0.34), seed=3, lights=True):
    """Open-sided parking structure: slabs on columns, low parapets, a ramp, parked cars, deck light strips."""
    r = random.Random(seed)
    dh = 4.4
    for d in range(decks + 1):
        z = d * dh
        box(x0, y0, z - 0.5, x1, y1, z + 0.1, col, facet=False)
        if d < decks:
            nx = max(2, int((x1 - x0) / 5.0))
            for k in range(nx + 1):
                xx = x0 + 0.3 + (x1 - x0 - 0.6) * k / nx
                beam((xx, y0 + 0.4, z), (xx, y0 + 0.4, z + dh - 0.5), 0.5, tuple(v * 0.8 for v in col))
                beam((xx, y1 - 0.4, z), (xx, y1 - 0.4, z + dh - 0.5), 0.5, tuple(v * 0.8 for v in col))
            if lights:
                quad_y(NEON, x0 + 0.6, z + dh - 0.62, x1 - 0.6, z + dh - 0.52, y0 + 0.8, (0.75, 0.85, 1.0))
            for k in range(int((x1 - x0) / 4.5)):
                if r.random() < 0.55:
                    cx = x0 + 2.2 + k * 4.5
                    cc = r.choice([(0.6, 0.15, 0.25), (0.15, 0.3, 0.5), (0.5, 0.5, 0.55), (0.2, 0.2, 0.22)])
                    _sk = Sink()        # r2: no parked cars either
                    _sk.__enter__()
                    box(cx - 1.5, y0 + 2.0, z + 0.1, cx + 1.5, y0 + 5.0, z + 1.2, cc, facet=False)
                    box(cx - 0.9, y0 + 2.4, z + 1.2, cx + 0.9, y0 + 4.6, z + 1.8, tuple(v * 0.6 for v in cc), facet=False)
                    if lights:
                        panel(cx - 1.4, z + 0.5, cx - 1.0, z + 0.8, y0 + 1.98, RED)
                        panel(cx + 1.0, z + 0.5, cx + 1.4, z + 0.8, y0 + 1.98, RED)
                    _sk.__exit__()
        if d > 0:
            box(x0, y0 - 0.1, z + 0.1, x1, y0 + 0.3, z + 1.0, tuple(v * 1.1 for v in col), facet=False)
    # ramp seen through the open side
    for d in range(decks):
        z = d * dh
        beam((x0 + 2, (y0 + y1) / 2 + 1, z + 0.3), (x1 - 2, (y0 + y1) / 2 + 1, z + dh - 0.2), 2.4, (0.26, 0.25, 0.3), h=0.4)
    quad_y(NEON, x0 + 1, decks * dh + 0.6, x0 + 6, decks * dh + 2.2, y0 - 0.2, (0.3, 0.55, 1.0))
    return decks * dh


def footbridge_block(x0, x1, y0, h0, x2, x3, y2, h1, bz, col):
    """Two blocks linked by an enclosed pedestrian footbridge (window band lit)."""
    box(x0, y0, 0, x1, y0 + 12, h0, col)
    windows(x0, y0, 0, x1, y0 + 12, h0, p=0.3, sx=2.2, sz=FH / 2, ww=1.0, wh=1.6, zoff=2.0, k=0.7, faces=(0, 1, 3))
    box(x2, y2, 0, x3, y2 + 12, h1, tuple(v * 0.92 for v in col))
    windows(x2, y2, 0, x3, y2 + 12, h1, p=0.3, sx=2.2, sz=FH / 2, ww=1.0, wh=1.6, zoff=2.0, k=0.7, faces=(0, 1, 3))
    ya, yb = y0 + 3, y0 + 8
    box(x1, ya, bz, x2, yb, bz + 3.6, (0.24, 0.23, 0.28), facet=False)
    quad_y(NEON, x1 + 0.4, bz + 1.2, x2 - 0.4, bz + 2.6, ya - 0.05, (0.55, 0.8, 1.0))
    box(x1, ya - 0.3, bz - 0.4, x2, yb + 0.3, bz, (0.18, 0.17, 0.22), facet=False)
    for xx in (x1 + (x2 - x1) * 0.5,):
        beam((xx, (ya + yb) / 2, 0), (xx, (ya + yb) / 2, bz - 0.4), 0.8, (0.2, 0.19, 0.24))
    roof_trim(x0 + 0.1, y0 + 0.1, x1 - 0.1, y0 + 11.9, h0 + 0.05, CYAN, 0.22)
    roof_trim(x2 + 0.1, y2 + 0.1, x3 - 0.1, y2 + 11.9, h1 + 0.05, PINK, 0.22)


def billboard_frame(x0, x1, y, z0, z1, pz0, pz1, palette, seed):
    """A standalone steel lattice frame holding a big billboard."""
    lattice(x0 + 1, x0 + 3, y, y + 2, 0, pz0, step=4.4)
    lattice(x1 - 3, x1 - 1, y, y + 2, 0, pz0, step=4.4)
    beam((x0, y - 0.4, pz0 - 0.4), (x1, y - 0.4, pz0 - 0.4), 0.8, (0.2, 0.19, 0.24))
    billboard_panel(x0 + 0.5, x1 - 0.5, pz0 + 0.6, pz1, y - 0.6, palette, seed)
    for k in range(5):
        xx = x0 + 1 + (x1 - x0 - 2) * k / 4
        beam((xx, y - 1.6, pz0 + 0.2), (xx, y - 2.6, pz0 + 1.0), 0.15, (0.25, 0.25, 0.28))
        panel(xx - 0.25, pz0 + 0.95, xx + 0.25, pz0 + 1.2, y - 2.7, (1.0, 0.9, 0.7))


def tower(x0, x1, y0, y1, h, col, crown=CYAN, seed=0):
    box(x0, y0, 0, x1, y1, h, col)
    windows(x0, y0, 0, x1, y1, h, p=0.32, sx=2.0, sz=FH / 2, ww=0.9, wh=1.8, zoff=1.8, k=0.75, faces=(0, 1, 3))
    for k in range(int(h / 16)):
        quad_y(NEON, x0 + 0.4, 6 + k * 16, x1 - 0.4, 6.25 + k * 16, y0 - 0.08, tuple(v * 0.6 for v in crown))
    box(x0 + 1.2, y0 + 1.2, h, x1 - 1.2, y1 - 1.2, h + 4, tuple(v * 0.85 for v in col))
    roof_trim(x0 + 1.3, y0 + 1.3, x1 - 1.3, y1 - 1.3, h + 4.05, crown, 0.25)
    spire((x0 + x1) / 2, (y0 + y1) / 2, h + 4, 10 + (seed % 3) * 4)


def slab(x0, x1, y0, y1, h, col, sign=None):
    box(x0, y0, 0, x1, y1, h, col)
    windows(x0, y0, 0, x1, y1, h, p=0.4, sx=2.2, sz=FH / 2, ww=1.2, wh=1.6, zoff=1.6, k=0.7, faces=(0, 1, 3))
    for k in range(3):
        box(x0 + 2 + k * 5, y0 + 3, h, x0 + 5 + k * 5, y0 + 6, h + 2.2, (0.3, 0.3, 0.34), facet=False)
    roof_trim(x0 + 0.1, y0 + 0.1, x1 - 0.1, y1 - 0.1, h + 0.05, sign or AMBER, 0.25)


# ------------------------------------------------------------------ route buildings (column l)
ROUTE_FLOORS = {}
for i, n in LY["nodes"].items():
    ROUTE_FLOORS.setdefault(int(n["layer"]), {})[n["floor"]] = i


DRUM_COL = 5          # r2: the route column rebuilt as a cut drum (shapes_r2.py)


def building(l):
    x0, x1 = LY["cols"][str(l)]
    st = LY["storeys"][str(l)]
    arch = LY["arch"][str(l)]
    OFF[1] = LY["dy"][l]
    top = st * FH
    c = FAMS[(l * 3 + 1) % len(FAMS)] if l != 7 else (0.34, 0.3, 0.36)
    fb = rid()
    rf = ROUTE_FLOORS.get(l, {})
    for f in range(st):
        za, zb = f * FH, (f + 1) * FH
        if f in rf:
            set_sem(0.3, 0, l)
            box(x0, 0, za - SLAB / 2 if f else 0, x1, DEPTH, za + SLAB / 2, CUT, facet=False, bid=fb)
            box(x0, 0, zb - SLAB / 2, x1, DEPTH, zb + SLAB / 2 if f < st - 1 else zb, CUT, facet=False, bid=fb)
            box(x0, 0, za, x0 + 0.7, DEPTH, zb, CUT, facet=False, bid=fb)
            box(x1 - 0.7, 0, za, x1, DEPTH, zb, CUT, facet=False, bid=fb)
            room(rf[f], LY["nodes"][rf[f]])
        else:
          with (Sink() if l == DRUM_COL else _nullctx()):     # r2: the drum replaces the box floors
            set_sem(0.1, 0, l)
            box(x0, 0, za, x1, DEPTH, zb, c, bid=fb, top=(f == st - 1))
            p = 0.4 if l != 7 else 0.6
            cols = None if l != 7 else [(1.0, 0.2, 0.12), (1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (0.9, 0.9, 1.0)]
            if l != 7:
                windows(x0, 0, za, x1, DEPTH, zb, p=p * 0.8, sx=2.15, sz=FH, ww=1.1, wh=3.0, cols=cols, zoff=2.6, k=0.45)
            else:
                # the TARGET tower: small dim slit windows (own seeded stream; the shared stream is consumed as before)
                global WIN
                real = WIN
                WIN = Acc("dummy")
                windows(x0, 0, za, x1, DEPTH, zb, p=p * 0.8, sx=2.15, sz=FH, ww=1.1, wh=3.0, cols=cols, zoff=2.6, k=0.38)
                WIN = real
                keep_state = rng.getstate()
                rng.seed(700 + f)
                windows(x0, 0, za, x1, DEPTH, zb, p=0.45, sx=2.15, sz=FH, ww=0.9, wh=1.3, cols=cols, zoff=3.8, k=0.3)
                rng.setstate(keep_state)
            windows(x0, 0, za, x1, DEPTH, zb, p=0.3, sx=2.4, sz=FH, ww=1.0, wh=3.6, faces=(1, 3), zoff=2.0, k=0.5)
            if f == 0:
                quad_y(NEON, x0 + 1.0, 0.4, x1 - 1.0, 3.6, -0.08, tuple(v * 0.55 for v in rng.choice(TRIMS)))
                box(x0 + 0.6, -1.6, 3.8, x1 - 0.6, 0, 4.2, rng.choice([(0.6, 0.15, 0.3), (0.15, 0.4, 0.5), (0.5, 0.35, 0.1)]), facet=False)
        # floor-line trim band on the alley faces (light spill catches it)
        if f % 2 == 1:
            set_sem(0.1, 0, l)
            quad_x(NEON if l != DRUM_COL else Acc("sink_t"), x1 + 0.08, 0.5, za + 0.2, DEPTH - 0.5, za + 0.35, tuple(v * 0.35 for v in TRIMS[(l + f) % 5]))
    set_sem(0.1, 0, l)
    with (Sink() if l == DRUM_COL else _nullctx()):
        box(x0, 0, top, x1, DEPTH, top + 0.8, tuple(v * 0.9 for v in c), facet=False)
        roof_trim(x0 + 0.1, 0.1, x1 - 0.1, DEPTH - 0.1, top + 0.85, TRIMS[l % len(TRIMS)] if l != 7 else MERIDIAN, w=0.28)
    zt = top + 0.8
    if arch == "relay":
        box(x0 + 1.5, 4, zt, x0 + 6.5, 9, zt + 3.2, (0.32, 0.28, 0.3), facet=False)
        beam((x1 - 3, 6, zt), (x1 - 3, 6, zt + 6), 0.3, (0.3, 0.3, 0.32))
        for k in range(6):
            a = 2 * math.pi * k / 6
            beam((x1 - 3, 6, zt + 6), (x1 - 3 + 2.4 * math.cos(a), 6 - 1.2, zt + 6 + 2.4 * math.sin(a)), 0.2, (0.5, 0.5, 0.55))
        panel(x1 - 3.3, zt + 5.8, x1 - 2.7, zt + 6.3, 4.6, LIME)
    elif arch == "setback":
        setback_tiers(x0, x1, 0, DEPTH, zt, 3 if l == 1 else 2, c)
    elif arch == "slab":
        for k in range(3):
            box(x0 + 1 + k * 4, 2.5, zt, x0 + 3.6 + k * 4, 6, zt + 2.4, (0.3, 0.3, 0.34), facet=False)
        # a rooftop neon frame sign
        beam((x0 + 2, 1, zt), (x0 + 2, 1, zt + 6), 0.3, (0.2, 0.2, 0.24))
        beam((x1 - 2, 1, zt), (x1 - 2, 1, zt + 6), 0.3, (0.2, 0.2, 0.24))
        quad_y(NEON, x0 + 2.3, zt + 3.2, x1 - 2.3, zt + 5.8, 0.8, tuple(v * 0.8 for v in PINK))
    elif arch == "tower":
        tw = (x1 - x0) * 0.55
        cx = (x0 + x1) / 2
        box(cx - tw / 2, 2.5, zt, cx + tw / 2, DEPTH - 2.5, zt + 18, tuple(v * 0.95 for v in c))
        windows(cx - tw / 2, 2.5, zt, cx + tw / 2, DEPTH - 2.5, zt + 18, p=0.35, sx=2.0, sz=FH / 2, ww=0.9, wh=1.8, zoff=1.8, k=0.7)
        roof_trim(cx - tw / 2 + 0.1, 2.6, cx + tw / 2 - 0.1, DEPTH - 2.6, zt + 18.05, CYAN if l == 3 else PINK, 0.22)
        spire(cx, DEPTH / 2, zt + 18, 14 if l == 3 else 10)
    elif arch == "billboard":
        billboard_frame(x0 - 1, x1 + 1, 3.0, zt, zt + 1, zt + 3, zt + 13, (PINK, CYAN), 77 + l)
    elif arch == "target":
        box(x0 + 2, 1.5, zt, x1 - 2, DEPTH - 1.5, zt + 4.2, (0.3, 0.26, 0.3))
        hazard(x0 + 2, x1 - 2, zt + 3.2, 1.45, 0.6, seg=1.2)
        beam(((x0 + x1) / 2, 6, zt + 4.2), ((x0 + x1) / 2, 6, zt + 14.2), 0.35, (0.3, 0.3, 0.32))
        panel((x0 + x1) / 2 - 0.4, zt + 13.8, (x0 + x1) / 2 + 0.4, zt + 14.6, 5.6, RED)
    if l in (2, 5, 4):
      with (Sink() if l == DRUM_COL else _nullctx()):
        blade_sign(x1 - 0.5, 0, top - 24, top - 8, PINK if l == 2 else (CYAN if l == 5 else VIOLET))
    OFF[1] = 0.0


for l in range(8):
    building(l)

# ------------------------------------------------------------------ connections (the 10 types + the legacy conduit)
STEEL = (0.22, 0.21, 0.26)
RAIL = (0.32, 0.31, 0.36)
PACKETS = []                     # (object, polyline, phase) animated along the data-pipe


def plen(p):
    return sum((Vector(b) - Vector(a)).length for a, b in zip(p, p[1:]))


def at(p, s):
    for a, b in zip(p, p[1:]):
        L = (Vector(b) - Vector(a)).length
        if s <= L:
            return Vector(a).lerp(Vector(b), s / L if L else 0)
        s -= L
    return Vector(p[-1])


def catwalk(a, b, rail=True):
    a, b = Vector(a), Vector(b)
    beam(a - Vector((0, 0, 0.55)), b - Vector((0, 0, 0.55)), 0.5, STEEL, h=0.3)
    if rail:
        beam(a + Vector((0, -0.6, 0.9)), b + Vector((0, -0.6, 0.9)), 0.12, RAIL)
        n = max(1, int((b - a).length / 1.4))
        for q in range(n + 1):
            p = a.lerp(b, q / n)
            beam(p + Vector((0, -0.6, -0.3)), p + Vector((0, -0.6, 0.9)), 0.1, RAIL)


def conn_tube(p):
    a, b = Vector(p[0]), Vector(p[-1])
    o = Vector((0, 0, 0.9))
    tube(a + o, b + o, 1.7, (0.26, 0.27, 0.34))
    d = (b - a)
    n = max(2, int(d.length / 1.6))
    for k in range(n + 1):
        q = a.lerp(b, k / n) + o
        tube(q - d.normalized() * 0.12, q + d.normalized() * 0.12, 1.86, (0.16, 0.15, 0.2), n=8)
    # glazing band (front) lit from inside
    s = Vector((0, -1.75, 0))
    beam(a + o + s + Vector((0, 0, 0.3)), b + o + s + Vector((0, 0, 0.3)), 0.06, (0.4, 0.75, 0.9), acc=NEON, h=0.9)
    beam(a - Vector((0, 0, 0.5)), b - Vector((0, 0, 0.5)), 1.6, STEEL, h=0.25)


def conn_plank(p):
    a, b = Vector(p[0]), Vector(p[-1])
    beam(a - Vector((0, 0, 0.6)), b - Vector((0, 0, 0.6)), 1.0, (0.45, 0.33, 0.2), h=0.18)
    for t in (0.0, 1.0):
        q = a.lerp(b, t)
        box(q.x - 0.8, q.y - 0.4, q.z - 0.9, q.x + 0.8, q.y + 0.6, q.z - 0.7, (0.3, 0.3, 0.34), facet=False)
    q = a.lerp(b, 0.5)
    beam(q - Vector((0, 0, 0.6)), q - Vector((0, 0, 1.5)), 0.12, (0.15, 0.15, 0.17))     # a sag rope
    box(q.x - 0.5, q.y - 0.4, q.z - 0.5, q.x + 0.3, q.y + 0.4, q.z + 0.1, (0.55, 0.42, 0.25), facet=False)  # a crate


def conn_pipe(p):
    a, b = Vector(p[0]), Vector(p[-1])
    tube(a, b, 0.9, (0.24, 0.3, 0.36))
    for t in (0.08, 0.5, 0.92):
        q = a.lerp(b, t)
        d = (b - a).normalized()
        tube(q - d * 0.2, q + d * 0.2, 1.08, (0.16, 0.18, 0.22))
    beam(a + Vector((0, -0.9, 0.0)), b + Vector((0, -0.9, 0.0)), 0.05, (0.08, 0.35, 0.45), acc=NEON, h=0.35)
    # packets: separate animated objects
    for k in range(6):
        acc = Acc("pk%d" % k)
        acc.face([(-0.55, 0, -0.2), (0.55, 0, -0.2), (0.55, 0, 0.2), (-0.55, 0, 0.2)], (0.6, 1.0, 0.9), (0, 0, 0))
        ob = acc.obj(NEONM, "packet_%d" % k)
        NEON_OBJS.append(ob)
        PACKETS.append((ob, [tuple(a + Vector((0, -0.97, 0))), tuple(b + Vector((0, -0.97, 0)))], k / 6.0))


def conn_conduit(p):
    for a, b in zip(p, p[1:]):
        a, b = Vector(a), Vector(b)
        if abs(a.z - b.z) < 1e-4:
            catwalk(a, b)
        elif abs(a.x - b.x) < 1e-4:
            for s in (-0.45, 0.45):
                beam((a.x + s, a.y + 0.2, min(a.z, b.z) - 0.6), (a.x + s, a.y + 0.2, max(a.z, b.z) + 0.6), 0.16, STEEL)
            z = min(a.z, b.z)
            while z < max(a.z, b.z):
                beam((a.x - 0.45, a.y + 0.2, z), (a.x + 0.45, a.y + 0.2, z), 0.08, RAIL)
                z += 0.9
        else:
            beam(a - Vector((0, 0, 0.4)), b - Vector((0, 0, 0.4)), 0.35, STEEL)


def conn_lift(p):
    (ax, ay, az), (lx, ly, lz0), (_, _, lz1), (bx, by, bz) = p
    lo, hi = min(lz0, lz1) - 1.2, max(lz0, lz1) + 4.5
    w = 1.3
    lattice(lx - w, lx + w, ly - w, ly + w, lo, hi, col=(0.26, 0.24, 0.2), step=2.6)
    # cage at the source floor, head wheel at the top, amber warning lights
    cz = lz0 - 0.6
    box(lx - 1.1, ly - 1.1, cz, lx + 1.1, ly + 1.1, cz + 0.25, (0.86, 0.62, 0.10), facet=False)
    for s in (-1.05, 1.05):
        beam((lx + s, ly - 1.05, cz), (lx + s, ly - 1.05, cz + 2.6), 0.1, (0.86, 0.62, 0.10))
    beam((lx - 1.05, ly - 1.05, cz + 2.6), (lx + 1.05, ly - 1.05, cz + 2.6), 0.1, (0.86, 0.62, 0.10))
    tube((lx - 0.4, ly, hi + 0.6), (lx + 0.4, ly, hi + 0.6), 1.0, (0.3, 0.3, 0.32))
    for z in (lo + 1.0, hi - 0.4):
        panel(lx - 0.25, z, lx + 0.25, z + 0.4, ly - w - 0.3, AMBER)
    catwalk((ax, ay, az), (lx - w, ly, az))
    catwalk((lx + w, by, bz), (bx, by, bz))


def conn_ladder(p):
    """Fire escape: landings at every turn, stair flights between, rails, posts down to the next landing."""
    a, b = Vector(p[0]), Vector(p[-1])
    pts = [Vector(q) for q in p[1:-1]]
    catwalk(a, pts[0])
    catwalk(pts[-1], b)
    for q in pts:
        box(q.x - 1.4, q.y - 0.9, q.z - 0.75, q.x + 1.4, q.y + 0.9, q.z - 0.5, (0.24, 0.22, 0.27), facet=False)
        beam((q.x - 1.4, q.y - 0.9, q.z + 0.5), (q.x + 1.4, q.y - 0.9, q.z + 0.5), 0.1, RAIL)
        beam((q.x - 1.4, q.y - 0.9, q.z - 0.6), (q.x - 1.4, q.y - 0.9, q.z + 0.5), 0.1, RAIL)
        beam((q.x + 1.4, q.y - 0.9, q.z - 0.6), (q.x + 1.4, q.y - 0.9, q.z + 0.5), 0.1, RAIL)
    for u, v in zip(pts, pts[1:]):
        beam(u - Vector((0, 0, 0.6)), v - Vector((0, 0, 0.6)), 0.9, (0.2, 0.19, 0.24), h=0.18)
        n = int((v - u).length / 0.6)
        for k in range(1, n):
            s = u.lerp(v, k / n) - Vector((0, 0, 0.45))
            beam(s + Vector((0, -0.45, 0)), s + Vector((0, 0.45, 0)), 0.08, RAIL)
        beam(u + Vector((0, -0.5, 0.7)), v + Vector((0, -0.5, 0.7)), 0.08, RAIL)
    zlo = min(q.z for q in pts)
    for q in pts:
        if q.z > zlo + 0.1:
            beam((q.x + 1.3, q.y + 0.8, q.z - 0.7), (q.x + 1.3, q.y + 0.8, zlo - 0.7), 0.12, STEEL)


def conn_zip(p):
    a, ha, hb, b = [Vector(q) for q in p]
    beam(ha, hb, 0.09, (0.75, 0.75, 0.8), acc=SOLID)
    for h, base in ((ha, a), (hb, b)):
        beam((h.x, h.y, base.z - 0.6), (h.x, h.y, h.z + 0.5), 0.3, STEEL)
        beam((h.x, h.y, h.z + 0.3), (base.x, base.y, h.z + 0.3), 0.2, STEEL)
        box(h.x - 0.4, h.y - 0.4, base.z - 0.75, h.x + 0.4, h.y + 0.4, base.z - 0.5, (0.86, 0.62, 0.10), facet=False)
    tr = ha.lerp(hb, 0.28)
    box(tr.x - 0.4, tr.y - 0.25, tr.z - 0.2, tr.x + 0.4, tr.y + 0.25, tr.z + 0.3, (0.86, 0.62, 0.10), facet=False)
    beam(tr, tr - Vector((0, 0, 1.4)), 0.08, (0.2, 0.2, 0.22))
    box(tr.x - 0.3, tr.y - 0.1, tr.z - 1.7, tr.x + 0.3, tr.y + 0.1, tr.z - 1.4, (0.3, 0.3, 0.34), facet=False)
    panel(ha.x - 0.2, ha.z + 0.5, ha.x + 0.2, ha.z + 0.9, ha.y - 0.2, RED)
    catwalk(a, Vector((ha.x, a.y, a.z)))


def conn_duct(p):
    pts = [Vector(q) for q in p]
    for u, v in zip(pts, pts[1:]):
        beam(u + Vector((0, 0, 0.6)), v + Vector((0, 0, 0.6)), 2.0, (0.42, 0.42, 0.46), h=1.8)
    for q in pts[1:-1]:
        box(q.x - 1.2, q.y - 1.15, q.z - 0.45, q.x + 1.2, q.y + 1.15, q.z + 1.65, (0.3, 0.3, 0.34), facet=False)
    for u, v in zip(pts, pts[1:]):
        L = (v - u).length
        n = int(L / 1.4)
        for k in range(1, n):
            q = u.lerp(v, k / n) + Vector((0, 0, 0.6))
            d = (v - u).normalized()
            beam(q - d * 0.08, q + d * 0.08, 2.15, (0.3, 0.3, 0.34), h=1.95)
    m = pts[1].lerp(pts[2], 0.5)
    quad_y(NEON, m.x - 0.6, m.z + 0.1, m.x + 0.6, m.z + 1.1, m.y - 1.06, (0.25, 0.45, 0.6))


def conn_tram(p):
    a, r0, r1, b = [Vector(q) for q in p]
    catwalk(a, r0)
    catwalk(r1, b)
    d = r1 - r0
    side = Vector((0, 0.6, 0))
    for s in (-1, 1):
        beam(r0 + side * s - Vector((0, 0, 0.5)), r1 + side * s - Vector((0, 0, 0.5)), 0.16, RAIL)
    n = int(d.length / 0.9)
    for k in range(n + 1):
        q = r0.lerp(r1, k / n) - Vector((0, 0, 0.62))
        beam(q - side * 1.4, q + side * 1.4, 0.14, (0.25, 0.2, 0.18))
    for t in (0.2, 0.55, 0.9):
        q = r0.lerp(r1, t)
        beam((q.x, q.y + 0.3, q.z - 0.7), (q.x, q.y + 0.3, max(0.0, r0.z - 0.8) if t > 0.25 else q.z - 3), 0.35, STEEL)
    c = r0.lerp(r1, 0.55)
    box(c.x - 1.3, c.y - 1.1, c.z - 0.4, c.x + 1.3, c.y + 1.1, c.z + 1.8, (0.75, 0.55, 0.12), facet=False)
    panel(c.x - 1.0, c.z + 0.5, c.x + 1.0, c.z + 1.4, c.y - 1.12, (0.8, 0.9, 1.0))
    panel(c.x + 1.0, c.z - 0.1, c.x + 1.25, c.z + 0.2, c.y - 1.12, RED)


def conn_roofjump(p):
    pts = [Vector(q) for q in p]
    # facade ladders up from A's door and down into B's roof hatch
    a_up0, a_up1 = pts[1], pts[2]
    for s in (-0.4, 0.4):
        beam((a_up0.x + s, a_up0.y, a_up0.z - 0.6), (a_up1.x + s, a_up1.y, a_up1.z + 1.0), 0.12, RAIL)
    z = a_up0.z
    while z < a_up1.z:
        beam((a_up0.x - 0.4, a_up0.y, z), (a_up0.x + 0.4, a_up0.y, z), 0.07, RAIL)
        z += 0.9
    ra, rb = pts[3], pts[-4]
    # a kicker ramp at A's roof edge and a landing mat with hazard stripes on B
    beam(ra - Vector((2.5, 0, 1.2)), ra - Vector((0, 0, 0.7)), 1.6, (0.45, 0.33, 0.2), h=0.2)
    box(rb.x - 1.5, rb.y - 1.0, rb.z - 1.25, rb.x + 2.5, rb.y + 2.0, rb.z - 1.0, (0.6, 0.15, 0.25), facet=False)
    for k in range(3):
        quad_y(NEON, ra.x - 2.0 + k * 0.7, ra.z - 1.1, ra.x - 1.7 + k * 0.7, ra.z - 0.8, ra.y - 0.85, AMBER)
    box(rb.x - 0.6, rb.y + 2.2, rb.z - 1.2, rb.x + 0.8, rb.y + 3.6, rb.z - 0.2, (0.3, 0.3, 0.34), facet=False)
    b0, b1 = pts[-3], pts[-2]
    for s in (-0.4, 0.4):
        beam((b0.x + s, b0.y, b1.z - 0.6), (b0.x + s, b0.y, b0.z + 0.6), 0.12, RAIL)


def conn_tunnel(p):
    pts = [Vector(q) for q in p]
    a, l0, l1, k0, k1, h0, h1, end = pts
    catwalk(a, l0)
    # the stair shaft down to the tunnel (a caged ladder)
    lattice(l0.x - 1.0, l0.x + 1.0, l0.y - 1.0, l0.y + 1.0, l1.z - 0.5, l0.z + 0.4, col=(0.24, 0.22, 0.26), step=2.0)
    # the tunnel: a cut half-tube under the street, strip lights, a hatch up at the far end
    tube(k0 - Vector((1.6, 0, 0)), k1 + Vector((1.6, 0, 0)), 2.3, (0.24, 0.22, 0.3), open_top=True, n=10)
    tube(l1, k0, 2.3, (0.24, 0.22, 0.3), open_top=True, n=10)
    beam(k0 - Vector((0, 0, 1.9)), k1 - Vector((0, 0, 1.9)), 1.4, (0.18, 0.17, 0.2), h=0.2)
    for s in (-1.6, 1.6):
        beam(k0 + Vector((0, s, -0.6)), k1 + Vector((0, s, -0.6)), 0.22, (1.0, 0.6, 0.25), acc=NEON)
    n = int((k1 - k0).length / 2.2)
    for q in range(n + 1):
        c = k0.lerp(k1, q / n)
        tube(c - Vector((0.15, 0, 0)), c + Vector((0.15, 0, 0)), 2.45, (0.16, 0.15, 0.2), open_top=True, n=10)
    lattice(h0.x - 0.9, h0.x + 0.9, h0.y - 0.9, h0.y + 0.9, h0.z - 3.8, h0.z + 0.2, col=(0.24, 0.22, 0.26), step=2.0)
    box(h0.x - 1.3, h0.y - 1.3, -0.05, h0.x + 1.3, h0.y + 1.3, 0.12, (0.86, 0.62, 0.10), facet=False)
    catwalk(Vector((h0.x, h0.y, 0.4)), h1)


CONN_FN = {"tube": conn_tube, "plank": conn_plank, "pipe": conn_pipe, "conduit": conn_conduit, "lift": conn_lift,
           "ladder": conn_ladder, "zip": conn_zip, "duct": conn_duct, "tram": conn_tram, "roofjump": conn_roofjump,
           "tunnel": conn_tunnel}


def build_connections(edges):
    set_sem(0.7, 0, 0)
    for e in edges:
        CONN_FN[e["type"]]([tuple(q) for q in e["path"]])


# ------------------------------------------------------------------ the street, the trench, the foreground
def build_street():
    set_sem(0.2, 0, 0)
    tun = next((e for e in LY["edges"] if e["type"] == "tunnel"), None)
    if tun:
        xs = [q[0] for q in tun["path"][2:7]]
        tx0, tx1 = min(xs) - 3.0, max(xs) + 3.0
        ty0, ty1 = -9.0, -1.2
    else:
        tx0 = tx1 = ty0 = ty1 = None
    G0, G1 = (-120, 330)
    gcol = (0.16, 0.14, 0.2)
    if tun:
        box(G0, -320, -9, tx0, 80, 0, gcol, facet=False)
        box(tx1, -320, -9, G1, 80, 0, gcol, facet=False)
        box(tx0, -320, -9, tx1, ty0, 0, gcol, facet=False)
        box(tx0, ty1, -9, tx1, 80, 0, gcol, facet=False)
        set_sem(0.3, 0, 0)
        box(tx0, ty0, -7.5, tx1, ty1, -7.0, (0.1, 0.09, 0.13), facet=False)
        for (a, b) in ((ty0, ty0 + 0.02),):
            quad_y(SOLID, tx0, -7.0, tx1, 0, ty0 + 0.03, CUT)
        set_sem(0.2, 0, 0)
        for k in range(int((tx1 - tx0) / 1.0)):
            x = tx0 + 0.5 + k
            beam((x, ty0 - 0.3, 0.2), (x, ty0 - 0.3, 1.3), 0.08, (0.86, 0.62, 0.10))
        beam((tx0, ty0 - 0.3, 1.3), (tx1, ty0 - 0.3, 1.3), 0.12, (0.86, 0.62, 0.10))
        quad_y(NEON, tx0, -0.3, tx1, -0.15, ty0 - 0.05, (0.9, 0.5, 0.15))
    else:
        box(G0, -320, -9, G1, 80, 0, gcol, facet=False)
    # road, kerb, lane glow, dashed centre line
    box(G0, -40, 0.0, G1, -9.5, 0.08, (0.12, 0.11, 0.16), facet=False)
    box(G0, -9.5, 0.0, G1, -8.5, 0.35, (0.24, 0.22, 0.28), facet=False)
    # AAA: the full-width kerb line was a false route line; it is now broken 2-6 BU segments at 30 % (own stream)
    _kr = random.Random(4242)
    _kx = G0
    while _kx < G1:
        _kl = _kr.uniform(2.0, 6.0)
        NEON.face([(_kx, -9.6, 0.36), (_kx + _kl, -9.6, 0.36), (_kx + _kl, -9.3, 0.36), (_kx, -9.3, 0.36)],
                  (0.45 * 0.3, 0.25 * 0.3, 0.75 * 0.3), (0, 0, 0))
        _kx += _kl + _kr.uniform(3.0, 9.0)
    for k in range(int((G1 - G0) / 6)):
        x = G0 + k * 6
        NEON.face([(x, -24.2, 0.09), (x + 3, -24.2, 0.09), (x + 3, -23.8, 0.09), (x, -23.8, 0.09)], (0.5, 0.45, 0.3), (0, 0, 0))
    # cars on the road: r2 builds them into a Sink (no car geometry; the shared stream is unchanged).
    # The traffic is the long-exposure streaks in shapes_r2.py.
    _sk = Sink()
    _sk.__enter__()
    for (cx, cy, dirn, cc) in ((-14.0, -16, 1, PINK), (58.0, -30, -1, CYAN), (104.0, -14, 1, AMBER), (150.0, -31, -1, VIOLET),
                               (196.0, -15, 1, (0.4, 1.0, 0.7))):
        box(cx - 2.6, cy - 1.5, 0.4, cx + 2.6, cy + 1.5, 1.5, (0.12, 0.1, 0.14), facet=False)
        box(cx - 1.4, cy - 1.1, 1.5, cx + 1.4, cy + 1.1, 2.3, (0.06, 0.06, 0.08), facet=False)
        panel(cx + dirn * 2.55 - 0.25, 0.8, cx + dirn * 2.55 + 0.25, 1.2, cy - 1.55, WHITE)
        panel(cx - dirn * 2.55 - 0.25, 0.8, cx - dirn * 2.55 + 0.25, 1.2, cy - 1.55, RED)
        quad_y(NEON, cx - 2.2, 0.25, cx + 2.2, 0.4, cy - 1.55, cc)
    _sk.__exit__()
    # street grates with steam come from atmosphere()


FG = []      # (name, solid Acc, neon Acc)


def fg_item(name):
    global SOLID, NEON
    s, n = Acc("fg_s_" + name), Acc("fg_n_" + name)
    FG.append((name, s, n))
    return s, n


def build_foreground():
    """Foreground occluders between the camera and the street: each its own object, so a shot can hide the ones that
    would cover an available room (the occlusion rule)."""
    global SOLID, NEON
    keep = (SOLID, NEON)
    set_sem(0.95, 0, 0)
    dark = (0.08, 0.07, 0.1)
    for k, lx in enumerate((-6.0, 34.0, 76.0, 118.0, 160.0, 204.0)):
        SOLID, NEON = fg_item("lamp%d" % k)
        beam((lx, -36, 0), (lx, -36, 11.5), 0.4, dark)
        beam((lx, -36, 11.5), (lx + 2.8, -36, 11.8), 0.28, dark)
        panel(lx + 1.8, 11.1, lx + 3.3, 11.4, -36.3, (1.0, 0.82, 0.55))
        quad_y(NEON, lx - 0.3, 4, lx + 0.3, 8, -36.25, PINK if k % 2 else CYAN)
    SOLID, NEON = fg_item("van")
    box(86.0, -45, 0.2, 96.0, -40, 3.8, dark, facet=False)
    box(87.0, -45, 3.8, 93.0, -40, 5.2, dark, facet=False)
    panel(95.6, 1.6, 96.05, 2.3, -45.05, (1.0, 0.9, 0.7))
    panel(85.95, 1.6, 86.4, 2.3, -45.05, RED)
    FG.pop()         # r2: the foreground van is a car: dropped (its faces still drew from the stream)
    SOLID, NEON = fg_item("kiosk")
    box(44.0, -52, 0, 52.0, -46, 7.5, (0.12, 0.1, 0.15))
    quad_y(NEON, 44.6, 1.5, 51.4, 4.0, -52.05, (0.9, 0.35, 0.6))
    box(43.0, -53.5, 7.5, 53.0, -45.5, 8.1, (0.5, 0.15, 0.3), facet=False)
    SOLID, NEON = fg_item("fence")
    for k in range(90):
        xx = -60 + k * 3.5
        beam((xx, -34, 0), (xx, -34, 1.6), 0.12, dark)
    beam((-60, -34, 1.5), (260, -34, 1.5), 0.12, dark)
    SOLID, NEON = fg_item("gantry")
    beam((128, -58, 0), (128, -58, 14), 0.6, dark)
    beam((128, -58, 13.5), (146, -58, 13.5), 0.6, dark)
    box(132, -58.6, 11.5, 144, -57.8, 15.5, (0.1, 0.12, 0.14), facet=False)
    quad_y(NEON, 132.4, 12.0, 143.6, 15.0, -58.65, (0.15, 0.6, 0.35))
    SOLID, NEON = keep
    for name, s, n in FG:
        objs = []
        if s.n:
            o = s.obj(TOON, "FG_%s_s" % name)
            SOLID_OBJS.append(o)
            objs.append(o)
        if n.n:
            o = n.obj(NEONM, "FG_%s_n" % name)
            NEON_OBJS.append(o)
            objs.append(o)
        FG_OBJS[name] = objs


# ------------------------------------------------------------------ the mid row and the far city
def build_midrow():
    set_sem(0.6, 0, 0)
    fam = lambda k: tuple(v * 0.82 for v in FAMS[k % len(FAMS)])  # noqa: E731
    parking(-30, -12, -2, 14, 5, fam(2), seed=5)
    with Sink():
        tower(14, 24, 22, 32, 74, fam(1), crown=CYAN, seed=1)
    with OwnRng(9101):                                   # r2: a round tower
        round_tower(19.0, 27.5, 5.8, 74.0, fam(1), crown=CYAN, spire_h=14.0)
    footbridge_block(34, 44, 24, 58, 52, 62, 30, 66, 40, fam(4))
    billboard_frame(64, 80, 18, 0, 0, 54, 68, (CYAN, PINK), 21)
    with Sink():
        box(73, 26, 0, 86, 40, 62, fam(0))
        windows(73, 26, 0, 86, 40, 62, p=0.3, sx=2.2, sz=FH / 2, ww=1.0, wh=1.6, zoff=1.6, k=0.7, faces=(0, 1, 3))
        setback_tiers(73, 86, 26, 40, 62, 3, fam(0))
    with OwnRng(9102):                                   # r2: a stepped ziggurat
        ziggurat(69.0, 26.0, 90.0, 44.0, 100.0, 5, fam(0), inset=2.0, trim=VIOLET)
    tower(98, 108, 24, 34, 84, fam(3), crown=PINK, seed=2)
    with Sink():
        slab(150, 176, 40, 52, 52, fam(5), sign=CYAN)
    with OwnRng(9103):                                   # r2: a curved facade (convex)
        curved_block(148.0, 40.0, 178.0, 56.0, 52.0, fam(5), 5.0, CYAN)
    box(122, 20, 0, 133, 30, 60, fam(2))
    windows(122, 20, 0, 133, 30, 60, p=0.3, sx=2.2, sz=FH / 2, ww=1.0, wh=1.6, zoff=1.6, k=0.7, faces=(0, 1, 3))
    setback_tiers(122, 133, 20, 30, 60, 2, fam(2))
    footbridge_block(152, 164, 22, 62, 192, 204, 24, 56, 46, fam(1))
    parking(192, 214, -4, 14, 4, fam(4), seed=8)
    slab(214, 246, 6, 20, 46, fam(3), sign=PINK)
    with Sink():
        tower(-56, -44, 10, 22, 70, fam(5), crown=AMBER, seed=0)
        slab(-90, -58, 16, 30, 52, fam(0), sign=VIOLET)
    with OwnRng(9104):                                   # r2: a drum joined to a terraced run on shared walls
        round_tower(-49.0, 17.0, 6.8, 70.0, fam(5), crown=PINK, spire_h=10.0)
        terraced_run(-92.0, 14.0, -55.0, 30.0, (52.0, 40.0, 30.0), fam(0), VIOLET)
    # glow between buildings: dim emissive back-walls in the gaps behind the route row (the light-spill source)
    for x, c in ((18, PINK), (44, CYAN), (67, VIOLET), (91.5, PINK), (115, CYAN), (139, AMBER), (161.5, PINK)):
        quad_y(NEON, x - 1.2, 0, x + 1.2, 3.0, 48, tuple(v * 0.5 for v in c))
    # blade signs on the mid row
    for x, z, c in ((24.2, 44, PINK), (100.2, 40, CYAN), (121.2, 56, AMBER), (62.2, 30, VIOLET)):
        blade_sign(x, 22 if x < 30 else 26, z, z + 18, c)


FAR_ALT = random.Random(7300)


def build_far():
    set_sem(0.85, 0, 0)
    for layer, (y0, hmin, hmax, p, dk) in enumerate(((70, 40, 100, 0.18, 0.42), (140, 70, 160, 0.12, 0.32),
                                                    (260, 110, 250, 0.08, 0.24))):
        x = -260.0
        while x < 460:
            w = rng.uniform(10, 24) * (1 + layer * 0.5)
            h = rng.uniform(hmin, hmax)
            c = tuple(v * dk for v in rng.choice(FAMS))
            yy = y0 + rng.uniform(-8, 8)
            _a = FAR_ALT.random()      # r2: own stream: which far buildings take a non-box shape
            _shape = "cyl" if _a < 0.22 else ("zig" if _a < 0.36 else ("fat" if _a < 0.46 else None))
            _sk = Sink() if _shape else None
            if _sk:
                _sk.__enter__()
            _h0 = h
            box(x, yy, 0, x + w, yy + w, h, c, facet=layer == 0)
            windows(x, yy, 0, x + w, yy + w, h, p=p, sx=2.4 + layer, sz=3.2 + layer, ww=1.0 + layer * 0.5, wh=1.4,
                    faces=(0,), k=0.6 - 0.12 * layer)
            if rng.random() < 0.5:
                tw = w * rng.uniform(0.4, 0.6)
                th = h * rng.uniform(0.15, 0.35)
                box(x + (w - tw) / 2, yy + (w - tw) / 2, h, x + (w + tw) / 2, yy + (w + tw) / 2, h + th, c, facet=False)
                h += th
            if rng.random() < 0.45:
                roof_trim(x + 0.2, yy + 0.2, x + w - 0.2, yy + w - 0.2, h + 0.1, rng.choice(TRIMS), w=0.4 + layer * 0.3)
            if rng.random() < 0.4:
                beam((x + w / 2, yy + w / 2, h), (x + w / 2, yy + w / 2, h + rng.uniform(8, 22)), 0.35 + layer * 0.3, (0.15, 0.15, 0.18))
                panel(x + w / 2 - 0.6 - layer * 0.4, h + 20, x + w / 2 + 0.6 + layer * 0.4, h + 21.5 + layer, yy + w / 2 - 1.0, RED)
            if rng.random() < 0.25:
                quad_y(NEON, x + w * 0.2, h * 0.3, x + w * 0.2 + 0.8 + layer, h * 0.9, yy - 0.1,
                       tuple(v * (0.6 - 0.15 * layer) for v in rng.choice([PINK, CYAN, VIOLET])))
            if _sk:
                _sk.__exit__()
                with OwnRng(9200 + int(x * 13) + layer * 100000):
                    far_alt(_shape, x, yy, w, _h0, h, c, layer)
            x += w + rng.uniform(1, 8)


# ------------------------------------------------------------------ atmosphere (additive, hidden in data passes)
TRAFFIC, SEARCH = [], []


def atmosphere():
    shafts = AtmosAcc("shafts")
    r = random.Random(91)
    # light shafts: soft columns rising from the deep gaps, brightest at the base
    for k in range(16):
        x = -150 + k * 34 + r.uniform(-8, 8)
        y = r.choice([95, 120, 180, 220])
        w = r.uniform(5, 13)
        h = r.uniform(140, 260)
        c = r.choice([PINK, CYAN, VIOLET, (0.9, 0.3, 1.0)])
        k0 = 0.32 * r.uniform(0.6, 1.0)
        lo, hi = tuple(v * k0 for v in c), (0, 0, 0)
        for half in (0, 1):
            xa, xb = (x - w / 2, x) if half == 0 else (x, x + w / 2)
            ca, cb = ((0, 0, 0), lo) if half == 0 else (lo, (0, 0, 0))
            shafts.quad([(xa, y, 0), (xb, y, 0), (xb, y, h), (xa, y, h)], [ca, cb, hi, hi])
    for k in range(12):
        x = -60 + k * 26 + r.uniform(-6, 6)
        y = 58 + r.uniform(-3, 3)
        w = r.uniform(4, 9)
        h = r.uniform(90, 170)
        c = r.choice([PINK, CYAN, VIOLET])
        lo = tuple(v * 0.22 * r.uniform(0.6, 1.0) for v in c)
        for half in (0, 1):
            xa, xb = (x - w / 2, x) if half == 0 else (x, x + w / 2)
            ca, cb = ((0, 0, 0), lo) if half == 0 else (lo, (0, 0, 0))
            shafts.quad([(xa, y, 0), (xb, y, 0), (xb, y, h), (xa, y, h)], [ca, cb, (0, 0, 0), (0, 0, 0)])
    # glow cards in the alleys behind the route row (light spill between buildings)
    for x, c in ((18, PINK), (44, CYAN), (67, VIOLET), (91.5, PINK), (115, CYAN), (139, AMBER), (161.5, PINK)):
        lo = tuple(v * 0.09 for v in c)
        shafts.quad([(x - 7, 30, 0), (x + 7, 30, 0), (x + 7, 30, 70), (x - 7, 30, 70)], [lo, lo, (0, 0, 0), (0, 0, 0)])
    ATMOS_OBJS.append(shafts.obj(AIRM, "air_shafts"))
    # searchlights: long cones from far roofs, swept by t
    for k, (x, y, z, base, col) in enumerate(((-40, 150, 150, -18, (0.75, 0.8, 1.0)), (70, 230, 210, 14, (0.75, 0.8, 1.0)),
                                               (150, 160, 170, -10, (1.0, 0.8, 0.6)), (260, 240, 200, 20, (0.75, 0.8, 1.0)))):
        acc = AtmosAcc("sl%d" % k)
        L, rr = 280.0, 16.0
        hot = tuple(v * 0.34 for v in col)
        for a in range(6):
            a0, a1 = 2 * math.pi * a / 6, 2 * math.pi * (a + 1) / 6
            acc.quad([(0, 0, 0), (0, 0, 0.01), (rr * math.cos(a1), rr * math.sin(a1), L), (rr * math.cos(a0), rr * math.sin(a0), L)],
                     [hot, hot, (0, 0, 0), (0, 0, 0)])
        ob = acc.obj(AIRM, "searchlight_%d" % k)
        ob.location = (x, y, z)
        ATMOS_OBJS.append(ob)
        SEARCH.append((ob, base, k))
    # sky traffic: three lanes at three depths, vehicles with head/tail lights and an additive trail
    for lane, (y, z, n, sp, sc) in enumerate(((52, 86, 9, 14.0, 1.0), (115, 118, 11, -20.0, 1.6), (205, 150, 12, 26.0, 2.4))):
        for k in range(n):
            s = Acc("car_%d_%d" % (lane, k))
            dirn = 1 if sp > 0 else -1
            col = (0.1, 0.09, 0.12)
            set_sem(0.85, 0, 0)
            box(-1.6 * sc, -0.6 * sc, -0.35 * sc, 1.6 * sc, 0.6 * sc, 0.35 * sc, col, facet=False, acc=s)
            ob = s.obj(TOON, "trafficbody_%d_%d" % (lane, k))
            SOLID_OBJS.append(ob)
            nl = Acc("carl_%d_%d" % (lane, k))
            hc = r.choice([WHITE, (1.0, 0.9, 0.6), CYAN])
            nl.face([(dirn * 1.62 * sc, -0.62 * sc, -0.15 * sc), (dirn * 1.62 * sc, -0.62 * sc, 0.15 * sc),
                     (dirn * 1.62 * sc, 0.62 * sc, 0.15 * sc), (dirn * 1.62 * sc, 0.62 * sc, -0.15 * sc)], hc, (0, 0, 0))
            nl.face([(-dirn * 1.0 * sc, -0.62 * sc, -0.1 * sc), (-dirn * 1.6 * sc, -0.62 * sc, -0.1 * sc),
                     (-dirn * 1.6 * sc, -0.62 * sc, 0.1 * sc), (-dirn * 1.0 * sc, -0.62 * sc, 0.1 * sc)], RED, (0, 0, 0))
            obl = nl.obj(NEONM, "trafficlight_%d_%d" % (lane, k))
            NEON_OBJS.append(obl)
            tr = AtmosAcc("trail_%d_%d" % (lane, k))
            _tc_unused = r.choice([PINK, CYAN, AMBER, VIOLET])      # (kept: the seeded stream is unchanged)
            tc = (0.55, 0.05, 0.04)                                  # AAA: a red tail light streak, fading out
            tl = sc * (5.0 + 14.0 * ((k * 37) % 11) / 10.0)          # short streaks of different lengths (5-19 BU)
            tr.quad([(-dirn * 1.6 * sc, -0.7 * sc, -0.15 * sc), (-dirn * (1.6 * sc + tl), -0.7 * sc, -0.05 * sc),
                     (-dirn * (1.6 * sc + tl), -0.7 * sc, 0.05 * sc), (-dirn * 1.6 * sc, -0.7 * sc, 0.15 * sc)],
                    [tc, (0, 0, 0), (0, 0, 0), tc])
            obt = tr.obj(TRAILM, "traffictrail_%d_%d" % (lane, k))
            ATMOS_OBJS.append(obt)
            x0 = -200 + k * (560.0 / n) + r.uniform(-12, 12)
            zz = z + r.uniform(-4, 4)
            TRAFFIC.append(([ob, obl, obt], x0, y + r.uniform(-3, 3), zz, sp * r.uniform(0.8, 1.2)))
    # steam: plumes from street grates and roof vents (noise-textured, very soft)
    st = AtmosAcc("steam")
    vents = [(30, -6, 0, 3.5, 18), (128, -6, 0, 3.5, 16), (178, -7, 0, 3, 14)]
    for l in (1, 3, 5):
        x0, x1 = LY["cols"][str(l)]
        vents.append((x0 + 3, LY["dy"][l] + 5, LY["storeys"][str(l)] * FH + 0.8, 2.5, 14))
    for (x, y, z, w, h) in vents:
        c = (0.24, 0.22, 0.3)
        for ang in (0.0, 1.5708):
            dx, dy = math.cos(ang) * w, math.sin(ang) * w
            st.quad([(x - dx, y - dy, z), (x + dx, y + dy, z), (x + dx * 2.2, y + dy * 2.2, z + h), (x - dx * 2.2, y - dy * 2.2, z + h)],
                    [c, c, (0, 0, 0), (0, 0, 0)])
    ATMOS_OBJS.append(st.obj(STEAMM, "air_steam"))


def animate(t):
    for objs, x0, y, z, sp in TRAFFIC:
        x = x0 + sp * t
        x = -200 + ((x + 200) % 560)
        for o in objs:
            o.location = (x, y, z)
    for ob, base, k in SEARCH:
        a = math.radians(base + 12 * math.sin(0.55 * t + k * 1.7))
        b = math.radians(8 * math.cos(0.4 * t + k))
        ob.rotation_euler = (b, a, 0)
    for ob, pl, ph in PACKETS:
        L = plen(pl)
        s = ((ph + t * 0.45) % 1.0) * L
        ob.location = tuple(at(pl, s))


# ------------------------------------------------------------------ sheet mode (architecture sheet)
def build_sheet():
    """Each building type and each connection type alone, in a grid of cells on one plane (labelled in post)."""
    cells = {}
    set_sem(0.1, 0, 0)
    CW = 58.0
    gcol = (0.16, 0.14, 0.2)

    def stub(x0, x1, y0, floors, room_floor, kind):
        set_sem(0.1, 0, 0)
        for f in range(floors):
            if f == room_floor:
                set_sem(0.3, 0, 0)
                box(x0, y0, f * FH - SLAB / 2 if f else 0, x1, y0 + DEPTH, f * FH + SLAB / 2, CUT, facet=False)
                box(x0, y0, (f + 1) * FH - SLAB / 2, x1, y0 + DEPTH, (f + 1) * FH + SLAB / 2, CUT, facet=False)
                box(x0, y0, f * FH, x0 + 0.7, y0 + DEPTH, (f + 1) * FH, CUT, facet=False)
                box(x1 - 0.7, y0, f * FH, x1, y0 + DEPTH, (f + 1) * FH, CUT, facet=False)
                OFF[1] = y0
                room("S", dict(room=(x0 + 0.7, f * FH + SLAB / 2, x1 - 0.7, (f + 1) * FH - SLAB / 2), kind=kind, layer=1, k=f))
                OFF[1] = 0
                set_sem(0.1, 0, 0)
            else:
                box(x0, y0, f * FH, x1, y0 + DEPTH, (f + 1) * FH, (0.4, 0.38, 0.48), top=(f == floors - 1))
                windows(x0, y0, f * FH, x1, y0 + DEPTH, (f + 1) * FH, p=0.4, sx=2.15, sz=FH, ww=1.1, wh=3.0, zoff=2.6, k=0.8, faces=(0,))
        box(x0, y0, floors * FH, x1, y0 + DEPTH, floors * FH + 0.8, (0.36, 0.34, 0.42), facet=False)

    ROOM_IDX["S"] = 0
    conn_specs = [("tube", 3, 3), ("zip", 3, 1), ("lift", 0, 3), ("duct", 1, 2), ("ladder", 0, 2),
                  ("roofjump", 3, 2), ("tram", 1, 3), ("plank", 2, 2), ("pipe", 2, 2), ("tunnel", 1, 0)]
    kinds = ["router", "elite", "terminal", "modem", "rack"]
    for idx, (typ, fa, fb) in enumerate(conn_specs):
        row = idx // 5
        ox = idx * CW
        # the cell is built at x offset ox; rows are separated in y depth instead of z so the ground stays one plane
        OFF[0], OFF[1], OFF[2] = ox, row * 0.0, 0
        x0a, x1a = 0.0, 13.0
        x0b, x1b = 24.0, 37.0
        flA = max(fa, fb) + 1 if typ != "roofjump" else fa + 1
        flB = max(fa, fb) + 1 if typ != "roofjump" else fb + 1
        stub(x0a, x1a, 0, flA, fa, kinds[idx % 5])
        stub(x0b, x1b, 0, flB, fb, kinds[(idx + 2) % 5])
        za, zb = fa * FH + SLAB / 2 + 1.6, fb * FH + SLAB / 2 + 1.6
        A, B = (x1a - 0.7, za), (x0b + 0.7, zb)
        lx = (x1a + x0b) / 2
        if typ in ("tube", "plank"):
            p = [(A[0], YF, A[1]), (B[0], YF, B[1])]
        elif typ == "pipe":
            p = [(A[0], YF, A[1] + 2.6), (B[0], YF, B[1] + 2.6)]
        elif typ == "lift":
            p = [(A[0], YF, za), (lx, YF, za), (lx, YF, zb), (B[0], YF, zb)]
        elif typ == "ladder":
            pts = [(A[0], YF, za), (lx - 1.6, YF, za)]
            n = 4
            for k in range(1, n + 1):
                pts.append((lx + (1.6 if k % 2 else -1.6), YF, za + (zb - za) * k / n))
            pts.append((B[0], YF, zb))
            p = pts
        elif typ == "zip":
            p = [(A[0], YF, za), (A[0] + 0.8, YF, za + 3.4), (B[0] - 0.8, YF, zb + 2.2), (B[0], YF, zb)]
        elif typ == "duct":
            h = abs(zb - za) / 2
            p = [(A[0], YF, za), (lx - h, YF, za), (lx + h, YF, zb), (B[0], YF, zb)]
        elif typ == "tram":
            p = [(A[0], YF, za), (x1a + 1, YF, za), (x0b - 1, YF, zb), (B[0], YF, zb)]
        elif typ == "roofjump":
            ra, rb = flA * FH + 1.2, flB * FH + 1.2
            xa_, xb_ = x1a - 1.5, x0b + 1.5
            pts = [(A[0], YF, za), (A[0] + 0.3, YF, za), (A[0] + 0.3, YF, ra - 1.0), (xa_, YF, ra)]
            top = max(ra, rb) + 3
            for k in range(1, 8):
                t = k / 8
                pts.append((xa_ + (xb_ - xa_) * t, YF, (1 - t) * ra + t * rb + 4 * (top - (ra + rb) / 2) * t * (1 - t)))
            pts += [(xb_, YF, rb), (B[0] - 0.3, YF, rb - 1.0), (B[0] - 0.3, YF, zb), (B[0], YF, zb)]
            p = pts
        elif typ == "tunnel":
            p = [(A[0], YF, za), (lx - 3, YF, za), (lx - 3, YF, -4.2), (lx - 1, -7.5, -4.2), (B[0] + 3.5, -7.5, -4.2),
                 (B[0] + 3.5, -7.5, -0.2), (B[0] + 3.5, YF, zb - 1.2), (B[0] + 4.0, 1.5, zb)]
        set_sem(0.7, 0, 0)
        CONN_FN[typ](p)
        set_sem(0.2, 0, 0)
        if typ == "tunnel":
            box(-4, -30, -9, 6, 20, 0, gcol, facet=False)
            box(31, -30, -9, 42, 20, 0, gcol, facet=False)
            box(6, -30, -9, 31, -11, 0, gcol, facet=False)
            box(6, -1.2, -9, 31, 20, 0, gcol, facet=False)
            box(6, -11, -7.5, 31, -1.2, -7.0, (0.1, 0.09, 0.13), facet=False)
        else:
            box(-4, -30, -9, 42, 20, 0, gcol, facet=False)
        cells[typ] = dict(ox=ox, row=row, path=[(q[0] + ox, q[1], q[2]) for q in p], a=(x0a + ox, x1a + ox), b=(x0b + ox, x1b + ox))
        OFF[0] = OFF[1] = OFF[2] = 0
    # building types row (third row, further along x)
    arch = [("setback tower", "setback"), ("tower + spire", "tower"), ("slab", "slab"), ("footbridge block", "foot"),
            ("parking structure", "parking"), ("billboard frame", "billboard"), ("TARGET tower", "target")]
    for k, (lab, a) in enumerate(arch):
        ox = 10 * CW + 30 + k * 46.0
        OFF[0] = ox
        set_sem(0.6, 0, 0)
        c = FAMS[k % len(FAMS)]
        if a == "setback":
            box(0, 0, 0, 22, 12, 32, c)
            windows(0, 0, 0, 22, 12, 32, p=0.4, sx=2.2, sz=FH / 2, ww=1.0, wh=1.6, zoff=1.6, k=0.8, faces=(0, 1, 3))
            setback_tiers(0, 22, 0, 12, 32, 3, c)
        elif a == "tower":
            tower(4, 16, 0, 12, 60, c, crown=CYAN, seed=2)
        elif a == "slab":
            slab(-3, 27, 0, 12, 34, c, sign=PINK)
        elif a == "foot":
            footbridge_block(-4, 6, 0, 46, 16, 26, 4, 54, 28, c)
        elif a == "parking":
            parking(-2, 26, 0, 14, 5, c, seed=4)
        elif a == "billboard":
            billboard_frame(-2, 26, 2, 0, 0, 22, 38, (PINK, CYAN), 9)
        else:
            box(0, 0, 0, 20, 12, 70, (0.34, 0.3, 0.36))
            windows(0, 0, 0, 20, 12, 70, p=0.5, sx=2.15, sz=FH, ww=1.1, wh=3.0, zoff=2.6, k=0.8,
                    cols=[(1.0, 0.2, 0.12), (1.0, 0.68, 0.28), (0.9, 0.9, 1.0)])
            box(2, 1.5, 70, 18, 10.5, 74.2, (0.3, 0.26, 0.3))
            hazard(2, 18, 73.2, 1.45, 0.6, seg=1.2)
            beam((10, 6, 74.2), (10, 6, 84), 0.35, (0.3, 0.3, 0.32))
            panel(9.6, 83.6, 10.4, 84.4, 5.6, RED)
        set_sem(0.2, 0, 0)
        box(-6, -30, -9, 34, 20, 0, gcol, facet=False)
        cells["arch_" + a] = dict(ox=ox, label=lab)
        OFF[0] = 0
    return cells


# ------------------------------------------------------------------ build
if MODE == "sheet":
    CELLS = build_sheet()
else:
    build_connections(LY["edges"])
    build_street()
    build_foreground()
    build_midrow()
    build_far()
    atmosphere()
    CELLS = {}
    exec(compile(open(os.path.join(HERE, "dress_aaa.py")).read(), "dress_aaa.py", "exec"), globals())
    # r2: no 3D holo route tubes (the route is the 2D wax grease pencil now)
    exec(compile(open(os.path.join(HERE, "dress2_aaa.py")).read(), "dress2_aaa.py", "exec"), globals())
    exec(compile(open(os.path.join(HERE, "shapes_r2.py")).read(), "shapes_r2.py", "exec"), globals())
    if JOB.get("shapes_sheet"):    # r2: the labelled sheet of the new building shapes, built far off to the side
        exec(compile(open(os.path.join(HERE, "shapes_sheet_r2.py")).read(), "shapes_sheet_r2.py", "exec"), globals())
SOLID_OBJS.append(SOLID.obj(TOON))
NEON_OBJS.append(NEON.obj(NEONM))
NEON_OBJS.append(WIN.obj(WINM))
print("built", len(bpy.data.objects), "objects", flush=True)

if MODE != "sheet":
    exec(compile(open(os.path.join(HERE, "light_aaa.py")).read(), "light_aaa.py", "exec"), globals())
    exec(compile(open(os.path.join(HERE, "fogcards_aaa.py")).read(), "fogcards_aaa.py", "exec"), globals())
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
cam_data.clip_start = 0.5
cam_data.clip_end = 4000
cam_data.sensor_fit = "HORIZONTAL"
cam_data.sensor_width = 36.0


def set_pose(p):
    if p.get("ortho"):
        cam_data.type = "ORTHO"
        cam_data.ortho_scale = p["ortho"]
    else:
        cam_data.type = "PERSP"
        cam_data.lens = p["lens"]
    cam.location = tuple(p["loc"])
    cam.rotation_euler = (Vector(p["tgt"]) - Vector(p["loc"])).to_track_quat("-Z", "Y").to_euler()
    cam_data.shift_x = p.get("shift_x", 0.0)
    cam_data.shift_y = p.get("shift_y", 0.0)
    bpy.context.view_layer.update()


def proj(p):
    v = world_to_camera_view(scene, cam, Vector(p))
    if v.z <= 0:
        return None
    if MODE == "sheet":
        return (round(v.x * scene.render.resolution_x, 2), round((1 - v.y) * scene.render.resolution_y, 2))
    return (round(v.x * W_OUT, 2), round((1 - v.y) * H_OUT, 2))


def bbox2(pts):
    q = [p for p in pts if p]
    if not q:
        return None
    return (min(p[0] for p in q), min(p[1] for p in q), max(p[0] for p in q), max(p[1] for p in q))


def obj_bbox_px(objs):
    pts = []
    for o in objs:
        for c in o.bound_box:
            pts.append(proj(o.matrix_world @ Vector(c)))
    return bbox2(pts)


def anchors_for(shot):
    A = dict(rooms={}, edges=[], hidden_fg=[], cam=shot["pose"])
    for i, n in LY["nodes"].items():
        x0, z0, x1, z1 = n["room"]
        y0 = n["dy"]
        y1 = y0 + DEPTH - 0.6
        A["rooms"][i] = dict(front=[proj((x0, y0, z0)), proj((x1, y0, z0)), proj((x1, y0, z1)), proj((x0, y0, z1))],
                             back=[proj((x0, y1, z0)), proj((x1, y1, z0)), proj((x1, y1, z1)), proj((x0, y1, z1))])
    for e in LY["edges"]:
        A["edges"].append(dict(a=e["a"], b=e["b"], type=e["type"], pts=[proj(q) for q in e["path"]],
                               world=e["path"]))
    for l in range(8):
        x0, x1 = LY["cols"][str(l)]
        top = LY["storeys"][str(l)] * FH
        A.setdefault("cols", {})[l] = [proj((x0, LY["dy"][l], top)), proj((x1, LY["dy"][l], top))]
    return A


def protect_hide(shot):
    """Hide every foreground occluder whose screen box overlaps a protected room (current + options)."""
    hidden = []
    boxes = []
    for i in shot.get("protect", []):
        n = LY["nodes"][i]
        x0, z0, x1, z1 = n["room"]
        y0 = n["dy"]
        pts = [proj((x, y, z)) for x in (x0, x1) for y in (y0, y0 + DEPTH - 0.6) for z in (z0, z1)]
        b = bbox2(pts)
        if b:
            boxes.append((b[0] - 12, b[1] - 40, b[2] + 12, b[3] + 12))
    for name, objs in FG_OBJS.items():
        bb = obj_bbox_px(objs)
        hide = False
        if bb:
            for b in boxes:
                if bb[0] < b[2] and bb[2] > b[0] and bb[1] < b[3] and bb[3] > b[1]:
                    hide = True
        for o in objs:
            o.hide_render = hide
        if hide:
            hidden.append(name)
    return hidden


def render(path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)


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
        mr.inputs["From Max"].default_value = 1500.0
        L(cd.outputs["View Distance"], mr.inputs["Value"])
        L(mr.outputs[0], em.inputs["Color"])
    elif kind == "wz":
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        sx = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = -10.0
        mr.inputs["From Max"].default_value = 290.0
        L(geo.outputs["Position"], sx.inputs[0])
        L(sx.outputs["Z"], mr.inputs["Value"])
        L(mr.outputs[0], em.inputs["Color"])
    elif kind == "sem":
        a = attr(nt, "sem")
        L(a.outputs["Color"], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m


exec(compile(open(os.path.join(HERE, "render_aaa.py")).read(), "render_aaa.py", "exec"), globals())
