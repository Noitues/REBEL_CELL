import sys
import numpy as np
from PIL import Image
for p in sys.argv[1:]:
    a = np.asarray(Image.open(p).convert("RGB")).astype(np.float32) / 255.0
    l = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    print("%s median %.3f mean %.3f  >0.95: %.2f%%  >0.85: %.2f%%  <0.05: %.1f%%" % (p, np.median(l), l.mean(), (l > 0.95).mean() * 100, (l > 0.85).mean() * 100, (l < 0.05).mean() * 100))
