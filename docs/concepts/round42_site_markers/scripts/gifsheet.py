"""Check helper: python gifsheet.py in.gif out.jpg [cols] -> every frame of a GIF on one sheet with its index and duration."""
import sys

from PIL import Image, ImageDraw, ImageSequence

src, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 5
g = Image.open(src)
frames = [(f.convert("RGB").copy(), f.info.get("duration", 0)) for f in ImageSequence.Iterator(g)]
w = 384
h = int(frames[0][0].height * w / frames[0][0].width)
rows = (len(frames) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (20, 20, 20))
d = ImageDraw.Draw(sheet)
for i, (f, du) in enumerate(frames):
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(f.resize((w, h)), (x, y))
    d.rectangle([x, y, x + 80, y + 16], fill=(0, 0, 0))
    d.text((x + 3, y + 2), "%d %dms" % (i, du), fill=(255, 255, 0))
sheet.save(out, quality=88)
print(len(frames), "frames")
