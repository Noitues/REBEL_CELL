"""ART-1 1D spike (b): the district baked in Blender 5.2 (Eevee), the concept pipeline.

blender -b --factory-startup --python bake_district.py -- <district.json> <outdir> <view>[,<view>...] [<width> <height>]

Builds the same district the real-time path draws (export_district.gd: the game's own layout) with the concept
recipe (art-concepts-r43 round 40 `unified40.city_building` + `target_corps`): walls split into jittered triangles
(~1.7 BU cells) with a tone value per triangle, the 3-band toon ramp (night), window quads, ledges, neon roof trim,
street-level shopfronts, the ground and lane glow triangles exported from Godot. Per view it renders:
  <view>_beauty.png, <view>_glow.png (emission only), <view>_normal.png, <view>_id.png, <view>_depth.png (16 bit)
  and, when the view is see-through (opacity < 1), <view>_gbeauty.png / <view>_gglow.png (ground only).
post_bake.py turns them into the finished layers. Deterministic: random.Random seeded per building key.
Godot world (X, Y up, Z) is Blender (X, -Z, Y).
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT, VIEWS = argv[0], argv[1], argv[2].split(",")
RES = (int(argv[3]), int(argv[4])) if len(argv) > 4 else (1920, 1080)
os.makedirs(OUT, exist_ok=True)
D = json.load(open(SRC))
FACET = 1.7
LEDGE = 6.0
WIN_COLS = [tuple(c) for c in D["window_colors"]]
WP = D["window_share"]
SHOP = [(1.0, 0.75, 0.45), (1.0, 0.5, 0.8), (0.5, 0.9, 1.0), (1.0, 0.85, 0.6)]
SIGNC = [(1.0, 0.3, 0.65), (0.3, 0.85, 1.0), (1.0, 0.62, 0.15), (0.75, 0.45, 1.0), (0.4, 1.0, 0.6), (1.0, 0.25, 0.25)]
rng = random.Random(4040)

for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.eevee.taa_render_samples = 16
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_depth = "16"
scene.render.film_transparent = False


def B(p):
    """Godot world -> Blender."""
    return (p[0], -p[2], p[1])


class Acc:
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

    def obj(self, mat):
        me = bpy.data.meshes.new(self.name)
        self.bm.to_mesh(me)
        self.bm.free()
        ob = bpy.data.objects.new(self.name, me)
        scene.collection.objects.link(ob)
        me.materials.append(mat)
        return ob


CITY, NEON, WIN, GROUND, LANE = Acc("city"), Acc("neon"), Acc("win"), Acc("ground"), Acc("lane")


def fgrid(A, B_, C, D_, col, bid, r, cell=FACET):
    """unified40.fgrid: a wall split into a jittered grid of triangles, a tone per triangle."""
    A, B_, C, D_ = map(Vector, (A, B_, C, D_))
    n = (B_ - A).cross(D_ - A)
    if n.length < 1e-6:
        return
    n.normalize()
    nu = max(2, min(12, int(round((B_ - A).length / cell))))
    nv = max(2, min(30, int(round((D_ - A).length / cell))))
    grid = []
    for j in range(nv + 1):
        row = []
        for i in range(nu + 1):
            u, v = i / nu, j / nv
            p = A.lerp(B_, u).lerp(D_.lerp(C, u), v)
            if 0 < i < nu and 0 < j < nv:
                p = p + (B_ - A) / nu * r.uniform(-0.28, 0.28) + (D_ - A) / nv * r.uniform(-0.28, 0.28) + n * r.uniform(-0.12, 0.12)
            row.append(tuple(p))
        grid.append(row)
    patch = r.random()
    for j in range(nv):
        for i in range(nu):
            p00, p10, p11, p01 = grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]
            f1 = 0.5 + (patch - 0.5) * 0.6 + r.uniform(-0.4, 0.4)
            f2 = 0.5 + (patch - 0.5) * 0.6 + r.uniform(-0.4, 0.4)
            if (i + j) % 2 == 0:
                CITY.face([p00, p10, p11], col, bid, fj=f1)
                CITY.face([p00, p11, p01], col, bid, fj=f2)
            else:
                CITY.face([p00, p10, p01], col, bid, fj=f1)
                CITY.face([p10, p11, p01], col, bid, fj=f2)


def beam(p0, p1, w, col, acc):
    p0, p1 = Vector(p0), Vector(p1)
    d = (p1 - p0)
    if d.length < 1e-6:
        return
    d.normalize()
    up = Vector((0, 0, 1)) if abs(d.z) < 0.95 else Vector((1, 0, 0))
    a = d.cross(up).normalized() * (w / 2)
    b = d.cross(a).normalized() * (w / 2)
    c0 = [p0 + a + b, p0 - a + b, p0 - a - b, p0 + a - b]
    c1 = [p1 + a + b, p1 - a + b, p1 - a - b, p1 + a - b]
    bid = (rng.random(), rng.random(), rng.random())
    for i in range(4):
        j = (i + 1) % 4
        acc.face([tuple(c0[i]), tuple(c0[j]), tuple(c1[j]), tuple(c1[i])], col, bid)
    acc.face([tuple(v) for v in c1], col, bid)


CAMDIR = (math.cos(math.radians(D["yaw"])), math.sin(math.radians(D["yaw"])))
CAMDIR = (-CAMDIR[0], -CAMDIR[1])  # horizontal direction from the scene toward the camera


def building(b):
    r = random.Random(b["key"] * 7 + 13)
    q = [(p[0], -p[1]) for p in b["poly"]]
    n = len(q)
    z0, h, ts = b["y0"], b["h"], b["taper"]
    col = tuple(b["col"])
    cx, cy = sum(p[0] for p in q) / n, sum(p[1] for p in q) / n
    top = [(cx + (x - cx) * ts, cy + (y - cy) * ts) for (x, y) in q]
    bid = (r.random(), r.random(), r.random())
    for i in range(n):
        j = (i + 1) % n
        a, c = q[i], q[j]
        quad = [(a[0], a[1], z0), (c[0], c[1], z0), (top[j][0], top[j][1], z0 + h), (top[i][0], top[i][1], z0 + h)]
        L = math.hypot(c[0] - a[0], c[1] - a[1])
        ux, uy = (c[0] - a[0]) / (L or 1), (c[1] - a[1]) / (L or 1)
        nx, ny = uy, -ux
        if nx * (a[0] - cx) + ny * (a[1] - cy) < 0:
            nx, ny = -nx, -ny
        seen = nx * CAMDIR[0] + ny * CAMDIR[1] > 0.1
        if seen and L > 2.0 and h > 3.0:
            fgrid(*quad, col, bid, r)
        else:
            CITY.face(quad, col, bid)
        if L < 1.2 or ts < 0.99 or not seen:
            continue
        if h > 2.4:
            nxw, nzw = int((L - 0.6) / 1.6), int((h - 1.6) / 1.9)
            for u in range(nxw):
                for v in range(nzw):
                    if r.random() > WP:
                        continue
                    t0 = 0.3 + u * 1.6 + 0.4
                    z = z0 + 1.6 + v * 1.9
                    wc = r.choice(WIN_COLS)
                    s = 0.5 + 0.5 * r.random()
                    p0 = (a[0] + ux * t0 + nx * 0.05, a[1] + uy * t0 + ny * 0.05)
                    p1 = (p0[0] + ux * 0.8, p0[1] + uy * 0.8)
                    WIN.face([(p0[0], p0[1], z), (p1[0], p1[1], z), (p1[0], p1[1], z + 0.7), (p0[0], p0[1], z + 0.7)],
                             tuple(x * s for x in wc), (0, 0, 0))
        if z0 > 0.5:
            continue
        if L > 2.5 and h > 2.0 and r.random() < 0.55:
            m0, m1 = 0.4, L - 0.4
            p0 = (a[0] + ux * m0 + nx * 0.06, a[1] + uy * m0 + ny * 0.06)
            p1 = (a[0] + ux * m1 + nx * 0.06, a[1] + uy * m1 + ny * 0.06)
            sc = r.choice(SHOP)
            WIN.face([(p0[0], p0[1], 0.15), (p1[0], p1[1], 0.15), (p1[0], p1[1], 1.05), (p0[0], p0[1], 1.05)],
                     tuple(v * 0.8 for v in sc), (0, 0, 0))
        if h > 7.0:
            k = 1
            while 3.0 * k < h - 1.0:
                zl = z0 + 3.0 * k + 0.9
                beam((a[0] + nx * 0.12, a[1] + ny * 0.12, zl), (c[0] + nx * 0.12, c[1] + ny * 0.12, zl), 0.16,
                     tuple(v * 0.8 for v in col), CITY)
                k += 2
        if h > 5.0 and L > 2.0 and r.random() < 0.16:
            sc = r.choice(SIGNC)
            t0 = r.uniform(0.6, L - 0.6)
            bx, by = a[0] + ux * t0 + nx * 0.5, a[1] + uy * t0 + ny * 0.5
            zb = r.uniform(1.6, max(2.0, min(h - 2.6, 7.0)))
            beam((bx, by, zb), (bx, by, zb + r.uniform(1.6, 3.2)), 0.36, sc, NEON)
    CITY.face([(x, y, z0 + h) for (x, y) in top], tuple(min(1, v * 1.08) for v in col), bid)
    if b["trim"]:
        for i in range(n):
            j = (i + 1) % n
            beam((top[i][0], top[i][1], z0 + h + 0.08), (top[j][0], top[j][1], z0 + h + 0.08), 0.22, tuple(b["ink"]), NEON)


for b in D["prisms"]:
    building(b)
print("BUILT faces", len(CITY.bm.faces), flush=True)


def tri_list(acc, tris, lift=0.0):
    for t in tris:
        pts = [B((t[0], t[1] + lift, t[2])), B((t[3], t[4] + lift, t[5])), B((t[6], t[7] + lift, t[8]))]
        acc.face(pts, (t[9], t[10], t[11]), (0, 0, 0), fj=0.5)


tri_list(GROUND, D["ground"])
tri_list(LANE, D["lanes"], 0.01)


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
    for e, c in zip(ramp.color_ramp.elements, D["ramp"]):
        e.color = (c[0], c[1], c[2], 1)
    return m, ramp


def mat_glow(name):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(attr(nt, "col").outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


def mat_override(kind):
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
        L(attr(nt, "bid").outputs["Color"], em.inputs["Color"])
    elif kind == "depth":
        cd = nt.nodes.new("ShaderNodeCameraData")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value = 0.0
        mr.inputs["From Max"].default_value = 6000.0
        L(cd.outputs["View Distance"], mr.inputs["Value"])
        L(mr.outputs[0], em.inputs["Color"])
    L(em.outputs[0], out.inputs[0])
    return m


TOON, RAMP = mat_toon()
GLOWM = mat_glow("glow")
city_o = CITY.obj(TOON)
ground_o = GROUND.obj(TOON)
neon_o = NEON.obj(GLOWM)
win_o = WIN.obj(GLOWM)
lane_o = LANE.obj(GLOWM)
BUILDINGS = [city_o, neon_o, win_o]

sun_d = bpy.data.lights.new("key", "SUN")
sun_d.energy = 3.2
sun = bpy.data.objects.new("key", sun_d)
sun.rotation_euler = (math.radians(48), math.radians(-28), math.radians(-38))
scene.collection.objects.link(sun)
world = bpy.data.worlds.new("w")
scene.world = world
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = tuple(D["sky"]) + (1,)
try:
    scene.eevee.shadow_pool_size = "1024"
except Exception:
    pass

cam_data = bpy.data.cameras.new("cam")
cam_data.type = "ORTHO"
cam_data.clip_start = 1.0
cam_data.clip_end = 8000
cam = bpy.data.objects.new("cam", cam_data)
scene.collection.objects.link(cam)
scene.camera = cam


def place(view):
    v = D["views"][view]
    yw, pt = math.radians(D["yaw"]), math.radians(D["pitch"])
    fwd = Vector((math.cos(yw) * math.cos(pt), math.sin(yw) * math.cos(pt), -math.sin(pt)))
    t = Vector(B(v["target"]))
    cam.location = t - fwd * D["distance"]
    cam.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()
    cam_data.ortho_scale = v["ortho"]


def render(path):
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDERED", path, flush=True)


def ramp_black(on):
    for e, c in zip(RAMP.color_ramp.elements, D["ramp"]):
        e.color = (0, 0, 0, 1) if on else (c[0], c[1], c[2], 1)


for view in VIEWS:
    place(view)
    base = os.path.join(OUT, view + "_")
    vl = scene.view_layers[0]
    vl.material_override = None
    ramp_black(False)
    render(base + "beauty.png")
    ramp_black(True)
    render(base + "glow.png")
    ramp_black(False)
    for kind in ("normal", "id", "depth"):
        vl.material_override = mat_override(kind)
        render(base + kind + ".png")
    vl.material_override = None
    if D["views"][view]["opacity"] < 0.999:
        for o in BUILDINGS:
            o.hide_render = True
        render(base + "gbeauty.png")
        ramp_black(True)
        render(base + "gglow.png")
        ramp_black(False)
        for o in BUILDINGS:
            o.hide_render = False
print("DONE", flush=True)
