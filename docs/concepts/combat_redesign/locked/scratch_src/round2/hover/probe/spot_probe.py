"""dot_audit spots inside a box, for each PNG.  python spot_probe.py x0 y0 x1 y1 <png> [<png> ...]"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import dot_audit as DA

x0, y0, x1, y1 = (float(v) for v in sys.argv[1:5])
for p in sys.argv[5:]:
    a = np.asarray(Image.open(p).convert('RGB'), np.float32)
    sp = DA.spots(a)
    sel = [s for s in sp if x0 <= s['x'] <= x1 and y0 <= s['y'] <= y1]
    print(p, 'spots in box', len(sel))
    for s in sorted(sel, key=lambda s: (s['y'], s['x'])):
        print('   x %.1f y %.1f area %.0f sign %+d col %s' % (s['x'], s['y'], s['area'], s['sign'], [int(c) for c in s['col']]))
