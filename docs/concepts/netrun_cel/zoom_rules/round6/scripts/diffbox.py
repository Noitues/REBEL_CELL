"""Usage: python diffbox.py a.png b.png : bounding box of differing pixels."""
import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(int)
d = np.abs(a - b).sum(axis=2) > 0
ys, xs = np.nonzero(d)
print("bbox x %d-%d y %d-%d count %d maxdiff %d" % (xs.min(), xs.max(), ys.min(), ys.max(), d.sum(), np.abs(a - b).max()))
