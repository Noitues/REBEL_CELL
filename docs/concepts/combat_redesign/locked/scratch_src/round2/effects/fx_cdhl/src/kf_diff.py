"""kf_diff.py <a.png> <b.png> [thr] : where two frames differ (bbox, px count, and the connected blobs' boxes), for checking state changes"""
import sys
import numpy as np
from PIL import Image
a = np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(int)
b = np.asarray(Image.open(sys.argv[2]).convert('RGB')).astype(int)
thr = int(sys.argv[3]) if len(sys.argv) > 3 else 24
m = np.abs(a - b).max(axis=2) > thr
print('px', int(m.sum()))
if m.any():
    ys, xs = np.nonzero(m)
    print('bbox', xs.min(), ys.min(), xs.max(), ys.max())
    # coarse blobs on a 10 px grid
    g = m[:m.shape[0] // 10 * 10, :m.shape[1] // 10 * 10].reshape(m.shape[0] // 10, 10, m.shape[1] // 10, 10).any(axis=(1, 3))
    seen = np.zeros_like(g)
    for y0, x0 in zip(*np.nonzero(g)):
        if seen[y0, x0]:
            continue
        st, cells = [(y0, x0)], []
        seen[y0, x0] = True
        while st:
            y, x = st.pop()
            cells.append((y, x))
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < g.shape[0] and 0 <= xx < g.shape[1] and g[yy, xx] and not seen[yy, xx]:
                        seen[yy, xx] = True
                        st.append((yy, xx))
        c = np.array(cells)
        print('blob', c[:, 1].min() * 10, c[:, 0].min() * 10, c[:, 1].max() * 10 + 10, c[:, 0].max() * 10 + 10, 'cells', len(cells))
