"""peek_t.py mode T1 T2 ... -> work/peek_t.jpg (board + HUD at 0.5x, 2 per row)"""
import sys, numpy as np
from PIL import Image, ImageDraw
sys.argv_ = sys.argv
import o30_render as RR
mode = sys.argv[1]
segs, n = RR.timeline()
ims = []
for Ts in sys.argv[2:]:
    T = float(Ts)
    i = RR.seg_at(segs, T)
    RR._cv.clear()
    fr = RR.render_c(segs, i, T - segs[i]['start'], mode == 'red', mode) if T >= 0 else RR.Q.ring1_move(RR.Q.pre_hud(RR.Q.P2), -60.0)
    im = Image.fromarray(np.clip(fr, 0, 255).astype(np.uint8)).resize((960, 540), Image.LANCZOS)
    ImageDraw.Draw(im).text((10, 520), '%s  T=%d  %s +%d' % (mode, T, segs[i]['name'], T - segs[i]['start']), fill=(255, 255, 0))
    ims.append(im)
cols = 2
sh = Image.new('RGB', (960 * cols, 540 * ((len(ims) + 1) // cols)))
for k, im in enumerate(ims):
    sh.paste(im, ((k % cols) * 960, (k // cols) * 540))
sh.save(RR.WK + 'peek_t.jpg', quality=88)
