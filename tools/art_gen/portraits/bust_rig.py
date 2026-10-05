"""Parametric low-poly cel busts (Cv2 facets + E toon bands + inverted-hull ink).
Ported from art-pass 9a62cec (tag art-concepts-r43, docs/concepts/round39_portraits/scripts/
bust_rig.py, the round 39 v2 gear: patch_r39 / r39b / r39c applied). ART-9 4B changes: the
job file may be {"res": [w, h], "jobs": [...]} (game-sized renders); nothing else.
One Blender run renders a whole job list (JSON): each job = class gear + a variant seed + a mouth/eye state.

blender -b --factory-startup -P bust_rig.py -- <jobs.json> <out_dir>
job: {"name": str, "cls": breaker|wrecker|ghost|phantom|rigger|overclocker|botnet|hivemind|fixer|merc,
      "seed": int, "mouth": closed|open|grimace, "eyes": open|shut|squint}
"""
import json
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
_SPEC = json.load(open(argv[0]))
JOBS = _SPEC["jobs"] if isinstance(_SPEC, dict) else _SPEC
RES = tuple(_SPEC.get("res", (600, 666))) if isinstance(_SPEC, dict) else (600, 666)
OUT = argv[1]

CLASS_COL = {
    "breaker": (1.0, 0.24, 0.66), "wrecker": (1.0, 0.43, 0.20), "ghost": (0.36, 0.88, 1.0),
    "phantom": (0.86, 0.76, 1.0), "rigger": (0.48, 0.88, 0.48), "overclocker": (1.0, 0.69, 0.25),
    "botnet": (0.38, 0.45, 1.0), "hivemind": (0.78, 0.35, 1.0), "fixer": (0.36, 0.88, 1.0), "merc": (1.0, 0.75, 0.3),
}
SKINS = [(0.62, 0.36, 0.26), (0.30, 0.17, 0.11), (0.80, 0.55, 0.42), (0.45, 0.27, 0.17), (0.70, 0.46, 0.33)]
HAIRS = [(0.06, 0.05, 0.07), (0.30, 0.16, 0.08), (0.75, 0.70, 0.62), (0.55, 0.12, 0.40), (0.12, 0.30, 0.55)]


def lin(c):
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


# ------------------------------------------------------------------ materials
INK = None
_mats = {}


def ink_mat():
    global INK
    INK = bpy.data.materials.new("ink")
    INK.use_nodes = True
    nt = INK.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = (0.012, 0.01, 0.02, 1)
    nt.links.new(e.outputs[0], o.inputs["Surface"])
    INK.use_backface_culling = True


def toon(name, base, rim, rim_k=0.55, emit=0.0):
    key = (name, base, rim, rim_k, emit)
    if key in _mats:
        return _mats[key]
    base = lin(base)
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
        _mats[key] = m
        return m
    dif = nt.nodes.new("ShaderNodeBsdfDiffuse")
    s2r = nt.nodes.new("ShaderNodeShaderToRGB")
    nt.links.new(dif.outputs[0], s2r.inputs[0])
    bw = nt.nodes.new("ShaderNodeRGBToBW")
    nt.links.new(s2r.outputs[0], bw.inputs[0])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    el = ramp.color_ramp.elements
    el[0].position = 0.0
    el[0].color = (0.42, 0.42, 0.42, 1)
    el[1].position = 0.32
    el[1].color = (1, 1, 1, 1)
    e2 = el.new(0.06)
    e2.color = (0.72, 0.72, 0.72, 1)
    nt.links.new(bw.outputs[0], ramp.inputs[0])
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
    lw = nt.nodes.new("ShaderNodeLayerWeight")
    lw.inputs["Blend"].default_value = 0.35
    rr = nt.nodes.new("ShaderNodeValToRGB")
    rr.color_ramp.interpolation = "CONSTANT"
    rr.color_ramp.elements[0].color = (0, 0, 0, 1)
    rr.color_ramp.elements[1].position = 0.62
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
    add.inputs[7].default_value = lin(rim) + (1,)
    em = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(add.outputs[2], em.inputs["Color"])
    nt.links.new(em.outputs[0], out.inputs["Surface"])
    _mats[key] = m
    return m


# ------------------------------------------------------------------ geometry helpers
RNG = random.Random(1)


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
    if ink > 0:
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


def sphere(seg, ring, r, loc, scale):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=ring, radius=r, location=loc)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    return o


def cyl(verts, r1, r2, depth, loc, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return o


def box(loc, size, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(scale=True, rotation=True)
    return o


def torus(R, r, loc, rot=(0, 0, 0), maj=12, mnr=4):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=maj, minor_segments=mnr, location=loc, rotation=rot)
    return bpy.context.object


def boolean(obj, cutter, op="DIFFERENCE"):
    m = obj.modifiers.new("b", "BOOLEAN")
    m.operation = op
    m.object = cutter
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(cutter, do_unlink=True)


def tri_prism(cx, cy, cz, r, depth):
    """A triangular prism facing the camera (-y), one vertex pointing DOWN."""
    pts = [(cx + r * math.cos(math.radians(a)), cz + r * math.sin(math.radians(a))) for a in (90 + 120 * 0 + 0, 210, 330)]
    pts = [(cx, cz - r), (cx + r * 0.95, cz + r * 0.55), (cx - r * 0.95, cz + r * 0.55)]
    verts = [(x, cy - depth / 2, z) for x, z in pts] + [(x, cy + depth / 2, z) for x, z in pts]
    faces = [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)]
    me = bpy.data.meshes.new("tri")
    me.from_pydata(verts, [], faces)
    me.update()
    o = bpy.data.objects.new("tri", me)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    return o


# ------------------------------------------------------------------ build
def build(job):
    global RNG
    cls = job["cls"]
    seed = job["seed"]
    RNG = random.Random(seed * 101 + len(cls))
    r = random.Random(seed * 7 + sum(map(ord, cls)))
    acc = CLASS_COL[cls]
    skin = SKINS[r.randrange(len(SKINS))] if cls not in ("fixer",) else (0.30, 0.17, 0.11)
    hairc = HAIRS[r.randrange(len(HAIRS))]
    jaw = r.uniform(0.28, 0.46)
    wid = r.uniform(0.76, 0.88)
    hair_style = r.choice(["buzz", "crop", "mohawk", "bald", "long"])
    beard = r.random() < 0.3 and cls not in ("breaker", "ghost", "phantom")
    mouth = job.get("mouth", "closed")
    eyes = job.get("eyes", "open")
    RIM = acc

    head = sphere(9, 7, 1.0, (0, 0, 0), (wid, 0.92, 1.08))
    for v in head.data.vertices:
        if v.co.z < -0.2:
            k = (-0.2 - v.co.z) / 0.9
            v.co.x *= 1 - jaw * k
            v.co.y = v.co.y * (1 - 0.22 * k) - 0.06 * k
    jitter_verts(head, 0.035)
    finish(head, toon("skin", skin, RIM, 0.45))
    nose = cyl(4, 0.15, 0.0, 0.34, (0, -0.9, -0.1), rot=(math.radians(100), 0, 0), scale=(0.8, 1, 1))
    finish(nose, toon("skin", skin, RIM, 0.45))
    for sx in (-1, 1):
        ear = sphere(5, 4, 0.2, (sx * (wid - 0.02), 0.05, -0.02), (0.4, 1.0, 1.3))
        finish(ear, toon("skin", skin, RIM, 0.45))
    # mouth
    dark = (0.18, 0.06, 0.08)
    # ART-9 4B: every frame of one rookie draws the same random numbers (the mouth's tilt is
    # drawn whatever the mouth; the mouth's face jitter never moves the shared stream past
    # what the closed mouth's 12 triangles take), so idle / blink / talk / hurt are one face
    # (the round 39 sheet only rendered idle). Idle is unchanged from round 39.
    mouth_tilt = r.uniform(-6, 6)
    rng_state = RNG.getstate()
    if mouth == "open":
        mo = sphere(6, 4, 0.16, (0, -0.8, -0.52), (1.25, 0.4, 0.75))
        finish(mo, toon("mouth", dark, RIM, 0.0), ink=0.006, tri=False)
    elif mouth == "grimace":
        mo = box((0, -0.8, -0.5), (0.38, 0.05, 0.08), rot=(0, 0, math.radians(-8)))
        finish(mo, toon("mouth", (0.85, 0.82, 0.78), RIM, 0.0), ink=0.012)
    else:
        mo = box((0, -0.8, -0.5), (0.3, 0.05, 0.035), rot=(0, 0, math.radians(mouth_tilt)))
        finish(mo, toon("mouth", (0.25, 0.1, 0.12), RIM, 0.0), ink=0.004)
    RNG.setstate(rng_state)
    for _ in range(12):
        RNG.random()
    covered_eyes = cls in ("breaker", "overclocker", "fixer", "phantom") or (cls == "botnet" and seed % 2 == 0) or (cls == "rigger" and seed % 3 == 0)
    if not covered_eyes:
        for sx in (-1, 1):
            if eyes == "open":
                e = box((sx * 0.3, -0.84, 0.12), (0.17, 0.05, 0.08))
            elif eyes == "squint":
                e = box((sx * 0.3, -0.84, 0.12), (0.18, 0.05, 0.03), rot=(0, math.radians(sx * 10), 0))
            else:
                e = box((sx * 0.3, -0.84, 0.1), (0.18, 0.05, 0.02))
            finish(e, toon("eye", (0.05, 0.04, 0.06), RIM, 0.0), ink=0.004)
            brow_tilt = r.uniform(-8, 6)  # ART-9 4B: drawn in every frame (see the mouth)
            brow = box((sx * 0.3, -0.83, 0.28 + (0.04 if eyes != "squint" else -0.02)), (0.22, 0.06, 0.05),
                       rot=(0, math.radians(sx * (-14 if eyes == "squint" else brow_tilt)), 0))
            finish(brow, toon("hair", hairc, RIM, 0.3), ink=0.004)
    if beard:
        bd = sphere(7, 5, 0.6, (0, -0.35, -0.62), (1.0, 0.8, 0.65))
        boolean(bd, box((0, -0.75, -0.42), (0.5, 0.6, 0.18)))
        boolean(bd, box((0, 0.6, -0.4), (2, 1.0, 2)))
        jitter_verts(bd, 0.03)
        finish(bd, toon("beard", hairc if hairc in HAIRS[:3] else HAIRS[seed % 2], RIM, 0.3))
    neck = cyl(7, 0.36, 0.42, 1.0, (0, 0.1, -1.15))
    finish(neck, toon("neck", tuple(c * 0.8 for c in skin), RIM, 0.35))
    torso = sphere(10, 6, 1.0, (0, 0.25, -2.55), (2.15, 1.05, 1.15))
    for v in torso.data.vertices:
        if v.co.z > -2.2:
            v.co.z = -2.2 + (v.co.z + 2.2) * 0.55
    jitter_verts(torso, 0.05)
    jacket = {"breaker": (0.09, 0.06, 0.12), "wrecker": (0.16, 0.10, 0.07), "ghost": (0.07, 0.09, 0.13),
              "phantom": (0.16, 0.14, 0.20), "rigger": (0.12, 0.16, 0.10), "overclocker": (0.18, 0.12, 0.06),
              "botnet": (0.08, 0.09, 0.18), "hivemind": (0.13, 0.07, 0.18), "fixer": (0.20, 0.11, 0.05), "merc": (0.12, 0.12, 0.10)}[cls]
    jacket = tuple(min(1, c * r.uniform(0.85, 1.3)) for c in jacket)
    finish(torso, toon("jacket", jacket, RIM, 0.6))
    collar = cyl(8, 0.72, 0.6, 0.55, (0, 0.18, -1.55))
    finish(collar, toon("collar", tuple(min(1, c * 1.3) for c in jacket), RIM, 0.6))
    emit = lambda c, k=1.4: toon("glow", c, RIM, 0, emit=k)

    # hair (under headgear for most)
    def hair():
        if hair_style == "bald":
            return
        if hair_style == "mohawk":
            mh = box((0, 0.05, 0.95), (0.18, 1.3, 0.35))
            boolean(mh, sphere(8, 6, 1.0, (0, 0.05, 0.25), (0.6, 1.2, 0.6)))
            finish(mh, toon("hair", hairc, RIM, 0.6))
            return
        h = sphere(9, 6, 1.0, (0, 0.06, 0.2 if hair_style != "buzz" else 0.12), (wid + 0.05, 0.98, 0.95))
        boolean(h, box((0, -0.2, -0.75 if hair_style != "long" else -1.25), (3, 3, 1.6)))
        boolean(h, box((0, -1.12, 0.1), (3, 0.9, 3)))
        jitter_verts(h, 0.025)
        finish(h, toon("hair", hairc, RIM, 0.6))

    if cls == "breaker":
        hood = sphere(10, 8, 1.0, (0, 0.18, 0.05), (wid + 0.24, 1.12, 1.28))
        for v in hood.data.vertices:
            if v.co.z < -0.4:
                k = (-0.4 - v.co.z)
                v.co.x *= 1 + 0.55 * k
                v.co.y += 0.25 * k
        boolean(hood, box((0, -1.2, -0.6), (1.75, 1.3, 2.8), rot=(math.radians(-14), 0, 0)))
        boolean(hood, box((0, -0.55, -1.15), (3.0, 1.1, 0.9)))  # chin cut
        jitter_verts(hood, 0.03)
        finish(hood, toon("hood", (0.16, 0.07, 0.19) if seed % 3 else (0.22, 0.20, 0.24), RIM, 0.7))
        vz = 0.16 if seed % 3 != 1 else 0.14
        visor = cyl(10, 0.9, 0.9, 0.22 if seed % 3 != 2 else 0.12, (0, 0.0, vz), scale=(wid + 0.12, 1.08, 1))
        boolean(visor, box((0, 0.55, vz), (2.4, 1.2, 1)))
        finish(visor, emit(acc, 1.6), ink=0.012, tri=False)
        st = box((0.9, -0.62, -2.45), (0.22, 0.12, 1.1), rot=(0, math.radians(-22), math.radians(14)))
        finish(st, emit(acc, 1.3), ink=0.01)
    elif cls == "wrecker":
        hair()
        resp = sphere(7, 5, 0.42, (0, -0.72, -0.5), (1.15, 0.7, 0.85))
        finish(resp, toon("resp", (0.18, 0.17, 0.2), RIM, 0.5))
        for sx in (-1, 1):
            f = cyl(8, 0.16, 0.16, 0.14, (sx * 0.38, -0.92, -0.58), rot=(math.radians(90), 0, 0))
            finish(f, emit(acc, 1.3), ink=0.01)
        for sx in (-1, 1):
            pad = sphere(6, 4, 0.7, (sx * 1.65, 0.2, -2.05), (0.75, 0.9, 0.45))
            finish(pad, toon("pad", tuple(c * 0.75 for c in acc), RIM, 0.5))
        if seed % 2:
            gl = box((0, -0.86, 0.16), (1.5, 0.12, 0.16))
            finish(gl, toon("glass", (0.15, 0.13, 0.16), RIM, 0.6))
    elif cls == "ghost":
        # ninja wrap: the whole head and face wrapped in cloth, one open band for the (real) eyes
        cloth = [(0.07, 0.08, 0.11), (0.16, 0.17, 0.20), (0.05, 0.05, 0.06)][seed % 3]
        wrap = sphere(10, 8, 1.0, (0, 0.02, 0.0), (wid + 0.07, 1.0, 1.12))
        for v in wrap.data.vertices:
            if v.co.z < -0.2:
                k = (-0.2 - v.co.z) / 0.9
                v.co.x *= 1 - (jaw - 0.06) * k
                v.co.y = v.co.y * (1 - 0.18 * k) - 0.05 * k
        boolean(wrap, box((0, -0.95, 0.14), (1.4, 0.6, 0.28)))
        jitter_verts(wrap, 0.02)
        finish(wrap, toon("wrap", cloth, RIM, 0.7))
        for z_, t_ in ((0.5, -10),):
            fold = torus(wid + 0.05, 0.045, (0, 0.02, z_), rot=(math.radians(t_), 0, 0), maj=14)
            fold.scale = (1, 1.12, 1)
            finish(fold, toon("wrapf", tuple(c * 1.6 for c in cloth), RIM, 0.6), ink=0.006)
        if seed % 3 != 2:
            hb = torus(wid + 0.06, 0.055, (0, 0.02, 0.36), rot=(math.radians(-6), 0, 0), maj=14)
            hb.scale = (1, 1.03, 1)
            finish(hb, toon("hb", acc, RIM, 0.3), ink=0.008)
        for k_, sx in enumerate((-1, 1)):
            tl = box((sx * 0.18, 1.25, 0.15 - 0.25 * k_), (0.16, 0.9 if seed % 2 else 0.6, 0.06),
                     rot=(math.radians(20 + 10 * k_), 0, math.radians(sx * 12)))
            finish(tl, toon("tail", acc if seed % 3 != 2 else tuple(c * 1.6 for c in cloth), RIM, 0.3), ink=0.008)
        nw = cyl(8, 0.46, 0.5, 0.7, (0, 0.1, -1.05))
        finish(nw, toon("wrap", cloth, RIM, 0.6))
    elif cls == "phantom":
        hair()
        # full mask: a smooth shell over the face, two round robotic eyes
        mk = sphere(10, 8, 1.0, (0, -0.04, -0.02), (wid + 0.05, 0.98, 1.1))
        for v in mk.data.vertices:
            if v.co.z < -0.2:
                k = (-0.2 - v.co.z) / 0.9
                v.co.x *= 1 - jaw * k
                v.co.y = v.co.y * (1 - 0.2 * k) - 0.06 * k
        boolean(mk, box((0, 0.62, 0), (3, 1.2, 3)))
        boolean(mk, box((0, 0, 1.0), (3, 3, 0.7)))
        finish(mk, toon("phmask", (0.93, 0.90, 0.98) if seed % 3 != 2 else (0.80, 0.74, 0.90), RIM, 0.5), ink=0.025)
        er = 0.19 if seed % 3 != 1 else 0.23
        for sx in (-1, 1):
            rim_ = tri_prism(sx * 0.31, -0.93, 0.12, er + 0.07, 0.12)
            finish(rim_, toon("ring", (0.25, 0.22, 0.32), RIM, 0.4), ink=0.01, tri=False)
            lens = tri_prism(sx * 0.31, -1.0, 0.12, er, 0.06)
            finish(lens, emit(acc, 2.0), ink=0.0, tri=False)
        for k_ in range(3 if seed % 2 else 2):
            vent = box((0, -0.9, -0.5 - k_ * 0.12), (0.28, 0.05, 0.035))
            finish(vent, toon("vent", (0.35, 0.3, 0.42), RIM, 0.0), ink=0.0)
    elif cls == "rigger":
        hair()
        gz = 0.62 if seed % 3 else 0.12
        # a level band hugging the head at the goggle height; the cups are centred ON the band
        rb = wid * math.sqrt(max(0.05, 1 - (gz / 1.1) ** 2)) + 0.07
        band = torus(rb, 0.075, (0, 0.0, gz), maj=18)
        band.scale = (1, 1.0, 1)
        finish(band, toon("band", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.01)
        for sx in (-1, 1):
            gy = -math.sqrt(max(0.01, rb ** 2 - 0.3 ** 2)) - 0.05
            g = cyl(8, 0.22, 0.22, 0.22, (sx * 0.3, gy, gz), rot=(math.radians(90), 0, 0))
            finish(g, toon("goggle", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.012)
            l = cyl(8, 0.16, 0.16, 0.05, (sx * 0.3, gy - 0.12, gz), rot=(math.radians(90), 0, 0))
            finish(l, emit(acc, 1.6), ink=0.006, tri=False)
        bridge = box((0, -rb - 0.06, gz), (0.24, 0.08, 0.075))
        finish(bridge, toon("band", (0.12, 0.12, 0.14), RIM, 0.5), ink=0.008)
        cup = cyl(8, 0.3, 0.3, 0.22, (-wid - 0.08, 0.05, 0.0), rot=(0, math.radians(90), 0))
        finish(cup, toon("cup", (0.15, 0.15, 0.18), RIM, 0.5))
        mic = box((-0.62, -0.6, -0.42), (0.06, 0.8, 0.06), rot=(0, 0, math.radians(30)))
        finish(mic, toon("mic", (0.12, 0.12, 0.14), RIM, 0.3), ink=0.008)
        tip = sphere(5, 4, 0.08, (-0.38, -0.95, -0.46), (1, 1, 1))
        finish(tip, emit(acc, 2.0), ink=0.005, tri=False)
    elif cls == "overclocker":
        hair_style = "mohawk" if seed % 2 == 0 else hair_style
        hair()
        g = box((0, -0.8, 0.14), (1.45, 0.22, 0.32))
        finish(g, toon("gog", (0.12, 0.10, 0.10), RIM, 0.5), ink=0.015)
        for sx in (-1, 1):
            l = box((sx * 0.3, -0.92, 0.14), (0.38, 0.05, 0.2))
            finish(l, emit(acc, 1.8), ink=0.006)
        for k in range(4):
            fin = box((wid + 0.12, 0.25 - k * 0.16, 0.25 + 0.1 * (k % 2)), (0.08, 0.06, 0.55))
            finish(fin, toon("fin", (0.55, 0.50, 0.46), RIM, 0.4), ink=0.01)
    elif cls == "botnet":
        hair()
        if seed % 2 == 0:
            mono = cyl(8, 0.24, 0.24, 0.12, (0.3, -0.84, 0.13), rot=(math.radians(90), 0, 0))
            finish(mono, emit(acc, 1.8), ink=0.012, tri=False)
            mono2 = cyl(8, 0.18, 0.18, 0.06, (-0.3, -0.84, 0.13), rot=(math.radians(90), 0, 0))
            finish(mono2, toon("lens", (0.1, 0.1, 0.14), RIM, 0.4), ink=0.01, tri=False)
        ant = box((wid - 0.1, 0.1, 0.9), (0.05, 0.05, 0.7), rot=(0, math.radians(18), 0))
        finish(ant, toon("ant", (0.15, 0.15, 0.18), RIM, 0.4), ink=0.006)
        for k, (dx, dz) in enumerate(((1.35, 0.35), (-1.25, 0.55), (1.15, -0.55))[: 2 + seed % 2]):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=0.24, location=(dx, -0.3, dz))
            dr = bpy.context.object
            finish(dr, toon("drone", (0.2, 0.22, 0.32), RIM, 0.6), ink=0.012)
            dl = sphere(5, 4, 0.08, (dx, -0.55, dz), (1, 1, 1))
            finish(dl, emit(acc, 2.5), ink=0.0, tri=False)
    elif cls == "hivemind":
        hair()
        circ = torus(wid + 0.1, 0.06, (0, 0.05, 0.38), rot=(math.radians(15), 0, 0), maj=6)
        finish(circ, emit(acc, 1.2), ink=0.012, tri=False)
        for k in range(6):
            a = math.radians(60 * k + 30)
            x, y = (wid + 0.1) * math.cos(a), (wid + 0.1) * math.sin(a) * 0.97
            z = 0.38 + y * math.tan(math.radians(15)) * -1
            nd = sphere(6, 4, 0.11, (x, 0.05 + y, z), (1, 1, 1))
            finish(nd, toon("node", (0.25, 0.15, 0.3), RIM, 0.6), ink=0.008, tri=False)
        # one eye replaced by a square lens (the Overclocker lens shape), wired up to the circlet
        hous = box((0.3, -0.86, 0.13), (0.42, 0.18, 0.34))
        finish(hous, toon("hous", (0.14, 0.10, 0.18), RIM, 0.5), ink=0.014)
        sq = box((0.3, -0.96, 0.13), (0.3 if seed % 3 != 1 else 0.34, 0.05, 0.24))
        finish(sq, emit(acc, 2.0), ink=0.006)

        def bar(p0, p1, t=0.05):
            p0, p1 = Vector(p0), Vector(p1)
            dv = p1 - p0
            bpy.ops.mesh.primitive_cube_add(size=1, location=(p0 + p1) / 2)
            o = bpy.context.object
            o.scale = (t, t, dv.length)
            o.rotation_euler = dv.to_track_quat("Z", "Y").to_euler()
            bpy.ops.object.transform_apply(scale=True, rotation=True)
            return o
        a = math.radians(-60)
        cx_, cy_ = (wid + 0.1) * math.cos(a), 0.05 + (wid + 0.1) * math.sin(a) * 0.97
        cz_ = 0.38 - (cy_ - 0.05) * math.tan(math.radians(15))
        arm = bar((0.5, -0.86, 0.22), (cx_, cy_, cz_), 0.07)
        finish(arm, toon("arm", (0.20, 0.16, 0.24), RIM, 0.5), ink=0.008)
        cab = bar((0.42, -0.84, 0.3), (cx_ - 0.05, cy_ + 0.05, cz_ + 0.02), 0.035)
        finish(cab, emit(acc, 1.4), ink=0.0)
    elif cls == "fixer":
        hair_style = "buzz"
        hair()
        for sx in (-1, 1):
            lens = cyl(6, 0.2, 0.2, 0.06, (sx * 0.3, -0.92, 0.12), rot=(math.radians(90), 0, 0))
            finish(lens, emit((0.2, 0.75, 1.0), 1.4), ink=0.012, tri=False)
        br = box((0, -0.94, 0.14), (0.24, 0.05, 0.05))
        finish(br, toon("frame", (0.1, 0.1, 0.12), RIM, 0.3), ink=0.008)
        for sx in (-1, 1):
            lap = box((sx * 0.42, -0.86, -2.15), (0.34, 0.1, 1.1), rot=(math.radians(14), math.radians(sx * 8), math.radians(-sx * 24)))
            finish(lap, toon("lapel", (0.12, 0.06, 0.03), RIM, 0.5))
        sh = box((0, -0.78, -2.0), (0.5, 0.1, 1.0), rot=(math.radians(14), 0, 0))
        finish(sh, toon("shirt", (0.55, 0.52, 0.5), RIM, 0.3))
    elif cls == "merc":
        hair_style = "crop"
        hair()
        scar = box((0.36, -0.84, 0.0), (0.04, 0.03, 0.5), rot=(0, math.radians(20), 0))
        finish(scar, toon("scar", (0.75, 0.4, 0.4), RIM, 0.0), ink=0.0)
        cap = sphere(9, 6, 1.0, (0, 0.04, 0.32), (wid + 0.08, 1.0, 0.75))
        boolean(cap, box((0, 0, -0.55), (3, 3, 1.4)))
        finish(cap, toon("cap", (0.25, 0.22, 0.12), RIM, 0.6))
        brim = box((0, -0.86, 0.42), (1.2, 0.6, 0.06), rot=(math.radians(-12), 0, 0))
        finish(brim, toon("cap", (0.25, 0.22, 0.12), RIM, 0.6), ink=0.015)
        for sx in (-1, 1):
            strap = box((sx * 0.8, -0.75, -2.2), (0.16, 0.1, 1.2), rot=(math.radians(10), 0, math.radians(sx * 10)))
            finish(strap, toon("strap", (0.08, 0.07, 0.06), RIM, 0.3), ink=0.01)


def setup_scene():
    scene = bpy.context.scene
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 62
    cam = bpy.data.objects.new("cam", cam_d)
    scene.collection.objects.link(cam)
    cam.location = (2.6, -7.6, 0.25)
    cam.rotation_euler = (Vector((0, 0, -0.75)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    key = bpy.data.lights.new("key", "SUN")
    key.energy = 2.4
    ko = bpy.data.objects.new("key", key)
    ko.rotation_euler = (Vector((0, 0, -0.3)) - Vector((-4.5, -6.0, 4.5))).to_track_quat("-Z", "Y").to_euler()
    scene.collection.objects.link(ko)
    r = scene.render
    try:
        r.engine = "BLENDER_EEVEE"
    except TypeError:
        r.engine = "BLENDER_EEVEE_NEXT"
    r.resolution_x = RES[0]
    r.resolution_y = RES[1]
    r.film_transparent = True
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "Standard"


bpy.ops.wm.read_factory_settings(use_empty=True)
ink_mat()
setup_scene()
for job in JOBS:
    for o in list(bpy.data.objects):
        if o.type == "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    for me in list(bpy.data.meshes):
        if me.users == 0:
            bpy.data.meshes.remove(me)
    build(job)
    bpy.context.scene.render.filepath = os.path.join(OUT, job["name"] + ".png")
    bpy.ops.render.render(write_still=True)
    print("RENDERED", job["name"], flush=True)
