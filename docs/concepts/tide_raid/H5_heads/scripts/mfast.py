"""fast iou check at 24 px for chosen families: python mfast.py T1 T2 ..."""
import sys
from shapes_h5 import *
from render import mask_at
import numpy as np


def iou(a, b):
    return float(np.minimum(a, b).sum() / np.maximum(a, b).sum())


for fk in sys.argv[1:]:
    fam = FAMILIES[fk]
    ops = {t: fam['fn'](t, 0) for t in TYPES}
    al = {t: mask_at(ops[t], 24, 0) for t in TYPES}
    r = [round(max(iou(al[a], mask_at(ops[b], 24, g)) for g in range(0, 360, 15)), 2) for a, b in (('D', 'N'), ('D', 'E'), ('N', 'E'))]
    print(fk, 'DN DE NE', r, 'area D N E', [int((al[t] > .5).sum()) for t in TYPES], flush=True)
