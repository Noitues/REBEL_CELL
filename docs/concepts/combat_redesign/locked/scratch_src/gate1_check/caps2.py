# sub-pixel cap height: for each word box, per-row max normalized ink (over columns) summed over the word's rows (+2 px pad)
import sys, numpy as np
from caps import words
from lab import *
def subpix(L, ch, w, pad=3):
    x0, y0, x1, y1 = w[0], w[1] - pad, w[2], w[3] + pad
    sub = L[y0:y1, x0:x1]
    bg = np.percentile(L[y0 - 6:y1 + 6, x0 - 6:x1 + 6], 20)
    pk = np.percentile(sub, 99)
    prof = ((sub - bg) / (pk - bg)).clip(0, 1).max(axis=1)
    return float(prof.sum()), prof
if __name__ == '__main__':
    p = sys.argv[1]; box = tuple(map(int, sys.argv[2].split(',')))
    im = load(p); L = Ls(Y(im)); ch = im.max(2) - im.min(2)
    W, t = words(p, box)
    for w in W:
        h, prof = subpix(L, ch, w)
        print('  word x %4d-%4d y %4d-%4d  rows@50%% %2d  subpixel height %.1f   profile %s' % (w[0], w[2], w[1], w[3], w[3] - w[1], h, ' '.join('%.2f' % v for v in prof)))
