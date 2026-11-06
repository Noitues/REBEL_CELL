"""crop1x.py <src> <out> x0 y0 x1 y1 [scale]: crop a region of an image (optionally scaled up) for looking"""
import sys
from PIL import Image
a = sys.argv
im = Image.open(a[1]).crop(tuple(int(v) for v in a[3:7]))
s = float(a[7]) if len(a) > 7 else 1.0
if s != 1.0:
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
im.save(a[2])
print(im.size)
