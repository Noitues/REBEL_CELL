import sys, numpy as np
from lab import *
for p in sys.argv[1:]:
    im = load(p); L = Ls(Y(im)); ch = im.max(2) - im.min(2)
    sub = (ch[:, 925:1655] > 0.18) | (L[:, 925:1655] > 45)
    rows = np.where(sub[900:1080].sum(axis=1) > 3)[0] + 900
    bg = np.where(sub[1060:1080].sum(axis=1) > 0)[0]
    print(p, 'lowest row with >3 coloured/bright px in the hand span:', rows.max(), '-> margin', 1079 - rows.max())
