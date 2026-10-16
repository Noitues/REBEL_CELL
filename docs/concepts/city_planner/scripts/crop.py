import sys
from PIL import Image
src, x0, y0, x1, y1, out = sys.argv[1], *map(float, sys.argv[2:6]), sys.argv[6]
im = Image.open(src)
s = im.width / 1000
c = im.crop((int(x0 * s), int(y0 * s), int(x1 * s), int(y1 * s)))
c.save(out)
print(c.size)
