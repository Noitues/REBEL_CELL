"""loud_both.py <id> [skin] [step]: peak loudness of one effect with both meters, full motion, every <step>-th 60 fps frame.
  mine : mp_lib method (px >= 5 L* brighter than max(pre, post, marks-off), x mean L* / 100)
  cdhl : fxk_lib.loud_frame (px with dE76 > 5 against the marks-off frame, weighted by L* / 100), the C/D/H/L designer's meter, so the
         four families' numbers rank on one scale (review 2.10)"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/src')
import numpy as np
import mp_eff as E
from mp_lib import *
import fxk_lib as K
fid = sys.argv[1]
skin = sys.argv[2] if len(sys.argv) > 2 else 'neutral'
step = int(sys.argv[3]) if len(sys.argv) > 3 else 1
s = E.FX[fid]
tot = s['timing']['total']
ts = [i * 1000.0 / 60 for i in range(0, int(tot * 60 / 1000) + 1, step)]
pre, post = s['pre'](skin), s['post'](skin)
Lpp = np.maximum(lstar(rel_lum(pre)), lstar(rel_lum(post)))
bm = (0, 0, 0)
bc = (0, 0, 0)
for t in ts:
    f = s['render'](t, skin, False)
    r = s['render'](t, skin, False, marks=False)
    Lf = lstar(rel_lum(f))
    m = (Lf - np.maximum(Lpp, lstar(rel_lum(r)))) >= LOUD_DL
    n = int(m.sum())
    av = n * (float(Lf[m].mean()) if n else 0) / 100
    if av > bm[0]:
        bm = (round(av, 1), n, round(t))
    lv, ar, _ = K.loud_frame(np.clip(f, 0, 255), np.clip(r, 0, 255))
    if lv > bc[0]:
        bc = (round(lv, 1), ar, round(t))
print(fid, skin, 'mine', bm, 'cdhl', bc, flush=True)
