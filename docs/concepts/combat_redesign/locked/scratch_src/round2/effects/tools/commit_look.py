"""commit_look.py <skin>: look only.  The fx_commit marks (yellow in p2 that change in p3) and their burn order on the round-2 bases,
plus a few keyframes -> work/look/commit_<skin>_*.png and a printout of the mark components (size, bbox, nearest point to the seed)."""
import sys, os
sys.dont_write_bytecode = True
MS = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/src/'
sys.path.insert(0, MS)
os.chdir(MS)
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import mp_eff as E
from mp_lib import *
skin = sys.argv[1] if len(sys.argv) > 1 else 'neutral'
LK = 'D:/rc_scratch/combat_redesign/locked/round2/effects/work/look/'
s = E.FX['fx_commit']
box = s['_box']
a2, a3 = box.crop(E.below(skin, 'p2')), box.crop(E.below(skin, 'p3'))
marks, nd, endp, rest = E.commit_data(('c', skin), a2, a3, box, s['seed'])
lab, n = ndi.label(marks, structure=np.ones((3, 3)))
print('marks px', int(marks.sum()), 'components', n, 'end point', endp, 'rest px', int(rest.sum()))
for i in range(1, n + 1):
    yy, xx = np.nonzero(lab == i)
    j = np.argmin(nd[yy, xx])
    k = np.argmax(nd[yy, xx])
    print(' comp', i, 'px', len(yy), 'bbox', (xx.min(), yy.min(), xx.max(), yy.max()), 'burn from', (xx[j], yy[j]), 'nd', round(float(nd[yy[j], xx[j]]), 3),
          'to', (xx[k], yy[k]), 'nd', round(float(nd[yy[k], xx[k]]), 3))
# burn order map
vis = (a2 * 0.35).astype(np.uint8)
col = np.zeros_like(a2)
f = np.clip(nd, 0, 1)
col[..., 0] = 255 * f
col[..., 2] = 255 * (1 - f)
col[..., 1] = 60
vis = np.where(marks[..., None], col, vis).astype(np.uint8)
vis = np.where(rest[..., None] & ~marks[..., None], np.clip(vis.astype(np.float32) + 40, 0, 255), vis).astype(np.uint8)
Image.fromarray(vis).crop((150, 450, 900, 1000)).save(LK + 'commit_%s_order.png' % skin)
h2, s2, v2 = E.hsv_np(a2)
for t in (0, 120, 230, 360, 450, 600):
    fr = s['render'](float(t), skin, False)
    im = to_img(fr)
    im.crop((150, 450, 900, 1000)).save(LK + 'commit_%s_%d.png' % (skin, t))
    hf, sf, vf = E.hsv_np(box.crop(np.asarray(fr, np.float32)))
    yf = (hf > 40) & (hf < 66) & (sf > 0.55) & (vf > 0.55) & (box.RHO > 205) & (box.RHO < 500)
    burnt_front = 1.08 * E.e_io3(E.seg(t, 60, 400))
    yb = yf & ~(marks & (nd <= burnt_front))
    h3, s3, v3 = E.hsv_np(a3)
    y3 = (h3 > 40) & (h3 < 66) & (s3 > 0.55) & (v3 > 0.55)
    print(' t %d: pencil-yellow px on the board %d; of them outside the burnt marks %d; yellow here but not on p3 %d' % (t, int(yf.sum()), int(yb.sum()),
          int((yf & ~y3).sum())))
print('ok')
