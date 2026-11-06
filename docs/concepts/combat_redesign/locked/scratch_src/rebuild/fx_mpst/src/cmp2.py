"""cmp2.py <a.png> <b.png>: max diff and bbox of differences"""
import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB'), np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB'), np.int16)
d = np.abs(a - b).max(2)
print('max', int(d.max()), 'px>8', int((d > 8).sum()), (lambda ys, xs: (xs.min(), ys.min(), xs.max(), ys.max()) if len(ys) else None)(*np.nonzero(d > 8)))
