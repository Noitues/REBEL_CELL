"""Probe the Blender 5.2 compositor API (node groups) and Glare node inputs."""
import bpy
scene = bpy.context.scene
print("has compositing_node_group", hasattr(scene, "compositing_node_group"))
ng = bpy.data.node_groups.new("comp", "CompositorNodeTree")
print("ng interface", [d for d in dir(ng.interface) if not d.startswith("_")])
g = ng.nodes.new("CompositorNodeGlare")
print("glare inputs", [(i.name, i.type) for i in g.inputs])
print("glare props", [d for d in dir(g) if not d.startswith("_") and d not in dir(bpy.types.Node)])
for t in ("NodeGroupInput", "NodeGroupOutput", "CompositorNodeRLayers", "CompositorNodeComposite"):
    try:
        n = ng.nodes.new(t); print("ok", t, [o.name for o in n.outputs], [i.name for i in n.inputs])
    except Exception as e:
        print("fail", t, e)
try:
    scene.view_settings.view_transform = "Standard"; print("VT ok", scene.view_settings.view_transform)
except Exception as e:
    print("VT fail", e)
m = bpy.data.materials.new("m")
print("mat props", [d for d in ("surface_render_method", "blend_method", "use_transparent_shadow", "use_backface_culling", "shadow_method") if hasattr(m, d)])
print("rm enum", [i.identifier for i in m.bl_rna.properties["surface_render_method"].enum_items])
cam = bpy.data.cameras.new("c"); print("dof", [d for d in dir(cam.dof) if not d.startswith("_")])
