"""dbg_stamp.py : the rim arc of h04 drawn alone with wax_stroke; row runs of the all / wax masks (gaps = rows where all == wax width)"""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
import hv_core as V
from hv_core import HL, L2

V.PEN_MASKS.clear()
if len(sys.argv) > 1:
    V._stamp = lambda *a: None
L = L2()
pts = HL.arc(491.5, 20, 86)
V.wax_stroke(L, pts, seed=3, cap=True)
A, Wm = V.PEN_MASKS['L6_all'], V.PEN_MASKS['L6_wax']
runs_a, runs_w, bad = [], [], 0
for y in range(380, 530):
    xa = np.nonzero(A[y, 900:1100])[0]
    xw = np.nonzero(Wm[y, 900:1100])[0]
    if len(xa) and len(xw):
        ra, rw = xa.max() - xa.min() + 1, xw.max() - xw.min() + 1
        runs_a.append(ra)
        runs_w.append(rw)
        lft, rgt = xw.min() - xa.min(), xa.max() - xw.max()
        if min(lft, rgt) < 2:
            bad += 1
print('rows', len(runs_a), 'all run min/med/max', min(runs_a), int(np.median(runs_a)), max(runs_a), 'wax', min(runs_w), int(np.median(runs_w)), max(runs_w),
      'rows with ink < 2 px a side', bad)
im = np.asarray(V.done_box(L))
a = im[..., 3]
ink_rows = 0
for y in range(380, 530):
    row = im[y, 900:1100]
    wax = np.nonzero((row[:, 0] > 150) & (row[:, 3] > 200))[0]
    if not len(wax):
        continue
    l, r = wax.min(), wax.max()
    if not (row[max(0, l - 2), 3] > 200 and row[min(199, r + 2), 3] > 200):
        ink_rows += 1
print('rendered rows with no opaque ink 2 px outside the wax', ink_rows)
