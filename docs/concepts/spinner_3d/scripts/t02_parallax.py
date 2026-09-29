"""02 parallax: outer ring, slices, hub and needle on separate planes; the pointer offset
slides them against each other. Flat (unlit) layers so parallax is the only depth cue."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

L.reset()
L.setup((1200, 1200), samples=24)
cam = L.camera(3.3, -0.15)
bd = L.backdrop(cam)
Z = {"slices": 0.0, "hp": 0.01, "bezel": 0.02, "hub": 0.03, "needle": 0.04}
objs = L.spinner_2d("op", "flat", z=Z, glow=1.6)
base = L.apply_parallax(objs, (0, 0))
for tag, p in (("a", (-1.0, 0.6)), ("b", (0.0, 0.0)), ("c", (1.0, -0.6))):
    L.apply_parallax(objs, p, base=base, backdrop_ob=bd)
    L.render(os.path.join(L.REN, f"02_parallax_{tag}.png"))
sc = L.bpy.context.scene
sc.render.resolution_x = sc.render.resolution_y = 600
sc.eevee.taa_render_samples = 12
N = 36
for i in range(N):
    L.apply_parallax(objs, L.orbit(i, N), base=base, backdrop_ob=bd)
    L.render(os.path.join(L.REN, "seq02", f"f{i:03d}.png"))
