"""python imgdiff.py a.png b.png  -> max abs diff (0..255) and the share of differing pixels."""
import sys

import numpy as np
from PIL import Image

sys.dont_write_bytecode = True
a = np.asarray(Image.open(sys.argv[1]).convert("RGB"), np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB"), np.int16)
if a.shape != b.shape:
    print("SHAPE", a.shape, b.shape)
    sys.exit(2)
d = np.abs(a - b)
print("max %d  differing %.6f  mean %.5f" % (d.max(), float((d.max(axis=2) > 0).mean()), float(d.mean())))
