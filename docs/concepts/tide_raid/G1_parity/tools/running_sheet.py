"""The running sheet: every iteration capture as a labelled thumbnail with its parity score, next to the plate and the city-only target.
usage: python running_sheet.py <runs dir> <sheets dir> <out.jpg> <plate.png> <target.png> iter_name ...   Written as a file (no python from stdin)."""
import json
import os
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw

runs, sheets, out, plate, target = sys.argv[1:6]
names = sys.argv[6:]
TW, TH = 480, 270
cols = 4
items = [("plate 01 (reference)", plate, None), ("city-only target (plate pipeline, no beams / UI)", target, None)]
for n in names:
    m = json.load(open(os.path.join(sheets, n + "_metrics.json")))
    a = m["godot"]["all"]
    items.append(("%s  score %.3f  luma %.3f warm %.2f lights %d" % (n, m["score"], a["luma"], a["warm"], a["light_points"]), os.path.join(runs, n + ".png"), m))
rows = (len(items) + cols - 1) // cols
sheet = Image.new("RGB", (cols * TW, rows * (TH + 16)), (8, 8, 20))
d = ImageDraw.Draw(sheet)
for i, (label, path, _) in enumerate(items):
    im = Image.open(path).convert("RGB").resize((TW, TH), Image.LANCZOS)
    x, y = (i % cols) * TW, (i // cols) * (TH + 16)
    sheet.paste(im, (x, y + 16))
    d.text((x + 3, y + 2), label[:78], fill=(235, 235, 235))
sheet.save(out, quality=88)
print("wrote", out, len(items), "tiles")
