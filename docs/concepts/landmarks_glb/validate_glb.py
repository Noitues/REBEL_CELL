"""Headless Blender: import every landmark .glb and print vertices, bounds and the custom attributes.
blender -b --factory-startup --python validate_glb.py"""
import glob
import os

import bpy

here = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "."
for p in sorted(glob.glob(os.path.join(here, "*_landmark.glb"))):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=p)
    nv = 0
    lo, hi = [1e9] * 3, [-1e9] * 3
    names = set()
    for o in bpy.context.scene.objects:
        if o.type != "MESH":
            continue
        nv += len(o.data.vertices)
        names.update(a.name for a in o.data.attributes)
        for v in o.data.vertices:
            w = o.matrix_world @ v.co
            for i in range(3):
                lo[i], hi[i] = min(lo[i], w[i]), max(hi[i], w[i])
    print("GLB", os.path.basename(p), "verts", nv, "bounds_z_up", [round(v, 1) for v in lo], [round(v, 1) for v in hi],
          "attrs", sorted(n for n in names if not n.startswith(".")), flush=True)
