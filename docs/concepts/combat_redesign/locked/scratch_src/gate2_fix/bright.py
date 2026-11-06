"""bright.py <sfx> <png> <mask> [n]: where the brightest pixels of a capture mask are, and their colours"""
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'D:/rc_scratch/combat_redesign/locked/corp/src')
import numpy as np
from PIL import Image
import rb_checks as RC
import rb_tokens as T
sfx, png, mk = sys.argv[1:4]
n = int(sys.argv[4]) if len(sys.argv) > 4 else 12
M = RC.load_masks(sfx)
m = M[mk]
rgb = np.asarray(Image.open(png).convert('RGB')).astype(np.float64)
L = T.lstar(T.lum(rgb))
ys, xs = np.nonzero(m)
v = L[ys, xs]
print(mk, 'px', m.sum(), 'p95 %.1f p99 %.1f' % (np.percentile(v, 95), np.percentile(v, 99)))
o = np.argsort(-v)
thr = np.percentile(v, 99)
hi = v >= thr
print('p99+ px box x %d-%d y %d-%d' % (xs[hi].min(), xs[hi].max(), ys[hi].min(), ys[hi].max()))
from collections import Counter
c = Counter(tuple(int(t) for t in rgb[ys[i], xs[i]]) for i in o[:max(n * 20, 200)])
for col, k in c.most_common(n):
    print(col, k)
for i in o[:n:max(1, n // 6)]:
    print('  at', xs[i], ys[i], 'L %.1f' % v[i])
