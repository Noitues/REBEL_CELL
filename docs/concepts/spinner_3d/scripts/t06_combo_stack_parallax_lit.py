"""06 combo 1+2+3: stacked layers with real shadows and a glass dome, normal-lit by the
pink sign and cyan tube, and parallax-shifted by the pointer offset."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

L.reset()
sc = L.setup((1200, 1200), samples=40)
cam = L.camera(3.3, -0.15)
bd = L.backdrop(cam)
objs = L.spinner_2d("op", "lit", z=L.STACK_Z, glow=1.5, bump=1.0,
                    emit={"slices": 0.3, "hub": 0.45, "bezel": 0.08, "hp": 0.9, "needle": 0.8})
objs["dome"] = L.dome(z0=0.18, h=0.2)
L.stack_lights(key=1.6, spec=110.0)
L.neon_props(z=0.3, power=(150.0, 120.0))
base = L.apply_parallax(objs, (0, 0))
for tag, p in (("a", (-1.0, 0.6)), ("b", (0.0, 0.0)), ("c", (1.0, -0.6))):
    L.apply_parallax(objs, p, base=base, backdrop_ob=bd)
    L.render(os.path.join(L.REN, f"06_combo_{tag}.png"))
sc.render.resolution_x = sc.render.resolution_y = 600
sc.eevee.taa_render_samples = 14
N = 36
for i in range(N):
    L.apply_parallax(objs, L.orbit(i, N), base=base, backdrop_ob=bd)
    L.render(os.path.join(L.REN, "seq06", f"f{i:03d}.png"))
