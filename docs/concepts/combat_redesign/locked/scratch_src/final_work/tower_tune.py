"""tower_tune.py base_plate.png out.png [PAGE_V] [TEXOP_K]: re-render the locked tower with loudness params, paste over a plate, squint the tower zone"""
import sys, os
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageFilter
import lw_render as LW
import lw_tower as LT
R = LW.R
A = R.A
base, out = sys.argv[1], sys.argv[2]
if len(sys.argv) > 3:
    LT.PAGE_V = float(sys.argv[3])
if len(sys.argv) > 4:
    LT.TEX_K = float(sys.argv[4])
if len(sys.argv) > 5:
    LT.HALO_K = float(sys.argv[5])
if len(sys.argv) > 6:
    LT.FILL_K = float(sys.argv[6])
f = A.J['f1']
tw, cv = LT.render_tower(f)
from cv_lib import C
bg = Image.open(base).convert('RGBA')
ox, oy = int(C[0] - R.FT.CT[0]), int(C[1] - R.FT.CT[1])
bg.alpha_composite(tw, (ox, oy))
bg = bg.convert('RGB')
bg.save(out)
lum = lambda a: 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]
s = bg.resize((120, 67), Image.BOX).filter(ImageFilter.GaussianBlur(1.0))
l = lum(np.asarray(s, np.float32) / 255.0)
yy, xx = np.mgrid[0:l.shape[0], 0:l.shape[1]]
m = np.hypot(xx * 16 + 8 - C[0], yy * 16 + 8 - C[1]) <= 212
print('tower loud %.4f mean %.4f p95 %.4f | plate loud %.4f' % ((l[m] > 0.38).mean(), l[m].mean(), np.percentile(l[m], 95), (l > 0.38).mean()))
