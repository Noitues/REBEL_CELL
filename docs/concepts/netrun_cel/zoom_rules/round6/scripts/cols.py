"""Usage: python cols.py img y0 y1 [seg]: mean luminance of rows y0..y1 per x segment."""
import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
im = np.asarray(Image.open(sys.argv[1]).convert("RGB"), dtype=np.float64) / 255.0
l = 0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]
y0, y1 = int(sys.argv[2]), int(sys.argv[3])
seg = int(sys.argv[4]) if len(sys.argv) > 4 else 160
print(" ".join("%d:%.2f" % (x, l[y0:y1, x:x + seg].mean()) for x in range(0, 1920, seg)))
