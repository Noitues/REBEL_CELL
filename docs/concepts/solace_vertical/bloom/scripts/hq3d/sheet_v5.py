"""v5 sheet: v4 (left) vs v5 (right) per camera, 2560 px wide. python sheet_v5.py"""
import os

from PIL import Image, ImageDraw, ImageFont

HQ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4 = os.path.join(HQ, "..", "..", "route_map_graph", "hq_solace", "plates")
CAMS = ("overview", "decision", "hover")
W = 2560
CW = (W - 30) // 2
CH = int(CW * 9 / 16)
LAB = 38
im = Image.new("RGB", (W, 3 * (CH + LAB) + 10), (10, 10, 12))
d = ImageDraw.Draw(im)
try:
    f = ImageFont.truetype("arial.ttf", 26)
except OSError:
    f = ImageFont.load_default()
for r, c in enumerate(CAMS):
    y = r * (CH + LAB) + 4
    for k, (nm, path) in enumerate((("v4 (golden plate)", os.path.join(V4, "H_%s_v4_plate.png" % c)),
                                    ("v5 (lime helix, park + plinth)", os.path.join(HQ, "H_%s_v5.png" % c)))):
        x = k * (CW + 30)
        d.text((x + 8, y + 4), "%s  %s" % (c.upper(), nm), fill=(220, 235, 220), font=f)
        t = Image.open(path).convert("RGB").resize((CW, CH), Image.LANCZOS)
        im.paste(t, (x, y + LAB))
im.save(os.path.join(HQ, "sheet_v5.jpg"), quality=90)
print("sheet", im.size)
