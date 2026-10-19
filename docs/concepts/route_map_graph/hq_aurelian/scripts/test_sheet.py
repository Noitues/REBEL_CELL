"""Aurelian HQ: the test frames (composites with the route UI) + their values on one <= 1280 px JPEG.

python test_sheet.py <test dir> <out.jpg>
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

SRC, OUT = sys.argv[1], sys.argv[2]
NAMES = ["H_overview", "H_decision", "H_decision_inner", "H_hover"]
V = json.load(open(os.path.join(SRC, "values.json")))


def font(sz, bold=False):
    for f in (("consolab.ttf" if bold else "consola.ttf"), ("arialbd.ttf" if bold else "arial.ttf")):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            continue
    return ImageFont.load_default()


W, H, TOP, CAP = 636, 358, 34, 24
sheet = Image.new("RGB", (2 * W + 8, TOP + 2 * (H + CAP) + 4), (12, 12, 16))
d = ImageDraw.Draw(sheet)
d.text((6, 8), "AURELIAN HQ v2 (outside-in route, Roman arcade): Cycles finals 2560 x 1440, 64 spp, shown at 636 px (mock route)",
       fill=(214, 178, 104), font=font(17, True))
for k, n in enumerate(NAMES):
    im = Image.open(os.path.join(SRC, n + ".png")).convert("RGB").resize((W, H), Image.LANCZOS)
    x, y = 2 + (k % 2) * (W + 4), TOP + (k // 2) * (H + CAP)
    sheet.paste(im, (x, y))
    v = V[n]
    txt = "%s  median %.3f  <0.10 %.0f%%  >0.85 %.1f%%  landmark/bg %.3f/%.3f = %.2f" % (
        n, v["median"], 100 * v["under_010"], 100 * v["over_085"], v["landmark"], v["local_bg"], v["ratio"])
    d.text((x + 2, y + H + 4), txt, fill=(225, 225, 230), font=font(13))
sheet.save(OUT, quality=85)
print("saved", OUT, sheet.size)
