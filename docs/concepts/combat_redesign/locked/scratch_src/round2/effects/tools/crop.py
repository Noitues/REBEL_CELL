"""crop.py <src> <x0> <y0> <x1> <y1> <out> [scale]: crop a published image (for viewing at 1x or zoomed)"""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
x0, y0, x1, y1 = [int(v) for v in sys.argv[2:6]]
c = im.crop((x0, y0, x1, y1))
s = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
if s != 1.0:
    c = c.resize((int(c.width * s), int(c.height * s)), Image.NEAREST if s > 1 else Image.LANCZOS)
c.save(sys.argv[6])
print(c.size)
