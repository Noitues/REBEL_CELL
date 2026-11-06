"""gun_geo.py: the p3 gun marks (generator 'guns' mask) as connected components: bbox, angle span, radius span, the inner and outer end"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
import mp_eff as E
from mp_lib import *
m = E.cmask('neutral', 'p3', 'guns')
lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
for i in range(1, n + 1):
    ys, xs = np.nonzero((lab == i) & m)
    if len(xs) < 30:
        continue
    r = FRHO[ys, xs]
    a = FANG[ys, xs]
    j0, j1 = int(np.argmin(r)), int(np.argmax(r))
    print(i, len(xs), 'bbox', (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())), 'r', round(float(r.min())), round(float(r.max())),
          'ang', round(float(a.min())), round(float(a.max())), 'inner', (int(xs[j0]), int(ys[j0])), 'outer', (int(xs[j1]), int(ys[j1])))
