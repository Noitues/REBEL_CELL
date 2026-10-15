"""Quick linear-pass stats of a render stem (debug): combined, emission and volume-direct luminance percentiles."""
import sys

import numpy as np

stem = sys.argv[1]
for k in ("combined", "emit", "voldir"):
    try:
        a = np.load(stem + "_" + k + ".npy").astype(np.float32)
    except FileNotFoundError:
        continue
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    print("%-9s mean %.4f p5 %.4f p50 %.4f p95 %.4f p99 %.4f" % (k, L.mean(), *np.percentile(L, (5, 50, 95, 99))))
