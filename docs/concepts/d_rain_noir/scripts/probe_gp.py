# Probe: Blender 5.2 Grease Pencil v3 API + EEVEE headless + compositor node ids.
import bpy, sys, os
out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "probe.png"
sc = bpy.context.scene
print("ENGINE", sc.render.engine)
for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
    try:
        sc.render.engine = e; print("ENGINE OK", e); break
    except TypeError as ex:
        print("ENGINE ERR", ex)
gp = bpy.data.grease_pencils.new("probe") if hasattr(bpy.data, "grease_pencils") else None
print("GPDATA", type(gp), [a for a in dir(gp) if not a.startswith("_")])
layer = gp.layers.new("L")
print("LAYER", [a for a in dir(layer) if not a.startswith("_")])
fr = layer.frames.new(1)
print("FRAME", [a for a in dir(fr) if not a.startswith("_")])
dr = fr.drawing
print("DRAWING", [a for a in dir(dr) if not a.startswith("_")])
dr.add_strokes([4])
s = dr.strokes[0]
print("STROKE", [a for a in dir(s) if not a.startswith("_")])
p = s.points[0]
print("POINT", [a for a in dir(p) if not a.startswith("_")])
for i, pt in enumerate(s.points):
    pt.position = (i * 0.5 - 0.75, 0, (i % 2) * 0.5)
    pt.radius = 0.05
    pt.opacity = 1.0
mat = bpy.data.materials.new("gpm")
bpy.data.materials.create_gpencil_data(mat)
print("GPSTYLE", [a for a in dir(mat.grease_pencil) if not a.startswith("_")])
mat.grease_pencil.color = (1, 0.2, 0.6, 1)
gp.materials.append(mat)
ob = bpy.data.objects.new("gpo", gp)
sc.collection.objects.link(ob)
print("OBJ modifiers types", [i.identifier for i in bpy.types.Modifier.bl_rna.properties["type"].enum_items if "GREASE" in i.identifier][:40])
print("SHADERFX", [i.identifier for i in bpy.types.ShaderFx.bl_rna.properties["type"].enum_items])
# camera
cd = bpy.data.cameras.new("c"); co = bpy.data.objects.new("c", cd); sc.collection.objects.link(co)
co.location = (0, -5, 0.25); co.rotation_euler = (1.5708, 0, 0); sc.camera = co
sc.render.resolution_x = 320; sc.render.resolution_y = 180
sc.render.filepath = out
# compositor probe
print("HAS compositing_node_group", hasattr(sc, "compositing_node_group"))
print("HAS node_tree", hasattr(sc, "node_tree"))
ng_types = [t for t in dir(bpy.types) if t.startswith("CompositorNode")]
print("COMPNODES", ng_types)
print("EEVEE props", [a for a in dir(sc.eevee) if not a.startswith("_")])
bpy.ops.render.render(write_still=True)
print("WROTE", os.path.exists(out))
