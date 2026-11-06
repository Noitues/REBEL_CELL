"""run_fx.py <id> <skin>: render one effect on one skin.
 - every frame at 60 fps over the whole animation (+100 ms tail) for the flash check (full motion and reduce motion)
 - keyframe tiles (spec keys) + a reduce-motion tile
 - strip jpg -> locked/effects/strips/<id>_<skin>.jpg ; numbers -> fx_mpst/work/res_<id>_<skin>.json ; tiles -> work/tiles/"""
import sys, os, json, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import fx_eff as E
from fxlib import *

OUTD = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/effects/'
fid, skin = sys.argv[1], sys.argv[2]
s = E.FX[fid]
os.makedirs(OUTD + 'strips', exist_ok=True)
os.makedirs(ME + 'work/tiles', exist_ok=True)
t0 = time.time()
total = s['timing']['total']
n = int(math.ceil((total + 100) * 60 / 1000.0)) + 1
ts = [i * 1000.0 / 60 for i in range(n)]
frames = [s['render'](t, skin, False) for t in ts]
fc = flash_check(frames)
framesr = [s['render'](t, skin, True) for t in ts]
fcr = flash_check(framesr)
del frames, framesr
# keyframes
sc = s['scale']
tiles = []
for (t, cap) in s['keys']:
    a = s['render'](float(t), skin, False)
    im = to_img(a)
    im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    fp = ME + 'work/tiles/%s_%s_%d.png' % (fid, skin, t)
    im.save(fp)
    tiles.append((t, cap, fp, False))
rt = s.get('reduce_t', s['keys'][3][0])
a = s['render'](float(rt), skin, True)
im = to_img(a).resize(tiles[0][2] and Image.open(tiles[0][2]).size, Image.LANCZOS)
fp = ME + 'work/tiles/%s_%s_reduce.png' % (fid, skin)
im.save(fp)
tiles.append((rt, 'REDUCE MOTION', fp, True))
# strip
tw, th = Image.open(tiles[0][2]).size
pad, lab = 10, 30
head = 60
Wd = pad + len(tiles) * (tw + pad)
strip = Image.new('RGB', (Wd, head + th + lab + pad), (14, 14, 20))
d = ImageDraw.Draw(strip)
skn = {'neutral': 'player skin (neutral corp)', 'solace': 'Solace skin', 'meridian': 'Meridian skin'}[skin]
d.text((pad, 4), '%s  %s  |  %s' % (fid, s['title'].upper(), skn), font=font('anton', 24), fill=(255, 255, 255))
tim = '  '.join('%s %d-%d ms %s' % (p[0].split(':')[0], p[1], p[2], p[3]) for p in s['timing']['phases'])
d.text((pad, 42), ('total %d ms | ' % total) + tim, font=font('mono', 12), fill=(190, 196, 214))
x = pad
for (t, cap, fp, red) in tiles:
    im = Image.open(fp)
    strip.paste(im, (x, head))
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
res = dict(id=fid, skin=skin, total_ms=total, frames=n, flash=fc, flash_reduce=fcr, tiles=[(t, c, f, r) for t, c, f, r in tiles],
           strip=fpj, strip_bytes=os.path.getsize(fpj), secs=round(time.time() - t0, 1))
json.dump(res, open(ME + 'work/res_%s_%s.json' % (fid, skin), 'w'))
print('ok', fid, skin, 'flashes', fc['flashes'], 'max/s', fc['max_flashes_per_s'], 'area up/down', fc['max_area_swing_up'], fc['max_area_swing_down'],
      '| reduce', fcr['max_flashes_per_s'], '| strip', res['strip_bytes'], res['secs'], 's', flush=True)
