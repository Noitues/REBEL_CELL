"""tune_red2.py <id>: more reduce-motion candidates (appear window, dissolve window, shadow strength) for one P block"""
import sys
sys.dont_write_bytecode = True
import mp_eff as E
from mp_lib import *
fid = sys.argv[1]
s = E.FX[fid]
ts = [i * 1000.0 / 60 for i in range(int(700 * 60 / 1000) + 1)]
orig_shadow = E.shadow
for fin, fout, shk in (((0, 200), (300, 600), 0.5), ((0, 200), (300, 600), 0.0), ((0, 250), (300, 600), 1.0), ((0, 250), (300, 600), 0.5),
                       ((0, 300), (300, 600), 1.0), ((0, 200), (250, 600), 0.5)):
    E.RED_FIN, E.RED_FOUT = fin, fout
    E.shadow = (lambda rgba, off=(3, 5), k=0.55, _k=shk: orig_shadow(rgba, off, k * _k))
    fr = [s['render'](t, 'neutral', True) for t in ts]
    fc = flash_check(fr)
    print(fid, 'in', fin, 'out', fout, 'shadow x', shk, '-> flashes', fc['flashes'], 'max/s', fc['max_flashes_per_s'], 'up/down', fc['max_area_swing_up'], fc['max_area_swing_down'], flush=True)
