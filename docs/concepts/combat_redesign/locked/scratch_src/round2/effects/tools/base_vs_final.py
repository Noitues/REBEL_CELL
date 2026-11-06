"""base_vs_final.py <base.png> <final plate name>: where an effects base differs from the published round-2 plate (px over 8, blobs)"""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
b = np.asarray(Image.open(FIN + sys.argv[2] + '.png').convert('RGB')).astype(int)
d = np.abs(a - b).max(2)
m = d > 8
print('px over 8', int(m.sum()), 'max', int(d.max()), 'mean', round(float(d.mean()), 4))
lab, n = ndi.label(ndi.binary_dilation(m, iterations=4))
rows = []
for i, s in enumerate(ndi.find_objects(lab)):
    k = int((m[s] & (lab[s] == i + 1)).sum())
    rows.append((k, s[1].start, s[0].start, s[1].stop, s[0].stop, int(d[s].max())))
for r in sorted(rows, reverse=True)[:12]:
    print('  blob %5d px  x %d-%d y %d-%d  max %d' % (r[0], r[1], r[3], r[2], r[4], r[5]))
if len(sys.argv) > 3:
    x0, y0, x1, y1 = [int(v) for v in sys.argv[3].split(',')]
    z = 4
    A_ = Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST)
    B_ = Image.fromarray(b[y0:y1, x0:x1].astype(np.uint8)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST)
    S = Image.new('RGB', (A_.width * 2 + 10, A_.height), (255, 0, 255))
    S.paste(A_, (0, 0))
    S.paste(B_, (A_.width + 10, 0))
    S.save(sys.argv[4])
