"""Raid target frames: the one Blender board, three moments (plan, reveal, impact).

    blender -b -P raid_scene.py -- <frame> <out_dir> [--res WxH] [--samples N]

frame = plan | reveal | impact.  Writes <out_dir>/<frame>_raw.png and <frame>_nodes.json (the
screen positions of every node, beam end and marker, for the Pillow composite).  Everything is
seeded; the board, the camera and the lights are identical across the three frames, only the state
(beams, damage, levers) changes.

Board (cols c0..c3, left to right; rows R1 far .. R3 near; the beams enter from the right):
  R1: c0 asset 4 | c1 asset 8 DARK | c2 decoy | c3 asset 8 (beam 1 hits it)
  R2: c0 . | c1 . | c2 asset 4 | c3 HOME
  R3: c0 . | c1 . | c2 asset 8 | c3 asset 8 GHOST
Beam 1 = R1 from the right. Sealed candidates: R2 (square), R3 (circle), R1 from the left (triangle).
The hunter turns down column c3 at the node beam 1 touched.
"""
import json
import math
import os
import random
import sys

import bpy
import bmesh
from mathutils import Matrix, Vector

argv = sys.argv[sys.argv.index("--") + 1:]
FRAME = argv[0]
OUT = argv[1]
RES = (1920, 1080)
SAMPLES = 48
if "--res" in argv:
    w, h = argv[argv.index("--res") + 1].split("x")
    RES = (int(w), int(h))
if "--samples" in argv:
    SAMPLES = int(argv[argv.index("--samples") + 1])

random.seed(4107)

# ---- palette (linear-ish sRGB triples, converted by col()) ----
def hexc(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))

def lin(c):
    return tuple((v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4) for v in c)

COBALT = lin(hexc("3D6BFF"))
COBALT_HOT = lin(hexc("9FC0FF"))
AMBER = lin(hexc("FFB020"))
GOLD = lin(hexc("FFD24D"))
EMBER = lin(hexc("FF6A1A"))
RED = lin(hexc("FF2A3C"))
CYAN = lin(hexc("5CE1FF"))
NAVY = lin(hexc("070B1E"))
STEEL = lin(hexc("1A1E2E"))
WARMMETAL = lin(hexc("2B2018"))

# ---- grid ----
COLS = [0.0, 2.9, 5.8, 8.7]
ROWS = {1: 7.0, 2: 3.5, 3: 0.0}   # y of R1, R2, R3
def P(c, r, z=0.0):
    return Vector((COLS[c], ROWS[r], z))

ENTRY_X = 12.4   # the right pylons
LEFT_X = -3.8

MATS = {}

def mat_emit(name, color, strength, alpha=1.0):
    k = (name, color, strength, alpha)
    if k in MATS:
        return MATS[k]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = (*color, 1)
    em.inputs["Strength"].default_value = strength
    if alpha < 0.999:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        mx.inputs["Fac"].default_value = alpha
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs["Surface"])
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
        m.use_backface_culling = False
    else:
        nt.links.new(em.outputs[0], out.inputs["Surface"])
    MATS[k] = m
    return m

def mat_solid(name, color, rough=0.5, metal=0.0, emit=None, emit_strength=0.0):
    k = (name, color, rough, metal, emit, emit_strength)
    if k in MATS:
        return MATS[k]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit is not None:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    MATS[k] = m
    return m

# ---- mesh helpers ----
def finish(name, bm, mat, wire=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    if wire:
        md = ob.modifiers.new("wire", "WIREFRAME")
        md.thickness = wire
        md.use_replace = True
    return ob

def box(name, loc, size, mat, rot=0.0, wire=None, bevel=0.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if rot:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"))
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    if bevel:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=1, affect="EDGES")
    return finish(name, bm, mat, wire)

def cyl(name, loc, r, h, verts, mat, rot=0.0, r2=None, wire=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r,
                          radius2=(r if r2 is None else r2), depth=h)
    if rot:
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rot, 3, "Z"))
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    return finish(name, bm, mat, wire)

def octa(name, loc, r, sq, mat):
    """A true octahedron (a diamond), r wide, r*sq tall, flat-shaded."""
    bm = bmesh.new()
    t, b = bm.verts.new((0, 0, r * sq)), bm.verts.new((0, 0, -r * sq))
    ring_v = [bm.verts.new((r, 0, 0)), bm.verts.new((0, r, 0)), bm.verts.new((-r, 0, 0)), bm.verts.new((0, -r, 0))]
    for i in range(4):
        j = (i + 1) % 4
        bm.faces.new((t, ring_v[i], ring_v[j]))
        bm.faces.new((b, ring_v[j], ring_v[i]))
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.radians(20), 3, "Z"))
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    return finish(name, bm, mat)

def sphere(name, loc, r, mat, sub=3):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=r)
    bmesh.ops.translate(bm, vec=Vector(loc), verts=bm.verts)
    return finish(name, bm, mat)

def ring(name, loc, r_out, r_in, mat, verts=48, z=0.03):
    bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=False, segments=verts, radius=r_out)
    inner = bmesh.ops.create_circle(bm, cap_ends=False, segments=verts, radius=r_in)
    bm.verts.ensure_lookup_table()
    n = verts
    faces = []
    for i in range(n):
        j = (i + 1) % n
        try:
            faces.append(bm.faces.new((bm.verts[i], bm.verts[j], bm.verts[n + j], bm.verts[n + i])))
        except ValueError:
            pass
    bmesh.ops.translate(bm, vec=Vector((loc[0], loc[1], loc[2] + z)), verts=bm.verts)
    return finish(name, bm, mat)

def lines_obj(name, segs, width, mat, z=0.0):
    """Flat ribbons on the floor: segs = [((x0,y0),(x1,y1)), ...] merged into one mesh."""
    bm = bmesh.new()
    for (a, b) in segs:
        d = Vector((b[0] - a[0], b[1] - a[1], 0))
        L = d.length
        if L < 1e-5:
            continue
        d /= L
        nrm = Vector((-d.y, d.x, 0)) * (width / 2)
        v = [bm.verts.new((a[0] - nrm.x, a[1] - nrm.y, z)), bm.verts.new((a[0] + nrm.x, a[1] + nrm.y, z)),
             bm.verts.new((b[0] + nrm.x, b[1] + nrm.y, z)), bm.verts.new((b[0] - nrm.x, b[1] - nrm.y, z))]
        bm.faces.new(v)
    return finish(name, bm, mat)

# ---------------------------------------------------------------- scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# world: deep navy, a touch of a horizon glow
world = bpy.data.worlds.new("w")
world.use_nodes = True
wn = world.node_tree.nodes
wn["Background"].inputs["Color"].default_value = (*lin(hexc("03050F")), 1)
wn["Background"].inputs["Strength"].default_value = 1.0
scene.world = world

# floor: dark, slightly glossy; the board slab rises a little
floor = box("floor", (4.35, 12, -0.30), (400, 400, 0.3), mat_solid("floor", lin(hexc("060A18")), 0.28, 0.0))
slab = box("slab", (4.3, 3.5, -0.12), (17.2, 11.4, 0.24), mat_solid("slab", lin(hexc("0C1224")), 0.38, 0.1), bevel=0.06)
# slab rim glow (the board's edge), warm and faint: the cell's territory
rim_m = mat_emit("rim", AMBER, 1.6)
pts = [(-4.3, -2.2), (12.9, -2.2), (12.9, 9.2), (-4.3, 9.2)]
rim_segs = [(pts[i], pts[(i + 1) % 4]) for i in range(4)]
lines_obj("rim", rim_segs, 0.07, rim_m, z=0.012)

# grid etched across the slab (cool, faint) and far floor (cooler, sparser)
grid = []
for gx in range(-4, 13):
    grid.append(((gx + 0.0, -2.2), (gx + 0.0, 9.2)))
for gy in range(-2, 10):
    grid.append(((-4.3, gy + 0.0), (12.9, gy + 0.0)))
lines_obj("grid", grid, 0.018, mat_emit("grid", CYAN, 0.22), z=0.008)
far = []
for gx in range(-60, 80, 4):
    far.append(((gx, 9.0), (gx, 140)))
for gy in range(12, 140, 4):
    far.append(((-60, gy), (80, gy)))
lines_obj("fargrid", far, 0.06, mat_emit("fargrid", CYAN, 0.14), z=-0.14)

# network links: the cell's own wires, warm copper, between neighbouring nodes
link_m = mat_emit("link", lin(hexc("C9741A")), 1.1)
links = []
for r in (1, 2, 3):
    for c in range(3):
        links.append(((COLS[c], ROWS[r]), (COLS[c + 1], ROWS[r])))
for c in range(4):
    for r in (1, 2):
        links.append(((COLS[c], ROWS[r]), (COLS[c], ROWS[r + 1])))
lines_obj("links", links, 0.11, link_m, z=0.03)

# far wireframe skyline (seeded), kept dark and cool so it is only depth
sky_fill = mat_emit("skyfill", (0.004, 0.008, 0.024), 0.0)
sky_wire = mat_emit("skywire", lin(hexc("3A8FD0")), 1.1)
rng = random.Random(77)
for i in range(110):
    x = rng.uniform(-40, 52)
    y = rng.uniform(10, 46)
    w = rng.uniform(2.0, 6.5)
    d = rng.uniform(2.0, 6.5)
    h = rng.uniform(7, 34) * (1.0 + (y - 10) / 60.0)
    if rng.random() < 0.08:
        h *= 1.9
    box("tw%d" % i, (x, y, h / 2 - 0.3), (w, d, h), sky_fill)
    box("tww%d" % i, (x, y, h / 2 - 0.3), (w, d, h), sky_wire, wire=0.07)
# a few warm window specks so the skyline breathes (never cobalt: cobalt is the threat's)
spk = mat_emit("spk", lin(hexc("FF9A3D")), 2.2)
for i in range(120):
    x = rng.uniform(-60, 80)
    y = rng.uniform(30, 120)
    box("sp%d" % i, (x, y, rng.uniform(1, 18)), (0.35, 0.35, 0.35), spk)

box('haze', (4.4, 200, 40), (600, 0.2, 140), mat_emit('haze', lin(hexc('5B2A9A')), 0.7))
box('haze2', (4.4, 190, 8), (600, 0.2, 30), mat_emit('haze2', lin(hexc('B04DFF')), 0.9))

# ---------------------------------------------------------------- nodes
NODES = {}   # name -> world position (top-of-stack anchor) for the composite

STACK_BODY = mat_solid("stack", WARMMETAL, 0.38, 0.55)
STACK_GLOW = mat_emit("stackglow", AMBER, 2.6)
PED = mat_solid("ped", STEEL, 0.4, 0.6)
RINGG = mat_emit("ringg", AMBER, 3.2)
DEAD_BODY = mat_solid("dead", lin(hexc("23252C")), 0.6, 0.3)
DEAD_RING = mat_emit("deadring", lin(hexc("5A6070")), 1.0)

def pedestal(nm, c, r, ring_mat, rad=1.05):
    p = P(c, r)
    cyl(nm + "_ped", (p.x, p.y, 0.12), rad, 0.24, 6, PED, rot=math.radians(30))
    ring(nm + "_ring", (p.x, p.y, 0.24), rad + 0.16, rad + 0.01, ring_mat, verts=6, z=0.012)
    return p

def stack(nm, c, r, value, down=False, ghost=False):
    n = max(1, value // 2)
    p = P(c, r)
    if ghost:
        # holo outline of the stack: wireframe, warm, with a dashed floor ring
        gm = mat_emit("ghost", GOLD, 2.2, alpha=0.9)
        for i in range(n):
            box("%s_g%d" % (nm, i), (p.x, p.y, 0.45 + i * 0.36), (0.85, 0.85, 0.32), gm, wire=0.03)
        dash = []
        for k in range(14):
            a0 = k * 2 * math.pi / 14
            a1 = a0 + 0.26 * 2 * math.pi / 14 * 2.2
            dash.append(((p.x + 1.3 * math.cos(a0), p.y + 1.3 * math.sin(a0)),
                         (p.x + 1.3 * math.cos(a1), p.y + 1.3 * math.sin(a1))))
        lines_obj(nm + "_dash", dash, 0.09, mat_emit("ghostdash", GOLD, 3.0), z=0.05)
        return
    pedestal(nm, c, r, DEAD_RING if down else RINGG)
    if not down:
        for i in range(n):
            z = 0.5 + i * 0.5
            box("%s_b%d" % (nm, i), (p.x, p.y, z), (0.9, 0.9, 0.42), STACK_BODY, bevel=0.03)
            # glowing data slit on the camera-facing sides
            box("%s_s%d" % (nm, i), (p.x, p.y - 0.445, z), (0.66, 0.02, 0.07), STACK_GLOW)
            box("%s_t%d" % (nm, i), (p.x + 0.445, p.y, z), (0.02, 0.66, 0.07), STACK_GLOW)
        box("%s_cap" % nm, (p.x, p.y, 0.5 + (n - 1) * 0.5 + 0.235), (0.94, 0.94, 0.05), mat_emit("stackcap", GOLD, 2.2))
    else:
        # collapsed: the blocks lie scattered flat, grey, cold
        rr = random.Random(c * 31 + r * 7)
        for i in range(n):
            box("%s_d%d" % (nm, i), (p.x + rr.uniform(-0.55, 0.55), p.y + rr.uniform(-0.55, 0.55), 0.34 + (i % 2) * 0.1),
                (0.7, 0.7, 0.26), DEAD_BODY, rot=rr.uniform(0, 3.1), bevel=0.03)

def dark_node(nm, c, r):
    p = pedestal(nm, c, r, mat_emit("darkring", lin(hexc("4A5368")), 0.9))
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=24, v_segments=12, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.001], context="VERTS")
    for v in bm.verts:
        v.co.x *= 0.95; v.co.y *= 0.95; v.co.z *= 1.15
    bmesh.ops.translate(bm, vec=(p.x, p.y, 0.24), verts=bm.verts)
    finish(nm + "_dome", bm, mat_solid("dome", lin(hexc("08090E")), 0.15, 0.8))
    # a cold slit of light: it is alive but hidden
    box(nm + "_slit", (p.x, p.y - 0.93, 0.6), (0.5, 0.02, 0.05), mat_emit("slit", lin(hexc("6C7894")), 1.6))

def home(down_pips=0, hit=False):
    p = P(3, 3)
    cyl("home_base", (p.x, p.y, 0.14), 1.5, 0.28, 6, PED, rot=math.radians(30))
    ring("home_ring", (p.x, p.y, 0.28), 1.72, 1.52, mat_emit("homering", GOLD if not hit else EMBER, 3.6), verts=6, z=0.0)
    body = mat_solid("homebody", lin(hexc("3A2A1E")), 0.35, 0.6)
    win = mat_emit("homewin", lin(hexc("FFE2A8")) if not hit else lin(hexc("FFB0A0")), 2.6 if not hit else 4.5)
    for i in range(3):
        z = 0.65 + i * 0.95
        s = 1.35 - i * 0.12
        box("home_s%d" % i, (p.x, p.y, z), (s, s, 0.82), body, bevel=0.05)
        for k in range(3):
            box("home_w%d_%d" % (i, k), (p.x, p.y - s / 2 - 0.005, z - 0.26 + k * 0.26), (s * 0.78, 0.02, 0.07), win)
            box("home_v%d_%d" % (i, k), (p.x + s / 2 + 0.005, p.y, z - 0.26 + k * 0.26), (0.02, s * 0.78, 0.07), win)
    # integrity: three floating warm cubes
    pipm = mat_emit("pip", GOLD, 4.0)
    shat = mat_emit("pipgone", lin(hexc("FF3B4A")), 7.0)
    for k in range(3):
        x = p.x + (k - 1) * 0.72
        if k < 3 - down_pips:
            box("home_pip%d" % k, (x, p.y, 3.95), (0.42, 0.42, 0.42), pipm, rot=math.radians(20 + k * 17), bevel=0.04)
        else:
            rr = random.Random(900 + k)
            for q in range(6):
                box("home_frag%d_%d" % (k, q), (x + rr.uniform(-0.6, 0.6), p.y + rr.uniform(-0.6, 0.6), 3.95 + rr.uniform(-0.2, 0.9)),
                    (0.13, 0.13, 0.13), shat, rot=rr.uniform(0, 3))
    NODES["home"] = (p.x, p.y, 3.95)

def empty_node(nm, c, r):
    p = P(c, r)
    ring(nm + "_e", (p.x, p.y, 0.0), 0.34, 0.2, mat_emit("emptyr", lin(hexc("C9741A")), 1.4), verts=24, z=0.04)

def decoy(nm, c, r, spent=False):
    p = P(c, r)
    pedestal(nm, c, r, mat_emit("decring", GOLD, 3.0), rad=0.9)
    if not spent:
        octa(nm + "_dia", (p.x, p.y, 1.45), 0.85, 1.5, mat_solid("decoy", lin(hexc("FFC040")), 0.22, 0.95, lin(hexc("FF9A10")), 1.1))
        ring(nm + "_halo", (p.x, p.y, 0.0), 1.55, 1.42, mat_emit("dechalo", GOLD, 3.0), verts=48, z=0.05)
    else:
        rr = random.Random(5)
        for q in range(9):
            box("%s_sh%d" % (nm, q), (p.x + rr.uniform(-1, 1), p.y + rr.uniform(-1, 1), 0.3 + rr.uniform(0, 1.0)),
                (0.2, 0.2, 0.2), mat_emit("decshard", lin(hexc("FFC24A")), 3.0), rot=rr.uniform(0, 3))

# ---- emitters (the corporation's pylons) ----
def pylon(nm, x, y, lit, label_h=2.7):
    body = mat_solid("pylon", lin(hexc("12172A")), 0.35, 0.7)
    box(nm + "_b", (x, y, 1.3), (1.1, 1.6, 2.6), body, bevel=0.06)
    box(nm + "_t", (x, y, 2.9), (0.7, 1.1, 0.5), body, bevel=0.04)
    eye = mat_emit("pyl_eye_on" if lit else "pyl_eye_off", COBALT_HOT if lit else COBALT, 4.0 if lit else 1.2)
    box(nm + "_eye", (x - 0.58, y, 2.9), (0.06, 0.8, 0.2), eye)
    box(nm + "_fl", (x - 0.58, y, 1.4), (0.04, 1.0, 0.06), mat_emit("pyl_fl", COBALT, 5.0 if lit else 0.6))
    NODES[nm] = (x, y, 3.3)

# ---- beams ----
HZ = 0.62

def strip_light(nm, loc, sx, sy, rot, strength, width):
    """A cobalt area light lying along a beam: it throws the colour onto the pedestals and the floor."""
    ld = bpy.data.lights.new(nm + "_lt", "AREA")
    ld.shape = "RECTANGLE"
    ld.size = max(sx, 0.5)
    ld.size_y = max(sy, 0.5)
    ld.color = COBALT
    ld.energy = 650.0 * strength * (width / 0.62)
    ob = bpy.data.objects.new(nm + "_lt", ld)
    ob.location = loc
    bpy.context.scene.collection.objects.link(ob)

def beam_h(nm, x0, x1, y, strength=1.0, z=HZ, width=0.62, hot=True):
    """A blazing sweep line along x from x0 to x1 (any order)."""
    lo, hi = min(x0, x1), max(x0, x1)
    L = hi - lo
    cx = (lo + hi) / 2
    layers = [(width * 2.6, 0.12, COBALT, 0.55), (width * 1.6, 0.25, COBALT, 0.95),
              (width, 0.6, COBALT, 1.5 * strength), (width * 0.38, 1.0, COBALT_HOT, 6.0 * strength)]
    for i, (w, a, col, s) in enumerate(layers):
        box("%s_L%d" % (nm, i), (cx, y, z), (L, w, w * 0.55), mat_emit("bm%d_%.1f" % (i, s), col, s, alpha=a))
    strip_light(nm, (cx, y, 2.4), L, width * 2.0, 0.0, strength, width)
    # the floor wash, so the line lights the board
    box(nm + "_wash", (cx, y, 0.05), (L, width * 3.6, 0.02), mat_emit("wash", COBALT, 0.5 * strength, alpha=0.16))

def beam_v(nm, y0, y1, x, strength=1.0, z=HZ, width=0.62):
    lo, hi = min(y0, y1), max(y0, y1)
    L = hi - lo
    cy = (lo + hi) / 2
    layers = [(width * 2.6, 0.12, COBALT, 0.55), (width * 1.6, 0.25, COBALT, 0.95),
              (width, 0.6, COBALT, 1.5 * strength), (width * 0.38, 1.0, COBALT_HOT, 6.0 * strength)]
    for i, (w, a, col, s) in enumerate(layers):
        box("%s_L%d" % (nm, i), (x, cy, z), (w, L, w * 0.55), mat_emit("bm%d_%.1f" % (i, s), col, s, alpha=a))
    strip_light(nm, (x, cy, 2.4), width * 2.0, L, 0.0, strength, width)
    box(nm + "_wash", (x, cy, 0.05), (width * 3.6, L, 0.02), mat_emit("wash", COBALT, 0.5 * strength, alpha=0.16))

def dashed_h(nm, x0, x1, y, strength=0.55, z=HZ, dash=0.9, gap=0.7, w=0.16):
    x = min(x0, x1)
    hi = max(x0, x1)
    i = 0
    m = mat_emit("dsh_%.2f" % strength, COBALT, 1.5 * strength)
    while x < hi:
        e = min(x + dash, hi)
        box("%s_%d" % (nm, i), ((x + e) / 2, y, z), (e - x, w, w), m)
        x += dash + gap
        i += 1

def dashed_v(nm, y0, y1, x, strength=0.6, z=HZ, dash=0.9, gap=0.7, w=0.18):
    y = min(y0, y1)
    hi = max(y0, y1)
    i = 0
    m = mat_emit("dsv_%.2f" % strength, COBALT, 1.5 * strength)
    while y < hi:
        e = min(y + dash, hi)
        box("%s_%d" % (nm, i), (x, (y + e) / 2, z), (w, e - y, w), m)
        y += dash + gap
        i += 1

def burst(nm, loc, r, strength=1.0, red=False):
    col = lin(hexc("FF5A5A")) if red else COBALT_HOT
    sphere(nm + "_core", loc, r * 0.34, mat_emit("bcore", (1, 1, 1) if not red else lin(hexc("FFE0D8")), 14.0 * strength), sub=3)
    sphere(nm + "_mid", loc, r * 0.55, mat_emit("bmid", col, 4.0 * strength, alpha=0.22), sub=3)
    ring(nm + "_sw1", (loc[0], loc[1], 0.0), r * 2.2, r * 2.05, mat_emit("sw", COBALT_HOT, 6.0 * strength), verts=48, z=0.07)
    ring(nm + "_sw2", (loc[0], loc[1], 0.0), r * 3.4, r * 3.3, mat_emit("sw2", COBALT, 3.0 * strength), verts=48, z=0.07)
    # hard light spikes, the graphic read of an impact
    spk_m = mat_emit("spike%d" % int(red), col, 9.0 * strength, alpha=0.85)
    for q in range(6):
        ang = q * math.pi / 3 + 0.3
        box("%s_spike%d" % (nm, q), loc, (r * 5.2, 0.07, 0.07), spk_m, rot=ang)
    rr = random.Random(11)
    for q in range(22):
        a = rr.uniform(0, 6.283)
        d = rr.uniform(0.9, 3.0) * r
        box("%s_sp%d" % (nm, q), (loc[0] + math.cos(a) * d, loc[1] + math.sin(a) * d, loc[2] + rr.uniform(-0.3, 1.6)),
            (0.1, 0.1, 0.1), mat_emit("spark", col, 10.0), rot=rr.uniform(0, 3))

# ---------------------------------------------------------------- build the state
# static layout (levers placed in all three frames)
down_r1c3 = FRAME in ("reveal", "impact")
down_r2c2 = FRAME == "impact"
home_hit = FRAME == "impact"

stack("a_r1c0", 0, 1, 4)
dark_node("a_r1c1", 1, 1)
decoy("a_r1c2", 2, 1, spent=(FRAME != "plan"))
stack("a_r1c3", 3, 1, 8, down=down_r1c3)
empty_node("e_r2c0", 0, 2)
empty_node("e_r2c1", 1, 2)
stack("a_r2c2", 2, 2, 4, down=down_r2c2)
empty_node("e_r3c0", 0, 3)
empty_node("e_r3c1", 1, 3)
stack("a_r3c2", 2, 3, 8)
stack("a_r2c3", 3, 2, 8, ghost=True)
home(down_pips=1 if home_hit else 0, hit=home_hit)

# 3D anchor points the composite needs
def anchor(nm, c, r, z):
    p = P(c, r)
    NODES[nm] = (p.x, p.y, z)

anchor("r1c0", 0, 1, 1.5)
anchor("r1c1", 1, 1, 1.7)
anchor("r1c2", 2, 1, 2.6)
anchor("r1c3", 3, 1, 2.0)
anchor("r2c2", 2, 2, 1.5)
anchor("r3c2", 2, 3, 2.0)
anchor("r2c3", 3, 2, 2.0)

pylon("p_r1_right", ENTRY_X, ROWS[1], FRAME != "reveal" or True)
pylon("p_r2_right", ENTRY_X, ROWS[2], FRAME in ("reveal", "impact"))
pylon("p_r3_right", ENTRY_X, ROWS[3], FRAME == "plan")
pylon("p_r1_left", LEFT_X, ROWS[1], FRAME == "plan")
for k in ("p_r2_right", "p_r1_left"):
    pass

if FRAME == "plan":
    # beam 1: known. It stops on the decoy.
    beam_h("beam1", ENTRY_X - 0.6, COLS[2] + 0.9, ROWS[1], strength=1.25, width=0.9)
    # sealed candidates: dashed ghost lines, each with its pylon lit dim
    dashed_h("cand_sq", ENTRY_X - 0.8, LEFT_X + 2.5, ROWS[2], strength=1.1, dash=1.1, gap=0.6, w=0.24)
    dashed_h("cand_ci", ENTRY_X - 0.8, LEFT_X + 2.5, ROWS[3], strength=1.1, dash=1.1, gap=0.6, w=0.24)
    dashed_h("cand_tr", LEFT_X + 0.8, COLS[2] - 1.6, ROWS[1], strength=1.1, z=HZ + 0.02, dash=1.1, gap=0.6, w=0.24)
    # hunter's column, forecast from the node beam 1 touches
    dashed_v("hunt", ROWS[1] - 0.9, ROWS[3] - 2.2, COLS[3], strength=1.1, z=1.3, dash=0.8, gap=0.5, w=0.28)
elif FRAME == "reveal":
    # beam 1 has gone: a fading afterglow on its row
    beam_h("beam1", ENTRY_X - 0.6, COLS[2] + 0.9, ROWS[1], strength=0.14, width=0.4)
    # the real line (square, R2) ignites, front travelling left
    beam_h("beam2", ENTRY_X - 0.6, 2.3, ROWS[2], strength=1.15, width=0.78)
    burst("front", (2.1, ROWS[2], HZ), 0.55, strength=0.8)
    # the collapsed candidates: two short dying stubs from their pylons
    for nm, y in (("c_ci", ROWS[3]),):
        dashed_h(nm, ENTRY_X - 0.8, ENTRY_X - 3.3, y, strength=0.22)
    dashed_h("c_tr", LEFT_X + 0.8, LEFT_X + 3.0, ROWS[1], strength=0.22)
    # the hunter column, waiting (the JAM target)
    dashed_v("hunt", ROWS[1] - 0.9, ROWS[3] - 2.2, COLS[3], strength=1.3, z=1.3, dash=0.8, gap=0.5, w=0.3)
else:
    beam_h("beam1", ENTRY_X - 0.6, COLS[2] + 0.9, ROWS[1], strength=0.10, width=0.36)
    beam_h("beam2", ENTRY_X - 0.6, COLS[2] - 0.6, ROWS[2], strength=0.30, width=0.5)
    burst("b2hit", (COLS[2], ROWS[2], 1.0), 0.42, strength=0.5)
    # the hunter: head at HOME, shaft back to row 1
    beam_v("hunter", ROWS[1] + 0.6, ROWS[3] - 1.4, COLS[3], strength=1.2, width=1.0)
    burst("hhit", (COLS[3], ROWS[3] - 1.0, 1.4), 0.85, strength=1.2, red=True)

# data motes drifting over the board (seeded): depth cues, warm and cool
mrng = random.Random(2026)
mote_w = mat_emit('mote_w', lin(hexc('FFB020')), 3.0)
mote_c = mat_emit('mote_c', lin(hexc('5CE1FF')), 2.2)
for i in range(170):
    box('mote%d' % i, (mrng.uniform(-8, 17), mrng.uniform(-6, 14), mrng.uniform(0.3, 9.0)), (0.07, 0.07, 0.07),
        mote_w if i % 3 else mote_c, rot=mrng.uniform(0, 3))

# ---------------------------------------------------------------- lights
def add_light(nm, kind, loc, color, energy, size=None, target=None):
    ld = bpy.data.lights.new(nm, kind)
    ld.color = color
    ld.energy = energy
    if size is not None:
        if kind == "AREA":
            ld.size = size
        else:
            ld.shadow_soft_size = size
    ob = bpy.data.objects.new(nm, ld)
    ob.location = loc
    scene.collection.objects.link(ob)
    if target is not None:
        d = Vector(target) - Vector(loc)
        ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return ob

add_light("key", "AREA", (-6, -9, 14), (0.55, 0.62, 1.0), 650, 14, (4.4, 3.5, 0))
add_light("warm", "AREA", (4.4, 3.5, 11), (1.0, 0.7, 0.4), 500, 10, (4.4, 3.5, 0))
add_light("rimL", "AREA", (16, 14, 9), (0.35, 0.5, 1.0), 260, 10, (4.4, 3.5, 1))
if FRAME == "plan":
    add_light("b1", "POINT", (8.7, 7, 2.0), COBALT, 900, 2.0)
elif FRAME == "reveal":
    add_light("b2", "POINT", (5.8, 3.5, 2.2), COBALT, 2400, 2.5)
    add_light("b2b", "POINT", (10.5, 3.5, 2.2), COBALT, 1500, 2.5)
else:
    add_light("h1", "POINT", (8.7, -0.8, 3.0), (1.0, 0.25, 0.25), 3600, 2.5)
    add_light("h2", "POINT", (8.7, 5, 2.0), COBALT, 1800, 2.5)
    add_light("b2h", "POINT", (5.8, 3.5, 2.0), COBALT, 900, 2.5)

# ---------------------------------------------------------------- camera (identical in all frames)
cam_d = bpy.data.cameras.new("cam")
cam_d.lens = 116
cam_d.shift_y = -0.02
cam_d.sensor_width = 36
cam_ob = bpy.data.objects.new("cam", cam_d)
cam_ob.location = (-3.0, -48.0, 56.0)
tgt = Vector((4.4, 3.4, 0.8))
cam_ob.rotation_euler = (tgt - Vector(cam_ob.location)).to_track_quat("-Z", "Y").to_euler()
scene.collection.objects.link(cam_ob)
scene.camera = cam_ob

r = scene.render
try:
    r.engine = "BLENDER_EEVEE"
except TypeError:
    r.engine = "BLENDER_EEVEE_NEXT"
r.resolution_x, r.resolution_y = RES
r.image_settings.file_format = "PNG"
r.image_settings.color_mode = "RGB"
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
try:
    scene.eevee.taa_render_samples = SAMPLES
    scene.eevee.use_raytracing = True
    scene.eevee.use_shadows = True
except Exception as e:
    print("eevee setting warn", e)

# project the anchors for the composite
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
proj = {"_res": list(RES)}
for k, (x, y, z) in NODES.items():
    co = world_to_camera_view(scene, cam_ob, Vector((x, y, z)))
    proj[k] = [co.x * RES[0], (1 - co.y) * RES[1]]
# beam ends and lane points the composite labels
for nm, (x, y, z) in {"in_r1": (ENTRY_X - 0.8, ROWS[1], HZ), "in_r2": (ENTRY_X - 0.8, ROWS[2], HZ),
                      "in_r3": (ENTRY_X - 0.8, ROWS[3], HZ), "in_r1L": (LEFT_X + 0.8, ROWS[1], HZ),
                      "hunt_top": (COLS[3], ROWS[1] - 0.9, HZ), "hunt_bot": (COLS[3], ROWS[3] - 2.2, HZ),
                      "r3_front": (2.1, ROWS[2], HZ), "hunt_head": (COLS[3], ROWS[3] - 0.9, HZ)}.items():
    co = world_to_camera_view(scene, cam_ob, Vector((x, y, z)))
    proj[nm] = [co.x * RES[0], (1 - co.y) * RES[1]]
for nm, (x, y, z) in {'cBL': (-4.3, -2.2, 0), 'cBR': (12.9, -2.2, 0), 'cTR': (12.9, 9.2, 0), 'cTL': (-4.3, 9.2, 0), 'pyl': (12.4, 7, 3.4), 'pylL': (-3.8, 7, 3.4)}.items():
    co = world_to_camera_view(scene, cam_ob, Vector((x, y, z)))
    print('CORNER', nm, round(co.x * 1920), round((1 - co.y) * 1080))
os.makedirs(OUT, exist_ok=True)
json.dump(proj, open(os.path.join(OUT, FRAME + "_nodes.json"), "w"), indent=1)

scene.render.filepath = os.path.join(OUT, FRAME + "_raw.png")
bpy.ops.render.render(write_still=True)
print("RENDERED", FRAME, flush=True)
