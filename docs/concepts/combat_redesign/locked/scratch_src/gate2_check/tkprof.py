"""tkprof.py <plate> -- profile across the top edge (y 16-34) and the left edge (x 16-34) of each ticket, at the ticket's mid column / row:
prints L* and sRGB per pixel so the edge stroke value of W6 / W5 / W4 can be read directly."""
import sys
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
rgb = np.asarray(Image.open(FINAL + sys.argv[1] + '.png').convert('RGB')).astype(float)
c = rgb / 255.0
c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
L = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
for nm, x0 in (('W6', 24), ('W5', 116), ('W4', 208)):
    xm = x0 + 50
    col = ' '.join('%d:%.0f' % (y, L[y, xm]) for y in range(18, 32))
    print('%s top edge, column x %d: %s' % (nm, xm, col))
    ym = 60
    row = ' '.join('%d:%.0f' % (x, L[ym, x]) for x in range(x0 - 6, x0 + 8))
    print('%s left edge, row y %d: %s' % (nm, ym, row))
    yb = int(np.argmax(L[18:32, xm])) + 18
    print('   brightest top-edge px y %d rgb %s' % (yb, rgb[yb, xm].astype(int)))
