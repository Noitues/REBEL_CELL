# r2b_painterly_matte - ornate brass spinners and shop spinner-parts (Blender 5.2, headless).
# Usage: blender -b --factory-startup --python spinner_scene.py -- <out_dir> [samples]
# Writes spinner_player.png, spinner_enemy.png, part_wedge.png, part_hub.png, part_pointer.png, spinners.json
import bpy, bmesh, sys, math, json, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
SAMPLES = int(argv[1]) if len(argv) > 1 else 64
scene = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o, do_unlink=True)

TICKS = 30
KIND_COL = {"ATTACK": (0.60, 0.05, 0.03), "BLOCK": (0.03, 0.34, 0.36), "HACK": (0.24, 0.08, 0.52),
            "CREDIT": (0.78, 0.50, 0.10), "BLANK": (0.035, 0.035, 0.045)}
LAYOUTS = {
    "player": [("ATTACK", 6), ("BLOCK", 5), ("HACK", 4), ("ATTACK", 4), ("CREDIT", 3), ("BLOCK", 5), ("BLANK", 3)],
    "enemy":  [("ATTACK", 8), ("BLANK", 4), ("ATTACK", 6), ("BLOCK", 6), ("HACK", 3), ("BLANK", 3)],
}

def principled(name, color, rough=0.5, metal=0.0, emit=0.0, noise=0.0, patina=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit > 0:
        b.inputs["Emission Color"].default_value = (*color, 1)
        b.inputs["Emission Strength"].default_value = emit
    if noise > 0 or patina:
        g = nt.nodes.new("ShaderNodeNewGeometry")
        nz = nt.nodes.new("ShaderNodeTexNoise"); nz.inputs["Scale"].default_value = 9.0; nz.inputs["Detail"].default_value = 8
        nt.links.new(g.outputs["Position"], nz.inputs["Vector"])
        bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = max(noise, 0.2)
        nt.links.new(nz.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], b.inputs["Normal"])
        if patina:
            ramp = nt.nodes.new("ShaderNodeValToRGB")
            e = ramp.color_ramp.elements
            e[0].position = 0.42; e[0].color = (*color, 1)
            e[1].position = 0.62; e[1].color = (0.22, 0.50, 0.44, 1)
            nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"]); nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m

BRASS = principled("brass", (0.86, 0.60, 0.26), 0.3, 1.0, noise=0.15, patina=True)
IRON = principled("iron", (0.16, 0.14, 0.14), 0.45, 1.0, noise=0.3)
DARK = principled("backplate", (0.04, 0.04, 0.05), 0.6, 0.3, noise=0.2)
PATINA = principled("patina", (0.30, 0.46, 0.40), 0.5, 0.4, noise=0.3, patina=True)
RED_GLOW = principled("redglow", (1.0, 0.1, 0.05), 0.3, 0.0, emit=6.0)
CYAN_GLOW = principled("cyanglow", (0.1, 0.95, 0.9), 0.3, 0.0, emit=5.0)
ENAMEL = {k: principled("en_" + k, c, 0.22, 0.0, emit=0.25) for k, c in KIND_COL.items()}

def link(ob):
    scene.collection.objects.link(ob); return ob

def mesh(name, verts, faces, mat, coll):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); me.materials.append(mat)
    coll.objects.link(ob)
    for p in me.polygons:
        p.use_smooth = False
    return ob

def pol(r, a):  # angle clockwise from 12 o'clock
    return (math.sin(a) * r, math.cos(a) * r)

def sector(name, a0, a1, r0, r1, z0, z1, mat, coll, steps=24, bevel=0.02):
    vt, vb = [], []
    n = max(4, int(steps * (a1 - a0) / (math.pi / 3)))
    outer = [pol(r1, a0 + (a1 - a0) * i / n) for i in range(n + 1)]
    inner = [pol(r0, a1 - (a1 - a0) * i / n) for i in range(n + 1)]
    ring = outer + inner
    verts = [(x, y, z1) for (x, y) in ring] + [(x, y, z0) for (x, y) in ring]
    m = len(ring)
    faces = [tuple(range(m))[::-1], tuple(range(m, 2 * m))]
    faces = [tuple(range(m)), tuple(range(2 * m - 1, m - 1, -1))]
    for i in range(m):
        j = (i + 1) % m
        faces.append((i, i + m, j + m, j))
    ob = mesh(name, verts, faces, mat, coll)
    return ob

def add_prim(kind, mat, coll, **kw):
    getattr(bpy.ops.mesh, "primitive_" + kind + "_add")(**kw)
    ob = bpy.context.active_object
    ob.data.materials.append(mat)
    for p in ob.data.polygons:
        p.use_smooth = True
    for c in ob.users_collection:
        c.objects.unlink(ob)
    coll.objects.link(ob)
    return ob

def new_coll(name):
    c = bpy.data.collections.new(name); scene.collection.children.link(c); return c

def build_spinner(tag, layout, rim_mat, accent):
    coll = new_coll(tag)
    add_prim("cylinder", DARK, coll, vertices=96, radius=1.0, depth=0.1, location=(0, 0, -0.05))
    add_prim("torus", rim_mat, coll, major_radius=1.0, minor_radius=0.07, major_segments=96, location=(0, 0, 0.03))
    add_prim("torus", rim_mat, coll, major_radius=1.13, minor_radius=0.045, major_segments=96, location=(0, 0, 0.02))
    add_prim("cylinder", rim_mat, coll, vertices=96, radius=1.13, depth=0.06, location=(0, 0, -0.04))
    # the 30 ticks: studs around the rim, every fifth a larger one
    for t in range(TICKS):
        a = t / TICKS * math.tau
        x, y = pol(1.065, a)
        r = 0.032 if t % 5 else 0.05
        add_prim("uv_sphere", BRASS if rim_mat == BRASS else IRON, coll, radius=r, segments=12, ring_count=8, location=(x, y, 0.06))
    # scalloped outer crest (the ornament)
    for t in range(TICKS):
        a = (t + 0.5) / TICKS * math.tau
        x, y = pol(1.17, a)
        add_prim("uv_sphere", rim_mat, coll, radius=0.038, segments=10, ring_count=6, location=(x, y, 0.0))
    # slices
    slices = []
    tick = 0
    gap = 0.012
    for (kind, n) in layout:
        a0 = tick / TICKS * math.tau; a1 = (tick + n) / TICKS * math.tau
        sector("%s_slice" % tag, a0 + gap, a1 - gap, 0.30, 0.93, 0.0, 0.05, ENAMEL[kind], coll)
        slices.append({"kind": kind, "start": tick, "len": n})
        tick += n
    # dividing spokes
    for s in slices:
        a = s["start"] / TICKS * math.tau
        x, y = pol(0.62, a)
        sp = add_prim("cube", rim_mat, coll, size=1.0, location=(x, y, 0.06))
        sp.scale = (0.022, 0.64, 0.03); sp.rotation_euler.z = -a
    # hub: layered boss with patina dome and brass finial
    add_prim("cylinder", rim_mat, coll, vertices=64, radius=0.31, depth=0.08, location=(0, 0, 0.06))
    add_prim("torus", rim_mat, coll, major_radius=0.30, minor_radius=0.03, location=(0, 0, 0.1))
    d = add_prim("uv_sphere", PATINA, coll, radius=0.24, segments=48, ring_count=24, location=(0, 0, 0.08))
    d.scale.z = 0.55
    for k in range(8):
        x, y = pol(0.27, k / 8 * math.tau)
        add_prim("uv_sphere", rim_mat, coll, radius=0.022, location=(x, y, 0.11))
    add_prim("uv_sphere", accent, coll, radius=0.07, location=(0, 0, 0.22))
    add_prim("cone", rim_mat, coll, vertices=24, radius1=0.05, depth=0.12, location=(0, 0, 0.3))
    # pointer at 12 o'clock, pointing into the wheel
    p = new_coll(tag + "_pointer")
    ptr = [build_pointer(p, rim_mat, accent, 0.0, 1.22)]
    return coll, p, slices

def build_pointer(coll, mat, accent, x, y):
    c = add_prim("cone", mat, coll, vertices=4, radius1=0.12, depth=0.34, location=(x, y - 0.02, 0.22),
                 rotation=(math.pi / 2, 0, 0))
    c.scale = (1.0, 0.45, 1.0)
    add_prim("uv_sphere", mat, coll, radius=0.11, location=(x, y + 0.14, 0.22))
    add_prim("uv_sphere", accent, coll, radius=0.05, location=(x, y + 0.14, 0.31))
    for sx in (-1, 1):
        w = add_prim("cone", mat, coll, vertices=3, radius1=0.09, depth=0.2, location=(x + sx * 0.14, y + 0.16, 0.2),
                     rotation=(0, sx * math.pi / 2, 0))
    return c

player, player_ptr, player_slices = build_spinner("player", LAYOUTS["player"], BRASS, CYAN_GLOW)
enemy, enemy_ptr, enemy_slices = build_spinner("enemy", LAYOUTS["enemy"], IRON, RED_GLOW)

# shop parts
part_w = new_coll("part_wedge")
sector("wedge", 0.0, 5 / TICKS * math.tau, 0.30, 0.93, 0.0, 0.07, ENAMEL["HACK"], part_w)
sector("wedge_rim", 0.0, 5 / TICKS * math.tau, 0.93, 1.02, -0.02, 0.09, BRASS, part_w)
for t in range(6):
    x, y = pol(0.975, t / TICKS * math.tau)
    add_prim("uv_sphere", BRASS, part_w, radius=0.035, location=(x, y, 0.1))
part_h = new_coll("part_hub")
add_prim("cylinder", BRASS, part_h, vertices=64, radius=0.31, depth=0.08, location=(0, 0, 0.0))
d = add_prim("uv_sphere", PATINA, part_h, radius=0.24, segments=48, ring_count=24, location=(0, 0, 0.03)); d.scale.z = 0.6
add_prim("uv_sphere", CYAN_GLOW, part_h, radius=0.07, location=(0, 0, 0.18))
for k in range(8):
    x, y = pol(0.27, k / 8 * math.tau)
    add_prim("uv_sphere", BRASS, part_h, radius=0.022, location=(x, y, 0.05))
part_p = new_coll("part_pointer")
build_pointer(part_p, BRASS, RED_GLOW, 0.0, 0.0)

# lights, world, camera
sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.2; sun.color = (1.0, 0.86, 0.66); sun.angle = math.radians(4)
so = bpy.data.objects.new("sun", sun); link(so); so.rotation_euler = (math.radians(40), math.radians(-25), 0)
fill = bpy.data.lights.new("fill", "SUN"); fill.energy = 0.8; fill.color = (0.45, 0.6, 1.0)
fo = bpy.data.objects.new("fill", fill); link(fo); fo.rotation_euler = (math.radians(-50), math.radians(30), 0)
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.25, 0.3, 0.45, 1); bg.inputs["Strength"].default_value = 0.6

cd = bpy.data.cameras.new("cam"); cd.type = "ORTHO"
cam = bpy.data.objects.new("cam", cd); link(cam); scene.camera = cam
try:
    scene.render.engine = "BLENDER_EEVEE"
except TypeError as e:
    print("ENGINE", e)
scene.eevee.taa_render_samples = SAMPLES
if hasattr(scene.eevee, "use_raytracing"):
    scene.eevee.use_raytracing = True
scene.render.film_transparent = True
scene.render.image_settings.file_format = "PNG"; scene.render.image_settings.color_mode = "RGBA"
try:
    scene.view_settings.view_transform = "Standard"
except Exception:
    pass

ALL = {"player": [player, player_ptr], "enemy": [enemy, enemy_ptr], "part_wedge": [part_w], "part_hub": [part_h],
       "part_pointer": [part_p]}

def show_only(key):
    for k, colls in ALL.items():
        for c in colls:
            c.hide_render = (k != key)

def shoot(key, size, ortho, center, fname, tilt=0.0):
    show_only(key)
    scene.render.resolution_x = size; scene.render.resolution_y = size
    cd.ortho_scale = ortho
    cam.location = (center[0], center[1] - math.sin(tilt) * 10, math.cos(tilt) * 10)
    cam.rotation_euler = (tilt, 0, 0)
    scene.render.filepath = os.path.join(OUT, fname)
    bpy.ops.render.render(write_still=True)

shoot("player", 900, 2.9, (0, 0.12), "spinner_player.png")
shoot("enemy", 900, 2.9, (0, 0.12), "spinner_enemy.png")
shoot("part_wedge", 400, 1.25, (0.28, 0.58), "part_wedge.png", math.radians(25))
shoot("part_hub", 400, 0.9, (0, 0), "part_hub.png", math.radians(35))
shoot("part_pointer", 400, 0.75, (0, 0.03), "part_pointer.png", math.radians(20))
with open(os.path.join(OUT, "spinners.json"), "w") as f:
    json.dump({"ticks": TICKS, "ortho": 2.9, "center": [0, 0.12], "size": 900,
               "player": player_slices, "enemy": enemy_slices}, f)
print("DONE spinners")
