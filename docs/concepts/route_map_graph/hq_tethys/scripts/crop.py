"""hq_tethys: crop (and optionally upscale) a region for review. python crop.py <in> <out> x0 y0 x1 y1 [scale]"""
import sys

from PIL import Image

im = Image.open(sys.argv[1])
x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])
k = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
c = im.crop((x0, y0, x1, y1))
if k != 1.0:
    c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
c.save(sys.argv[2])
