"""crop.py <png> <x0> <y0> <x1> <y1> <scale> <out>   (nearest-neighbour zoom of a region, for looking at marks at 2x-5x)"""
import sys
from PIL import Image
sys.dont_write_bytecode = True
p, x0, y0, x1, y1, s, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
im = Image.open(p).convert('RGB').crop((x0, y0, x1, y1))
im.resize((im.width * s, im.height * s), Image.NEAREST).save(out)
print('ok', out, im.size)
