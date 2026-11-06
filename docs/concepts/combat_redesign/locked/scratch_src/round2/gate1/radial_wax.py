"""gate1 C1: radial profiles across a PLAN mark that follows a circle about the board centre (e.g. the tower hover arc on p2b / h11):
for each degree where wax (dE76 < 30 of PLAN) is found in r0..r1, sample the radial line at 0.25 px (bilinear) and report wax width,
ink width each side (L* < 20 after up to 1.25 px blend) and the wax L* std.  usage: radial_wax.py <png> <r0> <r1> [th0 th1]"""
import sys
import numpy as np
import glib as G
rgb = G.load(sys.argv[1]); L = G.Lstar(rgb); dP = G.de(G.lab(rgb), '#FFE200')
r0, r1 = float(sys.argv[2]), float(sys.argv[3])
th0, th1 = (float(sys.argv[4]), float(sys.argv[5])) if len(sys.argv) > 5 else (0, 360)
cx, cy = G.CC


def bil(A, x, y):
    x0 = np.floor(x).astype(int); y0 = np.floor(y).astype(int); fx = x - x0; fy = y - y0
    return A[y0, x0] * (1 - fx) * (1 - fy) + A[y0, x0 + 1] * fx * (1 - fy) + A[y0 + 1, x0] * (1 - fx) * fy + A[y0 + 1, x0 + 1] * fx * fy


W, IL, IR = [], [], []
for th in np.arange(th0, th1, 1.0):
    t = np.radians(th)
    rs = np.arange(r0 - 8, r1 + 8, 0.25)
    xs = cx + rs * np.sin(t); ys = cy - rs * np.cos(t)
    d = bil(dP, xs, ys); l = bil(L, xs, ys)
    w = d < 30
    if w.sum() < 8:
        continue
    idx = np.nonzero(w)[0]
    a, b = idx.min(), idx.max()
    if (b - a + 1) > w.sum() + 4:
        continue  # two marks on this ray
    def run(i, step):
        bl = 0
        while 0 <= i < len(rs) and l[i] >= 20 and bl < 5:
            bl += 1; i += step
        k = 0
        while 0 <= i < len(rs) and l[i] < 20:
            k += 1; i += step
        return (k + bl * 0.5) * 0.25
    W.append((b - a + 1) * 0.25); IL.append(run(a - 1, -1)); IR.append(run(b + 1, 1))
if W:
    print('rays %d  wax med %.2f p10 %.2f p90 %.2f | ink inner med %.2f outer med %.2f' % (len(W), np.median(W), np.percentile(W, 10), np.percentile(W, 90), np.median(IL), np.median(IR)))
else:
    print('no wax found')
