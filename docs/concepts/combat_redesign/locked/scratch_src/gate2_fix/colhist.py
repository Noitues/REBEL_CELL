"""colhist.py <sfx> <png> <mask> [n]: most common colours of the pixels in a capture mask with L* above 60"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
from collections import Counter
import rb_checks as RC
import rb_tokens as T
sfx, png, mk = sys.argv[1:4]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 10
m = RC.load_masks(sfx)[mk]
rgb = np.asarray(Image.open(png).convert('RGB'))
L = T.lstar(T.lum(rgb.astype(np.float64)))
sel = m & (L > 60)
c = Counter(map(tuple, rgb[sel].tolist()))
print(mk, 'px', int(m.sum()), 'L>60', int(sel.sum()))
for col, k in c.most_common(n):
    print(col, k, 'L %.1f' % T.lstar(T.lum(np.array([col], np.float64)))[0])
