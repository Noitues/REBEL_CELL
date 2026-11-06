"""px.py <png> x,y ... : print RGB and L* at points"""
import sys
import numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
def L(c):
    c = c / 255; c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    return 116 * np.cbrt(y) - 16 if y > 0.008856 else 903.3 * y
for a in sys.argv[2:]:
    x, y = map(int, a.split(','))
    c = im[y, x]
    print(a, tuple(int(v) for v in c), round(float(L(c)), 1))
