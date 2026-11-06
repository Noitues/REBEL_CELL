"""gate1: diff map image (differing px in red over the dimmed first image) + per-region counts.  usage: diffmap.py a.png b.png out.png"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(np.int16)
d = np.abs(a - b).max(-1)
m = d > 2
o = (a * 0.35).astype(np.uint8)
o[ndi.binary_dilation(m, iterations=2)] = (255, 0, 0)
Image.fromarray(o).save(sys.argv[3])
yy, xx = np.mgrid[0:1080, 0:1920]
r = np.hypot(xx - 536, yy - 540)
for lo, hi in ((0, 212), (212, 385), (385, 430), (430, 470), (470, 500), (500, 3000)):
    sel = m & (r >= lo) & (r < hi)
    print('r %4d-%4d: px>2 %5d  max %3d' % (lo, hi, sel.sum(), d[sel].max() if sel.any() else 0))
lb, n = ndi.label(ndi.binary_dilation(m, iterations=3))
for i, sl in enumerate(ndi.find_objects(lb)):
    c = (m[sl]).sum()
    if c > 20:
        print('  cluster x %d-%d y %d-%d px %d max %d' % (sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, c, d[sl].max()))
