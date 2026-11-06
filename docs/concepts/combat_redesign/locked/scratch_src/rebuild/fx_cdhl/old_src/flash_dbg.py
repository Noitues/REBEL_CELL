import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import fxk_lib as K
import fx_cdhl as F
fx = F.BYID[sys.argv[1]]; skin = sys.argv[2] if len(sys.argv) > 2 else 'neutral'
ts = [-100 + k * 1000.0 / 60 for k in range(int((fx['dur'] + 300) * 60 / 1000.0) + 1)]
frs = [np.asarray(K.frame(fx, skin, t if t >= 0 else -1.0)) for t in ts]
Y = np.stack([K.rel_lum(f) for f in frs])
foot = (Y.max(0) - Y.min(0)) > 0.02
print('foot', foot.sum(), Y[0].size)
# replicate waves
r = K.flash_check(frs)
print({k: v for k, v in r.items() if k != 'mean_series_footprint'})
m = (Y * foot).reshape(len(ts), -1).sum(1) / foot.sum()
for t, v in zip(ts, m): print(round(t), round(float(v), 3), end=' | ')
