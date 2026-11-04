"""bd2_try.py <room> <corp> [base=<json file>] [key=value ...] : compose p1 on the room with a trial grade, print bd2 stats,
write work/try_<room>_<corp>.png and the 1x seam/room crop work/try_<room>_<corp>_crop.png"""
import sys, json
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/backdrop/src')
import numpy as np
from PIL import Image
import bd2_lib as L

room, corp = sys.argv[1], sys.argv[2]
P = {}
for kv in sys.argv[3:]:
    k, v = kv.split('=', 1)
    if k == 'base':
        P.update(json.load(open(v))[room] if v.endswith('.json') else {})
        continue
    P[k] = json.loads(v)
if 'spill_rgb' not in P and P.get('haze_out') is not None:
    P['spill_rgb'] = L.spill_rgb(room, lum_target=P.pop('spill_l', 0.30), P=P)
pl = L.compose(L.backdrop(room, P), corp)
s = L.stats(pl)
print(json.dumps(P))
for k, v in s.items():
    print('%-16s %s' % (k, v))
im = Image.fromarray(pl.astype(np.uint8))
im.save(L.HERE + 'work/try_%s_%s.png' % (room, corp))
im.crop((960, 380, 1920, 1080)).save(L.HERE + 'work/try_%s_%s_crop.png' % (room, corp))
