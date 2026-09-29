"""Probe 2: GP v3 vs mesh depth with a default (Principled) material, and per-object options."""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv
out = sys.argv[sys.argv.index("--") + 1]
gv.reset((640, 360), samples=2)
gv.camera((0, -20, 0), (90, 0, 0), ortho_scale=10)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
g = gv.GP("g", blend="REGULAR")
g.line([(-3, 2, 0.3), (3, 2, 0.3)], gv.col("phosphor"), 0.08)
g.line([(-3, -3, -0.3), (3, -3, -0.3)], gv.col("cyan"), 0.08)
g.flush("x")
print("OBJ PROPS", [a for a in dir(g.obj) if "grease" in a.lower() or "front" in a.lower() or "depth" in a.lower()])
print("GP PROPS", [a for a in dir(g.data) if "depth" in a.lower()])
gv.render(out)
