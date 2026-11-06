"""probe_pair.py <a.png> <b.png> <x0,y0,x1,y1> <scale> <out.png> -- side-by-side crop of two plates at an integer zoom (NEAREST), plus the
per-pixel L* of both along the crop (max, p99) and the mean signed difference a - b."""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import rb_tokens as TK
a = Image.open(sys.argv[1]).convert('RGB')
b = Image.open(sys.argv[2]).convert('RGB')
box = tuple(int(v) for v in sys.argv[3].split(','))
s = int(sys.argv[4])
ca, cb = a.crop(box), b.crop(box)
w, h = ca.size
out = Image.new('RGB', (w * s * 2 + 8, h * s), (255, 0, 255))
out.paste(ca.resize((w * s, h * s), Image.NEAREST), (0, 0))
out.paste(cb.resize((w * s, h * s), Image.NEAREST), (w * s + 8, 0))
out.save(sys.argv[5])
for nm, c in (('a', ca), ('b', cb)):
    L = TK.lstar(TK.lum(np.asarray(c, np.float64)))
    print(nm, 'L* max %.1f p99 %.1f mean %.1f' % (L.max(), np.percentile(L, 99), L.mean()))
d = np.asarray(ca, np.float64) - np.asarray(cb, np.float64)
print('mean a-b', d.mean(axis=(0, 1)).round(2), 'max |d|', np.abs(d).max())
