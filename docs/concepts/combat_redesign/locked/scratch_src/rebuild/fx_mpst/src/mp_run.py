"""mp_run.py <id> <skin>: render one effect on one skin (rebuilt board).
 - every frame at 60 fps over the whole animation (+100 ms tail), full and reduce motion: the flash meter (mp_lib.flash_check) and the
   loudness measure (mp_lib.loudness: peak area x value of the light the effect adds over its pre / post states and its marks-off frame)
 - keyframe tiles (spec keys) + a reduce-motion tile
 - strip jpg -> locked/effects/strips/<id>_<skin>.jpg ; numbers -> work/res_<id>_<skin>.json ; tiles -> work/tiles/"""
import sys, os, json, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import mp_eff as E
from mp_lib import *
sys.path.insert(1, ME + 'cdhl_snap')
import fxk_lib as K      # the C/D/H/L designer's loudness meter (read-only snapshot): one scale for all eight families

fid, skin = sys.argv[1], sys.argv[2]
s = E.FX[fid]
os.makedirs(OUTD + 'strips', exist_ok=True)
os.makedirs(ME + 'work/tiles', exist_ok=True)
t0 = time.time()
total = s['timing']['total']
red_total = max(p[2] for p in s['reduce_phases'])
n = int(math.ceil((max(total, red_total) + 100) * 60 / 1000.0)) + 1
ts = [i * 1000.0 / 60 for i in range(n)]
pre, post = s['pre'](skin), s['post'](skin)
Lpp = np.maximum(lstar(rel_lum(pre)), lstar(rel_lum(post)))


def run(reduce):
    frames = [s['render'](t, skin, reduce) for t in ts]
    fc = flash_check(frames)
    refs = []
    for t in ts:
        r = s['render'](t, skin, reduce, marks=False)
        refs.append(r)
    # reference per pixel: the brighter of pre, post and the marks-off frame (in L*), turned back into an RGB-free L* array
    Lf = [lstar(rel_lum(f)) for f in frames]
    Lr = [np.maximum(Lpp, lstar(rel_lum(r))) for r in refs]
    best = dict(av=0.0, area_px=0, mean_L=0.0, p95_L=0.0, frame=0)
    curve = []
    for i, (a, b) in enumerate(zip(Lf, Lr)):
        m = (a - b) >= LOUD_DL
        k = int(m.sum())
        v = float(a[m].mean()) if k else 0.0
        av = k * v / 100.0
        curve.append(round(av, 1))
        if av > best['av']:
            best = dict(av=round(av, 1), area_px=k, mean_L=round(v, 1), p95_L=round(float(np.percentile(a[m], 95)), 1) if k else 0.0, frame=i,
                        t_ms=round(ts[i], 1))
    best['curve'] = curve
    # shared gated meter (review 2.10): px with dE76 > 5 against the marks-off frame AND against the settled frame, weighted by L* / 100
    endf = np.clip(post, 0, 255)
    g = [K.loud_frame(np.clip(f, 0, 255), np.clip(r, 0, 255), endf) for f, r in zip(frames, refs)]
    gi = int(np.argmax([x[0] for x in g]))
    best['gated'] = dict(peak=round(g[gi][0], 1), area_px=g[gi][1], t_ms=round(ts[gi], 1), curve=[round(x[0], 1) for x in g])
    best['added_light_peak'] = round(max(float(np.clip(a - b, 0, None).sum()) / 100.0 for a, b in zip(Lf, Lr)), 1)
    return fc, best


fc, ld = run(False)
fcr, ldr = run(True)
sc = s['scale']
tiles = []
for (t, cap) in s['keys']:
    im = to_img(s['render'](float(t), skin, False))
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    fp = ME + 'work/tiles/%s_%s_%d.png' % (fid, skin, t)
    im.save(fp)
    tiles.append((t, cap, fp, False))
rt = s.get('reduce_t', 240)
im = to_img(s['render'](float(rt), skin, True)).resize(Image.open(tiles[0][2]).size, Image.LANCZOS)
fp = ME + 'work/tiles/%s_%s_reduce.png' % (fid, skin)
im.save(fp)
tiles.append((rt, 'REDUCE MOTION', fp, True))
tw, th = Image.open(tiles[0][2]).size
pad, lab, head = 10, 30, 84
Wd = max(pad + len(tiles) * (tw + pad), 1500)
strip = Image.new('RGB', (Wd, head + th + lab + pad), (14, 14, 20))
d = ImageDraw.Draw(strip)
skn = {'neutral': 'player skin (neutral corp)', 'solace': 'Solace skin', 'meridian': 'Meridian skin'}[skin]
d.text((pad, 4), '%s  %s  |  %s  |  rebuilt board 2026-11-03' % (fid, s['title'].upper(), skn), font=font('anton', 24), fill=(255, 255, 255))
tim = '  '.join('%s %d-%d ms %s' % (p[0].split(':')[0], p[1], p[2], p[3]) for p in s['timing']['phases'])
d.text((pad, 40), ('total %d ms (cap 600) | ' % total) + tim, font=font('mono', 12), fill=(190, 196, 214))
d.text((pad, 60), 'flash max/s: full %d, reduce %d (limit 3)  |  loudness (shared gated meter) %.0f (%d px), brighter-only %.0f; reduce %.0f  |  effect under the HUD and the hand%s'
       % (fc['max_flashes_per_s'], fcr['max_flashes_per_s'], ld['gated']['peak'], ld['gated']['area_px'], ld['av'], ldr['gated']['peak'], ' (trace_add crosses: allowed)' if fid == 'fx_trace_add' else ''),
       font=font('mono', 12), fill=(150, 220, 160))
x = pad
for (t, cap, fp, red) in tiles:
    strip.paste(Image.open(fp), (x, head))
    if red:
        d.rectangle([x - 2, head - 2, x + tw + 1, head + th + 1], outline=(255, 214, 0), width=3)
    d.text((x, head + th + 6), ('%d ms  %s' % (t, cap)) if not red else ('REDUCE MOTION, %d ms' % t), font=font('mono', 14),
           fill=(255, 214, 0) if red else (230, 232, 240))
    x += tw + pad
q = 90
fpj = OUTD + 'strips/%s_%s.jpg' % (fid, skin)
while True:
    strip.save(fpj, quality=q)
    if os.path.getsize(fpj) < 1.9e6 or q < 60:
        break
    q -= 6
res = dict(id=fid, skin=skin, total_ms=total, reduce_total_ms=red_total, frames=n, flash=fc, flash_reduce=fcr, loud=ld, loud_reduce=ldr,
           tiles=[(t, c, f, r) for t, c, f, r in tiles], strip=fpj, strip_bytes=os.path.getsize(fpj), secs=round(time.time() - t0, 1))
json.dump(res, open(ME + 'work/res_%s_%s.json' % (fid, skin), 'w'))
print('ok', fid, skin, 'flash max/s', fc['max_flashes_per_s'], 'reduce', fcr['max_flashes_per_s'], 'area up/down', fc['max_area_swing_up'], fc['max_area_swing_down'],
      '| loud gated', ld['gated']['peak'], ld['gated']['area_px'], '@', ld['gated']['t_ms'], 'bright', ld['av'], 'reduce gated', ldr['gated']['peak'], '| strip', res['strip_bytes'], res['secs'], 's', flush=True)
