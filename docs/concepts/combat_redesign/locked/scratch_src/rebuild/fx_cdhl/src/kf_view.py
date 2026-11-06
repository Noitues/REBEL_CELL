"""kf_view.py <id> <skin> [max_w] : the built keyframes (+ reduce still) of one effect at 1x, wrapped into rows no wider than max_w
-> work/view/<id>_<skin>.png (for looking at every render at 1x)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import fx_cdhl as F
from fxk_lib import W, mono
fid, skin = sys.argv[1], sys.argv[2]
max_w = int(sys.argv[3]) if len(sys.argv) > 3 else 1560
fx = F.BYID[fid]
os.makedirs(W + 'view', exist_ok=True)
ims = [(Image.open(W + 'kf/%s_%s_%d.png' % (fid, skin, i)), '%d ms %s' % (t, c[:40])) for i, (t, c) in enumerate(fx['keys'])]
ims.append((Image.open(W + 'kf/%s_%s_r.png' % (fid, skin)), 'REDUCE'))
w, h = ims[0][0].size
per = max(1, (max_w + 6) // (w + 6))
rows = (len(ims) + per - 1) // per
sheet = Image.new('RGB', (per * (w + 6) - 6, rows * (h + 18)), (10, 10, 12))
d = ImageDraw.Draw(sheet)
for k, (im, cap) in enumerate(ims):
    x, y = (k % per) * (w + 6), (k // per) * (h + 18)
    sheet.paste(im, (x, y + 18))
    d.text((x + 2, y + 2), cap, font=mono(13), fill=(220, 220, 230))
out = W + 'view/%s_%s.png' % (fid, skin)
sheet.save(out)
print(out, sheet.size)
