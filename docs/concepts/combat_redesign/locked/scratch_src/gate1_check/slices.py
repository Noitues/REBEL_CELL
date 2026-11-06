import sys, numpy as np
from lab import *
from lab import _xx, _yy
INK = {'BURST': '#F06EAE', 'SHIELD': '#5E9BE0', 'TURRET': '#D6A33A', 'REPAIR': '#3FB59A'}
WHEEL = {0: 'BURST', 1: 'SHIELD', 2: 'TURRET', 3: 'SHIELD', 4: 'BURST', 5: 'REPAIR'}
def ppx(r, a):
    return C[0] + r * np.sin(np.radians(a)), C[1] - r * np.cos(np.radians(a))
for p in sys.argv[1:]:
    im = load(p); y = Y(im); L = Ls(y)
    print('==', p)
    lab_im = None
    for s, t in WHEEL.items():
        ink = hex2rgb(INK[t]); Lab_ink = lab(ink)
        cx, cy = ppx(127, 60 * s)
        z = polar_mask(78, 182, 60 * s - 24, 60 * s + 24) & (np.hypot(_xx - cx, _yy - cy) > 60)
        # pixels close in Lab to the ink (within dE 18) = the ink fill, texture excluded
        sub = im[z]
        dl = np.linalg.norm(lab(sub) - Lab_ink, axis=1)
        inkpx = dl < 18
        Lz = L[z]
        disc = (np.hypot(_xx - cx, _yy - cy) < 56)
        sd = stats(y, disc)
        whole = stats(y, z)
        if inkpx.sum() > 30:
            Li = Lz[inkpx]
            print('  s%d %-6s ink hex L* %.1f | ink-fill px %5d (%.0f%% of slice) med L* %.1f p95 %.1f | slice area p95 %.1f mean %.1f | icon disc p95 %.1f max %.1f' % (s, t, Lab_ink[0], inkpx.sum(), 100 * inkpx.mean(), np.median(Li), np.percentile(Li, 95), whole['p95'], whole['mean'], sd['p95'], float(L[disc].max())))
        else:
            print('  s%d %-6s ink hex L* %.1f | ink-fill px %d (hatched?) | slice area p95 %.1f mean %.1f | icon disc p95 %.1f' % (s, t, Lab_ink[0], inkpx.sum(), whole['p95'], whole['mean'], sd['p95']))
    tw = R < 196
    st = stats(y, tw); print('  whole tower r<196: p95 %.1f med %.1f mean %.1f' % (st['p95'], st['med'], st['mean']))
