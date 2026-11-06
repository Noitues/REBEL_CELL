"""tune_red3.py <id>: reduce-motion appear / dissolve windows for a P block (no shadow in reduce, as shipped); reduce flashes per s"""
import sys
sys.dont_write_bytecode = True
import mp_eff as E
from mp_lib import *
fid = sys.argv[1]
s = E.FX[fid]
ts = [i * 1000.0 / 60 for i in range(int(700 * 60 / 1000) + 1)]
for fin, fout in (((0, 200), (300, 600)), ((0, 250), (300, 600)), ((0, 300), (300, 600)), ((0, 300), (320, 600)), ((0, 150), (250, 600))):
    E.RED_FIN, E.RED_FOUT = fin, fout
    fc = flash_check([s['render'](t, 'neutral', True) for t in ts])
    print(fid, 'in', fin, 'out', fout, '-> flashes', fc['flashes'], 'max/s', fc['max_flashes_per_s'], 'up/down', fc['max_area_swing_up'], fc['max_area_swing_down'], flush=True)
