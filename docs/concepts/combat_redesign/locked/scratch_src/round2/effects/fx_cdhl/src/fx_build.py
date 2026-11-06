"""fx_build.py [--skins=a,b] <id> [<id> ...] : keyframes (all skins) + reduce stills + the 60 fps meters -> work/kf/, work/flash/<id>_<skin>.json
Meters per skin, over every 60 fps frame from 100 ms before the start to 300 ms past the end:
  flash      fxk_lib.flash_check (<= 3 flashes / s), and the reduce-motion variant (neutral)
  loudness   fxk_lib.loud_frame: area x value of what the effect adds (full-value px), its peak and the frame of the peak (review 2.10);
             loud_peak = transient (px that differ from the no-effect frame AND from the settled frame), loud_total_peak = without the settled test
  settle     the last frame that differs from the settled frame (dE76 > 3 on any px): the effect's real length (review 2.11, T2 600 ms)
  layer      UNDER-layer px hidden by the HUD / hand, OVER-layer px drawn on the HUD (only hp_through, refund may: review 1.6)
  guard      effect px drawn within dE76 15 of GAIN, FOCUS or the lime (review 1.8)"""
import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import fx_cdhl as F
from fxk_lib import frame, frame_parts, flash_check, loud_frame, colour_guard, FPS, W, RT
os.makedirs(W + 'kf', exist_ok=True)
os.makedirs(W + 'flash', exist_ok=True)
SKINS = None
args = sys.argv[1:]
if args and args[0].startswith('--skins='):
    SKINS = args[0].split('=', 1)[1].split(',')
    args = args[1:]
for fid in args:
    fx = F.BYID[fid]
    peak = fx.get('peak', 2)
    for skin in fx['skins']:
        if SKINS and skin not in SKINS:
            continue
        t0 = time.time()
        for i, (t, cap) in enumerate(fx['keys']):
            frame(fx, skin, t).save(W + 'kf/%s_%s_%d.png' % (fid, skin, i))
        frame(fx, skin, fx['keys'][peak][0], reduce=True).save(W + 'kf/%s_%s_r.png' % (fid, skin))
        res = {}
        for red in ((False, True) if skin == 'neutral' else (False,)):
            ts = [-100 + k * 1000.0 / FPS for k in range(int((fx['dur'] + 300) * FPS / 1000.0) + 1)]
            frs, loud, area, dl, hid, cross, guard, tot = [], [], [], [], [], [], {}, []
            end = None if red else frame_parts(fx, skin, ts[-1])[0]      # the settled frame (200 ms past the end)
            for t in ts:
                img, ref, under, over, ab = frame_parts(fx, skin, max(0.0, t) if t >= 0 else -1.0, reduce=red)
                frs.append(img.astype(np.uint8))
                if not red:
                    lv, ar, d_ = loud_frame(img, ref, end)                  # transient: the gated 2.10 metric
                    loud.append(lv); area.append(ar); dl.append(d_)
                    tot.append(loud_frame(img, ref)[0])                     # total: transient + the mark it leaves
                    hud = ab[:, :, 3] > 128
                    hid.append(int(((under[:, :, 3] > 25) & hud).sum()))
                    cross.append(int(((over[:, :, 3] > 25) & hud).sum()) if over is not None else 0)
                    for lyr in (under, over):
                        for k, v in colour_guard(lyr).items():
                            guard[k] = max(guard.get(k, 0), v)
            r = flash_check(frs)
            r['t_ms'] = [round(t, 1) for t in ts]
            if not red:
                lab_last = RT.lab(frs[-1].astype(np.float32))
                settle = None
                for t, f_ in zip(ts, frs):
                    if np.linalg.norm(RT.lab(f_.astype(np.float32)) - lab_last, axis=2).max() > 3.0:
                        settle = t
                i_pk = int(np.argmax(loud))
                r['loud_peak'] = round(loud[i_pk], 1)
                r['loud_peak_ms'] = round(ts[i_pk], 1)
                r['loud_peak_area_px'] = area[i_pk]
                r['loud_peak_mean_L'] = round(100.0 * loud[i_pk] / max(1, area[i_pk]), 1)
                r['loud_dL_peak'] = round(max(dl), 1)
                r['loud_series'] = [round(v, 1) for v in loud]
                r['loud_total_peak'] = round(max(tot), 1)
                r['loud_total_peak_ms'] = round(ts[int(np.argmax(tot))], 1)
                r['settles_ms'] = None if settle is None else round(settle + 1000.0 / FPS, 1)
                r['under_px_hidden_by_hud_max'] = max(hid)
                r['over_px_on_hud_max'] = max(cross)
                r['guard_px'] = guard
            res['reduce' if red else 'full'] = r
        json.dump(res, open(W + 'flash/%s_%s.json' % (fid, skin), 'w'))
        f_ = res['full']
        print(fid, skin, 'flash', f_['max_flashes_per_s_footprint'], f_['max_flashes_per_s_crop'], 'loud', f_['loud_peak'], '@', f_['loud_peak_ms'],
              'area', f_['loud_peak_area_px'], 'settle', f_['settles_ms'], 'hid', f_['under_px_hidden_by_hud_max'], 'cross', f_['over_px_on_hud_max'],
              'guard', f_['guard_px'], round(time.time() - t0, 1), flush=True)
