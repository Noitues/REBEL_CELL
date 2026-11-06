"""fx_contact.py <skin> <out.png> <id:t,t,t> ... : frames of several effects, one row per effect, for looking at 1x"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
import fx_cdhl as F
from fxk_lib import frame, mono
skin, out = sys.argv[1], sys.argv[2]
rows = []
for spec in sys.argv[3:]:
    fid, ts = spec.split(':')
    fx = F.BYID[fid]
    ims = [frame(fx, skin, float(t)) for t in ts.split(',')]
    W_ = sum(i.width for i in ims) + 6 * (len(ims) - 1)
    r = Image.new('RGB', (W_, ims[0].height + 20), (20, 20, 24))
    d = ImageDraw.Draw(r)
    x = 0
    for i, t in zip(ims, ts.split(',')):
        r.paste(i, (x, 20))
        d.text((x + 2, 2), '%s %s ms' % (fid, t), font=mono(14), fill=(220, 220, 230))
        x += i.width + 6
    rows.append(r)
W_ = max(r.width for r in rows)
H_ = sum(r.height for r in rows) + 6 * len(rows)
sheet = Image.new('RGB', (W_, H_), (10, 10, 12))
y = 0
for r in rows:
    sheet.paste(r, (0, y))
    y += r.height + 6
sheet.save(out)
print(out, sheet.size)
