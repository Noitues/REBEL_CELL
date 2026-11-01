"""Usage: python rows24.py <image> [<image> ...] : mean luminance of each 54 px row band (20 bands), to see where the light sits."""
import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
for p in sys.argv[1:]:
    im = Image.open(p).convert("RGB").resize((1920, 1080))
    a = np.asarray(im, dtype=np.float64) / 255.0
    l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    print(p.split("/")[-1], " ".join("%.2f" % l[i * 54:(i + 1) * 54].mean() for i in range(20)))
