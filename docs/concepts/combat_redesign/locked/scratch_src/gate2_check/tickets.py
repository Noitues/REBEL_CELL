"""tickets.py -- wave ticket edge value per ticket (W6, W5, W4) and glyph p90, on every plate.

Ticket boxes (from the plates): W6 x 24-108, W5 x 116-200, W4 x 208-292, y 24-94.  Edge read: for each column of the top and bottom edge and
each row of the left and right edge (inset 8 px from the corners), the brightest pixel within 4 px of the box line; median of those = the edge
stroke L*.  Glyph read: pixels with L* > 60 inside the ticket, inset 10 px from the edge, p90 L* and the ink height of the row y 48-86."""
import sys
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
BOX = {'W6': (24, 24, 108, 94), 'W5': (116, 24, 200, 94), 'W4': (208, 24, 292, 94)}


def lstar_img(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


names = sys.argv[1:] or ['p1_decide', 'p1_decide_solace', 'p1_decide_meridian', 'p2_preview', 'p3_resolve', 'p2b_hover', 'p1_nowords']
for nm in names:
    rgb = np.asarray(Image.open(FINAL + nm + '.png').convert('RGB')).astype(float)
    L = lstar_img(rgb)
    # find the actual box lines: the column / row profiles of the bright border near the nominal box
    row = []
    for k, (x0, y0, x1, y1) in BOX.items():
        vals = []
        cols = []
        for x in range(x0 + 8, x1 - 8):
            seg = L[y0 - 4:y0 + 5, x]
            vals.append(seg.max())
            seg2 = L[y1 - 4:y1 + 5, x]
            vals.append(seg2.max())
        for y in range(y0 + 8, y1 - 8):
            vals.append(L[y, x0 - 4:x0 + 5].max())
            vals.append(L[y, x1 - 4:x1 + 5].max())
        e = float(np.median(vals))
        inner = L[y0 + 10:y1 - 6, x0 + 6:x1 - 6]
        g = inner[inner > 60]
        p90 = float(np.percentile(g, 90)) if g.size else -1
        # edge colour
        row.append('%s edge L* %.1f  glyph p90 %.1f' % (k, e, p90))
    print('%-22s' % nm, ' | '.join(row))
