"""lumgrid.py <png> x y [r]: luma (0-255) grid around a pixel, and the rgb of the centre"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
png, x, y = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
r = int(sys.argv[4]) if len(sys.argv) > 4 else 6
a = np.asarray(Image.open(png).convert('RGB')).astype(float)
l = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
for yy in range(y - r, y + r + 1):
    print('%4d ' % yy + ' '.join('%3d' % l[yy, xx] for xx in range(x - r, x + r + 1)))
print('centre rgb', a[y, x])
