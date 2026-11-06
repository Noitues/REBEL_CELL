"""peek_crop.py mode x0 y0 w h scale T1 T2 ... -> work/peek_crop.jpg"""
import sys, numpy as np
from PIL import Image, ImageDraw
import o30_render as RR
mode = sys.argv[1]
x0, y0, w, h, sc = [int(v) for v in sys.argv[2:7]]
segs, n = RR.timeline()
ims = []
for Ts in sys.argv[7:]:
    T = float(Ts)
    i = RR.seg_at(segs, T)
    fr = RR.render_c(segs, i, T - segs[i]['start'], mode == 'red', mode) if T >= 0 else RR.Q.ring1_move(RR.Q.pre_hud(RR.Q.P2), -60.0)
    im = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).crop((x0, y0, x0 + w, y0 + h)).resize((w * sc, h * sc), Image.LANCZOS)
    ImageDraw.Draw(im).text((4, 4), '%d %s+%d' % (T, segs[i]['name'], T - segs[i]['start']), fill=(255, 255, 0))
    ims.append(im)
cols = min(6, len(ims))
sh = Image.new('RGB', (w * sc * cols, h * sc * ((len(ims) + cols - 1) // cols)))
for k, im in enumerate(ims):
    sh.paste(im, ((k % cols) * w * sc, (k // cols) * h * sc))
sh.save(RR.WK + 'peek_crop.jpg', quality=90)
