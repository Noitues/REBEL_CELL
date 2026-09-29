"""Probe Blender 5.2 APIs: engine ids, Grease Pencil v3 layout. Writes a tiny test PNG."""
import bpy, sys, os

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "probe.png"
scene = bpy.context.scene
print("ENGINE current", scene.render.engine)
try:
    scene.render.engine = "NOPE"
except TypeError as e:
    print("ENGINES", e)

gp = bpy.data.grease_pencils_v3.new("probe") if hasattr(bpy.data, "grease_pencils_v3") else bpy.data.grease_pencils.new("probe")
print("GP type", type(gp), [d for d in dir(gp) if not d.startswith("_")])
layer = gp.layers.new("L")
print("layer", [d for d in dir(layer) if not d.startswith("_")])
frame = layer.frames.new(1)
print("frame", [d for d in dir(frame) if not d.startswith("_")])
dr = frame.drawing
print("drawing", [d for d in dir(dr) if not d.startswith("_")])
dr.add_strokes([4])
st = dr.strokes[0]
print("stroke", [d for d in dir(st) if not d.startswith("_")])
pt = st.points[0]
print("point", [d for d in dir(pt) if not d.startswith("_")])
print("attrs", [a.name for a in dr.attributes])

ob = bpy.data.objects.new("gpob", gp)
scene.collection.objects.link(ob)
mat = bpy.data.materials.new("gpm")
bpy.data.materials.create_gpencil_data(mat)
print("gpstyle", [d for d in dir(mat.grease_pencil) if not d.startswith("_")])
mat.grease_pencil.color = (1, 0.2, 0.6, 1)
gp.materials.append(mat)
for i, p in enumerate(st.points):
    p.position = (i * 0.5 - 0.75, 0, (i % 2) * 0.5)
    p.radius = 0.05
    p.opacity = 1.0
# camera
cam = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cam); scene.collection.objects.link(co)
co.location = (0, -5, 0.25); co.rotation_euler = (1.5708, 0, 0); scene.camera = co
scene.render.resolution_x = 320; scene.render.resolution_y = 180
scene.render.filepath = out
print("view transforms", [i.identifier for i in scene.view_settings.bl_rna.properties["view_transform"].enum_items])
bpy.ops.render.render(write_still=True)
print("DONE", os.path.exists(out))
