"""Usage: python cmp0.py a.png b.png : counts differing pixels."""
import sys
import numpy as np
from PIL import Image
sys.dont_write_bytecode = True
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)
b = np.asarray(Image.open(sys.argv[2]).convert("RGB")).astype(int)
print("differing pixels:", int((np.abs(a - b).sum(axis=2) > 0).sum()), "shape", a.shape, b.shape)
