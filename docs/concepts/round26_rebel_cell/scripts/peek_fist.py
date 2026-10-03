"""Round 26 helper: draw the fist roads + street cells + buildings in LOT space (top-down) -> ../scratch/peek_fist.png"""
import json
import os

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
LAY = json.load(open(os.path.join(HERE, "..", "scratch", "layout", "rebel_cell_hq.json")))
S = 16
X0, Y0 = 0, 10
im = Image.new("RGB", (60 * S, 56 * S), (20, 20, 26))
d = ImageDraw.Draw(im)


def P(p):
    return ((p[0] - X0) * S, (p[1] - Y0) * S)


for t in LAY["tiles"]:
    d.polygon([P(p) for p in t["q"]], fill=(60, 60, 70))
for b in LAY["buildings"]:
    d.polygon([P(p) for p in b["q"]], outline=(120, 110, 140))
for s in LAY["fist"]:
    d.line([P(s["a"]), P(s["b"])], fill=(255, 40, 40), width=6)
for x in range(0, 60, 5):
    d.line([(x * S, 0), (x * S, 56 * S)], fill=(40, 40, 60))
    d.text((x * S + 2, 2), str(x + X0), fill=(200, 200, 200))
for y in range(0, 56, 5):
    d.line([(0, y * S), (60 * S, y * S)], fill=(40, 40, 60))
    d.text((2, y * S + 2), str(y + Y0), fill=(200, 200, 200))
c = LAY["centre"]
d.ellipse([P((c[0] - 0.5, c[1] - 0.5)), P((c[0] + 0.5, c[1] + 0.5))], fill=(0, 255, 0))
im.save(os.path.join(HERE, "..", "scratch", "peek_fist.png"))
print([(round(s["a"][0], 1), round(s["a"][1], 1), round(s["b"][0], 1), round(s["b"][1], 1)) for s in LAY["fist"]])
