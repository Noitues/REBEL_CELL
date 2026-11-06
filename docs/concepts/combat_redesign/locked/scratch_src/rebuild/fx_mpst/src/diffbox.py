"""diffbox.py <skin> <kindA> <kindB>: bounding box of the pixels that differ between two base plates (full), split by layer"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from PIL import Image
ME = 'D:/rc_scratch/combat_redesign/locked/rebuild/fx_mpst/work/bases/'
sk, a, b = sys.argv[1:4]
for lay in ('full', 'below', 'above'):
    A = np.asarray(Image.open(ME + '%s_%s_%s.png' % (sk, a, lay)).convert('RGBA'), np.int16)
    B = np.asarray(Image.open(ME + '%s_%s_%s.png' % (sk, b, lay)).convert('RGBA'), np.int16)
    m = np.abs(A - B).max(2) > 6
    ys, xs = np.nonzero(m)
    print(lay, 'n', int(m.sum()), 'box', (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1) if len(xs) else None)
