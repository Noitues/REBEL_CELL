"""Render one S2 asset model to a transparent square PNG, auto-framed with an orthographic camera.

usage: blender -b --factory-startup --python render_item.py -- <item> <out.png> <px> [samples]
"""
import math
import os
import random
import sys
import bpy
from mathutils import Vector, Matrix
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tt_lib as T
import items3d as I

args = T.arg_list()
ITEM, OUT, PX = args[0], args[1], int(args[2])
SAMPLES = int(args[3]) if len(args) > 3 else 24

VIEW = {"op": (0.28, -1.0, 0.18), "en": (0.25, -1.0, 0.3), "bz": (0.0, -1.0, 0.0), "lm": (0.9, -1.0, 0.8),
        "th": (0.55, -1.0, 0.85), "cu": (0.3, -1.0, 0.35), "ca": (0.15, -1.0, 0.25), "it": (0.3, -1.0, 0.45),
        "gem": (0.0, -1.0, 0.0)}
fam = ITEM.split("_")[0]
LINE = {"th": 3.4, "cu": 3.0, "gem": 2.0}.get(fam, 3.2) * PX / 512.0

sc = T.reset()
T.MODE["name"] = "day"
T.MODE["grit"] = 0.7
T.setup_render(sc, w=PX, h=PX, samples=SAMPLES, transparent=True, line=max(1.4, LINE))
T.compositor(sc, bloom=(0.95, 0.6, 5))
wbg = next(n for n in sc.world.node_tree.nodes if n.type == "BACKGROUND")
wbg.inputs[1].default_value = 1.0
T.sun(2.6, "#ffe0b0", rot=(48, 0, -35), angle=8)
d = Vector(VIEW[fam]).normalized()
T.MODE["fake"] = tuple((Vector((-0.5, -0.8, 0.9))).normalized())
rng = random.Random(hash(ITEM) % 100000 if False else sum(ord(c) * (i + 1) for i, c in enumerate(ITEM)))
I.BUILDERS[ITEM](rng)
bpy.context.view_layer.update()

# camera basis
w_ = -d                       # camera looks along -w
w_ = (-d) * -1
fwd = -d                      # from camera toward target... camera placed at +d side
r_ = Vector((0, 0, 1)).cross(d).normalized() if abs(d.z) < 0.99 else Vector((1, 0, 0))
r_ = d.cross(Vector((0, 0, 1))).normalized() * -1
u_ = d.cross(r_).normalized() * -1
if u_.z < 0:
    u_ = -u_
r_ = u_.cross(d).normalized()
# project all evaluated geometry
dg = bpy.context.evaluated_depsgraph_get()
xs, ys, zs = [], [], []
for o in bpy.data.objects:
    if o.type not in ("MESH", "CURVE", "FONT") or o.hide_render:
        continue
    if any(c.name == "NOLINE" for c in o.users_collection) and o.name.startswith(("cyl",)) and False:
        continue
    oe = o.evaluated_get(dg)
    try:
        me = oe.to_mesh()
    except RuntimeError:
        continue
    mw = o.matrix_world
    for v in me.vertices:
        p = mw @ v.co
        xs.append(p.dot(r_))
        ys.append(p.dot(u_))
        zs.append(p.dot(d))
    oe.to_mesh_clear()
cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
span = max(max(xs) - min(xs), max(ys) - min(ys)) * 1.1
cam_d = bpy.data.cameras.new("ortho")
cam_d.type = "ORTHO"
cam_d.ortho_scale = span
cam_d.clip_start = 1.0
cam_d.clip_end = 120
cam = bpy.data.objects.new("cam", cam_d)
sc.collection.objects.link(cam)
cam.matrix_world = Matrix((r_, u_, d)).transposed().to_4x4()
cam.location = r_ * cx + u_ * cy + d * (max(zs) + 20)
sc.camera = cam
T.render(sc, OUT)
