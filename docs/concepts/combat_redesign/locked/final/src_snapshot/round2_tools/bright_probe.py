"""Round 2 probe: bright board pixels inside r < 480 that sit in no capture class (C3).
python bright_probe.py <png> <sfx> <outdir> [L_thr]
Prints clusters (bbox, px, max L*) and writes 4x crops of the largest clusters."""
import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import rb_tokens as T
import rb_checks as RC

png, sfx, out = sys.argv[1], sys.argv[2], sys.argv[3]
thr = float(sys.argv[4]) if len(sys.argv) > 4 else 88.0
os.makedirs(out, exist_ok=True)
rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.float64)
Ls = T.lstar(T.lum(rgb))
M = RC.load_masks(sfx)
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - 536, yy - 540)
anyc = np.zeros((1080, 1920), bool)
for k, m in M.items():
    if k.startswith('card_') or k == 'scrim':
        continue
    anyc |= m
print('classes', sorted(M))
sel = (rho < 480) & ~anyc & (Ls >= thr)
lab, n = ndi.label(sel, structure=np.ones((3, 3)))
print('unclassed bright px (L* >= %.0f) inside r480:' % thr, int(sel.sum()), 'clusters', n)
rows = []
for i, sl in enumerate(ndi.find_objects(lab), 1):
    m = lab[sl] == i
    v = Ls[sl][m]
    rows.append((int(m.sum()), sl[1].start, sl[0].start, sl[1].stop, sl[0].stop, float(v.max()), float(np.median(rho[sl][m]))))
rows.sort(key=lambda r: -r[0])
for r in rows[:40]:
    print('  px %5d  box x %d-%d y %d-%d  max L* %.1f  r %.0f' % (r[0], r[1], r[3], r[2], r[4], r[5], r[6]))
im = Image.open(png).convert('RGB')
for j, r in enumerate(rows[:8]):
    cx, cy = (r[1] + r[3]) // 2, (r[2] + r[4]) // 2
    box = (max(0, cx - 40), max(0, cy - 30), min(1920, cx + 40), min(1080, cy + 30))
    im.crop(box).resize(((box[2] - box[0]) * 5, (box[3] - box[1]) * 5), Image.NEAREST).save(out + '/c%d_%d_%d.png' % (j, cx, cy))
# all classes inside r480: share of pixels
tot = (rho < 480).sum()
print('classed share inside r480: %.3f' % ((anyc & (rho < 480)).sum() / tot))
