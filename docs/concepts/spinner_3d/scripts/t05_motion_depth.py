"""05 motion depth: depth sold by motion alone. The needle flap ticks on each slice peg and
drops its own shadow; the wheel overshoots and wobbles on the stop; motion blur is
rotational, so it is naturally stronger on the outer rim than near the hub."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

L.reset()
sc = L.setup((600, 600), samples=16, motion_blur=True)
cam = L.camera(3.3, -0.15)
L.backdrop(cam)
Z = {"slices": 0.0, "hp": 0.001, "bezel": 0.002, "hub": 0.003, "needle": 0.1}
objs = L.spinner_2d("op", "lit", z=Z, glow=1.6,
                    emit={"slices": 0.75, "hub": 0.8, "bezel": 0.4, "hp": 1.0, "needle": 1.0})
L.light("SUN", "key", (0, 0, 5), (1, 1, 1, 1), 1.3, rot=(-35, -25, 0), angle=3)
L.animate_spin(objs["slices"], objs["needle"], L.OP_TICKS)
L.render_seq("seq05")
