"""Quick look at a raw pass: python quick_view.py <stem> <out.png> [exposure]  (clip, gamma 2.2)."""
import sys
import numpy as np
from PIL import Image
a = np.load(sys.argv[1] + "_rgb.npy").astype(np.float32)
k = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
a = np.clip(a * k, 0, 1) ** (1 / 2.2)
Image.fromarray((a * 255).astype(np.uint8)).save(sys.argv[2])
print(a.shape, "median", float(np.median(a.mean(-1))))
