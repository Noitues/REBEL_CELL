"""loud_probe.py [skin] [ids...] : quick loudness peaks per effect (every 2nd 60 fps frame), sorted, for tuning the 2.10 order.
Prints the transient peak (vs the frame without the effect AND vs the settled frame) and the total peak (vs the frame without the effect)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fx_cdhl as F
from fxk_lib import frame_parts, loud_frame, FPS
skin = sys.argv[1] if len(sys.argv) > 1 else 'neutral'
ids = sys.argv[2:] or [f['id'] for f in F.FX] + ['fx_shield_block']
rows = []
for fid in ids:
    fx = F.BYID[fid]
    if skin not in fx['skins']:
        continue
    end = frame_parts(fx, skin, fx['dur'] + 300.0)[0]
    best, tot = (0, 0, 0), 0
    t = 0.0
    while t <= fx['dur']:
        img, ref, u, o, ab = frame_parts(fx, skin, t)
        lv, ar, d_ = loud_frame(img, ref, end)
        tot = max(tot, loud_frame(img, ref)[0])
        if lv > best[0]:
            best = (lv, t, ar)
        t += 2000.0 / FPS
    rows.append((best[0], fid, fx['kind'], best[1], best[2], tot))
    print(fid, fx['kind'], round(best[0]), '@', round(best[1]), 'area', best[2], 'total', round(tot), flush=True)
print('---- sorted (transient)')
for r in sorted(rows, reverse=True):
    print('%8.0f  %-22s %-7s @%4.0f ms  area %6d  total %6.0f' % r)
