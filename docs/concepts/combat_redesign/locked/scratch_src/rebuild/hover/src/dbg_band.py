"""dbg_band.py <name> : where the grain check's PLAN-yellow pixels outside the pencil are (coords, Lab, nearby masks), with a 4x crop of each cluster"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import hv_checks as HC
T = HC.T
g, dil = HC.g, HC.dil

name = sys.argv[1]
rep, M, lit, rgb, bg, probe = HC.load(name)
pen_all, pen_wax, focus, hover, ghost, inset, hand, stick = HC.board_mask_sets(M)
band = dil(pen_all, 3) & ~pen_all & ~dil(focus | hover & ~pen_all | hand | stick | inset, 1)
lab = T.lab(rgb)
yel = (lab[..., 2] > 35) & (np.abs(lab[..., 1]) < 25) & (lab[..., 0] > 40) & band
lb, n = ndi.label(dil(yel, 6))
print('yellow band px', int(yel.sum()), 'clusters', n)
for i in range(1, n + 1):
    ys, xs = np.nonzero(yel & (lb == i))
    if not len(xs):
        continue
    cx, cy = int(xs.mean()), int(ys.mean())
    near = [k for k in sorted(M) if M[k][max(0, cy - 6):cy + 7, max(0, cx - 6):cx + 7].any()]
    print('cluster %d: %d px at (%d, %d)  Lab %s  plate rgb %s board rgb %s  masks near %s' % (
        i, len(xs), cx, cy, np.round(lab[ys[0], xs[0]], 1).tolist(), rgb[ys[0], xs[0]].astype(int).tolist(), bg[ys[0], xs[0]].astype(int).tolist(), near))
    x0, y0 = max(0, cx - 30), max(0, cy - 30)
    Image.fromarray(rgb[y0:cy + 30, x0:cx + 30].astype(np.uint8)).resize((240, 240), Image.NEAREST).save(HC.HERE + 'dbg/band_%s_%d.png' % (name, i))
