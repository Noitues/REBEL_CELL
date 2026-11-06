"""Bakes the plates Blender light-spill layer (the blue ambient and light bleed of the city, P3 'plan' beat) to a texture over the plate camera frame, for the city post
to add in world space (same frame mapping as the warmth map). Encoded: value = (min(spill, 2) / 2) ^ (1 / 2.2) per channel, 8 bit.
usage: python bake_spill.py <out.png>   Written as a file (no python from stdin)."""
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, "D:/rc_art/art-pass/docs/concepts/tide_raid/P3_plates/scripts")
import numpy as np
from PIL import Image
import p1_comp as C

s = C.layers("plan", passes=("spill",))["spill"][..., :3]
enc = (np.clip(s, 0, 2) / 2.0) ** (1 / 2.2)
Image.fromarray((enc * 255 + .5).astype(np.uint8)).save(sys.argv[1])
print("baked", sys.argv[1], s.mean((0, 1)))
