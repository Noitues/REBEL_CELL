import numpy as np
from lab import *
im = load('p1_decide'); L = Ls(Y(im)); V = im.max(2)
def g(nm, x0, y0, x1, y1, thr=40):
    sub = L[y0:y1, x0:x1]; v = V[y0:y1, x0:x1]
    m = sub > thr
    print('%-26s ink px %4d  L* p90 %.1f  V p90 %.2f' % (nm, m.sum(), np.percentile(sub[m], 90), np.percentile(v[m], 90)))
g('RAW digit 16', 1092, 176, 1116, 200)
g('NEXT digit 2', 1201, 266, 1214, 286)
g('NEXT digit 10', 1457, 266, 1479, 286)
g('NEXT tally after 10', 1486, 268, 1576, 284, 25)
g('YOU tally (split row)', 1476, 236, 1536, 252, 25)
g('NEXT label', 1104, 266, 1156, 284)
g('RAW label', 1168, 154, 1207, 171)
