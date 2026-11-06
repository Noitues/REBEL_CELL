"""Silhouette checks per family at 24 and 32 px: worst-case pair overlap over rotations, solidity, pieces, motion delta.
usage: python metrics.py out.json"""
import json, sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
from shapes import *
from render import mask_at


def iou(a, b):
    return float(np.minimum(a, b).sum() / np.maximum(a, b).sum())


def opened(m, k=3):
    im = Image.fromarray((m > .5).astype(np.uint8) * 255)
    im = im.filter(ImageFilter.MinFilter(k)).filter(ImageFilter.MaxFilter(k))
    return np.asarray(im) > 127


res = {}
for fk, fam in FAMILIES.items():
    for size in (24, 32):
        ops = {t: fam['fn'](t, 0) for t in TYPES}
        r = {}
        al = {t: mask_at(ops[t], size, 0) for t in TYPES}
        for t in TYPES:
            m = al[t]
            r['area_' + t] = int((m > .5).sum())
            r['solid_' + t] = round(float(opened(m).sum() / max((m > .5).sum(), 1)), 2)
            r['pieces_' + t] = int(ndimage.label(m > .5)[1])
            m1 = mask_at(fam['fn'](t, 1), size, 0)
            r['motion_' + t] = round(1 - iou(m, m1), 3)  # 0 = frames identical at this size
        for a, b in (('D', 'N'), ('D', 'E'), ('N', 'E')):
            r[f'iouworst_{a}{b}'] = round(max(iou(al[a], mask_at(ops[b], size, ang)) for ang in range(0, 360, 15)), 2)
        r['iouworst_max'] = max(r['iouworst_DN'], r['iouworst_DE'], r['iouworst_NE'])
        res[f'{fk}_{size}'] = r
json.dump(res, open(sys.argv[1], 'w'), indent=1)
for k, v in res.items():
    print(k, v)
