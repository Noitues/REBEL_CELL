import sys, numpy as np
from scipy import ndimage as ndi
from lab import *
for p in sys.argv[1:]:
    im = load(p); L = Ls(Y(im))
    out = []
    for x0, x1 in [(26, 106), (118, 198), (210, 290)]:
        sub = L[52:92, x0:x1] > 70
        lab_, n = ndi.label(ndi.binary_closing(sub, iterations=1))
        gl = []
        for i, sl in enumerate(ndi.find_objects(lab_)):
            h = sl[0].stop - sl[0].start; w = sl[1].stop - sl[1].start
            if h >= 10 and w >= 6:
                m = lab_[sl] == i + 1
                vals = L[52:92, x0:x1][sl][m]
                gl.append('%dx%d p90 %.1f' % (w, h, np.percentile(vals, 90)))
        out.append(gl)
    print(p, out)
