"""r1r2_diff.py: where the round-2 plates differ from round 1 (published PNGs): hand boxes, board ring, HUD; bounding boxes of the change."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
FIN = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'
R1 = 'D:/rc_scratch/combat_redesign/locked/round2/effects/work/r1/'
C = (536.0, 540.0)
yy, xx = np.mgrid[0:1080, 0:1920]
rho = np.hypot(xx - C[0], yy - C[1])
BOX = {'TR_CARD_p1': (1267, 762, 1476, 1052), 'TR_SLOT_p3': (1275, 769, 1466, 1041), 'hand': (900, 740, 1680, 1080), 'buttons': (1660, 840, 1920, 1080)}
for p in ('p1_decide', 'p2_preview', 'p3_resolve'):
    a = np.asarray(Image.open(R1 + p + '.png').convert('RGB')).astype(int)
    b = np.asarray(Image.open(FIN + p + '.png').convert('RGB')).astype(int)
    d = np.abs(a - b).max(2) > 24
    print('==', p, 'changed px', int(d.sum()))
    for nm, (x0, y0, x1, y1) in BOX.items():
        dd = d[y0:y1, x0:x1]
        if dd.any():
            ys, xs = np.nonzero(dd)
            print('  %-11s %6d px  bbox x %d-%d y %d-%d' % (nm, int(dd.sum()), x0 + xs.min(), x0 + xs.max(), y0 + ys.min(), y0 + ys.max()))
        else:
            print('  %-11s 0 px' % nm)
    for r0, r1 in ((0, 200), (200, 390), (390, 505), (505, 560)):
        m = d & (rho >= r0) & (rho < r1)
        print('  board r %d-%d: %d px' % (r0, r1, int(m.sum())))
    lab, n = ndi.label(ndi.binary_dilation(d & (rho < 505), iterations=3))
    big = sorted([(int((lab[s] == i + 1).sum()), s) for i, s in enumerate(ndi.find_objects(lab))], key=lambda v: -v[0])[:8]
    for k, s in big:
        print('    blob %5d px x %d-%d y %d-%d' % (k, s[1].start, s[1].stop, s[0].start, s[0].stop))
