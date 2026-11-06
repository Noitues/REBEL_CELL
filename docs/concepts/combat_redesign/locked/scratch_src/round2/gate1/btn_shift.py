"""gate1 C6/C8: horizontal shift of the UNDO / SEND IT column between the board p1 plate and each hover plate (and round 1), by
best normalised correlation of the luminance edge map in the button box (x 1640-1919, y 850-1010) over shifts -24..24 px."""
import glob, os, sys
import numpy as np
from scipy import ndimage as ndi
import glib as G


def edges(p):
    Y = G.lum(G.load(p))[850:1010, :]
    gx = ndi.sobel(Y, 1); gy = ndi.sobel(Y, 0)
    return np.hypot(gx, gy)


ref = edges(G.FINAL + 'p1_decide.png')
x0, x1 = 1640, 1890
R = ref[:, x0:x1]
files = [G.FINAL + 'p2_preview.png', G.FINAL + 'p2b_hover.png', G.FINAL + 'p3_resolve.png'] + sorted(glob.glob(G.HOVER + 'h[0-9]*.png'))
files += sys.argv[1:]
for f in files:
    E = edges(f)
    best = None
    for s in range(-24, 25):
        C = E[:, x0 + s:x1 + s]
        c = float((R * C).sum() / (np.sqrt((R * R).sum() * (C * C).sum()) + 1e-9))
        if best is None or c > best[1]:
            best = (s, c)
    print('%-40s shift vs p1 %+d px (corr %.3f)' % (os.path.basename(f), best[0], best[1]))
