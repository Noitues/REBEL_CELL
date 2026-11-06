"""ringprof.py <png> ang: luma profile along the radius at one angle (deg, 0 = 12 o'clock, clockwise), r 262-290"""
import sys, math
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float)
l = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
ang = math.radians(float(sys.argv[2]))
out = []
for r10 in range(2620, 2900, 10):
    r = r10 / 10.0
    x, y = 536 + r * math.sin(ang), 540 - r * math.cos(ang)
    out.append('%d:%d' % (r, l[int(round(y)), int(round(x))]))
print(sys.argv[2], ' '.join(out))
