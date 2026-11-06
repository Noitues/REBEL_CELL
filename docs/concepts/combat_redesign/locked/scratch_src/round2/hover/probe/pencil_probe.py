"""rb_checks_r2.check_pencil restricted to a box of a hover plate's L6 pencil (no context cut), plus the wax mask's per-row runs.
python pencil_probe.py <plate name> x0 y0 x1 y1 [cls]"""
import sys
import numpy as np
from PIL import Image
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as T
import rb_checks_r2 as R2

HV = 'D:/rc_scratch/combat_redesign/locked/round2/hover/'
name = sys.argv[1]
x0, y0, x1, y1 = (int(v) for v in sys.argv[2:6])
cls = sys.argv[6] if len(sys.argv) > 6 else 'L6'
H, W = 1080, 1920
z = np.load(HV + 'chk/%s.npz' % name)
m = np.unpackbits(z['P__%s_all' % cls])[:H * W].reshape(H, W).astype(bool)
box = np.zeros((H, W), bool)
box[y0:y1, x0:x1] = True
rgb = np.asarray(Image.open(HV + 'out/%s.png' % name).convert('RGB')).astype(np.float64)
r = R2.check_pencil(rgb, T.lum(rgb), {'pen_box_all': m & box})
print(r['rows'])
lab = T.lab(rgb)
dpl = np.linalg.norm(lab - T.lab(np.array(T.TOKENS['PLAN'], np.float64)), axis=-1)
Ls = T.lstar(T.lum(rgb))
wax = m & box & (dpl < 30)
ink = m & box & (Ls < 30)
cy = (y0 + y1) // 2
row = ''.join('W' if wax[cy, x] else ('i' if ink[cy, x] else ('m' if m[cy, x] else '.')) for x in range(x0, x1))
print('row y %d: %s' % (cy, row))
cx = (x0 + x1) // 2
col = ''.join('W' if wax[y, cx] else ('i' if ink[y, cx] else ('m' if m[y, cx] else '.')) for y in range(y0, y1))
print('col x %d: %s' % (cx, col))
print('dE to PLAN along the row:', ' '.join('%.0f' % dpl[cy, x] for x in range(x0, x1) if m[cy, x]))
