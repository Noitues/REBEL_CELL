"""07 combo 4+5: the true 3D wheel, spun down with rotational motion blur, the physical
needle ticking on each divider with its real shadow, and a damped wobble on the stop."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sp_lib as L

L.reset()
sc = L.setup((600, 600), samples=16, motion_blur=True)
cam = L.camera(3.3, -0.15, tilt_deg=18.0)
L.backdrop(cam)
parts = L.spinner_3d("op")
L.studio_lights()
L.animate_spin(parts["wheel"], parts["needle"], L.OP_TICKS)
L.render_seq("seq07")
