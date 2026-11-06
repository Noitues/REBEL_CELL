"""findcol.py <png> r g b [tol]: bounding boxes of connected blobs of one colour"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
png = sys.argv[1]
c = np.array([int(v) for v in sys.argv[2:5]])
tol = int(sys.argv[5]) if len(sys.argv) > 5 else 0
a = np.asarray(Image.open(png).convert('RGB')).astype(int)
m = (np.abs(a - c).max(2) <= tol)
lab, n = ndi.label(ndi.binary_dilation(m, iterations=3))
print('px', int(m.sum()), 'blobs', n)
for i, sl in enumerate(ndi.find_objects(lab)[:30]):
    k = int((m[sl]).sum())
    print('  x %d-%d y %d-%d px %d' % (sl[1].start, sl[1].stop, sl[0].start, sl[0].stop, k))
