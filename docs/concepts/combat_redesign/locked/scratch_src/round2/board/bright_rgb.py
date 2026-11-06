"""print the RGB at the brightest unclassed pixels per radius band (C3 source hunt).  python bright_rgb.py <png> <sfx>"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import rb_tokens as T
import rb_checks as RC
png, sfx = sys.argv[1], sys.argv[2]
rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.int32)
Ls = T.lstar(T.lum(rgb.astype(np.float64)))
M = RC.load_masks(sfx)
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
ang = np.degrees(np.arctan2(xx - 536, -(yy - 540))) % 360
anyc = np.zeros((1080, 1920), bool)
for k, m in M.items():
    if not k.startswith('card_') and k != 'scrim':
        anyc |= m
sel = (rho < 480) & ~anyc & (Ls >= 88)
for r0 in range(190, 480, 6):
    m = sel & (rho >= r0) & (rho < r0 + 6)
    if m.sum() < 5:
        continue
    v = Ls[m]
    idx = np.argsort(-v)[:3]
    ys, xs = np.nonzero(m)
    s = ['(%d,%d) L%.0f rgb%s a%.0f' % (xs[i], ys[i], v[i], tuple(rgb[ys[i], xs[i]]), ang[ys[i], xs[i]]) for i in idx]
    print('r %3d-%3d n %5d ' % (r0, r0 + 6, m.sum()), ' | '.join(s))
