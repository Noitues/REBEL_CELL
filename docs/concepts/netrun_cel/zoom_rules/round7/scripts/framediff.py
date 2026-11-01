import glob, sys
import numpy as np
from PIL import Image
files = sorted(glob.glob(sys.argv[1] + "/gif_*.png"))
a0 = np.asarray(Image.open(files[0]).convert("RGB")).astype(np.int16)
for i, f in enumerate(files):
    d = np.abs(np.asarray(Image.open(f).convert("RGB")).astype(np.int16) - a0).max(axis=2)
    ys, xs = np.nonzero(d > 8)
    print(i, int((d > 0).sum()), int((d > 8).sum()), (xs.min(), ys.min(), xs.max(), ys.max()) if len(xs) else "")
