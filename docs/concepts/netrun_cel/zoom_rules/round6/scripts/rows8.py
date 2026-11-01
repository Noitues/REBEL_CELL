"""Usage: python rows8.py img [y0 y1 step]: row-mean luminance, fine."""
import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
im = np.asarray(Image.open(sys.argv[1]).convert("RGB"), dtype=np.float64) / 255.0
l = (0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]).mean(axis=1)
y0, y1, st = (int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (740, 920, 8)
print(" ".join("%d:%.2f" % (y, l[y:y + st].mean()) for y in range(y0, y1, st)))
