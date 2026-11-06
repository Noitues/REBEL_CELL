"""dbg_pen2.py <name> : pencil widths (the checks' estimator) per connected pencil mark of a plate: all, wax, bbox"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
import hv_checks as HC
name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
A = HC.g(M, 'P__L6_all')
Wx = HC.g(M, 'P__L6_wax')
lb, n = ndi.label(A)
for i in range(1, n + 1):
    m = lb == i
    if m.sum() < 60:
        continue
    ys, xs = np.nonzero(m)
    print('mark %d bbox (%d,%d)-(%d,%d) px %d  all %s  wax %s' % (i, xs.min(), ys.min(), xs.max(), ys.max(), m.sum(), HC.stroke_width(m), HC.stroke_width(Wx & m)))
