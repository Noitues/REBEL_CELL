import sys, numpy as np
from lab import *
p = sys.argv[1]
im = load(p); L = Ls(Y(im))
for b in sys.argv[2:]:
    x0, y0, x1, y1 = map(int, b.split(','))
    sub = L[y0:y1, x0:x1]
    bg = np.percentile(sub, 10); pk = np.percentile(sub, 99.5)
    prof = ((sub - bg) / (pk - bg)).clip(0, 1).max(axis=1)
    print('  box %s: subpix %.1f  prof %s' % (b, prof[prof > 0.08].sum(), ' '.join('%.2f' % v for v in prof)))
