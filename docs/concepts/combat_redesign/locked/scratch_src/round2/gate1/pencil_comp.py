"""gate1 C1: per connected PLAN-wax component (dE76 < 30 of #FFE200, >= 30 px) on a plate: bbox, px, ridge-width estimate
(2 * EDT on the ridge, median and p10), grain (L* std of wax eroded 1), modal colour.  usage: pencil_comp.py <png> [x0 y0 x1 y1]"""
import sys
import numpy as np
from scipy import ndimage as ndi
import glib as G
rgb = G.load(sys.argv[1])
L = G.Lstar(rgb)
dP = G.de(G.lab(rgb), '#FFE200')
wax = dP < 30
if len(sys.argv) > 5:
    x0, y0, x1, y1 = map(int, sys.argv[2:6])
    m = np.zeros_like(wax); m[y0:y1, x0:x1] = True; wax &= m
lab, n = ndi.label(wax, structure=np.ones((3, 3)))
edt = ndi.distance_transform_edt(wax)
ridge = wax & (edt >= ndi.maximum_filter(edt, size=3) - 1e-6) & (edt >= 1.5)
objs = ndi.find_objects(lab)
rows = []
for i, sl in enumerate(objs):
    k = i + 1
    cm = lab[sl] == k
    px = int(cm.sum())
    if px < 30:
        continue
    rd = ridge[sl] & cm
    w = 2 * edt[sl][rd] if rd.any() else np.array([0.0])
    inter = ndi.binary_erosion(cm, iterations=1)
    g = float(L[sl][inter].std()) if inter.sum() > 20 else float('nan')
    col = G.hexof(np.median(rgb[sl][cm], 0))
    rows.append((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop, px, float(np.median(w)), float(np.percentile(w, 10)), g, col))
rows.sort(key=lambda r: -r[4])
for r in rows:
    print('bbox x %4d-%4d y %4d-%4d px %6d ridge-w med %.2f p10 %.2f grain %.2f med %s' % (r[0], r[2], r[1], r[3], r[4], r[5], r[6], r[7], r[8]))
