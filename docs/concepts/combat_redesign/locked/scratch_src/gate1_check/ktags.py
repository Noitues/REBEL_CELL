import numpy as np
from lab import *
im = load('p1_decide'); L = Ls(Y(im))
for nm, (x0, y0, x1, y1) in {'+2 W3 tag': (684, 220, 748, 244), '+1 W2 tag': (664, 260, 724, 283), 'NOW W1 tag': (626, 308, 702, 334), 'digit disc 1': (858, 334, 884, 360), 'HOLD NEXT plate': (760, 800, 850, 870), '+2 THIS TURN plate': (570, 125, 740, 175)}.items():
    sub = L[y0:y1, x0:x1]
    print('%-20s median L* %.1f  p10 %.1f  p95 %.1f' % (nm, np.median(sub), np.percentile(sub, 10), np.percentile(sub, 95)))
