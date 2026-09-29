"""Probe the Blender 5.x Grease Pencil v3 + EEVEE + compositor API. Writes a test PNG.
Run: blender -b --factory-startup --python probe_api.py -- <out.png>
"""
import bpy, sys, math

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "probe.png"
print("VERSION", bpy.app.version_string)
sc = bpy.context.scene
for o in list(bpy.data.objects):
    bpy.data.objects.remove(o)
print("engine now", sc.render.engine)
try:
    sc.render.engine = "NOPE"
except TypeError as e:
    print("ENGINES", e)
sc.render.engine = "BLENDER_EEVEE"

gp = bpy.data.grease_pencils.new("probe") if hasattr(bpy.data, "grease_pencils") else None
print("gp type", type(gp), [a for a in dir(gp) if not a.startswith("_")])
ob = bpy.data.objects.new("probe", gp)
sc.collection.objects.link(ob)
layer = gp.layers.new("L")
print("layer", [a for a in dir(layer) if not a.startswith("_")])
fr = layer.frames.new(1)
print("frame", [a for a in dir(fr) if not a.startswith("_")])
dr = fr.drawing
print("drawing", [a for a in dir(dr) if not a.startswith("_")])
dr.add_strokes([8])
st = dr.strokes[0]
print("stroke", [a for a in dir(st) if not a.startswith("_")])
for i, p in enumerate(st.points):
    a = i / 7 * math.pi
    p.position = (math.cos(a), 0, math.sin(a))
    p.radius = 0.05
print("point", [a for a in dir(st.points[0]) if not a.startswith("_")])

mat = bpy.data.materials.new("gpmat")
bpy.data.materials.create_gpencil_data(mat)
print("gpstyle", [a for a in dir(mat.grease_pencil) if not a.startswith("_")])
mat.grease_pencil.color = (0, 1, 0.6, 1)
gp.materials.append(mat)

cam = bpy.data.cameras.new("cam")
cam.type = "ORTHO"; cam.ortho_scale = 4
co = bpy.data.objects.new("cam", cam); sc.collection.objects.link(co)
co.location = (0, -10, 0); co.rotation_euler = (math.pi / 2, 0, 0)
sc.camera = co
sc.render.resolution_x = 480; sc.render.resolution_y = 270
print("eevee props", [a for a in dir(sc.eevee) if not a.startswith("_")][:80])
print("scene has node_tree", hasattr(sc, "node_tree"), "compositing_node_group", hasattr(sc, "compositing_node_group"))
tree = bpy.data.node_groups.new("comp", "CompositorNodeTree")
print("comp node types sample")
try:
    g = tree.nodes.new("CompositorNodeGlare")
    print("glare inputs", [i.name for i in g.inputs], [a for a in dir(g) if not a.startswith("_")][-30:])
except Exception as e:
    print("glare err", e)
print("iface", [a for a in dir(tree.interface) if not a.startswith("_")])
print("world", bpy.context.scene.world)
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("DONE")
