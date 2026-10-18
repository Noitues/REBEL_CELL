"""Synthetic fixtures for the NA-04 tests: tiny PNG captures and data objects generated in code."""
import os

import numpy as np
from PIL import Image

from netrun_art import io

PRODUCER_SRC = '''
from netrun_art import seeds


def produce(layout_seed):
    out = {"dressing": {"items": []}, "derive": {"layout_seed": str(layout_seed)}}
    for bid in ("1:1", "1:2", "2:1", "2:2"):
        g = seeds.splitmix64(seeds.art_seed(layout_seed, "dress", bid))
        out["dressing"]["items"].append({"bid": bid, "x": round(seeds.uniform(next(g)) * 100.0, 4),
                                         "n": next(g) % 1000})
    return out


def placements(layout_seed, rename=None):
    rename = rename or {}
    out = {}
    for bid in ("1:1", "1:2", "2:1", "2:2"):
        key = rename.get(bid, bid)
        g = seeds.splitmix64(seeds.art_seed(layout_seed, "place", key))
        out[key] = {"x": round(seeds.uniform(next(g)), 4)}
    return out
'''


def write_producer(folder) -> str:
    """Write the synthetic producer module; returns its spec string."""
    p = os.path.join(str(folder), "producer_mod.py")
    with open(p, "w", encoding="utf-8") as f:
        f.write(PRODUCER_SRC)
    return p + ":produce"


def gray_png(path, w, h, values_by_row):
    """Write a gray PNG; `values_by_row(y, h)` gives the 0..255 value of row y."""
    a = np.zeros((h, w, 3), np.uint8)
    for y in range(h):
        a[y, :, :] = values_by_row(y, h)
    Image.fromarray(a).save(path)


def good_rows(y, h):
    """32 % of rows dark (13), 1 % bright (242), the rest 36: median 0.141, under 0.10 about 0.32, over 0.85 about 0.01."""
    f = y / h
    if f < 0.32:
        return 13
    if f > 0.99:
        return 242
    return 36


def make_capture(folder, w=160, h=100, rows=good_rows, ids=None, capture=None):
    """Write beauty.png, optional id.png (array of class bytes) and capture.json into `folder`."""
    os.makedirs(str(folder), exist_ok=True)
    gray_png(os.path.join(str(folder), "beauty.png"), w, h, rows)
    if ids is not None:
        a = np.zeros(ids.shape + (3,), np.uint8)
        a[..., 0] = ids
        Image.fromarray(a).save(os.path.join(str(folder), "id.png"))
    if capture is not None:
        io.dump(capture, os.path.join(str(folder), "capture.json"))
    return str(folder)


def landmark_capture(folder, lum_in, lum_out=36, w=160, h=100, frac=0.3, capture=None):
    """Capture whose landmark (class 1) block has luma value `lum_in` over a class 2 background of `lum_out`."""
    ids = np.full((h, w), 2, np.uint8)
    bw, bh = int(w * frac), int(h * frac)
    x0, y0 = (w - bw) // 2, (h - bh) // 2
    ids[y0:y0 + bh, x0:x0 + bw] = 1
    a = np.full((h, w, 3), lum_out, np.uint8)
    a[y0:y0 + bh, x0:x0 + bw] = lum_in
    os.makedirs(str(folder), exist_ok=True)
    Image.fromarray(a).save(os.path.join(str(folder), "beauty.png"))
    a2 = np.zeros((h, w, 3), np.uint8)
    a2[..., 0] = ids
    Image.fromarray(a2).save(os.path.join(str(folder), "id.png"))
    if capture is not None:
        io.dump(capture, os.path.join(str(folder), "capture.json"))
    return str(folder)


def square(x0, y0, x1, y1):
    """Axis-aligned polygon."""
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def city_with(parts_by_bid, streets=None):
    """Minimal city.json-shaped dict from `{bid: [(poly, z0, h)]}`."""
    return {"version": 1, "layout_seed": "1", "units": "BU", "lot_bu": 6.0, "origin_lot": [6, 6],
            "buildings": [{"bid": b, "cell": [0, 0, 1, 1], "terr": "", "hq": False, "key": 1,
                           "parts": [{"poly": p, "z0": z, "h": h, "taper": 1.0} for p, z, h in parts]}
                          for b, parts in parts_by_bid.items()],
            "streets": streets or [], "plazas": [], "hqs": {}}
