"""wave_look.py <skin> [t ...]: look only.  fx_wave_enter frames at 1x for the given times -> work/look/wave_<skin>_<t>.png"""
import sys, os
sys.dont_write_bytecode = True
MS = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/src/'
sys.path.insert(0, MS)
os.chdir(MS)
import mp_eff as E
from mp_lib import *
skin = sys.argv[1]
ts = [float(v) for v in sys.argv[2:]] or [380.0]
LK = 'D:/rc_scratch/combat_redesign/locked/round2/effects/work/look/'
for t in ts:
    to_img(E.FX['fx_wave_enter']['render'](t, skin, False)).save(LK + 'wave_%s_%d.png' % (skin, t))
print('ok')
