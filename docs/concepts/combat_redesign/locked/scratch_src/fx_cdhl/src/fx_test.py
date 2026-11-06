"""fx_test.py <id> [skin] [scale] : keyframes row (+ reduce still) -> work/test_<id>_<skin>.png"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw
import fx_cdhl as F
from fxk_lib import frame, mono
fid = sys.argv[1]
skin = sys.argv[2] if len(sys.argv) > 2 else 'neutral'
sc = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
fx = F.BYID.get(fid) or (F.SHIELD_BLOCK if fid == 'fx_shield_block' else None)
ims = [frame(fx, skin, t) for t, _ in fx['keys']] + [frame(fx, skin, fx['keys'][2][0], reduce=True)]
w, h = ims[0].size
w2, h2 = int(w * sc), int(h * sc)
out = Image.new('RGB', (w2 * len(ims) + 6 * len(ims), h2 + 20), (20, 20, 26))
d = ImageDraw.Draw(out)
for i, im in enumerate(ims):
    out.paste(im.resize((w2, h2), Image.LANCZOS), (i * (w2 + 6), 0))
    lab = '%d ms' % fx['keys'][i][0] if i < len(fx['keys']) else 'reduce'
    d.text((i * (w2 + 6) + 4, h2 + 3), lab, fill=(220, 220, 220), font=mono(13))
out.save('D:/rc_scratch/combat_redesign/locked/fx_cdhl/work/test_%s_%s.png' % (fid, skin))
print('ok')
