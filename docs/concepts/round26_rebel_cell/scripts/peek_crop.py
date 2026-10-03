"""Round 26 helper: side-by-side crops for checking. python peek_crop.py out.png x0 y0 x1 y1 img1 [img2 ...]"""
import sys

from PIL import Image

out, x0, y0, x1, y1 = sys.argv[1], *map(int, sys.argv[2:6])
ims = [Image.open(p).convert("RGB") for p in sys.argv[6:]]
cr = [im.resize((1920, 1080)).crop((x0, y0, x1, y1)) if im.width != 1920 else im.crop((x0, y0, x1, y1)) for im in ims]
W = sum(c.width for c in cr)
o = Image.new("RGB", (W, cr[0].height))
x = 0
for c in cr:
    o.paste(c, (x, 0))
    x += c.width
o.save(out)
