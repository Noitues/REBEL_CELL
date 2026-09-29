"""Smoke test for gv_lib + gv_font: vertex-coloured additive GP strokes, bloom, meshes."""
import bpy, sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gv_lib as gv, gv_font as gf

out = sys.argv[sys.argv.index("--") + 1]
gv.reset((960, 540), samples=4)
gv.camera((0, -20, 0), (90, 0, 0), ortho_scale=12)
gv.bloom(1.0, 0.2, 0.6)
g = gv.GP("t")
for pl in gf.layout("SEND IT 0101 MODEM", 0.8, origin=(-5.5, 2)):
    g.line([(x, 0, y) for x, y in pl], gv.col("phosphor"), 0.03)
rng = random.Random(1)
for pl, pr in gf.marker_hand("SEND IT", 1.6, rng, origin=(-4, -2.5)):
    g.line([(x, -1, y) for x, y in pl], gv.col("pink"), 0.12, radii=[0.12 * p for p in pr])
g.flush("a")
g.line([(math.cos(a / 20 * 6.283) * 2 + 3, 0, math.sin(a / 20 * 6.283) * 2 - 2) for a in range(20)],
       gv.col("cyan"), 0.02, cyclic=True, fill=gv.col("cyan", 0.2))
g.flush("b", blend="REGULAR")
gv.disc("glow", 2.5, gv.radial_glow_mat("gm", gv.col("magenta"), 1.5), loc=(3, 1, -2), rot=(math.pi / 2, 0, 0))
gv.render(out)
