"""test_fx.py <id> <skin> <t,t,..> [reduce 0|1] [scale] -> work/test_<id>_<skin>.png (frames side by side)"""
import sys, time
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw
import fx_eff as E
from fxlib import to_img, font, ME
fid, skin = sys.argv[1], sys.argv[2]
ts = [float(x) for x in sys.argv[3].split(',')]
red = len(sys.argv) > 4 and sys.argv[4] == '1'
sc = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
s = E.FX[fid]
ims = []
t0 = time.time()
for t in ts:
    a = s['render'](t, skin, red)
    im = to_img(a)
    if sc != 1.0:
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    d.text((6, 4), '%d ms' % t, font=font('mono', 18), fill=(255, 255, 0))
    ims.append(im)
W_ = sum(i.width for i in ims) + 6 * (len(ims) - 1)
out = Image.new('RGB', (W_, ims[0].height), (30, 30, 30))
x = 0
for i in ims:
    out.paste(i, (x, 0))
    x += i.width + 6
fp = ME + 'work/test_%s_%s%s.png' % (fid, skin, '_r' if red else '')
out.save(fp)
print('ok', fp, out.size, round(time.time() - t0, 1))
