"""NA-11c sky share of a capture PNG: the share of the frame above the first built-mass row of each column (the `sky_*`
definition of tools/netrun_art/checks/metrics.py `skyline`, composition.json constants, whole frame).
Usage: python tools/city/na11c_sky.py <png> [<png> ...]   (run from the repo root)"""
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from netrun_art.checks import metrics as M  # noqa: E402

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "netrun_art", "checks", "composition.json")


def sky_share(path: str) -> float:
    """Mean over columns of (rows above the first built row) / frame height."""
    k = json.load(open(HERE, encoding="utf-8"))["checks"]["composition"]["constants"]
    a = np.asarray(Image.open(path).convert("RGB"), dtype=np.float32) / 255.0
    L = a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722
    h, w = L.shape
    loc_std = np.sqrt(np.maximum(M.box_blur(L * L, 3) - M.box_blur(L, 3) ** 2, 0))
    built = (loc_std > k["built_std"])
    run = M.box_blur(built.astype(np.float32), 5) > k["built_run"]
    first = np.where(run.any(0), run.argmax(0), h)
    r = int(k["profile_median"]) // 2
    pad = np.pad(first / h, r, mode="edge")
    prof = np.median(np.stack([pad[i:i + w] for i in range(int(k["profile_median"]))]), 0)
    return float(prof.mean())


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print("%s sky share %.1f%%" % (p, sky_share(p) * 100))
