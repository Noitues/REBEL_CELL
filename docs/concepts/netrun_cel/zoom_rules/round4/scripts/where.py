import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
a = np.asarray(Image.open(sys.argv[1]).convert("RGB"), dtype=np.int16)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB"), dtype=np.int16)
d = np.abs(a - b).max(axis=2)
ys, xs = np.nonzero(d > 0)
print(len(ys))
if len(ys):
    print("bbox x %d-%d y %d-%d" % (xs.min(), xs.max(), ys.min(), ys.max()))
    # cluster by 64px cells
    cells = {}
    for y, x in zip(ys, xs):
        cells[(x // 64, y // 64)] = cells.get((x // 64, y // 64), 0) + 1
    for k, v in sorted(cells.items(), key=lambda kv: -kv[1])[:10]:
        print("cell x%d y%d n=%d" % (k[0] * 64, k[1] * 64, v))
