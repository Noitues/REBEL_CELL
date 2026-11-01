import glob, sys
import numpy as np
from PIL import Image
files = sorted(glob.glob(sys.argv[1] + "/gif_*.png"))
st = np.stack([np.asarray(Image.open(f).convert("L")).astype(np.float32) for f in files])
mx = st.max(0); mn = st.min(0)
m = (mx > 100) & (mn < 0.8 * mx)
m[:int(sys.argv[2])] = False
m[int(sys.argv[3]):] = False
ys, xs = np.nonzero(m)
print("dip pixels", m.sum())
if len(xs):
    # coarse clusters on a 40 px grid
    cells = {}
    for y, x in zip(ys, xs):
        cells.setdefault((x // 40, y // 40), []).append((x, y))
    for (cx, cy), p in sorted(cells.items(), key=lambda kv: -len(kv[1]))[:15]:
        px = np.array(p)
        x0, y0 = px.min(0); x1, y1 = px.max(0)
        reg = st[:, y0:y1 + 1, x0:x1 + 1].mean((1, 2))
        print("cell %d,%d n=%d box=(%d,%d,%d,%d) min/max=%.2f frames argmin=%d" % (cx, cy, len(p), x0, y0, x1, y1, reg.min() / reg.max(), reg.argmin()))
