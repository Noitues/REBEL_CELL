"""dotspots.py <png> x0 y0 x1 y1: the dot_audit spots inside a box (sign, area, colour) and the runs touching it"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import dot_audit as DA
png = sys.argv[1]
x0, y0, x1, y1 = [int(v) for v in sys.argv[2:6]]
a = np.asarray(Image.open(png).convert('RGB')).astype(np.float32)
sp = DA.spots(a)
for s in sp:
    if x0 <= s['x'] <= x1 and y0 <= s['y'] <= y1:
        print('spot x %.1f y %.1f area %.0f sign %s col %s' % (s['x'], s['y'], s['area'], s['sign'], [int(c) for c in s['col']]))
