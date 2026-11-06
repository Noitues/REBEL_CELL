"""loud_g.py <id> [step] [skin]: the shared gated loudness of one effect, full motion (fxk_lib.loud_frame: px with dE76 > 5 against the
marks-off frame and against the post frame, weighted by L* / 100), every <step>-th 60 fps frame"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/src')
import numpy as np
import mp_eff as E
from mp_lib import *
import fxk_lib as K
fid = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 2
skin = sys.argv[3] if len(sys.argv) > 3 else 'neutral'
s = E.FX[fid]
tot = s['timing']['total']
ts = [i * 1000.0 / 60 for i in range(0, int(tot * 60 / 1000) + 1, step)]
end = np.clip(s['post'](skin), 0, 255)
best = (0, 0, 0)
for t in ts:
    f = np.clip(s['render'](t, skin, False), 0, 255)
    r = np.clip(s['render'](t, skin, False, marks=False), 0, 255)
    lv, ar, _ = K.loud_frame(f, r, end)
    if lv > best[0]:
        best = (round(lv), ar, round(t))
print(fid, skin, 'gated', best, flush=True)
