"""dbg_stamp2.py : widths (the checks' estimator) of wax_stroke masks on a long arc, a ring and an L5 channel with chevrons; ink-gap rows"""
import sys, math
sys.dont_write_bytecode = True
import numpy as np
import hv_core as V
from hv_core import HL, L2
import hv_checks as HC

V.PEN_MASKS.clear()
L = L2()
V.wax_stroke(L, HL.arc(491.5, 20, 86), seed=3, cap=True)
V.wax_stroke(L, [(700 + 60 * math.cos(t), 800 + 45 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 120)], seed=4, cap=False, closed=True)
V.wax_stroke(L, [(1200, 900), (1400, 905)], seed=5, cap=False)
V.pc(L, [(1300, 300), (1500, 320), (1700, 420)], w=13, head=19)
for k in ('L6_wax', 'L6_all', 'L5_wax', 'L5_all'):
    print(k, HC.stroke_width(V.PEN_MASKS[k]) if k in V.PEN_MASKS else None, 'cov', HC.stroke_width(V.PEN_MASKS[k], cov=V.PEN_COV[k]) if k in V.PEN_COV else None)
A, Wm = V.PEN_MASKS['L6_all'], V.PEN_MASKS['L6_wax']
bad = 0
for y in range(380, 530):
    xa = np.nonzero(A[y, 900:1100])[0]
    xw = np.nonzero(Wm[y, 900:1100])[0]
    if len(xa) and len(xw) and min(xw.min() - xa.min(), xa.max() - xw.max()) < 2:
        bad += 1
print('rim rows with ink < 2 px a side', bad)
xs = np.nonzero(A[900, 1150:1450])[0]
print('butt stroke x extent at y 900:', xs.min() + 1150, xs.max() + 1150)
print('reference', HC._ref_widths())
for cx in (1500.0, 1500.25, 1500.5, 1500.75):
    V.PEN_MASKS.clear(); V.PEN_COV.clear()
    L = L2()
    V.wax_stroke(L, [(cx, 175.5 + (cx - 1500)), (cx + 60, 175.5 + (cx - 1500))], seed=9, cap=True)
    print('underline at +%.2f: all mask %s cov %s | wax mask %s cov %s' % (cx - 1500, HC.stroke_width(V.PEN_MASKS['L6_all']), HC.stroke_width(V.PEN_MASKS['L6_all'], cov=V.PEN_COV['L6_all']),
          HC.stroke_width(V.PEN_MASKS['L6_wax']), HC.stroke_width(V.PEN_MASKS['L6_wax'], cov=V.PEN_COV['L6_wax'])))
