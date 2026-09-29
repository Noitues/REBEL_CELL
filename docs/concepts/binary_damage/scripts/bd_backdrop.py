"""Blender 5.2 headless: renders a dark, low-detail isometric city backdrop for the
binary-damage VFX concept. Run:
  blender -b --factory-startup --python bd_backdrop.py -- <out.png>
Seeded (random.Random(7)), so reruns match. Desaturation/dimming happens later in Pillow.
"""
import bpy, sys, math, random

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "backdrop.png"
R = random.Random(7)

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
try:
    sc.render.engine = "BLENDER_EEVEE"
except TypeError as e:
    print("engine fallback", e)
    sc.render.engine = "CYCLES"
sc.render.resolution_x, sc.render.resolution_y = 1280, 720
sc.render.film_transparent = False
try:
    sc.eevee.taa_render_samples = 16
except Exception:
    pass
sc.view_settings.view_transform = "Standard"

world = bpy.data.worlds.new("w"); sc.world = world
world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs[0].default_value = (0.004, 0.006, 0.012, 1); bg.inputs[1].default_value = 1.0


def mat_emit(name, rgb, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*rgb, 1); e.inputs[1].default_value = strength
    nt.links.new(e.outputs[0], o.inputs[0])
    return m


def mat_slate(name, rgb):
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    p.inputs["Base Color"].default_value = (*rgb, 1)
    p.inputs["Roughness"].default_value = 0.6
    return m

slate = [mat_slate("s%d" % i, c) for i, c in enumerate([(0.03, 0.05, 0.07), (0.04, 0.04, 0.07), (0.02, 0.05, 0.05)])]
inks = [(0.36, 0.88, 1.0), (1.0, 0.24, 0.66), (0.83, 1.0, 0.0), (0.69, 0.30, 1.0), (1.0, 0.69, 0.0)]
win = [mat_emit("w%d" % i, c, 2.5) for i, c in enumerate(inks)]
road = mat_emit("road", (0.36, 0.88, 1.0), 1.2)

ground = bpy.data.meshes.new("g")
bpy.ops.mesh.primitive_plane_add(size=80)
bpy.context.object.data.materials.append(mat_slate("gnd", (0.01, 0.015, 0.02)))

# roads: glowing thin strips every 6 units
for i in range(-5, 6):
    for axis in (0, 1):
        bpy.ops.mesh.primitive_cube_add(size=1)
        o = bpy.context.object
        o.scale = (60, 0.08, 0.01) if axis == 0 else (0.08, 60, 0.01)
        o.location = (0, i * 6 + 3, 0.01) if axis == 0 else (i * 6 + 3, 0, 0.01)
        o.data.materials.append(road)

# blocks
for gx in range(-5, 5):
    for gy in range(-5, 5):
        for k in range(R.randint(1, 3)):
            w = R.uniform(1.2, 2.4); d = R.uniform(1.2, 2.4); h = R.choice([1, 2, 3, 4, 6, 9]) * R.uniform(0.7, 1.3)
            x = gx * 6 + R.uniform(-1.4, 1.4); y = gy * 6 + R.uniform(-1.4, 1.4)
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, h / 2))
            o = bpy.context.object; o.scale = (w, d, h)
            o.data.materials.append(R.choice(slate))
            # window bands on the two camera-facing faces
            ink = R.choice(win)
            for lvl in range(int(h / 0.7)):
                if R.random() < 0.45:
                    continue
                z = 0.4 + lvl * 0.7
                if z > h - 0.2:
                    break
                bpy.ops.mesh.primitive_cube_add(size=1, location=(x - w / 2 - 0.01, y, z))
                b = bpy.context.object; b.scale = (0.02, d * R.uniform(0.3, 0.9), 0.08)
                b.data.materials.append(ink)
                bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y - d / 2 - 0.01, z))
                b = bpy.context.object; b.scale = (w * R.uniform(0.3, 0.9), 0.02, 0.08)
                b.data.materials.append(ink)

# a curving elevated highway ribbon
for i in range(60):
    t = i / 59
    x = -30 + 60 * t; y = 8 * math.sin(t * 3.0) - 2; z = 5 + 2 * math.sin(t * 5)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, y, z))
    o = bpy.context.object; o.scale = (1.1, 1.6, 0.12)
    o.data.materials.append(mat_emit("hw%d" % i, (0.2, 0.9, 0.7), 0.6))

sun = bpy.data.lights.new("moon", "SUN"); sun.energy = 0.6; sun.color = (0.5, 0.7, 1.0)
so = bpy.data.objects.new("moon", sun); sc.collection.objects.link(so)
so.rotation_euler = (math.radians(50), 0, math.radians(30))

cam = bpy.data.cameras.new("cam"); cam.type = "ORTHO"; cam.ortho_scale = 34
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co); sc.camera = co
co.location = (-30, -30, 30)
co.rotation_euler = (math.radians(60), 0, math.radians(-45))

# compositor glare (API varies across versions; best effort)
try:
    sc.use_nodes = True
    tree = sc.node_tree
    rl = next(n for n in tree.nodes if n.type == "R_LAYERS")
    comp = next(n for n in tree.nodes if n.type == "COMPOSITE")
    g = tree.nodes.new("CompositorNodeGlare")
    try:
        g.glare_type = "FOG_GLOW"
    except Exception:
        pass
    tree.links.new(rl.outputs[0], g.inputs[0]); tree.links.new(g.outputs[0], comp.inputs[0])
except Exception as e:
    print("compositor skipped:", e)

sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("WROTE", out)
