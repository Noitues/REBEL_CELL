"""Round 42: the Cell's HQ room, a lived-in hacker den above the canyon street (Cv2 low-poly + E toon).
Blender headless:  blender -b --factory-startup -P hq_scene.py -- <out_dir> <window_image> <home|dispatch>
Writes <out_dir>/room_<variant>.png and <out_dir>/quads_<variant>.json: every screen / paper quad's 4
corners in image pixels (TL, TR, BR, BL as seen), so the 2D pass can warp CRT content onto them.
"""
import json
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

argv = sys.argv[sys.argv.index("--") + 1:]
OUT, WIN_IMG, VAR = argv[0], argv[1], argv[2]
DISPATCH = VAR == "dispatch"
RNG = random.Random(42)
RES = (1920, 1080)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def lin(c):
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


INK = bpy.data.materials.new("ink")
INK.use_nodes = True
_nt = INK.node_tree
for _n in list(_nt.nodes):
    _nt.nodes.remove(_n)
_o = _nt.nodes.new("ShaderNodeOutputMaterial")
_e = _nt.nodes.new("ShaderNodeEmission")
_e.inputs["Color"].default_value = (0.012, 0.01, 0.02, 1)
_nt.links.new(_e.outputs[0], _o.inputs["Surface"])
INK.use_backface_culling = True
_mats = {}


def toon(base, rim=(1.0, 0.24, 0.66), rim_k=0.25, emit=0.0, name="m"):
    key = (base, rim, rim_k, emit)
    if key in _mats:
        return _mats[key]
    b = lin(base)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    if emit > 0:
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs["Color"].default_value = b + (1,)
        e.inputs["Strength"].default_value = emit
        nt.links.new(e.outputs[0], out.inputs["Surface"])
        _mats[key] = m
        return m
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[0].color = (0.30, 0.30, 0.34, 1)
    el[1].position = 0.30
    el[1].color = (1.0, 1.0, 1.0, 1)
    e2 = el.new(0.08)
    e2.color = (0.62, 0.62, 0.66, 1)
    # keep the light colour (screens tint the room): multiply the ramp by the normalised light colour
    nt.links.new(s2r.outputs[0], ramp.inputs[0])
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(s2r.outputs[0], sep.inputs[0])
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    nt.links.new(sep.outputs[0], mx.inputs[0])
    nt.links.new(sep.outputs[1], mx.inputs[1])
    mx2 = nt.nodes.new("ShaderNodeMath")
    mx2.operation = "MAXIMUM"
    nt.links.new(mx.outputs[0], mx2.inputs[0])
    nt.links.new(sep.outputs[2], mx2.inputs[1])
    mx3 = nt.nodes.new("ShaderNodeMath")
    mx3.operation = "MAXIMUM"
    mx3.inputs[1].default_value = 0.001
    nt.links.new(mx2.outputs[0], mx3.inputs[0])
    hue = nt.nodes.new("ShaderNodeVectorMath")
    hue.operation = "DIVIDE"
    nt.links.new(s2r.outputs[0], hue.inputs[0])
    nt.links.new(mx3.outputs[0], hue.inputs[1])
    huemix = nt.nodes.new("ShaderNodeMix")
    huemix.data_type = "RGBA"
    huemix.inputs[0].default_value = 0.55
    huemix.inputs[6].default_value = (1, 1, 1, 1)
    nt.links.new(hue.outputs[0], huemix.inputs[7])
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_name = "jit"
    attr.attribute_type = "GEOMETRY"
    m1 = nt.nodes.new("ShaderNodeMix")
    m1.data_type = "RGBA"
    m1.blend_type = "MULTIPLY"
    m1.inputs[0].default_value = 1.0
    m1.inputs[6].default_value = b + (1,)
    nt.links.new(ramp.outputs[0], m1.inputs[7])
    m2 = nt.nodes.new("ShaderNodeMix")
    m2.data_type = "RGBA"
    m2.blend_type = "MULTIPLY"
    m2.inputs[0].default_value = 1.0
    nt.links.new(m1.outputs[2], m2.inputs[6])
    nt.links.new(huemix.outputs[2], m2.inputs[7])
    m3 = nt.nodes.new("ShaderNodeMix")
    m3.data_type = "RGBA"
    m3.blend_type = "MULTIPLY"
    m3.inputs[0].default_value = 1.0
    nt.links.new(m2.outputs[2], m3.inputs[6])
    nt.links.new(attr.outputs["Color"], m3.inputs[7])
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(m3.outputs[2], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    _mats[key] = m
    return m


def finish(o, mat, ink=0.02, jitter=0.06, tri=True):
    o.data.materials.append(mat)
    o.data.materials.append(INK)
    me = o.data
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
    if ink > 0:
        s = o.modifiers.new("ink", "SOLIDIFY")
        s.thickness = ink
        s.offset = 1
        s.use_flip_normals = True
        s.material_offset = 1
    o.visible_shadow = False
    return o


def box(c, size, rot=(0, 0, 0), mat=None, ink=0.02, jitter=0.06, subdiv=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=c, rotation=[math.radians(r) for r in rot])
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    if subdiv:
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.subdivide(number_cuts=subdiv)
        bpy.ops.object.mode_set(mode="OBJECT")
        for v in o.data.vertices:
            v.co += Vector((RNG.uniform(-0.015, 0.015), RNG.uniform(-0.015, 0.015), RNG.uniform(-0.015, 0.015)))
    if mat is not None:
        finish(o, mat, ink, jitter)
    return o


def cyl(c, r, depth, verts=8, rot=(0, 0, 0), mat=None, ink=0.015, r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r if r2 is None else r2, depth=depth,
                                    location=c, rotation=[math.radians(x) for x in rot])
    o = bpy.context.object
    if mat is not None:
        finish(o, mat, ink)
    return o


QUADS = {}


def screen(name, c, w, h, facing, glow=(0.3, 0.9, 1.0), strength=1.2):
    """A flat screen quad (later replaced by CRT content in 2D). facing: '-y' | '+x' | '-x'."""
    bpy.ops.mesh.primitive_plane_add(size=1, location=c)
    o = bpy.context.object
    if facing == "-y":
        o.rotation_euler = (math.radians(90), 0, 0)
        o.scale = (w, h, 1)
    elif facing == "+x":
        o.rotation_euler = (math.radians(90), 0, math.radians(-90))
        o.scale = (w, h, 1)
    elif facing == "-x":
        o.rotation_euler = (math.radians(90), 0, math.radians(90))
        o.scale = (w, h, 1)
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    finish(o, toon(glow, emit=strength), ink=0.0, jitter=0.0, tri=False)
    QUADS[name] = o
    return o


def crt_tv(name, c, w, h, depth, facing, body=(0.22, 0.2, 0.24), glow=(0.3, 0.9, 1.0)):
    """A chunky CRT set: a box body + bezel, the screen quad on the front face."""
    if facing == "-y":
        box((c[0], c[1] + depth / 2, c[2]), (w + 0.16, depth, h + 0.16), mat=toon(body))
        box((c[0], c[1] + depth * 0.8, c[2] - 0.02), (w * 0.8, depth * 0.6, h * 0.8), mat=toon(tuple(x * 0.8 for x in body)))
        return screen(name, (c[0], c[1] - 0.005, c[2]), w, h, facing, glow)
    if facing == "+x":
        box((c[0] - depth / 2, c[1], c[2]), (depth, w + 0.16, h + 0.16), mat=toon(body))
        return screen(name, (c[0] + 0.005, c[1], c[2]), w, h, facing, glow)
    box((c[0] + depth / 2, c[1], c[2]), (depth, w + 0.16, h + 0.16), mat=toon(body))
    return screen(name, (c[0] - 0.005, c[1], c[2]), w, h, facing, glow)


# ------------------------------------------------------------------ palette
PINK = (1.0, 0.24, 0.66)
CYAN = (0.36, 0.88, 1.0)
WALL = (0.24, 0.20, 0.28)
WALL2 = (0.30, 0.24, 0.30)
FLOOR = (0.20, 0.14, 0.12)
METAL = (0.32, 0.32, 0.36)
WOOD = (0.36, 0.24, 0.16)
RED = (1.0, 0.1, 0.12)
SCREEN_GLOW = RED if DISPATCH else CYAN

# ------------------------------------------------------------------ shell
X0, X1, Y1, ZC = -5.0, 5.0, 4.0, 3.8
WX0, WX1, WZ0, WZ1 = -2.7, 2.7, 0.95, 3.45
box((0, 0, -0.05), (10.2, 14, 0.1), mat=toon(FLOOR), ink=0.0)
for k in range(12):  # floorboards
    box((X0 + 0.42 + k * 0.85, 0, 0.002), (0.02, 14, 0.004), mat=toon((0.12, 0.08, 0.07)), ink=0.0)
box((0, 0, ZC + 0.05), (10.2, 14, 0.1), mat=toon((0.12, 0.10, 0.14)), ink=0.0)
# back wall with the window hole
box(((X0 + WX0) / 2, Y1, ZC / 2), (WX0 - X0, 0.2, ZC), mat=toon(WALL), subdiv=2)
box(((WX1 + X1) / 2, Y1, ZC / 2), (X1 - WX1, 0.2, ZC), mat=toon(WALL), subdiv=2)
box((0, Y1, WZ0 / 2), (WX1 - WX0, 0.2, WZ0), mat=toon(WALL), subdiv=1)
box((0, Y1, (WZ1 + ZC) / 2), (WX1 - WX0, 0.2, ZC - WZ1), mat=toon(WALL))
box((X0, 0, ZC / 2), (0.2, 14, ZC), mat=toon(WALL2), subdiv=2)
box((X1, 0, ZC / 2), (0.2, 14, ZC), mat=toon(WALL2), subdiv=2)
# window frame + mullions + sill
for x in (WX0, -0.9, 0.9, WX1):
    box((x, Y1 - 0.05, (WZ0 + WZ1) / 2), (0.1, 0.16, WZ1 - WZ0), mat=toon(METAL))
for z in (WZ0, 2.15, WZ1):
    box((0, Y1 - 0.05, z), (WX1 - WX0 + 0.1, 0.16, 0.1), mat=toon(METAL))
box((0, Y1 - 0.3, WZ0 - 0.04), (WX1 - WX0 + 0.4, 0.5, 0.08), mat=toon(WOOD))
# the view: an emissive image plane outside
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, Y1 + 5.0, 2.0))
view = bpy.context.object
view.rotation_euler = (math.radians(90), 0, 0)
view.scale = (13.0, 7.3, 1)
vm = bpy.data.materials.new("view")
vm.use_nodes = True
nt = vm.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
o_ = nt.nodes.new("ShaderNodeOutputMaterial")
em_ = nt.nodes.new("ShaderNodeEmission")
tx = nt.nodes.new("ShaderNodeTexImage")
tx.image = bpy.data.images.load(WIN_IMG)
nt.links.new(tx.outputs["Color"], em_.inputs["Color"])
em_.inputs["Strength"].default_value = 0.85
nt.links.new(em_.outputs[0], o_.inputs["Surface"])
view.data.materials.append(vm)

# ------------------------------------------------------------------ the deck (front centre)
DESK = toon((0.16, 0.14, 0.18))
DY = -3.05
box((0, DY, 0.78), (4.4, 1.2, 0.08), mat=DESK)
for x in (-2.1, 2.1):
    box((x, DY, 0.38), (0.08, 1.1, 0.76), mat=DESK)
crt_tv("deck", (-1.45, DY + 0.3, 1.36), 1.0, 0.74, 0.65, "-y", body=(0.20, 0.18, 0.22), glow=SCREEN_GLOW)
crt_tv("deck_r", (1.55, DY + 0.3, 1.2), 0.62, 0.46, 0.5, "-y", body=(0.26, 0.24, 0.26), glow=SCREEN_GLOW)
box((0.05, DY - 0.2, 0.85), (1.2, 0.36, 0.06), rot=(8, 0, 0), mat=toon((0.12, 0.12, 0.14)))  # keyboard
for i in range(10):
    box((-0.45 + i * 0.1, DY - 0.24, 0.89), (0.075, 0.075, 0.02), mat=toon((0.3, 0.3, 0.34)), ink=0.004)
cyl((0.85, DY - 0.1, 0.88), 0.07, 0.16, 7, mat=toon((0.9, 0.85, 0.75)))  # noodle cup
cyl((-0.6, DY + 0.1, 0.86), 0.06, 0.12, 7, mat=toon((0.9, 0.2, 0.4)))  # can
box((0.4, DY + 0.25, 0.83), (0.5, 0.35, 0.03), rot=(0, 0, 12), mat=toon((0.85, 0.82, 0.74)), ink=0.006)  # paper plan
cyl((0.0, DY + 0.35, 1.05), 0.012, 0.45, 4, rot=(0, -15, 0), mat=toon(METAL), ink=0.0)  # deck lamp
cyl((0.06, DY + 0.35, 1.3), 0.09, 0.12, 8, rot=(0, 140, 0), mat=toon((0.85, 0.2, 0.45)), ink=0.01, r2=0.03)
# ------------------------------------------------------------------ roster wall (left): 3 x 2 stacked TVs on a shelf
box((X0 + 0.45, 0.6, 0.55), (0.8, 3.4, 1.1), mat=toon(WOOD))
k = 0
for row, z in enumerate((1.55, 2.45)):
    for col, y in enumerate((-0.4, 0.6, 1.6)):
        crt_tv("roster_%d" % k, (X0 + 0.75, y, z), 0.72, 0.58, 0.55, "+x", body=[(0.24, 0.22, 0.26), (0.30, 0.27, 0.24), (0.20, 0.20, 0.24)][k % 3],
               glow=(0.5, 0.9, 0.6))
        k += 1
# ------------------------------------------------------------------ home server rack (right, near the window)
RK = (X1 - 0.6, 2.6)
box((RK[0], RK[1], 1.15), (0.9, 1.0, 2.3), mat=toon((0.12, 0.12, 0.15)))
for i in range(9):
    z = 0.35 + i * 0.22
    box((RK[0] - 0.46, RK[1], z), (0.02, 0.85, 0.16), mat=toon((0.2, 0.2, 0.24)), ink=0.004)
    for j in range(5):
        on = RNG.random() < 0.7
        col = RED if DISPATCH else ((0.4, 1.0, 0.5) if (i + j) % 4 else (1.0, 0.75, 0.2))
        box((RK[0] - 0.48, RK[1] - 0.3 + j * 0.06, z + 0.03), (0.01, 0.03, 0.03), mat=toon(col if on else (0.15, 0.15, 0.15), emit=3.0 if on else 0.0), ink=0.0)
screen("rack", (RK[0] - 0.47, RK[1] + 0.12, 2.05), 0.5, 0.3, "-x", glow=SCREEN_GLOW)
for i in range(6):  # cables from the rack into the floor
    cyl((RK[0] - 0.3 + i * 0.05, RK[1] - 0.55, 0.3), 0.025, 0.6, 5, mat=toon((0.08, 0.08, 0.1)), ink=0.0)
# ------------------------------------------------------------------ black market hatch (right wall, nearer the camera)
BM = (X1 - 0.1, 0.2)
box((BM[0] - 0.05, BM[1], 1.55), (0.12, 1.5, 1.2), mat=toon((0.06, 0.04, 0.05)))  # dark opening
box((BM[0] - 0.12, BM[1], 2.0), (0.06, 1.5, 0.3), mat=toon((0.4, 0.38, 0.42)))  # shutter (half open)
for i in range(4):
    box((BM[0] - 0.15, BM[1], 1.88 + i * 0.07), (0.02, 1.48, 0.01), mat=toon((0.25, 0.25, 0.28)), ink=0.0)
box((BM[0] - 0.4, BM[1], 0.95), (0.6, 1.6, 0.08), mat=toon(WOOD))  # counter
for (dy, h_) in ((-0.5, 0.2), (-0.25, 0.14), (0.4, 0.18)):
    box((BM[0] - 0.4, BM[1] + dy, 0.99 + h_ / 2), (0.25, 0.2, h_), mat=toon((0.55, 0.45, 0.3)), ink=0.01)
crt_tv("market", (BM[0] - 0.08, BM[1] + 1.05, 1.75), 0.5, 0.4, 0.4, "-x", body=(0.3, 0.26, 0.22), glow=(1.0, 0.75, 0.3) if not DISPATCH else RED)
light_bm = (1.0, 0.6, 0.25) if not DISPATCH else RED
box((BM[0] - 0.02, BM[1], 1.55), (0.02, 1.3, 0.9), mat=toon(light_bm, emit=0.6), ink=0.0)  # glow inside the hatch
# ------------------------------------------------------------------ heat poster + scrub terminal (back wall, left of the window)
bpy.ops.mesh.primitive_plane_add(size=1, location=(-3.7, Y1 - 0.12, 2.98))
pst = bpy.context.object
pst.rotation_euler = (math.radians(90), 0, math.radians(2))
pst.scale = (0.78, 1.0, 1)
bpy.ops.object.transform_apply(scale=True, rotation=True)
finish(pst, toon((0.9, 0.86, 0.78), emit=0.5), ink=0.0, jitter=0.0, tri=False)
QUADS["poster"] = pst
box((-3.7, Y1 - 0.3, 1.95), (1.4, 0.45, 0.06), mat=toon(WOOD))  # shelf
crt_tv("scrub", (-4.05, Y1 - 0.45, 2.28), 0.48, 0.38, 0.4, "-y", body=(0.26, 0.24, 0.26), glow=SCREEN_GLOW)
box((-3.3, Y1 - 0.3, 2.12), (0.5, 0.3, 0.3), mat=toon((0.35, 0.2, 0.18)))  # pirate radio
cyl((-3.18, Y1 - 0.46, 2.14), 0.08, 0.02, 10, rot=(90, 0, 0), mat=toon((0.8, 0.7, 0.4)), ink=0.005)
box((-3.42, Y1 - 0.46, 2.12), (0.14, 0.02, 0.16), mat=toon((0.1, 0.1, 0.1)), ink=0.004)
cyl((-3.5, Y1 - 0.3, 2.52), 0.008, 0.5, 4, mat=toon(METAL), ink=0.0)  # antenna
# ------------------------------------------------------------------ repair bench (under the window)
box((0.0, Y1 - 0.75, 0.75), (2.6, 0.7, 0.06), mat=toon(WOOD))
for x in (-1.2, 1.2):
    box((x, Y1 - 0.75, 0.37), (0.06, 0.6, 0.74), mat=toon(WOOD))
for i, (x, s) in enumerate(((-0.9, 0.22), (-0.45, 0.16), (0.3, 0.25), (0.85, 0.18))):
    box((x, Y1 - 0.75, 0.78 + s / 2), (s * 1.4, s, s), rot=(0, 0, RNG.uniform(-20, 20)), mat=toon((0.25, 0.4, 0.3) if i % 2 else (0.3, 0.3, 0.38)), ink=0.008)
    box((x, Y1 - 0.75, 0.79 + s), (s * 0.4, s * 0.4, 0.02), mat=toon((0.4, 1.0, 0.5), emit=2.0), ink=0.0)
cyl((0.0, Y1 - 0.85, 1.05), 0.02, 0.5, 5, rot=(0, 60, 20), mat=toon((0.9, 0.7, 0.2)), ink=0.004)  # soldering iron
cyl((-0.2, Y1 - 0.6, 1.2), 0.012, 0.8, 4, rot=(0, -30, 0), mat=toon(METAL), ink=0.0)  # lamp arm
cyl((-0.42, Y1 - 0.6, 1.55), 0.12, 0.18, 8, rot=(0, 120, 0), mat=toon((0.85, 0.2, 0.45)), ink=0.01, r2=0.04)
# ------------------------------------------------------------------ lived-in: mattress, crates, plants, cables, bulb
box((-2.4, 2.6, 0.18), (1.6, 1.0, 0.3), rot=(0, 0, 8), mat=toon((0.35, 0.3, 0.4)), subdiv=1)
box((-2.6, 2.75, 0.4), (0.5, 0.3, 0.14), rot=(0, 0, 5), mat=toon((0.8, 0.75, 0.8)), subdiv=1)
for (x, y, s) in ((2.6, 3.0, 0.5), (2.85, 3.05, 0.35), (-4.0, -2.2, 0.45)):
    box((x, y, s / 2), (s, s, s), rot=(0, 0, RNG.uniform(-15, 15)), mat=toon((0.42, 0.3, 0.2)), ink=0.015)
for (x, y) in ((2.1, 3.6), (-4.4, 3.4)):
    cyl((x, y, 0.2), 0.16, 0.4, 7, mat=toon((0.5, 0.3, 0.25)), r2=0.2)
    for k2 in range(6):
        a = k2 * 1.05
        box((x + 0.12 * math.cos(a), y + 0.12 * math.sin(a), 0.6), (0.06, 0.06, 0.45), rot=(25 * math.cos(a), 25 * math.sin(a), 0), mat=toon((0.25, 0.55, 0.3)), ink=0.006)
for i in range(5):  # ceiling cable bundle
    cyl((-4 + i * 2.0, 0.5 + 0.1 * i, ZC - 0.15), 0.04, 2.2, 5, rot=(0, 90, RNG.uniform(-8, 8)), mat=toon((0.06, 0.06, 0.08)), ink=0.0)
cyl((0.0, -0.5, ZC - 0.5), 0.01, 1.0, 4, mat=toon((0.06, 0.06, 0.08)), ink=0.0)
cyl((0.0, -0.5, ZC - 1.05), 0.09, 0.12, 8, mat=toon((1.0, 0.85, 0.6) if not DISPATCH else RED, emit=4.0), ink=0.0)
box((0, 1.8, 0.01), (3.0, 2.0, 0.02), mat=toon((0.45, 0.12, 0.25)), ink=0.0)  # rug
# pink neon tube along the left ceiling edge (the Cell colour)
box((X0 + 0.15, 0.5, ZC - 0.3), (0.05, 5.0, 0.05), mat=toon(PINK if not DISPATCH else RED, emit=3.0), ink=0.0)

# ------------------------------------------------------------------ lights + camera
def point(loc, col, energy, radius=0.5):
    L = bpy.data.lights.new("p", "POINT")
    L.color = col
    L.energy = energy
    L.shadow_soft_size = radius
    o = bpy.data.objects.new("p", L)
    o.location = loc
    scene.collection.objects.link(o)


if DISPATCH:
    point((0, 2.5, 2.4), (1.0, 0.15, 0.15), 900)
    point((0, -1.0, 2.0), (1.0, 0.2, 0.2), 500)
    point((-4.0, 0.6, 2.0), (1.0, 0.1, 0.1), 250)
    point((4.0, 2.0, 2.0), (1.0, 0.1, 0.1), 250)
else:
    point((0, 2.8, 2.4), (0.95, 0.45, 0.85), 700)   # window spill (pink/violet city)
    point((0, -1.2, 2.6), (1.0, 0.85, 0.65), 450)   # the bulb
    point((-3.8, 0.6, 2.0), (0.4, 1.0, 0.6), 220)   # roster TVs
    point((3.9, -0.6, 1.6), (1.0, 0.6, 0.25), 220)  # black market hatch
    point((3.8, 2.4, 2.0), (0.35, 0.85, 1.0), 200)  # server rack
    point((0, -1.6, 1.6), (0.35, 0.85, 1.0), 200)   # deck glow
world = bpy.data.worlds.new("w")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = (0.01, 0.01, 0.015, 1)
bg.inputs["Strength"].default_value = 1.0
scene.world = world
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 19
cam = bpy.data.objects.new("cam", cam_d)
scene.collection.objects.link(cam)
cam.location = (0.0, -5.9, 2.05)
cam.rotation_euler = (Vector((0, 2.0, 1.6)) - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam
r = scene.render
try:
    r.engine = "BLENDER_EEVEE"
except TypeError:
    r.engine = "BLENDER_EEVEE_NEXT"
r.resolution_x, r.resolution_y = RES
r.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "Standard"
r.filepath = os.path.join(OUT, "room_%s.png" % VAR)
bpy.context.view_layer.update()

# ------------------------------------------------------------------ quads -> pixels
q = {}
for name, o in QUADS.items():
    pts = []
    for v in o.data.vertices:
        w = o.matrix_world @ v.co
        p = world_to_camera_view(scene, cam, w)
        pts.append((p.x * RES[0], (1 - p.y) * RES[1], p.z))
    # order: TL, TR, BR, BL in image space
    cx = sum(p[0] for p in pts) / 4
    cy = sum(p[1] for p in pts) / 4
    tl = min(pts, key=lambda p: (p[0] - cx) + (p[1] - cy))
    br = max(pts, key=lambda p: (p[0] - cx) + (p[1] - cy))
    rest = [p for p in pts if p is not tl and p is not br]
    tr = max(rest, key=lambda p: (p[0] - cx) - (p[1] - cy))
    bl = min(rest, key=lambda p: (p[0] - cx) - (p[1] - cy))
    q[name] = [list(tl[:2]), list(tr[:2]), list(br[:2]), list(bl[:2])]
# the window opening too
wq = []
for (x, z) in ((WX0, WZ1), (WX1, WZ1), (WX1, WZ0), (WX0, WZ0)):
    p = world_to_camera_view(scene, cam, Vector((x, Y1 - 0.1, z)))
    wq.append([p.x * RES[0], (1 - p.y) * RES[1]])
q["window"] = wq
json.dump(q, open(os.path.join(OUT, "quads_%s.json" % VAR), "w"), indent=1)
bpy.ops.render.render(write_still=True)
print("RENDERED", VAR)
