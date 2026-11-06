"""diff_parts.py <skin> <kindA> <kindB> <layer>: connected regions where two base layers differ (bbox and px), largest first"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from scipy import ndimage as ndi
from PIL import Image
ME = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/work/bases/'
sk, a, b, lay = sys.argv[1:5]
A = np.asarray(Image.open(ME + '%s_%s_%s.png' % (sk, a, lay)).convert('RGBA'), np.int16)
B = np.asarray(Image.open(ME + '%s_%s_%s.png' % (sk, b, lay)).convert('RGBA'), np.int16)
m = np.abs(A - B).max(2) > 6
lab, n = ndi.label(ndi.binary_dilation(m, iterations=4))
out = []
for i in range(1, n + 1):
    ys, xs = np.nonzero((lab == i) & m)
    if len(xs):
        out.append((len(xs), (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)))
out.sort(reverse=True)
for k, bb in out[:15]:
    print(k, bb)
