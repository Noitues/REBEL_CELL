import sys, numpy as np
from lab import *
def hsv(im):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    mx = im.max(axis=2); mn = im.min(axis=2); d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, mx - mn
for p in sys.argv[1:]:
    im = load(p); y = Y(im); L = Ls(y); h, ch = hsv(im)
    print('==', p)
    allhot = np.zeros(L.shape, bool)
    for sct in [1, 2, 3, 4, 0, 5]:
        z = polar_mask(221, 250, 60 * sct - 7, 60 * sct + 7)
        mark = z & (((ch > 0.25) & ((h < 30) | (h > 335))) | (L > 80))
        if sct in (1, 2, 3, 4): allhot |= mark
        if mark.sum() < 10:
            print('  ring0 s%d: no chevron px' % sct); continue
        s = stats(y, mark)
        print('  ring0 s%d chevron px %4d p95 %.1f p99 %.1f max %.1f med %.1f' % (sct, s['n'], s['p95'], float(Ls(np.percentile(y[mark], 99))), float(L[mark].max()), s['med']))
    if allhot.any():
        s = stats(y, allhot); print('  ring0 HOT chevrons (s1-s4) all: p95 %.1f med %.1f n %d' % (s['p95'], s['med'], s['n']))
    # HP trays: cream ticks per ring (bright, low chroma, warm)
    for k, (r0, r1) in {0: (250, 265), 1: (306, 321), 2: (362, 379)}.items():
        z = polar_mask(r0, r1, 0, 360)
        tick = z & (L > 75) & (ch < 0.25)
        if tick.sum() < 10: print('  ring%d HP ticks: none' % k); continue
        s = stats(y, tick)
        print('  ring%d HP ticks px %5d p95 %.1f med %.1f max %.1f' % (k, s['n'], s['p95'], s['med'], float(L[tick].max())))
    # COLD chevrons ring 1 (s0 u5, s3/s4 u4) and FAR chevrons ring 2
    for k, (r0, r1), secs in [(1, (276, 306), (0, 3, 4)), (2, (333, 362), (2, 3, 4, 5))]:
        for sct in secs:
            z = polar_mask(r0, r1, 60 * sct - 7, 60 * sct + 7)
            mark = z & (ch > 0.12) & ((h < 30) | (h > 320))
            if mark.sum() < 10: continue
            s = stats(y, mark)
            print('  ring%d s%d chevron px %4d p95 %.1f med %.1f' % (k, sct, s['n'], s['p95'], s['med']))
