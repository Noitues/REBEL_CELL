# r2b_painterly_matte - the black-market stall (Blender 5.2, headless).
# Usage: blender -b --factory-startup --python shop_scene.py -- <beauty|depth> <out.png> [samples]
import bpy, bmesh, sys, math, random
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
MODE, OUT = argv[0], argv[1]
SAMPLES = int(argv[2]) if len(argv) > 2 else 64
DEPTH = MODE == "depth"
DMAX = 60.0
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)
rng = random.Random(777)

def mat(name, color, rough=0.6, metal=0.0, emit=0.0, bump=0.0, patina=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*color, 1); b.inputs["Emission Strength"].default_value = emit
    if bump or patina:
        g = nt.nodes.new("ShaderNodeNewGeometry")
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 2.5; nz.inputs["Detail"].default_value = 10
        nt.links.new(g.outputs["Position"], nz.inputs["Vector"])
        bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = max(bump, 0.2)
        nt.links.new(nz.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
        ramp = nt.nodes.new("ShaderNodeValToRGB"); e = ramp.color_ramp.elements
        e[0].position = 0.35; e[0].color = tuple(c * 0.6 for c in color) + (1,)
        e[1].position = 0.7; e[1].color = ((0.22, 0.5, 0.44, 1) if patina else (*color, 1))
        nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m

STUCCO = mat("stucco", (0.36, 0.25, 0.17), 0.9, bump=0.5)
STONE = mat("stone", (0.28, 0.18, 0.12), 0.95, bump=0.8)
WOOD = mat("wood", (0.22, 0.11, 0.06), 0.55, bump=0.4)
BRASS = mat("brass", (0.86, 0.60, 0.26), 0.3, 1.0, patina=True)
BLUE = mat("blue", (0.02, 0.035, 0.11), 0.5, bump=0.3)
DARK = mat("dark", (0.03, 0.025, 0.02), 0.9)
CLOTH = mat("cloth", (0.45, 0.04, 0.03), 0.85, emit=0.15)
ROBE = mat("robe", (0.10, 0.12, 0.13), 0.85)
LANTERN = mat("lantern", (1.0, 0.55, 0.22), 0.4, emit=14.0)
CYAN = mat("cyan", (0.1, 0.95, 0.9), 0.3, emit=12.0)
MAG = mat("mag", (1.0, 0.2, 0.7), 0.3, emit=10.0)
CRATE = mat("crate", (0.30, 0.20, 0.12), 0.8, bump=0.5)
TEAL = mat("tealcrate", (0.08, 0.26, 0.24), 0.7, bump=0.4)
SCREEN = mat("screen", (0.2, 0.8, 0.7), 0.3, emit=3.0)

def link(ob):
    scene.collection.objects.link(ob); return ob

def prim(kind, m, smooth=True, **kw):
    getattr(bpy.ops.mesh, "primitive_" + kind + "_add")(**kw)
    ob = bpy.context.active_object
    if m:
        ob.data.materials.append(m)
    for p in ob.data.polygons:
        p.use_smooth = smooth
    return ob

def box(x, y, z0, sx, sy, sz, m, rz=0.0):
    ob = prim("cube", m, False, size=1.0, location=(x, y, z0 + sz / 2))
    ob.scale = (sx, sy, sz); ob.rotation_euler.z = rz
    return ob

def upper_half(ob, loc):
    me = ob.data
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.y < -0.01], context="VERTS")
    bm.to_mesh(me); bm.free()
    ob.rotation_euler = (math.pi / 2, 0, 0); ob.location = loc
    return ob

# floor, back wall with a great arch, side walls
box(0, 4, -0.2, 40, 30, 0.2, STONE)
FLOORM = STONE
box(-7.5, 3.2, 0, 8, 1.2, 14, STUCCO)
box(7.5, 3.2, 0, 8, 1.2, 14, STUCCO)
box(0, 3.2, 8.2, 7.2, 1.2, 6, STUCCO)
upper_half(prim("torus", STUCCO, True, major_radius=3.6, minor_radius=0.45, major_segments=64, location=(0, 0, 0)), (0, 2.55, 4.6))
for k in range(15):
    a = math.pi * k / 14
    prim("uv_sphere", BRASS, True, radius=0.11, location=(math.cos(a) * 4.15, 2.45, 4.6 + math.sin(a) * 4.15))
# the alcove interior: deep, lit warm, shelves of contraband
box(0, 7.5, 0, 12, 1, 12, STONE)
box(-3.6, 5.5, 0, 0.4, 4, 9, STONE); box(3.6, 5.5, 0, 0.4, 4, 9, STONE)
for z in (1.6, 3.2, 4.8):
    box(0, 6.6, z, 6.6, 1.2, 0.12, WOOD)
    x = -3.0
    while x < 2.9:
        w = rng.uniform(0.25, 0.7); h = rng.uniform(0.3, 1.1)
        kind = rng.random()
        if kind < 0.35:
            prim("cylinder", BRASS if rng.random() < 0.5 else TEAL, True, vertices=16, radius=w * 0.4, depth=h,
                 location=(x + w / 2, 6.5 + rng.uniform(-0.2, 0.2), z + 0.12 + h / 2))
        elif kind < 0.8:
            box(x + w / 2, 6.5 + rng.uniform(-0.2, 0.2), z + 0.12, w, 0.6, h, CRATE if rng.random() < 0.6 else TEAL, rng.uniform(-0.2, 0.2))
        else:
            box(x + w / 2, 6.3, z + 0.12, w, 0.1, h * 0.7, SCREEN)
        x += w + rng.uniform(0.05, 0.25)
# blue pilasters with brass capitals framing the arch
for sx in (-1, 1):
    box(sx * 4.6, 2.3, 0, 0.7, 0.7, 8.4, BLUE)
    prim("uv_sphere", BRASS, True, radius=0.5, location=(sx * 4.6, 2.3, 8.8))
    box(sx * 4.6, 2.3, 0, 1.0, 1.0, 0.6, BRASS)
# hanging lanterns and cloth banners
for (x, z) in [(-2.3, 6.8), (2.3, 6.8), (0, 7.8), (-6.2, 6.0), (6.2, 6.0)]:
    prim("cylinder", DARK, False, vertices=6, radius=0.02, depth=4, location=(x, 2.0, z + 2.3))
    prim("cylinder", LANTERN, True, vertices=8, radius=0.22, depth=0.5, location=(x, 2.0, z))
    prim("cone", BRASS, True, vertices=8, radius1=0.3, depth=0.25, location=(x, 2.0, z + 0.36))
    pl = bpy.data.lights.new("lan", "POINT"); pl.energy = 220; pl.color = (1.0, 0.6, 0.3); pl.shadow_soft_size = 0.3
    po = bpy.data.objects.new("lan", pl); link(po); po.location = (x, 1.8, z - 0.1)
for sx in (-1, 1):
    b = box(sx * 5.7, 2.4, 3.6, 1.1, 0.06, 3.8, CLOTH)
# counter across the foreground
box(0, -1.6, 0, 11, 1.6, 1.15, WOOD)
box(0, -1.6, 1.15, 11.3, 1.8, 0.1, BRASS)
for k in range(12):
    prim("uv_sphere", BRASS, True, radius=0.07, location=(-5 + k * 10 / 11, -2.45, 0.6))
# clutter on the counter
for k in range(9):
    x = rng.uniform(-5, 5)
    if abs(x) < 1.0:
        continue
    box(x, -1.4 + rng.uniform(-0.3, 0.3), 1.25, rng.uniform(0.3, 0.6), rng.uniform(0.3, 0.5), rng.uniform(0.15, 0.4), CRATE, rng.uniform(-0.5, 0.5))
# the dealer: hooded figure behind the counter with a lit visor
prim("cone", ROBE, True, vertices=24, radius1=0.9, radius2=0.35, depth=2.6, location=(1.9, 0.4, 1.3))
prim("uv_sphere", ROBE, True, radius=0.42, location=(1.9, 0.4, 2.8))
hood = prim("cone", ROBE, True, vertices=24, radius1=0.52, depth=0.9, location=(1.9, 0.5, 3.05))
v = box(1.9, 0.04, 2.8, 0.5, 0.08, 0.08, CYAN)
prim("uv_sphere", ROBE, True, radius=0.45, location=(1.9, 0.5, 2.45))
# neon tubes
box(0, 2.4, 10.4, 5.0, 0.1, 0.12, CYAN)
box(-5.7, 2.2, 8.0, 0.1, 0.1, 2.5, MAG); box(5.7, 2.2, 8.0, 0.1, 0.1, 2.5, MAG)
# a small figure browsing at the left (scale)
prim("cone", CLOTH, True, vertices=16, radius1=0.45, radius2=0.18, depth=1.6, location=(-5.2, -0.3, 0.8))
prim("uv_sphere", ROBE, True, radius=0.2, location=(-5.2, -0.3, 1.75))

# wall ornament: brass cog medallions, a flickering screen, sagging cables
for sx in (-1, 1):
    g = prim("cylinder", BRASS, True, vertices=24, radius=0.9, depth=0.15, location=(sx * 7.0, 2.5, 9.6), rotation=(math.pi / 2, 0, 0))
    for k in range(12):
        a = k / 12 * math.tau
        box(sx * 7.0 + math.cos(a) * 1.0, 2.5, 9.6 + math.sin(a) * 1.0 - 0.12, 0.25, 0.15, 0.25, BRASS, 0)
    prim("uv_sphere", CYAN if sx < 0 else MAG, True, radius=0.25, location=(sx * 7.0, 2.4, 9.6))
box(-6.6, 2.5, 1.6, 2.2, 0.2, 1.4, SCREEN)
box(-6.6, 2.6, 1.45, 2.5, 0.2, 1.7, DARK)
for k in range(7):
    x0 = rng.uniform(-9, 9); x1 = x0 + rng.uniform(1.5, 4); zc = rng.uniform(10.5, 12.5); sag = rng.uniform(0.4, 1.2)
    for t in range(12):
        f = t / 11
        prim("uv_sphere", DARK, True, radius=0.05, segments=6, ring_count=4,
             location=(x0 + (x1 - x0) * f, 2.0, zc - sag * math.sin(f * math.pi)))
for k in range(8):   # crates stacked at the sides
    sx = -1 if k < 4 else 1
    box(sx * rng.uniform(6.5, 9), rng.uniform(-1, 1), 0, rng.uniform(0.9, 1.5), rng.uniform(0.9, 1.4), rng.uniform(0.7, 1.4),
        CRATE if k % 3 else TEAL, rng.uniform(-0.3, 0.3))

# lights: warm key from inside the alcove, cool night from outside-left, rim
for (loc, e, c) in [((0, 5.0, 3.5), 1600, (1.0, 0.55, 0.25)), ((-2.5, 4.5, 6), 500, (1.0, 0.6, 0.3)),
                    ((-9, -6, 6), 1100, (0.3, 0.5, 1.0)), ((8, -4, 3), 260, (1.0, 0.25, 0.6)), ((5, -5, 7), 1200, (1.0, 0.62, 0.35)),
                    ((0, -8, 4), 600, (0.9, 0.75, 0.6))]:
    pl = bpy.data.lights.new("k", "AREA" if e > 1000 else "POINT"); pl.energy = e; pl.color = c
    if pl.type == "AREA":
        pl.size = 3.0
    po = bpy.data.objects.new("k", pl); link(po); po.location = loc
    po.rotation_euler = (Vector((0, 2, 3)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.03, 0.05, 0.12, 1); bg.inputs["Strength"].default_value = 1.0

cd = bpy.data.cameras.new("cam"); cd.lens = 30
cam = bpy.data.objects.new("cam", cd); link(cam); scene.camera = cam
cam.location = (0, -13.5, 3.4); cam.rotation_euler = (math.radians(88), 0, 0)
try:
    scene.render.engine = "BLENDER_EEVEE"
except TypeError as e:
    print("ENGINE", e)
scene.eevee.taa_render_samples = SAMPLES if not DEPTH else 1
if hasattr(scene.eevee, "use_raytracing") and not DEPTH:
    scene.eevee.use_raytracing = True
scene.render.resolution_x, scene.render.resolution_y = 1920, 1080
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGBA"
try:
    scene.view_settings.view_transform = "Raw" if DEPTH else "Standard"
except Exception:
    pass
if DEPTH:
    m = bpy.data.materials.new("depth"); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        if n.type != "OUTPUT_MATERIAL":
            nt.nodes.remove(n)
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    c = nt.nodes.new("ShaderNodeCameraData")
    d = nt.nodes.new("ShaderNodeMath"); d.operation = "DIVIDE"; d.use_clamp = True; d.inputs[1].default_value = DMAX
    s = nt.nodes.new("ShaderNodeMath"); s.operation = "SQRT"
    e = nt.nodes.new("ShaderNodeEmission")
    nt.links.new(c.outputs["View Z Depth"], d.inputs[0]); nt.links.new(d.outputs[0], s.inputs[0])
    nt.links.new(s.outputs[0], e.inputs["Color"]); nt.links.new(e.outputs[0], out.inputs["Surface"])
    scene.view_layers[0].material_override = m
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("DONE shop", MODE)
