"""crop.py <src> <x0> <y0> <x1> <y1> <scale> <out>  -- nearest-neighbour enlarge a crop for inspection (gate1, read only on src)."""
import sys
from PIL import Image
src, x0, y0, x1, y1, s, out = sys.argv[1], *map(int, sys.argv[2:6]), float(sys.argv[6]), sys.argv[7]
im = Image.open(src)
try:
    im.seek(int(sys.argv[8]) if len(sys.argv) > 8 else 0)
except Exception:
    pass
im = im.convert('RGB').crop((x0, y0, x1, y1))
if s != 1:
    im = im.resize((int((x1 - x0) * s), int((y1 - y0) * s)), Image.NEAREST)
im.save(out)
print(out, im.size)
