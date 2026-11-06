import sys, numpy as np
from lab import *
for p in sys.argv[1:]:
    im = load(p); y = Y(im); L = Ls(y)
    warm = (im[..., 0] - im[..., 2]) > 0.06
    print('==', p)
    for k, (r0, r1) in {0: (250, 266), 1: (306, 322), 2: (362, 380)}.items():
        z = polar_mask(r0, r1, 0, 360)
        tick = z & (L > 75) & warm
        white = z & (L > 75) & ~warm
        s = stats(y, tick)
        print('  ring%d cream ticks px %5d p95 %.1f med %.1f | non-warm bright px %d (p95 %.1f)' % (k, s['n'], s['p95'], s['med'], int(white.sum()), stats(y, white)['p95'] if white.sum() > 5 else -1))
