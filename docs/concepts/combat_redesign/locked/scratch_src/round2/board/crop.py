"""crop a box of a PNG, optionally scaled up (nearest).  python crop.py <png> <out> x0 y0 x1 y1 [scale]"""
import sys
sys.dont_write_bytecode = True
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = (int(v) for v in sys.argv[3:7])
s = int(sys.argv[7]) if len(sys.argv) > 7 else 1
im = Image.open(src).convert('RGB').crop((x0, y0, x1, y1))
if s > 1:
    im = im.resize((im.width * s, im.height * s), Image.NEAREST)
im.save(out)
print(out, im.size)
