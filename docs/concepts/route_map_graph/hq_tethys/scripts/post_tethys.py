"""hq_tethys: the AAA-2 post (city_all_corps post_city.aaa, unchanged: black point, exposure solved to the r3 median
0.14, bloom, shoulder, toe search, vignette) + value checks + the landmark rule (HQ peak vs its local background).

python post_tethys.py <stem> <out.png>            stem = <outdir>/<cam>_aaa (reads <stem>_rgb.npy, <stem>_rooms.json)
"""
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
import tethys_preset as TP  # noqa: E402

sys.path.insert(1, TP.CITY_SCRIPTS)
import post_city as PC  # noqa: E402


def landmark_ratio(png, rooms_json, r_frac=0.075):
    """The 2x rule: the HQ's peak luma (99th percentile inside a disc round the station centre + crown) against the
    median luma of the ring round it (r .. 2.2 r)."""
    img = np.asarray(Image.open(png).convert("RGB")).astype(np.float32) / 255.0
    l = PC.luma(img)
    R = json.load(open(rooms_json))
    h, w = l.shape
    c = R["centre"]
    k = R["crown"]
    cx, cy = (c[0] + k[0]) / 2, (c[1] + k[1]) / 2
    r = r_frac * w
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot(xx - cx, yy - cy)
    inner = l[d < r]
    ring = l[(d >= r) & (d < 2.2 * r)]
    peak = float(np.percentile(inner, 99))
    mean_in = float(inner.mean())
    bg = float(np.median(ring))
    return dict(hq_peak=round(peak, 3), hq_mean=round(mean_in, 3), local_bg=round(bg, 3), ratio_peak=round(peak / max(bg, 1e-3), 2),
                ratio_mean=round(mean_in / max(bg, 1e-3), 2))


if __name__ == "__main__":
    stem, out = sys.argv[1], sys.argv[2]
    img, st = PC.aaa(stem, out)
    lr = landmark_ratio(out, stem + "_rooms.json")
    st.update(lr)
    print("VALUES", {k: (round(v, 4) if isinstance(v, float) else v) for k, v in st.items()})
    json.dump(st, open(os.path.splitext(out)[0] + "_values.json", "w"), indent=1)
