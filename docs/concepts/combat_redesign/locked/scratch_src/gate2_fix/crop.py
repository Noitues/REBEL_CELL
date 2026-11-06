"""crop.py <png> <x0> <y0> <x1> <y1> <scale> <out>  : crop and enlarge (nearest) for inspection"""
import sys
from PIL import Image
p, x0, y0, x1, y1, s, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
im = Image.open(p).convert('RGB').crop((x0, y0, x1, y1))
im = im.resize((im.width * s, im.height * s), Image.NEAREST)
im.save(out)
