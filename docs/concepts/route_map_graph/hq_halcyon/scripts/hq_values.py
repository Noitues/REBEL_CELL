"""Value check against the r3 targets (sRGB luma, the critic's measure: Rec.709 weights as crit_stats.py):
median ~0.14, 25-40 % of pixels under 0.10, at most 2.5 % over 0.85.  python hq_values.py <png> [...]"""
import sys

import numpy as np
from PIL import Image

for p in sys.argv[1:]:
    a = np.asarray(Image.open(p).convert("RGB"), np.float32) / 255.0
    L = 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
    print("%-40s median %.3f  p95 %.3f  <0.10 %.1f %%  >0.85 %.2f %%" % (
        p.replace("\\", "/").split("/")[-1], np.median(L), np.percentile(L, 95), (L < 0.10).mean() * 100,
        (L > 0.85).mean() * 100))
