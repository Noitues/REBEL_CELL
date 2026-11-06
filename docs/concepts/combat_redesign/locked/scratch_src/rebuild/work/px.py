"""px.py img r ang [r ang ...]: print RGB and L* at board polar points (C = 536, 540; angle from 12 o'clock clockwise)"""
import sys, math
import numpy as np
from PIL import Image
im = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
a = sys.argv[2:]
for i in range(0, len(a), 2):
    r, t = float(a[i]), math.radians(float(a[i + 1]))
    x, y = int(536 + r * math.sin(t)), int(540 - r * math.cos(t))
    p = im[y - 2:y + 3, x - 2:x + 3].reshape(-1, 3).mean(0)
    c = p / 255
    c = np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    Y = 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    L = 116 * Y ** (1 / 3) - 16 if Y > 0.008856 else 903.3 * Y
    print('r %5.0f a %5.0f xy (%d,%d) rgb %s L* %.1f' % (r, float(a[i + 1]), x, y, np.round(p).astype(int), L))
