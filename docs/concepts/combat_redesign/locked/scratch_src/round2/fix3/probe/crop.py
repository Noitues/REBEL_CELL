"""crop.py <src.png> <out.png> x0 y0 x1 y1 [scale]: a 1x (or scaled, NEAREST) crop for viewing"""
import sys
from PIL import Image
src, out = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(int, sys.argv[3:7])
s = int(sys.argv[7]) if len(sys.argv) > 7 else 1
im = Image.open(src).convert('RGB').crop((x0, y0, x1, y1))
if s != 1:
    im = im.resize((im.width * s, im.height * s), Image.NEAREST)
im.save(out)
print(out, im.size)
