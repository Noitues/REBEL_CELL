"""Grid overlay for placing things: python grid.py <in> <x0> <y0> <x1> <y1> <out> <step>"""
import sys

from PIL import Image, ImageDraw

im = Image.open(sys.argv[1]).convert("RGB")
x0, y0, x1, y1 = map(int, sys.argv[2:6])
step = int(sys.argv[7])
c = im.crop((x0, y0, x1, y1))
d = ImageDraw.Draw(c)
for x in range((x0 // step + 1) * step, x1, step):
    d.line([(x - x0, 0), (x - x0, c.height)], fill=(255, 255, 0) if x % (step * 2) == 0 else (0, 255, 255), width=1)
    d.text((x - x0 + 2, 2), str(x), fill=(255, 255, 0))
for y in range((y0 // step + 1) * step, y1, step):
    d.line([(0, y - y0), (c.width, y - y0)], fill=(255, 255, 0) if y % (step * 2) == 0 else (0, 255, 255), width=1)
    d.text((2, y - y0 + 2), str(y), fill=(255, 255, 0))
c.save(sys.argv[6])
