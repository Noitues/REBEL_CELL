"""hq_tethys: a quick look at a render's linear rgb npy (preview only, not the post).
python quick_png.py <stem_rgb.npy> <out.png> [exposure]"""
import sys

import numpy as np
from PIL import Image

a = np.load(sys.argv[1]).astype(np.float32)
k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
x = a * k
x = x / (1 + x)
x = np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(np.clip(x, 0, None), 1 / 2.4) - 0.055)
Image.fromarray((np.clip(x, 0, 1) * 255 + 0.5).astype(np.uint8)).save(sys.argv[2])
