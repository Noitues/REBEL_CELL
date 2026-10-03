"""Round 26: the betrayed MODEM sign. Recolours the locked round 4 sign (round4_modem_sign/sign_rgba.png, read-only)
to DISPATCH red: the pink tube and frame become signal red, the cyan CYBER SHOP text becomes a hot red-orange,
alpha untouched. Two letters of the plate are dimmed (a dying tube), seeded.
python red_sign.py -> ../../scratch/modem/sign_red.png
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "scratch", "modem")
SRC = os.path.join(HERE, "..", "..", "..", "round4_modem_sign", "sign_rgba.png")
os.makedirs(OUT, exist_ok=True)

a = np.asarray(Image.open(SRC).convert("RGBA"), np.float32) / 255
rgb, al = a[..., :3], a[..., 3:]
lum = rgb.max(axis=2, keepdims=True)
r, g, b = rgb[..., 0:1], rgb[..., 1:2], rgb[..., 2:3]
cyanish = np.clip((g + b) / 2 - r + 0.2, 0, 1)  # the cyan text / circuit traces
white = np.clip(rgb.min(axis=2, keepdims=True) * 2.0 - 0.5, 0, 1)  # hot tube cores stay hot (red reads darker than pink)
RED = np.array([1.0, 0.07, 0.08], np.float32)
ORG = np.array([1.0, 0.36, 0.20], np.float32)
col = RED * (1 - cyanish) + ORG * cyanish
out = col * lum
out = out * (1 - white) + np.array([1.0, 0.66, 0.60], np.float32) * white * lum
glowm = (al < 0.98) & (al > 0.0)  # the soft halo round the plate: a touch stronger
al = np.where(glowm, np.clip(al * 1.25, 0, 1), al)
h = out.shape[0]
# a dying tube: the D of MODEM flickers (dimmed to 40 %), the rest burns red
out[395:525, 120:270] *= 0.40
o = np.concatenate([np.clip(out, 0, 1), al], axis=2)
Image.fromarray((o * 255 + 0.5).astype(np.uint8), "RGBA").save(os.path.join(OUT, "sign_red.png"))
print("sign_red", o.shape)
