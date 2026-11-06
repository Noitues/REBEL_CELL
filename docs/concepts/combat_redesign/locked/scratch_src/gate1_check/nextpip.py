import numpy as np
from lab import *
im = load('p1_decide'); L = Ls(Y(im)); V = im.max(2)
for nm, (x0, y0, x1, y1) in {'NEXT YOU tally': (1486, 266, 1580, 286), 'NEXT ABSORBED tally': (1216, 266, 1240, 286), 'NEXT SOAK tally': (1374, 266, 1386, 286), 'SPLIT YOU tally': (1476, 234, 1540, 254), 'RAW tally': (1118, 178, 1290, 198)}.items():
    sub = im[y0:y1, x0:x1].reshape(-1, 3); v = sub.max(1)
    top = sub[v >= np.percentile(v, 85)]
    c = np.median(top, axis=0)
    print('%-20s brightest-15%% median rgb %s  V %.2f  L* %.1f' % (nm, tuple(int(255 * q) for q in c), c.max(), float(lab(c)[0])))
for h in ['D9877C', 'FF4433', '3A7EF3']:
    print(h, 'L*', round(float(lab(hex2rgb(h))[0]), 1))
