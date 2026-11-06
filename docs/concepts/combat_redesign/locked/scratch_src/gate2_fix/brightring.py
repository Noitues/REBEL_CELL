"""brightring.py <png> <sfx> r0 r1 Lmin: blobs of pixels above Lmin in an annulus, with the capture classes under each"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import rb_tokens as T
import rb_checks as RC
png, sfx = sys.argv[1], sys.argv[2]
r0, r1, Lmin = float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.float64)
L = T.lstar(T.lum(rgb))
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
m = (rho >= r0) & (rho < r1) & (L > Lmin)
M = RC.load_masks(sfx)
lab, n = ndi.label(ndi.binary_dilation(m, iterations=2))
print('px', int(m.sum()), 'blobs', n)
for i, sl in enumerate(ndi.find_objects(lab)):
    sub = (lab[sl] == i + 1) & m[sl]
    k = int(sub.sum())
    if k < 3:
        continue
    cls = [c for c, mm in M.items() if (mm[sl] & sub).any()]
    ys, xs = np.nonzero(sub)
    col = rgb[sl][sub].mean(0).astype(int).tolist()
    print('  x %d-%d y %d-%d px %d maxL %.1f col %s classes %s' % (sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, k, L[sl][sub].max(), col, cls))
