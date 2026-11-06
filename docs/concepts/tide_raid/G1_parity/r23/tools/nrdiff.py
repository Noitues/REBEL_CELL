import numpy as np
from PIL import Image
a = np.asarray(Image.open("D:/rc_scratch/g1/r23/nr_before/overview_seed1/beauty.png").convert("RGB")).astype(int)
b = np.asarray(Image.open("D:/rc_scratch/g1/r23/nr_after/overview_seed1/beauty.png").convert("RGB")).astype(int)
d = np.abs(a - b)
print("max diff", d.max(), "mean", d.mean(), "pixels differing", int((d.sum(axis=2) > 0).sum()))
