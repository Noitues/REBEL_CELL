"""Vein cell size in px: crossings of a vein mask along rows and columns in a region. python cellsize.py img x0 y0 x1 y1 [thr_pct]"""
import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
a = np.asarray(Image.open(sys.argv[1]).convert("RGB"), float)
x0, y0, x1, y1 = [int(v) for v in sys.argv[2:6]]
r = a[y0:y1, x0:x1]
pink = r[..., 0] - 0.5 * r[..., 1] - 0.3 * r[..., 2]
thr = float(sys.argv[6]) if len(sys.argv) > 6 else None
t = np.percentile(pink, 100 - thr) if thr else None
if t is None:
    t = 150
m = pink > t
def cross(mm):
    d = np.diff(mm.astype(int), axis=1)
    return (d == 1).sum() / mm.shape[0]
cx = cross(m); cy = cross(m.T)
W=x1-x0; H=y1-y0; print("mask %.3f cell x ~ %.1f px  y ~ %.1f px" % (m.mean(), W/max(cx,1e-6), H/max(cy,1e-6)))
