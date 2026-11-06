"""Objective silhouette checks per family at 24 and 32 px: confusability between types, solidity (survives a 3 px opening), fragments.
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
        ops = {t: fam['fn'](t) for t in TYPES}
        r = {}
        al = {t: mask_at(ops[t], size, 0) for t in TYPES}
        for t in TYPES:
            m = al[t]
            r['area_' + t] = int((m > .5).sum())
            r['solid_' + t] = round(float(opened(m).sum() / max((m > .5).sum(), 1)), 2)
            r['pieces_' + t] = int(ndimage.label(m > .5)[1])
        for a, b in (('D', 'N'), ('D', 'E'), ('N', 'E')):
            r[f'iou_{a}{b}'] = round(iou(al[a], al[b]), 2)
            r[f'iouworst_{a}{b}'] = round(max(iou(al[a], mask_at(ops[b], size, ang)) for ang in range(0, 360, 15)), 2)
        res[f'{fk}_{size}'] = r
json.dump(res, open(sys.argv[1], 'w'), indent=1)
for k, v in res.items():
    print(k, v)
