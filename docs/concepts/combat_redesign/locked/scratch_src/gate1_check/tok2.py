import sys, numpy as np
from lab import *
from lab import _xx, _yy
for hx in ['#D9E1EA', '#FFF4D6', '#FFEAE0', '#FF4433', '#C8CED8', '#F2EEE4', '#6E7580', '#969EAA', '#FF8C1A', '#F06EAE', '#5E9BE0', '#D6A33A', '#3FB59A', '#D9877C', '#96767A']:
    print(hx, 'L* %.1f' % float(lab(hex2rgb(hx))[0]))
print('cap (200,206,216) L* %.1f' % float(lab(np.array([200, 206, 216]) / 255)[0]))
def ppx(r, a):
    return C[0] + r * np.sin(np.radians(a)), C[1] - r * np.cos(np.radians(a))
for p in sys.argv[1:]:
    im = load(p); y = Y(im); L = Ls(y)
    print('==', p)
    toks = {'r0 u3 Worm': (242, 38.5), 'r0 u1 Packet': (242, 158.5), 'r0 u2 Worm dying': (242, 278), 'r1 u4 Payload': (300, 157.5), 'r1 u5 Packet': (300, 337.5), 'r2 u6 Packet': (356, 95.5), 'r2 u7 Packet': (356, 276)}
    for nm, (r, a) in toks.items():
        cx, cy = ppx(r, a)
        # refine centre: centroid of bright glyph px within 20 px
        d = np.hypot(_xx - cx, _yy - cy)
        inner = (d < 17)
        ring = (d >= 17) & (d < 28)
        si = stats(y, inner); sr = stats(y, ring)
        print('  %-18s glyph(r<17) p95 %.1f max %.1f | ring(17-28) p95 %.1f p99 %.1f max %.1f' % (nm, si['p95'], float(L[inner].max()), sr['p95'], float(Ls(np.percentile(y[ring], 99))), float(L[ring].max())))
