"""ovl_show.py masks.npz plate.png clsA clsB out.png : crop of the plate around the overlap of two mask classes (overlap in red)"""
import sys
import numpy as np
from PIL import Image
z = np.load(sys.argv[1])
m = lambda c: np.unpackbits(z[c])[:1080 * 1920].reshape(1080, 1920).astype(bool)
a, b = m(sys.argv[3]), m(sys.argv[4])
o = a & b
im = np.asarray(Image.open(sys.argv[2]).convert('RGB')).copy()
ys, xs = np.nonzero(o)
print('overlap px', o.sum(), 'bbox', xs.min(), ys.min(), xs.max(), ys.max())
im[a & ~b] = (im[a & ~b] * 0.5 + np.array([0, 255, 0]) * 0.5).astype(np.uint8)
im[b & ~a] = (im[b & ~a] * 0.5 + np.array([0, 0, 255]) * 0.5).astype(np.uint8)
im[o] = (255, 0, 0)
x0, y0 = max(0, xs.min() - 60), max(0, ys.min() - 60)
Image.fromarray(im).crop((x0, y0, min(1920, xs.max() + 60), min(1080, ys.max() + 60))).resize(((min(1920, xs.max() + 60) - x0) * 3, (min(1080, ys.max() + 60) - y0) * 3), Image.NEAREST).save(sys.argv[5])
