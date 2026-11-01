import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(np.int16)
d = (np.abs(a - b).max(axis=2) > 0).sum()
print("differing pixels: %d shape %s %s" % (d, a.shape, b.shape))
