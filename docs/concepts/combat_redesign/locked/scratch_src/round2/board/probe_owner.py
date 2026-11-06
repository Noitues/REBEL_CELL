"""which drawer is on top at the bright unclassed pixels (probe_layers output): exclusive combinations.  python probe_owner.py <dir>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import rb_tokens as T
from collections import Counter
d = sys.argv[1]
z = np.load(d + '/masks.npz')
M = {k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) for k in z.files}
rgb = np.asarray(Image.open(d + '/plate.png').convert('RGB')).astype(np.float64)
Ls = T.lstar(T.lum(rgb))
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
known = np.zeros((1080, 1920), bool)
for k, m in M.items():
    if not k.startswith('x_') and k != 'scrim':
        known |= m
sel = (rho < 480) & ~known & (Ls >= 88)
order = ['x_arcdisc', 'x_landing', 'x_ward', 'x_outline', 'x_schedule', 'x_bezel', 'x_plate']
cnt = Counter()
ex = {}
ys, xs = np.nonzero(sel)
for y, x in zip(ys, xs):
    key = tuple(k for k in order if k in M and M[k][y, x])
    cnt[key] += 1
    ex.setdefault(key, (x, y, round(float(Ls[y, x]), 1), tuple(int(v) for v in rgb[y, x]), round(float(rho[y, x]), 1)))
for k, n in cnt.most_common(20):
    print(n, k, 'e.g.', ex[k])
