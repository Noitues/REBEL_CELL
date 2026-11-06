"""loud_parts.py <id> [step]: the C/D/H/L designer's gated loudness (fxk_lib.loud_frame with ref = the marks-off frame and end = the post
frame: only the transient light counts) for one effect, as is and with parts switched off (echoes, arrows), to see what makes it loud"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(1, 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/cdhl_snap')
import numpy as np
import mp_eff as E
from mp_lib import *
import fxk_lib as K
fid = sys.argv[1]
step = int(sys.argv[2]) if len(sys.argv) > 2 else 2
s = E.FX[fid]
tot = s['timing']['total']
ts = [i * 1000.0 / 60 for i in range(0, int(tot * 60 / 1000) + 1, step)]
end = np.clip(s['post']('neutral'), 0, 255)
A0, U0, ar0, ca0 = E.ECHO_A, E.ECHO_U, E.arrow, E.clock_arrow


def run(tag):
    best = (0, 0, 0)
    for t in ts:
        f = np.clip(s['render'](t, 'neutral', False), 0, 255)
        r = np.clip(s['render'](t, 'neutral', False, marks=False), 0, 255)
        lv, ar, _ = K.loud_frame(f, r, end)
        if lv > best[0]:
            best = (round(lv), ar, round(t))
    print(fid, tag, best, flush=True)


run('as is')
E.ECHO_A, E.ECHO_U = (0, 0, 0), (0, 0, 0)
run('no echoes')
E.arrow = E.clock_arrow = (lambda *a, **k: None)
run('no echoes no arrows')
