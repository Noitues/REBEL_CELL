import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
a = np.asarray(Image.open(sys.argv[1]).convert("RGB"), dtype=np.float64)
h = a.shape[0]
y0 = int(sys.argv[2])
print("road share below y=%d: %.1f %%" % (y0, 100.0 * (h - y0) / h))
