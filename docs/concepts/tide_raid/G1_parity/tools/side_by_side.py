"""Final plate | Godot side by side at full size (3840 x 1080) and the squint pair (both at 320 px wide and at a 4 px blur).
usage: python side_by_side.py <plate.png> <godot.png> <out prefix> [label]   Written as a file (no python from stdin)."""
import sys

sys.dont_write_bytecode = True
from PIL import Image, ImageDraw, ImageFilter

plate, godot, prefix = sys.argv[1:4]
label = sys.argv[4] if len(sys.argv) > 4 else ""
p = Image.open(plate).convert("RGB")
g = Image.open(godot).convert("RGB")
if p.size != g.size:
    g = g.resize(p.size, Image.LANCZOS)
sbs = Image.new("RGB", (p.width * 2, p.height))
sbs.paste(p, (0, 0))
sbs.paste(g, (p.width, 0))
d = ImageDraw.Draw(sbs)
d.rectangle([0, 0, 360, 16], fill=(8, 8, 20))
d.text((4, 2), "plate  " + label, fill=(235, 235, 235))
d.rectangle([p.width, 0, p.width + 360, 16], fill=(8, 8, 20))
d.text((p.width + 4, 2), "godot (live city)  " + label, fill=(235, 235, 235))
sbs.save(prefix + "_side_by_side.png")
w = 320
h = int(p.height * w / p.width)
ps, gs = p.resize((w, h), Image.LANCZOS), g.resize((w, h), Image.LANCZOS)
pb, gb = p.filter(ImageFilter.GaussianBlur(4)).resize((w, h), Image.LANCZOS), g.filter(ImageFilter.GaussianBlur(4)).resize((w, h), Image.LANCZOS)
sq = Image.new("RGB", (w * 4, h))
for i, im in enumerate((ps, gs, pb, gb)):
    sq.paste(im, (i * w, 0))
sq.save(prefix + "_squint.png")
print("wrote", prefix + "_side_by_side.png", prefix + "_squint.png")
