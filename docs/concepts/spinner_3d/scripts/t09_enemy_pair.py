"""09 operative vs enemy, both in the combination-8 treatment. The enemy wears a machined
bezel in its corp hue (Meridian orange, container stripes) with a notched hostile edge."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

L.reset()
sc = L.setup((1920, 1080), samples=48, bloom=(1.1, 0.55, 0.6))
cam = L.camera(6.6, -0.1, tilt_deg=14.0)
L.backdrop(cam, wide=True)
for side, cx in (("op", -1.62), ("en", 1.62)):
    parts = L.spinner_3d(side, center=(cx, 0.0), inlay_emit=0.85)
    L.dome(center=(cx, 0.0), z0=0.142, h=0.24, strength=0.9)
    parts["wheel"].rotation_euler.z = L.math.radians(-236 if side == "op" else -40)
    parts["needle"].rotation_euler.z = L.math.radians(3 if side == "op" else -2)
L.bpy.data.objects["dome"].name = "dome_op"
k = L.light("AREA", "key", (-3.0, 2.4, 4.0), (1, 0.97, 0.94, 1), 150.0, size=2.2)
k.data.specular_factor = 0.25
L.aim(k, (0, 0, 0))
L.neon_props(x_pink=-3.15, x_cyan=3.15, z=0.35, power=(260.0, 220.0))
for cx in (-1.62, 1.62):
    s = L.light("AREA", "spec", (cx - 3.2, 2.6, 1.6), (0.85, 0.93, 1.0, 1), 90.0, size=0.45)
    L.aim(s, (cx, 0, 0))
L.render(os.path.join(L.REN, "09_enemy_pair.png"))
