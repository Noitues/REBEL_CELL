"""tags.py <plate.png> <sfx>: the ring-tag class (asm_render 'tags' mask) p95 / p99 L*, and the NOW W1 tag box (628-703, 306-335) line: L* of the
box's 1-3 px border ring, its max, and its median sRGB"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import rb_tokens as T
import rb_checks as RC
png, sfx = sys.argv[1], sys.argv[2]
rgb = np.asarray(Image.open(png).convert('RGB'))
Ls = 116 * np.cbrt(T.lum(rgb)) - 16 if T.lum(rgb).max() <= 1.0 else None
Y = T.lum(rgb)
Ls = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
M = RC.load_masks(sfx)
t = M.get('tags')
if t is not None:
    v = Ls[t]
    print('tags class px', int(t.sum()), 'p95 %.1f p99 %.1f max %.1f' % (np.percentile(v, 95), np.percentile(v, 99), v.max()))
    b = v >= 80
    print('  tags px L*>=80', int(b.sum()))
x0, y0, x1, y1 = 628, 306, 703, 335
sub = Ls[y0:y1 + 1, x0:x1 + 1]
ring = np.zeros_like(sub, bool)
ring[:3, :] = ring[-3:, :] = True
ring[:, :3] = ring[:, -3:] = True
print('NOW box border (3 px ring) p50 %.1f p95 %.1f max %.1f' % (np.median(sub[ring]), np.percentile(sub[ring], 95), sub[ring].max()))
mx = np.unravel_index(np.argmax(np.where(ring, sub, 0)), sub.shape)
print('  brightest border px at', (x0 + mx[1], y0 + mx[0]), rgb[y0 + mx[0], x0 + mx[1]])
br = sub >= 85
print('  box px L*>=85', int(br.sum()), 'max in box %.1f' % sub.max())
