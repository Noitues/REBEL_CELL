"""NA-22 value-band stats of a capture PNG: median luma, share under 0.10, share over 0.85 and luma p99
(Rec.709 weights on sRGB-encoded values, as tools/netrun_art/checks/metrics.py).
Usage: python tools/city/na22_stats.py <png> [<png> ...]"""
import sys

import numpy as np
from PIL import Image


def stats(path: str) -> dict:
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64) / 255.0
    lum = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    return {"median": float(np.median(lum)), "under_010": float((lum < 0.10).mean()),
            "over_085": float((lum > 0.85).mean()), "p99": float(np.percentile(lum, 99))}


if __name__ == "__main__":
    for p in sys.argv[1:]:
        s = stats(p)
        print("%s median %.4f under0.10 %.1f%% over0.85 %.2f%% p99 %.3f" % (p, s["median"], s["under_010"] * 100, s["over_085"] * 100, s["p99"]))
