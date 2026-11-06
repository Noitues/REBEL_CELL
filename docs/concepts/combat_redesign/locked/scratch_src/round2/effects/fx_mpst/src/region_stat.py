"""region_stat.py <skin> <kindA> <kindB> <layer> x0 y0 x1 y1: max / mean / p99 abs diff of two base layers inside a box"""
import sys
import numpy as np
from PIL import Image
ME = 'D:/rc_scratch/combat_redesign/locked/round2/effects/fx_mpst/work/bases/'
sk, a, b, lay = sys.argv[1:5]
x0, y0, x1, y1 = [int(v) for v in sys.argv[5:9]]
A = np.asarray(Image.open(ME + '%s_%s_%s.png' % (sk, a, lay)).convert('RGB'), np.float32)[y0:y1, x0:x1]
B = np.asarray(Image.open(ME + '%s_%s_%s.png' % (sk, b, lay)).convert('RGB'), np.float32)[y0:y1, x0:x1]
d = np.abs(A - B).max(2)
print('max', d.max(), 'mean', round(float(d.mean()), 2), 'p99', np.percentile(d, 99), 'px>6', int((d > 6).sum()), 'px>20', int((d > 20).sum()))
