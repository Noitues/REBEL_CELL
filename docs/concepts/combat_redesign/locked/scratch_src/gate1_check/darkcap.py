# dark-text glyph height: rows profile of normalized darkness over a small box around one capital or digit
import sys, numpy as np
from lab import *
p = sys.argv[1]
im = load(p); L = Ls(Y(im))
for b in sys.argv[2:]:
    x0, y0, x1, y1 = map(int, b.split(','))
    sub = L[y0:y1, x0:x1]
    bg = np.percentile(sub, 90); ink = np.percentile(sub, 3)
    prof = ((bg - sub) / (bg - ink)).clip(0, 1).max(axis=1)
    rows = np.where(prof > 0.5)[0]
    print('  box %s: rows>50%% %d (y %d-%d)  subpix %.1f  prof %s' % (b, len(rows), y0 + rows.min(), y0 + rows.max(), prof[prof > 0.08].sum(), ' '.join('%.2f' % v for v in prof)))
