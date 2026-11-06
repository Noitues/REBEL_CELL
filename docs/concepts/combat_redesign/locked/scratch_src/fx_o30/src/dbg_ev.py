import sys, math
sys.dont_write_bytecode = True
import numpy as np
import fx_eff as E
import fxlib as FL
fid = sys.argv[1]
s = E.FX[fid]
tot = s['timing']['total']
n = int(math.ceil((tot + 100) * 60 / 1000.0)) + 1
for red in (False, True):
    fr = [s['render'](i * 1000.0 / 60, 'neutral', red) for i in range(n)]
    # replicate the area series
    Ls = np.stack([FL.rel_lum(f)[::2, ::2] for f in fr])
    f = FL.flash_check(fr)
    dev = np.abs(Ls - Ls[0:1]).max(0); R = dev > 0.02
    L = Ls[:, R]
    # crude: fraction brighter / darker than frame0 by >= 0.10 per frame
    br = ((L - L[0]) >= 0.10).mean(1); dk = ((L[0] - L) >= 0.10).mean(1)
    print('reduce' if red else 'full', f['flashes'], f['flash_frames'], 'events', f['region_events'])
    print('  bright', ' '.join('%.2f' % v for v in br[::2]))
    print('  dark  ', ' '.join('%.2f' % v for v in dk[::2]))
