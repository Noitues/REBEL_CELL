"""turret.py -- p2 / p3 TURRET slice (sector 2, r 72-186, +-25 deg, icon disc r 48 cut): which capture masks hold the pixels above L* 90."""
import numpy as np
from PIL import Image

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)
yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
ANG = (np.degrees(np.arctan2(xx - C[0], -(yy - C[1]))) + 360) % 360
for n, s in (('p2_preview', 'p2'), ('p1_decide', 'p1')):
    rgb = np.asarray(Image.open(FINAL + n + '.png').convert('RGB')).astype(float)
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    L = np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)
    a = (ANG - 120 + 180) % 360 - 180
    cx, cy = C[0] + 120 * np.sin(np.radians(120)), C[1] - 120 * np.cos(np.radians(120))
    reg = (RHO >= 72) & (RHO <= 186) & (np.abs(a) <= 25) & (np.hypot(xx - cx, yy - cy) > 48)
    hi = reg & (L > 90)
    z = np.load(WORK + 'masks_%s.npz' % s)
    print('==', n, 'bright px', int(hi.sum()), 'region px', int(reg.sum()))
    for k in z.files:
        m = np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool)
        v = int((hi & m).sum())
        if v:
            print('   in mask %-10s %d' % (k, v))
    ys, xs = np.nonzero(hi)
    if len(xs):
        print('   box', xs.min(), ys.min(), xs.max(), ys.max(), 'median rgb', np.median(rgb[hi], 0).astype(int))
