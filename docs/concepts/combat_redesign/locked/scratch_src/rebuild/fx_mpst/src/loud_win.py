"""loud_win.py <id> <t0> <t1> [skin]: the shared gated loudness on every 60 fps frame between t0 and t1 ms"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/cdhl_snap')
import numpy as np
import mp_eff as E
from mp_lib import *
import fxk_lib as K
fid, t0, t1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
skin = sys.argv[4] if len(sys.argv) > 4 else 'neutral'
s = E.FX[fid]
end = np.clip(s['post'](skin), 0, 255)
for i in range(int(t0 * 60 / 1000), int(t1 * 60 / 1000) + 1):
    t = i * 1000.0 / 60
    f = np.clip(s['render'](t, skin, False), 0, 255)
    r = np.clip(s['render'](t, skin, False, marks=False), 0, 255)
    lv, ar, _ = K.loud_frame(f, r, end)
    print(fid, skin, round(t, 1), 'gated', round(lv), ar, flush=True)
