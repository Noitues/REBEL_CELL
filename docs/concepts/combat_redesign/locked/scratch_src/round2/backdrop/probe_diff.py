"""probe_diff.py <a.png> <b.png> [out.png] -- where two plates differ: clusters of pixels with max channel diff > 2 (bbox, px, max diff),
and an amplified diff image."""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
a = np.asarray(Image.open(sys.argv[1]).convert('RGB'), np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB'), np.int16)
d = np.abs(a - b).max(-1)
m = d > 2
print('px > 2:', int(m.sum()), 'max', int(d.max()), 'mean', round(float(np.abs(a - b).mean()), 3))
lab, n = ndi.label(ndi.binary_dilation(m, iterations=6))
objs = ndi.find_objects(lab)
rows = []
for i, sl in enumerate(objs):
    mm = (lab[sl] == i + 1) & m[sl]
    rows.append((int(mm.sum()), [sl[1].start, sl[0].start, sl[1].stop, sl[0].stop], int(d[sl][mm].max()) if mm.any() else 0))
for r in sorted(rows, reverse=True)[:25]:
    print(r)
if len(sys.argv) > 3:
    Image.fromarray(np.clip(d * 8, 0, 255).astype(np.uint8)).save(sys.argv[3])
