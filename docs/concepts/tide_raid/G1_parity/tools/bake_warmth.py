"""Bakes the plates district warmth field (p2_grade.warmth_field: 0 cool teal, 1 warm sodium) to a texture the city post reads in world space.
The field is defined over the plate camera frame (zoom 1.5 about plate px (722, 500), ortho 394.59 BU); the shader maps a ground footprint back to that frame.
usage: python bake_warmth.py <out.png>   Written as a file (no python from stdin)."""
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts")
import numpy as np
from PIL import Image
import p2_grade as G

w = G.warmth_field()
im = Image.fromarray((np.clip(w, 0, 1) * 255 + .5).astype(np.uint8)).resize((960, 540), Image.LANCZOS)
im.save(sys.argv[1])
print("baked", sys.argv[1], w.mean())
