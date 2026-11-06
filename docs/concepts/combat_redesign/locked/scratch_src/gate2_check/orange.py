"""orange.py -- SCHEDULE-orange pixels (R > 225, 105 < G < 175, B < 70) on the board half, split into: inside the tape mask (the live step),
the wave-ticket corner (W6 hazard ticks, allowed by VISUAL_PLAN F), and anywhere else (clusters listed).  Also the K clock material colour
(median sRGB of tape + plates pixels with chroma < 12)."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
WORK = 'D:/rc_scratch/combat_redesign/locked/corp/work/'
for n, s in (('p1_decide', 'p1'), ('p2_preview', 'p2'), ('p3_resolve', 'p3'), ('p2b_hover', 'p2b'), ('p1_decide_meridian', 'p1_meridian'), ('p1_decide_solace', 'p1_solace')):
    rgb = np.asarray(Image.open(FINAL + n + '.png').convert('RGB')).astype(float)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    org = (R > 225) & (G > 105) & (G < 175) & (B < 70)
    org[:, 1060:] = False
    z = np.load(WORK + 'masks_%s.npz' % s)
    get = lambda k: np.unpackbits(z[k])[:1080 * 1920].reshape(1080, 1920).astype(bool) if k in z.files else np.zeros((1080, 1920), bool)
    tape = ndi.binary_dilation(get('tape'), iterations=4)
    tick = np.zeros((1080, 1920), bool)
    tick[18:100, 18:300] = True
    other = org & ~tape & ~tick
    lab, k = ndi.label(ndi.binary_dilation(other, iterations=2))
    cl = []
    for i in range(1, k + 1):
        ys, xs = np.nonzero((lab == i) & other)
        if len(xs) >= 8:
            cl.append((len(xs), [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]))
    cl.sort(reverse=True)
    kk = (get('tape') | get('plates'))
    mx, mn = rgb.max(2), rgb.min(2)
    grey = kk & ((mx - mn) < 14)
    med = np.median(rgb[grey], 0).astype(int)
    print('%-20s orange px: in tape %d, W6 ticks %d, elsewhere %d  clusters %s | K material median #%02X%02X%02X' % (
        n, int((org & tape).sum()), int((org & tick).sum()), int(other.sum()), cl[:6], *med))
