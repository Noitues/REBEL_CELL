"""Usage: python rows.py <image> : row-mean luminance every 24 px (to see where the band peaks)."""
import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
im = np.asarray(Image.open(sys.argv[1]).convert("RGB"), dtype=np.float64) / 255.0
l = (0.2126 * im[..., 0] + 0.7152 * im[..., 1] + 0.0722 * im[..., 2]).mean(axis=1)
print(" ".join("%d:%.2f" % (y, l[y:y + 24].mean()) for y in range(240, 1080, 24)))
