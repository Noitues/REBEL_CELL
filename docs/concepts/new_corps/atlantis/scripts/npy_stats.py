"""Debug: linear stats of a render npy (per channel mean, median, p95) and of its top / middle / bottom thirds."""
import sys
import numpy as np

a = np.load(sys.argv[1]).astype(np.float32)[..., :3]
h = a.shape[0]
for name, sl in (("all", a), ("top", a[: h // 3]), ("mid", a[h // 3: 2 * h // 3]), ("bot", a[2 * h // 3:])):
    print(name, "mean", np.round(sl.reshape(-1, 3).mean(0), 4), "median", np.round(np.median(sl.reshape(-1, 3), 0), 4),
          "p95", np.round(np.percentile(sl.reshape(-1, 3), 95, axis=0), 3))
