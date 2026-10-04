"""Round 31: a low-poly cel bust (Cv2 triangulated facets + E toon bands + inverted-hull ink line).
Blender 5.2 headless:  blender -b --factory-startup -P bust_blender.py -- <out.png> <variant>
variant: breaker (operative, hood + visor) | fixer (contact, buzz cut + glasses, coat collar)
"""
import math
import random
import sys

import bpy
import bmesh
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
OUTP = argv[0] if argv else "bust.png"
VAR = argv[1] if len(argv) > 1 else "breaker"
DEBUG = len(argv) > 2 and argv[2] == "debug"
RNG = random.Random(31 if VAR == "breaker" else 47)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


# ------------------------------------------------------------------ materials
def toon(name, base, dark_k=0.42, mid_k=0.72, rim=(1.0, 0.25, 0.65), rim_k=0.55, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if emit > 0:
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs["Color"].default_value = base + (1,)
        e.inputs["Strength"].default_value = emit
        nt.links.new(e.outputs[0], out.inputs["Surface"])
        return m
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    dif.inputs["Color"].default_value = (1, 1, 1, 1)
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(s2r.outputs[0], bw.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[0].color = (dark_k, dark_k, dark_k, 1)
    el[1].position = 0.32
    el[1].color = (1, 1, 1, 1)
    e2 = el.new(0.06)
    e2.color = (mid_k, mid_k, mid_k, 1)
    nt.links.new(bw.outputs[0], ramp.inputs[0])
    # per-face jitter (gritty triangulation)
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "jit"
    attr.attribute_type = "GEOMETRY"
    mul0 = nt.nodes.new("ShaderNodeMix")
    mul0.data_type = "RGBA"
    mul0.blend_type = "MULTIPLY"
    mul0.inputs[0].default_value = 1.0
    mul0.inputs[6].default_value = base + (1,)
    nt.links.new(ramp.outputs[0], mul0.inputs[7])
    mulj = nt.nodes.new("ShaderNodeMix")
    mulj.data_type = "RGBA"
    mulj.blend_type = "MULTIPLY"
    mulj.inputs[0].default_value = 1.0
    nt.links.new(mul0.outputs[2], mulj.inputs[6])
    nt.links.new(attr.outputs["Color"], mulj.inputs[7])
    # rim on the right-hand side (class colour spill)
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    rr = nt.nodes.new("ShaderNodeValToRGB")
    rr.color_ramp.interpolation = "CONSTANT"
    rr.color_ramp.elements[0].color = (0, 0, 0, 1)
    rr.color_ramp.elements[1].position = 0.62
    rr.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(lw.outputs["Facing"], rr.inputs[0])
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(geo.outputs["Normal"], sep.inputs[0])
    side = nt.nodes.new("ShaderNodeMath")
    side.operation = "GREATER_THAN"
    side.inputs[1].default_value = 0.15
    nt.links.new(sep.outputs[0], side.inputs[0])
    rm = nt.nodes.new("ShaderNodeMath")
    rm.operation = "MULTIPLY"
    nt.links.new(rr.outputs[0], rm.inputs[0])
    nt.links.new(side.outputs[0], rm.inputs[1])
    rk = nt.nodes.new("ShaderNodeMath")
    rk.operation = "MULTIPLY"
    rk.inputs[1].default_value = rim_k
    nt.links.new(rm.outputs[0], rk.inputs[0])
    add = nt.nodes.new("ShaderNodeMix")
    add.data_type = "RGBA"
    add.blend_type = "ADD"
    nt.links.new(rk.outputs[0], add.inputs[0])
    nt.links.new(mulj.outputs[2], add.inputs[6])
    add.inputs[7].default_value = rim + (1,)
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(add.outputs[2], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    if DEBUG:
        nt.links.new(s2r.outputs[0], em.inputs["Color"])
    return m


INK = bpy.data.materials.new("ink")
INK.use_nodes = True
for n in list(INK.node_tree.nodes):
    INK.node_tree.nodes.remove(n)
_o = INK.node_tree.nodes.new("ShaderNodeOutputMaterial")
_e = INK.node_tree.nodes.new("ShaderNodeEmission")
_e.inputs["Color"].default_value = (0.012, 0.01, 0.02, 1)
INK.node_tree.links.new(_e.outputs[0], _o.inputs["Surface"])
INK.use_backface_culling = True


def finish(obj, mat, jitter=0.07, ink=0.03, tri=True):
    obj.data.materials.append(mat)
    obj.data.materials.append(INK)
    me = obj.data
    if tri:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.to_mesh(me)
        bm.free()
    for p in me.polygons:
        p.use_smooth = False
        p.material_index = 0
    a = me.attributes.new("jit", "FLOAT_COLOR", "FACE")
    for i in range(len(me.polygons)):
        v = 1.0 + RNG.uniform(-jitter, jitter)
        a.data[i].color = (v, v, v, 1)
    sol = obj.modifiers.new("ink", "SOLIDIFY")
    sol.thickness = ink
    sol.offset = 1
    sol.use_flip_normals = True
    sol.material_offset = 1
    obj.visible_shadow = False
    return obj


def jitter_verts(obj, amt):
    for v in obj.data.vertices:
        v.co += Vector((RNG.uniform(-amt, amt), RNG.uniform(-amt, amt), RNG.uniform(-amt, amt)))


def sphere(name, seg, ring, r, loc, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=r, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return o


def cyl(name, verts, r1, r2, depth, loc, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return o


def box(name, loc, size, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return o


def boolean(obj, cutter, op="DIFFERENCE"):
    m = obj.modifiers.new("b", "BOOLEAN")
    m.operation = op
    m.object = cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


# ------------------------------------------------------------------ the bust
SKIN = (0.62, 0.36, 0.26) if VAR == "breaker" else (0.30, 0.17, 0.11)
RIM = (1.0, 0.24, 0.66) if VAR == "breaker" else (0.36, 0.88, 1.0)

head = sphere("head", 9, 7, 1.0, (0, 0, 0), (0.82, 0.92, 1.08))
for v in head.data.vertices:
    if v.co.z < -0.2:  # jaw tapers to a chin
        k = (-0.2 - v.co.z) / 0.9
        v.co.x *= 1 - 0.38 * k
        v.co.y = v.co.y * (1 - 0.22 * k) - 0.06 * k
    if v.co.y < -0.5 and abs(v.co.x) < 0.3 and -0.3 < v.co.z < 0.3:
        v.co.y -= 0.08
jitter_verts(head, 0.035)
finish(head, toon("skin", SKIN, rim=RIM, rim_k=0.45))

nose = cyl("nose", 4, 0.15, 0.0, 0.34, (0, -0.9, -0.1), rot=(math.radians(100), 0, 0), scale=(0.8, 1, 1))
finish(nose, toon("skin2", SKIN, rim=RIM, rim_k=0.45))
for sx in (-1, 1):
    ear = sphere("ear", 5, 4, 0.2, (sx * 0.8, 0.05, -0.02), (0.4, 1.0, 1.3))
    finish(ear, toon("skin3", SKIN, rim=RIM, rim_k=0.45))

mouth = box("mouth", (0.0, -0.8, -0.5), (0.32, 0.05, 0.04), rot=(0, 0, math.radians(-4)))
finish(mouth, toon("mouth", (0.25, 0.1, 0.12), rim=RIM, rim_k=0.0), ink=0.004)

neck = cyl("neck", 7, 0.36, 0.42, 1.0, (0, 0.1, -1.15))
finish(neck, toon("neck", tuple(c * 0.8 for c in SKIN), rim=RIM, rim_k=0.35))

# torso / shoulders
torso = sphere("torso", 10, 6, 1.0, (0, 0.25, -2.55), (2.15, 1.05, 1.15))
for v in torso.data.vertices:
    if v.co.z > -2.2:
        v.co.z = -2.2 + (v.co.z + 2.2) * 0.55
jitter_verts(torso, 0.05)
JACKET = (0.09, 0.06, 0.12) if VAR == "breaker" else (0.20, 0.11, 0.05)
finish(torso, toon("jacket", JACKET, rim=RIM, rim_k=0.6))

collar = cyl("collar", 8, 0.72, 0.6, 0.55, (0, 0.18, -1.55))
finish(collar, toon("collar", tuple(c * 1.3 for c in JACKET), rim=RIM, rim_k=0.6))

if VAR == "breaker":
    hood = sphere("hood", 10, 8, 1.0, (0, 0.18, 0.05), (1.06, 1.12, 1.28))
    for v in hood.data.vertices:
        if v.co.z < -0.4:
            k = (-0.4 - v.co.z)
            v.co.x *= 1 + 0.55 * k
            v.co.y += 0.25 * k
    cut = box("cut", (0, -1.2, -0.6), (1.75, 1.3, 2.8), rot=(math.radians(-14), 0, 0))
    boolean(hood, cut)
    jitter_verts(hood, 0.03)
    finish(hood, toon("hood", (0.16, 0.07, 0.19), rim=RIM, rim_k=0.7))
    visor = cyl("visor", 10, 0.9, 0.9, 0.22, (0, 0.0, 0.16), scale=(0.97, 1.08, 1))
    boolean(visor, box("vcut", (0, 0.55, 0.16), (2.4, 1.2, 1)))
    finish(visor, toon("visor", (1.0, 0.16, 0.55), emit=1.6), ink=0.012, tri=False)
    # class stripe on the jacket
    stripe = box("stripe", (0.9, -0.62, -2.45), (0.22, 0.12, 1.1), rot=(0, math.radians(-22), math.radians(14)))
    finish(stripe, toon("stripe", (1.0, 0.16, 0.55), emit=1.3), ink=0.01)
    led = sphere("led", 5, 4, 0.07, (-0.83, -0.12, -0.05), (1, 1, 1))
    finish(led, toon("led", (0.36, 0.88, 1.0), emit=6.0), ink=0.006, tri=False)
else:
    hair = sphere("hair", 9, 6, 1.0, (0, 0.06, 0.2), (0.86, 0.96, 0.95))
    boolean(hair, box("hcut", (0, -0.2, -0.75), (3, 3, 1.6)))
    boolean(hair, box("hcut2", (0, -1.12, 0.1), (3, 0.9, 3)))
    jitter_verts(hair, 0.025)
    finish(hair, toon("hair", (0.08, 0.07, 0.09), rim=RIM, rim_k=0.6))
    for sx in (-1, 1):
        lens = cyl("lens", 6, 0.2, 0.2, 0.06, (sx * 0.3, -0.92, 0.12), rot=(math.radians(90), 0, 0))
        finish(lens, toon("lens", (0.2, 0.75, 1.0), emit=1.4), ink=0.012, tri=False)
    bridge = box("bridge", (0, -0.94, 0.14), (0.24, 0.05, 0.05))
    finish(bridge, toon("frame", (0.1, 0.1, 0.12), rim=RIM), ink=0.008)
    for sx in (-1, 1):
        lap = box("lapel", (sx * 0.42, -0.86, -2.15), (0.34, 0.1, 1.1), rot=(math.radians(14), math.radians(sx * 8), math.radians(-sx * 24)))
        finish(lap, toon("lapel", (0.12, 0.06, 0.03), rim=RIM, rim_k=0.5))
    shirt = box("shirt", (0, -0.78, -2.0), (0.5, 0.1, 1.0), rot=(math.radians(14), 0, 0))
    finish(shirt, toon("shirt", (0.55, 0.52, 0.5), rim=RIM, rim_k=0.3))

# ------------------------------------------------------------------ camera, lights, render
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 62
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
cam.location = (2.6, -7.6, 0.25)
direction = Vector((0, 0, -0.75)) - cam.location
cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

key = bpy.data.lights.new("key", "SUN")
key.energy = 2.4
ko = bpy.data.objects.new("key", key)
ko.rotation_euler = (Vector((0, 0, -0.3)) - Vector((-4.5, -6.0, 4.5))).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(ko)

world = bpy.data.worlds.new("w")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs["Color"].default_value = (0.02, 0.02, 0.03, 1)
    bg.inputs["Strength"].default_value = 0.3
scene.world = world

r = scene.render
try:
    r.engine = "BLENDER_EEVEE"
except TypeError:
    r.engine = "BLENDER_EEVEE_NEXT"
r.resolution_x = 900
r.resolution_y = 1000
r.film_transparent = True
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGBA"
try:
    scene.view_settings.view_transform = "Standard"
except Exception as ex:
    print("VT", ex, [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items])
print("VIEW", scene.view_settings.view_transform)
r.filepath = OUTP
bpy.ops.render.render(write_still=True)
print("RENDERED", OUTP)
