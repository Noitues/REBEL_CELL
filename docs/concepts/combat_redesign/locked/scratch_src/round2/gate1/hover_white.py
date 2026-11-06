"""gate1 C3 on hover: near-neutral white pixels (L* >= 95, C* < 6) inside 212 <= r < 480 on each hover plate, vs that plate's HOT reference
(b2_bright.hot_p95_lit from round2/hover/chk/<name>.checks.json).  Warm HOT core (C* >= 6) is excluded."""
import glob, os, json
import numpy as np
from scipy import ndimage as ndi
import glib as G
r_, th_, xx, yy = G.polar()
for f in sorted(glob.glob(G.HOVER + 'h[0-9]*.png')):
    nm = os.path.basename(f)[:-4]
    rgb = G.load(f); L = G.Lstar(rgb); lab = G.lab(rgb)
    C = np.hypot(lab[..., 1], lab[..., 2])
    m = (L >= 95) & (C < 6) & (r_ >= 212) & (r_ < 480)
    lb, n = ndi.label(ndi.binary_dilation(m, iterations=2))
    big = [(int((lb == k).sum() and (m & (lb == k)).sum())) for k in range(1, n + 1)]
    try:
        ck = json.load(open('D:/rc_scratch/combat_redesign/locked/round2/hover/chk/%s.checks.json' % nm))
        hot = ck['b2_bright'].get('hot_p95_lit')
    except Exception:
        hot = None
    ys, xs = np.nonzero(m)
    print('%-26s white px (L*>=95, C*<6) %4d in %d clusters %s; HOT ref p95 %s' % (nm, int(m.sum()), n,
          '(bbox %d-%d, %d-%d)' % (xs.min(), xs.max(), ys.min(), ys.max()) if len(xs) else '', hot))
