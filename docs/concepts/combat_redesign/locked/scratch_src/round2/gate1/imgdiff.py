"""gate1: pixel diff of two images (max channel abs diff): px > 0, px > 2, max, bbox of differing px.  usage: imgdiff.py a.png b.png"""
import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.int16)
if a.shape != b.shape:
    print('shape differs', a.shape, b.shape); sys.exit()
d = np.abs(a - b).max(-1)
ys, xs = np.nonzero(d > 0)
print('px>0 %d px>2 %d max %d bbox %s' % ((d > 0).sum(), (d > 2).sum(), d.max(), (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else None))
