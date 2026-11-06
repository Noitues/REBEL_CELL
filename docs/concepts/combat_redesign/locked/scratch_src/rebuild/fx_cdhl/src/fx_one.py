"""fx_one.py <id> <skin> <t> [t ...] [--reduce] [--sc=2] -> work/one.png : frames side by side, for looking (and a loudness print per frame)"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image
import fx_cdhl as F
from fxk_lib import frame_parts, loud_frame
a = sys.argv[1:]
red = '--reduce' in a
sc = 2.0
for x in a:
    if x.startswith('--sc='):
        sc = float(x.split('=')[1])
a = [x for x in a if not x.startswith('--')]
fx = F.BYID[a[0]]
skin = a[1]
ims = []
for t in a[2:]:
    img, ref, u, o, ab = frame_parts(fx, skin, float(t), reduce=red)
    lv, ar, d_ = loud_frame(img, ref)
    print(t, 'loud', round(lv, 1), 'area', ar)
    im = Image.fromarray(img.astype(np.uint8), 'RGB')
    ims.append(im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS if sc < 1 else Image.NEAREST))
W_ = sum(i.width for i in ims) + 6 * (len(ims) - 1)
out = Image.new('RGB', (W_, ims[0].height), (20, 20, 20))
x = 0
for i in ims:
    out.paste(i, (x, 0))
    x += i.width + 6
out.save('D:/rc_scratch/combat_redesign/locked/rebuild/fx_cdhl/work/one.png')
print(out.size)
