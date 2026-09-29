"""Probe: does an opaque mesh hide GP v3 strokes behind it in EEVEE? (per layer blend mode)"""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv

out = sys.argv[sys.argv.index("--") + 1]
gv.reset((640, 360), samples=2)
gv.camera((0, -20, 0), (90, 0, 0), ortho_scale=10)
m = gv.emit_mat("void", (0.2, 0.0, 0.0, 1), 1.0, 1.0, additive=False)
gv.mesh_from("box", [(-1, -1, -1), (1, -1, -1), (1, -1, 1), (-1, -1, 1)], [(0, 1, 2, 3)], m)
for i, bl in enumerate(["REGULAR", "ADD"]):
    g = gv.GP("g%d" % i, blend=bl)
    z = 0.5 - i
    g.line([(-3, 2, z), (3, 2, z)], gv.col("phosphor"), 0.08)   # behind the box (y=2 > -1)
    g.line([(-3, -3, z - 0.25), (3, -3, z - 0.25)], gv.col("cyan"), 0.08)  # in front
    g.flush(bl)
    print("depth order", g.data.stroke_depth_order)
gv.render(out)
