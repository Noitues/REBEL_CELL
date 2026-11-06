"""crop.py <png> <x0> <y0> <x1> <y1> <out> [zoom]: save a crop (NEAREST zoom) for viewing"""
import sys
from PIL import Image
p, x0, y0, x1, y1, out = sys.argv[1], *[int(v) for v in sys.argv[2:6]], sys.argv[6]
z = int(sys.argv[7]) if len(sys.argv) > 7 else 1
im = Image.open(p).convert('RGB').crop((x0, y0, x1, y1))
if z != 1:
    im = im.resize((im.width * z, im.height * z), Image.NEAREST)
im.save(out)
print(out, im.size)
