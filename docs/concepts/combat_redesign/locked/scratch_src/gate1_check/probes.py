import sys, numpy as np
from lab import *
from lab import _xx, _yy
plates = sys.argv[1:] or ['p1_decide']
def hsv_h(im):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    mx = im.max(axis=2); mn = im.min(axis=2); d = mx - mn + 1e-9
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    return h, mx - mn
def ppx(r, a):
    return C[0] + r * np.sin(np.radians(a)), C[1] - r * np.cos(np.radians(a))
for p in plates:
    im = load(p); y = Y(im); L = Ls(y); h, ch = hsv_h(im)
    print('==', p)
    # 1. THIS TURN live step on the bezel band (r 391-417), angles 0-118 (schedule +2 from sector 0)
    band = polar_mask(389, 419, 0, 118)
    orange = band & (h > 15) & (h < 45) & (ch > 0.35)
    gm = band & (ch < 0.12)
    s = stats(y, band); so = stats(y, orange); sg = stats(y, gm)
    print('  THIS TURN band 0-118deg: p95 %.1f med %.1f mean %.1f | orange px %d p95 %.1f med %.1f | grey px p95 %.1f med %.1f' % (s['p95'], s['med'], s['mean'], so['n'], so['p95'], so['med'], sg['p95'], sg['med']))
    for nm, a0, a1 in [('HOLD NEXT plate', 120, 158), ('HOLD THEN plate', 160, 198), ('+2 THIS TURN plate', 0, 30)]:
        m = polar_mask(392, 416, a0, a1) & (ch < 0.12)
        s = stats(y, m); print('  %-20s grey p95 %.1f med %.1f mean %.1f' % (nm, s['p95'], s['med'], s['mean']))
    # whole clock family proxy: bezel band all angles, grey only (plates + band) and orange
    allband = polar_mask(389, 419, 0, 360)
    s = stats(y, allband); print('  bezel band all: p95 %.1f med %.1f' % (s['p95'], s['med']))
    # 2. token discs: boxes around token centres (ring mid radius, cell start + ~7.5 deg)
    toks = {'r0 u3 Worm': (242, 38.5), 'r0 u1 Packet': (242, 158.5), 'r0 u2 Worm dying': (242, 278), 'r1 u4 Payload': (300, 157.5), 'r1 u5 Packet': (300, 337.5), 'r2 u6 Packet': (356, 95.5), 'r2 u7 Packet': (356, 276)}
    for nm, (r, a) in toks.items():
        cx, cy = ppx(r, a)
        m = np.hypot(_xx - cx, _yy - cy) < 27
        s = stats(y, m)
        mg = m & (L > 60)
        print('  token %-18s at (%4.0f,%4.0f) disc p95 %.1f p99 %.1f max %.1f mean %.1f bright-px %d' % (nm, cx, cy, s['p95'], float(Ls(np.percentile(y[m], 99))), float(L[m].max()), s['mean'], int(mg.sum())))
    # 3. HOT chevrons on ring NOW: sector centres of live ring-0 units with HOT marks (s1,s2,s3,s4)
    for sct in [1, 2, 3, 4, 0, 5]:
        m = polar_mask(216, 262, 60 * sct - 6, 60 * sct + 6)
        red = m & (ch > 0.25) & ((h < 25) | (h > 340))
        core = m & (L > 85)
        s = stats(y, m)
        sr = stats(y, red) if red.sum() > 20 else None
        print('  ring0 s%d chevron zone p95 %.1f p99 %.1f | red px %d %s | core(L>85) px %d' % (sct, s['p95'], float(Ls(np.percentile(y[m], 99))), int(red.sum()), ('red p95 %.1f med %.1f' % (sr['p95'], sr['med'])) if sr else '', int(core.sum())))
