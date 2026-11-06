"""Metrics: area, pieces, solidity, worst-case pair IoU over 24 rotations at 40/44/48 and 1280 sizes. python metrics6.py metrics.json"""
import json, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
from heads6 import *


def iou(a, b):
    return float(np.minimum(a, b).sum() / np.maximum(a, b).sum())


def opened(m, k=3):
    im = Image.fromarray((m > .5).astype(np.uint8) * 255)
    im = im.filter(ImageFilter.MinFilter(k)).filter(ImageFilter.MaxFilter(k))
    return np.asarray(im) > 127


res = {}
SIZES = [int(s) for s in sys.argv[2].split(",")] if len(sys.argv) > 2 else (27, 29, 32, 40, 44, 48)
for size in SIZES:
    r = {}
    ops = {t: head(t) for t in TYPES}
    al = {t: mask_at(ops[t], size, 0) for t in TYPES}
    for t in TYPES:
        m = al[t]
        r['area_' + t] = int((m > .5).sum())
        r['solid_' + t] = round(float(opened(m).sum() / max((m > .5).sum(), 1)), 2)
        r['pieces_' + t] = int(ndimage.label(m > .5)[1])
        # solidity of the hull: fill ratio inside the silhouette bbox
        ys, xs = np.nonzero(m > .5)
        from scipy.spatial import ConvexHull
        m0 = np.asarray(render_head(ops[t], size, 0, (255, 255, 255), ow=0, shade=False).split()[3], np.float32) / 255.0
        pts = np.argwhere(m0 > .5)
        r['fillarea_' + t] = int((m0 > .5).sum())
        r['hullfill_' + t] = round(float((m0 > .5).sum() / ConvexHull(pts).volume), 2)
        r['bbox_' + t] = [int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)]
    for a, b in (('D', 'N'), ('D', 'E'), ('N', 'E'), ('X', 'D'), ('X', 'N'), ('X', 'E')):
        r[f'iou_{a}{b}'] = round(max(iou(al[a], mask_at(ops[b], size, ang)) for ang in range(0, 360, 15)), 2)
    r['iou_main_max'] = max(r['iou_DN'], r['iou_DE'], r['iou_NE'])
    # motion delta frame 0 vs frame 1 (travel)
    for t in TYPES:
        r['motion_' + t] = round(1 - iou(al[t], mask_at(head(t, 1.0, 1.0), size, 0)), 3)
    res[str(size)] = r
json.dump(res, open(sys.argv[1], 'w'), indent=1)
for k, v in res.items():
    print(k, v)
