"""01 physical stack: bezel ring on top, slice disc set lower, glass dome over all.
Each layer casts a soft shadow on the one below; the dome carries a specular highlight."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

L.reset()
L.setup((1200, 1200), samples=48)
cam = L.camera(3.3, -0.15)
L.backdrop(cam)
L.spinner_2d("op", "lit", z=L.STACK_Z, emit={"slices": 0.22, "hub": 0.45, "bezel": 0.12, "hp": 1.0, "needle": 1.0},
             glow=1.6)
L.dome(z0=0.18, h=0.2)
L.stack_lights(key=3.2)
L.render(os.path.join(L.REN, "01_physical_stack.png"))
