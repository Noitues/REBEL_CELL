"""gate1: print raw normal profiles (L*, dE to PLAN, rgb) across board pencil strokes at a few points, to calibrate ink thresholds.
usage: pencil_prof.py <png> x,y,dx,dy ...   (dx,dy = stroke normal direction)"""
import sys
import numpy as np
import glib as G
rgb = G.load(sys.argv[1])
L = G.Lstar(rgb)
dP = G.de(G.lab(rgb), '#FFE200')
for a in sys.argv[2:]:
    x, y, dx, dy = map(float, a.split(','))
    n = np.hypot(dx, dy); dx /= n; dy /= n
    print('point', x, y, 'normal', round(dx, 2), round(dy, 2))
    for s in range(-12, 13):
        px = int(round(x + dx * s)); py = int(round(y + dy * s))
        print('  %3d (%4d,%4d) L*%5.1f dE%5.1f rgb %s' % (s, px, py, L[py, px], dP[py, px], tuple(int(v) for v in rgb[py, px])))
