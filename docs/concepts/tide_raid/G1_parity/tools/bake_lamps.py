"""Bakes the plates street-lamp lattice (p2_grade.lamp_field: a jittered world lattice, 9 BU cells) to a texture, so the city post places exactly the same lamps:
the plates hash (sin * 43758.5453 in float64) is not reproducible in float32 shaders. One texel per cell, cell index -128..127 on both axes:
R = x jitter (0..1), G = z jitter (0..1), B = lamp on (255) or off (0). usage: python bake_lamps.py <out.png>   Written as a file (no python from stdin)."""
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image

N = 256
OFF = 128


def rh(a, b):
    return np.mod(np.sin(a * 127.1 + b * 311.7) * 43758.5453, 1.0)


cx, cz = np.meshgrid(np.arange(-OFF, OFF), np.arange(-OFF, OFF), indexing="xy")
jx = rh(cx, cz)
jz = rh(cz, cx + 7)
on = rh(cx + 3, cz + 5) > 0.72
img = np.zeros((N, N, 3), np.uint8)
img[..., 0] = np.round(jx * 255)
img[..., 1] = np.round(jz * 255)
img[..., 2] = on * 255
# row = cell z index + OFF, column = cell x index + OFF
Image.fromarray(img).save(sys.argv[1])
print("baked", sys.argv[1], "lamps on", on.mean())
