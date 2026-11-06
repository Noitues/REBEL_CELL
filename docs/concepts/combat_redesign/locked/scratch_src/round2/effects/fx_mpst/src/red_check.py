"""red_check.py <id> [skin]: flash meter of one effect, full and reduce, with the current mp_eff settings"""
import sys
sys.dont_write_bytecode = True
import mp_eff as E
from mp_lib import *
fid = sys.argv[1]
skin = sys.argv[2] if len(sys.argv) > 2 else 'neutral'
s = E.FX[fid]
ts = [i * 1000.0 / 60 for i in range(int(700 * 60 / 1000) + 1)]
for red in (False, True):
    fc = flash_check([s['render'](t, skin, red) for t in ts])
    print(fid, skin, 'reduce' if red else 'full', 'flashes', fc['flashes'], 'max/s', fc['max_flashes_per_s'], 'up/down', fc['max_area_swing_up'], fc['max_area_swing_down'], flush=True)
