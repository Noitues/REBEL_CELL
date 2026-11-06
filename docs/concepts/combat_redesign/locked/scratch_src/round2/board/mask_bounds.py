"""bounding boxes of capture classes in corp/work/masks_<sfx>.npz.  python mask_bounds.py <sfx> [class ...]"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
import rb_checks as RC
M = RC.load_masks(sys.argv[1])
want = sys.argv[2:] or sorted(M)
for k in want:
    m = M.get(k)
    if m is None or not m.any():
        print('%-14s none' % k)
        continue
    ys, xs = np.nonzero(m)
    print('%-14s x %4d-%4d  y %4d-%4d  px %d' % (k, xs.min(), xs.max(), ys.min(), ys.max(), m.sum()))
