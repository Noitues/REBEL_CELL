"""ticket_ink.py <plate.png> : ink height (px) and L* of every kind glyph on the three wave tickets (glyph band of each ticket)"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import rb_tokens as T

a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float64)
Ls = T.lstar(T.lum(a))
x = 24
for i in range(3):
    y0 = 24
    band = Ls[y0 + 26:y0 + 58, x + 2:x + 82]
    m = band > 70
    lab, n = ndi.label(ndi.binary_dilation(m, iterations=1))
    out = []
    for k in range(1, n + 1):
        ys, xs = np.nonzero(lab == k)
        if len(ys) < 25:
            continue
        out.append((int(xs.min() + x + 2), int(ys.max() - ys.min() + 1), round(float(np.percentile(band[lab == k], 90)), 1)))
    print('ticket', i, 'glyphs (x, ink height px, p90 L*):', out)
    x += 84 + 8
