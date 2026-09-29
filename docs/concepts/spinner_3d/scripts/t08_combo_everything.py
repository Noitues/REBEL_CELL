"""08 everything, kept readable: the 3D wheel (4) under a glass dome (1), lit by the pink
sign and cyan tube (3), with a small camera orbit for parallax (2) and the ticking needle,
wobble and rim-weighted spin blur (5). Glyphs sit on an emissive inlay, never behind bloom."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

mode = (L.args() or ["all"])[0]
L.reset()
sc = L.setup((1200, 1200), samples=48, motion_blur=True, bloom=(1.1, 0.55, 0.6))
cam = L.camera(3.3, -0.15, tilt_deg=16.0)
L.backdrop(cam)
parts = L.spinner_3d("op", inlay_emit=0.85)
L.dome(z0=0.142, h=0.24, strength=0.9)
L.studio_lights(key=120.0, fills=(60.0, 50.0), key_spec=0.25)
L.neon_props(x_pink=-1.55, x_cyan=1.55, z=0.35, power=(170.0, 140.0))
spec = L.light("AREA", "spec", (-4.0, 3.4, 1.1), (0.85, 0.93, 1.0, 1), 70.0, size=0.4)
L.aim(spec, (0, 0, 0))
L.animate_spin(parts["wheel"], parts["needle"], L.OP_TICKS)
if mode in ("all", "hero"):
    L.orbit_camera(cam, 16.0, -6.0)
    sc.frame_set(L.SPIN_N)
    L.render(os.path.join(L.REN, "08_combo_everything.png"))
if mode in ("all", "seq"):
    sc.render.resolution_x = sc.render.resolution_y = 600
    sc.eevee.taa_render_samples = 16
    for f in range(1, L.SPIN_N + 1):
        u = (f - 1) / (L.SPIN_N - 1)
        L.orbit_camera(cam, 16.0 + 3.0 * L.math.sin(u * 2 * L.math.pi), -10.0 + 14.0 * u)
        sc.frame_set(f)
        L.render(os.path.join(L.REN, "seq08", f"f{f:03d}.png"))
