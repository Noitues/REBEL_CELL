"""mask_cmp.py: the generator mask classes of p3 (neutral) with their bounding boxes, and the p1 vs p3 ticket masks"""
import sys
sys.dont_write_bytecode = True
import numpy as np
import mp_eff as E
from mp_lib import *
d = np.load(ME + 'work/masks/masks_p3.npz')
for k in d.files:
    m = E.cmask('neutral', 'p3', k)
    ys, xs = np.nonzero(m)
    print(k, int(m.sum()), (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if len(xs) else None)
a, b = E.cmask('neutral', 'p1', 'tickets'), E.cmask('neutral', 'p3', 'tickets')
print('tickets p1 vs p3 differ px', int((a ^ b).sum()))
