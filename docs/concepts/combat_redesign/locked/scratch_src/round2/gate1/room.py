"""gate1 C9: room region mean L* (of mean luminance) on board and backdrop plates, with a geometry-only cut (no masks):
x >= 1100, y >= 420, r > 505, minus the HUD column (x >= 1066, y <= 615), the hand / buttons (y >= 575 and x >= 925 where the plate differs
from a blurred copy is NOT used: a fixed box cut x 925-1919, y 575-1080 for the hand on p2 lifted card etc. is too big, so the hand is cut
as y >= 760, x 925-1700 plus the lifted-card box x 1265-1480, y 570-870 on p2) and the buttons (x >= 1660, y >= 845).  Reported, as seen."""
import glob, os
import numpy as np
import glib as G
r_, th_, xx, yy = G.polar()
files = [G.FINAL + n + '.png' for b, c, n in G.plates()] + sorted(glob.glob(G.ROOT + 'backdrop/p1_*.png'))
for f in files:
    Y = G.lum(G.load(f))
    m = (xx >= 1100) & (yy >= 420) & (r_ > 505)
    m &= ~((xx >= 1066) & (yy <= 615))
    m &= ~((yy >= 760) & (xx >= 925) & (xx <= 1700))
    m &= ~((xx >= 1660) & (yy >= 845))
    if 'p2_preview' in f:
        m &= ~((xx >= 1160) & (xx <= 1480) & (yy >= 570) & (yy <= 870))
    if 'p3_resolve' in f:
        m &= ~((xx >= 1066) & (yy <= 715))
    print('%-34s room px %6d  mean L* %.1f  p95 %.1f' % (os.path.basename(f), m.sum(), G.lstar_y(Y[m].mean()), G.lstar_y(np.percentile(Y[m], 95))))
