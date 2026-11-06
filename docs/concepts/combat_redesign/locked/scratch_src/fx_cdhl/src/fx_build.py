"""fx_build.py <id> [<id> ...] : keyframes (all skins) + reduce stills + 60 fps flash check -> work/kf/, work/flash/"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import fx_cdhl as F
from fxk_lib import frame, flash_check, FPS, W
os.makedirs(W + 'kf', exist_ok=True)
os.makedirs(W + 'flash', exist_ok=True)
for fid in sys.argv[1:]:
    fx = F.BYID.get(fid) or F.SHIELD_BLOCK
    peak = fx.get('peak', 2)
    for skin in fx['skins']:
        t0 = time.time()
        for i, (t, cap) in enumerate(fx['keys']):
            frame(fx, skin, t).save(W + 'kf/%s_%s_%d.png' % (fid, skin, i))
        frame(fx, skin, fx['keys'][peak][0], reduce=True).save(W + 'kf/%s_%s_r.png' % (fid, skin))
        res = {}
        for red in ((False, True) if skin == 'neutral' else (False,)):
            ts = [-100 + k * 1000.0 / FPS for k in range(int((fx['dur'] + 300) * FPS / 1000.0) + 1)]
            frs = [np.asarray(frame(fx, skin, max(0.0, t) if t >= 0 else -1.0, reduce=red)) for t in ts]
            r = flash_check(frs)
            r['t_ms'] = [round(t, 1) for t in ts]
            res['reduce' if red else 'full'] = r
        json.dump(res, open(W + 'flash/%s_%s.json' % (fid, skin), 'w'))
        print(fid, skin, 'flash full', res['full']['max_flashes_per_s_footprint'], res['full']['max_flashes_per_s_crop'], res['full']['peak_up_share_footprint'], round(time.time() - t0, 1), flush=True)
