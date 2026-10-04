"""Scratch inspection: python crop.py <image> x0 y0 x1 y1 [scale]  -> scratch/probe/crop.png"""
import os
import sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1]
x0, y0, x1, y1 = map(int, sys.argv[2:6])
k = float(sys.argv[6]) if len(sys.argv) > 6 else 2.0
im = Image.open(src)
if getattr(im, "is_animated", False) and len(sys.argv) > 7:
    im.seek(int(sys.argv[7]))
im = im.convert("RGB").crop((x0, y0, x1, y1))
im = im.resize((int(im.width * k), int(im.height * k)), Image.NEAREST if k >= 2 else Image.LANCZOS)
out = os.path.join(os.path.dirname(HERE), "scratch", "probe", "crop.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
im.save(out)
print(out, im.size)
