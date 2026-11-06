"""cmp2.py <a> <b>: pixel difference stats of two images."""
import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(int)
if a.shape != b.shape:
    print('shape', a.shape, b.shape); sys.exit()
d = np.abs(a - b).max(-1)
print('max %d px>8 %d mean %.4f' % (d.max(), int((d > 8).sum()), d.mean()))
