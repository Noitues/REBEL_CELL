"""Round 11: close-up hero view of the Meridian target building, authored in Blender 5.2 (headless).

Run:  blender -b --factory-startup --python target_scene.py -- <variant> <outdir> [preview]
  variant: boss    = THE MANIFEST's Freight Ziggurat (Meridian HQ, Lane 15 depot) with its gantry crane
           regular = a smaller Meridian container depot (warehouse, stacked yard, yard gantry)
Writes, per variant: <v>_beauty_day.png, <v>_beauty_night.png (toon colour, emissives),
  <v>_glow_day.png / _glow_night.png (emissive-only, for bloom + light spill),
  <v>_normal.png, <v>_id.png, <v>_depth.png (data passes for ink lines and haze, via material override).
Ink lines, grime, haze, rain and bloom are added afterwards by backdrop.py (Pillow + numpy).

Style (matches round 6 city restyle = Cv2 gritty low-poly + E cel shading):
  - every wall is split into jittered triangles (facets) with a per-triangle tone jitter;
  - 3 hard toon bands from one key light, cool shadow / warm lit tints, day and night palettes;
  - glowing street lanes, window lights, neon roof trims, the crane's hazard stripes and red beacons.
Composition: the target sits centre-top; buildings that project into the two wheel zones are kept low,
dark and sparsely lit (calm behind the wheels); taller, brighter towers frame the edges and top.
All randomness is seeded.
"""
import math
import os
import random
import sys

import bmesh
import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["boss", "."]
VARIANT, OUTDIR = argv[0], argv[1]
PREVIEW = len(argv) > 2 and argv[2] == "preview"
RES = (960, 540) if PREVIEW else (2880, 1620)
os.makedirs(OUTDIR, exist_ok=True)
rng = random.Random(1101 if VARIANT == "boss" else 2202)

MERIDIAN = (0.86, 0.42, 0.10)
FONT = "C:/Windows/Fonts/bahnschrift.ttf"

# ------------------------------------------------------------------ scene reset
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 8 if PREVIEW else 24
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_depth = "16"
scene.render.film_transparent = False


# ------------------------------------------------------------------ geometry accumulator
class Acc:
    """One bmesh per material with face attributes: col (colour), fj (tone jitter), bid (part id colour)."""

    def __init__(self, name):
        self.name = name
        self.bm = bmesh.new()
        self.col = self.bm.faces.layers.float_color.new("col")
        self.fj = self.bm.faces.layers.float.new("fj")
        self.bid = self.bm.faces.layers.float_color.new("bid")

    def face(self, pts, col, bid, fj=None):
        vs = [self.bm.verts.new(p) for p in pts]
        f = self.bm.faces.new(vs)
        f[self.col] = (col[0], col[1], col[2], 1.0)
        f[self.fj] = rng.random() if fj is None else fj
        f[self.bid] = (bid[0], bid[1], bid[2], 1.0)
        return f

    def facet_quad(self, a, b, c, d, col, bid, jit=0.035):
        """Quad a-b-c-d split into 4 jittered triangles around a pushed centre vertex (Cv2 facets)."""
        A, B, C, D = map(Vector, (a, b, c, d))
        n = (B - A).cross(D - A)
        size = max((B - A).length, (D - A).length)
        if n.length < 1e-6 or size < 2.5:
            self.face([a, b, c, d], col, bid)
            return
        n.normalize()
        u, v = rng.uniform(0.3, 0.7), rng.uniform(0.3, 0.7)
        P = A.lerp(B, u).lerp(D.lerp(C, u), v) + n * rng.uniform(-jit, jit) * size
        for p, q in ((A, B), (B, C), (C, D), (D, A)):
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


SOLID = Acc("solid")
NEON = Acc("neon")
WIN = Acc("win")


def rid():
    return (rng.random(), rng.random(), rng.random())


def box(x0, y0, z0, x1, y1, z1, col, taper=0.0, facet=True, bid=None, top=True):
    bid = bid or rid()
    t = taper
    b = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)]
    u = [(x0 + t, y0 + t, z1), (x1 - t, y0 + t, z1), (x1 - t, y1 - t, z1), (x0 + t, y1 - t, z1)]
    sides = [(b[0], b[1], u[1], u[0]), (b[1], b[2], u[2], u[1]), (b[2], b[3], u[3], u[2]), (b[3], b[0], u[0], u[3])]
    for q in sides:
        if facet:
            SOLID.facet_quad(*q, col, bid)
        else:
            SOLID.face(list(q), col, bid)
    if top:
        if facet:
            SOLID.facet_quad(u[0], u[1], u[2], u[3], col, bid, jit=0.01)
        else:
            SOLID.face(u, col, bid)
    return bid


def beam(p0, p1, w, col, acc=None, bid=None):
    """Square-section beam between two points."""
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


def hazard_beam(p0, p1, w, seg=2.4):
    p0, p1 = Vector(p0), Vector(p1)
    n = max(1, int((p1 - p0).length / seg))
    bid = rid()
    for i in range(n):
        a, b = p0.lerp(p1, i / n), p0.lerp(p1, (i + 1) / n)
        beam(a, b, w, MERIDIAN if i % 2 == 0 else (0.06, 0.05, 0.05), bid=bid)


def flat_quad(acc, x0, y0, x1, y1, z, col, bid=(0, 0, 0)):
    acc.face([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], col, bid)


def strip(acc, p0, p1, w, z, col):
    """Flat glowing strip on the ground between two xy points."""
    p0, p1 = Vector((p0[0], p0[1], z)), Vector((p1[0], p1[1], z))
    d = (p1 - p0).normalized()
    n = Vector((-d.y, d.x, 0)) * (w / 2)
    acc.face([tuple(p0 + n), tuple(p0 - n), tuple(p1 - n), tuple(p1 + n)], col, (0, 0, 0))


WIN_COLS = [(1.0, 0.68, 0.28), (1.0, 0.68, 0.28), (1.0, 0.8, 0.5), (0.45, 0.9, 1.0), (1.0, 0.42, 0.72), (0.9, 0.9, 1.0)]


def windows(x0, y0, z0, x1, y1, z1, p=0.35, sx=2.4, sz=3.2, ww=1.1, wh=0.9, cols=None, faces=(0, 1, 2, 3)):
    """Window quads on the four walls of an axis-aligned box, slightly outset."""
    cols = cols or WIN_COLS
    o = 0.06
    walls = [((x0, y0 - o), (x1, y0 - o)), ((x1 + o, y0), (x1 + o, y1)), ((x1, y1 + o), (x0, y1 + o)), ((x0 - o, y1), (x0 - o, y0))]
    for fi in faces:
        (ax, ay), (bx, by) = walls[fi]
        L = math.hypot(bx - ax, by - ay)
        nx = int((L - 1.0) / sx)
        nz = int((z1 - z0 - 1.5) / sz)
        if nx < 1 or nz < 1:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        off = (L - nx * sx) / 2
        for i in range(nx):
            for k in range(nz):
                if rng.random() > p:
                    continue
                c = rng.choice(cols)
                s = 0.55 + 0.45 * rng.random()
                c = (c[0] * s, c[1] * s, c[2] * s)
                t0 = off + i * sx + (sx - ww) / 2
                z = z0 + 1.2 + k * sz
                pa = (ax + ux * t0, ay + uy * t0)
                pb = (ax + ux * (t0 + ww), ay + uy * (t0 + ww))
                WIN.face([(pa[0], pa[1], z), (pb[0], pb[1], z), (pb[0], pb[1], z + wh), (pa[0], pa[1], z + wh)], c, (0, 0, 0))


def roof_trim(x0, y0, x1, y1, z, col, w=0.35):
    for (a, b) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        beam((a[0], a[1], z), (b[0], b[1], z), w, col, acc=NEON)


def text_obj(s, loc, rot, size, mat, extrude=0.15):
    cu = bpy.data.curves.new("t_" + s, "FONT")
    cu.body = s
    try:
        cu.font = bpy.data.fonts.load(FONT)
    except Exception:
        pass
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new("t_" + s, cu)
    ob.location = loc
    ob.rotation_euler = rot
    scene.collection.objects.link(ob)
    ob.data.materials.append(mat)
    return ob


# ------------------------------------------------------------------ materials
def attr(nt, name, kind="Color"):
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


def mat_glow(name):
    """Emission = attribute colour * k, mixed toward a 'dark glass' colour by day."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    col = attr(nt, "col")
    sc = nt.nodes.new("ShaderNodeVectorMath")
    sc.operation = "SCALE"
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MIX"
    em = nt.nodes.new("ShaderNodeEmission")
    L = nt.links.new
    L(col.outputs["Color"], sc.inputs[0])
    L(sc.outputs[0], mix.inputs[6])
    L(mix.outputs[2], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m, sc, mix


def mat_flat(name, rgb):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = rgb + (1,)
    nt.links.new(em.outputs[0], out.inputs[0])
    return m, em


TOON, RAMP = mat_toon()
NEONM, NEON_SC, NEON_MIX = mat_glow("neon")
WINM, WIN_SC, WIN_MIX = mat_glow("win")
SIGNM, SIGN_EM = mat_flat("sign", (1.0, 0.62, 0.22))


# ------------------------------------------------------------------ camera (set first: composition uses it)
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam
if VARIANT == "boss":
    cam.location = (0, -205, 112)
    target = Vector((0, 6, 30))
    cam_data.lens = 34
else:
    cam.location = (0, -128, 92)
    target = Vector((0, 10, 6))
    cam_data.lens = 30
cam.rotation_euler = (target - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
cam_data.clip_end = 900
bpy.context.view_layer.update()

# wheel zones in normalised screen coords (x right, y up): player left, enemy right
ZONES = [((480 / 1920, 1 - 482 / 1080), 0.17), ((1450 / 1920, 1 - 500 / 1080), 0.19)]


def calm(x, y, z=0.0):
    """0 = far from both wheels, 1 = right behind a wheel centre."""
    p = world_to_camera_view(scene, cam, Vector((x, y, z)))
    best = 0.0
    for (cx, cy), r in ZONES:
        d = math.hypot((p.x - cx) * 1.78, p.y - cy) / (r * 1.78)
        best = max(best, max(0.0, 1.0 - d))
    return min(1.0, best * 1.6)


def onscreen(x, y, z=0.0, pad=0.15):
    p = world_to_camera_view(scene, cam, Vector((x, y, z)))
    return -pad < p.x < 1 + pad and -pad < p.y < 1 + pad and p.z > 0


# ------------------------------------------------------------------ ground + streets
ASPH = (0.16, 0.16, 0.20)
SIDEWALK = (0.30, 0.29, 0.33)
box(-400, -300, -1, 400, 600, 0, ASPH, facet=False)
AMBER, CYAN, PINK, RED, WHITE = (1.0, 0.62, 0.15), (0.3, 0.85, 1.0), (1.0, 0.3, 0.65), (1.0, 0.15, 0.12), (0.95, 0.95, 1.0)

if VARIANT == "boss":
    PLAZA_R = 38
    streets_x = [(-11, 11, -300, -PLAZA_R + 2)]  # avenue toward camera
    streets_y = [(-66, -52), (52, 64)]  # cross streets (y ranges)
    avenues_x = [(-70, -58), (58, 70), (-150, -140), (140, 150)]
else:
    PLAZA_R = 0
    streets_x = [(-9, 9, -300, -30)]
    streets_y = [(-46, -36), (44, 54)]
    avenues_x = [(-58, -48), (48, 58), (-120, -112), (112, 120)]


def in_street(x, y, pad=1.5):
    for (a, b, c, d) in streets_x:
        if a - pad < x < b + pad and c - pad < y < d + pad:
            return True
    for (a, b) in streets_y:
        if a - pad < y < b + pad:
            return True
    for (a, b) in avenues_x:
        if a - pad < x < b + pad:
            return True
    return False


def lanes():
    # avenue toward the camera: amber double centre line, cyan edges, traffic trails
    for (a, b, c, d) in streets_x:
        m = (a + b) / 2
        strip(NEON, (m, c), (m, d), b - a, 0.02, (0.22, 0.12, 0.05))
        strip(NEON, (m - 0.5, c), (m - 0.5, d), 0.45, 0.04, AMBER)
        strip(NEON, (m + 0.5, c), (m + 0.5, d), 0.45, 0.04, AMBER)
        strip(NEON, (a + 0.6, c), (a + 0.6, d), 0.35, 0.04, CYAN)
        strip(NEON, (b - 0.6, c), (b - 0.6, d), 0.35, 0.04, CYAN)
        for k in range(10):
            y0 = rng.uniform(c, d - 20)
            x = rng.choice([m - 4.5, m - 2.5, m + 2.5, m + 4.5])
            strip(NEON, (x, y0), (x, y0 + rng.uniform(6, 18)), 0.22, 0.05, RED if x > m else WHITE)
    for (a, b) in streets_y:
        m = (a + b) / 2
        strip(NEON, (-400, m), (400, m), b - a, 0.02, (0.16, 0.05, 0.12))
        strip(NEON, (-400, m), (400, m), 0.9, 0.04, PINK)
        strip(NEON, (-400, a + 0.6), (400, a + 0.6), 0.3, 0.04, AMBER)
        strip(NEON, (-400, b - 0.6), (400, b - 0.6), 0.3, 0.04, AMBER)
        for k in range(14):
            x0 = rng.uniform(-200, 200)
            y = rng.choice([m - 2.5, m + 2.5])
            strip(NEON, (x0, y), (x0 + rng.uniform(8, 22), y), 0.22, 0.05, RED if y > m else WHITE)
    for (a, b) in avenues_x:
        m = (a + b) / 2
        cc = rng.choice([CYAN, AMBER, PINK])
        strip(NEON, (m, -300), (m, 600), b - a, 0.02, tuple(v * 0.16 for v in cc))
        strip(NEON, (m, -300), (m, 600), 0.9, 0.04, cc)
        strip(NEON, (a + 0.5, -300), (a + 0.5, 600), 0.3, 0.04, AMBER)
        strip(NEON, (b - 0.5, -300), (b - 0.5, 600), 0.3, 0.04, AMBER)


lanes()

# ------------------------------------------------------------------ city blocks
FAMS = [(0.42, 0.40, 0.52), (0.38, 0.44, 0.52), (0.52, 0.42, 0.40), (0.36, 0.42, 0.40), (0.48, 0.44, 0.36),
        (0.55, 0.34, 0.22), (0.62, 0.36, 0.16), (0.40, 0.38, 0.46)]
TRIMS = [AMBER, AMBER, CYAN, PINK, (0.6, 0.4, 1.0), (0.4, 1.0, 0.6)]


def building(x0, y0, x1, y1, h, c):
    k = calm((x0 + x1) / 2, (y0 + y1) / 2, h * 0.5)
    if k > 0.05:  # calm zone behind a wheel: lower, darker, sparsely lit
        h = min(h, 5 + 10 * (1 - k))
        c = tuple(v * (1 - 0.35 * k) for v in c)
    taper = rng.choice([0, 0, 0, 0.4, 0.8]) if h > 14 else 0
    box(x0, y0, 0, x1, y1, h, c, taper=taper)
    windows(x0 + taper, y0 + taper, 0, x1 - taper, y1 - taper, h, p=(0.36 if h > 20 else 0.22) * (1 - 0.8 * k))
    top = h
    if h > 16 and rng.random() < 0.55:  # setback
        i = min(x1 - x0, y1 - y0) * rng.uniform(0.15, 0.28)
        h2 = h + rng.uniform(4, 14)
        box(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, tuple(v * 1.05 for v in c))
        windows(x0 + i, y0 + i, h, x1 - i, y1 - i, h2, p=0.3 * (1 - 0.8 * k))
        top = h2
        x0, y0, x1, y1 = x0 + i, y0 + i, x1 - i, y1 - i
    if k < 0.3 and rng.random() < 0.6:
        roof_trim(x0 + 0.2, y0 + 0.2, x1 - 0.2, y1 - 0.2, top + 0.15, rng.choice(TRIMS))
    if rng.random() < 0.35:  # roof box / AC units
        cx, cy = rng.uniform(x0 + 1, x1 - 3), rng.uniform(y0 + 1, y1 - 3)
        box(cx, cy, top, cx + 2, cy + 2, top + 1.4, (0.3, 0.3, 0.34), facet=False)
    if top > 26 and rng.random() < 0.6:  # antenna + beacon
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        beam((mx, my, top), (mx, my, top + rng.uniform(5, 12)), 0.25, (0.25, 0.25, 0.3))
        box(mx - 0.35, my - 0.35, top + 11.5, mx + 0.35, my + 0.35, top + 12.2, rng.choice([RED, CYAN]), facet=False, top=True) if False else None
        z = top + 8
        NEON.face([(mx - 0.5, my, z), (mx + 0.5, my, z), (mx + 0.5, my, z + 1), (mx - 0.5, my, z + 1)], RED, (0, 0, 0))


def fill_city(keep_out):
    for gx in range(-260, 260, 18):
        for gy in range(-150, 330, 18):
            for sub in range(rng.choice([1, 2, 2, 3])):
                w = rng.uniform(7, 15)
                d = rng.uniform(7, 15)
                x0 = gx + rng.uniform(0, 18 - min(w, 17))
                y0 = gy + rng.uniform(0, 18 - min(d, 17))
                x1, y1 = x0 + w, y0 + d
                bad = False
                for (xa, ya) in ((x0, y0), (x1, y0), (x0, y1), (x1, y1), ((x0 + x1) / 2, (y0 + y1) / 2)):
                    if in_street(xa, ya) or keep_out(xa, ya):
                        bad = True
                if bad or not onscreen((x0 + x1) / 2, (y0 + y1) / 2, 10, pad=0.25):
                    continue
                far = max(0.0, min(1.0, (y0 + 60) / 260))
                side = min(1.0, abs((x0 + x1) / 2) / 160)
                h = rng.uniform(6, 16) + far * rng.uniform(10, 60) + side * rng.uniform(0, 30)
                c = rng.choice(FAMS)
                if abs(x0) < 90 and -20 < y0 < 120:  # Meridian district: orange-brown family
                    c = rng.choice([(0.58, 0.38, 0.22), (0.62, 0.42, 0.24), (0.48, 0.34, 0.26)])
                building(x0, y0, x1, y1, h, c)


# ------------------------------------------------------------------ hero: Freight Ziggurat
def container(x, y, z, rot90=False, c=None, L=12.0, W=4.8, Hh=5.2):
    c = c or rng.choice([(0.72, 0.18, 0.12), (0.16, 0.36, 0.62), (0.15, 0.5, 0.48), MERIDIAN, (0.8, 0.78, 0.72), (0.5, 0.52, 0.2)])
    if rot90:
        x0, y0, x1, y1 = x - W / 2, y - L / 2, x + W / 2, y + L / 2
    else:
        x0, y0, x1, y1 = x - L / 2, y - W / 2, x + L / 2, y + W / 2
    bid = box(x0, y0, z, x1, y1, z + Hh, c, facet=True)
    # corrugation ribs on the long faces
    dark = tuple(v * 0.7 for v in c)
    n = 9
    for i in range(1, n):
        if rot90:
            yy = y0 + (y1 - y0) * i / n
            SOLID.face([(x0 - 0.05, yy - 0.2, z + 0.3), (x0 - 0.05, yy + 0.2, z + 0.3), (x0 - 0.05, yy + 0.2, z + Hh - 0.3), (x0 - 0.05, yy - 0.2, z + Hh - 0.3)], dark, bid)
        else:
            xx = x0 + (x1 - x0) * i / n
            SOLID.face([(xx - 0.2, y0 - 0.05, z + 0.3), (xx + 0.2, y0 - 0.05, z + 0.3), (xx + 0.2, y0 - 0.05, z + Hh - 0.3), (xx - 0.2, y0 - 0.05, z + Hh - 0.3)], dark, bid)
    return z + Hh


def ziggurat():
    tiers = [(32, 0, 11), (27, 11, 22), (22, 22, 33), (17, 33, 44), (12, 44, 55)]
    for i, (hs, z0, z1) in enumerate(tiers):
        c = (0.80 - i * 0.03, 0.44 - i * 0.02, 0.16)
        box(-hs, -hs, z0, hs, hs, z1, c)
        # tier window band: amber strip with mullion breaks on all four faces
        zb = z0 + (z1 - z0) * 0.42
        for (a, b, fixed, axis) in ((-hs, hs, -hs - 0.08, "y"), (-hs, hs, hs + 0.08, "y"), (-hs, hs, -hs - 0.08, "x"), (-hs, hs, hs + 0.08, "x")):
            n = int((b - a) / 3.0)
            for k in range(n):
                t0, t1 = a + k * 3.0 + 0.35, a + (k + 1) * 3.0 - 0.35
                if axis == "y":
                    q = [(t0, fixed, zb), (t1, fixed, zb), (t1, fixed, zb + 2.0), (t0, fixed, zb + 2.0)]
                else:
                    q = [(fixed, t0, zb), (fixed, t1, zb), (fixed, t1, zb + 2.0), (fixed, t0, zb + 2.0)]
                WIN.face(q, (1.0, 0.66, 0.26) if rng.random() < 0.85 else (0.45, 0.9, 1.0), (0, 0, 0))
        # corner steel columns + orange edge trim on the tier lip
        for sx in (-1, 1):
            for sy in (-1, 1):
                box(sx * hs - 0.9, sy * hs - 0.9, z0, sx * hs + 0.9, sy * hs + 0.9, z1 + 0.6, (0.14, 0.13, 0.15), facet=False)
        roof_trim(-hs, -hs, hs, hs, z1 + 0.1, (1.0, 0.55, 0.12), w=0.45)
        # pilasters on every face
        for k in range(1, 6):
            u = -hs + 2 * hs * k / 6
            for (x0_, y0_, x1_, y1_) in ((u - 0.5, -hs - 0.5, u + 0.5, -hs), (u - 0.5, hs, u + 0.5, hs + 0.5), (-hs - 0.5, u - 0.5, -hs, u + 0.5), (hs, u - 0.5, hs + 0.5, u + 0.5)):
                box(x0_, y0_, z0, x1_, y1_, z1, (0.30, 0.18, 0.10), facet=False)
        # cargo on the terrace ledge above this tier (the next tier is 5 smaller)
        if i < 4:
            for k in range(-1, 2):
                if rng.random() < 0.7:
                    container(k * (hs * 0.55), -hs + 2.6, z1, c=None, L=8, W=3.6, Hh=3.4)
                if rng.random() < 0.5:
                    container(-hs + 2.6, k * (hs * 0.55), z1, rot90=True, L=8, W=3.6, Hh=3.4)
    # loading docks on the front face of the base tier
    for k in range(-3, 4):
        x = k * 9.5
        box(x - 3.2, -36.6, 0, x + 3.2, -36.0, 6, (0.10, 0.09, 0.10), facet=False)
        for j in range(6):
            NEON.face([(x - 3.2 + j * 1.07, -36.7, 6.2), (x - 3.2 + (j + 0.5) * 1.07, -36.7, 6.2),
                       (x - 3.2 + (j + 0.5) * 1.07, -36.7, 6.8), (x - 3.2 + j * 1.07, -36.7, 6.8)], AMBER if j % 2 == 0 else (0.05, 0.04, 0.03), (0, 0, 0))
    # MERIDIAN FREIGHT sign on the front of tier 3, the gantry-hook logo on tier 4
    text_obj("MERIDIAN FREIGHT", (0, -27.6, 19.6), (math.radians(90), 0, 0), 3.6, SIGNM)
    text_obj("LANE 15", (0, -17.6, 41.4), (math.radians(90), 0, 0), 3.4, SIGNM)
    # crane gantry over the top
    hz = 80
    leg = (0.20, 0.18, 0.18)
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam((sx * 31, sy * 14, 0), (sx * 29, sy * 14, hz), 2.2, leg)
        beam((sx * 30.4, -14, 12), (sx * 29.6, 14, 40), 0.7, leg)
        beam((sx * 30.4, 14, 12), (sx * 29.6, -14, 40), 0.7, leg)
        beam((sx * 30, -14, hz - 18), (sx * 30, 14, hz - 18), 1.0, leg)
        beam((sx * 30.2, -14, 44), (sx * 29.8, 14, hz - 18), 0.7, leg)
        beam((sx * 30.2, 14, 44), (sx * 29.8, -14, hz - 18), 0.7, leg)
    for sy in (-1, 1):
        hazard_beam((-36, sy * 14, hz), (36, sy * 14, hz), 2.2)
    for sx in (-1, 1):
        beam((sx * 34, -14, hz), (sx * 34, 14, hz), 1.8, leg)
    # trolley + cables + hanging container
    box(2, -15, hz + 1.1, 9, 15, hz + 4, (0.24, 0.22, 0.22))
    for (cx, cy) in ((3.5, -2), (7.5, -2), (3.5, 2), (7.5, 2)):
        beam((cx, cy, hz), (cx, cy, 65.5), 0.18, (0.1, 0.1, 0.1))
    container(5.5, 0, 60, c=(0.16, 0.36, 0.62))
    for sx in (-36, 36):
        for sy in (-14, 14):
            box(sx - 0.6, sy - 0.6, hz + 1.1, sx + 0.6, sy + 0.6, hz + 2.3, RED, facet=False)
            NEON.face([(sx - 0.7, sy - 0.75, hz + 1.2), (sx + 0.7, sy - 0.75, hz + 1.2), (sx + 0.7, sy - 0.75, hz + 2.2), (sx - 0.7, sy - 0.75, hz + 2.2)], RED, (0, 0, 0))
    # plaza: disc of concrete with an orange ring line, lamps, container stacks flanking the front
    n = 48
    bid = rid()
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        SOLID.face([(0, 0, 0.02), (PLAZA_R * math.cos(a0), PLAZA_R * math.sin(a0), 0.02), (PLAZA_R * math.cos(a1), PLAZA_R * math.sin(a1), 0.02)], (0.30, 0.28, 0.30), bid)
        for r, w, c in ((PLAZA_R - 1.2, 0.5, AMBER), (PLAZA_R - 3.0, 0.25, (1.0, 0.45, 0.1))):
            strip(NEON, (r * math.cos(a0), r * math.sin(a0)), (r * math.cos(a1), r * math.sin(a1)), w, 0.05, c)
        if i % 4 == 0:
            x, y = (PLAZA_R - 2) * math.cos(a0), (PLAZA_R - 2) * math.sin(a0)
            if y < 0 and abs(x) < 13:
                continue
            beam((x, y, 0), (x, y, 5), 0.25, (0.2, 0.2, 0.22))
            box(x - 0.5, y - 0.5, 5, x + 0.5, y + 0.5, 5.6, (1.0, 0.8, 0.5), facet=False)
            NEON.face([(x - 0.55, y - 0.55, 5.62), (x + 0.55, y - 0.55, 5.62), (x + 0.55, y + 0.55, 5.62), (x - 0.55, y + 0.55, 5.62)], (1.0, 0.85, 0.55), (0, 0, 0))
    for sx in (-1, 1):  # stacks either side of the avenue mouth
        for row in range(2):
            for k in range(3):
                z = 0
                for lvl in range(rng.choice([2, 3, 3, 4])):
                    z = container(sx * (36 + k * 13), -46 - row * 6.4, z)
    # trucks on the avenue
    for (x, y, d) in ((-6.5, -70, 1), (6.5, -95, -1), (-6.5, -120, 1)):
        container(x, y, 1.4, rot90=True, L=12, W=4.4, Hh=4.6)
        box(x - 2.2, y + d * 6.5 - (0 if d > 0 else 3.5), 0.6, x + 2.2, y + d * 6.5 + (3.5 if d > 0 else 0), 4.8, (0.85, 0.82, 0.78))
        hy = y + d * 6.5 + (3.55 if d > 0 else -3.55)
        for hx in (x - 1.4, x + 1.4):
            NEON.face([(hx - 0.5, hy, 1.4), (hx + 0.5, hy, 1.4), (hx + 0.5, hy, 2.1), (hx - 0.5, hy, 2.1)], WHITE, (0, 0, 0))


def depot():
    # warehouse with sawtooth roof
    x0, x1, y0, y1 = -24, 24, 6, 34
    c = (0.62, 0.40, 0.20)
    box(x0, y0, 0, x1, y1, 11, c)
    for k in range(6):
        xa = x0 + k * 8
        bid = rid()
        SOLID.facet_quad((xa, y0, 11), (xa + 8, y0, 11), (xa + 8, y1, 11), (xa, y1, 11), (0.42, 0.30, 0.22), bid, jit=0.01)
        SOLID.face([(xa, y0, 11), (xa, y1, 11), (xa, y1, 15), (xa, y0, 15)], (0.75, 0.6, 0.35), bid)
        SOLID.face([(xa, y0, 15), (xa, y1, 15), (xa + 8, y1, 11), (xa + 8, y0, 11)], (0.5, 0.36, 0.24), bid)
        WIN.face([(xa - 0.05, y0 + 1, 11.5), (xa - 0.05, y1 - 1, 11.5), (xa - 0.05, y1 - 1, 14.3), (xa - 0.05, y0 + 1, 14.3)], (0.6, 0.85, 1.0), (0, 0, 0))
    for k in range(5):  # roll-up doors with hazard sills
        x = x0 + 5 + k * 9.5
        box(x - 3.2, y0 - 0.6, 0, x + 3.2, y0, 7, (0.10, 0.09, 0.10), facet=False)
        for j in range(6):
            NEON.face([(x - 3.2 + j * 1.07, y0 - 0.7, 7.2), (x - 3.2 + (j + 0.5) * 1.07, y0 - 0.7, 7.2),
                       (x - 3.2 + (j + 0.5) * 1.07, y0 - 0.7, 7.8), (x - 3.2 + j * 1.07, y0 - 0.7, 7.8)], AMBER if j % 2 == 0 else (0.05, 0.04, 0.03), (0, 0, 0))
    roof_trim(x0, y0, x1, y1, 11.1, (1.0, 0.55, 0.12), w=0.4)
    box(-15, y0 + 1, 15, 15, y0 + 1.6, 20.5, (0.12, 0.10, 0.10), facet=False)
    for x in (-12, 12):
        beam((x, y0 + 1.3, 11), (x, y0 + 1.3, 15), 0.5, (0.2, 0.2, 0.22))
    text_obj("MERIDIAN DEPOT 15", (0, y0 + 0.9, 17.8), (math.radians(90), 0, 0), 3.3, SIGNM)
    # yard: container rows in front
    for row in range(3):
        for k in range(-3, 4):
            if k == 0:
                continue
            z = 0
            for lvl in range(rng.choice([1, 1, 2, 2, 3])):
                z = container(k * 13.5, -8 - row * 7.0, z, L=12, W=4.8, Hh=4.4)
    # rubber-tyred yard gantry over the stacks
    hz = 26
    leg = (0.20, 0.18, 0.18)
    for sx in (-1, 1):
        for sy in (-1, 1):
            beam((sx * 26, -13 + sy * 6, 0), (sx * 26, -13 + sy * 6, hz), 1.2, leg)
    for sy in (-1, 1):
        hazard_beam((-28, -13 + sy * 6, hz), (28, -13 + sy * 6, hz), 1.6, seg=2.0)
    box(-20, -20, hz + 0.8, -14, -6, hz + 3, (0.24, 0.22, 0.22))
    for (cx, cy) in ((-18.5, -14), (-15.5, -14), (-18.5, -12), (-15.5, -12)):
        beam((cx, cy, hz), (cx, cy, 19.5), 0.15, (0.1, 0.1, 0.1))
    container(-17, -13, 15, c=MERIDIAN, L=12, W=4.8, Hh=4.4)
    for sx in (-28, 28):
        box(sx - 0.5, -13.5, hz + 0.8, sx + 0.5, -12.5, hz + 1.8, RED, facet=False)
    # floodlight masts
    for (x, y) in ((-36, -28), (36, -28), (-36, 40), (36, 40)):
        beam((x, y, 0), (x, y, 30), 0.6, (0.22, 0.22, 0.24))
        box(x - 2, y - 0.8, 30, x + 2, y + 0.8, 31.6, (0.9, 0.9, 0.85), facet=False)
        NEON.face([(x - 2, y - 0.85, 30.1), (x + 2, y - 0.85, 30.1), (x + 2, y - 0.85, 31.5), (x - 2, y - 0.85, 31.5)], (1.0, 0.95, 0.8), (0, 0, 0))
    # truck at the gate
    container(-5, -40, 1.4, rot90=True, L=12, W=4.4, Hh=4.6)
    box(-7.2, -50, 0.6, -2.8, -46.5, 4.8, (0.85, 0.82, 0.78))
    # yard fence line
    for x in range(-44, 45, 4):
        beam((x, -32, 0), (x, -32, 2.5), 0.15, (0.35, 0.35, 0.38))
    strip(NEON, (-44, -32), (-12, -32), 0.25, 2.4, AMBER)
    strip(NEON, (12, -32), (44, -32), 0.25, 2.4, AMBER)


if VARIANT == "boss":
    ziggurat()
    fill_city(lambda x, y: math.hypot(x, y) < PLAZA_R + 6 or (abs(x) < 70 and -56 < y < -36))
else:
    depot()
    fill_city(lambda x, y: (-50 < x < 50 and -36 < y < 40))

solid = SOLID.obj(TOON)
neon = NEON.obj(NEONM)
win = WIN.obj(WINM)

# key light (direction only matters for the toon ramp) + world
sun_d = bpy.data.lights.new("key", "SUN")
sun_d.energy = 3.2
sun = bpy.data.objects.new("key", sun_d)
sun.rotation_euler = (math.radians(48), math.radians(-28), math.radians(-38))
scene.collection.objects.link(sun)
world = bpy.data.worlds.new("w")
scene.world = world
wnt = world.node_tree
bg = wnt.nodes.get("Background")
bg.inputs["Color"].default_value = (0.05, 0.05, 0.07, 1)
bg.inputs["Strength"].default_value = 1.0

# ------------------------------------------------------------------ modes
MODES = {
    # ramp colours: shadow / mid / lit  (cool shadows, warm lit), glow gains, dark glass for windows by day
    "day": dict(ramp=[(0.26, 0.27, 0.40), (0.56, 0.55, 0.60), (0.86, 0.82, 0.72)], neon=0.75, neon_mix=0.0,
                win=0.55, win_mix=0.55, glass=(0.10, 0.13, 0.17), sign=(1.0, 0.6, 0.22), world=(0.50, 0.50, 0.52)),
    "night": dict(ramp=[(0.09, 0.08, 0.21), (0.20, 0.17, 0.36), (0.36, 0.30, 0.54)], neon=1.0, neon_mix=0.0,
                  win=1.0, win_mix=0.0, glass=(0.0, 0.0, 0.0), sign=(1.0, 0.62, 0.22), world=(0.03, 0.025, 0.06)),
}


def set_mode(m):
    M = MODES[m]
    els = RAMP.color_ramp.elements
    for e, c in zip(els, M["ramp"]):
        e.color = c + (1,)
    NEON_SC.inputs["Scale"].default_value = M["neon"]
    NEON_MIX.inputs["Factor"].default_value = M["neon_mix"]
    NEON_MIX.inputs[7].default_value = M["glass"] + (1,)
    WIN_SC.inputs["Scale"].default_value = M["win"]
    WIN_MIX.inputs["Factor"].default_value = M["win_mix"]
    WIN_MIX.inputs[7].default_value = M["glass"] + (1,)
    SIGN_EM.inputs["Color"].default_value = M["sign"] + (1,)
    bg.inputs["Color"].default_value = M["world"] + (1,)


def render(path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path, flush=True)


# ------------------------------------------------------------------ data-pass override materials
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
    L(em.outputs[0], out.inputs[0])
    return m


v = VARIANT
for m in ("day", "night"):
    set_mode(m)
    render(os.path.join(OUTDIR, "%s_beauty_%s.png" % (v, m)))
# glow-only pass: solid surfaces black, emissives as in the night/day mode
blackm, _ = mat_flat("black", (0.0, 0.0, 0.0))
solid.data.materials[0] = blackm
for m in ("day", "night"):
    set_mode(m)
    bg.inputs["Color"].default_value = (0, 0, 0, 1)
    render(os.path.join(OUTDIR, "%s_glow_%s.png" % (v, m)))
solid.data.materials[0] = TOON
bg.inputs["Color"].default_value = (0, 0, 0, 1)
scene.eevee.taa_render_samples = 4
for kind in ("normal", "id", "depth"):
    bpy.context.view_layer.material_override = override_mat(kind)
    if kind == "depth":
        bg.inputs["Color"].default_value = (1, 1, 1, 1)
    render(os.path.join(OUTDIR, "%s_%s.png" % (v, kind)))
bpy.context.view_layer.material_override = None
print("DONE", flush=True)






