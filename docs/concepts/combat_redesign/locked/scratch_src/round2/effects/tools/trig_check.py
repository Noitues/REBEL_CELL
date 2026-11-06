"""trig_check.py: the effect's pencil layer (trig_yel.png) against the published round-2 p2 plate's own pencil, inside the layer's opaque px;
and its C1 numbers (stroke / wax / ink width, grain) as the board's check f measures them, on the layer composited over p3.
Also a look image: p2 crop | p3 + trig_yel | p3 + trig_pink."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import rb_tokens as RT
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
W = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_cdhl/work/'
p2 = np.asarray(Image.open(FIN + 'p2_preview.png').convert('RGB')).astype(np.float64)
p3 = np.asarray(Image.open(FIN + 'p3_resolve.png').convert('RGB')).astype(np.float64)
ty = np.asarray(Image.open(W + 'trig_yel.png').convert('RGBA')).astype(np.float64)
tp = np.asarray(Image.open(W + 'trig_pink.png').convert('RGBA')).astype(np.float64)
a = ty[..., 3:4] / 255
cy = p3 * (1 - a) + ty[..., :3] * a
op = ty[..., 3] >= 254
d = np.abs(cy - p2).max(2)
print('opaque pencil px', int(op.sum()), 'vs published p2: max', int(d[op].max()), 'p99', round(float(np.percentile(d[op], 99)), 1), 'mean', round(float(d[op].mean()), 2))
lab = RT.lab(cy)
wax = (np.linalg.norm(lab - RT.lab(np.array(RT.TOKENS['PLAN'], np.float64)), axis=2) < 30) & (ty[..., 3] > 128)
ink = (lab[..., 0] < 30) & (ty[..., 3] > 128)
print('wax px', int(wax.sum()), 'wax L* median', round(float(np.median(lab[..., 0][wax])), 1), 'grain L* std', round(float(lab[..., 0][wax].std()), 2))
# widths: medial-axis distance x 2 on the whole stroke and the wax
for nm, m in (('stroke', ty[..., 3] > 128), ('wax', wax)):
    dt = ndi.distance_transform_edt(m)
    sk = (dt >= ndi.maximum_filter(dt, 3)) & m & (dt > 1)
    print('%s width (2 x medial distance, median)' % nm, round(float(np.median(2 * dt[sk] - 1)), 2))
ys, xs = np.nonzero(ty[..., 3] > 8)
x0, y0, x1, y1 = xs.min() - 10, ys.min() - 10, xs.max() + 10, ys.max() + 10
cp = p3 * (1 - tp[..., 3:4] / 255) + tp[..., :3] * tp[..., 3:4] / 255
row = np.concatenate([p2[y0:y1, x0:x1], np.full((y1 - y0, 6, 3), 255.0), cy[y0:y1, x0:x1], np.full((y1 - y0, 6, 3), 255.0), cp[y0:y1, x0:x1]], 1)
Image.fromarray(row.astype(np.uint8)).resize((row.shape[1] * 2, row.shape[0] * 2), Image.NEAREST).save('D:/rc_scratch/combat_redesign/locked/round2/effects/work/look/trig_check.png')
print('bbox', x0, y0, x1, y1)
