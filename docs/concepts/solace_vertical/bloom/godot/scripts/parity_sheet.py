"""parity_A.jpg: the concept targets (A3d_*) above, the Godot frozen captures below, labelled; plus the bloom-off diff numbers.

python parity_sheet.py <godot_dir> <out.jpg> [diff_json]
godot_dir holds street_creeping.png street_close.png street_catching.png hq_overview.png hq_decision.png (1920x1080).
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
T = r"D:/rc_art/art-pass/docs/concepts/solace_vertical/bloom"
G = sys.argv[1]
OUT = sys.argv[2]
DIFF = json.load(open(sys.argv[3])) if len(sys.argv) > 3 and os.path.exists(sys.argv[3]) else {}
W, H, PAD, LAB = 640, 360, 8, 22
cols = [("street_creeping", "STREET CREEPING gap 2.5"), ("street_close", "STREET CLOSE gap 1.25"), ("street_catching", "STREET CATCHING gap 0.6")]
hq = [("hq_overview", "HQ overview floor 9 of 27 (CATCHING)"), ("hq_decision", "HQ decision +2 floors (CLOSE)")]
try:
    font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
    big = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", 18)
except OSError:
    font = big = ImageFont.load_default()


def load(path):
    if not os.path.exists(path):
        im = Image.new("RGB", (W, H), (40, 0, 0))
        ImageDraw.Draw(im).text((10, 10), "missing " + os.path.basename(path), fill=(255, 120, 120), font=font)
        return im
    return Image.open(path).convert("RGB").resize((W, H), Image.LANCZOS)


rows = [("TARGET (Blender Cycles, A3d_*)", T, "A3d_", cols), ("GODOT (frozen --reduce-effects=1, plate camera)", G, "", cols),
        ("TARGET (Blender Cycles, A3d_*)", T, "A3d_", hq), ("GODOT (frozen --reduce-effects=1, plate camera)", G, "", hq)]
n = len(rows)
sheet = Image.new("RGB", (3 * W + 4 * PAD, n * (H + LAB) + (n + 1) * PAD + 60), (14, 10, 22))
d = ImageDraw.Draw(sheet)
d.text((PAD, PAD), "SOLACE THE BLOOM A Necrosis: Godot port parity. Target above, Godot below.   " + DIFF.get("note", ""), fill=(255, 90, 160), font=big)
y = 40
for ri, (lab, base, pre, items) in enumerate(rows):
    for ci, (key, name) in enumerate(items):
        x = PAD + ci * (W + PAD)
        d.text((x, y), "%s | %s" % (lab.split(" (")[0], name), fill=(200, 200, 220), font=font)
        sheet.paste(load(os.path.join(base, pre + key + ".png")), (x, y + LAB))
    y += H + LAB + PAD
sheet.save(OUT, quality=90)
print(OUT, sheet.size)
