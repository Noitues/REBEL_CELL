"""npz_near.py <npz> [x0 y0 x1 y1]: list the masks in a hover chk / board-cache npz and their px inside the box (default: the slot-0 corner
x 880-1000, y 700-830).  Read only."""
import sys
import numpy as np
H, W = 1080, 1920
z = np.load(sys.argv[1])
x0, y0, x1, y1 = [int(v) for v in sys.argv[2:6]] if len(sys.argv) > 5 else (880, 700, 1000, 830)
for k in sorted(z.files):
    m = np.unpackbits(z[k])[:H * W].reshape(H, W).astype(bool)
    n = int(m[y0:y1, x0:x1].sum())
    if n:
        ys, xs = np.nonzero(m[y0:y1, x0:x1])
        print('%-28s %6d px in box  x %d-%d y %d-%d   (total %d)' % (k, n, x0 + xs.min(), x0 + xs.max(), y0 + ys.min(), y0 + ys.max(), int(m.sum())))
