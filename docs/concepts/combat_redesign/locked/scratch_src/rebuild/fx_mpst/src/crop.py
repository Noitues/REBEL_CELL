"""crop.py <png> <x0> <y0> <x1> <y1> <scale> <out>: nearest/lanczos zoom crop for looking at details."""
import sys
from PIL import Image
im = Image.open(sys.argv[1]).convert('RGB')
x0, y0, x1, y1 = [int(v) for v in sys.argv[2:6]]
s = float(sys.argv[6])
c = im.crop((x0, y0, x1, y1))
c = c.resize((int(c.width * s), int(c.height * s)), Image.LANCZOS if s < 1 else Image.NEAREST)
c.save(sys.argv[7])
print('ok', c.size)
