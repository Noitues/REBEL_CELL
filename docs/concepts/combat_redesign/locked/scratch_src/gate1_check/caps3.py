import sys, numpy as np
from caps import words
from caps2 import subpix
from lab import *
p = sys.argv[1]; box = tuple(map(int, sys.argv[2].split(',')))
im = load(p); L = Ls(Y(im)); ch = im.max(2) - im.min(2)
W, t = words(p, box, chroma_max=float(sys.argv[3]) if len(sys.argv) > 3 else 0.18)
for w in W:
    if len(w[4]) < 2 and (w[3] - w[1]) < 12: continue
    h, prof = subpix(L, ch, w)
    edge = prof[0] + prof[-1]
    print('  x %4d-%4d y %4d-%4d letters %2d rows50 %2d subpix %.1f%s' % (w[0], w[2], w[1], w[3], len(w[4]), w[3] - w[1], h - edge, '  <16' if (h - edge) < 15.6 else ''))
