"""Probe 3: GP v3 fill strokes as occluders for GP lines (same object and across objects)."""
import bpy, sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv
out = sys.argv[sys.argv.index("--") + 1]
gv.reset((640, 360), samples=2)
gv.camera((0, -20, 0), (90, 0, 0), ortho_scale=10)
g = gv.GP("g", blend="REGULAR")
g.line([(-3, 2, 0.3), (3, 2, 0.3)], gv.col("phosphor"), 0.08)
g.line([(-3, -3, -0.3), (3, -3, -0.3)], gv.col("cyan"), 0.08)
g.line([(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1)], (0.3, 0, 0, 1), 0.01, cyclic=True, fill=(0.3, 0.0, 0.0, 1.0))
g.flush("x")
h = gv.GP("h", blend="ADD")
h.line([(-3, 3, 0.8), (3, 3, 0.8)], gv.col("magenta"), 0.08)
h.flush("y")
st = g.data.layers[0].frames[0].drawing.strokes[2]
print("FILL", st.material_index, tuple(st.fill_color), st.fill_opacity)
gv.render(out)
