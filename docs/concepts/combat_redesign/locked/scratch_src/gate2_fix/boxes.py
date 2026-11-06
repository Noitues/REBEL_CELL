"""print bounding boxes of capture mask classes for a plate suffix (work/masks_<sfx>.npz)"""
import sys
sys.dont_write_bytecode = True
import numpy as np
sfx = sys.argv[1] if len(sys.argv) > 1 else 'p1'
sys.path.insert(0, "D:/rc_scratch/combat_redesign/locked/corp/src"); import rb_checks as RC; M = RC.load_masks(sfx)
for k in sorted(M):
    m = M[k]
    if m.ndim != 2 or not m.any():
        continue
    ys, xs = np.nonzero(m)
    print('%-14s x %4d-%4d  y %4d-%4d  px %d' % (k, xs.min(), xs.max(), ys.min(), ys.max(), m.sum()))
