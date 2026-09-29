"""03 normal-lit: the spinner stays a flat 2D sprite, but every layer carries a normal map
(baked from its height map) and is lit by the scene's glows: a pink sign on the left, a
cyan tube on the right, raking across the bevels. No shadows between layers, no offsets."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

L.reset()
L.setup((1200, 1200), samples=32)
cam = L.camera(3.3, -0.15)
L.backdrop(cam)
Z = {"slices": 0.0, "hp": 0.001, "bezel": 0.002, "hub": 0.003, "needle": 0.004}
L.spinner_2d("op", "lit", z=Z, glow=1.4, bump=1.0,
             emit={"slices": 0.3, "hub": 0.45, "bezel": 0.08, "hp": 0.9, "needle": 0.6})
L.neon_props(z=0.22, power=(170.0, 140.0))
L.render(os.path.join(L.REN, "03_normal_lit.png"))
