import numpy as np
from PIL import Image
from lab import *
from lab import _xx, _yy
F = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
B = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/backdrop/'
pairs = [('p1_bio', 'p1_decide'), ('p1_bio_solace', 'p1_decide_solace'), ('p1_shop_meridian', 'p1_decide_meridian'), ('p1_srv', 'p1_decide'), ('p1_gh', 'p1_decide'), ('p1_rec', 'p1_decide'), ('p1_lobby', 'p1_decide'), ('p1_event', 'p1_decide'), ('p1_shop', 'p1_decide')]
board = R < 500
for b, f in pairs:
    A = np.asarray(Image.open(B + b + '.png').convert('RGB')).astype(int)
    Fm = np.asarray(Image.open(F + f + '.png').convert('RGB')).astype(int)
    d = np.abs(A - Fm).max(2)
    y = Y(A / 255.0)
    m = (_xx >= 1100) & (_yy >= 450) & (_yy < 760) & ~((_xx >= 916) & (_yy >= 760))
    print('%-18s vs %-20s board max diff %3d mean %.2f | whole max %3d | room box(1100-1920,450-760) mean L* %.1f p95 %.1f' % (b, f, d[board].max(), d[board].mean(), d.max(), float(Ls(y[m].mean())), float(Ls(np.percentile(y[m], 95)))))
