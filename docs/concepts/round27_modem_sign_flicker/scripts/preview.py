"""Quick look: beauty .npy -> sRGB png (no post)."""
import sys
import numpy as np
from PIL import Image
a = np.load(sys.argv[1]).astype(np.float32)
a = np.clip(a, 0, 1)
a = np.where(a <= 0.0031308, a * 12.92, 1.055 * np.power(a, 1 / 2.4) - 0.055)
Image.fromarray((a * 255).astype(np.uint8)).save(sys.argv[2])
