"""pencil.py -- PLAN pencil stroke width and ink edge on the board plates (VISUAL_PLAN A.5 / L6: PLAN 7 px + 3 px ink edge, wax grain).

PLAN-yellow pixels on the board half (x < 1060): R > 200, G > 170, B < 110, R >= G - 10 (FOCUS lime and Solace leaf have G >> R).
Stroke width = 2 x the Euclidean distance transform at skeleton pixels (approximated by local maxima of the distance transform), per
connected stroke; plus the ink edge: L* p50 of the 3 px band outside the stroke; plus grain: the L* standard deviation inside the stroke
(eroded 1 px)."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

FINAL = 'D:/rc_art/art-pass/docs/concepts/combat_redesign/locked/final/'


def lstar_img(rgb):
    c = rgb / 255.0
    c = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    Y = 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]
    return np.where(Y > 0.008856, 116 * np.cbrt(Y) - 16, 903.3 * Y)


for n in sys.argv[1:] or ['p2_preview', 'p2b_hover', 'p3_resolve', 'p1_decide']:
    rgb = np.asarray(Image.open(FINAL + n + '.png').convert('RGB')).astype(float)
    L = lstar_img(rgb)
    R, G, B = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    y = (R > 200) & (G > 170) & (B < 110) & (R >= G - 10)
    y[:, 1060:] = False
    y[:110, :310] = False   # wave tickets corner (W6 hazard ticks are SCHEDULE)
    y = ndi.binary_opening(y, iterations=0) if False else y
    lab, k = ndi.label(y)
    sizes = ndi.sum(y, lab, range(1, k + 1))
    print('==', n, 'PLAN-yellow px', int(y.sum()), 'strokes', k)
    for i in np.argsort(-sizes)[:8]:
        m = lab == (i + 1)
        if m.sum() < 60:
            continue
        dt = ndi.distance_transform_edt(m)
        mx = (dt == ndi.maximum_filter(dt, size=3)) & (dt > 0.9)
        w = 2 * dt[mx]
        ys, xs = np.nonzero(m)
        ring = ndi.binary_dilation(m, iterations=3) & ~m
        inner = ndi.binary_erosion(m, iterations=1)
        grain = float(L[inner].std()) if inner.any() else float('nan')
        print('   stroke px %5d box %s width p50 %.1f p90 %.1f | edge band L* p50 %.1f | interior L* std %.1f' % (
            m.sum(), [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())], float(np.median(w)), float(np.percentile(w, 90)),
            float(np.median(L[ring])), grain))
