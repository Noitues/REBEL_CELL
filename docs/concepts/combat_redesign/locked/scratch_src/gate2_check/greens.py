"""greens.py -- what green / lime marks sit on the enemy rings (r 214-385): clusters of FOCUS-lime (G > R + 15, G > 200, B < 90) and
GAIN-green (G > 170, G - R > 40, G - B > 60) pixels, with box, size and median colour; plus green on the badges mask."""
import sys, json
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
C = (536, 540)
yy, xx = np.mgrid[0:1080, 0:1920]
RHO = np.hypot(xx - C[0], yy - C[1])
for n, s in (('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p3_resolve', 'p3'), ('p2b_hover', 'p2b')):
    rgb = np.asarray(Image.open(FINAL + n + '.png').convert('RGB')).astype(float)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lime = (G > R + 15) & (G > 200) & (B < 90)
    green = (G > 170) & (G - R > 40) & (G - B > 60)
    ring = (RHO >= 214) & (RHO <= 385)
    z = np.load(WORK + 'masks_%s.npz' % s)
    badges = np.unpackbits(z['badges'])[:1080 * 1920].reshape(1080, 1920).astype(bool)
    print('==', n, 'lime on rings', int((lime & ring).sum()), 'green on rings', int((green & ring).sum()), 'green|lime on badges', int(((lime | green) & badges).sum()))
    for nm, m in (('lime', lime & ring), ('green', green & ring), ('badge-green', (lime | green) & badges)):
        lab, k = ndi.label(ndi.binary_dilation(m, iterations=3))
        for i in range(1, k + 1):
            ys, xs = np.nonzero((lab == i) & m)
            if len(xs) < 15:
                continue
            med = np.median(rgb[ys, xs], 0).astype(int)
            print('   %-11s n %4d box %s median #%02X%02X%02X' % (nm, len(xs), [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], *med))
