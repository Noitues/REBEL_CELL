"""Crop helper for looking at plates: python crop.py <in> <x0> <y0> <x1> <y1> <out> [scale]"""
import sys

from PIL import Image

im = Image.open(sys.argv[1]).convert("RGB")
x0, y0, x1, y1 = map(int, sys.argv[2:6])
c = im.crop((x0, y0, x1, y1))
if len(sys.argv) > 7:
    k = float(sys.argv[7])
    c = c.resize((int(c.width * k), int(c.height * k)), Image.LANCZOS)
c.save(sys.argv[6])
