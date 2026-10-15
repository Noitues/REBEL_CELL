"""r3: fog_compare.jpg - r2 vs r3 crops of the sky and fog, plus round 1's spotlight crop for reference.

python fog_compare.py  ->  ../fog_compare.jpg (plates, no UI; each tile labelled with its sky-region luma stats)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

import ui31 as K  # noqa: E402

ROOT = os.path.dirname(HERE)
V3 = os.path.dirname(ROOT)
R2 = os.path.join(V3, "r2", "plates", "AAA2r2_plate.png")
R3 = os.path.join(ROOT, "plates", "AAA2r3_plate.png")
R1 = os.path.join(V3, "plates", "AAA2_realistic_night_plate.png")
SKY = (0, 0, 2560, 900)              # the sky and the fog above the route row
SPOT = (1560, 560, 2560, 1260)       # round 1's coloured cones round the TARGET column (the designer's reference)
LAYER_FOG = (0, 380, 1100, 1080)     # the left bank round the mid-row bases


def stats(im):
    a = np.asarray(im.convert("RGB"), np.float32) / 255
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    return "median %.3f  p95 %.2f  <0.10 %.0f %%" % (np.median(L), np.percentile(L, 95), (L < 0.1).mean() * 100)


def tile(path, box, w, label):
    im = Image.open(path).convert("RGB").crop(box)
    im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    out = Image.new("RGB", (w, im.height + 34), (10, 9, 14))
    out.paste(im, (0, 0))
    d = ImageDraw.Draw(out)
    d.text((8, im.height + 6), label, font=K.F(K.MONO, 18), fill=(212, 255, 0))
    d.text((w - 330, im.height + 8), stats(im), font=K.F(K.MONO, 15), fill=(190, 200, 220))
    return out


def main():
    rows = [[tile(R2, SKY, 1600, "r2  sky + fog (fog cards)")],
            [tile(R3, SKY, 1600, "r3  sky + fog (volumetric city fog, rule-placed beams)")],
            [tile(R1, SPOT, 790, "round 1  coloured cones (reference)"), tile(R3, SPOT, 790, "r3  same region")],
            [tile(R2, LAYER_FOG, 790, "r2  left, mid-row bases"), tile(R3, LAYER_FOG, 790, "r3  left: bank round the bases")]]
    W = 1620
    H = sum(max(t.height for t in r) + 10 for r in rows) + 10
    out = Image.new("RGB", (W, H), (10, 9, 14))
    y = 10
    for r in rows:
        x = 10
        for t in r:
            out.paste(t, (x, y))
            x += t.width + 20
        y += max(t.height for t in r) + 10
    out.save(os.path.join(ROOT, "fog_compare.jpg"), quality=90)
    print("saved fog_compare.jpg", out.size)


if __name__ == "__main__":
    main()
