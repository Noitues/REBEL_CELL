"""gate1 C5: ticket edge value per ticket: the brightest 2 px ring just inside each ticket box (boxes from check g, x0 y0 x1 y1), corners
(8 px) left out; p90 L* and median rgb of the ring's top half by L*.  usage: tickets.py <png> ..."""
import sys
import numpy as np
import glib as G
BOX = [(24, 24, 108, 94), (116, 24, 200, 94), (208, 24, 292, 94)]
for f in sys.argv[1:]:
    rgb = G.load(f); L = G.Lstar(rgb)
    row = []
    for (x0, y0, x1, y1) in BOX:
        best = None
        for inset in range(0, 4):
            m = np.zeros(L.shape, bool)
            a, b, c, d = x0 + inset, y0 + inset, x1 - inset, y1 - inset
            m[b, a + 8:c - 8] = True; m[d - 1, a + 8:c - 8] = True; m[b + 8:d - 8, a] = True; m[b + 8:d - 8, c - 1] = True
            v = np.percentile(L[m], 90)
            if best is None or v > best[0]:
                best = (v, inset, G.hexof(np.median(rgb[m & (L >= np.percentile(L[m], 50))], 0)))
        row.append('L*p90 %.1f (inset %d, %s)' % best)
    print('%-28s W6 %s | W5 %s | W4 %s' % (f.split('/')[-1], *row))
