"""Round 20: threat vehicle matrix v2 (stronger corp livery), Blender 5.2 headless. Models: veh_models.py.

Run: blender -b --factory-startup --python vehicles20.py -- <outdir>
Writes veh_beauty.png, veh_glow.png, veh_id.png, veh_normal.png (1920 x 1080 at 3.6x map zoom) and veh_layout.json.
Same camera angle as the raid map (layout.CAM yaw / pitch), same toon + neon materials, so they drop into the map.

Design language (one silhouette family per corporation, readable at map size):
  MERIDIAN   logistics   boxy containers, orange + hazard stripes, amber beacons
  SOLACE     biotech     white rounded capsules, green helix stripe, cool green glow
  HALCYON    civic/police angular wedges, violet, red/blue light bars
  ORBITAL    space       hovering pods + fins + thruster glow, pale blue, star-dot lights
  REBEL_CELL mirror      improvised scrap: asymmetric plates, ram bars, spray-red tags
Upgraded (+): bigger by 10 %, extra armour plates, a second light, rank chevrons on the roof.
"""
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import layout as LY  # noqa: E402

OUT = os.path.abspath(sys.argv[sys.argv.index("--") + 1]) if "--" in sys.argv else "."
os.makedirs(OUT, exist_ok=True)
import veh_models as VM  # noqa: E402
from veh_models import Acc, beam, at, ROWS  # noqa: E402
rng = VM.rng
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE"
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.eevee.taa_render_samples = 24
scene.view_settings.view_transform = "Standard"
SOLID, NEON = Acc("solid"), Acc("neon")
VM.SOLID, VM.NEON = SOLID, NEON
BID = VM.BID
AMBER = VM.AMBER
# camera: same angle as the raid map, closer (3.6x)
LY.CAM["target"] = (0.0, 0.0, 0.0)
LY.CAM["ortho"] = 200.0
r_, u_, f_ = LY.cam_basis()
rh = Vector((r_[0], r_[1], 0)).normalized()
fh = Vector((f_[0], f_[1], 0)).normalized()
cam_d = bpy.data.cameras.new("cam")
cam_d.type = "ORTHO"
cam_d.ortho_scale = LY.CAM["ortho"]
cam_d.clip_end = 3000
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
scene.camera = cam
cam.location = LY.cam_location()
cam.rotation_euler = Vector(f_).to_track_quat("-Z", "Y").to_euler()

# ground plate + lanes
ground = Acc("ground")
BID[0] = (0.0, 0.0, 0.0)
ground.face([(-300, -300, 0), (300, -300, 0), (300, 300, 0), (-300, 300, 0)], (0.15, 0.15, 0.19), (0, 0, 0))
layout = []
heading = math.pi                              # vehicles drive along the street (world -x), as on the map
COLS = 6
for ri, (corp, ccol, units) in enumerate(ROWS):
    for ci in range(COLS):
        ui, up = ci // 2, ci % 2 == 1
        pos = rh * ((ci - 2.5) * 28.0 + 10.4) - fh * ((ri - 2.0) * 18.0) + fh * 12.2
        x, y = pos.x, pos.y
        # a street lane under each vehicle (aligned with world x, like the map's streets)
        lx = Vector((math.cos(heading), math.sin(heading), 0))
        for sgn in (-1, 1):
            p0 = pos - lx * 8 + Vector((-lx.y, lx.x, 0)) * sgn * 5.0
            p1 = pos + lx * 8 + Vector((-lx.y, lx.x, 0)) * sgn * 5.0
            BID[0] = (0.0, 0.0, 0.0)
            beam((p0.x, p0.y, 0.03), (p1.x, p1.y, 0.03), 0.25, (0.30, 0.30, 0.38), acc=NEON)
        BID[0] = (rng.random(), rng.random(), rng.random())
        name, role, fn = units[ui]
        VM.build(corp, ui, x, y, heading, up)
        layout.append(dict(corp=corp, unit=name, role=role, up=up, x=x, y=y, row=ri, col=ci))

solid = SOLID.obj(None)
TO = None


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
    el[0].position, el[1].position = 0.0, 0.12
    el.new(0.32)
    for e, c in zip(el, [(0.06, 0.055, 0.14), (0.16, 0.14, 0.28), (0.36, 0.32, 0.52)]):
        e.color = c + (1,)
    col = attr(nt, "col")
    fj = attr(nt, "fj")
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["To Min"].default_value = 0.9
    mr.inputs["To Max"].default_value = 1.1
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
    return m


def mat_emit(name, black=False):
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    if black:
        em.inputs["Color"].default_value = (0, 0, 0, 1)
    else:
        nt.links.new(attr(nt, "col").outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    return m


TOONM, NEONM, BLACK = mat_toon(), mat_emit("neon"), mat_emit("black", True)
solid.data.materials[0] = TOONM
neon = NEON.obj(NEONM)
gr = ground.obj(TOONM)
sun_d = bpy.data.lights.new("key", "SUN")
sun_d.energy = 3.2
sun = bpy.data.objects.new("key", sun_d)
sun.rotation_euler = (math.radians(46), math.radians(-24), math.radians(-30))
scene.collection.objects.link(sun)
world = bpy.data.worlds.new("w")
scene.world = world
world.node_tree.nodes.get("Background").inputs["Color"].default_value = (0.02, 0.02, 0.04, 1)


def render(name):
    scene.render.filepath = os.path.join(OUT, name)
    scene.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)


render("veh_beauty.png")
solid.data.materials[0] = BLACK
gr.data.materials[0] = BLACK
render("veh_glow.png")
solid.data.materials[0] = TOONM
gr.data.materials[0] = TOONM
scene.eevee.taa_render_samples = 1
scene.render.filter_size = 0.01
for kind in ("normal", "id"):
    m = bpy.data.materials.new("ov_" + kind)
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    if kind == "normal":
        geo = nt.nodes.new("ShaderNodeNewGeometry")
        vm = nt.nodes.new("ShaderNodeVectorMath")
        vm.operation = "MULTIPLY_ADD"
        vm.inputs[1].default_value = (0.5, 0.5, 0.5)
        vm.inputs[2].default_value = (0.5, 0.5, 0.5)
        nt.links.new(geo.outputs["Normal"], vm.inputs[0])
        nt.links.new(vm.outputs[0], em.inputs["Color"])
    else:
        nt.links.new(attr(nt, "bid").outputs["Color"], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs[0])
    bpy.context.view_layer.material_override = m
    render("veh_%s.png" % kind)
bpy.context.view_layer.material_override = None
for d in layout:
    p = LY.project(d["x"], d["y"], 0.0)
    d["px"], d["py"] = p[0], p[1]
json.dump(dict(items=layout, ortho=LY.CAM["ortho"]), open(os.path.join(OUT, "veh_layout.json"), "w"), indent=1)
print("DONE", flush=True)
