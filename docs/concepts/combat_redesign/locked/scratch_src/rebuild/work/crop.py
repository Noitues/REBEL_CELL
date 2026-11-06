"""crop.py <src.png> <x0> <y0> <x1> <y1> <out.png> [scale]   crop a plate region (optionally scale with NEAREST for 1x pixel look)"""
import sys
from PIL import Image
src, x0, y0, x1, y1, out = sys.argv[1], *map(int, sys.argv[2:6]), sys.argv[6]
s = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
im = Image.open(src).convert('RGB').crop((x0, y0, x1, y1))
if s != 1.0:
    im = im.resize((int(im.width * s), int(im.height * s)), Image.NEAREST if s > 1 else Image.LANCZOS)
im.save(out)
