# Probe: Blender 5.2 compositor node group API (Glare, Lens distortion, Defocus inputs).
import bpy
sc = bpy.context.scene
ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
sc.compositing_node_group = ng
for t in ("CompositorNodeRLayers", "CompositorNodeGlare", "CompositorNodeLensdist", "CompositorNodeDefocus", "CompositorNodeEllipseMask", "CompositorNodeBlur"):
    n = ng.nodes.new(t)
    print("NODE", t)
    print("  IN", [(s.name, s.type) for s in n.inputs])
    print("  OUT", [s.name for s in n.outputs])
    print("  PROPS", [p.identifier for p in n.bl_rna.properties if p.identifier not in bpy.types.Node.bl_rna.properties])
g = [n for n in ng.nodes if n.bl_idname == "CompositorNodeGlare"][0]
for s in g.inputs:
    if s.type == "MENU":
        print("MENU", s.name, s.default_value)
try:
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    o = ng.nodes.new("NodeGroupOutput"); print("GROUP OUTPUT OK", [s.name for s in o.inputs])
except Exception as e:
    print("ERR", e)
print("VIEW TRANSFORMS", [i.identifier for i in sc.view_settings.bl_rna.properties["view_transform"].enum_items])
print("LOOKS", [i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items][:30])
print("RENDER METHODS", [i.identifier for i in bpy.types.Material.bl_rna.properties["surface_render_method"].enum_items])
print("CURVE BODY FONT", hasattr(bpy.types.TextCurve, "body"))
print("LIGHTPROBE TYPES", [i.identifier for i in bpy.types.LightProbe.bl_rna.properties["type"].enum_items])
